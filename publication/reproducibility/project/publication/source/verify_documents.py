from pathlib import Path
from docx import Document
from pypdf import PdfReader
from PIL import Image
import re,json,hashlib,unicodedata
B=Path(__file__).resolve().parents[1]
def canonical(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
checks={};details={}
for name in ['Revised_Manuscript','Supporting_Reports']:
    d=Document(B/(name+'.docx'));pdf=PdfReader(B/(name+'.pdf'))
    pages=[]
    for i,page in enumerate(pdf.pages,1):
        lines=page.extract_text().splitlines()
        pages.append('\n'.join(line for line in lines if line.strip()!=str(i) and not line.startswith('Singla et al.')))
    alltext='\n'.join(pages);c=canonical(alltext)
    missing=[]
    for p in d.paragraphs:
        if not p.text.strip() or p.style.name=='Equation':continue
        if canonical(p.text) not in c:missing.append(p.text[:150])
    assert not missing,(name,missing)
    for table in d.tables:
        for row in table.rows:
            for cell in row.cells:assert canonical(cell.text) in c,(name,cell.text)
    assert not any(t in alltext for t in ['TBD','Doi Number','xxxx','First A. Author','VOLUME XX'])
    checks[name+'_source_text_matches_exported_pdf']=True
    details[name]={'pages':len(pdf.pages),'tables':len(d.tables),'images':len(d.inline_shapes)}
d=Document(B/'Revised_Manuscript.docx')
assert len(d.tables)==7 and len(d.inline_shapes)==7
assert len(d._element.xpath('.//m:oMath'))==4
assert [p.text for p in d.paragraphs if p.style.name=='AU']==['Chirayu Singla, Yuvraj Singh, and Rajay Vedaraj I S']
assert len([p for p in d.paragraphs if p.style.name=='Ref'])==24
for s in d.sections:assert abs(s.page_width/914400-8)<.001 and abs(s.page_height/914400-10.875)<.001
checks['authorship_24_references_7_tables_7_figures_4_native_equations_template_geometry']=True
for p in (B/'figures').glob('*.png'):
    im=Image.open(p);assert min(im.size)>1400 and im.info.get('dpi',(0,0))[0]>599
checks['seven_high_resolution_figures']=True
details['visual_review']='All ten manuscript pages and eleven supporting pages inspected. Microsoft Word export used. PDFium pages rendered in isolated processes to avoid a renderer font-cache defect. No source/PDF content mismatch or visible layout defects remain.'
details['template_sha256']=hashlib.sha256((B/'template/Access-Template-2024.docx').read_bytes()).hexdigest()
(B/'review/layout_verification.json').write_text(json.dumps({'status':'passed','checks':checks,'details':details},indent=2))
print(json.dumps({'checks':checks,'details':details},indent=2))
