# Experiment results appendix

This appendix traces manuscript results to saved source evidence. The original held-out experiment and exploratory extensions share the known 79-row holdout. Results do not imply prospective or external validation.

## Held-out metrics

| Model | Precision | Recall | F2 | ROC-AUC | AP | Brier |
|---|---|---|---|---|---|---|
| Logistic regression | 0.500 | 0.692 | 0.643 | 0.744 | 0.598 | 0.207 |
| Decision tree | 0.450 | 0.692 | 0.625 | 0.693 | 0.569 | 0.216 |
| Random forest | 0.583 | 0.538 | 0.547 | 0.723 | 0.676 | 0.209 |
| Gradient boosting | 0.647 | 0.423 | 0.455 | 0.721 | 0.564 | 0.197 |
| Majority | 0.000 | 0.000 | 0.000 | 0.500 | 0.329 | 0.329 |
| Always-At-Risk | 0.329 | 1.000 | 0.710 | 0.500 | 0.329 | 0.671 |
| Prevalence probability | 0.000 | 0.000 | 0.000 | 0.500 | 0.329 | 0.221 |
| Prior failure | 0.647 | 0.423 | 0.455 | 0.655 | 0.464 | 0.266 |

## Confusion matrices and calibrated variants

| Variant | TN | FP | FN | TP | Flags |
|---|---|---|---|---|---|
| LR | 35 | 18 | 8 | 18 | 36 |
| DT | 31 | 22 | 8 | 18 | 40 |
| RF | 43 | 10 | 12 | 14 | 24 |
| GB | 47 | 6 | 15 | 11 | 17 |
| LR__no_absences | 35 | 18 | 9 | 17 | 35 |
| DT__no_absences | 28 | 25 | 6 | 20 | 45 |
| LR__reduced_sensitive | 39 | 14 | 12 | 14 | 28 |
| DT__reduced_sensitive | 43 | 10 | 15 | 11 | 21 |
| LR__no_failures | 28 | 25 | 7 | 19 | 44 |
| DT__no_failures | 22 | 31 | 4 | 22 | 53 |
| LR__sigmoid | 53 | 0 | 24 | 2 | 2 |
| DT__sigmoid | 53 | 0 | 24 | 2 | 2 |
| majority | 53 | 0 | 26 | 0 | 0 |
| always_at_risk | 0 | 53 | 0 | 26 | 79 |
| prevalence | 53 | 0 | 26 | 0 | 0 |
| prior_failure | 47 | 6 | 15 | 11 | 17 |

## Evidence map

Table I: feature descriptions and source data dictionary. Tables II–III: heldout_metrics.csv and heldout_predictions.csv. Table IV: nested_summary.csv and nested_fold_metrics.csv. Table V: the same nested outputs grouped by feature subset. Table VI: heldout metrics for original and __sigmoid variants, with calibration_bins.csv. Table VII: subgroups.csv.

Figure 1: original confusion counts. Figure 2: saved ROC/precision-recall probabilities. Figure 3: dependent outer-fold F2 values. Figure 4: calibration bins and Wilson intervals. Figure 5: threshold_sensitivity.csv. Figure 6: subgroup recall and Wilson intervals. Figure 7: permutation_stability.csv. Files figure5_importance and figure6_thresholds are historical asset identifiers; visible manuscript numbering follows order of appearance.

Bootstrap evidence: bootstrap_intervals.csv, paired_differences.csv and mcnemar.json. Intervals condition on fixed fitted models and observed prevalence; no clustering or refitting uncertainty is covered. Feature schema: feature_subsets.json. Reproduction: reproduction_checks.json. Calibration protocol: protocol.json. Final audit: final/experiment_verification.json.

## Recorded-sex subgroup denominators

| Model/group | n | Failures | TP | FP | Negatives |
|---|---|---|---|---|---|
| LR/F | 43 | 17 | 12 | 14 | 26 |
| LR/M | 36 | 9 | 6 | 4 | 27 |
| DT/F | 43 | 17 | 12 | 9 | 26 |
| DT/M | 36 | 9 | 6 | 13 | 27 |

## Nested validation and retuned ablations

Each entry is mean (sample SD) across ten dependent folds, not a confidence interval.

| Subset / model | F2 mean (SD) | AUC mean (SD) | AP mean (SD) |
|---|---|---|---|
| All 30 / Always risk | 0.710 (0.006) | 0.500 (0.000) | 0.329 (0.007) |
| All 30 / DT | 0.538 (0.113) | 0.619 (0.044) | 0.436 (0.042) |
| All 30 / GB | 0.338 (0.094) | 0.646 (0.048) | 0.527 (0.068) |
| All 30 / LR | 0.498 (0.140) | 0.666 (0.091) | 0.545 (0.114) |
| All 30 / Majority | 0.000 (0.000) | 0.500 (0.000) | 0.329 (0.007) |
| All 30 / Prevalence | 0.000 (0.000) | 0.500 (0.000) | 0.329 (0.007) |
| All 30 / Prior failure | 0.422 (0.137) | 0.639 (0.066) | 0.448 (0.068) |
| All 30 / RF | 0.468 (0.145) | 0.665 (0.067) | 0.526 (0.081) |
| No absences / DT | 0.496 (0.094) | 0.622 (0.027) | 0.472 (0.067) |
| No absences / LR | 0.503 (0.118) | 0.659 (0.077) | 0.536 (0.092) |
| No failures / DT | 0.506 (0.092) | 0.560 (0.076) | 0.403 (0.091) |
| No failures / LR | 0.525 (0.103) | 0.610 (0.081) | 0.473 (0.095) |
| Reduced 15 / DT | 0.568 (0.123) | 0.642 (0.072) | 0.464 (0.046) |
| Reduced 15 / LR | 0.530 (0.111) | 0.678 (0.076) | 0.570 (0.100) |

## Conditional held-out bootstrap intervals

2,000 class-stratified paired resamples, seed 2701; percentile 95% intervals. Fixed models and prevalence; no cluster or retraining uncertainty.

| Model / metric | Point | Lower | Upper |
|---|---|---|---|
| LR / accuracy | 0.6709 | 0.5696 | 0.7722 |
| LR / precision | 0.5000 | 0.3889 | 0.6250 |
| LR / recall | 0.6923 | 0.5000 | 0.8462 |
| LR / f1 | 0.5806 | 0.4516 | 0.6909 |
| LR / f2 | 0.6429 | 0.4861 | 0.7770 |
| LR / AUC | 0.7438 | 0.6284 | 0.8454 |
| LR / AP | 0.5985 | 0.4714 | 0.7560 |
| LR / Brier | 0.2072 | 0.1709 | 0.2473 |
| DT / accuracy | 0.6203 | 0.5190 | 0.7215 |
| DT / precision | 0.4500 | 0.3556 | 0.5556 |
| DT / recall | 0.6923 | 0.5000 | 0.8462 |
| DT / f1 | 0.5455 | 0.4262 | 0.6552 |
| DT / f2 | 0.6250 | 0.4744 | 0.7566 |
| DT / AUC | 0.6930 | 0.5609 | 0.8197 |
| DT / AP | 0.5688 | 0.4276 | 0.7321 |
| DT / Brier | 0.2164 | 0.1711 | 0.2624 |
| RF / accuracy | 0.7215 | 0.6203 | 0.8101 |
| RF / precision | 0.5833 | 0.4231 | 0.7619 |
| RF / recall | 0.5385 | 0.3462 | 0.7308 |
| RF / f1 | 0.5600 | 0.4000 | 0.7059 |
| RF / f2 | 0.5469 | 0.3659 | 0.7143 |
| RF / AUC | 0.7228 | 0.5914 | 0.8375 |
| RF / AP | 0.6763 | 0.5363 | 0.8053 |
| RF / Brier | 0.2091 | 0.1924 | 0.2265 |
| GB / accuracy | 0.7342 | 0.6456 | 0.8228 |
| GB / precision | 0.6471 | 0.4499 | 0.8571 |
| GB / recall | 0.4231 | 0.2308 | 0.6154 |
| GB / f1 | 0.5116 | 0.3181 | 0.6809 |
| GB / f2 | 0.4545 | 0.2609 | 0.6400 |
| GB / AUC | 0.7213 | 0.6016 | 0.8309 |
| GB / AP | 0.5637 | 0.4335 | 0.7331 |
| GB / Brier | 0.1968 | 0.1547 | 0.2404 |

## Full subgroup denominators

Rates use observed positives for recall and observed negatives for false-positive rate.

| Model / attribute / group | n / positives | Recall | FPR |
|---|---|---|---|
| LR / sex / F | 43 / 17 | 0.706 | 0.538 |
| LR / sex / M | 36 / 9 | 0.667 | 0.148 |
| LR / address / R | 20 / 7 | 0.857 | 0.692 |
| LR / address / U | 59 / 19 | 0.632 | 0.225 |
| LR / school / GP | 69 / 23 | 0.696 | 0.326 |
| LR / school / MS | 10 / 3 | 0.667 | 0.429 |
| DT / sex / F | 43 / 17 | 0.706 | 0.346 |
| DT / sex / M | 36 / 9 | 0.667 | 0.481 |
| DT / address / R | 20 / 7 | 0.857 | 0.538 |
| DT / address / U | 59 / 19 | 0.632 | 0.375 |
| DT / school / GP | 69 / 23 | 0.696 | 0.413 |
| DT / school / MS | 10 / 3 | 0.667 | 0.429 |
| RF / sex / F | 43 / 17 | 0.471 | 0.231 |
| RF / sex / M | 36 / 9 | 0.667 | 0.148 |
| RF / address / R | 20 / 7 | 0.857 | 0.231 |
| RF / address / U | 59 / 19 | 0.421 | 0.175 |
| RF / school / GP | 69 / 23 | 0.522 | 0.174 |
| RF / school / MS | 10 / 3 | 0.667 | 0.286 |
| GB / sex / F | 43 / 17 | 0.294 | 0.154 |
| GB / sex / M | 36 / 9 | 0.667 | 0.074 |
| GB / address / R | 20 / 7 | 0.714 | 0.154 |
| GB / address / U | 59 / 19 | 0.316 | 0.100 |
| GB / school / GP | 69 / 23 | 0.391 | 0.109 |
| GB / school / MS | 10 / 3 | 0.667 | 0.143 |
