"""Authenticate the supplied pipelines before deserializing them."""
import json
from importlib.metadata import version

import joblib

from .config import FEATURES, ROOT
from .utils import sha256

MODEL_NAMES = {"logistic_regression", "decision_tree"}


def artifact_signature(root=ROOT):
    """Include model bytes in the Streamlit cache key, not only metadata bytes."""
    directory = root / "models"
    return (sha256(directory / "metadata.json"),
            tuple((name, sha256(directory / f"{name}.joblib")) for name in sorted(MODEL_NAMES)))


def load_artifacts(root=ROOT):
    directory = root / "models"
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if set(metadata["model_sha256"]) != MODEL_NAMES or metadata["selected_model"] not in MODEL_NAMES:
        raise ValueError("Model metadata must describe both supported research pipelines.")
    if metadata["input_features"] != FEATURES:
        raise ValueError("Model metadata does not match the approved input features.")
    for package in ("numpy", "pandas", "scipy", "scikit-learn", "joblib"):
        expected = metadata["environment"]["packages"][package]
        if version(package) != expected:
            raise ValueError(f"Saved models require {package}=={expected}; found {version(package)}. "
                             "Install requirements.txt using the project virtual environment's Python.")
    # Check every file before loading either pickle. Only use artifacts from trusted sources.
    for name, expected in metadata["model_sha256"].items():
        if sha256(directory / f"{name}.joblib") != expected:
            raise ValueError(f"Saved model integrity check failed: {name}")
    models = {name: joblib.load(directory / f"{name}.joblib") for name in metadata["model_sha256"]}
    for name, model in models.items():
        if model.feature_names_in_.tolist() != FEATURES:
            raise ValueError(f"Saved model input schema mismatch: {name}")
    return models, metadata
