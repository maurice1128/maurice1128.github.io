"""Build compact coding packets (religion passages + header/footer) for sampled narratives.
Usage: python3 -I packets.py WORK_DIR FROM TO [--ids file]
Prints packets in code_order FROM..TO (1-based, inclusive)."""
import re, sys, os, json, csv

TERMS = re.compile(r"\bch(?:u|o)'?r?ch|\bchurch|\bpreach|\bpray|baptiz|baptis|\bconvert|religi|'ligion|\bligion|\bjesus|camp[- ]meet|"
                   r"(?:brush|bush|hush)[- ]?(?:arbor|harbor)|\bsermon|\bbible|\bdeacon|\breviv|mourner|sunday[- ]school|"
                   r"\bshout|spiritual|\bsaved\b|\bsinner|\bheaven|\bsoul\b|\bmeetin|got happy|get happy|\bA\.?M\.?E\b|methodis|baptist|"
                   r"(?:pot|kettle)s? (?:turned|turnt|upside)|turn(?:ed)? (?:\w+ ){0,3}(?:pot|kettle)|catholic|presbyterian|episcopal", re.I)
GODLORD = re.compile(r"\b(god|lord|lawd)\b", re.I)
GODCTX = re.compile(r"pray|free|help|thank|trust|believ|heaven|soul|deliver|bless|save|merciful|faith", re.I)
SENT = re.compile(r'(?:(?<=[.!?])|(?<=[.!?]["\']))\s+(?=["\'A-Z])')

def paragraphs(lines, offset):
    paras, cur, start = [], [], None
    for i, l in enumerate(lines):
        if l.strip():
            if not cur: start = i
            cur.append(l.strip())
        elif cur:
            paras.append((start + offset, ' '.join(cur))); cur = []
    if cur: paras.append((start + offset, ' '.join(cur)))
    return paras

def relevant(sent):
    if TERMS.search(sent): return True
    if GODLORD.search(sent) and GODCTX.search(sent): return True
    return False

def packet(r, maxlen=3200):
    lines = r['text'].split('\n')
    nonempty = [l.strip() for l in lines if l.strip()]
    head = ' | '.join(x[:90] for x in nonempty[:5])[:260]
    tail = ' | '.join(x[:70] for x in nonempty[-2:])[:150]
    ages = re.findall(r"(?:\bage[d:]?\s*\d{2,3}|\d{2,3}\s+years? (?:old|of age)|born (?:in |about |on )?(?:\w+ \d{1,2},? )?18\d\d)", r['text'][:3000], re.I)
    head += ' || AGE: ' + '; '.join(dict.fromkeys(ages[:3]))
    out = []
    total = 0
    for ln, p in paragraphs(lines, r['start_line']):
        if not relevant(p): continue
        sents = SENT.split(p)
        if len(p) > 700:
            keep = set()
            for k, s in enumerate(sents):
                if relevant(s):
                    keep.update({k - 1, k, k + 1})
            chunks, prev = [], -2
            for k in sorted(x for x in keep if 0 <= x < len(sents)):
                chunks.append(('' if k == prev + 1 else '[...] ') + sents[k]); prev = k
            p2 = ' '.join(chunks)
        else:
            p2 = p
        out.append(f'[L{ln}] {p2}')
        total += len(p2)
        if total > maxlen:
            out.append('[TRUNCATED]'); break
    return head, tail, out

def main(work, a, b, idfile=None):
    segs = {}
    for l in open(os.path.join(work, 'segments.jsonl')):
        r = json.loads(l); segs[r['nid']] = r
    rows = list(csv.DictReader(open(os.path.join(work, 'sample.csv'))))
    if idfile:
        ids = [x.strip() for x in open(idfile) if x.strip()]
        rows = [r for r in rows if r['nid'] in ids]
        rows.sort(key=lambda r: ids.index(r['nid']))
    else:
        rows = [r for r in rows if a <= int(r['code_order']) <= b]
    for row in rows:
        r = segs[row['nid']]
        head, tail, out = packet(r)
        print(f"#### {row['code_order']} {r['nid']} | {r['toc_name']} | pg{r['pg_id']} L{r['start_line']}-{r['end_line']} | {r['n_chars']}ch")
        print('HEAD:', head)
        print('TAIL:', tail)
        for o in out: print(o)
        print()

if __name__ == '__main__':
    idf = None
    if '--ids' in sys.argv:
        idf = sys.argv[sys.argv.index('--ids') + 1]
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), idf)
