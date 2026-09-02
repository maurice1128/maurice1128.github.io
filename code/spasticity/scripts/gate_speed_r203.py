# -*- coding: utf-8 -*-
"""GATE G ONLY for PREREG_3d_speed_r203.md. No endpoints computed here.

G1 completion : history.txt >= 91 lines AND tag resolves to exactly one such dir
G2 duration   : >= 9.73 s  (r172's KV0.150 cells all reached 90 gens and lasted 0.66 s)
G3 cycles     : >= 4 admitted gait cycles in the window, left vGRF heel strikes
"""
import os, sys, glob, json
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SPEEDS = [("V080", 0.80), ("V105", 1.05), ("V130", 1.30)]
ARMS = [("C", "control"), ("S", "spastic"), ("W", "weak")]
SETTLE, T1 = 1.00, 13.58
MIN_DUR, MIN_CYC = 9.73, 4


def hist(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in open(h, errors="replace")) if os.path.exists(h) else 0


def rdir(tag):
    g = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
         if os.path.isdir(d) and hist(d) >= 91]
    if len(g) > 1:
        raise SystemExit("tag %s -> %d dirs" % (tag, len(g)))
    return g[0] if g else None


def cell(tag):
    d = rdir(tag)
    if d is None:
        return {"tag": tag, "G1": False, "why": "no complete dir"}
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not sto:
        return {"tag": tag, "G1": True, "G2": False, "why": "no .sto"}
    cols, dat = S.load_sto(sto[-1])
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    dur = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    if len(cyc) >= 2:
        cyc = cyc[:-1]
    return {"tag": tag, "G1": True, "dur": dur, "G2": dur >= MIN_DUR,
            "ncyc": len(cyc), "G3": len(cyc) >= MIN_CYC,
            "pass": dur >= MIN_DUR and len(cyc) >= MIN_CYC}


rows = {}
for vt, v in SPEEDS:
    for a, an in ARMS:
        for s in SEEDS:
            tag = "R203%s%s_s%d" % (vt, a, s)
            rows[tag] = cell(tag)

print("=" * 92)
print("GATE G -- PREREG_3d_speed_r203.md.  NO ENDPOINT IS COMPUTED IN THIS SCRIPT.")
print("=" * 92)
print("G1 history.txt >= 91 | G2 duration >= %.2f s | G3 admitted cycles >= %d" % (MIN_DUR, MIN_CYC))
print("window [%.2f, %.2f]\n" % (SETTLE, T1))
print("%-10s %-8s  %-28s %-24s %s" % ("speed", "arm", "duration s (6 seeds)", "cycles", "ADMITTED"))
tbl = {}
for vt, v in SPEEDS:
    for a, an in ARMS:
        rs = [rows["R203%s%s_s%d" % (vt, a, s)] for s in SEEDS]
        du = [r.get("dur", 0.0) for r in rs]
        nc = [r.get("ncyc", 0) for r in rs]
        ok = sum(1 for r in rs if r.get("pass"))
        tbl["%s_%s" % (vt, a)] = ok
        print("%-10s %-8s  %-28s %-24s %d/6" % (
            "%.2f" % v, an,
            "%.2f-%.2f" % (min(du), max(du)),
            "%d-%d" % (min(nc), max(nc)), ok))
print()
print("ADMISSION TABLE, cells passing G1+G2+G3 of 6:")
print("%-10s %8s %8s %8s" % ("speed", "control", "spastic", "weak"))
for vt, v in SPEEDS:
    print("%-10s %8d %8d %8d" % ("%.2f" % v, tbl[vt + "_C"], tbl[vt + "_S"], tbl[vt + "_W"]))
print("\ntotal admitted %d of 54" % sum(tbl.values()))
json.dump({"window": [SETTLE, T1], "min_dur": MIN_DUR, "min_cyc": MIN_CYC,
           "cells": rows, "admission": tbl},
          open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\GATE_speed_r203.json", "w"), indent=1)
print("deposited: paper/GATE_speed_r203.json")
