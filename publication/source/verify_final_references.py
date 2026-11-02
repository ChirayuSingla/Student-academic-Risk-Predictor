"""Refresh primary registry records; preserve failures as unresolved evidence."""
from pathlib import Path
import sys,re,json,urllib.request,urllib.parse,concurrent.futures,hashlib,time
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'source'))
from manuscript_content import REFERENCES
O=B/'final';O.mkdir(exist_ok=True)
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'AcademicReproducibilityAudit/1.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=35) as r:return r.read()
def one(ref):
    m=re.search(r'doi: (.+?)\.(?: \[|$)',ref)
    doi=m.group(1) if m else None
    out={'citation':ref,'doi':doi}
    try:
        if doi:
            endpoint=('https://api.datacite.org/dois/' if doi.startswith('10.24432') else 'https://api.crossref.org/works/')+urllib.parse.quote(doi,safe='')
            raw=json.loads(fetch(endpoint));meta=raw['data']['attributes'] if doi.startswith('10.24432') else raw['message']
            out.update(status='registry_retrieved',source=endpoint,metadata=meta)
            if not doi.startswith('10.24432'):
                title=(meta.get('title') or [''])[0]
                norm=lambda s: re.sub('[^a-z0-9]','',s.lower())
                out['title_matches']=norm(title) in norm(ref)
                out['registered_authors']=[(' '.join([a.get('given',''),a.get('family','')])).strip() for a in meta.get('author',[])]
                out['registered_dates']={k:meta[k] for k in ['published','published-print','published-online'] if k in meta}
                out['correction_or_update_records']=meta.get('update-to',[])
        else:
            url=re.search(r'https://[^\s]+',ref).group().rstrip('.')
            data=fetch(url);out.update(status='primary_page_retrieved',source=url,bytes=len(data))
    except Exception as e:out.update(status='unresolved_retrieval',error=str(e))
    return out
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:records=list(ex.map(one,REFERENCES))
record={'date':'2026-11-02','records':records,'scope':'Registry metadata and primary pages; retrieval is not a full-text review or proof of no retraction. Author review remains required.'}
(O/'reference_verification.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
for r in records:print(r['status'],r.get('doi'),r.get('title_matches',''),r.get('error',''))
try:
    official=fetch('https://ieeeaccess.ieee.org/wp-content/uploads/2025/08/Access-Template-2024.docx')
    local=(B/'template/Access-Template-2024.docx').read_bytes()
    assert official==local
    (O/'template_verification.json').write_text(json.dumps({'official_url':'https://ieeeaccess.ieee.org/wp-content/uploads/2025/08/Access-Template-2024.docx','sha256':hashlib.sha256(local).hexdigest(),'byte_identical':True},indent=2))
    print('Official template byte-identical')
except Exception as e:
    (O/'template_verification.json').write_text(json.dumps({'status':'unresolved_live_template_comparison','error':str(e)}))
schema=fetch('https://raw.githubusercontent.com/citation-file-format/citation-file-format/1.2.0/schema.json')
(O/'cff-schema-1.2.0.json').write_bytes(schema)
