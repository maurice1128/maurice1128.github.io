"""Re-detect the SAME frames with a second, architecturally different pose estimator.

Every result in this paper rests on one detector, and the central claim -- that most of the
position metric at hip and knee is a fixed joint-centre offset rather than triangulation error --
would be far weaker if that offset were a property of RTMPose rather than of the keypoint
convention. Reviewers asked for this directly, and it needs no new data collection.

The current pipeline is two-stage: YOLOX-m finds the person, RTMPose-m regresses COCO-17 keypoints
by coordinate classification. This script runs RTMO-m instead -- one-stage, no separate person
detector, a different training regime -- on EXACTLY the frames already cached, read from
`_cache_balanced` so the two detectors are compared frame for frame rather than on two samples.

Ground truth, camera calibration, the person-association rule and the COCO-to-Vicon mapping are
taken unchanged from biocv_detect.py, so the only thing that differs between the two caches is the
detector.

-> D:/BioCV/_cache_rtmo/*.pkl   (same structure as _cache_balanced)
"""
import glob
import io
import os
import pickle
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
DEVICE = os.environ.get("BIOCV_DEVICE", "cuda")
if DEVICE == "cuda":
    import cuda_init  # noqa  (must precede rtmlib/onnxruntime import)
from rtmlib import Body

from biocv_calib import load_biocv_cameras

SRC = "D:/BioCV/_cache_balanced"
DST = "D:/BioCV/_cache_rtmo"
LOG = "D:/BioCV/DETECT_LOG_rtmo.txt"
PROG = "D:/BioCV/_rtmo_progress.txt"
ASSOC_MAXPX = 80.0
os.makedirs(DST, exist_ok=True)

# Unchanged from biocv_detect.py.
COCO2VIC = {5: "LEFT_SHO", 6: "RIGHT_SHO", 7: "LEFT_ELBOW", 8: "RIGHT_ELBOW",
            9: "LEFT_WRIST", 10: "RIGHT_WRIST", 11: "LEFT_HIP", 12: "RIGHT_HIP",
            13: "LEFT_KNEE", 14: "RIGHT_KNEE", 15: "LEFT_ANKLE", 16: "RIGHT_ANKLE"}

body = Body(pose="rtmo", mode="balanced", backend="onnxruntime", device=DEVICE)


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    io.open(LOG, "a", encoding="utf-8").write(s + "\n")


def associate(persons_kp, persons_sc, gt_uv, valid):
    """Identical rule to biocv_detect.py: the detected person closest to the projected GT."""
    if len(persons_kp) == 0 or valid.sum() < 4:
        return None
    best, bestd = None, 1e18
    for kp, sc in zip(persons_kp, persons_sc):
        d = np.linalg.norm(kp[valid] - gt_uv[valid], axis=1)
        md = np.median(d)
        if md < bestd:
            bestd, best = md, np.concatenate([kp, sc[:, None]], 1)
    return best if bestd <= ASSOC_MAXPX else None


CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


def redo(src_pkl):
    D = pickle.load(open(src_pkl, "rb"))
    pid, trial = D["pid"], D["trial"]
    out = f"{DST}/{pid}_{trial}.pkl"
    if os.path.exists(out):
        log(f"  [skip cached] {pid} {trial}")
        return
    cams = cams_for(pid)
    tdir = f"D:/BioCV/{pid}/{trial}"
    vids = sorted(glob.glob(f"{tdir}/*.mp4"))[:D["n_cams"]]
    if len(vids) < D["n_cams"]:
        log(f"  [skip: {len(vids)} videos for {D['n_cams']} cameras] {pid} {trial}")
        return
    want = {fr["fi"]: fr["gt"] for fr in D["frames"]}
    caps = [cv2.VideoCapture(v) for v in vids]
    frames_out = []
    fi = -1
    hi = max(want)
    while fi < hi:
        grabbed = [c.grab() for c in caps]
        fi += 1
        if not all(grabbed):
            break
        if fi not in want:
            continue
        gtw = want[fi]
        cams_det = []
        for i, cap in enumerate(caps):
            ok, fr = cap.retrieve()
            if not ok:
                cams_det.append(None)
                continue
            gt_uv = np.zeros((17, 2))
            valid = np.zeros(17, bool)
            for c in COCO2VIC:
                try:
                    gt_uv[c] = cams[i].project(gtw[c])
                    valid[c] = True
                except Exception:
                    pass
            kp, sc = body(fr)
            cams_det.append(associate(np.asarray(kp), np.asarray(sc), gt_uv, valid))
        frames_out.append({"fi": fi, "gt": {c: gtw[c].copy() for c in gtw}, "det": cams_det})
    for c in caps:
        c.release()
    pickle.dump({"pid": pid, "trial": trial, "n_cams": D["n_cams"], "frames": frames_out},
                open(out, "wb"))
    log(f"  [done] {pid} {trial}: {len(frames_out)}/{len(want)} frames")


def main():
    io.open(LOG, "a", encoding="utf-8").write("\n===== RTMO RE-DETECT =====\n")
    src = sorted(glob.glob(f"{SRC}/*.pkl"))
    log(f"{len(src)} cached trials to re-detect with RTMO-m (one-stage)")
    io.open(PROG, "w").write("start\n")
    t0 = time.time()
    for n, f in enumerate(src, 1):
        io.open(PROG, "a").write(f"trial {n}/{len(src)} t={time.time()-t0:.0f}s\n")
        try:
            redo(f)
        except Exception as e:                       # one bad trial must not lose the rest
            log(f"  [ERROR] {os.path.basename(f)}: {e}")
    log("ALL DONE")


if __name__ == "__main__":
    main()
