# Early Detection of Student Academic Risk Using Machine Learning

An executed, reproducible research project using the **real UCI mathematics dataset**.
At Risk = `G3 < 10` (label 1); Not At Risk = `G3 >= 10` (label 0).
**G1, G2 and G3 never enter the primary model or application form.** No synthetic data or SMOTE is used.

## Quick start

Use **Python 3.12.10, Windows x64**. Open PowerShell in this directory (the one
containing this README and `app.py`), then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Recreate
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m src.doctor
.\.venv\Scripts\python.exe -m src.verify
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\smoke_streamlit.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Stop it
with Ctrl+C. The supplied data and trained models are sufficient; launching never
requires retraining, data downloads, Jupyter, environment activation, or administrator access.

`-Recreate` backs up an existing environment to `.venv-backup-<timestamp>` before
creating a fresh one. Close running Python/Streamlit processes first. Omit the flag
when creating an environment for the first time. `ExecutionPolicy Bypass` applies
only to this script process; it does not change your machine's execution policy.

The script looks for your per-user Python 3.12 installation, the local validation
runtime if present, then `py -3.12`. If Python is installed elsewhere, supply its
actual executable explicitly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Recreate -PythonExe "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
```

The repair session also downloaded the official Python 3.12.10 x64 NuGet runtime
to `.runtime/python31210/tools/`, allowing validation without a global installation.
The current `.venv` depends on this directory: **keep it in place**. A future setup
can use your installed Python instead. Environments must be recreated after moving
the project or removing their base Python; never copy an existing `.venv` between machines.

### Manual setup and dependency policy

For a manual clean installation, choose a **new** environment directory, explicitly
select Python 3.12 x64, and use its own interpreter for every subsequent command:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv-clean
.\.venv-clean\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.\.venv-clean\Scripts\python.exe -m pip check
.\.venv-clean\Scripts\python.exe -m src.doctor
.\.venv-clean\Scripts\python.exe -m streamlit run app.py
```

`requirements.txt` pins the eight direct dependencies and constrains their dependency
graph with `requirements-lock.txt`. The lock pins all 52 runtime/test packages.
Installing either file produces the same locked project dependency versions on
Python 3.12 Windows x64. `--only-binary=:all:` rejects incompatible/missing wheels
instead of attempting local C/C++ builds. Training writes its package snapshot to
`results/environment-freeze.txt`; it never overwrites the dependency lock.

| Direct package | Preserved version |
|---|---:|
| NumPy | 2.2.6 |
| pandas | 2.3.3 |
| SciPy | 1.16.2 |
| scikit-learn | 1.7.2 |
| Matplotlib | 3.10.7 |
| joblib | 1.5.2 |
| Streamlit | 1.50.0 |
| pytest | 8.4.2 |

These match the recorded training environment. Model loading checks the numerical
stack versions before deserialization. A scikit-learn upgrade requires deliberate
retraining and validation; do not silently load old models under a different version.
Python 3.10 is unsupported by this lock: SciPy requires at least 3.11 and contourpy
at least 3.12. Patch-level Python 3.12 differences are allowed; the repair targets
3.12.10, while the original model metadata correctly retains historical Python 3.12.14.
The Windows lock is tested on Windows; macOS/Linux wheel availability was not tested.

### Diagnosing the original import failure

The supplied `.venv/pyvenv.cfg` selected **Python 3.10.11**, while NumPy and SciPy
contained **`cp312-cp312-win_amd64`** wheels. NumPy's native extension was named
`_multiarray_umath.cp312-win_amd64.pyd`; Python 3.10 could not import it. The inner
exception was `ModuleNotFoundError: numpy._core._multiarray_umath`, wrapped by
NumPy's misleading "you should not try to import numpy from its source directory"
message, then surfaced when pandas imported NumPy. No local NumPy/pandas/SciPy/
Streamlit shadowing module was found in the active application paths.

Recreating the environment with the correct interpreter fixes this binary mismatch.
Reinstalling only pandas, installing into global Python, or downgrading NumPy does
not address the underlying mixed environment. Inspect the actual interpreter and
package origins with:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.version)"
.\.venv\Scripts\python.exe -m src.doctor --json
```

`src.doctor` checks Python version/architecture, virtual-environment isolation,
PYTHONHOME/PYTHONPATH overrides, local shadowing names, **every** locked version and
its Python requirement/wheel tags, imports and module origins, and both saved models.
It exits nonzero on failure. If path overrides exist, clear them in this terminal
with `Remove-Item Env:PYTHONHOME, Env:PYTHONPATH -ErrorAction SilentlyContinue` before setup.
For persistent DLL failures after a clean rebuild, retain the full inner traceback
and diagnostic output; do not diagnose from the outer pandas error alone.

In VS Code select `.venv\Scripts\python.exe` using **Python: Select Interpreter**.
The included workspace settings provide this default; an already-selected interpreter
may still need to be changed manually. `python`, `pip`, and `streamlit` on PATH can
still refer to Python 3.10, so use the explicit virtual-environment commands above.

### Optional data acquisition and training

```powershell
# Optional: extract the supplied archive and compare it with UCI (network required).
.\.venv\Scripts\python.exe -m src.acquire_data --archive "student+performance.zip" --verify-official
# Optional: reproduce training into a separate directory, preserving supplied results.
.\.venv\Scripts\python.exe -m src.run_pipeline --output-dir .diagnostics\pipeline-replay
# Deliberately replace the active models/results only when you want a new experiment:
# .\.venv\Scripts\python.exe -m src.run_pipeline
```

Omit `--verify-official` for offline extraction. The already-extracted `data/` is
sufficient for all experiments. A partial archive now fails before writing dataset files.
The full replay uses the same architecture, 380 CV fits, seeds, features, selection
objective, and threshold. `--output-dir` changes only where artifacts are saved.

### Project copies and provenance

The active project is this directory. `student-academic-risk-project/` and
`student-academic-risk-project.zip` are preserved original distribution copies;
they have not been synchronized with these repairs. Do not launch from that nested
directory. `pytest.ini` limits discovery to this root's `tests/` to avoid duplicate
module names and accidentally testing the distribution copy.

The original models, metadata, data, metric tables, plots and research reports are
preserved. `models/training-source/` contains the exact original source bytes whose
hashes were recorded in the model metadata. The verifier authenticates that snapshot,
reports current source changes explicitly, and recomputes predictions, metrics,
preprocessing statistics, splits and explanations using the repaired code. It does
not rewrite historical metadata to pretend the old models used the new source.
`--strict-source` additionally requires the current sources to match the historical
training run; it is expected to fail for the supplied models after these repairs.

See [results/repair-report.md](results/repair-report.md) for the repair inventory and
executed checks. `results/repair-tests.xml` records the new test run; the historical
`results/tests.xml` and UI review remain available.

## Files

```text
data/                  original CSVs, UCI documentation and SHA-256 provenance
notebooks/             optional exploration of the real data and saved results
src/
  acquire_data.py       safe extraction, optional official byte comparison
  artifacts.py          authenticated model loading and cache signatures
  config.py            fixed feature domains, labels and experiment constants
  data.py              schema validation, target and stratified split
  doctor.py            interpreter, dependency, native-wheel and prediction diagnostics
  preprocessing.py     ColumnTransformer and fold-local transformers
  training.py          imbalance inspection, five-fold tuning and selection
  evaluation.py        both-class metrics, confusion matrices, ROC and PR curves
  eda.py               class distribution and training-only exploratory plots
  explainability.py    coefficients, importance, tree and exact local explanations
  reporting.py         report generated from executed artifacts
  run_pipeline.py      complete reproducible workflow
  verify.py            saved-model, split, preprocessing and metrics audit
  ui.py                guided form, plain-language labels and responsive styling
models/                two joblib pipelines and metadata
models/training-source/ authenticated original sources from the supplied training run
results/figures/       11 PNG plots plus full tree SVG
results/               metrics, CV grids, predictions, explanations, audit and report
tests/                 scientific integrity and Streamlit integration checks
app.py                 Streamlit student-input research prototype
requirements.txt       pinned direct dependencies
requirements-lock.txt  exact installed package versions
scripts/setup.ps1      fresh Windows environment setup with optional backup
pytest.ini             test discovery restricted to the active project
```

Start with **[results/summary.md](results/summary.md)** for the concise research report;
the detailed methodology and results are in **[results/report.md](results/report.md)**.
All scores are calculated by actual model execution. `results/metrics.json` includes accuracy,
At Risk precision/recall/F1/F2, ROC-AUC, average precision, Brier score, specificity, both-class
classification reports, confusion matrices and a recall uncertainty interval.
`metrics_summary.csv` and held-out prediction CSVs allow independent inspection.

## Methodology

- The original `student-mat.csv` has 395 students, 33 columns and no missing values.
  `student-por.csv` is retained but **not used** in this experiment.
- Stratified 80/20 train-test split with `random_state=42`; 316 train / 79 test.
- Five-fold stratified training-only CV, shuffled with `random_state=42`.
  One complete scikit-learn pipeline is passed to each GridSearchCV.
  Imputation, category discovery and scaling are fitted inside each training fold.
- Categorical features: mode imputation, one-hot encoding with one omitted reference level.
  Numeric/ordinal features: median imputation; standardization for Logistic Regression only.
- Logistic Regression and Decision Tree compare `class_weight=None` and `'balanced'` in CV
  after inspecting training class imbalance. No synthetic oversampling is needed or used.
- Choose hyperparameters and the default model by highest mean **F2**, with ties decided by
  recall then ROC-AUC. F2 favors recall while penalizing false-positive overload.
  A fixed 0.5 classification threshold is declared before evaluation; the test data never
  determine preprocessing, hyperparameters, model choice or the threshold.
- Both final pipelines fit the full **training partition only**. The saved pipelines remain
  those evaluated on test; test rows are not used to refit a deployment model.
  Actual majority and always-At-Risk baselines contextualize the results.
- Seeds, source/dataset/model hashes, package versions, row IDs, CV folds, complete search
  tables, coefficients, reference categories, tree rules and plots are saved.

## Selected and excluded features

All 30 non-grade columns are included a priori:

| Group | Features |
|---|---|
| Demographic/school | school, sex, age, address, reason, guardian, traveltime |
| Family/home | famsize, Pstatus, Medu, Fedu, Mjob, Fjob, famsup, nursery, internet, famrel |
| Study/support/absence | studytime, failures, schoolsup, paid, activities, higher, absences |
| Lifestyle/wellbeing | romantic, freetime, goout, Dalc, Walc, health |

`G3` is excluded because it defines the outcome; `G1` and `G2` are excluded to withhold
current-course grade signals. `failures` refers to past class failures. The original codes
are preserved: the CSV observes 0–3, while the UCI documentation mentions code 4.
Numeric and categorical column lists are explicit in `src/config.py`; ordinal codes are
treated numerically, a modeling assumption documented in the report.

## Streamlit application

Complete four short steps using UCI meanings, review the profile, and submit. Model selection
is available under Model settings. Type the student's name, school and numeric details, including
age, absences and the ratings described beside each field. School accepts Gabriel Pereira / GP
or Mousinho da Silveira / MS, ignoring case and extra spaces, and validates the entry against
the two schools supported by the trained models. Other categorical questions use visible
radio choices; the form has no searchable dropdown controls. The required student name is
shown on the review and result pages, kept only in session memory, and excluded from model
inputs. Editing preserves it; starting a new assessment clears it.
Every student input starts blank and is required, preventing
training medians or modes from being mistaken for a real student's information. Back and
Continue save entries within the browser session. The app
shows predicted category, estimated probability, and an exact model explanation:

- Logistic Regression: grouped log-odds contributions relative to the mean transformed
  training profile. The reference plus contributions reconstructs the model's log-odds.
- Decision Tree: the exact split path and number of training rows at the reached leaf.

The UI includes category descriptions, input checks, training-support warnings, evaluation
results and citations. The result page offers editing and a fresh assessment. Changing model
settings does not relabel an existing estimate; changes apply to the next submission.
Submitted information is used in memory; this app does not persist student records.
Joblib artifacts must come from a trusted source; this app checks the recorded model hashes.

## Limitations

**Research prototype, never the sole basis for academic decisions.** These are associations,
not causal explanations or evidence that changing a variable improves performance.
Probabilities are uncalibrated estimates; weighting can alter their interpretation.

UCI does not supply per-feature timestamps; `absences` is a recorded total and could contain
late-year information. Grade exclusion removes direct grade leakage but cannot establish
that every feature was available at an early cutoff. This is a retrospective grade-free
prototype. Before operational use, freeze all inputs at a defined early cutoff, validate
prospectively and externally, assess subgroup fairness and review sensitive variables.
The small historical cohort does not establish applicability to other student populations.

## Research context and citations

Dataset: **Cortez, P. (2008). Student Performance [Dataset]. UCI Machine Learning Repository.**
[DOI: 10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T).
[UCI source and definitions](https://archive.ics.uci.edu/dataset/320/student+performance).
Data license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
`data/provenance.json` records the original archive and extracted-file hashes and whether
the contents were verified byte-for-byte against the official UCI download.

Conceptual paper: **Ewais, A., Arram, A., Diab, S., et al. (2026). Using machine learning
for early identification of At-risk students. Scientific Reports, 16, 19944.**
[DOI: 10.1038/s41598-026-48426-1](https://doi.org/10.1038/s41598-026-48426-1).
The publisher identifies the first author as Ahmed Ewais. Its institutional dataset is
available by reasonable request, not a public download. **It is not used here.**
This project differs by using public UCI data and binary Logistic Regression/Decision Tree
classification; the paper's regression scores should not be compared directly to these results.

The optional notebook reads actual source data and executed outputs; it ships with cleared
outputs and is not required by the pipeline. To use it, install Jupyter separately and open
`notebooks/01_explore_results.ipynb`. The verified execution is the modular CLI pipeline.
