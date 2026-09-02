# -*- coding: utf-8 -*-
"""Step 36 - CANONICAL generator of the primary 9-cluster solution (Table 1).

This is the script that writes `final_combined_table.csv` and
`final_combined_rows.json`, which 15_final_figs.py / 16_cluster_gallery.py /
25_overlay.py read.  (It was previously missing from the repository; Table 1 is
now traceable to code.)

Primary taxonomy:
  * stable-dose branch : circular KDE (kappa=12) of the PCA angle, cut at the
                         density valleys  -> 3 clusters (PCA-1..3)
  * dose-change branch : product von Mises mixture on (theta_min, theta_max),
                         K = 6 (investigator-chosen; ICL/BIC did not turn over)
Clusters are derived on POSITIVE tests only; negatives are assigned to the
fitted clusters.

Clustering reproducibility (bootstrap ARI, per-cluster Jaccard, bootstrap P/N
intervals) is computed by 40_stability.py, which reuses the same fitting code.
Outputs: final_combined_table.csv, final_combined_rows.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import pandas as pd

OUT = _os.path.join(ROOT, r'analysis')
NBOOT = 500
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
TP, TN = pos_pd.shape[0], neg_pd.shape[0]
assert (TP, TN) == (3401, 6499)

up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un

# ---------------- stable-dose branch: circular KDE valleys ----------------
proj = lambda pd_, ds_, mk: (np.hstack([pd_[mk], ds_[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - 0.0270, proj(pos_pd, pos_ds, up)[:, 0] + 0.04) % (2 * np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - 0.0270, proj(neg_pd, neg_ds, un)[:, 0] + 0.04) % (2 * np.pi)
GRID = np.linspace(0, 2 * np.pi, 721)[:-1]

def kde_cuts(theta, kappa=12.0):
    """circular KDE on GRID, cut at the density minima (vectorised)"""
    d = np.exp(kappa * np.cos(GRID[:, None] - theta[None, :])).sum(1)
    lo = np.roll(d, 1); hi = np.roll(d, -1)
    return np.sort(GRID[(d < lo) & (d <= hi)])

cuts = kde_cuts(thp)
pca_p = np.searchsorted(cuts, thp) % len(cuts); pca_n = np.searchsorted(cuts, thn) % len(cuts)

# ---------------- dose-change branch: product von Mises, K=6 ----------------
def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999)
    return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
def fit7(t1, t2, K=6, seed=0, it=150, n_init=5):
    lab = KMeans(K, n_init=n_init, random_state=seed).fit_predict(np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
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

tmn_p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); tmx_p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
tmn_n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); tmx_n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
pr = fit7(tmn_p, tmx_p, 6)
s7p = asg7(tmn_p, tmx_p, pr); s7n = asg7(tmn_n, tmx_n, pr)

clab_p = np.empty(TP, object); clab_p[up] = [f'PCA-{c+1}' for c in pca_p]; clab_p[svp] = [f'7d-{c+1}' for c in s7p]
clab_n = np.empty(TN, object); clab_n[un] = [f'PCA-{c+1}' for c in pca_n]; clab_n[svn] = [f'7d-{c+1}' for c in s7n]
clab = np.r_[clab_p, clab_n]; outcome = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
clusters = sorted(set(clab), key=lambda s: (s.split('-')[0], int(s.split('-')[1])))

rows = []
for c in clusters:
    inc = (clab == c).astype(float)
    res = sm.Logit(outcome, sm.add_constant(inc)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
    b, se = res.params[1], res.bse[1]
    posN = int(((clab == c) & (outcome == 1)).sum()); negN = int(((clab == c) & (outcome == 0)).sum())
    rows.append(dict(cluster=c, branch=c.split('-')[0], posN=posN, negN=negN, PN=(posN / TP) / (negN / TN),
                     OR=float(np.exp(b)), lo=float(np.exp(b - 1.96 * se)), hi=float(np.exp(b + 1.96 * se)),
                     p=float(res.pvalues[1])))
qv = multipletests([r['p'] for r in rows], method='fdr_bh')[1]
for r, q in zip(rows, qv):
    r['q'] = float(q)
    r['label'] = ('Higher-risk' if r['PN'] > 1.2 and q < 0.05 else ('Lower-risk' if r['PN'] < 0.83 and q < 0.05 else 'ns'))
pd.DataFrame(rows).to_csv(OUT + r'\final_combined_table.csv', index=False)
json.dump(rows, open(OUT + r'\final_combined_rows.json', 'w', encoding='utf-8'), indent=1)
print('=== PRIMARY 9-cluster solution (Table 1) ===')
print(f'KDE valleys (deg): {[round(float(x)) for x in np.rad2deg(cuts)]}')
for r in sorted(rows, key=lambda r: -r['PN']):
    print(f"  {r['cluster']:7} pos={r['posN']:4d} neg={r['negN']:4d} P/N={r['PN']:.2f} "
          f"OR={r['OR']:.2f}({r['lo']:.2f}-{r['hi']:.2f}) q={r['q']:.1e} {r['label']}")

print('\nsaved final_combined_table.csv, final_combined_rows.json')
print('run 40_stability.py for the bootstrap reproducibility metrics')
