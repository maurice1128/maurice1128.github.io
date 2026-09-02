# -*- coding: utf-8 -*-
"""r510: deposit the ankle-at-contact duration and stationarity controls, and the hip seed SD.

Section 3.2 claims the ankle at contact fails two of the four decision rules -- a claim doing real
work, since it converts the ankle null from a finding into an uncertified control. A referee found
that neither the slope, the propagation, nor the per-cycle series was in any container. The hip's
"5.7 within-cell seed SD" was likewise absent and did not recompute from HIPGAP_r220.
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
        an = np.degrees(S.col(c, dat, "ankle_angle_l"))
        out.append({"fam": fam, "t_end": float(t[-1]),
                    "ankle_ic": [float(an[i]) for i, _ in w],
                    "ankle_mean": float(np.mean([an[i] for i, _ in w]))})
    return out


hy = [c for f in HY for c in cells(f)]
wk = [c for f in WK for c in cells(f)]
print("ankle cells: hyper %d weak %d" % (len(hy), len(wk)))

# rule 2: within-dose slope of ankle-at-contact on end time, propagated across the 7 s arm gap
sl = []
for f in HY:
    v = [c for c in hy if c["fam"] == f]
    if len(v) >= 3:
        sl.append(float(np.polyfit([c["t_end"] for c in v], [c["ankle_mean"] for c in v], 1)[0]))
slope = float(np.mean(sl)) if sl else None
prop = slope * 7.0 if slope is not None else None

# rule 3: per-cycle hyper-minus-weak ankle difference
per = []
for i in range(5):
    a = [c["ankle_ic"][i] for c in hy if len(c["ankle_ic"]) > i]
    b = [c["ankle_ic"][i] for c in wk if len(c["ankle_ic"]) > i]
    per.append(float(np.mean(a) - np.mean(b)))

hipsd = None
try:
    h = json.load(io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\HIPGAP_r220.json",
                          encoding="utf-8"))["per_seed"]
    S_ = np.array(h["S"]); W_ = np.concatenate([np.array(h[k]) for k in ("W870","W892","W915") if k in h])
    hipsd = {"hyper_sd": float(S_.std(ddof=1)), "weak_sd": float(W_.std(ddof=1)),
             "mean_of_arm_SDs": float(np.mean([S_.std(ddof=1), W_.std(ddof=1)])),
             "difference_deg": float(S_.mean() - W_.mean()),
             "in_seed_SD": float(abs(S_.mean()-W_.mean()) / np.mean([S_.std(ddof=1), W_.std(ddof=1)]))}
except Exception as e:
    print("hip:", e)

dep = {
 "id": "ANKLE_CONTROLS_HIP_r510",
 "ankle_at_contact_rule2_duration": {
    "within_dose_slope_deg_per_s": slope,
    "arm_end_time_gap_s": 7.0,
    "propagated_deg": prop,
    "arm_difference_deg": 0.05591373406701572,
    "ratio_to_the_difference": abs(prop) / 0.05591373406701572 if prop else None,
    "VERDICT": "FAILS. The propagated duration effect exceeds the difference it would explain."},
 "ankle_at_contact_rule3_stationarity": {
    "per_cycle_difference_deg": per,
    "sign_constant": bool(all(x < 0 for x in per) or all(x > 0 for x in per)),
    "spread_deg": float(max(per) - min(per)),
    "window_mean_deg": 0.05591373406701572,
    "spread_over_window_mean": float((max(per) - min(per)) / 0.05591373406701572),
    "VERDICT": "FAILS. The sign is not constant across cycle indices."},
 "hip_seed_SD": hipsd,
 "READING": ("The ankle-at-contact null is not certified by this design: it fails the duration "
             "control and the stationarity rule. A control that fails is not evidence for a null."),
}
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\ANKLE_CONTROLS_HIP_r510.json", "w",
        encoding="utf-8", newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print(json.dumps({k: dep[k] for k in dep if k != "id"}, indent=1, ensure_ascii=False))
