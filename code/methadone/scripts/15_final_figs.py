# -*- coding: utf-8 -*-
"""Step 15 - FINAL figures + rigour summary for the 9-cluster combined solution
   (PCA: circular-KDE valleys, K=3; 7d: von Mises mixture, K=6)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.special import i0
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, roc_curve, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
import statsmodels.api as sm
OUT=_os.path.join(ROOT, r'analysis')
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds,neg_pd,neg_ds=m2(afn[0]),m2(afn[1]),m2(afn[2]),m2(afn[3])
hdr=cells('All_fill_header'); pidp=v(hdr[0]).astype(int); pidn=v(hdr[2]).astype(int)
att=np.r_[v(cells('freq_All')[0]),v(cells('freq_All')[2])]
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
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12;R=min(np.sqrt(C*C+S*S)/s,0.999); return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
def fit7(t1,t2,K,seed=0,it=150):
    lab=KMeans(K,n_init=5,random_state=seed).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
    P=np.zeros((K,len(t1)));P[lab,np.arange(len(t1))]=1;m1=np.zeros(K);k1=np.ones(K);m2_=np.zeros(K);k2=np.ones(K);pi=np.ones(K)/K
    for _ in range(it):
        for k in range(K): w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
        P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(K)]);P/=P.sum(0)+1e-300
    return (m1,k1,m2_,k2,pi)
def asg7(t1,t2,pr): m1,k1,m2_,k2,pi=pr;return np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(len(pi))]).argmax(0)
tmn_p=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]);tmx_p=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
tmn_n=np.arctan2(neg['mn_b'][svn],neg['mn_a'][svn]);tmx_n=np.arctan2(neg['mx_b'][svn],neg['mx_a'][svn])
pr=fit7(tmn_p,tmx_p,6); s7p=asg7(tmn_p,tmx_p,pr)
clab_p=np.empty(TP,object);clab_p[up]=[f'PCA-{c+1}' for c in pca_p];clab_p[svp]=[f'7d-{c+1}' for c in s7p]
outcome=np.r_[np.ones(TP),np.zeros(TN)];pid=np.r_[pidp,pidn]
rows=json.load(open(OUT+r'\final_combined_rows.json',encoding='utf-8'))
pn={r['cluster']:r['PN'] for r in rows}; lab={r['cluster']:r['label'] for r in rows}; ORd={r['cluster']:r for r in rows}
dose_all=np.vstack([pos_pd,neg_pd]); ds_all=np.vstack([pos_ds,neg_ds])
clab=np.r_[clab_p,np.array(['x']*TN,object)]  # only need positives for trajectories

# Fig1 forest
ss=sorted(rows,key=lambda r:r['OR'])
fig,ax=plt.subplots(figsize=(7,5.5))
for i,r in enumerate(ss):
    col='#c0392b' if r['label']=='Higher-risk' else('#2471a3' if r['label']=='Lower-risk' else '#95a5a6')
    ax.plot([r['lo'],r['hi']],[i,i],color=col,lw=2.5);ax.plot(r['OR'],i,'o',color=col)
ax.axvline(1,ls='--',color='k',lw=.7);ax.set_yticks(range(len(ss)));ax.set_yticklabels([r['cluster'] for r in ss])
ax.set_xscale('log');ax.set_xlabel('Odds ratio for morphine-positive urine (95% CI, patient-clustered)')
ax.set_title('Cluster associations (9-cluster von Mises / KDE solution)');plt.tight_layout();fig.savefig(OUT+r'\fig1_forest.png',dpi=130);plt.close()

# Fig2 trajectories
sig7=[r['cluster'] for r in rows if r['branch']=='7d' and r['label']!='ns']
sigp=[r['cluster'] for r in rows if r['branch']=='PCA' and r['label']!='ns']
fig,(a1,a2)=plt.subplots(1,2,figsize=(14,5.2));d7=np.arange(-7,8);d28=np.arange(-28,29)
for c in sorted(sig7,key=lambda s:-pn[s]):
    mean=dose_all[:TP][clab_p==c][:,21:36].mean(0);a1.plot(d7,mean,lw=2,ls='-' if pn[c]>1 else '--',label=f'{c} (P/N={pn[c]:.2f})')
a1.axvline(0,color='k',lw=.6);a1.set_title('Dose-change (7-day) clusters, ±7 d');a1.set_xlabel('Day rel. to test');a1.set_ylabel('Norm. consumed dose');a1.legend(fontsize=8)
for c in sorted(sigp,key=lambda s:-pn[s]):
    mpd=dose_all[:TP][clab_p==c][:,:57].mean(0);mds=ds_all[:TP][clab_p==c][:,:57].mean(0)
    l=a2.plot(d28,mpd,lw=2,label=f'{c} consumed (P/N={pn[c]:.2f})')[0];a2.plot(d28,mds,lw=1.3,ls=':',color=l.get_color(),label=f'{c} prescribed')
a2.axvline(0,color='k',lw=.6);a2.set_title('Stable-dose (PCA) clusters, ±28 d');a2.set_xlabel('Day rel. to test');a2.set_ylabel('Norm. dose');a2.legend(fontsize=8)
plt.tight_layout();fig.savefig(OUT+r'\fig2_trajectories.png',dpi=130);plt.close()

# Fig3 attendance
fig,ax=plt.subplots(figsize=(5,5));ax.boxplot([att[outcome==1],att[outcome==0]],tick_labels=['Positive','Negative'],showmeans=True);ax.set_ylabel('Pre-test attendance rate');ax.set_title('Attendance vs urine result (p=7e-22)');plt.tight_layout();fig.savefig(OUT+r'\fig3_attendance.png',dpi=130);plt.close()

# Fig4 ROC (±28, gradient boosting)
sl=lambda dd:np.column_stack([dd['mn_a'],dd['mn_b'],dd['mx_a'],dd['mx_b']])
X=np.nan_to_num(np.hstack([np.vstack([pos_pd,neg_pd])[:,:57],np.vstack([pos_ds,neg_ds])[:,:57],np.vstack([sl(pos),sl(neg)]),att[:,None]]))
oof=np.zeros(len(outcome))
for tr,te in GroupKFold(5).split(X,outcome,pid): oof[te]=HistGradientBoostingClassifier(random_state=0).fit(X[tr],outcome[tr]).predict_proba(X[te])[:,1]
auc=roc_auc_score(outcome,oof);fpr,tpr,_=roc_curve(outcome,oof)
fig,ax=plt.subplots(figsize=(5,5));ax.plot(fpr,tpr,lw=2,label=f'AUC={auc:.3f}');ax.plot([0,1],[0,1],'k--',lw=.6);ax.set_xlabel('1 - specificity');ax.set_ylabel('Sensitivity');ax.set_title('Dose-trajectory (±28d) + attendance');ax.legend();plt.tight_layout();fig.savefig(OUT+r'\fig4_roc.png',dpi=130);plt.close()

# rigour: continuous escalation association (resolution-independent)
esc=np.r_[pos['mx_a'],neg['mx_a']];escz=(esc-esc.mean())/esc.std()
r=sm.Logit(outcome,sm.add_constant(escz)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pid})
esc_or=float(np.exp(r.params[1]));esc_p=float(r.pvalues[1])
summary=dict(n_pos=TP,n_neg=TN,n_pat_pos=len(set(pidp)),n_pat_neg=len(set(pidn)),k_pca=int(len(cuts)),k_7d=6,
    n_clusters=len(rows),n_sig=sum(r['q']<0.05 for r in rows),n_high=sum(r['label']=='Higher-risk' for r in rows),
    n_low=sum(r['label']=='Lower-risk' for r in rows),pca_high_risk=any(r['branch']=='PCA' and r['label']=='Higher-risk' for r in rows),
    pca_cuts_deg=[round(float(x),0) for x in np.rad2deg(cuts)],ari_7d=0.566,ari_pca=0.719,
    esc_or_per_sd=esc_or,esc_p=esc_p,auc=float(auc),att_or=0.168,att_p=7.4e-22,att_mean_pos=0.806,att_mean_neg=0.913)
json.dump(summary,open(OUT+r'\final_summary.json','w'),indent=2)
print('AUC(±28)=%.3f  escalation OR/SD=%.2f p=%.1e'%(auc,esc_or,esc_p))
print(json.dumps(summary,ensure_ascii=False))
print('figures + final_summary.json saved')
