"""Round-trip test: project Vicon joint centres to all 9 cams, triangulate back.
Isolates calibration/triangulation correctness from RTMPose 2D quality."""
import glob, numpy as np, ezc3d, sys
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
trial="D:/BioCV/P06/P06_WALK_01"
cams,files=load_biocv_cameras("D:/BioCV/_calib/P06")
print("calib files:", [f.split('/')[-1] for f in files])
d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
VP=np.transpose(d["data"]["points"][:3],(2,1,0))
li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
# find a frame where all three present
fi=None
for t in range(VP.shape[0]):
    if all(np.any(VP[t][li[k]]) for k in li): fi=t; break
print("using valid frame", fi)
for jn,idx in li.items():
    X=VP[fi][idx]
    uvs=np.array([c.project(X) for c in cams])          # project GT 3D to all cams
    inframe=[(0<=u[0]<c.w and 0<=u[1]<c.h) for u,c in zip(uvs,cams)]
    Xrec=R.triangulate_wdlt(cams,uvs)                    # triangulate back
    err=np.linalg.norm(Xrec-X)
    print(f"{jn}: GT={np.round(X,0)} recovered={np.round(Xrec,0)} err={err:.2f}mm  in-frame={sum(inframe)}/9  uv0={np.round(uvs[0],0)}")
# knee angle from GT vs from a noisy version (add 5px noise to 2D, then triangulate)
def ang(a,b,c):
    u=a-b; v=c-b; return np.degrees(np.arccos(np.clip(u@v/(np.linalg.norm(u)*np.linalg.norm(v)),-1,1)))
H,K,A=[VP[fi][li[k]] for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]]
print("GT knee angle:", round(ang(H,K,A),1))
rng=np.random.default_rng(0)
Hn,Kn,An=[R.triangulate_wdlt(cams,np.array([c.project(P)+rng.normal(0,5,2) for c in cams])) for P in (H,K,A)]
print("knee angle from 5px-noisy 2D triangulation:", round(ang(Hn,Kn,An),1))
