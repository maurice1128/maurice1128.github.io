# Assemble gild units from OCR'd table cells of Westlake (1919) Appendix.
# Usage: python3 -I assemble.py cells_all.json corrections.json units.json review.txt
import sys, json, re

cells_path, corr_path, out_path, review_path = sys.argv[1:5]
D = json.load(open(cells_path))
try:
    CORR = json.load(open(corr_path))
except FileNotFoundError:
    CORR = {}

HEADER = re.compile(r'^(Certificate\.?|No[.,]? and|Lan[gq]uage\.?|Place, Dedication,?.*|and Da[ti]e of|.*Fou?n[a-z]*ation[.,]?\s*;?|'
                    r'Origin, Purpose,.*|Friendly Benefits|to Members,?|[ia]f any\.?|\|?\s*Remarks\.?.*|pa aU)$', re.I)
COUNTIES = ['BEDFORDSHIRE','BERKSHIRE','CAMBRIDGESHIRE','DERBYSHIRE','DORSET','ESSEX','GLOUCESTERSHIRE','HERTFORDSHIRE',
            'KENT','LANCASHIRE','LEICESTERSHIRE','LINCOLNSHIRE','LONDON','NORFOLK','NORTHAMPTONSHIRE','NOTTINGHAMSHIRE',
            'OXFORDSHIRE','RUTLAND','SOMERSET','STAFFORDSHIRE','SUFFOLK','SURREY','SUSSEX','WARWICKSHIRE','WILTSHIRE',
            'WORCESTERSHIRE','YORKSHIRE','HUNTINGDONSHIRE','DEVON','CORNWALL','HAMPSHIRE','NORTHUMBERLAND','CHESHIRE',
            'SHROPSHIRE','HEREFORDSHIRE','BUCKINGHAMSHIRE','MIDDLESEX','WESTMORLAND','CUMBERLAND','DURHAM']

def clean(cell):
    out = []
    for l in cell.split('\n'):
        s = l.strip().strip('|').strip()
        if not s:
            continue
        if HEADER.match(s):
            continue
        out.append(s)
    return out

rows = []
for k in sorted(D, key=int):
    pg = D[k]
    for i, r in enumerate(pg.get('rows', [])):
        c = [clean(x) for x in r['cells']]
        if not any(c):
            continue
        rows.append({'pdf_page': int(k), 'page': int(k) - 24, 'row': i, 'certbreak': r['certbreak'], 'c': c})

def is_county(s):
    t = re.sub(r'[^A-Z]', '', s.upper())
    letters = re.sub(r'[^A-Za-z]', '', s)
    if len(letters) < 4 or sum(ch.isupper() for ch in letters) / len(letters) < 0.85:
        return None
    for cty in COUNTIES:
        if t.startswith(cty[:6]):
            return cty
    return None

units = []
for r in rows:
    certtxt = ' '.join(r['c'][0])
    nums = [int(n) for n in re.findall(r'\b(\d{1,3})\b', certtxt) if 0 < int(n) < 600]
    place = r['c'][1]
    joined = ' '.join(place)
    cont = (not nums) and (not place or 'Continued' in joined or 'ontinued' in joined)
    if cont and units:
        u = units[-1]
        for j in (2, 3, 4):
            u['cols'][j] += r['c'][j]
        u['rows'].append('%d:%d' % (r['pdf_page'], r['row']))
        continue
    units.append({'pdf_page': r['pdf_page'], 'page': r['page'], 'rows': ['%d:%d' % (r['pdf_page'], r['row'])],
                  'certbreak': r['certbreak'], 'cert_ocr': certtxt, 'cert_nums': nums,
                  'cols': [list(x) for x in r['c']]})

# certificate numbering: take OCR number when it fits sequence, else infer
last = 0
for u in units:
    n = [x for x in u['cert_nums'] if last <= x <= last + 3]
    if n:
        u['cert_no'] = n[0]; u['cert_inferred'] = 0
    elif u['certbreak']:
        u['cert_no'] = last + 1; u['cert_inferred'] = 1
    else:
        u['cert_no'] = last; u['cert_inferred'] = 1
    last = u['cert_no']

# apply manual corrections / splits keyed by first row id
final = []
for u in units:
    key = u['rows'][0]
    cr = CORR.get(key)
    if cr and 'split' in cr:
        for part in cr['split']:
            v = json.loads(json.dumps(u))
            v.update(part)
            final.append(v)
        continue
    if cr:
        if cr.get('drop'):
            continue
        u.update(cr)
    final.append(u)

# carry forward county / place
county = place = None
for idx, u in enumerate(final):
    lines = u['cols'][1]
    if 'county' not in u:
        for l in lines[:2]:
            c = is_county(l)
            if c:
                county = c
        u['county'] = county
    else:
        county = u['county']
    u['unit_seq'] = idx + 1

json.dump(final, open(out_path, 'w'), indent=1)
with open(review_path, 'w') as f:
    for u in final:
        f.write('%s | p%d | cert %s%s | %s | %s\n' % (u['rows'][0], u['page'], u['cert_no'], '*' if u['cert_inferred'] else '',
                u['county'], ' / '.join(u['cols'][1])))
print(len(rows), 'rows', len(final), 'units')
