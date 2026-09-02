"""
Controlled test of the user's intuition: does object-space (distance) outlier
removal's advantage over reprojection GROW with the 2D outlier rate (as in
multi-person / occlusion / weak-detector conditions)?

Uses the CLEAN balanced BioCV cache and injects synthetic gross outliers at rate
p per camera-joint (large pixel displacement = "confident wrong detection", the
real failure mode from HANDOFF lesson 2), keeping confidence unchanged. Then runs
the same iterative same-MAD removal with each metric and measures 3D error vs the
INDEPENDENT Vicon GT. If dMEAN and dP95 rise with p, the "benefit scales with
outlier rate" claim is demonstrated on real GT. -> D:/BioCV/BIOCV_INJECT.txt
"""
import glob, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K = 3.0
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
RATES = [0.0, 0.1, 0.2, 0.3, 0.4]
OUT_PX = 200.0           # gross-outlier displacement magnitude (pixels)
SEED = 2024

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

# preload all valid (cams, uvs, w, Xg) observations from clean balanced cache
obs = []
for f in sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            obs.append(([cams[i] for i in vi],
                        np.array([det[i][cj, :2] for i in vi], float),
                        np.array([det[i][cj, 2] for i in vi], float), Xg))

lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real Vicon GT — controlled outlier injection, N={len(obs)} clean obs, "
    f"gross outlier = +{OUT_PX:.0f}px random displacement, iterative same-MAD removal")
out(f"{'inj rate':>9}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}"
    f"{'P95_re':>8}{'P95_di':>8}{'dP95':>8}{'nrec_re':>9}{'nrec_di':>9}")
for p in RATES:
    rng = np.random.default_rng(SEED)   # same corruption pattern across metrics per rate
    er, ed = [], []
    for cs, uvs, w, Xg in obs:
        m = len(cs)
        corrupt = rng.random(m) < p
        uvc = uvs.copy()
        for i in range(m):
            if corrupt[i]:
                ang = rng.uniform(0, 2 * np.pi)
                uvc[i] = uvs[i] + OUT_PX * np.array([np.cos(ang), np.sin(ang)])
        Xr = iter_rm(cs, uvc, w, rep); Xd = iter_rm(cs, uvc, w, objd)
        er.append(np.linalg.norm(Xr - Xg)); ed.append(np.linalg.norm(Xd - Xg))
    er, ed = np.array(er), np.array(ed)
    out(f"{p:>9.1f}{er.mean():>9.1f}{ed.mean():>9.1f}{er.mean()-ed.mean():>+8.2f}"
        f"{np.percentile(er,95):>8.1f}{np.percentile(ed,95):>8.1f}"
        f"{np.percentile(er,95)-np.percentile(ed,95):>+8.1f}"
        f"{100*(er<50).mean():>8.0f}%{100*(ed<50).mean():>8.0f}%")
out("nrec = % obs reconstructed within 50mm (usable). dMEAN/dP95>0 = distance better.")
open("D:/BioCV/BIOCV_INJECT.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
