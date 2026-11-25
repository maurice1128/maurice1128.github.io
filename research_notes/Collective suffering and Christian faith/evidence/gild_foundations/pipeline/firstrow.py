# Re-OCR the first row of each page with the crop extended upward (top rule often absent)
import sys, json, os, subprocess
from PIL import Image
d=json.load(open(sys.argv[1])); imgdir=sys.argv[2]; lo,hi=int(sys.argv[3]),int(sys.argv[4])
out={}
for k,v in d.items():
    if 'rows' not in v or not v['rows'] or not (lo<=int(k)<=hi): continue
    pil=Image.open(os.path.join(imgdir,'r-%s.png'%k)).convert('L')
    r=v['rows'][0]; vv=v['v']
    y0=max(0,r['y0']-70)
    cells=[]
    for c in range(5):
        tmp=os.path.join(imgdir,'_fr%d.png'%lo)
        pil.crop((vv[c]+6,y0,vv[c+1]-6,r['y1']-6)).save(tmp)
        cells.append(subprocess.run(['tesseract',tmp,'-','--psm','6'],capture_output=True,text=True).stdout.strip())
    out[k]=cells
json.dump(out,open(sys.argv[5],'w'),indent=1)
