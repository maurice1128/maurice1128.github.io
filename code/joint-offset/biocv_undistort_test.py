"""DECISIVE TEST (referee objection M1): is the asymmetry-dependent object-space
advantage an artefact of UNCORRECTED LENS DISTORTION?

BioCV cameras have substantial barrel distortion (k1~-0.15, k2~+0.08): tens of px
at the image periphery, vs an effect size of ~0.05 px (+0.15mm pooled) to ~2 px
(+4.6mm at ratio 3-4). The pipeline so far parsed distortion but projected with a
pure pinhole, so residuals carried the full distortion error. The manuscript claimed
this "biases both metrics equally". The referee argues it does NOT: a near camera
images the subject across a large image excursion (high-distortion periphery) while a
far camera images it near the principal point (low distortion), so neglecting
distortion inflates NEAR-camera residuals preferentially -- and object-space
down-weights near cameras by multiplying by distance. That would manufacture exactly
the reported asymmetry effect.

This script:
 (1) DIAGNOSTIC: measures distortion displacement (px) at the actual detected
     keypoints, and tests whether it correlates with camera-to-joint distance
     (the confound mechanism).
 (2) CORRECTED ANALYSIS: undistorts every detection into the ideal pinhole frame
     (cv2.undistortPoints) and re-runs the full-rig deployable comparison.
 (3) Prints corrected vs uncorrected side by side.
-> D:/BioCV/BIOCV_UNDISTORT.txt
"""
import glob, os, pickle, numpy as np, sys, cv2
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
# The control ran at [pos:AW] only, which left every hip/knee/ankle criterion result
# conditional on an unvalidated distortion model. BIOCV_JOINTSET=HKA runs the same test on the
# joint set the paper's main claims are made on.
_JS = os.environ.get("BIOCV_JOINTSET", "AW").upper()
SEV = ({"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10} if _JS == "AW" else
       {"L-hip": 11, "R-hip": 12, "L-knee": 13, "R-knee": 14, "L-ankle": 15, "R-ankle": 16})
B = 3000; rng = np.random.default_rng(7)

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
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

def undistort_uv(cam, uv):
    """Map a DISTORTED pixel observation to the ideal pinhole frame."""
    pts = np.array(uv, float).reshape(1, 1, 2)
    d = np.array(cam.dist, float).reshape(1, -1)
    out = cv2.undistortPoints(pts, cam.K, d, P=cam.K)
    return out.reshape(2)

lines = []
def out(s): print(s); lines.append(s)

rows_u = []; rows_c = []; subj = []; pid2id = {}
dist_disp = []      # (distortion displacement px, camera-to-joint distance mm, image radius px)
for f in sorted(glob.glob("D:/BioCV/_cache_balanced/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    sid = pid2id.setdefault(D["pid"], len(pid2id))
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for jn, cj in SEV.items():
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs_d = np.array([det[i][cj, :2] for i in vi])                 # as-detected (distorted)
            uvs_u = np.array([undistort_uv(cams[i], det[i][cj, :2]) for i in vi])  # corrected
            w = np.array([det[i][cj, 2] for i in vi])
            dists = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
            asym = dists.max() / dists.min()
            for k, i in enumerate(vi):
                r_img = np.linalg.norm(uvs_d[k] - np.array([cams[i].K[0, 2], cams[i].K[1, 2]]))
                dist_disp.append((np.linalg.norm(uvs_u[k] - uvs_d[k]), dists[k], r_img))
            # uncorrected (as published) and corrected
            Xr_u = iter_rm(cs, uvs_d, w, rep); Xd_u = iter_rm(cs, uvs_d, w, objd)
            Xr_c = iter_rm(cs, uvs_u, w, rep); Xd_c = iter_rm(cs, uvs_u, w, objd)
            rows_u.append((asym, np.linalg.norm(Xr_u - Xg), np.linalg.norm(Xd_u - Xg)))
            rows_c.append((asym, np.linalg.norm(Xr_c - Xg), np.linalg.norm(Xd_c - Xg)))
            subj.append(sid)

rows_u = np.array(rows_u); rows_c = np.array(rows_c); subj = np.array(subj)
dd = np.array(dist_disp)
nsub = len(pid2id)

out("DECISIVE TEST: does uncorrected lens distortion manufacture the asymmetry effect?")
out(f"N={len(rows_u)} joint-observations, {nsub} subjects, joint set [pos:{_JS}]. "
    f"Distortion applied via cv2.undistortPoints.")
out("All intervals below are percentile bootstrap, B=3000, RESAMPLING SUBJECTS (not "
    "observations), so they carry the within-subject clustering.")
out("")
out("--- (1) DIAGNOSTIC: distortion displacement at the actual detections ---")
out(f"distortion displacement (px): mean={dd[:,0].mean():.2f} median={np.median(dd[:,0]):.2f} "
    f"p90={np.percentile(dd[:,0],90):.2f} max={dd[:,0].max():.2f}")
out(f"  (compare: effect sizes are ~0.05 px equivalent for the pooled +0.15mm, ~1.5-2 px for +4.6mm)")
# does distortion displacement correlate with camera distance? (the confound mechanism)
r = np.corrcoef(dd[:,0], dd[:,1])[0,1]
out(f"corr(distortion displacement, camera-to-joint distance) = {r:+.3f}")
q = np.percentile(dd[:,1], [25, 50, 75])
near = dd[dd[:,1] <= q[0]]; far = dd[dd[:,1] >= q[2]]
out(f"  NEAR cameras (bottom quartile dist, {near[:,1].mean():.0f}mm): mean distortion {near[:,0].mean():.2f} px, "
    f"mean image radius {near[:,2].mean():.0f} px")
out(f"  FAR  cameras (top quartile dist, {far[:,1].mean():.0f}mm): mean distortion {far[:,0].mean():.2f} px, "
    f"mean image radius {far[:,2].mean():.0f} px")
out(f"  -> the near-camera mechanism requires NEAR >> FAR distortion. Ratio near/far = {near[:,0].mean()/max(far[:,0].mean(),1e-9):.2f}")
out("")

def table(rows, tag):
    asym, er, ed = rows[:,0], rows[:,1], rows[:,2]
    out(f"--- {tag} ---")
    out(f"{'asym bin':>10}{'n':>8}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'   dMEAN 95%CI':>20}")
    res = {}
    for lo, hi, nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,2.5,'2-2.5'),(2.5,3,'2.5-3'),(3,4,'3-4'),(4,99,'>4')]:
        m = (asym >= lo) & (asym < hi)
        if m.sum() < 30: out(f"{nm:>10}{int(m.sum()):>8}   few"); continue
        er_b, ed_b, sj_b = er[m], ed[m], subj[m]
        sl = np.unique(sj_b); idx = {t: np.where(sj_b == t)[0] for t in sl}
        bs = np.empty(B)
        for b in range(B):
            pick = rng.choice(sl, size=len(sl), replace=True)
            ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er_b[ii] - ed_b[ii]).mean()
        ci = np.percentile(bs, [2.5, 97.5])
        star = "*" if (len(sl) >= 4 and (ci[0] > 0 or ci[1] < 0)) else " "
        out(f"{nm:>10}{int(m.sum()):>8}{er_b.mean():>9.1f}{ed_b.mean():>9.1f}{(er_b-ed_b).mean():>+8.2f}"
            f"{f'[{ci[0]:+.2f},{ci[1]:+.2f}]{star}':>20}")
        res[nm] = ((er_b-ed_b).mean(), ci)
    # pooled
    sl = np.unique(subj); idx = {t: np.where(subj == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = (er[ii] - ed[ii]).mean()
    ci = np.percentile(bs, [2.5, 97.5])
    out(f"POOLED: dMEAN={(er-ed).mean():+.3f} mm, CI [{ci[0]:+.3f},{ci[1]:+.3f}]  "
        f"| mean abs error reproj={er.mean():.1f} objd={ed.mean():.1f} mm")
    out("")
    return res

table(rows_u, "(2a) UNCORRECTED (pinhole projection, distorted detections)")
table(rows_c, "(2b) DISTORTION-CORRECTED (detections undistorted to ideal pinhole)")
out("READ: if the corrected table keeps the asymmetry-dependent advantage, objection M1 dies.")
out("If the advantage collapses or reverses, the published effect was a distortion artefact.")
open(os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_UNDISTORT.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
