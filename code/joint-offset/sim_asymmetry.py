"""Controlled-geometry experiment isolating the ASYMMETRY effect from the
narrow-baseline confound. Cameras sit at FIXED azimuths (constant angular baseline
= constant triangulation conditioning) but VARYING radial distance, so camera-
distance asymmetry A = max_dist/min_dist is swept independently of baseline.

Realistic Gaussian pixel noise on all cameras + one gross outlier on a random
camera. Iterative same-MAD removal, reproj vs object-space metric, weighted DLT.
Reports 3D error and the distance-advantage vs asymmetry (sweepable to any A).
-> D:/BioCV/SIM_ASYM.txt
"""
import numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R

F = 1200.0; CX = CY = 600.0
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.0]])
# 8 cameras SURROUNDING the point (full 360 azimuth + varied elevation) so the
# triangulation is well-conditioned (~cm errors like a real ring/dome); asymmetry
# is swept via radial distance only, azimuth/elevation FIXED (constant baseline).
AZ = np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315])
EL = np.deg2rad([15, 40, 25, 45, 20, 38, 22, 42])
NOISE_PX = 3.0; OUTLIER_PX = 60.0; MIN_CAM = 4; Kmad = 3.0
rng = np.random.default_rng(20260719)

def look_at(C, T=np.zeros(3)):
    f = (T - C); f /= np.linalg.norm(f)
    r = np.cross([0, 0, 1.0], f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    Rm = np.vstack([r, u, f])                    # world->cam rows
    return R.Camera(K, Rm, C)

def build_cams(A, base=3000.0):
    """8 surrounding cams; alternating near (base) / far (A*base) -> asym = A."""
    radii = [base if i % 2 == 0 else A * base for i in range(len(AZ))]
    cams = []
    for az, el, rad in zip(AZ, EL, radii):
        C = np.array([rad * np.cos(el) * np.cos(az),
                      rad * np.cos(el) * np.sin(az),
                      rad * np.sin(el)])
        cams.append(look_at(C))
    return cams

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
Xtrue = np.zeros(3)
lines = []
def out(s): print(s); lines.append(s)
out(f"Controlled geometry: 6 cams fixed azimuths (constant baseline), asym swept via "
    f"radial distance only. noise={NOISE_PX}px, 1 gross outlier={OUTLIER_PX}px, {TRIALS} trials/level.")
out(f"{'asym':>6}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'  dMEAN 95%CI':>18}{'dP95':>8}")
for A in [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0]:
    cams = build_cams(A)
    proj0 = [c.project(Xtrue) for c in cams]
    er = np.empty(TRIALS); ed = np.empty(TRIALS)
    for t in range(TRIALS):
        uvs = np.array([p + rng.normal(0, NOISE_PX, 2) for p in proj0])
        oc = rng.integers(0, len(cams))          # random outlier camera
        ang = rng.uniform(0, 2 * np.pi)
        uvs[oc] += OUTLIER_PX * np.array([np.cos(ang), np.sin(ang)])
        w = np.ones(len(cams))
        Xr = iter_rm(cams, uvs, w, rep); Xd = iter_rm(cams, uvs, w, objd)
        er[t] = np.linalg.norm(Xr - Xtrue); ed[t] = np.linalg.norm(Xd - Xtrue)
    d = er - ed
    bs = np.array([ (d[rng.integers(0, TRIALS, TRIALS)]).mean() for _ in range(2000) ])
    ci = np.percentile(bs, [2.5, 97.5]); star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
    out(f"{A:>6.1f}{er.mean():>9.1f}{ed.mean():>9.1f}{d.mean():>+8.2f}"
        f"{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>18}"
        f"{np.percentile(er,95)-np.percentile(ed,95):>+8.1f}")
out("Baseline (angular spread) is CONSTANT across rows; only camera-distance asymmetry changes.")
out("If dMEAN grows with asym here, the asymmetry effect is real and isolated from baseline.")
open("D:/BioCV/SIM_ASYM.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
