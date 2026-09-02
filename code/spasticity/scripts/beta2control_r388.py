# -*- coding: utf-8 -*-
"""PREREG_rectifier_r382.md (8c8731ad...) -- the uncancellable |v| component.

max(0,v) = v/2 + |v|/2. Re-optimisation adjusts gains, which are linear, so it can cancel the
v/2 half and cannot cancel the |v|/2 half. r366 regressed on max(0,v) as ONE regressor and
pooled the two halves; this splits them.

PRIMARY: BETA_abs = the |v| coefficient of
    act_soleus_l(t) = b1*v(t-tau) + b2*|v(t-tau)| + c
fitted over ALL samples of the admissible cycles (whole cycle, sec 2 -- no phase restriction).
v is ankle dorsiflexion angular velocity in rad/s, positive = dorsiflexion, tau = 0.020 s.

Sec 9.3 requires the design-matrix condition number per cell, because v and |v| are correlated
over a gait cycle and the split is not unique in the presence of noise.
Sec 9.2 forbids reporting any SE/CI/p from the regression; inference is the sec 7 permutation.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\BETA2CONTROL_r388.json"
PREREG_SHA = "2dcddafda33d25749729050f6c9abb082ce79b98f3749baefb13e56ad935394e"
SETTLE, T1, TAU_S, MIN_N = 1.0, 9.73, 0.020, 30

LADDER = [(0.00625, "R289KV00625"), (0.0125, "R289KV0125"),
          (0.035, "R291KV0035"), (0.070, "R291KV0070")]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CONTROL = ["R151C"]           # r387 sec 2: WITHIN-SCENARIO matched control, 6 seeds
MUS = ["soleus", "gastroc", "tib_ant"]


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


def fit(v, av, y):
    """OLS of y on [v, |v|, 1]. Returns b1, b2, r2, cond, n. No SE -- sec 9.2."""
    X = np.column_stack([v, av, np.ones(len(v))])
    try:
        beta, _, _, sv = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else float("inf")
    resid = y - X.dot(beta)
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = float(1.0 - (resid ** 2).sum() / ss) if ss > 0 else None
    return {"b1": float(beta[0]), "b2": float(beta[1]), "c": float(beta[2]),
            "r2": r2, "cond": cond, "n": int(len(v))}


def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        return rec
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        return rec
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        return rec
    t = dat[:, 0]
    rec["t_end_s"] = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["gate_G"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec
    rec["gate_G"] = True

    ang = S.col(cols, dat, "ankle_angle_l")
    if ang is None:
        rec["error"] = "no ankle_angle_l"
        return rec
    v_all = np.gradient(ang, t)                       # rad/s, + = dorsiflexion
    lag = int(round(TAU_S / float(np.median(np.diff(t)))))
    rec["tau_samples"] = lag
    vlag = np.concatenate([np.zeros(lag), v_all[:-lag]]) if lag > 0 else v_all

    on = grf > thr
    idx_all = np.concatenate([np.arange(a, b) for a, b in win])
    idx_st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    sw = [np.arange(a, b)[~on[a:b]] for a, b in win if (~on[a:b]).any()]
    idx_sw = np.concatenate(sw) if sw else None

    if len(idx_all) < MIN_N:
        rec["gate_G"] = False
        rec["guard"] = "only %d pooled samples, need %d (sec 8)" % (len(idx_all), MIN_N)
        return rec

    out = {}
    for m in MUS:
        a = S.muscle_signal(cols, dat, m, "l", "activation")
        if a is None:
            continue
        for phase, idx in (("cycle", idx_all), ("stance", idx_st), ("swing", idx_sw)):
            if idx is None or len(idx) < MIN_N:
                continue
            f = fit(vlag[idx], np.abs(vlag[idx]), a[idx])
            if f is None:
                continue
            den = abs(f["b1"]) + abs(f["b2"])
            f["ratio_abs"] = (f["b2"] / den) if den > 0 else None
            out["%s_%s" % (m, phase)] = f
    rec["fits"] = out
    # PRIMARY, sec 2
    p = out.get("soleus_cycle")
    rec["BETA_abs"] = p["b2"] if p else None
    rec["RATIO_abs"] = p["ratio_abs"] if p else None
    rec["cond"] = p["cond"] if p else None
    return rec


def seed_means(tags, cells, getter):
    out = {}
    for tg in tags:
        r = cells[tg]
        if not r.get("gate_G"):
            continue
        v = getter(r)
        if v is None:
            continue
        out.setdefault(tg.split("_")[-1], []).append(v)
    return {k: float(np.mean(v)) for k, v in out.items()}


def floor(a, b):
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
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot,
            "convention": "two-sided, gap-based (r371 convention; counts the complement)"}


def cmp_arms(s, w):
    s, w = sorted(s), sorted(w)
    gap = max(w[0] - s[-1], s[0] - w[-1])
    d = {"n_spastic": len(s), "n_weak": len(w), "spastic_range": [s[0], s[-1]],
         "weak_range": [w[0], w[-1]], "spastic_mean": float(np.mean(s)),
         "weak_mean": float(np.mean(w)), "gap": gap, "separated": bool(gap > 0)}
    if gap > 0:
        d["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "SPASTIC LOW"
        d["permutation"] = floor(s, w)
        d["VERDICT"] = "SEPARATED"
    else:
        d["VERDICT"] = "OVERLAP"
    return d


def main():
    res = {"registration": "PREREG_beta2control_r387.md", "registration_sha256": PREREG_SHA,
           "derivation": "max(0,v) = v/2 + |v|/2; gains are linear so they cancel v/2 and "
                         "cannot cancel |v|/2",
           "primary": "BETA_abs = |v| coefficient of act_soleus_l ~ b1*v + b2*|v| + c, "
                      "whole cycle, tau = 0.020 s",
           "predictions": {"P1": "BETA_abs > 0 in every spastic rung; DF-weak indistinguishable "
                                 "from control",
                           "P2": "arm-mean BETA_abs non-decreasing in KV over 0.00625/0.0125/0.035",
                           "P3": "BETA_abs separates spastic from DF-weak AT KV 0.00625 AND 0.0125, "
                                 "where every amplitude endpoint has overlapped"},
           "inference_note": "sec 9.2: no SE/CI/p from the regression; inference is the sec 7 "
                             "seed-level permutation only",
           "cells": {}}

    wt = tags_for(DFWEAK)
    for tg in wt:
        res["cells"][tg] = measure(tg)
    w_sm = seed_means(wt, res["cells"], lambda r: r.get("BETA_abs"))
    w = sorted(w_sm.values())
    print("DFWEAK  n=%d  BETA_abs [%+.6f, %+.6f]  mean %+.6f" % (len(w), w[0], w[-1], np.mean(w)))

    ct = tags_for(CONTROL)
    for tg in ct:
        res["cells"][tg] = measure(tg)
    c_sm = seed_means(ct, res["cells"], lambda r: r.get("BETA_abs"))
    c = sorted(c_sm.values())
    print("CONTROL n=%d  BETA_abs [%+.6f, %+.6f]  mean %+.6f   [R151C WITHIN-SCENARIO, r387 sec 2]"
          % (len(c), c[0], c[-1], np.mean(c)))
    res["dfweak"] = {"seed_means": w_sm, "range": [w[0], w[-1]], "mean": float(np.mean(w))}
    res["control"] = {"seed_means": c_sm, "range": [c[0], c[-1]], "mean": float(np.mean(c)),
                      "between_scenario": False}
    print()

    rungs = {}
    for kv, fam in LADDER:
        tg = tags_for([fam])
        for x in tg:
            if x not in res["cells"]:
                res["cells"][x] = measure(x)
        n_ok = sum(1 for x in tg if res["cells"][x].get("gate_G"))
        e = {"family": fam, "n_gate_G": n_ok}
        if n_ok < 4:
            e["VERDICT"] = "UNINFORMATIVE"
            e["why"] = "sec 8: fewer than 4 Gate-G seeds (%d); reported, not dropped" % n_ok
            print("  KV %-8s UNINFORMATIVE (%d Gate-G)" % (kv, n_ok))
        else:
            sm = seed_means(tg, res["cells"], lambda r: r.get("BETA_abs"))
            s = sorted(sm.values())
            e["seed_means"] = sm
            e["vs_dfweak"] = cmp_arms(s, w)
            e["vs_control_R151C_WITHIN_SCENARIO"] = cmp_arms(s, c)
            conds = [res["cells"][x]["cond"] for x in tg
                     if res["cells"][x].get("gate_G") and res["cells"][x].get("cond")]
            e["design_cond_number"] = {"min": float(min(conds)), "max": float(max(conds)),
                                       "note": "sec 9.3: large values mean the b1/b2 split is unstable"}
            ratios = seed_means(tg, res["cells"], lambda r: r.get("RATIO_abs"))
            e["RATIO_abs_seed_means"] = ratios
            e["RATIO_abs_vs_dfweak"] = cmp_arms(
                sorted(ratios.values()),
                sorted(seed_means(wt, res["cells"], lambda r: r.get("RATIO_abs")).values()))
            v = e["vs_dfweak"]
            print("  KV %-8s n=%d  S [%+.6f, %+.6f]  W [%+.6f, %+.6f]  gap %+.6f  %s%s  cond<=%.0f"
                  % (kv, len(s), s[0], s[-1], w[0], w[-1], v["gap"], v["VERDICT"],
                     "  " + v["direction"] if v.get("direction") else "",
                     e["design_cond_number"]["max"]))
        rungs[str(kv)] = e
    res["rungs"] = rungs

    # secondaries, sec 6
    sec = {}
    for key in ("gastroc_cycle", "tib_ant_cycle", "soleus_stance", "soleus_swing"):
        pair = {}
        for nm, tags in (("SPASTIC_KV0.035", tags_for(["R291KV0035"])), ("DFWEAK", wt),
                         ("CONTROL", ct)):
            sm = seed_means(tags, res["cells"],
                            lambda r, k=key: (r.get("fits", {}).get(k) or {}).get("b2"))
            if sm:
                vv = sorted(sm.values())
                pair[nm] = {"n": len(vv), "range": [vv[0], vv[-1]], "mean": float(np.mean(vv))}
        sec[key + "_b2"] = pair
    res["SECONDARY_never_promoted"] = sec

    # prediction assessment
    got = [(kv, rungs[str(kv)]) for kv, _ in LADDER
           if rungs[str(kv)].get("VERDICT") != "UNINFORMATIVE"]
    means = [(kv, float(np.mean(list(e["seed_means"].values())))) for kv, e in got]
    p1 = all(m > 0 for _, m in means)
    p2 = all(means[i][1] <= means[i + 1][1] + 1e-15 for i in range(len(means) - 1))
    low = [kv for kv, e in got if kv <= 0.0125 and e["vs_dfweak"]["separated"]]
    res["PREDICTION_ASSESSMENT"] = {
        "P1_all_positive": {"holds": bool(p1), "rung_means": {str(a): b for a, b in means}},
        "P2_monotonic": {"holds": bool(p2)},
        "P3_separates_at_low_rungs": {"holds": bool(low), "rungs_that_separated": low,
                                      "note": "P3 is the risky prediction; failure means even "
                                              "the uncancellable component is below the noise "
                                              "floor of this model (sec 3)"}}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    pa = res["PREDICTION_ASSESSMENT"]
    print()
    print("P1 all positive        : %s   %s" % (pa["P1_all_positive"]["holds"],
                                                pa["P1_all_positive"]["rung_means"]))
    print("P2 monotonic in KV     : %s" % pa["P2_monotonic"]["holds"])
    print("P3 separates at <=0.0125: %s  %s" % (pa["P3_separates_at_low_rungs"]["holds"],
                                                pa["P3_separates_at_low_rungs"]["rungs_that_separated"]))
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
