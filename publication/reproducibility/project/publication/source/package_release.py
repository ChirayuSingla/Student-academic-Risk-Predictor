from pathlib import Path
import re,json,hashlib,shutil,csv,zipfile
B=Path(__file__).resolve().parents[1];ROOT=B.parent
meta=json.loads((B/'review/reference_metadata.json').read_text())
report=['# Reference verification record','Checked 1 November 2026. The update is a focused literature search, not a systematic review. DOI registration metadata and official publisher/repository pages were used; no bibliographic field was inferred from an AI-generated citation. Full returned DOI metadata are in review/reference_metadata.json. An HTTP 429 denotes registry throttling, not an invalid DOI; UCI uses DataCite rather than Crossref.','## New literature used','- Boujmiraz, Darhmaoui and Drissi el maliani, 2026: DOI 10.1016/j.caeai.2026.100548; publisher abstract and Crossref agree on title, authors, year, volume 10 and article 100548. Supports the established breadth of ML and XAI work, not a claim of superiority for our models.\n- Santos and Henriques, 2023: DOI 10.1016/j.caeai.2023.100175; publisher abstract and Crossref verified. Supports evaluation at course-completion cutoffs.\n- Kleter, Matzat and Conijn, 2024: DOI 10.1109/TLT.2024.3443079; official author-institution page and Crossref verified. Page ranges conflict: the author portal reports 2183-2194 while registry metadata report 2129-2140. Pagination is deliberately omitted from the manuscript citation rather than guessed.\n- Gunasekara and Saarela, 2025: DOI 10.1109/ACCESS.2025.3643645; IEEE publication metadata and Crossref verified, volume 13, pages 214387-214408. The review identifies a shortage of quantified explanation evaluation.\n- Idowu, 2024: DOI 10.1007/s40593-023-00389-4; Springer official article and Crossref verified. The DOI year 2023 differs from the final volume publication year 2024; citation uses the final volume year.\n- Pham, Pham Ngoc and Nguyen-Duc, 2025: DOI 10.1016/j.jss.2024.112244; official publisher search record and Crossref verified, volume 219, article 112244. DOI year 2024 is not the issue year.','## Original references audited','The original numbering below refers to the supplied PDF; the revised bibliography is renumbered by first appearance. Foundational citations were not labeled obsolete solely because they are old. Removed references are generally valid but no longer necessary for the focused manuscript.','| Original | Verification and decision |','|---|---|']
old=[
('Romero and Ventura','10.1002/widm.1355','Valid survey; replaced with more recent focused reviews.'),
('Cortez dataset','10.24432/C5TG7T','Verified on UCI official page, CC BY 4.0; retained.'),
('Ewais et al.','10.1038/s41598-026-48426-1','Verified on Scientific Reports official page, 24 April 2026, vol. 16, article 19944; retained. Six regression models, not our binary task.'),
('Kapoor and Narayanan','10.1016/j.patter.2023.100804','Retained leakage reference.'),
('Cortez and Silva',None,'Title/authors/year and conference verified through UCI source attribution. Repository link retained. No claimed fresh full-text review; page range retained from supplied bibliography.'),
('Marbouti et al.','10.1016/j.compedu.2016.09.005','Valid; replaced with recent explicitly cutoff-based work.'),
('Altman and Royston','10.1136/bmj.332.7549.1080','Verified BMJ official PDF and author archive; not needed in focused bibliography.'),
('Rudin','10.1038/s42256-019-0048-x','Retained interpretability motivation.'),
('Khosravi et al.','10.1016/j.caeai.2022.100074','Retained education stakeholder context.'),
('Cawley and Talbot',None,'Verified on JMLR official page, vol. 11, pages 2079-2107; retained.'),
('Pedregosa et al.',None,'Verified on JMLR official page, vol. 12, pages 2825-2830; retained.'),
('He and Garcia','10.1109/TKDE.2008.239','Retained weighting/imbalance context; no claim that weighting improves fairness.'),
('Fawcett','10.1016/j.patrec.2005.10.010','Valid; removed to reduce redundant metric citations.'),
('Saito and Rehmsmeier','10.1371/journal.pone.0118432','Retained precision-recall context.'),
('Brier','10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2','Retained original probability-error definition.'),
('Hosmer et al.','10.1002/9781118548387','Verified title, authors and 2013 date; retained third-edition reference from supplied manuscript.'),
('Breiman et al.',None,'1984 book citation consistent with supplied source; not independently verified against a publisher copy here and not retained. This is not classified as fabricated.'),
('Harris et al.','10.1038/s41586-020-2649-2','Valid software citation; environment versions recorded separately instead.'),
('McKinney','10.25080/Majora-92bf1922-00a','Valid software citation; omitted to focus bibliography.'),
('Hunter','10.1109/MCSE.2007.55','Valid software citation; omitted to focus bibliography.'),
('Strobl et al.','10.1186/1471-2105-8-25','Retained importance-bias caution.'),
('Shmueli','10.1214/10-STS330','Verified official Statistical Science PDF, title and author; retained prediction/causation distinction.'),
('Streamlit',None,'Verified official https://docs.streamlit.io; retained and access date updated.'),
('Joblib',None,'Software implementation inspected; documentation URL is plausible but not independently browsed; citation removed.'),
('Slade and Prinsloo','10.1177/0002764213479366','Valid; registry splits title and subtitle. Replaced with recent fairness sources.'),
('Drachsler and Greller','10.1145/2883851.2883893','Valid; registry splits title/subtitle. Omitted in focused bibliography.'),
('Baker and Hawn','10.1007/s40593-021-00285-9','Verified final 2022 volume despite DOI 2021; retained.')]
for i,(name,doi,decision) in enumerate(old,1):
    status=meta.get(doi,{}).get('status')
    evidence=('Crossref metadata matched; ' if status==200 else '')
    report.append(f'| [{i}] {name} | {evidence}{decision} |')
report.extend(['## Additional source checks','OULAD: official Scientific Data article/PDF, DOI 10.1038/sdata.2017.171, confirms J. Kuzilek, M. Hlosta and Z. Zdrahal, volume 4, article 170171, CC BY 4.0. It is proposed as a separate temporal benchmark, not used for an executed external validation. UCI repository is cited as the dataset authority. OpenAI is cited solely to disclose the assistance actually used in this revision.','## Search record','Queries combined student academic risk/performance, early warning, interpretable/explainable machine learning, fairness, and temporal/generalizability with 2023-2026. IEEE Xplore, Springer, Elsevier, ACM-related publisher material, Nature and official author-institution pages were prioritized. Not every publisher allowed full-page access; claims were restricted to verified abstracts/metadata. Several unrelated or low-relevance results were excluded. No number of screened papers is invented.','## Retraction and access limits','No retraction statement was observed in the official pages consulted. This is not an exhaustive Crossmark/retraction-database clearance. Authors should perform the journal-required final reference-status check immediately before submission. Network failures and registry throttling are retained in the metadata rather than presented as successful retrievals.','## Official sources','https://ieeeaccess.ieee.org/authors/submission-guidelines/\nhttps://archive.ics.uci.edu/dataset/320/student+performance\nhttps://www.nature.com/articles/s41598-026-48426-1\nhttps://ieeexplore.ieee.org/document/11298693\nhttps://link.springer.com/article/10.1007/s40593-023-00389-4\nhttps://research.tue.nl/en/publications/boundary-conditions-of-generalizing-predictive-models-for-academi/\nhttps://www.nature.com/articles/sdata2017171.pdf'])
(B/'Reference_Verification.md').write_text('\n\n'.join(report),encoding='utf-8')
# Export each actual manuscript table as editable CSV.
td=B/'tables';td.mkdir(exist_ok=True)
blocks=json.loads((B/'source/manuscript_blocks.json').read_text())
for i,b in enumerate([x for x in blocks if x[0]=='table'],1):
    with (td/f'Table_{i:02}.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(b[2]);w.writerows(b[3])
for file in (B/'results').glob('*.csv'):shutil.copy2(file,td/file.name)
# Standalone source project preserves the required paths and original comparison evidence.
P=B/'reproducibility/project';P.mkdir(parents=True,exist_ok=True)
for dirname in ['src','tests','data','models','notebooks','.streamlit']:
    shutil.copytree(ROOT/dirname,P/dirname,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for filename in ['app.py','README.md','requirements.txt','requirements-lock.txt','pytest.ini']:
    shutil.copy2(ROOT/filename,P/filename)
(P/'results').mkdir(exist_ok=True)
for file in (ROOT/'results').iterdir():
    if file.is_file() and file.suffix in ['.csv','.json','.md','.txt']:shutil.copy2(file,P/'results'/file.name)
shutil.copytree(ROOT/'results/figures',P/'results/figures',dirs_exist_ok=True)
shutil.copytree(B/'source',P/'publication/source',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(B/'template',P/'publication/template',dirs_exist_ok=True)
shutil.copytree(ROOT/'scripts',P/'scripts',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
req='numpy==2.2.6\npandas==2.3.3\nscipy==1.16.2\nscikit-learn==1.7.2\nmatplotlib==3.10.7\njoblib==1.5.2\n'
(B/'reproducibility/requirements-experiments.txt').write_text(req)
(B/'reproducibility/requirements-authoring.txt').write_text('python-docx==1.2.0\npypdf==6.10.0\npypdfium2==5.14.0\nPillow==12.3.0\n')
(B/'reproducibility/DATA_LICENSE.md').write_text('Student Performance by Paulo Cortez (2008), original research with Alice M. G. Silva. UCI Machine Learning Repository, DOI 10.24432/C5TG7T. Data: https://archive.ics.uci.edu/dataset/320/student+performance. Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Mathematics file is unmodified. No code license is asserted on behalf of the authors.\n')
readme='''# Research paper revision package

Prepared 1 November 2026. Start with Revised_Manuscript.pdf or the editable DOCX. The manuscript uses the official IEEE Access template and confines conclusions to retrospective classification.

Supporting_Reports contains the 34-issue technical audit, experiment report, reproduction instructions and readiness checklist. Individual Markdown versions allow direct review. Reference_Verification.md records the original and new bibliography checks and retrieval limitations.

Seven figures are supplied as 600 dpi PNG and vector PDF/SVG. Tables contains the seven manuscript tables and complete numerical outputs. Results includes trained extension models, saved row-level probabilities, nested folds, search results, bootstrap intervals and verification records.

Reproducibility/project is a portable copy of the relevant original project and all new scripts. From that project directory install ../requirements-experiments.txt into a Python 3.12 environment, then run `python publication/source/run_experiments.py` and `python publication/source/make_figures.py`. The source scripts in the main package have the same content. Authoring dependencies are separate; Microsoft Word is needed for the exact DOCX-to-PDF export used here. Additional app/test dependencies are in the original lockfile.

The original experiment reproduced; 27 project tests passed and seven independent output checks passed. Calibration, ablation, subgroup and extra-model results are exploratory because the original test results were known. All tests of the original application are separate from evidence of educational effectiveness.

Submission is still pending: author biographies, funding/conflict and institutional ethics declarations, final author review, a versioned public code archive, ORCID/consent checks, and an assessment of venue fit. No approval, funding, lack of conflicts, or prospective validation has been invented. No submission has been made.
'''
(B/'README.md').write_text(readme,encoding='utf-8')
# Manifest excludes transient rendering/test material and itself.
manifest={}
for file in B.rglob('*'):
    if file.is_file() and ('review' not in file.relative_to(B).parts or file.name in ['reference_metadata.json','pytest.log','experiment_run.log','layout_verification.json']) and '__pycache__' not in file.parts and file.name not in ['SHA256SUMS.json','Research_Revision_Package.zip']:
        manifest[str(file.relative_to(B)).replace('\\','/')]=hashlib.sha256(file.read_bytes()).hexdigest()
(B/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(B/'Research_Revision_Package.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in B.rglob('*'):
        rel=file.relative_to(B)
        if not file.is_file() or file.name=='Research_Revision_Package.zip' or '__pycache__' in rel.parts:continue
        if 'review' in rel.parts and file.name not in ['reference_metadata.json','pytest.log','experiment_run.log','layout_verification.json']:continue
        z.write(file,str(rel))
print('Package files',len(manifest),'ZIP bytes',(B/'Research_Revision_Package.zip').stat().st_size)
