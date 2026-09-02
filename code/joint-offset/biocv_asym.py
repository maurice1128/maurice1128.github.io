"""
The FAIR test for distance-error: stratify by camera-distance ASYMMETRY.
distance-error only helps when the subject is at the edge of the volume (near
some cameras, far from others). We compute per-frame asymmetry (far/near ratio
of the associated cameras to the subject), and compare reproj vs distance
single-removal knee-angle error in LOW vs HIGH asymmetry frames.
P06+P10 walk trials. Writes D:/BioCV/ASYM_RESULT.txt.
"""
import glob, numpy as np, ezc3d, cv2, sys, os
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
OUT="D:/BioCV/ASYM_RESULT.txt"; open(OUT,"w").close()
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
COCO={'Lhip':11,'Lkne':13,'Lank':15}; BODY=[5,6,11,12,13,14,15,16]
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
# collect (asymmetry, err_wdlt, err_reproj, err_distance) per frame
rows=[]
for pid in ["P06","P10"]:
    trials=[t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*")) if 'ML' not in os.path.basename(t) and glob.glob(f"{t}/*marker*.c3d")][:4]
    cams,_=load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    for trial in trials:
        tv=sorted(glob.glob(f"{trial}/*.mp4")); n=min(len(cams),len(tv))
        d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
        VP=np.transpose(d["data"]["points"][:3],(2,1,0))
        if not all(k in lab for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]): continue
        li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
        caps=[cv2.VideoCapture(v) for v in tv[:n]]; vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
        for fi in list(range(0,min(vN,VP.shape[0]),6))[:140]:
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
            good=[i for i in range(n) if dets[i] is not None and
                  (lambda es:es and np.median(es)<40)([re(cams[i],skel[j],dets[i][j,:2]) for j in BODY if skel[j] is not None])]
            if len(good)<4: continue                       # need >=4 so single-removal leaves >=3
            gc=[cams[i] for i in good]
            # subject position = knee 3D (Vicon), asymmetry of good cameras to it
            dists=[np.linalg.norm(c.C-vk) for c in gc]; asym=max(dists)/min(dists)
            J={}
            for m,fn in [('w',None),('r',re),('d',de)]:
                JJ={}
                for key,cj in [('h',COCO['Lhip']),('k',COCO['Lkne']),('a',COCO['Lank'])]:
                    uvs=U(cj)[good]; w=W(cj)[good]; JJ[key]=wdlt(gc,uvs,w) if fn is None else single_rm(gc,uvs,w,fn)
                J[m]=ang(JJ['h'],JJ['k'],JJ['a'])
            if all(np.isfinite(J[m]) for m in J):
                rows.append((asym,abs(J['w']-gk),abs(J['r']-gk),abs(J['d']-gk)))
        for c in caps: c.release()
        log(f"[{pid}/{os.path.basename(trial)}] frames so far {len(rows)}")
rows=np.array(rows)
log(f"\ntotal frames={len(rows)}  asymmetry: median={np.median(rows[:,0]):.2f} p90={np.percentile(rows[:,0],90):.2f} max={rows[:,0].max():.2f}")
log("\n=== knee-angle MAE (deg) by camera-distance asymmetry ===")
log(f"{'asym bin':>14}{'n':>6}{'no-removal':>12}{'reproj':>10}{'distance':>10}")
for lo,hi,name in [(1.0,1.5,'low <1.5'),(1.5,2.0,'1.5-2.0'),(2.0,3.0,'2.0-3.0'),(3.0,99,'high >3.0')]:
    m=(rows[:,0]>=lo)&(rows[:,0]<hi)
    if m.sum()<3: log(f"{name:>14}{m.sum():>6}   (too few)"); continue
    log(f"{name:>14}{m.sum():>6}{rows[m,1].mean():>12.2f}{rows[m,2].mean():>10.2f}{rows[m,3].mean():>10.2f}")
log("\n=> distance-error's claim holds ONLY if 'distance' < 'reproj' in the HIGH asymmetry bins.")
