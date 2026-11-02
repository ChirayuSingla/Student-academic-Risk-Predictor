import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.tree import export_text, plot_tree

from .config import CATEGORICAL, FEATURES, NUMERIC


def transformed_schema(model):
    preprocess = model.named_steps["preprocess"]
    encoder = preprocess.named_transformers_["categorical"].named_steps["onehot"]
    names = preprocess.get_feature_names_out().tolist()
    raw_features = NUMERIC.copy()
    references = {}
    for name, categories, drop in zip(CATEGORICAL, encoder.categories_, encoder.drop_idx_):
        references[name] = str(categories[int(drop)])
        raw_features.extend([name] * (len(categories)-1))
    if len(names) != len(raw_features):
        raise ValueError("Unexpected transformed feature schema.")
    return names, raw_features, references


def global_explanations(models, X_train, results_dir, figures_dir):
    info = {}
    for name, model in models.items():
        feature_names, raw_features, references = transformed_schema(model)
        classifier = model.named_steps["classifier"]
        if name == "logistic_regression":
            values = classifier.coef_[0]
            table = pd.DataFrame({"transformed_feature": feature_names, "raw_feature": raw_features,
                                  "coefficient_log_odds": values, "odds_ratio": np.exp(values)})
            table["reference_category"] = table.raw_feature.map(references).fillna("per training standard deviation")
            table.to_csv(results_dir / "logistic_regression_coefficients.csv", index=False)
            order = np.argsort(np.abs(values))[-20:]
            fig, ax = plt.subplots(figsize=(10, 7))
            ax.barh(np.array(feature_names)[order], values[order],
                    color=["#c85250" if v > 0 else "#3784a6" for v in values[order]])
            ax.axvline(0, color="black", linewidth=0.7)
            ax.set(xlabel="At Risk log-odds coefficient (numeric: per training SD)",
                   title="Logistic regression · 20 largest absolute coefficients")
            fig.tight_layout()
            fig.savefig(figures_dir / "logistic_regression_coefficients.png", dpi=170)
            plt.close(fig)
            transformed = model.named_steps["preprocess"].transform(X_train)
            mean = np.asarray(transformed).mean(axis=0)
            info[name] = {"feature_names": feature_names, "raw_features": raw_features,
                          "reference_categories": references, "training_transformed_mean": mean.tolist(),
                          "reference_log_odds": float(classifier.intercept_[0] + mean @ values)}
        else:
            values = classifier.feature_importances_
            table = pd.DataFrame({"transformed_feature": feature_names, "raw_feature": raw_features,
                                  "impurity_importance": values})
            table.to_csv(results_dir / "decision_tree_transformed_importances.csv", index=False)
            grouped = table.groupby("raw_feature").impurity_importance.sum().sort_values(ascending=False)
            grouped.to_csv(results_dir / "decision_tree_feature_importances.csv")
            fig, ax = plt.subplots(figsize=(9, 7))
            shown = grouped.head(20).sort_values()
            ax.barh(shown.index, shown.values, color="#3784a6")
            ax.set(xlabel="Summed impurity importance (one-hot levels grouped)",
                   title="Decision tree · feature importance (association only)")
            fig.tight_layout()
            fig.savefig(figures_dir / "decision_tree_feature_importance.png", dpi=170)
            plt.close(fig)
            leaves = classifier.get_n_leaves()
            fig, ax = plt.subplots(figsize=(max(18, leaves*1.7), max(10, classifier.get_depth()*2.4)))
            plot_tree(classifier, feature_names=feature_names, class_names=["Not At Risk", "At Risk"],
                      filled=True, rounded=True, precision=3, fontsize=9, ax=ax)
            ax.set_title("Full fitted decision tree · counts may be class-weighted", fontsize=15)
            fig.tight_layout()
            fig.savefig(figures_dir / "decision_tree.png", dpi=130)
            fig.savefig(figures_dir / "decision_tree.svg")
            plt.close(fig)
            (results_dir / "decision_tree_rules.txt").write_text(
                export_text(classifier, feature_names=feature_names, decimals=4, max_depth=20), encoding="utf-8")
            info[name] = {"feature_names": feature_names, "raw_features": raw_features,
                          "reference_categories": references, "depth": int(classifier.get_depth()), "leaves": int(leaves)}
    return info


def logistic_local_explanation(model, student, metadata):
    info = metadata["explainability"]["logistic_regression"]
    vector = np.asarray(model.named_steps["preprocess"].transform(student))[0]
    mean = np.asarray(info["training_transformed_mean"])
    contributions = (vector-mean) * model.named_steps["classifier"].coef_[0]
    table = pd.DataFrame({"feature": info["raw_features"], "log_odds_contribution": contributions})
    grouped = table.groupby("feature").log_odds_contribution.sum().reindex(FEATURES)
    reconstructed = info["reference_log_odds"] + grouped.sum()
    actual = float(model.decision_function(student)[0])
    if not np.isclose(reconstructed, actual):
        raise ValueError("Explanation does not reconstruct model log-odds.")
    return grouped.sort_values(key=abs, ascending=False), info["reference_log_odds"]


def tree_local_explanation(model, student):
    vector = np.asarray(model.named_steps["preprocess"].transform(student))[0]
    classifier = model.named_steps["classifier"]
    names = model.named_steps["preprocess"].get_feature_names_out()
    tree = classifier.tree_
    node = 0
    path = []
    while tree.children_left[node] != tree.children_right[node]:
        feature = int(tree.feature[node])
        value = float(vector[feature])
        threshold = float(tree.threshold[node])
        go_left = value <= threshold
        path.append({"feature": names[feature], "value": value,
                     "comparison": "≤" if go_left else ">", "threshold": threshold})
        node = tree.children_left[node] if go_left else tree.children_right[node]
    return path, int(tree.n_node_samples[node])
