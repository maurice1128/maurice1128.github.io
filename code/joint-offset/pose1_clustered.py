"""Second real dataset replication: does the distance-error advantage grow with
camera-distance asymmetry on Panoptic pose1 (single person, DOME geometry — different
from BioCV's ring), independent 480-cam GT? Same clustered-subset method as BioCV.
Reads the pose1 detection cache; associates the single GT body per camera; enumerates
6-cam subsets to sweep asymmetry; reproj vs object-space removal; frame-cluster CIs.
-> D:/BioCV/POSE1_CLUSTERED.txt
"""
import os
os.environ["HAG_SEQ"] = "171204_pose1"
import sys, pickle, itertools, numpy as np
sys.path.insert(0, "D:/ROWV_paper")
import panoptic_multi as PM

SUBSET = 6; MIN_CAM = PM.MIN_CAM; CM2MM = PM.CM2MM
SEV = PM.SEV; C17_P19 = PM.C17_P19
cams = PM.load_cameras()
D = pickle.load(open(PM.CACHE, "rb")); sel = D["sel"]; frames = D["frames"]; raw = D["raw"]
B = 3000; rng = np.random.default_rng(7)

rows = []  # (asym, err_re, err_di, frame_idx)
for fk, fid in enumerate(frames):
    gts = PM.load_gt(fid)
    if not gts: continue
    gt19 = gts[0]
    assoc = {}
    for n in sel:
        if fid not in raw[n]: continue
        a = PM.associate(*raw[n][fid], gt19, cams[n])
        if a is not None: assoc[n] = a
    for jn, cj in SEV.items():
        p19 = C17_P19[cj]
        if gt19[p19, 3] <= 0.1: continue
        Xg = gt19[p19, :3] * CM2MM
        names = [n for n in assoc if np.isfinite(assoc[n][cj, 0]) and assoc[n][cj, 2] > 0]
        if len(names) < SUBSET: continue
        for sub in itertools.combinations(names, SUBSET):
            cs = [cams[n] for n in sub]
            uvs = np.array([assoc[n][cj, :2] for n in sub])
            w = np.array([assoc[n][cj, 2] for n in sub])
            dists = [np.linalg.norm(cams[n].C - Xg) for n in sub]
            asym = max(dists) / min(dists)
            Xr = PM.iter_rm(cs, uvs, w, PM.rep); Xd = PM.iter_rm(cs, uvs, w, PM.objd)
            rows.append((asym, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg), fk))
rows = np.array(rows)
if len(rows) == 0:
    open("D:/BioCV/POSE1_CLUSTERED.txt", "w").write("no rows (cache empty / assoc failed)\n")
    print("no rows"); sys.exit()
asym, er, ed, fr = rows[:,0], rows[:,1], rows[:,2], rows[:,3].astype(int)
lines = []
def out(s): print(s); lines.append(s)
out(f"Panoptic pose1 (single, dome), clustered {SUBSET}-cam subsets, N={len(rows)}, "
    f"asym median={np.median(asym):.2f} p90={np.percentile(asym,90):.2f} max={asym.max():.2f}")
out("d = err_reproj - err_dist (mm); + = distance better. Frame-cluster bootstrap 95% CI.")
out(f"{'asym bin':>10}{'n':>8}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'   dMEAN 95%CI':>18}")
for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]:
    m = (asym >= lo) & (asym < hi)
    if m.sum() < 30: out(f"{nm:>10}{int(m.sum()):>8}   few"); continue
    er_b, ed_b, fr_b = er[m], ed[m], fr[m]; d = er_b - ed_b
    fl = np.unique(fr_b); idx = {t: np.where(fr_b == t)[0] for t in fl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(fl, size=len(fl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
    ci = np.percentile(bs, [2.5, 97.5]); star = "*" if (ci[0] > 0 or ci[1] < 0) else " "
    out(f"{nm:>10}{int(m.sum()):>8}{er_b.mean():>9.1f}{ed_b.mean():>9.1f}{d.mean():>+8.2f}"
        f"{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>18}")
out("REPLICATION iff dMEAN grows with asymmetry AND high-asym CIs exclude 0 (as in BioCV).")
open("D:/BioCV/POSE1_CLUSTERED.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
