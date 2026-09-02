"""IS THE JOINT-CENTRE OFFSET POSTURE-DEPENDENT? -- watchdog directive D4-13/D5-12, third asking.

The watchdog ordered this at Cycle 3j and repeated it at Cycles 4 and 5. It was never run
and never declined in writing. Running it now.

WHY IT MATTERS. Section 3.5 of the manuscript rests on the offset between the detector's
keypoint convention and the marker-based joint centre being a FIXED per-participant-per-joint
vector -- that is what makes it (a) 79% of squared 3D error, (b) beyond the reach of
triangulation, and (c) in principle correctable by a table. We have already found it is not
perfectly fixed: it moves up to 3.10 mm across triangulation arms (the A3 test). The
remaining question is whether it moves with POSTURE.

If the offset swings with knee flexion, then:
  - part of what the decomposition scores as "random" is actually systematic-but-
    posture-dependent, so the 79% understates the structured share;
  - a static per-joint correction table cannot work even in principle, which strengthens
    the paper's finding that the LOO correction makes knee flexion worse (-0.606 deg);
  - and the knee's flexion-sensitive offset component (11.04 mm of 32.4 mm) would itself
    be a function of the angle being measured -- a circularity the paper should disclose.

If it does not swing, the fixed-offset account is strengthened and the LOO failure has to
be explained purely by across-participant magnitude variation, as Section 3.5 currently does.

METHOD. Triangulate with the reference arm (confidence weights, no rejection). For every
observation compute the offset vector (estimate - ground truth) at hip, knee and ankle, in
the BODY frame, and the ground-truth knee flexion angle. Bin by GT knee flexion. Report the
offset magnitude and the flexion-sensitive component per bin. Test the extreme-bin difference
per participant with the exact sign-flip test used everywhere else in the paper.
-> D:/BioCV/BIOCV_POSTURE.txt
"""
import glob, os, pickle, itertools, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = "D:/BioCV/_cache_undist"
OUTF = "D:/BioCV/BIOCV_POSTURE.txt"
PROG = "D:/BioCV/_posture_progress.txt"
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}
JN = {0: "hip", 1: "knee", 2: "ankle"}

def ang3(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

REC = []   # (pid, jslot, flex, ox, oy, oz, |o|, flex_sensitive_component)
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
files = sorted(glob.glob(f"{CACHE}/*.pkl"))
for f in files:
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"file {nf}/{len(files)} t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        if not all(j in gt and np.any(gt[j]) for j in (5, 6, 11, 12)): continue
        ml = gt[12] - gt[11]; nml = np.linalg.norm(ml)
        if nml < 1e-6: continue
        ml = ml / nml
        up = np.array([0.0, 0.0, 1.0]); up = up - np.dot(up, ml) * ml
        nu = np.linalg.norm(up)
        if nu < 1e-6: continue
        up = up / nu
        fwd = np.cross(up, ml)          # body frame: ml (lateral), fwd (anterior), up
        for side, (jsh, jh, jk, ja) in SIDES.items():
            need = (jsh, jh, jk, ja, 5, 6, 11, 12)
            if not all(j in gt and np.any(gt[j]) for j in need): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in need)]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            flex = ang3(gt[jh], gt[jk], gt[ja])
            if not np.isfinite(flex): continue
            # unit vector in the flexion-sensitive direction at the knee:
            # perpendicular to the hip-ankle chord, inside the hip-knee-ankle plane
            chord = gt[ja] - gt[jh]; nc = np.linalg.norm(chord)
            if nc < 1e-6: continue
            chord = chord / nc
            mid = gt[jk] - gt[jh]
            perp = mid - np.dot(mid, chord) * chord
            npp = np.linalg.norm(perp)
            perp = perp / npp if npp > 1e-6 else None
            for s, j in enumerate((jh, jk, ja)):
                uvs = np.array([det[i][j, :2] for i in vi])
                conf = np.array([det[i][j, 2] for i in vi])
                X = R.triangulate_wdlt(cs, uvs, conf)
                o = X - gt[j]
                ob = np.array([np.dot(o, ml), np.dot(o, fwd), np.dot(o, up)])
                fs = float(np.dot(o, perp)) if perp is not None else np.nan
                REC.append((pid, s, float(flex), ob[0], ob[1], ob[2],
                            float(np.linalg.norm(o)), fs))

A = np.array([r[1:] for r in REC], dtype=float)
PID = np.array([r[0] for r in REC])
flex = A[:, 1]
upids = sorted(set(PID))
SIGNS = np.array(list(itertools.product([-1, 1], repeat=len(upids))), dtype=float)
def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == len(upids) else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)

qs = np.quantile(flex, [0, .2, .4, .6, .8, 1.0])
L = []
def out(s): print(s); L.append(s)
out("IS THE JOINT-CENTRE OFFSET POSTURE-DEPENDENT?  (watchdog D4-13, third asking)")
out(f"Cache={CACHE}. N={len(A)} joint-observations, {len(upids)} participants.")
out("Arm = confidence weights, no rejection. Offsets are (estimate - ground truth) in the")
out("body frame: x = mediolateral, y = anterior, z = superior. Bins are quintiles of the")
out("GROUND-TRUTH knee flexion angle, so the binning variable is not itself estimated.")
out("")
for s in (0, 1, 2):
    m0 = A[:, 0] == s
    out(f"--- {JN[s]} ---")
    out(f"{'GT knee flexion':>18}{'n':>8}{'off x':>9}{'off y':>9}{'off z':>9}{'|off|':>9}"
        + ("{:>12}".format("flex-sens") if s == 1 else ""))
    for b in range(5):
        lo, hi = qs[b], qs[b + 1]
        sel = m0 & (flex >= lo) & (flex <= hi if b == 4 else flex < hi)
        if sel.sum() < 50: continue
        row = (f"{f'{lo:.0f}-{hi:.0f} deg':>18}{sel.sum():>8}{A[sel,2].mean():>+9.1f}"
               f"{A[sel,3].mean():>+9.1f}{A[sel,4].mean():>+9.1f}{A[sel,5].mean():>9.1f}")
        if s == 1:
            row += f"{np.nanmean(A[sel,6]):>+12.1f}"
        out(row)
    # extreme-bin contrast, per participant, exact sign-flip
    lo1, hi1 = qs[0], qs[1]; lo2, hi2 = qs[4], qs[5]
    for comp, cname in ([(2, "x"), (3, "y"), (4, "z"), (5, "|off|")] +
                        ([(6, "flex-sens")] if s == 1 else [])):
        ds = []
        for p in upids:
            a1 = A[(PID == p) & m0 & (flex >= lo1) & (flex < hi1), comp]
            a2 = A[(PID == p) & m0 & (flex >= lo2) & (flex <= hi2), comp]
            if len(a1) < 20 or len(a2) < 20: continue
            ds.append(np.nanmean(a2) - np.nanmean(a1))
        if len(ds) < 6: continue
        d = np.array(ds)
        out(f"   most-extended bin minus most-flexed, {cname:>10}: "
            f"{d.mean():+7.2f} mm   exact p = {exact_p(d):.4f}   (n={len(d)} participants)")
    out("")

out("READ: if the offset components swing significantly between the lowest and highest")
out("flexion quintiles, the 'fixed per-participant-per-joint offset' of Section 3.5 is")
out("posture-dependent. Consequences if so: part of the decomposition's 'random' component")
out("is structured, a static correction table cannot work even in principle (which is")
out("consistent with the LOO correction worsening knee flexion by 0.606 deg), and the knee's")
out("flexion-sensitive offset component is itself a function of the angle being measured --")
out("a circularity the manuscript must disclose. If the swings are small or non-significant,")
out("the fixed-offset account stands and the LOO failure is due to across-participant")
out("magnitude variation alone, as Section 3.5 currently argues.")
open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
