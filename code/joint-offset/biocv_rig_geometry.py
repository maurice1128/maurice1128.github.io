"""Characterise the camera rig, so Section 2.1's geometry figures have a producer.

Section 2.1 describes nine cameras "1.07-1.55 m above the floor" on a non-circular ring with
"per-camera distance from centroid 3.0-6.0 m", focal lengths "1235-1241 px and two at 1643 and
1650 px, a 1.34x spread", and radial distortion "k1 in [-0.175, -0.142], k2 in [+0.072, +0.135];
tangential terms are zero". Those numbers were read off the calibration files by hand and had no
artefact behind them.

Two corrections since the first version of this script:

  * it globbed D:/BioCV/P*/*.calib, which is the ORIGINAL `mocAligned` calibration. The analysis
    reads D:/BioCV/_calib/P*/*.calib -- `mocAligned2`, the updated calibration Section 2.1 says
    was used. Both round to the same height and radius, but characterising a rig from a
    calibration the analysis did not use is not a defensible provenance chain.
  * it emitted only heights and radii, so the focal lengths and distortion coefficients quoted in
    the same paragraph remained unsourced.

Camera centres are C = -R^T t, in the calibration's own units (mm), reported here in metres. The
ring radius is the horizontal distance from the mean horizontal position of the nine centres,
which is what "distance from centroid" means in the manuscript.

Output: D:/BioCV/BIOCV_RIG.txt
"""
import glob
import io
import os
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
from biocv_calib import load_biocv_cameras

OUTF = "D:/BioCV/BIOCV_RIG.txt"
CALIB_ROOT = "D:/BioCV/_calib"

L = []


def out(s):
    print(s)
    L.append(s)


dirs = sorted(d for d in glob.glob(os.path.join(CALIB_ROOT, "P*"))
              if os.path.isdir(d) and glob.glob(os.path.join(d, "*.calib")))
if not dirs:
    raise SystemExit("no participant calibration directories found under " + CALIB_ROOT)


def analysed_participants():
    """The participants that actually contributed data, read from the per-participant means.

    The archive holds calibrations for all fifteen; trial data reached us for eleven. Section 2.1
    quotes distortion ranges "across all 99 calibrations used here", and a range computed over
    all 135 archived calibrations is not that range. Which eleven is not typed here either --
    it is read from the accumulators the tests run on.
    """
    import pickle
    acc = {}
    for f in ("D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl", "D:/BioCV/_persubj_v2.pkl"):
        try:
            acc.update(pickle.load(open(f, "rb")))
        except OSError:
            pass
    pids = set()
    for v in acc.values():
        pids |= set(v)
    return {str(p) for p in pids}


USED = analysed_participants()

out("CAMERA RIG GEOMETRY AND LENS PARAMETERS")
out("Source: the updated `mocAligned2` calibration in " + CALIB_ROOT + ", which is the")
out("calibration the analysis reads. Camera centres C = -R^T t; the files are in millimetres and")
out("distances are reported here in metres. 'radius' is the horizontal distance from the mean")
out("horizontal position of that participant's nine camera centres.")
out("")
out(f"{'participant':<13}{'n':>3}{'h min':>9}{'h max':>9}{'r min':>9}{'r med':>9}{'r max':>9}")

H, R, F, K1, K2, TAN, N = [], [], [], [], [], [], set()
uK1, uK2, uF, used_dirs = [], [], [], []
for d in dirs:
    cams, files = load_biocv_cameras(d)
    if os.path.basename(d) in USED:
        used_dirs.append(os.path.basename(d))
        for c in cams:
            _d = np.asarray(c.dist, float).ravel()
            uK1.append(float(_d[0]))
            uK2.append(float(_d[1]))
            _K = np.asarray(c.K, float)
            uF += [float(_K[0, 0]), float(_K[1, 1])]
    C = np.array([np.asarray(c.C).ravel() for c in cams], float) / 1000.0
    r = np.linalg.norm(C[:, :2] - C[:, :2].mean(0), axis=1)
    H += list(C[:, 2])
    R += list(r)
    N.add(len(cams))
    for c in cams:
        K = np.asarray(c.K, float)
        F += [float(K[0, 0]), float(K[1, 1])]
        dist = np.asarray(c.dist, float).ravel()
        K1.append(float(dist[0]))
        K2.append(float(dist[1]))
        if len(dist) >= 4:
            TAN += [float(dist[2]), float(dist[3])]
    out(f"{os.path.basename(d):<13}{len(cams):>3}{C[:, 2].min():>9.3f}{C[:, 2].max():>9.3f}"
        f"{r.min():>9.3f}{np.median(r):>9.3f}{r.max():>9.3f}")

lo = [f for f in F if f < 1400]
hi = [f for f in F if f >= 1400]
out("")
out(f"participants: {len(dirs)}    cameras per participant: {sorted(N)}    "
    f"calibrations: {len(dirs) * max(N)}")
out(f"height above floor:      {min(H):.2f} to {max(H):.2f} m")
out(f"radius from centroid:    {min(R):.1f} to {max(R):.1f} m   (median {np.median(R):.2f} m)")
out(f"ring non-circularity:    {max(R) / min(R):.2f}x")
out("")
out(f"focal length, lower group ({len(lo) // 2} cameras per participant): "
    f"{min(lo):.0f} to {max(lo):.0f} px")
out(f"focal length, upper group ({len(hi) // 2} cameras per participant): "
    f"{min(hi):.0f} to {max(hi):.0f} px")
out(f"focal-length spread:     {max(F) / min(F):.3f}x")
out("")
out(f"radial k1:               {min(K1):+.4f} to {max(K1):+.4f}")
out(f"radial k2:               {min(K2):+.4f} to {max(K2):+.4f}")
out(f"tangential p1, p2:       {min(TAN):+.4f} to {max(TAN):+.4f}"
    f"{'  (identically zero)' if max(abs(t) for t in TAN) == 0 else ''}")
out("")
out("=== RESTRICTED TO THE PARTICIPANTS ANALYSED ===")
out("The block above covers every archived calibration. Section 2.1 quotes these ranges as holding")
out("across the calibrations the analysis actually used, which is a smaller set, so they are")
out("recomputed over it here. Quote these.")
out("")
if used_dirs:
    out(f"participants analysed:   {len(used_dirs)} ({', '.join(sorted(used_dirs))})")
    out(f"calibrations used:       {len(uK1)}")
    out(f"radial k1:               {min(uK1):+.4f} to {max(uK1):+.4f}")
    out(f"radial k2:               {min(uK2):+.4f} to {max(uK2):+.4f}")
    _ulo = [f for f in uF if f < 1400]
    _uhi = [f for f in uF if f >= 1400]
    out(f"focal length, lower:     {min(_ulo):.0f} to {max(_ulo):.0f} px")
    out(f"focal length, upper:     {min(_uhi):.0f} to {max(_uhi):.0f} px")
    out(f"focal-length spread:     {max(uF) / min(uF):.3f}x")
else:
    out("could not identify the analysed participants from the per-participant means; the")
    out("manuscript must then quote the all-participant ranges above and say so.")
out("")
out("These are the figures Section 2.1 quotes for the rig. A value quoted in the manuscript must")
out("lie inside the corresponding interval printed here.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
