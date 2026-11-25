# Segment rotated Westlake appendix pages into table cells and OCR each cell.
import sys, os, json, subprocess, glob
import numpy as np
from PIL import Image
imgdir, outjson = sys.argv[1], sys.argv[2]
lo,hi=int(sys.argv[3]),int(sys.argv[4])
def grp(v, gap=3):
    g=[]
    for x in v:
        if g and x-g[-1][-1]<=gap: g[-1].append(x)
        else: g.append([x])
    return [(a[0],a[-1]) for a in g]
def ocr(im):
    tmp=os.path.join(imgdir,'_cell%d.png'%lo); im.save(tmp)
    r=subprocess.run(['tesseract',tmp,'-','--psm','6'],capture_output=True,text=True)
    return r.stdout.strip()
res=json.load(open(outjson)) if os.path.exists(outjson) else {}
for f in sorted(glob.glob(os.path.join(imgdir,'d-*.png'))):
    pdfp=int(f.split('-')[-1].split('.')[0]); key=str(pdfp)
    if key in res or not (lo<=pdfp<=hi): continue
    pil=Image.open(f).convert('L'); a=np.array(pil)<128; h,w=a.shape
    col=a.sum(0)/h
    v=[(x0+x1)//2 for x0,x1 in grp([x for x in range(w) if col[x]>0.45])]
    if len(v)<6 and len(v)>=3:
        T=[0,182,545,1410,1777,2213]
        best=None
        for x in v:
            for t in T:
                sh=x-t
                sc=sum(min(abs(y-(tt+sh)) for tt in T)<15 for y in v)
                if best is None or sc>best[0]: best=(sc,sh)
        sh=best[1]; nv=[]
        for tt in T:
            near=[y for y in v if abs(y-(tt+sh))<15]
            nv.append(near[0] if near else tt+sh)
        print(key,'interpolated',v,'->',nv); v=nv
    if len(v)<6:
        res[key]={'error':'vlines %s'%v}; print(key,'vlines',v); continue
    v=v[:6] if len(v)==6 else v
    def dil(s,k=3):
        d=s.copy()
        for i in range(1,k+1):
            d[i:]|=s[:-i]; d[:-i]|=s[i:]
        return d
    def hl(c):
        x0,x1=v[c]+5,v[c+1]-5
        sub=dil(a[:,x0:x1]).sum(1)/(x1-x0)
        return [(y0+y1)//2 for y0,y1 in grp([y for y in range(h) if sub[y]>0.9],gap=8)]
    L=[hl(c) for c in range(5)]
    cand=sorted(y for c in (1,2,3,4) for y in L[c])
    clusters=[]
    for y in cand:
        if clusters and y-clusters[-1][-1]<=14: clusters[-1].append(y)
        else: clusters.append([y])
    hb=[int(np.median(cl)) for cl in clusters if len(set(c for c in (1,2,3,4) for yy in L[c] if any(abs(yy-q)<=14 for q in cl)))>=2]
    if len(hb)<2:
        vl=a[:,v[0]-2:v[0]+3].any(1); ys=np.where(vl)[0]; hb=[int(ys.min()),int(ys.max())]+hb
    vl=a[:,v[1]-2:v[1]+3].sum(1)>=2; ys=np.where(vl)[0]; vt,vb=int(ys.min()),int(ys.max())
    hb=sorted(set(hb))
    if hb[0]-vt>40: hb=[vt]+hb
    if vb-hb[-1]>40: hb=hb+[vb]
    bounds=hb
    def certline_at(y):
        return any(abs(y-q)<=14 for q in L[0])
    rows=[]
    for i in range(len(bounds)-1):
        y0,y1=bounds[i],bounds[i+1]
        if y1-y0<25: continue
        # does a line in cert column also exist at y0? (certificate-level break)
        certline = certline_at(y0) if i>0 else True
        cells=[]
        for c in range(5):
            cell=pil.crop((v[c]+6,(max(0,y0-70) if i==0 else y0+6),v[c+1]-6,y1-6))
            cells.append(ocr(cell))
        rows.append({'y0':int(y0),'y1':int(y1),'certbreak':bool(certline),'cells':cells})
    res[key]={'v':v,'rows':rows}
    print(key,len(rows),flush=True)
    json.dump(res,open(outjson,'w'),indent=1)
json.dump(res,open(outjson,'w'),indent=1)
