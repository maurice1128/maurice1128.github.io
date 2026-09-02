"""
Option 1 deliverable: does object-space removal's advantage grow with the REAL
2D outlier rate of the detector? (Evidence D on real Vicon GT, real detectors —
not synthetic injection.)

For each detector cache (lightweight=RTMPose-s, balanced=RTMPose-m, [performance=
RTMPose-l]), on the SAME 60-frame selection, measures:
  - real 2D outlier rate: fraction of camera-joint detections whose pixel error
    to the projected Vicon GT exceeds OUTLIER_PX (a genuine gross mis-detection)
  - object-space advantage: dMEAN, dP95 (reproj - distance) on severe joints
A rising advantage with rising outlier rate = the claim, on real detectors + GT.
-> D:/BioCV/BIOCV_SWEEP.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K = 3.0; OUTLIER_PX = 25.0
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
MODES = ["lightweight", "balanced", "performance"]

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
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real Vicon GT — object-space advantage vs REAL detector outlier rate "
    f"(outlier = 2D err > {OUTLIER_PX:.0f}px vs projected GT)")
out(f"{'detector':>12}{'N':>7}{'med2Dpx':>9}{'outlier%':>9}{'dMEAN':>8}{'dP95':>8}"
    f"{'usable_re':>10}{'usable_di':>10}")

for mode in MODES:
    files = sorted(glob.glob(f"D:/BioCV/_cache_{mode}/*.pkl"))
    if not files:
        out(f"{mode:>12}   (no cache)"); continue
    px_err = []; er = []; ed = []
    for f in files:
        D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
        for fr in D["frames"]:
            det = fr["det"]; gt = fr["gt"]
            for jn, cj in SEV.items():
                Xg = gt[cj]
                vi = [i for i, dd in enumerate(det)
                      if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
                if len(vi) < MIN_CAM: continue
                cs = [cams[i] for i in vi]
                uvs = np.array([det[i][cj, :2] for i in vi])
                w = np.array([det[i][cj, 2] for i in vi])
                for i, cam in zip(vi, cs):
                    px_err.append(np.linalg.norm(cam.project(Xg) - det[i][cj, :2]))
                Xr = iter_rm(cs, uvs, w, rep); Xd = iter_rm(cs, uvs, w, objd)
                er.append(np.linalg.norm(Xr - Xg)); ed.append(np.linalg.norm(Xd - Xg))
    px_err = np.array(px_err); er = np.array(er); ed = np.array(ed)
    orate = 100 * (px_err > OUTLIER_PX).mean()
    out(f"{mode:>12}{len(er):>7}{np.median(px_err):>9.1f}{orate:>8.1f}%"
        f"{er.mean()-ed.mean():>+8.2f}{np.percentile(er,95)-np.percentile(ed,95):>+8.1f}"
        f"{100*(er<50).mean():>9.0f}%{100*(ed<50).mean():>9.0f}%")

out("Rising dMEAN/dP95 with rising outlier% across detectors = object-space benefit "
    "scales with real detector outlier rate (real GT, real detectors).")
open("D:/BioCV/BIOCV_SWEEP.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
