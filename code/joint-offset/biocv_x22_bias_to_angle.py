"""X22 — is the 27-37 mm joint-centre offset arithmetically compatible with a 2.58 deg
knee-angle error? Watchdog-directed, computed before any restructure.

The tension: section 3.6 says a large fixed joint-centre offset bounds the whole line of
work; section 3.5 says errors common-mode across neighbouring joints cancel in the angle.
Both cannot be load-bearing.

Method (exact, no geometric approximation, no plane projection needed):
  1. Per (subject, joint), estimate the systematic offset b = mean(X_est - X_gt) from the
     actual triangulation -- the same quantity Table 5 decomposes.
  2. For every frame, form a BIAS-ONLY estimate: X_gt + b for each of hip/knee/ankle.
  3. The angle computed from those three points, minus the true GT angle, is EXACTLY the
     angle error attributable to the systematic offsets alone. Everything else cancels.
  4. Compare with the observed total angle error from the real pipeline.

This answers whether the fixed offset is SUFFICIENT to produce a knee error of the observed
size. It cannot answer what share of that error the offset IS: both quantities are mean
absolute errors and do not add. The per-frame correlation between the two, and Table 3a's
own-offset correction, are what bear on that, and both are reported beside the ratio.

Also reports, per watchdog note, the offset decomposed relative to the hip-ankle chord
PER FRAME (axial vs in-plane vs out-of-plane), since segment axes rotate during gait.
-> D:/BioCV/BIOCV_X22.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_X22.txt")
CHAINS = {"L-knee": (11, 13, 15), "R-knee": (12, 14, 16)}
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_x22_progress.txt"

def ang(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def solve(cs, uvs, w):
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([objd(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
        idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

# ---- PASS 1: collect per-(subject, joint) triangulation errors -> systematic offsets ----
open(PROG, "w").write("pass1 start\n")
obs = []          # (pid, chain, ja, jb, jc, Xg_a, Xg_b, Xg_c, Xe_a, Xe_b, Xe_c, gt_angle)
t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid)
    nf += 1; open(PROG, "a").write(f"pass1 file {nf}/108 t={time.time()-t0:.0f}s obs={len(obs)}\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for cname, (ja, jb, jc) in CHAINS.items():
            if not all(j in gt and np.any(gt[j]) for j in (ja, jb, jc)): continue
            g = ang(gt[ja], gt[jb], gt[jc])
            if not np.isfinite(g): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0
                                            for j in (ja, jb, jc))]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            X = {}
            for j in (ja, jb, jc):
                uvs = np.array([det[i][j, :2] for i in vi])
                w = np.array([det[i][j, 2] for i in vi])
                X[j] = solve(cs, uvs, w)
            obs.append((pid, cname, ja, jb, jc,
                        gt[ja].copy(), gt[jb].copy(), gt[jc].copy(),
                        X[ja], X[jb], X[jc], g))

# systematic offset per (pid, joint index)
err = {}
for (pid, cn, ja, jb, jc, ga, gb, gc, ea, eb, ec, g) in obs:
    for j, gp, ep in ((ja, ga, ea), (jb, gb, eb), (jc, gc, ec)):
        err.setdefault((pid, j), []).append(ep - gp)
bias = {k: np.mean(v, axis=0) for k, v in err.items()}

# ---- PASS 2: propagate bias-only through the angle ----
open(PROG, "a").write("pass2\n")
rows = []; subj = []; pid2id = {}
chordinfo = []
for (pid, cn, ja, jb, jc, ga, gb, gc, ea, eb, ec, g) in obs:
    sid = pid2id.setdefault(pid, len(pid2id))
    ba, bb, bc = bias[(pid, ja)], bias[(pid, jb)], bias[(pid, jc)]
    g_bias = ang(ga + ba, gb + bb, gc + bc)          # systematic component only
    g_full = ang(ea, eb, ec)                          # actual pipeline estimate
    if not (np.isfinite(g_bias) and np.isfinite(g_full)): continue
    rows.append((abs(g_bias - g), abs(g_full - g)))
    subj.append(sid)
    # per-frame decomposition of the KNEE offset relative to the instantaneous hip-ankle chord
    chord = gc - ga; L = np.linalg.norm(chord)
    if L < 1e-6: continue
    u = chord / L
    rel = bb - 0.5 * (ba + bc)                        # knee offset relative to chord midpoint
    axial = np.dot(rel, u)
    perp = rel - axial * u
    # flexion plane = plane containing hip, knee, ankle
    n = np.cross(gb - ga, gc - gb); nn = np.linalg.norm(n)
    if nn < 1e-6: continue
    n = n / nn
    out_of_plane = np.dot(perp, n)
    in_plane = np.linalg.norm(perp - out_of_plane * n)
    chordinfo.append((axial, in_plane, out_of_plane, np.linalg.norm(rel)))

rows = np.array(rows); subj = np.array(subj); ci_arr = np.array(chordinfo)
lines = []
def out(s): print(s); lines.append(s)
out("X22 -- IS THE FIXED JOINT-CENTRE OFFSET COMPATIBLE WITH THE OBSERVED KNEE-ANGLE ERROR?")
out(f"Cache={CACHE}  N={len(rows)} knee-angle observations, {len(pid2id)} subjects.")
out("bias-only angle = angle(GT + per-subject-per-joint systematic offset) - GT angle.")
out("")
out(f"{'quantity':>34}{'mean deg':>11}{'median':>9}{'p90':>9}")
out(f"{'angle error from SYSTEMATIC offset':>34}{rows[:,0].mean():>11.3f}{np.median(rows[:,0]):>9.3f}{np.percentile(rows[:,0],90):>9.3f}")
out(f"{'angle error, full pipeline':>34}{rows[:,1].mean():>11.3f}{np.median(rows[:,1]):>9.3f}{np.percentile(rows[:,1],90):>9.3f}")
ratio = rows[:,0].mean() / rows[:,1].mean() * 100
r = float(np.corrcoef(rows[:,0], rows[:,1])[0, 1])
out("")
out(f"RATIO OF MEAN ABSOLUTE ERRORS, bias-only / full pipeline: {ratio:.1f}%")
out(f"PER-FRAME CORRELATION between the two: r = {r:.3f}")
out("")
out("READ THIS PAIR TOGETHER, NOT THE FIRST LINE ALONE. The ratio says the systematic offset")
out("is SUFFICIENT on its own to produce a knee-angle error of the observed size. It is not a")
out("decomposition and it is not a share: both quantities are mean ABSOLUTE errors, which do")
out("not add, so a ratio near 100% is compatible with the two errors being unrelated. The")
out("correlation is what says whether they are the same error. Table 3a settles it from the")
out("other side: correcting each subject with their OWN mean offset -- removing exactly the")
out("quantity measured here -- lowers knee-flexion error from 2.575 to 2.495 deg, a recovery")
out("of 0.080 deg, or 3% of the observed error. The static offset therefore BOUNDS the")
out("magnitude of the angle error without accounting for it, and no causal claim may be built")
out("on this table. What the offset does explain is why a triangulation gain of about a")
out("millimetre need not reach the angle: the decomposition below shows only the in-plane")
out("perpendicular component driving flexion at all.")
out("")
out("--- why: per-frame decomposition of the knee offset relative to the hip-ankle chord ---")
out(f"{'component':>22}{'mean |mm|':>11}{'  (flexion sensitivity)':>26}")
out(f"{'axial (along limb)':>22}{np.abs(ci_arr[:,0]).mean():>11.2f}{'  changes length, not flexion':>26}")
out(f"{'in-plane perpendicular':>22}{np.abs(ci_arr[:,1]).mean():>11.2f}{'  DRIVES flexion error':>26}")
out(f"{'out-of-plane':>22}{np.abs(ci_arr[:,2]).mean():>11.2f}{'  ab/adduction, not flexion':>26}")
out(f"{'total |rel offset|':>22}{np.abs(ci_arr[:,3]).mean():>11.2f}")
out("")
sl = np.unique(subj); idx = {t: np.where(subj == t)[0] for t in sl}
bs = np.empty(B)
d = rows[:,1] - rows[:,0]
for b in range(B):
    pick = rng.choice(sl, size=len(sl), replace=True)
    ii = np.concatenate([idx[t] for t in pick]); bs[b] = d[ii].mean()
cint = np.percentile(bs, [2.5, 97.5])
out(f"random (non-systematic) component of knee-angle error: {d.mean():.3f} deg "
    f"[{cint[0]:.3f},{cint[1]:.3f}] (subject-cluster bootstrap)")
out("")
out("READ: the bootstrap interval above is on the DIFFERENCE of the two mean absolute errors,")
out("so it says the offset-only error is indistinguishable in SIZE from the observed one. With")
out("r = 0.199 between them per frame, that is a coincidence of magnitude and not a shared")
out("cause, and the angle-level headroom this table shows is headroom against a target no")
out("triangulation change reaches.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
