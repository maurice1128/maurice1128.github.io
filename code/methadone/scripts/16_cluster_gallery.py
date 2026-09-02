# -*- coding: utf-8 -*-
"""Step 16 - cluster gallery: one panel per cluster (9 panels), assembled into a
   single large figure for the paper. 7d clusters show the ±7-day prescription
   trajectory; PCA clusters show the ±28-day prescription (solid) + taken (dotted)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.special import i0
from sklearn.cluster import KMeans
OUT=_os.path.join(ROOT, r'analysis')
f=h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'),'r')
cells=lambda n:[np.array(f[r]) for r in np.array(f[n]).ravel()]; m2=lambda a:(a.T if a.shape[0]==57 else a); v=lambda a:np.array(a).ravel()
coeff=np.array(f['coeff']); mu0=v(f['mu'])
afn=cells('All_fill_norm'); pos_pd,pos_ds=m2(afn[0]),m2(afn[1])
sa,sb,xa,xb=cells('slope_burst_min_7da'),cells('slope_burst_min_7db'),cells('slope_burst_max_7da'),cells('slope_burst_max_7db')
pos=dict(mn_a=v(sa[0]),mn_b=v(sb[0]),mx_a=v(xa[0]),mx_b=v(xb[0]))
TP=3401
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
proj=(np.hstack([pos_pd[up],pos_ds[up]])-mu0)@coeff.T
thp=np.arctan2(proj[:,1]-0.0270,proj[:,0]+0.04)%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]; d=np.array([np.exp(12*np.cos(g-thp)).sum() for g in grid])
cuts=np.sort(grid[[i for i in range(len(d)) if d[i]<d[(i-1)%len(d)] and d[i]<=d[(i+1)%len(d)]]])
pca_p=np.searchsorted(cuts,thp)%len(cuts)
def vmpdf(t,m,k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t,w):
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12;R=min(np.sqrt(C*C+S*S)/s,0.999);return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
t1=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]);t2=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
P=np.zeros((6,len(t1)));P[lab0,np.arange(len(t1))]=1;m1=np.zeros(6);k1=np.ones(6);m2_=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(150):
    for k in range(6): w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
s7p=P.argmax(0)
clab=np.empty(TP,object);clab[up]=[f'PCA-{c+1}' for c in pca_p];clab[svp]=[f'7d-{c+1}' for c in s7p]
rows=json.load(open(OUT+r'\final_combined_rows.json',encoding='utf-8'))
info={r['cluster']:r for r in rows}
order=sorted([r['cluster'] for r in rows], key=lambda c:-info[c]['PN'])
d7=np.arange(-7,8); d28=np.arange(-28,29)
fig,axes=plt.subplots(3,3,figsize=(15,11))
for ax,c in zip(axes.ravel(),order):
    r=info[c]; hi=r['label']=='Higher-risk'; col='#c0392b' if hi else('#2471a3' if r['label']=='Lower-risk' else '#7f8c8d')
    mem=clab==c
    if c.startswith('7d'):
        traj=pos_pd[mem][:,21:36]
        for row in traj[np.random.RandomState(0).choice(len(traj),min(40,len(traj)),replace=False)]:
            ax.plot(d7,row,color=col,alpha=0.08,lw=.8)
        ax.plot(d7,traj.mean(0),color=col,lw=3); ax.set_xlim(-7,7); ax.set_xlabel('day (±7)')
    else:
        mpd=pos_pd[mem][:,:57].mean(0); mds=pos_ds[mem][:,:57].mean(0)
        ax.plot(d28,mpd,color=col,lw=3,label='taken (consumed)'); ax.plot(d28,mds,color=col,lw=1.6,ls=':',label='prescribed')
        ax.set_xlim(-28,28); ax.set_xlabel('day (±28)'); ax.legend(fontsize=7,loc='upper left')
    ax.axvline(0,color='k',lw=.5); ax.axhline(1,color='gray',lw=.4,ls='--')
    ax.set_title(f"{c}  |  P/N={r['PN']:.2f}  |  {r['label']}  (n={r['posN']})",fontsize=10,color=col,fontweight='bold')
    ax.set_ylabel('norm. dose')
    for sp in ax.spines.values(): sp.set_edgecolor(col); sp.set_linewidth(1.5)
fig.suptitle('Methadone dose-trajectory clusters (higher-risk red, lower-risk blue)',fontsize=13,y=1.005)
plt.tight_layout(); fig.savefig(OUT+r'\fig5_cluster_gallery.png',dpi=140,bbox_inches='tight'); plt.close()
print('saved fig5_cluster_gallery.png; order:',order)
