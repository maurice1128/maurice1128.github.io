# -*- coding: utf-8 -*-
"""EXPLORATORY: consumed-as-fraction-of-prescribed ("gap") around the urine test.

The syrup concentration is identifiable from the raw extract: mg/cc has a hard floor at
exactly 10.0000 over 1,009,074 dosing rows with zero values below it, and taking 10 mg/cc
bounds consumed/prescribed at exactly 1.0000 with zero violations. The MAT windows already
carry consumed in mg, so the fraction is computable directly on the analysis windows.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, sys, warnings
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit

f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
C = [m2(x) for x in cells('All_raw_fix')]
CONSUMED = np.vstack([C[0], C[2]])          # mg actually drunk
PRESCRIBED = np.vstack([C[1], C[3]])        # mg prescribed
OBS = (CONSUMED != -1) & (PRESCRIBED != -1) & (PRESCRIBED > 0)

TP, TN = 3401, 6499
y = np.r_[np.ones(TP), np.zeros(TN)]
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
free7 = ~((CONSUMED[:, 21:36] == -1).any(1))          # no interpolated day, -7..+7
freqA = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])] if 'freq_All' in f else None

FRAC = np.where(OBS, CONSUMED / np.where(PRESCRIBED > 0, PRESCRIBED, 1), np.nan)
PRE = slice(21, 29)      # day -7 .. 0
POST = slice(28, 36)     # day 0 .. +7

def nanmean(M): 
    with warnings.catch_warnings(): warnings.simplefilter('ignore'); return np.nanmean(M, 1)
def maxslope(M):
    out = np.full(M.shape[0], np.nan)
    for i in range(M.shape[0]):
        w = M[i]; s = [(w[j+2]-w[j])/2.0 for j in range(len(w)-2) if np.isfinite(w[j]) and np.isfinite(w[j+2])]
        if s: out[i] = max(s)
    return out

feats = {
 'pre-test mean consumption fraction'      : nanmean(FRAC[:, PRE]),
 'pre-test max 3-day rise in fraction'     : maxslope(FRAC[:, PRE]),
 'pre-test max 3-day FALL in fraction'     : -maxslope(-FRAC[:, PRE]),
 'whole-window mean consumption fraction'  : nanmean(FRAC),
}

def zs(x, m):
    z = np.full_like(x, np.nan, dtype=float); s = x[m]
    z[m] = (s - np.nanmean(s)) / np.nanstd(s); return z

print('=' * 92)
print('%-42s %-26s %s' % ('特徵', '全樣本 (病人叢集穩健)', '無內插子集'))
print('=' * 92)
for name, x in feats.items():
    row = ['%-42s' % name]
    for lab, sub in [('all', np.ones(len(y), bool)), ('free7', free7)]:
        m = sub & np.isfinite(x)
        z = zs(x, m)
        X = sm.add_constant(z[m])
        r = sm.GLM(y[m], X, family=sm.families.Binomial()).fit(
            cov_type='cluster', cov_kwds={'groups': pid[m]})
        or_, p = np.exp(r.params[1]), r.pvalues[1]
        lo, hi = np.exp(r.conf_int()[1])
        row.append('OR %.2f (%.2f-%.2f) p=%.1e' % (or_, lo, hi, p))
    print('  '.join(row))
print('=' * 92)

print('\n病人內自比（conditional logit, 病人固定效果）:')
for name, x in feats.items():
    for lab, sub in [('全樣本', np.ones(len(y), bool)), ('無內插', free7)]:
        m = sub & np.isfinite(x)
        d = pd.DataFrame({'y': y[m], 'x': zs(x, m)[m], 'g': pid[m]})
        keep = d.groupby('g')['y'].transform('nunique') > 1
        d = d[keep]
        if len(d) < 100: print('  %-42s %-8s (可用樣本不足)' % (name, lab)); continue
        try:
            r = ConditionalLogit(d['y'], d[['x']], groups=d['g']).fit(disp=0)
            print('  %-42s %-8s OR %.2f (%.2f-%.2f) p=%.1e   n=%d, %d 人'
                  % (name, lab, np.exp(r.params[0]), np.exp(r.conf_int().iloc[0,0]),
                     np.exp(r.conf_int().iloc[0,1]), r.pvalues[0], len(d), d['g'].nunique()))
        except Exception as e:
            print('  %-42s %-8s 失敗 %s' % (name, lab, str(e)[:40]))

print('\n描述統計（服用佔處方的比例）:')
for lab, m in [('陽性', y == 1), ('陰性', y == 0)]:
    pre = nanmean(FRAC[:, PRE])[m]
    print('  %s  驗尿前一週平均: 中位=%.3f  平均=%.3f  n=%d'
          % (lab, np.nanmedian(pre), np.nanmean(pre), np.isfinite(pre).sum()))
