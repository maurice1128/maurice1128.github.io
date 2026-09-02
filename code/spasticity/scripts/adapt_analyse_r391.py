# -*- coding: utf-8 -*-
"""PREREG_adaptation_r390.md (9664b8ed...) -- GAP(g), the adaptation-time sweep.

PRIMARY (sec 3): GAP(g) = the spastic-vs-dorsiflexor-weak gap on mean ankle_angle_l over
stance, in degrees, at adaptation budget g in {1, 5, 15, 40, 91}.
Registered prediction: GAP(g) monotonically DECREASING in g, and GAP(1) >= 3.8 deg (the
clinical MDC floor) while GAP(91) is the ~1 deg already measured.

Sec 4: a budget with fewer than 4 Gate-G seeds per arm is UNINFORMATIVE and is reported, not
dropped -- and if the acute budgets fall, that answers a different question (the model cannot
walk) and must not be presented as a gap measurement.
Sec 4: every verdict is read against the 21.3% BATCH NULL, not the 1/924 permutation floor.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\ADAPT_RESULT_r391.json"
PREREG_SHA = "9664b8edbe2f3232bcd3f2dc4ad07f81897b9143c8436b226a703a42d23b8334"
SETTLE, T1, MDC_LO = 1.0, 9.73, 3.8
BUDGETS = ["001", "005", "015", "040", "091"]
SEEDS = list(range(101, 107))
BATCH_NULL_NOTE = ("HARMONIC_r383.json measured 96/450 = 21.3% separation between two "
                   "dorsiflexor-weakness families with the SAME lesion mechanism. Both arms "
                   "here are single families, so that is this design's null, not 1/924.")


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))]
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
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])

    ank = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    rec["mean_ankle_stance_deg"] = float(np.mean(ank[st]))          # PRIMARY input
    # secondaries, sec 5
    kne = S.col(cols, dat, "knee_angle_l")
    hip = S.col(cols, dat, "hip_flexion_l")
    sec = {}
    sec["knee_at_heelstrike_deg"] = float(np.mean([np.degrees(kne[a]) for a, _ in win]))
    sec["min_ankle_cycle_deg"] = float(np.mean([np.min(ank[a:b]) for a, b in win]))
    sec["ankle_rom_cycle_deg"] = float(np.mean([np.ptp(ank[a:b]) for a, b in win]))
    per = []
    for a, b in win:
        m = ~on[a:b]
        if m.any():
            per.append(float(np.max(np.degrees(hip[a:b][m]))))
    sec["hip_swing_peak_L_deg"] = float(np.mean(per)) if per else None
    sol = S.muscle_signal(cols, dat, "soleus", "l", "activation")
    sec["A_soleus_stance"] = float(np.mean(sol[st])) if sol is not None else None
    rec["secondary"] = sec
    # the independent variable's own readout, sec 5
    h = os.path.join(d, "history.txt")
    if os.path.exists(h):
        rows = [ln.rstrip("\n").split("\t") for ln in io.open(h, encoding="utf-8",
                                                              errors="replace")]
        hdr = rows[0]
        if "best_fitness" in hdr:
            bi = hdr.index("best_fitness")
            vals = [float(r[bi]) for r in rows[1:] if len(r) > bi]
            if vals:
                rec["n_generations"] = len(vals)
                rec["terminal_objective"] = min(vals)
                rec["objective_gen0"] = vals[0]
    return rec


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
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot}


def main():
    res = {"registration": "PREREG_adaptation_r390.md", "registration_sha256": PREREG_SHA,
           "primary": "GAP(g) = spastic-vs-DFweak gap on mean ankle_angle_l over stance, deg",
           "registered_prediction": "GAP(g) monotonically DECREASING in g; GAP(1) >= 3.8 deg",
           "BATCH_NULL": BATCH_NULL_NOTE, "MDC_deg": [3.8, 11.5], "cells": {}, "budgets": {}}

    for g in BUDGETS:
        e = {"budget_generations": int(g)}
        arms = {}
        for arm, L in (("SPASTIC", "S"), ("DFWEAK", "W")):
            vals, tends, nok = {}, {}, 0
            for s in SEEDS:
                tag = "R390ADAPT%sg%s_s%d" % (L, g, s)
                r = measure(tag)
                res["cells"][tag] = r
                tends["s%d" % s] = r.get("t_end_s")
                if r.get("gate_G"):
                    nok += 1
                    vals["s%d" % s] = r["mean_ankle_stance_deg"]
            arms[arm] = {"n_gate_G": nok, "seed_values": vals, "t_end_s": tends}
            if vals:
                v = sorted(vals.values())
                arms[arm]["range"] = [v[0], v[-1]]
                arms[arm]["mean"] = float(np.mean(v))
        e["arms"] = arms
        ns, nw = arms["SPASTIC"]["n_gate_G"], arms["DFWEAK"]["n_gate_G"]
        if ns < 4 or nw < 4:
            e["VERDICT"] = "UNINFORMATIVE"
            e["why"] = ("sec 4: fewer than 4 Gate-G seeds per arm (%d spastic, %d weak). "
                        "The acute state may be unmeasurable because the model cannot walk; "
                        "this is NOT a gap measurement." % (ns, nw))
            e["GAP_deg"] = None
            print("  g=%-4s  S %d/6  W %d/6   UNINFORMATIVE" % (g, ns, nw))
        else:
            s = sorted(arms["SPASTIC"]["seed_values"].values())
            w = sorted(arms["DFWEAK"]["seed_values"].values())
            gap = max(w[0] - s[-1], s[0] - w[-1])
            e["GAP_deg"] = gap
            e["separated"] = bool(gap > 0)
            e["above_MDC"] = bool(gap >= MDC_LO)
            if gap > 0:
                e["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "SPASTIC LOW"
                e["permutation"] = floor(s, w)
                e["permutation_note"] = ("subordinate to the batch null; see /BATCH_NULL")
            print("  g=%-4s  S %d/6 [%+.4f,%+.4f]  W %d/6 [%+.4f,%+.4f]  GAP %+.4f deg  %s%s"
                  % (g, ns, s[0], s[-1], nw, w[0], w[-1], gap,
                     "ABOVE MDC" if gap >= MDC_LO else "below MDC",
                     "  " + e["direction"] if gap > 0 else "  OVERLAP"))
        res["budgets"][g] = e

    got = [(int(g), res["budgets"][g]["GAP_deg"]) for g in BUDGETS
           if res["budgets"][g].get("GAP_deg") is not None]
    got.sort()
    mono = all(got[i][1] >= got[i + 1][1] - 1e-12 for i in range(len(got) - 1))
    res["PREDICTION_ASSESSMENT"] = {
        "measurable_budgets": [a for a, _ in got],
        "GAP_by_budget": {str(a): b for a, b in got},
        "monotonically_decreasing": bool(mono) if len(got) >= 2 else None,
        "GAP_at_smallest_measurable_budget": got[0][1] if got else None,
        "any_budget_above_MDC": bool(any(b >= MDC_LO for _, b in got)),
        "verdict": ("NO BUDGET CLEARS THE CLINICAL MDC -- the lesion is not clinically visible "
                    "at this severity even before adaptation completes"
                    if got and not any(b >= MDC_LO for _, b in got) else
                    "at least one budget clears the MDC; see GAP_by_budget"
                    if got else "UNINFORMATIVE -- no budget had 4 Gate-G seeds per arm")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    pa = res["PREDICTION_ASSESSMENT"]
    print()
    print("GAP by budget        : %s" % pa["GAP_by_budget"])
    print("monotone decreasing  : %s" % pa["monotonically_decreasing"])
    print("any budget >= 3.8 deg: %s" % pa["any_budget_above_MDC"])
    print("VERDICT: %s" % pa["verdict"])
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
