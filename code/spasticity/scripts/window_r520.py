# -*- coding: utf-8 -*-
"""r520: is an early-stance WINDOW a better readout than the contact instant?

The contact instant inherits whatever error the event detector has -- in impaired populations only
89% of kinematic events land within two frames of the force-plate standard [23]. A window mean over
early stance averages that away. Figure 1B shows the hyperreflexia trace below the others across the
whole first 15%, not only at the instant, so the window is worth testing directly.

For every admissible cell this computes the mean knee angle over 0-5%, 0-10%, 0-15%, 0-20% and
5-20% of each kept cycle, and scores each window the way the contact instant is scored: arm
difference, cell-level gap, disjointness, and the gap in units of the within-cell seed SD.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
WINDOWS = [("instant", 0, 0), ("0-5%", 0, 5), ("0-10%", 0, 10), ("0-15%", 0, 15),
           ("0-20%", 0, 20), ("5-20%", 5, 20)]


def cells(fam):
    out = []
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g: continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st: continue
        c, dat = S.load_sto(st[-1])
        if dat.size == 0: continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(c, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k+1]) for k in range(len(hs)-1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5: continue
        kn = np.degrees(S.col(c, dat, "knee_angle_l"))
        row = {"fam": fam}
        for name, lo, hi in WINDOWS:
            vals = []
            for a, b in w:
                if hi == 0:
                    vals.append(kn[a])
                else:
                    n = b - a
                    i0, i1 = a + int(round(n * lo / 100.0)), a + max(int(round(n * hi / 100.0)), 1)
                    vals.append(float(np.mean(kn[i0:i1])))
            row[name] = float(np.mean(vals))
        out.append(row)
    return out


hy = [c for f in HY for c in cells(f)]
wk = [c for f in WK for c in cells(f)]
print("cells: hyper %d  weak %d\n" % (len(hy), len(wk)))
print("%-9s %9s %9s %9s %10s %9s %8s"
      % ("window", "hyper", "weak", "arm diff", "cell gap", "seed SD", "gap/SD"))
res = {}
for name, lo, hi in WINDOWS:
    a = [c[name] for c in hy]; b = [c[name] for c in wk]
    sds = []
    for f in HY + WK:
        v = [c[name] for c in (hy + wk) if c["fam"] == f]
        if len(v) > 1: sds.append(np.std(v, ddof=1))
    sd = float(np.mean(sds))
    gap = float(min(b) - max(a))
    res[name] = {"hyper_mean": float(np.mean(a)), "weak_mean": float(np.mean(b)),
                 "arm_difference_deg": float(np.mean(a) - np.mean(b)),
                 "cell_gap_deg": gap, "cells_disjoint": bool(max(a) < min(b)),
                 "mean_within_cell_seed_SD_deg": sd, "gap_in_seed_SD": gap / sd}
    print("%-9s %9.3f %9.3f %9.3f %10.3f %9.3f %8.2f"
          % (name, np.mean(a), np.mean(b), np.mean(a) - np.mean(b), gap, sd, gap / sd))

io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\WINDOW_r520.json", "w",
        encoding="utf-8", newline="").write(json.dumps(
    {"id": "WINDOW_r520",
     "why": ("the contact instant inherits the event detector's error; a window mean averages it "
             "away. This scores early-stance windows the way the instant is scored."),
     "windows": res}, indent=1, ensure_ascii=False))
