"""DECISIVE TEST for the proposed new thesis ("3D positional accuracy is an invalid
surrogate for joint-kinematic accuracy"), ordered by the watchdog before any restructure.

BIOCV_LM_NOISE_BIG.txt shows the largest position effect in the whole project:
with LM (geometric/ML) triangulation, outlier rejection is worth +4.12 mm [3.11, 5.18]
-- an order of magnitude above anything else measured here.

If the thesis is true, that effect must ALSO fail to propagate to the knee angle.
If it does propagate, the thesis is false and must not be built on.

Same design as biocv_angles.py: one shared CANDIDATE camera set per observation
(cameras seeing all three chain joints); each arm then runs its own rejection loop and
its own estimator, so only the estimator/rejection choice differs.
-> D:/BioCV/BIOCV_LM_ANGLES.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_LM_ANGLES.txt")
STRIDE = int(os.environ.get("BIOCV_STRIDE", "4"))
B = 3000; rng = np.random.default_rng(7)
CHAINS = {"L-knee": (11, 13, 15), "R-knee": (12, 14, 16)}

def ang(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def lm_tri(cs, uvs, w, X0, iters=10):
    X = X0.astype(float).copy(); lam = 1e-3
    for _ in range(iters):
        JtJ = np.zeros((3, 3)); Jtr = np.zeros(3)
        for k, cam in enumerate(cs):
            Xc = cam.R @ (X - cam.C); z = Xc[2]
            if abs(z) < 1e-9: continue
            fx, fy = cam.K[0, 0], cam.K[1, 1]
            proj = np.array([fx * Xc[0] / z + cam.K[0, 2], fy * Xc[1] / z + cam.K[1, 2]])
            r = proj - uvs[k]
            dp = np.array([[fx / z, 0, -fx * Xc[0] / z**2],
                           [0, fy / z, -fy * Xc[1] / z**2]])
            J = dp @ cam.R
            JtJ += w[k] * (J.T @ J); Jtr += w[k] * (J.T @ r)
        try: dX = np.linalg.solve(JtJ + lam * np.eye(3), -Jtr)
        except np.linalg.LinAlgError: break
        if not np.all(np.isfinite(dX)): break
        X = X + dX
        if np.linalg.norm(dX) < 1e-4: break
    return X

def keep(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is None: return idx
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
        idx.pop(worst)
    return idx

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

ARMS = ["dlt_noRej", "dlt_objdRej", "lm_noRej", "lm_repRej", "lm_objdRej"]
rows = []; subj = []; pid2id = {}; seen = 0
prog = "D:/BioCV/_lmang_progress.txt"; open(prog, "w").write("start\n")
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
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
            seen += 1
            if seen % STRIDE: continue
            if len(rows) % 200 == 0: open(prog, "a").write(f"kept={len(rows)} seen={seen}\n")
            cs = [cams[i] for i in vi]
            est = {a: {} for a in ARMS}
            for j in (ja, jb, jc):
                uvs = np.array([det[i][j, :2] for i in vi])
                conf = np.array([det[i][j, 2] for i in vi])
                i_all = keep(cs, uvs, conf, None)
                i_obj = keep(cs, uvs, conf, objd)
                i_rep = keep(cs, uvs, conf, rep)
                def dlt(ix): return R.triangulate_wdlt([cs[i] for i in ix], uvs[ix], conf[ix])
                est["dlt_noRej"][j]   = dlt(i_all)
                est["dlt_objdRej"][j] = dlt(i_obj)
                est["lm_noRej"][j]    = lm_tri(cs, uvs, conf, dlt(i_all))
                est["lm_repRej"][j]   = lm_tri([cs[i] for i in i_rep], uvs[i_rep], conf[i_rep], dlt(i_rep))
                est["lm_objdRej"][j]  = lm_tri([cs[i] for i in i_obj], uvs[i_obj], conf[i_obj], dlt(i_obj))
            e = [ang(est[a][ja], est[a][jb], est[a][jc]) for a in ARMS]
            if not all(np.isfinite(x) for x in e): continue
            rows.append([abs(x - g) for x in e]); subj.append(sid)

rows = np.array(rows); subj = np.array(subj)
E = {a: rows[:, k] for k, a in enumerate(ARMS)}
lines = []
def out(s): print(s); lines.append(s)
out("LM TRIANGULATION AT THE JOINT-ANGLE LEVEL -- decisive test of the surrogate-invalidity thesis.")
out(f"Cache={CACHE}  N={len(rows)} knee-angle observations, {len(pid2id)} subjects, stride={STRIDE}.")
out("Shared candidate camera set per observation; each arm runs its own rejection + estimator.")
out("")
out(f"{'arm':>14}{'mean knee angle error (deg)':>30}")
for a in ARMS: out(f"{a:>14}{E[a].mean():>30.3f}")
out("")
def ci(diff):
    sl = np.unique(subj); idx = {t: np.where(subj == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = diff[ii].mean()
    return diff.mean(), np.percentile(bs, [2.5, 97.5])
out("CONTRASTS (positive = the SECOND arm has lower angle error):")
for a, b, lab in [("lm_noRej", "lm_repRej", "THE DECISIVE ONE: with LM, does rejection help the ANGLE?"),
                  ("lm_repRej", "lm_objdRej", "with LM, does the object-space criterion help the angle?"),
                  ("dlt_noRej", "lm_noRej", "does LM beat DLT at the angle level (no rejection)?"),
                  ("dlt_noRej", "lm_repRej", "best-LM vs plain DLT no-rejection"),
                  ("dlt_noRej", "dlt_objdRej", "DLT reference: does objd rejection help the angle?")]:
    mu, c = ci(E[a] - E[b])
    star = "*" if (c[0] > 0 or c[1] < 0) else " "
    out(f"  {lab:<58} {mu:+.3f} [{c[0]:+.3f},{c[1]:+.3f}]{star}")
out("")
out("READ: in 3D POSITION, lm_repRej beats lm_noRej by +4.12 mm [3.11,5.18] -- the largest")
out("effect in the project. If the surrogate-invalidity thesis holds, the same contrast at")
out("the knee should be ~0. If instead it is a large significant angular gain, the thesis")
out("is FALSE and must not be built on.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
