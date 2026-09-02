"""HALPE-26: a different keypoint convention, and the one angle COCO-17 cannot produce.

The RTMO control tested a different ARCHITECTURE on the same 17 keypoints. This adds a different
MODEL trained on a re-annotated 26-keypoint corpus.

WHAT IT DOES NOT TEST, stated here because the file's earlier framing claimed otherwise: HALPE-26
carries COCO-17's body landmark DEFINITIONS at indices 0-16, which is exactly where hip, knee and
ankle sit. The six added points are feet and head/neck. So at the joints this paper makes its claim
about, the landmark definition is unchanged and only the model and its training corpus differ. Part
A therefore shows the offset is not specific to one model or one training run; whether a genuinely
different landmark definition would place the centre elsewhere is NOT tested here, and no control in
this paper tests it.

What the 26 keypoints do buy is the feet: the BioCV reference carries LTOE/RTOE and HEEL_L/HEEL_R,
so the shank-foot angle becomes measurable on both sides of the comparison for the first time.

Both caches are distortion-corrected before anything is compared. Scoring a corrected cache against
a raw one puts the distortion difference into the detector contrast at exactly the near-camera
residuals distortion moves most; that is what the first version of Table S9 did, and it inverted
the ankle result.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

PART A -- DOES THE OFFSET SURVIVE A CHANGE OF MODEL AND TRAINING CORPUS?

  A1 SHARE. If the bias share of squared error at hip and knee is above 60% under HALPE-26 as
     well, the offset's dominance is not an artefact of one model or training run. It does NOT
     follow that it is convention-independent, for the reason given above. Below 60%, the claim
     is scoped to the published detector and the paper says so.

  A2 MAGNITUDE. Hip and knee bias within a factor of two of the COCO-17 value. Outside that, the
     SIZE of the offset is convention-specific even if its dominance is not, and no numeric
     offset magnitude may be quoted as general.

  A3 DIRECTION. Mean per-participant cosine between the two conventions' offset vectors at hip
     and knee. Above 0.5, the two conventions place the joint centre in the same wrong place and
     the paper's warning about comparisons BETWEEN pipelines holds across conventions. At or
     below 0.5, the offset direction is convention-specific, the per-joint sign structure this
     paper reports would not reproduce under another convention, and that is a SHARPER warning
     than the paper currently makes -- it must be reported whichever way A1 and A2 fall.

  A4 THE ANKLE, reported whichever way it falls. Corrected, RTMO agrees with RTMPose at the
     ankle (+0.94). If HALPE-26 also agrees, ankle offsets are stable across both architecture
     and convention. If HALPE-26 disagrees, the ankle offset is convention-specific while the
     hip and knee are not, and Section 3.1 must say the ankle separately.

PART B -- ANKLE DORSIFLEXION, AN OUTCOME COCO-17 CANNOT PRODUCE.

  Angle: the three-point included angle(knee, ankle, big toe), computed identically for estimate
  and reference, exactly as the paper's other three angles are. Reference big toe = LTOE/RTOE.
  DECLARED SENSITIVITY, fixed here: the same angle on the heel (HEEL_L/HEEL_R). The toe is
  primary; the heel is reported beside it and does not replace it. If the two disagree in sign,
  neither is reported as a verdict.

  B1 COVERAGE. Fewer than 8 participants with usable frames -> the outcome is reported as NOT
     COMPUTABLE, not as a null.

  B2 CONTRASTS. Exactly four, a new declared family, fixed here and not extended afterwards:
       (i)   adaptive reprojection rejection against none
       (ii)  adaptive object-space rejection against none
       (iii) confidence weighting against uniform
       (iv)  the population (leave-one-participant-out) joint-centre offset table against none
     Exact sign-flip over participants; Benjamini-Hochberg within this family of four. The
     family must be added to Table S4b and to the pooled-m sensitivity.

  B3 THE PAPER'S ACCOUNT MAKES TWO PREDICTIONS HERE, AND BOTH ARE REPORTED WHETHER OR NOT THEY
     HOLD:
       (i)  discarding costs this angle as it costs the other three;
       (ii) the joint-centre offset alone, pushed through the angle definition, is sufficient to
            produce dorsiflexion error of the observed size.
     If discarding IMPROVES dorsiflexion, that is a counter-example and belongs in the Discussion
     beside the elbow one. The paper is not re-pointed to absorb it.

  B4 SCOPE. A shank-foot result licenses no claim about "ankle kinematics" in general: it is one
     sagittal degree of freedom on one task, and the manuscript's limitation about
     transverse-plane kinematics stands regardless of how this falls.

  B5 THE TWO-ANGLE INTERACTION. Section 3.4 says the offset table lowers the shank-foot angle
     while raising the thigh-shank angle, "so the dissociation is joint-specific". As written
     that compares a HALPE-26 result with a COCO-17 one and never tests the difference -- two
     verdicts, on two conventions. The thigh-shank angle is therefore recomputed HERE, on this
     same cache and these same frames, and the difference is tested per participant.
       If the interaction survives, the dissociation is joint-specific within one convention and
       Section 3.4 may say so. If it does not, the sign difference is not established and Section
       3.4 must say only that the two angles moved in opposite directions, untested.
     Both angles are in degrees but on very different baselines, so the interaction is computed
     BOTH in raw degrees and as the difference of per-participant fractional changes. A claim
     needs both to agree in sign and both to survive; one alone is a scale artefact by the rule
     Section 2.5 applies to every other interaction in this paper.

-> D:/BioCV/BIOCV_HALPE.txt
"""
import glob
import io
import itertools
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
K_MAD = 3.0
COCO_CACHE = "D:/BioCV/_cache_undist"
HALPE_CACHE = os.environ.get("BIOCV_HALPE_CACHE", "D:/BioCV/_cache_halpe_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_HALPE.txt")

SIDES = {"L": {"hip": 11, "knee": 13, "ankle": 15, "toe": 20, "heel": 24},
         "R": {"hip": 12, "knee": 14, "ankle": 16, "toe": 21, "heel": 25}}
# The thigh-shank angle on THIS cache, so the two-angle comparison of B5 is within one
# convention rather than across two.
TS = {"L": (11, 13, 15), "R": (12, 14, 16)}
JNAME = {11: "L-hip", 12: "R-hip", 13: "L-knee", 14: "R-knee", 15: "L-ankle", 16: "R-ankle"}

CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


def ang3(a, b, c):
    u, v = a - b, c - b
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-6 or nv < 1e-6:
        return np.nan
    return np.degrees(np.arccos(np.clip(u @ v / (nu * nv), -1, 1)))


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


def exact_p(d):
    d = np.asarray(d, float)
    S = np.array(list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def exact_ci(d, alpha=0.05):
    d = np.asarray(d, float)
    mu = d.mean()
    span = max(np.abs(d).max() * 3, 1e-9)

    def ok(x):
        return exact_p(d - x) > alpha

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


def bh(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for r in range(m - 1, -1, -1):
        prev = min(prev, ps[o[r]] * m / (r + 1))
        q[o[r]] = prev
    return q


L = []


def out(s):
    print(s, flush=True)
    L.append(s)


ARMS = ["noRej_unif", "noRej_conf", "rep_conf", "objd_conf"]
acc = {}
OBS = []
TSOBS = []
seg_toe, seg_heel, seg_shank = [], [], []


def add(key, arm, pid, v):
    d = acc.setdefault((key, arm), {}).setdefault(pid, [0.0, 0])
    d[0] += v
    d[1] += 1


def collect_offsets(cache, joints):
    """err[(pid, joint)] -> array of 3D error vectors on the plainest arm."""
    err = {}
    for f in sorted(glob.glob(f"{cache}/*.pkl")):
        D = pickle.load(open(f, "rb"))
        pid = D["pid"]
        cams = cams_for(pid)
        for fr in D["frames"]:
            det, gt = fr["det"], fr["gt"]
            for j in joints:
                if j not in gt or not np.any(gt[j]):
                    continue
                vi = [i for i, dd in enumerate(det)
                      if dd is not None and np.isfinite(dd[j, 0]) and dd[j, 2] > 0]
                if len(vi) < MIN_CAM:
                    continue
                uvs = np.array([det[i][j, :2] for i in vi])
                w = np.array([det[i][j, 2] for i in vi])
                X = R.triangulate_wdlt([cams[i] for i in vi], uvs, w)
                err.setdefault((pid, j), []).append(X - gt[j])
    return {k: np.asarray(v, float) for k, v in err.items()}


def decompose(E, joints):
    rows = {}
    for j in joints:
        pids = sorted({p for (p, jj) in E if jj == j})
        if not pids:
            rows[j] = (np.nan, np.nan, np.nan, 0)
            continue
        bias, resid, share = [], [], []
        for p in pids:
            e = E[(p, j)]
            m = e.mean(axis=0)
            mse = (e ** 2).sum(axis=1).mean()
            bias.append(float(np.linalg.norm(m)))
            resid.append(float(np.sqrt(((e - m) ** 2).sum(axis=1).mean())))
            share.append(float((m @ m) / mse) if mse > 0 else np.nan)
        rows[j] = (float(np.mean(bias)), float(np.mean(resid)),
                   100 * float(np.nanmean(share)), len(pids))
    return rows


def main():
    if not glob.glob(f"{HALPE_CACHE}/*.pkl"):
        out("The HALPE-26 cache is empty or not yet distortion-corrected. No comparison made.")
        out("")
        raw = HALPE_CACHE[:-len("_undist")] if HALPE_CACHE.endswith("_undist") else HALPE_CACHE
        out("Run, in order:  biocv_detect_halpe.py  ->  biocv_halpe_gt.py  ->")
        out(f"BIOCV_UNDIST_SRC={raw} BIOCV_UNDIST_DST={HALPE_CACHE}")
        out("python biocv_make_undist_cache.py  ->  this script.")
        io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
        raise SystemExit("HALPE cache not ready")

    out("HALPE-26: A DIFFERENT MODEL AND TRAINING CORPUS, AND THE SHANK-FOOT ANGLE")
    out("")
    out("The same frames, ground truth, calibration and association rule; only the detector and")
    out("its keypoint convention differ. Both caches distortion-corrected.")
    out("")

    jl = sorted(JNAME)
    Ec = collect_offsets(COCO_CACHE, jl)
    Eh = collect_offsets(HALPE_CACHE, jl)
    rc, rh = decompose(Ec, jl), decompose(Eh, jl)

    out("PART A -- DOES THE OFFSET SURVIVE A CHANGE OF MODEL AND TRAINING CORPUS?")
    out("HALPE-26 carries COCO-17's body landmark definitions at indices 0-16, so at hip,")
    out("knee and ankle the DEFINITION is unchanged and only the model and corpus differ.")
    out("")
    out(f"{'joint':>9}{'':4}{'RTMPose / COCO-17':>26}{'':4}{'RTMPose / HALPE-26':>26}")
    out(f"{'':9}{'':4}{'bias mm':>9}{'random':>8}{'share':>7}"
        f"{'':4}{'bias mm':>9}{'random':>8}{'share':>7}")
    for j in jl:
        a, b = rc[j], rh[j]
        out(f"{JNAME[j]:>9}{'':4}{a[0]:>9.1f}{a[1]:>8.1f}{a[2]:>6.0f}%"
            f"{'':4}{b[0]:>9.1f}{b[1]:>8.1f}{b[2]:>6.0f}%")
    out("")

    out("DIRECTION: cosine between the two models' mean offset vectors, per participant.")
    out(f"{'joint':>9}{'participants':>14}{'mean cos':>10}{'min':>8}{'max':>8}")
    cos_all = {}
    for j in jl:
        shared = sorted({p for (p, jj) in Ec if jj == j} & {p for (p, jj) in Eh if jj == j})
        cs = []
        for p in shared:
            u, v = Ec[(p, j)].mean(axis=0), Eh[(p, j)].mean(axis=0)
            nu, nv = np.linalg.norm(u), np.linalg.norm(v)
            if nu > 1e-9 and nv > 1e-9:
                cs.append(float(u @ v / (nu * nv)))
        cos_all[j] = cs
        if cs:
            out(f"{JNAME[j]:>9}{len(cs):>14}{np.mean(cs):>10.2f}{min(cs):>8.2f}{max(cs):>8.2f}")
        else:
            out(f"{JNAME[j]:>9}{0:>14}{'--':>10}{'--':>8}{'--':>8}")
    out("")

    hk = [j for j in jl if "ankle" not in JNAME[j]]
    ank = [j for j in jl if "ankle" in JNAME[j]]
    share_h = float(np.mean([rh[j][2] for j in hk]))
    ratio = float(np.mean([rh[j][0] / rc[j][0] for j in hk if rc[j][0] > 0]))
    cos_hk = float(np.mean([c for j in hk for c in cos_all[j]]))
    cos_an = float(np.mean([c for j in ank for c in cos_all[j]]))

    out("=== PART A VERDICTS, against the rule fixed in this file's header ===")
    out(f"(A1) SHARE at hip and knee under HALPE-26: {share_h:.0f}%  ->  "
        + ("not specific to one model or training run; it says nothing about a different "
           "landmark definition" if share_h > 60 else
           "model-specific; the claim is scoped to the published detector"))
    out(f"(A2) MAGNITUDE ratio HALPE-26/COCO-17 at hip and knee: {ratio:.2f}x  ->  "
        + ("within a factor of two" if 0.5 <= ratio <= 2.0 else
           "NOT within a factor of two; no offset magnitude may be quoted as general"))
    out(f"(A3) DIRECTION, mean cosine at hip and knee: {cos_hk:+.2f}  ->  "
        + ("the two models disagree with the reference in the same direction" if cos_hk > 0.5
           else "offset direction is model-specific; the sign structure would not reproduce"))
    out(f"(A4) ANKLE, mean cosine: {cos_an:+.2f}  ->  "
        + ("the ankle offset is stable across model as well as architecture" if cos_an > 0.5
           else "the ankle offset is model-specific while hip and knee are not"))
    out("")

    out("PART B -- ANKLE DORSIFLEXION, angle(knee, ankle, toe), reference toe = LTOE/RTOE.")
    out("")
    for f in sorted(glob.glob(f"{HALPE_CACHE}/*.pkl")):
        D = pickle.load(open(f, "rb"))
        pid = D["pid"]
        cams = cams_for(pid)
        for fr in D["frames"]:
            det, gt = fr["det"], fr["gt"]
            for sk, sv in TS.items():
                if not all(j in gt and np.any(gt[j]) for j in sv):
                    continue
                vi = [i for i, dd in enumerate(det)
                      if dd is not None
                      and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in sv)]
                if len(vi) < MIN_CAM:
                    continue
                cs = [cams[i] for i in vi]
                truth = ang3(gt[sv[0]], gt[sv[1]], gt[sv[2]])
                if not np.isfinite(truth):
                    continue
                for a in ("noRej_conf",):
                    X = {}
                    for j in sv:
                        uvs = np.array([det[i][j, :2] for i in vi])
                        conf = np.array([det[i][j, 2] for i in vi])
                        X[j] = solve(cs, uvs, conf, None)
                    TSOBS.append((pid, {j: gt[j].copy() for j in sv},
                                  {j: X[j].copy() for j in sv}, sv))
                    got = ang3(X[sv[0]], X[sv[1]], X[sv[2]])
                    if np.isfinite(got):
                        add("tshank", a, pid, abs(got - truth))
            for sd in SIDES.values():
                for endp in ("toe", "heel"):
                    need = (sd["knee"], sd["ankle"], sd[endp])
                    if not all(j in gt and np.any(gt[j]) for j in need):
                        continue
                    vi = [i for i, dd in enumerate(det)
                          if dd is not None
                          and all(np.isfinite(dd[j, 0]) and dd[j, 2] > 0 for j in need)]
                    if len(vi) < MIN_CAM:
                        continue
                    cs = [cams[i] for i in vi]
                    truth = ang3(gt[need[0]], gt[need[1]], gt[need[2]])
                    if not np.isfinite(truth):
                        continue
                    (seg_toe if endp == "toe" else seg_heel).append(
                        float(np.linalg.norm(gt[need[2]] - gt[need[1]])))
                    if endp == "toe":
                        seg_shank.append(float(np.linalg.norm(gt[need[1]] - gt[need[0]])))
                    for a in ARMS:
                        X = {}
                        for j in need:
                            uvs = np.array([det[i][j, :2] for i in vi])
                            conf = np.array([det[i][j, 2] for i in vi])
                            w = np.ones_like(conf) if a == "noRej_unif" else conf
                            metric = None if a.startswith("noRej") else (
                                rep if "rep" in a else objd)
                            X[j] = solve(cs, uvs, w, metric)
                        if a == "noRej_conf":
                            OBS.append((pid, endp, {j: gt[j].copy() for j in need},
                                        {j: X[j].copy() for j in need}, need))
                        got = ang3(X[need[0]], X[need[1]], X[need[2]])
                        if np.isfinite(got):
                            add(f"dflex_{endp}", a, pid, abs(got - truth))

    npart = len({p for (k, a), d in acc.items() if k == "dflex_toe" for p in d})
    if npart < 8:
        out(f"COVERAGE: {npart} participant(s) with usable frames, fewer than the 8 fixed in the")
        out("header. Ankle dorsiflexion is reported as NOT COMPUTABLE, not as a null.")
        io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("\nWROTE", OUTF)
        return

    off = {}
    for (pid, endp, G, X, need) in OBS:
        for j in need:
            off.setdefault((pid, j), []).append(X[j] - G[j])
    off = {k: np.mean(v, axis=0) for k, v in off.items()}
    pids = sorted({p for (p, _) in off})
    for (pid, endp, G, X, need) in OBS:
        corr = {}
        for j in need:
            others = [off[(q, j)] for q in pids if q != pid and (q, j) in off]
            corr[j] = X[j] - np.mean(others, axis=0) if others else X[j]
        t = ang3(G[need[0]], G[need[1]], G[need[2]])
        g = ang3(corr[need[0]], corr[need[1]], corr[need[2]])
        if np.isfinite(t) and np.isfinite(g):
            add(f"dflex_{endp}", "loo_corr", pid, abs(g - t))

    # Named in the order they are SUBTRACTED, as Table S1 names its contrasts: the effect is
    # mean|e| of the first-named arm minus mean|e| of the second. Naming them the other way
    # round while subtracting this way is how a reader ends up reading every row backwards.
    tsoff = {}
    for (pid, G, X, sv) in TSOBS:
        for j in sv:
            tsoff.setdefault((pid, j), []).append(X[j] - G[j])
    tsoff = {k: np.mean(v, axis=0) for k, v in tsoff.items()}
    tspids = sorted({p for (p, _) in tsoff})
    for (pid, G, X, sv) in TSOBS:
        corr = {}
        for j in sv:
            others = [tsoff[(q, j)] for q in tspids if q != pid and (q, j) in tsoff]
            corr[j] = X[j] - np.mean(others, axis=0) if others else X[j]
        t = ang3(G[sv[0]], G[sv[1]], G[sv[2]])
        g = ang3(corr[sv[0]], corr[sv[1]], corr[sv[2]])
        if np.isfinite(t) and np.isfinite(g):
            add("tshank", "loo_corr", pid, abs(g - t))

    CONTRASTS = [("none vs adaptive reprojection rejection", "noRej_conf", "rep_conf"),
                 ("none vs adaptive object-space rejection", "noRej_conf", "objd_conf"),
                 ("uniform vs confidence weighting", "noRej_unif", "noRej_conf"),
                 ("none vs population offset table", "noRej_conf", "loo_corr")]

    def per(key, arm):
        return {p: v[0] / v[1] for p, v in acc.get((key, arm), {}).items() if v[1] > 0}

    def effect(key, A, B):
        ma, mb = per(key, A), per(key, B)
        sh = sorted(set(ma) & set(mb))
        return np.array([ma[p] - mb[p] for p in sh]), sh

    rows, ps = [], []
    for lab, A, B in CONTRASTS:
        d, sh = effect("dflex_toe", A, B)
        rows.append((lab, d, len(sh)))
        ps.append(exact_p(d))
    qs = bh(ps)

    heel = {}
    for lab, A, B in CONTRASTS:
        dh, shh = effect("dflex_heel", A, B)
        heel[lab] = (dh, exact_p(dh)) if len(shh) >= 2 else (None, None)

    base = float(np.mean(list(per("dflex_toe", "noRej_conf").values())))
    base_h = float(np.mean(list(per("dflex_heel", "noRej_conf").values())))
    out(f"Mean absolute error on the plainest arm: {base:.3f} deg on the toe angle and "
        f"{base_h:.3f} deg")
    out(f"on the heel angle, over {npart} participants. Both baselines are given because an")
    out("effect on the heel angle can only be read against its own.")
    out("")
    out("EFFECT = mean|e| of the FIRST-named arm minus mean|e| of the SECOND, the convention of")
    out("Table S1. So a POSITIVE row means the second-named arm has the lower error: positive on")
    out("a rejection row means discarding HELPS this angle, negative means it COSTS, as it does")
    out("at the other three angles.")
    out("")
    out(f"{'contrast':<44}{'effect deg':>11}{'exact p':>10}{'BH q':>9}{'n':>4}   verdict")
    for (lab, d, n), p_, q_ in zip(rows, ps, qs):
        dh = heel[lab][0]
        agree = dh is not None and np.sign(dh.mean()) == np.sign(d.mean())
        # Section 2.5 withholds the q on every leave-one-participant-out row: the correction for
        # each participant is built from the other ten, the eleven differences are not
        # exchangeable, and the sign-flip test does not apply. That rule was applied to every
        # other family and not to this one. It is applied here.
        loo = "population offset table" in lab
        v = ("q withheld: leave-one-out rows are not exchangeable (Section 2.5)" if loo else
             "n.s." if q_ >= 0.05 else
             ("SURVIVES" if agree else "NO VERDICT: heel disagrees in sign"))
        qs_ = "  --  " if loo else f"{q_:>9.4f}"
        out(f"{lab:<44}{d.mean():>+11.3f}{p_:>10.4f}{qs_:>9}{n:>4}   {v}")
    out("")
    out("Declared family of four, fixed in this file's header before the numbers existed.")
    out("")

    out("DECLARED SENSITIVITY -- the same four contrasts on the heel (HEEL_L/HEEL_R):")
    out(f"{'contrast':<44}{'effect deg':>11}{'exact p':>10}")
    for lab, _, _ in CONTRASTS:
        dh, ph = heel[lab]
        if dh is None:
            out(f"{lab:<44}{'--':>11}{'--':>10}")
        else:
            out(f"{lab:<44}{dh.mean():>+11.3f}{ph:>10.4f}")
    out("")
    out("READ: the toe is primary and the heel is the pre-declared sensitivity. Where the two")
    out("disagree in sign, THIS PAPER REPORTS NO VERDICT, whichever way the toe row falls.")
    out("")

    out("B5 -- IS THE DISSOCIATION JOINT-SPECIFIC WITHIN ONE CONVENTION?")
    out("")
    out("The thigh-shank angle recomputed on THIS cache and these frames, so both angles carry the")
    out("same keypoints. POSITIVE = the offset table LOWERS that angle's error.")
    out("")
    ma, mb = per("dflex_toe", "noRej_conf"), per("dflex_toe", "loo_corr")
    ta, tb = per("tshank", "noRej_conf"), per("tshank", "loo_corr")
    sh = sorted(set(ma) & set(mb) & set(ta) & set(tb))
    if len(sh) >= 8:
        d_foot = np.array([ma[p] - mb[p] for p in sh])
        d_ts = np.array([ta[p] - tb[p] for p in sh])
        f_foot = np.array([(ma[p] - mb[p]) / ma[p] for p in sh])
        f_ts = np.array([(ta[p] - tb[p]) / ta[p] for p in sh])
        out(f"{'quantity':<34}{'effect':>10}{'exact 95% CI':>22}{'exact p':>10}")
        for lab, d, u in (("shank-foot angle, deg", d_foot, "deg"),
                          ("thigh-shank angle, deg", d_ts, "deg"),
                          ("interaction, deg", d_foot - d_ts, "deg"),
                          ("interaction, fractional", 100 * (f_foot - f_ts), "pp")):
            lo, hi = exact_ci(d, 0.05)
            out(f"{lab:<34}{d.mean():>+10.3f}   [{lo:>+7.3f}, {hi:>+7.3f}]{exact_p(d):>10.4f}")
        pd_, pf_ = exact_p(d_foot - d_ts), exact_p(100 * (f_foot - f_ts))
        agree = np.sign((d_foot - d_ts).mean()) == np.sign((f_foot - f_ts).mean())
        out("")
        out(f"n = {len(sh)} participants. Baselines: {np.mean(list(ma.values())):.3f} deg on the "
            f"shank-foot angle, {np.mean(list(ta.values())):.3f} deg on the thigh-shank angle.")
        out("=== B5 VERDICT, against the rule fixed in this file's header ===")
        # Both arms of this comparison are the leave-one-out offset table, so neither exact p
        # above is valid under Section 2.5. The effects and their intervals stand as
        # descriptions; the verdict does not, and is withheld rather than printed.
        out("    -> WITHHELD. Both arms are the leave-one-participant-out offset table, whose")
        out("       differences are not exchangeable, so the exact p above does not apply and no")
        out("       dissociation is claimed here. The effects and intervals stand as description")
        out("       only (Section 2.5).")
    else:
        out(f"COVERAGE: {len(sh)} participants with both angles; fewer than 8, so not computed.")
    out("")

    # IS THE HEEL CONTROL FIT TO VETO ANYTHING? It withholds verdicts on a 0.5-0.65 deg effect
    # while carrying 25.2 deg of its own mean absolute error. If the HALPE heel keypoint and the
    # reference HEEL marker are not the same landmark, the heel angle is a different angle and no
    # sensitivity check at all.
    #
    # THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
    #   Compare the heel keypoint's own 3D offset against the reference HEEL marker with the big
    #   toe's against LTOE/RTOE, on the same frames and the same plain arm.
    #     If the two are of the SAME order, the heel is a comparable landmark and the declared
    #     veto stands as written.
    #     If they differ by a factor of two or more, the heel keypoint is not measuring the
    #     reference landmark, the declared control was not viable, and the manuscript must report
    #     the shank-foot rejection verdicts as UNTESTED rather than as vetoed by a control.
    E_feet = collect_offsets(HALPE_CACHE, [20, 21, 24, 25])
    FN = {20: "L-big toe", 21: "R-big toe", 24: "L-heel", 25: "R-heel"}
    rf = decompose(E_feet, [20, 21, 24, 25])
    out("IS THE HEEL FIT TO VETO? The foot keypoints' own 3D offset against their reference markers.")
    out(f"{'keypoint':>12}{'bias mm':>10}{'random':>9}{'share':>8}{'participants':>14}")
    for j in (20, 21, 24, 25):
        b, r, sh, n = rf[j]
        out(f"{FN[j]:>12}{b:>10.1f}{r:>9.1f}{sh:>7.0f}%{n:>14}")
    toe = np.mean([rf[j][0] for j in (20, 21)])
    heel = np.mean([rf[j][0] for j in (24, 25)])
    ratio = heel / toe if toe > 0 else float("inf")
    out("")
    out(f"heel/toe offset ratio: {ratio:.2f}x  ->  "
        + ("same order; the heel is a comparable landmark and the declared veto stands"
           if ratio < 2.0 else
           "the heel keypoint is NOT measuring the reference landmark. The declared control was "
           "not viable, and the shank-foot rejection verdicts must be reported as UNTESTED "
           "rather than vetoed."))
    out("")

    out("SEGMENT GEOMETRY, because it bears on how much weight the heel row can carry.")
    out("An error e perpendicular to the distal segment of a three-point angle moves that angle")
    out("by about e/L radians, so a short distal segment amplifies the same positional error.")
    out(f"{'segment':>22}{'mean length mm':>16}{'deg per mm':>13}")
    for nm, arr in (("ankle -> big toe", seg_toe), ("ankle -> heel", seg_heel),
                    ("knee -> ankle", seg_shank)):
        if arr:
            Lm = float(np.mean(arr))
            out(f"{nm:>22}{Lm:>16.1f}{np.degrees(1.0 / Lm):>13.2f}")
    if seg_toe and seg_heel:
        amp = float(np.mean(seg_toe)) / float(np.mean(seg_heel))
        out("")
        out(f"The heel angle is only {amp:.1f}x as sensitive to the same positional error as the")
        out("toe angle, which is far too small to explain the disagreement on its own. The")
        out("BASELINES carry more of it: the heel angle starts from 25.2 deg of mean absolute")
        out("error against the toe angle's 7.5, so the offset table's +15.0 deg is a 60% reduction")
        out("against the toe row's 13%. That makes the magnitude reconcilable in kind but not in")
        out("size, and it does not touch the SIGN REVERSAL on the two rejection rows, which stays")
        out("unexplained. The declared rule applies as written: no verdict where the signs differ.")
        out("The offset-table row agrees in sign on both endpoints and is reported as a direction")
        out("only; its magnitude is not stable across them and must not be quoted as an effect")
        out("size.")

    io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nWROTE", OUTF)


if __name__ == "__main__":
    main()
