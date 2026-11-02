"""Execute the complete training-only selection and held-out evaluation workflow."""
import json
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from importlib.metadata import version

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier

from .config import CATEGORICAL, DATA_PATH, EXCLUDED, FEATURES, NUMERIC, ROOT, SEED, THRESHOLD
from .data import load_data, split_data
from .eda import plot_eda
from .evaluation import evaluate_model, evaluate_predictions, plot_curves, positive_probability
from .explainability import global_explanations
from .reporting import generate_report
from .training import tune_models
from .utils import sha256, write_json


def main():
    results_dir = ROOT / "results"
    figures_dir = results_dir / "figures"
    models_dir = ROOT / "models"
    for directory in [results_dir, figures_dir, models_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    provenance_path = ROOT / "data" / "provenance.json"
    if not provenance_path.exists():
        raise FileNotFoundError("Run python -m src.acquire_data first to record provenance.")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if sha256(DATA_PATH) != provenance["files"]["student-mat.csv"]["sha256"]:
        raise ValueError("Dataset hash differs from acquisition provenance.")
    frame, X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    models, tuning, selected, imbalance, folds = tune_models(X_train, y_train, results_dir)
    # Persist the training-only model selection before accessing test predictions.
    write_json(results_dir / "model_selection.json", {
        "selected_model": selected, "objective": "mean CV F2", "threshold": THRESHOLD,
        "source_partition": "training only", "tuning": tuning})
    explanations = global_explanations(models, X_train, results_dir, figures_dir)
    plot_eda(frame, X_train, y_train, y_test, figures_dir)
    metrics, probabilities = {}, {}
    for name, model in models.items():
        joblib.dump(model, models_dir / f"{name}.joblib", compress=3)
        metrics[name], probabilities[name] = evaluate_model(name, model, X_test, y_test, results_dir, figures_dir)
    for name, baseline in {
        "dummy_majority": DummyClassifier(strategy="most_frequent"),
        "dummy_always_at_risk": DummyClassifier(strategy="constant", constant=1),
    }.items():
        baseline.fit(X_train, y_train)
        metrics[name], _ = evaluate_predictions(y_test, positive_probability(baseline, X_test))
    plot_curves(y_test, probabilities, figures_dir)
    write_json(results_dir / "metrics.json", metrics)
    pd.DataFrame({name: {key: value for key, value in result.items() if isinstance(value, (int, float))}
                  for name, result in metrics.items()}).T.to_csv(results_dir / "metrics_summary.csv", index_label="model")
    split = {"train_size": len(X_train), "test_size": len(X_test),
             "train_row_ids": X_train.index.tolist(), "test_row_ids": X_test.index.tolist(),
             "test_class_counts": {str(k): int(v) for k, v in y_test.value_counts().sort_index().items()},
             "method": "stratified train_test_split, test_size=0.2, random_state=42"}
    defaults = {name: str(X_train[name].mode().iloc[0]) for name in CATEGORICAL}
    defaults.update({name: int(X_train[name].median()) for name in NUMERIC})
    metadata = {
        "project_title": "Early Detection of Student Academic Risk Using Machine Learning",
        "run_id": str(uuid.uuid4()), "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "target_definition": "1 if G3 < 10 else 0", "positive_class": "At Risk",
        "threshold": THRESHOLD, "input_features": FEATURES, "excluded_features": EXCLUDED,
        "feature_groups": {"categorical/binary": CATEGORICAL, "numeric/ordinal": NUMERIC},
        "dataset": {"file": "data/student-mat.csv", "rows": len(frame), "original_columns": len(frame.columns),
                    "sha256": sha256(DATA_PATH), "missing_cells": int(frame.isna().sum().sum()),
                    "duplicate_full_rows": int(frame.duplicated().sum()),
                    "duplicate_input_rows": int(X.duplicated().sum()),
                    "class_counts": {str(k): int(v) for k, v in y.value_counts().sort_index().items()}},
        "provenance": provenance, "split": split, "cv_folds": folds, "tuning": tuning,
        "imbalance": imbalance, "selected_model": selected, "explainability": explanations,
        "input_defaults": defaults,
        "training_numeric_ranges": {name: [int(X_train[name].min()), int(X_train[name].max())] for name in NUMERIC},
        "training_categories": {name: sorted(X_train[name].unique().tolist()) for name in CATEGORICAL},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "packages": {name: version(name) for name in ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "joblib", "streamlit", "pytest"]}},
        "model_sha256": {name: sha256(models_dir / f"{name}.joblib") for name in models},
        "source_sha256": {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path)
                          for path in sorted((ROOT / "src").glob("*.py")) + [ROOT / "app.py", ROOT / "requirements.txt"]},
        "limitations": ["Feature availability at an early cutoff is not established by UCI, especially total absences.",
                        "Small historical cohort; no external/temporal or fairness validation.",
                        "Uncalibrated model estimates; associations are not causal."],
    }
    write_json(models_dir / "metadata.json", metadata)
    for name in models:
        write_json(models_dir / f"{name}_metadata.json", {
            "model": name, "run_id": metadata["run_id"], "dataset_sha256": metadata["dataset"]["sha256"],
            "model_sha256": metadata["model_sha256"][name], "input_features": FEATURES,
            "excluded_features": EXCLUDED, "threshold": THRESHOLD, "tuning": tuning[name],
            "test_metrics": metrics[name], "fit_partition": "training only", "environment": metadata["environment"]})
    write_json(results_dir / "split_indices.json", split)
    write_json(results_dir / "cv_folds.json", folds)
    lock = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (ROOT / "requirements-lock.txt").write_text(lock, encoding="utf-8")
    generate_report(metadata, metrics, results_dir)
    print(pd.read_csv(results_dir / "metrics_summary.csv").to_string(index=False), flush=True)
    print(f"Complete. App default from training CV: {selected}", flush=True)
    from .verify import verify
    verify()


if __name__ == "__main__":
    main()
