# -*- coding: utf-8 -*-
"""Council FINAL gate: within- vs between-patient decomposition.
Conditional logistic regression (patient fixed effects) uses ONLY within-patient
variation — it asks: within the same patient, do their POSITIVE tests differ from
their NEGATIVE tests in dose behaviour / attendance? If the association vanishes,
it is a static patient typology, not peri-test behaviour."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
att=np.r_[v(cells('freq_All')[0]),v(cells('freq_All')[2])]
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]; pid=np.r_[pidp,pidn]
z=lambda x:(x-np.nanmean(x))/(np.nanstd(x)+1e-9)
mxa=z(np.r_[pos['mx_a'],neg['mx_a']]); mxb=z(np.r_[pos['mx_b'],neg['mx_b']]); atz=z(att)

def between(col):  # pooled (patient-clustered SE) = between+within
    r=sm.Logit(y,sm.add_constant(np.nan_to_num(col))).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    return np.exp(r.params[1]),r.pvalues[1]
def within(col):   # conditional logit = within-patient only
    try:
        r=ConditionalLogit(y,np.nan_to_num(col).reshape(-1,1),groups=pid).fit(disp=0)
        return np.exp(r.params[0]),r.pvalues[0]
    except Exception as e:
        return float('nan'),float('nan')

n_disc=len(set(pid[y==1])&set(pid[y==0]))
print(f'patients with BOTH pos and neg tests (contribute to within-patient): {n_disc}')
print('\n=== pooled (between+within) vs WITHIN-patient (conditional logit) ===')
print(f'{"feature":26s} {"pooled OR/SD":>13s} {"p":>9s} | {"WITHIN OR/SD":>13s} {"p":>9s}')
for name,c in [('post-test escalation',mxa),('pre-test escalation',mxb),('attendance',atz)]:
    bo,bp=between(c); wo,wp=within(c)
    print(f'{name:26s} {bo:13.2f} {bp:9.1e} | {wo:13.2f} {wp:9.1e}')
print('\n(If WITHIN OR ~1 / ns -> the effect is between-patient typology, not peri-test dynamics.)')
