# Proposed v1.0.0 release

Status: prepared, unpublished, approval required. No tag, GitHub release or Zenodo record has been created.

Manuscript: Retrospective Student Academic Risk Classification Using Interpretable Machine Learning. Submitted manuscript status confirmed by Chirayu Singla on 4 November 2026; submission venue, date and identifier are not recorded here. Final document preparation dated 2 November 2026; editable source and matching Word PDF are under publication/Final_IEEE_Access_Manuscript.*. Not a journal publication.

Dataset: unchanged UCI mathematics records, Cortez (2008), DOI 10.24432/C5TG7T, CC BY 4.0. 395 rows, target G3 < 10, 30 non-grade inputs, frozen 316/79 split. No synthetic records or SMOTE.

Original model artifacts and training-source hashes are preserved. The source version is the reviewed Git commit containing these notes; record its full SHA when publishing. Original LR/DT detect 18/26 failures with F2 0.643/0.625. Always-At-Risk F2 is 0.710. Calibration ensembles detect 2/26 at 0.5. Exploratory extensions include RF/GB, dependent ten-fold nested resampling, ablations, subgroup diagnostics, permutation stability and paired class-stratified bootstrap intervals.

Reproduction: follow README and publication/Final_Reproducibility_Report.pdf. Verification records are in publication/final/experiment_verification.json. Assets: final manuscript DOCX/PDF, four final supporting PDFs, scientific CSVs/figures, CITATION.cff and SHA256 manifest.

Known limitations: previously inspected holdout, small historical two-school cohort, no feature timestamps, no independent external institution, no prospective validation, no causal claims, no educational-effectiveness claim. The preparation checklist listed licence approval, author biographies/declarations and correspondence/ORCID confirmation as author actions; their completion since submission has not been reverified. Acceptance and publication have not been confirmed. No journal publication or DOI is asserted.

Publication procedure after approval: verify clean reviewed commit and checks, choose the approved licence, set released version/date in CITATION.cff, create v1.0.0 without modifying history, publish with these notes and final artifacts, then verify Zenodo processing. Review IEEE template redistribution before attaching it to the archive.
