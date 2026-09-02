# -*- coding: utf-8 -*-
"""STEP 2 -- achieved speed per cell, and the registered DROP gate. No endpoints here.

Registered tolerance: |achieved - commanded| <= 0.05 m/s. A cell outside it is DROPPED.
Achieved speed = pelvis forward travel / elapsed time over the admitted window, the same
measure step 1 used on the control corpus.
"""
import os, sys, glob, json
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SPEEDS = [("V080", 0.80), ("V105", 1.05), ("V130", 1.30)]
ARMS = [("C", "control"), ("S", "spastic"), ("W", "weak")]
SETTLE, T1, TOL = 1.00, 13.58, 0.05


def cell(tag):
    d = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)][0]
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    a, b = cyc[0][0], cyc[-1][1]
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    return float((px[b - 1] - px[a]) / (t[b - 1] - t[a]))


rows, tbl = {}, {}
for vt, v in SPEEDS:
    for a, an in ARMS:
        vals = []
        for s in SEEDS:
            tag = "R203%s%s_s%d" % (vt, a, s)
            ach = cell(tag)
            keep = abs(ach - v) <= TOL
            rows[tag] = {"cmd": v, "achieved": ach, "err": ach - v, "keep": bool(keep)}
            vals.append((ach, keep))
        tbl["%s_%s" % (vt, a)] = vals

print("=" * 96)
print("STEP 2 -- ACHIEVED SPEED AND THE DROP GATE.  NO ENDPOINT IS COMPUTED HERE.")
print("=" * 96)
print("registered tolerance |achieved - commanded| <= %.2f m/s; outside -> DROPPED\n" % TOL)
print("%-8s %-8s %-22s %-20s %s" % ("cmd", "arm", "achieved (6 seeds)", "mean err", "KEPT"))
for vt, v in SPEEDS:
    for a, an in ARMS:
        vals = tbl["%s_%s" % (vt, a)]
        ach = [x for x, _ in vals]
        keep = sum(1 for _, k in vals if k)
        print("%-8s %-8s %-22s %+.4f              %d/6" % (
            "%.2f" % v, an, "%.4f-%.4f" % (min(ach), max(ach)),
            float(np.mean(ach)) - v, keep))
print()
print("KEPT AFTER THE DROP GATE, of 6:")
print("%-10s %8s %8s %8s" % ("cmd", "control", "spastic", "weak"))
for vt, v in SPEEDS:
    r = [sum(1 for _, k in tbl["%s_%s" % (vt, a)] if k) for a, _ in ARMS]
    print("%-10s %8d %8d %8d" % ("%.2f" % v, r[0], r[1], r[2]))
tot = sum(1 for r in rows.values() if r["keep"])
print("\ntotal kept %d of 54  (dropped %d)" % (tot, 54 - tot))
json.dump({"tolerance": TOL, "window": [SETTLE, T1], "cells": rows},
          open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPEEDGATE_r203.json", "w"), indent=1)
print("deposited: paper/SPEEDGATE_r203.json")
