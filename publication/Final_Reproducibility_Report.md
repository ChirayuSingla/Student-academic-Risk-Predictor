# Final reproducibility report

The scientific audit preserves the original protocol, saved model hashes and historical sources. The current interpreter is Windows Python 3.12.10; historical metadata are not retroactively changed. Numerical package versions remain locked.

## Reproduce on Windows Python 3.12.10

From the repository root, create a fresh environment with `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1`. The setup script requires an installed Python 3.12 x64; an excluded local runtime is not needed by a fresh clone. Dependencies and the 52-package lock preserve the model environment. Do not copy an existing virtual environment between machines.

Run `.venv/Scripts/python.exe -m pip check`, `.venv/Scripts/python.exe -m src.doctor`, `.venv/Scripts/python.exe -m src.verify`, and `.venv/Scripts/python.exe -m pytest -q --basetemp .diagnostics/pytest-fresh`. Then run `.venv/Scripts/python.exe scripts/smoke_streamlit.py` and `.venv/Scripts/python.exe -m streamlit run app.py`.

To reproduce every publication extension without replacing saved evidence, set `$env:RISK_PUBLICATION_OUTPUT = Join-Path (Get-Location) '.diagnostics/publication-reproduction-20261102'` in PowerShell and run `.venv/Scripts/python.exe publication/source/run_experiments.py`. This executes original tuning, four model families, ten outer folds, retuned ablations, calibration ensembles and 2,000 paired stratified bootstrap samples; allow several minutes. Then run `.venv/Scripts/python.exe publication/source/audit_final.py`. Its fresh-run comparison covers scientific CSV columns and excludes nondeterministic search timings.

Saved-output verification alone: `.venv/Scripts/python.exe publication/source/verify_outputs.py` and `.venv/Scripts/python.exe publication/source/audit_final.py`. Read the JSON result: a fresh-rerun check is only present after that rerun completes. Source changes produce an expected historical-snapshot warning; preserve `models/training-source`.

The experiment dependencies are in `publication/reproducibility/requirements-experiments.txt`; the root lock also supports the app and tests. To regenerate the seven figures, run `.venv/Scripts/python.exe publication/source/make_figures.py` only in a disposable clone because it replaces the derived figure exports. To author the final package, use a separate document environment with `python-docx`, `reportlab`, `pypdf`, Pillow and a PDF renderer, run `publication/source/prepare_final.py`, then `publication/source/export_word.ps1 -Files publication/Final_IEEE_Access_Manuscript.docx`. Microsoft Word exports the matching PDF. Authoring is separate from model execution.

## Verification scope

The independent auditor recalculates 16 held-out variants, original-row baselines, all 140 nested fold records, summary means/sample SD, 24 subgroup slices and Wilson intervals, calibration bins, and predictions from 12 saved extension artifacts. It validates the calibration ensemble's three members and very low recall. A completed isolated training rerun additionally compares scientific CSV outputs, including bootstrap intervals and permutation stability, against the saved results at numerical tolerance. Machine-dependent timings and serialization bytes are not scientific-equality requirements.

The full rerun is intentionally separate from the original results. No test-set threshold optimization or new split is introduced. All revision analyses are exploratory. Read final/experiment_verification.json for the actual completed check set, not a generic reproducibility assertion.

## Assets and limits

Original data: data/student-mat.csv; split: results/split_indices.json and publication/results/frozen_split.json; protocol: publication/results/protocol.json; extension source: publication/source/run_experiments.py. Source tables are in publication/results and manuscript figures are generated from those CSVs by make_figures.py. Historical project copies in publication/reproducibility preserve the earlier version and are not the current entry point.

Full training reruns assess computational reproducibility within this environment. They do not provide a new cohort, prospective validation, operational threshold or educational effectiveness. No independent external institutional validation or feature timestamps can be produced from this data.
