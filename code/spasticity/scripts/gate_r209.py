# -*- coding: utf-8 -*-
"""GATE G ONLY for PREREG_3d_replication_r209.md. No endpoint computed here.

G1 history.txt >= 91 lines AND tag resolves to exactly one such dir
G2 duration >= 9.73 s
G3 >= 4 admitted cycles in [1.00, 13.58]
Uses analyse_ladder_r169.py's OWN cycles_in(), exec'd definitions-only.
"""
import os, sys, glob, json
SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\analyse_ladder_r169.py"
src = open(SRC, encoding="utf-8").read()
ns = {"__name__": "_defs_only"}
exec(compile(src[:src.index("# ================================================== 0. selection + replay")],
             SRC, "exec"), ns)
cycles_in, S = ns["cycles_in"], ns["S"]

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1, MIN_DUR, MIN_CYC = 1.00, 13.58, 9.73, 4

print("=" * 88)
print("GATE G -- PREREG_3d_replication_r209.md.  NO ENDPOINT IS COMPUTED HERE.")
print("=" * 88)
print("%-8s %8s %8s %7s %7s %7s %8s" % ("seed", "lines", "t_end", "ncyc", "G1", "G2", "G3"))
rows, npass = {}, 0
for s in range(201, 207):
    g = [d for d in glob.glob(os.path.join(RES, "R209S_s%d.*" % s)) if os.path.isdir(d)]
    n = [d for d in g if sum(1 for _ in open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(n) != 1:
        print("%-8d tag resolves to %d complete dirs -> G1 FAIL" % (s, len(n))); continue
    d = n[0]
    lines = sum(1 for _ in open(os.path.join(d, "history.txt"), errors="replace"))
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, T1)
    g1, g2, g3 = bool(lines >= 91), bool(t[-1] >= MIN_DUR), bool(len(cyc) >= MIN_CYC)
    ok = g1 and g2 and g3
    npass += ok
    rows["s%d" % s] = {"lines": lines, "t_end": float(t[-1]), "ncyc": len(cyc),
                       "G1": g1, "G2": g2, "G3": g3, "pass": bool(ok)}
    print("%-8d %8d %8.2f %7d %7s %7s %7s" %
          (s, lines, t[-1], len(cyc), "YES" if g1 else "NO", "YES" if g2 else "NO", "YES" if g3 else "NO"))
print("\nPASSING CELLS: %d of 6" % npass)
band = {6: (-2.941, -1.117), 5: (-2.985, -1.073), 4: (-3.048, -1.009)}
if npass >= 4:
    lo, hi = band[npass]
    print("REGISTERED BAND SELECTED BY n_new = %d:  [%.3f, %.3f]" % (npass, lo, hi))
    print("  (fixed before the data; not chosen now)")
else:
    print("n_new < 4 -> UNDERPOWERED, no reproduction verdict (registration section 6)")
json.dump({"min_dur": MIN_DUR, "min_cyc": MIN_CYC, "window": [SETTLE, T1],
           "cells": rows, "n_pass": npass},
          open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\GATE_r209.json", "w"), indent=1)
print("deposited paper/GATE_r209.json")
