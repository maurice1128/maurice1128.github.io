# -*- coding: utf-8 -*-
"""Council-3 load-bearing checks:
 (1) attendance-missingness artifact: do cluster P/N survive among COMPLETE-attendance tests?
 (2) estimand: does CLUSTER MEMBERSHIP (not just the scalar) survive WITHIN-patient (conditional logit)?"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.discrete.conditional_models import ConditionalLogit
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
freq=[v(cells('freq_All')[0]),v(cells('freq_All')[2])]   # attendance rate per test
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]; pid=np.r_[pidp,pidn]
att=np.r_[freq[0],freq[1]]
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
un=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0); svn=~un
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
proj=lambda pd_,ds_,mk:(np.hstack([pd_[mk],ds_[mk]])-mu0)@coeff.T
thp=np.arctan2(proj(pos_pd,pos_ds,up)[:,1]-0.0270,proj(pos_pd,pos_ds,up)[:,0]+0.04)%(2*np.pi)
thn=np.arctan2(proj(neg_pd,neg_ds,un)[:,1]-0.0270,proj(neg_pd,neg_ds,un)[:,0]+0.04)%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]; d=np.array([np.exp(12*np.cos(g-thp)).sum() for g in grid])
cuts=np.sort(grid[[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]])
pca_p=np.searchsorted(cuts,thp)%len(cuts); pca_n=np.searchsorted(cuts,thn)%len(cuts)
def vmpdf(t,m,k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t,w):
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12;R=min(np.sqrt(C*C+S*S)/s,0.999);return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
t1=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]);t2=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
P=np.zeros((6,len(t1)));P[lab0,np.arange(len(t1))]=1;m1=np.zeros(6);k1=np.ones(6);m2_=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(120):
    for k in range(6):w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
asg=lambda a,b,c,dd:(lambda a1,a2:np.array([pi[k]*vmpdf(a1,m1[k],k1[k])*vmpdf(a2,m2_[k],k2[k]) for k in range(6)]).argmax(0))(np.arctan2(b,a),np.arctan2(dd,c))
clab=np.empty(TP+TN,object)
clab[:TP][up]=[f'PCA-{c+1}' for c in pca_p];clab[:TP][svp]=[f'7d-{c+1}' for c in P.argmax(0)]
clab[TP:][un]=[f'PCA-{c+1}' for c in pca_n];clab[TP:][svn]=[f'7d-{c+1}' for c in asg(neg['mn_a'][svn],neg['mn_b'][svn],neg['mx_a'][svn],neg['mx_b'][svn])]
clusters=sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1])))

print('=== (1) COMPLETE-ATTENDANCE sensitivity (does escalation survive without missing days?) ===')
comp=att>=0.99   # full attendance in the window
print(f'complete-attendance tests: {comp.sum()} / {len(att)} ({comp.mean()*100:.0f}%);  pos among them={int(y[comp].sum())}, neg={int((y[comp]==0).sum())}')
TPc=int(y[comp].sum()); TNc=int((y[comp]==0).sum())
rows=[]
for c in clusters:
    m=(clab==c)&comp; posN=int((m&(y==1)).sum()); negN=int((m&(y==0)).sum())
    if posN<5 or negN<5: rows.append((c,np.nan,np.nan)); continue
    pn=(posN/TPc)/(negN/TNc)
    inc=((clab==c)&comp).astype(float)
    try: p=sm.Logit(y[comp],sm.add_constant(inc[comp])).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid[comp]}).pvalues[1]
    except: p=np.nan
    rows.append((c,pn,p))
qs=multipletests([r[2] if np.isfinite(r[2]) else 1 for r in rows],method='fdr_bh')[1]
for (c,pn,p),q in zip(rows,qs):
    tag='HIGH' if pn>1.2 and q<0.05 else ('LOW' if pn<0.83 and q<0.05 else '')
    print(f'  {c:8s} P/N={pn:.2f} q={q:.1e} {tag}')

print('\n=== (2) WITHIN-PATIENT validation of CLUSTER MEMBERSHIP (conditional logit, cluster dummies) ===')
import pandas as pd
D=pd.get_dummies(pd.Series(clab),drop_first=True).astype(float)   # cluster indicators
try:
    r=ConditionalLogit(y,D.values,groups=pid).fit(disp=0)
    print('  within-patient cluster effects (OR, p) — vs reference cluster:')
    for name,b,p in zip(D.columns,r.params,r.pvalues):
        s='*' if p<0.05 else ''
        print(f'    {name:8s} OR={np.exp(b):.2f}  p={p:.1e} {s}')
    nsig=int((r.pvalues<0.05).sum())
    print(f'  >>> {nsig}/{len(D.columns)} cluster indicators significant WITHIN-patient (vs reference)')
except Exception as e:
    print('  conditional logit error:',e)
