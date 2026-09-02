"""UNCERTAINTY-BUDGET framing (Measurement path, action B).

Turns the catch-rate mechanism into a measurement-uncertainty statement that a
Measurement referee understands: given a realistic gross-outlier rate p per camera,
how much RESIDUAL 3D position uncertainty (RMS, mm) does each rejection metric leave
UNremoved, as a function of camera-distance asymmetry?

Physical, realizable regime only (real BioCV P06 geometry, asymmetry manufactured by
radial camera moves but capped where cameras still detect the joint, realA<=~5).
Base detection noise 4 px; gross outlier 60 px (a limb/person mis-association);
outlier present independently on each camera with prob p. This is an honest
uncertainty budget, NOT the retracted per-frame-guaranteed-outlier magnitudes.
-> D:/BioCV/BIOCV_UNCERTAINTY.txt
"""
import glob, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K = 3.0
NOISE = 4.0; OUTLIER = 60.0; TR = 4000
rng = np.random.default_rng(3)

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C; return np.linalg.norm(w - np.dot(w, dv) * dv)
def iter_rm(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]; X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

cams0, _ = load_biocv_cameras("D:/BioCV/_calib/P06")
f0 = sorted(glob.glob("D:/BioCV/_cache_balanced/P06_*.pkl"))[0]
D = pickle.load(open(f0, "rb")); Xg = None
for fr in D["frames"]:
    if np.any(fr["gt"][15]): Xg = fr["gt"][15].copy(); break
def repoint(Kmat, C, T):
    fdir = (T - C); fdir /= np.linalg.norm(fdir)
    a = np.array([0,0,1.0]) if abs(fdir[2]) < 0.95 else np.array([0,1.0,0])
    r = np.cross(a, fdir); r /= np.linalg.norm(r); u = np.cross(fdir, r)
    return R.Camera(Kmat, np.vstack([r, u, fdir]), C)
def build(A):
    out = []
    for i, c in enumerate(cams0):
        v = c.C - Xg; rr = np.linalg.norm(v); u = v / rr
        out.append(repoint(c.K, Xg + u * (rr * A if i % 2 == 0 else rr), Xg))
    return out

lines = []
def out(s): print(s); lines.append(s)
out("BioCV P06 geometry -- MEASUREMENT UNCERTAINTY BUDGET of the outlier-rejection metric.")
out(f"Residual RMS 3D position uncertainty (mm) left UNremoved, vs camera-distance asymmetry (realA),")
out(f"at gross-outlier rate p per camera (noise={NOISE}px, outlier={OUTLIER}px, {TR} trials/cell).")
out(f"'penalty' = reproj RMS - objd RMS = the extra measurement uncertainty from using reprojection.")
out(f"Realizable range only (realA<=~5; beyond, far cameras cannot detect the joint -> not reported).")
out("")
for p in [0.0, 0.02, 0.05, 0.10]:
    tag = " (pure noise, NO outliers -> scale-weighting/conditioning component only)" if p == 0 else ""
    out(f"--- gross-outlier rate p = {p:.0%} per camera{tag} ---")
    out(f"{'realA':>7}{'reproj RMS':>12}{'objd RMS':>12}{'penalty':>10}")
    for A in [1.0, 1.15, 1.3, 1.5]:                 # realA 3.15 -> ~4.7 (realizable)
        cams = build(A); dists = np.array([np.linalg.norm(c.C - Xg) for c in cams])
        realA = dists.max() / dists.min()
        proj0 = [c.project(Xg) for c in cams]
        er2 = ed2 = 0.0
        for _ in range(TR):
            uvs = np.array([p0 + rng.normal(0, NOISE, 2) for p0 in proj0])
            for i in range(len(cams)):
                if rng.random() < p:
                    ang = rng.uniform(0, 2*np.pi)
                    uvs[i] += OUTLIER * np.array([np.cos(ang), np.sin(ang)])
            Xr = iter_rm(cams, uvs, np.ones(len(cams)), rep)
            Xd = iter_rm(cams, uvs, np.ones(len(cams)), objd)
            er2 += np.sum((Xr - Xg)**2); ed2 += np.sum((Xd - Xg)**2)
        rre = np.sqrt(er2 / TR); rdi = np.sqrt(ed2 / TR)
        out(f"{realA:>7.2f}{rre:>12.2f}{rdi:>12.2f}{rre-rdi:>+10.2f}")
    out("")
out("READ: object-space keeps residual uncertainty ~flat; reprojection's grows with asymmetry because")
out("its far-camera catch rate falls. In the realizable range the penalty is small (sub-mm to few-mm) at")
out("realistic p; it is the SLOPE (penalty rising with asymmetry), not the magnitude, that is the result.")
open("D:/BioCV/BIOCV_UNCERTAINTY.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
