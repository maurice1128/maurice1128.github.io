"""Are the opposed per-joint signs a property of triangulation, or of which way each joint's
definitional offset points?

A reviewer's objection, and it is the sharpest one the paper has received. Table S3m shows that
74-81% of [pos:HKA] position error is a systematic joint-centre offset -- 27-37 mm at hip and knee
-- while the per-joint effects the paper reports are 0.2-0.7 mm. To first order

    |e| = |b + n| ~= |b| + bhat . n            (b = the fixed offset, n the perturbation)

so a change in the triangulated point changes the SCALAR error only through its component along
bhat. Whether an intervention "improves the hip" and "degrades the knee" could therefore be a
statement about the two joints' offset DIRECTIONS rather than about triangulation accuracy. If so,
the aggregation lesson survives -- opposed effects still cancel -- but the mechanism offered in
Section 3.4 is misattributed.

Two tests, on the same frames, arms and estimator as the per-joint family (biocv_round5.py):

(A) OFFSET-REMOVED ERROR, the decisive one. Subtract each participant's own per-joint mean error
    vector, taken from ONE reference arm and applied unchanged to both arms of a contrast, then
    recompute the effect on |e - b|. This removes the definitional offset without removing the
    intervention. If the opposed hip/knee signs survive, the dissociation is about triangulation.
    Run twice -- reference = first-named arm, then reference = second-named arm -- because which
    arm supplies b is a free choice and the answer must not depend on it.

(B) DIRECTIONAL DECOMPOSITION. Split the per-participant mean error-vector difference into the
    component along bhat and the component perpendicular to it. By the expansion above the
    along-component IS the linearised prediction of the scalar effect, so comparing them measures
    how much of the reported effect is offset-mediated.

Vectors are taken in a BODY frame (x = right, hip-to-hip; z = world up made orthogonal to x;
y = anterior), the frame in which a definitional offset is fixed -- the same convention as
biocv_gt_offset.py. In the world frame a walking participant's offset would average towards zero.

Exact sign-flip over the 11 participants, 2^11 = 2048 patterns, as everywhere else.

-> D:/BioCV/BIOCV_OFFSET_CONFOUND.txt
"""
import glob
import io
import itertools
import os
import pickle
import sys
import time

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_OFFSET_CONFOUND.txt")
PROG = "D:/BioCV/_offconf_progress.txt"
SIDES = {"L": (5, 11, 13, 15), "R": (6, 12, 14, 16)}
JNAME = {0: "hip", 1: "knee", 2: "ankle"}

# The four per-joint contrasts of the declared m = 12 family, same order and labels as Table 1b.
# POSITIVE effect = the SECOND-NAMED arm is better.
# THE READING FOR THE TWO ROWS ADDED BELOW IS FIXED HERE, BEFORE THEY HAVE BEEN RUN.
#
# The Conclusion rests on a NULL: discarding cameras buys no detectable position accuracy under
# DLT, bounded within +/-0.35 mm. That bound is computed on a scalar whose 74-81% is a displaced
# target, so it bounds distance-to-a-displaced-target and not necessarily triangulation. The
# offset-removed control of Part A was never applied to those two contrasts. It is applied here.
#
#   - If NEITHER rejection contrast produces a surviving per-joint effect under EITHER reference
#     arm, the null is a null about triangulation and the Conclusion may be stated as it is.
#   - If either produces a surviving effect under BOTH reference arms, the null is an artefact of
#     the displaced target: the Conclusion must say that discarding's position effect is masked by
#     the offset, and the equivalence bound must be restated on offset-removed error.
#   - If a surviving effect appears under ONE reference arm only, that is reported as
#     arm-dependent and carries no verdict, the same rule the rest of this file uses.
#
# Family: these two rows join the m = 12 per-joint family as six more tests (two contrasts x three
# joints), so the BH family for Part A becomes m = 18 and is recomputed whole, not appended.
PJ = [("rep_conf", "objd_conf", "adaptive criterion"),
      ("mk1_re", "mk1_ob", "criterion at matched k=1"),
      ("mk2_re", "mk2_ob", "criterion at matched k=2"),
      ("noRej_unif", "noRej_conf", "uniform -> confidence"),
      ("noRej_conf", "objd_conf", "no rejection -> object-space rejection"),
      ("noRej_conf", "rep_conf", "no rejection -> reprojection rejection")]
ARMS = sorted({a for a, b, _ in PJ} | {b for a, b, _ in PJ})


def rep(cam, X, uv):
    return np.linalg.norm(cam.project(X) - uv)


def objd(cam, X, uv):
    dv = cam.ray_dir(uv)
    w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)


def keep_idx(cs, uvs, w, metric):
    idx = list(range(len(cs)))
    if metric is None:
        return idx
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e)
        mad = np.median(np.abs(e - med)) * 1.4826
        wj = int(np.argmax(e))
        if mad < 1e-9 or e[wj] <= med + K_MAD * mad:
            break
        idx.pop(wj)
    return idx


def solve(cs, uvs, w, metric):
    ii = keep_idx(cs, uvs, w, metric)
    return R.triangulate_wdlt([cs[i] for i in ii], uvs[ii], w[ii])


def drop_k(cs, uvs, w, metric, k):
    idx = list(range(len(cs)))
    for _ in range(k):
        if len(idx) <= MIN_CAM:
            break
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([metric(CS[j], X, uvs[idx][j]) for j in range(len(idx))])
        idx.pop(int(np.argmax(e)))
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])


CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


def body_frame(ml):
    """x = right (hip-to-hip, unit), z = world up orthogonalised to x, y = anterior = z x x."""
    x = ml
    up = np.array([0.0, 0.0, 1.0])
    z = up - np.dot(up, x) * x
    n = np.linalg.norm(z)
    if n < 1e-6:
        return None
    z = z / n
    y = np.cross(z, x)
    return np.vstack([x, y, z])            # rows are the body axes


# VEC[(joint, arm)][pid] -> list of body-frame error vectors, one per observation.
VEC = {}


def addv(joint, arm, pid, v):
    VEC.setdefault((joint, arm), {}).setdefault(pid, []).append(v)


# Trial index and reference posture per observation, parallel to VEC. An odd/even split of
# retained frames leaves the halves 90 ms apart inside the same trial at the same posture, so it
# tests only literal in-sample fitting; a trial-level split and a posture-conditioned removal are
# the tests that bear on the confound the paper itself identifies.
MET = {}


def addm(joint, arm, pid, tri, post):
    MET.setdefault((joint, arm), {}).setdefault(pid, []).append((tri, post))


io.open(PROG, "w").write("start\n")
t0 = time.time()
nf = 0
files = sorted(glob.glob(f"{CACHE}/*.pkl"))
for f in files:
    D = pickle.load(open(f, "rb"))
    pid = D["pid"]
    cams = cams_for(pid)
    nf += 1
    io.open(PROG, "a").write(f"file {nf}/{len(files)} t={time.time()-t0:.0f}s\n")
    for fr in D["frames"]:
        det = fr["det"]
        gt = fr["gt"]
        if not all(j in gt and np.any(gt[j]) for j in (5, 6, 11, 12)):
            continue
        ml = gt[12] - gt[11]
        nml = np.linalg.norm(ml)
        if nml < 1e-6:
            continue
        ml = ml / nml
        B = body_frame(ml)
        if B is None:
            continue
        for side, (jsh, jh, jk, ja) in SIDES.items():
            need = (jsh, jh, jk, ja, 5, 6, 11, 12)
            if not all(j in gt and np.any(gt[j]) for j in need):
                continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in need)]
            if len(vi) < MIN_CAM:
                continue
            cs = [cams[i] for i in vi]
            LIMB = (jh, jk, ja)
            for a in ARMS:
                X = {}
                for j in set(LIMB):
                    uvs = np.array([det[i][j, :2] for i in vi])
                    conf = np.array([det[i][j, 2] for i in vi])
                    w = np.ones_like(conf) if a == "noRej_unif" else conf
                    if a.startswith("mk"):
                        k = int(a[2])
                        m2 = rep if a.endswith("_re") else objd
                        X[j] = drop_k(cs, uvs, w, m2, k)
                    else:
                        metric = None if a.startswith("noRej") else (rep if "rep" in a else objd)
                        X[j] = solve(cs, uvs, w, metric)
                _u = gt[LIMB[0]] - gt[LIMB[1]]
                _v = gt[LIMB[2]] - gt[LIMB[1]]
                _nu, _nv = np.linalg.norm(_u), np.linalg.norm(_v)
                _post = (float(np.degrees(np.arccos(np.clip(np.dot(_u, _v) / (_nu * _nv),
                                                            -1.0, 1.0))))
                         if _nu > 1e-9 and _nv > 1e-9 else float("nan"))
                for s, j in enumerate(LIMB):
                    # Keyed by SIDE as well as joint. Pooling left and right BEFORE taking
                    # the mean offset cancels the mediolateral component, which at the hip
                    # is its largest (L -18.9, R +18.5 mm): the "offset-removed" error would
                    # then still contain the very component it claims to remove.
                    addv(side + "-" + JNAME[s], a, pid, B @ (X[j] - gt[j]))
                    addm(side + "-" + JNAME[s], a, pid, nf, _post)

VEC = {k: {p: np.asarray(v, float) for p, v in d.items()} for k, d in VEC.items()}
MET = {k: {p: np.asarray(v, float) for p, v in d.items()} for k, d in MET.items()}
pickle.dump({k: {p: v.mean(axis=0) for p, v in d.items()} for k, d in VEC.items()},
            open("D:/BioCV/_offset_means.pkl", "wb"))

def _sides(joint, arm):
    return [k for k in (("L-" + joint), ("R-" + joint)) if (k, arm) in VEC]


# WHICH ARM SUPPLIES THE OFFSET IS NOT A FREE CHOICE, AND THE READING BELOW IS FIXED HERE.
#
# Subtracting b = mean(e_A) centres arm A's error cloud on its own centroid, which minimises
# mean|e_A - b| while leaving arm B uncentred. The contrast, defined as first minus second, is
# therefore biased DOWNWARD when b comes from the first arm and UPWARD when it comes from the
# second. This is deterministic, not a fragility: across all 18 rows of the previous run the
# ref=1st column was smaller than the ref=2nd column without exception, mean gap 0.149 mm. An
# earlier version of this file called it "a free choice" and reported the disagreement between
# the two columns as substantive. That was wrong.
#
# The symmetric estimator is the MIDPOINT of the two arms' per-participant mean error vectors.
# Both arms are then displaced from b by the same amount and neither is preferentially centred,
# so the minimisation advantage cancels from the difference.
#
#   - Verdicts are taken from the MIDPOINT column.
#   - The two single-arm columns are retained and labelled as the endpoints of a known bias,
#     not as alternative answers. A quoted range must not be built from them.
#   - Where the midpoint verdict differs from both single-arm verdicts, that is reported.
def pair_scalars(joint, a, b, p):
    """(raw, r1, r2, rm) for one participant. r1/r2 subtract one arm's own mean error vector and
    are biased by construction; rm subtracts the midpoint of the two and is symmetric."""
    raw, r1, r2, rm = [], [], [], []
    for k in _sides(joint, a):
        if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
            continue
        ea, eb = VEC[(k, a)][p], VEC[(k, b)][p]
        raw.append(np.linalg.norm(ea, axis=1).mean() - np.linalg.norm(eb, axis=1).mean())
        for ref, dst in ((ea, r1), (eb, r2)):
            o = ref.mean(axis=0)
            dst.append(np.linalg.norm(ea - o, axis=1).mean()
                       - np.linalg.norm(eb - o, axis=1).mean())
        om = 0.5 * (ea.mean(axis=0) + eb.mean(axis=0))
        rm.append(np.linalg.norm(ea - om, axis=1).mean()
                  - np.linalg.norm(eb - om, axis=1).mean())
    if not raw:
        return None
    return (float(np.mean(raw)), float(np.mean(r1)), float(np.mean(r2)), float(np.mean(rm)))


def pair_pids(joint, a, b):
    ps = None
    for k in _sides(joint, a):
        if (k, b) not in VEC:
            continue
        s_ = set(VEC[(k, a)]) & set(VEC[(k, b)])
        ps = s_ if ps is None else (ps | s_)
    return sorted(ps or [])


SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def bh(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))
    return q


L = []


def out(s):
    print(s)
    L.append(s)


out("IS THE PER-JOINT SIGN STRUCTURE AN ARTEFACT OF OFFSET DIRECTION?")
out("")
out(f"Cache={CACHE}. 11 subjects -> 2^11 = 2048 sign patterns, fully enumerated.")
out("POSITIVE effect = the SECOND-NAMED arm is better (effect = mean|e| of the first arm minus")
out("mean|e| of the second), the same convention as every other family in this paper.")
out("Error vectors are expressed in a body frame (x right, y anterior, z up).")
out("")

# ---------------------------------------------------------------- (A) offset-removed
out("=== (A) THE SAME CONTRASTS ON OFFSET-REMOVED ERROR ===")
out("")
out("|e - b| where b is that participant's own mean error vector for the joint, taken from ONE")
out("reference arm and subtracted from BOTH arms. 'as measured' repeats the published per-joint")
out("effect for comparison. If the hip/knee signs oppose in the offset-removed columns too, the")
out("dissociation is a property of triangulation and not of where each joint's offset points.")
out("")
out("Verdicts come from the MIDPOINT column. The two single-arm columns are the endpoints of a")
out("known downward/upward bias (see the note above pair_scalars) and are shown for reference")
out("only; a range must not be built from them.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'as measured':>13}{'p meas':>10}{'midpoint':>13}{'p':>10}"
    f"{'ref=1st arm':>13}{'ref=2nd arm':>13}")

rows = []
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        raw, r1, r2, rm = [], [], [], []
        for p in pids:
            t = pair_scalars(joint, a, b, p)
            if t is None:
                continue
            raw.append(t[0]); r1.append(t[1]); r2.append(t[2]); rm.append(t[3])
        raw, r1, r2, rm = map(np.array, (raw, r1, r2, rm))
        rows.append((lab, joint, raw.mean(), r1.mean(), r2.mean(),
                     exact_p(r1), exact_p(r2), len(pids), rm.mean(), exact_p(rm)))
        out(f"{lab:<28}{joint:>6}{raw.mean():>+13.3f}{exact_p(raw):>10.4f}"
            f"{rm.mean():>+13.3f}{exact_p(rm):>10.4f}"
            f"{r1.mean():>+13.3f}{r2.mean():>+13.3f}")
    out("")

qm = bh([r[9] for r in rows])
q1 = bh([r[5] for r in rows])
q2 = bh([r[6] for r in rows])
out(f"Benjamini-Hochberg within m = {len(rows)}, run twice -- once per reference arm -- so each")
out("column is a complete correction over the same contrasts, not one correction over both. The")
out("first four contrasts are Table 1b's; the last two are the rejection contrasts the")
out("Conclusion's position null rests on, added under the rule declared at the top of this file.")
# One line per reference choice, each q immediately followed by its own verdict: a q that shares
# a line with another q is invisible to check_prose_q.py, whose regex reads only the value adjacent
# to the verdict. An artefact the standing checker cannot harvest is not evidence.
# The uncorrected p is printed beside the corrected q so this family can be folded into the
# pooled and arbitrary-dependence sensitivities, which both work from raw p.
out(f"{'contrast':<28}{'joint':>6}{'reference':>11}{'effect mm':>11}{'p':>9}{'q':>9}   verdict")
_flips = []
for r, qa, qb, qmm in zip(rows, q1, q2, qm):
    for tag, eff, pv, q in (("midpoint", r[8], r[9], qmm), ("1st arm", r[3], r[5], qa),
                            ("2nd arm", r[4], r[6], qb)):
        v = "SURVIVES" if q < 0.05 else "n.s."
        out(f"{r[0]:<28}{r[1]:>6}{tag:>11}{eff:>+11.3f}{pv:>9.4f}{q:>9.4f}   {v}")
    if (qmm < 0.05) != (qa < 0.05) and (qmm < 0.05) != (qb < 0.05):
        _flips.append((r[0], r[1]))
out("")
if _flips:
    out("The midpoint verdict differs from BOTH single-arm verdicts on:")
    for _l, _j in _flips:
        out(f"    {_l} [{_j}]")
else:
    out("No row has a midpoint verdict differing from both single-arm verdicts.")
out("")

# ---------------------------------------------------------------- (B) decomposition
out("=== (B) HOW MUCH OF EACH EFFECT IS MOTION ALONG THE OFFSET DIRECTION? ===")
out("")
out("For each participant, dvec = mean(e_first) - mean(e_second) and bhat = the unit mean error")
out("vector of the first-named arm. To first order the scalar effect equals bhat . dvec, so the")
out("'along' column is the linearised prediction of the 'as measured' column. 'share' is")
out("along / as-measured: near 1 means the reported effect is entirely offset-mediated.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'|b| mm':>9}{'as measured':>13}{'along':>10}{'perp':>10}"
    f"{'share':>9}")
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        meas, alo, per, bn = [], [], [], []
        for p in pids:
            for k in _sides(joint, a):
                if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
                    continue
                ma = VEC[(k, a)][p].mean(axis=0)
                mb = VEC[(k, b)][p].mean(axis=0)
                nb = np.linalg.norm(ma)
                if nb < 1e-9:
                    continue
                bh_ = ma / nb
                dv = ma - mb
                al = float(dv @ bh_)
                meas.append(np.linalg.norm(VEC[(k, a)][p], axis=1).mean()
                            - np.linalg.norm(VEC[(k, b)][p], axis=1).mean())
                alo.append(al)
                per.append(float(np.linalg.norm(dv - al * bh_)))
                bn.append(nb)
        m_, a_, p_ = np.mean(meas), np.mean(alo), np.mean(per)
        sh = a_ / m_ if abs(m_) > 1e-9 else np.nan
        out(f"{lab:<28}{joint:>6}{np.mean(bn):>9.2f}{m_:>+13.3f}{a_:>+10.3f}{p_:>10.3f}"
            f"{sh:>9.2f}")
    out("")


# ---------------------------------------------------------------- (D) out of sample
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#
# Part A estimates each participant's offset from the same frames it then corrects, and Table 3c
# shows the offset varies with posture by 2.82-6.19 mm, so the residual is not offset-free and the
# correction is in sample. A first attempt to test this by decomposing the offset-removed effect
# against the residual direction was DEGENERATE: subtracting the midpoint leaves the two arms with
# residual means that are exactly equal and opposite, so the difference is collinear with the
# direction by construction and the perpendicular component is identically zero. That version is
# not reported because it measures nothing.
#
# This is the out-of-sample version. The offset is estimated on the odd-indexed observations and
# applied to the even-indexed ones, where the contrast is recomputed. Nothing about the estimate
# comes from the frames it is tested on.
#
#   - If a verdict from Part A keeps its sign and significance out of sample, the in-sample
#     objection is answered for that contrast.
#   - If it loses either, Part A is reporting a fit to its own frames and the Conclusion must
#     withdraw the causal reading of the hip degradation.
#   - Reported for every contrast whichever way it falls, including the halving of n.
out("=== (D) THE SAME CONTRASTS WITH THE OFFSET ESTIMATED OUT OF SAMPLE ===")
out("")
out("Three removals, weakest first. ODD/EVEN splits retained frames within a trial, which are")
out("90 ms apart at the same posture, so it tests only literal in-sample fitting. TRIAL holds one")
out("whole trial out and estimates from the rest. POSTURE removes the offset within quintiles of")
out("the reference thigh-shank angle, which is the confound Table 3c identifies: the residual")
out("after removing a participant MEAN still carries 2.82-6.19 mm of posture-dependent offset,")
out("larger than the effect read out of it.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'in sample':>11}{'odd/even':>10}{'trial-out':>11}"
    f"{'posture':>9}{'p trial':>9}{'p posture':>11}")
_drows = []
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        ins, oe, tr, po = [], [], [], []
        for p in pids:
            vi, ve, vt, vp = [], [], [], []
            for k in _sides(joint, a):
                if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
                    continue
                ea, eb = VEC[(k, a)][p], VEC[(k, b)][p]
                ma_, mb_ = MET.get((k, a), {}).get(p), MET.get((k, b), {}).get(p)
                n = min(len(ea), len(eb))
                if n < 20 or ma_ is None or mb_ is None or len(ma_) < n or len(mb_) < n:
                    continue
                ea, eb, ma_, mb_ = ea[:n], eb[:n], ma_[:n], mb_[:n]
                om = 0.5 * (ea.mean(axis=0) + eb.mean(axis=0))
                vi.append(np.linalg.norm(ea - om, axis=1).mean()
                          - np.linalg.norm(eb - om, axis=1).mean())
                od, ev = slice(1, None, 2), slice(0, None, 2)
                oo = 0.5 * (ea[od].mean(axis=0) + eb[od].mean(axis=0))
                ve.append(np.linalg.norm(ea[ev] - oo, axis=1).mean()
                          - np.linalg.norm(eb[ev] - oo, axis=1).mean())
                # leave one whole trial out
                tris = np.unique(ma_[:, 0])
                dt = []
                for t in tris:
                    hold = ma_[:, 0] == t
                    if hold.sum() < 5 or (~hold).sum() < 20:
                        continue
                    ot = 0.5 * (ea[~hold].mean(axis=0) + eb[~hold].mean(axis=0))
                    dt.append(np.linalg.norm(ea[hold] - ot, axis=1).mean()
                              - np.linalg.norm(eb[hold] - ot, axis=1).mean())
                if dt:
                    vt.append(float(np.mean(dt)))
                # remove the offset WITHIN posture quintile
                q = ma_[:, 1]
                good = np.isfinite(q)
                if good.sum() > 25:
                    edges = np.quantile(q[good], [0.2, 0.4, 0.6, 0.8])
                    binid = np.digitize(q, edges)
                    dq = []
                    for bnum in range(5):
                        m_ = (binid == bnum) & good
                        if m_.sum() < 5:
                            continue
                        ob = 0.5 * (ea[m_].mean(axis=0) + eb[m_].mean(axis=0))
                        dq.append(np.linalg.norm(ea[m_] - ob, axis=1).mean()
                                  - np.linalg.norm(eb[m_] - ob, axis=1).mean())
                    if dq:
                        vp.append(float(np.mean(dq)))
            if vi:
                ins.append(float(np.mean(vi)))
                oe.append(float(np.mean(ve)) if ve else float("nan"))
                tr.append(float(np.mean(vt)) if vt else float("nan"))
                po.append(float(np.mean(vp)) if vp else float("nan"))
        if len(ins) < 5:
            continue
        trv = np.array([x for x in tr if np.isfinite(x)])
        pov = np.array([x for x in po if np.isfinite(x)])
        ptr = exact_p(trv) if len(trv) >= 5 else float("nan")
        ppo = exact_p(pov) if len(pov) >= 5 else float("nan")
        _drows.append((lab, joint, float(np.mean(ins)),
                       float(np.nanmean(tr)), float(np.nanmean(po)), ptr, ppo))
        out(f"{lab:<28}{joint:>6}{np.mean(ins):>+11.3f}{np.nanmean(oe):>+10.3f}"
            f"{np.nanmean(tr):>+11.3f}{np.nanmean(po):>+9.3f}{ptr:>9.4f}{ppo:>11.4f}")
    out("")
_key = [r for r in _drows if r[0].startswith("no rejection") and r[1] == "hip"]
if _key:
    out("=== VERDICT (D), against the rule fixed above ===")
    for lab, joint, i_, t_, q_, pt, pq in _key:
        ok_t = np.isfinite(pt) and (i_ < 0) == (t_ < 0) and pt < 0.05
        ok_q = np.isfinite(pq) and (i_ < 0) == (q_ < 0) and pq < 0.05
        out(f"  {lab} [{joint}]: {i_:+.3f} in sample, {t_:+.3f} trial-out (p = {pt:.4f}),"
            f" {q_:+.3f} within posture (p = {pq:.4f})")
        out(f"      trial-out {'HOLDS' if ok_t else 'DOES NOT HOLD'};"
            f" posture-conditioned {'HOLDS' if ok_q else 'DOES NOT HOLD'}")
    if all(np.isfinite(r[6]) and (r[2] < 0) == (r[4] < 0) and r[6] < 0.05 for r in _key):
        out("  The hip degradation survives removal of the offset WITHIN posture, so it is not the")
        out("  posture-dependent residual Table 3c identifies.")
    else:
        out("  The hip degradation does NOT survive posture-conditioned removal. The Conclusion")
        out("  must withdraw its causal reading and state the result as a change of estimand.")
out("")
_E = []
# ---------------------------------------------------------------- (E) what carries the offset-removed effect
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#
# Part A subtracts ONE b, the midpoint, from BOTH arms, so each arm keeps a residual mean of
# +/- (mean e_A - mean e_B)/2. The contrast on |e - b| therefore mixes a residual MEAN SHIFT with
# a change in DISPERSION, and Section 3.2 currently calls it a precision statement. That is only
# right if dispersion carries it.
#
# Each arm is split into ||mean(e - b)|| and mean||(e - b) - mean(e - b)||, and the contrast is
# taken on each part.
#
#   - If the dispersion part carries most of the hip effect, the precision wording stands.
#   - If the mean-shift part carries it, the word "dispersion" must go and Section 3.2 and the
#     Conclusion must say what the quantity is instead.
#   - Reported for every contrast whichever way it falls.
out("=== (E) IS THE OFFSET-REMOVED EFFECT DISPERSION OR A RESIDUAL MEAN SHIFT? ===")
out("")
out("Part A subtracts one vector from both arms, so each arm keeps a residual mean. The effect on")
out("|e - b| is split into the part from those residual means and the part from scatter about")
out("them. POSITIVE = the second-named arm is better, as everywhere else.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'total':>10}{'mean-shift':>12}{'dispersion':>12}{'disp share':>12}")
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        tot, mshift, disp = [], [], []
        for p in pids:
            vt, vm, vd = [], [], []
            for k in _sides(joint, a):
                if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
                    continue
                ea, eb = VEC[(k, a)][p], VEC[(k, b)][p]
                om = 0.5 * (ea.mean(axis=0) + eb.mean(axis=0))
                ra, rb = ea - om, eb - om
                vt.append(np.linalg.norm(ra, axis=1).mean() - np.linalg.norm(rb, axis=1).mean())
                vm.append(float(np.linalg.norm(ra.mean(axis=0)))
                          - float(np.linalg.norm(rb.mean(axis=0))))
                vd.append(float(np.linalg.norm(ra - ra.mean(axis=0), axis=1).mean())
                          - float(np.linalg.norm(rb - rb.mean(axis=0), axis=1).mean()))
            if vt:
                tot.append(float(np.mean(vt)))
                mshift.append(float(np.mean(vm)))
                disp.append(float(np.mean(vd)))
        if len(tot) < 5:
            continue
        T, M, D = np.mean(tot), np.mean(mshift), np.mean(disp)
        sh = D / T if abs(T) > 1e-9 else float("nan")
        out(f"{lab:<28}{joint:>6}{T:>+10.3f}{M:>+12.3f}{D:>+12.3f}{sh:>12.2f}")
        if lab.startswith("no rejection") and joint == "hip":
            _E.append((lab, T, M, D, sh))
    out("")
if _E:
    out("=== VERDICT (E), against the rule fixed above ===")
    for lab, T, M, D, sh in _E:
        out(f"  {lab}: total {T:+.3f}, mean-shift {M:+.3f}, dispersion {D:+.3f} "
            f"(dispersion carries {100 * sh:.0f}%)")
    if all(x[4] >= 0.5 for x in _E):
        out("  Dispersion carries at least half of each hip effect, so the precision wording in")
        out("  Section 3.2 stands.")
    else:
        out("  Dispersion does NOT carry the hip effect. The word must be replaced: the quantity is")
        out("  a residual mean shift left by subtracting one vector from two arms whose means")
        out("  differ, and Section 3.2 and the Conclusion must say so.")
out("")
out("READ: (A) is decisive. If a contrast keeps its SIGN and survives BH on offset-removed error")
out("under BOTH reference choices, the reviewer's confound does not explain it. If it loses")
out("significance, the effect is a statement about offset geometry and Section 3.4's mechanism")
out("must be restated -- the aggregation lesson would survive either way, since opposed effects")
out("cancel whatever produces them.")


# ---------------------------------------------------------------- (C) the subset control
out("=== (C) THE MATCHED-k SUBSET CONTROL ON OFFSET-REMOVED ERROR ===")
out("")
out("Section 3.4's verdict pair -- the criterion harmful on {knee, ankle}, beneficial on {hip,")
out("ankle}, null on all three -- is a mean over the same per-joint scalars Part A shows to be")
out("offset-mediated, so the caveat has to be carried into it rather than estimated. Each subset")
out("mean is rebuilt from the same offset-removed observations, per participant, and tested the")
out("same way. Family of four subsets x two retentions, BH within each reference arm (m = 8),")
out("")
out("This subsection keeps the two single-arm offsets because Table S4b declares the family that")
out("way; re-declaring it now would be a further degree of freedom. The downward/upward bias")
out("described above pair_scalars applies here too, so the two columns bracket the symmetric")
out("value rather than offering a choice between them.")
out("")
SUBSETS = [("hip+knee+ankle", ("hip", "knee", "ankle")), ("knee+ankle", ("knee", "ankle")),
           ("hip+knee", ("hip", "knee")), ("hip+ankle", ("hip", "ankle"))]

# Table S4b declares this family as 4 subsets x 2 retentions x 2 reference arms, and Section 2.5
# discloses only the ARM split. Correcting inside each retention as well would be a third,
# undeclared split and the more permissive of the two, so the two retentions are pooled here:
# BH at m = 8 within each reference arm, which is what the declaration says.
COLLECT = []
for a, b, lab in PJ:
    if not lab.startswith("criterion at matched"):
        continue
    for nm, js in SUBSETS:
        pids = pair_pids(js[0], a, b)
        raw, r1, r2 = [], [], []
        for p in pids:
            ts = [pair_scalars(j, a, b, p) for j in js]
            if any(t is None for t in ts):
                continue
            raw.append(float(np.mean([t[0] for t in ts])))
            r1.append(float(np.mean([t[1] for t in ts])))
            r2.append(float(np.mean([t[2] for t in ts])))
        COLLECT.append([lab, nm, float(np.mean(raw)), np.array(r1), np.array(r2)])

Q1 = bh([exact_p(r[3]) for r in COLLECT])
Q2 = bh([exact_p(r[4]) for r in COLLECT])
out(f"BH within each reference arm over all {len(COLLECT)} tests (4 subsets x 2 retentions).")
out("")
for want in sorted({r[0] for r in COLLECT}):
    out(f"{want}")
    out(f"  {'subset':<18}{'as measured':>13}{'reference':>11}{'offset-removed':>16}{'p':>9}{'q':>9}   verdict")
    for r, x1, x2 in zip(COLLECT, Q1, Q2):
        if r[0] != want:
            continue
        for tag, arr, q in (("1st arm", r[3], x1), ("2nd arm", r[4], x2)):
            v = "SURVIVES" if q < 0.05 else "n.s."
            out(f"  {r[1]:<18}{r[2]:>+13.3f}{tag:>11}{arr.mean():>+16.3f}"
                f"{exact_p(arr):>9.4f}{q:>9.4f}   {v}")
    out("")
out("READ: if the harmful and beneficial subset verdicts do not survive as an OPPOSED pair on")
out("offset-removed error, the matched-k verdict flip is a statement about what the conventional")
out("metric reports, not about triangulation, and Section 3.4 and the abstract must say so.")
out("")


# ---------------------------------------------------------------- (F) a test Part E could not be
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#
# Part E cannot fail. It subtracts the MIDPOINT om = (mean e_A + mean e_B)/2 from both arms, so
# ra.mean = +(mean e_A - mean e_B)/2 and rb.mean = -(mean e_A - mean e_B)/2. Those two vectors have
# IDENTICAL norms, so its "mean-shift" column is zero for every row by construction and its
# "dispersion share" is forced to 1.00. It could not have returned any other answer, and it is
# therefore withdrawn as support for the precision wording of Section 3.2 whatever this returns.
#
# The quantities below are both free to differ:
#
#   DISPERSION  mean||e_A - mean e_A||  -  mean||e_B - mean e_B||   scatter about each arm's OWN
#                                                                   centre; no shared reference
#   CENTROID    ||mean e_A||            -  ||mean e_B||             how far each arm's centre sits
#                                                                   from the reference joint centre
#
#   - (1) PRECISION STANDS if at the hip the dispersion contrast carries the sign of the total and
#     at least half its magnitude, AND the centroid contrast is smaller in magnitude than the
#     dispersion one. Section 3.2 and the Conclusion may then keep the word.
#   - (2) IT DOES NOT if the centroid contrast is the larger. The wording must then say the arms
#     differ in where their error centre sits, which is an accuracy statement.
#   - (3) Either way Part E is reported as degenerate, because it is.
out("=== (F) DISPERSION OR CENTROID? THE TEST PART E COULD NOT BE ===")
out("")
out("Part E's mean-shift column is zero by construction: it subtracts the midpoint of the two")
out("arms' mean errors from both, which leaves residual means of equal norm and opposite sign.")
out("It is withdrawn. Below, DISPERSION is scatter about each arm's own centre and CENTROID is")
out("the distance of that centre from the reference joint centre; both are free to differ.")
out("POSITIVE = the second-named arm is better, as everywhere else.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'total':>10}{'dispersion':>12}{'centroid':>11}{'verdict':>10}")
_F = {}
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        tot, dsp, cen = [], [], []
        for p in pids:
            vt, vd, vc = [], [], []
            for k in _sides(joint, a):
                if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
                    continue
                ea, eb = VEC[(k, a)][p], VEC[(k, b)][p]
                om = 0.5 * (ea.mean(axis=0) + eb.mean(axis=0))
                vt.append(np.linalg.norm(ea - om, axis=1).mean()
                          - np.linalg.norm(eb - om, axis=1).mean())
                vd.append(np.linalg.norm(ea - ea.mean(axis=0), axis=1).mean()
                          - np.linalg.norm(eb - eb.mean(axis=0), axis=1).mean())
                vc.append(float(np.linalg.norm(ea.mean(axis=0)))
                          - float(np.linalg.norm(eb.mean(axis=0))))
            if vt:
                tot.append(float(np.mean(vt)))
                dsp.append(float(np.mean(vd)))
                cen.append(float(np.mean(vc)))
        if len(tot) < 5:
            continue
        T, D, C = float(np.mean(tot)), float(np.mean(dsp)), float(np.mean(cen))
        ok = (np.sign(D) == np.sign(T) and abs(D) >= 0.5 * abs(T) and abs(C) < abs(D))
        out(f"{lab:<28}{joint:>6}{T:>+10.3f}{D:>+12.3f}{C:>+11.3f}"
            f"{('precision' if ok else 'NOT'):>10}")
        _F[(lab, joint)] = (T, D, C, ok)
out("")
out("=== VERDICT, against the rule fixed above ===")
_hips = [(k, v) for k, v in _F.items() if k[1] == "hip" and k[0].startswith("no rejection")]
if _hips and all(v[3] for _, v in _hips):
    out("(1) PRECISION STANDS. At the hip the dispersion contrast carries the sign of the total and")
    out("    at least half its magnitude, and the centroid contrast is the smaller of the two, on")
    out("    both rejection rows. Section 3.2 and the Conclusion may keep the word.")
elif _hips:
    out("(2) AGAINST THE PAPER: the precision wording is NOT supported on both rejection rows at")
    out("    the hip. Section 3.2 and the Conclusion must say the arms differ in where their error")
    out("    centre sits, which is an accuracy statement, not a precision one.")
    for k, v in _hips:
        out(f"      {k[0]}: total {v[0]:+.3f}, dispersion {v[1]:+.3f}, centroid {v[2]:+.3f}")
else:
    out("No hip rejection row had enough participants to decide.")
out("")
out("NOTE. Part E is degenerate whichever way this falls, and is reported as such.")
out("")



# ---------------------------------------------------------------- (G) is the reversal a tested
# THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
#
# The title and abstract say removing the offset REVERSES per-joint verdicts. That claim has been
# made by pairing an as-measured effect with an offset-removed effect, observing opposite signs,
# and noting each is individually significant -- with the two halves held to different standards:
# the as-measured half is an uncorrected p in no declared family, the offset-removed half a
# BH-corrected q within m = 18. This paper cites Gelman and Stern (2006) twice against exactly
# that inference and tests every OTHER such claim as an interaction. The one claim in the title
# was never tested that way. It is testable from the same per-participant vectors.
#
# The quantity is, per participant, (offset-removed effect) - (as-measured effect), on the same
# contrast and joint, with the offset-removed arm using the symmetric midpoint as everywhere else.
# The exact sign-flip test over all 2^11 sign patterns applies, and BH is applied within the same
# declared family of eighteen (six contrasts x three joints).
#
#   - (1) DEMONSTRATED. If the difference survives correction at the HIP on both deployable
#     rejection contrasts, the reversal is a demonstrated difference in effect and the title may
#     say "reverses".
#   - (2) NOT DEMONSTRATED -- AGAINST THE PAPER. If it does not, the title and abstract must be
#     restated as a CHANGE OF VERDICT and not as a demonstrated difference in effect, in the
#     language Table S3j already prescribes for the joint-set claim.
#   - (3) The matched-k knee rows are reported identically. They are control arms and cannot carry
#     a practical claim whatever they return.
#   - (4) Reported whichever way it falls.
out("=== (G) IS THE REVERSAL A TESTED DIFFERENCE, OR A PAIR OF VERDICTS? ===")
out("")
out("Per participant, (offset-removed effect) minus (as-measured effect), same contrast and joint.")
out("The offset-removed arm uses the symmetric midpoint, as in Part A. Exact sign-flip over all")
out("2^11 sign patterns; BH within the same declared family of eighteen.")
out("")
out(f"{'contrast':<28}{'joint':>6}{'as measured':>13}{'offset-removed':>16}"
    f"{'difference':>12}{'exact p':>10}{'BH q':>9}   verdict")
_G, _Gp = [], []
for a, b, lab in PJ:
    for joint in ("hip", "knee", "ankle"):
        pids = pair_pids(joint, a, b)
        if not pids:
            continue
        vm, vo = [], []
        for p in pids:
            m1, m2 = [], []
            for k in _sides(joint, a):
                if (k, b) not in VEC or p not in VEC[(k, a)] or p not in VEC[(k, b)]:
                    continue
                ea, eb = VEC[(k, a)][p], VEC[(k, b)][p]
                m1.append(np.linalg.norm(ea, axis=1).mean() - np.linalg.norm(eb, axis=1).mean())
                om = 0.5 * (ea.mean(axis=0) + eb.mean(axis=0))
                m2.append(np.linalg.norm(ea - om, axis=1).mean()
                          - np.linalg.norm(eb - om, axis=1).mean())
            if m1:
                vm.append(float(np.mean(m1)))
                vo.append(float(np.mean(m2)))
        if len(vm) < 5:
            continue
        vm, vo = np.array(vm), np.array(vo)
        d = vo - vm
        _G.append((lab, joint, float(vm.mean()), float(vo.mean()), float(d.mean())))
        _Gp.append(exact_p(d))
_Gq = bh(_Gp) if _G else []
for (lab, joint, am, om_, dm), p_, q_ in zip(_G, _Gp, _Gq):
    out(f"{lab:<28}{joint:>6}{am:>+13.3f}{om_:>+16.3f}{dm:>+12.3f}{p_:>10.4f}{q_:>9.4f}   "
        f"{'SURVIVES' if q_ < 0.05 else 'n.s.'}")
out("")
out("=== VERDICT, against the rule fixed above ===")
_hip = [(g, q) for g, q in zip(_G, _Gq)
        if g[1] == "hip" and g[0].startswith("no rejection")]
if _hip and all(q < 0.05 for _, q in _hip):
    out("(1) DEMONSTRATED. The difference between the as-measured and offset-removed effects")
    out("    survives correction at the hip on both deployable rejection contrasts, so the")
    out("    reversal is a tested difference in effect and the title may say 'reverses'.")
elif _hip:
    out("(2) AGAINST THE PAPER: NOT DEMONSTRATED. The difference does not survive correction at")
    out("    the hip on both deployable rejection contrasts:")
    for g, q in _hip:
        out(f"      {g[0]}: difference {g[4]:+.3f} mm, q = {q:.4f}")
    out("    The title and abstract must be restated as a CHANGE OF VERDICT and not as a")
    out("    demonstrated difference in effect, in the language Table S3j prescribes.")
else:
    out("No deployable hip row had enough participants to decide.")
out("")
out("(3) The matched-k knee rows above are control arms and carry no practical claim either way.")
out("")


io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
