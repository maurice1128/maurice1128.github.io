"""IS alpha = -1.111 REAL DETECTOR HETEROSCEDASTICITY, OR THE JOINT-CENTRE OFFSET SEEN
THROUGH PERSPECTIVE?

Council round 4, first-time reader, strongest technical objection:

  BIOCV_LM_NOISE_BIG.txt measures "detector pixel error vs camera distance" as the
  distance from the detection to the projection of the VICON ground truth, and fits
  sigma_px ~ d^alpha, getting alpha = -1.111. Section 3.2 of the manuscript uses this
  to argue the object-space criterion is well-motivated by derivation.

  But Section 3.5 of the same manuscript says 79% of squared 3D error is a FIXED
  per-subject-per-joint offset Delta between the detector's keypoint convention and
  the marker-based joint centre. A fixed 3D offset projects to f*|Delta|/Z pixels --
  i.e. EXACTLY d^-1. alpha = -1.111 is what you get from measuring a constant offset
  through perspective, whether or not detector noise depends on distance at all.

  Reader's arithmetic: Delta ~ 20 mm, f ~ 1236 px, Z = 3.36 m -> 7.4 px; Z = 6.30 m
  -> 3.9 px. Observed: 6.01 and 3.10. The offset alone very nearly reproduces the
  whole effect.

THE TEST. Re-measure the same table against a reference that has the offset removed:
project (GT + per-subject-per-joint mean offset) instead of GT. That reference sits at
the detector's own convention, so what remains is detector scatter alone.

  If alpha stays near -1  -> pixel noise really is distance-dependent; Section 3.2 stands.
  If alpha moves to ~0    -> Section 3.2's argument is an artifact of the offset and
                             MUST BE WITHDRAWN. In that case reprojection error, not
                             object-space error, is the correctly-weighted residual,
                             and the criterion's position advantage needs another
                             explanation (or none).

Offsets are computed LEAVE-ONE-SUBJECT-OUT so the correction is not fitted to the same
subject it is applied to. The in-sample version is printed alongside as a bound.
-> D:/BioCV/BIOCV_ALPHA.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = "D:/BioCV/_cache_undist"
OUTF = "D:/BioCV/BIOCV_ALPHA.txt"
PROG = "D:/BioCV/_alpha_progress.txt"
JOINTS = [5, 6, 9, 10, 11, 12, 13, 14, 15, 16]

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

# ---------------- pass 1: per-subject-per-joint 3D offset (est - gt) ----------------
off_acc = {}
open(PROG, "w").write("pass1\n"); t0 = time.time(); nf = 0
files = sorted(glob.glob(f"{CACHE}/*.pkl"))
for f in files:
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"pass1 {nf}/{len(files)} t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for j in JOINTS:
            if j not in gt or not np.any(gt[j]): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[j, 0]) and dd[j, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][j, :2] for i in vi])
            conf = np.array([det[i][j, 2] for i in vi])
            X = R.triangulate_wdlt(cs, uvs, conf)
            d = off_acc.setdefault((pid, j), [np.zeros(3), 0])
            d[0] += (X - gt[j]); d[1] += 1
OFF = {k: v[0] / v[1] for k, v in off_acc.items() if v[1] > 0}
PIDS = sorted({p for (p, _) in OFF})

def loo_off(pid, j):
    vs = [OFF[(p, j)] for p in PIDS if p != pid and (p, j) in OFF]
    return np.mean(vs, axis=0) if vs else np.zeros(3)

# ---------------- pass 2: pixel error against three references ----------------
# raw      = distance from detection to projection of GT          (what the paper did)
# loo      = ... to projection of GT + LOO mean offset            (deployable correction)
# insample = ... to projection of GT + this subject's own offset  (bound)
REC = []   # (dist_mm, e_raw, e_loo, e_ins)
open(PROG, "a").write("pass2\n"); nf = 0
for f in files:
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"pass2 {nf}/{len(files)} t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for j in JOINTS:
            if j not in gt or not np.any(gt[j]): continue
            if (pid, j) not in OFF: continue
            Xg = gt[j]
            Xl = Xg + loo_off(pid, j)
            Xi = Xg + OFF[(pid, j)]
            for i, dd in enumerate(det):
                if dd is None or not np.isfinite(dd[j, 0]) or dd[j, 2] <= 0: continue
                cam = cams[i]; uv = dd[j, :2]
                REC.append((float(np.linalg.norm(cam.C - Xg)),
                            float(np.linalg.norm(cam.project(Xg) - uv)),
                            float(np.linalg.norm(cam.project(Xl) - uv)),
                            float(np.linalg.norm(cam.project(Xi) - uv))))
A = np.array(REC)
dist = A[:, 0]

def table(col, name, lines):
    e = A[:, col]
    qs = np.quantile(dist, [0, .2, .4, .6, .8, 1.0])
    lines.append(f"--- {name} ---")
    lines.append(f"{'dist bin (mm)':>20}{'n':>8}{'median e_px':>13}{'mean e_px':>11}{'p90 e_px':>10}")
    cd, cm = [], []
    for b in range(5):
        lo, hi = qs[b], qs[b + 1]
        s = (dist >= lo) & (dist <= hi if b == 4 else dist < hi)
        if s.sum() < 10: continue
        lines.append(f"{f'{lo:.0f}-{hi:.0f}':>20}{s.sum():>8}{np.median(e[s]):>13.2f}"
                     f"{e[s].mean():>11.2f}{np.quantile(e[s],.9):>10.2f}")
        cd.append(np.median(dist[s])); cm.append(np.median(e[s]))
    cd, cm = np.array(cd), np.array(cm)
    alpha = np.polyfit(np.log(cd), np.log(cm), 1)[0]
    lines.append(f"power-law fit on medians: sigma_px ~ d^alpha with alpha = {alpha:+.3f}")
    lines.append("")
    return alpha

L = []
L.append("IS THE DISTANCE DEPENDENCE REAL HETEROSCEDASTICITY, OR THE JOINT-CENTRE OFFSET")
L.append("SEEN IN PERSPECTIVE?  (BIOCV_LM_NOISE_BIG.txt reported alpha = -1.111 on a wider")
L.append("joint set; this file recomputes it on the ten joints listed below -- shoulders,")
L.append("wrists, hips, knees and ankles, NOT the lower limb -- hence the small difference.)")
L.append(f"Cache={CACHE}. N={len(A)} camera-joint observations, {len(PIDS)} subjects, "
         f"joints {JOINTS}.")
L.append("Reference for 'pixel error' differs per panel; everything else is identical.")
L.append("")
a_raw = table(1, "(1) vs projection of VICON GT  [this is what BIOCV_LM_NOISE_BIG.txt did]", L)
a_loo = table(2, "(2) vs projection of GT + LEAVE-ONE-SUBJECT-OUT mean offset", L)
a_ins = table(3, "(3) vs projection of GT + THAT SUBJECT'S OWN mean offset (in-sample bound)", L)

L.append("=== VERDICT ===")
L.append(f"alpha(raw GT)      = {a_raw:+.3f}")
L.append(f"alpha(LOO-offset)  = {a_loo:+.3f}")
L.append(f"alpha(in-sample)   = {a_ins:+.3f}")
L.append("")
shrink = 1.0 - abs(a_ins) / abs(a_raw) if abs(a_raw) > 1e-9 else float("nan")
# The sentence used to say "shrinks by" whatever the sign of `shrink` was, so a NEGATIVE
# shrink printed as "shrinks by -5%" while the number said |alpha| had grown. Let the
# direction follow the arithmetic.
L.append("|alpha| %s by %.0f%% once the joint-centre offset is removed."
         % ("shrinks" if shrink >= 0 else "GROWS", abs(100 * shrink)))
L.append("")
if abs(a_ins) < 0.35:
    L.append("READ: the distance dependence LARGELY DISAPPEARS. The reader's objection is")
    L.append("UPHELD: alpha = -1.111 was the fixed keypoint-convention offset viewed through")
    L.append("perspective, not detector heteroscedasticity. Manuscript Section 3.2's claim that")
    L.append("the object-space criterion is 'well-motivated by derivation' MUST BE WITHDRAWN,")
    L.append("and reprojection error is the correctly-weighted residual after all.")
elif abs(a_ins) > 0.7:
    L.append("READ: the distance dependence SURVIVES offset removal. Detector pixel noise really")
    L.append("does fall with distance and Section 3.2's argument stands as written.")
else:
    L.append("READ: PARTIAL. Some of the distance dependence is the offset and some is real.")
    L.append("Section 3.2 must be restated with the offset-removed alpha, not the raw one,")
    L.append("and must disclose that the raw figure is confounded by the offset.")
open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
print("\nWROTE", OUTF)
