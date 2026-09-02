"""MATCHED-RETENTION CONTROL -- answers hostile-referee objection M1, which is a live
threat to both of the paper's significant results.

M1: the two rejection criteria are not matched on how much they discard. Mean cameras
retained (BIOCV_CONTROLS.txt): reproj 8.09/7.71/7.29/6.46 vs objd 8.10/7.77/7.42/6.69.
The retention gap (+0.01/+0.06/+0.13/+0.23) grows monotonically IN LOCKSTEP with the
claimed object-space advantage (+0.16/+0.47/+0.67/+0.68). Because median+k*MAD is not
scale-equivariant across heterogeneous camera distances, the two arms differ in effective
THRESHOLD as well as in ranking -- so the measured "criterion effect" may simply be
"object-space discards less".

FIX: remove exactly k cameras by each criterion, k = 0,1,2,3. Retention is then identical
by construction and only the ORDERING differs. If the object-space advantage survives at
matched k, M1 is answered. If it collapses, the criterion effect was an aggressiveness
artefact and must be reported as such.

Reported on BOTH levels, because they disagree elsewhere in this paper:
  - 3D position error, peripheral joints
  - knee flexion angle error
-> D:/BioCV/BIOCV_MATCHED_K.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_MATCHED_K.txt")
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
KNEE = {"L": (11, 13, 15), "R": (12, 14, 16)}
KS = [0, 1, 2, 3]
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_mk_progress.txt"

def ang3(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def rep(cam, X, uv): return np.linalg.norm(cam.project(X) - uv)
def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def drop_k(cs, uvs, w, metric, k):
    """Remove exactly k cameras, worst-first by `metric`. Retention is identical
    across criteria by construction; only the ordering differs."""
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM: break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx]), len(idx)

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

pos = {k: {"re": [], "ob": [], "keep_re": [], "keep_ob": []} for k in KS}
pos_s = {k: [] for k in KS}
ang = {k: {"re": [], "ob": []} for k in KS}
ang_s = {k: [] for k in KS}
pid2id = {}
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid)
    sid = pid2id.setdefault(pid, len(pid2id)); nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        # ---- 3D position, peripheral joints ----
        for jn, cj in SEV.items():
            if cj not in gt or not np.any(gt[cj]): continue
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM + max(KS): continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            w = np.array([det[i][cj, 2] for i in vi])
            for k in KS:
                Xr, nr = drop_k(cs, uvs, w, rep, k)
                Xo, no = drop_k(cs, uvs, w, objd, k)
                pos[k]["re"].append(np.linalg.norm(Xr - Xg))
                pos[k]["ob"].append(np.linalg.norm(Xo - Xg))
                pos[k]["keep_re"].append(nr); pos[k]["keep_ob"].append(no)
                pos_s[k].append(sid)
        # ---- knee flexion angle ----
        for side, (jh, jk, ja) in KNEE.items():
            if not all(j in gt and np.any(gt[j]) for j in (jh, jk, ja)): continue
            g = ang3(gt[jh], gt[jk], gt[ja])
            if not np.isfinite(g): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0
                                            for j in (jh, jk, ja))]
            if len(vi) < MIN_CAM + max(KS): continue
            cs = [cams[i] for i in vi]
            for k in KS:
                Xr = {}; Xo = {}
                for j in (jh, jk, ja):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    w = np.array([det[i][j, 2] for i in vi])
                    Xr[j], _ = drop_k(cs, uvs, w, rep, k)
                    Xo[j], _ = drop_k(cs, uvs, w, objd, k)
                er = ang3(Xr[jh], Xr[jk], Xr[ja]); eo = ang3(Xo[jh], Xo[jk], Xo[ja])
                if not (np.isfinite(er) and np.isfinite(eo)): continue
                ang[k]["re"].append(abs(er - g)); ang[k]["ob"].append(abs(eo - g))
                ang_s[k].append(sid)

lines = []
def out(s): print(s); lines.append(s)
def ci(d, s):
    s = np.array(s); sl = np.unique(s); idx = {t: np.where(s == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = d[ii].mean()
    return d.mean(), np.percentile(bs, [2.5, 97.5])

out("MATCHED-RETENTION CONTROL (referee M1): exactly k cameras dropped by each criterion,")
out("so retention is identical by construction and ONLY the ordering differs.")
out(f"Cache={CACHE}, {len(pid2id)} subjects.")
out("")
out("=== 3D POSITION, peripheral joints ===")
out(f"{'k dropped':>10}{'n':>8}{'keep_re':>9}{'keep_ob':>9}{'reproj mm':>11}{'objd mm':>10}"
    f"{'   objd advantage (95% CI)':>30}")
for k in KS:
    r = np.array(pos[k]["re"]); o = np.array(pos[k]["ob"])
    if len(r) < 50: continue
    mu, c = ci(r - o, pos_s[k])
    star = "*" if (c[0] > 0 or c[1] < 0) else " "
    out(f"{k:>10}{len(r):>8}{np.mean(pos[k]['keep_re']):>9.2f}{np.mean(pos[k]['keep_ob']):>9.2f}"
        f"{r.mean():>11.2f}{o.mean():>10.2f}{f'{mu:+.3f} [{c[0]:+.3f},{c[1]:+.3f}]{star}':>30}")
out("")
out("=== KNEE FLEXION ANGLE ===")
out(f"{'k dropped':>10}{'n':>8}{'reproj deg':>12}{'objd deg':>10}{'   objd advantage (95% CI)':>30}")
for k in KS:
    r = np.array(ang[k]["re"]); o = np.array(ang[k]["ob"])
    if len(r) < 50: continue
    mu, c = ci(r - o, ang_s[k])
    star = "*" if (c[0] > 0 or c[1] < 0) else " "
    out(f"{k:>10}{len(r):>8}{r.mean():>12.3f}{o.mean():>10.3f}"
        f"{f'{mu:+.3f} [{c[0]:+.3f},{c[1]:+.3f}]{star}':>30}")
out("")
out("READ: k=0 is the no-rejection reference (both arms identical by construction; any")
out("nonzero value there would indicate a bug). If the object-space advantage seen with")
out("MAD thresholding survives at matched k, referee M1 is answered. If it collapses, the")
out("criterion effect was an artefact of object-space discarding fewer cameras.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
