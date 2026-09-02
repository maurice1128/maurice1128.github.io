# -*- coding: utf-8 -*-
"""Table S6: the ALTERNATIVE partition of the stable-dose branch.

The manuscript downgrades the whole stable-dose branch to exploratory partly
because a 1-D von Mises mixture (K=3) on the same tests gives a different split
under which no cluster is higher-risk. That table was cited but never computed.
This produces it."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings, json; warnings.filterwarnings('ignore')
from scipy.special import i0
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_c, pos_p, neg_c, neg_p = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
up = ~(np.abs(np.diff(pos_c[:, 21:36], axis=1)).sum(1) != 0)
un = ~(np.abs(np.diff(neg_c[:, 21:36], axis=1)).sum(1) != 0)
proj = lambda a, b, mk: (np.hstack([a[mk], b[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_c, pos_p, up)[:, 1] - .0270, proj(pos_c, pos_p, up)[:, 0] + .04) % (2*np.pi)
thn = np.arctan2(proj(neg_c, neg_p, un)[:, 1] - .0270, proj(neg_c, neg_p, un)[:, 0] + .04) % (2*np.pi)
print('stable-dose branch: %d positive, %d negative tests' % (up.sum(), un.sum()))

# --- reported partition: circular KDE density valleys ---
G = np.linspace(0, 2*np.pi, 721)[:-1]
d = np.array([np.exp(12*np.cos(g - thp)).sum() for g in G])
cuts = np.sort(G[[i for i in range(len(d)) if d[i] < d[(i-1) % len(d)] and d[i] <= d[(i+1) % len(d)]]])
kde_p = np.searchsorted(cuts, thp) % len(cuts); kde_n = np.searchsorted(cuts, thn) % len(cuts)

# --- alternative partition: 1-D von Mises mixture, K = 3 ---
def vmpdf(t, m, k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm1(t, K=3, iters=200, seed=0):
    rng = np.random.default_rng(seed)
    m = np.sort(rng.uniform(0, 2*np.pi, K)); k = np.ones(K)*4.0; pi = np.ones(K)/K
    for _ in range(iters):
        P = np.array([pi[j]*vmpdf(t, m[j], k[j]) for j in range(K)]); P /= P.sum(0)+1e-300
        for j in range(K):
            w = P[j]; C = (w*np.cos(t)).sum(); S = (w*np.sin(t)).sum(); s = w.sum()+1e-12
            R = min(np.sqrt(C*C+S*S)/s, .999)
            m[j] = np.arctan2(S, C); k[j] = R*(2-R*R)/(1-R*R); pi[j] = w.mean()+1e-9
    return m, k, pi
prm = vm1(thp)
asg = lambda t: np.array([prm[2][j]*vmpdf(t, prm[0][j], prm[1][j]) for j in range(3)]).argmax(0)
vm_p, vm_n = asg(thp), asg(thn)

def table(lp, ln, name):
    print('\n=== %s ===' % name)
    rows = []
    for c in range(len(set(lp)) if name.startswith('alt') else len(cuts)):
        a = int((lp == c).sum()); b = int((ln == c).sum())
        if a < 5 or b < 5: rows.append((c, a, b, np.nan, np.nan)); continue
        pn = (a/TP)/(b/TN)
        inc = np.zeros(TP+TN); inc[:TP][up] = (lp == c); inc[TP:][un] = (ln == c)
        r = sm.Logit(y, sm.add_constant(inc)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
        rows.append((c, a, b, pn, float(r.pvalues[1])))
    qs = multipletests([r[4] if np.isfinite(r[4]) else 1 for r in rows], method='fdr_bh')[1]
    out = []
    for (c, a, b, pn, p), q in zip(rows, qs):
        tag = 'higher-risk' if pn > 1.2 and q < .05 else ('lower-risk' if pn < 0.83 and q < .05 else 'ns')
        print('  cluster %d: pos=%4d neg=%4d  P/N=%.2f  q=%.3f  %s' % (c+1, a, b, pn, q, tag))
        out.append(dict(cluster=c+1, pos=a, neg=b, PN=round(pn, 3), q=round(float(q), 4), label=tag))
    return out
kde = table(kde_p, kde_n, 'reported partition (circular KDE density valleys)')
alt = table(vm_p, vm_n, 'alternative partition (1-D von Mises mixture, K=3)')
print('\n>>> higher-risk clusters — reported: %d | alternative: %d'
      % (sum(r['label'] == 'higher-risk' for r in kde), sum(r['label'] == 'higher-risk' for r in alt)))
json.dump(dict(reported=kde, alternative=alt),
          open(_os.path.join(ROOT, r'analysis\table_S6_alt_partition.json'), 'w'), indent=2)
print('wrote table_S6_alt_partition.json')
