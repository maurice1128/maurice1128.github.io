"""DEPLOYABLE-REGIME test (Measurement path, action A).

Unlike biocv_clustered.py (which ENUMERATES C(9,6)=84 six-camera subsets to
manufacture a wide asymmetry range), this uses the ACTUAL FULL RIG: every camera
that detects the joint is used, exactly as a real Pose2Sim-style pipeline would.
The asymmetry per joint-observation is therefore the REAL max/min camera-distance
ratio the deployed 9-camera ring produces -- not a manufactured one.

Reports: (1) the real deployable asymmetry distribution, (2) reproj vs object-space
net 3D error stratified by that real asymmetry, subject-cluster bootstrap 95% CI.
Answers the referee question "when does the metric choice matter in a real rig?"
-> D:/BioCV/BIOCV_FULLRIG.txt
"""
import glob, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K = 3.0
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
B = 3000; rng = np.random.default_rng(7)

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)
def iter_rm(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

rows = []; subj = []; pid2id = {}
for ti, f in enumerate(sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl"))):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue          # use ALL valid cameras (full rig)
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            w = np.array([det[i][cj, 2] for i in vi])
            dists = [np.linalg.norm(cams[i].C - Xg) for i in vi]
            asym = max(dists) / min(dists)
            Xr = iter_rm(cs, uvs, w, rep); Xd = iter_rm(cs, uvs, w, objd)
            rows.append((asym, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg), len(vi)))
            subj.append(sid)
rows = np.array(rows); subj = np.array(subj)
asym, er, ed, ncam = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3].astype(int)
nsub = len(pid2id)
lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real Vicon GT -- FULL-RIG (deployable) analysis, N={len(rows)} joint-observations "
    f"from {nsub} subjects. Each obs uses ALL cameras that detect the joint (mean {ncam.mean():.1f}, "
    f"range {ncam.min()}-{ncam.max()}).")
out(f"REAL deployable asymmetry distribution (max/min camera-distance over the full rig): "
    f"median={np.median(asym):.2f} p25={np.percentile(asym,25):.2f} p75={np.percentile(asym,75):.2f} "
    f"p90={np.percentile(asym,90):.2f} p95={np.percentile(asym,95):.2f} max={asym.max():.2f}")
frac_hi = 100 * np.mean(asym >= 3.0)
out(f"Fraction of real full-rig observations at asym>=3 (where the subset study saw the effect): {frac_hi:.1f}%")
out(f"d = err_reproj - err_dist (mm); +=object-space better. SUBJECT-cluster bootstrap 95% CI "
    f"(inferential unit = subject; n={nsub}).")
out(f"{'asym bin':>10}{'n':>8}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'   dMEAN 95%CI':>20}")
for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]:
    m = (asym >= lo) & (asym < hi)
    if m.sum() < 30: out(f"{nm:>10}{int(m.sum()):>8}   few"); continue
    er_b, ed_b, sj_b = er[m], ed[m], subj[m]; d = er_b - ed_b
    sl = np.unique(sj_b); idx = {t: np.where(sj_b == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
    ci = np.percentile(bs, [2.5, 97.5])
    star = "*" if (len(sl) >= 4 and (ci[0] > 0 or ci[1] < 0)) else " "
    cistr = f"[{ci[0]:+.2f},{ci[1]:+.2f}]{star}"
    out(f"{nm:>10}{int(m.sum()):>8}{er_b.mean():>9.1f}{ed_b.mean():>9.1f}{d.mean():>+8.2f}{cistr:>20}")
# overall (the single number a deployment cares about)
d_all = er - ed
sl = np.unique(subj); idx = {t: np.where(subj == t)[0] for t in sl}
bs = np.empty(B)
for b in range(B):
    pick = rng.choice(sl, size=len(sl), replace=True)
    ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er[ii] - ed[ii]).mean()
ci = np.percentile(bs, [2.5, 97.5])
out(f"OVERALL (full-rig, all obs pooled): dMEAN={d_all.mean():+.2f} mm, "
    f"subject-cluster CI [{ci[0]:+.2f},{ci[1]:+.2f}] -> the net effect a real deployment sees.")
open("D:/BioCV/BIOCV_FULLRIG.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
