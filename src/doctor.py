"""Diagnose interpreter, locked packages, native wheels and model loading.

The entry point uses only the standard library until dependency checks, so it can
explain a broken NumPy installation without importing pandas first.
"""
import argparse
import importlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import struct
import sys
import traceback

from .config import ROOT

IMPORTS = {"numpy": "numpy", "pandas": "pandas", "scipy": "scipy",
           "scikit-learn": "sklearn", "matplotlib": "matplotlib", "joblib": "joblib",
           "streamlit": "streamlit", "pytest": "pytest", "pillow": "PIL"}


def locked_packages():
    packages = {}
    for line in (ROOT / "requirements-lock.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s;]+)", line)
        if not match:
            raise ValueError(f"Expected an exact lock pin, found: {line}")
        packages[match[1]] = match[2]
    return packages


def diagnose():
    report = {"python": platform.python_version(), "executable": sys.executable,
              "base_executable": getattr(sys, "_base_executable", None),
              "architecture_bits": struct.calcsize("P") * 8,
              "platform": platform.platform(), "project_root": str(ROOT),
              "checks": {}, "packages": {}, "errors": []}

    def check(name, passed, message):
        report["checks"][name] = bool(passed)
        if not passed:
            report["errors"].append(message)

    check("python_312_x64", sys.version_info[:2] == (3, 12) and struct.calcsize("P") == 8,
          "Use Python 3.12 x64 (tested target: 3.12.10). Recreate the environment with scripts/setup.ps1.")
    check("isolated_virtual_environment", sys.prefix != sys.base_prefix,
          "Run this command with the project virtual environment's own Scripts/python.exe.")
    check("no_python_path_overrides", not any(os.environ.get(k) for k in ("PYTHONHOME", "PYTHONPATH")),
          "Clear PYTHONHOME/PYTHONPATH; they can redirect imports to another interpreter's packages.")
    shadowing = [str(path.relative_to(ROOT)) for directory in (ROOT, ROOT / "src")
                 for name in set(IMPORTS.values()) | {"packaging"}
                 for path in (directory / f"{name}.py", directory / name) if path.exists()]
    check("no_local_package_shadowing", not shadowing, f"Local names shadow installed libraries: {shadowing}")
    try:
        from packaging.specifiers import SpecifierSet
        from packaging.tags import parse_tag, sys_tags
        supported_tags = set(sys_tags())
        for name, expected in locked_packages().items():
            try:
                distribution = metadata.distribution(name)
                requires_python = distribution.metadata.get("Requires-Python", "")
                wheel = distribution.read_text("WHEEL") or ""
                tags = [line[5:].strip() for line in wheel.splitlines() if line.startswith("Tag:")]
                compatible = not tags or any(parse_tag(tag) & supported_tags for tag in tags)
                record = {"expected": expected, "installed": distribution.version,
                          "requires_python": requires_python, "wheel_tags": tags}
                report["packages"][name] = record
                check(f"pin:{name}", distribution.version == expected,
                      f"{name}: expected {expected}, installed {distribution.version}.")
                check(f"python_requirement:{name}", platform.python_version() in SpecifierSet(requires_python),
                      f"{name} requires Python {requires_python}.")
                check(f"wheel:{name}", compatible,
                      f"{name} wheel {tags} is incompatible with this Python interpreter.")
            except metadata.PackageNotFoundError:
                check(f"pin:{name}", False, f"Missing locked package: {name}=={expected}.")
    except ImportError:
        check("packaging_available", False, "Install requirements.txt to make package diagnostics available.")
    for package, module_name in IMPORTS.items():
        try:
            module = importlib.import_module(module_name)
            origin = Path(module.__file__).resolve()
            check(f"import:{package}", origin.is_relative_to(Path(sys.prefix).resolve()),
                  f"{package} imported from outside the virtual environment: {origin}")
            report["packages"].setdefault(package, {})["import_path"] = str(origin)
        except Exception:
            check(f"import:{package}", False, f"{package} import failed:\n{traceback.format_exc()}")
    if all(report["checks"].values()):
        try:
            from .artifacts import load_artifacts
            from .config import FEATURES
            from .data import validate_inputs
            import pandas as pd
            models, model_metadata = load_artifacts()
            row = validate_inputs(pd.DataFrame([model_metadata["input_defaults"]], columns=FEATURES))
            for model in models.values():
                probability = model.predict_proba(row)
                assert probability.shape == (1, 2) and abs(float(probability.sum()) - 1) < 1e-10
            check("saved_models_predict", True, "")
        except Exception:
            check("saved_models_predict", False, f"Model check failed:\n{traceback.format_exc()}")
    report["status"] = "passed" if all(report["checks"].values()) else "failed"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the full machine-readable diagnostic report.")
    args = parser.parse_args()
    report = diagnose()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"StudentLens environment: {report['status']} | Python {report['python']} | {report['architecture_bits']}-bit")
        print(f"Interpreter: {report['executable']}")
        print(f"Project: {report['project_root']}")
        for error in report["errors"]:
            print(error)
        print(f"{sum(report['checks'].values())}/{len(report['checks'])} checks passed.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
