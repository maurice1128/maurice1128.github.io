# -*- coding: utf-8 -*-
"""r501: extract knee and ankle at foot contact for every admissible cell, once, into a cache the
figure script can read. Figure 5 must show cell-level data because the cell-level non-overlap IS the
claim, and re-reading the .sto archive for every redraw is slow enough to discourage redrawing.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\CELL_CACHE_r501.json"
SETTLE, T1 = 1.0, 9.73
# delivered KV = 2 x archived label
FAM = [("R151C", "control", None, None),
       ("R151S", "hyper", 0.100, 1.00), ("R393SPg070", "hyper", 0.140, 1.00),
       ("R393SPg100", "hyper", 0.200, 1.00), ("R396SPg110", "hyper", 0.220, 1.00),
       ("R396SPg120", "hyper", 0.240, 1.00),
       ("R151W", "weak", None, 0.80), ("R174W870", "weak", None, 0.87),
       ("R174W892", "weak", None, 0.892), ("R169W090", "weak", None, 0.90),
       ("R174W915", "weak", None, 0.915), ("R169W095", "weak", None, 0.95)]


def cells(fam):
    out = []
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g:
            continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st:
            continue
        c, dat = S.load_sto(st[-1])
        if dat.size == 0:
            continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(c, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5:
            continue
        kn = np.degrees(S.col(c, dat, "knee_angle_l"))
        an = np.degrees(S.col(c, dat, "ankle_angle_l"))
        out.append({"seed": sd,
                    "knee_ic_deg": float(np.mean([kn[i] for i, _ in w])),
                    "ankle_ic_deg": float(np.mean([an[i] for i, _ in w])),
                    "t_end_s": float(t[-1]), "n_cycles": len(w)})
    return out


cache = {}
for fam, arm, kv, wk in FAM:
    v = cells(fam)
    cache[fam] = {"arm": arm, "kv_delivered": kv, "weak_scale": wk, "cells": v,
                  "n": len(v),
                  "knee_mean": float(np.mean([x["knee_ic_deg"] for x in v])) if v else None,
                  "ankle_mean": float(np.mean([x["ankle_ic_deg"] for x in v])) if v else None,
                  "knee_sd": float(np.std([x["knee_ic_deg"] for x in v], ddof=1)) if len(v) > 1 else None,
                  "ankle_sd": float(np.std([x["ankle_ic_deg"] for x in v], ddof=1)) if len(v) > 1 else None}
    print("%-12s %-8s n=%d" % (fam, arm, len(v)))
io.open(OUT, "w", encoding="utf-8", newline="").write(json.dumps(cache, indent=1, ensure_ascii=False))
print("cache -> %s" % OUT)
