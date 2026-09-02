# -*- coding: utf-8 -*-
"""Council H2: re-derive clusters OUTCOME-BLIND (fit on pooled pos+neg, not
   positives-only) and re-estimate P/N + patient-clustered significance.
   If higher/lower-risk pattern survives -> associations are not circular artefact."""
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
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499
upp=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); upn=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0)
svp=~upp; svn=~upn
# ---- pooled arrays (blinded) ----
pd_all=np.vstack([pos_pd,neg_pd]); ds_all=np.vstack([pos_ds,neg_ds]); pid=np.r_[pidp,pidn]; y=np.r_[np.ones(TP),np.zeros(TN)]
up=np.r_[upp,upn]; sv=~up
mna=np.r_[pos['mn_a'],neg['mn_a']];mnb=np.r_[pos['mn_b'],neg['mn_b']];mxa=np.r_[pos['mx_a'],neg['mx_a']];mxb=np.r_[pos['mx_b'],neg['mx_b']]
# ---- PCA branch: fit PCA + KDE valleys on POOLED unchanged ----
X=np.hstack([pd_all[up],ds_all[up]]); mu=X.mean(0); coeff=np.linalg.svd(X-mu,full_matrices=False)[2].T
th=np.arctan2(((X-mu)@coeff)[:,1],((X-mu)@coeff)[:,0])%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]; d=np.array([np.exp(12*np.cos(gg-th)).sum() for gg in grid])
cuts=np.sort(grid[[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]])
pca_lab=np.searchsorted(cuts,th)%max(len(cuts),1)
# ---- 7d branch: von Mises K=6 on POOLED dose-change angles ----
def vmpdf(t,m,k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t,w):
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12;R=min(np.sqrt(C*C+S*S)/s,0.999);return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
t1=np.arctan2(mnb[sv],mna[sv]);t2=np.arctan2(mxb[sv],mxa[sv])
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
P=np.zeros((6,len(t1)));P[lab0,np.arange(len(t1))]=1;m1=np.zeros(6);k1=np.ones(6);m2_=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(120):
    for k in range(6):w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
sev_lab=P.argmax(0)
clab=np.empty(len(y),object);clab[up]=[f'PCA-{c+1}' for c in pca_lab];clab[sv]=[f'7d-{c+1}' for c in sev_lab]
rows=[]
for c in sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1]))):
    inc=(clab==c).astype(float)
    r=sm.Logit(y,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    posN=int(((clab==c)&(y==1)).sum());negN=int(((clab==c)&(y==0)).sum())
    pn=(posN/TP)/(negN/TN) if negN else np.nan
    rows.append((c,posN,negN,pn,r.pvalues[1]))
q=multipletests([r[4] for r in rows],method='fdr_bh')[1]
print('=== OUTCOME-BLIND clustering (fit on pooled pos+neg) ===')
print(f'{"cluster":8s} {"P/N":>6s} {"q":>9s}')
nsig=0
for (c,pN,nN,pn,p),qq in zip(rows,q):
    tag='HIGH' if pn>1.2 and qq<0.05 else('LOW' if pn<0.83 and qq<0.05 else '')
    if qq<0.05:nsig+=1
    print(f'{c:8s} {pn:6.2f} {qq:9.1e} {tag}')
print(f'\nsignificant after outcome-blind: {nsig}/{len(rows)}  (paper positive-only-fit: 9/9)')
print('PCA has high-risk?', any(c.startswith("PCA") and pn>1.2 and qq<0.05 for (c,_,_,pn,_),qq in zip(rows,q)))
