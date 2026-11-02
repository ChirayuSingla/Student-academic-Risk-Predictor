# Retrospective Student Academic Risk Classification Using Interpretable Machine Learning

This report is generated from an executed experiment, not manually entered scores.
Run timestamp (UTC): 2026-10-11T11:08:12.131674+00:00. Run ID: `daf3b3a9-f0eb-4190-b811-7364bf8d80f7`.

## Dataset and research context

The primary dataset is the real UCI `student-mat.csv`, verified byte-for-byte against the official UCI download. It contains
395 students and 33 original columns from two Portuguese secondary schools.
No synthetic records were generated; `student-por.csv` is retained as source material only.
CSV SHA-256: `e47f9ee225e1ee6e69b7564e6dac7123e80b8486677fe111f351964cef5dec80`. No rows were removed or deduplicated.
The At Risk target is **G3 < 10**, encoded 1; Not At Risk is **G3 >= 10**, encoded 0.
Full class counts: {'0': 265, '1': 130}. Training counts:
{'0': 212, '1': 104}; majority/minority ratio 2.038.

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

- **categorical/binary:** school, sex, address, famsize, Pstatus, Mjob, Fjob, reason, guardian, schoolsup, famsup, paid, activities, nursery, higher, internet, romantic
- **numeric/ordinal:** age, Medu, Fedu, traveltime, studytime, failures, famrel, freetime, goout, Dalc, Walc, health, absences

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

Stratified 80/20 split, `random_state=42`: **316 training** and
**79 test** students. Both models use the same split.
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

- **logistic_regression:** `{'classifier__C': 1.0, 'classifier__class_weight': 'balanced', 'classifier__penalty': 'l2'}`. Mean training CV F2 0.5101, recall 0.5300.
- **decision_tree:** `{'classifier__class_weight': 'balanced', 'classifier__criterion': 'entropy', 'classifier__max_depth': 5, 'classifier__min_samples_leaf': 20}`. Mean training CV F2 0.5375, recall 0.5781.

Default application model: **decision_tree**, chosen by training CV F2.
CV scores used for tuning are optimistic selection estimates, not an independent evaluation.

## Actual held-out results

Precision, recall, F1 and F2 below refer to **At Risk (positive class 1)**. ROC-AUC and AP
use the probability assigned to class 1; AP is average precision, not trapezoidal PR area.
Metrics for both classes, support counts, confusion matrices, Brier scores and specificity
are saved in `metrics.json`. Baselines were fitted on training rows and executed on test.

| Model | Accuracy | At Risk precision | At Risk recall | At Risk F1 | At Risk F2 | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.6709 | 0.5000 | 0.6923 | 0.5806 | 0.6429 | 0.7438 | 0.5985 |
| decision_tree | 0.6203 | 0.4500 | 0.6923 | 0.5455 | 0.6250 | 0.6930 | 0.5688 |
| dummy_majority | 0.6709 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.3291 |
| dummy_always_at_risk | 0.3291 | 0.3291 | 1.0000 | 0.4952 | 0.7104 | 0.5000 | 0.3291 |

Confusion matrix rows are actual [Not At Risk, At Risk]; columns are predicted in the same order.

- **logistic_regression:** TN=35, FP=18, FN=8, TP=18; identified 18 of 26 At Risk students and missed 8. At Risk recall 95% Wilson interval [0.500, 0.835]. Brier score 0.2072.
- **decision_tree:** TN=31, FP=22, FN=8, TP=18; identified 18 of 26 At Risk students and missed 8. At Risk recall 95% Wilson interval [0.500, 0.835]. Brier score 0.2164.

The always-At-Risk baseline shows the cost of achieving recall=1 by flagging everyone.
logistic_regression does not exceed the always-At-Risk baseline on test F2. decision_tree does not exceed the always-At-Risk baseline on test F2. Higher precision and ranking performance do not establish superiority
on this recall-weighted objective. The original training-only model selection remains fixed;
test findings do not change hyperparameters, threshold, or the application default.
The majority-class baseline shows why accuracy alone is insufficient. The test cohort is small;
Wilson intervals quantify binomial sampling uncertainty in recall, not population transfer or
model-selection uncertainty. Neither model is established as suitable for deployment.

## Interpretation

Largest absolute fitted Logistic Regression coefficients (log-odds units): `categorical__reason_other` (-0.729); `categorical__schoolsup_yes` (+0.719); `numeric__failures` (+0.618); `categorical__Mjob_teacher` (+0.555); `categorical__higher_yes` (-0.502).
Positive coefficients increase the model's At Risk log-odds, conditional on its other inputs;
negative coefficients decrease it. Numeric coefficients are per training standard deviation;
categorical coefficients compare with the saved omitted reference category. Coefficients from
regularized models and correlated inputs are not causal effects or significance tests.

Largest nonzero tree feature importances: `failures` (0.362); `absences` (0.265); `Mjob` (0.138); `Medu` (0.096); `schoolsup` (0.085).
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
records the exact executed environment; Python version: 3.12.14.
`models/` contains both full joblib pipelines, individual metadata, and shared metadata.
`results/` contains CV searches, held-out row-level predictions, metrics, audits, tree rules,
coefficient/importance tables, this report, and PNG/SVG figures. `notebooks/` contains an
optional exploration notebook that reads the executed artifacts; it is not required for training.

Dataset citation: Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning
Repository. [DOI: 10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T).
Dataset license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Source documentation: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance).
