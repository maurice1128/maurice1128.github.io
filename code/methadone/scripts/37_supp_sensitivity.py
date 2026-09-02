# -*- coding: utf-8 -*-
"""Step 37 - SUPPLEMENTARY TABLE S1: every cluster x every sensitivity analysis.

Columns per cluster:
  primary            P/N, OR (95% CI), q            (patient-clustered logistic, FDR)
  attendance-adj     OR, q                          (+ pre-test attendance covariate)
  complete-attend    P/N, q                         (tests with full +-7 d attendance)
  true-neg (pub)     P/N, q                         all 3,401 positives vs supervised negatives
  true-neg (LFL)     P/N, q                         LIKE-FOR-LIKE: positives AND negatives
                                                    both restricted to supervised patients
  within-patient     OR, p                          conditional logistic, one indicator per model

Plus:
  * outcome-blind crosswalk: contingency table + ARI between the 9 primary and the
    10 outcome-blind clusters, and the direction/size of every outcome-blind cluster
  * case-mix diagnostics for the supervised (true-negative) subset

Writes supp_table_S1.csv, supp_outcomeblind_crosswalk.csv, supp_sensitivity_summary.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings, openpyxl; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.discrete.conditional_models import ConditionalLogit
import pandas as pd

OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
TP, TN = 3401, 6499
y = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un

GRID = np.linspace(0, 2 * np.pi, 721)[:-1]
def kde_cuts(theta, kappa=12.0):
    d = np.array([np.exp(kappa * np.cos(g - theta)).sum() for g in GRID])
    return np.sort(GRID[[i for i in range(len(d)) if d[i] < d[(i - 1) % len(d)] and d[i] <= d[(i + 1) % len(d)]]])
def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999); return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
def fit7(t1, t2, K=6, seed=0, it=150):
    lab = KMeans(K, n_init=5, random_state=seed).fit_predict(np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab, np.arange(len(t1))] = 1
    m1 = np.zeros(K); k1 = np.ones(K); m2_ = np.zeros(K); k2 = np.ones(K); pi = np.ones(K) / K
    for _ in range(it):
        for k in range(K):
            w = P[k]; m1[k], k1[k] = vm_mle(t1, w); m2_[k], k2[k] = vm_mle(t2, w); pi[k] = w.mean() + 1e-9
        P = np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(K)]); P /= P.sum(0) + 1e-300
    return (m1, k1, m2_, k2, pi)
def asg7(t1, t2, pr):
    m1, k1, m2_, k2, pi = pr
    return np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(len(pi))]).argmax(0)

# ---------- primary (positive-derived) labels ----------
proj = lambda pd_, ds_, mk: (np.hstack([pd_[mk], ds_[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - 0.0270, proj(pos_pd, pos_ds, up)[:, 0] + 0.04) % (2 * np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - 0.0270, proj(neg_pd, neg_ds, un)[:, 0] + 0.04) % (2 * np.pi)
cuts = kde_cuts(thp)
pca_p = np.searchsorted(cuts, thp) % len(cuts); pca_n = np.searchsorted(cuts, thn) % len(cuts)
tmn_p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); tmx_p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
tmn_n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); tmx_n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
pr = fit7(tmn_p, tmx_p, 6)
clab_p = np.empty(TP, object); clab_p[up] = [f'PCA-{c+1}' for c in pca_p]; clab_p[svp] = [f'7d-{c+1}' for c in asg7(tmn_p, tmx_p, pr)]
clab_n = np.empty(TN, object); clab_n[un] = [f'PCA-{c+1}' for c in pca_n]; clab_n[svn] = [f'7d-{c+1}' for c in asg7(tmn_n, tmx_n, pr)]
clab = np.r_[clab_p, clab_n]
clusters = sorted(set(clab), key=lambda s: (s.split('-')[0], int(s.split('-')[1])))

# ---------- supervised (true-negative) patient list ----------
wb = openpyxl.load_workbook(_os.path.join(ROOT, r'raw data\陪同驗尿的名單.xlsx'), read_only=True, data_only=True)
ws = wb.active; it = ws.iter_rows(values_only=True); next(it)
sup = set()
for r in it:
    if r[1] is not None:
        try: sup.add(int(r[1]))
        except Exception: pass
wb.close()
sup_p = np.isin(pidp, list(sup)); sup_n = np.isin(pidn, list(sup))

def logit_p(yv, X, groups):
    try:
        r = sm.Logit(yv, sm.add_constant(X)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': groups})
        return float(np.exp(r.params[1])), float(np.exp(r.params[1] - 1.96 * r.bse[1])), float(np.exp(r.params[1] + 1.96 * r.bse[1])), float(r.pvalues[1])
    except Exception:
        return np.nan, np.nan, np.nan, np.nan

# ================= build the table =================
rec = {c: dict(cluster=c) for c in clusters}
comp = att >= 0.99                                  # complete +-7 d attendance
TPc = int(y[comp].sum()); TNc = int((y[comp] == 0).sum())
nT_pub = int(sup_n.sum())                           # supervised negatives
lfl = np.r_[sup_p, sup_n]                           # like-for-like mask over all tests
TPl = int(sup_p.sum()); TNl = int(sup_n.sum())

pv = {k: [] for k in ['primary', 'attadj', 'comp', 'tnpub', 'tnlfl', 'within']}
for c in clusters:
    inc = (clab == c).astype(float)
    posN = int(((clab == c) & (y == 1)).sum()); negN = int(((clab == c) & (y == 0)).sum())
    r = rec[c]; r.update(posN=posN, negN=negN, PN=(posN / TP) / (negN / TN))
    o, lo, hi, p = logit_p(y, inc, pid); r.update(OR=o, lo=lo, hi=hi); pv['primary'].append(p)
    # attendance-adjusted
    o2, _, _, p2 = logit_p(y, np.column_stack([inc, att]), pid); r.update(OR_attadj=o2); pv['attadj'].append(p2)
    # complete-attendance subset
    pN = int(((clab == c) & comp & (y == 1)).sum()); nN = int(((clab == c) & comp & (y == 0)).sum())
    r['PN_comp'] = (pN / TPc) / (nN / TNc) if nN else np.nan
    r['posN_comp'] = pN; r['negN_comp'] = nN
    _, _, _, p3 = logit_p(y[comp], inc[comp], pid[comp]) if (pN >= 5 and nN >= 5) else (0, 0, 0, np.nan)
    pv['comp'].append(p3)
    # true-negative as published: ALL positives vs supervised negatives
    negT = int((clab_n[sup_n] == c).sum())
    r['PN_tn_pub'] = (posN / TP) / (negT / nT_pub) if negT else np.nan
    mk = np.r_[np.ones(TP, bool), sup_n]
    _, _, _, p4 = logit_p(y[mk], inc[mk], pid[mk]); pv['tnpub'].append(p4)
    # true-negative LIKE-FOR-LIKE: positives also restricted to supervised patients
    posL = int((clab_p[sup_p] == c).sum())
    r['posN_lfl'] = posL; r['negN_lfl'] = negT
    r['PN_tn_lfl'] = (posL / TPl) / (negT / TNl) if negT else np.nan
    _, _, _, p5 = logit_p(y[lfl], inc[lfl], pid[lfl]) if (posL >= 5 and negT >= 5) else (0, 0, 0, np.nan)
    pv['tnlfl'].append(p5)
    # within-patient conditional logistic, one indicator per model
    try:
        cr = ConditionalLogit(y, inc.reshape(-1, 1), groups=pid).fit(disp=0)
        r['OR_within'] = float(np.exp(cr.params[0])); pv['within'].append(float(cr.pvalues[0]))
    except Exception:
        r['OR_within'] = np.nan; pv['within'].append(np.nan)

for key, dst in [('primary', 'q'), ('attadj', 'q_attadj'), ('comp', 'q_comp'),
                 ('tnpub', 'q_tn_pub'), ('tnlfl', 'q_tn_lfl'), ('within', 'p_within')]:
    arr = np.array(pv[key], float); ok = np.isfinite(arr)
    qq = np.full(len(arr), np.nan)
    if key == 'within':
        qq = arr
    else:
        qq[ok] = multipletests(arr[ok], method='fdr_bh')[1]
    for c, q in zip(clusters, qq): rec[c][dst] = float(q)

df = pd.DataFrame([rec[c] for c in clusters])
df.to_csv(OUT + r'\supp_table_S1.csv', index=False)

print('=== SUPPLEMENTARY TABLE S1: all clusters x all sensitivity analyses ===')
print(f'complete-attendance subset: {int(comp.sum())} tests ({TPc} pos / {TNc} neg)')
print(f'supervised (true-negative) subset: {TNl} negatives, {TPl} positives, '
      f'{len(set(pidn[sup_n]))} neg patients / {len(set(pidp[sup_p]))} pos patients')
hdrs = f"{'cluster':7} {'P/N':>5} {'q':>8} | {'ORadj':>6} {'q':>8} | {'P/Ncomp':>7} {'q':>8} | {'P/Ntn':>6} {'q':>8} | {'P/NtnLFL':>8} {'q':>8} | {'ORwith':>6} {'p':>8}"
print(hdrs)
for c in clusters:
    r = rec[c]
    print(f"{c:7} {r['PN']:5.2f} {r['q']:8.1e} | {r['OR_attadj']:6.2f} {r['q_attadj']:8.1e} | "
          f"{r['PN_comp']:7.2f} {r['q_comp']:8.1e} | {r['PN_tn_pub']:6.2f} {r['q_tn_pub']:8.1e} | "
          f"{r['PN_tn_lfl']:8.2f} {r['q_tn_lfl']:8.1e} | {r['OR_within']:6.2f} {r['p_within']:8.1e}")

# ---------- case-mix of the supervised subset ----------
print('\n=== case-mix diagnostics for the supervised (true-negative) subset ===')
allpid = np.r_[pidp, pidn]
supmask = np.isin(allpid, list(sup))
dd = pd.DataFrame(dict(pid=allpid, y=y, sup=supmask))
per = dd.groupby('pid').agg(rate=('y', 'mean'), sup=('sup', 'first'), n=('y', 'size'))
print(f"  patients with any supervised-collection flag: {int(per.sup.sum())} of {len(per)}")
print(f"  mean per-patient positive rate: supervised {per[per.sup].rate.mean():.3f} vs "
      f"other {per[~per.sup].rate.mean():.3f}")
print(f"  positives from supervised patients: {TPl} / {TP} ({TPl/TP*100:.1f}%)")
print(f"  negatives from supervised patients: {TNl} / {TN} ({TNl/TN*100:.1f}%)")
print('  -> the published true-negative analysis compares ALL positives against negatives drawn')
print('     from a lower-risk subpopulation; the like-for-like column removes that mismatch.')

# ---------- outcome-blind crosswalk ----------
print('\n=== outcome-blind clustering: crosswalk against the primary taxonomy ===')
pd_all = np.vstack([pos_pd, neg_pd]); ds_all = np.vstack([pos_ds, neg_ds])
upa = np.r_[up, un]; sva = ~upa
X = np.hstack([pd_all[upa], ds_all[upa]]); muB = X.mean(0)
coefB = np.linalg.svd(X - muB, full_matrices=False)[2].T
thB = np.arctan2(((X - muB) @ coefB)[:, 1], ((X - muB) @ coefB)[:, 0]) % (2 * np.pi)
cutB = kde_cuts(thB); labB_pca = np.searchsorted(cutB, thB) % len(cutB)
mna = np.r_[pos['mn_a'], neg['mn_a']]; mnb = np.r_[pos['mn_b'], neg['mn_b']]
mxa = np.r_[pos['mx_a'], neg['mx_a']]; mxb = np.r_[pos['mx_b'], neg['mx_b']]
t1B = np.arctan2(mnb[sva], mna[sva]); t2B = np.arctan2(mxb[sva], mxa[sva])
prB = fit7(t1B, t2B, 6, it=120); labB_7 = asg7(t1B, t2B, prB)
clabB = np.empty(len(y), object)
clabB[upa] = [f'ob-PCA-{c+1}' for c in labB_pca]; clabB[sva] = [f'ob-7d-{c+1}' for c in labB_7]
obs = sorted(set(clabB), key=lambda s: (s.split('-')[1], int(s.split('-')[2])))
rowsB = []
for c in obs:
    inc = (clabB == c).astype(float)
    pN = int(((clabB == c) & (y == 1)).sum()); nN = int(((clabB == c) & (y == 0)).sum())
    o, lo, hi, p = logit_p(y, inc, pid)
    rowsB.append(dict(cluster=c, posN=pN, negN=nN, PN=(pN / TP) / (nN / TN) if nN else np.nan, OR=o, p=p))
qB = multipletests([r['p'] for r in rowsB], method='fdr_bh')[1]
for r, q in zip(rowsB, qB):
    r['q'] = float(q)
    r['direction'] = 'higher-risk' if (r['PN'] > 1.2 and q < 0.05) else ('lower-risk' if (r['PN'] < 0.83 and q < 0.05) else 'ns/intermediate')
print(f'{"outcome-blind":14} {"P/N":>5} {"OR":>5} {"q":>9}  direction')
for r in rowsB:
    print(f"{r['cluster']:14} {r['PN']:5.2f} {r['OR']:5.2f} {r['q']:9.1e}  {r['direction']}")
ct = pd.crosstab(pd.Series(clab, name='primary'), pd.Series(clabB, name='outcome_blind'))
ct.to_csv(OUT + r'\supp_outcomeblind_crosswalk.csv')
print('\ncrosswalk (rows = primary cluster, cols = outcome-blind cluster):')
print(ct.to_string())
ari_ob = adjusted_rand_score(clab, clabB)
print(f'\nadjusted Rand index between the primary and outcome-blind partitions: {ari_ob:.3f}')
# direction agreement for the best-matching outcome-blind cluster of each primary cluster
print('\nbest-matching outcome-blind cluster per primary cluster (by Jaccard) and direction agreement:')
dirB = {r['cluster']: r['direction'] for r in rowsB}; pnB = {r['cluster']: r['PN'] for r in rowsB}
agree = 0; tot = 0
match_rows = []
for c in clusters:
    A = clab == c
    best = max(obs, key=lambda b: (A & (clabB == b)).sum() / max((A | (clabB == b)).sum(), 1))
    j = (A & (clabB == best)).sum() / max((A | (clabB == best)).sum(), 1)
    dprim = rec[c]
    dirp = 'higher-risk' if (dprim['PN'] > 1.2 and dprim['q'] < 0.05) else ('lower-risk' if (dprim['PN'] < 0.83 and dprim['q'] < 0.05) else 'ns/intermediate')
    ok = (dirp == dirB[best]); agree += ok; tot += 1
    match_rows.append(dict(primary=c, PN_primary=dprim['PN'], direction_primary=dirp,
                           best_outcome_blind=best, jaccard=float(j), PN_ob=pnB[best],
                           direction_ob=dirB[best], direction_agrees=bool(ok)))
    print(f"  {c:7} P/N={dprim['PN']:.2f} ({dirp:16}) -> {best:12} J={j:.2f} P/N={pnB[best]:.2f} ({dirB[best]:16}) {'MATCH' if ok else 'DIFFERS'}")
print(f'  direction agreement: {agree}/{tot} matched clusters')
pd.DataFrame(match_rows).to_csv(OUT + r'\supp_outcomeblind_match.csv', index=False)

json.dump(dict(n_complete_attendance=int(comp.sum()), TPc=TPc, TNc=TNc,
               n_sup_neg=TNl, n_sup_pos=TPl,
               n_sup_pat_neg=len(set(pidn[sup_n])), n_sup_pat_pos=len(set(pidp[sup_p])),
               mean_pat_posrate_sup=float(per[per.sup].rate.mean()),
               mean_pat_posrate_other=float(per[~per.sup].rate.mean()),
               ari_primary_vs_outcomeblind=float(ari_ob),
               outcome_blind_direction_agreement=f'{agree}/{tot}',
               outcome_blind=rowsB),
          open(OUT + r'\supp_sensitivity_summary.json', 'w'), indent=2, default=float)
print('\nsaved supp_table_S1.csv, supp_outcomeblind_crosswalk.csv, supp_outcomeblind_match.csv, supp_sensitivity_summary.json')
