"""Does the joint-centre offset belong to the detector, or to the keypoint convention?

The paper's central claim is that most of the position metric at hip and knee is a fixed
joint-centre offset rather than triangulation error. Everything rests on one detector. If the
offset is a property of RTMPose, the claim is about RTMPose; if it is a property of the COCO-17
convention, it applies to every pipeline scored on those keypoints, which is the only result here
that generalises past this rig.

`biocv_detect_rtmo.py` re-detected EXACTLY the cached frames with RTMO-m -- one-stage, no separate
person detector, different training -- leaving ground truth, calibration, association and the
COCO-to-Vicon mapping untouched. This script repeats the bias/variance decomposition of
biocv_gt_offset.py on both caches and compares.

THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.

  (1) SHARE. If the bias share at hip and knee is above 60% under RTMO as well, the offset is not
      detector-specific and Section 3.1's claim may be stated for the keypoint convention rather
      than for RTMPose. If it falls below 60%, the claim must be scoped to RTMPose and the paper
      must say so.

  (2) MAGNITUDE. If the per-joint bias magnitudes agree within a factor of two, the two detectors
      disagree with the marker-based model by a similar amount. If they do not, the size of the
      effect is detector-specific even if its dominance is not.

  (3) DIRECTION -- the sharpest of the three. The cosine between the two detectors' mean offset
      vectors, per participant and joint. If it is near +1, both detectors place the joint centre
      in the same wrong place, and a comparison BETWEEN detectors on this metric is contaminated
      the same way a comparison between pipeline variants is. If it is near zero or negative, the
      offset direction is detector-specific, which means the per-joint sign structure this paper
      reports would not reproduce under another detector -- a sharper warning than the paper
      currently makes, and one that must be reported whichever way the first two tests fall.

  (4) A NULL RESULT IS PUBLISHABLE HERE. If RTMO's detections are too sparse to compare (fewer
      than 8 participants with usable frames at a joint), the comparison is reported as not
      possible rather than as agreement.

Both caches are scored on the same arm: no rejection, confidence weighting, weighted DLT --
the plainest pipeline, so the comparison is about detectors and not about triangulation choices.
Both are also distortion-corrected by `biocv_make_undist_cache.py`, as every published result is;
comparing a corrected cache with a raw one would put the distortion difference into the detector
contrast, at exactly the near-camera residuals distortion moves most.

-> D:/BioCV/BIOCV_DETECTOR_TRANSFER.txt
"""
import glob
import io
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_DETECTOR_TRANSFER.txt")
CACHES = {"RTMPose (two-stage)": "D:/BioCV/_cache_undist",
          "RTMO (one-stage)": "D:/BioCV/_cache_rtmo_undist"}
SIDES = {"L": (11, 13, 15), "R": (12, 14, 16)}
JNAME = {11: "L-hip", 12: "R-hip", 13: "L-knee", 14: "R-knee", 15: "L-ankle", 16: "R-ankle"}

CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


def collect(cache):
    """err[(pid, joint)] -> list of 3D error vectors, plain arm: no rejection, confidence weights."""
    err = {}
    for f in sorted(glob.glob(f"{cache}/*.pkl")):
        D = pickle.load(open(f, "rb"))
        pid = D["pid"]
        cams = cams_for(pid)
        for fr in D["frames"]:
            det, gt = fr["det"], fr["gt"]
            for side, joints in SIDES.items():
                for j in joints:
                    if j not in gt or not np.any(gt[j]):
                        continue
                    vi = [i for i, dd in enumerate(det)
                          if dd is not None and np.isfinite(dd[j, 0]) and dd[j, 2] > 0]
                    if len(vi) < MIN_CAM:
                        continue
                    uvs = np.array([det[i][j, :2] for i in vi])
                    w = np.array([det[i][j, 2] for i in vi])
                    X = R.triangulate_wdlt([cams[i] for i in vi], uvs, w)
                    err.setdefault((pid, j), []).append(X - gt[j])
    return {k: np.asarray(v, float) for k, v in err.items()}


L = []


def out(s):
    print(s)
    L.append(s)


out("DOES THE JOINT-CENTRE OFFSET BELONG TO THE DETECTOR OR TO THE KEYPOINT CONVENTION?")
out("")
out("The same frames, ground truth, calibration and association rule; only the detector differs.")
out("Both scored on the plainest arm: no rejection, confidence weights, weighted DLT.")
out("")

if not glob.glob(f"{CACHES['RTMO (one-stage)']}/*.pkl"):
    out("The RTMO cache is empty -- biocv_detect_rtmo.py has not been run. No comparison made.")
    io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
    raise SystemExit("RTMO cache empty")

E = {name: collect(path) for name, path in CACHES.items()}
names = list(CACHES)
a, b = E[names[0]], E[names[1]]

out(f"{'joint':>9}{'':4}{names[0]:>28}{'':4}{names[1]:>24}")
out(f"{'':9}{'':4}{'bias mm':>9}{'random':>8}{'share':>7}{'':4}{'bias mm':>9}{'random':>8}{'share':>7}")
summary = {}
for j in sorted(JNAME):
    row = []
    for E_ in (a, b):
        pids = sorted({p for (p, jj) in E_ if jj == j})
        if not pids:
            row.append((np.nan, np.nan, 0, np.nan))
            continue
        bias, share, resid, n = [], [], [], 0
        for p in pids:
            e = E_[(p, j)]
            m = e.mean(axis=0)
            mse = (e ** 2).sum(axis=1).mean()
            bias.append(np.linalg.norm(m))
            # The random half, printed because the manuscript quotes it: a share can fall
            # either because the bias shrank or because the noise grew, and only this tells
            # the reader which happened.
            resid.append(float(np.sqrt(((e - m) ** 2).sum(axis=1).mean())))
            share.append(float((m @ m) / mse) if mse > 0 else np.nan)
            n += len(e)
        row.append((np.mean(bias), 100 * np.nanmean(share), n, np.mean(resid)))
    summary[j] = row
    out(f"{JNAME[j]:>9}{'':4}{row[0][0]:>9.1f}{row[0][3]:>8.1f}{row[0][1]:>6.0f}%"
        f"{'':4}{row[1][0]:>9.1f}{row[1][3]:>8.1f}{row[1][1]:>6.0f}%")
out("")

out("DIRECTION: cosine between the two detectors' mean offset vectors, per participant and joint.")
out(f"{'joint':>9}{'participants':>14}{'mean cos':>10}{'min':>8}{'max':>8}")
cos_all = {}
for j in sorted(JNAME):
    shared = sorted({p for (p, jj) in a if jj == j} & {p for (p, jj) in b if jj == j})
    cs = []
    for p in shared:
        u, v = a[(p, j)].mean(axis=0), b[(p, j)].mean(axis=0)
        nu, nv = np.linalg.norm(u), np.linalg.norm(v)
        if nu > 1e-9 and nv > 1e-9:
            cs.append(float(u @ v / (nu * nv)))
    cos_all[j] = cs
    if cs:
        out(f"{JNAME[j]:>9}{len(cs):>14}{np.mean(cs):>10.2f}{min(cs):>8.2f}{max(cs):>8.2f}")
    else:
        out(f"{JNAME[j]:>9}{0:>14}{'--':>10}{'--':>8}{'--':>8}")
out("")

# --- the pre-registered verdicts, applied ---
hipknee = [j for j in JNAME if "ankle" not in JNAME[j]]
share_b = np.mean([summary[j][1][1] for j in hipknee])
ratio = np.mean([summary[j][1][0] / summary[j][0][0] for j in hipknee
                 if summary[j][0][0] > 0])
cos_hk = np.mean([c for j in hipknee for c in cos_all[j]]) if any(cos_all[j] for j in hipknee) else np.nan
enough = min(len(cos_all[j]) for j in JNAME) >= 8

out("=== VERDICTS, against the rule fixed in this file's header ===")
out(f"(1) SHARE at hip and knee under RTMO: {share_b:.0f}%  ->  "
    + ("NOT detector-specific; the claim may be stated for the keypoint convention"
       if share_b > 60 else "detector-specific; the claim must be scoped to RTMPose"))
out(f"(2) MAGNITUDE ratio RTMO/RTMPose at hip and knee: {ratio:.2f}x  ->  "
    + ("within a factor of two" if 0.5 <= ratio <= 2.0 else "NOT within a factor of two"))
out(f"(3) DIRECTION, mean cosine at hip and knee: {cos_hk:+.2f}  ->  "
    + ("same wrong place; between-detector comparison is contaminated the same way"
       if cos_hk > 0.5 else
       "offset direction differs by detector; the per-joint sign structure would not reproduce"))
out(f"(4) COVERAGE: {'sufficient' if enough else 'INSUFFICIENT -- treat the comparison as not possible'}"
    f" (fewest participants at any joint: {min(len(cos_all[j]) for j in JNAME)})")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
