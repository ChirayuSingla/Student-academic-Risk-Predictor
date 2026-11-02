"""Audit saved artifacts and recompute all held-out metrics without tuning on test."""
import argparse
import json
import warnings
from importlib.metadata import version

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold

from .config import CATEGORICAL, DATA_PATH, EXCLUDED, FEATURES, NUMERIC, ROOT, SEED
from .artifacts import load_artifacts
from .data import load_data, split_data
from .evaluation import evaluate_predictions, positive_probability
from .explainability import logistic_local_explanation, tree_local_explanation
from .training import refit_index
from .utils import sha256, write_json


def compare_nested(actual, expected, path="metrics"):
    if isinstance(actual, dict):
        assert set(actual) == set(expected), path
        for key in actual:
            compare_nested(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(actual, list):
        assert len(actual) == len(expected), path
        for i, (a, e) in enumerate(zip(actual, expected)):
            compare_nested(a, e, f"{path}[{i}]")
    elif isinstance(actual, (float, int)):
        assert np.isclose(actual, expected, rtol=1e-10, atol=1e-12), path
    else:
        assert actual == expected, path


def verify(artifact_root=ROOT, strict_source=False):
    models, metadata = load_artifacts(artifact_root)
    stored_metrics = json.loads((artifact_root / "results" / "metrics.json").read_text(encoding="utf-8"))
    frame, X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    checks = {}
    assert sha256(DATA_PATH) == metadata["dataset"]["sha256"] == metadata["provenance"]["files"]["student-mat.csv"]["sha256"]
    assert frame.shape == (395, 33) and int(y.sum()) == 130
    checks["dataset_hash_and_real_mathematics_schema"] = True
    assert X.columns.tolist() == FEATURES and not set(EXCLUDED) & set(FEATURES)
    assert np.array_equal(y, (frame.G3 < 10).astype(int))
    checks["grade_exclusion_and_exact_target_definition"] = True
    assert X_train.index.tolist() == metadata["split"]["train_row_ids"]
    assert X_test.index.tolist() == metadata["split"]["test_row_ids"]
    train_ids, test_ids = set(X_train.index), set(X_test.index)
    assert not train_ids & test_ids and train_ids | test_ids == set(X.index)
    assert len(train_ids) == 316 and len(test_ids) == 79
    checks["reproduced_stratified_split_and_partition_isolation"] = True
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    validation_ids = []
    for record, (fit, validation) in zip(metadata["cv_folds"], cv.split(X_train, y_train)):
        assert record["fit_row_ids"] == X_train.iloc[fit].index.tolist()
        assert record["validation_row_ids"] == X_train.iloc[validation].index.tolist()
        fit_set, validation_set = set(record["fit_row_ids"]), set(record["validation_row_ids"])
        assert not fit_set & validation_set and fit_set | validation_set == train_ids
        assert not (fit_set | validation_set) & test_ids
        assert set(y.loc[list(fit_set)].unique()) == {0, 1}
        assert set(y.loc[list(validation_set)].unique()) == {0, 1}
        validation_ids.extend(record["validation_row_ids"])
    assert sorted(validation_ids) == sorted(train_ids)
    checks["five_training_only_stratified_folds"] = True
    source_changes = []
    for relative, digest in metadata["source_sha256"].items():
        current = ROOT / relative
        if not current.exists() or sha256(current) != digest:
            source_changes.append(relative)
            archived = artifact_root / "models" / "training-source" / relative
            assert archived.exists() and sha256(archived) == digest, f"Training source unavailable or altered: {relative}"
    if strict_source:
        assert not source_changes, f"Current source changed after training: {source_changes}"
    if source_changes:
        warnings.warn("Current source differs from the original training run; authenticated training sources "
                      "are preserved in models/training-source. See verification.json for changed files.", stacklevel=2)
    checks["training_source_provenance_verified"] = True
    for package, expected in metadata["environment"]["packages"].items():
        assert version(package) == expected, f"Package version mismatch: {package}"
    checks["executed_dependency_versions_match"] = True
    for name, digest in metadata["model_sha256"].items():
        path = artifact_root / "models" / f"{name}.joblib"
        assert sha256(path) == digest
        model = models[name]
        assert model.feature_names_in_.tolist() == FEATURES
        preprocess = model.named_steps["preprocess"]
        assert preprocess.feature_names_in_.tolist() == FEATURES
        assert all(not any(part in feature.split("__")[-1].split("_") for part in EXCLUDED)
                   for feature in preprocess.get_feature_names_out())
        numeric = preprocess.named_transformers_["numeric"]
        np.testing.assert_allclose(numeric.named_steps["impute"].statistics_, X_train[NUMERIC].median())
        categorical = preprocess.named_transformers_["categorical"]
        encoder = categorical.named_steps["onehot"]
        for feature, categories, mode in zip(CATEGORICAL, encoder.categories_, categorical.named_steps["impute"].statistics_):
            assert categories.tolist() == sorted(X_train[feature].unique().tolist())
            assert mode in X_train[feature].mode().tolist()
        if name == "logistic_regression":
            scaler = numeric.named_steps["scale"]
            np.testing.assert_allclose(scaler.mean_, X_train[NUMERIC].mean())
            np.testing.assert_allclose(scaler.var_, X_train[NUMERIC].var(ddof=0))
            assert scaler.n_samples_seen_ == len(X_train)
            # Replay just fold preprocessors on actual fold fit rows; compare training statistics.
            for fold in metadata["cv_folds"]:
                fold_X = X.loc[fold["fit_row_ids"]]
                replay = clone(preprocess).fit(fold_X)
                fold_scaler = replay.named_transformers_["numeric"].named_steps["scale"]
                np.testing.assert_allclose(fold_scaler.mean_, fold_X[NUMERIC].mean())
                assert fold_scaler.n_samples_seen_ == len(fold_X)
            for row_id in X_test.index:
                logistic_local_explanation(model, X_test.loc[[row_id]], metadata)
        else:
            assert model.named_steps["classifier"].tree_.n_node_samples[0] == len(X_train)
            for row_id in X_test.index:
                path_rows, samples = tree_local_explanation(model, X_test.loc[[row_id]])
                assert samples > 0
        probability = positive_probability(model, X_test)
        actual_metrics, prediction = evaluate_predictions(y_test, probability, metadata["threshold"])
        compare_nested(actual_metrics, stored_metrics[name], name)
        saved = pd.read_csv(artifact_root / "results" / f"{name}_test_predictions.csv")
        assert saved.row_id.tolist() == X_test.index.tolist()
        np.testing.assert_array_equal(saved.true_at_risk, y_test.to_numpy())
        np.testing.assert_array_equal(saved.predicted_at_risk, prediction)
        np.testing.assert_allclose(saved.probability_at_risk, probability, rtol=1e-12, atol=1e-14)
        csv = pd.read_csv(artifact_root / "results" / f"{name}_cv_results.csv")
        chosen = refit_index(csv)
        assert chosen == metadata["tuning"][name]["best_index"]
        for metric, score in metadata["tuning"][name]["cv_scores"].items():
            assert np.isclose(csv.loc[chosen, f"mean_test_{metric}"], score["mean"])
        checks[f"{name}_preprocessing_metrics_predictions_explanations_and_selection"] = True
    expected_selected = max(metadata["tuning"], key=lambda name: (
        metadata["tuning"][name]["cv_scores"]["f2"]["mean"],
        metadata["tuning"][name]["cv_scores"]["recall"]["mean"],
        metadata["tuning"][name]["cv_scores"]["roc_auc"]["mean"]))
    assert expected_selected == metadata["selected_model"]
    checks["default_model_selected_from_training_cv"] = True
    for name, baseline in {"dummy_majority": DummyClassifier(strategy="most_frequent"),
                           "dummy_always_at_risk": DummyClassifier(strategy="constant", constant=1)}.items():
        baseline.fit(X_train, y_train)
        metrics, _ = evaluate_predictions(y_test, positive_probability(baseline, X_test))
        compare_nested(metrics, stored_metrics[name], name)
    checks["baselines_recomputed"] = True
    expected_figures = ["class_distribution.png", "training_feature_distributions.png", "training_risk_associations.png",
                        "training_numeric_correlations.png", "logistic_regression_confusion_matrix.png",
                        "decision_tree_confusion_matrix.png", "roc_curves.png", "precision_recall_curves.png",
                        "logistic_regression_coefficients.png", "decision_tree_feature_importance.png", "decision_tree.png", "decision_tree.svg"]
    from PIL import Image
    for name in expected_figures:
        path = artifact_root / "results" / "figures" / name
        assert path.stat().st_size > 1000
        if name.endswith(".png"):
            with Image.open(path) as image:
                image.verify()
    checks["all_required_figures_present_and_images_valid"] = True
    write_json(artifact_root / "results" / "verification.json", {
        "status": "passed", "run_id": metadata["run_id"], "checks": checks,
        "current_source_matches_training": not source_changes, "changed_source_files": source_changes,
        "note": "Checks recompute test predictions/metrics without refitting models; fold preprocessing is replayed on training rows only."})
    print(f"Verification passed: {len(checks)} audit groups.", flush=True)
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-source", action="store_true", help="Also require current source to match the historical training run.")
    verify(strict_source=parser.parse_args().strict_source)
