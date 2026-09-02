# -*- coding: utf-8 -*-
"""Confound battery for the consumption-fraction ("gap") signal.

Concentration identification: in raw data\2018-2022美沙冬每日劑量.xlsx the ratio
處方劑量(mg)/服藥劑量(cc) has a hard floor at exactly 10.0000 across 1,009,074 rows with
ZERO values below it; taking 10 mg/cc bounds consumed/prescribed at exactly 1.0000 with
zero violations. All_raw_fix[0]/[2] already hold consumed in mg, so the fraction is
computable directly on the analysis windows (verified: max ratio 1.0000, 0 violations).

Run: python 52_gap_confounds.py
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, sys, warnings; warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from statsmodels.discrete.conditional_models import ConditionalLogit

f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
C = [m2(x) for x in cells('All_raw_fix')]
CON = np.vstack([C[0], C[2]]); PRS = np.vstack([C[1], C[3]])
OBS = (CON != -1) & (PRS != -1) & (PRS > 0)
FR = np.where(OBS, CON / np.where(PRS > 0, PRS, 1), np.nan)
CONn = np.where(OBS, CON, np.nan); PRSn = np.where(OBS, PRS, np.nan)
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
free7 = ~((CON[:, 21:36] == -1).any(1))
FREQ = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
P = slice(21, 29)
F_frac = np.nanmean(FR[:, P], 1); F_con = np.nanmean(CONn[:, P], 1)
F_prs = np.nanmean(PRSn[:, P], 1); N_att = np.sum(OBS[:, P], 1).astype(float)

assert np.nanmax(FR) <= 1.0001, 'consumed exceeds prescribed - concentration wrong'

def within(mask, X, names, tag):
    m = mask.copy()
    for x in X: m &= np.isfinite(x)
    d = pd.DataFrame(dict(y=y[m], g=pid[m])); ok = d.groupby('g').y.nunique() == 2
    k = d.g.map(ok).values
    cols, keep = [], []
    for x, nm in zip(X, names):
        s = x[m][k]
        if np.nanstd(s) < 1e-12: print('     %-40s (no variance in this subset)' % nm); continue
        cols.append((s - s.mean()) / s.std()); keep.append(nm)
    if not cols: return
    Z = np.column_stack(cols)
    r = ConditionalLogit(y[m][k], Z, groups=pid[m][k]).fit(disp=0)
    print('  %s' % tag)
    for i, nm in enumerate(keep):
        b, se = r.params[i], r.bse[i]
        print('     %-40s OR/SD=%.3f  95%%CI %.2f-%.2f  p=%.1e'
              % (nm, np.exp(b), np.exp(b-1.96*se), np.exp(b+1.96*se), r.pvalues[i]))
    print('       n=%d tests, %d patients' % (len(Z), pd.Series(pid[m][k]).nunique()))

for lab, mask in [('ALL tests', np.ones(len(y), bool)), ('imputation-free +-7', free7)]:
    print('\n=================== %s ===================' % lab)
    within(mask, [F_frac], ['consumption fraction'], '1. unadjusted')
    within(mask, [F_frac, FREQ], ['fraction | adj. attendance', 'attendance | adj. fraction'],
           '2. adjusted for attendance')
    within(mask, [F_con, F_prs], ['consumed mg (absolute)', 'prescribed mg (absolute)'],
           '3. decomposition - which side moves?')
    within(mask, [F_frac, F_prs], ['fraction | adj. prescribed', 'prescribed | adj. fraction'],
           '4. is the fraction just prescribing in reverse?')
    within(mask, [F_frac, N_att], ['fraction | adj. days attended', 'days attended'],
           '5. adjusted for observable days')
