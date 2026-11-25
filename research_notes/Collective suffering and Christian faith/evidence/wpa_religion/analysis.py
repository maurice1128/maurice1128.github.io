"""Re-runnable analysis for the WPA religion coding (project wpa_religion).

Reads data.csv (400 coded narratives), double_code.csv (the first coder's own
same-session recodes of 40 narratives: intra-coder stability), corpus_screen.csv
(all 2,143 segmented narratives, keyword screen) and, if present,
second_coder.csv (independent blind second coding of the same 40). Prints the
tables reported in results.md. Standard library only.

    python3 analysis.py
"""
import csv, math, os, collections, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
D = list(csv.DictReader(open(os.path.join(HERE, 'data.csv'), encoding='utf-8')))
DC = list(csv.DictReader(open(os.path.join(HERE, 'double_code.csv'), encoding='utf-8')))
CS = list(csv.DictReader(open(os.path.join(HERE, 'corpus_screen.csv'), encoding='utf-8')))
N = len(D)

# ---------------------------------------------------------------- statistics helpers
def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*k/n:5.1f}% (95% CI {100*lo:4.1f}-{100*hi:4.1f})" if n else f"{k}/0"

def _gammainc_lower_reg(a, x):
    # regularized lower incomplete gamma P(a,x) (series / continued fraction)
    if x <= 0: return 0.0
    if x < a + 1:
        s, term, n = 1.0 / a, 1.0 / a, 0
        while abs(term) > 1e-15 * abs(s) and n < 10000:
            n += 1; term *= x / (a + n); s += term
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q
    b = x + 1 - a; c = 1 / 1e-300; d = 1 / b; h = d
    for i in range(1, 10000):
        an = -i * (i - a); b += 2
        d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-15: break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

def chi2_sf(x, df):
    return 1 - _gammainc_lower_reg(df / 2, x / 2)

def chisq(table):
    rows = [sum(r) for r in table]; cols = [sum(c) for c in zip(*table)]; n = sum(rows)
    x = 0.0; small = 0
    for i, r in enumerate(table):
        for j, o in enumerate(r):
            e = rows[i] * cols[j] / n if n else 0
            if e < 5: small += 1
            if e > 0: x += (o - e) ** 2 / e
    df = (len(rows) - 1) * (len(cols) - 1)
    return x, df, chi2_sf(x, df), small

def fisher_2x2(a, b, c, d):
    """two-sided Fisher exact p (sum of probabilities <= observed)."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def p(x):
        return math.exp(math.lgamma(r1 + 1) + math.lgamma(r2 + 1) + math.lgamma(c1 + 1) + math.lgamma(n - c1 + 1)
                        - math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(r1 - x + 1) - math.lgamma(c1 - x + 1)
                        - math.lgamma(r2 - c1 + x + 1))
    po = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= po * (1 + 1e-7)))

def odds_ratio(a, b, c, d):
    # Haldane-Anscombe correction if any zero
    if 0 in (a, b, c, d): a, b, c, d = a + .5, b + .5, c + .5, d + .5
    orr = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return orr, math.exp(math.log(orr) - 1.96 * se), math.exp(math.log(orr) + 1.96 * se)

def kappa(x, y):
    cats = sorted(set(x) | set(y)); n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    cx, cy = collections.Counter(x), collections.Counter(y)
    pe = sum(cx[c] * cy[c] for c in cats) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan')

def derive_wc(flags):
    f = set(flags)
    if not f: return 'not_stated'
    if f == {'S', 'F'}: return 'secret'
    if len(f) == 1:
        return {'W': 'white_supervised', 'B': 'black_led_permitted', 'S': 'secret', 'F': 'forbidden'}[f.pop()]
    return 'mixed'

def hdr(t):
    print('\n' + '=' * 78 + '\n' + t + '\n' + '=' * 78)

# ---------------------------------------------------------------- 1. corpus & screen
hdr('1. Corpus, keyword screen and sample')
print(f"narratives segmented: {len(CS)}  (TOC informant entries: 2,178; see results.md)")
rm = sum(int(r['religion_mention']) for r in CS)
print(f"mention religion (>=1 core keyword): {fmt(rm, len(CS))}")
bys = collections.defaultdict(lambda: [0, 0, 0])
for r in CS:
    bys[r['state']][0] += 1; bys[r['state']][1] += int(r['religion_mention']); bys[r['state']][2] += int(r['sampled'])
print(f"{'state':6}{'narr.':>7}{'relig.':>8}{'sample':>8}")
for s in sorted(bys): print(f"{s:6}{bys[s][0]:7}{bys[s][1]:8}{bys[s][2]:8}")
print(f"sample N = {N}")

# ---------------------------------------------------------------- 2. marginals
hdr('2. Marginal distributions (denominator: all 400 sampled narratives, then among stated)')
def dist(var, order=None, stated_exclude=('ns', 'not_stated')):
    c = collections.Counter(r[var] for r in D)
    keys = order or sorted(c)
    st = sum(v for k, v in c.items() if k not in stated_exclude)
    print(f"\n{var}:")
    for k in keys:
        line = f"  {k:22} {fmt(c[k], N)}"
        if k not in stated_exclude and st: line += f"   | of stated: {fmt(c[k], st)}"
        print(line)
    return c
dist('worship_control', ['white_supervised', 'black_led_permitted', 'secret', 'forbidden', 'mixed', 'not_stated'])
for f in ['wc_white', 'wc_blackled', 'wc_secret', 'wc_forbidden']:
    k = sum(r[f] == 'y' for r in D); print(f"  any {f:18} {fmt(k, N)}")
dist('black_control_pre1865', ['y', 'n', 'ns'])
dist('obedience_preaching', ['y', 'n', 'ns'])
dist('attitude_white_preachers', ['negative', 'positive', 'neutral', 'ns'])
dist('conversion_timing', ['before_1865', 'after_1865', 'ns'])
dist('faith_commitment_before_freedom', ['y', 'n', 'ns'])
dist('faith_subject', ['self', 'kin', 'others', 'ns'])
dist('postwar_church_any', ['y', 'ns'])
dist('postwar_black_church', ['y', 'n', 'ns'])
dist('prayed_for_freedom', ['y', 'n', 'ns'])
# religion actually coded (any non-ns religion code)
anyrel = [r for r in D if r['worship_control'] != 'not_stated' or any(r[v] not in ('ns',) for v in
          ['obedience_preaching', 'attitude_white_preachers', 'conversion_timing', 'faith_commitment_before_freedom',
           'postwar_church_any', 'postwar_black_church', 'prayed_for_freedom'])]
print(f"\nnarratives with at least one substantive code: {fmt(len(anyrel), N)}")
pre = [r for r in D if r['worship_control'] != 'not_stated']
print(f"narratives describing worship before 1865: {fmt(len(pre), N)}")
obs = [r for r in D if r['obedience_preaching'] != 'ns']
print(f"obedience-only preaching among narratives describing preaching content: {fmt(sum(r['obedience_preaching']=='y' for r in obs), len(obs))}")

# ---------------------------------------------------------------- 3. key cross-tab
hdr('3. Black control of worship before 1865 x faith commitment before freedom')
def xtab(rows, rv, cv, rlev, clev, title):
    print(f"\n{title}")
    t = [[sum(1 for r in rows if rv(r) == a and cv(r) == b) for b in clev] for a in rlev]
    print(f"  {'':24}" + ''.join(f"{str(b):>12}" for b in clev) + f"{'total':>8}")
    for a, row in zip(rlev, t):
        print(f"  {str(a):24}" + ''.join(f"{v:12}" for v in row) + f"{sum(row):8}")
    return t
bc = lambda r: r['black_control_pre1865']
fy = lambda r: 'y' if r['faith_commitment_before_freedom'] == 'y' else 'not_y'
stated = [r for r in D if r['black_control_pre1865'] != 'ns']
t = xtab(stated, bc, fy, ['y', 'n'], ['y', 'not_y'], 'A. Among narratives stating worship control (n=%d): faith y vs not y' % len(stated))
(a, b), (c, d) = t
print(f"  faith y | Black control y: {fmt(a, a+b)}")
print(f"  faith y | Black control n: {fmt(c, c+d)}")
orr = odds_ratio(a, b, c, d); x, df, p, small = chisq(t)
print(f"  OR = {orr[0]:.2f} (95% CI {orr[1]:.2f}-{orr[2]:.2f}); chi2 = {x:.2f}, df={df}, p = {p:.4g}; Fisher exact p = {fisher_2x2(a,b,c,d):.4g}")

t = xtab(D, bc, fy, ['y', 'n', 'ns'], ['y', 'not_y'], 'B. All 400 (worship control not stated kept as a row)')
x, df, p, small = chisq(t); print(f"  chi2 = {x:.2f}, df={df}, p = {p:.4g} (cells with expected<5: {small})")

fself = lambda r: 'y' if r['faith_commitment_before_freedom'] == 'y' and r['faith_subject'] in ('self', 'kin') else 'not_y'
t = xtab(stated, bc, fself, ['y', 'n'], ['y', 'not_y'], 'C. Stricter outcome: faith stated for the informant or kin (self/kin only)')
(a, b), (c, d) = t
orr = odds_ratio(a, b, c, d)
print(f"  {fmt(a, a+b)} vs {fmt(c, c+d)}; OR = {orr[0]:.2f} ({orr[1]:.2f}-{orr[2]:.2f}); Fisher p = {fisher_2x2(a,b,c,d):.4g}")

# D: faith measured independently of the worship-description snippet
indep = lambda r: 'y' if (r['faith_commitment_before_freedom'] == 'y' and r['snip_faith'].strip() and r['snip_faith'].strip() not in r['snip_wc']) else 'not_y'
t = xtab(stated, bc, indep, ['y', 'n'], ['y', 'not_y'], 'D. Overlap check: faith counted only when its evidence is not part of the worship-control snippet')
(a, b), (c, d) = t
orr = odds_ratio(a, b, c, d)
print(f"  {fmt(a, a+b)} vs {fmt(c, c+d)}; OR = {orr[0]:.2f} ({orr[1]:.2f}-{orr[2]:.2f}); Fisher p = {fisher_2x2(a,b,c,d):.4g}")

wc = lambda r: r['worship_control']
t = xtab(stated, wc, fy, ['white_supervised', 'black_led_permitted', 'secret', 'forbidden', 'mixed'], ['y', 'not_y'],
         'E. Five-category worship control x faith')
for lev, row in zip(['white_supervised', 'black_led_permitted', 'secret', 'forbidden', 'mixed'], t):
    print(f"  faith y | {lev:20} {fmt(row[0], sum(row))}")
x, df, p, small = chisq(t); print(f"  chi2 = {x:.2f}, df={df}, p = {p:.4g} (cells with expected<5: {small})")

# exclude hearsay-only and narrators not formerly enslaved / born late
sens = [r for r in stated if r['hearsay_only'] != 'y']
t = xtab(sens, bc, fy, ['y', 'n'], ['y', 'not_y'], 'F. Sensitivity: excluding hearsay-only narratives (n=%d)' % len(sens))
(a, b), (c, d) = t
print(f"  {fmt(a, a+b)} vs {fmt(c, c+d)}; Fisher p = {fisher_2x2(a,b,c,d):.4g}")

sub = [r for r in stated if r['interviewer_race'] != 'Black']
t = xtab(sub, bc, fy, ['y', 'n'], ['y', 'not_y'], 'G. Sensitivity: white/unknown interviewers only (n=%d)' % len(sub))
(a, b), (c, d) = t
print(f"  {fmt(a, a+b)} vs {fmt(c, c+d)}; Fisher p = {fisher_2x2(a,b,c,d):.4g}")
old = [r for r in stated if r['age_1937'].isdigit() and int(r['age_1937']) >= 80]
t = xtab(old, bc, fy, ['y', 'n'], ['y', 'not_y'], 'H. Sensitivity: informants aged 80+ at interview (at least c.8 in 1865; n=%d)' % len(old))
(a, b), (c, d) = t
print(f"  {fmt(a, a+b)} vs {fmt(c, c+d)}; Fisher p = {fisher_2x2(a,b,c,d):.4g}")
# Mantel-Haenszel common OR across states (strata with both rows present)
num = den = 0.0
for s in sorted(set(r['state'] for r in stated)):
    R = [r for r in stated if r['state'] == s]
    a = sum(bc(r) == 'y' and fy(r) == 'y' for r in R); b = sum(bc(r) == 'y' and fy(r) != 'y' for r in R)
    c = sum(bc(r) == 'n' and fy(r) == 'y' for r in R); d = sum(bc(r) == 'n' and fy(r) != 'y' for r in R)
    n = a + b + c + d
    if n: num += a * d / n; den += b * c / n
print(f"\nI. Mantel-Haenszel OR stratified by state: {num/den:.2f}")

# ---------------------------------------------------------------- 4. conversion timing
hdr('4. Conversion timing')
ct = [r for r in D if r['conversion_timing'] != 'ns']
k = sum(r['conversion_timing'] == 'after_1865' for r in ct)
print(f"dated conversions/joinings: {len(ct)} of {N}; after 1865: {fmt(k, len(ct))}")
ages = [int(r['age_1937']) for r in ct if r['age_1937'].isdigit()]
if ages: print(f"  age at interview of those with dated conversion: median {sorted(ages)[len(ages)//2]}")
t = xtab(ct, bc, lambda r: r['conversion_timing'], ['y', 'n', 'ns'], ['before_1865', 'after_1865'], 'conversion timing by Black control of pre-1865 worship')
t = xtab(D, lambda r: r['conversion_timing'], lambda r: r['postwar_black_church'], ['before_1865', 'after_1865', 'ns'], ['y', 'n', 'ns'], 'conversion timing x postwar Black-run church')

# ---------------------------------------------------------------- 5. interviewer race
hdr('5. Interviewer race (documented) comparisons')
ir = collections.Counter(r['interviewer_race'] for r in D)
print('interviewer_race:', dict(ir))
def comp(var, val, title, base=lambda r: True):
    B = [r for r in D if r['interviewer_race'] == 'Black' and base(r)]
    O = [r for r in D if r['interviewer_race'] != 'Black' and base(r)]
    a = sum(r[var] == val for r in B); c = sum(r[var] == val for r in O)
    print(f"  {title:52} Black-int.: {fmt(a, len(B))} | white/unknown: {fmt(c, len(O))} | Fisher p = {fisher_2x2(a, len(B)-a, c, len(O)-c):.3g}")
comp('obedience_preaching', 'y', 'obedience-only preaching reported')
comp('attitude_white_preachers', 'negative', 'negative attitude to white preachers/church')
comp('attitude_white_preachers', 'positive', 'positive attitude to white preachers/church')
comp('wc_secret', 'y', 'secret worship reported')
comp('black_control_pre1865', 'y', 'Black control of worship reported')
comp('faith_commitment_before_freedom', 'y', 'faith before freedom reported')
comp('prayed_for_freedom', 'y', 'prayer for freedom reported')
comp('postwar_black_church', 'y', 'postwar Black-run church')
print('\n  Among narratives that state an attitude (neg/pos/neutral):')
comp('attitude_white_preachers', 'negative', 'negative', base=lambda r: r['attitude_white_preachers'] != 'ns')
comp('attitude_white_preachers', 'positive', 'positive', base=lambda r: r['attitude_white_preachers'] != 'ns')
W = [r for r in D if r['interviewer_race'] == 'white']
print(f"\n  documented-white interviewers only (n={len(W)}): negative {sum(r['attitude_white_preachers']=='negative' for r in W)}, positive {sum(r['attitude_white_preachers']=='positive' for r in W)}, obedience y {sum(r['obedience_preaching']=='y' for r in W)}")

# ---------------------------------------------------------------- 6. attitude by worship mode
hdr('6. Attitude to white preachers by obedience preaching')
t = xtab([r for r in D if r['attitude_white_preachers'] != 'ns'], lambda r: r['obedience_preaching'], lambda r: r['attitude_white_preachers'],
         ['y', 'n', 'ns'], ['negative', 'neutral', 'positive'], 'obedience preaching x attitude (narratives stating attitude)')

# ---------------------------------------------------------------- 7. prayer for freedom
hdr('7. Prayer for freedom by worship mode')
t = xtab(stated, wc, lambda r: 'y' if r['prayed_for_freedom'] == 'y' else 'not_y',
         ['white_supervised', 'black_led_permitted', 'secret', 'forbidden', 'mixed'], ['y', 'not_y'], 'worship control x prayed for freedom')

# ---------------------------------------------------------------- 8. age of informants
hdr('8. Age of informants (stated or computed, best effort)')
ages = sorted(int(r['age_1937']) for r in D if r['age_1937'].isdigit())
print(f"age recorded for {len(ages)} of {N}; median {ages[len(ages)//2]}; IQR {ages[len(ages)//4]}-{ages[3*len(ages)//4]}")
u = sum(a <= 79 for a in ages)
print(f"aged <=79 (born c.1858 or later, i.e. under ~7 in 1865): {fmt(u, len(ages))}")
print(f"aged <=72 (born after c.1865, not formerly enslaved or infant): {fmt(sum(a <= 72 for a in ages), len(ages))}")
print(f"hearsay_only = y: {fmt(sum(r['hearsay_only']=='y' for r in D), N)}")

# ---------------------------------------------------------------- 9. reliability
hdr('9. Intra-coder reliability: blind recode of 40 narratives (percent agreement, Cohen kappa)')
first = {r['nid']: r for r in D}
pairs = []
for r2 in DC:
    r1 = first[r2['nid']]
    r2 = dict(r2); r2['worship_control'] = derive_wc([x for x in r2['wc_flags'] if x in 'WBSF'])
    f = set(x for x in r2['wc_flags'] if x in 'WBSF')
    r2['black_control_pre1865'] = 'ns' if not f else ('y' if ('B' in f or 'S' in f) else 'n')
    for fl, ch in [('wc_white', 'W'), ('wc_blackled', 'B'), ('wc_secret', 'S'), ('wc_forbidden', 'F')]:
        r2[fl] = 'y' if ch in f else 'n'
    pairs.append((r1, r2))
VARS = ['worship_control', 'black_control_pre1865', 'wc_white', 'wc_blackled', 'wc_secret', 'wc_forbidden',
        'obedience_preaching', 'attitude_white_preachers', 'conversion_timing', 'faith_commitment_before_freedom',
        'faith_subject', 'postwar_church_any', 'postwar_black_church', 'prayed_for_freedom']
print(f"n = {len(pairs)}")
for v in VARS:
    x = [p[0][v] for p in pairs]; y = [p[1][v] for p in pairs]
    po, k = kappa(x, y)
    dis = [p[0]['nid'] for p in pairs if p[0][v] != p[1][v]]
    print(f"  {v:34} agreement {100*po:5.1f}%  kappa {k:5.2f}   disagreements: {', '.join(dis) if dis else '-'}")

# ---------------------------------------------------------------- 10. independent second coder
SC_PATH = os.path.join(HERE, 'second_coder.csv')
if os.path.exists(SC_PATH):
    hdr('10. Independent second coder (separate blind session, full narratives): first codes in data.csv vs second_coder.csv')
    SC = {r['nid']: r for r in csv.DictReader(open(SC_PATH, encoding='utf-8'))}
    ids = [r['nid'] for r in DC]
    SNIP = {'attitude_white_preachers': 'att', 'conversion_timing': 'conv', 'faith_commitment_before_freedom': 'faith',
            'faith_subject': 'faith', 'postwar_church_any': 'post', 'postwar_black_church': 'post',
            'prayed_for_freedom': 'free', 'obedience_preaching': 'obed'}
    print(f"n = {len(ids)}")
    for v in VARS + ['interviewer_race', 'hearsay_only']:
        x = [first[i][v] for i in ids]; y = [SC[i][v] for i in ids]
        po, k = kappa(x, y)
        ks = '   NA' if k != k else f"{k:5.2f}"
        dis = [i for i in ids if first[i][v] != SC[i][v]]
        print(f"  {v:34} agreement {sum(a == b for a, b in zip(x, y)):2}/{len(ids)} = {100*po:5.1f}%  kappa {ks}   disagreements: {', '.join(dis) if dis else '-'}")
    print("  disagreements (first -> second), with snippets:")
    for i in ids:
        for v in VARS + ['interviewer_race', 'hearsay_only']:
            if first[i][v] != SC[i][v]:
                k = None if v in ('interviewer_race', 'hearsay_only') else SNIP.get(v, 'wc')
                s1 = first[i].get('snip_' + k, '') if k else ''
                s2 = SC[i].get('snip_' + k, '') if k else ''
                print(f"    {i} {first[i]['informant']} | {v}: {first[i][v]} -> {SC[i][v]}")
                if s1: print(f"        first:  {s1[:160]}")
                if s2: print(f"        second: {s2[:160]}")
