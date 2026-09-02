# -*- coding: utf-8 -*-
"""CORRECTION of 40_decisive_zerofill.py, forced by the R2 adversarial reviewer.

40_* defined its "complete-attendance" subset as freq_All == 1.0. freq_All is the
PRE-TEST-WEEK attendance rate only: it constrains neither the post-test window nor
the day-(-7) normalisation anchor. The headline shape/magnitude dissociation was
therefore computed on a mislabelled subset.

Here the imputation-free subsets are built directly from the pre-fill array
`All_raw_fix`, in which non-attended days carry -1:
    free_pre  : no -1 in days -7..0     (cols 21:29)
    free_post : no -1 in days  0..+7    (cols 28:36)
    free7     : no -1 anywhere in +-7   (cols 21:36)
    free28    : no -1 anywhere in +-28  (all 57 cols)
Every quantity the paper claims is re-estimated on free7, and the escalation->P/N
ordering (blocker B2/B3) is recomputed with p-values using BOTH the post-test slope
(which the paper declines to claim) and the pre-test slope (which it does claim)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit

f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
coeff = np.array(f['coeff']); mu0 = v(f['mu'])
afn = cells('All_fill_norm'); pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
raw = cells('All_raw_fix'); rpos, rneg = m2(raw[0]), m2(raw[2])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
xa, xb = cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
sa, sb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db')
POST = np.r_[v(xa[0]), v(xa[2])]     # post-test max slope
PRE  = np.r_[v(xb[0]), v(xb[2])]     # pre-test max slope

R = np.vstack([rpos, rneg])
free_pre  = ~(R[:, 21:29] == -1).any(1)
free_post = ~(R[:, 28:36] == -1).any(1)
free7     = ~(R[:, 21:36] == -1).any(1)
free28    = ~(R == -1).any(1)
oldmask   = att == 1.0
print('=== subset definitions compared ===')
for nm, m in [('OLD freq_All==1.0 (pre-week only)', oldmask), ('free_pre (-7..0)', free_pre),
              ('free_post (0..+7)', free_post), ('free7 (+-7 all)', free7), ('free28 (+-28 all)', free28)]:
    print('  %-34s n=%5d (%4.1f%%)  pos=%4d neg=%4d' % (nm, m.sum(), m.mean()*100, int(y[m].sum()), int((y[m]==0).sum())))
print('  OLD subset that is NOT actually +-7 imputation-free: %d of %d (%.0f%%)'
      % ((oldmask & ~free7).sum(), oldmask.sum(), (oldmask & ~free7).mean()*100))
print('  anchor day (-7) itself imputed within OLD subset: %d tests' % int((oldmask & (R[:, 21] == -1)).sum()))

# ---------- rebuild taxonomy (same method as 15/36) ----------
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un
proj = lambda a, b, mk: (np.hstack([a[mk], b[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(pos_pd, pos_ds, up)[:, 1] - .0270, proj(pos_pd, pos_ds, up)[:, 0] + .04) % (2*np.pi)
thn = np.arctan2(proj(neg_pd, neg_ds, un)[:, 1] - .0270, proj(neg_pd, neg_ds, un)[:, 0] + .04) % (2*np.pi)
G = np.linspace(0, 2*np.pi, 721)[:-1]
dd = np.array([np.exp(12*np.cos(g - thp)).sum() for g in G])
cuts = np.sort(G[[i for i in range(len(dd)) if dd[i] < dd[(i-1) % len(dd)] and dd[i] <= dd[(i+1) % len(dd)]]])
def vmpdf(t, m, k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t, w):
    C=(w*np.cos(t)).sum(); S=(w*np.sin(t)).sum(); s=w.sum()+1e-12
    Rr=min(np.sqrt(C*C+S*S)/s, .999); return np.arctan2(S, C), Rr*(2-Rr*Rr)/(1-Rr*Rr)
def vm_fit(t1, t2, K, seed=0, it=120):
    lab = KMeans(K, n_init=5, random_state=seed).fit_predict(np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab, np.arange(len(t1))] = 1
    m1=np.zeros(K); k1=np.ones(K); mm=np.zeros(K); k2=np.ones(K); pi=np.ones(K)/K
    for _ in range(it):
        for k in range(K): w=P[k]; m1[k],k1[k]=vm_mle(t1,w); mm[k],k2[k]=vm_mle(t2,w); pi[k]=w.mean()+1e-9
        P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,mm[k],k2[k]) for k in range(K)]); P/=P.sum(0)+1e-300
    return m1,k1,mm,k2,pi
def vm_assign(t1,t2,p):
    m1,k1,mm,k2,pi=p
    return np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,mm[k],k2[k]) for k in range(len(pi))]).argmax(0)
t1p=np.arctan2(v(sb[0])[svp], v(sa[0])[svp]); t2p=np.arctan2(v(xb[0])[svp], v(xa[0])[svp])
t1n=np.arctan2(v(sb[2])[svn], v(sa[2])[svn]); t2n=np.arctan2(v(xb[2])[svn], v(xa[2])[svn])
prm = vm_fit(t1p, t2p, 6)
clab = np.empty(TP+TN, object)
clab[:TP][up]=[f'PCA-{c+1}' for c in np.searchsorted(cuts,thp)%len(cuts)]
clab[:TP][svp]=[f'7d-{c+1}' for c in vm_assign(t1p,t2p,prm)]
clab[TP:][un]=[f'PCA-{c+1}' for c in np.searchsorted(cuts,thn)%len(cuts)]
clab[TP:][svn]=[f'7d-{c+1}' for c in vm_assign(t1n,t2n,prm)]

def disc(mask):
    d=pd.DataFrame(dict(y=y[mask],g=pid[mask])); ok=d.groupby('g').y.nunique()==2
    return d.g.map(ok).values
def cont(mask,x,nm):
    k=disc(mask); xx=x[mask][k]; z=(xx-xx.mean())/xx.std()
    r=ConditionalLogit(y[mask][k],z[:,None],groups=pid[mask][k]).fit(disp=0)
    b,se=r.params[0],r.bse[0]
    print('    %-30s n=%5d OR/SD=%.3f CI %.2f-%.2f p=%.2e %s'%(nm,k.sum(),np.exp(b),
        np.exp(b-1.96*se),np.exp(b+1.96*se),r.pvalues[0],'SIG' if r.pvalues[0]<.05 else 'ns'))

print('\n=== B1: within-patient escalation on the CORRECT imputation-free subsets ===')
print('  post-test magnitude (mx_a) — paper reports 1.36 full sample:')
for nm,m in [('ALL tests',np.ones(len(y),bool)),('OLD (freq==1.0)',oldmask),('free7 CORRECT',free7),('free28 CORRECT',free28)]:
    cont(m,POST,nm)
print('  pre-test (mx_b) — paper reports 1.15 full sample:')
for nm,m in [('ALL tests',np.ones(len(y),bool)),('OLD (freq==1.0)',oldmask),('free7 CORRECT',free7),('free28 CORRECT',free28)]:
    cont(m,PRE,nm)

print('\n=== B1b: within-patient CLUSTER MEMBERSHIP on free7 ===')
for nm,m in [('ALL tests',np.ones(len(y),bool)),('free7 CORRECT',free7)]:
    k=disc(m); D=pd.get_dummies(pd.Series(clab[m][k]),drop_first=True).astype(float); D=D.loc[:,D.sum()>=10]
    try:
        r=ConditionalLogit(y[m][k],D.values,groups=pid[m][k]).fit(disp=0)
        print('  %-16s n=%5d pat=%4d -> %d/%d cluster contrasts significant'%(nm,k.sum(),len(set(pid[m][k])),int((r.pvalues<.05).sum()),D.shape[1]))
    except Exception as e: print('  ',nm,'failed',e)

print('\n=== B2/B3: escalation -> P/N ordering, WITH p-values, full sample vs imputation-free ===')
for slope_name, SL in [('post-test (mx_a, NOT claimed)', POST), ('pre-test (mx_b, claimed)', PRE)]:
    print('  ordering variable:', slope_name)
    for K in [4,5,6,7,8]:
        p6=vm_fit(t1p,t2p,K)
        for sub_nm, mask in [('full', np.ones(len(y),bool)), ('free7', free7)]:
            lp=vm_assign(t1p,t2p,p6); ln=vm_assign(t1n,t2n,p6)
            lab=np.empty(TP+TN,object); lab[:TP][svp]=lp; lab[TP:][svn]=ln
            sel=mask & np.array([x is not None and not isinstance(x,str) for x in lab])
            TPk=int(y[sel].sum()); TNk=int((y[sel]==0).sum())
            esc=[];pn=[]
            for c in range(K):
                mm_=sel & (lab==c)
                a=int((mm_&(y==1)).sum()); b=int((mm_&(y==0)).sum())
                if a<5 or b<5: continue
                esc.append(SL[mm_].mean()); pn.append((a/TPk)/(b/TNk))
            if len(esc)<3: print('    K=%d %-6s too few clusters'%(K,sub_nm)); continue
            rho,pv=spearmanr(esc,pn)
            print('    K=%d %-6s clusters=%d  Spearman rho=%+.2f  p=%.3f %s'%(K,sub_nm,len(esc),rho,pv,'SIG' if pv<.05 else 'ns'))
