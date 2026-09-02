# -*- coding: utf-8 -*-
"""
Step 06 - SCIENTIFIC clustering to replace the eyeballed angle cuts.

Instead of hand-drawn degree thresholds (170/200/250/290 ...), we fit a
Gaussian Mixture Model and let BIC choose the number of components -- a
reproducible, model-selection-based clustering.

Two branches (same split as the original: dose unchanged->PCA, changed->7d):
  - PCA branch : GMM with BIC on the first-2 PCA scores (2D Euclidean).
  - 7d  branch : GMM with BIC on the CIRCULAR embedding
                 [cos t_min, sin t_min, cos t_max, sin t_max]  (respects angle
                 periodicity; a von Mises mixture is the ideal refinement).

Model is FIT ON POSITIVES ONLY (the study design clusters positives), then both
positives and negatives are ASSIGNED to the fitted components, giving a clean
P/N ratio per data-driven cluster. Negatives are projected onto the positive
PCA space, exactly like the original.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np
from sklearn.mixture import GaussianMixture

MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a)
v  = lambda a: np.array(a).ravel()
RNG = 0

afn = cells('All_fill_norm_positive_training')
pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
Lp, Ln = pos_pd.shape[0], neg_pd.shape[0]
sa = cells('slope_burst_min_7da_training'); sb = cells('slope_burst_min_7db_training')
xa = cells('slope_burst_max_7da_training'); xb = cells('slope_burst_max_7db_training')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))

def split(pd_mat):
    w = pd_mat[:, 21:36]
    changed = np.abs(np.diff(w, axis=1)).sum(axis=1) != 0
    return ~changed, changed

def pick_gmm(X, kmax=12, label=''):
    best, bestk, bestbic = None, None, np.inf
    for k in range(2, kmax + 1):
        g = GaussianMixture(k, covariance_type='full', n_init=5, random_state=RNG).fit(X)
        b = g.bic(X)
        if b < bestbic:
            best, bestk, bestbic = g, k, b
    print(f'  [{label}] BIC selected K={bestk}')
    return best, bestk

# ---------- PCA branch ----------
pu_p, sv_p = split(pos_pd)
Xp = np.hstack([pos_pd[pu_p], pos_ds[pu_p]])
mu = Xp.mean(0)
coeff = np.linalg.svd(Xp - mu, full_matrices=False)[2].T
score_p = (Xp - mu) @ coeff
pu_n, sv_n = split(neg_pd)
Xn = np.hstack([neg_pd[pu_n], neg_ds[pu_n]])
score_n = (Xn - mu) @ coeff

gm_pca, k_pca = pick_gmm(score_p[:, :2], 10, 'PCA')
lab_pca_p = gm_pca.predict(score_p[:, :2])
lab_pca_n = gm_pca.predict(score_n[:, :2])

# ---------- 7d branch ----------
def embed(d, idx):
    tmn = np.arctan2(d['mn_b'][idx], d['mn_a'][idx])
    tmx = np.arctan2(d['mx_b'][idx], d['mx_a'][idx])
    return np.column_stack([np.cos(tmn), np.sin(tmn), np.cos(tmx), np.sin(tmx)])

Ep = embed(pos, np.where(sv_p)[0])
En = embed(neg, np.where(sv_n)[0])
gm_7d, k_7d = pick_gmm(Ep, 14, '7d')
lab_7d_p = gm_7d.predict(Ep)
lab_7d_n = gm_7d.predict(En)

# ---------- P/N per data-driven cluster ----------
from scipy.stats import chi2_contingency
print(f'\nData-driven clusters: PCA K={k_pca} + 7d K={k_7d} = {k_pca + k_7d} total')
print(f'{"cluster":10s} {"posN":>6s} {"posRate":>8s} {"negN":>6s} {"negRate":>8s} {"P/N":>7s} {"chi2 p":>10s}')
rows = []
def report(prefix, lp, ln, K):
    for c in range(K):
        pn_pos = int((lp == c).sum()); pn_neg = int((ln == c).sum())
        pr, nr = pn_pos / Lp, pn_neg / Ln
        pn = pr / nr if nr > 0 else np.nan
        # 2x2 chi-square: in-cluster vs not, positive vs negative
        table = [[pn_pos, Lp - pn_pos], [pn_neg, Ln - pn_neg]]
        try:
            p = chi2_contingency(table)[1]
        except ValueError:
            p = np.nan
        flag = 'HIGH-RISK' if pn > 1.2 else ('SAFE' if pn < 0.83 else '')
        print(f'{prefix+str(c+1):10s} {pn_pos:6d} {pr:8.4f} {pn_neg:6d} {nr:8.4f} {pn:7.3f} {p:10.2e}  {flag}')
        rows.append((prefix+str(c+1), pn_pos, pn_neg, pr, nr, pn, p))
report('PCA-', lab_pca_p, lab_pca_n, k_pca)
report('7d-',  lab_7d_p,  lab_7d_n,  k_7d)

import pandas as pd
pd.DataFrame(rows, columns=['cluster','posN','negN','posRate','negRate','PN','chi2_p']).to_csv(
    _os.path.join(ROOT, r'analysis\scientific_clusters_PN.csv'), index=False)
print('\nsaved scientific_clusters_PN.csv')
