# -*- coding: utf-8 -*-
"""PROVENANCE FIX for Table 1 + honest bootstrap ARI.

Two defects found by the R4 statistical reviewer and independently confirmed:
 (1) final_combined_rows.json (the source of Table 1) was READ by scripts 15/16/25
     but WRITTEN by none -> Table 1 was untraceable. This script regenerates it
     from aim2.mat and diffs it cell-by-cell against the orphan backup.
 (2) the reported stable-dose bootstrap ARI (0.72) was computed on a von Mises K=3
     partition (13_vonmises_final.py:72,102), NOT on the KDE density-valley
     partition the paper actually uses. Here the ARI is recomputed by bootstrapping
     the ACTUAL procedure for each branch.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, os, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

AN = _os.path.join(ROOT, r'analysis')
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un
sa, sb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db')
xa, xb = cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
proj = lambda pd_, ds_, mk: (np.hstack([pd_[mk], ds_[mk]]) - mu0) @ coeff.T

# ---------- stable-dose branch: circular KDE density valleys (the METHOD THE PAPER USES) ----------
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - 0.0270, proj(pos_pd, pos_ds, up)[:, 0] + 0.04) % (2 * np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - 0.0270, proj(neg_pd, neg_ds, un)[:, 0] + 0.04) % (2 * np.pi)
GRID = np.linspace(0, 2 * np.pi, 721)[:-1]
def kde_cuts(th, kappa=12):
    d = np.array([np.exp(kappa * np.cos(g - th)).sum() for g in GRID])
    return np.sort(GRID[[i for i in range(len(d)) if d[i] < d[(i - 1) % len(d)] and d[i] <= d[(i + 1) % len(d)]]])
cuts = kde_cuts(thp)
pca_p = np.searchsorted(cuts, thp) % len(cuts); pca_n = np.searchsorted(cuts, thn) % len(cuts)

# ---------- dose-change branch: von Mises mixture K=6 ----------
def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999)
    return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
def vm_fit(t1, t2, K=6, seed=0, iters=120):
    lab0 = KMeans(K, n_init=5, random_state=seed).fit_predict(
        np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab0, np.arange(len(t1))] = 1
    m1 = np.zeros(K); k1 = np.ones(K); mm2 = np.zeros(K); k2 = np.ones(K); pi = np.ones(K) / K
    for _ in range(iters):
        for k in range(K):
            w = P[k]; m1[k], k1[k] = vm_mle(t1, w); mm2[k], k2[k] = vm_mle(t2, w); pi[k] = w.mean() + 1e-9
        P = np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, mm2[k], k2[k]) for k in range(K)])
        P /= P.sum(0) + 1e-300
    return m1, k1, mm2, k2, pi
def vm_assign(t1, t2, prm):
    m1, k1, mm2, k2, pi = prm
    return np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, mm2[k], k2[k]) for k in range(len(pi))]).argmax(0)

t1p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); t2p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
t1n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); t2n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
prm = vm_fit(t1p, t2p, 6)
lab7p = vm_assign(t1p, t2p, prm); lab7n = vm_assign(t1n, t2n, prm)

clab = np.empty(TP + TN, object)
clab[:TP][up] = [f'PCA-{c+1}' for c in pca_p]; clab[:TP][svp] = [f'7d-{c+1}' for c in lab7p]
clab[TP:][un] = [f'PCA-{c+1}' for c in pca_n]; clab[TP:][svn] = [f'7d-{c+1}' for c in lab7n]
clusters = sorted(set(clab), key=lambda s: (s.split('-')[0], int(s.split('-')[1])))

# ---------- Table 1 regeneration ----------
rows = []
for c in clusters:
    m = (clab == c); posN = int((m & (y == 1)).sum()); negN = int((m & (y == 0)).sum())
    pn = (posN / TP) / (negN / TN)
    r = sm.Logit(y, sm.add_constant(m.astype(float))).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
    b = r.params[1]; se = r.bse[1]
    rows.append(dict(cluster=c, branch=c.split('-')[0], posN=posN, negN=negN, PN=pn,
                     OR=float(np.exp(b)), lo=float(np.exp(b - 1.96 * se)), hi=float(np.exp(b + 1.96 * se)),
                     p=float(r.pvalues[1])))
qs = multipletests([r['p'] for r in rows], method='fdr_bh')[1]
for r, q in zip(rows, qs):
    r['q'] = float(q)
    r['label'] = 'Higher-risk' if (r['PN'] > 1.2 and q < 0.05) else ('Lower-risk' if (r['PN'] < 0.83 and q < 0.05) else 'ns')
rows.sort(key=lambda r: -r['PN'])
json.dump(rows, open(os.path.join(AN, 'final_combined_rows.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'REGENERATED final_combined_rows.json ({len(rows)} clusters) -- Table 1 is now script-traceable.')

# ---------- cell-by-cell diff vs the orphan file ----------
orph = {r['cluster']: r for r in json.load(open(os.path.join(AN, 'final_combined_rows.ORPHAN_BACKUP.json'), encoding='utf-8'))}
print('\n=== DIFF vs orphan (the file Table 1 was actually built from) ===')
bad = 0
for r in rows:
    o = orph.get(r['cluster'])
    if o is None:
        print(f"  {r['cluster']}: MISSING in orphan"); bad += 1; continue
    for k in ('posN', 'negN', 'PN', 'OR', 'q'):
        a, b_ = r[k], o[k]
        same = (a == b_) if isinstance(a, int) else (abs(a - b_) <= 0.005 * max(abs(b_), 1e-9))
        if not same:
            print(f"  MISMATCH {r['cluster']}.{k}: regenerated={a} orphan={b_}"); bad += 1
print(f'  >>> {"ALL CELLS MATCH -- Table 1 reproduces exactly" if bad==0 else str(bad)+" mismatching cell(s)"}')

# ---------- honest bootstrap ARI: bootstrap the ACTUAL procedure of each branch ----------
print('\n=== bootstrap ARI on the PROCEDURE ACTUALLY USED (B=20) ===')
rng = np.random.default_rng(0); B = 20
ar_pca = []
for _ in range(B):
    idx = rng.integers(0, len(thp), len(thp))
    c2 = kde_cuts(thp[idx])                      # refit KDE valleys on the resample
    if len(c2) < 2: continue
    ar_pca.append(adjusted_rand_score(pca_p, np.searchsorted(c2, thp) % len(c2)))
ar_7d = []
for s in range(B):
    idx = rng.integers(0, len(t1p), len(t1p))
    p2 = vm_fit(t1p[idx], t2p[idx], 6, seed=s, iters=60)   # refit vM mixture on the resample
    ar_7d.append(adjusted_rand_score(lab7p, vm_assign(t1p, t2p, p2)))
print(f'  stable-dose branch (KDE density-valley, as used): ARI = {np.mean(ar_pca):.3f}  (n_boot={len(ar_pca)}, k_cuts={len(cuts)})')
print(f'  dose-change branch (von Mises K=6, as used)     : ARI = {np.mean(ar_7d):.3f}  (n_boot={len(ar_7d)})')
print(f'  [paper currently reports 0.72 (stable) / 0.57 (dose-change); the 0.72 came from a vM K=3 fit, not the KDE method]')
json.dump(dict(ari_pca_kde_asused=float(np.mean(ar_pca)), ari_7d_vm6_asused=float(np.mean(ar_7d)),
               n_boot=B, kde_cuts_deg=[round(float(x), 1) for x in np.rad2deg(cuts)],
               table1_cells_mismatching=bad),
          open(os.path.join(AN, 'provenance_check.json'), 'w'), indent=2)
print('\nwrote provenance_check.json')
