#!/usr/bin/env python3
"""gild_foundations: re-runnable analysis of the 1388-9 gild returns as calendared by Westlake (1919).

Reads data.csv (one row per gild), double_coding.csv (10% reliability sample) and
crosscheck_smith.csv (Toulmin Smith 1870 cross-check) from this directory and prints
all tables reported in results.md. Standard library only.
"""
import csv, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'data.csv'), encoding='utf-8')))
N = len(rows)
PURP = ['funeral', 'masses', 'chaplain', 'lights', 'aid', 'alms_general', 'feast', 'other']


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def pct(k, n):
    lo, hi = wilson(k, n)
    return '%d/%d = %.1f%% [%.1f, %.1f]' % (k, n, 100 * k / n if n else float('nan'), 100 * lo, 100 * hi)


def chi2_2x2(a, b, c, d):
    n = a + b + c + d
    num = n * (a * d - b * c) ** 2
    den = (a + b) * (c + d) * (a + c) * (b + d)
    if den == 0:
        return float('nan'), float('nan')
    x = num / den
    return x, math.erfc(math.sqrt(x / 2))  # df = 1


def fisher_2x2(a, b, c, d):
    """two-sided Fisher exact p (sum of tables with prob <= observed)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    def lp(x):
        return (math.lgamma(r1 + 1) - math.lgamma(x + 1) - math.lgamma(r1 - x + 1)
                + math.lgamma(r2 + 1) - math.lgamma(c1 - x + 1) - math.lgamma(r2 - c1 + x + 1)
                - (math.lgamma(n + 1) - math.lgamma(c1 + 1) - math.lgamma(n - c1 + 1)))
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p0 = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(lo, hi + 1) if lp(x) <= p0 + 1e-9))


def kappa(x, y):
    cats = sorted(set(x) | set(y))
    n = len(x)
    po = sum(1 for a, b in zip(x, y) if a == b) / n
    pe = sum((x.count(c) / n) * (y.count(c) / n) for c in cats)
    k = (po - pe) / (1 - pe) if pe < 1 else float('nan')
    return po, k


def yr(r):
    return int(r['found_year']) if r['found_year'] not in ('', None) else None


print('=' * 78)
print('A. SAMPLE')
print('Units (gilds) in Westlake appendix:', N, '; certificates:', len(set(r['cert'] for r in rows)))
cty = collections.Counter(r['county'].split(' [')[0].split(' (')[0] for r in rows)
print('By county:', ', '.join('%s %d' % kv for kv in cty.most_common()))

print('=' * 78)
print('B. FOUNDATION-DATE STATEMENTS (date_class), all units')
dc = collections.Counter(r['date_class'] for r in rows)
for k, v in dc.most_common():
    print('  %-22s %4d  %s' % (k, v, pct(v, N)))
withyear = [r for r in rows if yr(r) is not None]
print('Units with a usable foundation year (exact or approx/glossed):', pct(len(withyear), N))
print('Units with no foundation year (undated, time out of mind, document date only, reign, recent, etc.):', pct(N - len(withyear), N))

print('=' * 78)
print('C. DECADE DISTRIBUTION OF STATED FOUNDATION YEARS, 1300-1389')
in14 = [r for r in withyear if 1300 <= yr(r) <= 1389]
early = [r for r in withyear if yr(r) < 1300]
print('Years before 1300: %d ; 1300-1389: %d' % (len(early), len(in14)))
print('  decade   all-with-year  exact-only  approx("c."/"?")')
for d in range(1300, 1390, 10):
    a = sum(1 for r in in14 if int(r['decade']) == d)
    e = sum(1 for r in in14 if int(r['decade']) == d and r['date_class'] == 'exact')
    ap = a - e
    print('  %ds   %4d  %s   %4d        %4d' % (d, a, '#' * a, e, ap))
# 1340s split
pre40 = sum(1 for r in in14 if 1340 <= yr(r) <= 1348)
post40 = sum(1 for r in in14 if yr(r) == 1349)
print('  (1340s split: 1340-1348 = %d; 1349 = %d)' % (pre40, post40))
ap = [r for r in in14 if r['date_class'] != 'exact']
nine = sum(1 for r in ap if yr(r) % 10 == 9)
print('Heaping: of %d approximate ("c.") years 1300-89, %d end in 9 (1389 minus a round number of years)' % (len(ap), nine))
print('  approximate years ending in 9:', dict(collections.Counter(yr(r) for r in ap if yr(r) % 10 == 9)))

print('=' * 78)
print('D. PRE (1300-1348) vs POST (1349-1389) FOUNDATIONS -- SURVIVORS TO 1389 ONLY')


def prepost(sel, label):
    pre = sum(1 for r in sel if 1300 <= yr(r) <= 1348)
    post = sum(1 for r in sel if 1349 <= yr(r) <= 1389)
    n = pre + post
    print('%-46s pre %3d (%.2f/yr)  post %3d (%.2f/yr)  share post %s  rate ratio %.1f' %
          (label, pre, pre / 49, post, post / 41, pct(post, n), (post / 41) / (pre / 49) if pre else float('nan')))
    return pre, post


p_all = prepost(in14, 'All with year (exact + approx)')
prepost([r for r in in14 if r['date_class'] == 'exact'], 'Exact years only')
prepost([r for r in in14 if r['date_class'] == 'exact' and not (1348 <= yr(r) <= 1349)], 'Exact only, excluding 1348-49')
prepost([r for r in in14 if r['date_class'] in ('exact', 'approx') and r['date_note'] == ''], 'Excluding glossed/claimed dates')
# period-level classification (adds units dated only relative to 1349)
per = collections.Counter(r['period'] for r in rows)
print('Period-level classification incl. "lately begun", "temp. Ric. II", statutes/licences <=1348, "before the pestilence":')
print('  early(<1300) %d, pre %d, post %d, indeterminate %d' % (per['early'], per['pre'], per['post'], per['']))
pp = per['pre'] + per['post']
print('  share post among pre+post:', pct(per['post'], pp))
print('Time out of mind / of old / formerly:', dc['time_out_of_mind'], '; these are by construction older foundations (mostly pre-1349).')

print('-' * 78)
print('Survivorship sensitivity: constant annual dissolution hazard h, constant foundation rate F.')
print('Observed per-year rate ratio post/pre would arise from survival alone if')
print('  mean survival(1349-89)/mean survival(1300-48) = ratio. Solving for h:')
pre, post = p_all
target = (post / 41) / (pre / 49)


def surv_ratio(h):
    def m(a, b):
        if h == 0:
            return 1.0
        return (math.exp(-h * (1389 - b)) - math.exp(-h * (1389 - a))) / (h * (b - a))
    return m(1349, 1389) / m(1300, 1348)


lo, hi = 0.0, 0.5
for _ in range(100):
    mid = (lo + hi) / 2
    if surv_ratio(mid) < target:
        lo = mid
    else:
        hi = mid
h = (lo + hi) / 2
print('  observed rate ratio %.2f -> h = %.4f per year (half-life %.0f years)' % (target, h, math.log(2) / h if h else float('inf')))
for hh in (0.01, 0.02, 0.03, 0.05):
    print('  h=%.2f: survival alone gives rate ratio %.2f' % (hh, surv_ratio(hh)))
print('  (A one-off Black Death loss of fraction L of pre-1349 gilds multiplies the ratio by 1/(1-L).)')
print('-' * 78)
print('Trend check: annual rate of surviving foundations by period, and log-linear extrapolation of the')
print('pre-1349 trend (1300-09 ... 1340-48) into the post-1349 periods. Survivors-to-1389 already rise')
print('steeply before 1349, so part of any post-1349 excess is expected from recency alone.')
def trend(sel, label):
    print('  [%s]' % label)
    bins = [(1300, 1309), (1310, 1319), (1320, 1329), (1330, 1339), (1340, 1348), (1349, 1359), (1360, 1369), (1370, 1379), (1380, 1389)]
    rate = []
    for a, b in bins:
        k = sum(1 for r in sel if a <= yr(r) <= b)
        rate.append((a, b, k, k / (b - a + 1)))
    xs = [(a + b) / 2 for a, b, k, rr in rate[:5]]
    ys = [math.log(max(rr, 0.05)) for a, b, k, rr in rate[:5]]
    mx, my = sum(xs) / 5, sum(ys) / 5
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    icpt = my - slope * mx
    print('  pre-1349 log-linear growth: x%.2f per decade' % math.exp(10 * slope))
    for a, b, k, rr in rate:
        pred = math.exp(icpt + slope * (a + b) / 2)
        print('  %d-%d  n=%3d  %.2f/yr   pre-trend projection %.2f/yr%s' % (a, b, k, rr, pred, '' if a < 1349 else '   observed/projected %.2f' % (rr / pred)))

trend(in14, 'exact + approx years')
trend([r for r in in14 if r['date_class'] == 'exact'], 'exact years only')
print('  NB 1380-89 counts only gilds founded before the returns of Nov 1388-Feb 1389.')

print('=' * 78)
print('E. STATED PURPOSES (units with any stated content; inherited "as in (a)" included)')
cont = [r for r in rows if r['content_free'] == '0']
print('Content units:', len(cont), 'of', N, '(content-free: lists, charters or blank =', N - len(cont), ')')
for v in PURP:
    k = sum(int(r[v]) for r in cont)
    print('  %-13s %s' % (v, pct(k, len(cont))))
core = sum(1 for r in cont if int(r['funeral']) or int(r['masses']) or int(r['lights']) or int(r['aid']))
print('  any of funeral/masses/lights/aid:', pct(core, len(cont)))
dead = sum(1 for r in cont if int(r['funeral']) or int(r['masses']))
print('  any provision for dead members (funeral or masses):', pct(dead, len(cont)))
tags = collections.Counter(t.strip() for r in cont for t in r['other_text'].split(';') if t.strip())
print('  "other" purposes by tag:', dict(tags.most_common()))

print('-' * 78)
print('Purposes by period of foundation (content units with year 1300-1389; exact + approx)')
pre = [r for r in cont if yr(r) is not None and 1300 <= yr(r) <= 1348]
post = [r for r in cont if yr(r) is not None and 1349 <= yr(r) <= 1389]
und = [r for r in cont if r['date_class'] in ('not_stated', 'time_out_of_mind')]
print('  variable        pre-1349 (n=%d)            post-1349 (n=%d)           undated/immemorial (n=%d)   Fisher p(pre vs post)' % (len(pre), len(post), len(und)))
for v in PURP:
    a = sum(int(r[v]) for r in pre); c = sum(int(r[v]) for r in post); u = sum(int(r[v]) for r in und)
    p = fisher_2x2(a, len(pre) - a, c, len(post) - c)
    print('  %-13s %-28s %-28s %-28s %.3f' % (v, pct(a, len(pre)), pct(c, len(post)), pct(u, len(und)), p))

print('=' * 78)
print('F. EXPLICIT PESTILENCE MENTIONS (anywhere in the calendared entry)')
pm = [r for r in rows if r['pest_mention'] == '1']
print(pct(len(pm), N))
for r in pm:
    print('  cert %s%s %s, %s (%s; p.%s): %s' % (r['cert'], r['sub'], r['place'], r['dedication'], r['date_raw'], r['page'], r['pest_snippet'][:220]))

print('=' * 78)
print('G. FOUNDERS AND CLERGY')
fo = collections.Counter(r['founders'] for r in rows)
for k, v in fo.most_common():
    print('  founders %-13s %s' % (k, pct(v, N)))
stated = N - fo['not_stated']
for k in ('parishioners', 'craft', 'mixed', 'clergy'):
    print('  among %d with founders described: %-12s %s' % (stated, k, pct(fo[k], stated)))
print('  clergy role in governance stated:', pct(sum(int(r['clergy_gov']) for r in rows), N))
print('  clergy excluded from membership/office:', pct(sum(int(r['clergy_excluded']) for r in rows), N))
ch = [r for r in cont if r['chaplain'] == '1']
print('  gilds maintaining/seeking a chaplain (lay-employed priest):', pct(len(ch), len(cont)))

print('=' * 78)
print('H. RELIABILITY (double coding of a random 10%, seed 1389)')
p2 = os.path.join(HERE, 'double_coding.csv')
if os.path.exists(p2):
    sec = {r['unit_id']: r for r in csv.DictReader(open(p2, encoding='utf-8'))}
    first = {r['unit_id']: r for r in rows}
    ids = sorted(sec)
    print('  n =', len(ids))
    for v in ['date_class', 'decade', 'period', 'pest_mention'] + PURP + ['founders', 'clergy_gov']:
        x = [str(first[i][v]) for i in ids]
        y = [str(sec[i][v]) for i in ids]
        po, k = kappa(x, y)
        dis = [i for i in ids if str(first[i][v]) != str(sec[i][v])]
        print('  %-13s agreement %.1f%%  kappa %s  disagreements: %s' % (v, 100 * po, 'n/a (no variance)' if k != k else '%.2f' % k, ','.join(dis)))
else:
    print('  double_coding.csv not found')

print('=' * 78)
print('I. CROSS-CHECK WITH TOULMIN SMITH (1870)')
p3 = os.path.join(HERE, 'crosscheck_smith.csv')
if os.path.exists(p3):
    cc = list(csv.DictReader(open(p3, encoding='utf-8')))
    agree = collections.Counter(r['agreement'] for r in cc)
    print('  n =', len(cc), dict(agree))
    for r in cc:
        if r['agreement'] != 'agree':
            print('  cert %s: Westlake "%s" vs Smith "%s" -- %s' % (r['cert'], r['westlake_date'], r['smith_date'], r['note']))
