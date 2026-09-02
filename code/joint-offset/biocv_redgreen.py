"""
BioCV red/green — unattended full best-effort run.
Calib is mocAligned => markerless triangulation is in the SAME spatial frame as
markers.c3d (no coordinate transform). Dataset is hardware-synchronised => assume
video frame i <-> mocap frame i (log a warning if angle correlation is low, which
would indicate a temporal offset to fix). Everything -> D:/BioCV/REDGREEN_RESULT.txt.
"""
import os, sys, glob, traceback
import numpy as np
sys.path.insert(0, "D:/ROWV_paper")
LOG = open("D:/BioCV/REDGREEN_RESULT.txt", "w", encoding="utf-8")
def log(*a):
    s=" ".join(str(x) for x in a); print(s); LOG.write(s+"\n"); LOG.flush()

BIO="D:/BioCV"
COCO={'nose':0,'Lsho':5,'Rsho':6,'Lhip':11,'Rhip':12,'Lknee':13,'Rknee':14,'Lank':15,'Rank':16}

def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))

def main():
    import rowv as R
    from biocv_calib import load_biocv_cameras
    if not os.path.isdir(f"{BIO}/P06") and os.path.exists(f"{BIO}/P06.tar"):
        log("extracting P06.tar..."); os.system(f'tar -xf "{BIO}/P06.tar" -C "{BIO}"')
    root=f"{BIO}/P06"
    # structure
    log("=== tree (d<=3) ===");
    for dp,dns,fns in os.walk(root):
        d=dp.replace(root,"").count(os.sep)
        if d<=3:
            log("  "*d+os.path.basename(dp)+"/"); [log("  "*(d+1)+f) for f in fns[:10]]
    vids=glob.glob(f"{root}/**/*.mp4",recursive=True); c3ds=glob.glob(f"{root}/**/*.c3d",recursive=True)
    log(f"\n#mp4={len(vids)} #c3d={len(c3ds)}")
    # choose a WALK trial dir that has ~9 mp4s + a markers c3d
    trialdirs={}
    for v in vids:
        trialdirs.setdefault(os.path.dirname(v),[]).append(v)
    walk_trials=[d for d in trialdirs if 'WALK' in d.upper() and len(trialdirs[d])>=6]
    log("WALK trial dirs (>=6 cams):", [os.path.basename(d) for d in walk_trials[:8]])
    if not walk_trials: log("NO walk trial with enough videos found — see tree above."); return
    trial=sorted(walk_trials)[0]; tvids=sorted(trialdirs[trial]); log("\nUSing trial:", trial, "videos:", [os.path.basename(x) for x in tvids])
    tc3d=[c for c in c3ds if os.path.dirname(c)==trial and 'marker' in c.lower()] or \
         [c for c in c3ds if os.path.basename(os.path.dirname(c))==os.path.basename(trial)] or \
         [c for c in c3ds if 'marker' in c.lower()]
    log("trial c3d:", [os.path.basename(x) for x in tc3d[:3]])

    cams,_=load_biocv_cameras(f"{BIO}/_calib/P06")
    log(f"cameras: {len(cams)}; videos: {len(tvids)}")
    n=min(len(cams),len(tvids))
    if n<4: log("fewer than 4 cam/video pairs — abort"); return

    # Vicon joint centres
    import ezc3d
    d=ezc3d.c3d(tc3d[0]); lab=d["parameters"]["POINT"]["LABELS"]["value"]; rate=d["parameters"]["POINT"]["RATE"]["value"][0]
    VP=np.transpose(d["data"]["points"][:3],(2,1,0))  # (T,M,3) mm
    log(f"vicon rate={rate} frames={VP.shape[0]} markers={VP.shape[1]}")
    need=["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE","RIGHT_HIP","RIGHT_KNEE","RIGHT_ANKLE"]
    jc={k:lab.index(k) for k in need if k in lab}
    log("joint-centre markers:", jc)
    if len(jc)<6: log("missing joint-centre markers; labels were:", lab); return

    # RTMPose (CPU balanced), subsample frames
    import cv2
    from rtmlib import Body
    body=Body(mode="balanced", backend="onnxruntime", device="cpu")
    caps=[cv2.VideoCapture(v) for v in tvids[:n]]
    vfps=caps[0].get(cv2.CAP_PROP_FPS); vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
    log(f"video fps={vfps} frames={vN}")
    step=max(1,int(round(vfps/30)))            # ~30fps analysis
    idxs=list(range(0,min(vN,VP.shape[0]),step))[:150]   # cap 150 frames
    log(f"analysing {len(idxs)} frames (step {step})")

    def detect(cap,fi):
        cap.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cap.read()
        if not ok: return None
        k,s=body(fr)
        if not len(k): return None
        p=int(np.argmax(s.mean(1))); return np.concatenate([k[p],s[p][:,None]],axis=1)

    def de(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)*np.linalg.norm(cam.C-X)
    def re(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
    def tri(cs,uvs,w,metric):
        val=[i for i in range(len(cs)) if np.isfinite(uvs[i]).all()]
        if len(val)<2: return None
        X=R.triangulate_wdlt([cs[i] for i in val],uvs[val],w[val])
        if metric and len(val)>=3:
            kk=int(np.argmax([metric(cs[val[i]],X,uvs[val[i]]) for i in range(len(val))]))
            keep=[val[i] for i in range(len(val)) if i!=kk]
            X=R.triangulate_wdlt([cs[i] for i in keep],uvs[keep],w[keep])
        return X

    err={'reproj':{'knee':[],'hip':[],'ankle':[]},'distance':{'knee':[],'hip':[],'ankle':[]}}
    done=0
    for fi in idxs:
        dets=[detect(caps[i],fi) for i in range(n)]
        if sum(x is not None for x in dets)<4: continue
        # build per-joint uvs across cameras
        def uvs_of(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan,np.nan] for i in range(n)])
        def w_of(j):   return np.array([dets[i][j,2]  if dets[i] is not None else 0.0 for i in range(n)])
        rec={}
        for name,method in [('reproj',re),('distance',de)]:
            J={}
            for jn,cj in COCO.items():
                X=tri(cams[:n],uvs_of(cj),w_of(cj),method)
                J[jn]=X
            rec[name]=J
        V=VP[fi]
        gt={'Lhip':V[jc['LEFT_HIP']],'Lknee':V[jc['LEFT_KNEE']],'Lank':V[jc['LEFT_ANKLE']],
            'Rhip':V[jc['RIGHT_HIP']],'Rknee':V[jc['RIGHT_KNEE']],'Rank':V[jc['RIGHT_ANKLE']]}
        gknee=ang(gt['Lhip'],gt['Lknee'],gt['Lank']); ghip=None; gank=None
        for name in ('reproj','distance'):
            J=rec[name]
            if any(J[k] is None for k in ['Lhip','Lknee','Lank']): continue
            mknee=ang(J['Lhip'],J['Lknee'],J['Lank'])
            if np.isfinite(mknee) and np.isfinite(gknee): err[name]['knee'].append(abs(mknee-gknee))
            # hip: trunk (hip->sho) vs thigh (hip->knee)
            if J['Lsho'] is not None:
                mhip=ang(J['Lsho'],J['Lhip'],J['Lknee']); ghipv=ang(V[jc['LEFT_HIP']]*0+gt['Lhip'],gt['Lhip'],gt['Lknee'])
                # vicon hip needs a trunk point; use shoulder marker if present
                if 'LEFT_SHO' in lab:
                    gsho=VP[fi][lab.index('LEFT_SHO')]; ghipv=ang(gsho,gt['Lhip'],gt['Lknee'])
                    if np.isfinite(mhip) and np.isfinite(ghipv): err[name]['hip'].append(abs(mhip-ghipv))
        done+=1
    log(f"\nframes used: {done}")
    log("=== JOINT-ANGLE MAE (deg), left leg, N=1 trial PRELIMINARY ===")
    log(f"{'joint':>7}{'reproj':>10}{'distance':>10}{'nframes':>9}")
    for j in ['knee','hip']:
        r=err['reproj'][j]; dd=err['distance'][j]
        rr=np.mean(r) if r else float('nan'); dv=np.mean(dd) if dd else float('nan')
        log(f"{j:>7}{rr:>10.2f}{dv:>10.2f}{len(dd):>9}")
    log("\nCAVEAT: N=1 trial, i<->i sync assumed, CPU. If numbers are absurd (knee MAE>30deg),")
    log("temporal sync offset is the likely cause -> needs cross-correlation fix. Treat as a")
    log("smoke test of the pipeline, not the real red/green.")
    for c in caps: c.release()

try: main()
except Exception: log("FATAL:\n"+traceback.format_exc())
finally: LOG.close()
