# -*- coding: utf-8 -*-
"""Step 17 - clean METHODS figure (replaces the MATLAB screenshots):
  A. example dose trajectory -> moving-window min/max slopes -> polar angle
  B. 2-D angular density of (theta_min, theta_max) with von Mises component means (7d)
  C. circular density of the PCA angle with the density-valley cut points (stable-dose)"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, warnings; warnings.filterwarnings('ignore')
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
up=~(np.abs(np.diff(pos_pd[:,21:36],axis=1)).sum(1)!=0); svp=~up

fig=plt.figure(figsize=(16,4.8))

# ---- Panel A: example trajectory + slopes ----
axA=fig.add_subplot(1,3,1)
# pick a dose-change test with clear dip-then-rise
cand=np.where(svp)[0]
ex=cand[np.argmax([ (pos_pd[i,28]-pos_pd[i,25]) - (pos_pd[i,25]-pos_pd[i,22]) for i in cand])]
tr=pos_pd[ex,21:36]/pos_pd[ex,21]   # normalize to day -7
days=np.arange(-7,8)
axA.plot(days,tr,'-o',color='#333',lw=1.5,ms=4,zorder=3)
def bestwin(lo,hi,want='max'):
    best=None
    for s in range(lo,hi-2):
        sl=np.polyfit([0,1,2],tr[s:s+3],1)[0]
        if best is None or (sl>best[1] if want=='max' else sl<best[1]): best=(s,sl)
    return best
for side,(lo,hi) in [('pre',(0,8)),('post',(7,15))]:
    for want,col in [('max','#c0392b'),('min','#2471a3')]:
        s,sl=bestwin(lo,hi,want); xs=days[s:s+3]; ys=tr[s:s+3]
        p=np.polyfit(xs,ys,1); axA.plot(xs,np.polyval(p,xs),col,lw=3,alpha=.8,zorder=2)
axA.axvline(0,color='k',lw=.6); axA.set_title('A. Moving-window slopes → polar angle',fontsize=11)
axA.set_xlabel('day relative to urine test'); axA.set_ylabel('normalized dose')
axA.text(.02,.97,'red = steepest rise (max slope)\nblue = steepest fall (min slope)\nθ = atan2(post-slope, pre-slope)',
         transform=axA.transAxes,va='top',fontsize=8,bbox=dict(fc='white',ec='gray',alpha=.8))

# ---- Panel B: 2D angular density + von Mises means ----
axB=fig.add_subplot(1,3,2)
t1=np.arctan2(pos['mn_b'][svp],pos['mn_a'][svp]); t2=np.arctan2(pos['mx_b'][svp],pos['mx_a'][svp])
H,xe,ye=np.histogram2d(t1,t2,bins=40,range=[[-np.pi,np.pi],[-np.pi,np.pi]])
axB.imshow(H.T,origin='lower',extent=[-np.pi,np.pi,-np.pi,np.pi],aspect='auto',cmap='viridis')
def vmpdf(t,m,k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t,w):
    C=(w*np.cos(t)).sum();S=(w*np.sin(t)).sum();s=w.sum()+1e-12;R=min(np.sqrt(C*C+S*S)/s,0.999);return np.arctan2(S,C),R*(2-R*R)/(1-R*R)
lab0=KMeans(6,n_init=5,random_state=0).fit_predict(np.column_stack([np.cos(t1),np.sin(t1),np.cos(t2),np.sin(t2)]))
P=np.zeros((6,len(t1)));P[lab0,np.arange(len(t1))]=1;m1=np.zeros(6);k1=np.ones(6);m2_=np.zeros(6);k2=np.ones(6);pi=np.ones(6)/6
for _ in range(120):
    for k in range(6): w=P[k];m1[k],k1[k]=vm_mle(t1,w);m2_[k],k2[k]=vm_mle(t2,w);pi[k]=w.mean()+1e-9
    P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,m2_[k],k2[k]) for k in range(6)]);P/=P.sum(0)+1e-300
axB.scatter(m1,m2_,c='red',s=120,marker='x',lw=3,label='von Mises means (K=6)')
axB.set_title('B. Dose-change branch: (θmin, θmax) density\n+ von Mises components',fontsize=11)
axB.set_xlabel('θ min (rad)'); axB.set_ylabel('θ max (rad)'); axB.legend(fontsize=8,loc='upper right')

# ---- Panel C: PCA circular density + valley cuts ----
axC=fig.add_subplot(1,3,3)
proj=(np.hstack([pos_pd[up],pos_ds[up]])-mu0)@coeff.T
thp=np.arctan2(proj[:,1]-0.0270,proj[:,0]+0.04)%(2*np.pi)
grid=np.linspace(0,2*np.pi,721)[:-1]; dens=np.array([np.exp(12*np.cos(g-thp)).sum() for g in grid])
deg=np.rad2deg(grid)
axC.fill_between(deg,dens,color='#9b59b6',alpha=.4); axC.plot(deg,dens,color='#8e44ad',lw=1.5)
cuts_deg=[156,237,338]
for cd in cuts_deg: axC.axvline(cd,color='#c0392b',ls='--',lw=2)
axC.set_title('C. Stable-dose branch: circular density of θ\n+ valley cuts (3 clusters)',fontsize=11)
axC.set_xlabel('θ (degrees)'); axC.set_ylabel('circular kernel density'); axC.set_xlim(0,360)
axC.text(.98,.95,'cuts: 156°, 237°, 338°\n(stable across bandwidth)',transform=axC.transAxes,ha='right',va='top',fontsize=8,color='#c0392b')

plt.tight_layout(); fig.savefig(OUT+r'\fig0_methods.png',dpi=140,bbox_inches='tight'); plt.close()
print('saved fig0_methods.png')
