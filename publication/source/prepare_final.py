"""Prepare the final manuscript, research README and submission support files.

Use the bundled document Python runtime. Scientific results are read, never fitted.
"""
from pathlib import Path
import sys,json,csv,re,shutil,hashlib,html
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'publication';F=B/'final';F.mkdir(exist_ok=True)
sys.path.insert(0,str(B/'source'))
import build_documents as builder
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
TITLE='Retrospective Student Academic Risk Classification Using Interpretable Machine Learning'
URL='https://github.com/ChirayuSingla/Student-academic-Risk-Predictor'
AFF='Department of Computer Science and Engineering, Vellore Institute of Technology, Vellore, Tamil Nadu, India'
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n',encoding='utf-8',newline='\n')
def rows(name):return list(csv.DictReader((B/'results'/name).open(encoding='utf-8')))
def mdtable(headers,data):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers)]+['| '+' | '.join(map(str,r))+' |' for r in data])
def pdf(name,md):
    styles=getSampleStyleSheet()
    for k in ['Title','Heading1','Heading2']:
        styles[k].textColor=colors.black;styles[k].keepWithNext=True
    styles['BodyText'].fontSize=10;styles['BodyText'].leading=14
    styles['BodyText'].spaceAfter=7
    if name=='Final_Reproducibility_Report':
        styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
        styles['BodyText'].spaceAfter=6
    if name=='Final_Technical_Audit':
        styles['BodyText'].fontSize=9.5;styles['BodyText'].leading=13
        styles['BodyText'].spaceAfter=6
    styles['Heading1'].fontSize=14;styles['Heading2'].fontSize=11
    story=[];lines=md.splitlines();i=0
    def para(t,style='BodyText'):
        t=html.escape(t);t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t);return Paragraph(t,styles[style])
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith('|'):
            rr=[]
            while True:
                if not re.fullmatch(r'[|:\-\s]+',line):rr.append([para(c.strip()) for c in line.strip('|').split('|')])
                if i==len(lines) or not lines[i].strip().startswith('|'):break
                line=lines[i].strip();i+=1
            n=len(rr[0]);widths=[468/n]*n
            if n>=3:widths=[130]+[(468-130)/(n-1)]*(n-1)
            t=Table(rr,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf0')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([t,Spacer(1,10)]);continue
        if line.startswith('# '):story.append(para(line[2:],'Title'))
        elif line.startswith('## '):story.append(para(line[3:],'Heading1'))
        elif line.startswith('### '):story.append(para(line[4:],'Heading2'))
        else:story.append(para(line))
    def foot(c,d):c.setFont('Helvetica',8);c.drawString(60,28,'Research preparation | 2 November 2026');c.drawRightString(528,28,str(d.page))
    SimpleDocTemplate(str(B/(name+'.pdf')),pagesize=(612,792),leftMargin=60,rightMargin=60,topMargin=48,bottomMargin=48,title=name.replace('_',' '),author='').build(story,onFirstPage=foot,onLaterPages=foot)
    write(B/(name+'.md'),md)

# Keep the original exports and training snapshots as provenance.
builder.manuscript('Final_IEEE_Access_Manuscript')
metrics={r['model']:r for r in rows('heldout_metrics.csv')}
order=['logistic_regression','decision_tree','random_forest','gradient_boosting','majority','always_at_risk','prevalence','prior_failure']
labels={'logistic_regression':'Logistic regression','decision_tree':'Decision tree','random_forest':'Random forest','gradient_boosting':'Gradient boosting','majority':'Majority','always_at_risk':'Always-At-Risk','prevalence':'Prevalence probability','prior_failure':'Prior failure'}
mt=mdtable(['Model','Precision','Recall','F2','ROC-AUC','AP','Brier'],[[labels[n]]+[f'{float(metrics[n][k]):.3f}' for k in ['precision','recall','f2','roc_auc','average_precision','brier_score']] for n in order])
repro='''## Reproduce on Windows Python 3.12.10

From the repository root, create a fresh environment with `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1`. The setup script requires an installed Python 3.12 x64; an excluded local runtime is not needed by a fresh clone. Dependencies and the 52-package lock preserve the model environment. Do not copy an existing virtual environment between machines.

Run `.venv/Scripts/python.exe -m pip check`, `.venv/Scripts/python.exe -m src.doctor`, `.venv/Scripts/python.exe -m src.verify`, and `.venv/Scripts/python.exe -m pytest -q --basetemp .diagnostics/pytest-fresh`. Then run `.venv/Scripts/python.exe scripts/smoke_streamlit.py` and `.venv/Scripts/python.exe -m streamlit run app.py`.

To reproduce every publication extension without replacing saved evidence, set `$env:RISK_PUBLICATION_OUTPUT = Join-Path (Get-Location) '.diagnostics/publication-reproduction-20261102'` in PowerShell and run `.venv/Scripts/python.exe publication/source/run_experiments.py`. This executes original tuning, four model families, ten outer folds, retuned ablations, calibration ensembles and 2,000 paired stratified bootstrap samples; allow several minutes. Then run `.venv/Scripts/python.exe publication/source/audit_final.py`. Its fresh-run comparison covers scientific CSV columns and excludes nondeterministic search timings.

Saved-output verification alone: `.venv/Scripts/python.exe publication/source/verify_outputs.py` and `.venv/Scripts/python.exe publication/source/audit_final.py`. Read the JSON result: a fresh-rerun check is only present after that rerun completes. Source changes produce an expected historical-snapshot warning; preserve `models/training-source`.

The experiment dependencies are in `publication/reproducibility/requirements-experiments.txt`; the root lock also supports the app and tests. To regenerate the seven figures, run `.venv/Scripts/python.exe publication/source/make_figures.py` only in a disposable clone because it replaces the derived figure exports. To author the final package, use a separate document environment with `python-docx`, `reportlab`, `pypdf`, Pillow and a PDF renderer, run `publication/source/prepare_final.py`, then `publication/source/export_word.ps1 -Files publication/Final_IEEE_Access_Manuscript.docx`. Microsoft Word exports the matching PDF. Authoring is separate from model execution.
'''
readme=f'''# {TITLE}

Research manuscript and reproducible Python project by **Chirayu Singla, Yuvraj Singh, and Rajay Vedaraj I S**. {AFF}.

## Research overview and objectives

This study classifies final mathematics failure in the public UCI cohort while excluding all three grade columns from model inputs. It audits the preserved logistic-regression (LR) and decision-tree (DT) experiment and explores whether its conclusions hold under simple baselines, nested resampling, model diversity, feature exclusions, calibration diagnostics and subgroup analysis. Its contribution is a reproducible sensitivity assessment of a small retrospective classification task.

The problem is `At Risk = 1[G3 < 10]`. The objective is to describe discrimination, probability error, referral workload and uncertainty without implying that recorded predictors were available at a useful early cutoff. No independent institution, prospective cohort or intervention study is evaluated.

## Data and licence

Paulo Cortez (2008), [Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance), DOI [10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Mathematics: 395 rows, 33 original columns, 30 non-grade predictors, 130 failures and 265 passes, no missing values. The frozen split contains 316 training and 79 test rows (26 failures, 53 passes). Portuguese data are supplied as source material and are not pooled or used for external validation. Original data bytes and attribution are preserved in `data/` and `data/provenance.json`.

The repository previously had no project-wide licence. [LICENSE](LICENSE) records that fact and the scope of third-party permissions; it grants no new rights over author-owned code or manuscript. An open-source licence needs rights-holder approval before release.

## Methodology and model descriptions

Training-only pipelines impute numeric values by median and categories by mode, encode categories with first-level dropping, and scale numeric LR inputs. LR searches 16 configurations, DT 60, using stratified five-fold cross-validation, F2 selection with recall and ROC-AUC tie breaks, and optional balanced class weights. No SMOTE or synthetic records are used. The threshold stays 0.5. DT remains the application default selected using training CV. LR supplies grouped log-odds contributions; DT supplies the exact decision path and leaf support.

Random forest and gradient boosting each use a bounded four-configuration exploratory search. Repeated nested validation uses five outer folds repeated twice on only the original 316 training rows, with full five-fold inner retuning. Fold scores are dependent and are summarized by mean and sample SD, not independent confidence intervals.

## Verified results and baseline comparison

The following values are recalculated from saved probabilities and checked against fitted models. LR/DT are the original held-out experiment. RF/GB and all revision analyses are exploratory because the same test cohort was already examined.

{mt}

LR confusion matrix is [[35,18],[8,18]], DT [[31,22],[8,18]], in observed/predicted pass-fail order. Both identify 18/26 failures, with recall 0.692 and Wilson interval 0.500–0.835. LR flags 36/79 and DT 40/79 students. Always-At-Risk flags 79/79 and exceeds both on F2; the selective models improve precision and reduce workload. Majority matches LR accuracy while detecting no failures. AP denotes non-interpolated average precision. Smaller Brier scores are better.

## Calibration, subgroup analysis and ablations

Nested-search sigmoid ensembles use three training calibration folds. Their held-out recall falls to 2/26 = 0.077 at 0.5, despite Brier improving to 0.197 (LR) and 0.202 (DT), versus prevalence 0.221. These models are diagnostic extensions and are not substituted into the app.

Recorded sex, address and school slices retain positive and negative denominators and Wilson intervals. For LR, recorded-F false positives are 14/26 and recorded-M 4/27; DT gives 9/26 and 13/27. Recall uses 12/17 and 6/9 positives. These small, overlapping groups cannot establish fairness or transportable disparities.

Ablations retune LR/DT without absences, without failures, and using a defined reduced set of 15 inputs on identical outer folds. Outer-validation AP permutation importance and coefficient stability describe fitted associations. Results and figures are in [publication/results](publication/results) and [publication/figures](publication/figures). Class-stratified paired bootstrap intervals condition on this cohort, fixed models and observed prevalence; they omit retraining and school clustering.

## Research prototype

The Streamlit application guides profile entry, runs the original models and displays explanations and held-out evaluation. Inputs remain in session memory. Use fictional profiles when demonstrating; personal names are unnecessary for model inference. App tests demonstrate software behavior, not educational effectiveness.

![Research prototype screenshot](results/ui-preview.jpg)

## Limitations

The cohort is small and historical, with two schools, only 26 failing test students and unknown predictor timing. Total absences may include late-year information. Excluding grades or absences cannot establish prospective availability. No external validation, causal effect, operational fairness guarantee or student-outcome benefit is claimed. Future work requires timestamped prospective features, a predeclared cutoff, independent cohorts, contextual ethics review and evaluation of support outcomes.

{repro}
## Repository structure and evidence

- `src/`, `app.py`, `scripts/`, `tests/`: runnable original experiment, app and checks.
- `data/`, `models/`, `results/`: preserved dataset, original fitted models and evidence.
- `models/training-source/`: authenticated historical source snapshots.
- `publication/source/`: exploratory experiments, independent audit and final authoring source.
- `publication/results/`, `publication/tables/`, `publication/figures/`: full scientific evidence and manuscript assets.
- `publication/reproducibility/`: portable historical project snapshot and separate dependency lists; historical copies are intentional.
- `publication/final/`: new verification, reference and layout records.
- `notebooks/`: optional cleared exploration notebook; Jupyter is not needed to run the app.

## Manuscript, reports and publication status

Prepared for IEEE Access; **not submitted, accepted or published**. [Final manuscript PDF](publication/Final_IEEE_Access_Manuscript.pdf) · [editable DOCX](publication/Final_IEEE_Access_Manuscript.docx) · [Technical audit](publication/Final_Technical_Audit.pdf) · [Reproducibility report](publication/Final_Reproducibility_Report.pdf) · [Submission checklist](publication/IEEE_Access_Submission_Checklist.pdf) · [Results appendix](publication/Experiment_Results_Appendix.pdf) · [Release notes](Repository_Release_Notes.md).

Biographies, author declarations, ORCID details, correspondence confirmation and a code-licence decision remain author actions. The proposed v1.0.0 release is prepared locally; publication and Zenodo archival require approval. No project DOI has been assigned. Historical documents remain as provenance; use the `Final_` files for this revision.

## Citation and authors

Use [CITATION.cff](CITATION.cff) for the repository and cite the dataset separately. Suggested repository citation: Chirayu Singla, Yuvraj Singh, and Rajay Vedaraj I S, “{TITLE},” research software and manuscript preparation, {URL}, accessed 2 November 2026. The intended release version is v1.0.0, currently unreleased; do not cite an invented journal volume or DOI.

Correspondence in the supplied manuscript: Rajay Vedaraj I S, rajay@vit.ac.in (author confirmation required). No author biography or institutional approval is inferred from affiliation.
'''
historical=ROOT/'docs/HISTORICAL_SETUP.md'
if not historical.exists():historical.parent.mkdir(exist_ok=True);shutil.copyfile(ROOT/'README.md',historical)
write(ROOT/'README.md',readme)
for file in ['src/reporting.py','results/report.md','results/summary.md']:
    path=ROOT/file;text=path.read_text(encoding='utf-8')
    text=text.replace('Early Detection of Student Academic Risk Using Machine Learning',TITLE).replace('grade-free early-warning **prototype**','retrospective grade-free classification **prototype**')
    if file.startswith('results/'):
        path.write_bytes((text.rstrip()+'\n').replace('\n','\r\n').encode('utf-8'))
    else:write(path,text)
path=ROOT/'app.py';text=path.read_text(encoding='utf-8').replace('StudentLens · Academic Risk Research','Retrospective Academic Risk Research');write(path,text)

write(ROOT/'LICENSE','''# Rights and third-party licences

No project-wide software or manuscript licence was supplied in the repository at the start of this review. This file records the current rights status and does not grant a new licence. Author-owned code and manuscript rights remain with their respective rights holders, subject to applicable law. All authors/rights holders must approve an explicit software licence before an open-source release or Zenodo licence declaration. Public availability alone does not supply that permission.

UCI Student Performance dataset: Paulo Cortez (2008), DOI 10.24432/C5TG7T, Creative Commons Attribution 4.0 International (https://creativecommons.org/licenses/by/4.0/). Preserve attribution and indicate changes. Original data bytes are unchanged.

IEEE Access template files in publication/template are retained from the official journal download for manuscript preparation. Their inclusion is not a representation that the authors own or can relicense IEEE template content. Review IEEE's template and redistribution terms before archival; retain the source link in publication/template/artifact.md. Third-party dependency licences are governed by their respective distributions and are not replaced by this notice.
''')
# JSON is valid YAML; use literal names to avoid inventing family-name parsing.
cff={'cff-version':'1.2.0','message':'Please cite this repository and the UCI dataset separately. Proposed v1.0.0 is not yet released.','title':TITLE,'type':'software','url':URL,'repository-code':URL,'authors':[{'name':n,'affiliation':AFF} for n in ['Chirayu Singla','Yuvraj Singh','Rajay Vedaraj I S']],'keywords':['academic risk','retrospective classification','interpretable machine learning','reproducibility'],'abstract':'Retrospective UCI mathematics classification with preserved original LR/DT models and exploratory sensitivity analyses. No prospective or independent institutional validation.'}
cff['authors']=[{'given-names':g,'family-names':f,'affiliation':AFF} for g,f in [('Chirayu','Singla'),('Yuvraj','Singh'),('Rajay','Vedaraj I S')]]
write(ROOT/'CITATION.cff',json.dumps(cff,indent=2))
write(F/'zenodo-metadata-preparation.json',json.dumps({'title':TITLE,'upload_type':'software','description':cff['abstract'],'creators':[{'name':n,'affiliation':AFF} for n in ['Chirayu Singla','Yuvraj Singh','Rajay Vedaraj I S']],'version':'1.0.0','notes':'Draft metadata only. Licence and author identity details require confirmation; no DOI assigned.'},indent=2))
write(ROOT/'ZENODO_PREPARATION.md',f'''# Zenodo archival preparation

No deposit, public release or DOI was created. The intended version is v1.0.0. `publication/final/zenodo-metadata-preparation.json` is a preparation file, not an automatically consumed `.zenodo.json`: it intentionally omits an unapproved licence and DOI. `CITATION.cff` is the citation source; no competing root `.zenodo.json` is installed.

After author approval: (1) approve the code licence and confirm author names/ORCIDs, manuscript declarations and third-party template rights; (2) approve and publish the v1.0.0 tag/release from the reviewed commit using Repository_Release_Notes.md; (3) sign into Zenodo with GitHub, open Settings > GitHub and enable ChirayuSingla/Student-academic-Risk-Predictor before publishing the release; (4) wait for Zenodo processing, inspect its metadata and archival result; (5) copy only the DOI actually issued to CITATION.cff, README and the manuscript availability statement, distinguishing the version DOI from the concept DOI. If the GitHub release predates integration, use Zenodo's supported manual upload route rather than assuming automatic archival.

Validate CFF using `cffconvert --validate` in a separate tools environment. Assign the approved licence before archival. Do not add a date-released or released version until publication occurs. This task's local validation record is in publication/final/citation_validation.json.

Official instructions checked 2 November 2026: https://help.zenodo.org/docs/github/ ; https://help.zenodo.org/docs/github/describe-software/citation-file/ ; https://help.zenodo.org/docs/github/archive-software/github-upload/ . IEEE submission checklist: https://ieeeaccess.ieee.org/authors/submission-guidelines/ .
''')
release=f'''# Proposed v1.0.0 release

Status: prepared, unpublished, approval required. No tag, GitHub release or Zenodo record has been created.

Manuscript: {TITLE}. Final preparation dated 2 November 2026; editable source and matching Word PDF are under publication/Final_IEEE_Access_Manuscript.*. Not a journal publication.

Dataset: unchanged UCI mathematics records, Cortez (2008), DOI 10.24432/C5TG7T, CC BY 4.0. 395 rows, target G3 < 10, 30 non-grade inputs, frozen 316/79 split. No synthetic records or SMOTE.

Original model artifacts and training-source hashes are preserved. The source version is the reviewed Git commit containing these notes; record its full SHA when publishing. Original LR/DT detect 18/26 failures with F2 0.643/0.625. Always-At-Risk F2 is 0.710. Calibration ensembles detect 2/26 at 0.5. Exploratory extensions include RF/GB, dependent ten-fold nested resampling, ablations, subgroup diagnostics, permutation stability and paired class-stratified bootstrap intervals.

Reproduction: follow README and publication/Final_Reproducibility_Report.pdf. Verification records are in publication/final/experiment_verification.json. Assets: final manuscript DOCX/PDF, four final supporting PDFs, scientific CSVs/figures, CITATION.cff and SHA256 manifest.

Known limitations: previously inspected holdout, small historical two-school cohort, no feature timestamps, no independent external institution, no prospective validation, no causal claims, no educational-effectiveness claim. Licence approval, author biographies/declarations, correspondence/ORCID confirmation and journal submission remain pending. No acceptance or DOI is asserted.

Publication procedure after approval: verify clean reviewed commit and checks, choose the approved licence, set released version/date in CITATION.cff, create v1.0.0 without modifying history, publish with these notes and final artifacts, then verify Zenodo processing. Review IEEE template redistribution before attaching it to the archive.
'''
write(ROOT/'Repository_Release_Notes.md',release)
audit=['# Final technical audit','Review date: 2 November 2026. This is a research preparation audit, not an IEEE decision. The repository and local publication source were inspected; original model artifacts and authenticated training-source snapshots remain unchanged.']
for code,se,title,why,fix,left in builder.ISSUES:
    audit += [f'## {code} {title}',f'Severity: {se}. {why}',f'Prior revision evidence: {fix}',f'Remaining scope or author action: {left}']
audit += ['## Additional repository findings and corrections',
'F01 corrected: README and current report generator still used Early Detection. Current README, report titles and app description now use retrospective framing; historical setup and training snapshots retain provenance.',
'F02 corrected: manuscript said no public code was available although the repository is public. Final availability statement links the repository and distinguishes an unpublished release from a DOI archive.',
'F03 corrected: original verifier recomputed only model nested predictions and checked subgroup totals, not all baseline fold calculations. audit_final.py independently recomputes all 140 fold records including 40 baseline records, summary sample SD, exact subgroup confusion matrices and Wilson intervals, saved-model probabilities, calibration-bin counts and ensemble membership.',
'F04 corrected: full experiment script wrote into existing publication/results. An explicit RISK_PUBLICATION_OUTPUT override allows isolated reruns without changing the protocol or historical outputs.',
'F05 corrected: no citation metadata, release notes or licence-status document. Added CITATION.cff, rights notice, proposed release notes and Zenodo steps. No new reuse licence was imposed without rights-holder approval.',
'F06 preserved: duplicate project/reproducibility copies and historical papers are intentional evidence. Local duplicate ZIPs, environments, caches, review renders and credentials remain ignored. Useful source/model artifacts are retained.',
'F07 residual: stored historical XML/log/environment files contain old local paths. They are diagnostic provenance, not portable setup instructions. New documentation uses relative paths; no credentials or private identifiable student dataset were found in the targeted token scan. UCI anonymous records remain attributed.',
'F08 corrected: final document builder accepts a separate output stem, retaining Revised_Manuscript exports. Word is used for the final matching PDF; no LaTeX manuscript source exists, so no synthetic TEX conversion is represented as original source.',
'F09 residual: author biographies, funding/conflict declarations, ethics determination, ORCID details, licence and correspondence confirmation require human evidence. The final manuscript deliberately contains no invented declarations; it remains author-action pending.',
'F10 corrected: final PDF authoring needs ReportLab, absent from the prior authoring dependency list. Added reportlab==4.4.9 and a separate jsonschema validation requirement without changing the numerical project lock. The new reference verifier uses the standard library; the earlier requests-based verifier is historical and is not the documented current command.',
'F11 residual: live registry queries retrieved all DOI-backed references with matching titles and recorded full author/date/journal metadata. Direct retrieval of the 2008 paper host failed certificate validation, and the AI-system page rejected the scripted request. UCI independently confirms the original paper authors/title/year; the AI-system page was reachable through the browser retrieval service. These fallbacks do not verify the original paper page range or prove absence of retractions. See final/Reference_Review.md.',
'## Verification evidence','See final/experiment_verification.json for executed independent checks and fresh-run comparisons, final/reference_verification.json for live bibliography metadata, and final/document_verification.json for final DOCX/PDF parity. Original 27 tests and Streamlit startup are rerun for this revision. Failed or incomplete checks must be reported rather than converted into success claims.',
'## Remaining rejection risks','Limited novelty from standard algorithms on a heavily used dataset; small/cohort-specific evidence; inability to establish predictor timing or independent transportability; dependent resampling and post-hoc exploratory extensions; incomplete author declarations and biographies. No amount of local testing repairs the unavailable external cohort or timestamps.']
pdf('Final_Technical_Audit','\n\n'.join(audit))
pdf('Final_Reproducibility_Report',f'''# Final reproducibility report

The scientific audit preserves the original protocol, saved model hashes and historical sources. The current interpreter is Windows Python 3.12.10; historical metadata are not retroactively changed. Numerical package versions remain locked.

{repro}
## Verification scope

The independent auditor recalculates 16 held-out variants, original-row baselines, all 140 nested fold records, summary means/sample SD, 24 subgroup slices and Wilson intervals, calibration bins, and predictions from 12 saved extension artifacts. It validates the calibration ensemble's three members and very low recall. A completed isolated training rerun additionally compares scientific CSV outputs, including bootstrap intervals and permutation stability, against the saved results at numerical tolerance. Machine-dependent timings and serialization bytes are not scientific-equality requirements.

The full rerun is intentionally separate from the original results. No test-set threshold optimization or new split is introduced. All revision analyses are exploratory. Read final/experiment_verification.json for the actual completed check set, not a generic reproducibility assertion.

## Assets and limits

Original data: data/student-mat.csv; split: results/split_indices.json and publication/results/frozen_split.json; protocol: publication/results/protocol.json; extension source: publication/source/run_experiments.py. Source tables are in publication/results and manuscript figures are generated from those CSVs by make_figures.py. Historical project copies in publication/reproducibility preserve the earlier version and are not the current entry point.

Full training reruns assess computational reproducibility within this environment. They do not provide a new cohort, prospective validation, operational threshold or educational effectiveness. No independent external institutional validation or feature timestamps can be produced from this data.
''')
check='''# IEEE Access submission checklist

Preparation date 2 November 2026. Status: technically prepared, author actions pending; do not submit as complete until the unresolved items are supplied.

## Completed technical preparation

- Retrospective framing and public repository availability synchronized.
- Official Access Word template retained; full-width front matter and double-column body preserved.
- Final editable DOCX and Word-exported PDF prepared; parity and page-render verification recorded separately.
- Dataset attribution, original frozen split, explicit baselines, exploratory caveats, calibration and subgroup denominators documented.
- AI assistance disclosure retained in the acknowledgment and its system reference retained. All assisted material requires author verification.
- Citation metadata, licence status, proposed v1.0.0 notes and Zenodo preparation supplied without an invented DOI.

## Author confirmations required

- Supply approved short biographies for Chirayu Singla, Yuvraj Singh, and Rajay Vedaraj I S, in that order. IEEE requires them below the references; they cannot be invented.
- Confirm names, affiliation spelling and corresponding author Rajay Vedaraj I S / rajay@vit.ac.in from the supplied source. Confirm all authors consent and satisfy authorship requirements.
- Supply actual funding, acknowledgments and conflicts statements, including a no-funding/no-conflict statement only if true and approved.
- Verify all AI-assisted sections/code, final references, claims, figures and tables; approve the specific disclosure. The disclosure is required research transparency, not a decorative watermark.
- Provide submitting author's populated public ORCID; confirm any other author ORCID details.
- Approve a software licence and confirm third-party IEEE template redistribution before archival. Approve public v1.0.0 release and Zenodo publication separately.

## Institutional determination required

- Obtain/document the institution's actual ethics/exemption determination for secondary public student data, as applicable. Public availability alone does not establish exemption.
- Obtain relevant institutional permissions and approve privacy/governance statements. No institutional clearance has been asserted here.

## Journal submission actions

- Check the live guidelines immediately before submission: https://ieeeaccess.ieee.org/authors/submission-guidelines/ . Current requirements include the prescribed template, matching editable source/PDF, all-author biographies and a submitting-author ORCID.
- Select the manuscript type and 3–10 accurate keywords; verify all authors are extracted correctly by the submission system.
- Confirm the work is not concurrently submitted elsewhere and check for retractions/corrections in references. Resolve bibliography retrieval failures before asserting complete reference verification.
- Confirm editable source and PDF are below 40 MB each and preferably under 20 pages; prepare supporting material and any required response to prior rejection, if applicable.
- Review journal scope, contribution and current APC/payment terms directly with the journal; no funding commitment or acceptance prediction is made.

## Approval gates

No public release, Zenodo deposit, branch deletion, history rewrite, force push or journal submission is authorized by preparation alone. The user requested preparation of these actions. A regular repository synchronization can proceed within the existing push authorization.
'''
pdf('IEEE_Access_Submission_Checklist',check)
appendix=f'''# Experiment results appendix

This appendix traces manuscript results to saved source evidence. The original held-out experiment and exploratory extensions share the known 79-row holdout. Results do not imply prospective or external validation.

## Held-out metrics

{mt}

## Confusion matrices and calibrated variants

'''+mdtable(['Variant','TN','FP','FN','TP','Flags'],[[r['model'].replace('logistic_regression','LR').replace('decision_tree','DT').replace('gradient_boosting','GB').replace('random_forest','RF')]+[r[k] for k in ['TN','FP','FN','TP','flags']] for r in rows('heldout_metrics.csv')])+'''

## Evidence map

Table I: feature descriptions and source data dictionary. Tables II–III: heldout_metrics.csv and heldout_predictions.csv. Table IV: nested_summary.csv and nested_fold_metrics.csv. Table V: the same nested outputs grouped by feature subset. Table VI: heldout metrics for original and __sigmoid variants, with calibration_bins.csv. Table VII: subgroups.csv.

Figure 1: original confusion counts. Figure 2: saved ROC/precision-recall probabilities. Figure 3: dependent outer-fold F2 values. Figure 4: calibration bins and Wilson intervals. Figure 5: threshold_sensitivity.csv. Figure 6: subgroup recall and Wilson intervals. Figure 7: permutation_stability.csv. Files figure5_importance and figure6_thresholds are historical asset identifiers; visible manuscript numbering follows order of appearance.

Bootstrap evidence: bootstrap_intervals.csv, paired_differences.csv and mcnemar.json. Intervals condition on fixed fitted models and observed prevalence; no clustering or refitting uncertainty is covered. Feature schema: feature_subsets.json. Reproduction: reproduction_checks.json. Calibration protocol: protocol.json. Final audit: final/experiment_verification.json.

## Recorded-sex subgroup denominators

'''+mdtable(['Model/group','n','Failures','TP','FP','Negatives'],[[r['model'].replace('logistic_regression','LR').replace('decision_tree','DT')+'/'+r['group'],r['n'],r['positives'],r['TP'],r['FP'],str(int(r['n'])-int(r['positives']))] for r in rows('subgroups.csv') if r['attribute']=='sex' and r['model'] in ['logistic_regression','decision_tree']])
appendix+='\n\n## Nested validation and retuned ablations\n\nEach entry is mean (sample SD) across ten dependent folds, not a confidence interval.\n\n'
foldrows=rows('nested_fold_metrics.csv')
from statistics import mean,stdev
groups={}
for r in foldrows:groups.setdefault((r['subset'],r['model']),[]).append(r)
short={'logistic_regression':'LR','decision_tree':'DT','random_forest':'RF','gradient_boosting':'GB','majority':'Majority','always_at_risk':'Always risk','prevalence':'Prevalence','prior_failure':'Prior failure'}
subsetlabels={'all':'All 30','no_absences':'No absences','no_failures':'No failures','reduced_sensitive':'Reduced 15'}
appendix+=mdtable(['Subset / model','F2 mean (SD)','AUC mean (SD)','AP mean (SD)'],[[subsetlabels[s]+' / '+short[n]]+[f'{mean(float(r[k]) for r in rr):.3f} ({stdev(float(r[k]) for r in rr):.3f})' for k in ['f2','roc_auc','average_precision']] for (s,n),rr in sorted(groups.items())])
appendix+='\n\n## Conditional held-out bootstrap intervals\n\n2,000 class-stratified paired resamples, seed 2701; percentile 95% intervals. Fixed models and prevalence; no cluster or retraining uncertainty.\n\n'
appendix+=mdtable(['Model / metric','Point','Lower','Upper'],[[short[r['model']]+' / '+r['metric'].replace('average_precision','AP').replace('roc_auc','AUC').replace('brier_score','Brier')]+[f'{float(r[k]):.4f}' for k in ['point','low','high']] for r in rows('bootstrap_intervals.csv')])
appendix+='\n\n## Full subgroup denominators\n\nRates use observed positives for recall and observed negatives for false-positive rate.\n\n'
appendix+=mdtable(['Model / attribute / group','n / positives','Recall','FPR'],[[short[r['model']]+' / '+r['attribute']+' / '+r['group'],r['n']+' / '+r['positives'],f'{float(r["recall"]):.3f}',f'{float(r["fpr"]):.3f}'] for r in rows('subgroups.csv')])
pdf('Experiment_Results_Appendix',appendix)
scores=[('Technical correctness',8,'Pipeline isolation, metrics and subgroup/calibration calculations are directly audited; public-data measurement limits persist.'),('Research contribution',6,'Useful reproducibility and sensitivity audit; practical conclusions are carefully bounded.'),('Novelty',4,'Standard models on an established benchmark provide limited methodological novelty.'),('Methodological soundness',7,'Nested retuning and explicit baselines are sound; extensions use a previously inspected holdout.'),('Experimental completeness',7,'Multiple diagnostics and baselines; no independent cohort or prospective cutoff validation.'),('Statistical validity',7,'Conditional bootstrap and dependent-fold caveats are explicit; small subgroups and unobserved school clustering constrain inference.'),('Reproducibility',8,'Executable source, frozen rows, saved probabilities and independent checks supplied; rights and final archive still need approval.'),('Literature coverage',6,'Focused recent and foundational references; not a systematic review and unresolved retrieval must remain documented.'),('Writing quality',8,'Scope, baseline trade-offs and limitations are explicit; author final review remains essential.'),('IEEE formatting',8,'Official template and matching Word PDF; required biographies remain unavailable.'),('Publication readiness',5,'Technical preparation is advanced; licence, biographies, declarations and author approvals prevent submission-complete status.')]
review='# Independent critical review\n\nThis is a separate critical review pass by the same assistant, not an independent human peer review or an IEEE editorial decision. Scores are judgmental, not acceptance probabilities.\n\n'+mdtable(['Category','Score / 10','Reason'],scores)+'\n\nPotential rejection reasons: limited novelty and scope, insufficient significance for IEEE Access, repeated benchmark analysis without an independent institution, post-hoc extensions, uncertain predictor timing, unstable small-group results, and missing mandatory biographies/declarations. No acceptance is promised.'
write(B/'Final_Independent_Review.md',review)
print('Prepared final manuscript source, four supporting PDFs, README, citation and release documents')
