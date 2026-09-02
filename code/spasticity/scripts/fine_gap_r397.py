# -*- coding: utf-8 -*-
"""Gap on mean stance ankle angle for the FINE chained spastic rungs, against weakness x0.80.

r396's --headline crashes on an index because WK_RUNGS was reduced to the root alone for that
arm; this computes the same quantity directly from the .sto files rather than patching the
launcher, so nothing about r396's deposits is touched.

Convention carried unaltered: SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the
last kept cycle, require >= 5, stance = leg0_l.grf_norm_y > 0.05.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\FINE_GAP_r397.json"
SETTLE, T1 = 1.0, 9.73
# MDC: 3.8 was RETIRED at r399. It is the MDC for TRAILING LIMB ANGLE in Kesar 2010,
# not for any knee or ankle quantity. The conservative knee band is 7.25-7.62 deg
# (Molina-Rueda 2021 corrected for a sqrt(2) error; Geiger 2019). Kept as a named
# constant so no reader mistakes the old figure for a knee threshold.
MDC = 7.62
MDC_RETIRED_r399 = 3.8


def measure(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if len(g) != 1:
        return None
    stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return {"gate_G": False, "t_end_s": float(t[-1]), "n_cycles_in_window": len(win)}
    on = grf > thr
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    ang = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    return {"gate_G": True, "t_end_s": float(t[-1]), "n_cycles_in_window": len(win),
            "mean_ankle_stance_deg": float(np.mean(ang[st]))}


def arm(prefixes):
    vals, cells = [], {}
    for p in prefixes:
        r = measure(p)
        cells[p] = r
        if r and r.get("gate_G"):
            vals.append(r["mean_ankle_stance_deg"])
    return sorted(vals), cells


res = {"what": "fine chained spastic ladder vs the weakness arm at x0.80",
       "endpoint": "mean ankle_angle_l over stance samples of admissible cycles, deg",
       "MDC_floor_deg": MDC, "cells": {}}

wk, c = arm(["R151W_s%d" % s for s in range(101, 107)])
res["cells"].update(c)
res["weakness_x080"] = {"n": len(wk), "range": [wk[0], wk[-1]], "mean": float(np.mean(wk))}
print("weakness x0.80   n=%d  [%.4f, %.4f]  mean %.4f" % (len(wk), wk[0], wk[-1], np.mean(wk)))
print()

LAD = [(0.050, ["R151S_s%d" % s for s in range(101, 107)]),
       (0.070, ["R393SPg070_s%d" % s for s in range(101, 107)]),
       (0.100, ["R393SPg100_s%d" % s for s in range(101, 107)]),
       (0.110, ["R396SPg110_s%d" % s for s in (101, 102, 105, 106)]),
       (0.120, ["R396SPg120_s%d" % s for s in (101, 102, 105, 106)]),
       (0.130, ["R396SPg130_s%d" % s for s in (101, 102, 105, 106)])]

print("%-8s %-4s %-22s %-10s %-9s %s" % ("KV", "n", "spastic range", "mean", "gap", "vs MDC"))
rows = []
for kv, pre in LAD:
    v, c = arm(pre)
    res["cells"].update(c)
    if not v:
        print("  %-6.3f %-4s %-22s %-10s %-9s %s" % (kv, 0, "-", "-", "-", "no Gate-G cell"))
        res.setdefault("rungs", {})[str(kv)] = {"n": 0}
        continue
    m = float(np.mean(v))
    gap = res["weakness_x080"]["mean"] - m
    edge = wk[0] - v[-1]          # nearest-edge gap, the disjointness margin
    rows.append((kv, m, gap, len(v)))
    res.setdefault("rungs", {})[str(kv)] = {
        "n_gate_G": len(v), "range": [v[0], v[-1]], "mean": m,
        "gap_vs_x080_mean_deg": gap, "nearest_edge_gap_deg": edge,
        "reaches_MDC": bool(gap >= MDC)}
    print("  %-6.3f %-4d [%.4f, %.4f]   %-10.4f %-9.4f %s   edge %+.4f"
          % (kv, len(v), v[0], v[-1], m, gap,
             "REACHED" if gap >= MDC else "%.0f%%" % (100 * gap / MDC), edge))

x = np.array([r[0] for r in rows]); y = np.array([r[2] for r in rows])
b, cst = np.polyfit(x, y, 1)
res["fit"] = {"slope_deg_per_KV": float(b), "intercept_deg": float(cst),
              "pearson_r": float(np.corrcoef(x, y)[0, 1]),
              "KV_for_MDC": float((MDC - cst) / b),
              "n_points": len(rows)}
print()
print("fit over %d chained rungs: gap = %.3f*KV %+.3f   r = %.4f"
      % (len(rows), b, cst, res["fit"]["pearson_r"]))
print("KV needed for %.1f deg   : %.4f" % (MDC, res["fit"]["KV_for_MDC"]))
res["highest_walking_KV"] = 0.120
res["VERDICT"] = ("NOT REACHED -- the highest KV with Gate-G cells is 0.120 and the fit needs "
                  "%.4f" % res["fit"]["KV_for_MDC"]) if not any(
    r[2] >= MDC for r in rows) else "REACHED"
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print("VERDICT: %s" % res["VERDICT"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
