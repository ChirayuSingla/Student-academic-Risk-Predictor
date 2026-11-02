"""Check final source/PDF text parity, geometry, assets and historical integrity."""
from pathlib import Path
import re,json,unicodedata,hashlib,subprocess,ast,csv
from docx import Document
from pypdf import PdfReader
B=Path(__file__).resolve().parents[1];ROOT=B.parent;O=B/'final'
canonical=lambda s:re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
d=Document(B/'Final_IEEE_Access_Manuscript.docx');r=PdfReader(B/'Final_IEEE_Access_Manuscript.pdf')
text='\n'.join('\n'.join(line for line in p.extract_text().splitlines() if line.strip()!=str(i) and not line.startswith('Singla et al.')) for i,p in enumerate(r.pages,1));c=canonical(text)
missing=[p.text for p in d.paragraphs if p.text.strip() and p.style.name!='Equation' and canonical(p.text) not in c]
assert not missing,missing
for t in d.tables:
    for row in t.rows:
        for cell in row.cells:assert canonical(cell.text) in c,cell.text
for i,t in enumerate(d.tables,1):
    saved=list(csv.reader((B/f'tables/Table_{i:02}.csv').open(encoding='utf-8-sig')))
    saved=[[v.replace('__sigmoid',' sigmoid') for v in row] for row in saved]
    assert saved==[[cell.text for cell in row.cells] for row in t.rows],i
assert len(d.tables)==7 and len(d.inline_shapes)==7 and len(d._element.xpath('.//m:oMath'))==4
assert len([p for p in d.paragraphs if p.style.name=='Ref'])==24
assert [p.text for p in d.paragraphs if p.style.name=='AU']==['Chirayu Singla, Yuvraj Singh, and Rajay Vedaraj I S']
for s in d.sections:
    assert abs(s.page_width/914400-8)<.001 and abs(s.page_height/914400-10.875)<.001
assert not any(v in text for v in ['TBD','Doi Number','First A. Author','VOLUME XX'])
assert all((B/('Final_IEEE_Access_Manuscript'+suffix)).stat().st_size<40_000_000 for suffix in ['.docx','.pdf'])
support={}
for name in ['Final_Technical_Audit','Final_Reproducibility_Report','IEEE_Access_Submission_Checklist','Experiment_Results_Appendix']:
    rr=PdfReader(B/(name+'.pdf'));tt='\n'.join(p.extract_text() for p in rr.pages)
    assert tt.strip() and '\ufffd' not in tt
    support[name]={'pages':len(rr.pages),'bytes':(B/(name+'.pdf')).stat().st_size}
# Every original model, snapshot and original data file remains byte-identical to Git HEAD.
preserved=[]
for folder in ['models','data']:
    names=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD',folder],cwd=ROOT,text=True).splitlines()
    for n in names:
        historical=subprocess.check_output(['git','show','HEAD:'+n],cwd=ROOT)
        assert historical==(ROOT/n).read_bytes(),n
        preserved.append(n)
inventory=[]
for folder in ['src','scripts','tests','notebooks','data','models','results','publication/source','publication/results']:
    for p in sorted((ROOT/folder).rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
        inventory.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'repository_inventory.json').write_text(json.dumps(inventory,indent=2))
out={'status':'passed','manuscript':{'pages':len(r.pages),'tables':7,'figures':7,'native_equations':4,'references':24,'source_pdf_text_and_cells_match':True,'official_template_geometry_preserved':True},'supporting_reports':support,'historical_data_model_and_snapshot_files_unchanged':len(preserved),'rendering':'Packaged render_docx.py unavailable because LibreOffice is absent. Microsoft Word export succeeded; PDFium rendered page PNGs in publication/review for visual review.','required_author_actions':['all-author biographies','funding and conflicts','institutional ethics determination','ORCID and corresponding-author confirmation','licence approval','final review and consent'],'latex':'No original LaTeX manuscript source available; no .tex fabricated.'}
(O/'document_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
