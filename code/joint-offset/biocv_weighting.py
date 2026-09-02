"""DECISIVE TEST 2 (council R2's baseline reversal), on DISTORTION-CORRECTED data.

Council R2 showed, on UNCORRECTED detections, that simply dividing the DLT weights
by camera distance (keeping reprojection as the rejection criterion) beats the
paper's object-space-rejection proposal by +1.51 mm pooled, and that when BOTH arms
get distance weighting -- so only the REJECTION CRITERION differs -- object-space
becomes significantly WORSE (-0.57 pooled, -1.87 at ratio 3-4).

But distortion is near-camera-biased (near/far displacement ratio 2.82, this repo's
BIOCV_UNDISTORT.txt), so 1/d weighting may win largely by down-weighting the
high-distortion near cameras. This script therefore runs the full arm matrix on
DISTORTION-CORRECTED detections to separate the two explanations.

ARMS (rejection criterion x triangulation weighting):
  none   /w=conf        no rejection, detector-confidence weights   (M5 control)
  none   /w=conf/dist   no rejection, distance-downweighted
  reproj /w=conf        as published
  objd   /w=conf        the paper's proposal
  reproj /w=conf/dist   council R2's proposed baseline
  objd   /w=conf/dist   controlled comparison (only criterion differs)
-> D:/BioCV/BIOCV_WEIGHTING.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_WEIGHTING.txt")
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
B = 3000; rng = np.random.default_rng(7)

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def solve(cs, uvs, w, metric):
    """metric=None -> no rejection. Returns triangulated X."""
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
    CS = [cs[i] for i in idx]
    return R.triangulate_wdlt(CS, uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

ARMS = ["none_conf", "none_wd", "rep_conf", "objd_conf", "rep_wd", "objd_wd"]
rows = []; subj = []; pid2id = {}
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            conf = np.array([det[i][cj, 2] for i in vi])
            dists = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
            asym = dists.max() / dists.min()
            wd = conf / dists                     # distance-downweighted
            errs = [
                np.linalg.norm(solve(cs, uvs, conf, None) - Xg),
                np.linalg.norm(solve(cs, uvs, wd,   None) - Xg),
                np.linalg.norm(solve(cs, uvs, conf, rep) - Xg),
                np.linalg.norm(solve(cs, uvs, conf, objd) - Xg),
                np.linalg.norm(solve(cs, uvs, wd,   rep) - Xg),
                np.linalg.norm(solve(cs, uvs, wd,   objd) - Xg),
            ]
            rows.append([asym] + errs); subj.append(sid)

rows = np.array(rows); subj = np.array(subj)
asym = rows[:, 0]; E = {a: rows[:, 1 + k] for k, a in enumerate(ARMS)}
lines = []
def out(s): print(s); lines.append(s)

out(f"ARM MATRIX on {'DISTORTION-CORRECTED' if 'undist' in CACHE else 'UNCORRECTED'} detections "
    f"({CACHE}). N={len(rows)} obs, {len(pid2id)} subjects, severe joints.")
out("Mean 3D error (mm) per arm; rejection criterion x triangulation weighting.")
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
    d = diff[mask]; bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = d[ii].mean()
    return d.mean(), np.percentile(bs, [2.5, 97.5])

def contrast(a, b, label):
    out(f"--- {label}:  {a} minus {b}   (POSITIVE = '{b}' is better) ---")
    out(f"{'asym bin':>9}{'n':>7}{'diff':>9}{'   95%CI':>20}")
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

contrast("rep_conf", "objd_conf", "PAPER'S CLAIM (conf weights): does object-space rejection help?")
contrast("rep_conf", "rep_wd",   "COUNCIL R2 BASELINE: does 1/d TRIANGULATION weighting beat the base?")
contrast("objd_conf", "rep_wd",  "R2's KEY REVERSAL: 1/d weighting vs the paper's object-space rejection")
contrast("rep_wd",  "objd_wd",   "CONTROLLED (both 1/d weighted): does the CRITERION still help?")
contrast("none_conf", "rep_conf","M5: does rejection help at all? (no-rejection vs reproj)")
contrast("none_conf", "objd_conf","M5: no-rejection vs object-space")
out("READ: if 'rep_wd' wins big here too, distance-WEIGHTING (not distance-based rejection)")
out("is the real effect, and the paper must be restructured around it. If its advantage")
out("collapses relative to the uncorrected run, much of R2's reversal was a distortion artefact.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
