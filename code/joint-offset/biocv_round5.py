"""COUNCIL ROUND 5 — the three tests the referee named as decisive, plus the estimator audit.

(1) PER-JOINT [pos:HKA] BREAKDOWN.
    Section 3.2's headline is that matched-k criterion gains (+0.148/+0.428/+0.782 mm on
    ankles+wrists) vanish on hip/knee/ankle (+0.029/+0.039/+0.169, n.s.). The referee's
    objection: [pos:HKA] averages hip (RMSE 41 mm, 74-80% fixed offset), knee (31-33) and
    ankle (17). A distal gain divided by three into a nearly doubled baseline is diluted by
    construction, and a 5-15x shrink is exactly what dilution predicts. If the criterion gain
    is genuinely absent AT THE ANKLE -- the same joint that carries it in [pos:AW] -- the
    finding is real and much stronger. If it is present at the ankle and swamped by the hip,
    Section 3.2's argument is an averaging artefact and two Conclusion "design lessons" fall.

(2) THE MISSING INTERACTIONS.
    The paper calls the LOO offset correction "the cleanest dissociation we measured"
    (+9.848 mm position, -0.606 deg knee, both FDR-surviving) and it has NO interaction test
    -- exactly the difference-of-significance reasoning the previous round rejected. Same for
    the GN arms. Also: no equivalence bound on the POSITION half of "position-neutral"
    (+0.005 / -0.163 mm), which is the paper's own load-bearing null.

(3) THE GN ESTIMATOR AUDIT — a possible bug certified by Benjamini-Hochberg.
    `rowv.triangulate_wdlt` scales DLT ROWS by w, so the SVD minimises sum w^2 r^2.
    `lm_tri` accumulates JtJ += w * (J^T J), minimising sum w r^2.
    The DLT therefore optimises w^2 and the GN arm optimises w: "GN vs DLT" (-1.384 mm,
    q = 0.0033, IN-FAMILY) compares two different objectives, and GN moving away from its own
    initialiser is explained by that alone, with no heteroscedasticity story required.
    Here we run GN with w^2 so the two estimators share an objective, and record convergence
    (iterations used, final step norm, divergence count).

Every contrast uses exact sign-flip over the 11 participants. Equivalence bounds invert the
same test; the bisection is checked against a brute-force grid for contiguity, since
monotonicity of the sign-flip p in the shift is assumed rather than proved.
-> D:/BioCV/BIOCV_PERJOINT_GN.txt
"""
import glob, os, pickle, itertools, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = "D:/BioCV/_cache_undist"
OUTF = "D:/BioCV/BIOCV_PERJOINT_GN.txt"
PROG = "D:/BioCV/_round5_progress.txt"
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}
JNAME = {0: "hip", 1: "knee", 2: "ankle"}

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

def solve(cs, uvs, w, metric):
    ii = keep_idx(cs, uvs, w, metric)
    return R.triangulate_wdlt([cs[i] for i in ii], uvs[ii], w[ii])

def drop_k(cs, uvs, w, metric, k):
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM: break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

GNDIAG = {"n": 0, "iters": 0, "diverged": 0, "laststep": []}
def lm_tri(cs, uvs, w, X0, iters=10):
    X = X0.astype(float).copy(); lam = 1e-3; used = 0; step = np.nan
    for t in range(iters):
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
        X = X + dX; used = t + 1; step = float(np.linalg.norm(dX))
        if step < 1e-4: break
    GNDIAG["n"] += 1; GNDIAG["iters"] += used
    GNDIAG["laststep"].append(step)
    if np.isfinite(step) and step > 1.0: GNDIAG["diverged"] += 1
    return X

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

# per-joint position: acc[(jslot, arm)][pid] = [sum, n];  angles: acc[(angle, arm)]
acc = {}
def add(key, arm, pid, v):
    d = acc.setdefault((key, arm), {}).setdefault(pid, [0.0, 0])
    d[0] += v; d[1] += 1

ARMS = ["noRej_unif", "noRej_conf", "rep_conf", "objd_conf",
        "mk1_re", "mk1_ob", "mk2_re", "mk2_ob",
        "gn_w", "gn_w2", "gn_rej_w2"]
LOO_OBS = []

open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
files = sorted(glob.glob(f"{CACHE}/*.pkl"))
for f in files:
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"file {nf}/{len(files)} t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
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
            LIMB = (jh, jk, ja)
            for a in ARMS:
                X = {}
                for j in set(need):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    w = np.ones_like(conf) if a == "noRej_unif" else conf
                    if a.startswith("mk"):
                        k = int(a[2]); m2 = rep if a.endswith("_re") else objd
                        X[j] = drop_k(cs, uvs, w, m2, k)
                    elif a == "gn_w":            # as published: GN weights w, DLT weights w^2
                        X0 = R.triangulate_wdlt(cs, uvs, conf)
                        X[j] = lm_tri(cs, uvs, conf, X0)
                    elif a == "gn_w2":           # AUDIT: GN weights w^2, matching the DLT
                        X0 = R.triangulate_wdlt(cs, uvs, conf)
                        X[j] = lm_tri(cs, uvs, conf**2, X0)
                    elif a == "gn_rej_w2":
                        ii = keep_idx(cs, uvs, conf, rep)
                        X0 = R.triangulate_wdlt([cs[q] for q in ii], uvs[ii], conf[ii])
                        X[j] = lm_tri([cs[q] for q in ii], uvs[ii], conf[ii]**2, X0)
                    else:
                        metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                        X[j] = solve(cs, uvs, w, metric)
                if a == "noRej_conf":
                    LOO_OBS.append((pid, jsh, jh, jk, ja,
                                    {j: gt[j].copy() for j in set(need)},
                                    {j: X[j].copy() for j in X}, ml))
                mlx = X[12] - X[11]; nm = np.linalg.norm(mlx)
                mlx = mlx / nm if nm > 1e-6 else ml
                got = {"knee_flex": ang3(X[jh], X[jk], X[ja]),
                       "knee_abd":  frontal(X[jh], X[jk], X[ja], mlx),
                       "hip_flex":  ang3(0.5 * (X[5] + X[6]), X[jh], X[jk])}
                for o in ("knee_flex", "knee_abd", "hip_flex"):
                    if np.isfinite(truth[o]) and np.isfinite(got[o]):
                        add(o, a, pid, abs(got[o] - truth[o]))
                for s, j in enumerate(LIMB):
                    add(JNAME[s], a, pid, float(np.linalg.norm(X[j] - gt[j])))
                add("posl", a, pid, float(np.mean([np.linalg.norm(X[j] - gt[j]) for j in LIMB])))

# ---- LOO offset correction, scored at position AND angle so it can be interacted ----
_off = {}
for (pid, jsh, jh, jk, ja, G, X, ml) in LOO_OBS:
    for j in X: _off.setdefault((pid, j), []).append(X[j] - G[j])
_off = {k: np.mean(v, axis=0) for k, v in _off.items()}
_pids = sorted({p for (p, _) in _off})
def _loo(pid, j):
    vs = [_off[(p, j)] for p in _pids if p != pid and (p, j) in _off]
    return np.mean(vs, axis=0) if vs else np.zeros(3)
for (pid, jsh, jh, jk, ja, G, X, ml) in LOO_OBS:
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
    for s, j in enumerate((jh, jk, ja)):
        add(JNAME[s], "loo_corr", pid, float(np.linalg.norm(Y[j] - G[j])))
    add("posl", "loo_corr", pid,
        float(np.mean([np.linalg.norm(Y[j] - G[j]) for j in (jh, jk, ja)])))

pickle.dump(acc, open("D:/BioCV/_persubj_round5.pkl", "wb"))

def sm(key, arm): return {p: v[0] / v[1] for p, v in acc[(key, arm)].items() if v[1] > 0}
SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)
def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)

def exact_ci(d, alpha=0.10, check=False):
    d = np.asarray(d, float); mu = d.mean(); span = max(np.abs(d).max() * 3, 1e-9)
    def ok(x): return exact_p(d - x) > alpha
    def bis(lo, hi):
        for _ in range(60):
            m = (lo + hi) / 2
            if ok(m): lo = m
            else: hi = m
        return (lo + hi) / 2
    L, U = bis(mu, mu - span), bis(mu, mu + span)
    holes = None
    if check:                      # contiguity check vs brute-force grid
        gs = np.linspace(mu - span, mu + span, 4001)
        acc_mask = np.array([ok(g) for g in gs])
        idx = np.where(acc_mask)[0]
        holes = 0 if len(idx) == 0 else int((np.diff(idx) > 1).sum())
    return L, U, holes

def contrast(key, a, b):
    ma, mb = sm(key, a), sm(key, b)
    ps = sorted(set(ma) & set(mb))
    return np.array([ma[p] - mb[p] for p in ps])

L = []
def out(s): print(s); L.append(s)
out("COUNCIL ROUND 5 -- per-joint breakdown, missing interactions, GN estimator audit")
out(f"Cache={CACHE}. 11 subjects, exact sign-flip (2048 patterns). "
    "POSITIVE = the SECOND-NAMED arm is better.")
out("")

out("=== (1) PER-JOINT [pos:HKA]: is the criterion gain absent, or diluted by the hip? ===")
out(f"{'contrast':<40}{'joint':>8}{'baseline':>10}{'effect mm':>11}{'rel %':>8}{'exact p':>10}")
PJ = [("rep_conf", "objd_conf", "adaptive criterion"),
      ("mk1_re", "mk1_ob", "criterion at matched k=1"),
      ("mk2_re", "mk2_ob", "criterion at matched k=2"),
      ("noRej_unif", "noRej_conf", "uniform -> confidence")]
for a, b, lab in PJ:
    for key in ("hip", "knee", "ankle", "posl"):
        if (key, a) not in acc or (key, b) not in acc: continue
        d = contrast(key, a, b); base = np.mean(list(sm(key, b).values()))
        out(f"{lab:<40}{key:>8}{base:>10.2f}{d.mean():>+11.3f}"
            f"{100*d.mean()/base:>+8.2f}{exact_p(d):>10.4f}")
    out("")
out("READ: if the criterion gain is absent AT THE ANKLE (where [pos:AW] locates it), the")
out("Section 3.2 finding is real. If it is present at the ankle and only the hip average")
out("kills it, Section 3.2 is an averaging artefact and must be restated per joint.")
out("")

out("=== (2) THE MISSING INTERACTIONS (loo_corr and the GN arms) ===")
out(f"{'intervention':<46}{'dpos%':>8}{'dang%':>8}{'interact':>10}{'exact p':>10}")
MISS = [("noRej_conf", "loo_corr", "knee_flex", "LOO offset correction  [knee flex]"),
        ("noRej_conf", "loo_corr", "knee_abd",  "LOO offset correction  [frontal knee]"),
        ("noRej_conf", "loo_corr", "hip_flex",  "LOO offset correction  [hip flex]"),
        ("gn_w", "gn_rej_w2", "knee_flex", "GN: rejection (w^2-matched)  [knee flex]"),
        ("noRej_conf", "gn_w",  "knee_flex", "DLT -> GN as published (w)  [knee flex]"),
        ("noRej_conf", "gn_w2", "knee_flex", "DLT -> GN w^2-matched  [knee flex]")]
for a, b, ang, lab in MISS:
    if ("posl", a) not in acc or ("posl", b) not in acc: continue
    pa, pb, aa, ab = sm("posl", a), sm("posl", b), sm(ang, a), sm(ang, b)
    ps = sorted(set(pa) & set(pb) & set(aa) & set(ab))
    rp = np.array([(pa[p] - pb[p]) / pb[p] for p in ps])
    ra = np.array([(aa[p] - ab[p]) / ab[p] for p in ps])
    dif = rp - ra
    out(f"{lab:<46}{100*rp.mean():>+8.2f}{100*ra.mean():>+8.2f}"
        f"{100*dif.mean():>+10.2f}{exact_p(dif):>10.4f}")
out("")

out("=== (3) GN ESTIMATOR AUDIT ===")
out("rowv.triangulate_wdlt scales DLT ROWS by w  -> the SVD minimises sum w^2 r^2.")
out("lm_tri accumulates JtJ += w*(J^T J)         -> GN minimises sum w r^2.")
out("So the published 'GN vs DLT' contrast compares two different objectives.")
out("")
out(f"{'contrast':<52}{'effect mm':>11}{'exact p':>10}")
for a, b, lab in [("noRej_conf", "gn_w",  "[pos:HKA] DLT vs GN weighted w   (as published)"),
                  ("noRej_conf", "gn_w2", "[pos:HKA] DLT vs GN weighted w^2 (objective-matched)"),
                  ("gn_w", "gn_w2",       "[pos:HKA] GN(w) vs GN(w^2)")]:
    if ("posl", a) not in acc or ("posl", b) not in acc: continue
    d = contrast("posl", a, b)
    out(f"{lab:<52}{d.mean():>+11.3f}{exact_p(d):>10.4f}")
out("")
n = max(GNDIAG["n"], 1)
out(f"GN convergence: {GNDIAG['n']} calls, mean {GNDIAG['iters']/n:.2f} iterations, "
    f"median final step {np.nanmedian(GNDIAG['laststep']):.2e} mm, "
    f"{GNDIAG['diverged']} calls ({100*GNDIAG['diverged']/n:.2f}%) ended with a step > 1 mm.")
out("READ: if DLT-vs-GN shrinks or reverses once the objective is matched, Section 3.4's")
out("heteroscedasticity interpretation is unsupported and the published contrast is an")
out("artefact of the w vs w^2 mismatch, not a finding about estimators.")
out("")

out("=== (4) EQUIVALENCE BOUNDS ON THE LOAD-BEARING NULLS ===")
out("Exact 90% CI by sign-flip inversion, with a 4001-point brute-force contiguity check")
out("('holes' = interior gaps in the acceptance set; 0 validates the bisection).")
out(f"{'contrast':<50}{'effect':>9}{'90% CI':>24}{'holes':>7}")
EQ = [("posl", "rep_conf", "noRej_conf", "[pos:HKA] reproj rejection vs none (mm)"),
      ("posl", "objd_conf", "noRej_conf", "[pos:HKA] objd rejection vs none (mm)"),
      ("posl", "mk1_re", "mk1_ob", "[pos:HKA] criterion at matched k=1 (mm)"),
      ("knee_flex", "noRej_unif", "noRej_conf", "knee flex: uniform vs confidence (deg)")]
for key, a, b, lab in EQ:
    if (key, a) not in acc or (key, b) not in acc: continue
    d = contrast(key, a, b); lo, hi, holes = exact_ci(d, 0.10, check=True)
    out(f"{lab:<50}{d.mean():>+9.3f}{f'[{lo:+.3f}, {hi:+.3f}]':>24}{holes:>7}")
out("")
out("--- and the bound on the TRANSMISSION interaction (the new thesis) ---")
pa, pb = sm("posl", "noRej_unif"), sm("posl", "noRej_conf")
for ang, lab in [("knee_abd", "frontal knee"), ("hip_flex", "hip flex"), ("knee_flex", "knee flex")]:
    aa, ab = sm(ang, "noRej_unif"), sm(ang, "noRej_conf")
    ps = sorted(set(pa) & set(pb) & set(aa) & set(ab))
    rp = np.array([(pa[p] - pb[p]) / pb[p] for p in ps])
    ra = np.array([(aa[p] - ab[p]) / ab[p] for p in ps])
    dif = rp - ra
    lo, hi, holes = exact_ci(dif, 0.10, check=True)
    out(f"uniform->confidence [{lab}]: interaction {100*dif.mean():+.2f}%  "
        f"90% CI [{100*lo:+.2f}, {100*hi:+.2f}] pp   (position effect {100*rp.mean():+.2f}%)  holes={holes}")
out("")
out("READ: 'proportional transmission' requires the interaction interval to be TIGHT around")
out("zero relative to the position effect. A wide interval centred near zero is absence of")
out("evidence, not evidence of proportionality, and must not be claimed as the latter.")

open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
