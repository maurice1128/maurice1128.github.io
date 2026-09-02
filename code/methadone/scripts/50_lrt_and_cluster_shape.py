# -*- coding: utf-8 -*-
"""Two gaps the R4 cold reader identified.

(1) The claim "cluster membership is not reducible to any single continuous
    slope" is supported by a likelihood-ratio test against the POST-test slope
    only -- the quantity the paper disclaims. Redo it against the pre-test slope
    (the claimed exposure), and against both together.
(2) Table 2 gives no indication of what each cluster's trajectory looks like.
    Compute per-cluster mean pre- and post-test slopes so the table can show the
    gradient the paper claims."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings, json; warnings.filterwarnings('ignore')
from scipy.special import i0
from scipy.stats import chi2
from sklearn.cluster import KMeans
import statsmodels.api as sm
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
c = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = c('All_fill_norm'); pc, pp, nc, np_ = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = c('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
sa, sb, xa, xb = c('slope_burst_min_7da'), c('slope_burst_min_7db'), c('slope_burst_max_7da'), c('slope_burst_max_7db')
POST = np.r_[v(xa[0]), v(xa[2])]      # post-test max slope (disclaimed)
PRE = np.r_[v(xb[0]), v(xb[2])]       # pre-test max slope  (claimed)

up = ~(np.abs(np.diff(pc[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(nc[:, 21:36], axis=1)).sum(1) != 0); svn = ~un
proj = lambda a, b, mk: (np.hstack([a[mk], b[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pc, pp, up)[:, 1]-.0270, proj(pc, pp, up)[:, 0]+.04) % (2*np.pi)
thn = np.arctan2(proj(nc, np_, un)[:, 1]-.0270, proj(nc, np_, un)[:, 0]+.04) % (2*np.pi)
G = np.linspace(0, 2*np.pi, 721)[:-1]
dd = np.array([np.exp(12*np.cos(g-thp)).sum() for g in G])
cuts = np.sort(G[[i for i in range(len(dd)) if dd[i] < dd[(i-1) % len(dd)] and dd[i] <= dd[(i+1) % len(dd)]]])
def vmpdf(t, m, k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
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

# ---------- (1) LRT: clusters vs each scalar ----------
D=np.column_stack([(clab==f'7d-{i}').astype(float) for i in range(1,7)]+
                  [(clab==f'PCA-{i}').astype(float) for i in range(1,4)])[:,1:]  # drop one as reference
z=lambda a:(a-a.mean())/a.std()
print('=== LRT: does cluster membership add to a single continuous slope? ===')
for nm,S in [('post-test slope (disclaimed)',[POST]),('pre-test slope (CLAIMED)',[PRE]),
             ('both slopes together',[PRE,POST])]:
    X0=sm.add_constant(np.column_stack([z(s) for s in S]))
    r0=sm.Logit(y,X0).fit(disp=0)
    r1=sm.Logit(y,np.column_stack([X0,D])).fit(disp=0)
    lr=2*(r1.llf-r0.llf); df=D.shape[1]
    print('  vs %-30s LR chi2=%.1f df=%d p=%.2e | pseudo-R2 %.4f -> %.4f'
          %(nm,lr,df,chi2.sf(lr,df),r0.prsquared,r1.prsquared))

# ---------- (2) per-cluster trajectory descriptors for Table 2 ----------
print('\n=== per-cluster mean slopes (for Table 2) ===')
print('cluster | pre-test slope | post-test slope | shape')
out={}
for cl in [f'7d-{i}' for i in range(1,7)]+[f'PCA-{i}' for i in range(1,4)]:
    m=(clab==cl)
    pr,po=PRE[m].mean(),POST[m].mean()
    if cl.startswith('PCA'): shape='stable dose (no ±7-day change)'
    else:
        shape=('rise before, rise after' if pr>0 and po>0 else
               'rise before, fall after' if pr>0 else
               'fall before, rise after' if po>0 else 'fall before, fall after')
    print('  %-6s | %+8.4f | %+8.4f | %s'%(cl,pr,po,shape))
    out[cl]=dict(pre=round(float(pr),4),post=round(float(po),4),shape=shape)
json.dump(out,open(_os.path.join(ROOT, r'analysis\cluster_shape.json'),'w'),indent=2)
print('wrote cluster_shape.json')
