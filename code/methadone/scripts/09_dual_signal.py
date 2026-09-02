# -*- coding: utf-8 -*-
"""
Step 09 - DUAL-SIGNAL enhancement: use BOTH prescription dose (pd) and taken
dose (ds), plus their divergence, in the 7-day slope clustering and prediction.

First VALIDATES the slope computation by reproducing aim2.mat's precomputed
slope_burst_{min,max}_7d{a,b}{1} from All_fill_norm{1} (prescription). Then
applies the same computation to All_fill_norm{2} (taken dose) and adds a
prescription-minus-taken divergence feature.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings
warnings.filterwarnings('ignore')
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import pandas as pd

RNG = 0
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm')
pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
Lp, Ln = pos_pd.shape[0], neg_pd.shape[0]

# ---- slope features from a 57-col normalized series (day -28..+28, idx28=day0) ----
def moving_slopes(row, lo, hi):                # 3-day windows over idx [lo,hi]
    sl = []
    for s in range(lo, hi - 1):
        y = row[s:s + 3]
        if np.all(np.isfinite(y)):
            sl.append(np.polyfit([0, 1, 2], y, 1)[0])
    return (min(sl), max(sl)) if sl else (np.nan, np.nan)

def slope_feats(mat):
    # pre = days -7..0 -> idx 21..28 ; post = days 0..+7 -> idx 28..35
    out = np.zeros((len(mat), 4))              # [min_b, max_b, min_a, max_a]
    for i, row in enumerate(mat):
        mnb, mxb = moving_slopes(row, 21, 29)  # before (pre)
        mna, mxa = moving_slopes(row, 28, 36)  # after (post)
        out[i] = [mnb, mxb, mna, mxa]
    return out

pd_pos, pd_neg = slope_feats(pos_pd), slope_feats(neg_pd)
ds_pos, ds_neg = slope_feats(pos_ds), slope_feats(neg_ds)

# ---- VALIDATE against precomputed slope_burst (prescription) ----
sb = dict(min_a=v(cells('slope_burst_min_7da')[0]), min_b=v(cells('slope_burst_min_7db')[0]),
          max_a=v(cells('slope_burst_max_7da')[0]), max_b=v(cells('slope_burst_max_7db')[0]))
def corr(a, b):
    m = np.isfinite(a) & np.isfinite(b); return float(np.corrcoef(a[m], b[m])[0, 1])
print('=== slope validation (my pd slopes vs aim2 precomputed) ===')
print('  min_after :', round(corr(pd_pos[:, 2], sb['min_a']), 3),
      ' min_before:', round(corr(pd_pos[:, 0], sb['min_b']), 3),
      ' max_after :', round(corr(pd_pos[:, 3], sb['max_a']), 3),
      ' max_before:', round(corr(pd_pos[:, 1], sb['max_b']), 3))

# ---- branch split (on prescription, same as original) ----
def split(pdm):
    ch = np.abs(np.diff(pdm[:, 21:36], axis=1)).sum(1) != 0; return ~ch, ch
pu_p, sv_p = split(pos_pd); pu_n, sv_n = split(neg_pd)

# ---- divergence feature: mean |pd - ds| over +/-7d ----
def diverg(pdm, dsm): return np.nanmean(np.abs(pdm[:, 21:36] - dsm[:, 21:36]), axis=1)
dv_pos, dv_neg = diverg(pos_pd, pos_ds), diverg(neg_pd, neg_ds)

# ---- 7d clustering on BOTH signals' angles (8D circular embedding) ----
def ang_embed(sf):                             # sf columns [min_b,max_b,min_a,max_a]
    tmn = np.arctan2(sf[:, 0], sf[:, 2]); tmx = np.arctan2(sf[:, 1], sf[:, 3])
    return np.column_stack([np.cos(tmn), np.sin(tmn), np.cos(tmx), np.sin(tmx)])
E_pos = np.hstack([ang_embed(pd_pos[sv_p]), ang_embed(ds_pos[sv_p])])   # 8D
E_neg = np.hstack([ang_embed(pd_neg[sv_n]), ang_embed(ds_neg[sv_n])])
E_pos = np.nan_to_num(E_pos); E_neg = np.nan_to_num(E_neg)

def guarded(X, kmax, lab):
    order = []
    for k in range(2, kmax + 1):
        g = GaussianMixture(k, covariance_type='full', n_init=6, random_state=RNG).fit(X)
        order.append((g.bic(X), k, g, np.bincount(g.predict(X), minlength=k).min()))
    order.sort()
    for bic, k, g, mn in order:
        if mn >= max(20, 0.01 * len(X)): print(f'  [{lab}] K={k}'); return g, k
    return order[0][2], order[0][1]

# PCA branch (unchanged - already both signals)
Xp = np.hstack([pos_pd[pu_p], pos_ds[pu_p]]); mu = Xp.mean(0)
coeff = np.linalg.svd(Xp - mu, full_matrices=False)[2].T
sc_p = (Xp - mu) @ coeff; sc_n = (np.hstack([neg_pd[pu_n], neg_ds[pu_n]]) - mu) @ coeff
gm_pca, k_pca = guarded(sc_p[:, :2], 10, 'PCA')
gm_7d, k_7d = guarded(E_pos, 16, '7d-dual')

# stability
base = gm_7d.predict(E_pos); rs = np.random.RandomState(RNG); aris = []
for _ in range(25):
    idx = rs.choice(len(E_pos), len(E_pos), replace=True)
    aris.append(adjusted_rand_score(base, GaussianMixture(k_7d, covariance_type='full', n_init=2, random_state=RNG).fit(E_pos[idx]).predict(E_pos)))
stab = float(np.mean(aris))

clab_p = np.empty(Lp, object); clab_p[pu_p] = [f'PCA-{c+1}' for c in gm_pca.predict(sc_p[:, :2])]; clab_p[sv_p] = [f'7d-{c+1}' for c in base]
clab_n = np.empty(Ln, object); clab_n[pu_n] = [f'PCA-{c+1}' for c in gm_pca.predict(sc_n[:, :2])]; clab_n[sv_n] = [f'7d-{c+1}' for c in gm_7d.predict(E_neg)]
outcome = np.r_[np.ones(Lp), np.zeros(Ln)]; clab = np.r_[clab_p, clab_n]
clusters = sorted(set(clab), key=lambda s: (s.split('-')[0], int(s.split('-')[1])))

# association
rows = []
for c in clusters:
    inc = (clab == c).astype(float)
    res = sm.Logit(outcome, sm.add_constant(inc)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
    posN = int(((clab == c) & (outcome == 1)).sum()); negN = int(((clab == c) & (outcome == 0)).sum())
    pn = (posN / Lp) / (negN / Ln) if negN > 0 else np.nan
    rows.append(dict(cluster=c, posN=posN, negN=negN, PN=pn, OR=float(np.exp(res.params[1])), p=float(res.pvalues[1])))
q = multipletests([r['p'] for r in rows], method='fdr_bh')[1]
nsig = 0
print(f'\n=== dual-signal clusters: PCA {k_pca} + 7d {k_7d} = {len(clusters)}, ARI={stab:.3f} ===')
for r, qq in zip(rows, q):
    r['q'] = float(qq)
    tag = 'HIGH' if (r['PN'] > 1.2 and qq < 0.05) else ('LOW' if (r['PN'] < 0.83 and qq < 0.05) else '')
    if qq < 0.05: nsig += 1
    if tag: print(f"  {r['cluster']:8s} P/N={r['PN']:.2f} OR={r['OR']:.2f} q={qq:.1e} {tag}")
print(f'total significant (q<0.05): {nsig}')

# prediction with dual signal + divergence
def feats(pdm, dsm, sf_pd, sf_ds, dv, a):
    return np.hstack([pdm[:, 21:36], dsm[:, 21:36], sf_pd, sf_ds, dv[:, None], a[:, None]])
X = np.nan_to_num(np.vstack([feats(pos_pd, pos_ds, pd_pos, ds_pos, dv_pos, att[:Lp]),
                             feats(neg_pd, neg_ds, pd_neg, ds_neg, dv_neg, att[Lp:])]))
aucs = []
for tr, te in GroupKFold(5).split(X, outcome, pid):
    sc = StandardScaler().fit(X[tr]); m = LogisticRegression(max_iter=1000, class_weight='balanced').fit(sc.transform(X[tr]), outcome[tr])
    aucs.append(roc_auc_score(outcome[te], m.predict_proba(sc.transform(X[te]))[:, 1]))
print(f'\nDUAL-signal prediction AUC (GroupKFold): {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}   (single-signal was 0.642)')

pd.DataFrame(rows).to_csv(OUT + r'\dual_signal_cluster_table.csv', index=False)
json.dump(dict(k_pca=int(k_pca), k_7d=int(k_7d), stability=stab, n_sig=int(nsig),
               auc_dual=float(np.mean(aucs)), auc_dual_sd=float(np.std(aucs)),
               diverg_pos=float(np.nanmean(dv_pos)), diverg_neg=float(np.nanmean(dv_neg))),
          open(OUT + r'\dual_signal_summary.json', 'w'), indent=2)
print('saved dual_signal_cluster_table.csv + summary')
