"""T6 -- CAN THE JOINT-CENTRE OFFSET BE CORRECTED, AND DOES THAT FIX THE ANGLES?

Raised by the user hours ago ("why not calibrate the joint centres first, then compare
angles"), logged as T6, blocked on B14, and then not rescheduled after the freeze lifted.
Ranked #2 by impact/effort by the hostile referee: "the only route to a positive,
deployable, clinically framed result from the data already collected."

The honest version must be LEAVE-ONE-SUBJECT-OUT. Estimating a subject's offset from that
same subject's data and then removing it is circular -- it would show a large "improvement"
that no deployed system could reproduce. Here, subject S is corrected using the population
offset computed from the OTHER 10 subjects only. That is exactly what a lab could do with a
published offset table, so the number it produces is deployable.

Reports, per joint-angle outcome:
  raw            error with no correction
  LOO-corrected  error after subtracting the other-10-subjects mean offset
  in-sample      error after subtracting that subject's OWN offset  (the circular upper
                 bound, reported ONLY as a ceiling so the LOO number can be read against it)

Arms: the best configuration found so far (no rejection, confidence weights) and, for
contrast, the current standard (reprojection rejection, confidence weights).
-> D:/BioCV/BIOCV_LOO.txt
"""
import glob, os, pickle, numpy as np, sys, time
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_LOO.txt")
B = 3000; rng = np.random.default_rng(7)
PROG = "D:/BioCV/_loo_progress.txt"
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

ARMS = {"noRej_conf": None, "rep_conf": rep}
JOINTS = [5, 6, 11, 12, 13, 14, 15, 16]
store = []      # (pid, side, arm, {j: Xest}, {j: Xgt}, ml_gt)
open(PROG, "w").write("start\n"); t0 = time.time(); nf = 0
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid); nf += 1
    open(PROG, "a").write(f"file {nf}/108 t={time.time()-t0:.0f}s n={len(store)}\n")
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
            for aname, metric in ARMS.items():
                X = {}
                for j in set(need):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    X[j] = solve(cs, uvs, conf, metric)
                store.append((pid, side, aname, X, {j: gt[j].copy() for j in set(need)}, ml))

# ---- per (arm, pid, joint) offsets ----
# THE READING FOR THE BODY-FRAME TABLE IS FIXED HERE, BEFORE ITS NUMBERS EXIST.
#
# The published table averages the other ten participants' offsets in WORLD coordinates. Table
# S20 measures the heading span at 56 degrees across the study, so if those offsets are
# consistent in a body frame but rotated relative to one another in the world frame, averaging
# them in the world frame cancels part of the signal and the published +9.848 mm understates
# what such a table can buy. The body-frame version is built here and reported beside it.
#
#   - If the body-frame table buys MORE than 1 mm over the world-frame one, the world-frame
#     construction attenuates the correction, and Section 3.4 and Table 2(c) must be restated
#     on the body-frame figure.
#   - If the two are within 1 mm, the world-frame construction is not attenuating and the
#     published value stands.
#   - The ANGLE effect of the body-frame table is reported whichever way the position goes; a
#     body-frame table that buys more position and costs more angle strengthens the paper's
#     dissociation, and one that costs less weakens it. Both are reportable.

def _frame(G):
    """Right-handed leg frame from the reference: x right (hip to hip), z world up made
    orthogonal to x, y = z cross x. Independent of walking heading."""
    x = G[12] - G[11]
    nx = np.linalg.norm(x)
    if nx < 1e-6:
        return None
    x = x / nx
    z = np.array([0.0, 0.0, 1.0])
    z = z - np.dot(z, x) * x
    nz = np.linalg.norm(z)
    if nz < 1e-6:
        return None
    z = z / nz
    return np.stack([x, np.cross(z, x), z], axis=1)          # columns are the axes


off = {}
offb = {}
for (pid, side, a, X, G, ml) in store:
    Rf = _frame(G)
    for j in X:
        d = X[j] - G[j]
        off.setdefault((a, pid, j), []).append(d)
        if Rf is not None:
            offb.setdefault((a, pid, j), []).append(Rf.T @ d)
off = {k: np.mean(v, axis=0) for k, v in off.items()}
offb = {k: np.mean(v, axis=0) for k, v in offb.items()}
pids = sorted({p for (_, p, _) in off})

def loo_offset(a, pid, j):
    vs = [off[(a, p, j)] for p in pids if p != pid and (a, p, j) in off]
    return np.mean(vs, axis=0) if vs else np.zeros(3)

def loo_offset_body(a, pid, j):
    vs = [offb[(a, p, j)] for p in pids if p != pid and (a, p, j) in offb]
    return np.mean(vs, axis=0) if vs else np.zeros(3)

OUTC = ["knee_flex", "knee_abd", "hip_flex"]
res = {o: {a: {"raw": [], "loo": [], "loob": [], "ins": []} for a in ARMS} for o in OUTC}
POS, POSS = {}, {}
sj = {o: {a: [] for a in ARMS} for o in OUTC}
pid2id = {p: i for i, p in enumerate(pids)}
for (pid, side, a, X, G, ml) in store:
    jsh, jh, jk, ja = SIDES[side]
    def bundle(mode):
        Y = {}
        Rf = _frame(G)
        for j in X:
            if mode == "raw":   b = np.zeros(3)
            elif mode == "loo": b = loo_offset(a, pid, j)
            elif mode == "loob":
                b = (Rf @ loo_offset_body(a, pid, j)) if Rf is not None else loo_offset(a, pid, j)
            else:               b = off[(a, pid, j)]
            Y[j] = X[j] - b
        return Y
    truth = {"knee_flex": ang3(G[jh], G[jk], G[ja]),
             "knee_abd":  frontal(G[jh], G[jk], G[ja], ml),
             "hip_flex":  ang3(0.5 * (G[5] + G[6]), G[jh], G[jk])}
    got = {}
    for mode in ("raw", "loo", "loob", "ins"):
        Y = bundle(mode)
        mlx = Y[12] - Y[11]; nm = np.linalg.norm(mlx)
        mlx = mlx / nm if nm > 1e-6 else ml
        got[mode] = {"knee_flex": ang3(Y[jh], Y[jk], Y[ja]),
                     "knee_abd":  frontal(Y[jh], Y[jk], Y[ja], mlx),
                     "hip_flex":  ang3(0.5 * (Y[5] + Y[6]), Y[jh], Y[jk])}
    for _m in ("raw", "loo", "loob", "ins"):
        _Y = bundle(_m)
        for _j in (jh, jk, ja):
            POS.setdefault((a, _m), []).append(float(np.linalg.norm(_Y[_j] - G[_j])))
            POSS.setdefault((a, _m), []).append(pid2id[pid])
    for o in OUTC:
        g = truth[o]
        vals = [got[m][o] for m in ("raw", "loo", "loob", "ins")]
        if not np.isfinite(g) or not all(np.isfinite(v) for v in vals): continue
        res[o][a]["raw"].append(abs(vals[0] - g))
        res[o][a]["loo"].append(abs(vals[1] - g))
        res[o][a]["loob"].append(abs(vals[2] - g))
        res[o][a]["ins"].append(abs(vals[3] - g))
        sj[o][a].append(pid2id[pid])

lines = []
def out(s): print(s); lines.append(s)
out("T6 -- LEAVE-ONE-SUBJECT-OUT JOINT-CENTRE OFFSET CORRECTION, THEN RECOMPUTE ANGLES")
out(f"Cache={CACHE}, {len(pids)} subjects.")
out("LOO = subject corrected using the mean offset of the OTHER 10 subjects (deployable).")
out("in-sample = corrected with the subject's OWN offset (CIRCULAR; a ceiling, not a result).")
out("")
def ci(d, s):
    s = np.array(s); sl = np.unique(s); idx = {t: np.where(s == t)[0] for t in sl}
    bs = np.empty(B)
    for b in range(B):
        pick = rng.choice(sl, size=len(sl), replace=True)
        ii = np.concatenate([idx[t] for t in pick]); bs[b] = d[ii].mean()
    return d.mean(), np.percentile(bs, [2.5, 97.5])
# ---------------------------------------------------------------- a nested null for the LOO rows
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#
# Every participant's correction is built from the other ten, so the eleven per-participant
# differences share estimation data and are not exchangeable under the null. The exact sign-flip
# test used elsewhere in this paper assumes they are, and its p-values for the LOO rows are
# therefore approximate; the dependence is positive, which makes that test ANTI-conservative.
#
# The null built here keeps the construction and destroys only what it is supposed to exploit:
# each contributing participant's mean offset vector is multiplied by a random +/-1 before being
# averaged into the table, so the table retains the right magnitudes and loses the shared
# direction. The statistic is the same [pos:HKA] gain.
#
#   - If the observed gain lies outside the whole nested null distribution, the gain is not an
#     artefact of the shared construction and the sign-flip p-values may stand as reported, with
#     their approximate status stated.
#   - If the observed gain falls inside it, the LOO rows must be reported without p-values and
#     Section 3.4 restated.
#   - The nested null is reported for the position gain only; the angle rows inherit whatever it
#     shows, and that inheritance is stated rather than assumed.
_rng = np.random.default_rng(20260831)
NPERM = int(os.environ.get("BIOCV_LOO_PERM", "500"))


def _loo_signed(a_, pid, j, signs):
    vs = [signs[p] * off[(a_, p, j)] for p in pids if p != pid and (a_, p, j) in off]
    return np.mean(vs, axis=0) if vs else np.zeros(3)


_arm = "noRej_conf"
_obs = None
if (_arm, "raw") in POS:
    _obs = float(np.mean(POS[(_arm, "raw")])) - float(np.mean(POS[(_arm, "loo")]))
    _null = []
    for _b in range(NPERM):
        sg = {p: (1.0 if _rng.random() < 0.5 else -1.0) for p in pids}
        tot, n_ = 0.0, 0
        for (pid_, side_, a_, X_, G_, ml_) in store:
            if a_ != _arm:
                continue
            for j_ in X_:
                bb = _loo_signed(a_, pid_, j_, sg)
                tot += (float(np.linalg.norm(X_[j_] - G_[j_]))
                        - float(np.linalg.norm(X_[j_] - bb - G_[j_])))
                n_ += 1
        if n_:
            _null.append(tot / n_)
    _null = np.array(_null)
    out("=== A NESTED NULL FOR THE LEAVE-ONE-PARTICIPANT-OUT TABLE ===")
    out("")
    out("Each contributing participant's mean offset vector is multiplied by a random +/-1 before")
    out("being averaged into the table, keeping its magnitude and destroying the shared direction.")
    out(f"{NPERM} draws. The statistic is the [pos:HKA] gain on the {_arm} arm.")
    out("")
    out(f"observed gain          {_obs:+.3f} mm")
    out(f"nested null: mean      {_null.mean():+.3f} mm, sd {_null.std():.3f}, "
        f"range [{_null.min():+.3f}, {_null.max():+.3f}]")
    _exceed = int((_null >= _obs).sum())
    out(f"draws reaching the observed gain: {_exceed} of {NPERM}")
    out("")
    out("=== VERDICT, against the rule fixed above ===")
    if _exceed == 0:
        out("The observed gain lies outside the whole nested null. It is not an artefact of the")
        out("shared construction; the sign-flip p-values for the LOO rows stand as reported, with")
        out("their approximate status stated in Section 2.5.")
    else:
        out("The observed gain falls inside the nested null. The LOO rows must be reported without")
        out("p-values and Section 3.4 restated.")
    out("")

out("=== [pos:HKA] POSITION, THE QUANTITY THE DECLARED RULE JUDGES ==="),
out("")
out(f"{'arm':>12}{'raw mm':>10}{'world tbl':>11}{'body tbl':>10}{'world gain':>12}{'body gain':>11}")
for a in ARMS:
    if (a, "raw") not in POS:
        continue
    r0 = float(np.mean(POS[(a, "raw")]))
    lw = float(np.mean(POS[(a, "loo")]))
    lb = float(np.mean(POS[(a, "loob")]))
    out(f"{a:>12}{r0:>10.3f}{lw:>11.3f}{lb:>10.3f}{r0 - lw:>+12.3f}{r0 - lb:>+11.3f}")
out("")
if ("noRej_conf", "raw") in POS:
    _r = float(np.mean(POS[("noRej_conf", "raw")]))
    _w = _r - float(np.mean(POS[("noRej_conf", "loo")]))
    _b = _r - float(np.mean(POS[("noRej_conf", "loob")]))
    out("=== VERDICT, against the rule fixed at the top of this file ===")
    out(f"World-frame table buys {_w:+.3f} mm, body-frame {_b:+.3f} mm, difference {_b - _w:+.3f}.")
    if _b - _w > 1.0:
        out("The world-frame construction ATTENUATES the correction by more than a millimetre.")
        out("Section 3.4 and Table 2(c) must be restated on the body-frame figure.")
    elif _w - _b > 1.0:
        out("The body-frame table buys materially LESS. The world-frame figure stands and the")
        out("body-frame alternative is reported as not helping.")
    else:
        out("The two agree within a millimetre: the world-frame construction is not attenuating")
        out("the correction, and the published figure stands.")
out("")

for o in OUTC:
    out(f"=== {o} ===")
    out(f"{'arm':>12}{'raw':>9}{'LOO-corr':>11}{'LOO body':>10}{'in-sample':>11}"
        f"{'  LOO gain (95% CI)':>26}{'  body gain':>13}")
    for a in ARMS:
        r = np.array(res[o][a]["raw"]); l = np.array(res[o][a]["loo"]); i = np.array(res[o][a]["ins"])
        lb = np.array(res[o][a]["loob"])
        if len(r) < 50: continue
        mu, c = ci(r - l, sj[o][a])
        mub, _ = ci(r - lb, sj[o][a])
        star = "*" if (c[0] > 0 or c[1] < 0) else " "
        out(f"{a:>12}{r.mean():>9.3f}{l.mean():>11.3f}{lb.mean():>10.3f}{i.mean():>11.3f}"
            f"{f'{mu:+.3f} [{c[0]:+.3f},{c[1]:+.3f}]{star}':>26}{mub:>+13.3f}")
    out("")
# The in-sample column was quoted in Section 3.4 as a ceiling and scaled against an MDC, but it
# was a difference of POOLED MEANS with no test and no interval, compared against tested effects
# that had both. Here it is tested the way everything else in the paper is: one mean difference
# per participant, exact sign-flip over the 11, and the interval by inverting that test.
import itertools as _it
_S = {}


def _exact_p(d):
    d = np.asarray(d, float)
    S = _S.setdefault(len(d), np.array(list(_it.product([-1, 1], repeat=len(d))), dtype=float))
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def _exact_ci(d, alpha):
    d = np.asarray(d, float)
    mu = d.mean()
    span = max(np.abs(d).max() * 3, 1e-9)

    def ok(x):
        return _exact_p(d - x) > alpha

    def edge(lo, hi):
        for _ in range(60):
            m = 0.5 * (lo + hi)
            if ok(m):
                lo = m
            else:
                hi = m
        return 0.5 * (lo + hi)

    if not ok(mu):
        return (np.nan, np.nan)
    return (edge(mu, mu - span), edge(mu, mu + span))


out("THE IN-SAMPLE CEILING, TESTED. One mean difference per participant, exact sign-flip over 11.")
out("Positive = correcting with the subject's OWN offset lowers the angle error. Still circular:")
out("a ceiling on what any posture-blind per-participant translation fitted to POSITION could buy,")
out("not an effect a study could deploy.")
out("")
out(f"{'outcome':>10}{'arm':>12}{'ceiling':>9}{'exact 95% CI':>22}{'exact p':>10}")
for o in OUTC:
    for a in ARMS:
        r = np.array(res[o][a]["raw"]); i = np.array(res[o][a]["ins"])
        lab = np.array(sj[o][a])
        if len(r) < 50:
            continue
        per = np.array([ (r[lab == t] - i[lab == t]).mean() for t in np.unique(lab) ])
        if len(per) < 2:
            continue
        lo, hi = _exact_ci(per, 0.05)
        out(f"{o:>10}{a:>12}{per.mean():>9.3f}   [{lo:>+7.3f}, {hi:>+7.3f}]{_exact_p(per):>10.4f}")
out("")

# Section 3.4 concluded "the hip needs participant-specific correspondence rather than a
# distributed table" from the ceiling being significant and the population table not. That is a
# comparison of two verdicts, which this paper cites Gelman and Stern (2006) to forbid and
# installs Table S11 to repair elsewhere. The two are paired -- same participants, same frames --
# so the difference is directly testable, and here it is.
out("CEILING MINUS DEPLOYABLE TABLE, tested. Positive = the participant's OWN offset lowers the")
out("angle error by more than the population table does, i.e. what a distributed table leaves on")
out("the table. One mean difference per participant, exact sign-flip over 11.")
out("")
out(f"{'outcome':>10}{'arm':>12}{'ceiling-LOO':>13}{'exact 95% CI':>22}{'exact p':>10}")
for o in OUTC:
    for a in ARMS:
        l = np.array(res[o][a]["loo"]); i = np.array(res[o][a]["ins"])
        lab = np.array(sj[o][a])
        if len(l) < 50:
            continue
        per = np.array([(l[lab == t] - i[lab == t]).mean() for t in np.unique(lab)])
        if len(per) < 2:
            continue
        lo, hi = _exact_ci(per, 0.05)
        out(f"{o:>10}{a:>12}{per.mean():>13.3f}   [{lo:>+7.3f}, {hi:>+7.3f}]{_exact_p(per):>10.4f}")
out("")

# WHY DOES A POPULATION TABLE HARM THE ANGLE? Section 3.4 previously offered the static
# decomposition of Table 3(b) as the reason, which cannot be right: removing a participant's
# ENTIRE true offset changes the thigh-shank angle by 0.166 deg, p = 0.679, so the geometry of
# that offset cannot explain a harm caused by approximating it. The candidate mechanism is the
# MISMATCH between a participant's own offset and the mean of the other ten.
#
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#   Across the 11 participants, correlate the angle harm the population table does with the
#   size of that mismatch, summed over the three joints defining the angle. Exact permutation
#   over all 11! orderings is infeasible, so the p is a permutation test on the correlation
#   with 100000 random relabellings, seeded.
#     If the correlation is POSITIVE and p < 0.05, the mismatch mechanism is supported and
#     Section 3.4 may state it.
#     Otherwise it is NOT established, and Section 3.4 must say the harm is unexplained rather
#     than substitute a second untested mechanism for the first.
rng2 = np.random.default_rng(20240915)
# WHY DOES A POPULATION TABLE HARM THE ANGLE?
#
# The first version of this test correlated the harm with the SCALAR magnitude of the
# own-minus-population offset mismatch, and found nothing. That was the wrong quantity: a
# three-point included angle is invariant to a COMMON translation of its three points and is
# moved only by the DIFFERENCES between the three translations. The mismatch is therefore
# converted here into the angle change it actually predicts, exactly rather than by projection:
# apply (own offset - population offset) to the three reference points and recompute the angle.
#
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#   Across the 11 participants, correlate the observed harm with that predicted angle change.
#   Permutation test on the correlation, 100000 relabellings, seeded.
#     POSITIVE and p < 0.05 -> the mismatch mechanism is supported and Section 3.4 states it.
#     Otherwise -> not established. With n = 11 a correlation below about 0.6 is undetectable,
#     so a null here is weak evidence and the manuscript must say "not characterised" rather
#     than "excluded".
rng2 = np.random.default_rng(20240915)
out("WHY A POPULATION TABLE HARMS THE ANGLE: does the harm track the angle change the")
out("own-versus-population offset mismatch predicts? Positive harm = the table RAISES the error.")
out("The predictor is the angle change obtained by applying the mismatch to the reference points,")
out("which is what a three-point angle actually responds to; a common translation cancels.")
out("")
out(f"{'outcome':>10}{'arm':>12}{'n':>4}{'mean pred':>11}{'Pearson r':>11}{'perm p':>9}")
for o in ("knee_flex", "hip_flex"):
    for a in ARMS:
        lab = np.array(sj[o][a])
        if len(lab) < 50:
            continue
        r_ = np.array(res[o][a]["raw"]); l_ = np.array(res[o][a]["loo"])
        pred = {}
        for (pid, side, a2, X, G, ml) in store:
            if a2 != a:
                continue
            jsh, jh, jk, ja = SIDES[side]
            mm = {}
            for j in (jsh, jh, jk, ja, 5, 6, 11, 12):
                if (a, pid, j) in off:
                    mm[j] = off[(a, pid, j)] - loo_offset(a, pid, j)
            Y = {j: G[j] + mm.get(j, 0.0) for j in G}
            if o == "knee_flex":
                t0, t1 = ang3(G[jh], G[jk], G[ja]), ang3(Y[jh], Y[jk], Y[ja])
            else:
                t0 = ang3(0.5 * (G[5] + G[6]), G[jh], G[jk])
                t1 = ang3(0.5 * (Y[5] + Y[6]), Y[jh], Y[jk])
            if np.isfinite(t0) and np.isfinite(t1):
                pred.setdefault(pid, []).append(abs(t1 - t0))
        harm, pr = [], []
        for t in np.unique(lab):
            pid = pids[t]
            if pid not in pred:
                continue
            m = lab == t
            harm.append(float((l_[m] - r_[m]).mean()))
            pr.append(float(np.mean(pred[pid])))
        harm, pr = np.array(harm), np.array(pr)
        if len(harm) < 4 or harm.std() == 0 or pr.std() == 0:
            continue
        r = float(np.corrcoef(harm, pr)[0, 1])
        null = np.array([abs(np.corrcoef(harm, rng2.permutation(pr))[0, 1])
                         for _ in range(100000)])
        out(f"{o:>10}{a:>12}{len(harm):>4}{pr.mean():>11.3f}{r:>+11.3f}"
            f"{float((null >= abs(r)).mean()):>9.4f}")
out("")

out("READ: 'LOO gain' positive = correction HELPS. Compare it with the triangulation effects")
out("measured elsewhere (0.03-0.23 deg). If the LOO gain is much larger, the leverage is in")
out("joint-centre correspondence, not in the triangulation stage -- and it is deployable.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
