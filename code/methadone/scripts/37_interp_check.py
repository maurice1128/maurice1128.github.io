# -*- coding: utf-8 -*-
"""Does the reviewers' blocker (d) -- undisclosed filling/interpolation of the
primary exposure across missed dosing days -- threaten the MAIN CLAIM?

Logic: 'All_fill_norm' is filled. If the escalation signal were an artefact of
filling, it must vanish where nothing was filled. freq_All is the attendance rate;
freq==1.0 means every day in the window was attended => NOTHING to fill.
So: compare the headline escalation association on filled vs never-filled tests."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
import statsmodels.api as sm
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; v=lambda a:np.array(a).ravel()
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
fr=cells('freq_All'); att=np.r_[v(fr[0]),v(fr[2])]
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]; pid=np.r_[pidp,pidn]
xa,xb=cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
esc=np.r_[v(xa[0]),v(xa[2])]                      # post-test max slope = the escalation signal
print('attendance distribution: min=%.3f  ==1.0: %d (%.0f%%)  >=0.99: %d'%(att.min(),(att==1.0).sum(),(att==1.0).mean()*100,(att>=0.99).sum()))

def fit(mask,name):
    e=esc[mask]; z=(e-e.mean())/e.std()
    r=sm.Logit(y[mask],sm.add_constant(z)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid[mask]})
    print('  %-34s n=%5d  OR/SD=%.3f  95%%CI %.2f-%.2f  p=%.1e'%(
        name,mask.sum(),np.exp(r.params[1]),np.exp(r.params[1]-1.96*r.bse[1]),np.exp(r.params[1]+1.96*r.bse[1]),r.pvalues[1]))
    return float(np.exp(r.params[1]))

print('\n=== headline escalation -> positive urine, by how much was FILLED ===')
a=fit(np.ones(len(y),bool),'ALL tests (as reported in paper)')
b=fit(att==1.0,'ZERO filling (attendance exactly 1.0)')
c=fit(att<1.0,'SOME filling (attendance < 1.0)')
print('\n>>> if the signal were a filling artefact, the ZERO-filling OR would collapse to ~1.0')
print('>>> ZERO-filling OR = %.3f  vs  full-sample OR = %.3f'%(b,a))
print('>>> VERDICT: %s'%('SURVIVES - not a filling artefact' if b>1.05 else 'AT RISK - signal may be filling-driven'))
