import json,csv,collections,re,sys
U=json.load(open(sys.argv[1])); I=list(csv.DictReader(open(sys.argv[2]),delimiter='\t'))
byp=collections.defaultdict(list)
for u in U: byp[u['page']].append(u)
ibyp=collections.defaultdict(list)
for x in I: ibyp[int(x['page'])].append(x)
out={}; flags=[]
def words(s): return set(w.lower() for w in re.findall(r'[A-Za-z]{4,}',s))
for p in sorted(ibyp):
    us=byp.get(p,[]); xs=ibyp[p]
    if len(us)==len(xs):
        for u,x in zip(us,xs):
            key=x['cert']+(x['sub'] and '.'+x['sub'])
            ok = int(x['cert']) in u['cert_nums'] or bool(words(x['dedication']+' '+x['place']+' '+x['church_note']) & words(' '.join(u['cols'][1])))
            out[key]=u['rows']
            if not ok: flags.append((p,key,u['rows'],' / '.join(u['cols'][1])[:80]))
    else:
        flags.append((p,'COUNT',len(us),len(xs)))
json.dump(out,open(sys.argv[3],'w'),indent=0)
for f in flags: print(f)
