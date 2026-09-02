"""Two-dataset + mechanism figure. A: distance advantage vs asymmetry on BioCV
(real Vicon GT) and AIST++ (pseudo-GT, different rig) — same direction. B: mechanism
catch-rate at realistic asymmetry."""
import glob, pickle, numpy as np, sys, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

# BioCV real (BIOCV_CLUSTERED)
b_as=[1.25,1.75,2.25,2.75,3.5]; b_dm=[0.11,0.11,0.41,1.38,3.61]
b_lo=[0.04,0.06,0.28,0.7,2.32]; b_hi=[0.17,0.15,0.55,2.0,5.25]
# AIST pseudo-GT (AIST_CLUSTERED), realistic bins only
a_as=[1.25,1.75,2.5,3.5]; a_dm=[0.02,1.46,0.63,1.65]
a_lo=[-0.02,0.05,0.37,0.45]; a_hi=[0.08,4.47,0.95,4.76]

# mechanism catch-rate (realistic asym) — reuse biocv_sim geometry
cams0,_=load_biocv_cameras("D:/BioCV/_calib/P06")
D=pickle.load(open(sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl"))[0],"rb"))
Xg=next(fr["gt"][15].copy() for fr in D["frames"] if np.any(fr["gt"][15]))
def repoint(Kf,C,T):
    f=(T-C); f/=np.linalg.norm(f); a=np.array([0,0,1.0]) if abs(f[2])<0.95 else np.array([0,1.0,0])
    r=np.cross(a,f); r/=np.linalg.norm(r); u=np.cross(f,r); return R.Camera(Kf,np.vstack([r,u,f]),C)
def build(A):
    o=[]
    for i,c in enumerate(cams0):
        v=c.C-Xg; rr=np.linalg.norm(v); u=v/rr; o.append(repoint(c.K,Xg+u*(rr*A if i%2==0 else rr),Xg))
    return o
def rep(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
def objd(cam,X,uv):
    dv=cam.ray_dir(uv); w=X-cam.C; return np.linalg.norm(w-np.dot(w,dv)*dv)
rng=np.random.default_rng(1); TR=2500; rA=[]; crr=[]; crd=[]
for A in [1.0,1.15,1.3,1.5,1.7,2.0]:
    cams=build(A); dd=np.array([np.linalg.norm(c.C-Xg) for c in cams])
    if dd.max()/dd.min()>6.5: continue
    rA.append(dd.max()/dd.min()); far=int(np.argmax(dd)); p0=[c.project(Xg) for c in cams]
    hr=hd=0
    for _ in range(TR):
        uv=np.array([p+rng.normal(0,4,2) for p in p0]); an=rng.uniform(0,2*np.pi); uv[far]+=80*np.array([np.cos(an),np.sin(an)])
        Xn=R.triangulate_wdlt(cams,uv,np.ones(len(cams)))
        er=np.array([rep(cams[i],Xn,uv[i]) for i in range(len(cams))]); ed=np.array([objd(cams[i],Xn,uv[i]) for i in range(len(cams))])
        hr+=int(np.argmax(er)==far); hd+=int(np.argmax(ed)==far)
    crr.append(100*hr/TR); crd.append(100*hd/TR)

fig,(a1,a2)=plt.subplots(1,2,figsize=(11,4.2))
a1.errorbar(b_as,b_dm,yerr=[np.array(b_dm)-b_lo,np.array(b_hi)-np.array(b_dm)],fmt='o-',color='#2a7',capsize=4,label='BioCV (real Vicon GT)')
a1.errorbar([x+0.03 for x in a_as],a_dm,yerr=[np.array(a_dm)-a_lo,np.array(a_hi)-np.array(a_dm)],fmt='s--',color='#a72',capsize=4,label='AIST++ (pseudo-GT)')
a1.axhline(0,color='k',lw=.6); a1.set_xlabel('camera-distance asymmetry (max/min)')
a1.set_ylabel('object-space advantage (mm)'); a1.set_title('(A) Two datasets: same direction\n(small, ~mm, grows with asymmetry)'); a1.grid(alpha=.3); a1.legend()
a2.plot(rA,crr,'o-',color='#c44',label='reprojection'); a2.plot(rA,crd,'s-',color='#37a',label='object-space')
a2.set_xlabel('camera-distance asymmetry (max/min)'); a2.set_ylabel('far-camera outlier caught (%)')
a2.set_title('(B) Mechanism: reprojection fails to catch\nfar-camera outliers as asymmetry grows'); a2.set_ylim(0,105); a2.grid(alpha=.3); a2.legend()
fig.suptitle('Object-space outlier removal: a real, small, asymmetry-dependent benefit (2 datasets + mechanism)',y=1.02)
fig.tight_layout(); fig.savefig("D:/BioCV/fig_two.png",dpi=140,bbox_inches='tight')
print("saved D:/BioCV/fig_two.png"); print("mech realA",[round(x,1) for x in rA],"reproj",[round(x) for x in crr])
