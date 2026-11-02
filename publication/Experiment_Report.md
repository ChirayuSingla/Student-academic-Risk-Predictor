# Experiment report

All numbers below are executed results. Extensions are exploratory. The original test cohort was already known; no new holdout is claimed.

## Protocol

{
  "outer": "5-fold stratified, 2 repeats, seed 2026, on original 316 training records only",
  "inner": "5-fold stratified shuffled seed 42, F2 then recall then ROC-AUC tie-break",
  "grids": {
    "logistic_regression": {
      "classifier__C": [
        0.01,
        0.1,
        1.0,
        10.0
      ],
      "classifier__penalty": [
        "l1",
        "l2"
      ],
      "classifier__class_weight": [
        null,
        "balanced"
      ]
    },
    "decision_tree": {
      "classifier__criterion": [
        "gini",
        "entropy"
      ],
      "classifier__max_depth": [
        2,
        3,
        4,
        5,
        6
      ],
      "classifier__min_samples_leaf": [
        5,
        10,
        20
      ],
      "classifier__class_weight": [
        null,
        "balanced"
      ]
    },
    "random_forest": {
      "classifier__max_depth": [
        3,
        null
      ],
      "classifier__min_samples_leaf": [
        10
      ],
      "classifier__class_weight": [
        null,
        "balanced"
      ]
    },
    "gradient_boosting": {
      "classifier__learning_rate": [
        0.03,
        0.1
      ],
      "classifier__max_depth": [
        1,
        2
      ]
    }
  },
  "threshold": 0.5,
  "calibration": "sigmoid, ensemble=True, 3 stratified calibration folds seed 73; nested 5-fold hyperparameter searches within each fitting fold",
  "bootstrap": "2000 class-stratified paired resamples seed 2701; fixed fitted models; percentile 95% intervals",
  "exploratory": true
}

## Preserved original experiment

Both original models reproduce saved probabilities to maximum absolute difference 1.1102230246251565e-16. The original DT default and 0.5 threshold are retained. See results/reproduction_checks.json and frozen_split.json.

## Executed analyses

Original 16-candidate LR and 60-candidate DT searches; four-candidate RF and GB searches; ten nested outer folds with four model families and four baselines; LR/DT retuned ablations for no absences, reduced personal attributes, and no failures; nested-search sigmoid calibration ensembles; 2,000 paired class-stratified bootstraps; exact McNemar; three subgroup slices; threshold curves; raw-feature outer-validation permutation and coefficient stability.

## Actual held-out results

| Model | Accuracy | Precision | Recall | F1 | F2 | AUC | AP | Brier | Flags |

|---|---|---|---|---|---|---|---|---|---|

| logistic_regression | 0.671 | 0.500 | 0.692 | 0.581 | 0.643 | 0.744 | 0.598 | 0.207 | 36 |

| decision_tree | 0.620 | 0.450 | 0.692 | 0.545 | 0.625 | 0.693 | 0.569 | 0.216 | 40 |

| random_forest | 0.722 | 0.583 | 0.538 | 0.560 | 0.547 | 0.723 | 0.676 | 0.209 | 24 |

| gradient_boosting | 0.734 | 0.647 | 0.423 | 0.512 | 0.455 | 0.721 | 0.564 | 0.197 | 17 |

| logistic_regression__no_absences | 0.658 | 0.486 | 0.654 | 0.557 | 0.612 | 0.735 | 0.628 | 0.209 | 35 |

| decision_tree__no_absences | 0.608 | 0.444 | 0.769 | 0.563 | 0.671 | 0.701 | 0.530 | 0.236 | 45 |

| logistic_regression__reduced_sensitive | 0.671 | 0.500 | 0.538 | 0.519 | 0.530 | 0.698 | 0.571 | 0.218 | 28 |

| decision_tree__reduced_sensitive | 0.684 | 0.524 | 0.423 | 0.468 | 0.440 | 0.599 | 0.448 | 0.250 | 21 |

| logistic_regression__no_failures | 0.595 | 0.432 | 0.731 | 0.543 | 0.642 | 0.638 | 0.478 | 0.242 | 44 |

| decision_tree__no_failures | 0.557 | 0.415 | 0.846 | 0.557 | 0.701 | 0.689 | 0.471 | 0.221 | 53 |

| logistic_regression__sigmoid | 0.696 | 1.000 | 0.077 | 0.143 | 0.094 | 0.748 | 0.607 | 0.197 | 2 |

| decision_tree__sigmoid | 0.696 | 1.000 | 0.077 | 0.143 | 0.094 | 0.678 | 0.599 | 0.202 | 2 |

| majority | 0.671 | 0.000 | 0.000 | 0.000 | 0.000 | 0.500 | 0.329 | 0.329 | 0 |

| always_at_risk | 0.329 | 0.329 | 1.000 | 0.495 | 0.710 | 0.500 | 0.329 | 0.671 | 79 |

| prevalence | 0.671 | 0.000 | 0.000 | 0.000 | 0.000 | 0.500 | 0.329 | 0.221 | 0 |

| prior_failure | 0.734 | 0.647 | 0.423 | 0.512 | 0.455 | 0.655 | 0.464 | 0.266 | 17 |

## Nested outer-fold results

The ten fold scores overlap and are dependent. Mean and sample SD are descriptive; they are not test-set results or independent-replicate confidence intervals.

| Feature subset | Model | F2 mean | F2 SD | AUC mean |

|---|---|---|---|---|

| all | always_at_risk | 0.7103 | 0.0061 | 0.5000 |

| all | decision_tree | 0.5385 | 0.1127 | 0.6186 |

| all | gradient_boosting | 0.3383 | 0.0937 | 0.6462 |

| all | logistic_regression | 0.4985 | 0.1403 | 0.6657 |

| all | majority | 0.0000 | 0.0000 | 0.5000 |

| all | prevalence | 0.0000 | 0.0000 | 0.5000 |

| all | prior_failure | 0.4220 | 0.1365 | 0.6386 |

| all | random_forest | 0.4681 | 0.1455 | 0.6650 |

| no_absences | decision_tree | 0.4955 | 0.0944 | 0.6217 |

| no_absences | logistic_regression | 0.5033 | 0.1185 | 0.6587 |

| no_failures | decision_tree | 0.5064 | 0.0915 | 0.5598 |

| no_failures | logistic_regression | 0.5252 | 0.1033 | 0.6103 |

| reduced_sensitive | decision_tree | 0.5680 | 0.1228 | 0.6419 |

| reduced_sensitive | logistic_regression | 0.5296 | 0.1112 | 0.6776 |

## Statistical comparisons

{
  "LR_correct_DT_wrong": 15,
  "DT_correct_LR_wrong": 11,
  "exact_two_sided_p": 0.557197093963623,
  "exploratory": true
}

Paired differences and percentile limits are in paired_differences.csv. Metric intervals condition on observed class counts and fixed fitted models. No cluster adjustment, model-refitting bootstrap or multiplicity-adjusted confirmatory significance claim is made.

## Interpretation

F2 rewards broad referral; compare both precision and workload with Always-At-Risk. Rank metrics and Brier measure different properties. The prevalence baseline is the appropriate constant probability comparison. Calibration ensembles change base fits and averaging; their performance change is not solely a calibration effect. Ablations are predictive sensitivity tests. Small subgroup denominators prevent certification of fairness.

## Not performed

No external or prospective cohort validation, prediction-cutoff reconstruction, OULAD training, Portuguese-subject transfer, operational intervention, teacher usability trial, fairness mitigation, Explainable Boosting Machine, SHAP study, or ordinal recoding experiment was performed. These are neither implicit successes nor fabricated pending results.

## Output map

heldout_metrics.csv includes all completed variants; nested_fold_metrics.csv and nested_predictions.csv contain the repeated nested runs; subgroups.csv includes denominators and Wilson intervals; calibration_bins.csv includes bin counts and observed-rate intervals; bootstrap_intervals.csv contains eight metric intervals for the four model families. Every figure is generated by make_figures.py from those outputs.