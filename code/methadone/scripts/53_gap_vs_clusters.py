# -*- coding: utf-8 -*-
"""(1) Do the nine clusters still add anything once consumption fraction is in the model?
   (2) Out-of-sample predictive utility of the fraction vs the clusters."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings, json; warnings.filterwarnings('ignore')
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from scipy.special import i0
from scipy.stats import chi2
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
import statsmodels.api as sm

f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
c = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = c('All_fill_norm'); pc, pp, nc, np_ = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = c('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
sa, sb, xa, xb = c('slope_burst_min_7da'), c('slope_burst_min_7db'), c('slope_burst_max_7da'), c('slope_burst_max_7db')
PRE = np.r_[v(xb[0]), v(xb[2])]
FREQ = np.r_[v(c('freq_All')[0]), v(c('freq_All')[2])]

# ---- clusters, exactly as 50_ ----
up = ~(np.abs(np.diff(pc[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(nc[:, 21:36], axis=1)).sum(1) != 0); svn = ~un
proj = lambda a, b, mk: (np.hstack([a[mk], b[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pc, pp, up)[:, 1]-.0270, proj(pc, pp, up)[:, 0]+.04) % (2*np.pi)
thn = np.arctan2(proj(nc, np_, un)[:, 1]-.0270, proj(nc, np_, un)[:, 0]+.04) % (2*np.pi)
G = np.linspace(0, 2*np.pi, 721)[:-1]
dd = np.array([np.exp(12*np.cos(g-thp)).sum() for g in G])
cuts = np.sort(G[[i for i in range(len(dd)) if dd[i] < dd[(i-1) % len(dd)] and dd[i] <= dd[(i+1) % len(dd)]]])
vmpdf = lambda t, m, k: np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t, w):
    C=(w*np.cos(t)).sum(); S=(w*np.sin(t)).sum(); s=w.sum()+1e-12
    R=min(np.sqrt(C*C+S*S)/s,.999); return np.arctan2(S,C), R*(2-R*R)/(1-R*R)
t1p=np.arctan2(v(sb[0])[svp],v(sa[0])[svp]); t2p=np.arctan2(v(xb[0])[svp],v(xa[0])[svp])
t1n=np.arctan2(v(sb[2])[svn],v(sa[2])[svn]); t2n=np.arctan2(v(xb[2])[svn],v(xa[2])[svn])
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1p),np.sin(t1p),np.cos(t2p),np.sin(t2p)]))
P=np.zeros((6,len(t1p))); P[lab0,np.arange(len(t1p))]=1
m1=np.zeros(6);k1=np.ones(6);mm=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(120):
    for k in range(6): w=P[k]; m1[k],k1[k]=vm_mle(t1p,w); mm[k],k2[k]=vm_mle(t2p,w); pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1p,m1[k],k1[k])*vmpdf(t2p,mm[k],k2[k]) for k in range(6)]); P/=P.sum(0)+1e-300
asg=lambda a,b:np.array([pi[k]*vmpdf(a,m1[k],k1[k])*vmpdf(b,mm[k],k2[k]) for k in range(6)]).argmax(0)
clab=np.empty(TP+TN,object)
clab[:TP][up]=[f'PCA-{x+1}' for x in np.searchsorted(cuts,thp)%len(cuts)]
clab[:TP][svp]=[f'7d-{x+1}' for x in P.argmax(0)]
clab[TP:][un]=[f'PCA-{x+1}' for x in np.searchsorted(cuts,thn)%len(cuts)]
clab[TP:][svn]=[f'7d-{x+1}' for x in asg(t1n,t2n)]
D=np.column_stack([(clab==f'7d-{i}').astype(float) for i in range(1,7)]+
                  [(clab==f'PCA-{i}').astype(float) for i in range(1,4)])[:,1:]

# ---- consumption fraction ----
C4=[m2(x) for x in c('All_raw_fix')]
CON=np.vstack([C4[0],C4[2]]); PRS=np.vstack([C4[1],C4[3]])
OBS=(CON!=-1)&(PRS!=-1)&(PRS>0)
FR=np.where(OBS,CON/np.where(PRS>0,PRS,1),np.nan)
FRAC=np.nanmean(FR[:,21:29],1)
free7=~((CON[:,21:36]==-1).any(1))
z=lambda a:(a-np.nanmean(a))/np.nanstd(a)

ok=np.isfinite(FRAC)&np.isfinite(PRE)&np.isfinite(FREQ)
print('可用 n = %d（%d 位病人）\n'%(ok.sum(),pd.Series(pid[ok]).nunique()))

def lrt(base_cols,add_cols,mask,nm):
    X0=sm.add_constant(np.column_stack(base_cols)[mask]) if base_cols else np.ones((mask.sum(),1))
    X1=sm.add_constant(np.column_stack(base_cols+add_cols)[mask]) if base_cols else sm.add_constant(np.column_stack(add_cols)[mask])
    r0=sm.GLM(y[mask],X0,family=sm.families.Binomial()).fit()
    r1=sm.GLM(y[mask],X1,family=sm.families.Binomial()).fit()
    df=X1.shape[1]-X0.shape[1]; st=2*(r1.llf-r0.llf); p=chi2.sf(st,df)
    print('   %-52s chi2=%8.1f  df=%2d  p=%.2e'%(nm,st,df,p))

for lab,mask in [('全樣本',ok),('無內插 ±7',ok&free7)]:
    print('=== %s (n=%d) ==='%(lab,mask.sum()))
    print('  問題1：分群還有沒有用？')
    lrt([z(FRAC)],[D],mask,'服用比例  →  加上 9 個分群')
    lrt([D],[z(FRAC)],mask,'9 個分群  →  加上服用比例')
    lrt([z(PRE)],[z(FRAC)],mask,'主稿曝險  →  加上服用比例')
    lrt([z(FRAC)],[z(PRE)],mask,'服用比例  →  加上主稿曝險')
    print()

print('=== 問題2：樣本外預測力（依病人分組 5-fold，不讓同一病人跨組）===')
def cv_auc(cols,mask):
    X=np.column_stack(cols)[mask]; Y=y[mask]; G=pid[mask]; pr=np.zeros(len(Y))
    add=lambda M: np.column_stack([np.ones(len(M)),M])
    for tr,te in GroupKFold(5).split(X,Y,G):
        r=sm.GLM(Y[tr],add(X[tr]),family=sm.families.Binomial()).fit()
        pr[te]=r.predict(add(X[te]))
    return roc_auc_score(Y,pr)
for lab,mask in [('全樣本',ok),('無內插 ±7',ok&free7)]:
    print('  --- %s ---'%lab)
    base=[z(FREQ)]
    rows=[('出席率（基準）',base),
          ('基準 + 主稿曝險',base+[z(PRE)]),
          ('基準 + 9 個分群',base+[D]),
          ('基準 + 服用比例',base+[z(FRAC)]),
          ('基準 + 服用比例 + 分群',base+[z(FRAC),D]),
          ('只用服用比例',[z(FRAC)])]
    b=None
    for nm,cols in rows:
        a=cv_auc(cols,mask)
        if b is None: b=a
        print('     %-26s AUC=%.4f   ΔAUC=%+.4f'%(nm,a,a-b))
