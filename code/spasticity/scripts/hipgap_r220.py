# -*- coding: utf-8 -*-
"""Per-seed hip_flexion_LmR, spastic vs each weakness severity, window [1.00, 9.73].
Read-only. Same measurement path as channels_g2_r219.py."""
import io, os, sys, glob, json, math
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S
RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)
ARMS = {"C": "R151C", "S": "R151S", "W870": "R174W870", "W892": "R174W892", "W915": "R174W915"}

def val(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
    sto = sorted(glob.glob(os.path.join(ds[0], "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k+1]) for k in range(len(idx)-1)
           if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b+1]) - min(v[a:b+1])) for a, b in cyc) / len(cyc)
    return rom("hip_flexion_l") - rom("hip_flexion_r")

V = {a: [val("%s_s%d" % (p, s)) for s in SEEDS] for a, p in ARMS.items()}
out = {"channel": "hip_flexion_LmR", "window": [SETTLE, T1],
       "method": "per-cycle mean ROM(l) - ROM(r), degrees; window [1.00, 9.73]; read-only",
       "per_seed": V}
print("arm    per-seed hip_flexion_LmR (deg)                          mean")
for a in ("C", "S", "W870", "W892", "W915"):
    print("%-6s %s  %+8.4f" % (a, " ".join("%+8.4f" % x for x in sorted(V[a])), np.mean(V[a])))
print()
smax = max(V["S"]); out["spastic_max"] = smax
print("SPASTIC vs WEAK -- gap between arm means, and seed-level overlap")
for w in ("W870", "W892", "W915"):
    wmin = min(V[w]); gap = float(np.mean(V[w]) - np.mean(V["S"]))
    disj = wmin > smax
    out[w] = {"mean_gap_deg": gap, "weak_min": wmin, "spastic_max": smax,
              "seed_gap_deg": wmin - smax, "disjoint_at_seed_level": bool(disj)}
    print("  %s  mean gap %+.4f deg | weak min %+.4f vs spastic max %+.4f -> seed gap %+.4f  %s"
          % (w, gap, wmin, smax, wmin - smax, "DISJOINT" if disj else "OVERLAP"))
allw = V["W870"] + V["W892"] + V["W915"]
out["pooled_weak"] = {"n": len(allw), "min": min(allw),
                      "seed_gap_deg": min(allw) - smax,
                      "disjoint_at_seed_level": bool(min(allw) > smax),
                      "mean_gap_deg": float(np.mean(allw) - np.mean(V["S"]))}
print("  POOLED 18 weak cells vs 6 spastic: mean gap %+.4f | weak min %+.4f -> seed gap %+.4f  %s"
      % (out["pooled_weak"]["mean_gap_deg"], min(allw), min(allw) - smax,
         "DISJOINT" if min(allw) > smax else "OVERLAP"))
json.dump(out, io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\HIPGAP_r220.json",
                       "w", encoding="utf-8"), indent=1)
print("\ndeposited paper/HIPGAP_r220.json")
