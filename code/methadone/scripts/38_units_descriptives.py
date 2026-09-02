# -*- coding: utf-8 -*-
"""Step 38 - reporting-scale harmonisation + Methods descriptives.

(a) ATTENDANCE on ONE scale.  The attendance variable is a 0-1 proportion
    (attended days in the 7 days before the test / 7).  The manuscript had
    quoted it per unit (pooled) and per SD (within-patient/temporal), which are
    not comparable.  This prints every estimate on all three scales.
(b) CURATED vs RAW-DATA reconstruction of the escalation association, using the
    SAME estimand (post-test maximum 3-day slope of the day-(-7)-normalised
    consumed dose) on both pipelines, with sample sizes.  The pipelines differ
    only in that the curated one linearly interpolates non-attended days while
    the raw reconstruction uses observed days only.
(c) IMPUTATION extent (proportion of days linearly interpolated).
(d) PCA variance explained by PC1/PC2 for the stable-dose branch.
(e) Stable-dose clusters restricted to tests with NO imputed day in the +-28 d
    window (the complete-attendance check in the paper only covers +-7 d).
(f) columns available in the daily-dose extract (observed vs take-home dosing).
Writes units_descriptives.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, json, os, openpyxl, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.discrete.conditional_models import ConditionalLogit

OUT = _os.path.join(ROOT, r'analysis'); RAW = _os.path.join(ROOT, r'raw data')
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu']); explained = v(f['explained'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
raw = cells('All_raw_fix'); rpos, rneg = m2(raw[0]), m2(raw[2])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
res = {}

# ---------------- (a) attendance on one scale ----------------
print('=== (a) ATTENDANCE: one variable, three scales ===')
sd_att = float(att.std())
print(f'attendance is a 0-1 proportion; SD in the analysis sample = {sd_att:.3f}')
r = sm.Logit(y, sm.add_constant(att)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
b_unit, p_pool = float(r.params[1]), float(r.pvalues[1])
print(f'POOLED (patient-clustered logistic):')
print(f'   per 1.00 (0 -> 100% attendance): OR = {np.exp(b_unit):.3f}   p = {p_pool:.1e}')
print(f'   per 0.10 increment             : OR = {np.exp(b_unit*0.10):.3f}')
print(f'   per SD ({sd_att:.3f})                 : OR = {np.exp(b_unit*sd_att):.3f}')
cw = ConditionalLogit(y, att.reshape(-1, 1), groups=pid).fit(disp=0)
b_w, p_w = float(cw.params[0]), float(cw.pvalues[0])
print(f'WITHIN-PATIENT (conditional logistic, patient fixed effects):')
print(f'   per 1.00                       : OR = {np.exp(b_w):.3f}   p = {p_w:.1e}')
print(f'   per 0.10 increment             : OR = {np.exp(b_w*0.10):.3f}')
print(f'   per SD ({sd_att:.3f})                 : OR = {np.exp(b_w*sd_att):.3f}')
print('   -> the pooled and within-patient estimates must be compared on the SAME scale.')
res['attendance'] = dict(sd=sd_att,
                         pooled_per_unit=float(np.exp(b_unit)), pooled_per_0p1=float(np.exp(b_unit * .1)),
                         pooled_per_sd=float(np.exp(b_unit * sd_att)), pooled_p=p_pool,
                         within_per_unit=float(np.exp(b_w)), within_per_0p1=float(np.exp(b_w * .1)),
                         within_per_sd=float(np.exp(b_w * sd_att)), within_p=p_w,
                         mean_pos=float(att[:TP].mean()), mean_neg=float(att[TP:].mean()))

# escalation, both scales, pooled and within
print('\n--- escalation slopes (for reference; reported per SD throughout) ---')
z = lambda x: (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)
esc_post = np.r_[pos['mx_a'], neg['mx_a']]; esc_pre = np.r_[pos['mx_b'], neg['mx_b']]
for nm, col in [('post-test escalation', esc_post), ('pre-test escalation', esc_pre)]:
    rp = sm.Logit(y, sm.add_constant(z(col))).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
    rw = ConditionalLogit(y, z(col).reshape(-1, 1), groups=pid).fit(disp=0)
    print(f'  {nm:22s} pooled OR/SD={np.exp(rp.params[1]):.2f} (p={rp.pvalues[1]:.1e}) | '
          f'within OR/SD={np.exp(rw.params[0]):.2f} (p={rw.pvalues[0]:.1e})')
    res[nm.replace(' ', '_')] = dict(pooled_or_sd=float(np.exp(rp.params[1])), pooled_p=float(rp.pvalues[1]),
                                     within_or_sd=float(np.exp(rw.params[0])), within_p=float(rw.pvalues[0]))

# ---------------- (c) imputation extent ----------------
print('\n=== (c) IMPUTATION of non-attended days (Index_ver2.m linear fill) ===')
imp = {}
for nm, rr in [('positive', rpos), ('negative', rneg)]:
    miss = (rr == -1)
    imp[nm] = dict(frac_days_28=float(miss[:, :57].mean()), frac_days_7=float(miss[:, 21:36].mean()),
                   rows_any_7=float(miss[:, 21:36].any(1).mean()), rows_any_28=float(miss[:, :57].any(1).mean()),
                   anchor_imputed=float((rr[:, 21] == -1).mean()))
    print(f'  {nm}: imputed days = {imp[nm]["frac_days_7"]*100:.1f}% of the +-7 d window, '
          f'{imp[nm]["frac_days_28"]*100:.1f}% of the +-28 d window')
    print(f'      tests with >=1 imputed day: {imp[nm]["rows_any_7"]*100:.0f}% (+-7 d), '
          f'{imp[nm]["rows_any_28"]*100:.0f}% (+-28 d); anchor day (-7) imputed in '
          f'{imp[nm]["anchor_imputed"]*100:.1f}% of tests')
anc = np.r_[m2(cells("All_fill")[0])[:, 21], m2(cells("All_fill")[2])[:, 21]]
print(f'  anchor (day -7) consumed dose after filling: min={anc.min():.1f} mg, median={np.median(anc):.1f} mg, '
      f'zero in {int((anc==0).sum())} tests  -> the ratio normalisation d_t / d_(-7) is always defined')
res['imputation'] = imp; res['anchor_min_mg'] = float(anc.min()); res['anchor_zero_n'] = int((anc == 0).sum())

# ---------------- (d) PCA variance explained ----------------
print('\n=== (d) stable-dose branch PCA ===')
print(f'  PC1 = {explained[0]:.1f}% of variance, PC2 = {explained[1]:.1f}%, PC1+PC2 = {explained[0]+explained[1]:.1f}%')
print(f'  (PC3 = {explained[2]:.1f}%, so the angle theta is taken in a plane carrying most of the signal)')
res['pca_explained'] = [float(x) for x in explained[:5]]

# ---------------- (e) +-28-day fully-observed subset for the PCA branch ----------------
print('\n=== (e) stable-dose clusters restricted to tests with NO imputed day in +-28 d ===')
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0)
proj = lambda pd_, ds_, mk: (np.hstack([pd_[mk], ds_[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - .0270, proj(pos_pd, pos_ds, up)[:, 0] + .04) % (2 * np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - .0270, proj(neg_pd, neg_ds, un)[:, 0] + .04) % (2 * np.pi)
GRID = np.linspace(0, 2 * np.pi, 721)[:-1]
d = np.array([np.exp(12 * np.cos(g - thp)).sum() for g in GRID])
cuts = np.sort(GRID[[i for i in range(len(d)) if d[i] < d[(i - 1) % len(d)] and d[i] <= d[(i + 1) % len(d)]]])
lp = np.searchsorted(cuts, thp) % len(cuts); ln = np.searchsorted(cuts, thn) % len(cuts)
clab = np.empty(TP + TN, object); clab[:TP][up] = [f'PCA-{c+1}' for c in lp]; clab[TP:][un] = [f'PCA-{c+1}' for c in ln]
full28 = np.r_[~(rpos == -1).any(1), ~(rneg == -1).any(1)]
sub = full28 & np.array([isinstance(x, str) for x in clab])
TPs = int(((y == 1) & full28).sum()); TNs = int(((y == 0) & full28).sum())
print(f'  tests with a fully observed +-28 d window: {int(full28.sum())} / {TP+TN} '
      f'({TPs} pos / {TNs} neg)')
rows = []
for c in [f'PCA-{i+1}' for i in range(len(cuts))]:
    m = (clab == c) & full28
    pN = int((m & (y == 1)).sum()); nN = int((m & (y == 0)).sum())
    pn = (pN / TPs) / (nN / TNs) if nN else np.nan
    if pN >= 5 and nN >= 5:
        rr = sm.Logit(y[full28], sm.add_constant(((clab == c) & full28)[full28].astype(float))).fit(
            disp=0, cov_type='cluster', cov_kwds={'groups': pid[full28]})
        p = float(rr.pvalues[1]); o = float(np.exp(rr.params[1]))
    else:
        p, o = np.nan, np.nan
    rows.append((c, pN, nN, pn, o, p))
qs = multipletests([r[5] if np.isfinite(r[5]) else 1 for r in rows], method='fdr_bh')[1]
res['pca_full28'] = []
for (c, pN, nN, pn, o, p), q in zip(rows, qs):
    tag = 'HIGH' if pn > 1.2 and q < .05 else ('LOW' if pn < 0.83 and q < .05 else 'ns')
    print(f'  {c:7} pos={pN:4d} neg={nN:4d} P/N={pn:.2f} OR={o:.2f} q={q:.1e} {tag}')
    res['pca_full28'].append(dict(cluster=c, posN=pN, negN=nN, PN=float(pn), OR=float(o), q=float(q), label=tag))

# ---------------- (b) curated vs raw-data reconstruction ----------------
print('\n=== (b) CURATED vs RAW-DATA reconstruction of the escalation association ===')
rc = sm.Logit(y, sm.add_constant(z(esc_post))).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
print(f'  curated (aim2.mat, interpolated series): n = {TP+TN}, OR = {np.exp(rc.params[1]):.2f} per SD, p = {rc.pvalues[1]:.1e}')

def roc2d(vv):
    try: vv = int(vv)
    except Exception: return None
    yy, mm, dd = vv // 10000, (vv // 100) % 100, vv % 100
    if not (1 <= mm <= 12 and 1 <= dd <= 31): return None
    try: return pd.Timestamp(year=yy + 1911, month=mm, day=dd)
    except Exception: return None
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022驗尿結果.xlsx'), read_only=True, data_only=True)
ws = wb['驗尿結果']; it = ws.iter_rows(values_only=True); next(it); ur = []
for r_ in it:
    if r_[2] == 1 and r_[3] in (0, 1):
        dd = roc2d(r_[1])
        if dd is not None: ur.append((int(r_[0]), dd, int(r_[3])))
wb.close()
mor = pd.DataFrame(ur, columns=['pid', 'date', 'pos']).drop_duplicates(['pid', 'date'])
dose = pd.read_parquet(os.path.join(OUT, 'dose_cache.parquet'))
dose_by = {p: g.set_index('date')['dose_cc'].sort_index() for p, g in dose.groupby('pid')}
keep = set(np.r_[pidp, pidn].tolist())
rows = []
for t in mor[mor.pid.isin(keep)].itertuples(index=False):
    s = dose_by.get(t.pid)
    if s is None: continue
    ref = s[s.index == t.date - pd.Timedelta(days=7)]
    if len(ref) == 0 or ref.iloc[0] == 0: continue
    refv = float(ref.iloc[0]); sl = []
    for k in range(0, 6):                      # post-test 3-day windows, mirroring MATLAB idx 29:34
        pts = [(o, s[s.index == t.date + pd.Timedelta(days=o)]) for o in (k, k + 1, k + 2)]
        pts = [(o, float(x.iloc[0]) / refv) for o, x in pts if len(x)]
        if len(pts) >= 2: sl.append(np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)[0])
        # NOTE: only OBSERVED days are used -- no interpolation
    if sl: rows.append((t.pid, t.pos, max(sl)))
dfr = pd.DataFrame(rows, columns=['pid', 'pos', 'esc']).dropna()
rr = sm.Logit(dfr.pos.values, sm.add_constant(z(dfr.esc.values))).fit(disp=0, cov_type='cluster', cov_kwds={'groups': dfr.pid.values})
print(f'  raw reconstruction (observed days only, no interpolation): n = {len(dfr)}, '
      f'OR = {np.exp(rr.params[1]):.2f} per SD, p = {rr.pvalues[1]:.1e}')
print('  Pipelines differ ONLY in the treatment of non-attended days (interpolated vs dropped),')
print('  and in that the raw reconstruction does not apply the Index_ver2 window-completeness drop.')
res['escalation_pipelines'] = dict(curated_n=TP + TN, curated_or_sd=float(np.exp(rc.params[1])), curated_p=float(rc.pvalues[1]),
                                   raw_n=int(len(dfr)), raw_or_sd=float(np.exp(rr.params[1])), raw_p=float(rr.pvalues[1]))

# ---------------- (f) daily-dose extract columns ----------------
print('\n=== (f) daily-dose extract: what is recorded ===')
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022美沙冬每日劑量.xlsx'), read_only=True, data_only=True)
ws = wb['2018-2020美沙冬']; it = ws.iter_rows(values_only=True)
hdr_row = next(it); ex = [next(it) for _ in range(3)]
wb.close()
print('  header:', hdr_row)
for e in ex: print('  example:', e)
res['dose_header'] = [str(x) for x in hdr_row]

json.dump(res, open(OUT + r'\units_descriptives.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('\nsaved units_descriptives.json')
