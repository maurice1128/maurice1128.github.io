"""Second real dataset + higher asymmetry: CMU Panoptic 171204_pose1 (SINGLE person,
dome rig -> cameras at more varied distances than BioCV ring). Reuses the cached real
RTMPose detections (dets_171204_pose1.npz) and 480-cam GT. Asymmetry-stratified
reproj vs object-space removal on severe joints -> does the growth-with-asymmetry
trend replicate on an independent dataset/geometry? -> D:/BioCV/POSE1_ASYM.txt
"""
import sys, json, numpy as np
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from rowv_panoptic import load_hd_cameras, DATA, CM2MM

MIN_CAM = 4; K = 3.0
C17_P19 = {5:3, 6:9, 7:4, 8:10, 9:5, 10:11, 11:6, 12:12, 13:7, 14:13, 15:8, 16:14}
SEV = {"L-ankle":15, "R-ankle":16, "L-wrist":9, "R-wrist":10}

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
        if mad < 1e-9 or e[worst] <= med + K * mad: break
        idx.pop(worst)
    CS = [cs[i] for i in idx]; return R.triangulate_wdlt(CS, uvs[idx], w[idx])

def load_gt_frame(fid):
    fp = f"{DATA}/hdPose3d_stage1_coco19/body3DScene_{fid:08d}.json"
    d = json.load(open(fp))
    if not d["bodies"]: return None
    return np.array(d["bodies"][0]["joints19"], float).reshape(-1, 4)[:, :3] * CM2MM

d = np.load("D:/ROWV_paper/data/panoptic/dets_171204_pose1.npz", allow_pickle=True)
cam_names = [str(x) for x in d["cams"]]; frames = [int(x) for x in d["frames"]]; det = d["det"]
allc = load_hd_cameras(); cams = [allc[c] for c in cam_names]

rows = []  # (asym, err_re, err_di)
for fi, fid in enumerate(frames):
    gt = load_gt_frame(fid)
    if gt is None: continue
    for jn, cj in SEV.items():
        p19 = C17_P19[cj]; Xg = gt[p19]
        vi = [ci for ci in range(len(cams))
              if not np.isnan(det[ci, fi, cj, 0]) and det[ci, fi, cj, 2] > 0]
        if len(vi) < MIN_CAM: continue
        cs = [cams[ci] for ci in vi]
        uvs = np.array([det[ci, fi, cj, :2] for ci in vi])
        w = np.array([det[ci, fi, cj, 2] for ci in vi])
        dists = [np.linalg.norm(cams[ci].C - Xg) for ci in vi]
        asym = max(dists) / min(dists)
        Xr = iter_rm(cs, uvs, w, rep); Xd = iter_rm(cs, uvs, w, objd)
        rows.append((asym, np.linalg.norm(Xr - Xg), np.linalg.norm(Xd - Xg)))
rows = np.array(rows); a, er, ed = rows[:,0], rows[:,1], rows[:,2]
lines = []
def out(s): print(s); lines.append(s)
out(f"Panoptic pose1 (single person, dome), {len(cam_names)} cams, N={len(rows)} joint-obs vs 480-cam GT")
out(f"asym median={np.median(a):.2f} p90={np.percentile(a,90):.2f} max={a.max():.2f} "
    f"(BioCV capped ~3.8; dome should reach higher)")
out(f"{'asym bin':>10}{'n':>7}{'mean_re':>9}{'mean_di':>9}{'dMEAN':>8}{'dP95':>8}")
for lo,hi,nm in [(1,1.5,'<1.5'),(1.5,2,'1.5-2'),(2,3,'2-3'),(3,4,'3-4'),(4,6,'4-6'),(6,99,'>6')]:
    m = (a>=lo)&(a<hi)
    if m.sum()<15: out(f"{nm:>10}{int(m.sum()):>7}   few"); continue
    r,dd = er[m],ed[m]
    out(f"{nm:>10}{int(m.sum()):>7}{r.mean():>9.1f}{dd.mean():>9.1f}{r.mean()-dd.mean():>+8.2f}"
        f"{np.percentile(r,95)-np.percentile(dd,95):>+8.1f}")
out("Replication check: does dMEAN grow with asymmetry here too (independent dataset+geometry)?")
open("D:/BioCV/POSE1_ASYM.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
