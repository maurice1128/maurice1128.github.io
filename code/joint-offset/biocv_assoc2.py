"""Extended association pipeline: P06+P10, knee+hip, per-participant knee/hip
angle MAE (deg) + waveform Pearson r vs Vicon, comparing (after association):
no-removal wDLT vs reproj single-removal vs distance single-removal.
Writes D:/BioCV/ASSOC_RESULT.txt."""
import glob, numpy as np, ezc3d, cv2, sys, os
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
OUT="D:/BioCV/ASSOC_RESULT.txt"; open(OUT,"w").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s); open(OUT,"a").write(s+"\n")
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
def re(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
def de(cam,X,uv): return re(cam,X,uv)*np.linalg.norm(cam.C-X)
def wdlt(cs,uvs,w): return R.triangulate_wdlt(cs,uvs,w)
def single_rm(cs,uvs,w,m):
    if len(cs)<3: return wdlt(cs,uvs,w)
    X=wdlt(cs,uvs,w); k=int(np.argmax([m(cs[i],X,uvs[i]) for i in range(len(cs))]))
    keep=[i for i in range(len(cs)) if i!=k]; return wdlt([cs[i] for i in keep],uvs[keep],w[keep])
COCO={'Lhip':11,'Lkne':13,'Lank':15,'Lsho':5}; BODY=[5,6,11,12,13,14,15,16]
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
METH=['wDLT','reproj','distance']
allmae={m:{'knee':[], 'hip':[]} for m in METH}
for pid in ["P06","P10"]:
    trials=[t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*")) if 'ML' not in os.path.basename(t) and glob.glob(f"{t}/*marker*.c3d")][:3]
    cams,_=load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    for trial in trials:
        tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
        d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
        VP=np.transpose(d["data"]["points"][:3],(2,1,0))
        need=["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE","LEFT_SHO"]
        if not all(k in lab for k in need): continue
        li={k:lab.index(k) for k in need}
        caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
        idxs=list(range(0,min(vN,VP.shape[0]),6))[:130]
        series={m:{'knee':[], 'hip':[]} for m in METH}; vser={'knee':[], 'hip':[]}
        for fi in idxs:
            vh,vk,va,vs=[VP[fi][li[k]] for k in need]
            if not all(np.any(x) for x in [vh,vk,va,vs]): continue
            gknee=ang(vh,vk,va); ghip=ang(vs,vh,vk)
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
            good=[i for i in range(n) if dets[i] is not None and
                  (lambda es:es and np.median(es)<40)([re(cams[i],skel[j],dets[i][j,:2]) for j in BODY if skel[j] is not None])]
            if len(good)<3: continue
            gc=[cams[i] for i in good]
            for m in METH:
                fn={'wDLT':None,'reproj':re,'distance':de}[m]
                J={}
                for key,cj in [('Lhip',COCO['Lhip']),('Lkne',COCO['Lkne']),('Lank',COCO['Lank']),('Lsho',COCO['Lsho'])]:
                    uvs=U(cj)[good]; w=W(cj)[good]
                    J[key]=wdlt(gc,uvs,w) if fn is None else single_rm(gc,uvs,w,fn)
                mk=ang(J['Lhip'],J['Lkne'],J['Lank']); mh=ang(J['Lsho'],J['Lhip'],J['Lkne'])
                if np.isfinite(mk) and np.isfinite(gknee): series[m]['knee'].append((mk,gknee))
                if np.isfinite(mh) and np.isfinite(ghip): series[m]['hip'].append((mh,ghip))
            vser['knee'].append(gknee); vser['hip'].append(ghip)
        for c in caps: c.release()
        for m in METH:
            for jt in ['knee','hip']:
                arr=np.array(series[m][jt])
                if len(arr)>5:
                    mae=np.mean(np.abs(arr[:,0]-arr[:,1])); allmae[m][jt].append(mae)
        log(f"[{pid}/{os.path.basename(trial)}] done, frames~{len(series['wDLT']['knee'])}")
log("\n=== ASSOCIATION pipeline: joint-angle MAE (deg), P06+P10 walk trials ===")
log(f"{'method':>10}{'knee MAE':>10}{'hip MAE':>10}{'n_trials':>10}")
for m in METH:
    k=allmae[m]['knee']; h=allmae[m]['hip']
    log(f"{m:>10}{(np.mean(k) if k else float('nan')):>10.2f}{(np.mean(h) if h else float('nan')):>10.2f}{len(k):>10}")
log("\nInterpretation: 'wDLT'=association only, no per-joint removal (Pose2Sim/ROWV both ADD removal).")
log("If wDLT <= reproj and <= distance -> per-joint outlier removal (incl. distance-error) does NOT help real gait.")
