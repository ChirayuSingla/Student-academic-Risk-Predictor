# StudentLens Windows repair and validation

Validated on 19 October 2026 with **CPython 3.12.10, 64-bit Windows**.

## Root cause

The supplied `.venv` ran Python **3.10.11**, while its installed NumPy 2.2.6 and
SciPy 1.16.2 distributions declared **`cp312-cp312-win_amd64`** wheel tags.
NumPy's compiled module was `_multiarray_umath.cp312-win_amd64.pyd`. Python 3.10
could not load this module; the inner exception was:

```text
ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'
```

NumPy wrapped this with the misleading source-directory message; pandas exposed
the failure when it imported NumPy. The active application paths contained no
`numpy.py`, `pandas.py`, `scipy.py`, `streamlit.py`, or equivalent shadowing package.
The available Python launcher reported no registered interpreters; PATH selected
Python 3.10, and the Python313 folder had no executable. These conditions made
bare `python`, `pip`, and launcher-based setup unreliable.

This confirms an interpreter/binary mismatch. The available evidence does not
establish how the incompatible files originally entered that environment.

## Repairs

- Rebuilt `.venv` from the official Python **3.12.10 x64** NuGet runtime in
  `.runtime/python31210/tools/`. The setup script preserved the broken environment
  in `.venv-backup-20261019-232010-868`.
- Added `scripts/setup.ps1`: checks the selected Python version/architecture,
  prevents reuse of an existing environment without an explicit recreation flag,
  backs it up, installs binary wheels using the environment's own interpreter,
  runs `pip check`, and diagnoses the complete installation. No global package
  installation, activation script, PATH changes, or administrator access is needed.
- Kept **every package version unchanged**. `requirements.txt` now constrains
  transitive dependencies with the complete lock. Both installation paths were
  exercised in independent clean Python 3.12.10 environments: the full lock,
  then the direct requirements plus lock constraints.
- Added `src.doctor`: checks all 52 locked versions, `Requires-Python`, wheel
  tags, interpreter isolation, local package names, import locations, environment
  overrides, native imports, and predictions from both saved models.
- Added explicit VS Code interpreter/test defaults and `.python-version`.
- Restricted pytest discovery to this project's `tests/`. The preserved nested
  distribution contains another `tests/test_project.py` that otherwise risks
  duplicate module collection and tests against the old application copy.
- Added shared model loading with hash, input-schema, and numerical-package
  compatibility checks before model deserialization. Streamlit's cache signature
  includes the model files themselves, so replacing or corrupting a model can no
  longer bypass integrity validation through an unchanged metadata cache key.
- Fixed input validation to reject duplicate columns and boolean numeric values,
  normalize numeric strings into actual numbers, and retain the missing-value
  option used by preprocessing without mutating the caller's data.
- Made incomplete dataset archives fail before extraction writes any files.
- Training now writes its environment snapshot to `results/environment-freeze.txt`
  instead of overwriting `requirements-lock.txt`. Added `--output-dir` for isolated
  experiment replays.
- Preserved the exact original training sources in `models/training-source/`.
  Verification authenticates the historical source bytes and reports repaired
  source differences separately, while recomputing scientific checks using the
  current implementation. Original metadata and model hashes remain unchanged.
  `--strict-source` correctly rejects the changed current sources.
- Expanded the README with setup, explicit interpreter commands, dependency policy,
  troubleshooting, retraining, provenance, and duplicate-project guidance.

## Executed validation

| Check | Result |
|---|---|
| Install all 52 locked packages using only Windows-compatible wheels | Passed |
| Run setup script against the broken default `.venv` | Passed; old environment backed up |
| Install direct requirements constrained by the lock | Passed; identical dependency versions |
| `.venv\Scripts\python.exe -m pip check` | No broken requirements |
| `.venv\Scripts\python.exe -m src.doctor` | **170/170 checks passed** |
| Automated tests, including both full Streamlit assessment flows | **24 passed** |
| Saved experiment verification | **11 audit groups passed** |
| Complete training replay | **380 CV fits**, both models refitted and evaluated |
| Replayed metrics versus supplied metrics | Exactly equal |
| Replayed Logistic Regression and Decision Tree files | Both byte-identical to supplied files |
| Streamlit server health endpoint and application HTML | Both HTTP **200** |
| Python source compilation and notebook code-cell compilation | Passed |
| Original artifact preservation checks | **119 files unchanged** |
| Strict historical source comparison | Correctly rejects repaired source differences |

The 119 preservation checks include the original models/metadata, data, notebooks,
research metrics, CSVs, plots, reports, archives, and nested project distribution.
The regenerated `results/verification.json` records the current audit; historical
`results/tests.xml`, UI baseline and UI review were retained.

One expected pytest warning explains that the current source differs from the
historical training run and points to its authenticated source snapshot. It is not
a dependency, prediction, or UI failure.

The command sandbox's default temporary directory could not support pytest's
temporary fixtures, so the recorded test execution used project-local temporary
directories. Its sandbox also prevented the child Streamlit server from becoming
ready; the HTTP check passed when executed outside that sandbox. Neither workaround
requires changing application code or Windows system settings. The final test run
used this equivalent command with `TEMP`/`TMP` set to `.diagnostics/temp`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.diagnostics\pytest-final --junitxml=results\repair-tests.xml
```

## Evidence

- `environment-check.json`: actual interpreter, module locations, every package
  requirement/wheel tag and all 170 environment checks.
- `dependency-compatibility.csv`: all 52 locked packages and Python compatibility.
- `repair-tests.xml`: new automated test results; `tests.xml` is historical.
- `verification.json`: scientific audit and current-versus-training source changes.
- `streamlit-smoke.json` and `streamlit-smoke.log`: real localhost server checks.
- `repair-preservation.json`: original artifact hashes, replay equality, and the
  official runtime package URL/SHA-256.
- `.diagnostics/pipeline-replay/`: complete separately generated models/results.

The research architecture, 30 non-grade features, target, split, seed, tuning grids,
F2 selection, threshold, existing UI styling, and historical findings are preserved.
The project still has its documented small-cohort, timing, calibration, and external
validation limitations. Optional Jupyter installation and browser-based notebook
execution were not required for, or included in, this repair.

References: [NumPy import troubleshooting](https://numpy.org/doc/stable/user/troubleshooting-importerror.html),
[Python virtual environment documentation](https://docs.python.org/3.12/library/venv.html),
and [scikit-learn model persistence guidance](https://scikit-learn.org/1.7/model_persistence.html).

## Launch the repaired project

From this project root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Keep `.runtime/python31210/` in place while this environment uses it. To switch
to your installed Python later, recreate the environment with the README's explicit
`-PythonExe` setup command. The nested `student-academic-risk-project/` remains an
unchanged distribution copy and does not include these repairs.
