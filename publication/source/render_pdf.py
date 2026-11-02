from pathlib import Path
import sys,subprocess,concurrent.futures
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw
src=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(parents=True,exist_ok=True)
if len(sys.argv)>3:
    pdf=pdfium.PdfDocument(str(src));p=pdf[int(sys.argv[3])];bitmap=p.render(scale=1.7)
    bitmap.to_pil().copy().save(dest/f'page-{int(sys.argv[3])+1:02}.png')
    sys.exit(0)
pdf=pdfium.PdfDocument(str(src));count=len(pdf);pdf.close()
def render_one(i):
    # Isolated PDFium processes avoid a font-cache defect seen across Word-exported pages.
    subprocess.run([sys.executable,str(Path(__file__).resolve()),str(src),str(dest),str(i)],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render_one,range(count)))
thumbs=[]
for i in range(count):
    im=Image.open(dest/f'page-{i+1:02}.png')
    t=im.copy();t.thumbnail((330,470));can=Image.new('RGB',(350,500),'#ddd');can.paste(t,((350-t.width)//2,20));ImageDraw.Draw(can).text((12,480),str(i+1),fill='black');thumbs.append(can)
for j in range(0,len(thumbs),6):
    page=Image.new('RGB',(1050,1000),'white')
    for k,t in enumerate(thumbs[j:j+6]):page.paste(t,((k%3)*350,(k//3)*500))
    page.save(dest/f'contact-{j//6+1}.png')
print('Rendered',count,'pages',dest)
