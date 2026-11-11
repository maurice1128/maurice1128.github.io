import json, csv, sys
from PIL import Image, ImageDraw
D=json.load(open('work/v3/cells_all.json')); S=json.load(open('work/dc_sample.json'))
R={x['unit_id']:x for x in csv.DictReader(open('work/coded.csv'))}
crops=[]
for uid in S:
    parts=[]
    for rid in R[uid]['ocr_rows'].split(';'):
        p,i=rid.split(':'); row=D[p]['rows'][int(i)]; v=D[p]['v']
        im=Image.open('img/d-%s.png'%p).convert('L')
        y0=max(0,row['y0']-(70 if int(i)==0 else 0)); parts.append(im.crop((v[0],y0,v[5],row['y1'])))
    W=max(c.width for c in parts); H=sum(c.height for c in parts)+40
    out=Image.new('L',(W,H),255); d=ImageDraw.Draw(out); d.text((5,5),uid,fill=0)
    y=40
    for c in parts: out.paste(c,(0,y)); y+=c.height
    crops.append(out)
# pack into pages up to ~1700 px tall
pages=[]; cur=[]; h=0
for c in crops:
    if cur and h+c.height>1900: pages.append(cur); cur=[]; h=0
    cur.append(c); h+=c.height+10
pages.append(cur)
for k,pg in enumerate(pages):
    W=max(c.width for c in pg); H=sum(c.height+10 for c in pg)
    out=Image.new('L',(W,H),255); y=0
    for c in pg: out.paste(c,(0,y)); y+=c.height+10
    out=out.resize((int(W*0.55),int(H*0.55)))
    out.save('dc/dc%02d.png'%k)
print(len(pages))
