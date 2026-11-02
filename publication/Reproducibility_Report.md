# Reproducibility report

Run date: 1 November 2026, Asia/Calcutta. Dataset: UCI mathematics file, CC BY 4.0. No synthetic data. Original source and artifacts remain in their original directories; new results are written only under publication.

## Observed environment

{
  "python": "3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "packages": {
    "numpy": "2.2.6",
    "pandas": "2.3.3",
    "scipy": "1.16.2",
    "scikit-learn": "1.7.2",
    "matplotlib": "3.10.7",
    "joblib": "1.5.2"
  },
  "elapsed_seconds": 992.0400466918945
}

## Commands from the project root

```powershell
.venv/Scripts/python.exe publication/source/run_experiments.py
.venv/Scripts/python.exe publication/source/make_figures.py
.venv/Scripts/python.exe -m pytest -q --basetemp=publication/review/pytest-new-run
```

Use a fresh, nonexistent test temporary directory inside the workspace and set TEMP and TMP to a writable workspace location when the restricted default Windows temp directory is unavailable. The first test attempt had three temp-directory setup errors; the second used a writable directory and passed all 27 tests, with the expected historical-source warning.

## Artifact authoring

The bundled Codex Python is used for DOCX authoring and PDF rasterization. It requires python-docx, pypdfium2 and Pillow. Run source/build_documents.py to rebuild both DOCXs and Markdown; run source/export_word.ps1 with Microsoft Word installed to export the PDFs; run source/render_pdf.py for the page images used in QA. The packaged render_docx.py was attempted and failed because LibreOffice is unavailable; Word was used as the native fallback.

## Portable reproduction

The source bundle includes a standalone project copy under reproducibility/project, with src/, data/, original model metadata and predictions needed for exact comparison. The runner detects that it is in that copied project using its source location. Place the publication source directory in project/publication/source, as packaged, and run from project. Install the scientific requirements in reproducibility/requirements-experiments.txt in an isolated Python 3.12 environment. The large original app lockfile is retained separately for app reconstruction; its historic package versions may require an appropriate index.

## Protocol details

Read results/protocol.json for grids, seeds, nested split logic, calibration and bootstrap design. frozen_split.json preserves the original 316/79 row IDs. nested_folds.json preserves every outer fit/validation ID; inner folds are deterministic from their fitting row order and seed 42. Pipeline preprocessing and weighting are refitted within fitting partitions. No test-based threshold, feature or final-model choice is made.

## Integrity checks

SHA256SUMS.json records final deliverables, source files, data and experiment artifacts. Reproduction checks assert row order and original probabilities before extensions run. No external data or network connection is necessary for experiments; verify_references.py is the optional network-dependent bibliography audit. Joblib artifacts must be loaded only from this trusted generated package.

## Hardware and repeatability

All estimator fits use n_jobs=1. Runtime is recorded in environment.json, not treated as a portable performance benchmark. Floating-point differences across libraries or platforms may occur. The scripted probability comparison uses absolute and relative tolerance 1e-12. Figure rendering may differ slightly with installed fonts.