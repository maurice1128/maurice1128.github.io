# Remove vertical shear (row rules slanted while column rules vertical)
import sys, glob, os, numpy as np
from PIL import Image
d=sys.argv[1]; lo,hi=int(sys.argv[2]),int(sys.argv[3])
for f in sorted(glob.glob(os.path.join(d,'r-*.png'))):
    p=int(f.split('-')[-1].split('.')[0])
    if not lo<=p<=hi: continue
    im=Image.open(f).convert('L')
    small=im.resize((im.width//2,im.height//2))
    best=None
    for a in np.arange(-1.5,1.51,0.05):
        k=np.tan(np.radians(a))
        r=np.array(small.transform(small.size,Image.AFFINE,(1,0,0,k,1,-k*small.width/2),fillcolor=255))<128
        s=r.sum(1).astype(float); sc=(s**2).sum()
        if best is None or sc>best[0]: best=(sc,a)
    k=np.tan(np.radians(best[1]))
    out=im.transform(im.size,Image.AFFINE,(1,0,0,k,1,-k*im.width/2),fillcolor=255)
    out.save(f.replace('r-','d-'))
    print(p, round(best[1],2), flush=True)
