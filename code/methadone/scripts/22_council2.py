# -*- coding: utf-8 -*-
"""Verification council round-2: the three substantive questions.
 A. Do cluster associations survive ADJUSTMENT for attendance? (dose vs attendance-in-disguise)
 B. PRE-test vs POST-test slope: which side carries the association? (behaviour vs clinic-response)
 C. Does the 9-cluster TAXONOMY beat a single CONTINUOUS dose-change scalar? (is clustering worth it)
Uses the aim2 final clustering (consumed dose) + freq_All attendance."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
att=np.r_[v(cells('freq_All')[0]),v(cells('freq_All')[2])]
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499; y=np.r_[np.ones(TP),np.zeros(TN)]; pid=np.r_[pidp,pidn]
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
un=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0); svn=~un
# ---- reproduce final clustering (PCA KDE-3 + 7d vM-6) ----
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
s7p=P.argmax(0)
def asg7(mn_a,mn_b,mx_a,mx_b):
    a1=np.arctan2(mn_b,mn_a);a2=np.arctan2(mx_b,mx_a)
    return np.array([pi[k]*vmpdf(a1,m1[k],k1[k])*vmpdf(a2,m2_[k],k2[k]) for k in range(6)]).argmax(0)
s7n=asg7(neg['mn_a'][svn],neg['mn_b'][svn],neg['mx_a'][svn],neg['mx_b'][svn])
clab=np.empty(TP+TN,object)
clab[:TP][up]=[f'PCA-{c+1}' for c in pca_p]; clab[:TP][svp]=[f'7d-{c+1}' for c in s7p]
clab[TP:][un]=[f'PCA-{c+1}' for c in pca_n]; clab[TP:][svn]=[f'7d-{c+1}' for c in s7n]
clusters=sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1])))

print('=== A. cluster associations UNADJUSTED vs ATTENDANCE-ADJUSTED ===')
rows=[]
for c in clusters:
    inc=(clab==c).astype(float)
    r0=sm.Logit(y,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    X=np.column_stack([inc,att]); r1=sm.Logit(y,sm.add_constant(X)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    rows.append((c,np.exp(r0.params[1]),r0.pvalues[1],np.exp(r1.params[1]),r1.pvalues[1]))
q0=multipletests([r[2] for r in rows],method='fdr_bh')[1]; q1=multipletests([r[4] for r in rows],method='fdr_bh')[1]
print(f'{"clu":7s} {"OR":>5s} {"q":>8s} | {"OR|att":>7s} {"q|att":>8s}  survive?')
nsurv=0
for (c,o0,p0,o1,p1),Q0,Q1 in zip(rows,q0,q1):
    s=(Q1<0.05); nsurv+=s
    print(f'{c:7s} {o0:5.2f} {Q0:8.1e} | {o1:7.2f} {Q1:8.1e}  {"YES" if s else "no"}')
print(f'clusters still significant after adjusting for attendance: {nsurv}/{len(clusters)}')

print('\n=== B. PRE-test vs POST-test slope (which side drives it?) ===')
def orsd(arr_p,arr_n):
    x=np.r_[arr_p,arr_n]; z=(x-np.nanmean(x))/np.nanstd(x)
    r=sm.Logit(y,sm.add_constant(np.nan_to_num(z))).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid}); return np.exp(r.params[1]),r.pvalues[1]
for nm,a,b in [('PRE-test max slope (7db)',pos['mx_b'],neg['mx_b']),('POST-test max slope (7da)',pos['mx_a'],neg['mx_a']),
               ('PRE-test min slope (7db)',pos['mn_b'],neg['mn_b']),('POST-test min slope (7da)',pos['mn_a'],neg['mn_a'])]:
    o,p=orsd(a,b); print(f'  {nm:26s}: OR/SD={o:.2f}  p={p:.1e}')

print('\n=== C. does the 9-cluster TAXONOMY beat a single continuous scalar? ===')
# continuous scalar = post-test max slope (the escalation gradient)
scal=np.r_[pos['mx_a'],neg['mx_a']]; scal=(scal-scal.mean())/scal.std()
import pandas as pd
dfm=pd.DataFrame({'y':y,'scal':np.nan_to_num(scal),'clu':clab})
m_scal=sm.Logit(dfm.y,sm.add_constant(dfm[['scal']])).fit(disp=0)
Xc=pd.get_dummies(dfm.clu,drop_first=True).astype(float); m_clu=sm.Logit(dfm.y,sm.add_constant(Xc)).fit(disp=0)
Xb=pd.concat([dfm[['scal']],Xc],axis=1); m_both=sm.Logit(dfm.y,sm.add_constant(Xb.astype(float))).fit(disp=0)
print(f'  scalar only : AIC={m_scal.aic:.0f}  pseudo-R2={m_scal.prsquared:.4f}')
print(f'  clusters    : AIC={m_clu.aic:.0f}  pseudo-R2={m_clu.prsquared:.4f}')
print(f'  both        : AIC={m_both.aic:.0f}  pseudo-R2={m_both.prsquared:.4f}')
from scipy.stats import chi2
lr=2*(m_both.llf-m_scal.llf); dfree=Xc.shape[1]; pval=chi2.sf(lr,dfree)
print(f'  LRT clusters add over scalar: chi2={lr:.1f}, df={dfree}, p={pval:.1e}  -> {"clusters ADD" if pval<0.05 else "clusters do NOT add"}')
