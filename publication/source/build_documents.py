"""Build manuscript from the official template and a separate supporting report."""
from pathlib import Path
import sys,re,json,copy,hashlib,statistics
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from manuscript_content import content,REFERENCES,rows,LABEL,num
B=Path(__file__).resolve().parents[1]
def keep(p):p.paragraph_format.keep_with_next=True
def no_number(p):
    pp=p._p.get_or_add_pPr();n=OxmlElement('w:numPr');i=OxmlElement('w:numId');i.set(qn('w:val'),'0');n.append(i);pp.append(n)
def font_black(d):
    for s in d.styles:
        if s.type==1:
            s.font.color.rgb=RGBColor(0,0,0)
        for b in s.element.xpath('.//w:pBdr'):b.getparent().remove(b)
    for b in d._element.xpath('.//w:pBdr'):b.getparent().remove(b)
def footer(d):
    seen=set()
    for sec in d.sections:
        for area in [sec.header,sec.first_page_header,sec.even_page_header,sec.footer,sec.first_page_footer,sec.even_page_footer]:
            if id(area._element) in seen:continue
            seen.add(id(area._element))
            for e in list(area._element):area._element.remove(e)
            p=area.add_paragraph()
            if 'hdr' in area._element.tag:
                p.text='Singla et al.  Retrospective Student Academic Risk Classification';p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
                for r in p.runs:r.font.size=Pt(7)
            else:
                p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
                r=p.add_run();f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');r._r.addnext(f)
def table(d,caption,headers,data,width,style=False):
    p=d.add_paragraph(caption,style='Table Caption' if style else 'Caption');keep(p)
    t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=[width/len(headers)]*len(headers)
    if len(headers)>=3:
        widths[0]=width*.27
        widths[1:]=[(width-widths[0])/(len(headers)-1)]*(len(headers)-1)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for c,h in zip(t.rows[0].cells,headers):c.text=str(h)
    hdr=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(hdr)
    for vals in data:
        for c,v in zip(t.add_row().cells,vals):c.text=str(v).replace('__sigmoid',' sigmoid')
    for ri,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
        for j,c in enumerate(row.cells):
            c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=c._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'45');e.set(qn('w:type'),'dxa');m.append(e)
            pr.append(m);b=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
            pr.append(b)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7EDF0');pr.append(sh)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(1);p.paragraph_format.space_before=Pt(1);p.paragraph_format.line_spacing=1
                p.paragraph_format.keep_with_next=ri<len(t.rows)-1
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(7.5 if style else 9);r.bold=ri==0
    d.add_paragraph().paragraph_format.space_after=Pt(2)
def mathrun(text):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def sub(x,i):
    e=OxmlElement('m:sSub');a=OxmlElement('m:e');a.append(mathrun(x));b=OxmlElement('m:sub');b.append(mathrun(i));e.extend([a,b]);return e
def frac(a,b):
    f=OxmlElement('m:f');n=OxmlElement('m:num');n.append(mathrun(a));de=OxmlElement('m:den');de.append(mathrun(b));f.extend([n,de]);return f
def equation(d,number):
    p=d.add_paragraph(style='Equation');no_number(p)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(3.1),WD_ALIGN_PARAGRAPH.RIGHT)
    m=OxmlElement('m:oMath')
    if number=='1':m.extend([sub('y','i'),mathrun(' = 1['),sub('G3','i'),mathrun(' < 10]')])
    elif number=='2':m.extend([sub('ŷ','i'),mathrun(' = 1['),sub('p','i'),mathrun(' ≥ 0.5]')])
    elif number=='3':m.extend([sub('F','2'),mathrun(' = '),frac('5TP','5TP + 4FN + FP')])
    else:m.extend([mathrun('Brier = '),frac('1','n'),sub('∑','i'),mathrun(' ('),sub('p','i'),mathrun(' − '),sub('y','i'),mathrun(')²')])
    p._p.append(m);p.add_run('\t('+number+')')
def remap_citations(blocks):
    mapping={}
    def rep(match):
        old=int(match.group(1))
        if old not in mapping:mapping[old]=len(mapping)+1
        return '['+str(mapping[old])+']'
    out=[]
    for b in blocks:
        if b[0]=='reference':continue
        if b[0] in ['p','abstract']:b=(b[0],re.sub(r'\[(\d+)\]',rep,b[1]))
        out.append(b)
    for old,new in mapping.items():out.append(('reference',f'[{new}] '+REFERENCES[old-1]))
    (B/'updated_references.md').write_text('# Verified bibliography\n\n'+'\n\n'.join(b[1] for b in out if b[0]=='reference'),encoding='utf-8')
    return out
def manuscript(output_stem='Revised_Manuscript'):
    d=Document(B/'template/Access-Template-2024.docx');font_black(d)
    front=copy.deepcopy(d.sections[0]._sectPr);body=copy.deepcopy(d.sections[1]._sectPr)
    for child in list(d._element.body):d._element.body.remove(child)
    d._element.body.append(body)
    blocks=remap_citations(content());started=False
    md=[]
    for block in blocks:
        typ=block[0]
        if typ=='h1' and not started:
            p=d.add_paragraph();p._p.get_or_add_pPr().append(front);p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=Pt(1)
            started=True
        if typ in ['title','authors','affiliation','correspondence','abstract','keywords','p','h1','h2','reference']:
            styles={'title':'Paper Title','authors':'AU','affiliation':'PI','correspondence':'PI','abstract':'Abstract','keywords':'IT','p':'PARA','h1':'H1','h2':'H2_First','reference':'Ref'}
            txt=block[1]
            if typ=='abstract':txt='ABSTRACT '+txt
            if typ=='keywords':txt='INDEX TERMS '+txt
            p=d.add_paragraph(txt,styles[typ]);no_number(p)
            for r in p.runs:r.font.color.rgb=RGBColor(0,0,0)
            if typ=='title':
                p.paragraph_format.space_before=Pt(10);p.paragraph_format.space_after=Pt(12)
            if typ in ['h1','h2']:keep(p)
            if typ=='p':p.paragraph_format.widow_control=True
            md.append(('## ' if typ=='h1' else '### ' if typ=='h2' else '# ' if typ=='title' else '')+txt+'\n')
        elif typ=='equation':equation(d,block[2]);md.append(block[1]+' ('+block[2]+')\n')
        elif typ=='table':
            table(d,block[1],block[2],block[3],3.34,True)
            md.extend([block[1]+'\n','| '+' | '.join(map(str,block[2]))+' |','|'+'---|'*len(block[2])]+['| '+' | '.join(map(str,r))+' |' for r in block[3]]+['\n'])
        elif typ=='figure':
            p=d.add_paragraph();p.paragraph_format.space_after=Pt(2);keep(p);p.add_run().add_picture(str(B/'figures'/(block[1]+'.png')),width=Inches(3.34))
            pic=p._p.xpath('.//wp:docPr')[0];pic.set('descr',block[2]);pic.set('title',block[1])
            p=d.add_paragraph(block[2],style='Fig Caption');no_number(p);p.paragraph_format.space_after=Pt(8)
            md.append('!['+block[2]+'](figures/'+block[1]+'.png)\n')
    footer(d)
    d.core_properties.title=blocks[0][1];d.core_properties.author='Chirayu Singla; Yuvraj Singh; Rajay Vedaraj I S';d.core_properties.comments=''
    d.save(B/(output_stem+'.docx'))
    (B/(output_stem+'.md')).write_text('\n'.join(md),encoding='utf-8')
    (B/'source'/(output_stem+'_blocks.json')).write_text(json.dumps(blocks,indent=2),encoding='utf-8')
    print('Manuscript',len(' '.join(md).split()),'words; abstract',len(next(b[1] for b in blocks if b[0]=='abstract').split()),'words')

ISSUES=[
('A01','Critical','Early detection title','Title implies a verified prediction cutoff; no predictor timestamps exist.','Renamed retrospective classification; revised abstract, objectives and conclusion.','Needs new timestamped cohort for prospective claim.'),
('A02','High','Absences availability','Aggregate absences may span the outcome period.','Retuned no-absences models under the same nested folds.','Other feature timestamps remain unknown.'),
('A03','High','Small holdout','Only 26 positive outcomes produce wide rate uncertainty.','Wilson recall intervals and conditional paired bootstrap intervals added.','Larger independent cohorts required.'),
('A04','High','Tuning optimism','Five-fold maximum scores reuse the folds that choose settings.','Added 5-fold x 2-repeat outer validation with complete inner search on original training rows.','Dependent folds are not independent cohorts.'),
('A05','High','Known holdout','Revision was designed after original test results were known.','Extensions labeled exploratory; fixed original row IDs, no threshold/default replacement.','Fresh validation remains necessary.'),
('A06','High','Objective baseline','Always-At-Risk exceeds both original models on test F2.','Retained baseline; explicitly interpret precision, recall and workload.','No institution-specific cost or capacity elicitation.'),
('A07','Medium','Historical rule baseline','Original study lacked a past-failure rule.','Added failures > 0 rule without tuned cutoff.','Timing of recorded history still requires confirmation.'),
('A08','Medium','Probability benchmark','Hard constant baselines are weak probability comparators.','Added training prevalence constant for Brier comparison.','Hard heuristic scores are not probabilities.'),
('A09','Medium','Model diversity','Two models alone do not test nonlinear ensemble behavior.','Added bounded RF and GB searches using same partitions and scoring.','Search budgets differ; no universal family ranking.'),
('A10','High','No calibration evidence','Brier and displayed percentages do not establish calibration.','Added nested-search sigmoid calibration ensembles and fixed-bin reliability diagnostics.','Small test bins; ensemble effect confounds pure recalibration effect.'),
('A11','High','Subgroup fairness','No sex, address or school error assessment existed.','Added denominators, recall and FPR with Wilson intervals.','No fairness certification, causal analysis or mitigation.'),
('A12','Medium','Sensitive predictors','Private, health and proxy inputs create use concerns.','Retuned reduced 15-feature sensitivity scenario.','Removal does not eliminate proxies or establish fairness.'),
('A13','Medium','Prior-failure dependence','Unclear whether other information adds predictive value.','Added no-failures ablation and simple-rule comparison.','No causal effect inferred.'),
('A14','Medium','Threshold selection','F2 search at 0.5 may hide workload trade-offs.','Added descriptive 0.1-0.9 test sensitivity curves.','No test-based threshold tuning; capacity study pending.'),
('A15','Medium','Paired uncertainty','Ranking differences had point estimates only.','2,000 paired stratified bootstraps; exact LR-DT McNemar test.','Intervals condition on fixed models/prevalence, omit cluster/retraining uncertainty.'),
('A16','Medium','Fold independence','Repeated folds overlap in fit rows and students.','Means and sample SD only; no naive fold-based significance test.','External replication remains needed.'),
('A17','Medium','Importance bias','Training impurity can favor split-rich inputs.','Added raw-feature AP permutation on outer validation folds.','Correlation and out-of-distribution permutations remain limitations.'),
('A18','Medium','Explanation stability','One fitted coefficient/tree ranking is unstable on small data.','Saved per-fold LR coefficients and validation permutation values.','No causal or intervention interpretation.'),
('A19','Medium','Odds ratio units','Numeric and categorical coefficients have different units.','Clarified per-training-SD effects and omitted categorical references.','No conventional unpenalized inferential CI claimed.'),
('A20','Medium','Ordinal codes','LR treats ordinal steps as equally spaced.','Preserved actual encoding and stated assumption.','Alternative categorical/spline coding is a possible future study.'),
('A21','High','External validation','No independent school/cohort evaluation.','Scope limited; public future benchmark suitability documented.','Requires compatible independent data; not repairable with random resampling.'),
('A22','High','Temporal validation','Random split does not test future cohorts.','Explained cutoff and cohort validation requirements; assessed OULAD compatibility.','New temporal data needed; OULAD is a separate task.'),
('A23','Medium','School clustering','Shared school/class context may overstate independence.','Reported assumptions; school subgroup counts retained.','Only two schools and no class IDs; no cluster-robust inference claimed.'),
('A24','Medium','Zero grades','38 zero grades may mix absence/withdrawal/achievement.','Retained original target and explicitly reported ambiguity.','Administrative meaning needs source confirmation.'),
('A25','Medium','Dataset identity','UCI summary has 649 language records versus 395 mathematics rows.','Verified actual shape, hash, labels, missingness and full-row duplicates.','No mathematics/language pooling or false external validation.'),
('A26','Medium','Novelty','Two standard algorithms and an app offer limited algorithmic contribution.','Reframed as reproducibility and sensitivity audit with bounded claims.','Venue fit and sufficient significance require editorial assessment.'),
('A27','Medium','Literature currency','Original bibliography mostly predates 2023.','Added six relevant 2023-2026 works; DOI and official-source records saved.','Focused update, not a systematic literature review.'),
('A28','Medium','Environment claim','Paper says Python 3.12.14 while current environment is 3.12.10.','Reported observed interpreter and retained historical metadata separately.','Historical run environment not retroactively altered.'),
('A29','Medium','Prototype privacy','Current interface requests a name unnecessary for inference.','Inspected session/code behavior; recommended data minimization.','App is not modified or represented as validated deployment.'),
('A30','High','Unsupported declarations','Funding/conflicts/ethics/repository placeholders were unresolved.','Removed placeholders and invented acknowledgment; tracked author actions separately.','Authors must provide actual declarations and archive URL.'),
('A31','High','Authorship and biographies','Author identity must remain and biographies are required by Access.','Names/order/affiliation/correspondence preserved; no biographies invented.','All authors must supply approved biographies and verify identity details.'),
('A32','Medium','AI disclosure','Original AI declaration was a placeholder.','Factual acknowledgment describes AI assistance and cites the system.','Authors must approve disclosure and verify all assisted material.'),
('A33','Medium','Formatting and equations','Original PDF had large blank areas and was not the Access template.','Built editable DOCX from official template; added native equations, numbered figures/tables.','Final Word/PDF layout and content checked; submission still awaits author actions.'),
('A34','Low','Unknown categories','Ignored one-hot levels can encode like a reference category.','Documented pipeline behavior and inspected application checks.','Unknown cohort categories and range drift require deployment validation.'),
]
def support():
    # Separate human-readable supporting documents, preserving detailed numerical CSVs.
    m={r['model']:r for r in rows('heldout_metrics.csv')}
    protocol=json.loads((B/'results/protocol.json').read_text());env=json.loads((B/'results/environment.json').read_text())
    audit=['# Technical audit report','Review date: 1 November 2026. All nine original PDF pages and the available source, saved models, predictions, metadata, tests, and current interface were inspected. Severity denotes impact on claim validity; it is not a publication acceptance prediction.']
    for i,se,title,why,fix,left in ISSUES:audit.extend([f'## {i} {title}',f'Severity: {se}. {why}',f'Action and evidence: {fix}',f'Residual requirement: {left}'])
    audit.extend(['## What was already correct','The original manuscript already described retrospective scope, no test threshold tuning, absence of fairness/calibration analysis, and the Always-At-Risk F2 limitation. These were not newly discovered code defects. The title remained inconsistent with its careful text. Pipeline isolation, grade exclusion, class-1 orientation, test confusion matrices, AP definition, class weighting, and coefficient units were implemented correctly. The original 39-column encoding and saved probabilities reproduced.'])
    (B/'Technical_Audit.md').write_text('\n\n'.join(audit),encoding='utf-8')
    exp=['# Experiment report','All numbers below are executed results. Extensions are exploratory. The original test cohort was already known; no new holdout is claimed.','## Protocol',json.dumps(protocol,indent=2),'## Preserved original experiment','Both original models reproduce saved probabilities to maximum absolute difference 1.1102230246251565e-16. The original DT default and 0.5 threshold are retained. See results/reproduction_checks.json and frozen_split.json.','## Executed analyses','Original 16-candidate LR and 60-candidate DT searches; four-candidate RF and GB searches; ten nested outer folds with four model families and four baselines; LR/DT retuned ablations for no absences, reduced personal attributes, and no failures; nested-search sigmoid calibration ensembles; 2,000 paired class-stratified bootstraps; exact McNemar; three subgroup slices; threshold curves; raw-feature outer-validation permutation and coefficient stability.','## Actual held-out results']
    headers=['Model','Accuracy','Precision','Recall','F1','F2','AUC','AP','Brier','Flags']
    exp.extend(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers)])
    for n,r in m.items():exp.append('| '+' | '.join([n]+[num(r[k]) for k in ['accuracy','precision','recall','f1','f2','roc_auc','average_precision','brier_score']]+[r['flags']])+' |')
    nf=rows('nested_fold_metrics.csv')
    exp.extend(['## Nested outer-fold results','The ten fold scores overlap and are dependent. Mean and sample SD are descriptive; they are not test-set results or independent-replicate confidence intervals.','| Feature subset | Model | F2 mean | F2 SD | AUC mean |','|---|---|---|---|---|'])
    for s,n in sorted(set((r['subset'],r['model']) for r in nf)):
        rr=[r for r in nf if r['subset']==s and r['model']==n];v=[float(r['f2']) for r in rr];a=[float(r['roc_auc']) for r in rr]
        exp.append(f'| {s} | {n} | {statistics.mean(v):.4f} | {statistics.stdev(v):.4f} | {statistics.mean(a):.4f} |')
    exp.extend(['## Statistical comparisons',json.dumps(json.loads((B/'results/mcnemar.json').read_text()),indent=2),'Paired differences and percentile limits are in paired_differences.csv. Metric intervals condition on observed class counts and fixed fitted models. No cluster adjustment, model-refitting bootstrap or multiplicity-adjusted confirmatory significance claim is made.','## Interpretation','F2 rewards broad referral; compare both precision and workload with Always-At-Risk. Rank metrics and Brier measure different properties. The prevalence baseline is the appropriate constant probability comparison. Calibration ensembles change base fits and averaging; their performance change is not solely a calibration effect. Ablations are predictive sensitivity tests. Small subgroup denominators prevent certification of fairness.','## Not performed','No external or prospective cohort validation, prediction-cutoff reconstruction, OULAD training, Portuguese-subject transfer, operational intervention, teacher usability trial, fairness mitigation, Explainable Boosting Machine, SHAP study, or ordinal recoding experiment was performed. These are neither implicit successes nor fabricated pending results.','## Output map','heldout_metrics.csv includes all completed variants; nested_fold_metrics.csv and nested_predictions.csv contain the repeated nested runs; subgroups.csv includes denominators and Wilson intervals; calibration_bins.csv includes bin counts and observed-rate intervals; bootstrap_intervals.csv contains eight metric intervals for the four model families. Every figure is generated by make_figures.py from those outputs.'])
    (B/'Experiment_Report.md').write_text('\n\n'.join(exp),encoding='utf-8')
    repro=['# Reproducibility report','Run date: 1 November 2026, Asia/Calcutta. Dataset: UCI mathematics file, CC BY 4.0. No synthetic data. Original source and artifacts remain in their original directories; new results are written only under publication.','## Observed environment',json.dumps(env,indent=2),'## Commands from the project root','```powershell\n.venv/Scripts/python.exe publication/source/run_experiments.py\n.venv/Scripts/python.exe publication/source/make_figures.py\n.venv/Scripts/python.exe -m pytest -q --basetemp=publication/review/pytest-new-run\n```','Use a fresh, nonexistent test temporary directory inside the workspace and set TEMP and TMP to a writable workspace location when the restricted default Windows temp directory is unavailable. The first test attempt had three temp-directory setup errors; the second used a writable directory and passed all 27 tests, with the expected historical-source warning.','## Artifact authoring','The bundled Codex Python is used for DOCX authoring and PDF rasterization. It requires python-docx, pypdfium2 and Pillow. Run source/build_documents.py to rebuild both DOCXs and Markdown; run source/export_word.ps1 with Microsoft Word installed to export the PDFs; run source/render_pdf.py for the page images used in QA. The packaged render_docx.py was attempted and failed because LibreOffice is unavailable; Word was used as the native fallback.','## Portable reproduction','The source bundle includes a standalone project copy under reproducibility/project, with src/, data/, original model metadata and predictions needed for exact comparison. The runner detects that it is in that copied project using its source location. Place the publication source directory in project/publication/source, as packaged, and run from project. Install the scientific requirements in reproducibility/requirements-experiments.txt in an isolated Python 3.12 environment. The large original app lockfile is retained separately for app reconstruction; its historic package versions may require an appropriate index.','## Protocol details','Read results/protocol.json for grids, seeds, nested split logic, calibration and bootstrap design. frozen_split.json preserves the original 316/79 row IDs. nested_folds.json preserves every outer fit/validation ID; inner folds are deterministic from their fitting row order and seed 42. Pipeline preprocessing and weighting are refitted within fitting partitions. No test-based threshold, feature or final-model choice is made.','## Integrity checks','SHA256SUMS.json records final deliverables, source files, data and experiment artifacts. Reproduction checks assert row order and original probabilities before extensions run. No external data or network connection is necessary for experiments; verify_references.py is the optional network-dependent bibliography audit. Joblib artifacts must be loaded only from this trusted generated package.','## Hardware and repeatability','All estimator fits use n_jobs=1. Runtime is recorded in environment.json, not treated as a portable performance benchmark. Floating-point differences across libraries or platforms may occur. The scripted probability comparison uses absolute and relative tolerance 1e-12. Figure rendering may differ slightly with installed fonts.']
    (B/'Reproducibility_Report.md').write_text('\n\n'.join(repro),encoding='utf-8')
    checklist=['# Publication readiness checklist','Status: scientifically revised and locally reproducible; not yet submission-ready. This is not a guarantee of IEEE Access suitability or acceptance.','## Completed','- Original mathematics data and original predictions reproduced.\n- Title and claims restricted to retrospective classification.\n- Same original holdout, grade exclusion, fixed threshold, and original default preserved.\n- Baselines, ensembles, nested validation, ablations, uncertainty, calibration diagnostics, subgroups and stability executed.\n- Official IEEE Access Word template obtained; editable manuscript and matching exported PDF prepared.\n- Verified bibliography and factual AI-assistance acknowledgment added.\n- Full numerical tables, figure sources, code, configurations and provenance retained.','## Required author actions before submission','- Confirm spelling, exact institutional affiliation, authorship order, author contributions and corresponding-author email; no identity changes have been made.\n- Provide approved biographies for all three authors; IEEE Access requires biographies below the references. They were not invented.\n- Provide funding and conflict-of-interest declarations; neither absence of funding nor absence of conflicts is asserted.\n- Obtain the institution\'s actual ethics determination for secondary analysis; public data do not establish an exemption.\n- Review every AI-assisted section and script, approve the AI disclosure and verify all results.\n- Publish a versioned, licensed code/data archive with a stable URL or DOI and replace the local-package availability statement with the actual archive citation. The authors must choose a code license and confirm redistribution rights.\n- Confirm corresponding-author account, public populated ORCID, coauthor consent, and absence of simultaneous submission.\n- Resolve the modest novelty and venue-fit concern: the work is an audit on one small historical benchmark, with no algorithmic novelty.\n- Decide whether a fresh independent cohort and a timestamped prediction design are required to make the intended contribution sufficient. Without them, maintain all retrospective and exploratory qualifications.\n- Run the journal\'s final file/metadata checks and select 3-10 keywords; confirm PDF/source content after inserting biographies and declarations.','## Strongly recommended research before operational claims','Independent secondary-school cohort; prospective cutoff snapshots; time-separated evaluation; larger subgroup samples; support-capacity and cost elicitation; educator usability and intervention outcome studies. None can be inferred from current software checks.','## Current IEEE Access requirements consulted','https://ieeeaccess.ieee.org/authors/submission-guidelines/ (accessed 1 November 2026). The page requires the official double-column single-spaced template, matching source/PDF files, AI disclosure and citation, author biographies, ORCID, and accurate references. No submission or communication with the journal has been performed.']
    (B/'Publication_Readiness_Checklist.md').write_text('\n\n'.join(checklist),encoding='utf-8')
    # One editable companion report, with readable pages and no long prose tables.
    d=Document();font_black(d)
    for s in d.sections:s.top_margin=Inches(.7);s.bottom_margin=Inches(.7);s.left_margin=Inches(.75);s.right_margin=Inches(.75)
    for st in d.styles:
        if st.type==1:st.font.name='Arial'
    d.styles['Title'].font.size=Pt(22)
    norm=d.styles['Normal'];norm.font.name='Arial';norm.font.size=Pt(10);norm.paragraph_format.space_after=Pt(6)
    d.add_paragraph('Research Revision Supporting Reports','Title')
    d.add_paragraph('Student Academic Risk Classification\n1 November 2026')
    d.add_paragraph('The original experiment reproduces. The revised evidence remains retrospective and exploratory, with unresolved author declarations and independent validation requirements. This document contains the technical audit, experiment record, reproduction instructions and submission checklist. Detailed numerical outputs remain in the accompanying CSV files.')
    for name,parts in [('Technical Audit',audit),('Experiment Report',exp),('Reproducibility Report',repro),('Publication Readiness Checklist',checklist)]:
        d.add_heading(name,0)
        j=1
        while j<len(parts):
            txt=parts[j];j+=1
            if txt.startswith('## '):d.add_heading(txt[3:],1)
            elif txt.startswith('|'):
                lines=[txt]
                while j<len(parts) and parts[j].startswith('|'):lines.append(parts[j]);j+=1
                values=[[v.strip() for v in line.strip('|').split('|')] for line in lines]
                table(d,'',values[0],[v for v in values[1:] if not all(set(x)<=set('-: ') for x in v)],6.9)
            elif txt.startswith('{'):
                ob=json.loads(txt)
                if 'grids' in ob:
                    d.add_paragraph('Outer evaluation: '+ob['outer']+'. Inner search: '+ob['inner']+'.')
                    for model,grid in ob['grids'].items():d.add_paragraph(model.replace('_',' ')+': '+ '; '.join(k.replace('classifier__','')+'='+str(v) for k,v in grid.items()))
                    d.add_paragraph('Calibration: '+ob['calibration']+'. Bootstrap: '+ob['bootstrap']+'.')
                elif 'python' in ob:
                    d.add_paragraph('Python '+ob['python'].split()[0]+'. '+ob['platform']+'.')
                    d.add_paragraph('; '.join(k+' '+v for k,v in ob['packages'].items())+'.')
                    d.add_paragraph('Recorded experiment elapsed time: '+str(round(ob['elapsed_seconds'],1))+' seconds.')
                else:d.add_paragraph('; '.join(k.replace('_',' ')+' = '+str(v) for k,v in ob.items())+'.')
            elif txt.startswith('```'):
                p=d.add_paragraph(txt.replace('```powershell\n','').replace('```',''));p.style='No Spacing'
                for r in p.runs:r.font.name='Consolas';r.font.size=Pt(8)
            else:
                for paragraph in txt.split('\n'):
                    if paragraph.startswith('- '):d.add_paragraph(paragraph[2:],style='List Bullet')
                    elif paragraph:
                        p=d.add_paragraph(paragraph)
                        if paragraph.startswith(('Severity:','Action and evidence:')):keep(p)
    footer(d);d.core_properties.title='Research Revision Supporting Reports';d.core_properties.author='';d.save(B/'Supporting_Reports.docx')
    print('Supporting reports built')
if __name__=='__main__':manuscript();support()


