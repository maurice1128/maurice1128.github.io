# -*- coding: utf-8 -*-
"""r389 -- RE-TEST EVERY SEPARATION CLAIM AGAINST THE *BATCH* NULL, NOT THE PERMUTATION FLOOR.

Independent re-implementation. Nothing is read from HARMONIC_r383.json / RECTIFIER_r385.json /
DOSELADDER_r371.json / KINPAIR_r379.json / COMPENSATION_r381.json; every number below is
re-measured from the .par.sto files. Conventions (run-directory selection, SETTLE, T1,
admissible-cycle window, drop-last-cycle, Gate-G, stance/swing masks, gap-based disjointness,
exhaustive permutation floor) are carried verbatim from doseladder_r371.py, with the BETA_abs
regression carried verbatim from rectifier_r385.py.

THE PROBLEM BEING TESTED
------------------------
Every separation claim in this line is "the two arms' 6 values are disjoint", quoted against an
exhaustive-permutation floor of 2/924 = 0.22%.  That floor assumes seeds are exchangeable across
arms.  If an optimisation family is a BATCH -- 6 seeds that cluster because they came out of the
same optimisation campaign -- then two arms can be disjoint for reasons that have nothing to do
with the lesion, and the operating false-positive rate is whatever two same-mechanism families
do to each other.  That rate is measured here, per endpoint, and every claim is re-tested
against it.

Two independent null cohorts:
  NULL-DF : the 6 dorsiflexor-weakness families, C(6,2) = 15 pairs.  Same lesion mechanism
            (a linear scaling of tib_ant_l max_isometric_force), no reflex lesion in either.
  NULL-PF : the 5 plantarflexor/other-weakness families, C(5,2) = 10 pairs.

Two geometries for the claims:
  PUBLISHED  : one ladder family's 6 seeds vs 6 DFweak "seed means", each pooled over SIX
               families.  Reproduced here only to show the published number is reproducible
               and to quantify how much the pooling shrinks the weak arm.
  LIKE-FOR-LIKE : ladder family (6 seeds) vs EACH DFweak family (6 seeds), 6 comparisons per
               rung.  This has the same geometry as the null, so it is the only hit rate that
               can legitimately be compared with it.
"""
import glob
import io
import itertools
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\BATCHNULL_r389.json"

SETTLE, T1, TAU_S, MIN_N = 1.0, 9.73, 0.020, 30      # verbatim r371 / r385

DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
PFWEAK = ["R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"]
LADDER = [("0.00625", "R289KV00625"), ("0.0125", "R289KV0125"),
          ("0.035", "R291KV0035"), ("0.070", "R291KV0070")]
WITHIN_CTL = "R151C"

# endpoint key -> (human name, corpus source)
ENDPOINTS = [
    ("BETA_abs", "|v| coefficient of act_soleus_l ~ b1*v + b2*|v| + c, whole cycle, tau=0.020 s",
     "paper/RECTIFIER_r385.json / scone/rectifier_r385.py"),
    ("A", "mean soleus_l.activation over stance samples of admissible cycles",
     "paper/DOSELADDER_r371.json / scone/doseladder_r371.py"),
    ("mean_ankle_stance_deg", "mean ankle_angle_l over stance samples, degrees",
     "paper/KINPAIR_r379.json / scone/kinpair_r379.py"),
    ("hip_swing_peak_L", "per-cycle max of hip_flexion_l over swing samples, degrees",
     "paper/COMPENSATION_r381.json / scone/compensation_r381.py"),
]
# negative-control endpoints (unlesioned right side); not corpus claims
NEG = [("BETA_abs_R", "|v| coefficient of act_soleus_r on the RIGHT ankle velocity, "
                      "left-leg-defined admissible-cycle samples"),
       ("BETA_abs_R_rgait", "same but gated on the RIGHT leg's own heel strikes")]

ALL_KEYS = [e[0] for e in ENDPOINTS] + [n[0] for n in NEG]


# ------------------------------------------------------------------ corpus access (r371 verbatim)
def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def tags_for(fams):
    out = []
    for f in fams:
        seen = set()
        for d in sorted(glob.glob(os.path.join(RES, f + "_s*"))):
            b = os.path.basename(d).split(".")[0]
            if b not in seen:
                seen.add(b)
                out.append(b)
    return out


def fit_abs(v, y):
    """OLS of y on [v, |v|, 1] -- rectifier_r385.fit verbatim, no SE (sec 9.2)."""
    X = np.column_stack([v, np.abs(v), np.ones(len(v))])
    try:
        beta, _, _, sv = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else float("inf")
    resid = y - X.dot(beta)
    ss = float(((y - y.mean()) ** 2).sum())
    return {"b1": float(beta[0]), "b2": float(beta[1]), "c": float(beta[2]),
            "r2": float(1.0 - (resid ** 2).sum() / ss) if ss > 0 else None,
            "cond": cond, "n": int(len(v))}


def cycles_for_side(t, cols, dat, side):
    grf, thr = S.grf_vertical(cols, dat, side)
    if grf is None:
        return None, None, None
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    return win, grf, thr


def measure(tag):
    """All five endpoints from ONE load of the run's .par.sto, one gating pass."""
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        rec["gate_G"] = False
        return rec
    rec["run_dir"] = os.path.basename(d)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        rec["gate_G"] = False
        return rec
    rec["sto"] = os.path.basename(stos[-1])
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        rec["gate_G"] = False
        return rec
    t = dat[:, 0]
    rec["t_end_s"] = float(t[-1])

    win, grf, thr = cycles_for_side(t, cols, dat, "l")
    if win is None:
        rec["error"] = "no left GRF"
        rec["gate_G"] = False
        return rec
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:                     # Gate G, r371 verbatim
        rec["gate_G"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec
    rec["gate_G"] = True

    on = grf > thr
    idx_all = np.concatenate([np.arange(a, b) for a, b in win])
    st = [np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()]
    idx_st = np.concatenate(st) if st else None
    lag = int(round(TAU_S / float(np.median(np.diff(t)))))
    rec["tau_samples"] = lag

    def lagged_velocity(angle):
        v = np.gradient(angle, t)
        return np.concatenate([np.zeros(lag), v[:-lag]]) if lag > 0 else v

    # ---- (a) BETA_abs, left (rectifier_r385 primary)
    ang_l = S.col(cols, dat, "ankle_angle_l")
    sol_l = S.muscle_signal(cols, dat, "soleus", "l", "activation")
    if ang_l is not None and sol_l is not None and len(idx_all) >= MIN_N:
        f = fit_abs(lagged_velocity(ang_l)[idx_all], sol_l[idx_all])
        if f:
            rec["BETA_abs"] = f["b2"]
            rec["BETA_abs_fit"] = f

    # ---- (4) BETA_abs, UNLESIONED RIGHT side, same left-defined sample set
    ang_r = S.col(cols, dat, "ankle_angle_r")
    sol_r = S.muscle_signal(cols, dat, "soleus", "r", "activation")
    if ang_r is not None and sol_r is not None and len(idx_all) >= MIN_N:
        f = fit_abs(lagged_velocity(ang_r)[idx_all], sol_r[idx_all])
        if f:
            rec["BETA_abs_R"] = f["b2"]
            rec["BETA_abs_R_fit"] = f
    # ---- and again with the RIGHT leg's own gait cycles, as a robustness check
    winr, grfr, thrr = cycles_for_side(t, cols, dat, "r")
    if winr and len(winr) >= 5 and ang_r is not None and sol_r is not None:
        ir = np.concatenate([np.arange(a, b) for a, b in winr])
        if len(ir) >= MIN_N:
            f = fit_abs(lagged_velocity(ang_r)[ir], sol_r[ir])
            if f:
                rec["BETA_abs_R_rgait"] = f["b2"]
    rec["n_cycles_right"] = len(winr) if winr else 0

    # ---- (b) A = mean soleus_l activation over stance (doseladder_r371 primary)
    if sol_l is not None and idx_st is not None:
        rec["A"] = float(np.mean(sol_l[idx_st]))

    # ---- (c) mean ankle_angle_l over stance, degrees (kinpair_r379)
    if ang_l is not None and idx_st is not None:
        rec["mean_ankle_stance_deg"] = float(np.mean(np.degrees(ang_l)[idx_st]))

    # ---- (d) hip_swing_peak_L (compensation_r381 primary)
    hip = S.col(cols, dat, "hip_flexion_l")
    if hip is not None:
        hip = np.degrees(hip)
        per = []
        for a, b in win:
            m = ~on[a:b]
            if m.any():
                per.append(float(np.max(hip[a:b][m])))
        rec["hip_swing_peak_L"] = float(np.mean(per)) if per else None
    return rec


# ------------------------------------------------------------------ statistics
def fam_values(cells, fam, key):
    """The family's Gate-G cell values for one endpoint, sorted. 6 seeds = 6 values."""
    out = []
    for tg in sorted(cells):
        if tg.split("_")[0] != fam:
            continue
        r = cells[tg]
        if not r.get("gate_G"):
            continue
        v = r.get(key)
        if v is not None and np.isfinite(v):
            out.append(float(v))
    return sorted(out)


def separated(a, b, min_n=4):
    """r371/r383 convention: gap-based disjointness, >= 4 usable values per arm."""
    if len(a) < min_n or len(b) < min_n:
        return None
    return bool(max(b[0] - a[-1], a[0] - b[-1]) > 0)


def gap(a, b):
    return max(b[0] - a[-1], a[0] - b[-1])


def perm_floor(a, b):
    """Exhaustive two-sided gap permutation floor -- doseladder_r371.floor verbatim."""
    allv = list(a) + list(b)
    n1 = len(a)
    obs = max(min(b) - max(a), min(a) - max(b))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        x = [allv[i] for i in comb]
        y = [allv[i] for i in range(len(allv)) if i not in comb]
        if max(min(y) - max(x), min(x) - max(y)) >= obs - 1e-12:
            cnt += 1
        tot += 1
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "%d/%d" % (cnt, tot),
            "p": cnt / float(tot)}


def binom_tail(k, n, p):
    """P(X >= k) for X ~ Bin(n, p). Exact -- how surprising the hit rate is UNDER THE BATCH NULL."""
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def cmp_pair(a, b):
    d = {"n_a": len(a), "n_b": len(b),
         "a_range": [a[0], a[-1]] if a else None, "b_range": [b[0], b[-1]] if b else None,
         "a_mean": float(np.mean(a)) if a else None, "b_mean": float(np.mean(b)) if b else None}
    s = separated(a, b)
    d["separated"] = s
    if s is None:
        d["VERDICT"] = "UNINFORMATIVE (<4 Gate-G values on one side)"
        return d
    d["gap"] = gap(a, b)
    d["direction"] = ("A HIGH" if a[0] > b[-1] else "A LOW") if s else None
    d["VERDICT"] = "SEPARATED" if s else "OVERLAP"
    if s:
        d["permutation_floor"] = perm_floor(a, b)
    return d


def null_cohort(cells, fams, label):
    out = {"label": label, "families": fams,
           "n_family_pairs": len(list(itertools.combinations(fams, 2))), "by_endpoint": {}}
    for key in ALL_KEYS:
        rows, n, k = [], 0, 0
        for A, B in itertools.combinations(fams, 2):
            va, vb = fam_values(cells, A, key), fam_values(cells, B, key)
            s = separated(va, vb)
            if s is None:
                rows.append({"pair": [A, B], "verdict": "UNINFORMATIVE",
                             "n_a": len(va), "n_b": len(vb)})
                continue
            n += 1
            k += int(s)
            rows.append({"pair": [A, B], "separated": s, "gap": gap(va, vb),
                         "a_range": [va[0], va[-1]], "b_range": [vb[0], vb[-1]],
                         "direction": (("%s HIGH" % A) if s and va[0] > vb[-1]
                                       else ("%s HIGH" % B) if s else None)})
        out["by_endpoint"][key] = {
            "n_pairs_tested": n, "n_separated": k,
            "BATCH_FALSE_POSITIVE_RATE": (k / float(n)) if n else None,
            "excess_over_permutation_floor_2_over_924":
                ((k / float(n)) / (2.0 / 924.0)) if n else None,
            "pairs": rows}
    return out


def main():
    cells = {}
    fams = DFWEAK + PFWEAK + [f for _, f in LADDER] + [WITHIN_CTL]
    tags = tags_for(fams)
    print("measuring %d cells across %d families" % (len(tags), len(fams)))
    for i, tg in enumerate(tags):
        cells[tg] = measure(tg)
        r = cells[tg]
        print("  [%2d/%d] %-20s gate_G=%-5s cyc=%-3s BETA_abs=%s"
              % (i + 1, len(tags), tg, r.get("gate_G"), r.get("n_cycles_in_window"),
                 ("%+.6f" % r["BETA_abs"]) if r.get("BETA_abs") is not None else "-"))

    res = {
        "what": "re-test of every separation claim in the dynamics line against the BATCH null "
                "(family-vs-family false-positive rate) instead of the 2/924 exhaustive "
                "permutation floor",
        "independent_of": ["paper/HARMONIC_r383.json", "paper/RECTIFIER_r385.json",
                           "paper/DOSELADDER_r371.json", "paper/KINPAIR_r379.json",
                           "paper/COMPENSATION_r381.json"],
        "conventions_carried_from": "scone/doseladder_r371.py (run selection, SETTLE=1.0, "
                                    "T1=9.73, drop-last-cycle, Gate-G >=5 cycles & t_end>=T1, "
                                    "GRF-defined stance, gap disjointness, exhaustive floor); "
                                    "scone/rectifier_r385.py (BETA_abs regression, tau=0.020 s, "
                                    "MIN_N=30)",
        "disjointness_convention": "arms separate iff max(min(B)-max(A), min(A)-max(B)) > 0, "
                                   "both arms needing >= 4 Gate-G values",
        "endpoints": {k: {"definition": d, "corpus_source": s} for k, d, s in ENDPOINTS},
        "negative_control_endpoints": {k: d for k, d in NEG},
        "cells": cells,
    }

    # ------------------------------------------------------------ gate ledger
    ledger = {}
    for f in fams:
        tg = [t for t in tags if t.split("_")[0] == f]
        ok = [t for t in tg if cells[t].get("gate_G")]
        ledger[f] = {"n_cells": len(tg), "n_gate_G": len(ok),
                     "guards": {t: cells[t].get("guard") or cells[t].get("error")
                                for t in tg if not cells[t].get("gate_G")}}
    res["GATE_LEDGER"] = ledger

    # ------------------------------------------------------------ STEP 1: the two nulls
    nd = null_cohort(cells, DFWEAK, "NULL-DF: dorsiflexor-weakness family vs family")
    npf = null_cohort(cells, PFWEAK, "NULL-PF: plantarflexor/other-weakness family vs family")
    res["STEP1_BATCH_NULL"] = {
        "NULL_DF": nd, "NULL_PF": npf,
        "quoted_permutation_floor": 2.0 / 924.0,
        "agreement": {k: {"NULL_DF": nd["by_endpoint"][k]["BATCH_FALSE_POSITIVE_RATE"],
                          "NULL_PF": npf["by_endpoint"][k]["BATCH_FALSE_POSITIVE_RATE"]}
                      for k in ALL_KEYS},
    }

    # ------------------------------------------------------------ STEP 3: like-for-like claims
    lfl = {}
    for kv, fam in LADDER:
        lfl[kv] = {"family": fam, "n_gate_G": ledger[fam]["n_gate_G"], "by_endpoint": {}}
        for key in ALL_KEYS:
            va = fam_values(cells, fam, key)
            rows, n, k = [], 0, 0
            for D in DFWEAK:
                vb = fam_values(cells, D, key)
                s = separated(va, vb)
                if s is None:
                    rows.append({"vs": D, "verdict": "UNINFORMATIVE"})
                    continue
                n += 1
                k += int(s)
                rows.append({"vs": D, "separated": s, "gap": gap(va, vb),
                             "direction": ("SPASTIC HIGH" if s and va[0] > vb[-1]
                                           else "SPASTIC LOW" if s else None),
                             "ladder_range": [va[0], va[-1]] if va else None,
                             "weak_range": [vb[0], vb[-1]] if vb else None})
            nullrate = nd["by_endpoint"][key]["BATCH_FALSE_POSITIVE_RATE"]
            lfl[kv]["by_endpoint"][key] = {
                "n_tested": n, "n_separated": k,
                "hit_rate": (k / float(n)) if n else None,
                "batch_null_rate_NULL_DF": nullrate,
                "p_binomial_vs_batch_null": (binom_tail(k, n, nullrate)
                                             if n and nullrate is not None else None),
                "comparisons": rows}
    res["STEP3_LIKE_FOR_LIKE"] = {
        "what": "each ladder family's 6 seeds vs EACH dorsiflexor-weak family's 6 seeds, "
                "6 comparisons per rung per endpoint; same geometry as the batch null",
        "by_rung": lfl}

    # ------------------------------------------------------------ published geometry, reproduced
    def pooled_seed_means(famlist, key):
        acc = {}
        for tg in sorted(cells):
            if tg.split("_")[0] not in famlist:
                continue
            r = cells[tg]
            if not r.get("gate_G"):
                continue
            v = r.get(key)
            if v is None or not np.isfinite(v):
                continue
            acc.setdefault(tg.split("_")[-1], []).append(float(v))
        return sorted(float(np.mean(v)) for v in acc.values())

    pub = {}
    for kv, fam in LADDER:
        pub[kv] = {"family": fam, "by_endpoint": {}}
        for key in ALL_KEYS:
            va = fam_values(cells, fam, key)
            vb = pooled_seed_means(DFWEAK, key)
            c = cmp_pair(va, vb)
            singles = [fam_values(cells, D, key) for D in DFWEAK]
            singles = [x for x in singles if len(x) >= 4]
            c["weak_arm_spread_pooled"] = (vb[-1] - vb[0]) if len(vb) >= 2 else None
            c["weak_arm_spread_mean_single_family"] = (
                float(np.mean([x[-1] - x[0] for x in singles])) if singles else None)
            c["pooling_shrink_factor"] = (
                (c["weak_arm_spread_mean_single_family"] / c["weak_arm_spread_pooled"])
                if c["weak_arm_spread_pooled"] else None)
            pub[kv]["by_endpoint"][key] = c
    res["PUBLISHED_GEOMETRY_REPRODUCED"] = {
        "what": "the corpus geometry: ladder family's 6 seeds vs 6 DFweak SEED MEANS each "
                "pooled over SIX families. Reproduced to confirm the published separations and "
                "to quantify how much pooling shrinks the weak arm's range.",
        "by_rung": pub}

    # ------------------------------------------------------------ STEP 4: negative control
    negcmp = {}
    for key in ("BETA_abs", "BETA_abs_R", "BETA_abs_R_rgait"):
        rung = {}
        for kv, fam in LADDER:
            e = lfl[kv]["by_endpoint"][key]
            rung[kv] = {"n_tested": e["n_tested"], "n_separated": e["n_separated"],
                        "hit_rate": e["hit_rate"]}
        tot_n = sum(rung[kv]["n_tested"] for kv, _ in LADDER)
        tot_k = sum(rung[kv]["n_separated"] for kv, _ in LADDER)
        negcmp[key] = {"by_rung": rung, "n_tested_all_rungs": tot_n,
                       "n_separated_all_rungs": tot_k,
                       "hit_rate_all_rungs": (tot_k / float(tot_n)) if tot_n else None,
                       "batch_null_rate_NULL_DF":
                           nd["by_endpoint"][key]["BATCH_FALSE_POSITIVE_RATE"],
                       "batch_null_rate_NULL_PF":
                           npf["by_endpoint"][key]["BATCH_FALSE_POSITIVE_RATE"]}
    res["STEP4_NEGATIVE_CONTROL_SIDE"] = {
        "what": "the spastic reflex is LEFT-ONLY. BETA_abs_R is the identical coefficient on the "
                "unlesioned right soleus and right ankle velocity. If the right side separates "
                "from the DFweak families at a similar rate to the left, the left-side result "
                "is a batch artefact, not a lesion signature.",
        "by_endpoint": negcmp}

    # ------------------------------------------------------------ STEP 5: R151C within-scenario
    c151 = fam_values(cells, WITHIN_CTL, "BETA_abs")
    w5 = {"n_gate_G": len(c151), "R151C_values": c151,
          "R151C_range": [c151[0], c151[-1]] if c151 else None,
          "R151C_mean": float(np.mean(c151)) if c151 else None,
          "vs_ladder_rungs": {}, "vs_dfweak_families": {}, "vs_pfweak_families": {}}
    for kv, fam in LADDER:
        w5["vs_ladder_rungs"][kv] = cmp_pair(c151, fam_values(cells, fam, "BETA_abs"))
        w5["vs_ladder_rungs"][kv]["note_A_is"] = "R151C"
        w5["vs_ladder_rungs"][kv]["note_B_is"] = fam
    for D in DFWEAK:
        w5["vs_dfweak_families"][D] = cmp_pair(c151, fam_values(cells, D, "BETA_abs"))
    for D in PFWEAK:
        w5["vs_pfweak_families"][D] = cmp_pair(c151, fam_values(cells, D, "BETA_abs"))
    nsep_lad = sum(1 for kv, _ in LADDER if w5["vs_ladder_rungs"][kv].get("separated"))
    nsep_dfw = sum(1 for D in DFWEAK if w5["vs_dfweak_families"][D].get("separated"))
    w5["n_ladder_rungs_separated"] = nsep_lad
    w5["n_dfweak_families_separated"] = nsep_dfw
    w5["R151C_vs_R151W_same_batch"] = cmp_pair(c151, fam_values(cells, "R151W", "BETA_abs"))
    res["STEP5_WITHIN_SCENARIO_CONTROL_R151C"] = {
        "what": "R151C is an unlesioned control at min_velocity 1.0 whose model file differs "
                "from R151W in exactly one line (tib_ant_l max_isometric_force 1759 vs 1407.2), "
                "6 seeds, SAME optimisation batch as R151W. It has NO reflex lesion and NO "
                "dorsiflexor lesion. Where BETA_abs puts it decides whether BETA_abs responds "
                "to the reflex lesion or to the dorsiflexor lesion (or to neither).",
        "result": w5}

    # ------------------------------------------------------------ VERDICTS
    verdicts = {}
    for key, defn, src in ENDPOINTS:
        ndr = nd["by_endpoint"][key]["BATCH_FALSE_POSITIVE_RATE"]
        npr = npf["by_endpoint"][key]["BATCH_FALSE_POSITIVE_RATE"]
        rows = {}
        tot_n = tot_k = 0
        for kv, fam in LADDER:
            e = lfl[kv]["by_endpoint"][key]
            rows[kv] = {"family": fam, "n_tested": e["n_tested"],
                        "n_separated": e["n_separated"], "hit_rate": e["hit_rate"],
                        "p_vs_batch_null": e["p_binomial_vs_batch_null"]}
            if lfl[kv]["n_gate_G"] >= 4:
                tot_n += e["n_tested"]
                tot_k += e["n_separated"]
        hr = (tot_k / float(tot_n)) if tot_n else None
        p_all = binom_tail(tot_k, tot_n, ndr) if tot_n and ndr is not None else None
        pubsep = [kv for kv, _ in LADDER
                  if pub[kv]["by_endpoint"][key].get("separated")]
        if hr is None:
            v = "INDETERMINATE"
            why = "no rung has 4 Gate-G seeds for this endpoint"
        elif ndr is not None and hr <= ndr + 1e-12:
            v = "DOES NOT SURVIVE"
            why = ("like-for-like hit rate %.1f%% is at or below the batch false-positive rate "
                   "%.1f%% measured between two lesion-free-of-reflex families of the SAME "
                   "mechanism. The claim's separations are indistinguishable from what two "
                   "arbitrary optimisation batches do to each other." % (100 * hr, 100 * ndr))
        elif p_all is not None and p_all < 0.05 and hr >= 2 * ndr:
            v = "SURVIVES THE BATCH NULL"
            why = ("like-for-like hit rate %.1f%% vs batch null %.1f%%, binomial "
                   "P(>= %d of %d | null) = %.4f" % (100 * hr, 100 * ndr, tot_k, tot_n, p_all))
        else:
            v = "INDETERMINATE"
            why = ("like-for-like hit rate %.1f%% exceeds the batch null %.1f%% but not "
                   "decisively: binomial P(>= %d of %d | null) = %s. The excess is an effect "
                   "size sitting on a large batch effect, not a clean detection."
                   % (100 * hr, 100 * ndr, tot_k, tot_n,
                      ("%.4f" % p_all) if p_all is not None else "n/a"))
        verdicts[key] = {
            "endpoint": defn, "corpus_source": src,
            "VERDICT": v, "why": why,
            "like_for_like_hit_rate": hr,
            "like_for_like_n_separated": tot_k, "like_for_like_n_tested": tot_n,
            "batch_null_rate_NULL_DF": ndr, "batch_null_rate_NULL_PF": npr,
            "quoted_permutation_floor": 2.0 / 924.0,
            "null_over_quoted_floor": (ndr / (2.0 / 924.0)) if ndr is not None else None,
            "by_rung": rows,
            "published_geometry_rungs_that_separated": pubsep,
        }
    res["VERDICTS"] = verdicts

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False, default=str))

    # ------------------------------------------------------------ console
    print()
    print("=" * 94)
    print("STEP 1  BATCH NULL  (family vs family, same mechanism, no reflex lesion in either)")
    print("%-24s %-22s %-22s" % ("endpoint", "NULL-DF (15 pairs)", "NULL-PF (10 pairs)"))
    for key in ALL_KEYS:
        a, b = nd["by_endpoint"][key], npf["by_endpoint"][key]
        print("%-24s %2d/%-2d = %6.1f%%        %2d/%-2d = %6.1f%%"
              % (key, a["n_separated"], a["n_pairs_tested"],
                 100 * (a["BATCH_FALSE_POSITIVE_RATE"] or 0),
                 b["n_separated"], b["n_pairs_tested"],
                 100 * (b["BATCH_FALSE_POSITIVE_RATE"] or 0)))
    print("  quoted exhaustive permutation floor = 2/924 = 0.22%")
    print()
    print("=" * 94)
    print("STEP 3  LIKE-FOR-LIKE  (ladder family vs each DFweak family, 6 per rung)")
    for key in ALL_KEYS:
        print("  %s" % key)
        for kv, fam in LADDER:
            e = lfl[kv]["by_endpoint"][key]
            print("    KV %-8s %-12s %d/%d separated%s"
                  % (kv, fam, e["n_separated"], e["n_tested"],
                     ("   p_vs_null=%.4f" % e["p_binomial_vs_batch_null"])
                     if e["p_binomial_vs_batch_null"] is not None else "   [UNINFORMATIVE]"))
    print()
    print("=" * 94)
    print("STEP 4  NEGATIVE-CONTROL SIDE  (left lesioned vs right unlesioned)")
    for key in ("BETA_abs", "BETA_abs_R", "BETA_abs_R_rgait"):
        e = negcmp[key]
        print("  %-20s all rungs %2d/%-2d = %5.1f%%   batch null DF %5.1f%%  PF %5.1f%%"
              % (key, e["n_separated_all_rungs"], e["n_tested_all_rungs"],
                 100 * (e["hit_rate_all_rungs"] or 0),
                 100 * (e["batch_null_rate_NULL_DF"] or 0),
                 100 * (e["batch_null_rate_NULL_PF"] or 0)))
    print()
    print("=" * 94)
    print("STEP 5  R151C within-scenario control, BETA_abs")
    print("  R151C n=%d  range [%s]" % (len(c151), ", ".join("%+.6f" % x for x in c151)))
    for kv, fam in LADDER:
        d = w5["vs_ladder_rungs"][kv]
        print("    vs KV %-8s %-12s %s" % (kv, fam, d["VERDICT"]))
    for D in DFWEAK:
        d = w5["vs_dfweak_families"][D]
        print("    vs %-12s %s" % (D, d["VERDICT"]))
    print()
    print("=" * 94)
    print("VERDICTS")
    for key, _, _ in ENDPOINTS:
        v = verdicts[key]
        print("  %-24s %-24s hit %s/%s = %s   null %s"
              % (key, v["VERDICT"], v["like_for_like_n_separated"], v["like_for_like_n_tested"],
                 ("%.1f%%" % (100 * v["like_for_like_hit_rate"]))
                 if v["like_for_like_hit_rate"] is not None else "n/a",
                 ("%.1f%%" % (100 * v["batch_null_rate_NULL_DF"]))
                 if v["batch_null_rate_NULL_DF"] is not None else "n/a"))
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
