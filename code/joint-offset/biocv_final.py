"""
Definitive fair test of the distance-error contribution, stratified by asymmetry.
Two FULL pipelines + baseline, per frame, knee-angle error vs Vicon:
  FULL_REPROJ  : associate cameras by reprojection error (Pose2Sim-faithful),
                 then reprojection single-removal.
  FULL_DIST    : associate cameras by object-space (distance) error,
                 then distance single-removal.
  NO_REMOVAL   : reproj association, weighted DLT on all associated cameras.
Reported by camera-distance asymmetry bin. distance-error's claim holds ONLY if
FULL_DIST < FULL_REPROJ in the HIGH asymmetry bins.  P06+P10.  -> D:/BioCV/FINAL_RESULT.txt
"""
import glob, numpy as np, ezc3d, cv2, sys, os
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
OUT="D:/BioCV/FINAL_RESULT3.txt"
def log(*a):
    s=" ".join(str(x) for x in a); print(s)
    with open(OUT,"a",encoding="utf-8") as f: f.write(s+"\n")
open(OUT,"w").close()
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
def re(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
def objd(cam,X,uv):                                   # object-space perpendicular distance (mm)
    dvec=cam.ray_dir(uv); w=X-cam.C; return np.linalg.norm(w-np.dot(w,dvec)*dvec)
def de(cam,X,uv): return re(cam,X,uv)*np.linalg.norm(cam.C-X)
def wdlt(cs,uvs,w): return R.triangulate_wdlt(cs,uvs,w)
def single_rm(cs,uvs,w,m):
    if len(cs)<3: return wdlt(cs,uvs,w)
    X=wdlt(cs,uvs,w); k=int(np.argmax([m(cs[i],X,uvs[i]) for i in range(len(cs))]))
    keep=[i for i in range(len(cs)) if i!=k]; return wdlt([cs[i] for i in keep],uvs[keep],w[keep])
COCO={'h':11,'k':13,'a':15}; BODY=[5,6,11,12,13,14,15,16]
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
rows=[]   # (asym, err_norem, err_reproj, err_dist)
pids=sorted(os.path.basename(p) for p in glob.glob("D:/BioCV/P[0-9][0-9]") if os.path.isdir(p) and glob.glob(p+"/*WALK*") and os.path.isdir("D:/BioCV/_calib/"+os.path.basename(p)))
log("participants:",pids)
for pid in pids:
    trials=[t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*")) if 'ML' not in os.path.basename(t) and glob.glob(f"{t}/*marker*.c3d")][:4]
    cams,_=load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    for trial in trials:
        tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
        d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
        VP=np.transpose(d["data"]["points"][:3],(2,1,0))
        if not all(k in lab for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]): continue
        li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
        caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
        for fi in list(range(0,min(vN,VP.shape[0]),4))[:220]:
            vh,vk,va=[VP[fi][li[k]] for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]]
            if not all(np.any(x) for x in [vh,vk,va]): continue
            gk=ang(vh,vk,va)
            dets=[]
            for cp in caps[:n]:
                cp.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cp.read()
                if not ok: dets.append(None); continue
                k,s=body(fr); dets.append(np.concatenate([k[int(np.argmax(s.mean(1)))],s[int(np.argmax(s.mean(1)))][:,None]],1) if len(k) else None)
            def U(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan]*2 for i in range(n)])
            def W(j): return np.array([dets[i][j,2] if dets[i] is not None else 0. for i in range(n)])
            skel={}
            for j in BODY:
                uvs=U(j); val=[i for i in range(n) if np.isfinite(uvs[i]).all()]
                skel[j]=R.m_ransac([cams[i] for i in val],uvs[val],W(j)[val],thresh_px=30) if len(val)>=2 else None
            valid=[i for i in range(n) if dets[i] is not None]
            def assoc(metric,th):
                g=[]
                for i in valid:
                    es=[metric(cams[i],skel[j],dets[i][j,:2]) for j in BODY if skel[j] is not None]
                    if es and np.median(es)<th: g.append(i)
                return g
            g_re=assoc(re,40); g_di=assoc(objd,100)      # reproj-assoc(px) vs distance-assoc(mm)
            if len(g_re)<4 or len(g_di)<4: continue
            # asymmetry from reproj-assoc good cams to knee
            dists=[np.linalg.norm(cams[i].C-vk) for i in g_re]; asym=max(dists)/min(dists)
            def pipe(good,rmmetric):
                J={}
                for key,cj in COCO.items():
                    uvs=U(cj)[good]; w=W(cj)[good]; J[key]=single_rm([cams[i] for i in good],uvs,w,rmmetric)
                return ang(J['h'],J['k'],J['a'])
            def pipe_norem(good):
                J={}
                for key,cj in COCO.items():
                    uvs=U(cj)[good]; w=W(cj)[good]; J[key]=wdlt([cams[i] for i in good],uvs,w)
                return ang(J['h'],J['k'],J['a'])
            en=pipe_norem(g_re); er=pipe(g_re,re); ed=pipe(g_di,de)
            if all(np.isfinite(x) for x in [en,er,ed]):
                rows.append((asym,abs(en-gk),abs(er-gk),abs(ed-gk)))
        for c in caps: c.release()
        log(f"[{pid}/{os.path.basename(trial)}] frames {len(rows)}")
rows=np.array(rows)
log(f"\nN frames={len(rows)}  asym median={np.median(rows[:,0]):.2f} p90={np.percentile(rows[:,0],90):.2f} max={rows[:,0].max():.2f}")
log(f"{'asym bin':>12}{'n':>6}{'no-removal':>12}{'FULL_reproj':>13}{'FULL_dist':>11}")
for lo,hi,nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,3,'2-3'),(3,99,'>3')]:
    m=(rows[:,0]>=lo)&(rows[:,0]<hi)
    if m.sum()<3: log(f"{nm:>12}{int(m.sum()):>6}  few"); continue
    log(f"{nm:>12}{int(m.sum()):>6}{rows[m,1].mean():>12.2f}{rows[m,2].mean():>13.2f}{rows[m,3].mean():>11.2f}")
log("\nVERDICT: distance-error contribution holds iff FULL_dist < FULL_reproj in the >2 / >3 bins.")
