import sys, glob, os
from PIL import Image
d=sys.argv[1]
for f in sorted(glob.glob(os.path.join(d,'w-*.png'))):
    out=f.replace('w-','r-')
    if os.path.exists(out): continue
    im=Image.open(f)
    w,h=im.size
    if h>w: im=im.rotate(-90,expand=True)
    im.save(out)
