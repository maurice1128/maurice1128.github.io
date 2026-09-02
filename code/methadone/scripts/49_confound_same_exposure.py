# -*- coding: utf-8 -*-
"""CORRECTION of 47_prescribed_adjustment.py.

47_ adjusted an 8-day OLS slope of the consumed series. The manuscript's claimed
exposure is `slope_burst_max_7db` -- the maximum 3-day moving-window slope over
the pre-test days. Those are different variables, which is why 47_ reported 1.204
where the manuscript reports 1.26. Here the confounding analysis uses the CLAIMED
exposure, and computes the prescribed-dose comparator with the SAME algorithm."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from statsmodels.discrete.conditional_models import ConditionalLogit
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm'); pos_c, pos_p, neg_c, neg_p = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
R = np.vstack([m2(cells('All_raw_fix')[0]), m2(cells('All_raw_fix')[2])])
free7 = ~(R[:, 21:36] == -1).any(1)

# the manuscript's claimed exposure, straight from the file
xb = cells('slope_burst_max_7db')
CONS = np.r_[v(xb[0]), v(xb[2])]

def maxslope_pre(M):
    """Same algorithm as slope_burst_max_7d*: max 3-day moving-window slope over
    the pre-test days (cols 21..28 = day -7..0)."""
    W = M[:, 21:29]
    return np.max(np.array([(W[:, i+2] - W[:, i]) / 2.0 for i in range(W.shape[1]-2)]), axis=0)

PRES = np.r_[maxslope_pre(pos_p), maxslope_pre(neg_p)]
# sanity: our re-implementation on the CONSUMED series should track the stored variable
own = np.r_[maxslope_pre(pos_c), maxslope_pre(neg_c)]
print('sanity: our re-implementation vs stored slope_burst_max_7db, r = %.3f'
      % np.corrcoef(own, CONS)[0, 1])
print('correlation(consumed exposure, prescribed analogue) = %.3f' % np.corrcoef(CONS, PRES)[0, 1])

def within(mask, X, names):
    d = pd.DataFrame(dict(y=y[mask], g=pid[mask]))
    ok = d.groupby('g').y.nunique() == 2; k = d.g.map(ok).values
    Z = np.column_stack([(x[mask][k]-x[mask][k].mean())/x[mask][k].std() for x in X])
    r = ConditionalLogit(y[mask][k], Z, groups=pid[mask][k]).fit(disp=0)
    for i, nm in enumerate(names):
        b, se = r.params[i], r.bse[i]
        print('    %-38s OR/SD=%.3f  95%%CI %.2f-%.2f  p=%.2e'
              % (nm, np.exp(b), np.exp(b-1.96*se), np.exp(b+1.96*se), r.pvalues[i]))

for lab, mask in [('ALL tests', np.ones(len(y), bool)), ('imputation-free +-7 window', free7)]:
    print('\n=== %s ===' % lab)
    within(mask, [CONS], ['consumed (claimed exposure) alone'])
    within(mask, [CONS, PRES], ['consumed | adj. prescribed', 'prescribed | adj. consumed'])
