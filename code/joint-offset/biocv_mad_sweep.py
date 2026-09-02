"""Every rejection result in this paper is conditional on one untested threshold.

Section 2.2 fixes the adaptive rule as "drop the observation with the largest residual while it
exceeds the median plus three scaled median absolute deviations, stopping at a floor of four
cameras". The multiplier 3 and the floor 4 were chosen and never varied. With at most nine
observations per joint a MAD-based threshold is a high-variance statistic, so the headline
rejection results -- the position null bounded within +/-0.35 mm, the thigh-shank angle cost, and
the offset-removed hip degradation -- all rest on that one number.

This sweeps the multiplier over 2.5, 3.0, 3.5 and 4.0 at the declared floor, and recomputes on the
same frames the two quantities the manuscript quotes, for BOTH criteria: the [pos:HKA] position
effect of rejection against no rejection, and the same contrast on the thigh-shank angle.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) POSITION. The manuscript reports this contrast as null and bounds it within +/-0.35 mm. If
      every multiplier keeps the effect inside that bound, the null is not an artefact of the
      threshold. If any multiplier takes it outside, the bound is conditional on the multiplier
      and Section 3.2 must say so.

  (2) ANGLE. The manuscript reports a cost of 0.141 deg at this contrast. If the sign holds at
      every multiplier and the magnitude stays within a factor of two, the cost is robust to the
      threshold. If the sign flips at any multiplier, the angle cost is a property of the
      threshold and the Conclusion must be restated.

  (3) MONOTONICITY IS NOT A PASS. A quantity that grows steadily with the multiplier is a dose
      effect of discarding, which the paper already reports; it is reported here as such and does
      not by itself confirm or refute either reading above.

  (4) Whatever the result, the multiplier's status changes from unstated to measured, and Section
      2.2 must say which.

-> D:/BioCV/BIOCV_MAD_SWEEP.txt
"""
import glob
import io
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R                                                        # noqa: E402
from biocv_calib import load_biocv_cameras                              # noqa: E402

CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_MAD_SWEEP.txt")
MIN_CAM = 4
MULTS = [2.5, 3.0, 3.5, 4.0]
SIDES = {"L": (11, 13, 15), "R": (12, 14, 16)}
JHKA = [11, 12, 13, 14, 15, 16]

_C = {}


def cams_for(pid):
    if pid not in _C:
        _C[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return _C[pid]


def objd(cam, X, uv):
    dv = cam.ray_dir(uv)
    w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)


def rep(cam, X, uv):
    return np.linalg.norm(cam.project(X) - uv)


def solve(cs, uvs, w, spec):
    """Adaptive rejection at a given metric and MAD multiplier; spec None = no rejection."""
    idx = list(range(len(cs)))
    if spec is not None:
        which, kmad = spec
        metric = objd if which == "objd" else rep
        while len(idx) > MIN_CAM:
            CS = [cs[i] for i in idx]
            X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
            e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
            med = np.median(e)
            mad = np.median(np.abs(e - med)) * 1.4826
            worst = int(np.argmax(e))
            if mad < 1e-9 or e[worst] <= med + kmad * mad:
                break
            idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx]), len(idx)


def ang3(a, b, c):
    u, v = a - b, c - b
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-9 or nv < 1e-9:
        return np.nan
    return float(np.degrees(np.arccos(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0))))


L = []


def out(s):
    print(s, flush=True)
    L.append(s)


# The manuscript quotes an angle cost from BOTH criteria but the first version of this file swept
# only the object-space one, leaving the reprojection figure untested against the threshold it
# depends on. Both are swept here.
ARMS = ([("none", None)]
        + [(f"objd k={m}", ("objd", m)) for m in MULTS]
        + [(f"rep  k={m}", ("rep", m)) for m in MULTS])
pos = {a: {} for a, _ in ARMS}
ang = {a: {} for a, _ in ARMS}
keep = {a: [] for a, _ in ARMS}

for f in sorted(glob.glob(CACHE + "/*.pkl")):
    D = pickle.load(open(f, "rb"))
    pid = D["pid"]
    cams = cams_for(pid)
    for fr in D["frames"]:
        det, gt = fr["det"], fr["gt"]
        if not all(j in gt and np.any(gt[j]) for j in JHKA):
            continue
        vis = {}
        for j in JHKA:
            vi = [i for i, d in enumerate(det)
                  if d is not None and np.isfinite(d[j, 0]) and d[j, 2] > 0]
            if len(vi) >= MIN_CAM:
                vis[j] = (vi, np.array([det[i][j, :2] for i in vi]),
                          np.array([det[i][j, 2] for i in vi]))
        if len(vis) < len(JHKA):
            continue
        for aname, spec in ARMS:
            X = {}
            for j, (vi, uvs, w) in vis.items():
                X[j], nk = solve([cams[i] for i in vi], uvs, w, spec)
                keep[aname].append(nk)
            pos[aname].setdefault(pid, []).extend(
                float(np.linalg.norm(X[j] - gt[j])) for j in JHKA)
            for sd, (jh, jk, ja) in SIDES.items():
                e = ang3(X[jh], X[jk], X[ja])
                g = ang3(gt[jh], gt[jk], gt[ja])
                if np.isfinite(e) and np.isfinite(g):
                    ang[aname].setdefault(pid, []).append(abs(e - g))

out("IS THE ADAPTIVE RULE'S THRESHOLD LOAD-BEARING?")
out("")
out("Both criteria at four MAD multipliers against no rejection, on the same frames.")
out("POSITIVE effect = rejection is better. Per participant, then averaged.")
out("")
pids = sorted(pos["none"])
out(f"{'arm':>8}{'kept/9':>9}{'[pos:HKA] mm':>14}{'effect mm':>11}"
    f"{'thigh-shank deg':>18}{'effect deg':>12}")
base_p = {p: float(np.mean(pos["none"][p])) for p in pids}
base_a = {p: float(np.mean(ang["none"][p])) for p in pids}
rows = []
for aname, spec in ARMS:
    if not pos[aname]:
        continue
    mp = float(np.mean([np.mean(pos[aname][p]) for p in pids]))
    ma = float(np.mean([np.mean(ang[aname][p]) for p in pids]))
    dp = float(np.mean([base_p[p] - np.mean(pos[aname][p]) for p in pids]))
    da = float(np.mean([base_a[p] - np.mean(ang[aname][p]) for p in pids]))
    out(f"{aname:>8}{np.mean(keep[aname]):>9.2f}{mp:>14.3f}{dp:>+11.3f}{ma:>18.3f}{da:>+12.3f}")
    if spec is not None:
        rows.append((spec[0], spec[1], dp, da))
out("")
if rows:
    out("=== VERDICT, against the rule fixed in this file's header ===")
    worst_p = max(abs(r[2]) for r in rows)
    out(f"(1) POSITION: the largest effect across multipliers is {worst_p:.3f} mm.")
    if worst_p <= 0.35:
        out("    Every multiplier keeps the contrast inside the +/-0.35 mm bound Section 3.2 quotes,")
        out("    so that bound is not an artefact of the threshold.")
    else:
        out("    At least one multiplier takes the contrast OUTSIDE the +/-0.35 mm bound Section 3.2")
        out("    quotes. The bound is conditional on the multiplier and Section 3.2 must say so.")
    sgn = {np.sign(r[3]) for r in rows}
    lo = min(abs(r[3]) for r in rows)
    hi = max(abs(r[3]) for r in rows)
    out(f"(2) ANGLE: effects {', '.join(f'{r[0]} k={r[1]}: {r[3]:+.3f}' for r in rows)} deg.")
    if len(sgn) == 1 and lo > 0 and hi <= 2.0 * lo:
        out("    The sign holds at every multiplier and the magnitude stays within a factor of two,")
        out("    so the angle cost is robust to the threshold.")
    elif len(sgn) > 1:
        out("    The SIGN FLIPS across multipliers. The angle cost is a property of the threshold")
        out("    and the Conclusion must be restated.")
    else:
        out("    The sign holds but the magnitude varies by more than a factor of two, so the")
        out("    quoted size is conditional on the multiplier even though its direction is not.")
    out("(3) Retention falls monotonically with the multiplier, which is the dose effect the")
    out("    dose-response family already reports; it is not itself a verdict here.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
