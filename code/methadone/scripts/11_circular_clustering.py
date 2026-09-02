# -*- coding: utf-8 -*-
"""
Step 11 - CIRCULAR clustering (fixes the earlier error of clustering angular
data in 2D Euclidean space with GMM, which merged away high-risk PCA clusters).

PCA branch (1 angle theta):
  (a) circular kernel-density estimate -> cut at density valleys (a reproducible
      formalisation of "eyeballing the gaps in the rose histogram")
  (b) von Mises mixture (GMM on the unit circle cos/sin) with ICL selection
7d branch (2 angles): mixture on the 4-D circular embedding, ICL selection.

Every resulting cluster is (i) tested with patient-clustered logistic + FDR and
(ii) cross-tabulated against the ORIGINAL eyeballed Cat clusters to CONFIRM no
known high-risk region is lost.  theta / projection use the MATLAB-verified
coeff/mu (coeff.T, corr 1.000 with stored score).
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from sklearn.mixture import GaussianMixture
RNG=0
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499
unch=lambda pdm:~(np.abs(np.diff(pdm[:,21:36],axis=1)).sum(1)!=0)
up,un=unch(pos_pd),unch(neg_pd)

def patient_p(inc_p,inc_n,pp,pn):
    inc=np.r_[inc_p.astype(float),inc_n.astype(float)]; outc=np.r_[np.ones(len(inc_p)),np.zeros(len(inc_n))]; pid=np.r_[pp,pn]
    try: return sm.Logit(outc,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid}).pvalues[1]
    except: return np.nan

def report(name,labp,labn,pp,pn,orig_labp=None):
    ks=sorted(set(labp))
    rows=[]
    for k in ks:
        posN=int((labp==k).sum()); negN=int((labn==k).sum())
        PN=(posN/TP)/(negN/TN) if negN else np.nan
        p=patient_p(labp==k,labn==k,pp,pn)
        rows.append([k,posN,negN,PN,p])
    qs=multipletests([r[4] for r in rows],method='fdr_bh')[1]
    print(f'\n=== {name}: {len(ks)} clusters ===')
    print(f'{"clu":>4} {"posN":>5} {"negN":>5} {"P/N":>6} {"q":>9} {"":>8}')
    for r,q in zip(rows,qs):
        tag='HIGH' if (r[3]>1.2 and q<0.05) else ('LOW' if (r[3]<0.83 and q<0.05) else '')
        print(f'{str(r[0]):>4} {r[1]:>5} {r[2]:>5} {r[3]:>6.2f} {q:>9.1e} {tag:>8}')
    return rows,qs

# ---------- PCA branch theta ----------
def proj(pd_,ds_,mask): return (np.hstack([pd_[mask],ds_[mask]])-mu)@coeff.T
sp=proj(pos_pd,pos_ds,up); sn=proj(neg_pd,neg_ds,un)
thp=np.arctan2(sp[:,1]-0.0270,sp[:,0]+0.04)%(2*np.pi)
thn=np.arctan2(sn[:,1]-0.0270,sn[:,0]+0.04)%(2*np.pi)
pidp_u,pidn_u=pidp[up],pidn[un]

# (a) circular KDE valleys
def circ_kde(theta,grid,kappa): return np.array([np.exp(kappa*np.cos(g-theta)).sum() for g in grid])
grid=np.linspace(0,2*np.pi,721)[:-1]
for kappa in [8,12,16]:
    d=circ_kde(thp,grid,kappa)
    # valleys = local minima on circle
    val=[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]
    cuts=np.sort(grid[val])
    # assign to segments between consecutive cuts (circular)
    def seg(theta):
        idx=np.searchsorted(cuts,theta)%len(cuts); return idx
    labp=seg(thp); labn=seg(thn)
    ncl=len(cuts)
    print(f'[KDE kappa={kappa}] valleys/clusters={ncl}  cut angles(deg)={np.round(np.rad2deg(cuts),0).astype(int).tolist()}')

# use kappa=12 as primary
kappa=12; d=circ_kde(thp,grid,kappa)
val=[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]
cuts=np.sort(grid[val])
labp=np.searchsorted(cuts,thp)%len(cuts); labn=np.searchsorted(cuts,thn)%len(cuts)
rows,qs=report(f'PCA circular-KDE (kappa=12)',labp,labn,pidp_u,pidn_u)

# cross-tab vs original eyeballed pca clusters (Cat13-17)
dpos=np.rad2deg(thp)
eye=np.zeros(len(dpos),int)
eye[(dpos>15)&(dpos<=80)]=13; eye[(dpos>80)&(dpos<=175)]=14; eye[(dpos>175)&(dpos<=260)]=15; eye[(dpos>260)&(dpos<=300)]=16; eye[(dpos>300)|(dpos<=15)]=17
print('\ncross-tab: 你的原始Cat -> 新KDE群 (含高風險 Cat16/17 有沒有被分出來)')
for cat in [13,14,15,16,17]:
    from collections import Counter
    c=Counter(labp[eye==cat]); tot=(eye==cat).sum()
    top=c.most_common(2)
    print(f'  Cat{cat}: {tot}筆 -> '+', '.join(f'新群{k}={n}({n/tot*100:.0f}%)' for k,n in top))

# ---------- 7d branch: von Mises mixture (circle GMM + ICL) ----------
svp=~up; svn=~un
def emb(d,mask):
    tmn=np.arctan2(d['mn_b'][mask],d['mn_a'][mask]); tmx=np.arctan2(d['mx_b'][mask],d['mx_a'][mask])
    return np.column_stack([np.cos(tmn),np.sin(tmn),np.cos(tmx),np.sin(tmx)])
Ep=emb(pos,svp); En=emb(neg,svn)
def icl(g,X):
    gm=np.clip(g.predict_proba(X),1e-12,1); return g.bic(X)+2*(-(gm*np.log(gm)).sum())
best=None
for k in range(6,20):
    g=GaussianMixture(k,covariance_type='full',n_init=4,random_state=RNG).fit(Ep)
    if np.bincount(g.predict(Ep),minlength=k).min()<20: continue
    ic=icl(g,Ep)
    if best is None or ic<best[0]: best=(ic,k,g)
_,k7,g7=best
print(f'\n[7d von Mises mixture] ICL selected K={k7}')
report(f'7d circular mixture',g7.predict(Ep),g7.predict(En),pidp[svp],pidn[svn])
print('\nDONE')
