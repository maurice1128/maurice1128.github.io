# -*- coding: utf-8 -*-
"""r521: does referencing the paretic knee to the patient's own unaffected side help?

The obstacle to a per-patient reading is not the instrument, it is that patients differ from one
another at this landmark by more than either lesion moves them (section 3.5). A within-patient
contrast -- paretic minus non-paretic -- removes everything the two limbs share: anthropometry,
walking speed, gait habit, footwear. It is standard in stroke gait analysis.

The cost is known and measured here: this model's UNLESIONED knee also moves, carrying 35.5% of the
arm separation above KV 0.200 (SIDE_CONTROL_r496). So the contrast should preserve the effect at the
low rungs, where the right knee barely moves, and erode it at the high ones. This computes both
sides per cell and scores the difference the way the single-side reading is scored.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", None), ("R174W870", None), ("R174W892", None),
      ("R169W090", None), ("R174W915", None), ("R169W095", None)]


def one(fam, sd, side):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g: return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st: return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0: return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, side)
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k+1]) for k in range(len(hs)-1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5: return None
    kn = np.degrees(S.col(c, dat, "knee_angle_%s" % side))
    return float(np.mean([kn[i] for i, _ in w]))


rows = []
for fam, kv in HY + WK:
    for sd in range(101, 107):
        L, R = one(fam, sd, "l"), one(fam, sd, "r")
        if L is None or R is None: continue
        rows.append({"fam": fam, "kv": kv, "arm": "hyper" if kv else "weak",
                     "L": L, "R": R, "LmR": L - R})
hy = [r for r in rows if r["arm"] == "hyper"]; wk = [r for r in rows if r["arm"] == "weak"]
print("cells: hyper %d  weak %d\n" % (len(hy), len(wk)))


def score(key):
    a = [r[key] for r in hy]; b = [r[key] for r in wk]
    sds = [np.std([r[key] for r in rows if r["fam"] == f], ddof=1)
           for f in set(r["fam"] for r in rows)
           if len([r for r in rows if r["fam"] == f]) > 1]
    sd = float(np.mean(sds))
    gap = float(min(b) - max(a))
    return {"hyper_mean": float(np.mean(a)), "weak_mean": float(np.mean(b)),
            "arm_difference_deg": float(np.mean(a) - np.mean(b)),
            "cell_gap_deg": gap, "cells_disjoint": bool(max(a) < min(b)),
            "mean_seed_SD_deg": sd, "gap_in_seed_SD": gap / sd}


res = {"paretic_side_only": score("L"), "paretic_minus_nonparetic": score("R" if False else "LmR")}
print("%-26s %9s %10s %9s %8s" % ("readout", "arm diff", "cell gap", "seed SD", "gap/SD"))
for k, v in res.items():
    print("%-26s %9.3f %10.3f %9.3f %8.2f"
          % (k, v["arm_difference_deg"], v["cell_gap_deg"], v["mean_seed_SD_deg"], v["gap_in_seed_SD"]))
print()
print("by rung, paretic-minus-nonparetic:")
for fam, kv in HY:
    v = [r["LmR"] for r in hy if r["fam"] == fam]
    l = [r["L"] for r in hy if r["fam"] == fam]
    if v: print("   KV %.3f   L %+7.3f   L-R %+7.3f   (n=%d)" % (kv, np.mean(l), np.mean(v), len(v)))

io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\LIMBDIFF_r521.json", "w",
        encoding="utf-8", newline="").write(json.dumps(
    {"id": "LIMBDIFF_r521",
     "why": ("a within-patient limb contrast removes what the two limbs share and is the standard "
             "route to reducing between-patient variance; its cost here is that the unlesioned knee "
             "also moves"),
     "scores": res,
     "per_cell": rows}, indent=1, ensure_ascii=False))
