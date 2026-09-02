# -*- coding: utf-8 -*-
"""Step 12 - FINAL analysis with corrected CIRCULAR clustering. Produces the
   table (OR+CI+FDR), bootstrap stability, and all figures for the paper."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, roc_curve, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
RNG=0; OUT=_os.path.join(ROOT, r'analysis')
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
att=np.r_[v(cells('freq_All')[0]),v(cells('freq_All')[2])]
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0])); neg=dict(mn_a=v(sa[2]),mn_b=v(sb[2]),mx_a=v(xa[2]),mx_b=v(xb[2]))
TP,TN=3401,6499
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); un=~(np.abs(np.diff(neg_pd[:,21:36],axis=1)).sum(1)!=0)
svp=~up; svn=~un

# ---- PCA branch: circular KDE valleys (kappa=12) ----
proj=lambda pd_,ds_,mk:(np.hstack([pd_[mk],ds_[mk]])-mu)@coeff.T
sp=proj(pos_pd,pos_ds,up); sn=proj(neg_pd,neg_ds,un)
thp=np.arctan2(sp[:,1]-0.0270,sp[:,0]+0.04)%(2*np.pi); thn=np.arctan2(sn[:,1]-0.0270,sn[:,0]+0.04)%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]
d=np.array([np.exp(12*np.cos(g-thp)).sum() for g in grid])
cuts=np.sort(grid[[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]])
pca_p=np.searchsorted(cuts,thp)%len(cuts); pca_n=np.searchsorted(cuts,thn)%len(cuts)

# ---- 7d branch: von Mises mixture, ICL ----
emb=lambda d,mk:np.column_stack([np.cos(np.arctan2(d['mn_b'][mk],d['mn_a'][mk])),np.sin(np.arctan2(d['mn_b'][mk],d['mn_a'][mk])),np.cos(np.arctan2(d['mx_b'][mk],d['mx_a'][mk])),np.sin(np.arctan2(d['mx_b'][mk],d['mx_a'][mk]))])
Ep=emb(pos,svp); En=emb(neg,svn)
def icl(g,X): gm=np.clip(g.predict_proba(X),1e-12,1); return g.bic(X)+2*(-(gm*np.log(gm)).sum())
best=None
for k in range(6,20):
    g=GaussianMixture(k,covariance_type='full',n_init=4,random_state=RNG).fit(Ep)
    if np.bincount(g.predict(Ep),minlength=k).min()<20: continue
    ic=icl(g,Ep); best=(ic,k,g) if best is None or ic<best[0] else best
_,k7,g7=best; sev_p=g7.predict(Ep); sev_n=g7.predict(En)

# bootstrap ARI (7d)
rs=np.random.RandomState(RNG); aris=[]
for _ in range(25):
    idx=rs.choice(len(Ep),len(Ep),replace=True)
    aris.append(adjusted_rand_score(sev_p,GaussianMixture(k7,covariance_type='full',n_init=2,random_state=RNG).fit(Ep[idx]).predict(Ep)))
stab=float(np.mean(aris))

# ---- assemble labels over ALL tests ----
clab_p=np.empty(TP,object); clab_p[up]=[f'PCA-{c+1}' for c in pca_p]; clab_p[svp]=[f'7d-{c+1}' for c in sev_p]
clab_n=np.empty(TN,object); clab_n[un]=[f'PCA-{c+1}' for c in pca_n]; clab_n[svn]=[f'7d-{c+1}' for c in sev_n]
outcome=np.r_[np.ones(TP),np.zeros(TN)]; clab=np.r_[clab_p,clab_n]; pid=np.r_[pidp,pidn]
clusters=sorted(set(clab),key=lambda s:(s.split('-')[0],int(s.split('-')[1])))
rows=[]
for c in clusters:
    inc=(clab==c).astype(float)
    res=sm.Logit(outcome,sm.add_constant(inc)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
    b,se=res.params[1],res.bse[1]; posN=int(((clab==c)&(outcome==1)).sum()); negN=int(((clab==c)&(outcome==0)).sum())
    pn=(posN/TP)/(negN/TN) if negN else np.nan
    rows.append(dict(cluster=c,branch=c.split('-')[0],posN=posN,negN=negN,PN=pn,OR=float(np.exp(b)),lo=float(np.exp(b-1.96*se)),hi=float(np.exp(b+1.96*se)),p=float(res.pvalues[1])))
qv=multipletests([r['p'] for r in rows],method='fdr_bh')[1]
for r,q in zip(rows,qv): r['q']=float(q); r['label']=('Higher-risk' if r['PN']>1.2 and q<0.05 else ('Lower-risk' if r['PN']<0.83 and q<0.05 else 'ns'))
nsig=sum(1 for r in rows if r['q']<0.05)
pd.DataFrame(rows).to_csv(OUT+r'\final_circular_table.csv',index=False)

# ---- prediction (unchanged features; for completeness) ----
feat=lambda pdm,dsm,d,a:np.hstack([pdm[:,21:36],dsm[:,21:36],np.column_stack([d['mn_a'],d['mn_b'],d['mx_a'],d['mx_b']]),a[:,None]])
X=np.nan_to_num(np.vstack([feat(pos_pd,pos_ds,pos,att[:TP]),feat(neg_pd,neg_ds,neg,att[TP:])]))
oof=np.zeros(len(outcome))
for tr,te in GroupKFold(5).split(X,outcome,pid):
    sc=StandardScaler().fit(X[tr]); oof[te]=LogisticRegression(max_iter=1000,class_weight='balanced').fit(sc.transform(X[tr]),outcome[tr]).predict_proba(sc.transform(X[te]))[:,1]
auc=roc_auc_score(outcome,oof)

summary=dict(n_pos=TP,n_neg=TN,n_pat_pos=len(set(pidp)),n_pat_neg=len(set(pidn)),
    k_pca=len(cuts),k_7d=int(k7),n_clusters=len(clusters),n_sig=nsig,stability_ari=stab,
    pca_cuts_deg=[round(float(x),0) for x in np.rad2deg(cuts)],auc=float(auc),
    att_or=0.168,att_p=7.4e-22,att_mean_pos=0.806,att_mean_neg=0.913)
json.dump(dict(summary=summary,clusters=rows),open(OUT+r'\final_circular_summary.json','w'),indent=2)

# ---- figures ----
dose_all=np.vstack([pos_pd,neg_pd]); ds_all=np.vstack([pos_ds,neg_ds])
sig=[r for r in rows if r['q']<0.05 and r['label']!='ns']
# Fig1 forest
fig,ax=plt.subplots(figsize=(7,8)); ss=sorted(rows,key=lambda r:r['OR'])
for i,r in enumerate(ss):
    col='#c0392b' if r['label']=='Higher-risk' else ('#2471a3' if r['label']=='Lower-risk' else '#95a5a6')
    ax.plot([r['lo'],r['hi']],[i,i],color=col,lw=2); ax.plot(r['OR'],i,'o',color=col)
ax.axvline(1,ls='--',color='k',lw=.7); ax.set_yticks(range(len(ss))); ax.set_yticklabels([r['cluster'] for r in ss],fontsize=8)
ax.set_xscale('log'); ax.set_xlabel('Odds ratio for morphine-positive urine (95% CI, patient-clustered)')
ax.set_title('Cluster associations (circular clustering)'); plt.tight_layout(); fig.savefig(OUT+r'\fig1_forest.png',dpi=130); plt.close()
# Fig2 trajectories
sig7=[r['cluster'] for r in sig if r['branch']=='7d']; sigp=[r['cluster'] for r in sig if r['branch']=='PCA']
pnmap={r['cluster']:r['PN'] for r in rows}
fig,(a1,a2)=plt.subplots(1,2,figsize=(14,5.2)); d7=np.arange(-7,8); d28=np.arange(-28,29)
for c in sorted(sig7,key=lambda s:-pnmap[s]):
    mean=dose_all[clab==c][:,21:36].mean(0); a1.plot(d7,mean,lw=2,ls='-' if pnmap[c]>1 else '--',label=f'{c} (P/N={pnmap[c]:.2f})')
a1.axvline(0,color='k',lw=.6); a1.set_title('Dose-change (7-day) clusters, ±7 d'); a1.set_xlabel('Day rel. to test'); a1.set_ylabel('Norm. prescription dose'); a1.legend(fontsize=7,ncol=2)
for c in sorted(sigp,key=lambda s:-pnmap[s]):
    mpd=dose_all[clab==c][:,:57].mean(0); mds=ds_all[clab==c][:,:57].mean(0)
    l=a2.plot(d28,mpd,lw=2,label=f'{c} presc (P/N={pnmap[c]:.2f})')[0]; a2.plot(d28,mds,lw=1.3,ls=':',color=l.get_color(),label=f'{c} taken')
a2.axvline(0,color='k',lw=.6); a2.set_title('Stable-dose (PCA) clusters, ±28 d'); a2.set_xlabel('Day rel. to test'); a2.set_ylabel('Norm. dose'); a2.legend(fontsize=7)
plt.tight_layout(); fig.savefig(OUT+r'\fig2_trajectories.png',dpi=130); plt.close()
# Fig3 attendance, Fig4 ROC
fig,ax=plt.subplots(figsize=(5,5)); ax.boxplot([att[outcome==1],att[outcome==0]],tick_labels=['Positive','Negative'],showmeans=True); ax.set_ylabel('Pre-test attendance rate'); ax.set_title('Attendance vs urine result (p=7e-22)'); plt.tight_layout(); fig.savefig(OUT+r'\fig3_attendance.png',dpi=130); plt.close()
fpr,tpr,_=roc_curve(outcome,oof); fig,ax=plt.subplots(figsize=(5,5)); ax.plot(fpr,tpr,lw=2,label=f'AUC={auc:.3f}'); ax.plot([0,1],[0,1],'k--',lw=.6); ax.set_xlabel('1 - specificity'); ax.set_ylabel('Sensitivity'); ax.set_title('Dose-trajectory + attendance (GroupKFold)'); ax.legend(); plt.tight_layout(); fig.savefig(OUT+r'\fig4_roc.png',dpi=130); plt.close()

print('FINAL:',json.dumps(summary,ensure_ascii=False))
print('significant clusters:',[(r['cluster'],round(r['PN'],2),r['label']) for r in sig])
PY = None
