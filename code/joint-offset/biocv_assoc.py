"""
Person-association pipeline (the proper fix), validated on P06_WALK_01.
Step 1: RTMPose top person per camera.
Step 2: ASSOCIATION at camera level — rough 3D skeleton via per-joint RANSAC, then
        each camera's WHOLE-skeleton reprojection error; keep only cameras whose
        person matches the multi-view consensus (median reproj < TH). This removes
        wrong-person / out-of-frame cameras entirely.
Step 3: on the associated (target) cameras, triangulate each joint with:
        wDLT (no removal), reproj single-removal, distance single-removal.
Compare knee-angle MAE vs Vicon for: RANSAC-only(no assoc), assoc+wDLT,
        assoc+reproj, assoc+distance.
"""
import glob, numpy as np, ezc3d, cv2, sys
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
def re(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
def de(cam,X,uv): return re(cam,X,uv)*np.linalg.norm(cam.C-X)
def wdlt(cs,uvs,w): return R.triangulate_wdlt(cs,uvs,w)
def single_rm(cs,uvs,w,metric):
    if len(cs)<3: return wdlt(cs,uvs,w)
    X=wdlt(cs,uvs,w); k=int(np.argmax([metric(cs[i],X,uvs[i]) for i in range(len(cs))]))
    keep=[i for i in range(len(cs)) if i!=k]; return wdlt([cs[i] for i in keep],uvs[keep],w[keep])
COCO={'hip':11,'knee':13,'ank':15}; BODY=[5,6,11,12,13,14,15,16]  # for skeleton reproj

trial="D:/BioCV/P06/P06_WALK_01"
cams,_=load_biocv_cameras("D:/BioCV/_calib/P06")
tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
VP=np.transpose(d["data"]["points"][:3],(2,1,0)); li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
step=6; idxs=list(range(0,min(vN,VP.shape[0]),step))[:120]
err={'RANSAC_noassoc':[], 'assoc_wDLT':[], 'assoc_reproj':[], 'assoc_distance':[]}
n_assoc=[]
for fi in idxs:
    vh,vk,va=VP[fi][li['LEFT_HIP']],VP[fi][li['LEFT_KNEE']],VP[fi][li['LEFT_ANKLE']]
    if not (np.any(vh) and np.any(vk) and np.any(va)): continue
    gk=ang(vh,vk,va)
    dets=[]
    for cp in caps[:n]:
        cp.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cp.read()
        if not ok: dets.append(None); continue
        k,s=body(fr); dets.append(np.concatenate([k[int(np.argmax(s.mean(1)))],s[int(np.argmax(s.mean(1)))][:,None]],1) if len(k) else None)
    def U(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan]*2 for i in range(n)])
    def W(j): return np.array([dets[i][j,2] if dets[i] is not None else 0. for i in range(n)])
    # --- rough skeleton via per-joint RANSAC (for association) ---
    skel={}
    for j in BODY:
        uvs=U(j); val=[i for i in range(n) if np.isfinite(uvs[i]).all()]
        skel[j]=R.m_ransac([cams[i] for i in val],uvs[val],W(j)[val],thresh_px=30) if len(val)>=2 else None
    # --- camera-level association: whole-skeleton median reproj ---
    good=[]
    for i in range(n):
        if dets[i] is None: continue
        es=[re(cams[i],skel[j],dets[i][j,:2]) for j in BODY if skel[j] is not None]
        if es and np.median(es)<40: good.append(i)      # target camera
    n_assoc.append(len(good))
    # RANSAC no-assoc (per-joint, all cams)
    def ransac_joint(j):
        uvs=U(j); val=[i for i in range(n) if np.isfinite(uvs[i]).all()]
        return R.m_ransac([cams[i] for i in val],uvs[val],W(j)[val],thresh_px=30) if len(val)>=2 else None
    Hr,Kr,Ar=[ransac_joint(COCO[x]) for x in ['hip','knee','ank']]
    if all(v is not None for v in [Hr,Kr,Ar]):
        m=ang(Hr,Kr,Ar);
        if np.isfinite(m): err['RANSAC_noassoc'].append(abs(m-gk))
    if len(good)>=3:
        gc=[cams[i] for i in good]
        for nm,fn in [('assoc_wDLT',None),('assoc_reproj',re),('assoc_distance',de)]:
            J={}
            for x in ['hip','knee','ank']:
                j=COCO[x]; uvs=U(j)[good]; w=W(j)[good]
                J[x]=wdlt(gc,uvs,w) if fn is None else single_rm(gc,uvs,w,fn)
            m=ang(J['hip'],J['knee'],J['ank'])
            if np.isfinite(m): err[nm].append(abs(m-gk))
for c in caps: c.release()
print(f"frames used ~{len(err['assoc_wDLT'])}; mean associated cameras/frame={np.mean(n_assoc):.1f}/{n}")
print(f"{'method':>18}{'knee MAE deg':>14}{'nframes':>9}")
for k in err:
    print(f"{k:>18}{(np.mean(err[k]) if err[k] else float('nan')):>14.2f}{len(err[k]):>9}")
