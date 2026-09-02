# -*- coding: utf-8 -*-
"""Confounding by indication: is the pre-test rise in CONSUMED dose merely the
clinician raising the PRESCRIPTION? Raised by an audience reviewer of the talk;
the manuscript needs the answer that the slide already carries."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from statsmodels.discrete.conditional_models import ConditionalLogit
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm')
pos_c, pos_p, neg_c, neg_p = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
raw = cells('All_raw_fix'); R = np.vstack([m2(raw[0]), m2(raw[2])])
free7 = ~(R[:, 21:36] == -1).any(1)

# pre-test slope over days -7..0 (cols 21:29) for each series
sl = lambda M: np.polyfit(np.arange(8), M[:, 21:29].T, 1)[0]
cons = np.r_[sl(pos_c), sl(neg_c)]
pres = np.r_[sl(pos_p), sl(neg_p)]
print('correlation(consumed pre-test slope, prescribed pre-test slope) = %.3f'
      % np.corrcoef(cons, pres)[0, 1])

def within(mask, X, names):
    d = pd.DataFrame(dict(y=y[mask], g=pid[mask]))
    ok = d.groupby('g').y.nunique() == 2; k = d.g.map(ok).values
    Z = np.column_stack([(x[mask][k] - x[mask][k].mean()) / x[mask][k].std() for x in X])
    r = ConditionalLogit(y[mask][k], Z, groups=pid[mask][k]).fit(disp=0)
    for i, nm in enumerate(names):
        b, se = r.params[i], r.bse[i]
        print('    %-34s OR/SD=%.3f  95%%CI %.2f-%.2f  p=%.2e' % (
            nm, np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se), r.pvalues[i]))

for lab, mask in [('ALL tests', np.ones(len(y), bool)), ('imputation-free +-7 window', free7)]:
    print('\n=== %s ===' % lab)
    within(mask, [cons], ['consumed slope alone'])
    within(mask, [cons, pres], ['consumed slope | adj. prescribed', 'prescribed slope | adj. consumed'])
