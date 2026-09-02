# -*- coding: utf-8 -*-
"""Step 40 - clustering reproducibility for the primary 9-cluster solution.

Each branch is bootstrapped with ITS OWN procedure -- this is the correction to
the earlier metric, in which the stable-dose figure came from bootstrapping a
von Mises mixture rather than the density-valley cut actually used for Table 1.

  stable-dose branch : every bootstrap sample re-estimates the circular KDE and
                       re-derives the density valleys, then re-labels the full
                       data with those cut-points
  dose-change branch : every bootstrap sample is an independent product-von-Mises
                       K = 6 refit (k-means initialised), then re-labels the full data

Reports, for each branch: bootstrap adjusted Rand index vs the full-data solution;
and for each cluster: mean best-match Jaccard across refits, and the bootstrap
2.5-97.5% interval of its P/N ratio (i.e. the effect-size uncertainty coming from
clustering instability rather than sampling error alone).

Writes final_stability.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings, sys; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

OUT = _os.path.join(ROOT, r'analysis')
NBOOT = int(sys.argv[1]) if len(sys.argv) > 1 else 500
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
f.close()
TP, TN = pos_pd.shape[0], neg_pd.shape[0]
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un

GRID = np.linspace(0, 2 * np.pi, 721)[:-1]
def kde_cuts(theta, kappa=12.0, chunk=256):
    d = np.zeros(len(GRID))
    for s in range(0, len(theta), chunk):
        d += np.exp(kappa * np.cos(GRID[:, None] - theta[None, s:s + chunk])).sum(1)
    lo = np.roll(d, 1); hi = np.roll(d, -1)
    return np.sort(GRID[(d < lo) & (d <= hi)])
def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999); return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
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

proj = lambda pd_, ds_, mk: (np.hstack([pd_[mk], ds_[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - 0.0270, proj(pos_pd, pos_ds, up)[:, 0] + 0.04) % (2 * np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - 0.0270, proj(neg_pd, neg_ds, un)[:, 0] + 0.04) % (2 * np.pi)
cuts = kde_cuts(thp)
pca_p = np.searchsorted(cuts, thp) % len(cuts); pca_n = np.searchsorted(cuts, thn) % len(cuts)
tmn_p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); tmx_p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
tmn_n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); tmx_n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
pr = fit7(tmn_p, tmx_p, 6)
s7p = asg7(tmn_p, tmx_p, pr)
print(f'full-data solution: KDE valleys {[round(float(x)) for x in np.rad2deg(cuts)]}, von Mises K=6', flush=True)

def jaccard(base, boot, K):
    out = np.full(K, np.nan)
    for a in range(K):
        A = base == a
        if A.sum() == 0: continue
        out[a] = max(((A & (boot == b)).sum()) / max((A | (boot == b)).sum(), 1) for b in range(K))
    return out

rs = np.random.RandomState(0)
Kp = len(cuts)
ari_pca, jac_pca, ncut = [], [], []
pn_pca = {c: [] for c in range(Kp)}
n_p = len(thp)
for i in range(NBOOT):
    idx = rs.choice(n_p, n_p, replace=True)
    cb = kde_cuts(thp[idx]); ncut.append(len(cb))
    if len(cb) == 0: continue
    lb_p = np.searchsorted(cb, thp) % len(cb)
    ari_pca.append(adjusted_rand_score(pca_p, lb_p))
    if len(cb) == Kp:
        jac_pca.append(jaccard(pca_p, lb_p, Kp))
        lb_n = np.searchsorted(cb, thn) % len(cb)
        for c in range(Kp):
            pN = int((lb_p == c).sum()); nN = int((lb_n == c).sum())
            if nN: pn_pca[c].append((pN / TP) / (nN / TN))
    if (i + 1) % 100 == 0: print(f'  stable-dose bootstrap {i+1}/{NBOOT}', flush=True)
jac_pca = np.array(jac_pca) if jac_pca else np.zeros((0, Kp))

ari7, jac7 = [], []
pn_7 = {c: [] for c in range(6)}
n7 = len(tmn_p)
for i in range(NBOOT):
    idx = rs.choice(n7, n7, replace=True)
    prb = fit7(tmn_p[idx], tmx_p[idx], 6, seed=0, it=60, n_init=1)
    lb_p = asg7(tmn_p, tmx_p, prb); lb_n = asg7(tmn_n, tmx_n, prb)
    ari7.append(adjusted_rand_score(s7p, lb_p)); jac7.append(jaccard(s7p, lb_p, 6))
    for c in range(6):
        pN = int((lb_p == c).sum()); nN = int((lb_n == c).sum())
        if nN: pn_7[c].append((pN / TP) / (nN / TN))
    if (i + 1) % 50 == 0: print(f'  dose-change bootstrap {i+1}/{NBOOT}', flush=True)
jac7 = np.array(jac7)

def interval(a):
    return (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))) if len(a) > 10 else (float('nan'), float('nan'))

ari_pca_m = float(np.mean(ari_pca)); ari7_m = float(np.mean(ari7))
print(f'\n=== reproducibility ({NBOOT} bootstrap refits per branch) ===')
print(f'stable-dose branch (KDE-valley procedure refit each time): ARI = {ari_pca_m:.3f}')
print(f'   valleys recovered: median {int(np.median(ncut))}; {100*np.mean(np.array(ncut)==Kp):.0f}% of refits gave {Kp}')
print(f'dose-change branch (von Mises K=6 refit each time):        ARI = {ari7_m:.3f}')
print('\nper-cluster stability and bootstrap P/N interval:')
stab = {}
for c in range(Kp):
    nm = f'PCA-{c+1}'; lo, hi = interval(pn_pca[c])
    j = float(np.nanmean(jac_pca[:, c])) if len(jac_pca) else float('nan')
    stab[nm] = dict(jaccard=j, pn_boot_lo=lo, pn_boot_hi=hi, n_boot=len(pn_pca[c]))
    print(f'   {nm:7} Jaccard={j:.2f}  P/N bootstrap 95% interval {lo:.2f}-{hi:.2f}')
for c in range(6):
    nm = f'7d-{c+1}'; lo, hi = interval(pn_7[c])
    j = float(np.nanmean(jac7[:, c]))
    stab[nm] = dict(jaccard=j, pn_boot_lo=lo, pn_boot_hi=hi, n_boot=len(pn_7[c]))
    print(f'   {nm:7} Jaccard={j:.2f}  P/N bootstrap 95% interval {lo:.2f}-{hi:.2f}')

json.dump(dict(n_boot=NBOOT, ari_pca_kde=ari_pca_m, ari_7d_vm=ari7_m,
               n_valleys_median=int(np.median(ncut)),
               frac_refits_same_k=float(np.mean(np.array(ncut) == Kp)),
               per_cluster=stab),
          open(OUT + r'\final_stability.json', 'w'), indent=2)
print('\nsaved final_stability.json')
