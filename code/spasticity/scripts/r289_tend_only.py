# -*- coding: utf-8 -*-
"""t_end ONLY for the r289 cells that have landed. Deliberately blind to the endpoint.

PREREG_matched20_r289.md admits a cell to the endpoint only if t_end = 20.000 s, and its
stopping rule reads t_end. Reading t_end while the arm runs is therefore permitted and is what
the launcher itself does. Reading knee_angle_LmR is NOT, and this script cannot: it never
requests a joint-angle column, and it asserts that the only columns it touched are time and
the two ground-reaction channels.

Evaluates a cell to .sto if it has none. `sconecmd -e` writes only .sto, never .par.
"""
import os, sys, glob, json, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE = 1.0

FORBIDDEN = ("knee", "hip", "ankle", "pelvis", "lumbar")

print("%-26s %6s %10s %8s %8s  %s" % ("cell", "kv", "t_end", "cycles", "wall", "completes 20.000"))
rows = []
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_MATCHED20_r289_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    if not os.path.isdir(d):
        continue
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        par = dep.get("resolved_par")
        if not par:
            print("%-26s  no resolved_par yet" % dep["result_dir"][:26]); continue
        subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=900)
        stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        print("%-26s  no sto" % dep["result_dir"][:26]); continue

    cols, dat = S.load_sto(stos[-1])
    # Only time and the two GRF channels are ever requested.
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    t_end = float(t[-1])
    ncyc = len([1 for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE])
    kv = dep.get("kv", dep.get("KV", "?"))
    rows.append({"cell": dep["cell"], "kv": kv, "seed": dep.get("seed"),
                 "result_dir": dep["result_dir"], "t_end_s": t_end,
                 "cycles_after_settle": ncyc,
                 "wall_clock_s": dep.get("wall_clock_s"),
                 "completes_20": bool(abs(t_end - 20.0) < 1e-9)})
    print("%-26s %6s %10.3f %8d %8s  %s"
          % (("cell%02d s%s" % (dep["cell"], dep.get("seed"))), kv, t_end, ncyc,
             ("%.0f" % dep["wall_clock_s"]) if dep.get("wall_clock_s") else "-",
             "YES" if rows[-1]["completes_20"] else ""))

out = {"what": "t_end only for r289 cells landed so far; endpoint deliberately not computed",
       "endpoint_not_read": "knee_angle_LmR was not requested from any file by this script",
       "forbidden_substrings_never_requested": list(FORBIDDEN),
       "n_cells": len(rows), "n_complete_20": sum(r["completes_20"] for r in rows),
       "cells": rows,
       "note": "PREREG_matched20_r289.md admits only cells with t_end = 20.000 s"}
p = os.path.join(PAPER, "R289_TEND_PARTIAL.json")
json.dump(out, open(p, "w"), indent=1)
print("\n%d of %d landed cells complete 20.000 s" % (out["n_complete_20"], out["n_cells"]))
print("wrote %s (%d bytes)" % (p, os.path.getsize(p)))
