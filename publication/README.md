# Research paper revision package

Prepared 1 November 2026. Start with Revised_Manuscript.pdf or the editable DOCX. The manuscript uses the official IEEE Access template and confines conclusions to retrospective classification.

Supporting_Reports contains the 34-issue technical audit, experiment report, reproduction instructions and readiness checklist. Individual Markdown versions allow direct review. Reference_Verification.md records the original and new bibliography checks and retrieval limitations.

Seven figures are supplied as 600 dpi PNG and vector PDF/SVG. Tables contains the seven manuscript tables and complete numerical outputs. Results includes trained extension models, saved row-level probabilities, nested folds, search results, bootstrap intervals and verification records.

Reproducibility/project is a portable copy of the relevant original project and all new scripts. From that project directory install ../requirements-experiments.txt into a Python 3.12 environment, then run `python publication/source/run_experiments.py` and `python publication/source/make_figures.py`. The source scripts in the main package have the same content. Authoring dependencies are separate; Microsoft Word is needed for the exact DOCX-to-PDF export used here. Additional app/test dependencies are in the original lockfile.

The original experiment reproduced; 27 project tests passed and seven independent output checks passed. Calibration, ablation, subgroup and extra-model results are exploratory because the original test results were known. All tests of the original application are separate from evidence of educational effectiveness.

Submission is still pending: author biographies, funding/conflict and institutional ethics declarations, final author review, a versioned public code archive, ORCID/consent checks, and an assessment of venue fit. No approval, funding, lack of conflicts, or prospective validation has been invented. No submission has been made.
