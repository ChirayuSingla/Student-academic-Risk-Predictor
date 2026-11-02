from pathlib import Path
import json, requests, concurrent.futures
BASE=Path(__file__).resolve().parents[1]
dois=['10.1002/widm.1355','10.24432/C5TG7T','10.1038/s41598-026-48426-1','10.1016/j.patter.2023.100804','10.1016/j.compedu.2016.09.005','10.1136/bmj.332.7549.1080','10.1038/s42256-019-0048-x','10.1016/j.caeai.2022.100074','10.1109/TKDE.2008.239','10.1016/j.patrec.2005.10.010','10.1371/journal.pone.0118432','10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2','10.1002/9781118548387','10.1038/s41586-020-2649-2','10.25080/Majora-92bf1922-00a','10.1109/MCSE.2007.55','10.1186/1471-2105-8-25','10.1214/10-STS330','10.1177/0002764213479366','10.1145/2883851.2883893','10.1007/s40593-021-00285-9',
'10.1109/ACCESS.2025.3643645','10.1016/j.caeai.2026.100548','10.1016/j.caeai.2023.100175','10.1109/TLT.2024.3443079','10.1007/s40593-023-00389-4','10.1016/j.jss.2024.112244','10.5281/zenodo.10117682','10.1038/sdata.2017.171']
def get(doi):
    u='https://api.crossref.org/works/'+requests.utils.quote(doi,safe='')
    r=requests.get(u,timeout=40)
    return doi,{'url':u,'status':r.status_code,'metadata':r.json().get('message') if r.status_code==200 else None}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    out=dict(ex.map(get,dois))
(BASE/'review/reference_metadata.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for doi,r in out.items():
    m=r['metadata'] or {}
    print(doi,r['status'],m.get('title'),[(a.get('given'),a.get('family')) for a in m.get('author',[])[:7]],m.get('volume'),m.get('page'),m.get('article-number'),m.get('published',{}).get('date-parts'))
