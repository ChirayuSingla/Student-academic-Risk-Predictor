from pathlib import Path
import pandas as pd


def generate_report(metadata, metrics, results_dir):
    rows = []
    for name, result in metrics.items():
        rows.append(f"| {name} | " + " | ".join(f"{result[key]:.4f}" for key in
                    ["accuracy", "precision", "recall", "f1", "f2", "roc_auc", "average_precision"]) + " |")
    table = "\n".join(rows)
    feature_text = "\n".join(f"- **{key}:** {', '.join(value)}" for key, value in
                             metadata["feature_groups"].items())
    params = "\n".join(f"- **{name}:** `{info['best_params']}`. Mean training CV F2 "
                         f"{info['cv_scores']['f2']['mean']:.4f}, recall "
                         f"{info['cv_scores']['recall']['mean']:.4f}."
                         for name, info in metadata["tuning"].items())
    details = []
    for name in metadata["tuning"]:
        m = metrics[name]
        tn, fp = m["confusion_matrix"][0]
        fn, tp = m["confusion_matrix"][1]
        low, high = m["at_risk"]["recall_95pct_wilson_interval"]
        details.append(f"- **{name}:** TN={tn}, FP={fp}, FN={fn}, TP={tp}; identified {tp} of {tp+fn} "
                       f"At Risk students and missed {fn}. At Risk recall 95% Wilson interval "
                       f"[{low:.3f}, {high:.3f}]. Brier score {m['brier_score']:.4f}.")
    coefficients = pd.read_csv(results_dir / "logistic_regression_coefficients.csv")
    top_coefficients = coefficients.loc[coefficients.coefficient_log_odds.abs().nlargest(5).index]
    coefficients_text = "; ".join(f"`{r.transformed_feature}` ({r.coefficient_log_odds:+.3f})"
                                  for r in top_coefficients.itertuples())
    importance = pd.read_csv(results_dir / "decision_tree_feature_importances.csv")
    importance_text = "; ".join(f"`{r.raw_feature}` ({r.impurity_importance:.3f})"
                               for r in importance.head(5).itertuples() if r.impurity_importance > 0)
    baseline_comparison = " ".join(
        f"{name} {'does not exceed' if metrics[name]['f2'] <= metrics['dummy_always_at_risk']['f2'] else 'exceeds'} "
        "the always-At-Risk baseline on test F2."
        for name in metadata["tuning"])
    caveat = "verified byte-for-byte against the official UCI download" if metadata["provenance"]["official_contents_verified"] else "extracted from the user-supplied UCI archive (official byte comparison not performed)"
    report = f"""# Retrospective Student Academic Risk Classification Using Interpretable Machine Learning

This report is generated from an executed experiment, not manually entered scores.
Run timestamp (UTC): {metadata['run_timestamp_utc']}. Run ID: `{metadata['run_id']}`.

## Dataset and research context

The primary dataset is the real UCI `student-mat.csv`, {caveat}. It contains
{metadata['dataset']['rows']} students and 33 original columns from two Portuguese secondary schools.
No synthetic records were generated; `student-por.csv` is retained as source material only.
CSV SHA-256: `{metadata['dataset']['sha256']}`. No rows were removed or deduplicated.
The At Risk target is **G3 < 10**, encoded 1; Not At Risk is **G3 >= 10**, encoded 0.
Full class counts: {metadata['dataset']['class_counts']}. Training counts:
{metadata['imbalance']['training_counts']}; majority/minority ratio {metadata['imbalance']['majority_to_minority_ratio']:.3f}.

Conceptual inspiration: Ewais, A., Arram, A., Diab, S., et al. (2026),
[Using machine learning for early identification of At-risk students](https://doi.org/10.1038/s41598-026-48426-1),
*Scientific Reports*, 16, 19944. The publisher lists Ahmed Ewais as first author (the supplied
initial “E.” is corrected here). Its institutional dataset is available by reasonable request,
not as a public download. This project does **not** use it or reproduce its experiments.
The paper uses regression; this work instead uses binary Logistic Regression and Decision Tree
classification on UCI, with grade exclusion and training-only preprocessing/tuning.
Its reported regression scores are not comparable to our classification metrics.

## Features and preprocessing

All 30 non-grade columns are selected a priori; no feature selection uses test outcomes.

{feature_text}

Excluded: **G1, G2, G3**. G3 creates the label only; G1/G2 are prior-period grades intentionally
withheld to support prediction without current-course grade signals. `failures` describes past
class failures, not G1/G2. The UCI documentation's failures description mentions code 4;
the supplied mathematics data has observed codes 0–3. Original observed codes are preserved.

Nominal and binary features are one-hot encoded with one training-derived reference level
dropped per feature (`handle_unknown='ignore'`). Numeric/ordinal features use median imputation;
Logistic Regression additionally standardizes using training mean/SD, whereas the tree does not.
Categorical imputation uses the training mode. There are no missing values in the original CSV,
so imputation is a defensive pipeline step. Ordinal codes are treated numerically, imposing a
linear step assumption for Logistic Regression. Reference levels and coefficients are saved.

## Experimental protocol

Stratified 80/20 split, `random_state=42`: **{metadata['split']['train_size']} training** and
**{metadata['split']['test_size']} test** students. Both models use the same split.
Five-fold shuffled stratified CV (`random_state=42`) is performed on training rows only.
Each CV fit clones and fits the complete pipeline, including preprocessing, on its fold's
training portion. Hyperparameters and the app's default model are chosen before test evaluation.
The chosen pipelines are refitted only on the full training partition and saved without
retraining on the test partition. Split row IDs and CV fold row IDs are saved for auditing.

The predeclared selection objective is mean CV **F2**; exact ties favor recall, then ROC-AUC.
F2 weights recall four times as much as precision in its harmonic formulation, emphasizing
missed At Risk students while avoiding recall-only selection of an indiscriminate classifier.
Threshold is fixed at **0.5** throughout; neither threshold nor class weighting is tuned on test.
All CV candidates and seven scoring metrics are saved in CSVs.

The class distribution was inspected before tuning. Balanced class weighting and no weighting
are compared in CV. No SMOTE or other synthetic sampling is used. Balanced weights, when
selected, are recomputed by the estimator on each fold's training rows.

Search spaces:

- Logistic Regression: C in [0.01, 0.1, 1, 10], penalty in [l1, l2],
  class_weight in [None, balanced]; liblinear solver, max_iter=5000, random_state=42 (16 candidates).
- Decision Tree: criterion in [gini, entropy], max_depth in [2, 3, 4, 5, 6],
  min_samples_leaf in [5, 10, 20], class_weight in [None, balanced], random_state=42 (60 candidates).

Selected hyperparameters:

{params}

Default application model: **{metadata['selected_model']}**, chosen by training CV F2.
CV scores used for tuning are optimistic selection estimates, not an independent evaluation.

## Actual held-out results

Precision, recall, F1 and F2 below refer to **At Risk (positive class 1)**. ROC-AUC and AP
use the probability assigned to class 1; AP is average precision, not trapezoidal PR area.
Metrics for both classes, support counts, confusion matrices, Brier scores and specificity
are saved in `metrics.json`. Baselines were fitted on training rows and executed on test.

| Model | Accuracy | At Risk precision | At Risk recall | At Risk F1 | At Risk F2 | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|---:|
{table}

Confusion matrix rows are actual [Not At Risk, At Risk]; columns are predicted in the same order.

{chr(10).join(details)}

The always-At-Risk baseline shows the cost of achieving recall=1 by flagging everyone.
{baseline_comparison} Higher precision and ranking performance do not establish superiority
on this recall-weighted objective. The original training-only model selection remains fixed;
test findings do not change hyperparameters, threshold, or the application default.
The majority-class baseline shows why accuracy alone is insufficient. The test cohort is small;
Wilson intervals quantify binomial sampling uncertainty in recall, not population transfer or
model-selection uncertainty. Neither model is established as suitable for deployment.

## Interpretation

Largest absolute fitted Logistic Regression coefficients (log-odds units): {coefficients_text}.
Positive coefficients increase the model's At Risk log-odds, conditional on its other inputs;
negative coefficients decrease it. Numeric coefficients are per training standard deviation;
categorical coefficients compare with the saved omitted reference category. Coefficients from
regularized models and correlated inputs are not causal effects or significance tests.

Largest nonzero tree feature importances: {importance_text}.
These are training impurity reductions, summed over one-hot levels. Such importance can favor
features with more possible splits and does not indicate causation. The full tree and text rules
are saved. The app shows the exact decision path for a student.
For Logistic Regression, it shows exact grouped log-odds contributions relative to the mean
transformed training profile; contributions plus reference log-odds reconstruct its decision
function. That reference profile is a mathematical average, not an actual student.

## Limitations and responsible use

- Excluding G1/G2/G3 prevents direct grade leakage. UCI does not provide per-feature timestamps:
  total `absences` and potentially other attributes may span the school year. This is a retrospective,
  retrospective grade-free classification **prototype**, not verified beginning-of-term prediction. Prospectively
  validate inputs frozen at a defined cutoff (or exclude unavailable fields) before operational use.
- One small, historical, two-school mathematics cohort cannot establish generalization to other
  schools, countries, subjects, or present-day populations. Random splitting is not temporal or
  institution-held-out validation. This experiment makes no claim to replicate the base paper.
- Sex, family circumstances, health and alcohol variables can be sensitive or act as socioeconomic
  proxies. Subgroup fairness, consent, access controls and local policies need assessment before use.
- Probabilities are model estimates and have not been calibrated. Class weighting changes fitted
  probabilities; a percentage must not be treated as a verified individual likelihood.
- School support can reflect help given to already struggling students (confounding/reverse
  association). Correlation, coefficients, and split importance do not show which interventions work.
- Unknown categories are encoded as the dropped baseline at pipeline level; the app rejects invalid
  UCI codes and flags values outside training support. It does not accept G1, G2 or G3.
- Research prototype only; predictions must not be the sole basis for academic decisions or sanctions.

## Reproducibility and deliverables

Run `python -m src.run_pipeline` from the project root after installing `requirements.txt`.
Run `python -m src.verify` to recompute stored test metrics from saved models and audit feature
exclusion, split/fold isolation, numeric preprocessing statistics and artifact hashes.
Run `python -m pytest -q` for leakage and Streamlit integration checks. `requirements-lock.txt`
records the exact executed environment; Python version: {metadata['environment']['python']}.
`models/` contains both full joblib pipelines, individual metadata, and shared metadata.
`results/` contains CV searches, held-out row-level predictions, metrics, audits, tree rules,
coefficient/importance tables, this report, and PNG/SVG figures. `notebooks/` contains an
optional exploration notebook that reads the executed artifacts; it is not required for training.

Dataset citation: Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning
Repository. [DOI: 10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T).
Dataset license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Source documentation: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance).
"""
    (results_dir / "report.md").write_text(report, encoding="utf-8")
    summary = f"""# Experiment summary

**Retrospective Student Academic Risk Classification Using Interpretable Machine Learning**

**Data:** Original UCI mathematics CSV, 395 real students, 33 original columns;
At Risk = G3 < 10 (130 students), Not At Risk = G3 >= 10 (265 students).
The extracted source bytes were {caveat}. No synthetic data, SMOTE, or removed rows.

**Inputs:** 30 non-grade demographic, family, school, study, support, lifestyle and absence
features. G1/G2/G3 are excluded. Explicit selected lists and feature domains are in
`src/config.py`; the full methodology and feature lists are in `report.md`.
Numeric/ordinal columns use median imputation and, for Logistic Regression, training-only
standardization. Nominal/binary columns use mode imputation and one-hot encoding with
training-derived reference categories. The source data has no missing cells.

**Protocol:** Stratified 316/79 train-test split, seed 42. Five-fold shuffled stratified CV
on training only, seed 42, full pipelines inside GridSearchCV. Training imbalance is 212:104;
compare unweighted and balanced weights without oversampling. Select by mean CV F2
(emphasizes recall), ties by recall then ROC-AUC; hold classification threshold at 0.5.
No test preprocessing, tuning, threshold selection, or deployment refitting.

**Selected hyperparameters:**

{params}

**Actual held-out metrics:** All precision/recall/F1/F2 scores below refer to At Risk.

| Model | Accuracy | Precision | Recall | F1 | F2 | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|---:|
{table}

{chr(10).join(details)}

{baseline_comparison} The app default remains **{metadata['selected_model']}**, chosen
before test evaluation. These results do not establish deployment readiness.

**Interpretation:** Coefficients and impurity importance indicate fitted associations,
not causal effects. Saved coefficient references, full tree rules/visualization and exact
local model explanations make the estimates inspectable.

**Limitations:** Small historical two-school sample, uncalibrated probabilities and no
external, temporal or fairness validation. Feature timestamps are unavailable; total absences
may include late-year information. Grade exclusion alone cannot validate early availability.
This is a retrospective research prototype, never the sole basis for academic decisions.

**Reproduce:** Install `requirements.txt` (or exact `requirements-lock.txt`), then run
`python -m src.run_pipeline`, `python -m src.verify`, and `python -m pytest -q`.
Start the application with `python -m streamlit run app.py`. Dataset/model/source hashes,
split/fold row IDs, complete CV results, predictions, plots and metadata are saved.

Dataset: Cortez, P. (2008). *Student Performance*, UCI,
[DOI 10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T), CC BY 4.0.
Conceptual reference: Ewais, A., et al. (2026), *Scientific Reports*,
[DOI 10.1038/s41598-026-48426-1](https://doi.org/10.1038/s41598-026-48426-1).
Its separate institutional regression dataset was **not used**; this UCI binary classifier
is not a replication of that paper.
"""
    (results_dir / "summary.md").write_text(summary, encoding="utf-8")
