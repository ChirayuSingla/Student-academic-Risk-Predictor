# Final technical audit

Review date: 2 November 2026. This is a research preparation audit, not an IEEE decision. The repository and local publication source were inspected; original model artifacts and authenticated training-source snapshots remain unchanged.

## A01 Early detection title

Severity: Critical. Title implies a verified prediction cutoff; no predictor timestamps exist.

Prior revision evidence: Renamed retrospective classification; revised abstract, objectives and conclusion.

Remaining scope or author action: Needs new timestamped cohort for prospective claim.

## A02 Absences availability

Severity: High. Aggregate absences may span the outcome period.

Prior revision evidence: Retuned no-absences models under the same nested folds.

Remaining scope or author action: Other feature timestamps remain unknown.

## A03 Small holdout

Severity: High. Only 26 positive outcomes produce wide rate uncertainty.

Prior revision evidence: Wilson recall intervals and conditional paired bootstrap intervals added.

Remaining scope or author action: Larger independent cohorts required.

## A04 Tuning optimism

Severity: High. Five-fold maximum scores reuse the folds that choose settings.

Prior revision evidence: Added 5-fold x 2-repeat outer validation with complete inner search on original training rows.

Remaining scope or author action: Dependent folds are not independent cohorts.

## A05 Known holdout

Severity: High. Revision was designed after original test results were known.

Prior revision evidence: Extensions labeled exploratory; fixed original row IDs, no threshold/default replacement.

Remaining scope or author action: Fresh validation remains necessary.

## A06 Objective baseline

Severity: High. Always-At-Risk exceeds both original models on test F2.

Prior revision evidence: Retained baseline; explicitly interpret precision, recall and workload.

Remaining scope or author action: No institution-specific cost or capacity elicitation.

## A07 Historical rule baseline

Severity: Medium. Original study lacked a past-failure rule.

Prior revision evidence: Added failures > 0 rule without tuned cutoff.

Remaining scope or author action: Timing of recorded history still requires confirmation.

## A08 Probability benchmark

Severity: Medium. Hard constant baselines are weak probability comparators.

Prior revision evidence: Added training prevalence constant for Brier comparison.

Remaining scope or author action: Hard heuristic scores are not probabilities.

## A09 Model diversity

Severity: Medium. Two models alone do not test nonlinear ensemble behavior.

Prior revision evidence: Added bounded RF and GB searches using same partitions and scoring.

Remaining scope or author action: Search budgets differ; no universal family ranking.

## A10 No calibration evidence

Severity: High. Brier and displayed percentages do not establish calibration.

Prior revision evidence: Added nested-search sigmoid calibration ensembles and fixed-bin reliability diagnostics.

Remaining scope or author action: Small test bins; ensemble effect confounds pure recalibration effect.

## A11 Subgroup fairness

Severity: High. No sex, address or school error assessment existed.

Prior revision evidence: Added denominators, recall and FPR with Wilson intervals.

Remaining scope or author action: No fairness certification, causal analysis or mitigation.

## A12 Sensitive predictors

Severity: Medium. Private, health and proxy inputs create use concerns.

Prior revision evidence: Retuned reduced 15-feature sensitivity scenario.

Remaining scope or author action: Removal does not eliminate proxies or establish fairness.

## A13 Prior-failure dependence

Severity: Medium. Unclear whether other information adds predictive value.

Prior revision evidence: Added no-failures ablation and simple-rule comparison.

Remaining scope or author action: No causal effect inferred.

## A14 Threshold selection

Severity: Medium. F2 search at 0.5 may hide workload trade-offs.

Prior revision evidence: Added descriptive 0.1-0.9 test sensitivity curves.

Remaining scope or author action: No test-based threshold tuning; capacity study pending.

## A15 Paired uncertainty

Severity: Medium. Ranking differences had point estimates only.

Prior revision evidence: 2,000 paired stratified bootstraps; exact LR-DT McNemar test.

Remaining scope or author action: Intervals condition on fixed models/prevalence, omit cluster/retraining uncertainty.

## A16 Fold independence

Severity: Medium. Repeated folds overlap in fit rows and students.

Prior revision evidence: Means and sample SD only; no naive fold-based significance test.

Remaining scope or author action: External replication remains needed.

## A17 Importance bias

Severity: Medium. Training impurity can favor split-rich inputs.

Prior revision evidence: Added raw-feature AP permutation on outer validation folds.

Remaining scope or author action: Correlation and out-of-distribution permutations remain limitations.

## A18 Explanation stability

Severity: Medium. One fitted coefficient/tree ranking is unstable on small data.

Prior revision evidence: Saved per-fold LR coefficients and validation permutation values.

Remaining scope or author action: No causal or intervention interpretation.

## A19 Odds ratio units

Severity: Medium. Numeric and categorical coefficients have different units.

Prior revision evidence: Clarified per-training-SD effects and omitted categorical references.

Remaining scope or author action: No conventional unpenalized inferential CI claimed.

## A20 Ordinal codes

Severity: Medium. LR treats ordinal steps as equally spaced.

Prior revision evidence: Preserved actual encoding and stated assumption.

Remaining scope or author action: Alternative categorical/spline coding is a possible future study.

## A21 External validation

Severity: High. No independent school/cohort evaluation.

Prior revision evidence: Scope limited; public future benchmark suitability documented.

Remaining scope or author action: Requires compatible independent data; not repairable with random resampling.

## A22 Temporal validation

Severity: High. Random split does not test future cohorts.

Prior revision evidence: Explained cutoff and cohort validation requirements; assessed OULAD compatibility.

Remaining scope or author action: New temporal data needed; OULAD is a separate task.

## A23 School clustering

Severity: Medium. Shared school/class context may overstate independence.

Prior revision evidence: Reported assumptions; school subgroup counts retained.

Remaining scope or author action: Only two schools and no class IDs; no cluster-robust inference claimed.

## A24 Zero grades

Severity: Medium. 38 zero grades may mix absence/withdrawal/achievement.

Prior revision evidence: Retained original target and explicitly reported ambiguity.

Remaining scope or author action: Administrative meaning needs source confirmation.

## A25 Dataset identity

Severity: Medium. UCI summary has 649 language records versus 395 mathematics rows.

Prior revision evidence: Verified actual shape, hash, labels, missingness and full-row duplicates.

Remaining scope or author action: No mathematics/language pooling or false external validation.

## A26 Novelty

Severity: Medium. Two standard algorithms and an app offer limited algorithmic contribution.

Prior revision evidence: Reframed as reproducibility and sensitivity audit with bounded claims.

Remaining scope or author action: Venue fit and sufficient significance require editorial assessment.

## A27 Literature currency

Severity: Medium. Original bibliography mostly predates 2023.

Prior revision evidence: Added six relevant 2023-2026 works; DOI and official-source records saved.

Remaining scope or author action: Focused update, not a systematic literature review.

## A28 Environment claim

Severity: Medium. Paper says Python 3.12.14 while current environment is 3.12.10.

Prior revision evidence: Reported observed interpreter and retained historical metadata separately.

Remaining scope or author action: Historical run environment not retroactively altered.

## A29 Prototype privacy

Severity: Medium. Current interface requests a name unnecessary for inference.

Prior revision evidence: Inspected session/code behavior; recommended data minimization.

Remaining scope or author action: App is not modified or represented as validated deployment.

## A30 Unsupported declarations

Severity: High. Funding/conflicts/ethics/repository placeholders were unresolved.

Prior revision evidence: Removed placeholders and invented acknowledgment; tracked author actions separately.

Remaining scope or author action: Authors must provide actual declarations and archive URL.

## A31 Authorship and biographies

Severity: High. Author identity must remain and biographies are required by Access.

Prior revision evidence: Names/order/affiliation/correspondence preserved; no biographies invented.

Remaining scope or author action: All authors must supply approved biographies and verify identity details.

## A32 AI disclosure

Severity: Medium. Original AI declaration was a placeholder.

Prior revision evidence: Factual acknowledgment describes AI assistance and cites the system.

Remaining scope or author action: Authors must approve disclosure and verify all assisted material.

## A33 Formatting and equations

Severity: Medium. Original PDF had large blank areas and was not the Access template.

Prior revision evidence: Built editable DOCX from official template; added native equations, numbered figures/tables.

Remaining scope or author action: Final Word/PDF layout and content checked; submission still awaits author actions.

## A34 Unknown categories

Severity: Low. Ignored one-hot levels can encode like a reference category.

Prior revision evidence: Documented pipeline behavior and inspected application checks.

Remaining scope or author action: Unknown cohort categories and range drift require deployment validation.

## Additional repository findings and corrections

F01 corrected: README and current report generator still used Early Detection. Current README, report titles and app description now use retrospective framing; historical setup and training snapshots retain provenance.

F02 corrected: manuscript said no public code was available although the repository is public. Final availability statement links the repository and distinguishes an unpublished release from a DOI archive.

F03 corrected: original verifier recomputed only model nested predictions and checked subgroup totals, not all baseline fold calculations. audit_final.py independently recomputes all 140 fold records including 40 baseline records, summary sample SD, exact subgroup confusion matrices and Wilson intervals, saved-model probabilities, calibration-bin counts and ensemble membership.

F04 corrected: full experiment script wrote into existing publication/results. An explicit RISK_PUBLICATION_OUTPUT override allows isolated reruns without changing the protocol or historical outputs.

F05 corrected: no citation metadata, release notes or licence-status document. Added CITATION.cff, rights notice, proposed release notes and Zenodo steps. No new reuse licence was imposed without rights-holder approval.

F06 preserved: duplicate project/reproducibility copies and historical papers are intentional evidence. Local duplicate ZIPs, environments, caches, review renders and credentials remain ignored. Useful source/model artifacts are retained.

F07 residual: stored historical XML/log/environment files contain old local paths. They are diagnostic provenance, not portable setup instructions. New documentation uses relative paths; no credentials or private identifiable student dataset were found in the targeted token scan. UCI anonymous records remain attributed.

F08 corrected: final document builder accepts a separate output stem, retaining Revised_Manuscript exports. Word is used for the final matching PDF; no LaTeX manuscript source exists, so no synthetic TEX conversion is represented as original source.

F09 residual: author biographies, funding/conflict declarations, ethics determination, ORCID details, licence and correspondence confirmation require human evidence. The final manuscript deliberately contains no invented declarations; it remains author-action pending.

F10 corrected: final PDF authoring needs ReportLab, absent from the prior authoring dependency list. Added reportlab==4.4.9 and a separate jsonschema validation requirement without changing the numerical project lock. The new reference verifier uses the standard library; the earlier requests-based verifier is historical and is not the documented current command.

F11 residual: live registry queries retrieved all DOI-backed references with matching titles and recorded full author/date/journal metadata. Direct retrieval of the 2008 paper host failed certificate validation, and the AI-system page rejected the scripted request. UCI independently confirms the original paper authors/title/year; the AI-system page was reachable through the browser retrieval service. These fallbacks do not verify the original paper page range or prove absence of retractions. See final/Reference_Review.md.

## Verification evidence

See final/experiment_verification.json for executed independent checks and fresh-run comparisons, final/reference_verification.json for live bibliography metadata, and final/document_verification.json for final DOCX/PDF parity. Original 27 tests and Streamlit startup are rerun for this revision. Failed or incomplete checks must be reported rather than converted into success claims.

## Remaining rejection risks

Limited novelty from standard algorithms on a heavily used dataset; small/cohort-specific evidence; inability to establish predictor timing or independent transportability; dependent resampling and post-hoc exploratory extensions; incomplete author declarations and biographies. No amount of local testing repairs the unavailable external cohort or timestamps.
