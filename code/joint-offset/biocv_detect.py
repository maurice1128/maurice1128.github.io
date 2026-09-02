"""
STEP 1 of the real-GT decisive test for the asymmetry claim (Measurement paper).

Runs RTMPose ONCE over BioCV P06/P10 (all WALK trials with Vicon markers), does
GT-projection person association per camera (kills the "confident wrong person"
problem, so the 2D is as clean as AIST++'s), and caches per-trial:
  - associated 17-keypoint COCO detections (x,y,score) for each of 9 cameras
  - Vicon GT 3D (mm) for the joints we compare
This is the SLOW part (CPU RTMPose). Analysis (biocv_severe.py) reads the cache
and is instant, so bins/metrics/joints can be re-tuned without re-detecting.

Cache -> D:/BioCV/_cache/{pid}_{trial}.pkl
"""
import glob, os, sys, pickle, numpy as np, cv2, ezc3d
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
DEVICE = os.environ.get("BIOCV_DEVICE", "cuda")   # cuda | cpu
if DEVICE == "cuda":
    import cuda_init  # noqa  (must precede rtmlib/onnxruntime import)
from rtmlib import Body

# --- config via env: BIOCV_MODE (lightweight|balanced), BIOCV_FRAMES per trial ---
MODE = os.environ.get("BIOCV_MODE", "balanced")
FRAMES_PER_TRIAL = int(os.environ.get("BIOCV_FRAMES", "45"))
ASSOC_MAXPX = 80.0             # reject a camera if best person's median skel dist > this
CACHE = f"D:/BioCV/_cache_{MODE}"; os.makedirs(CACHE, exist_ok=True)
LOG = f"D:/BioCV/DETECT_LOG_{MODE}.txt"

def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True)
    open(LOG, "a", encoding="utf-8").write(s + "\n")

# COCO17 index -> BioCV Vicon joint-centre label (12 body joints; face absent in GT)
COCO2VIC = {5:"LEFT_SHO",6:"RIGHT_SHO",7:"LEFT_ELBOW",8:"RIGHT_ELBOW",
            9:"LEFT_WRIST",10:"RIGHT_WRIST",11:"LEFT_HIP",12:"RIGHT_HIP",
            13:"LEFT_KNEE",14:"RIGHT_KNEE",15:"LEFT_ANKLE",16:"RIGHT_ANKLE"}

body = Body(mode=MODE, backend="onnxruntime", device=DEVICE)

def associate(persons_kp, persons_sc, gt_uv, valid):
    """Pick the detected person whose visible COCO joints best match projected GT.
    persons_kp:(P,17,2) persons_sc:(P,17) gt_uv:(17,2) valid:bool(17). Returns
    (17,3) [x,y,score] of chosen person, or None."""
    if len(persons_kp) == 0 or valid.sum() < 4:
        return None
    best, bestd = None, 1e18
    for kp, sc in zip(persons_kp, persons_sc):
        d = np.linalg.norm(kp[valid] - gt_uv[valid], axis=1)
        md = np.median(d)
        if md < bestd:
            bestd, best = md, np.concatenate([kp, sc[:, None]], 1)
    return best if bestd <= ASSOC_MAXPX else None

def run_trial(pid, cams, trial):
    name = os.path.basename(trial)
    out = f"{CACHE}/{pid}_{name}.pkl"
    if os.path.exists(out):
        log(f"  [skip cached] {name}"); return
    d = ezc3d.c3d(f"{trial}/markers.c3d")
    lab = d["parameters"]["POINT"]["LABELS"]["value"]
    if not all(v in lab for v in COCO2VIC.values()):
        log(f"  [skip: missing GT joints] {name}"); return
    VP = np.transpose(d["data"]["points"][:3], (2, 1, 0))   # (F,marker,xyz) mm
    vidx = {c: lab.index(v) for c, v in COCO2VIC.items()}
    vids = sorted(glob.glob(f"{trial}/*.mp4"))[:len(cams)]
    n = len(vids)
    caps = [cv2.VideoCapture(v) for v in vids]
    F = min(int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT)), VP.shape[0])
    # frames where all needed GT joints are present, spread evenly, capped
    valid = [fi for fi in range(F)
             if all(np.any(VP[fi][vidx[c]]) for c in COCO2VIC)]
    if len(valid) > FRAMES_PER_TRIAL:
        step = len(valid) / FRAMES_PER_TRIAL
        valid = [valid[int(i * step)] for i in range(FRAMES_PER_TRIAL)]
    sel = set(valid)
    frames_out = []
    fi = -1
    while True:
        grabbed = [c.grab() for c in caps]
        fi += 1
        if fi >= F or not all(grabbed):
            break
        if fi not in sel:
            continue
        gtw = {c: VP[fi][vidx[c]] for c in COCO2VIC}
        cams_det = []
        for i, cap in enumerate(caps):
            ok, fr = cap.retrieve()
            if not ok:
                cams_det.append(None); continue
            # projected GT skeleton for association
            gt_uv = np.zeros((17, 2)); valid = np.zeros(17, bool)
            for c in COCO2VIC:
                try:
                    gt_uv[c] = cams[i].project(gtw[c]); valid[c] = True
                except Exception:
                    pass
            kp, sc = body(fr)
            cams_det.append(associate(np.asarray(kp), np.asarray(sc), gt_uv, valid))
        frames_out.append({"fi": fi,
                            "gt": {c: gtw[c].copy() for c in COCO2VIC},
                            "det": cams_det})
    for c in caps: c.release()
    pickle.dump({"pid": pid, "trial": name, "n_cams": n, "frames": frames_out},
                open(out, "wb"))
    log(f"  [done] {name}: {len(frames_out)} frames cached")

def main():
    open(LOG, "a").write("\n===== DETECT RUN =====\n")
    # subjects: env BIOCV_PIDS (comma-sep) or auto-scan extracted D:/BioCV/P?? with WALK trials
    env_pids = os.environ.get("BIOCV_PIDS", "").strip()
    if env_pids:
        pids = [p.strip() for p in env_pids.split(",") if p.strip()]
    else:
        pids = sorted(os.path.basename(d) for d in glob.glob("D:/BioCV/P??")
                      if glob.glob(f"{d}/*WALK*") and os.path.isdir(f"D:/BioCV/_calib/{os.path.basename(d)}"))
    log(f"subjects: {pids}")
    for pid in pids:
        cams, _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
        trials = [t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*"))
                  if "ML" not in os.path.basename(t) and glob.glob(f"{t}/*marker*.c3d")]
        log(f"{pid}: {len(trials)} trials, {len(cams)} cams")
        for t in trials:
            run_trial(pid, cams, t)
    log("ALL DONE")

if __name__ == "__main__":
    main()
