# -*- coding: utf-8 -*-
"""F5 VERIFICATION -- is the dose-matching scale s* void?

Claim under test: SCONE's MuscleReflex reads <muscle>.V, and V = 10 x ce_vel_norm.
dose_r174.py uses ce_vel_norm, so the SPASTIC dose is one tenth of the reflex's true input
while the WEAK dose -- (1-s) x tib_ant force -- is on the true scale. If so the two arms were
never on a common scale and s* = 1 - spastic/tib_ant may be negative.

Reproduces dose_r174.py's construction EXACTLY (its lines 63-73), then re-runs it with the
corrected velocity channel. dose_r174.py is a REGISTERED script and is NOT edited; this is a
separate read-only verification.
"""
import io
import os
import sys
import glob
import json
import hashlib

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE, T1 = 1.0, 13.58            # dose_r174.py's own window
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

    ta = np.asarray(S.col(cols, dat, "tib_ant_l.F"), dtype=float)[a:b] * FMAX["tib_ant_l"]
    out = {"seed": s, "n_cycles": len(cyc),
           "tib_ant_mean_force_N": float(np.mean(np.abs(ta)))}

    for label, chan, fac in (("as_registered_ce_vel", "ce_vel_norm", 1.0),
                             ("corrected_V", "ce_vel_norm", 10.0)):
        add = np.zeros(b - a)
        clipped = 0
        for m in ("soleus_l", "gastroc_l"):
            v = np.asarray(S.col(cols, dat, m + "." + chan), dtype=float)[a:b] * fac
            u = np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]
            raw = KV * np.maximum(0.0, v)
            du = np.minimum(raw, np.maximum(0.0, 1.0 - u))
            clipped += int(np.sum(raw > du + 1e-12))
            add = add + du * FMAX[m]
        out[label] = float(np.mean(add))
        out[label + "_clipped_samples"] = clipped
    # sanity: does the .V channel agree with 10 x ce_vel_norm here?
    if "soleus_l.V" in cols:
        vv = np.asarray(dat[:, cols.index("soleus_l.V")], dtype=float)[a:b]
        cc = np.asarray(S.col(cols, dat, "soleus_l.ce_vel_norm"), dtype=float)[a:b]
        k = np.abs(cc) > 1e-6
        out["V_over_ce_vel_median"] = float(np.median(vv[k] / cc[k]))
    return out


def main():
    rows = [per_seed(s) for s in SEEDS]
    ta = float(np.mean([r["tib_ant_mean_force_N"] for r in rows]))
    reg = float(np.mean([r["as_registered_ce_vel"] for r in rows]))
    cor = float(np.mean([r["corrected_V"] for r in rows]))

    res = {"window": [SETTLE, T1], "kv": KV, "fmax": FMAX,
           "tib_ant_mean_force_N": ta,
           "spastic_dose_as_registered_N": reg,
           "spastic_dose_corrected_V_N": cor,
           "ratio_corrected_over_registered": cor / reg if reg else None,
           "s_star_as_registered": 1.0 - reg / ta,
           "s_star_corrected": 1.0 - cor / ta,
           "s_star_corrected_is_negative": bool((1.0 - cor / ta) < 0.0),
           "per_seed": rows}
    p = os.path.join(PAPER, "VERIFY_F5_r231.json")
    json.dump(res, io.open(p, "w", encoding="utf-8"), indent=1)

    print("control seeds: %d   window [%.2f, %.2f]   KV = %.3f" % (len(rows), SETTLE, T1, KV))
    print("V / ce_vel_norm on control cells: %r"
          % [round(r.get("V_over_ce_vel_median", float('nan')), 4) for r in rows])
    print()
    print("  tib_ant_l mean force            : %10.3f N" % ta)
    print("  spastic dose AS REGISTERED      : %10.3f N   (dose_r174.py, ce_vel_norm)" % reg)
    print("  spastic dose CORRECTED (V=10x)  : %10.3f N" % cor)
    print("  ratio corrected / registered    : %10.3f  (NOT 10 -- the 1-u clip binds)" % (cor / reg))
    print()
    print("  s* as registered                : %10.4f" % (1.0 - reg / ta))
    print("  s* corrected                    : %10.4f  %s"
          % (1.0 - cor / ta, "<-- NEGATIVE: no weakness scale in [0,1] matches"
             if (1.0 - cor / ta) < 0 else ""))
    print()
    print("clipped samples per seed (registered / corrected):")
    for r in rows:
        print("   s%d  %6d / %6d" % (r["seed"], r["as_registered_ce_vel_clipped_samples"],
                                     r["corrected_V_clipped_samples"]))
    print("\nwrote %s" % p)


if __name__ == "__main__":
    main()
