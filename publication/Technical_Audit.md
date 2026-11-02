# Technical audit report

Review date: 1 November 2026. All nine original PDF pages and the available source, saved models, predictions, metadata, tests, and current interface were inspected. Severity denotes impact on claim validity; it is not a publication acceptance prediction.

## A01 Early detection title

Severity: Critical. Title implies a verified prediction cutoff; no predictor timestamps exist.

Action and evidence: Renamed retrospective classification; revised abstract, objectives and conclusion.

Residual requirement: Needs new timestamped cohort for prospective claim.

## A02 Absences availability

Severity: High. Aggregate absences may span the outcome period.

Action and evidence: Retuned no-absences models under the same nested folds.

Residual requirement: Other feature timestamps remain unknown.

## A03 Small holdout

Severity: High. Only 26 positive outcomes produce wide rate uncertainty.

Action and evidence: Wilson recall intervals and conditional paired bootstrap intervals added.

Residual requirement: Larger independent cohorts required.

## A04 Tuning optimism

Severity: High. Five-fold maximum scores reuse the folds that choose settings.

Action and evidence: Added 5-fold x 2-repeat outer validation with complete inner search on original training rows.

Residual requirement: Dependent folds are not independent cohorts.

## A05 Known holdout

Severity: High. Revision was designed after original test results were known.

Action and evidence: Extensions labeled exploratory; fixed original row IDs, no threshold/default replacement.

Residual requirement: Fresh validation remains necessary.

## A06 Objective baseline

Severity: High. Always-At-Risk exceeds both original models on test F2.

Action and evidence: Retained baseline; explicitly interpret precision, recall and workload.

Residual requirement: No institution-specific cost or capacity elicitation.

## A07 Historical rule baseline

Severity: Medium. Original study lacked a past-failure rule.

Action and evidence: Added failures > 0 rule without tuned cutoff.

Residual requirement: Timing of recorded history still requires confirmation.

## A08 Probability benchmark

Severity: Medium. Hard constant baselines are weak probability comparators.

Action and evidence: Added training prevalence constant for Brier comparison.

Residual requirement: Hard heuristic scores are not probabilities.

## A09 Model diversity

Severity: Medium. Two models alone do not test nonlinear ensemble behavior.

Action and evidence: Added bounded RF and GB searches using same partitions and scoring.

Residual requirement: Search budgets differ; no universal family ranking.

## A10 No calibration evidence

Severity: High. Brier and displayed percentages do not establish calibration.

Action and evidence: Added nested-search sigmoid calibration ensembles and fixed-bin reliability diagnostics.

Residual requirement: Small test bins; ensemble effect confounds pure recalibration effect.

## A11 Subgroup fairness

Severity: High. No sex, address or school error assessment existed.

Action and evidence: Added denominators, recall and FPR with Wilson intervals.

Residual requirement: No fairness certification, causal analysis or mitigation.

## A12 Sensitive predictors

Severity: Medium. Private, health and proxy inputs create use concerns.

Action and evidence: Retuned reduced 15-feature sensitivity scenario.

Residual requirement: Removal does not eliminate proxies or establish fairness.

## A13 Prior-failure dependence

Severity: Medium. Unclear whether other information adds predictive value.

Action and evidence: Added no-failures ablation and simple-rule comparison.

Residual requirement: No causal effect inferred.

## A14 Threshold selection

Severity: Medium. F2 search at 0.5 may hide workload trade-offs.

Action and evidence: Added descriptive 0.1-0.9 test sensitivity curves.

Residual requirement: No test-based threshold tuning; capacity study pending.

## A15 Paired uncertainty

Severity: Medium. Ranking differences had point estimates only.

Action and evidence: 2,000 paired stratified bootstraps; exact LR-DT McNemar test.

Residual requirement: Intervals condition on fixed models/prevalence, omit cluster/retraining uncertainty.

## A16 Fold independence

Severity: Medium. Repeated folds overlap in fit rows and students.

Action and evidence: Means and sample SD only; no naive fold-based significance test.

Residual requirement: External replication remains needed.

## A17 Importance bias

Severity: Medium. Training impurity can favor split-rich inputs.

Action and evidence: Added raw-feature AP permutation on outer validation folds.

Residual requirement: Correlation and out-of-distribution permutations remain limitations.

## A18 Explanation stability

Severity: Medium. One fitted coefficient/tree ranking is unstable on small data.

Action and evidence: Saved per-fold LR coefficients and validation permutation values.

Residual requirement: No causal or intervention interpretation.

## A19 Odds ratio units

Severity: Medium. Numeric and categorical coefficients have different units.

Action and evidence: Clarified per-training-SD effects and omitted categorical references.

Residual requirement: No conventional unpenalized inferential CI claimed.

## A20 Ordinal codes

Severity: Medium. LR treats ordinal steps as equally spaced.

Action and evidence: Preserved actual encoding and stated assumption.

Residual requirement: Alternative categorical/spline coding is a possible future study.

## A21 External validation

Severity: High. No independent school/cohort evaluation.

Action and evidence: Scope limited; public future benchmark suitability documented.

Residual requirement: Requires compatible independent data; not repairable with random resampling.

## A22 Temporal validation

Severity: High. Random split does not test future cohorts.

Action and evidence: Explained cutoff and cohort validation requirements; assessed OULAD compatibility.

Residual requirement: New temporal data needed; OULAD is a separate task.

## A23 School clustering

Severity: Medium. Shared school/class context may overstate independence.

Action and evidence: Reported assumptions; school subgroup counts retained.

Residual requirement: Only two schools and no class IDs; no cluster-robust inference claimed.

## A24 Zero grades

Severity: Medium. 38 zero grades may mix absence/withdrawal/achievement.

Action and evidence: Retained original target and explicitly reported ambiguity.

Residual requirement: Administrative meaning needs source confirmation.

## A25 Dataset identity

Severity: Medium. UCI summary has 649 language records versus 395 mathematics rows.

Action and evidence: Verified actual shape, hash, labels, missingness and full-row duplicates.

Residual requirement: No mathematics/language pooling or false external validation.

## A26 Novelty

Severity: Medium. Two standard algorithms and an app offer limited algorithmic contribution.

Action and evidence: Reframed as reproducibility and sensitivity audit with bounded claims.

Residual requirement: Venue fit and sufficient significance require editorial assessment.

## A27 Literature currency

Severity: Medium. Original bibliography mostly predates 2023.

Action and evidence: Added six relevant 2023-2026 works; DOI and official-source records saved.

Residual requirement: Focused update, not a systematic literature review.

## A28 Environment claim

Severity: Medium. Paper says Python 3.12.14 while current environment is 3.12.10.

Action and evidence: Reported observed interpreter and retained historical metadata separately.

Residual requirement: Historical run environment not retroactively altered.

## A29 Prototype privacy

Severity: Medium. Current interface requests a name unnecessary for inference.

Action and evidence: Inspected session/code behavior; recommended data minimization.

Residual requirement: App is not modified or represented as validated deployment.

## A30 Unsupported declarations

Severity: High. Funding/conflicts/ethics/repository placeholders were unresolved.

Action and evidence: Removed placeholders and invented acknowledgment; tracked author actions separately.

Residual requirement: Authors must provide actual declarations and archive URL.

## A31 Authorship and biographies

Severity: High. Author identity must remain and biographies are required by Access.

Action and evidence: Names/order/affiliation/correspondence preserved; no biographies invented.

Residual requirement: All authors must supply approved biographies and verify identity details.

## A32 AI disclosure

Severity: Medium. Original AI declaration was a placeholder.

Action and evidence: Factual acknowledgment describes AI assistance and cites the system.

Residual requirement: Authors must approve disclosure and verify all assisted material.

## A33 Formatting and equations

Severity: Medium. Original PDF had large blank areas and was not the Access template.

Action and evidence: Built editable DOCX from official template; added native equations, numbered figures/tables.

Residual requirement: Final Word/PDF layout and content checked; submission still awaits author actions.

## A34 Unknown categories

Severity: Low. Ignored one-hot levels can encode like a reference category.

Action and evidence: Documented pipeline behavior and inspected application checks.

Residual requirement: Unknown cohort categories and range drift require deployment validation.

## What was already correct

The original manuscript already described retrospective scope, no test threshold tuning, absence of fairness/calibration analysis, and the Always-At-Risk F2 limitation. These were not newly discovered code defects. The title remained inconsistent with its careful text. Pipeline isolation, grade exclusion, class-1 orientation, test confusion matrices, AP definition, class weighting, and coefficient units were implemented correctly. The original 39-column encoding and saved probabilities reproduced.