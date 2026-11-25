# Make composite images of cert+place columns (4 pages side by side) for visual verification
import sys, glob, os, numpy as np
from PIL import Image, ImageDraw
imgdir, outdir = sys.argv[1], sys.argv[2]
def grp(v, gap=3):
    g=[]
    for x in v:
        if g and x-g[-1][-1]<=gap: g[-1].append(x)
        else: g.append([x])
    return [(a[0]+a[-1])//2 for a in g]
pages=list(range(162,263))
crops=[]
for p in pages:
    im=Image.open(os.path.join(imgdir,'d-%d.png'%p)).convert('L')
    a=np.array(im)<128; h,w=a.shape
    v=grp([x for x in range(w) if a[:,x].sum()/h>0.45])
    x0=(v[0] if v and v[0]<250 else 120)-5
    crop=im.crop((x0,0,x0+560,h))
    d=ImageDraw.Draw(crop); d.rectangle((0,0,140,40),fill=255); d.text((5,5),'PDF %d / p.%d'%(p,p-24),fill=0)
    crops.append(crop)
for i in range(0,len(crops),4):
    grp4=crops[i:i+4]
    W=sum(c.width for c in grp4)+10*len(grp4); H=max(c.height for c in grp4)
    out=Image.new('L',(W,H),255); x=0
    for c in grp4: out.paste(c,(x,0)); x+=c.width+10
    out=out.resize((int(W*0.62),int(H*0.62)))
    out.save(os.path.join(outdir,'s%03d.png'%(i//4)))
print('ok')
