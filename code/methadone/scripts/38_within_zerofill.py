# -*- coding: utf-8 -*-
"""Does the paper's MOST load-bearing number -- the WITHIN-PATIENT escalation
OR 1.36/SD -- survive on tests with ZERO interpolation (attendance == 1.0)?

37_interp_check.py showed the pooled continuous escalation scalar does NOT
(OR 1.07, p=0.11 on zero-filled tests), while the CLUSTER taxonomy does
(34_council3_checks.py: 7d-1 P/N 1.95, q=3.8e-08). This decides whether the
within-patient result belongs to the surviving side or the dying side."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from statsmodels.discrete.conditional_models import ConditionalLogit
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; v=lambda a:np.array(a).ravel()
hdr=cells('All_fill_header'); pid=np.r_[v(hdr[0]).astype(int),v(hdr[2]).astype(int)]
fr=cells('freq_All'); att=np.r_[v(fr[0]),v(fr[2])]
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]
xa=cells('slope_burst_max_7da'); sa=cells('slope_burst_min_7da')
esc=np.r_[v(xa[0]),v(xa[2])]        # post-test max slope (escalation)
pre=np.r_[v(sa[0]),v(sa[2])]        # pre-test min slope

def within(mask,x,name):
    xx=x[mask]; z=(xx-xx.mean())/xx.std()
    g=pid[mask]; yy=y[mask]
    # keep only patients with BOTH outcomes (conditional logit uses discordant sets only)
    d=pd.DataFrame(dict(y=yy,g=g)); ok=d.groupby('g').y.nunique()==2
    keep=d.g.map(ok).values
    if keep.sum()<50: print(f'  {name}: too few discordant ({keep.sum()})'); return
    r=ConditionalLogit(yy[keep],z[keep][:,None],groups=g[keep]).fit(disp=0)
    b,se=r.params[0],r.bse[0]
    print('  %-40s n=%5d pat=%4d  OR/SD=%.3f  95%%CI %.2f-%.2f  p=%.2e  %s'%(
        name,keep.sum(),len(set(g[keep])),np.exp(b),np.exp(b-1.96*se),np.exp(b+1.96*se),r.pvalues[0],
        'SIG' if r.pvalues[0]<0.05 else 'ns'))

allm=np.ones(len(y),bool); zero=att==1.0; some=att<1.0
print('=== WITHIN-PATIENT (conditional logit) escalation -> positive urine ===')
print('post-test escalation (the paper reports OR 1.36/SD on all tests):')
within(allm,esc,'ALL tests'); within(zero,esc,'ZERO filling (attendance==1.0)'); within(some,esc,'SOME filling (attendance<1.0)')
print('\npre-test slope (paper reports OR 1.15/SD):')
within(allm,pre,'ALL tests'); within(zero,pre,'ZERO filling (attendance==1.0)')
print('\n>>> Read: if ZERO-filling within-patient stays significant, the within-patient')
print('    claim is NOT filling-driven. If it collapses like the pooled scalar did,')
print('    the paper must say so and lean on the CLUSTER result instead.')
