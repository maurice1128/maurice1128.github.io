# -*- coding: utf-8 -*-
"""DECISIVE TEST for the main claim.

Established so far:
  * pooled continuous escalation  : dies on zero-filled tests (OR 1.07, p=0.11)
  * within-patient continuous esc.: ALSO dies on zero-filled tests (OR 1.07, p=0.11)
  * cluster P/N (between)         : SURVIVES on zero-filled tests (7d-1 P/N 1.95, q=3.8e-08)

Open question that decides the paper: does WITHIN-PATIENT CLUSTER MEMBERSHIP
survive on the ZERO-FILLING subset? If yes, the taxonomy claim is safe and only
the continuous-scalar sentences need weakening. If no, the within-patient claim
must be restricted to the full sample and flagged as filling-dependent.

Also re-runs the continuous within-patient test with the CORRECT pre-test
variable (mx_b, as used by 24_within_patient.py; an earlier check wrongly used mn_a)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from statsmodels.discrete.conditional_models import ConditionalLogit
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]
m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pid=np.r_[v(hdr[0]).astype(int),v(hdr[2]).astype(int)]
fr=cells('freq_All'); att=np.r_[v(fr[0]),v(fr[2])]
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]
sa,sb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db')
xa,xb=cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0]))
neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
POST=np.r_[pos['mx_a'],neg['mx_a']]      # post-test escalation  (24_within_patient.py: mxa)
PRE =np.r_[pos['mx_b'],neg['mx_b']]      # pre-test escalation   (24_within_patient.py: mxb)

# ---------- rebuild the 9-cluster taxonomy (identical method to 15/36) ----------
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
un=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0); svn=~un
proj=lambda pd_,ds_,mk:(np.hstack([pd_[mk],ds_[mk]])-mu0)@coeff.T
thp=np.arctan2(proj(pos_pd,pos_ds,up)[:,1]-0.0270,proj(pos_pd,pos_ds,up)[:,0]+0.04)%(2*np.pi)
thn=np.arctan2(proj(neg_pd,neg_ds,un)[:,1]-0.0270,proj(neg_pd,neg_ds,un)[:,0]+0.04)%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]; dd=np.array([np.exp(12*np.cos(g-thp)).sum() for g in grid])
cuts=np.sort(grid[[i for i in range(len(dd)) if dd[i]<dd[(i-1)%len(dd)] and dd[i]<=dd[(i+1)%len(dd)]]])
pca_p=np.searchsorted(cuts,thp)%len(cuts); pca_n=np.searchsorted(cuts,thn)%len(cuts)
def vmpdf(t,m,k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t,w):
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12
    R=min(np.sqrt(C*C+S*S)/s,0.999); return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
t1=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]); t2=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
P=np.zeros((6,len(t1)));P[lab0,np.arange(len(t1))]=1
m1=np.zeros(6);k1=np.ones(6);mm=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(120):
    for k in range(6): w=P[k];m1[k],k1[k]=vm_mle(t1,w);mm[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,mm[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
asg=lambda a,b,c,d:np.array([pi[k]*vmpdf(np.arctan2(b,a),m1[k],k1[k])*vmpdf(np.arctan2(d,c),mm[k],k2[k]) for k in range(6)]).argmax(0)
clab=np.empty(TP+TN,object)
clab[:TP][up]=[f'PCA-{c+1}' for c in pca_p]; clab[:TP][svp]=[f'7d-{c+1}' for c in P.argmax(0)]
clab[TP:][un]=[f'PCA-{c+1}' for c in pca_n]
clab[TP:][svn]=[f'7d-{c+1}' for c in asg(neg['mn_a'][svn],neg['mn_b'][svn],neg['mx_a'][svn],neg['mx_b'][svn])]

def discordant(mask):
    d=pd.DataFrame(dict(y=y[mask],g=pid[mask]))
    ok=d.groupby('g').y.nunique()==2
    return d.g.map(ok).values

def cont(mask,x,name):
    k=discordant(mask); xx=x[mask][k]; z=(xx-xx.mean())/xx.std()
    r=ConditionalLogit(y[mask][k],z[:,None],groups=pid[mask][k]).fit(disp=0)
    b,se=r.params[0],r.bse[0]
    print('  %-38s n=%5d pat=%4d OR/SD=%.3f CI %.2f-%.2f p=%.2e %s'%(
        name,k.sum(),len(set(pid[mask][k])),np.exp(b),np.exp(b-1.96*se),np.exp(b+1.96*se),r.pvalues[0],
        'SIG' if r.pvalues[0]<0.05 else 'ns'))

zero=att==1.0; allm=np.ones(len(y),bool)
print('=== A. continuous within-patient, CORRECT variables (24_within_patient.py convention) ===')
print('post-test escalation (mx_a) — paper: OR 1.36')
cont(allm,POST,'ALL tests'); cont(zero,POST,'ZERO filling')
print('pre-test escalation (mx_b) — paper: OR 1.15')
cont(allm,PRE,'ALL tests'); cont(zero,PRE,'ZERO filling')

print('\n=== B. ★DECISIVE: within-patient CLUSTER MEMBERSHIP on ZERO-FILLING tests ===')
for nm,mask in [('ALL tests',allm),('ZERO filling (attendance==1.0)',zero)]:
    k=discordant(mask); yy=y[mask][k]; gg=pid[mask][k]
    D=pd.get_dummies(pd.Series(clab[mask][k]),drop_first=True).astype(float)
    D=D.loc[:,D.sum()>=10]
    try:
        r=ConditionalLogit(yy,D.values,groups=gg).fit(disp=0)
        nsig=int((r.pvalues<0.05).sum())
        print(f'  {nm}: n={k.sum()} pat={len(set(gg))} clusters_tested={D.shape[1]} -> {nsig}/{D.shape[1]} significant within-patient')
        for n_,b_,p_ in zip(D.columns,r.params,r.pvalues):
            print('      %-8s OR=%.2f p=%.1e %s'%(n_,np.exp(b_),p_,'*' if p_<0.05 else ''))
    except Exception as e:
        print(f'  {nm}: conditional logit failed: {e}')
print('\n>>> If cluster membership stays significant within-patient on ZERO-filling tests,')
print('    the TAXONOMY claim is safe and only the continuous-scalar sentences need weakening.')
