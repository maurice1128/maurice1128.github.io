# Combine OCR cells into per-unit text using auto + manual row mapping
import json, sys, csv
D=json.load(open(sys.argv[1])); auto=json.load(open(sys.argv[2])); man=json.load(open(sys.argv[3]))
I=list(csv.DictReader(open(sys.argv[4]),delimiter='\t'))
def cell(rid,c):
    p,i=rid.split(':'); return D[p]['rows'][int(i)]['cells'][c]
m={}
for x in I:
    key=x['cert']+(x['sub'] and '.'+x['sub'])
    rows=list(auto.get(key,[]))
    if key in man:
        mm=man[key]
        if all(r.startswith('+') for r in mm): rows=rows+[r[1:] for r in mm]
        else: rows=[r.lstrip('+') for r in mm]
    m[key]=rows
out={}
for k,rows in m.items():
    out[k]={'rows':rows,'purpose':'\n'.join(cell(r,2) for r in rows),'benefits':'\n'.join(cell(r,3) for r in rows),'remarks':'\n'.join(cell(r,4) for r in rows)}
missing=[k for k,v in out.items() if not v['rows']]
print('units',len(out),'missing',missing)
json.dump(out,open(sys.argv[5],'w'),indent=1)
