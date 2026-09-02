# -*- coding: utf-8 -*-
"""r421 registered endpoint: the single-muscle spanning test.

Registration: paper/PREREG_spanning_r421.md, sha256 323568b2d8da15cf..., hashed before any cell
in its section 4 existed.

Reading dose is fixed by section 5 as the HIGHEST rung at which BOTH single-muscle arms reach
>= 4/6 Gate G. It is read off the data, not chosen.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPANNING_RESULT_r421.json"
SETTLE, T1 = 1.0, 9.73
RUNGS = ["0125", "0250", "0500"]
KV = {"0125": 0.0125, "0250": 0.025, "0500": 0.050}
ARMS = ["GASONLY", "SOLONLY", "BOTH"]
SEEDS = range(101, 107)
CONTROL = ["R151C_s%d" % s for s in SEEDS]


def measure(prefix):
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
    ok = float(t[-1]) >= T1 and len(win) >= 5
    if not ok:
        return {"gate_G": False, "t_end": float(t[-1]), "n_cycles": len(win)}
    on = grf > thr
    stance = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    hp = np.degrees(S.col(cols, dat, "hip_flexion_l"))
    return {"gate_G": True, "t_end": float(t[-1]), "n_cycles": len(win),
            "KNEE_ic": float(np.mean([kn[a] for a, _ in win])),
            "ANKLE_st": float(np.mean(an[stance])),
            "HIP_ic": float(np.mean([hp[a] for a, _ in win]))}


def arm_cells(arm, rung):
    out = {}
    for s in SEEDS:
        p = "R421%s%s_s%d" % (arm, rung, s)
        out[p] = measure(p)
    return out


def stat(cells, key):
    v = [c[key] for c in cells.values() if c and c.get("gate_G")]
    if not v:
        return None
    return {"n": len(v), "mean": float(np.mean(v)),
            "range": [float(min(v)), float(max(v))], "values": sorted(v)}


def overlaps(a, b):
    return not (a["range"][1] < b["range"][0] or b["range"][1] < a["range"][0])


def edge_gap(a, b):
    """positive when the two ranges are disjoint; sign follows a-below-b."""
    if a["range"][1] < b["range"][0]:
        return b["range"][0] - a["range"][1]
    if b["range"][1] < a["range"][0]:
        return -(a["range"][0] - b["range"][1])
    return 0.0


res = {"round": "SPANNING_RESULT_r421", "registration": "PREREG_spanning_r421.md",
       "registration_sha256":
           "323568b2d8da15cf1634c9f21faaf5d38fe7e53054239eabca6c7c2f8b41432"[:64],
       "cells": {}, "by_rung": {}}

ctrl = {p: measure(p) for p in CONTROL}
res["cells"].update(ctrl)
res["control_R151C"] = {k: stat(ctrl, k) for k in ("KNEE_ic", "ANKLE_st", "HIP_ic")}
res["control_R151C"]["n_gate_G"] = sum(1 for c in ctrl.values() if c and c.get("gate_G"))

print("%-9s %-6s %-4s  %-24s %-24s %s" % ("arm", "KV", "n", "KNEE_ic", "ANKLE_st", "HIP_ic"))
c = res["control_R151C"]
print("%-9s %-6s %-4d  [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]"
      % ("CONTROL", "-", c["n_gate_G"], c["KNEE_ic"]["range"][0], c["KNEE_ic"]["range"][1],
         c["ANKLE_st"]["range"][0], c["ANKLE_st"]["range"][1],
         c["HIP_ic"]["range"][0], c["HIP_ic"]["range"][1]))

for rung in RUNGS:
    res["by_rung"][rung] = {"KV": KV[rung], "arms": {}}
    for arm in ARMS:
        cs = arm_cells(arm, rung)
        res["cells"].update(cs)
        n = sum(1 for x in cs.values() if x and x.get("gate_G"))
        e = {"n_gate_G": n, "uninformative": n < 4,
             "t_end": stat({k: {**v, "t_end_v": v["t_end"]} for k, v in cs.items() if v},
                           "t_end") if any(cs.values()) else None}
        for k in ("KNEE_ic", "ANKLE_st", "HIP_ic"):
            e[k] = stat(cs, k)
        res["by_rung"][rung]["arms"][arm] = e
        if e["KNEE_ic"]:
            print("%-9s %-6.4f %-4d  [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]"
                  % (arm, KV[rung], n, e["KNEE_ic"]["range"][0], e["KNEE_ic"]["range"][1],
                     e["ANKLE_st"]["range"][0], e["ANKLE_st"]["range"][1],
                     e["HIP_ic"]["range"][0], e["HIP_ic"]["range"][1]))
        else:
            print("%-9s %-6.4f %-4d  no Gate-G cell" % (arm, KV[rung], n))

# ---- reading dose, fixed by section 5: highest rung with BOTH single-muscle arms >= 4/6 -----
elig = [r for r in RUNGS
        if res["by_rung"][r]["arms"]["GASONLY"]["n_gate_G"] >= 4
        and res["by_rung"][r]["arms"]["SOLONLY"]["n_gate_G"] >= 4]
res["reading_dose"] = elig[-1] if elig else None
print()
print("eligible rungs (both single-muscle arms >= 4/6): %s" % elig)
print("READING DOSE: %s" % (("KV %.4f" % KV[res["reading_dose"]]) if elig else "NONE"))

P = {}
if not elig:
    res["VERDICT"] = "UNINFORMATIVE -- no rung has both single-muscle arms at >= 4/6 Gate G."
else:
    rd = res["reading_dose"]
    A = res["by_rung"][rd]["arms"]
    G, SO, B = A["GASONLY"], A["SOLONLY"], A["BOTH"]

    gap_k = edge_gap(G["KNEE_ic"], SO["KNEE_ic"])
    P["P1_knee_GAS_more_flexed_and_disjoint"] = {
        "GASONLY": G["KNEE_ic"], "SOLONLY": SO["KNEE_ic"],
        "GAS_more_flexed": G["KNEE_ic"]["mean"] < SO["KNEE_ic"]["mean"],
        "disjoint": not overlaps(G["KNEE_ic"], SO["KNEE_ic"]),
        "edge_gap_deg": gap_k,
        "VERDICT": "HOLDS" if (G["KNEE_ic"]["mean"] < SO["KNEE_ic"]["mean"]
                               and not overlaps(G["KNEE_ic"], SO["KNEE_ic"])) else "FAILS"}
    P["P2_ankle_overlaps"] = {
        "GASONLY": G["ANKLE_st"], "SOLONLY": SO["ANKLE_st"],
        "overlap": overlaps(G["ANKLE_st"], SO["ANKLE_st"]),
        "edge_gap_deg": edge_gap(G["ANKLE_st"], SO["ANKLE_st"]),
        "VERDICT": "HOLDS" if overlaps(G["ANKLE_st"], SO["ANKLE_st"]) else "FAILS"}
    P["P3_hip_overlaps"] = {
        "GASONLY": G["HIP_ic"], "SOLONLY": SO["HIP_ic"],
        "overlap": overlaps(G["HIP_ic"], SO["HIP_ic"]),
        "VERDICT": "HOLDS" if overlaps(G["HIP_ic"], SO["HIP_ic"]) else "FAILS"}

    lo, hi = sorted([G["KNEE_ic"]["mean"], SO["KNEE_ic"]["mean"]])
    ctrl_k = res["control_R151C"]["KNEE_ic"]["mean"]
    bm = B["KNEE_ic"]["mean"] if B["KNEE_ic"] else None
    between_or_beyond = bm is not None and (lo - 1e-9 <= bm <= hi + 1e-9 or bm < lo or bm > hi)
    near_control = bm is not None and abs(bm - ctrl_k) < abs(lo - ctrl_k) * 0.25
    P["P4_BOTH_not_back_at_control"] = {
        "BOTH_mean": bm, "control_mean": ctrl_k,
        "GASONLY_mean": G["KNEE_ic"]["mean"], "SOLONLY_mean": SO["KNEE_ic"]["mean"],
        "BOTH_within_or_beyond_the_two_arms": bool(between_or_beyond),
        "BOTH_back_near_control": bool(near_control),
        "VERDICT": "FAILS" if near_control else "HOLDS",
        "note": "if BOTH returns to control the causal reading of P1 is void, per section 5"}

    med = {}
    for arm in ("GASONLY", "SOLONLY"):
        for r in RUNGS:
            cs = {k: v for k, v in res["cells"].items()
                  if k.startswith("R421%s%s_" % (arm, r)) and v}
            if cs:
                med.setdefault(arm, {})[r] = float(np.median([v["t_end"] for v in cs.values()]))
    P["P5_GAS_survives_less_than_SOL"] = {
        "median_t_end": med,
        "holds_at_each_rung": {r: (med["GASONLY"][r] < med["SOLONLY"][r])
                               for r in RUNGS if r in med.get("GASONLY", {})
                               and r in med.get("SOLONLY", {})},
        "VERDICT": None}
    hv = P["P5_GAS_survives_less_than_SOL"]["holds_at_each_rung"]
    P["P5_GAS_survives_less_than_SOL"]["VERDICT"] = "HOLDS" if all(hv.values()) else "FAILS"

    # ---- section 6 duration control, registered in advance ------------------------------
    ct, ck = [], []
    per = {}
    for arm in ("GASONLY", "SOLONLY"):
        cs = [v for k, v in res["cells"].items()
              if k.startswith("R421%s%s_" % (arm, rd)) and v and v.get("gate_G")]
        tt = np.array([c["t_end"] for c in cs])
        kk = np.array([c["KNEE_ic"] for c in cs])
        if len(set(tt.tolist())) > 1:
            per[arm] = {"slope_deg_per_s": float(np.polyfit(tt, kk, 1)[0]),
                        "pearson_r": float(np.corrcoef(tt, kk)[0, 1]), "n": len(cs)}
        else:
            per[arm] = {"t_end_identical": float(tt[0]), "n": len(cs)}
        ct += list(tt - tt.mean())
        ck += list(kk - kk.mean())
    bw = float(np.polyfit(ct, ck, 1)[0]) if len(set(ct)) > 1 else 0.0
    rw = float(np.corrcoef(ct, ck)[0, 1]) if len(set(ct)) > 1 else 0.0
    tspan = abs(np.mean([c["t_end"] for k, c in res["cells"].items()
                         if k.startswith("R421GASONLY%s_" % rd) and c and c.get("gate_G")])
                - np.mean([c["t_end"] for k, c in res["cells"].items()
                           if k.startswith("R421SOLONLY%s_" % rd) and c and c.get("gate_G")]))
    eff = abs(G["KNEE_ic"]["mean"] - SO["KNEE_ic"]["mean"])
    attrib = abs(bw) * tspan
    frac = attrib / eff if eff else float("inf")
    res["duration_control"] = {"per_arm": per, "pooled_slope_deg_per_s": bw, "pearson_r": rw,
                               "t_end_span_s": float(tspan), "effect_deg": float(eff),
                               "deg_attributable": float(attrib), "fraction": float(frac),
                               "threshold": 0.50, "CONFOUNDED": bool(frac > 0.50)}
    if res["duration_control"]["CONFOUNDED"] and P["P1_knee_GAS_more_flexed_and_disjoint"]["VERDICT"] == "HOLDS":
        P["P1_knee_GAS_more_flexed_and_disjoint"]["VERDICT"] = \
            "CONFOUNDED (section 6); not counted as holding"

    res["predictions"] = P
    held = [k for k, v in P.items() if v["VERDICT"] == "HOLDS"]
    res["VERDICT"] = "%d of %d hold at KV %.4f: %s" % (len(held), len(P), KV[rd],
                                                       ", ".join(held) or "none")
    print()
    for k, v in P.items():
        print("  %-44s %s" % (k, v["VERDICT"]))
    dc = res["duration_control"]
    print()
    print("duration control: pooled %+.4f deg/s (r %+.4f), %.4f of %.4f deg = %.0f%% -> %s"
          % (dc["pooled_slope_deg_per_s"], dc["pearson_r"], dc["deg_attributable"],
             dc["effect_deg"], 100 * dc["fraction"], "CONFOUNDED" if dc["CONFOUNDED"] else "clear"))

io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("VERDICT:", res["VERDICT"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
