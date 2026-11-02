import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_eda(frame, X_train, y_train, y_test, figures_dir):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    full_y = (frame.G3 < 10).astype(int)
    for ax, labels, title in zip(axes, [full_y, y_train, y_test], ["Full dataset", "Training", "Test"]):
        counts = labels.value_counts().reindex([0, 1], fill_value=0)
        bars = ax.bar(["Not At Risk", "At Risk"], counts, color=["#3784a6", "#c85250"])
        ax.bar_label(bars, padding=3)
        ax.set(title=title, ylabel="Students", ylim=(0, counts.max()*1.18))
    fig.suptitle("Class distribution · G3 < 10 defines At Risk")
    fig.tight_layout()
    fig.savefig(figures_dir / "class_distribution.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, name in zip(axes, ["age", "studytime", "absences"]):
        for label, color in [(0, "#3784a6"), (1, "#c85250")]:
            ax.hist(X_train.loc[y_train == label, name], bins=12 if name == "absences" else 8,
                    alpha=0.6, color=color, label="At Risk" if label else "Not At Risk")
        ax.set(title=name, ylabel="Training students", xlabel="Value / UCI code")
    axes[0].legend()
    fig.suptitle("Feature distributions · training data only")
    fig.tight_layout()
    fig.savefig(figures_dir / "training_feature_distributions.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    train = X_train.assign(at_risk=y_train)
    for ax, name in zip(axes, ["failures", "studytime"]):
        stats = train.groupby(name).at_risk.agg(["mean", "count"])
        bars = ax.bar(stats.index.astype(str), stats["mean"], color="#3784a6")
        ax.bar_label(bars, labels=[f"n={n}" for n in stats["count"]], padding=3)
        ax.set(title=name, ylabel="Observed At Risk fraction", xlabel="UCI code", ylim=(0, 1.15))
    fig.suptitle("Exploratory associations · training only · not causal")
    fig.tight_layout()
    fig.savefig(figures_dir / "training_risk_associations.png", dpi=170)
    plt.close(fig)
    numeric = train.select_dtypes(include="number").corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(numeric, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(numeric)), numeric.columns, rotation=65, ha="right")
    ax.set_yticks(range(len(numeric)), numeric.columns)
    ax.set_title("Pearson correlations of ordinal/numeric codes · training only")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(figures_dir / "training_numeric_correlations.png", dpi=170)
    plt.close(fig)
