import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, f1_score, fbeta_score, precision_score,
    recall_score, roc_auc_score, roc_curve, precision_recall_curve,
)

from .config import LABELS, THRESHOLD


def positive_probability(model, X):
    position = int(np.flatnonzero(model.classes_ == 1)[0])
    return model.predict_proba(X)[:, position]


def wilson_interval(successes, total):
    """95% Wilson interval for the finite test sample's binomial recall estimate."""
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z*z / total
    center = (p + z*z / (2*total)) / denominator
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return [max(0.0, center-half), min(1.0, center+half)]


def evaluate_predictions(y, probability, threshold=THRESHOLD):
    probability = np.asarray(probability)
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    report = classification_report(y, prediction, labels=[0, 1],
                                   target_names=[LABELS[0], LABELS[1]], output_dict=True, zero_division=0)
    metrics = {
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "f2": float(fbeta_score(y, prediction, beta=2, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probability)),
        "average_precision": float(average_precision_score(y, probability)),
        "brier_score": float(brier_score_loss(y, probability)),
        "specificity": float(tn / (tn+fp)), "threshold": threshold,
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "confusion_matrix_order": [LABELS[0], LABELS[1]],
        "at_risk": {**report["At Risk"], "support": int(tp+fn),
                    "true_positives": int(tp), "false_negatives": int(fn),
                    "recall_95pct_wilson_interval": wilson_interval(int(tp), int(tp+fn))},
        "classification_report": report,
    }
    return metrics, prediction


def evaluate_model(name, model, X_test, y_test, results_dir, figures_dir):
    probability = positive_probability(model, X_test)
    metrics, prediction = evaluate_predictions(y_test, probability)
    pd.DataFrame({"row_id": X_test.index, "true_at_risk": y_test.to_numpy(),
                  "probability_at_risk": probability, "predicted_at_risk": prediction}).to_csv(
        results_dir / f"{name}_test_predictions.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ConfusionMatrixDisplay(np.array(metrics["confusion_matrix"]),
                           display_labels=[LABELS[0], LABELS[1]]).plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"{name.replace('_', ' ').title()} · held-out test")
    fig.tight_layout()
    fig.savefig(figures_dir / f"{name}_confusion_matrix.png", dpi=170)
    plt.close(fig)
    return metrics, probability


def plot_curves(y_test, probabilities, figures_dir):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for name, probability in probabilities.items():
        fpr, tpr, _ = roc_curve(y_test, probability)
        ax.plot(fpr, tpr, label=f"{name.replace('_', ' ').title()} (AUC={roc_auc_score(y_test, probability):.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
    ax.set(xlabel="False positive rate", ylabel="At Risk recall", title="ROC curves · held-out test")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(figures_dir / "roc_curves.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for name, probability in probabilities.items():
        precision, recall, _ = precision_recall_curve(y_test, probability)
        ax.step(recall, precision, where="post", label=f"{name.replace('_', ' ').title()} (AP={average_precision_score(y_test, probability):.3f})")
    ax.axhline(float(y_test.mean()), linestyle="--", color="gray", label="Test prevalence")
    ax.set(xlabel="At Risk recall", ylabel="At Risk precision", ylim=(0, 1.05),
           title="Precision–recall curves · held-out test")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(figures_dir / "precision_recall_curves.png", dpi=170)
    plt.close(fig)
