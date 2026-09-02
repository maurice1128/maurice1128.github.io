# -*- coding: utf-8 -*-
"""Does PCA-3 (and the taxonomy) hold against TRUE negatives (supervised/陪同 urine)?
If PCA-3's higher-risk survives when the comparator is confirmed true-negatives,
its outcome-blind failure was false-negative contamination, not an artefact."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings, openpyxl; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
# --- supervised (true-negative) patient list ---
wb=openpyxl.load_workbook(_os.path.join(ROOT, r'raw data\陪同驗尿的名單.xlsx'),read_only=True,data_only=True)
ws=wb.active; it=ws.iter_rows(values_only=True); next(it)
sup=set()
for r in it:
    if r[1] is not None:
        try: sup.add(int(r[1]))
        except: pass
wb.close()
print(f'supervised patients: {len(sup)}')
# --- aim2 clustering (consumed dose) ---
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
un=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0); svn=~un
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
def asg(mn_a,mn_b,mx_a,mx_b):
    a1=np.arctan2(mn_b,mn_a);a2=np.arctan2(mx_b,mx_a)
    return np.array([pi[k]*vmpdf(a1,m1[k],k1[k])*vmpdf(a2,m2_[k],k2[k]) for k in range(6)]).argmax(0)
s7n=asg(neg['mn_a'][svn],neg['mn_b'][svn],neg['mx_a'][svn],neg['mx_b'][svn])
clab_p=np.empty(TP,object);clab_p[up]=[f'PCA-{c+1}' for c in pca_p];clab_p[svp]=[f'7d-{c+1}' for c in P.argmax(0)]
clab_n=np.empty(TN,object);clab_n[un]=[f'PCA-{c+1}' for c in pca_n];clab_n[svn]=[f'7d-{c+1}' for c in s7n]
# --- restrict negatives to TRUE (supervised) negatives ---
truen=np.array([p in sup for p in pidn])
nTN=int(truen.sum())
print(f'aim2 negative tests: {TN}; from supervised patients (TRUE negatives): {nTN} ({nTN/TN*100:.1f}%)')
print(f'aim2 positive tests from supervised patients: {int(np.isin(pidp,list(sup)).sum())}')
clusters=sorted(set(clab_p),key=lambda s:(s.split("-")[0],int(s.split("-")[1])))
print(f'\n{"cluster":8s} {"P/N vs ALL neg":>14s} {"P/N vs TRUE neg":>16s} {"q(true)":>9s}')
y_all=np.r_[np.ones(TP),np.zeros(nTN)]; pid_all=np.r_[pidp,pidn[truen]]
rows=[]
for c in clusters:
    posN=int((clab_p==c).sum()); negA=int((clab_n==c).sum()); negT=int((clab_n[truen]==c).sum())
    pnA=(posN/TP)/(negA/TN) if negA else np.nan
    pnT=(posN/TP)/(negT/nTN) if negT else np.nan
    inc=np.r_[(clab_p==c).astype(float),(clab_n[truen]==c).astype(float)]
    try: p=sm.Logit(y_all,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid_all}).pvalues[1]
    except: p=np.nan
    rows.append((c,pnA,pnT,p))
q=multipletests([r[3] for r in rows],method='fdr_bh')[1]
for (c,pnA,pnT,p),qq in zip(rows,q):
    mark=' <<< PCA-3' if c=='PCA-3' else ''
    tag='HIGH' if pnT>1.2 and qq<0.05 else ('LOW' if pnT<0.83 and qq<0.05 else 'ns')
    print(f'{c:8s} {pnA:>14.2f} {pnT:>16.2f} {qq:>9.1e} {tag}{mark}')
