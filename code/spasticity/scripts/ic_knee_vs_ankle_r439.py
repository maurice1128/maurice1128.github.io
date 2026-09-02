# -*- coding: utf-8 -*-
"""r439: at initial contact, does the ANKLE separate the two lesions, and does the KNEE?

WHY THIS EXISTS. For most of this project the corpus asserted "the ankle does not separate, the
knee does" without a container. On 2026-08-27 a cold audit computed a group-level ankle STANCE
contrast, found it disjoint, and the assertion was withdrawn as false. That withdrawal was itself
imprecise: it compared a stance-phase mean against an initial-contact value. This round measures
BOTH joints AT THE SAME INSTANT and deposits the result, so neither claim can be made again
without one.

STATUS: EXPLORATORY. No registration exists for this comparison. The endpoints are corpus-standard
and the cells are all previously simulated, but the contrast was chosen after seeing that the
ankle-stance result differed from the ankle-at-contact result. It must be confirmed on untouched
material before it can carry a confirmatory claim. NO SIMULATION IS RUN.

Every effect is reported against (a) the within-cell seed SD, the only non-confounded model noise
scale (FLOOR_CORRECTION_r436), and (b) a clinical single-measurement SEM back-derived from a
published MDC, averaged over the number of steps the endpoint actually uses.
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\IC_KNEE_VS_ANKLE_r439.json"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

CONTROL = ["R151C"]
WEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
SPAS = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]

# clinical single-measurement SEM, back-derived from MDC95 = 1.96 * sqrt(2) * SEM
KNEE_MDC, ANKLE_MDC = 7.62, 7.00     # see KNEE_MDC_BATCHNULL_r399 for provenance of both
SEM = {"knee": KNEE_MDC / (1.96 * np.sqrt(2)), "ankle": ANKLE_MDC / (1.96 * np.sqrt(2))}


def cell(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    cols, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return None
    on = grf > thr
    stance = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    return {"knee_ic": float(np.mean([kn[a] for a, _ in win])),
            "ankle_ic": float(np.mean([an[a] for a, _ in win])),
            "ankle_stance": float(np.mean(an[stance])),
            "n_cycles": len(win), "t_end": float(t[-1])}


def pool(fams):
    out = []
    for f in fams:
        for s in SEEDS:
            c = cell("%s_s%d" % (f, s))
            if c:
                c["family"] = f
                out.append(c)
    return out


C, W, SP = pool(CONTROL), pool(WEAK), pool(SPAS)
print("control %d   weakness %d   spastic %d" % (len(C), len(W), len(SP)))


def cohen_d(a, b):
    a, b = np.asarray(a), np.asarray(b)
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                 / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp) if sp else float("nan")


def seed_sd(key, fams):
    """within-cell seed SD: same lesion, same lineage, only the optimisation seed differs."""
    sds = []
    for f in fams:
        v = [cell("%s_s%d" % (f, s)) for s in SEEDS]
        v = [x[key] for x in v if x]
        if len(v) >= 4:
            sds.append(np.std(v, ddof=1))
    return float(np.mean(sds)) if sds else None


res = {"round": "IC_KNEE_VS_ANKLE_r439", "no_simulation_run": True,
       "status": "EXPLORATORY. No registration. The contrast was chosen after observing that a "
                 "stance-phase ankle result and an initial-contact ankle result disagreed. Must "
                 "be confirmed on untouched material before carrying a confirmatory claim.",
       "why": "the corpus asserted 'the ankle does not separate' for most of the project with no "
              "container; a cold audit then computed an ankle STANCE contrast, found it disjoint, "
              "and the assertion was withdrawn. Both statements were about different endpoints. "
              "This file measures both joints AT THE SAME INSTANT.",
       "groups": {}, "endpoints": {}}

for lab, grp in (("control", C), ("weakness_tib_ant", W), ("spastic_plantarflexor", SP)):
    res["groups"][lab] = {"n": len(grp), "families": sorted({c["family"] for c in grp})}

for key, joint in (("knee_ic", "knee"), ("ankle_ic", "ankle"), ("ankle_stance", "ankle")):
    w = [c[key] for c in W]
    s = [c[key] for c in SP]
    ctl = [c[key] for c in C]
    sd = seed_sd(key, WEAK + SPAS)
    sem1 = SEM[joint]
    ncyc = float(np.mean([c["n_cycles"] for c in W + SP]))
    sem_n = sem1 / np.sqrt(ncyc)
    diff = float(np.mean(s) - np.mean(w))
    res["endpoints"][key] = {
        "joint": joint,
        "control": {"n": len(ctl), "mean": float(np.mean(ctl)),
                    "range": [float(min(ctl)), float(max(ctl))]},
        "weakness": {"n": len(w), "mean": float(np.mean(w)),
                     "range": [float(min(w)), float(max(w))]},
        "spastic": {"n": len(s), "mean": float(np.mean(s)),
                    "range": [float(min(s)), float(max(s))]},
        "displacement_from_control": {"weakness": float(np.mean(w) - np.mean(ctl)),
                                      "spastic": float(np.mean(s) - np.mean(ctl))},
        "spastic_minus_weakness_deg": diff,
        "cohen_d_spastic_vs_weakness": cohen_d(s, w),
        "within_cell_seed_SD_deg": sd,
        "effect_in_seed_SDs": abs(diff) / sd if sd else None,
        "clinical_SEM_single_measurement_deg": sem1,
        "mean_cycles_averaged": ncyc,
        "clinical_SEM_after_averaging_deg": sem_n,
        "effect_in_clinical_SEMs": abs(diff) / sem_n}
    e = res["endpoints"][key]
    print()
    print("%-13s ctl %+8.3f   weak %+8.3f   spas %+8.3f" %
          (key, np.mean(ctl), np.mean(w), np.mean(s)))
    print("   displacement from control:  weak %+7.3f   spastic %+7.3f"
          % (e["displacement_from_control"]["weakness"],
             e["displacement_from_control"]["spastic"]))
    print("   spastic - weakness = %+7.3f deg   d = %+6.3f   %.1f seed SD   %.2f clinical SEM"
          % (diff, e["cohen_d_spastic_vs_weakness"], e["effect_in_seed_SDs"],
             e["effect_in_clinical_SEMs"]))

# --- are the two initial-contact endpoints independent? ---
K = np.array([c["knee_ic"] for c in W + SP])
A = np.array([c["ankle_ic"] for c in W + SP])
Y = np.array([0] * len(W) + [1] * len(SP))
kc = K - np.where(Y == 1, K[Y == 1].mean(), K[Y == 0].mean())
ac = A - np.where(Y == 1, A[Y == 1].mean(), A[Y == 0].mean())
res["independence"] = {
    "pearson_r_knee_ic_vs_ankle_ic": float(np.corrcoef(K, A)[0, 1]),
    "within_group_centred_r": float(np.corrcoef(kc, ac)[0, 1]),
    "reading": "a low raw correlation means the two endpoints are not redundant; the knee is not "
               "a mirror of the ankle."}


def loo(cols_):
    X = np.c_[K, A]
    ok = 0
    for i in range(len(Y)):
        tr = [j for j in range(len(Y)) if j != i]
        x, y = X[tr][:, cols_], Y[tr]
        mu1, mu0 = x[y == 1].mean(0), x[y == 0].mean(0)
        cov = np.cov(x.T, ddof=1) if len(cols_) > 1 else np.array([[x.var(ddof=1)]])
        ic = np.linalg.pinv(np.atleast_2d(cov))
        xi = X[i][cols_]
        ok += (1 if (xi - mu1) @ ic @ (xi - mu1) < (xi - mu0) @ ic @ (xi - mu0) else 0) == Y[i]
    return ok / len(Y)


res["classification_LOO"] = {"knee_ic_only": loo([0]), "ankle_ic_only": loo([1]),
                             "both": loo([0, 1]), "n": len(Y),
                             "note": "leave-one-out, nearest-centroid with pooled covariance; "
                                     "cells share optimisation lineages so effective n is below "
                                     "the cell count and no p-value is reported"}

k, a = res["endpoints"]["knee_ic"], res["endpoints"]["ankle_ic"]
res["READING"] = {
    "at_initial_contact_the_ankle_is_the_SAME_for_both_lesions":
        "weakness displaces the ankle %+.3f deg from control and spasticity %+.3f deg -- a "
        "difference of %.3f deg between the two lesions, d = %+.3f, and leave-one-out "
        "classification on that endpoint alone is %.1f%%, i.e. chance."
        % (a["displacement_from_control"]["weakness"], a["displacement_from_control"]["spastic"],
           abs(a["spastic_minus_weakness_deg"]), a["cohen_d_spastic_vs_weakness"],
           100 * res["classification_LOO"]["ankle_ic_only"]),
    "the_mechanical_reading": "both lesions plantarflex the foot at contact -- spasticity actively "
        "through plantarflexor overactivity, dorsiflexor weakness passively through foot drop. "
        "Different causes, the same angle.",
    "at_the_same_instant_the_knee_moves_in_OPPOSITE_directions":
        "weakness %+.3f deg, spasticity %+.3f deg from control; the two lesions differ by %.3f "
        "deg, d = %+.3f, and classify at %.1f%%."
        % (k["displacement_from_control"]["weakness"], k["displacement_from_control"]["spastic"],
           abs(k["spastic_minus_weakness_deg"]), k["cohen_d_spastic_vs_weakness"],
           100 * res["classification_LOO"]["knee_ic_only"]),
    "ratio_of_the_two_contrasts": abs(k["spastic_minus_weakness_deg"]
                                      / a["spastic_minus_weakness_deg"]),
    "the_ankle_DOES_separate_but_LATER": "over stance the ankle separates (%.3f deg, %.1f seed SD) "
        "because dorsiflexor weakness is a SWING problem that resolves once the foot is loaded, "
        "while spastic plantarflexors keep acting through stance. The instant matters."
        % (abs(res["endpoints"]["ankle_stance"]["spastic_minus_weakness_deg"]),
           res["endpoints"]["ankle_stance"]["effect_in_seed_SDs"]),
    "candidate_anatomical_account": "gastrocnemius spans knee AND ankle; soleus and tibialis "
        "anterior span the ankle only. The ankle therefore sums three muscles while the knee sees "
        "only the biarticular one. THIS IS AN INTERPRETATION, NOT A RESULT -- "
        "SPANNING_RESULT_r421 tested the spanning rule at single-muscle level and it failed at "
        "the hip, so joint-level anatomical inference is not reliable in this system.",
    "what_this_does_not_establish": [
        "exploratory: the contrast was chosen after seeing the stance/contact disagreement",
        "one model, six seeds from one control optimisation, cells share lineages",
        "no patients; no contracture arm; both lesions have severity ceilings",
        "the clinical SEM figures are back-derived from published MDCs in other cohorts and are "
        "extrapolations, as KNEE_MDC_BATCHNULL_r399 records"]}
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("independence: r(knee_ic, ankle_ic) = %+.4f"
      % res["independence"]["pearson_r_knee_ic_vs_ankle_ic"])
print("LOO classification: knee %.4f   ankle %.4f   both %.4f"
      % (res["classification_LOO"]["knee_ic_only"], res["classification_LOO"]["ankle_ic_only"],
         res["classification_LOO"]["both"]))
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
