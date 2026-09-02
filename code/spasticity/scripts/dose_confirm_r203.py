# -*- coding: utf-8 -*-
"""STEP 3 -- dose CONFIRMATION, not a linearity test.

The manipulation failed (step 2): achieved speed is flat. This script asks only whether the
delivered provocation is flat too. If it is, the loop closes: no speed change -> no fibre
velocity change -> no dose change -> the provocation was never delivered.

Method copied from dose_r174.py / speed_dose_r200.py, unmodified, including the clamp.
"""
import os, sys, glob, json
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SPEEDS = [("V080", 0.80), ("V105", 1.05), ("V130", 1.30)]
ARMS = [("C", "control"), ("S", "spastic"), ("W", "weak")]
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
SETTLE, T1, KV = 1.00, 13.58, 0.050


def cell(tag):
    d = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)][0]
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    a, b = cyc[0][0], cyc[-1][1]
    vt, add = 0.0, None
    for m in FMAX:
        v = np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), dtype=float)[a:b]
        u = np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]
        vt += float(np.mean(np.maximum(0.0, v)))
        du = np.minimum(KV * np.maximum(0.0, v), np.maximum(0.0, 1.0 - u))
        add = du * FMAX[m] if add is None else add + du * FMAX[m]
    return vt, float(np.mean(add))


rows = {}
print("=" * 96)
print("STEP 3 -- DOSE CONFIRMATION.  The manipulation failed at step 2; this only asks whether")
print("          the delivered provocation is flat as well.  NOT a test of linearity.")
print("=" * 96)
print("%-8s %-9s %-26s %-26s" % ("cmd", "arm", "sum mean max(0,ce_vel_norm)", "dose at KV 0.050 (N)"))
for vtag, v in SPEEDS:
    for a, an in ARMS:
        vts, ds = [], []
        for s in SEEDS:
            tag = "R203%s%s_s%d" % (vtag, a, s)
            x, y = cell(tag)
            rows[tag] = {"cmd": v, "arm": an, "vel_term": x, "dose_N_at_kv050": y}
            vts.append(x); ds.append(y)
        print("%-8.2f %-9s %-26s %-26s" % (
            v, an, "%.5f  [%.5f, %.5f]" % (np.mean(vts), min(vts), max(vts)),
            "%.3f  [%.3f, %.3f]" % (np.mean(ds), min(ds), max(ds))))
print()
print("CHANGE FROM COMMAND 0.80 TO COMMAND 1.30:")
for a, an in ARMS:
    lo = np.mean([rows["R203V080%s_s%d" % (a, s)]["dose_N_at_kv050"] for s in SEEDS])
    hi = np.mean([rows["R203V130%s_s%d" % (a, s)]["dose_N_at_kv050"] for s in SEEDS])
    print("  %-9s dose %.3f -> %.3f N   change %+.3f N  (%+.1f %%)" % (an, lo, hi, hi - lo, 100 * (hi - lo) / lo))
print()
print("THE REGISTERED LINE predicted 13.340 N per (m/s) x achieved speed.")
print("It is NOT tested here: with achieved speed flat, the line has no range to be tested over.")
json.dump({"kv": KV, "window": [SETTLE, T1], "cells": rows},
          open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\DOSECONF_r203.json", "w"), indent=1)
print("deposited: paper/DOSECONF_r203.json")
