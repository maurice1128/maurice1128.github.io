# -*- coding: utf-8 -*-
"""Step 08 - regenerate cluster labels (deterministic) and produce paper figures
   + a per-cluster table with odds-ratio 95% CIs for the forest plot."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

RNG = 0
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')
OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm')
pos_pd, pos_ds, neg_pd, neg_ds = m2(afn[0]), m2(afn[1]), m2(afn[2]), m2(afn[3])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
Lp, Ln = pos_pd.shape[0], neg_pd.shape[0]
split = lambda pdm: (~(np.abs(np.diff(pdm[:,21:36],axis=1)).sum(1)!=0), (np.abs(np.diff(pdm[:,21:36],axis=1)).sum(1)!=0))

def guarded(X, kmax, lab):
    order=[]
    for k in range(2,kmax+1):
        g=GaussianMixture(k,covariance_type='full',n_init=6,random_state=RNG).fit(X)
        order.append((g.bic(X),k,g,np.bincount(g.predict(X),minlength=k).min()))
    order.sort()
    for bic,k,g,mn in order:
        if mn>=max(20,0.01*len(X)): return g,k
    return order[0][2],order[0][1]

pu_p,sv_p=split(pos_pd); pu_n,sv_n=split(neg_pd)
Xp=np.hstack([pos_pd[pu_p],pos_ds[pu_p]]); mu=Xp.mean(0)
coeff=np.linalg.svd(Xp-mu,full_matrices=False)[2].T
sc_p=(Xp-mu)@coeff; sc_n=(np.hstack([neg_pd[pu_n],neg_ds[pu_n]])-mu)@coeff
gm_pca,k_pca=guarded(sc_p[:,:2],10,'PCA')
emb=lambda d,idx:np.column_stack([np.cos(np.arctan2(d['mn_b'][idx],d['mn_a'][idx])),np.sin(np.arctan2(d['mn_b'][idx],d['mn_a'][idx])),np.cos(np.arctan2(d['mx_b'][idx],d['mx_a'][idx])),np.sin(np.arctan2(d['mx_b'][idx],d['mx_a'][idx]))])
Ep=emb(pos,np.where(sv_p)[0]); En=emb(neg,np.where(sv_n)[0])
gm_7d,k_7d=guarded(Ep,14,'7d')
clab_pos=np.empty(Lp,object); clab_pos[pu_p]=[f'PCA-{c+1}' for c in gm_pca.predict(sc_p[:,:2])]; clab_pos[sv_p]=[f'7d-{c+1}' for c in gm_7d.predict(Ep)]
clab_neg=np.empty(Ln,object); clab_neg[pu_n]=[f'PCA-{c+1}' for c in gm_pca.predict(sc_n[:,:2])]; clab_neg[sv_n]=[f'7d-{c+1}' for c in gm_7d.predict(En)]
outcome=np.r_[np.ones(Lp),np.zeros(Ln)]; clab=np.r_[clab_pos,clab_neg]
dose_all=np.vstack([pos_pd,neg_pd])
clusters=sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1])))

# per-cluster OR + CI
rows=[]
for c in clusters:
    inc=(clab==c).astype(float); X=sm.add_constant(inc)
    res=sm.Logit(outcome,X).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    b,se=res.params[1],res.bse[1]
    posN=int(((clab==c)&(outcome==1)).sum()); negN=int(((clab==c)&(outcome==0)).sum())
    pn=(posN/Lp)/(negN/Ln) if negN>0 else np.nan
    rows.append(dict(cluster=c,posN=posN,negN=negN,PN=pn,OR=np.exp(b),lo=np.exp(b-1.96*se),hi=np.exp(b+1.96*se),p=res.pvalues[1]))
q=multipletests([r['p'] for r in rows],method='fdr_bh')[1]
for r,qq in zip(rows,q): r['q']=qq
import pandas as pd; pd.DataFrame(rows).to_csv(OUT+r'\final_cluster_table.csv',index=False)

# Fig 1: forest plot
fig,ax=plt.subplots(figsize=(7,7))
rows_s=sorted(rows,key=lambda r:r['OR'])
y=np.arange(len(rows_s))
for i,r in enumerate(rows_s):
    col='#c0392b' if (r['PN']>1.2 and r['q']<0.05) else ('#2471a3' if (r['PN']<0.83 and r['q']<0.05) else '#7f8c8d')
    ax.plot([r['lo'],r['hi']],[i,i],color=col,lw=2); ax.plot(r['OR'],i,'o',color=col)
ax.axvline(1,ls='--',color='k',lw=.8); ax.set_yticks(y); ax.set_yticklabels([r['cluster'] for r in rows_s])
ax.set_xscale('log'); ax.set_xlabel('Odds ratio for positive urine (95% CI, patient-clustered)')
ax.set_title('Cluster association with morphine-positive urine'); plt.tight_layout(); fig.savefig(OUT+r'\fig1_forest.png',dpi=130); plt.close()

# Fig 2: mean +/-7d dose trajectory of significant clusters
sig=[r['cluster'] for r in rows if r['q']<0.05 and (r['PN']>1.2 or r['PN']<0.83)]
fig,ax=plt.subplots(figsize=(9,5)); days=np.arange(-7,8)
for c in sig:
    mask=(clab==c); mean=dose_all[mask][:,21:36].mean(0)
    hi=rows[[r['cluster'] for r in rows].index(c)]['PN']>1
    ax.plot(days,mean,lw=2,ls='-' if hi else '--',label=f"{c} (P/N={rows[[r['cluster'] for r in rows].index(c)]['PN']:.2f})")
ax.axvline(0,color='k',lw=.6); ax.set_xlabel('Day relative to urine test'); ax.set_ylabel('Normalized methadone dose (% of day -7)')
ax.set_title('Mean dose trajectory: high-risk (solid) vs safe (dashed) clusters'); ax.legend(fontsize=8,ncol=2); plt.tight_layout(); fig.savefig(OUT+r'\fig2_trajectories.png',dpi=130); plt.close()

# Fig 3: attendance
fig,ax=plt.subplots(figsize=(5,5))
ax.boxplot([att[outcome==1],att[outcome==0]],tick_labels=['Positive','Negative'],showmeans=True)
ax.set_ylabel('Attendance rate (week before test)'); ax.set_title('Attendance vs urine result (p=7e-22)'); plt.tight_layout(); fig.savefig(OUT+r'\fig3_attendance.png',dpi=130); plt.close()

# Fig 4: ROC (pooled out-of-fold)
def feat(pdm,dsm,d,a): return np.hstack([pdm[:,21:36],dsm[:,21:36],np.column_stack([d['mn_a'],d['mn_b'],d['mx_a'],d['mx_b']]),a[:,None]])
Xall=np.nan_to_num(np.vstack([feat(pos_pd,pos_ds,pos,v(cells('freq_All')[0])),feat(neg_pd,neg_ds,neg,v(cells('freq_All')[2]))]))
oof=np.zeros(len(outcome))
for tr,te in GroupKFold(5).split(Xall,outcome,pid):
    sc=StandardScaler().fit(Xall[tr]); m=LogisticRegression(max_iter=1000,class_weight='balanced').fit(sc.transform(Xall[tr]),outcome[tr]); oof[te]=m.predict_proba(sc.transform(Xall[te]))[:,1]
fpr,tpr,_=roc_curve(outcome,oof); auc=roc_auc_score(outcome,oof)
fig,ax=plt.subplots(figsize=(5,5)); ax.plot(fpr,tpr,lw=2,label=f'AUC={auc:.3f}'); ax.plot([0,1],[0,1],'k--',lw=.6)
ax.set_xlabel('1 - specificity'); ax.set_ylabel('Sensitivity'); ax.set_title('Dose-trajectory + attendance (GroupKFold)'); ax.legend(); plt.tight_layout(); fig.savefig(OUT+r'\fig4_roc.png',dpi=130); plt.close()
print('figures saved; significant clusters:',sig,' pooled AUC=%.3f'%auc)
