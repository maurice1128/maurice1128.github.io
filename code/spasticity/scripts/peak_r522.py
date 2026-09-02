# -*- coding: utf-8 -*-
"""r522: is the first knee flexion peak a better landmark than the contact instant?

The contact instant is defined by an EXTERNAL event detector, and in impaired populations only 89%
of kinematic events land within two frames of the force-plate standard [23]. The first flexion peak
in early stance is defined by the DATA -- it is a turning point of the curve itself -- so it needs no
event detection at all. That is a different and stronger argument than window averaging, which only
averages the error down.

For every admissible cell this locates the first knee flexion peak inside the first 40% of each kept
cycle and scores it the way the contact instant is scored, alongside its timing.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


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
        peaks, times, ic = [], [], []
        for a, b in w:
            n = b - a
            seg = kn[a:a + max(int(round(n * 0.40)), 3)]     # first 40% of the cycle
            j = int(np.argmin(seg))                          # flexion is negative as stored
            peaks.append(float(seg[j])); times.append(100.0 * j / n); ic.append(float(kn[a]))
        out.append({"fam": fam, "peak": float(np.mean(peaks)), "peak_pct": float(np.mean(times)),
                    "instant": float(np.mean(ic))})
    return out


hy = [c for f in HY for c in cells(f)]
wk = [c for f in WK for c in cells(f)]
rows = hy + wk
print("cells: hyper %d  weak %d" % (len(hy), len(wk)))
print("first flexion peak occurs at %.1f%% of the cycle (SD %.1f)\n"
      % (np.mean([r["peak_pct"] for r in rows]), np.std([r["peak_pct"] for r in rows], ddof=1)))


def score(key):
    a = [r[key] for r in hy]; b = [r[key] for r in wk]
    sds = [np.std([r[key] for r in rows if r["fam"] == f], ddof=1)
           for f in set(r["fam"] for r in rows) if len([r for r in rows if r["fam"] == f]) > 1]
    sd = float(np.mean(sds)); gap = float(min(b) - max(a))
    return {"hyper_mean": float(np.mean(a)), "weak_mean": float(np.mean(b)),
            "arm_difference_deg": float(np.mean(a) - np.mean(b)), "cell_gap_deg": gap,
            "cells_disjoint": bool(max(a) < min(b)), "mean_seed_SD_deg": sd,
            "gap_in_seed_SD": gap / sd, "effect_in_seed_SD": abs(np.mean(a) - np.mean(b)) / sd}


res = {"contact_instant": score("instant"), "first_flexion_peak": score("peak")}
print("%-20s %10s %10s %9s %8s %9s" % ("readout", "arm diff", "cell gap", "seed SD", "gap/SD", "disjoint"))
for k, v in res.items():
    print("%-20s %10.3f %10.3f %9.3f %8.2f %9s"
          % (k, v["arm_difference_deg"], v["cell_gap_deg"], v["mean_seed_SD_deg"],
             v["gap_in_seed_SD"], v["cells_disjoint"]))
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\PEAK_r522.json", "w",
        encoding="utf-8", newline="").write(json.dumps(
    {"id": "PEAK_r522",
     "why": ("the contact instant needs an external event detector; the first flexion peak is a "
             "turning point of the curve itself and needs none"),
     "peak_timing_pct_of_cycle": {"mean": float(np.mean([r["peak_pct"] for r in rows])),
                                  "sd": float(np.std([r["peak_pct"] for r in rows], ddof=1))},
     "scores": res}, indent=1, ensure_ascii=False))
