# -*- coding: utf-8 -*-
"""STEP 2 -- the six new per-cell values and the arm SD. NO VERDICT IN THIS SCRIPT.

Registered reporting requirement of PREREG_3d_replication_r209.md 5b. Deposited and printed
BEFORE the verdict, so a reader can see what a mean-only criterion cannot.

Endpoint: rom(hip_flexion_l) - rom(hip_flexion_r), rom() = degrees(max-min) per admitted cycle,
averaged. analyse_ladder_r169.py's OWN rom() and cycles_in() are used, definitions exec'd only.
"""
import os, sys, glob, json
import numpy as np
SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\analyse_ladder_r169.py"
src = open(SRC, encoding="utf-8").read()
ns = {"__name__": "_defs_only"}
exec(compile(src[:src.index("# ================================================== 0. selection + replay")],
             SRC, "exec"), ns)
rom, cycles_in, S = ns["rom"], ns["cycles_in"], ns["S"]

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.00, 13.58
ANCHOR = {101: -1.575016, 102: -1.558770, 103: -2.858404,
          104: -1.349297, 105: -1.628149, 106: -3.203713}

vals = {}
for s in range(201, 207):
    d = [x for x in glob.glob(os.path.join(RES, "R209S_s%d.*" % s)) if os.path.isdir(x)][0]
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, T1)
    vals[s] = float(rom(cols, dat, "hip_flexion_l", cyc) - rom(cols, dat, "hip_flexion_r", cyc))

v = np.array([vals[s] for s in sorted(vals)])
a = np.array([ANCHOR[s] for s in sorted(ANCHOR)])

print("=" * 84)
print("STEP 2 -- THE SIX NEW PER-CELL VALUES.  NO VERDICT IS STATED IN THIS SCRIPT.")
print("=" * 84)
print("endpoint: rom(hip_flexion_l) - rom(hip_flexion_r), degrees, per-cycle mean\n")
print("%-8s %14s     %-8s %14s" % ("new seed", "value", "anchor", "value"))
for i, s in enumerate(sorted(vals)):
    print("%-8d %14.6f     %-8d %14.6f" % (s, vals[s], 101 + i, a[i]))
print()
print("NEW ARM   mean %+.4f   SD %.4f   range [%+.4f, %+.4f]" %
      (v.mean(), v.std(ddof=1), v.min(), v.max()))
print("ANCHOR    mean %+.4f   SD %.4f   range [%+.4f, %+.4f]" %
      (a.mean(), a.std(ddof=1), a.min(), a.max()))
print()
print("CLUSTER STRUCTURE -- description only, not a test and not a criterion")
print("  anchor : 4 cells near -1.5 (%s) and 2 far out (%s)" %
      (", ".join("%.2f" % x for x in sorted(a)[2:]), ", ".join("%.2f" % x for x in sorted(a)[:2])))
sv = np.sort(v)
gaps = np.diff(sv)
k = int(np.argmax(gaps))
print("  new    : largest gap %.3f between %.3f and %.3f -> %d below, %d above" %
      (gaps[k], sv[k], sv[k + 1], k + 1, len(sv) - k - 1))
print("  new sorted: %s" % ", ".join("%.3f" % x for x in sv))
json.dump({"per_cell": {str(k2): vals[k2] for k2 in sorted(vals)},
           "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
           "min": float(v.min()), "max": float(v.max()),
           "anchor_per_cell": {str(k2): ANCHOR[k2] for k2 in sorted(ANCHOR)},
           "anchor_mean": float(a.mean()), "anchor_sd": float(a.std(ddof=1))},
          open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\CELLS_r209.json", "w"), indent=1)
print("\ndeposited paper/CELLS_r209.json")
