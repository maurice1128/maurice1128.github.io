"""Cross-correlation sync diagnostic for P06_WALK_01: markerless vs Vicon knee
angle time series. Tells us if the residual error is a temporal offset (fixable)
or bad triangulation."""
import glob, os, numpy as np, ezc3d, cv2, sys
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
def de(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)*np.linalg.norm(cam.C-X)
def tri(cs,uvs,w):
    val=[i for i in range(len(cs)) if np.isfinite(uvs[i]).all()]
    if len(val)<2: return None
    X=R.triangulate_wdlt([cs[i] for i in val],uvs[val],w[val])
    if len(val)>=3:
        k=int(np.argmax([de(cs[val[i]],X,uvs[val[i]]) for i in range(len(val))]))
        keep=[val[i] for i in range(len(val)) if i!=k]; X=R.triangulate_wdlt([cs[i] for i in keep],uvs[keep],w[keep])
    return X
trial="D:/BioCV/P06/P06_WALK_01"
cams,_=load_biocv_cameras("D:/BioCV/_calib/P06")
tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
VP=np.transpose(d["data"]["points"][:3],(2,1,0)); li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
COCO={'hip':11,'knee':13,'ank':15}
step=4; idxs=list(range(0,min(vN,VP.shape[0]),step))[:160]
ml=[]; vi=[]
for fi in idxs:
    dets=[]
    for cp in caps[:n]:
        cp.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cp.read()
        if not ok: dets.append(None); continue
        k,s=body(fr); dets.append(np.concatenate([k[int(np.argmax(s.mean(1)))],s[int(np.argmax(s.mean(1)))][:,None]],1) if len(k) else None)
    def U(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan]*2 for i in range(n)])
    def W(j): return np.array([dets[i][j,2] if dets[i] is not None else 0. for i in range(n)])
    H=tri(cams[:n],U(COCO['hip']),W(COCO['hip'])); K=tri(cams[:n],U(COCO['knee']),W(COCO['knee'])); A=tri(cams[:n],U(COCO['ank']),W(COCO['ank']))
    ml.append(ang(H,K,A) if (H is not None and K is not None and A is not None) else np.nan)
    vh,vk,va=VP[fi][li['LEFT_HIP']],VP[fi][li['LEFT_KNEE']],VP[fi][li['LEFT_ANKLE']]
    vi.append(ang(vh,vk,va) if (np.any(vh) and np.any(vk) and np.any(va)) else np.nan)
ml=np.array(ml); vi=np.array(vi)
print(f"markerless knee: min={np.nanmin(ml):.0f} max={np.nanmax(ml):.0f} mean={np.nanmean(ml):.0f}")
print(f"vicon knee:      min={np.nanmin(vi):.0f} max={np.nanmax(vi):.0f} mean={np.nanmean(vi):.0f}")
# cross-correlation over frame offsets (in subsampled units)
best=None
for off in range(-15,16):
    a=ml.copy(); b=vi.copy()
    if off>0: a=a[off:]; b=b[:len(a)]
    elif off<0: b=b[-off:]; a=a[:len(b)]
    m=np.isfinite(a)&np.isfinite(b)
    if m.sum()<20: continue
    mae=np.mean(np.abs(a[m]-b[m]))
    if best is None or mae<best[1]: best=(off,mae,m.sum())
print(f"best offset={best[0]*step} frames  MAE={best[1]:.1f}deg  (n={best[2]})   [offset in subsampled units *{step}]")
print("markerless first 15:", np.round(ml[:15],0))
print("vicon      first 15:", np.round(vi[:15],0))
for c in caps: c.release()
