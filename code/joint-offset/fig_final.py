"""Honest main figure (post-verification). Panel A: real BioCV Vicon-GT effect
(true magnitude, natural outliers). Panel B: the MECHANISM at REALISTIC asymmetry
(realA up to ~6) — reproj's catch rate of a far-camera outlier collapses while
object-space stays high. Magnitude numbers from the sim are NOT shown (non-physical
beyond realA~6); only the catch-rate mechanism, which the verification confirmed robust."""
import glob, pickle, numpy as np, sys, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

# ---- Panel A data: real BioCV clustered (BIOCV_CLUSTERED.txt), FINAL 11 subjects ----
# bins <1.5 / 1.5-2 / 2-3 / 3-4 -> centers; dMEAN + subject-cluster 95% CI.
# Shows the SIGN-CROSSOVER: trivially sig-negative below ratio 2, null at 2-3, sig-positive at 3-4.
b_as = [1.25, 1.75, 2.5, 3.5]
b_dm = [-0.10, -0.27, 0.08, 3.74]
b_lo = [-0.17, -0.45, -0.20, 2.14]; b_hi = [-0.03, -0.11, 0.34, 6.30]

# ---- Panel B: mechanism catch-rate vs asymmetry at REALISTIC geometry ----
cams0, _ = load_biocv_cameras("D:/BioCV/_calib/P06")
# Use a P06 cache file for the joint position so cameras+joint are the SAME subject
# (matches the documented mechanism curve 100/100/98/84/62/29 at realA 3.15->6.30).
f0 = sorted(glob.glob("D:/BioCV/_cache_balanced/P06_*.pkl"))[0]
D = pickle.load(open(f0, "rb")); Xg = None
for fr in D["frames"]:
    if np.any(fr["gt"][15]): Xg = fr["gt"][15].copy(); break
def repoint(Kmat, C, T):
    f = (T - C); f /= np.linalg.norm(f)
    a = np.array([0,0,1.0]) if abs(f[2]) < 0.95 else np.array([0,1.0,0])
    r = np.cross(a, f); r /= np.linalg.norm(r); u = np.cross(f, r)
    return R.Camera(Kmat, np.vstack([r, u, f]), C)
def build(A):
    out = []
    for i, c in enumerate(cams0):
        v = c.C - Xg; rr = np.linalg.norm(v); u = v / rr
        out.append(repoint(c.K, Xg + u * (rr * A if i % 2 == 0 else rr), Xg))
    return out
def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C; return np.linalg.norm(w - np.dot(w, dv) * dv)
rng = np.random.default_rng(1); TR = 3000
realA, cr_re, cr_di = [], [], []
for A in [1.0, 1.15, 1.3, 1.5, 1.7, 2.0]:
    cams = build(A); dists = np.array([np.linalg.norm(c.C - Xg) for c in cams])
    if dists.max()/dists.min() > 6.5: continue          # keep realistic (realA<=~6)
    realA.append(dists.max()/dists.min())
    far = int(np.argmax(dists)); proj0 = [c.project(Xg) for c in cams]
    hit_re = hit_di = 0
    for _ in range(TR):
        uvs = np.array([p + rng.normal(0, 4, 2) for p in proj0])
        ang = rng.uniform(0, 2*np.pi); uvs[far] += 80*np.array([np.cos(ang), np.sin(ang)])
        Xn = R.triangulate_wdlt(cams, uvs, np.ones(len(cams)))
        er = np.array([rep(cams[i], Xn, uvs[i]) for i in range(len(cams))])
        ed = np.array([objd(cams[i], Xn, uvs[i]) for i in range(len(cams))])
        hit_re += int(np.argmax(er) == far); hit_di += int(np.argmax(ed) == far)
    cr_re.append(100*hit_re/TR); cr_di.append(100*hit_di/TR)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.errorbar(b_as, b_dm, yerr=[np.array(b_dm)-b_lo, np.array(b_hi)-np.array(b_dm)],
            fmt='o-', color='#2a7', capsize=4)
a1.axhline(0, color='k', lw=.6)
a1.set_xlabel('camera-distance asymmetry (max/min)')
a1.set_ylabel('object-space accuracy advantage  (mm)')
a1.set_title('(A) Real BioCV Vicon-GT (11 subj): small (~mm) significant\nsign-crossover — neg below ratio 2, +3.7mm at 3-4')
a1.grid(alpha=.3)
a2.plot(realA, cr_re, 'o-', color='#c44', label='reprojection (px)')
a2.plot(realA, cr_di, 's-', color='#37a', label='object-space (mm)')
a2.set_xlabel('camera-distance asymmetry (max/min)')
a2.set_ylabel('far-camera outlier caught (%)')
a2.set_title('(B) Mechanism: reprojection fails to catch\nfar-camera outliers as asymmetry grows')
a2.set_ylim(0, 105); a2.grid(alpha=.3); a2.legend()
fig.suptitle('Object-space outlier removal: a real, small, asymmetry-dependent sign-crossover (+ robust catch-rate mechanism)', y=1.02)
fig.tight_layout(); fig.savefig("D:/BioCV/fig_final.png", dpi=140, bbox_inches='tight')
print("saved D:/BioCV/fig_final.png")
print("realA:", [round(x,2) for x in realA])
print("catch reproj:", [round(x) for x in cr_re]); print("catch distance:", [round(x) for x in cr_di])
