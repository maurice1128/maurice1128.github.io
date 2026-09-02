"""Why do the toe and heel endpoints disagree about the shank-foot angle?

Table S13 leaves one result avowedly unexplained: under HALPE-26 the shank-foot angle carries
7.524 deg of mean absolute error on the toe endpoint and 25.202 deg on the heel, the offset table
improves the heel by 15.014 deg and the toe by 0.981, and the two rejection rows disagree in SIGN
between endpoints, so the declared rule returns no verdict there. S13 rejects a sensitivity
explanation on the ground that the heel is only 1.5x as sensitive per millimetre, which it calls
far too small to explain the gap.

That is the wrong comparison. What moves a three-point angle is not the offset's length but its
component PERPENDICULAR to the segment, in the plane of the angle; a component along the segment
changes the segment's length and not the angle. The same decomposition was already run for the
knee (Table 3b, 11.04 mm of 32.4 mm in the flexion-moving direction). It has never been run for
the foot, and the data to run it are already cached.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

For each endpoint the offset is split, relative to that endpoint's OWN ankle-to-endpoint segment
and in the plane of angle(knee, ankle, endpoint), into

    axial          along the segment            changes length, not the angle
    in-plane perp  perpendicular, in plane      MOVES the angle
    out-of-plane   perpendicular, out of plane  moves the other rotation, not this angle

and the in-plane perpendicular component is converted to degrees as atan2(perp, |segment|).

  (1) EXPLAINED. If the heel's implied angle offset is a large fraction of its 25.202 deg
      baseline while the toe's is a small fraction of its 7.524 deg baseline, the baseline gap
      and the endpoint disagreement follow from geometry. Table S13's unexplained result is
      then explained and must be restated as such.

  (2) NOT EXPLAINED. If the two implied angle offsets are comparable fractions of their
      baselines, geometry does not account for the disagreement and S13's statement stands
      unchanged. This is reportable and must be reported.

  (3) AGAINST THE PAPER. If the TOE -- the pre-declared primary endpoint -- turns out to be the
      one whose angle is dominated by its offset, then the primary outcome is the worse-founded
      of the two and Part B of Table S13 must say so.

  (4) The veto is not lifted by anything here. Table S13 returns no verdict where the endpoints
      disagree in sign, and explaining a disagreement is not agreement.

-> D:/BioCV/BIOCV_FOOT_GEOMETRY.txt
"""
import glob
import io
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R                                                        # noqa: E402
from biocv_calib import load_biocv_cameras                                     # noqa: E402

CACHE = os.environ.get("BIOCV_HALPE_CACHE", "D:/BioCV/_cache_halpe_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_FOOT_GEOMETRY.txt")
MIN_CAM = 4
SIDES = {"L": {"knee": 13, "ankle": 15, "toe": 20, "heel": 24},
         "R": {"knee": 14, "ankle": 16, "toe": 21, "heel": 25}}
BASELINE = {"toe": 7.524, "heel": 25.202}          # Table S13, mean absolute angle error, deg

_C = {}


def cams_for(pid):
    if pid not in _C:
        _C[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return _C[pid]


def tri(det, cams, j):
    vi = [i for i, d in enumerate(det)
          if d is not None and np.isfinite(d[j, 0]) and d[j, 2] > 0]
    if len(vi) < MIN_CAM:
        return None
    uvs = np.array([det[i][j, :2] for i in vi])
    w = np.array([det[i][j, 2] for i in vi])
    return R.triangulate_wdlt([cams[i] for i in vi], uvs, w)


L = []


def out(s):
    print(s, flush=True)
    L.append(s)


off = {}
seg = {}
for f in sorted(glob.glob(CACHE + "/*.pkl")):
    D = pickle.load(open(f, "rb"))
    pid = D["pid"]
    cams = cams_for(pid)
    for fr in D["frames"]:
        det, gt = fr["det"], fr["gt"]
        for sd, J in SIDES.items():
            if not all(J[k] in gt and np.any(gt[J[k]]) for k in ("knee", "ankle", "toe", "heel")):
                continue
            for ep in ("toe", "heel"):
                X = tri(det, cams, J[ep])
                if X is None:
                    continue
                a, e, k = gt[J["ankle"]], gt[J[ep]], gt[J["knee"]]
                u = e - a
                v = k - a
                nu = np.linalg.norm(u)
                n = np.cross(u, v)
                nn = np.linalg.norm(n)
                if nu < 1e-6 or nn < 1e-6:
                    continue
                off.setdefault((pid, ep), []).append(X - e)
                seg.setdefault((pid, ep), []).append((u / nu, n / nn, nu))

out("WHY THE TOE AND HEEL ENDPOINTS DISAGREE: THE OFFSET'S DIRECTION, NOT ITS LENGTH")
out("")
out("Each endpoint's mean offset is decomposed against ITS OWN ankle-to-endpoint segment, in the")
out("plane of angle(knee, ankle, endpoint). Only the in-plane perpendicular component moves that")
out("angle. Baselines are Table S13's mean absolute angle errors: toe 7.524 deg, heel 25.202 deg.")
out("")
out(f"{'endpoint':>9}{'n':>5}{'|offset|':>10}{'axial':>9}{'in-plane':>10}{'out-plane':>11}"
    f"{'|segment|':>11}{'implied deg':>13}{'of baseline':>13}")

summary = {}
for ep in ("toe", "heel"):
    pids = sorted({p for (p, e) in off if e == ep})
    rows = []
    for p in pids:
        E = np.asarray(off[(p, ep)], float)
        U = np.asarray([s[0] for s in seg[(p, ep)]], float)
        N = np.asarray([s[1] for s in seg[(p, ep)]], float)
        Ln = np.asarray([s[2] for s in seg[(p, ep)]], float)
        m = E.mean(axis=0)
        uhat, nhat, seglen = U.mean(axis=0), N.mean(axis=0), float(Ln.mean())
        uhat = uhat / np.linalg.norm(uhat)
        nhat = nhat - np.dot(nhat, uhat) * uhat
        nhat = nhat / np.linalg.norm(nhat)
        axial = float(np.dot(m, uhat))
        outp = float(np.dot(m, nhat))
        perp = m - axial * uhat - outp * nhat
        inpl = float(np.linalg.norm(perp))
        rows.append((float(np.linalg.norm(m)), abs(axial), inpl, abs(outp), seglen,
                     float(np.degrees(np.arctan2(inpl, seglen)))))
    if not rows:
        continue
    A = np.array(rows)
    mean = A.mean(axis=0)
    frac = 100.0 * mean[5] / BASELINE[ep]
    summary[ep] = (mean[5], frac)
    out(f"{ep:>9}{len(rows):>5}{mean[0]:>10.2f}{mean[1]:>9.2f}{mean[2]:>10.2f}{mean[3]:>11.2f}"
        f"{mean[4]:>11.1f}{mean[5]:>13.2f}{frac:>12.1f}%")

out("")
if len(summary) == 2:
    dt, ft = summary["toe"]
    dh, fh = summary["heel"]
    out("=== VERDICT, against the rule fixed in this file's header ===")
    out(f"Toe:  the offset implies {dt:.2f} deg of angle error, {ft:.1f}% of its 7.524 deg baseline.")
    out(f"Heel: the offset implies {dh:.2f} deg of angle error, {fh:.1f}% of its 25.202 deg baseline.")
    out("")
    if fh > 2 * ft:
        out("(1) EXPLAINED in the direction the header anticipated: the heel's angle is far more")
        out("    offset-dominated than the toe's. The baseline gap and the endpoint disagreement")
        out("    follow from where each offset points, not from how long it is, and Table S13's")
        out("    'unexplained' statement must be replaced by this decomposition.")
    elif ft > 2 * fh:
        out("(3) AGAINST THE PAPER: the TOE, which is the pre-declared PRIMARY endpoint, is the one")
        out("    whose angle is offset-dominated. The primary outcome is the worse-founded of the")
        out("    two and Part B of Table S13 must say so.")
    else:
        out("(2) NOT EXPLAINED: the two implied angle offsets are comparable fractions of their")
        out("    baselines, so geometry does not account for the disagreement. Table S13's")
        out("    statement stands unchanged and this file adds only a bound.")
    out("")
    out("(4) The veto stands either way: Table S13 returns no verdict where the two endpoints")
    out("    disagree in sign, and explaining a disagreement is not agreement.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
