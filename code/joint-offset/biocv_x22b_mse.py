"""X22b -- CORRECTED per watchdog Cycle 3g attacks A1/A2/A3/A4.

A2: the first version compared mean ABSOLUTE angle deviations, which do not decompose
    additively, and reported 101.6% as if it were a share comparable to B14's MSE-based
    55%. It is not. Worse, >100% is a misspecification signature: angle() is nonlinear,
    so propagating the mean position offset yields f(E[e]) while the comparator was
    E|f(e)|. FIX: decompose the ANGLE ERROR itself the way B14 decomposed positions --
    per (subject, chain) SIGNED angle error, then MSE = bias^2 + variance.

A3: b = mean(X_est - X_gt) is the TOTAL systematic error, which may include a
    triangulation-induced component, not only joint-centre convention. FIX: recompute b
    separately for every arm. If b is invariant across arms the convention attribution
    holds; if b varies, part of the systematic error is triangulation-induced.

A4: the original denominator was one arm (objd_conf). FIX: report all six arms.

A1 is a writing constraint, not a computation: X22's random CI (+-0.3 deg) contains every
effect Table 4 detects with tighter intervals, so "triangulation is not detectably
involved" is an absence-of-evidence claim and must not be written.
-> D:/BioCV/BIOCV_X22B.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_X22B.txt")
CHAINS = {"L-knee": (11, 13, 15), "R-knee": (12, 14, 16)}
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_x22b_progress.txt"

def ang(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def solve(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is not None:
        while len(idx) > MIN_CAM:
            CS = [cs[i] for i in idx]
            X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
            e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
            med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
            worst = int(np.argmax(e))
            if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
            idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

ARMS = ["noRej_conf", "noRej_wd", "rep_conf", "objd_conf", "rep_wd", "objd_wd"]
recs = []            # per observation: pid, chain, gt angle, {arm: (angle, {joint: err_vec})}
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid)
    nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s recs={len(recs)}\n")
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
            per_arm = {}
            for a in ARMS:
                metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                use_wd = a.endswith("_wd")
                Xs = {}
                for j in (ja, jb, jc):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    if use_wd:
                        dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                        w = conf / dj
                    else:
                        w = conf
                    Xs[j] = solve(cs, uvs, w, metric)
                per_arm[a] = (ang(Xs[ja], Xs[jb], Xs[jc]),
                              {j: Xs[j] - gt[j] for j in (ja, jb, jc)})
            recs.append((pid, cname, ja, jb, jc,
                         gt[ja].copy(), gt[jb].copy(), gt[jc].copy(), g, per_arm))

lines = []
def out(s): print(s); lines.append(s)
out("X22b -- CORRECTED ANGLE ERROR DECOMPOSITION (MSE, per-arm), watchdog Cycle 3g")
out(f"Cache={CACHE}  N={len(recs)} knee-angle observations, "
    f"{len(set(r[0] for r in recs))} subjects.")
out("")

# ---------- A2: MSE decomposition of the SIGNED angle error, per arm ----------
out("=== A2 FIX: MSE decomposition of SIGNED angle error (comparable to B14's position 55%) ===")
out(f"{'arm':>12}{'RMSE deg':>10}{'bias deg':>10}{'random deg':>12}{'bias% of MSE':>14}{'mean|err|':>11}")
for a in ARMS:
    per_sc = {}
    for (pid, cn, ja, jb, jc, ga, gb, gc, g, pa) in recs:
        e = pa[a][0] - g
        if np.isfinite(e): per_sc.setdefault((pid, cn), []).append(e)
    allv = np.concatenate([np.array(v) for v in per_sc.values()])
    mse = np.mean(allv**2)
    b2 = np.mean([np.mean(v)**2 for v in per_sc.values()])
    out(f"{a:>12}{np.sqrt(mse):>10.3f}{np.sqrt(b2):>10.3f}"
        f"{np.sqrt(max(mse-b2,0)):>12.3f}{100*b2/mse:>13.0f}%{np.abs(allv).mean():>11.3f}")
out("  (compare: systematic share of PERIPHERAL-JOINT squared POSITION error = 55%)")
out("")

# ---------- A3: is the position bias b invariant across arms? ----------
out("=== A3 TEST: is the systematic position offset b the same for every arm? ===")
out("  If b is invariant -> it is a joint-centre convention offset, not triangulation-induced.")
out("  If b varies      -> part of the systematic error IS triangulation-induced.")
JN = {11: "L-hip", 12: "R-hip", 13: "L-knee", 14: "R-knee", 15: "L-ankle", 16: "R-ankle"}
bias_by_arm = {}
for a in ARMS:
    acc = {}
    for (pid, cn, ja, jb, jc, ga, gb, gc, g, pa) in recs:
        for j, ev in pa[a][1].items():
            acc.setdefault((pid, j), []).append(ev)
    bias_by_arm[a] = {k: np.mean(v, axis=0) for k, v in acc.items()}
out(f"{'joint':>9}" + "".join(f"{a:>12}" for a in ARMS) + f"{'max spread':>12}")
for jj in sorted(JN):
    mags = []
    for a in ARMS:
        vs = [b for (p, j), b in bias_by_arm[a].items() if j == jj]
        mags.append(np.linalg.norm(np.mean(vs, axis=0)) if vs else np.nan)
    ref = np.mean([np.mean([b for (p, j), b in bias_by_arm[a].items() if j == jj], axis=0)
                   for a in ARMS], axis=0)
    spread = max(np.linalg.norm(
        np.mean([b for (p, j), b in bias_by_arm[a].items() if j == jj], axis=0) - ref)
        for a in ARMS)
    out(f"{JN[jj]:>9}" + "".join(f"{m:>12.2f}" for m in mags) + f"{spread:>12.2f}")
out("  columns = ||mean offset|| (mm) per arm; 'max spread' = largest deviation of any arm")
out("  from the across-arm mean, in mm.")
out("")

# ---------- A1: the random component, stated with its power ----------
out("=== A1: power of the 'random component' estimate (this is a NULL, not an absence) ===")
a0 = "objd_conf"
per_sc = {}
for (pid, cn, ja, jb, jc, ga, gb, gc, g, pa) in recs:
    e = pa[a0][0] - g
    if np.isfinite(e): per_sc.setdefault(pid, []).append(e)
sl = list(per_sc); idx = {p: np.array(per_sc[p]) for p in sl}
allv = np.concatenate([idx[p] for p in sl])
bs = np.empty(B)
for b in range(B):
    pick = rng.choice(sl, size=len(sl), replace=True)
    ii = np.concatenate([idx[t] for t in pick]); bs[b] = np.sqrt(np.mean(ii**2))
c = np.percentile(bs, [2.5, 97.5])
out(f"  RMSE of {a0} = {np.sqrt(np.mean(allv**2)):.3f} deg, subject-cluster CI [{c[0]:.3f},{c[1]:.3f}]")
out(f"  Table 4 detects triangulation effects of 0.03-0.20 deg with CIs EXCLUDING zero.")
out(f"  Any 'no detectable triangulation contribution' claim must be checked against that.")
out("")
out("READ: report the MSE-based bias share (comparable to B14). Do NOT claim the")
out("triangulation stage is uninvolved -- Table 4 detects it with tighter intervals.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
