# -*- coding: utf-8 -*-
"""r496: score the unlesioned-side negative control on the SAME metric the paper uses to certify
its own families.

The manuscript certifies every lesion family by displacement from control divided by the 0.586 deg
sham artefact. It scores the unlesioned-side control by a different statistic -- cell-range
disjointness -- which is suppressed on the right knee by its larger seed dispersion. An adversarial
reader argued that on the certification metric the control fails from KV 0.100 rather than KV 0.110.
This computes it. Both lesions are LEFT-only; knee_angle_r is sampled at RIGHT heel strike using the
right leg's own GRF, as KNEE_MDC_BATCHNULL_r399 defines the endpoint.
"""
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1, SHAM = 1.0, 9.73, 0.5860145801831838
FAM = [("R151C", "control", 0.0), ("R151S", "spastic", 0.050), ("R393SPg070", "spastic", 0.070),
       ("R393SPg100", "spastic", 0.100), ("R396SPg110", "spastic", 0.110),
       ("R396SPg120", "spastic", 0.120), ("R151W", "weak", 0.800), ("R174W870", "weak", 0.870),
       ("R174W892", "weak", 0.892), ("R169W090", "weak", 0.900), ("R174W915", "weak", 0.915),
       ("R169W095", "weak", 0.950)]


def cells(fam, side):
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
        grf, thr = S.grf_vertical(c, dat, side)
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5:
            continue
        kn = np.degrees(S.col(c, dat, "knee_angle_%s" % side))
        out.append(float(np.mean([kn[i] for i, _ in w])))
    return out


res = {}
for f, arm, dose in FAM:
    res[f] = (arm, dose, cells(f, "l"), cells(f, "r"))
cl = np.mean(res["R151C"][2]) if res["R151C"][2] else None
cr = np.mean(res["R151C"][3]) if res["R151C"][3] else None
print("control  left %+8.3f   right %+8.3f   (n=%d/%d)"
      % (cl, cr, len(res["R151C"][2]), len(res["R151C"][3])))
print()
print("%-12s %6s %4s %4s | %9s %7s | %9s %7s | %s"
      % ("family", "dose", "nL", "nR", "L-ctrl", "x sham", "R-ctrl", "x sham", "R/L"))
sp_l, sp_r, wk_l, wk_r = [], [], [], []
for f, arm, dose in FAM:
    if f == "R151C":
        continue
    a, d, L, R = res[f]
    if not L or not R:
        print("%-12s %6.3f  incomplete (nL=%d nR=%d)" % (f, d, len(L), len(R)))
        continue
    dl, dr = np.mean(L) - cl, np.mean(R) - cr
    print("%-12s %6.3f %4d %4d | %+9.3f %7.2f | %+9.3f %7.2f | %.0f%%"
          % (f, d, len(L), len(R), dl, abs(dl) / SHAM, dr, abs(dr) / SHAM,
             100.0 * abs(dr) / abs(dl) if dl else 0))
    (sp_l if a == "spastic" else wk_l).append(np.mean(L))
    (sp_r if a == "spastic" else wk_r).append(np.mean(R))
print()
print("arm separation   left  %+.3f deg" % (np.mean(sp_l) - np.mean(wk_l)))
print("arm separation   right %+.3f deg" % (np.mean(sp_r) - np.mean(wk_r)))
print("unlesioned side carries %.1f%% of the separation"
      % (100.0 * abs(np.mean(sp_r) - np.mean(wk_r)) / abs(np.mean(sp_l) - np.mean(wk_l))))
print()
print("seed SD  left  %.3f deg" % np.mean([np.std(res[f][2], ddof=1) for f, a, d in FAM
                                           if a != "control" and len(res[f][2]) > 1]))
print("seed SD  right %.3f deg" % np.mean([np.std(res[f][3], ddof=1) for f, a, d in FAM
                                           if a != "control" and len(res[f][3]) > 1]))
