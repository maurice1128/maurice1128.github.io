# -*- coding: utf-8 -*-
"""PREREG_emgvskin_r376.md (fe28136e...) -- does activation detect at a smaller dose than kinematics?

KV_act = smallest ladder rung where soleus stance activation is disjoint from the CONTROL arm.
KV_kin = smallest ladder rung where ANY of four kinematic endpoints is disjoint from control.
Taking the minimum over four kinematic endpoints is deliberately generous to kinematics (sec 5).

Gastrocnemius activation is computed alongside because r371 limitation L8 says it shows no
threshold against the DF-weak arm; sec 8 registers that a soleus/gastroc disagreement IS the
finding and forbids quoting a single KV_act in that case.

Conventions carried unaltered from doseladder_r371.py.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\EMGVSKIN_r377.json"
PREREG_SHA = "fe28136e2ffde1409ac8af004f6fb5e417ba8b2198062d7485bd6b6bf545c6c2"
SETTLE, T1 = 1.0, 9.73

LADDER = [(0.00625, "R289KV00625"), (0.0125, "R289KV0125"),
          (0.035, "R291KV0035"), (0.070, "R291KV0070")]
CONTROL = ["R203V080C", "R203V105C", "R203V130C"]

ACT = ["A_soleus", "A_gastroc"]
KIN = ["knee_at_heelstrike_deg", "min_ankle_cycle_deg",
       "ankle_rom_cycle_deg", "mean_ankle_stance_deg"]


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
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])

    for m, key in (("soleus", "A_soleus"), ("gastroc", "A_gastroc")):
        v = S.muscle_signal(cols, dat, m, "l", "activation")
        rec[key] = float(np.mean(v[st])) if v is not None else None

    knee = S.col(cols, dat, "knee_angle_l")
    ank = S.col(cols, dat, "ankle_angle_l")
    if knee is None or ank is None:
        rec["error"] = "missing kinematic channel"
        return rec
    knee = np.degrees(knee)
    ank = np.degrees(ank)
    # sec 4.1 heel strike = the cycle's opening index, which IS the heel-strike event
    rec["knee_at_heelstrike_deg"] = float(np.mean([knee[a] for a, _ in win]))
    rec["min_ankle_cycle_deg"] = float(np.mean([np.min(ank[a:b]) for a, b in win]))
    rec["ankle_rom_cycle_deg"] = float(np.mean([np.ptp(ank[a:b]) for a, b in win]))
    rec["mean_ankle_stance_deg"] = float(np.mean(ank[st]))
    return rec


def seed_means(tags, cells, key):
    out = {}
    for tg in tags:
        r = cells[tg]
        if not r.get("gate_G") or r.get(key) is None:
            continue
        out.setdefault(tg.split("_")[-1], []).append(r[key])
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
    res = {"registration": "PREREG_emgvskin_r376.md", "registration_sha256": PREREG_SHA,
           "question": "does an activation endpoint separate from CONTROL at a smaller reflex "
                       "gain than any of four kinematic endpoints",
           "hypothesis": "KV_act < KV_kin",
           "between_scenario": True,
           "between_scenario_note": "the control arm is at min_velocity 0.80/1.05/1.30 while "
                                    "the ladder is at 1.0 (sec 3); every statement of this "
                                    "result carries that label",
           "kinematic_multiplicity": len(KIN),
           "generous_to_kinematics": "KV_kin is the MINIMUM over four kinematic endpoints (sec 5)",
           "cells": {}}

    ctags = tags_for(CONTROL)
    for tg in ctags:
        res["cells"][tg] = measure(tg)
    ctrl = {k: seed_means(ctags, res["cells"], k) for k in ACT + KIN}
    res["control"] = {"n_cells": len(ctags),
                      "n_gate_G": sum(1 for t in ctags if res["cells"][t].get("gate_G")),
                      "seed_means": ctrl}
    print("CONTROL gate-G %d/%d" % (res["control"]["n_gate_G"], len(ctags)))

    rungs = {}
    for kv, fam in LADDER:
        tg = tags_for([fam])
        for x in tg:
            if x not in res["cells"]:
                res["cells"][x] = measure(x)
        e = {"family": fam, "n_gate_G": sum(1 for x in tg if res["cells"][x].get("gate_G")),
             "endpoints": {}}
        if e["n_gate_G"] < 4:
            e["VERDICT"] = "UNINFORMATIVE"
            e["why"] = "sec 7: fewer than 4 Gate-G seeds (%d); reported, not dropped" % e["n_gate_G"]
            print("  KV %-8s UNINFORMATIVE (%d Gate-G)" % (kv, e["n_gate_G"]))
        else:
            for key in ACT + KIN:
                sm = seed_means(tg, res["cells"], key)
                s = sorted(sm.values())
                c = sorted(ctrl[key].values())
                gap = max(min(c) - max(s), min(s) - max(c))
                d = {"n": len(s), "range": [s[0], s[-1]], "mean": float(np.mean(s)),
                     "control_range": [c[0], c[-1]], "control_mean": float(np.mean(c)),
                     "gap_vs_control": gap, "separated": bool(gap > 0), "seed_means": sm}
                if gap > 0:
                    d["direction"] = "LESION HIGH" if s[0] > c[-1] else "LESION LOW"
                    d["permutation"] = floor(s, c)
                e["endpoints"][key] = d
            print("  KV %-8s  %s" % (kv, "  ".join(
                "%s=%s" % (k.replace("_deg", "").replace("A_", ""),
                           "SEP" if e["endpoints"][k]["separated"] else "ovl")
                for k in ACT + KIN)))
        rungs[str(kv)] = e
    res["rungs"] = rungs

    def first_sep(keys):
        for kv, _ in LADDER:
            e = rungs[str(kv)]
            if e.get("VERDICT") == "UNINFORMATIVE":
                continue
            if any(e["endpoints"][k]["separated"] for k in keys):
                return kv
        return None

    kv_act_sol = first_sep(["A_soleus"])
    kv_act_gas = first_sep(["A_gastroc"])
    kv_kin = first_sep(KIN)
    per_kin = {k: first_sep([k]) for k in KIN}

    out = {"KV_act_soleus": kv_act_sol, "KV_act_gastroc": kv_act_gas,
           "KV_kin_min_over_four": kv_kin, "KV_kin_per_endpoint": per_kin,
           "measurable_rungs": [kv for kv, _ in LADDER
                                if rungs[str(kv)].get("VERDICT") != "UNINFORMATIVE"]}
    # sec 8: a soleus/gastroc disagreement IS the finding and forbids a single KV_act
    if kv_act_sol != kv_act_gas:
        out["sec8_channel_disagreement"] = True
        out["sec8_note"] = ("soleus and gastrocnemius disagree on KV_act (%s vs %s); sec 8 "
                            "forbids quoting a single KV_act, and the disagreement is the "
                            "finding" % (kv_act_sol, kv_act_gas))
        out["VERDICT"] = "CHANNEL-DEPENDENT -- no single KV_act"
    elif kv_act_sol is None and kv_kin is None:
        out["VERDICT"] = "UNINFORMATIVE -- nothing separated at any rung"
    elif kv_act_sol is None:
        out["VERDICT"] = "REFUTED -- kinematics separated where activation did not"
    elif kv_kin is None:
        out["VERDICT"] = "SUPPORTED -- activation separated, no kinematic endpoint did at any rung"
    elif kv_act_sol < kv_kin:
        out["VERDICT"] = "SUPPORTED -- activation separates one or more rungs earlier"
    elif kv_act_sol == kv_kin:
        out["VERDICT"] = "NOT SUPPORTED -- same rung"
    else:
        out["VERDICT"] = "REFUTED -- kinematics separates earlier"
    res["PRIMARY"] = out

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print("KV_act soleus  = %s" % kv_act_sol)
    print("KV_act gastroc = %s" % kv_act_gas)
    print("KV_kin (min over 4) = %s   per-endpoint %s" % (kv_kin, per_kin))
    print("VERDICT: %s" % out["VERDICT"])
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
