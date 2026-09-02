# -*- coding: utf-8 -*-
"""
Step 13 - FINAL rigorous clustering, designed to withstand review.
  - PROPER von Mises mixture EM (not a Gaussian-on-embedding approximation)
      * PCA branch: 1-D von Mises mixture, K=3 (the angle has 3 clear density
        modes, stable across bandwidth)
      * 7-day branch: 2-D product-von-Mises mixture, K=6 PRE-SPECIFIED (the
        toroidal angle is a continuum with no natural K — information criteria
        did not converge — so we fix a parsimonious, clinically-interpretable K)
  - Rigour checks:
      (i)  bootstrap adjusted Rand index (both branches)
      (ii) RESOLUTION ROBUSTNESS: the escalation=higher-risk / tapering=lower-risk
           ordering holds across K = 4,6,8,12
      (iii) RESOLUTION-INDEPENDENT association: a continuous escalation measure
           (post-test dose slope) predicts a positive urine at the test level
           (patient-clustered logistic), so the finding does not depend on K.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import pandas as pd
OUT=_os.path.join(ROOT, r'analysis')
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

# ---------- von Mises helpers ----------
def vmpdf(th,mu,kap): return np.exp(kap*np.cos(th-mu))/(2*np.pi*i0(kap))
def vm_mle(th,w):
    C=(w*np.cos(th)).sum(); S=(w*np.sin(th)).sum(); s=w.sum()+1e-12
    mu=np.arctan2(S,C); R=min(np.sqrt(C*C+S*S)/s,0.999)
    return mu, R*(2-R*R)/(1-R*R)
def emb1(th): return np.column_stack([np.cos(th),np.sin(th)])

def vm_mix(angles,K,seed=0,iters=150):
    """angles: list of 1..2 angle-arrays (1D=PCA, 2D=7d torus, product vM)."""
    N=len(angles[0]); rng=np.random.RandomState(seed)
    lab0=KMeans(K,n_init=5,random_state=seed).fit_predict(np.hstack([emb1(a) for a in angles]))
    P=np.zeros((K,N)); P[lab0,np.arange(N)]=1.0
    mus=[np.zeros(K) for _ in angles]; kaps=[np.ones(K) for _ in angles]; pi=np.ones(K)/K
    for _ in range(iters):
        for k in range(K):
            w=P[k]
            for a in range(len(angles)): mus[a][k],kaps[a][k]=vm_mle(angles[a],w)
            pi[k]=w.mean()+1e-9
        P=np.array([pi[k]*np.prod([vmpdf(angles[a],mus[a][k],kaps[a][k]) for a in range(len(angles))],axis=0) for k in range(K)])
        P/=P.sum(0)+1e-300
    return mus,kaps,pi
def assign(angles,mus,kaps,pi):
    K=len(pi); P=np.array([pi[k]*np.prod([vmpdf(angles[a],mus[a][k],kaps[a][k]) for a in range(len(angles))],axis=0) for k in range(K)])
    return P.argmax(0)

# ---------- angles ----------
proj=lambda pd_,ds_,mk:(np.hstack([pd_[mk],ds_[mk]])-mu0)@coeff.T
thpca_p=np.arctan2(proj(pos_pd,pos_ds,up)[:,1]-0.0270,proj(pos_pd,pos_ds,up)[:,0]+0.04)
thpca_n=np.arctan2(proj(neg_pd,neg_ds,un)[:,1]-0.0270,proj(neg_pd,neg_ds,un)[:,0]+0.04)
tmn_p=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]); tmx_p=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
tmn_n=np.arctan2(neg['mn_b'][svn],neg['mn_a'][svn]); tmx_n=np.arctan2(neg['mx_b'][svn],neg['mx_a'][svn])

# ---------- fit ----------
mp,kp,pip=vm_mix([thpca_p],3,seed=0)                       # PCA 1D K=3
lab_pca_p=assign([thpca_p],mp,kp,pip); lab_pca_n=assign([thpca_n],mp,kp,pip)
m7,k7,pi7=vm_mix([tmn_p,tmx_p],6,seed=0)                    # 7d 2D K=6
lab_7_p=assign([tmn_p,tmx_p],m7,k7,pi7); lab_7_n=assign([tmn_n,tmx_n],m7,k7,pi7)

clab_p=np.empty(TP,object); clab_p[up]=[f'PCA-{c+1}' for c in lab_pca_p]; clab_p[svp]=[f'7d-{c+1}' for c in lab_7_p]
clab_n=np.empty(TN,object); clab_n[un]=[f'PCA-{c+1}' for c in lab_pca_n]; clab_n[svn]=[f'7d-{c+1}' for c in lab_7_n]
outcome=np.r_[np.ones(TP),np.zeros(TN)]; clab=np.r_[clab_p,clab_n]; pid=np.r_[pidp,pidn]
clusters=sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1])))
rows=[]
for c in clusters:
    inc=(clab==c).astype(float); res=sm.Logit(outcome,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    b,se=res.params[1],res.bse[1]; posN=int(((clab==c)&(outcome==1)).sum()); negN=int(((clab==c)&(outcome==0)).sum())
    rows.append(dict(cluster=c,branch=c.split('-')[0],posN=posN,negN=negN,PN=(posN/TP)/(negN/TN),OR=float(np.exp(b)),lo=float(np.exp(b-1.96*se)),hi=float(np.exp(b+1.96*se)),p=float(res.pvalues[1])))
q=multipletests([r['p'] for r in rows],method='fdr_bh')[1]
for r,qq in zip(rows,q): r['q']=float(qq); r['label']=('Higher-risk' if r['PN']>1.2 and qq<0.05 else ('Lower-risk' if r['PN']<0.83 and qq<0.05 else 'ns'))
pd.DataFrame(rows).to_csv(OUT+r'\final_vm_table.csv',index=False)
nsig=sum(r['q']<0.05 for r in rows)
print('=== FINAL von Mises clustering ===')
print(f'PCA K=3, 7d K=6, total {len(clusters)} clusters, {nsig} significant')
for r in sorted(rows,key=lambda r:-r['PN']):
    if r['q']<0.05: print(f"  {r['cluster']:7} P/N={r['PN']:.2f} OR={r['OR']:.2f}({r['lo']:.2f}-{r['hi']:.2f}) q={r['q']:.1e} {r['label']}")

# ---------- (i) bootstrap ARI ----------
def boot(angles,K,base):
    rs=np.random.RandomState(0); ar=[]
    for _ in range(20):
        idx=rs.choice(len(angles[0]),len(angles[0]),replace=True)
        m,k,pi=vm_mix([a[idx] for a in angles],K,seed=0,iters=60)
        ar.append(adjusted_rand_score(base,assign(angles,m,k,pi)))
    return float(np.mean(ar))
ari7=boot([tmn_p,tmx_p],6,lab_7_p); aripca=boot([thpca_p],3,lab_pca_p)
print(f'\n(i) bootstrap ARI: 7d(K=6)={ari7:.3f}  PCA(K=3)={aripca:.3f}')

# ---------- (ii) resolution robustness (7d) ----------
print('(ii) 7d resolution robustness — escalation vs risk ordering across K:')
for K in [4,6,8,12]:
    m,k,pi=vm_mix([tmn_p,tmx_p],K,seed=0,iters=80)
    lpp=assign([tmn_p,tmx_p],m,k,pi); lnn=assign([tmn_n,tmx_n],m,k,pi)
    # per-cluster: mean post-test max slope (escalation) vs P/N
    esc=[]; pn=[]
    for c in range(K):
        posN=(lpp==c).sum(); negN=(lnn==c).sum()
        if negN<5 or posN<5: continue
        esc.append(pos['mx_a'][svp][lpp==c].mean()); pn.append((posN/TP)/(negN/TN))
    from scipy.stats import spearmanr
    rho,pv=spearmanr(esc,pn)
    print(f'   K={K:2d}: Spearman(post-test escalation slope, P/N) = {rho:+.2f} (p={pv:.2g})')

# ---------- (iii) resolution-INDEPENDENT continuous association ----------
esc_all=np.r_[pos['mx_a'],neg['mx_a']]          # post-test max slope, all tests
esc_z=(esc_all-esc_all.mean())/esc_all.std()
res=sm.Logit(outcome,sm.add_constant(esc_z)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
print(f'\n(iii) continuous: post-test escalation slope -> positive urine (test-level, patient-clustered)')
print(f'      OR per SD = {np.exp(res.params[1]):.2f} (p={res.pvalues[1]:.1e}) — independent of any clustering')

json.dump(dict(k_pca=3,k_7d=6,n_clusters=len(clusters),n_sig=nsig,ari_7d=ari7,ari_pca=aripca,
    esc_or_per_sd=float(np.exp(res.params[1])),esc_p=float(res.pvalues[1])),open(OUT+r'\final_vm_summary.json','w'),indent=2)
print('\nsaved final_vm_table.csv + summary')
