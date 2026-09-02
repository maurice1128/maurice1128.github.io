# -*- coding: utf-8 -*-
"""Step 10 - corrected Figure 2:
   - 7d (dose-change) clusters shown over +/-7 days (their defining window)
   - PCA (stable-dose) clusters shown over the FULL +/-28 days, BOTH signals
     (prescription + taken), matching the original MATLAB plotting.
   Uses the PRIMARY single-signal (prescription) clustering (stable, ARI 0.80)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture

RNG = 0
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm')
pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
Lp = pos_pd.shape[0]
split = lambda pdm: (~(np.abs(np.diff(pdm[:,21:36],axis=1)).sum(1)!=0), (np.abs(np.diff(pdm[:,21:36],axis=1)).sum(1)!=0))
def guarded(X, kmax):
    order=[]
    for k in range(2,kmax+1):
        g=GaussianMixture(k,covariance_type='full',n_init=6,random_state=RNG).fit(X)
        order.append((g.bic(X),k,g,np.bincount(g.predict(X),minlength=k).min()))
    order.sort()
    for bic,k,g,mn in order:
        if mn>=max(20,0.01*len(X)): return g,k
    return order[0][2],order[0][1]
pu,sv=split(pos_pd)
Xp=np.hstack([pos_pd[pu],pos_ds[pu]]); mu=Xp.mean(0); coeff=np.linalg.svd(Xp-mu,full_matrices=False)[2].T
gm_pca,_=guarded(((Xp-mu)@coeff)[:,:2],10)
emb=lambda idx:np.column_stack([np.cos(np.arctan2(pos['mn_b'][idx],pos['mn_a'][idx])),np.sin(np.arctan2(pos['mn_b'][idx],pos['mn_a'][idx])),np.cos(np.arctan2(pos['mx_b'][idx],pos['mx_a'][idx])),np.sin(np.arctan2(pos['mx_b'][idx],pos['mx_a'][idx]))])
Ep=emb(np.where(sv)[0]); gm_7d,_=guarded(Ep,14)
clab=np.empty(Lp,object); clab[pu]=[f'PCA-{c+1}' for c in gm_pca.predict(((Xp-mu)@coeff)[:,:2])]; clab[sv]=[f'7d-{c+1}' for c in gm_7d.predict(Ep)]

# significant clusters from the primary run (07)
import json
res=json.load(open(OUT+r'\results_summary.json'))
pn={r['cluster']:r['PN'] for r in res['clusters']}
sig7d=[c for c in set(clab) if c.startswith('7d-') and pn.get(c,1) and (pn[c]>1.2 or pn[c]<0.83) and c in pn]
# use FDR from json
q={r['cluster']:r['p_fdr'] for r in res['clusters']}
sig7d=[c for c in sorted(set(clab)) if c.startswith('7d-') and q.get(c,1)<0.05 and (pn[c]>1.2 or pn[c]<0.83)]
sigpca=[c for c in sorted(set(clab)) if c.startswith('PCA-') and q.get(c,1)<0.05]

days28=np.arange(-28,29); days7=np.arange(-7,8)
fig,(a1,a2)=plt.subplots(1,2,figsize=(14,5.2))
# panel A: 7d clusters +/-7 (prescription)
for c in sorted(sig7d,key=lambda s:-pn[s]):
    mean=pos_pd[clab==c][:,21:36].mean(0); hi=pn[c]>1
    a1.plot(days7,mean,lw=2,ls='-' if hi else '--',label=f'{c} (P/N={pn[c]:.2f})')
a1.axvline(0,color='k',lw=.6); a1.set_xlabel('Day relative to urine test'); a1.set_ylabel('Normalized prescription dose (% of day -7)')
a1.set_title('Dose-change clusters (±7 d): higher-risk solid, lower-risk dashed'); a1.legend(fontsize=8,ncol=2)
# panel B: PCA clusters +/-28 both signals
for c in sorted(sigpca,key=lambda s:-pn[s]):
    mpd=pos_pd[clab==c][:,:57].mean(0); mds=pos_ds[clab==c][:,:57].mean(0)
    l=a2.plot(days28,mpd,lw=2,label=f'{c} presc (P/N={pn[c]:.2f})')[0]
    a2.plot(days28,mds,lw=1.4,ls=':',color=l.get_color(),label=f'{c} taken')
a2.axvline(0,color='k',lw=.6); a2.set_xlabel('Day relative to urine test'); a2.set_ylabel('Normalized dose')
a2.set_title('Stable-dose (PCA) clusters (±28 d): prescription solid, taken dotted'); a2.legend(fontsize=7,ncol=2)
plt.tight_layout(); fig.savefig(OUT+r'\fig2_trajectories.png',dpi=130); plt.close()
print('fixed Figure 2. sig 7d:',sig7d,' sig PCA:',sigpca)
