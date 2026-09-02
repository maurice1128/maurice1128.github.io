"""Are the null triangulation results a property of the pipeline, or of a redundant rig?

Section 3.2 reports that adaptive rejection leaves lower-limb position where it was, bounded
within +/-0.35 mm, and Section 5 generalises that to "no triangulation decision mattered
practically". Both are measured on a nine-camera ring where the adaptive rule retains 8.26-8.68
cameras of nine (Table S21): under that much redundancy, discarding one observation is nearly a
no-op, so a small effect is what the geometry predicts rather than what the pipeline reveals.
Most laboratories this recommendation would reach run four to eight cameras.

The cached detections hold all nine views per frame, so the same contrasts can be recomputed on
camera SUBSETS at no new detection cost. The subsets are fixed here by index, spread around the
ring, and are one choice rather than an average over all subsets of that size:

    9 cameras   all
    7 cameras   all but indices 2 and 6
    5 cameras   indices 0, 2, 4, 6, 8

The rejection floor stays at four cameras throughout, so at five cameras the rule may discard one
observation and at four it may discard none.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) THE NULL IS NOT RIG-DEPENDENT. If at every camera count the rejection-versus-none position
      contrast stays inside the +/-0.35 mm bound Section 3.2 quotes, the null is a property of the
      decision and not of redundancy. Section 5 may then keep its present scope and the rig
      condition is a caveat rather than a limit.

  (2) THE NULL IS RIG-DEPENDENT -- AGAINST THE PAPER. If any reduced camera count takes the
      contrast outside that bound, the headline null holds only under redundancy. Section 3.2 and
      Section 5 must then be restated as conditional on a nine-camera ring, and the reporting
      recommendation must say that a sparser rig was not tested to the same conclusion. This
      outcome is reported as readily as the other.

  (3) ANGLE. The thigh-shank cost of discarding is reported as positive (rejection is worse). If
      its SIGN holds at every camera count, the direction is not a redundancy artefact. If it
      flips at any count, the Conclusion's angle claim must be restated as rig-conditional.

  (4) BASELINE ERROR IS EXPECTED TO RISE as cameras are removed, and a rise is not itself a
      verdict here: the question is what happens to the CONTRAST between arms, not to the level.

  (5) One subset per size is not an average over subsets. Whatever this returns is evidence about
      these subsets, not about five-camera rigs in general.

-> D:/BioCV/BIOCV_CAMERA_SUBSETS.txt
"""
import glob
import io
import itertools
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R                                                        # noqa: E402
from biocv_calib import load_biocv_cameras                              # noqa: E402

CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_CAMERA_SUBSETS.txt")
MIN_CAM = 4
K_MAD = 3.0
BOUND = 0.35
SUBSETS = [("9 cameras", None),
           ("7 cameras", [0, 1, 3, 4, 5, 7, 8]),
           ("5 cameras", [0, 2, 4, 6, 8])]
JHKA = [11, 12, 13, 14, 15, 16]
SIDES = {"L": (11, 13, 15), "R": (12, 14, 16)}

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


def solve(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is not None:
        while len(idx) > MIN_CAM:
            CS = [cs[i] for i in idx]
            X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
            e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
            med = np.median(e)
            mad = np.median(np.abs(e - med)) * 1.4826
            worst = int(np.argmax(e))
            if mad < 1e-9 or e[worst] <= med + K_MAD * mad:
                break
            idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx]), len(idx)


def ang3(a, b, c):
    u, v = a - b, c - b
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-9 or nv < 1e-9:
        return np.nan
    return float(np.degrees(np.arccos(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0))))


ARMS = [("none", None), ("rep", rep), ("objd", objd)]
pos = {(s, a): {} for s, _ in SUBSETS for a, _ in ARMS}
ang = {(s, a): {} for s, _ in SUBSETS for a, _ in ARMS}
keep = {(s, a): [] for s, _ in SUBSETS for a, _ in ARMS}

for f in sorted(glob.glob(CACHE + "/*.pkl")):
    D = pickle.load(open(f, "rb"))
    pid = D["pid"]
    cams = cams_for(pid)
    for fr in D["frames"]:
        det, gt = fr["det"], fr["gt"]
        if not all(j in gt and np.any(gt[j]) for j in JHKA):
            continue
        for sname, sel in SUBSETS:
            allow = set(range(len(det))) if sel is None else set(sel)
            vis = {}
            for j in JHKA:
                vi = [i for i, d in enumerate(det)
                      if i in allow and d is not None
                      and np.isfinite(d[j, 0]) and d[j, 2] > 0]
                if len(vi) >= MIN_CAM:
                    vis[j] = (vi, np.array([det[i][j, :2] for i in vi]),
                              np.array([det[i][j, 2] for i in vi]))
            if len(vis) < len(JHKA):
                continue
            for aname, metric in ARMS:
                X = {}
                for j, (vi, uvs, w) in vis.items():
                    X[j], nk = solve([cams[i] for i in vi], uvs, w, metric)
                    keep[(sname, aname)].append(nk)
                pos[(sname, aname)].setdefault(pid, []).extend(
                    float(np.linalg.norm(X[j] - gt[j])) for j in JHKA)
                for sd, (jh, jk, ja) in SIDES.items():
                    e = ang3(X[jh], X[jk], X[ja])
                    g = ang3(gt[jh], gt[jk], gt[ja])
                    if np.isfinite(e) and np.isfinite(g):
                        ang[(sname, aname)].setdefault(pid, []).append(abs(e - g))

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


out("IS THE TRIANGULATION NULL A PROPERTY OF THE RULE, OR OF A REDUNDANT RIG?")
out("")
out("Same frames, same detections, same adaptive rule at k = 3 MAD with a four-camera floor.")
out("Only the set of candidate cameras changes. EFFECT = no rejection minus rejection, per")
out("participant then averaged; POSITIVE means rejection is better. Frames are those where all")
out("six lower-limb joints keep at least four cameras within the subset, so the frame set")
out("narrows as cameras are removed and the LEVELS are not comparable across rows -- the")
out("CONTRAST is.")
out("")
out(f"{'subset':>11}{'arm':>7}{'kept':>7}{'position mm':>13}"
    f"{'effect mm':>11}{'exact p':>10}{'angle deg':>11}{'effect deg':>12}{'exact p':>10}")

verdict = {}
for sname, _sel in SUBSETS:
    pids = sorted(pos[(sname, "none")])
    if not pids:
        continue
    bp = {p: float(np.mean(pos[(sname, "none")][p])) for p in pids}
    ba = {p: float(np.mean(ang[(sname, "none")][p])) for p in pids}
    for aname, _m in ARMS:
        d = pos[(sname, aname)]
        if not d:
            continue
        mp = float(np.mean([np.mean(d[p]) for p in pids]))
        ma = float(np.mean([np.mean(ang[(sname, aname)][p]) for p in pids]))
        dp = np.array([bp[p] - np.mean(d[p]) for p in pids])
        da = np.array([ba[p] - np.mean(ang[(sname, aname)][p]) for p in pids])
        pp = exact_p(dp) if aname != "none" else float("nan")
        pa = exact_p(da) if aname != "none" else float("nan")
        out(f"{sname:>11}{aname:>7}{np.mean(keep[(sname, aname)]):>7.2f}"
            f"{mp:>13.3f}{dp.mean():>+11.3f}{pp:>10.4f}"
            f"{ma:>11.3f}{da.mean():>+12.3f}{pa:>10.4f}")
        if aname != "none":
            verdict[(sname, aname)] = (float(dp.mean()), float(da.mean()))

out("")
out("=== VERDICTS, against the rule fixed in this file's header ===")
outside = [(k, v) for k, v in verdict.items() if abs(v[0]) > BOUND]
if not outside:
    out(f"(1) THE NULL IS NOT RIG-DEPENDENT. Every position contrast stays inside +/-{BOUND} mm at")
    out("    every camera count, so the null Section 3.2 reports is a property of the decision and")
    out("    not of redundancy. The rig remains a caveat and not a limit on that claim.")
else:
    out(f"(2) AGAINST THE PAPER: the null IS rig-dependent. {len(outside)} contrast(s) leave the")
    out(f"    +/-{BOUND} mm bound once cameras are removed:")
    for (s, a), v in outside:
        out(f"      {s}, {a}: {v[0]:+.3f} mm")
    out("    The null of Sections 3.2 and 5 is therefore conditional on a nine-camera ring,")
    out("    and a sparser rig was not tested to the same conclusion.")

signs = {np.sign(v[1]) for v in verdict.values() if abs(v[1]) > 1e-9}
out("")
if len(signs) <= 1:
    out("(3) ANGLE: the cost of discarding keeps its sign at every camera count, so its direction")
    out("    is not an artefact of redundancy.")
else:
    out("(3) ANGLE: the cost of discarding CHANGES SIGN across camera counts. The Conclusion's")
    out("    angle claim must be restated as conditional on the rig.")
out("")
out("(5) One subset per size, not an average over subsets. This is evidence about these camera")
out("    sets, not about five-camera rigs in general.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
