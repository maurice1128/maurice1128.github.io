# -*- coding: utf-8 -*-
"""r494: the family-level inference the manuscript reports, computed and deposited.

A cold statistical reader found that the leave-one-family-out classification, the family-level
permutation p, the family-level Welch interval and the arm means existed only as sentences in the
manuscript, while the Declarations claim every analysis script and output is available. This script
is that container. It recomputes all of them from the archived .sto files.

Unit of analysis is the lesion FAMILY, not the cell: cells within a family share an optimisation
lineage and are not independent.
"""
import glob
import itertools
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\FAMILY_LEVEL_r494.json"
SETTLE, T1 = 1.0, 9.73
SP = [("R151S", 0.050), ("R393SPg070", 0.070), ("R393SPg100", 0.100),
      ("R396SPg110", 0.110), ("R396SPg120", 0.120)]
WK = [("R151W", 0.800), ("R174W870", 0.870), ("R174W892", 0.892),
      ("R169W090", 0.900), ("R174W915", 0.915), ("R169W095", 0.950)]


def knee_cells(fam):
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
        out.append(float(np.mean([kn[i] for i, _ in w])))
    return out


fam = {}
for f, _ in SP + WK:
    v = knee_cells(f)
    if v:
        fam[f] = v
names_sp = [f for f, _ in SP if f in fam]
names_wk = [f for f, _ in WK if f in fam]
means = {f: float(np.mean(v)) for f, v in fam.items()}
a = np.array([means[f] for f in names_sp])
b = np.array([means[f] for f in names_wk])

# ---- arm means and the family-level Welch interval ------------------------------------------------
na, nb = len(a), len(b)
va, vb = a.var(ddof=1), b.var(ddof=1)
diff = a.mean() - b.mean()
se = math.sqrt(va / na + vb / nb)
df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
try:
    from scipy import stats
    tcrit = float(stats.t.ppf(0.975, df))
except Exception:                                    # no scipy: bisect the Student-t quantile
    def _cdf(x, k):
        n = 20000
        u = np.linspace(-40, x, n)
        lg = (math.lgamma((k + 1) / 2.0) - math.lgamma(k / 2.0) - 0.5 * math.log(k * math.pi))
        return float(np.trapezoid(np.exp(lg - (k + 1) / 2.0 * np.log1p(u * u / k)), u))
    lo, hi = 0.0, 20.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _cdf(mid, df) < 0.975:
            lo = mid
        else:
            hi = mid
    tcrit = 0.5 * (lo + hi)
ci = (diff - tcrit * se, diff + tcrit * se)

# ---- exhaustive family-level permutation ----------------------------------------------------------
allm = list(a) + list(b)
obs = abs(diff)
tot = hit = 0
for idx in itertools.combinations(range(len(allm)), na):
    g1 = np.array([allm[i] for i in idx])
    g2 = np.array([allm[i] for i in range(len(allm)) if i not in idx])
    tot += 1
    if abs(g1.mean() - g2.mean()) >= obs - 1e-12:
        hit += 1

# ---- leave-one-family-out classification ----------------------------------------------------------
ok = tot_cells = 0
per_family = {}
for held in names_sp + names_wk:
    tr_sp = [means[f] for f in names_sp if f != held]
    tr_wk = [means[f] for f in names_wk if f != held]
    thr = 0.5 * (np.mean(tr_sp) + np.mean(tr_wk))
    truth_sp = held in names_sp
    good = sum(1 for v in fam[held] if (v < thr) == truth_sp)
    per_family[held] = {"n_cells": len(fam[held]), "correct": good,
                        "threshold_deg": float(thr), "all_correct": good == len(fam[held])}
    ok += good
    tot_cells += len(fam[held])

dep = {
 "id": "FAMILY_LEVEL_r494",
 "why": ("The manuscript's strongest inferential statements had no container. A cold reader "
         "reproduced them from family means and they were correct, but nothing on disk computed "
         "them. This script does."),
 "unit_of_analysis": "lesion family (cells within a family share an optimisation lineage)",
 "families": {f: {"n_cells": len(v), "mean_knee_ic_deg": means[f]} for f, v in fam.items()},
 "arm_means_deg": {"hyperreflexia": float(a.mean()), "weakness": float(b.mean())},
 "difference_deg": float(diff),
 "welch": {"se": float(se), "df": float(df), "t_crit_0.975": float(tcrit),
           "ci95_deg": [float(ci[0]), float(ci[1])]},
 "permutation": {"design": "exhaustive, C(%d,%d)" % (len(allm), na), "n_splits": tot,
                 "n_at_least_as_extreme": hit, "p": hit / float(tot),
                 "resolution_floor": 1.0 / tot,
                 "note": "p cannot go below the floor; this is the design's resolution, not strength"},
 "leave_one_family_out": {"cells_correct": ok, "cells_total": tot_cells,
                          "accuracy": ok / float(tot_cells),
                          "families_all_correct": sum(1 for v in per_family.values() if v["all_correct"]),
                          "families_total": len(per_family), "per_family": per_family},
}
io_open = open(OUT, "w", encoding="utf-8", newline="")
io_open.write(json.dumps(dep, indent=2, ensure_ascii=False))
io_open.close()
print(json.dumps({k: dep[k] for k in
                  ["arm_means_deg", "difference_deg", "welch", "permutation"]}, indent=2))
print("LOFO %d/%d = %.4f, families all-correct %d/%d"
      % (ok, tot_cells, ok / float(tot_cells),
         dep["leave_one_family_out"]["families_all_correct"], len(per_family)))
