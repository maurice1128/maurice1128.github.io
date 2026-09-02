"""EXACT EQUIVALENCE BOUNDS (TOST) + EXPLICIT INTERACTION TESTS FOR EVERY DISSOCIATION.

Council round 4, hostile J Biomech referee, findings 4 and 8. Both are analyses the
paper needed, could compute from data already in hand, and did not run.

FINDING 8 -- "the authors have thrown away a strong, publishable, affirmative result".
  The paper says nulls cannot be read as equivalence because "no consensus margin
  exists for these contrasts". The referee's answer: no consensus margin is needed --
  report the interval and let the reader apply their own margin. Their power
  calculation says a 0.3 deg effect would have been detected with power 0.92-1.00, and
  the load-bearing nulls are equivalent to zero within +-0.09-0.20 deg, i.e. within
  2-4% of the ~5 deg between-session MDC the paper quotes (Wilken et al., 2012).
  We compute the bound EXACTLY rather than from bootstrap SEs, by inverting the same
  sign-flip test the paper uses elsewhere: the 90% CI is the set of shifts delta for
  which the sign-flip test on (d - delta) is not rejected at alpha = 0.10. No
  normality, no asymptotics, consistent with Section 2.7.

FINDING 4 -- "the central claim is a dissociation, and the dissociation is never tested."
  Every "does not transmit" claim in the paper is established by observing that a
  position contrast is significant and an angle contrast is not. That is the
  difference-of-significance fallacy (Gelman & Stern 2006). The correct test is an
  INTERACTION: per participant, compute the position effect and the angle effect on a
  common RELATIVE scale (fraction of that arm's own baseline error), take the
  difference, and sign-flip test it. If the dissociation is real, the interaction is
  significant. If it is not, the paper's central claim is unsupported no matter how the
  two halves look separately.
  Position is taken at the `posl` level -- hip/knee/ankle, the joints the angles are
  actually built from -- NOT the ankles+wrists set the m=33 family used, because two of
  those four joints enter no angle at all.

Also dumps per-subject means to D:/BioCV/_persubj.pkl so later analyses need no re-run.
-> D:/BioCV/BIOCV_EQUIV.txt
"""
import glob, os, pickle, itertools, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = "D:/BioCV/_cache_undist"
OUTF = "D:/BioCV/BIOCV_EQUIV_BOUNDS.txt"
DUMP = "D:/BioCV/_persubj.pkl"
PROG = "D:/BioCV/_equiv_progress.txt"
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}

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

def drop_k(cs, uvs, w, metric, k):
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM: break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

ARMS = ["noRej_unif", "noRej_conf", "noRej_wd", "rep_conf", "objd_conf",
        "mk1_re", "mk1_ob", "mk2_re", "mk2_ob", "mk3_re", "mk3_ob"]
KS = [1, 2, 3]

acc = {}
def add(level, arm, pid, v):
    d = acc.setdefault((level, arm), {}).setdefault(pid, [0.0, 0])
    d[0] += v; d[1] += 1

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
                mk = a.startswith("mk")
                if mk and len(vi) < MIN_CAM + max(KS): continue
                if not mk:
                    metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                X = {}
                for j in set(need):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    if a.endswith("_unif"): w = np.ones_like(conf)
                    elif a.endswith("_wd"):
                        dj = np.array([np.linalg.norm(cams[i].C - gt[j]) for i in vi])
                        w = conf / dj
                    else: w = conf
                    if mk:
                        k = int(a[2]); m2 = rep if a.endswith("_re") else objd
                        X[j] = drop_k(cs, uvs, w, m2, k)
                    else:
                        X[j] = solve(cs, uvs, w, metric)
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

pickle.dump(acc, open(DUMP, "wb"))

def sm(level, arm):
    return {p: v[0] / v[1] for p, v in acc[(level, arm)].items() if v[1] > 0}

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)
def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)

def exact_ci(d, alpha=0.10):
    """Invert the sign-flip test: the set of shifts not rejected at alpha.
    Monotone in |mean - delta|, so a bisection on each side is exact to tolerance."""
    d = np.asarray(d, float); mu = d.mean()
    span = max(np.abs(d).max() * 3, 1e-9)
    def ok(delta): return exact_p(d - delta) > alpha
    lo, hi = mu, mu - span
    for _ in range(60):
        mid = (lo + hi) / 2
        if ok(mid): lo = mid
        else: hi = mid
    L = (lo + hi) / 2
    lo, hi = mu, mu + span
    for _ in range(60):
        mid = (lo + hi) / 2
        if ok(mid): lo = mid
        else: hi = mid
    U = (lo + hi) / 2
    return L, U

# ---- contrasts: (level, armA, armB, label). effect = mean|err|(A) - mean|err|(B) ----
CONTRASTS = [
    ("knee_flex", "rep_conf", "objd_conf", "knee flex: criterion"),
    ("knee_abd",  "rep_conf", "objd_conf", "frontal knee: criterion"),
    ("hip_flex",  "rep_conf", "objd_conf", "hip flex: criterion"),
    ("knee_flex", "noRej_unif", "noRej_conf", "knee flex: uniform vs confidence"),
    ("knee_abd",  "noRej_unif", "noRej_conf", "frontal knee: uniform vs confidence"),
    ("hip_flex",  "noRej_unif", "noRej_conf", "hip flex: uniform vs confidence"),
    ("knee_flex", "mk3_re", "mk3_ob", "knee flex matched-k=3: criterion"),
    ("knee_flex", "noRej_conf", "noRej_wd", "knee flex: 1/d weighting"),
]
# ---- interactions: does the RELATIVE position effect differ from the RELATIVE angle effect? ----
INTER = [
    ("noRej_unif", "noRej_conf", "knee_flex", "uniform->confidence weighting  [knee flex]"),
    ("noRej_unif", "noRej_conf", "knee_abd",  "uniform->confidence weighting  [frontal knee]"),
    ("noRej_unif", "noRej_conf", "hip_flex",  "uniform->confidence weighting  [hip flex]"),
    ("rep_conf", "objd_conf", "knee_flex", "reproj->object-space criterion  [knee flex]"),
    ("rep_conf", "objd_conf", "knee_abd",  "reproj->object-space criterion  [frontal knee]"),
    ("mk1_re", "mk1_ob", "knee_flex", "criterion at matched k=1  [knee flex]"),
    ("mk2_re", "mk2_ob", "knee_flex", "criterion at matched k=2  [knee flex]"),
    ("mk3_re", "mk3_ob", "knee_flex", "criterion at matched k=3  [knee flex]"),
    ("noRej_conf", "noRej_wd", "knee_abd", "confidence->1/d weighting  [frontal knee]"),
    ("noRej_conf", "noRej_wd", "hip_flex", "confidence->1/d weighting  [hip flex]"),
    ("noRej_conf", "rep_conf", "knee_flex", "no rejection->reproj rejection  [knee flex]"),
    ("noRej_conf", "objd_conf", "knee_flex", "no rejection->objd rejection  [knee flex]"),
    ("noRej_conf", "objd_conf", "hip_flex",  "no rejection->objd rejection  [hip flex]"),
]

L = []
def out(s): print(s); L.append(s)
out("EXACT EQUIVALENCE BOUNDS ON THE NULL CONTRASTS")
out(f"Cache={CACHE}. 11 subjects, 2^11 = 2048 sign patterns fully enumerated.")
out("Intervals are EXACT sign-flip confidence intervals (test inversion), not bootstrap.")
out("")
out("=== PART 1. EQUIVALENCE: how large an effect can we rule out? ===")
out("90% CI on the per-subject mean difference. Under TOST, a contrast is equivalent to")
out("zero at margin m if the whole 90% interval lies inside (-m, +m). We quote the")
out("SMALLEST margin at which each null is declared equivalent -- the tightest honest")
out("bound -- rather than testing one margin we chose ourselves.")
out("")
out(f"{'contrast':<44}{'effect':>9}{'90% CI':>22}{'bound':>9}{'% of 5deg MDC':>15}")
for lvl, a, b, lab in CONTRASTS:
    if (lvl, a) not in acc or (lvl, b) not in acc: continue
    ma, mb = sm(lvl, a), sm(lvl, b)
    ps = sorted(set(ma) & set(mb))
    d = np.array([ma[p] - mb[p] for p in ps])
    lo, hi = exact_ci(d, 0.10)
    bound = max(abs(lo), abs(hi))
    out(f"{lab:<44}{d.mean():>+9.3f}{f'[{lo:+.3f}, {hi:+.3f}]':>22}"
        f"{bound:>9.3f}{100*bound/5.0:>14.1f}%")
out("")
out("READ: 'bound' is the smallest equivalence margin this dataset supports for that")
out("contrast. A bound of 0.15 deg means the data rule out any true effect larger than")
out("0.15 deg -- 3% of a ~5 deg minimal detectable change. That is an affirmative")
out("result, not an absence of evidence, and it is what the null-based claims should say.")
out("")
out("Part 2 of this file previously carried an interaction table on a denominator the project")
out("abandoned; the interaction family is now computed by biocv_interaction_fdr.py and reported")
out("in Table 2(c). It is not emitted here.")
open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
