import io
import json
import shutil
import zipfile

import numpy as np
import pandas as pd
import pytest

from src.acquire_data import FILES, dataset_members
from src.artifacts import artifact_signature, load_artifacts
from src.config import ROOT
from src.data import load_data, validate_inputs
from src.doctor import locked_packages


def test_direct_dependencies_are_locked():
    locked = {name.lower(): value for name, value in locked_packages().items()}
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line and not line.startswith("#"):
            name, version = line.split("==")
            assert locked[name.lower()] == version


def test_numeric_strings_are_normalized_without_mutating_input():
    _, X, _ = load_data()
    row = X.iloc[[0]].copy()
    row["age"] = row.age.astype(str)
    result = validate_inputs(row)
    assert pd.api.types.is_numeric_dtype(result.age)
    assert isinstance(row.age.iloc[0], str)


@pytest.mark.parametrize("value", [True, np.inf, -np.inf, 17.5, 99, "not numeric", None])
def test_invalid_numeric_inputs(value):
    _, X, _ = load_data()
    row = X.iloc[[0]].astype({"age": object})
    row.loc[:, "age"] = value
    with pytest.raises(ValueError):
        validate_inputs(row)


def test_duplicate_columns_rejected():
    _, X, _ = load_data()
    row = pd.concat([X.iloc[[0]], X.iloc[[0]][["age"]]], axis=1)
    with pytest.raises(ValueError, match="exactly"):
        validate_inputs(row)


def test_missing_values_allowed_only_for_preprocessing():
    _, X, _ = load_data()
    row = X.iloc[[0]].astype({"age": float})
    row.loc[:, "age"] = np.nan
    assert validate_inputs(row, allow_missing=True).age.isna().all()


@pytest.fixture
def artifact_copy(tmp_path):
    shutil.copytree(ROOT / "models", tmp_path / "models")
    return tmp_path


def test_model_changes_invalidate_cache_and_are_rejected(artifact_copy):
    before = artifact_signature(artifact_copy)
    path = artifact_copy / "models/decision_tree.joblib"
    path.write_bytes(path.read_bytes() + b"tampered")
    assert artifact_signature(artifact_copy) != before
    with pytest.raises(ValueError, match="integrity"):
        load_artifacts(artifact_copy)


def test_wrong_sklearn_version_has_actionable_error(artifact_copy):
    path = artifact_copy / "models/metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["environment"]["packages"]["scikit-learn"] = "0.0.0"
    path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="scikit-learn==0.0.0"):
        load_artifacts(artifact_copy)


def test_missing_model_file(artifact_copy):
    (artifact_copy / "models/decision_tree.joblib").unlink()
    with pytest.raises(FileNotFoundError):
        load_artifacts(artifact_copy)


def test_original_nested_archive_preserves_dataset_bytes():
    members = dataset_members((ROOT / "student+performance.zip").read_bytes())
    assert set(members) == set(FILES)
    for name, content in members.items():
        assert content == (ROOT / "data" / name).read_bytes()


def test_partial_archive_fails_before_extraction():
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("student-mat.csv", b"incomplete")
    with pytest.raises(ValueError, match="incomplete"):
        dataset_members(payload.getvalue())
