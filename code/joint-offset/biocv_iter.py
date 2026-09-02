"""
Fairest head-to-head for the user's claim, WITHOUT a separate association step
(Pose2Sim's real approach = iterative camera removal handles wrong-person too).
Same statistical removal rule (remove worst while > median+3*MAD, down to min 3),
only the METRIC differs:
  ITER_REPROJ  : reprojection error (px)         = Pose2Sim-faithful
  ITER_DIST    : object-space distance error (mm) = author's distance-correction
Stratified by camera-distance asymmetry. If ITER_DIST < ITER_REPROJ in HIGH
asymmetry, the user's claim holds on real gait.  P06+P10 -> D:/BioCV/ITER_RESULT.txt
"""
import glob, numpy as np, ezc3d, cv2, sys, os
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
OUT="D:/BioCV/ITER_RESULT.txt"; open(OUT,"w").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s)
    open(OUT,"a",encoding="utf-8").write(s+"\n")
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
def rep(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
def objd(cam,X,uv):
    dv=cam.ray_dir(uv); w=X-cam.C; return np.linalg.norm(w-np.dot(w,dv)*dv)
def wdlt(cs,uvs,w): return R.triangulate_wdlt(cs,uvs,w)
def iter_rm(cs,uvs,w,metric,min_cam=3,k=3.0):
    idx=list(range(len(cs)))
    while len(idx)>min_cam:
        CS=[cs[i] for i in idx]; UU=uvs[idx]; WW=w[idx]
        X=wdlt(CS,UU,WW); e=np.array([metric(CS[i],X,UU[i]) for i in range(len(idx))])
        med=np.median(e); mad=np.median(np.abs(e-med))*1.4826
        worst=int(np.argmax(e))
        if mad<1e-9 or e[worst]<=med+k*mad: break
        idx.pop(worst)
    CS=[cs[i] for i in idx]; return wdlt(CS,uvs[idx],w[idx])
COCO={'h':11,'k':13,'a':15}
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
rows=[]
for pid in ["P06","P10"]:
    trials=[t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*")) if 'ML' not in os.path.basename(t) and glob.glob(f"{t}/*marker*.c3d")][:6]
    cams,_=load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    for trial in trials:
        tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
        d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
        VP=np.transpose(d["data"]["points"][:3],(2,1,0))
        if not all(k in lab for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]): continue
        li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
        caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
        for fi in list(range(0,min(vN,VP.shape[0]),5))[:170]:
            vh,vk,va=[VP[fi][li[x]] for x in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]]
            if not all(np.any(x) for x in [vh,vk,va]): continue
            gk=ang(vh,vk,va)
            dets=[]
            for cp in caps[:n]:
                cp.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cp.read()
                if not ok: dets.append(None); continue
                kp,s=body(fr); dets.append(np.concatenate([kp[int(np.argmax(s.mean(1)))],s[int(np.argmax(s.mean(1)))][:,None]],1) if len(kp) else None)
            def U(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan]*2 for i in range(n)])
            def W(j): return np.array([dets[i][j,2] if dets[i] is not None else 0. for i in range(n)])
            valj={x:[i for i in range(n) if dets[i] is not None and np.isfinite(dets[i][COCO[x],0])] for x in COCO}
            if any(len(valj[x])<4 for x in COCO): continue
            dists=[np.linalg.norm(cams[i].C-vk) for i in valj['k']]; asym=max(dists)/min(dists)
            res={}
            for nm,metric in [('r',rep),('d',objd)]:
                J={}
                for x,cj in COCO.items():
                    vi=valj[x]; J[x]=iter_rm([cams[i] for i in vi],U(cj)[vi],W(cj)[vi],metric)
                res[nm]=ang(J['h'],J['k'],J['a'])
            if all(np.isfinite(res[m]) for m in res):
                rows.append((asym,abs(res['r']-gk),abs(res['d']-gk)))
        for c in caps: c.release()
        log(f"[{pid}/{os.path.basename(trial)}] frames {len(rows)}")
rows=np.array(rows)
log(f"\nN={len(rows)}  asym median={np.median(rows[:,0]):.2f} max={rows[:,0].max():.2f}")
log(f"{'asym bin':>12}{'n':>6}{'ITER_reproj':>13}{'ITER_dist':>11}{'winner':>9}")
for lo,hi,nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,3,'2-3'),(3,99,'>3')]:
    m=(rows[:,0]>=lo)&(rows[:,0]<hi)
    if m.sum()<3: log(f"{nm:>12}{int(m.sum()):>6}  few"); continue
    r=rows[m,1].mean(); dd=rows[m,2].mean()
    log(f"{nm:>12}{int(m.sum()):>6}{r:>13.2f}{dd:>11.2f}{('DIST' if dd<r else 'reproj'):>9}")
log("\nVERDICT: user's claim holds iff ITER_dist < ITER_reproj in >2/>3 bins.")
