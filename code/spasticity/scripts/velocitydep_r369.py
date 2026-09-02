# -*- coding: utf-8 -*-
"""PREREG_velocitydep_r368.md (8cf88c12...) -- SLOPE_v, section 3.

A      = mean soleus_l.activation over stance samples of the admissible cycles.
SLOPE_v = OLS slope of A on min_velocity in {0.80, 1.05, 1.30}, within one seed and one
          condition. A seed contributes only if ALL THREE of its speed cells pass Gate G
          (section 3); no partial imputation.

Primary comparison S vs W. C is reported as the unlesioned speed response (section 2), and
under section 6 it may never become the primary.

Conventions carried unaltered: rd() >= 91-line history.txt; sorted(*.par.sto)[-1];
SETTLE 1.00, T1 9.73, >= 5 cycles in window, last cycle in window dropped;
stance = leg0_l.grf_norm_y > 0.05, the threshold sto_utils.heel_strikes uses.

Section 8.3 forbids reporting any SE/CI/p from the three-point fit. Inference is the
seed-level permutation of section 5 only, whose floor is 1/924 and can be no smaller.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\VELOCITYDEP_r369.json"
PREREG_SHA = "8cf88c12a7f2b395f50a8e08d6e7749af6a41b0464a2715346f8b73a09b8f44d"
SETTLE, T1 = 1.0, 9.73
SPEEDS = [("080", 0.80), ("105", 1.05), ("130", 1.30)]
SEEDS = list(range(101, 107))
CONDS = ["C", "S", "W"]


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


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
    rec["dir"] = os.path.basename(d)
    rec["sto"] = os.path.basename(stos[-1])
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

    on = grf > thr
    idx = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    rec["n_stance_samples"] = int(len(idx))

    def act(m):
        v = S.muscle_signal(cols, dat, m, "l", "activation")
        return float(np.mean(v[idx])) if v is not None else None

    rec["A_soleus"] = act("soleus")                    # PRIMARY input, section 3
    tq = S.col(cols, dat, "ankle_l.torque")
    ang = S.col(cols, dat, "ankle_angle_l")
    sec = {"A_gastroc": act("gastroc"), "A_tib_ant": act("tib_ant"),
           "ankle_torque_stance": float(np.mean(tq[idx])) if tq is not None else None}
    if ang is not None:
        a_deg = np.degrees(ang)
        sec["ankle_rom_deg"] = float(np.mean([np.ptp(a_deg[a:b]) for a, b in win]))
        sec["peak_stance_dorsiflexion_deg"] = float(np.max(a_deg[idx]))
    rec["secondary"] = sec
    return rec


def ols3(xs, ys):
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    vx = x - x.mean()
    return float((vx * (y - y.mean())).sum() / (vx * vx).sum())


def perm_floor(sp, wk):
    allv = list(sp) + list(wk)
    n1 = len(sp)
    obs = max(min(wk) - max(sp), min(sp) - max(wk))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        a = [allv[i] for i in comb]
        b = [allv[i] for i in range(len(allv)) if i not in comb]
        g = max(min(b) - max(a), min(a) - max(b))
        tot += 1
        if g >= obs - 1e-12:
            cnt += 1
    return {"method": "exhaustive over C(%d,%d)" % (len(allv), n1), "n_total": tot,
            "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot, "fraction": cnt / float(tot)}


def main():
    res = {"registration": "PREREG_velocitydep_r368.md", "registration_sha256": PREREG_SHA,
           "design": "R203 3 speeds x {C control, S spastic KV=0.050 soleus/gastroc L, "
                     "W dorsiflexor weakness tib_ant_l max_isometric_force 1759->1569.0 "
                     "(x0.892)}, 6 seeds",
           "endpoint": "SLOPE_v = OLS slope of stance-mean soleus_l.activation on "
                       "min_velocity in {0.80, 1.05, 1.30}, within seed and condition",
           "registered_prediction": "SPASTIC HIGH, DORSIFLEXOR-WEAK LOW; and W ~ C",
           "inference_note": "section 8.3: no SE/CI/p from the three-point fit; inference is "
                             "the seed-level permutation of section 5, floor 1/924",
           "cells": {}, "slopes": {}}

    for cond in CONDS:
        res["slopes"][cond] = {}
        for sd in SEEDS:
            trip, ok = [], True
            for vs, vv in SPEEDS:
                tag = "R203V%s%s_s%d" % (vs, cond, sd)
                r = measure(tag)
                res["cells"][tag] = r
                if not r.get("gate_G") or r.get("A_soleus") is None:
                    ok = False
                else:
                    trip.append((vv, r["A_soleus"], r))
                print("  %-16s %s" % (tag, "A=%.6f t_end=%.2f cyc=%d"
                                      % (r["A_soleus"], r["t_end_s"], r["n_cycles_in_window"])
                                      if r.get("gate_G") and r.get("A_soleus") is not None
                                      else r.get("guard", r.get("error", "?"))))
            if ok and len(trip) == 3:
                sl = ols3([a for a, _, _ in trip], [b for _, b, _ in trip])
                entry = {"SLOPE_v": sl,
                         "A_by_speed": {str(a): b for a, b, _ in trip}}
                for key in ("A_gastroc", "A_tib_ant", "ankle_torque_stance",
                            "ankle_rom_deg", "peak_stance_dorsiflexion_deg"):
                    vals = [(a, rr["secondary"].get(key)) for a, _, rr in trip]
                    if all(v is not None for _, v in vals):
                        entry["SLOPE_" + key] = ols3([a for a, _ in vals], [v for _, v in vals])
                res["slopes"][cond]["s%d" % sd] = entry
            else:
                res["slopes"][cond]["s%d" % sd] = {"SLOPE_v": None,
                                                   "why": "not all three speed cells pass Gate G"}
        got = [v["SLOPE_v"] for v in res["slopes"][cond].values() if v.get("SLOPE_v") is not None]
        print("%s: %d contributing seeds" % (cond, len(got)))

    def arm(c):
        return [(k, v["SLOPE_v"]) for k, v in sorted(res["slopes"][c].items())
                if v.get("SLOPE_v") is not None]

    Sa, Wa, Ca = arm("S"), arm("W"), arm("C")
    r = {"n_S": len(Sa), "n_W": len(Wa), "n_C": len(Ca),
         "S_seeds": dict(Sa), "W_seeds": dict(Wa), "C_seeds": dict(Ca)}
    s = [b for _, b in Sa]
    w = [b for _, b in Wa]
    c = [b for _, b in Ca]
    if len(s) < 4 or len(w) < 4:
        r["VERDICT"] = "UNINFORMATIVE"
        r["why"] = "section 7 requires >=4 contributing seeds per arm; got %d S, %d W" % (len(s), len(w))
    else:
        r["S_range"] = [min(s), max(s)]
        r["W_range"] = [min(w), max(w)]
        r["C_range"] = [min(c), max(c)] if c else None
        r["S_mean"], r["W_mean"] = float(np.mean(s)), float(np.mean(w))
        r["C_mean"] = float(np.mean(c)) if c else None
        gap = max(min(w) - max(s), min(s) - max(w))
        r["gap"] = gap
        r["separated"] = bool(gap > 0)
        if gap > 0:
            r["direction"] = "SPASTIC HIGH" if min(s) > max(w) else "SPASTIC LOW"
            r["matches_registered_prediction"] = bool(r["direction"] == "SPASTIC HIGH")
            r["permutation"] = perm_floor(s, w)
            r["VERDICT"] = "SEPARATED"
        else:
            r["VERDICT"] = "OVERLAP"
        if c:
            r["W_vs_C_secondary_prediction"] = {
                "W_mean": r["W_mean"], "C_mean": r["C_mean"],
                "W_range": r["W_range"], "C_range": r["C_range"],
                "note": "section 3 additionally predicted W ~ C; reported, not primary"}
    res["PRIMARY_S_vs_W"] = r

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    print("VERDICT %s" % r["VERDICT"])
    if r.get("separated"):
        print("  gap=%.8f  direction=%s  matches_prediction=%s  floor=%s"
              % (r["gap"], r["direction"], r["matches_registered_prediction"],
                 r["permutation"]["floor"]))
    if "S_range" in r:
        print("  S %s mean %.6f" % (r["S_range"], r["S_mean"]))
        print("  W %s mean %.6f" % (r["W_range"], r["W_mean"]))
        print("  C %s mean %s" % (r["C_range"], r["C_mean"]))
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
