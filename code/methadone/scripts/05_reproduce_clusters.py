# -*- coding: utf-8 -*-
"""
Step 05 - Reproduce the ORIGINAL 17-cluster P/N table from aim2.mat features,
to verify we captured the final method (must match the PPTX numbers).

Faithful port of:
  clustering_28_7_ab_cat19_ver2.m  +  Postive_locs_7_28_ab_method.m
Data: including_False_N_splitdata_testingvalidating/aim2.mat
  All_fill_norm_positive_training{1,2} = pos training dose/presc (2721 x 57)
  All_fill_norm_positive_training{3,4} = neg training dose/presc (5819 x 57)
  slope_burst_{min,max}_7d{a,b}_training{1}=pos(2721), {3}=neg(5819)
Boundaries are the ORIGINAL eyeballed ones (to reproduce). Step 06 replaces them
with a data-driven / statistical clustering.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np

MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
f = h5py.File(MAT, 'r')

def cells(name):
    return [np.array(f[r]) for r in np.array(f[name]).ravel()]

def m2(a):                      # matlab matrix -> (N,57)
    return a.T if a.shape[0] == 57 else a

def v(a):                       # matlab vector -> 1D
    return np.array(a).ravel()

afn_t = cells('All_fill_norm_positive_training')
pos_pd = m2(afn_t[0]); pos_ds = m2(afn_t[1])      # dose, prescription (pos 2721)
neg_pd = m2(afn_t[2]); neg_ds = m2(afn_t[3])      # dose, prescription (neg 5819)
Lp, Ln = pos_pd.shape[0], neg_pd.shape[0]
print(f'pos training={Lp}  neg training={Ln}')

smin_a = cells('slope_burst_min_7da_training'); smin_b = cells('slope_burst_min_7db_training')
smax_a = cells('slope_burst_max_7da_training'); smax_b = cells('slope_burst_max_7db_training')
pos = dict(min_a=v(smin_a[0]), min_b=v(smin_b[0]), max_a=v(smax_a[0]), max_b=v(smax_b[0]))
neg = dict(min_a=v(smin_a[2]), min_b=v(smin_b[2]), max_a=v(smax_a[2]), max_b=v(smax_b[2]))
print('pos slope len:', len(pos['min_a']), ' neg slope len:', len(neg['min_a']))

def deg(theta):
    d = np.rad2deg(theta); d[d < 0] += 360; return d

def branch_mask(pd_mat):
    w = pd_mat[:, 21:36]                          # cols 22:36 (matlab) = +/-7d
    changed = np.abs(np.diff(w, axis=1)).sum(axis=1) != 0
    return ~changed, changed                      # unchanged(PCA), changed(7d)

# ---- fit PCA on positive PCA-branch, get coeff+mu (for projecting negatives) ----
pca_unch_pos, seven_pos = branch_mask(pos_pd)
Xp = np.hstack([pos_pd[pca_unch_pos], pos_ds[pca_unch_pos]])    # (n,114)
mu = Xp.mean(0)
U, S, Vt = np.linalg.svd(Xp - mu, full_matrices=False)
coeff = Vt.T                                                    # (114,114) principal dirs
score_p = (Xp - mu) @ coeff

def pca_angle(score):
    th, _ = np.arctan2(score[:,1]-0.0270, score[:,0]+0.04), None
    return deg(th)

def assign_pca(score):
    d = pca_angle(score)
    return [np.where((d>15)&(d<=80))[0], np.where((d>80)&(d<=175))[0],
            np.where((d>175)&(d<=260))[0], np.where((d>260)&(d<=300))[0],
            np.where((d>300)|(d<=15))[0]]

def assign_7d(s):
    tmin = deg(np.arctan2(s['min_b'], s['min_a']))     # cart2pol(x=after,y=before)->atan2(before,after)
    tmax = deg(np.arctan2(s['max_b'], s['max_a']))
    xb = [(170,200),(200,250),(250,290)]               # theta_min bins
    yb = [(10,65),(65,120),(180,270),(270,10)]         # theta_max bins (last wraps)
    out = []
    for (xl,xh) in xb:
        for (yl,yh) in yb:
            if yl > yh:      # wrap bin (270,10]
                m = (tmin>xl)&(tmin<=xh)&((tmax>yl)|(tmax<=yh))
            else:
                m = (tmin>xl)&(tmin<=xh)&(tmax>yl)&(tmax<=yh)
            out.append(np.where(m)[0])
    return out            # 12 groups, order: xmin outer, xmax inner

# positive counts
pos_pca = assign_pca(score_p)
# 7d branch uses only the 'changed' rows; slopes arrays are full-length(2721) but
# original code indexes a=changed indices into the full slope vectors
seven_idx_p = np.where(seven_pos)[0]
pos7 = {k: pos[k][seven_idx_p] for k in pos}
pos_7d = assign_7d(pos7)

# negative: project onto positive PCA
pca_unch_neg, seven_neg = branch_mask(neg_pd)
Xn = np.hstack([neg_pd[pca_unch_neg], neg_ds[pca_unch_neg]])
score_n = (Xn - mu) @ coeff
neg_pca = assign_pca(score_n)
seven_idx_n = np.where(seven_neg)[0]
neg7 = {k: neg[k][seven_idx_n] for k in neg}
neg_7d = assign_7d(neg7)

names = ['pca1','pca2','pca3','pca4','pca5'] + [f'7d{i}' for i in range(1,13)]
pos_sizes = [len(x) for x in pos_pca] + [len(x) for x in pos_7d]
neg_sizes = [len(x) for x in neg_pca] + [len(x) for x in neg_7d]

pptx_PN = [1.3327,1.7932,1.7018,1.5524,1.1347,1.0585,0.5783,0.4447,0.5893,
           1.3449,1.3589,1.2916,0.8033,0.5405,0.7854,1.1938,1.5353]

print(f'\n{"clust":6s} {"posN":>6s} {"posRate":>8s} {"negN":>6s} {"negRate":>8s} {"P/N":>7s}')
mine = []
for i in range(17):
    pr = pos_sizes[i]/Lp; nr = neg_sizes[i]/Ln
    pn = pr/nr if nr>0 else float('nan')
    mine.append(pn)
    print(f'{names[i]:6s} {pos_sizes[i]:6d} {pr:8.4f} {neg_sizes[i]:6d} {nr:8.4f} {pn:7.3f}')

print(f'\nsum pos in clusters: {sum(pos_sizes)} / {Lp}   neg: {sum(neg_sizes)} / {Ln}')
print('\ncompare P/N sets (sorted) mine vs PPTX:')
print('  mine:', sorted(round(x,2) for x in mine))
print('  pptx:', sorted(pptx_PN))
