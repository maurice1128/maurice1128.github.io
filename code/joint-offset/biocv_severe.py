"""
STEP 2: the decisive real-GT test. Reads biocv_detect.py's cache and, on BioCV's
independent Vicon ground truth, runs the SAME analysis as AIST_SEVERE.txt:
  severe peripheral joints (ankles + wrists), 3D POSITION error (mm),
  iterative same-MAD removal, reproj-metric vs distance(object-space)-metric,
  stratified by camera-distance asymmetry, reporting MEAN and P95 (worst frames).

If distance beats reproj and the gap grows with asymmetry HERE (real Vicon GT),
the asymmetry finding escapes the "AIST++ pseudo-GT is circular" objection and
the Measurement submission stands. Result -> D:/BioCV/BIOCV_SEVERE.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MODE = os.environ.get("BIOCV_MODE", "balanced")
OUT = f"D:/BioCV/BIOCV_SEVERE_{MODE}.txt"
MIN_CAM = 4
K = 3.0
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def iter_rm(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]; UU = uvs[idx]; WW = w[idx]
        X = R.triangulate_wdlt(CS, UU, WW)
        e = np.array([metric(CS[i], X, UU[i]) for i in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]
    return R.triangulate_wdlt(CS, uvs[idx], w[idx])

# camera objects per pid (indexed 0..n matching the cached detection order)
CAMS = {}
def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

rows = []   # (asym, joint_name, err_reproj_mm, err_dist_mm)
trial_ids = []; joints = []
files = sorted(glob.glob(f"D:/BioCV/_cache_{MODE}/*.pkl"))
for ti, f in enumerate(files):
    D = pickle.load(open(f, "rb"))
    cams = cams_for(D["pid"])
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM:
                continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            w = np.array([det[i][cj, 2] for i in vi])
            dists = [np.linalg.norm(cams[i].C - Xg) for i in vi]
            asym = max(dists) / min(dists)
            Xr = iter_rm(cs, uvs, w, rep)
            Xd = iter_rm(cs, uvs, w, objd)
            rows.append((asym, jn, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg)))
            trial_ids.append(ti); joints.append(jn)

joints = np.array(joints)
trial_ids = np.array(trial_ids)
rows = np.array([(a, er, ed) for a, _, er, ed in rows])
if len(rows):
    np.save(f"D:/BioCV/biocv_rows_{MODE}.npy", rows)
    np.save(f"D:/BioCV/biocv_joints_{MODE}.npy", joints)
    np.save(f"D:/BioCV/biocv_trials_{MODE}.npy", trial_ids)
lines = []
def out(s): print(s); lines.append(s)
if len(rows) == 0:
    out("no rows (cache empty?)")
else:
    out(f"BioCV real Vicon GT — severe joints (ankle/wrist) N={len(rows)} joint-obs; "
        f"asym median={np.median(rows[:,0]):.2f} p90={np.percentile(rows[:,0],90):.2f} "
        f"max={rows[:,0].max():.2f}")
    out("3D POSITION error (mm), reproj vs distance, by asymmetry — MEAN and P95:")
    out(f"{'asym bin':>10}{'n':>8}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>7}"
        f"{'P95_re':>9}{'P95_di':>9}{'dP95':>8}")
    for lo, hi, nm in [(1,1.3,'<1.3'),(1.3,1.6,'1.3-1.6'),(1.6,2,'1.6-2'),
                       (2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,99,'>3')]:
        m = (rows[:,0] >= lo) & (rows[:,0] < hi)
        if m.sum() < 10:
            out(f"{nm:>10}{int(m.sum()):>8}  few"); continue
        pr, pd = rows[m,1], rows[m,2]
        out(f"{nm:>10}{int(m.sum()):>8}{pr.mean():>9.1f}{pd.mean():>9.1f}"
            f"{pr.mean()-pd.mean():>+7.1f}{np.percentile(pr,95):>9.1f}"
            f"{np.percentile(pd,95):>9.1f}{np.percentile(pr,95)-np.percentile(pd,95):>+8.1f}")
    out("Positive dMEAN/dP95 = distance better (mm). Compare shape to AIST_SEVERE.txt.")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
