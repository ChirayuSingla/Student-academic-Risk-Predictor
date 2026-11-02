# Experiment summary

**Retrospective Student Academic Risk Classification Using Interpretable Machine Learning**

**Data:** Original UCI mathematics CSV, 395 real students, 33 original columns;
At Risk = G3 < 10 (130 students), Not At Risk = G3 >= 10 (265 students).
The extracted source bytes were verified byte-for-byte against the official UCI download. No synthetic data, SMOTE, or removed rows.

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

- **logistic_regression:** `{'classifier__C': 1.0, 'classifier__class_weight': 'balanced', 'classifier__penalty': 'l2'}`. Mean training CV F2 0.5101, recall 0.5300.
- **decision_tree:** `{'classifier__class_weight': 'balanced', 'classifier__criterion': 'entropy', 'classifier__max_depth': 5, 'classifier__min_samples_leaf': 20}`. Mean training CV F2 0.5375, recall 0.5781.

**Actual held-out metrics:** All precision/recall/F1/F2 scores below refer to At Risk.

| Model | Accuracy | Precision | Recall | F1 | F2 | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.6709 | 0.5000 | 0.6923 | 0.5806 | 0.6429 | 0.7438 | 0.5985 |
| decision_tree | 0.6203 | 0.4500 | 0.6923 | 0.5455 | 0.6250 | 0.6930 | 0.5688 |
| dummy_majority | 0.6709 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.3291 |
| dummy_always_at_risk | 0.3291 | 0.3291 | 1.0000 | 0.4952 | 0.7104 | 0.5000 | 0.3291 |

- **logistic_regression:** TN=35, FP=18, FN=8, TP=18; identified 18 of 26 At Risk students and missed 8. At Risk recall 95% Wilson interval [0.500, 0.835]. Brier score 0.2072.
- **decision_tree:** TN=31, FP=22, FN=8, TP=18; identified 18 of 26 At Risk students and missed 8. At Risk recall 95% Wilson interval [0.500, 0.835]. Brier score 0.2164.

logistic_regression does not exceed the always-At-Risk baseline on test F2. decision_tree does not exceed the always-At-Risk baseline on test F2. The app default remains **decision_tree**, chosen
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
