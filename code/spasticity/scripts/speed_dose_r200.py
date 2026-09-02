# -*- coding: utf-8 -*-
"""STEP 1: does GAIT SPEED reach KV 0.150's delivered dose at fixed KV 0.050?

Read-only. No simulation. Reads the six CONTROL cells (R151C_s101..106) only.

Delivered dose uses the REGISTERED method, copied from dose_r174.py without modification:

    du = KV * max(0, ce_vel_norm)                 per muscle
    du = min(du, max(0, 1 - excitation))          excitation cannot exceed 1   <-- THE CLAMP
    dose_N = mean over the window of sum_m du * Fmax[m]     for m in soleus_l, gastroc_l

The speed question, stated exactly:
  The reflex is velocity-gated, so at FIXED KV the delivered dose rises with fibre velocity.
  If gait kinematics TIME-SCALE with speed, then ce_vel_norm scales linearly with speed, and
  a speed multiplier k multiplies the PRE-CLAMP term by k.
  We therefore evaluate dose(KV=0.050, v -> k*v) against dose(KV=0.150, v) on the same trajectory.

  ** THE TIME-SCALING ASSUMPTION IS AN ASSUMPTION, NOT A MEASUREMENT. **
  Real gait does not perfectly time-scale; stride length and duty factor both change with speed.
  This computation therefore gives an OPTIMISTIC bound on what speed can deliver: it credits speed
  with a proportional rise in fibre velocity that a real faster gait may not produce.
  A bound that fails is conclusive; a bound that succeeds would still need runs.
"""
import os
import sys
import glob
import json

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE, T1 = 1.0, 13.58
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
KV_LO, KV_HI = 0.050, 0.150


def ctrl_dir(s):
    g = [d for d in glob.glob(os.path.join(RESULTS, "R151C_s%d.*" % s)) if os.path.isdir(d)]
    g = [d for d in g if os.path.exists(os.path.join(d, "history.txt"))]
    return sorted(g)[0]


def cycles(cols, dat, t):
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    return c[:-1] if len(c) >= 2 else c


def dose(v_by_m, u_by_m, kv, k=1.0):
    """Registered dose formula, with fibre velocity scaled by k."""
    add = None
    for m in FMAX:
        du = kv * np.maximum(0.0, v_by_m[m] * k)
        du = np.minimum(du, np.maximum(0.0, 1.0 - u_by_m[m]))
        term = du * FMAX[m]
        add = term if add is None else add + term
    return float(np.mean(add))


def per_seed(s):
    d = ctrl_dir(s)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    cyc = cycles(cols, dat, t)
    a, b = cyc[0][0], cyc[-1][1]

    v_by_m, u_by_m = {}, {}
    for m in FMAX:
        v_by_m[m] = np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), dtype=float)[a:b]
        u_by_m[m] = np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]

    # achieved gait speed over the same window: pelvis forward travel / elapsed time
    px = None
    for cand in ("pelvis_tx", "com_x", "pelvis_tx_pos"):
        try:
            px = np.asarray(S.col(cols, dat, cand), dtype=float)[a:b]
            used = cand
            break
        except Exception:
            continue
    speed = float((px[-1] - px[0]) / (t[b - 1] - t[a])) if px is not None else float("nan")

    return {"seed": s, "n_cycles": len(cyc), "speed_mps": speed, "speed_channel": used,
            "v": v_by_m, "u": u_by_m, "sto": os.path.basename(sto)}


rows = [per_seed(s) for s in SEEDS]

print("=" * 88)
print("STEP 1  --  can SPEED alone reach KV 0.150's delivered dose at KV 0.050?")
print("=" * 88)
print("containers: 6 control cells R151C_s101..106, newest *.par.sto each, window [%.2f, %.2f]"
      % (SETTLE, T1))
print("method    : dose_r174.py, unmodified, including the excitation clamp")
print("speed     : %s, forward travel / elapsed time over the same window" % rows[0]["speed_channel"])
print()

sp = [r["speed_mps"] for r in rows]
print("achieved gait speed, per seed (m/s): " + ", ".join("%.4f" % x for x in sp))
print("  mean %.4f   range [%.4f, %.4f]" % (np.mean(sp), min(sp), max(sp)))
print()

d_lo = [dose(r["v"], r["u"], KV_LO, 1.0) for r in rows]
d_hi = [dose(r["v"], r["u"], KV_HI, 1.0) for r in rows]
print("delivered dose on the control trajectory, k = 1 (no speed change):")
print("  KV 0.050 : mean %8.3f N   range [%.3f, %.3f]" % (np.mean(d_lo), min(d_lo), max(d_lo)))
print("  KV 0.150 : mean %8.3f N   range [%.3f, %.3f]" % (np.mean(d_hi), min(d_hi), max(d_hi)))
print("  ratio    : %.4f x   (3.0000 would be the unclamped ratio)" % (np.mean(d_hi) / np.mean(d_lo)))
print()

target = np.mean(d_hi)
print("dose at KV 0.050 as fibre velocity is scaled by k (time-scaling assumption):")
print("   k      speed implied (m/s)     dose (N)      vs KV0.150 target")
hit = None
for k in (1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0, 12.0, 20.0):
    dk = float(np.mean([dose(r["v"], r["u"], KV_LO, k) for r in rows]))
    mark = ""
    if hit is None and dk >= target:
        hit = k
        mark = "  <-- reaches"
    print("  %5.2f    %8.3f              %8.3f      %6.1f %%%s"
          % (k, np.mean(sp) * k, dk, 100.0 * dk / target, mark))

print()
# asymptote: k -> infinity means every positive-velocity sample saturates to (1-u)
inf_dose = float(np.mean([
    float(np.mean(sum(np.where(r["v"][m] > 0, np.maximum(0.0, 1.0 - r["u"][m]), 0.0) * FMAX[m]
                      for m in FMAX)))
    for r in rows]))
print("CEILING as k -> infinity (every lengthening sample saturated): %8.3f N" % inf_dose)
print("  KV 0.150 target: %8.3f N    reachable by speed at all: %s"
      % (target, "YES" if inf_dose >= target else "NO"))

out = {"containers": {"control_cells": [ctrl_dir(s) for s in SEEDS],
                      "sto": [r["sto"] for r in rows]},
       "window": [SETTLE, T1],
       "speed_mps": {"per_seed": sp, "mean": float(np.mean(sp))},
       "dose_N": {"KV0.050_k1": float(np.mean(d_lo)), "KV0.150_k1": float(np.mean(d_hi)),
                  "ceiling_k_inf": inf_dose},
       "k_that_reaches_KV0.150": hit,
       "assumption": "fibre velocity scales linearly with gait speed (time-scaling); optimistic bound"}
with open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPEED_DOSE_r200.json", "w") as f:
    json.dump(out, f, indent=1)
print("\ndeposited: paper/SPEED_DOSE_r200.json")
