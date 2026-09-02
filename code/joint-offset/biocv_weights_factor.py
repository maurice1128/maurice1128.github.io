"""WEIGHT FACTORISATION (addresses referee objection F9 / ledger F9).

The pipeline weights the DLT by RTMPose confidence. That was never justified, and
confidence is plausibly itself distance-dependent (a person further away is smaller in
the image, so keypoint confidence may fall). If so, `conf/d` weighting applies the
distance factor TWICE -- the same error we criticise when distance-based rejection is
combined with distance weighting.

This decomposes the weighting into its factors, on both outcomes:
    w = 1          uniform (no weighting at all)
    w = conf       detector confidence only        (current practice)
    w = 1/d        distance only
    w = conf/d     both                            (our proposed fix)
    w = conf/d^2   distance squared (inverse-variance-like)
plus the DIAGNOSTIC: how does confidence actually vary with camera distance?

All arms use NO rejection, so only the weighting differs.
-> D:/BioCV/BIOCV_WEIGHTFACTOR.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_WEIGHTFACTOR.txt")
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
KNEE = {"L-knee": (11, 13, 15), "R-knee": (12, 14, 16)}
B = 3000; rng = np.random.default_rng(7)

def ang(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

WARMS = ["uniform", "conf", "inv_d", "conf_d", "conf_d2"]
def weights(conf, d):
    return {"uniform": np.ones_like(conf), "conf": conf, "inv_d": 1.0 / d,
            "conf_d": conf / d, "conf_d2": conf / d**2}

# ---------- diagnostic + 3D position ----------
pos_rows = []; pos_subj = []; pid2id = {}
cd = []            # (confidence, camera distance)
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            if cj not in gt or not np.any(gt[cj]): continue
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            conf = np.array([det[i][cj, 2] for i in vi])
            dists = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
            for k in range(len(vi)): cd.append((conf[k], dists[k]))
            W = weights(conf, dists)
            pos_rows.append([np.linalg.norm(R.triangulate_wdlt(cs, uvs, W[a]) - Xg) for a in WARMS])
            pos_subj.append(sid)
pos = np.array(pos_rows); pos_subj = np.array(pos_subj); cd = np.array(cd)

# ---------- knee angle ----------
ang_rows = []; ang_subj = []
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id[D["pid"]]
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for cname, (ja, jb, jc) in KNEE.items():
            if not all(j in gt and np.any(gt[j]) for j in (ja, jb, jc)): continue
            g = ang(gt[ja], gt[jb], gt[jc])
            if not np.isfinite(g): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in (ja, jb, jc))]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            est = {a: {} for a in WARMS}
            for j in (ja, jb, jc):
                uvs = np.array([det[i][j, :2] for i in vi])
                conf = np.array([det[i][j, 2] for i in vi])
                dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                W = weights(conf, dj)
                for a in WARMS: est[a][j] = R.triangulate_wdlt(cs, uvs, W[a])
            e = [ang(est[a][ja], est[a][jb], est[a][jc]) for a in WARMS]
            if not all(np.isfinite(x) for x in e): continue
            ang_rows.append([abs(x - g) for x in e]); ang_subj.append(sid)
ang_arr = np.array(ang_rows); ang_subj = np.array(ang_subj)

lines = []
def out(s): print(s); lines.append(s)

out("WEIGHT FACTORISATION -- which factor in the DLT weights is doing the work?")
out(f"Cache={CACHE}, {len(pid2id)} subjects. NO rejection in any arm; only weighting differs.")
out("")
out("--- DIAGNOSTIC: is detector confidence itself distance-dependent? ---")
c, d = cd[:, 0], cd[:, 1]
out(f"corr(confidence, camera distance) = {np.corrcoef(c, d)[0,1]:+.3f}   (n={len(cd)})")
qs = np.percentile(d, [0, 25, 50, 75, 100])
out(f"{'distance bin (mm)':>20}{'n':>9}{'mean conf':>11}{'median conf':>13}")
cen, mc = [], []
for i in range(4):
    m = (d >= qs[i]) & (d <= qs[i+1] if i == 3 else d < qs[i+1])
    if m.sum() < 50: continue
    out(f"{f'{qs[i]:.0f}-{qs[i+1]:.0f}':>20}{int(m.sum()):>9}{c[m].mean():>11.3f}{np.median(c[m]):>13.3f}")
    cen.append(d[m].mean()); mc.append(c[m].mean())
if len(cen) >= 2:
    beta = np.polyfit(np.log(cen), np.log(mc), 1)[0]
    out(f"power-law fit: confidence ~ d^{beta:+.3f}")
    out(f"  If beta is strongly negative, 'conf' already encodes distance and dividing by d")
    out(f"  again double-counts it -- the same error as combining distance rejection + weighting.")
out("")

def table(arr, subj_a, unit, label):
    out(f"--- {label} (N={len(arr)} obs) ---")
    out(f"{'weighting':>12}{'mean':>10}{'  vs conf (95% CI)':>26}")
    base = arr[:, WARMS.index("conf")]
    sl = np.unique(subj_a); idx = {t: np.where(subj_a == t)[0] for t in sl}
    for k, a in enumerate(WARMS):
        diff = base - arr[:, k]         # positive => arm k better than conf
        bs = np.empty(B)
        for b in range(B):
            pick = rng.choice(sl, size=len(sl), replace=True)
            ii = np.concatenate([idx[t] for t in pick]); bs[b] = diff[ii].mean()
        ci = np.percentile(bs, [2.5, 97.5])
        star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
        s = "  (reference)" if a == "conf" else f"{diff.mean():+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]{star}"
        out(f"{a:>12}{arr[:, k].mean():>10.3f}{s:>26}")
    out(f"   ({unit}; POSITIVE = better than the current confidence weighting)")
    out("")

table(pos, pos_subj, "mm", "3D POSITION error, peripheral joints")
table(ang_arr, ang_subj, "deg", "KNEE ANGLE error")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
