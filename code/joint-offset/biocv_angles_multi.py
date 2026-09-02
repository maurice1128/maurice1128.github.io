"""ANGLE COVERAGE beyond sagittal knee -- watchdog Cycle 3h, ordered BEFORE the restructure.

Rationale (watchdog): "You do not write a thesis and then run the experiment most likely to
falsify it." The hostile referee identified FRONTAL-PLANE knee as the place a triangulation
change has its best remaining chance of mattering, and J Biomech will not accept a kinematic
claim resting on one angle in one plane.

Outcomes computed:
  knee_flex   sagittal knee flexion, angle(hip, knee, ankle)          [replicates Table 4]
  knee_abd    FRONTAL-PLANE knee angle -- thigh and shank projected onto the pelvis frontal
              plane (medio-lateral axis = hip-to-hip, vertical = world up, orthogonalised)
  hip_flex    angle(mid-shoulder, hip, knee) -- trunk-referenced hip flexion

NOT COMPUTABLE and stated as such: ankle dorsiflexion. COCO-17 provides no foot/toe keypoint,
so the shank-foot chain does not exist in this data. Reported as a limitation, not silently
dropped.

Same design as biocv_angles.py: one shared CANDIDATE camera set per observation; each arm
then runs its own rejection loop, so only the rejection/weighting choice differs.
-> D:/BioCV/BIOCV_ANGLES_MULTI.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_ANGLES_MULTI.txt")
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_angmulti_progress.txt"
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}   # shoulder, hip, knee, ankle

def ang3(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def frontal_knee(hip, knee, ankle, ml):
    """Angle between thigh and shank after projecting both onto the frontal plane.
    ml = medio-lateral unit axis (hip-to-hip). Frontal plane spans ml and vertical."""
    up = np.array([0.0, 0.0, 1.0])
    up = up - np.dot(up, ml) * ml
    n = np.linalg.norm(up)
    if n < 1e-6: return np.nan
    up = up / n
    def proj(v): return np.array([np.dot(v, ml), np.dot(v, up)])
    t = proj(hip - knee); s = proj(ankle - knee)
    nt = np.linalg.norm(t); ns = np.linalg.norm(s)
    if nt < 1e-6 or ns < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(t @ s / (nt * ns), -1, 1)))

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def solve(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is not None:
        while len(idx) > MIN_CAM:
            CS = [cs[i] for i in idx]
            X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
            e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
            med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
            worst = int(np.argmax(e))
            if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
            idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

ARMS = ["noRej_conf", "noRej_wd", "rep_conf", "objd_conf", "rep_wd", "objd_wd"]
OUTC = ["knee_flex", "knee_abd", "hip_flex"]
rows = {o: [] for o in OUTC}; subj = {o: [] for o in OUTC}; pid2id = {}
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid)
    sid = pid2id.setdefault(pid, len(pid2id)); nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s n={len(rows['knee_flex'])}\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        if not all(j in gt and np.any(gt[j]) for j in (5, 6, 11, 12)): continue
        ml = gt[12] - gt[11]; nml = np.linalg.norm(ml)
        if nml < 1e-6: continue
        ml = ml / nml
        msh_gt = 0.5 * (gt[5] + gt[6])
        for side, (jsh, jh, jk, ja) in SIDES.items():
            need = (jsh, jh, jk, ja, 5, 6, 11, 12)
            if not all(j in gt and np.any(gt[j]) for j in need): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in need)]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            per_arm = {}
            for a in ARMS:
                metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                use_wd = a.endswith("_wd")
                X = {}
                for j in set(need):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    if use_wd:
                        dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                        w = conf / dj
                    else:
                        w = conf
                    X[j] = solve(cs, uvs, w, metric)
                mlx = X[12] - X[11]; nm = np.linalg.norm(mlx)
                mlx = mlx / nm if nm > 1e-6 else ml
                per_arm[a] = {
                    "knee_flex": ang3(X[jh], X[jk], X[ja]),
                    "knee_abd":  frontal_knee(X[jh], X[jk], X[ja], mlx),
                    "hip_flex":  ang3(0.5 * (X[5] + X[6]), X[jh], X[jk]),
                }
            truth = {
                "knee_flex": ang3(gt[jh], gt[jk], gt[ja]),
                "knee_abd":  frontal_knee(gt[jh], gt[jk], gt[ja], ml),
                "hip_flex":  ang3(msh_gt, gt[jh], gt[jk]),
            }
            for o in OUTC:
                g = truth[o]
                vals = [per_arm[a][o] for a in ARMS]
                if not np.isfinite(g) or not all(np.isfinite(v) for v in vals): continue
                rows[o].append([abs(v - g) for v in vals]); subj[o].append(sid)

lines = []
def out(s): print(s); lines.append(s)
out("ANGLE COVERAGE: sagittal knee, FRONTAL-PLANE knee, trunk-referenced hip flexion")
out(f"Cache={CACHE}, {len(pid2id)} subjects. Shared candidate camera set per observation.")
out("ANKLE DORSIFLEXION IS NOT COMPUTABLE: COCO-17 has no foot/toe keypoint, so the")
out("shank-foot chain does not exist in this dataset. Stated, not silently omitted.")
out("")
def cif(diff, sj):
    sl = np.unique(sj); idx = {t: np.where(sj == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = diff[ii].mean()
    return diff.mean(), np.percentile(bs, [2.5, 97.5])
for o in OUTC:
    A = np.array(rows[o]); sj = np.array(subj[o])
    if len(A) < 50: out(f"=== {o}: too few observations ({len(A)}) ==="); continue
    out(f"=== {o} | N={len(A)} ===")
    out(f"{'arm':>12}{'mean |err| deg':>16}")
    for k, a in enumerate(ARMS): out(f"{a:>12}{A[:,k].mean():>16.3f}")
    out("  contrasts (positive = SECOND arm better):")
    for i, j, lab in [(2, 0, "reproj rejection vs NO rejection"),
                      (3, 0, "object-space rejection vs NO rejection"),
                      (2, 3, "object-space vs reprojection criterion"),
                      (0, 1, "1/d weighting, no rejection"),
                      (4, 1, "under best weighting: is rejection still harmful?")]:
        mu, c = cif(A[:, i] - A[:, j], sj)
        star = "*" if (c[0] > 0 or c[1] < 0) else " "
        out(f"    {lab:<48}{mu:+.3f} [{c[0]:+.3f},{c[1]:+.3f}]{star}")
    out("")
out("READ: frontal-plane knee is where a triangulation change has its best remaining chance")
out("of mattering. If effects there are also ~0.1-0.2 deg, the thesis survives its hardest test.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
