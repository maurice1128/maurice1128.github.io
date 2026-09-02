# -*- coding: utf-8 -*-
"""UPSTREAM lesion dose, evaluated on the CONTROL trajectory only.

Why upstream. Let L = lesion, Z = optimiser seed/basin, G = achieved gait, F = fitness, Y = endpoint.
The causal structure is L -> G, Z -> G, G -> F, G -> Y. Fitness, duration, speed and cost are all
CHILDREN of G, so matching on any of them partially conditions on G and therefore partially blocks
the very path L -> G -> Y that the experiment measures. That is "matching away the answer" in its
general form, and it disqualifies every gait-derived metric, not only the endpoints.

This metric is a property of the LESION applied to a FIXED reference trajectory -- the control arm's
own gait -- so it is upstream of G for both arms and identical in construction for both.

  weak dose at scale s      = mean over cycles of (1 - s) * tib_ant_l force actually used
  spastic dose at KV        = mean over cycles of the reflex-added force on soleus + gastroc,
                              KV * max(0, ce_vel_norm) * max_isometric_force, added excitation
                              clipped to <= 1 - resting excitation

Both are in newtons of muscle force on the SAME trajectory. Reads control cells only; no simulation.
"""
import io
import os
import sys
import glob
import json
import math

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE, T1 = 1.0, 13.58
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0, "tib_ant_l": 1759.0}
KV = 0.050


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


def per_seed(s):
    d = ctrl_dir(s)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    cyc = cycles(cols, dat, t)
    a, b = cyc[0][0], cyc[-1][1]

    # UNITS: <muscle>.F is IDENTICAL to <muscle>.mtu_force_norm in these files -- it is force
    # NORMALISED by max_isometric_force, NOT newtons. Verified by comparing the two channels.
    # The first version of this script treated it as newtons and returned a tib_ant mean of
    # 0.072 N for a 1759 N muscle, which is the r145 radians-as-degrees class.
    ta_F = np.asarray(S.col(cols, dat, "tib_ant_l.F"), dtype=float)[a:b] * FMAX["tib_ant_l"]
    out = {"tib_ant_mean_force": float(np.mean(np.abs(ta_F))), "n_cycles": len(cyc)}

    add = np.zeros(b - a)
    for m in ("soleus_l", "gastroc_l"):
        v = np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), dtype=float)[a:b]
        u = np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]
        du = KV * np.maximum(0.0, v)
        du = np.minimum(du, np.maximum(0.0, 1.0 - u))       # excitation cannot exceed 1
        add = add + du * FMAX[m]
        out[m + "_pos_vel_frac"] = float(np.mean(v > 0))
        out[m + "_mean_added_N"] = float(np.mean(du * FMAX[m]))
    out["spastic_dose_N"] = float(np.mean(add))
    return out


rows = [per_seed(s) for s in SEEDS]
ta = float(np.mean([r["tib_ant_mean_force"] for r in rows]))
sp = float(np.mean([r["spastic_dose_N"] for r in rows]))
sp_lo = min(r["spastic_dose_N"] for r in rows)
sp_hi = max(r["spastic_dose_N"] for r in rows)

print("=" * 84)
print("UPSTREAM DOSE on the CONTROL trajectory (6 control seeds, window [%.2f, %.2f])"
      % (SETTLE, T1))
print("=" * 84)
for s, r in zip(SEEDS, rows):
    print("  C_%d  cycles %2d  tib_ant mean force %8.2f N   spastic added %7.2f N"
          " (sol %6.2f + gas %6.2f)  pos-vel frac sol %.3f gas %.3f"
          % (s, r["n_cycles"], r["tib_ant_mean_force"], r["spastic_dose_N"],
             r["soleus_l_mean_added_N"], r["gastroc_l_mean_added_N"],
             r["soleus_l_pos_vel_frac"], r["gastroc_l_pos_vel_frac"]))
print("\n  tib_ant_l mean force on control gait : %8.3f N" % ta)
print("  spastic dose at KV = %.3f            : %8.3f N   [seed range %.3f, %.3f]"
      % (KV, sp, sp_lo, sp_hi))

print("\n  weak dose (1 - s) * %.3f N, and the scale that matches the spastic dose:" % ta)
for s in (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.50):
    print("    x%.2f -> %8.3f N %s" % (s, (1 - s) * ta,
                                       "  <-- nearest above" if (1 - s) * ta >= sp else ""))
smatch = 1.0 - sp / ta
print("\n  MATCHING SCALE  s* = 1 - dose/force = %.4f" % smatch)
print("  i.e. tib_ant_l x %.3f  ->  max_isometric_force %.1f N" % (smatch, 1759.0 * smatch))

json.dump({"window": [SETTLE, T1], "kv": KV, "fmax": FMAX,
           "tib_ant_mean_force_N": ta, "spastic_dose_N": sp,
           "spastic_dose_seed_range": [sp_lo, sp_hi],
           "matching_scale": smatch, "per_seed": rows},
          io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\DOSE_r174.json",
                  "w", encoding="utf-8"), indent=1)
print("\nwrote DOSE_r174.json")
