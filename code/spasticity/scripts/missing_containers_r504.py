# -*- coding: utf-8 -*-
"""r504: deposit the three quantities the manuscript reports that no container held.

A cold verification pass over every JSON deposit found three quantities present in the manuscript
text and in no container: the speed control, the per-cycle knee difference series, and the peak
swing dorsiflexion result. A paper whose Declarations claim every statistic is reproducible from the
archive cannot rest any of them on prose. This recomputes all three from the archived .sto files
under the same Gate G as every other analysis and writes MISSING_CONTAINERS_r504.json.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MISSING_CONTAINERS_r504.json"
SETTLE, T1 = 1.0, 9.73
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
CT = [("R151C", None)]


def cell(fam, sd):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5:
        return None
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    # forward speed: pelvis translation over the analysed window divided by its duration
    try:
        px = S.col(c, dat, "pelvis_tx")
    except Exception:
        px = None
    a0, b0 = w[0][0], w[-1][1]
    speed = float((px[b0] - px[a0]) / (t[b0] - t[a0])) if px is not None else None
    # peak dorsiflexion during swing: swing is the span from toe-off to the next contact
    on = grf > thr
    peaks = []
    for a, b in w:
        seg = an[a:b]
        st_on = on[a:b]
        idx = np.where(~st_on)[0]
        if idx.size:
            peaks.append(float(np.max(seg[idx])))
    return {"seed": sd, "knee_ic": [float(kn[i]) for i, _ in w], "ankle_ic": [float(an[i]) for i, _ in w],
            "knee_ic_mean": float(np.mean([kn[i] for i, _ in w])),
            "t_end": float(t[-1]), "speed_mps": speed,
            "peak_swing_df": float(np.mean(peaks)) if peaks else None}


def arm(fams):
    out = []
    for f, _ in fams:
        for sd in range(101, 107):
            c = cell(f, sd)
            if c:
                c["family"] = f
                out.append(c)
    return out


hy, wk, ct = arm(HY), arm(WK), arm(CT)
print("cells: hyper %d  weak %d  control %d" % (len(hy), len(wk), len(ct)))


def m(v, k):
    x = [c[k] for c in v if c[k] is not None]
    return (float(np.mean(x)), float(np.std(x, ddof=1)), len(x)) if x else (None, None, 0)


# ---- speed control -------------------------------------------------------------------------------
sh, sw, sc = m(hy, "speed_mps"), m(wk, "speed_mps"), m(ct, "speed_mps")
gap = sh[0] - sw[0] if sh[0] and sw[0] else None
# within-dose slope of knee-at-contact on speed, pooled over hyperreflexia families
sl = []
for f, _ in HY:
    v = [c for c in hy if c["family"] == f and c["speed_mps"] is not None]
    if len(v) >= 3:
        sl.append(float(np.polyfit([c["speed_mps"] for c in v], [c["knee_ic_mean"] for c in v], 1)[0]))
slope = float(np.mean(sl)) if sl else None

# ---- per-cycle knee difference --------------------------------------------------------------------
per = []
for i in range(5):
    a = [c["knee_ic"][i] for c in hy if len(c["knee_ic"]) > i]
    b = [c["knee_ic"][i] for c in wk if len(c["knee_ic"]) > i]
    per.append(float(np.mean(a) - np.mean(b)))

# ---- peak swing dorsiflexion -----------------------------------------------------------------------
ph, pw, pc = m(hy, "peak_swing_df"), m(wk, "peak_swing_df"), m(ct, "peak_swing_df")
pooled_sd = float(np.sqrt((ph[1] ** 2 + pw[1] ** 2) / 2)) if ph[1] and pw[1] else None

dep = {
 "id": "MISSING_CONTAINERS_r504",
 "why": ("A cold verification pass found these three quantities in the manuscript text and in no "
         "deposit. They are recomputed here from the archived .sto under the same Gate G."),
 "n_cells": {"hyperreflexia": len(hy), "weakness": len(wk), "control": len(ct)},
 "speed_control": {
    "definition": "pelvis forward translation over the analysed window divided by its duration",
    "mean_speed_mps": {"hyperreflexia": sh[0], "weakness": sw[0], "control": sc[0]},
    "sd_mps": {"hyperreflexia": sh[1], "weakness": sw[1], "control": sc[1]},
    "arm_gap_mps": gap,
    "within_dose_slope_deg_per_mps": slope,
    "propagated_deg": (slope * gap) if (slope is not None and gap is not None) else None,
    "as_fraction_of_knee_effect": ((slope * gap) / -5.2799)
                                  if (slope is not None and gap is not None) else None,
    "CAVEAT": ("walking speed is a consequence of the lesion, not a variable independent of it, so "
               "this adjusts a mediator. It is an indication of scale, not a bound.")},
 "per_cycle_knee_difference_deg": {
    "by_cycle_index": per,
    "sign_constant": bool(all(x < 0 for x in per) or all(x > 0 for x in per)),
    "spread": float(max(per) - min(per)),
    "first_to_last_drift": float(per[-1] - per[0])},
 "peak_swing_dorsiflexion_deg": {
    "definition": "mean over kept cycles of the maximum ankle angle during the swing span",
    "control": pc[0], "weakness": pw[0], "hyperreflexia": ph[0],
    "sd": {"weakness": pw[1], "hyperreflexia": ph[1]},
    "hyper_minus_weak": (ph[0] - pw[0]) if (ph[0] and pw[0]) else None,
    "cohens_d": ((ph[0] - pw[0]) / pooled_sd) if (pooled_sd and ph[0] and pw[0]) else None,
    "weakness_displacement_from_control": (pw[0] - pc[0]) if (pw[0] and pc[0]) else None},
}
io.open(OUT, "w", encoding="utf-8", newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print(json.dumps({k: dep[k] for k in ("speed_control", "per_cycle_knee_difference_deg",
                                      "peak_swing_dorsiflexion_deg")}, indent=1))
print("-> %s" % OUT)
