import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import fbeta_score, make_scorer, precision_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .config import SEED
from .preprocessing import make_preprocessor

SCORING = {
    "accuracy": "accuracy", "precision": make_scorer(precision_score, zero_division=0),
    "recall": "recall", "f1": "f1", "f2": make_scorer(fbeta_score, beta=2, zero_division=0),
    "roc_auc": "roc_auc", "average_precision": "average_precision",
}


def refit_index(results):
    """Maximize mean CV F2; deterministic ties prefer recall, then ROC-AUC."""
    return int(max(range(len(results["params"])), key=lambda i: (
        results["mean_test_f2"][i], results["mean_test_recall"][i],
        results["mean_test_roc_auc"][i], -i)))


def model_specs():
    return {
        "logistic_regression": (
            Pipeline([("preprocess", make_preprocessor(True)),
                      ("classifier", LogisticRegression(solver="liblinear", max_iter=5000, random_state=SEED))]),
            {"classifier__C": [0.01, 0.1, 1.0, 10.0], "classifier__penalty": ["l1", "l2"],
             "classifier__class_weight": [None, "balanced"]}),
        "decision_tree": (
            Pipeline([("preprocess", make_preprocessor(False)),
                      ("classifier", DecisionTreeClassifier(random_state=SEED))]),
            {"classifier__criterion": ["gini", "entropy"], "classifier__max_depth": [2, 3, 4, 5, 6],
             "classifier__min_samples_leaf": [5, 10, 20], "classifier__class_weight": [None, "balanced"]}),
    }


def inspect_imbalance(y_train):
    counts = y_train.value_counts().sort_index()
    ratio = float(counts.max() / counts.min())
    return {"training_counts": {str(k): int(v) for k, v in counts.items()},
            "majority_to_minority_ratio": ratio,
            "decision": "Compare no weighting with balanced weights inside training CV; no SMOTE.",
            "reason": "Both training classes have enough examples for five folds. Weighting is a simple option; "
                      "synthetic oversampling is unnecessary for this small, mixed categorical/ordinal dataset."}


def tune_models(X_train, y_train, results_dir):
    imbalance = inspect_imbalance(y_train)
    print(f"Training class counts: {imbalance['training_counts']}; ratio={imbalance['majority_to_minority_ratio']:.3f}", flush=True)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_records = []
    for fold, (train, validation) in enumerate(cv.split(X_train, y_train), start=1):
        fold_records.append({"fold": fold, "fit_row_ids": X_train.iloc[train].index.tolist(),
                             "validation_row_ids": X_train.iloc[validation].index.tolist()})
    estimators, summaries = {}, {}
    for name, (pipeline, grid) in model_specs().items():
        print(f"Tuning {name} using training-only stratified CV...", flush=True)
        search = GridSearchCV(pipeline, grid, scoring=SCORING, refit=refit_index,
                              cv=cv, n_jobs=1, return_train_score=False, error_score="raise")
        search.fit(X_train, y_train)
        pd.DataFrame(search.cv_results_).to_csv(results_dir / f"{name}_cv_results.csv", index=False)
        chosen = search.best_index_
        summary = {"best_params": search.best_params_, "best_index": chosen,
                   "candidates": len(search.cv_results_["params"]),
                   "cv_scores": {metric: {"mean": float(search.cv_results_[f"mean_test_{metric}"][chosen]),
                                           "std": float(search.cv_results_[f"std_test_{metric}"][chosen]),
                                           "folds": [float(search.cv_results_[f"split{k}_test_{metric}"][chosen]) for k in range(5)]}
                                 for metric in SCORING}}
        estimators[name] = search.best_estimator_
        summaries[name] = summary
        print(f"{name}: CV F2={summary['cv_scores']['f2']['mean']:.4f}; {search.best_params_}", flush=True)
    selected = max(summaries, key=lambda name: (
        summaries[name]["cv_scores"]["f2"]["mean"],
        summaries[name]["cv_scores"]["recall"]["mean"],
        summaries[name]["cv_scores"]["roc_auc"]["mean"]))
    return estimators, summaries, selected, imbalance, fold_records
