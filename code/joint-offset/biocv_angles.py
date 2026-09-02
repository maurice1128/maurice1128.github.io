"""JOINT-ANGLE analysis -- the decisive experiment for a Journal of Biomechanics
submission. Biomechanists do not care about 3D joint-centre position error in mm;
they care about JOINT KINEMATICS in degrees.

Fixes two flaws in the earlier `biocv_final.py` angle pipeline:
  (1) it gave each arm a DIFFERENT camera set (association at 40 px vs 100 mm), so the
      comparison confounded association with the rejection criterion. Here every arm
      sees the SAME cameras; only the rejection criterion / triangulation weighting
      differs.
  (2) it used single removal on 2 subjects from video. Here: iterative MAD removal,
      11 subjects, from the distortion-corrected cache.

Angles (COCO): knee = angle(hip, knee, ankle); elbow = angle(shoulder, elbow, wrist),
both sides. Error = |estimated - Vicon| in degrees. Subject-cluster bootstrap CI.
-> D:/BioCV/BIOCV_ANGLES.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_ANGLES.txt")
B = 3000; rng = np.random.default_rng(7)

# COCO-17: 5/6 shoulder, 7/8 elbow, 9/10 wrist, 11/12 hip, 13/14 knee, 15/16 ankle
CHAINS = {
    "L-knee":  (11, 13, 15), "R-knee":  (12, 14, 16),
    "L-elbow": (5, 7, 9),    "R-elbow": (6, 8, 10),
}

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
rows = []; subj = []; chain_of = []; pid2id = {}
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for cname, (ja, jb, jc) in CHAINS.items():
            if not all(j in gt and np.any(gt[j]) for j in (ja, jb, jc)): continue
            gt_ang = ang(gt[ja], gt[jb], gt[jc])
            if not np.isfinite(gt_ang): continue
            # SAME camera set for every arm: cameras that see ALL THREE joints
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0
                                            for j in (ja, jb, jc))]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            # asymmetry measured at the middle (moving) joint
            dists = np.array([np.linalg.norm(cams[i].C - gt[jb]) for i in vi])
            asym = dists.max() / dists.min()
            est = {a: {} for a in ARMS}
            for j in (ja, jb, jc):
                uvs = np.array([det[i][j, :2] for i in vi])
                conf = np.array([det[i][j, 2] for i in vi])
                dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                wd = conf / dj
                est["noRej_conf"][j] = solve(cs, uvs, conf, None)
                est["noRej_wd"][j]   = solve(cs, uvs, wd,   None)
                est["rep_conf"][j]   = solve(cs, uvs, conf, rep)
                est["objd_conf"][j]  = solve(cs, uvs, conf, objd)
                est["rep_wd"][j]     = solve(cs, uvs, wd,   rep)
                est["objd_wd"][j]    = solve(cs, uvs, wd,   objd)
            errs = []
            for a in ARMS:
                e = ang(est[a][ja], est[a][jb], est[a][jc])
                errs.append(abs(e - gt_ang) if np.isfinite(e) else np.nan)
            if not all(np.isfinite(x) for x in errs): continue
            rows.append([asym] + errs); subj.append(sid); chain_of.append(cname)

rows = np.array(rows); subj = np.array(subj); chain_of = np.array(chain_of)
asym = rows[:, 0]; E = {a: rows[:, 1 + k] for k, a in enumerate(ARMS)}
lines = []
def out(s): print(s); lines.append(s)

out("JOINT-ANGLE error (degrees) vs Vicon -- the outcome biomechanists care about.")
out(f"Cache={CACHE}  N={len(rows)} joint-angle observations, {len(pid2id)} subjects.")
out("All arms use the SAME camera set per observation; only rejection/weighting differs.")
out("")

def ci_of(diff, mask):
    sj = subj[mask]; sl = np.unique(sj)
    idx = {t: np.where(sj == t)[0] for t in sl}
    d = diff[mask]; bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = d[ii].mean()
    return d.mean(), np.percentile(bs, [2.5, 97.5])

for scope, mask0 in [("KNEE (gait-relevant)", np.isin(chain_of, ["L-knee", "R-knee"])),
                     ("ELBOW", np.isin(chain_of, ["L-elbow", "R-elbow"])),
                     ("ALL CHAINS", np.ones(len(rows), bool))]:
    out(f"=== {scope} | n={int(mask0.sum())} ===")
    out(f"{'asym bin':>9}{'n':>7}" + "".join(f"{a:>12}" for a in ARMS))
    for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]:
        m = mask0 & (asym >= lo) & (asym < hi)
        if m.sum() < 30: continue
        out(f"{nm:>9}{int(m.sum()):>7}" + "".join(f"{E[a][m].mean():>12.2f}" for a in ARMS))
    out(f"{'ALL':>9}{int(mask0.sum()):>7}" + "".join(f"{E[a][mask0].mean():>12.2f}" for a in ARMS))
    # key contrasts, POSITIVE = second arm better
    for a, b, lab in [("rep_conf", "noRej_conf", "does reproj rejection beat NO rejection?"),
                      ("objd_conf", "noRej_conf", "does object-space rejection beat NO rejection?"),
                      ("rep_conf", "objd_conf", "object-space vs reprojection criterion"),
                      ("rep_conf", "rep_wd", "does 1/d triangulation weighting help?"),
                      ("noRej_conf", "noRej_wd", "1/d weighting WITHOUT any rejection"),
                      ("rep_wd", "noRej_wd", "best-weighted: is rejection still harmful?"),
                      ("objd_wd", "noRej_wd", "no-rejection+1/d vs objd+1/d")]:
        mu, ci = ci_of(E[a] - E[b], mask0)
        star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
        out(f"   {lab:<48} {a} - {b} = {mu:+.3f} deg [{ci[0]:+.3f},{ci[1]:+.3f}]{star}")
    out("")

out("READ: POSITIVE contrast = the SECOND arm has lower angle error (is better).")
out("If noRej beats both rejection arms on knee angle, the honest message for a")
out("biomechanics readership is that the outlier-rejection step degrades kinematics.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
