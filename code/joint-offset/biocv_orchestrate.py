"""
BioCV overnight orchestrator — pull N up autonomously.
Loops for a time budget: moves completed .tar from Downloads to D:/BioCV, extracts
new participants, runs the angle analysis per participant (reproj vs distance
outlier removal, vs Vicon joint centres), aggregates across participants.
Gate: after the first participant, if knee MAE is absurd (>40deg) for BOTH methods,
temporal sync is broken -> stop before wasting compute. Writes AGGREGATE_RESULT.txt.
"""
import os, sys, glob, time, traceback
import numpy as np
sys.path.insert(0, "D:/ROWV_paper")
BIO="D:/BioCV"; DL="C:/Users/maurice/Downloads"
TARGETS=["P06","P10","P08","P09","P16"]
OUT=f"{BIO}/AGGREGATE_RESULT.txt"
def log(*a):
    s=" ".join(str(x) for x in a)
    with open(OUT,"a",encoding="utf-8") as f: f.write(s+"\n")
    print(s)
COCO={'nose':0,'Lsho':5,'Rsho':6,'Lhip':11,'Rhip':12,'Lknee':13,'Rknee':14,'Lank':15,'Rank':16}
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))

def analyze(pid):
    import rowv as R, cv2, ezc3d
    from biocv_calib import load_biocv_cameras
    from rtmlib import Body
    root=f"{BIO}/{pid}"
    cams,_=load_biocv_cameras(f"{BIO}/_calib/{pid}")
    vids=glob.glob(f"{root}/**/*.mp4",recursive=True); c3ds=glob.glob(f"{root}/**/*.c3d",recursive=True)
    tdirs={}
    for v in vids: tdirs.setdefault(os.path.dirname(v),[]).append(v)
    walks=sorted(d for d in tdirs if 'WALK' in os.path.basename(d).upper()
                 and 'ML' not in os.path.basename(d) and len(tdirs[d])>=6
                 and glob.glob(f"{d}/*marker*.c3d"))
    if not walks: log(f"[{pid}] no valid WALK trial (non-ML, with markers.c3d)"); return None
    body=Body(mode="balanced",backend="onnxruntime",device="cpu")
    def de(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)*np.linalg.norm(cam.C-X)
    def re(cam,X,uv): return np.linalg.norm(cam.project(X)-uv)
    def tri(cs,uvs,w,metric):
        val=[i for i in range(len(cs)) if np.isfinite(uvs[i]).all()]
        if len(val)<2: return None
        CS=[cs[i] for i in val]; UU=uvs[val]; WW=w[val]
        if metric=='ransac': return R.m_ransac(CS,UU,WW,thresh_px=30)   # multi-outlier consensus
        X=R.triangulate_wdlt(CS,UU,WW)
        if metric is not None and len(val)>=3:                          # single-removal (ROWV/Pose2Sim style)
            kk=int(np.argmax([metric(CS[i],X,UU[i]) for i in range(len(val))]))
            keep=[i for i in range(len(val)) if i!=kk]
            X=R.triangulate_wdlt([CS[i] for i in keep],UU[keep],WW[keep])
        return X
    perr={'reproj':[], 'distance':[], 'ransac':[]}
    for trial in walks[:2]:                    # up to 2 walk trials/participant
        tv=sorted(tdirs[trial]); n=min(len(cams),len(tv))
        if n<4: continue
        mk=glob.glob(f"{trial}/*marker*.c3d")     # this trial's OWN markers only
        if not mk: continue
        d=ezc3d.c3d(mk[0]); lab=d["parameters"]["POINT"]["LABELS"]["value"]
        VP=np.transpose(d["data"]["points"][:3],(2,1,0))
        if not all(k in lab for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]): continue
        li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
        caps=[cv2.VideoCapture(v) for v in tv[:n]]
        vN=int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT)); fps=caps[0].get(cv2.CAP_PROP_FPS) or 200
        step=max(1,int(round(fps/30))); idxs=list(range(0,min(vN,VP.shape[0]),step))[:120]
        for fi in idxs:
            dets=[]
            for cp in caps[:n]:
                cp.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cp.read()
                if not ok: dets.append(None); continue
                k,s=body(fr); dets.append(np.concatenate([k[int(np.argmax(s.mean(1)))],s[int(np.argmax(s.mean(1)))][:,None]],1) if len(k) else None)
            if sum(x is not None for x in dets)<4: continue
            def uvs(j): return np.array([dets[i][j,:2] if dets[i] is not None else [np.nan]*2 for i in range(n)])
            def wj(j): return np.array([dets[i][j,2] if dets[i] is not None else 0. for i in range(n)])
            vh,vk,va=VP[fi][li['LEFT_HIP']],VP[fi][li['LEFT_KNEE']],VP[fi][li['LEFT_ANKLE']]
            if not (np.any(vh) and np.any(vk) and np.any(va)): continue   # skip missing markers (0,0,0)
            gk=ang(vh,vk,va)
            if not np.isfinite(gk): continue
            for nm,mt in [('reproj',re),('distance',de),('ransac','ransac')]:
                H=tri(cams[:n],uvs(COCO['Lhip']),wj(COCO['Lhip']),mt)
                K=tri(cams[:n],uvs(COCO['Lknee']),wj(COCO['Lknee']),mt)
                A=tri(cams[:n],uvs(COCO['Lank']),wj(COCO['Lank']),mt)
                if H is None or K is None or A is None: continue
                mk_=ang(H,K,A)
                if np.isfinite(mk_) and np.isfinite(gk): perr[nm].append(abs(mk_-gk))
        for cp in caps: cp.release()
        log(f"[{pid}] trial {os.path.basename(trial)} done, samples reproj={len(perr['reproj'])}")
    if not perr['ransac']: return None
    return {'reproj':float(np.mean(perr['reproj'])), 'distance':float(np.mean(perr['distance'])),
            'ransac':float(np.mean(perr['ransac'])), 'n':len(perr['ransac'])}

def main():
    open(OUT,"w").close()
    log(f"=== BioCV orchestrator start {time.strftime('%H:%M')} ===")
    results={}; t0=time.time(); GATE_OK=None
    while time.time()-t0 < 9*3600:            # 9h budget
        # move any COMPLETED tar (P*.tar in Downloads is final; in-progress ones are .crdownload)
        import shutil
        for tar in glob.glob(f"{DL}/P*.tar"):
            base=os.path.basename(tar)
            try: shutil.move(tar, f"{BIO}/{base}"); log("moved",base)
            except Exception as e: log("move fail",base,repr(e)[:80])
        # extract + analyze
        for pid in TARGETS:
            if pid in results: continue
            extracted = bool(glob.glob(f"{BIO}/{pid}/**/*.mp4", recursive=True))
            if not extracted and os.path.exists(f"{BIO}/{pid}.tar"):
                log(f"extracting {pid}.tar via tarfile ...")
                try:
                    import tarfile
                    with tarfile.open(f"{BIO}/{pid}.tar") as t: t.extractall(BIO)
                    extracted = bool(glob.glob(f"{BIO}/{pid}/**/*.mp4", recursive=True))
                    log(f"  extracted={extracted}")
                except Exception: log(f"extract fail {pid}\n"+traceback.format_exc())
            if extracted:
                try:
                    log(f"--- analyzing {pid} ---"); r=analyze(pid)
                    if r: results[pid]=r; log(f"[{pid}] knee MAE reproj(single)={r['reproj']:.2f} distance(single)={r['distance']:.2f} RANSAC(multi)={r['ransac']:.2f} (n={r['n']})")
                    else: results[pid]={'reproj':float('nan'),'distance':float('nan'),'n':0}; log(f"[{pid}] no result")
                except Exception: log(f"[{pid}] ERROR\n"+traceback.format_exc()); results[pid]={'reproj':float('nan'),'distance':float('nan'),'n':0}
                # sanity gate after first real result
                if GATE_OK is None and results[pid]['n']>0:
                    r=results[pid]; GATE_OK = r['ransac']<25   # RANSAC (multi-outlier) should give sane angles if pipeline OK
                    if not GATE_OK: log(f"!!! GATE FAIL: RANSAC knee MAE {r['ransac']:.1f}>25deg -> pipeline still broken (not just single-vs-multi removal). Stopping."); break
        # aggregate
        good={k:v for k,v in results.items() if v['n']>0}
        if good:
            rr=np.mean([v['reproj'] for v in good.values()]); dd=np.mean([v['distance'] for v in good.values()]); ra=np.mean([v['ransac'] for v in good.values()])
            log(f"AGGREGATE N={len(good)}: knee MAE reproj-single={rr:.2f}  distance-single={dd:.2f}  RANSAC-multi={ra:.2f}")
        if GATE_OK is False: break
        if all(p in results for p in TARGETS): log("all targets processed"); break
        time.sleep(60)
    log("\n=== FINAL ===")
    for pid,v in results.items():
        if v['n']>0: log(f"{pid}: reproj-single={v['reproj']:.2f} distance-single={v['distance']:.2f} RANSAC-multi={v['ransac']:.2f} n={v['n']}")
    good={k:v for k,v in results.items() if v['n']>0}
    if good:
        rr=np.mean([v['reproj'] for v in good.values()]); dd=np.mean([v['distance'] for v in good.values()]); ra=np.mean([v['ransac'] for v in good.values()])
        log(f"OVERALL N={len(good)}: reproj-single {rr:.2f} | distance-single {dd:.2f} | RANSAC-multi {ra:.2f} deg")
        log("Interpretation: if RANSAC-multi << single-removal methods -> confirms real gait data has MULTIPLE")
        log("confidently-wrong (wrong-person) detections/joint that single-removal (ROWV/Pose2Sim) cannot handle.")
    log("CAVEAT: i<->i sync assumed; CPU; knee angle only; treat as preliminary until sync verified + N>=10.")

try: main()
except Exception:
    with open(OUT,"a") as f: f.write("FATAL\n"+traceback.format_exc())
