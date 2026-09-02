"""DECISIVE TEST 3: (a) does a proper geometric (ML) triangulation dominate all the
DLT variants, making the whole weighting/rejection comparison moot? and (b) what is
the detector's ACTUAL pixel-error-vs-distance scaling law, which determines from
first principles what the correct weighting is?

(a) LM ARM. DLT minimises an ALGEBRAIC error whose residual ~ depth x pixel error,
    so it is biased toward distant cameras. The ML estimate under homoscedastic pixel
    noise minimises the sum of squared REPROJECTION errors -- nonlinear, solved by
    Gauss-Newton/LM from the DLT initialisation (3 unknowns, so each iteration is a
    tiny 3x3 solve). If LM dominates every DLT variant, the paper's comparison is a
    comparison of approximations to something one should simply compute properly.

(b) NOISE SCALING. LM-as-ML assumes the same pixel sigma on every camera. If the
    detector's pixel error GROWS with camera distance (the person is smaller in the
    image), the correct weighting is neither uniform nor 1/d. We measure sigma_px vs
    distance directly against Vicon GT and fit sigma_px ~ d^alpha.
      alpha ~ 0   -> pixel noise distance-independent -> reprojection is the right
                     residual; object-space is mis-weighted.
      alpha ~ 1   -> pixel error grows linearly with d -> object-space residuals are
                     the homoscedastic ones -> object-space correct BY DERIVATION.
-> D:/BioCV/BIOCV_LM_NOISE.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_LM_NOISE.txt")
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
B = 3000; rng = np.random.default_rng(7)

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def lm_triangulate(cs, uvs, w, X0, iters=10):
    """Gauss-Newton on sum_i w_i * ||project(cam_i,X) - uv_i||^2 . 3 unknowns."""
    X = X0.astype(float).copy()
    lam = 1e-3
    for _ in range(iters):
        Jt_J = np.zeros((3, 3)); Jt_r = np.zeros(3); cost = 0.0
        for k, cam in enumerate(cs):
            Xc = cam.R @ (X - cam.C)                # camera coords
            z = Xc[2]
            if abs(z) < 1e-9: continue
            f = np.array([cam.K[0, 0], cam.K[1, 1]])
            proj = np.array([cam.K[0, 0] * Xc[0] / z + cam.K[0, 2],
                             cam.K[1, 1] * Xc[1] / z + cam.K[1, 2]])
            r = proj - uvs[k]
            # d(proj)/d(Xc)
            dpdXc = np.array([[f[0] / z, 0, -f[0] * Xc[0] / z**2],
                              [0, f[1] / z, -f[1] * Xc[1] / z**2]])
            J = dpdXc @ cam.R                        # d(proj)/dX
            sw = w[k]
            Jt_J += sw * (J.T @ J); Jt_r += sw * (J.T @ r); cost += sw * r @ r
        try:
            dX = np.linalg.solve(Jt_J + lam * np.eye(3), -Jt_r)
        except np.linalg.LinAlgError:
            break
        if not np.all(np.isfinite(dX)): break
        X = X + dX
        if np.linalg.norm(dX) < 1e-4: break
    return X

def reject(cs, uvs, w, metric):
    idx = list(range(len(cs)))
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

ARMS = ["dlt_conf", "dlt_wd", "objd_conf", "lm_noRej", "lm_repRej", "lm_objdRej"]
# LM in pure Python is ~50x the cost of a DLT solve. Subsample: a mean difference over
# several thousand observations across all 11 subjects has ample power, and the earlier
# full-N run died silently after 4.5h with no progress output (watchdog flagged this).
STRIDE = int(os.environ.get("BIOCV_STRIDE", "6"))
PROG = "D:/BioCV/_lm_progress.txt"
open(PROG, "w").write("starting\n")
rows = []; subj = []; pid2id = {}
noise = []   # (pixel error vs GT projection, camera distance)
_seen = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            if cj not in gt: continue
            Xg = gt[cj]
            if not np.any(Xg): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            _seen += 1
            if _seen % STRIDE: continue
            if len(rows) % 250 == 0:
                open(PROG, "a").write(f"kept={len(rows)} seen={_seen}\n")
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            conf = np.array([det[i][cj, 2] for i in vi])
            dists = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
            asym = dists.max() / dists.min()
            wd = conf / dists
            # (b) detector pixel error vs GT projection, per camera
            for k, i in enumerate(vi):
                e_px = np.linalg.norm(cams[i].project(Xg) - uvs[k])
                noise.append((e_px, dists[k]))
            X_dlt = R.triangulate_wdlt(cs, uvs, conf)
            X_wd = R.triangulate_wdlt(cs, uvs, wd)
            io = reject(cs, uvs, conf, objd)
            X_objd = R.triangulate_wdlt([cs[i] for i in io], uvs[io], conf[io])
            X_lm = lm_triangulate(cs, uvs, conf, X_dlt)
            ir = reject(cs, uvs, conf, rep)
            X_lmr = lm_triangulate([cs[i] for i in ir], uvs[ir], conf[ir],
                                   R.triangulate_wdlt([cs[i] for i in ir], uvs[ir], conf[ir]))
            X_lmo = lm_triangulate([cs[i] for i in io], uvs[io], conf[io], X_objd)
            rows.append([asym] + [np.linalg.norm(x - Xg) for x in
                                  (X_dlt, X_wd, X_objd, X_lm, X_lmr, X_lmo)])
            subj.append(sid)

rows = np.array(rows); subj = np.array(subj); noise = np.array(noise)
asym = rows[:, 0]; E = {a: rows[:, 1 + k] for k, a in enumerate(ARMS)}
lines = []
def out(s): print(s); lines.append(s)

out(f"LM (geometric/ML) triangulation vs DLT variants, and detector noise scaling.")
out(f"Cache={CACHE}  N={len(rows)} obs, {len(pid2id)} subjects, severe joints.")
out("")
out("--- (b) DETECTOR PIXEL ERROR vs CAMERA DISTANCE (vs Vicon GT projection) ---")
d = noise[:, 1]; e = noise[:, 0]
qs = np.percentile(d, [0, 20, 40, 60, 80, 100])
out(f"{'dist bin (mm)':>18}{'n':>8}{'median e_px':>13}{'mean e_px':>11}{'p90 e_px':>10}")
cent = []; med = []
for i in range(5):
    m = (d >= qs[i]) & (d < qs[i + 1] if i < 4 else d <= qs[i + 1])
    if m.sum() < 50: continue
    out(f"{f'{qs[i]:.0f}-{qs[i+1]:.0f}':>18}{int(m.sum()):>8}{np.median(e[m]):>13.2f}"
        f"{e[m].mean():>11.2f}{np.percentile(e[m],90):>10.2f}")
    cent.append(d[m].mean()); med.append(np.median(e[m]))
cent = np.array(cent); med = np.array(med)
alpha = np.polyfit(np.log(cent), np.log(med), 1)[0]
out(f"power-law fit on medians: sigma_px ~ d^alpha with alpha = {alpha:+.3f}")
out("  alpha~0 => pixel noise distance-independent => REPROJECTION is the correctly-")
out("            weighted residual, object-space over-weights far cameras.")
out("  alpha~1 => pixel error grows linearly with d => OBJECT-SPACE residuals are the")
out("            homoscedastic ones => object-space correct by derivation.")
out("")
out("--- (a) ARM MATRIX incl. proper geometric (LM) triangulation ---")
out(f"{'asym bin':>9}{'n':>7}" + "".join(f"{a:>12}" for a in ARMS))
bins = [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]
for lo, hi, nm in bins:
    m = (asym >= lo) & (asym < hi)
    if m.sum() < 30: continue
    out(f"{nm:>9}{int(m.sum()):>7}" + "".join(f"{E[a][m].mean():>12.2f}" for a in ARMS))
out(f"{'ALL':>9}{len(rows):>7}" + "".join(f"{E[a].mean():>12.2f}" for a in ARMS))
out("")

def ci_of(diff, mask):
    sj = subj[mask]; sl = np.unique(sj)
    idx = {t: np.where(sj == t)[0] for t in sl}
    dd = diff[mask]; bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = dd[ii].mean()
    return dd.mean(), np.percentile(bs, [2.5, 97.5])

def contrast(a, b, label):
    out(f"--- {label}: {a} minus {b} (POSITIVE = '{b}' better) ---")
    diff = E[a] - E[b]
    for lo, hi, nm in bins:
        m = (asym >= lo) & (asym < hi)
        if m.sum() < 30: continue
        mu, ci = ci_of(diff, m)
        star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
        out(f"{nm:>9}{int(m.sum()):>7}{mu:>+9.2f}{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>20}")
    mu, ci = ci_of(diff, np.ones(len(rows), bool))
    star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
    out(f"{'ALL':>9}{len(rows):>7}{mu:>+9.2f}{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>20}")
    out("")

contrast("dlt_wd", "lm_noRej", "Does proper LM beat the best DLT tweak (1/d weighting)?")
contrast("objd_conf", "lm_noRej", "Does proper LM beat the paper's object-space rejection?")
contrast("lm_noRej", "lm_repRej", "With LM, does reprojection rejection still add anything?")
contrast("lm_repRej", "lm_objdRej", "With LM, does the object-space CRITERION help?")
out("READ: if lm_noRej dominates dlt_wd and objd_conf, the entire DLT-tweak comparison")
out("is moot and the honest recommendation is 'use a proper geometric triangulation'.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
