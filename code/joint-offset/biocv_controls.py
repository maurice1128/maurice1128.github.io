"""REFEREE-RESPONSE CONTROLS (addresses objections M2, M5, M6, M8 in one pass).

M5  no-rejection baseline: triangulate with ALL detected cameras, reject nothing.
    (The referee: a guideline about which rejection criterion to use is meaningless
     without the do-nothing arm; FINAL_RESULT2 suggests no-removal may beat both.)
M6  all-joints scope: the headline +0.15mm was ankles+wrists only but was described
    as "what a real deployment sees". Report BOTH scopes.
M2  false-rejection / operating point: report mean cameras RETAINED per metric per
    bin. If object-space systematically prunes more (or prunes far cameras), the
    comparison is confounded with estimator variance, not outlier identification.
M8  per-bin SUBJECT-CLUSTER COUNTS and leave-one-subject-out, plus the pooled effect
    EXCLUDING the 3-4 tail bin (which carries ~2% of data but most of the pooled mean).

Set UNDISTORT=1 to run on distortion-corrected detections (referee objection M1).
-> D:/BioCV/BIOCV_CONTROLS.txt
"""
import glob, os, pickle, numpy as np, sys, cv2
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
# Read from a pre-undistorted cache (built by biocv_make_undist_cache.py) so no
# per-point cv2 calls are needed. Set BIOCV_CACHE to _cache_balanced for the
# uncorrected (as-published) comparison.
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_CONTROLS.txt")
UNDISTORT = False   # cache is already corrected; no per-point undistortion here
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
# full-body COCO-17 minus face keypoints (0-4), which have no meaningful Vicon GT
ALL = {f"j{c}": c for c in range(5, 17)}
B = 3000; rng = np.random.default_rng(7)

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def iter_rm(cs, uvs, w, metric):
    """returns (X, n_retained)"""
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]
    return R.triangulate_wdlt(CS, uvs[idx], w[idx]), len(idx)

CAMS = {}; UND = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

def undistort_block(cam, uv_arr):
    if not UNDISTORT: return uv_arr
    pts = np.asarray(uv_arr, float).reshape(-1, 1, 2)
    d = np.asarray(cam.dist, float).reshape(1, -1)
    return cv2.undistortPoints(pts, cam.K, d, P=cam.K).reshape(-1, 2)

def run(joints, tag, lines):
    rows = []; subj = []; pid2id = {}
    for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
        D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
        sid = pid2id.setdefault(D["pid"], len(pid2id))
        for fr in D["frames"]:
            det = fr["det"]; gt = fr["gt"]
            for jn, cj in joints.items():
                # gt is a DICT keyed by joint index (keys 5..16) -- NOT a list.
                # (An earlier `cj >= len(gt)` guard silently dropped the ankles.)
                if cj not in gt: continue
                Xg = gt[cj]
                if not np.any(Xg): continue
                vi = [i for i, dd in enumerate(det)
                      if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
                if len(vi) < MIN_CAM: continue
                cs = [cams[i] for i in vi]
                uvs = np.array([det[i][cj, :2] for i in vi])
                if UNDISTORT:
                    uvs = np.array([undistort_block(cams[i], det[i][cj, :2][None, :])[0] for i in vi])
                w = np.array([det[i][cj, 2] for i in vi])
                dists = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
                asym = dists.max() / dists.min()
                Xn = R.triangulate_wdlt(cs, uvs, w)                 # M5: NO rejection
                Xr, nr = iter_rm(cs, uvs, w, rep)
                Xd, nd = iter_rm(cs, uvs, w, objd)
                rows.append((asym, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg),
                             np.linalg.norm(Xn - Xg), nr, nd, len(vi)))
                subj.append(sid)
    rows = np.array(rows); subj = np.array(subj)
    asym, er, ed, en, nr, nd, nv = (rows[:,0], rows[:,1], rows[:,2], rows[:,3],
                                    rows[:,4], rows[:,5], rows[:,6])
    def out(s): print(s); lines.append(s)
    out(f"=== {tag} | N={len(rows)} obs, {len(pid2id)} subjects, undistort={UNDISTORT} ===")
    out(f"{'asym bin':>9}{'n':>7}{'nSubj':>6}{'noRej':>8}{'reproj':>8}{'objd':>8}"
        f"{'d(re-ob)':>9}{'  d 95%CI':>18}{'keepRe':>7}{'keepOb':>7}")
    for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]:
        m = (asym >= lo) & (asym < hi)
        if m.sum() < 30: continue
        sj_b = subj[m]; sl = np.unique(sj_b)
        idx = {t: np.where(sj_b == t)[0] for t in sl}
        er_b, ed_b = er[m], ed[m]
        bs = np.empty(B)
        for b in range(B):
            pick = rng.choice(sl, size=len(sl), replace=True)
            ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
        ci = np.percentile(bs, [2.5, 97.5])
        star = "*" if (len(sl) >= 4 and (ci[0] > 0 or ci[1] < 0)) else " "
        out(f"{nm:>9}{int(m.sum()):>7}{len(sl):>6}{en[m].mean():>8.1f}{er_b.mean():>8.1f}"
            f"{ed_b.mean():>8.1f}{(er_b-ed_b).mean():>+9.2f}{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>18}"
            f"{nr[m].mean():>7.2f}{nd[m].mean():>7.2f}")
    def pooled(mask, label):
        sj_b = subj[mask]; sl = np.unique(sj_b)
        idx = {t: np.where(sj_b == t)[0] for t in sl}
        er_b, ed_b, en_b = er[mask], ed[mask], en[mask]
        bs = np.empty(B)
        for b in range(B):
            pick = rng.choice(sl, size=len(sl), replace=True)
            ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
        ci = np.percentile(bs, [2.5, 97.5])
        out(f"{label}: d(reproj-objd)={(er_b-ed_b).mean():+.3f} CI[{ci[0]:+.3f},{ci[1]:+.3f}] | "
            f"noRej={en_b.mean():.2f} reproj={er_b.mean():.2f} objd={ed_b.mean():.2f} mm "
            f"| d(noRej-objd)={(en_b-ed_b).mean():+.3f} d(noRej-reproj)={(en_b-er_b).mean():+.3f}")
    pooled(np.ones(len(rows), bool), "POOLED all")
    pooled(asym < 3, "POOLED excl 3-4 tail")
    # M8 leave-one-subject-out on the 3-4 bin
    m34 = (asym >= 3) & (asym < 4)
    if m34.sum() > 30:
        sl = np.unique(subj[m34])
        contrib = [(int(s), int((subj[m34] == s).sum())) for s in sl]
        out(f"3-4 bin per-subject obs: {contrib}")
        loo = []
        for s in sl:
            k = m34 & (subj != s)
            loo.append((int(s), (er[k] - ed[k]).mean()))
        out(f"3-4 bin leave-one-subject-out dMEAN: {[(a, round(b,2)) for a,b in loo]}")
    out("")

lines = []
run(SEV, "A) SEVERE joints only (ankles+wrists) -- the published scope", lines)
run(ALL, "B) ALL body joints (COCO 5-16) -- the true deployment scope", lines)
lines.append("READ: 'noRej' = triangulate with all cameras, reject nothing (M5 control).")
lines.append("If noRej <= both reproj and objd, the rejection step itself is not helping and the")
lines.append("guideline must say so. keepRe/keepOb = mean cameras retained (M2 operating point).")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
