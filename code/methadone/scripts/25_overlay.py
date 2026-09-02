# -*- coding: utf-8 -*-
"""All-clusters overlay figure (every significant cluster in one view).
Left: dose-change clusters (±7d consumed dose), higher-risk solid / lower-risk dashed.
Right: stable-dose clusters (±28d), consumed solid / prescribed dotted."""
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
TP=3401; up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up
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
for _ in range(120):
    for k in range(6):w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
clab=np.empty(TP,object);clab[up]=[f'PCA-{c+1}' for c in pca_p];clab[svp]=[f'7d-{c+1}' for c in P.argmax(0)]
rows=json.load(open(OUT+r'\final_combined_rows.json',encoding='utf-8'))
pn={r['cluster']:r['PN'] for r in rows}; lab={r['cluster']:r['label'] for r in rows}
d7=np.arange(-7,8); d28=np.arange(-28,29)
import matplotlib.cm as cm
fig,(a1,a2)=plt.subplots(1,2,figsize=(15,5.6))
sig7=sorted([c for c in set(clab) if c.startswith('7d') and lab[c]!='ns'],key=lambda s:-pn[s])
for i,c in enumerate(sig7):
    hi=pn[c]>1; col=cm.Reds(0.4+0.5*i/len(sig7)) if hi else cm.Blues(0.4+0.5*i/len(sig7))
    a1.plot(d7,pos_pd[clab==c][:,21:36].mean(0),lw=2.5,ls='-' if hi else '--',color=col,label=f'{c} (P/N={pn[c]:.2f})')
a1.axvline(0,color='k',lw=.6);a1.axhline(1,color='gray',lw=.4,ls=':')
a1.set_title('Dose-change clusters (±7 d, consumed dose)\nhigher-risk solid / lower-risk dashed',fontsize=11)
a1.set_xlabel('day relative to urine test');a1.set_ylabel('normalized consumed dose');a1.legend(fontsize=8,ncol=2)
sigp=sorted([c for c in set(clab) if c.startswith('PCA') and lab[c]!='ns'],key=lambda s:-pn[s])
for c in sigp:
    hi=pn[c]>1; col='#c0392b' if hi else '#2471a3'
    l=a2.plot(d28,pos_pd[clab==c][:,:57].mean(0),lw=2.5,color=col,label=f'{c} consumed (P/N={pn[c]:.2f})')[0]
    a2.plot(d28,m2(afn[1])[clab==c][:,:57].mean(0),lw=1.4,ls=':',color=col)
a2.axvline(0,color='k',lw=.6);a2.axhline(1,color='gray',lw=.4,ls=':')
a2.set_title('Stable-dose clusters (±28 d)\nconsumed solid / prescribed dotted',fontsize=11)
a2.set_xlabel('day relative to urine test');a2.set_ylabel('normalized dose');a2.legend(fontsize=8)
plt.tight_layout();fig.savefig(OUT+r'\fig_overlay.png',dpi=140,bbox_inches='tight');plt.close()
print('saved fig_overlay.png; 7d sig:',sig7,'PCA sig:',sigp)
