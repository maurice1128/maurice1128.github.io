"""Disentangle ASYMMETRY from the narrow-BASELINE confound using REAL BioCV data +
real Vicon GT (trustworthy), instead of a synthetic sim. For every 6-camera subset
compute BOTH: camera-distance asymmetry (max/min dist to joint) AND baseline width
(mean pairwise angle between camera->joint directions; wide=spread, narrow=clustered).
Then stratify dMEAN (reproj-err minus distance-err) by BOTH. The key question:
within a FIXED baseline band, does the distance advantage still grow with asymmetry?
If yes -> asymmetry is the real driver (user right). If it flattens -> it was baseline.
-> D:/BioCV/BIOCV_DISENTANGLE.txt
"""
import glob, pickle, itertools, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K = 3.0; SUBSET = 6
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}

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

def baseline_deg(cams_sub, Xg):
    """mean pairwise angle (deg) between camera->joint unit directions."""
    dirs = []
    for c in cams_sub:
        v = c.C - Xg; dirs.append(v / np.linalg.norm(v))
    dirs = np.array(dirs); ang = []
    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            ang.append(np.degrees(np.arccos(np.clip(dirs[i] @ dirs[j], -1, 1))))
    return np.mean(ang)

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

rows = []  # (asym, baseline_deg, err_re, err_di, trial)
for ti, f in enumerate(sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl"))):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
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
                bl = baseline_deg(cs, Xg)
                Xr = iter_rm(cs, uvs, w, rep); Xd = iter_rm(cs, uvs, w, objd)
                rows.append((asym, bl, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg), ti))
rows = np.array(rows)
asym, bl, er, ed, tr = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3], rows[:, 4].astype(int)
lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real GT, N={len(rows)} subset-obs. baseline=mean pairwise cam-direction angle(deg).")
out(f"baseline range: p10={np.percentile(bl,10):.0f} median={np.median(bl):.0f} p90={np.percentile(bl,90):.0f} deg")
out("dMEAN = err_reproj - err_dist (mm); + = distance better. Cell = mean dMEAN (n).")
BL = [(0,45,'narrow<45'),(45,65,'mid45-65'),(65,200,'wide>65')]
AS = [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,9,'>3')]
label = "base\\asym"
hdr = f"{label:>14}" + "".join(f"{nm:>13}" for *_,nm in AS)
out(hdr)
for blo, bhi, bnm in BL:
    cells = []
    for alo, ahi, anm in AS:
        m = (bl >= blo) & (bl < bhi) & (asym >= alo) & (asym < ahi)
        if m.sum() < 50: cells.append(f"{'-':>13}"); continue
        cells.append(f"{(er[m]-ed[m]).mean():>+8.2f}({m.sum()//1000}k)".rjust(13))
    out(f"{bnm:>14}" + "".join(cells))
out("\nKEY: read each ROW (fixed baseline) left->right. If dMEAN still grows with asym")
out("within a fixed-baseline row, asymmetry is the real driver (not the baseline confound).")
open("D:/BioCV/BIOCV_DISENTANGLE.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
