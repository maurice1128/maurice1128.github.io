"""Reach asymmetry BEYOND BioCV's natural ~3.8 cap while keeping realistic
conditioning: take BioCV's REAL, well-conditioned 9-camera calibration (verified
~cm accuracy), and manufacture higher asymmetry by moving a subset of cameras
RADIALLY outward from the target joint (re-pointed at it) — angular positions
(baseline) preserved, only distances change. Project a real joint + realistic
pixel noise + one gross outlier on a random camera; iterative same-MAD removal,
reproj vs object-space. Sweep asymmetry 1..10. -> D:/BioCV/BIOCV_SIM.txt
First row A=1.0 validates conditioning (~cm expected)."""
import glob, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

NOISE_PX = 4.0; OUTLIER_PX = 80.0; MIN_CAM = 4; Kmad = 3.0
rng = np.random.default_rng(20260719)

cams0, _ = load_biocv_cameras("D:/BioCV/_calib/P06")
# a real ankle position from the balanced cache (mm, mocap frame)
f0 = sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl"))[0]
D = pickle.load(open(f0, "rb")); Xg = None
for fr in D["frames"]:
    if np.any(fr["gt"][15]): Xg = fr["gt"][15].copy(); break
print("target joint (mm):", np.round(Xg))

def repoint(Kmat, C, T):
    f = (T - C); f /= np.linalg.norm(f)
    a = np.array([0, 0, 1.0]) if abs(f[2]) < 0.95 else np.array([0, 1.0, 0])
    r = np.cross(a, f); r /= np.linalg.norm(r); u = np.cross(f, r)
    return R.Camera(Kmat, np.vstack([r, u, f]), C)

def build(A):
    """Move even-indexed cams to distance A*base along their real bearing -> asym~A."""
    out = []
    for i, c in enumerate(cams0):
        dirv = c.C - Xg; r = np.linalg.norm(dirv); u = dirv / r
        newr = r * A if i % 2 == 0 else r
        out.append(repoint(c.K, Xg + u * newr, Xg))
    return out

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
        if mad < 1e-9 or e[worst] <= med + Kmad * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

TRIALS = 4000
lines = []
def out(s): print(s); lines.append(s)
out(f"BioCV real-calib base, asymmetry manufactured by radial camera moves. "
    f"noise={NOISE_PX}px, outlier={OUTLIER_PX}px, {TRIALS} trials/level.")
out(f"{'asym':>6}{'realA':>7}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'  dMEAN 95%CI':>18}")
for A in [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0]:
    cams = build(A)
    dists = [np.linalg.norm(c.C - Xg) for c in cams]
    realA = max(dists) / min(dists)
    proj0 = [c.project(Xg) for c in cams]
    er = np.empty(TRIALS); ed = np.empty(TRIALS)
    for t in range(TRIALS):
        uvs = np.array([p + rng.normal(0, NOISE_PX, 2) for p in proj0])
        oc = rng.integers(0, len(cams)); ang = rng.uniform(0, 2*np.pi)
        uvs[oc] += OUTLIER_PX * np.array([np.cos(ang), np.sin(ang)])
        w = np.ones(len(cams))
        er[t] = np.linalg.norm(iter_rm(cams, uvs, w, rep) - Xg)
        ed[t] = np.linalg.norm(iter_rm(cams, uvs, w, objd) - Xg)
    d = er - ed
    bs = np.array([d[rng.integers(0, TRIALS, TRIALS)].mean() for _ in range(2000)])
    ci = np.percentile(bs, [2.5, 97.5]); star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
    out(f"{A:>6.1f}{realA:>7.2f}{er.mean():>9.1f}{ed.mean():>9.1f}{d.mean():>+8.2f}"
        f"{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>18}")
out("A=1.0 row = conditioning check (want ~cm). If dMEAN grows with asym and CIs exclude 0,")
out("the asymmetry benefit is confirmed at HIGH asymmetry on realistic geometry.")
open("D:/BioCV/BIOCV_SIM.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
