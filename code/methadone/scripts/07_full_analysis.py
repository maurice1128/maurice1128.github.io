# -*- coding: utf-8 -*-
"""
Step 07 - Full analysis on the COMPLETE data (3401 positive + 6499 negative
morphine urine tests), with patient IDs, for the paper.

  A. Scientific clustering (GMM + BIC, guarded against degenerate clusters)
     on the positive tests; negatives projected/assigned the same way.
  B. Bootstrap stability of the clustering (adjusted Rand index).
  C. Patient-level association: per-cluster logistic regression of test
     positivity on cluster membership with CLUSTER-ROBUST (by patient) SE,
     + Benjamini-Hochberg FDR. Attendance rate added as covariate.
  D. Prediction: dose trajectory features -> positive, GroupKFold(5) by
     patient, AUC for logistic / gradient boosting; attendance-only and
     combined models for comparison.

All numbers are printed AND saved to results_summary.json + *_table.csv so the
paper quotes only executed output (anti-hallucination protocol).
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

RNG = 0
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a)
v  = lambda a: np.array(a).ravel()

afn = cells('All_fill_norm')                 # {0}pos dose {1}pos presc {2}neg dose {3}neg presc
pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header')
pid_pos, pid_neg = v(hdr[0]).astype(int), v(hdr[2]).astype(int)
att_pos, att_neg = v(cells('freq_All')[0]), v(cells('freq_All')[2])
sa = cells('slope_burst_min_7da'); sb = cells('slope_burst_min_7db')
xa = cells('slope_burst_max_7da'); xb = cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
Lp, Ln = pos_pd.shape[0], neg_pd.shape[0]
print(f'FULL data: positive={Lp} (patients {len(set(pid_pos))}), negative={Ln} (patients {len(set(pid_neg))})')

def split(pd_mat):
    w = pd_mat[:, 21:36]
    changed = np.abs(np.diff(w, axis=1)).sum(axis=1) != 0
    return ~changed, changed

def guarded_gmm(X, kmax, min_frac=0.01, label=''):
    """lowest-BIC K whose smallest component still has >= min_frac*N members."""
    n = len(X); best = None
    order = []
    for k in range(2, kmax + 1):
        g = GaussianMixture(k, covariance_type='full', n_init=6, random_state=RNG).fit(X)
        lab = g.predict(X)
        sizes = np.bincount(lab, minlength=k)
        order.append((g.bic(X), k, g, sizes.min()))
    order.sort()
    for bic, k, g, mn in order:
        if mn >= max(20, min_frac * n):
            print(f'  [{label}] BIC K={k} (min cluster {mn})')
            return g, k
    bic, k, g, mn = order[0]
    print(f'  [{label}] fallback BIC K={k} (min cluster {mn})')
    return g, k

# ---- A. clustering ----
pu_p, sv_p = split(pos_pd); pu_n, sv_n = split(neg_pd)
Xp = np.hstack([pos_pd[pu_p], pos_ds[pu_p]]); mu = Xp.mean(0)
coeff = np.linalg.svd(Xp - mu, full_matrices=False)[2].T
sc_p = (Xp - mu) @ coeff
Xn = np.hstack([neg_pd[pu_n], neg_ds[pu_n]]); sc_n = (Xn - mu) @ coeff
gm_pca, k_pca = guarded_gmm(sc_p[:, :2], 10, label='PCA')

def embed(d, idx):
    tmn = np.arctan2(d['mn_b'][idx], d['mn_a'][idx]); tmx = np.arctan2(d['mx_b'][idx], d['mx_a'][idx])
    return np.column_stack([np.cos(tmn), np.sin(tmn), np.cos(tmx), np.sin(tmx)])
Ep = embed(pos, np.where(sv_p)[0]); En = embed(neg, np.where(sv_n)[0])
gm_7d, k_7d = guarded_gmm(Ep, 14, label='7d')

# assemble cluster labels over ALL tests (string labels)
def labels(gm, Xpca_or_emb_p, Xpca_or_emb_n, pref):
    return [f'{pref}{c+1}' for c in gm.predict(Xpca_or_emb_p)], \
           [f'{pref}{c+1}' for c in gm.predict(Xpca_or_emb_n)]
lp_pca, ln_pca = labels(gm_pca, sc_p[:, :2], sc_n[:, :2], 'PCA-')
lp_7d,  ln_7d  = labels(gm_7d, Ep, En, '7d-')

clab_pos = np.empty(Lp, dtype=object); clab_pos[pu_p] = lp_pca; clab_pos[sv_p] = lp_7d
clab_neg = np.empty(Ln, dtype=object); clab_neg[pu_n] = ln_pca; clab_neg[sv_n] = ln_7d

# ---- B. bootstrap stability (positives) ----
base = gm_7d.predict(Ep); aris = []
rs = np.random.RandomState(RNG)
for _ in range(25):
    idx = rs.choice(len(Ep), len(Ep), replace=True)
    g = GaussianMixture(k_7d, covariance_type='full', n_init=2, random_state=RNG).fit(Ep[idx])
    aris.append(adjusted_rand_score(base, g.predict(Ep)))
stab = float(np.mean(aris))
print(f'\n7d clustering bootstrap stability (ARI): {stab:.3f}')

# ---- pooled table for stats ----
outcome = np.r_[np.ones(Lp), np.zeros(Ln)]
clab    = np.r_[clab_pos, clab_neg]
pid     = np.r_[pid_pos, pid_neg]
att     = np.r_[att_pos, att_neg]
clusters = sorted(set(clab), key=lambda s: (s.split('-')[0], int(s.split('-')[1])))

# ---- C. patient-level association per cluster (cluster-robust logistic) ----
print('\n=== Per-cluster patient-level association (cluster-robust by patient) ===')
rows = []
for c in clusters:
    inc = (clab == c).astype(float)
    X = sm.add_constant(inc)
    try:
        res = sm.Logit(outcome, X).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
        OR = float(np.exp(res.params[1])); p = float(res.pvalues[1])
    except Exception:
        OR, p = float('nan'), float('nan')
    pr = float((outcome[clab == c] == 1).mean()) if (clab == c).any() else float('nan')
    posN = int(((clab == c) & (outcome == 1)).sum()); negN = int(((clab == c) & (outcome == 0)).sum())
    pn = (posN / Lp) / (negN / Ln) if negN > 0 else float('nan')
    rows.append(dict(cluster=c, posN=posN, negN=negN, PN=pn, OR=OR, p=p))
pvals = [r['p'] for r in rows]
fdr = multipletests(np.nan_to_num(pvals, nan=1.0), method='fdr_bh')[1]
for r, q in zip(rows, fdr):
    r['p_fdr'] = float(q)
    tag = 'HIGH-RISK' if r['PN'] > 1.2 and q < 0.05 else ('SAFE' if r['PN'] < 0.83 and q < 0.05 else '')
    print(f"  {r['cluster']:8s} P/N={r['PN']:.3f}  OR={r['OR']:.2f}  p={r['p']:.1e}  q={q:.1e}  {tag}")

# attendance effect (combined model, cluster-robust)
Xa = sm.add_constant(att)
resa = sm.Logit(outcome, Xa).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
att_OR = float(np.exp(resa.params[1])); att_p = float(resa.pvalues[1])
print(f'\nAttendance rate -> positivity: OR(per +1.0)={att_OR:.3f}, p={att_p:.1e}  '
      f'(mean att: pos={att_pos.mean():.3f} neg={att_neg.mean():.3f})')

# ---- D. prediction: dose trajectory -> positive, GroupKFold by patient ----
def feat(pd_mat, ds_mat, d, att_):
    w = np.hstack([pd_mat[:, 21:36], ds_mat[:, 21:36]])          # dose+presc +/-7d
    sl = np.column_stack([d['mn_a'], d['mn_b'], d['mx_a'], d['mx_b']])
    return np.hstack([w, sl, att_[:, None]])
Xall = np.vstack([feat(pos_pd, pos_ds, pos, att_pos), feat(neg_pd, neg_ds, neg, att_neg)])
Xall = np.nan_to_num(Xall)
gkf = GroupKFold(5)
def cv_auc(model_fn, X):
    aucs = []
    for tr, te in gkf.split(X, outcome, pid):
        sc = StandardScaler().fit(X[tr]); m = model_fn().fit(sc.transform(X[tr]), outcome[tr])
        pr = m.predict_proba(sc.transform(X[te]))[:, 1]
        aucs.append(roc_auc_score(outcome[te], pr))
    return float(np.mean(aucs)), float(np.std(aucs))
lr = lambda: LogisticRegression(max_iter=1000, class_weight='balanced')
gb = lambda: HistGradientBoostingClassifier(random_state=RNG)
auc_lr = cv_auc(lr, Xall); auc_gb = cv_auc(gb, Xall)
auc_att = cv_auc(lr, np.nan_to_num(np.r_[att_pos, att_neg])[:, None])
print(f'\n=== Prediction (GroupKFold-5 by patient, AUC mean+/-sd) ===')
print(f'  dose-trajectory + attendance, logistic : {auc_lr[0]:.3f} +/- {auc_lr[1]:.3f}')
print(f'  dose-trajectory + attendance, grad-boost: {auc_gb[0]:.3f} +/- {auc_gb[1]:.3f}')
print(f'  attendance only, logistic               : {auc_att[0]:.3f} +/- {auc_att[1]:.3f}')

# ---- save ----
summary = dict(
    n_pos=Lp, n_neg=Ln, n_pat_pos=len(set(pid_pos)), n_pat_neg=len(set(pid_neg)),
    k_pca=int(k_pca), k_7d=int(k_7d), n_clusters=len(clusters),
    stability_ari=stab, attendance_OR=att_OR, attendance_p=att_p,
    att_mean_pos=float(att_pos.mean()), att_mean_neg=float(att_neg.mean()),
    auc_traj_lr=auc_lr, auc_traj_gb=auc_gb, auc_att=auc_att, clusters=rows)
json.dump(summary, open(OUT + r'\results_summary.json', 'w'), indent=2)
import pandas as pd
pd.DataFrame(rows).to_csv(OUT + r'\cluster_association_table.csv', index=False)
print('\nsaved results_summary.json + cluster_association_table.csv')
