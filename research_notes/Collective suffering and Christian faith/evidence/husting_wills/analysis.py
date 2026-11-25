"""Analysis of London Husting wills, 1320-1400 (project husting_wills).

Re-runnable, standard library only:
    python3 -I analysis.py            (run from this folder, or pass the folder as argv[1])
Reads data.csv (rule-coded, one row per will) and double_coding.csv (blind second coding
of a 10% random sample) and prints all tables used in results.md.
"""
import csv, math, os, sys, collections

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
DATA = list(csv.DictReader(open(os.path.join(HERE, 'data.csv'), encoding='utf-8')))
DC = list(csv.DictReader(open(os.path.join(HERE, 'double_coding.csv'), encoding='utf-8')))

VARS = ['parish', 'chantry', 'obit', 'masses', 'lights', 'fraternity', 'friars', 'monastic',
        'hospital', 'charity', 'cathedral', 'named_chaplain', 'pious_uses', 'pestilence']
LABEL = {'parish': 'Parish church', 'chantry': 'Chantry / priest to celebrate', 'obit': 'Obit / anniversary',
         'masses': 'Masses / trentals', 'lights': 'Lights', 'fraternity': 'Fraternity / gild',
         'friars': 'Friars', 'monastic': 'Monastery / nunnery / canons', 'hospital': 'Hospital / lepers',
         'charity': 'Poor / prisoners / roads / bridges', 'cathedral': "St Paul's", 'named_chaplain': 'Named chaplain to pray',
         'pious_uses': 'Unspecified "pious uses"', 'pestilence': 'Mentions plague/pestilence',
         'any_specified': 'Any specified pious/charitable bequest', 'self_lay_intercession': 'Chantry, obit, masses, fraternity or named chaplain',
         'institution': 'Parish, friars, monastery, hospital or St Paul\'s', 'chantry_perpetual': 'Chantry said to be perpetual',
         'chantry_temporary': 'Chantry for years / for a life'}
PERIODS = ['P1', 'P2', 'P3', 'P4']
PLAB = {'P1': 'P1 1320-48', 'P2': 'P2 1349-60', 'P3': 'P3 1361-75', 'P4': 'P4 1376-1400'}

rows = [r for r in DATA if r['empty_entry'] == '0']
for r in rows:
    for v in VARS + ['chantry_perpetual', 'chantry_temporary', 'cleric', 'enrol_year', 'entry_words']:
        r[v] = int(r[v])
    r['any_specified'] = int(any(r[v] for v in VARS if v not in ('pious_uses', 'pestilence')))
    r['self_lay_intercession'] = int(any(r[v] for v in ('chantry', 'obit', 'masses', 'fraternity', 'named_chaplain')))
    r['institution'] = int(any(r[v] for v in ('parish', 'friars', 'monastic', 'hospital', 'cathedral')))


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def two_prop(k1, n1, k2, n2):
    """Pooled two-proportion z test; chi-square (1 df, no continuity correction) = z^2."""
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else float('nan')
    if not se or se != se:
        return float('nan'), float('nan')
    z = (k2 / n2 - k1 / n1) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def chi2_sf_df3(x):
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)


def chi2_4x2(ks, ns):
    K, N = sum(ks), sum(ns)
    p = K / N
    x = 0.0
    for k, n in zip(ks, ns):
        for obs, exp in ((k, n * p), (n - k, n * (1 - p))):
            if exp > 0:
                x += (obs - exp) ** 2 / exp
    return x, chi2_sf_df3(x)


def fmt_p(p):
    return 'nan' if p != p else ('<0.001' if p < 0.001 else f'{p:.3f}')


def table(var, subset=None, title=None):
    sub = subset if subset is not None else rows
    out = []
    ks, ns = [], []
    for P in PERIODS:
        g = [r for r in sub if r['period'] == P]
        k, n = sum(r[var] for r in g), len(g)
        lo, hi = wilson(k, n)
        ks.append(k); ns.append(n)
        out.append(f'{PLAB[P]}: {k}/{n} = {100*k/n:5.1f}% [{100*lo:4.1f}-{100*hi:4.1f}]' if n else f'{PLAB[P]}: 0/0')
    tests = []
    for a, b in (('P1', 'P2'), ('P2', 'P3'), ('P3', 'P4'), ('P1', 'P3')):
        i, j = PERIODS.index(a), PERIODS.index(b)
        if ns[i] and ns[j]:
            z, p = two_prop(ks[i], ns[i], ks[j], ns[j])
            tests.append(f'{a}v{b}: diff {100*(ks[j]/ns[j]-ks[i]/ns[i]):+.1f} pts, chi2={z*z:.2f}, p={fmt_p(p)}')
    x, p4 = chi2_4x2(ks, ns)
    print(f'\n{title or LABEL.get(var, var)}')
    for o in out:
        print('   ', o)
    print('    tests:', ' | '.join(tests), f'| 4-period chi2(3)={x:.2f}, p={fmt_p(p4)}')
    return ks, ns


def kappa(a, b):
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan')


print('=' * 78)
print('LONDON HUSTING WILLS 1320-1400: rule-coded entries (Sharpe 1889-90, via BHO)')
print('=' * 78)
print(f'Entries in scope: {len(DATA)}; empty entries excluded: {len(DATA) - len(rows)}; analysed: {len(rows)}')

print('\nN by period:')
for P in PERIODS:
    g = [r for r in rows if r['period'] == P]
    yrs = sorted({r['enrol_year'] for r in g})
    print(f'    {PLAB[P]}: N={len(g)}  ({len(yrs)} calendar years with enrolments; mean {len(g)/len(yrs):.1f}/yr)')

print('\nEnrolments per calendar year (mortality marker; 1360 has no roll in the calendar):')
c = collections.Counter(r['enrol_year'] for r in rows)
line = []
for y in range(1320, 1401):
    line.append(f'{y}:{c.get(y, 0)}')
for i in range(0, len(line), 10):
    print('   ', '  '.join(line[i:i + 10]))
base = [c.get(y, 0) for y in range(1340, 1348)]
print(f'    1349 = {c[1349]} vs mean 1340-47 = {sum(base)/len(base):.1f} ({c[1349]/(sum(base)/len(base)):.1f}x); '
      f'1361 = {c[1361]} vs mean 1350-59 = {sum(c.get(y,0) for y in range(1350,1360))/10:.1f}')

print('\nComposition by period (sex, clerics, summary length):')
for P in PERIODS:
    g = [r for r in rows if r['period'] == P]
    f = sum(1 for r in g if r['sex'] == 'F')
    cl = sum(r['cleric'] for r in g)
    words = sorted(r['entry_words'] for r in g)
    med = words[len(words) // 2]
    print(f'    {PLAB[P]}: women {f}/{len(g)} ({100*f/len(g):.1f}%), clerics {cl} ({100*cl/len(g):.1f}%), '
          f'median entry length {med} words, mean {sum(words)/len(words):.0f}')

print('\n' + '=' * 78)
print('TABLE 1. Share of wills with each bequest type, by period of enrolment (Wilson 95% CI)')
print('=' * 78)
for v in ['parish', 'chantry', 'chantry_perpetual', 'chantry_temporary', 'obit', 'masses', 'lights', 'fraternity',
          'named_chaplain', 'friars', 'monastic', 'hospital', 'cathedral', 'charity', 'pious_uses', 'pestilence',
          'any_specified', 'self_lay_intercession', 'institution']:
    table(v)

print('\n' + '=' * 78)
print('TABLE 2. Among wills with ANY specified pious/charitable bequest: share with each type')
print('=' * 78)
spec = [r for r in rows if r['any_specified']]
for v in ['parish', 'chantry', 'obit', 'lights', 'fraternity', 'friars', 'monastic', 'hospital', 'cathedral', 'charity']:
    table(v, spec, LABEL[v] + ' (denominator: wills with any specified bequest)')

print('\n' + '=' * 78)
print('TABLE 3. Who holds the chantry/obit property (wills with chantry or obit)')
print('=' * 78)
co = [r for r in rows if r['chantry'] or r['obit']]
for k in ['private', 'parish_body', 'lay_corporate', 'church_corporate']:
    for r in co:
        r['tr_' + k] = int(k in r['chantry_trustee'].split(';'))
    table('tr_' + k, co, f'Trustee named: {k} (denominator: wills with chantry or obit)')
for r in co:
    r['tr_parish_or_lay'] = int(r['tr_parish_body'] or r['tr_lay_corporate'])
table('tr_parish_or_lay', co, 'Trustee named: parish body OR lay corporate (denominator: wills with chantry or obit)')

print('\n' + '=' * 78)
print('TABLE 4. Burial place stated (share of all wills)')
print('=' * 78)
for site in ['parish', 'st_pauls', 'religious_house', 'friars', 'hospital', 'none_stated']:
    for r in rows:
        r['b_' + site] = int(r['burial_site'] == site)
    table('b_' + site, rows, f'Burial: {site}')

print('\n' + '=' * 78)
print('TABLE 5. By sex (key variables)')
print('=' * 78)
for sx in ('M', 'F'):
    sub = [r for r in rows if r['sex'] == sx]
    for v in ['chantry', 'parish', 'friars', 'monastic', 'fraternity', 'charity', 'any_specified']:
        table(v, sub, f'{LABEL[v]} - {"men" if sx == "M" else "women"}')

print('\n' + '=' * 78)
print('TABLE 6. Sensitivity checks')
print('=' * 78)
lay = [r for r in rows if not r['cleric']]
for v in ['chantry', 'parish', 'friars', 'monastic', 'fraternity']:
    table(v, lay, f'{LABEL[v]} - lay testators only')
no49 = [r for r in rows if r['enrol_year'] != 1349]
for v in ['chantry', 'parish', 'friars', 'fraternity', 'any_specified']:
    table(v, no49, f'{LABEL[v]} - excluding 1349 enrolments')
# period by date of will (where the will gives an A.D. year)
wd = []
for r in rows:
    if r['will_year']:
        y = int(r['will_year'])
        if 1300 <= y <= 1400:
            r2 = dict(r)
            r2['period'] = 'P1' if y <= 1348 else 'P2' if y <= 1360 else 'P3' if y <= 1375 else 'P4'
            wd.append(r2)
print(f'\n(Wills with an A.D. date: {len(wd)} of {len(rows)}; periods below use the will date, not enrolment)')
for v in ['chantry', 'parish', 'friars', 'fraternity', 'any_specified']:
    table(v, wd, f'{LABEL[v]} - periods by year the will was made')
# summary-length control: long vs short entries
for lab, sub in (('entries <= 120 words', [r for r in rows if r['entry_words'] <= 120]),
                 ('entries > 120 words', [r for r in rows if r['entry_words'] > 120])):
    for v in ['chantry', 'parish', 'friars']:
        table(v, sub, f'{LABEL[v]} - {lab}')

print('\n' + '=' * 78)
print('TABLE 7. Wills whose summary states a burial place (proxy: the soul-part of the testament was enrolled and calendared)')
print('=' * 78)
bur = [r for r in rows if r['burial_site'] != 'none_stated']
for v in ['parish', 'chantry', 'obit', 'masses', 'lights', 'fraternity', 'friars', 'monastic', 'hospital', 'cathedral', 'charity',
          'self_lay_intercession', 'institution']:
    table(v, bur, f'{LABEL[v]} - wills stating a burial place')

TYPES = ['parish', 'chantry', 'obit', 'masses', 'lights', 'fraternity', 'friars', 'monastic', 'hospital', 'cathedral', 'charity']
print('\nDispersion: mean number of the 11 specified bequest types per will (95% CI, normal approx.)')
for lab, sub in (('all wills', rows), ('wills stating a burial place', bur)):
    for P in PERIODS:
        xs = [sum(r[t] for t in TYPES) for r in sub if r['period'] == P]
        m = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))
        print(f'    {lab:<30} {PLAB[P]}: mean {m:.2f} [{m - 1.96*sd/math.sqrt(len(xs)):.2f}-{m + 1.96*sd/math.sqrt(len(xs)):.2f}] (n={len(xs)})')

print('\n' + '=' * 78)
print('Pestilence mentions (verbatim snippets)')
print('=' * 78)
for r in rows:
    if r['pestilence']:
        print(f"    {r['will_id']} vol {r['vol']} p {r['page']} Roll {r['roll']} ({r['enrol_year']}): {r['pestilence_snip']}")

print('\n' + '=' * 78)
print('RELIABILITY: rule coder vs blind second coding of a 10% random sample')
print('=' * 78)
byid = {r['will_id']: r for r in DATA}
print(f'Sample size: {len(DC)}')
print(f'{"variable":<16}{"n":>5}{"rule=1":>8}{"2nd=1":>8}{"agree%":>8}{"kappa":>8}{"FP":>5}{"FN":>5}')
dis = []
for v in VARS + ['sex']:
    a, b = [], []
    for d in DC:
        r = byid[d['will_id']]
        if v == 'sex':
            a.append(int(r['sex'] == 'F')); b.append(int(d['sex'] == 'F'))
        else:
            a.append(int(r[v])); b.append(int(d[v]))
        if a[-1] != b[-1]:
            dis.append((v, d['will_id'], a[-1], b[-1]))
    po, k = kappa(a, b)
    fp = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)
    fn = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)
    ks = 'n/a' if k != k else f'{k:.2f}'
    print(f'{v:<16}{len(a):>5}{sum(a):>8}{sum(b):>8}{100*po:>8.1f}{ks:>8}{fp:>5}{fn:>5}')
print('\nDisagreements (variable, will, rule code, second code):')
for x in dis:
    print('   ', x)
