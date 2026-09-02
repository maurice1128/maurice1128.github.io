"""MECHANISM TEST: why does improving 3D position make joint ANGLES worse?

The offset finding (X22b: ~45-50% of knee-angle MSE is a fixed joint-centre offset)
explains why triangulation gains are SMALL. It cannot explain why they are NEGATIVE --
a fixed offset does not grow when you change the rejection criterion.

LEADING HYPOTHESIS (untested until now): COMMON-MODE CANCELLATION IS DESTROYED.
A joint angle is determined by three joint centres. If their error vectors are CORRELATED
(all displaced the same way, e.g. because they share the same cameras), much of the error
cancels in the angle. Rejection runs INDEPENDENTLY PER JOINT -- each joint has its own
camera-distance profile, so object-space rejection discards a different camera set for the
hip, the knee and the ankle. That decorrelates the three error vectors: each joint gets
individually more accurate while the angle gets worse.

PREDICTIONS, all falsifiable here:
 P1  Correlation between the three joints' error vectors FALLS as more cameras are dropped.
 P2  Object-space rejection decorrelates MORE than reprojection at matched retention
     (it is the arm that is better in position and worse in knee angle).
 P3  The mean pairwise camera-set overlap between the three joints falls with k, and is
     lower for object-space than for reprojection at the same k.

If P1-P3 hold, the mechanism is established. If they fail, the hypothesis is wrong and the
paper must say the harm is unexplained rather than invent a story for it.
-> D:/BioCV/BIOCV_DECORR.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_DECORR.txt")
SIDES = {"L": (11, 13, 15), "R": (12, 14, 16)}      # hip, knee, ankle
KS = [0, 1, 2, 3]
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_decorr_progress.txt"

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def drop_k_idx(cs, uvs, w, metric, k):
    """Return (X, kept_index_set) after dropping exactly k cameras worst-first."""
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM: break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx]), set(idx)

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

# per (criterion, k): lists of pairwise error-vector cosines, camera overlaps, |err|
data = {(c, k): {"cos": [], "ov": [], "mag": []} for c in ("re", "ob") for k in KS}
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        for side, (jh, jk, ja) in SIDES.items():
            js = (jh, jk, ja)
            if not all(j in gt and np.any(gt[j]) for j in js): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in js)]
            if len(vi) < MIN_CAM + max(KS): continue
            cs = [cams[i] for i in vi]
            for cname, metric in (("re", rep), ("ob", objd)):
                for k in KS:
                    errs = {}; keep = {}
                    for j in js:
                        uvs = np.array([det[i][j, :2] for i in vi])
                        w = np.array([det[i][j, 2] for i in vi])
                        X, kept = drop_k_idx(cs, uvs, w, metric, k)
                        errs[j] = X - gt[j]; keep[j] = kept
                    # P1/P2: mean pairwise cosine between the three error vectors
                    cosines = []
                    for a in range(3):
                        for b in range(a + 1, 3):
                            u = errs[js[a]]; v = errs[js[b]]
                            nu = np.linalg.norm(u); nv = np.linalg.norm(v)
                            if nu > 1e-9 and nv > 1e-9: cosines.append(u @ v / (nu * nv))
                    # P3: mean pairwise Jaccard overlap of retained camera sets
                    ovs = []
                    for a in range(3):
                        for b in range(a + 1, 3):
                            A, Bs = keep[js[a]], keep[js[b]]
                            ovs.append(len(A & Bs) / max(len(A | Bs), 1))
                    if cosines:
                        data[(cname, k)]["cos"].append(np.mean(cosines))
                        data[(cname, k)]["ov"].append(np.mean(ovs))
                        data[(cname, k)]["mag"].append(
                            np.mean([np.linalg.norm(errs[j]) for j in js]))

lines = []
def out(s): print(s); lines.append(s)
out("MECHANISM TEST -- does rejection destroy common-mode cancellation between joints?")
out(f"Cache={CACHE}. Hip/knee/ankle chains, exactly k cameras dropped per joint independently.")
out("cos = mean pairwise cosine between the three joints' 3D error vectors (1 = perfectly")
out("      common-mode and therefore cancelling in the angle; 0 = independent).")
out("ov  = mean pairwise Jaccard overlap of the retained camera sets across the three joints.")
out("mag = mean per-joint |position error| (mm).")
out("")
out(f"{'criterion':>10}{'k':>4}{'n':>8}{'cos':>9}{'overlap':>9}{'mag mm':>9}")
for c, nm in (("re", "reproj"), ("ob", "objd")):
    for k in KS:
        d = data[(c, k)]
        if len(d["cos"]) < 50: continue
        out(f"{nm:>10}{k:>4}{len(d['cos']):>8}{np.mean(d['cos']):>9.4f}"
            f"{np.mean(d['ov']):>9.4f}{np.mean(d['mag']):>9.2f}")
out("")
out("P1  cos falls as k rises            -> rejection decorrelates the joints")
out("P2  cos(objd) < cos(reproj) at same k -> the arm better in position, worse in angle,")
out("                                       decorrelates more")
out("P3  overlap falls with k, lower for objd -> the joints stop sharing cameras")
out("")
for k in KS:
    if len(data[("re", k)]["cos"]) < 50: continue
    dc = np.mean(data[("ob", k)]["cos"]) - np.mean(data[("re", k)]["cos"])
    do = np.mean(data[("ob", k)]["ov"]) - np.mean(data[("re", k)]["ov"])
    out(f"  k={k}: cos(objd)-cos(reproj) = {dc:+.4f}   overlap(objd)-overlap(reproj) = {do:+.4f}")
out("")
out("READ: if P1-P3 hold, the harm mechanism is established -- per-joint accuracy gains are")
out("bought by decorrelating errors that used to cancel in the angle. If they fail, the")
out("paper must report the harm as unexplained rather than assert a mechanism.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
