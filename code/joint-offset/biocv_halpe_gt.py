"""Add the reference foot markers to the HALPE-26 cache.

`biocv_detect_halpe.py` detects 26 keypoints but copies its ground truth from `_cache_balanced`,
whose `gt` dict holds only the twelve COCO-mapped Vicon markers. The detected toe and heel therefore
have nothing to be scored against. This pass reads them from the trial's own `markers.c3d` and
writes them into the cache under the HALPE indices they correspond to.

The frame index `fi` stored in the cache indexes `markers.c3d` directly -- `biocv_detect.py` builds
`gtw` as `VP[fi][vidx[c]]` from the same array -- so the merge is a lookup, not a re-alignment. That
claim is CHECKED rather than assumed: for every frame this script re-derives the twelve markers
already in the cache and refuses to write unless all of them match bit for bit. A silent
off-by-one here would put the foot a stride away from the leg and every dorsiflexion number
downstream would be wrong in a way no later check could see.

Correspondence, fixed here:

    HALPE 20 / 21  L / R big toe  ->  LTOE   / RTOE     (primary)
    HALPE 24 / 25  L / R heel     ->  HEEL_L / HEEL_R   (declared sensitivity)

Both are markers on the foot rather than anatomical centres, exactly as the twelve already in use
are markers rather than the keypoints a detector regresses; the offset between the two definitions
is the subject of this paper, not a defect of this mapping.

-> rewrites D:/BioCV/_cache_halpe/*.pkl in place, adding gt keys 20, 21, 24, 25
"""
import glob
import io
import os
import pickle
import sys

import ezc3d
import numpy as np

CACHE = "D:/BioCV/_cache_halpe"
LOG = "D:/BioCV/HALPE_GT_MERGE.txt"

# What is already in the cache, used only to prove the frame alignment.
COCO2VIC = {5: "LEFT_SHO", 6: "RIGHT_SHO", 7: "LEFT_ELBOW", 8: "RIGHT_ELBOW",
            9: "LEFT_WRIST", 10: "RIGHT_WRIST", 11: "LEFT_HIP", 12: "RIGHT_HIP",
            13: "LEFT_KNEE", 14: "RIGHT_KNEE", 15: "LEFT_ANKLE", 16: "RIGHT_ANKLE"}

FOOT = {20: "LTOE", 21: "RTOE", 24: "HEEL_L", 25: "HEEL_R"}

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


def merge(pkl):
    D = pickle.load(open(pkl, "rb"))
    pid, trial = D["pid"], D["trial"]
    c3d = f"D:/BioCV/{pid}/{trial}/markers.c3d"
    if not os.path.exists(c3d):
        return pid, trial, "no markers.c3d", 0
    d = ezc3d.c3d(c3d)
    lab = d["parameters"]["POINT"]["LABELS"]["value"]
    missing = [v for v in FOOT.values() if v not in lab]
    if missing:
        return pid, trial, "reference lacks " + ",".join(missing), 0
    VP = np.transpose(d["data"]["points"][:3], (2, 1, 0))       # (F, marker, xyz) mm
    fidx = {k: lab.index(v) for k, v in FOOT.items()}
    cidx = {k: lab.index(v) for k, v in COCO2VIC.items() if v in lab}

    # --- alignment proof, before anything is written ---
    for fr in D["frames"]:
        fi = fr["fi"]
        if fi >= VP.shape[0]:
            return pid, trial, f"frame {fi} past the c3d ({VP.shape[0]})", 0
        for k, vi in cidx.items():
            if k not in fr["gt"]:
                continue
            if not np.array_equal(np.asarray(fr["gt"][k], float), VP[fi][vi].astype(float)):
                return pid, trial, f"frame {fi} marker {COCO2VIC[k]} disagrees -- NOT ALIGNED", 0

    n = 0
    for fr in D["frames"]:
        fi = fr["fi"]
        for k, vi in fidx.items():
            p = VP[fi][vi]
            if np.any(p):                       # a zeroed row is an unlabelled gap, not a position
                fr["gt"][k] = p.copy()
        n += 1
    pickle.dump(D, open(pkl, "wb"))
    return pid, trial, "ok", n


def main():
    files = sorted(glob.glob(f"{CACHE}/*.pkl"))
    out(f"ADDING REFERENCE FOOT MARKERS TO {len(files)} HALPE-26 TRIALS")
    out("")
    out("Each trial's twelve cached markers are re-derived from markers.c3d and compared bit for")
    out("bit before the foot markers are written; a mismatch means the frame index does not line")
    out("up and the trial is left untouched.")
    out("")
    ok = bad = 0
    for f in files:
        pid, trial, status, n = merge(f)
        if status == "ok":
            ok += 1
        else:
            bad += 1
            out(f"  [SKIPPED] {pid} {trial}: {status}")
    out("")
    out(f"{ok} trial(s) merged, {bad} skipped")
    have = 0
    for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
        D = pickle.load(open(f, "rb"))
        have += sum(1 for fr in D["frames"] if all(k in fr["gt"] for k in FOOT))
    out(f"{have} frame(s) now carry all four reference foot markers")
    io.open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nWROTE", LOG)
    if bad and ok == 0:
        sys.exit("nothing merged")


if __name__ == "__main__":
    main()
