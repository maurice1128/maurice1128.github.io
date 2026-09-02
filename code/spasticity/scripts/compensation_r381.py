# -*- coding: utf-8 -*-
"""PREREG_compensation_r380.md (34a81d3c...) -- where did the absorbed 86% go?

PRIMARY (sec 3): hip_swing_peak_L = per-cycle max of hip_flexion_l over SWING samples,
averaged over admissible cycles, degrees. Predicted DORSIFLEXOR-WEAK HIGH, SPASTIC LOW
(steppage gait is the textbook compensation for foot drop from weakness).

SECONDARIES (sec 4) are a DESCRIPTIVE MAP with declared multiplicity. No floor, no verdict and
no discriminator claim may be attached to any of them -- the script therefore computes ranges
and means for them and deliberately does NOT compute permutation floors for them.

Conventions carried unaltered from doseladder_r371.py / kinpair_r379.py.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\COMPENSATION_r381.json"
PREREG_SHA = "34a81d3cb309bf5a829af07669eff4c2d1ff7e4bcb4acf343ad09e73735ccca3"
SETTLE, T1 = 1.0, 9.73

LADDER = [(0.00625, "R289KV00625"), (0.0125, "R289KV0125"),
          (0.035, "R291KV0035"), (0.070, "R291KV0070")]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]

MUSCLES = ["add_mag", "bifemsh", "gastroc", "glut_max", "glut_med", "hamstrings",
           "iliopsoas", "rect_fem", "soleus", "tib_ant", "vasti"]
PRIMARY = "hip_swing_peak_L"


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

    def phase_idx(swing):
        segs = []
        for a, b in win:
            m = (~on[a:b]) if swing else on[a:b]
            if m.any():
                segs.append(np.arange(a, b)[m])
        return np.concatenate(segs) if segs else None

    sw_i, st_i = phase_idx(True), phase_idx(False)
    if sw_i is None or st_i is None:
        rec["gate_G"] = False
        rec["guard"] = "a phase mask was empty in every cycle"
        return rec

    # PRIMARY, sec 3 -- per-cycle peak over SWING samples only, then averaged
    for side, key in (("l", "hip_swing_peak_L"), ("r", "hip_swing_peak_R")):
        v = S.col(cols, dat, "hip_flexion_%s" % side)
        if v is None:
            rec["error"] = "no hip_flexion_%s" % side
            return rec
        v = np.degrees(v)
        per = []
        for a, b in win:
            m = ~on[a:b]
            if m.any():
                per.append(float(np.max(v[a:b][m])))
        rec[key] = float(np.mean(per)) if per else None

    sec = {}
    for side in ("l", "r"):
        v = S.col(cols, dat, "knee_angle_%s" % side)
        if v is not None:
            v = np.degrees(v)
            per = []
            for a, b in win:
                m = ~on[a:b]
                if m.any():
                    # knee flexion is negative in this model; peak flexion is the minimum
                    per.append(float(np.min(v[a:b][m])))
            sec["knee_swing_peak_%s" % side.upper()] = float(np.mean(per)) if per else None
    for m in MUSCLES:
        for side in ("l", "r"):
            a = S.muscle_signal(cols, dat, m, side, "activation")
            if a is None:
                continue
            sec["%s_%s_swing" % (m, side)] = float(np.mean(a[sw_i]))
            sec["%s_%s_stance" % (m, side)] = float(np.mean(a[st_i]))
    rec["secondary"] = sec
    return rec


def seed_means(tags, cells, key, sec=False):
    out = {}
    for tg in tags:
        r = cells[tg]
        if not r.get("gate_G"):
            continue
        v = r["secondary"].get(key) if sec else r.get(key)
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


def main():
    res = {"registration": "PREREG_compensation_r380.md", "registration_sha256": PREREG_SHA,
           "primary": "hip_swing_peak_L = per-cycle max of hip_flexion_l over swing, deg",
           "registered_prediction": "DORSIFLEXOR-WEAK HIGH, SPASTIC LOW (steppage gait)",
           "within_scenario": True,
           "secondary_note": "sec 4: descriptive map with declared multiplicity; no floor, no "
                             "verdict, no discriminator claim attaches to any secondary",
           "cells": {}}

    wt = tags_for(DFWEAK)
    for tg in wt:
        res["cells"][tg] = measure(tg)
    wsm = seed_means(wt, res["cells"], PRIMARY)
    w = sorted(wsm.values())
    print("DFWEAK gate-G %d/%d   %s [%.4f, %.4f] deg"
          % (sum(1 for t in wt if res["cells"][t].get("gate_G")), len(wt), PRIMARY, w[0], w[-1]))

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
            e["why"] = "sec 6: fewer than 4 Gate-G seeds (%d); reported, not dropped" % n_ok
            print("  KV %-8s UNINFORMATIVE (%d Gate-G)" % (kv, n_ok))
        else:
            sm = seed_means(tg, res["cells"], PRIMARY)
            s = sorted(sm.values())
            gap = max(w[0] - s[-1], s[0] - w[-1])
            e.update({"n": len(s), "range": [s[0], s[-1]], "mean": float(np.mean(s)),
                      "dfweak_range": [w[0], w[-1]], "dfweak_mean": float(np.mean(w)),
                      "gap": gap, "separated": bool(gap > 0), "seed_means": sm})
            if gap > 0:
                e["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "DFWEAK HIGH"
                e["matches_registered_prediction"] = bool(e["direction"] == "DFWEAK HIGH")
                e["permutation"] = floor(s, w)
                e["VERDICT"] = "SEPARATED"
                e["MDC_note"] = ("sec 3: hip MDC not sourced; gap %.4f deg is presumptively "
                                 "sub-threshold if below 3.8 deg" % gap)
            else:
                e["VERDICT"] = "OVERLAP"
            print("  KV %-8s n=%d  S [%.4f, %.4f]  W [%.4f, %.4f]  gap %+.4f deg  %s%s"
                  % (kv, len(s), s[0], s[-1], w[0], w[-1], gap, e["VERDICT"],
                     "  " + e["direction"] if gap > 0 else ""))
        rungs[str(kv)] = e
    res["rungs"] = rungs

    # sec 4 descriptive map -- arm means only, no tests
    print()
    print("=== where the compensation went (descriptive, no tests) ===")
    keys = sorted({k for t in res["cells"] if res["cells"][t].get("gate_G")
                   for k in res["cells"][t]["secondary"]})
    kv035 = tags_for(["R291KV0035"])
    smap = {}
    for k in keys:
        sv = list(seed_means(kv035, res["cells"], k, sec=True).values())
        wv = list(seed_means(wt, res["cells"], k, sec=True).values())
        if not sv or not wv:
            continue
        ms, mw = float(np.mean(sv)), float(np.mean(wv))
        pooled = float(np.std(sv + wv, ddof=1)) or float("nan")
        smap[k] = {"KV0.035_mean": ms, "DFWEAK_mean": mw, "diff": ms - mw,
                   "abs_diff_over_pooled_sd": abs(ms - mw) / pooled if pooled == pooled else None,
                   "KV0.035_range": [min(sv), max(sv)], "DFWEAK_range": [min(wv), max(wv)]}
    res["SECONDARY_descriptive_map"] = smap
    top = sorted((v for v in smap.items()),
                 key=lambda kv_: -(kv_[1]["abs_diff_over_pooled_sd"] or 0))[:14]
    print("  %-26s %11s %11s %10s %8s" % ("channel", "KV0.035", "DFWEAK", "diff", "|d|/sd"))
    for k, v in top:
        print("  %-26s %11.5f %11.5f %+10.5f %8.2f"
              % (k, v["KV0.035_mean"], v["DFWEAK_mean"], v["diff"],
                 v["abs_diff_over_pooled_sd"] or float("nan")))

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
