"""Clean, thorough test of the user's key claim: at HIGH camera-distance asymmetry
(common when people walk to the edge of a large capture volume), does object-space
(distance) outlier removal's advantage over reprojection HOLD and GROW?

Uses BioCV balanced cache (clean RTMPose detections, real Vicon GT, natural outliers).
For each joint-observation, enumerates 6-camera SUBSETS of the available cameras
(clustered subsets manufacture a wide range of asymmetry from a centreline walker),
runs the SAME iterative same-MAD removal with each metric, errors vs Vicon GT,
stratified by the subset's own max/min camera-distance asymmetry, with trial-cluster
bootstrap 95% CIs. -> D:/BioCV/BIOCV_CLUSTERED.txt
"""
import glob, os, pickle, itertools, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_balanced")
OUT = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_CLUSTERED.txt")

MIN_CAM = 4; K = 3.0; SUBSET = 6
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

rows = []; subj = []  # cluster by SUBJECT (council fix: subject is the inferential unit, not trial)
pid2id = {}
for ti, f in enumerate(sorted(glob.glob(f"{CACHE}/*.pkl"))):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < SUBSET: continue
            for sub in itertools.combinations(vi, SUBSET):
                cs = [cams[i] for i in sub]
                uvs = np.array([det[i][cj, :2] for i in sub])
                w = np.array([det[i][cj, 2] for i in sub])
                dists = [np.linalg.norm(cams[i].C - Xg) for i in sub]
                asym = max(dists) / min(dists)
                Xr = iter_rm(cs, uvs, w, rep); Xd = iter_rm(cs, uvs, w, objd)
                rows.append((asym, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg), ti))
                subj.append(sid)
rows = np.array(rows); subj = np.array(subj)
asym, er, ed, tr = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3].astype(int)
nsub = len(pid2id)
lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real Vicon GT, clustered {SUBSET}-cam subsets, N={len(rows)} subset-obs "
    f"(NOT the inferential N) from {nsub} subjects / {len(np.unique(tr))} trials, "
    f"asym median={np.median(asym):.2f} p90={np.percentile(asym,90):.2f} max={asym.max():.2f}")
_ciq = ("CI UNDEFINED (degeneracy, <4 clusters)" if nsub < 4
        else f"CI computable but FRAGILE from only {nsub} clusters "
             f"(well below the ~30+ needed for trustworthy coverage; >=~8 preferred; treat as preliminary)")
out(f"d = err_reproj - err_dist (mm); +=distance better. SUBJECT-cluster bootstrap 95% CI "
    f"(inferential unit = subject; n={nsub} subjects -> {_ciq}).")
out(f"{'asym bin':>10}{'n':>8}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'   dMEAN 95%CI':>18}{'dP95':>8}")
for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,3,'2-3'),(3,4,'3-4'),(4,6,'4-6'),(6,99,'>6')]:
    m = (asym >= lo) & (asym < hi)
    if m.sum() < 30: out(f"{nm:>10}{int(m.sum()):>8}   few"); continue
    er_b, ed_b, sj_b = er[m], ed[m], subj[m]; d = er_b - ed_b
    sl = np.unique(sj_b); idx = {t: np.where(sj_b == t)[0] for t in sl}   # cluster by SUBJECT
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
    ci = np.percentile(bs, [2.5, 97.5])
    n_cl = len(sl)
    # A cluster bootstrap with <4 clusters cannot represent between-subject variance;
    # any "exclusion of 0" is a degeneracy artifact, NOT significance. Do not star it.
    if n_cl < 4:
        cistr = f"[{ci[0]:+.2f},{ci[1]:+.2f}] UNDEF(n_subj={n_cl}<4)"
    else:
        star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
        cistr = f"[{ci[0]:+.2f},{ci[1]:+.2f}]{star}"
    out(f"{nm:>10}{int(m.sum()):>8}{er_b.mean():>9.1f}{ed_b.mean():>9.1f}{d.mean():>+8.2f}"
        f"{cistr:>28}{np.percentile(er_b,95)-np.percentile(ed_b,95):>+8.1f}")
if nsub < 4:
    out("NOTE: <4 subjects -> subject-cluster CI UNDEFINED (degeneracy), not significance; >=~8 preferred.")
else:
    out(f"NOTE: subject-cluster CIs are computable but FRAGILE from n={nsub} clusters (well below the ~30+ "
        "needed for trustworthy cluster-bootstrap coverage; >=~8 preferred). '*' = CI excludes 0 "
        "(subject-level significant, but PRELIMINARY at this cluster count).")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
