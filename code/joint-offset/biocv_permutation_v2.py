"""EXACT SIGN-FLIP PERMUTATION TEST + BH-FDR -- the manuscript's authoritative family (m = 50).

Supersedes biocv_permutation.py (m=33). Three holes found by the council round-4
first-time reader, all closed here:

 (R1) CONFIDENCE WEIGHTING WAS NEVER TESTED AT THE ANGLE LEVEL.
      The m=33 family had no uniform-weight angle arm, yet the abstract claimed
      "none improved any joint angle" and confidence weighting is the largest
      position lever in the paper (+5.062 mm). The claim had a hole exactly where
      the biggest effect is. Adds arm `noRej_unif` and three angle contrasts.

 (R2) POSITION AND ANGLES WERE MEASURED ON DIFFERENT JOINTS.
      `SEV` = ankles + WRISTS. Wrists enter none of the three angles. So the
      paper's central comparison -- position improves, angles do not -- was partly
      a comparison across different joints. Adds level `posl`: 3D position error
      over exactly the lower-limb joints that form the angles (hip, knee, ankle),
      accumulated inside the angle loop, so it shares the observations, the frames,
      the candidate camera set and the arm definitions with the angle outcomes.
      This is the matched comparison the thesis actually needs.

 (R3) THE +4.12 mm LM REJECTION EFFECT HAD NO q-VALUE.
      It was quoted in the abstract and conclusion from a bootstrap CI only, in a
      paper whose Section 2.7 says the exact test governs. `posl` covers the LM arms,
      so it now gets one.

The old `pos` level (ankles + wrists) is RETAINED unchanged so that every number
already in the manuscript remains checkable and the two joint sets can be compared.

Family size grows 33 -> 50, so every q rises by roughly 46/33 = 1.39x. Contrasts
near the boundary may drop out. That is the honest cost of testing the comparison
fairly rather than on a favourable joint set, and any contrast that drops out is
reported as having dropped out.
-> D:/BioCV/BIOCV_PERM_V3.txt
"""
import glob, os, pickle, itertools, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
# The authoritative family for the manuscript. Do NOT override via BIOCV_OUT for the
# submission run: the paper quotes this file by name and its provenance must be
# reproducible from the script alone.
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_PERM_V3.txt")
SEV = {"L-ankle": 15, "R-ankle": 16, "L-wrist": 9, "R-wrist": 10}
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}
PROG = "D:/BioCV/_perm_v2_progress.txt"

def ang3(a, b, c):
    u = a - b; v = c - b
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6: return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))

def frontal(hip, knee, ankle, ml):
    up = np.array([0.0, 0.0, 1.0]); up = up - np.dot(up, ml) * ml
    n = np.linalg.norm(up)
    if n < 1e-6: return np.nan
    up = up / n
    def pr(v): return np.array([np.dot(v, ml), np.dot(v, up)])
    t = pr(hip - knee); s = pr(ankle - knee)
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
            wj = int(np.argmax(e))
            if mad < 1e-9 or e[wj] <= med + K_MAD * mad: break
            idx.pop(wj)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

POS_ARMS = ["uniform", "conf", "inv_d", "conf_d", "rep_conf", "objd_conf", "rep_wd", "objd_wd",
            "mk1_re", "mk1_ob", "mk2_re", "mk2_ob", "mk3_re", "mk3_ob"]
# R1: noRej_unif added. It is the uniform-weight, no-rejection arm -- the missing
# reference against which confidence weighting can be judged at the angle level.
ANG_ARMS = ["noRej_unif", "noRej_conf", "noRej_wd", "rep_conf", "objd_conf", "rep_wd", "objd_wd",
            "mk1_re", "mk1_ob", "mk2_re", "mk2_ob", "mk3_re", "mk3_ob",
            "lm_noRej", "lm_repRej", "lm_objdRej"]
KS = [1, 2, 3]

def lm_tri(cs, uvs, w, X0, iters=10):
    """Gauss-Newton on sum_i w_i * ||project(cam_i,X) - uv_i||^2 (3 unknowns)."""
    X = X0.astype(float).copy(); lam = 1e-3
    for _ in range(iters):
        JtJ = np.zeros((3, 3)); Jtr = np.zeros(3)
        for k, cam in enumerate(cs):
            Xc = cam.R @ (X - cam.C); z = Xc[2]
            if abs(z) < 1e-9: continue
            fx, fy = cam.K[0, 0], cam.K[1, 1]
            proj = np.array([fx * Xc[0] / z + cam.K[0, 2], fy * Xc[1] / z + cam.K[1, 2]])
            r = proj - uvs[k]
            dp = np.array([[fx / z, 0, -fx * Xc[0] / z**2],
                           [0, fy / z, -fy * Xc[1] / z**2]])
            J = dp @ cam.R
            JtJ += w[k] * (J.T @ J); Jtr += w[k] * (J.T @ r)
        try: dX = np.linalg.solve(JtJ + lam * np.eye(3), -Jtr)
        except np.linalg.LinAlgError: break
        if not np.all(np.isfinite(dX)): break
        X = X + dX
        if np.linalg.norm(dX) < 1e-4: break
    return X

def keep_idx(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is None: return idx
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        wj = int(np.argmax(e))
        if mad < 1e-9 or e[wj] <= med + K_MAD * mad: break
        idx.pop(wj)
    return idx

def drop_k(cs, uvs, w, metric, k):
    """Remove exactly k cameras, worst-first. Retention identical across criteria."""
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM: break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

acc = {}   # (level, arm) -> {pid: [sum, n]}
LOO_OBS = []
def add(level, arm, pid, v):
    d = acc.setdefault((level, arm), {}).setdefault(pid, [0.0, 0])
    d[0] += v; d[1] += 1

open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        # ---------- 3D position, ORIGINAL joint set (ankles + wrists) ----------
        for jn, cj in SEV.items():
            if cj not in gt or not np.any(gt[cj]): continue
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            conf = np.array([det[i][cj, 2] for i in vi])
            dj = np.array([np.linalg.norm(cams[i].C - Xg) for i in vi])
            wd = conf / dj
            E = {
                "uniform":   R.triangulate_wdlt(cs, uvs, np.ones_like(conf)),
                "conf":      R.triangulate_wdlt(cs, uvs, conf),
                "inv_d":     R.triangulate_wdlt(cs, uvs, 1.0 / dj),
                "conf_d":    R.triangulate_wdlt(cs, uvs, wd),
                "rep_conf":  solve(cs, uvs, conf, rep),
                "objd_conf": solve(cs, uvs, conf, objd),
                "rep_wd":    solve(cs, uvs, wd,  rep),
                "objd_wd":   solve(cs, uvs, wd,  objd),
            }
            if len(vi) >= MIN_CAM + max(KS):
                for k in KS:
                    E[f"mk{k}_re"] = drop_k(cs, uvs, conf, rep, k)
                    E[f"mk{k}_ob"] = drop_k(cs, uvs, conf, objd, k)
            for a in POS_ARMS:
                if a in E: add("pos", a, pid, np.linalg.norm(E[a] - Xg))
        # ---------- joint angles, and (R2) position on the SAME joints ----------
        if not all(j in gt and np.any(gt[j]) for j in (5, 6, 11, 12)): continue
        ml = gt[12] - gt[11]; nml = np.linalg.norm(ml)
        if nml < 1e-6: continue
        ml = ml / nml
        for side, (jsh, jh, jk, ja) in SIDES.items():
            need = (jsh, jh, jk, ja, 5, 6, 11, 12)
            if not all(j in gt and np.any(gt[j]) for j in need): continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in need)]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            truth = {"knee_flex": ang3(gt[jh], gt[jk], gt[ja]),
                     "knee_abd":  frontal(gt[jh], gt[jk], gt[ja], ml),
                     "hip_flex":  ang3(0.5 * (gt[5] + gt[6]), gt[jh], gt[jk])}
            LIMB = (jh, jk, ja)   # R2: the three joints the angles are built from
            loo_store_X = {}
            for a in ANG_ARMS:
                mk = a.startswith("mk"); lm = a.startswith("lm")
                if mk and len(vi) < MIN_CAM + max(KS): continue
                if lm:
                    X = {}
                    m2 = None if a == "lm_noRej" else (rep if "rep" in a else objd)
                    for j in set(need):
                        uvs = np.array([det[i][j, :2] for i in vi])
                        conf = np.array([det[i][j, 2] for i in vi])
                        ii = keep_idx(cs, uvs, conf, m2)
                        X0 = R.triangulate_wdlt([cs[q] for q in ii], uvs[ii], conf[ii])
                        X[j] = lm_tri([cs[q] for q in ii], uvs[ii], conf[ii], X0)
                    mlx = X[12] - X[11]; nm = np.linalg.norm(mlx)
                    mlx = mlx / nm if nm > 1e-6 else ml
                    g2 = {"knee_flex": ang3(X[jh], X[jk], X[ja]),
                          "knee_abd":  frontal(X[jh], X[jk], X[ja], mlx),
                          "hip_flex":  ang3(0.5 * (X[5] + X[6]), X[jh], X[jk])}
                    for o in ("knee_flex", "knee_abd", "hip_flex"):
                        if np.isfinite(truth[o]) and np.isfinite(g2[o]):
                            add(o, a, pid, abs(g2[o] - truth[o]))
                    for j in LIMB:
                        add("posl", a, pid, float(np.linalg.norm(X[j] - gt[j])))
                    continue
                if not mk:
                    metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                use_wd = a.endswith("_wd"); use_unif = a.endswith("_unif")
                X = {}
                for j in set(need):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    if use_unif:
                        w = np.ones_like(conf)
                    elif use_wd:
                        dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                        w = conf / dj
                    else:
                        w = conf
                    if mk:
                        k = int(a[2]); m2 = rep if a.endswith("_re") else objd
                        X[j] = drop_k(cs, uvs, w, m2, k)
                    else:
                        X[j] = solve(cs, uvs, w, metric)
                if a == "noRej_conf":
                    loo_store_X = {j: X[j].copy() for j in X}
                    LOO_OBS.append((pid, side, jsh, jh, jk, ja,
                                    {j: gt[j].copy() for j in set(need)}, loo_store_X, ml))
                mlx = X[12] - X[11]; nm = np.linalg.norm(mlx)
                mlx = mlx / nm if nm > 1e-6 else ml
                got = {"knee_flex": ang3(X[jh], X[jk], X[ja]),
                       "knee_abd":  frontal(X[jh], X[jk], X[ja], mlx),
                       "hip_flex":  ang3(0.5 * (X[5] + X[6]), X[jh], X[jk])}
                for o in ("knee_flex", "knee_abd", "hip_flex"):
                    if np.isfinite(truth[o]) and np.isfinite(got[o]):
                        add(o, a, pid, abs(got[o] - truth[o]))
                for j in LIMB:
                    add("posl", a, pid, float(np.linalg.norm(X[j] - gt[j])))

# ---------- LOO pass ----------
_off = {}
for (pid, side, jsh, jh, jk, ja, G, X, ml) in LOO_OBS:
    for j in X: _off.setdefault((pid, j), []).append(X[j] - G[j])
_off = {k: np.mean(v, axis=0) for k, v in _off.items()}
_pids = sorted({p for (p, _) in _off})
def _loo(pid, j):
    vs = [_off[(p, j)] for p in _pids if p != pid and (p, j) in _off]
    return np.mean(vs, axis=0) if vs else np.zeros(3)
for (pid, side, jsh, jh, jk, ja, G, X, ml) in LOO_OBS:
    Y = {j: X[j] - _loo(pid, j) for j in X}
    mlx = Y[12] - Y[11]; nm = np.linalg.norm(mlx)
    mlx = mlx / nm if nm > 1e-6 else ml
    truth = {"knee_flex": ang3(G[jh], G[jk], G[ja]),
             "knee_abd":  frontal(G[jh], G[jk], G[ja], ml),
             "hip_flex":  ang3(0.5 * (G[5] + G[6]), G[jh], G[jk])}
    got = {"knee_flex": ang3(Y[jh], Y[jk], Y[ja]),
           "knee_abd":  frontal(Y[jh], Y[jk], Y[ja], mlx),
           "hip_flex":  ang3(0.5 * (Y[5] + Y[6]), Y[jh], Y[jk])}
    for o in ("knee_flex", "knee_abd", "hip_flex"):
        if np.isfinite(truth[o]) and np.isfinite(got[o]):
            add(o, "loo_corr", pid, abs(got[o] - truth[o]))
    # the LOO correction is a POSITION operation; score it at the position level too
    for j in (jh, jk, ja):
        add("posl", "loo_corr", pid, float(np.linalg.norm(Y[j] - G[j])))

def subj_means(level, arm):
    d = acc[(level, arm)]
    return {p: v[0] / v[1] for p, v in d.items() if v[1] > 0}

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)

def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    obs = abs(d.mean())
    null = np.abs((S * d).mean(axis=1))
    return float((null >= obs - 1e-15).sum()) / len(S)

FAMILY = [
    # ---- 3D position, ORIGINAL joint set: ankles + wrists ----
    ("pos", "uniform",  "conf",      "[pos:AW] uniform vs confidence weighting"),
    ("pos", "inv_d",    "conf",      "[pos:AW] 1/d alone vs confidence"),
    ("pos", "conf",     "conf_d",    "[pos:AW] does 1/d refine confidence?"),
    ("pos", "rep_conf", "objd_conf", "[pos:AW] reprojection vs object-space criterion"),
    ("pos", "rep_conf", "rep_wd",    "[pos:AW] reproj rejection vs the same + 1/d weighting"),
    ("pos", "objd_conf","rep_wd",    "[pos:AW] object-space rejection vs reproj+1/d weighting"),
    # --- D5-4: rejection vs none at the ORIGINAL joint set, the contrast the watchdog
    #     ordered in D4-1 and which the [pos:HKA] substitute did not supply. ---
    ("pos", "conf", "rep_conf",  "[pos:AW] no rejection vs reprojection rejection"),
    ("pos", "conf", "objd_conf", "[pos:AW] no rejection vs object-space rejection"),
    ("pos", "rep_wd",   "objd_wd",   "[pos:AW] criterion, both 1/d-weighted"),
    ("pos", "mk1_re", "mk1_ob", "[pos:AW] matched-k=1: reprojection vs object-space at equal retention"),
    ("pos", "mk2_re", "mk2_ob", "[pos:AW] matched-k=2: reprojection vs object-space at equal retention"),
    ("pos", "mk3_re", "mk3_ob", "[pos:AW] matched-k=3: reprojection vs object-space at equal retention"),
    # ---- R2: 3D position on the SAME joints the angles are built from ----
    ("posl", "noRej_unif", "noRej_conf", "[pos:HKA] uniform vs confidence weighting"),
    ("posl", "noRej_conf", "noRej_wd",   "[pos:HKA] 1/d weighting, no rejection"),
    ("posl", "rep_conf",   "noRej_conf", "[pos:HKA] reproj rejection vs none"),
    ("posl", "objd_conf",  "noRej_conf", "[pos:HKA] objd rejection vs none"),
    ("posl", "rep_conf",   "objd_conf",  "[pos:HKA] reprojection vs object-space criterion"),
    ("posl", "mk1_re", "mk1_ob", "[pos:HKA] matched-k=1: reprojection vs object-space at equal retention"),
    ("posl", "mk2_re", "mk2_ob", "[pos:HKA] matched-k=2: reprojection vs object-space at equal retention"),
    ("posl", "mk3_re", "mk3_ob", "[pos:HKA] matched-k=3: reprojection vs object-space at equal retention"),
    ("posl", "noRej_conf", "loo_corr", "[pos:HKA] LOO population offset correction"),
    # ---- R3: the LM arms now carry a q-value at the position level ----
    ("posl", "lm_noRej",   "lm_repRej",  "[pos:HKA] GN: no rejection vs reprojection rejection"),
    ("posl", "lm_repRej",  "lm_objdRej", "[pos:HKA] GN: reprojection vs object-space criterion"),
    ("posl", "noRej_conf", "lm_noRej",   "[pos:HKA] DLT vs GN, no rejection"),
    # ---- R1: confidence weighting AT THE ANGLE LEVEL (the hole) ----
    ("knee_flex", "noRej_unif", "noRej_conf", "knee flex: uniform vs confidence weighting"),
    ("knee_abd",  "noRej_unif", "noRej_conf", "frontal knee: uniform vs confidence weighting"),
    ("hip_flex",  "noRej_unif", "noRej_conf", "hip flex: uniform vs confidence weighting"),
    # ---- angles, as before ----
    ("knee_flex", "rep_conf",  "noRej_conf", "knee flex: reproj rejection vs none"),
    ("knee_flex", "objd_conf", "noRej_conf", "knee flex: objd rejection vs none"),
    ("knee_flex", "rep_conf",  "objd_conf",  "knee flex: reprojection vs object-space criterion"),
    ("knee_flex", "noRej_conf","noRej_wd",   "knee flex: 1/d weighting, no rejection"),
    ("knee_flex", "rep_wd",    "noRej_wd",   "knee flex: rejection under best weighting"),
    ("knee_abd",  "rep_conf",  "noRej_conf", "frontal knee: reproj rejection vs none"),
    ("knee_abd",  "objd_conf", "noRej_conf", "frontal knee: objd rejection vs none"),
    ("knee_abd",  "rep_conf",  "objd_conf",  "frontal knee: reprojection vs object-space criterion"),
    ("knee_abd",  "noRej_conf","noRej_wd",   "frontal knee: 1/d weighting, no rejection"),
    ("hip_flex",  "rep_conf",  "noRej_conf", "hip flex: reproj rejection vs none"),
    ("hip_flex",  "objd_conf", "noRej_conf", "hip flex: objd rejection vs none"),
    ("hip_flex",  "rep_conf",  "objd_conf",  "hip flex: reprojection vs object-space criterion"),
    ("hip_flex",  "noRej_conf","noRej_wd",   "hip flex: 1/d weighting, no rejection"),
    ("knee_flex", "mk1_re", "mk1_ob", "knee flex matched-k=1: reprojection vs object-space at equal retention"),
    ("knee_flex", "mk2_re", "mk2_ob", "knee flex matched-k=2: reprojection vs object-space at equal retention"),
    ("knee_flex", "mk3_re", "mk3_ob", "knee flex matched-k=3: reprojection vs object-space at equal retention"),
    ("knee_flex", "noRej_conf", "loo_corr", "knee flex: LOO population offset correction"),
    ("knee_abd",  "noRej_conf", "loo_corr", "frontal knee: LOO population offset correction"),
    ("hip_flex",  "noRej_conf", "loo_corr", "hip flex: LOO population offset correction"),
    ("knee_flex", "lm_noRej",   "lm_repRej",  "knee flex GN: no rejection vs reprojection rejection"),
    ("knee_flex", "lm_repRej",  "lm_objdRej", "knee flex GN: reprojection vs object-space criterion"),
    ("knee_flex", "noRej_conf", "lm_noRej",   "knee flex: DLT vs GN, no rejection"),
    ("knee_flex", "noRej_conf", "lm_repRej",  "knee flex: plain DLT vs best-GN"),
]

rows = []
for lvl, a, b, lab in FAMILY:
    if (lvl, a) not in acc or (lvl, b) not in acc: continue
    ma, mb = subj_means(lvl, a), subj_means(lvl, b)
    ps = sorted(set(ma) & set(mb))
    d = np.array([ma[p] - mb[p] for p in ps])
    rows.append((lab, len(ps), d.mean(), exact_p(d)))

order = np.argsort([r[3] for r in rows]); m = len(rows)
q = [0.0] * m; prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    k = m - rank + 1
    val = min(prev, rows[i][3] * m / k)
    q[i] = val; prev = val

lines = []
def out(s): print(s); lines.append(s)
out("EXACT SIGN-FLIP PERMUTATION TEST + BENJAMINI-HOCHBERG FDR")
out("Authoritative contrast family for the manuscript.")
out(f"Cache={CACHE}. 11 subjects -> 2^11 = 2048 sign patterns, fully enumerated.")
out("No asymptotics, no coverage assumption. Minimum attainable two-sided p = 0.000977.")
out(f"Family size m = {m} contrasts. POSITIVE effect = the SECOND-NAMED arm is better")
out("(i.e. effect = mean|error| of the first arm minus mean|error| of the second).")
out("EVERY label names its two arms in the SAME order they are subtracted. Council round 5")
out("found that six labels in the previous run named them in the reverse order -- the numbers")
out("and the prose were right, but the stated decoding rule inverted them. Fixed here.")
out("")
out("LEVELS:  [pos:AW]  3D position over ankles + wrists (the original joint set)")
out("         [pos:HKA] 3D position over hip/knee/ankle -- the SAME joints the angles")
out("                   are built from, same frames, same candidate cameras, same arms.")
out("                   This is the matched comparison; prefer it over [pos:AW] whenever")
out("                   the question is whether position gains transmit to angles.")
out("         knee_flex / knee_abd / hip_flex  joint-angle outcomes")
out("")
out(f"{'contrast':<58}{'n':>4}{'effect':>9}{'exact p':>10}{'BH q':>9}  verdict")
for (lab, n, eff, p), qq in zip(rows, q):
    v = "SURVIVES FDR" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    out(f"{lab:<58}{n:>4}{eff:>+9.3f}{p:>10.4f}{qq:>9.4f}  {v}")
out("")
out("READ: 'raw only' = significant unadjusted but NOT after multiplicity correction.")
out("Any claim resting on a 'raw only' contrast must be withdrawn or restated as exploratory.")
out("")
out("NOTE ON RESOLUTION: with 11 subjects the minimum attainable two-sided p is 2/2048 =")
out("0.000977. Contrasts reported at p = 0.0010 are AT THAT FLOOR and cannot be ranked")
out("against one another; the paper must not imply differing strength within that group.")
out("NOTE ON FAMILY: this family SUPERSEDES the m=33 family in BIOCV_PERM_FINAL.txt. It is")
out("larger, so every q is higher; contrasts that survived at m=33 and do not survive here")
out("must be reported as having dropped out, not quietly retained from the smaller family.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\nWROTE", OUTF)

# Persist the per-participant accumulator. Without it the [pos:AW] level exists only inside
# this process, so the one interaction the paper most needs -- does the SAME contrast behave
# differently on the two joint sets? -- cannot be tested without a 3.3-hour rerun. A cold
# reader found that gap: the manuscript establishes its central dissociation by comparing a
# significant verdict on one joint set with a null on the other, which is the Gelman and Stern
# error the manuscript itself cites twice against. The test is computable from `acc`; this
# dump makes it computable without recomputation.
pickle.dump(acc, open("D:/BioCV/_persubj_v2.pkl", "wb"))
print("WROTE D:/BioCV/_persubj_v2.pkl  (levels:",
      sorted({k[0] for k in acc}), ")")
