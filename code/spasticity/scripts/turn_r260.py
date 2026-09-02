"""turn_r260.py -- round 260. Is the lesioned model turning, and does that explain the rest?

PHASE_r258.json showed the reflex arm accumulates ~1.4-1.6 deg of pelvis rotation per cycle
against ~0.1 deg in control. That is not a finding; it is a threat to every channel measured
over a window, and a candidate mechanism for the window-sensitivity of section 7.

Per CELL (arm x seed), not per arm, so that spread is visible:
  1. NET ROTATION PER CYCLE for every arm -- does it scale with weakness dose or is it
     specific to the reflex arm?
  2. Whether the 80 %-of-cycle ankle deviation SURVIVES adjustment for turning, by
     covariate regression across cells. Curve surgery is avoided: the turn is removed as a
     covariate, not subtracted from the trajectory.
  3. PER-SEED SPREAD of the phase of peak deviation, so the reflex arm's 80 % can be judged
     against the weakness arms' 71-74 %.

Read-only.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S
import metric_r255 as MR
import phase_r258 as PH

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEV = ["W800", "W870", "W892", "W900", "W915", "W950"]
SCALE = {"W800": .800, "W870": .870, "W892": .892, "W900": .900, "W915": .915, "W950": .950}
TIB = 125.85307120231857
REFLEX_DOSE = 136.2663747371695


def per_cycle_turn(sto, T1):
    """Net pelvis_rotation change per cycle, in degrees, averaged over cycles."""
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= MR.SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    v = np.degrees(np.asarray(S.col(cols, dat, "pelvis_rotation"), dtype=float))
    per = [v[b] - v[a] for a, b in c]
    return float(np.mean(per)), float(np.sum(per)), len(c)


def main():
    out = {"round": 260,
           "what": "turning rate per cell, its effect on the 80% ankle deviation, and the "
                   "per-seed spread of the phase of peak deviation",
           "gate_G": {
               "source": "analyse_ladder_r169.py MIN_SEEDS, MIN_DUR, MIN_CYC = 4, 9.73, 5",
               "tests": ["simulated duration >= 9.73 s", ">= 5 gait cycles",
                         ">= 4 of 6 seeds passing both"],
               "does_NOT_test": ["heading", "net rotation", "straightness of path",
                                 "lateral displacement", "any stability criterion beyond "
                                 "not falling before 9.73 s"],
               "consequence": "a cell that walks in a circle for 9.73 s passes Gate G"},
           "windows": {}}

    for T1 in MR.WINDOWS:
        cells = {}
        for arm, pre in MR.ARMS.items():
            cells[arm] = []
            for s in MR.SEEDS:
                sto = sorted(glob.glob(os.path.join(MR.rd("%s_s%d" % (pre, s)),
                                                    "*.par.sto")))[-1]
                cur, ncyc = PH.curves(sto, T1)
                rate, total, n2 = per_cycle_turn(sto, T1)
                cells[arm].append({"seed": s, "turn_per_cycle_deg": rate,
                                   "turn_total_deg": total, "n_cycles": ncyc,
                                   "curves": cur})

        Cmean = {ch: np.mean([c["curves"][ch] for c in cells["C"]], axis=0)
                 for ch in cells["C"][0]["curves"]}

        w = {"turn_rate_by_arm": {}, "per_cell": {}}
        for arm in MR.ARMS:
            r = [c["turn_per_cycle_deg"] for c in cells[arm]]
            tt = [c["turn_total_deg"] for c in cells[arm]]
            w["turn_rate_by_arm"][arm] = {
                "per_seed_deg_per_cycle": r,
                "mean": float(np.mean(r)), "sd": float(np.std(r, ddof=1)),
                "min": float(min(r)), "max": float(max(r)),
                "total_deg_mean": float(np.mean(tt)),
                "dose_N": (REFLEX_DOSE if arm == "S"
                           else (0.0 if arm == "C" else (1 - SCALE[arm]) * TIB))}

        # ---- per-cell deviation measures against the control mean curve
        rows = []
        for arm in MR.ARMS:
            for c in cells[arm]:
                d_ank = np.asarray(c["curves"]["ankle_angle_l"]) - Cmean["ankle_angle_l"]
                d_hip = np.asarray(c["curves"]["hip_flexion_LmR"]) - Cmean["hip_flexion_LmR"]
                rows.append({
                    "arm": arm, "seed": c["seed"],
                    "turn": c["turn_per_cycle_deg"],
                    "ank_dev80": float(d_ank[80]),
                    "ank_peak_phase": int(np.argmax(np.abs(d_ank))),
                    "ank_peak_dev": float(d_ank[int(np.argmax(np.abs(d_ank)))]),
                    "hip_dev80": float(d_hip[80])})
        w["per_cell"] = rows

        # ---- does turning explain the 80 % ankle deviation?
        x = np.array([r["turn"] for r in rows])
        y = np.array([r["ank_dev80"] for r in rows])
        isS = np.array([r["arm"] == "S" for r in rows])
        m, b = np.polyfit(x, y, 1)
        resid = y - (m * x + b)
        r2 = 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
        # weakness-only fit, then check the reflex arm against it
        wk = ~isS & np.array([r["arm"] != "C" for r in rows])
        mw, bw = np.polyfit(x[wk], y[wk], 1)
        w["turn_vs_ankle_dev80"] = {
            "pearson_r_all_cells": float(np.corrcoef(x, y)[0, 1]),
            "slope_all": float(m), "r2_all": float(r2),
            "reflex_mean_raw": float(y[isS].mean()),
            "control_mean_raw": float(y[np.array([r["arm"] == "C" for r in rows])].mean()),
            "reflex_mean_residual_after_turn": float(resid[isS].mean()),
            "control_mean_residual_after_turn": float(
                resid[np.array([r["arm"] == "C" for r in rows])].mean()),
            "weakness_only_slope": float(mw),
            "reflex_predicted_from_turn_weakness_line": float(mw * x[isS].mean() + bw),
            "reflex_observed": float(y[isS].mean()),
            "survives_adjustment": bool(abs(resid[isS].mean()) > 1.0)}

        # ---- per-seed spread of the phase of peak deviation
        w["peak_phase_by_arm"] = {}
        for arm in MR.ARMS:
            ph = [r["ank_peak_phase"] for r in rows if r["arm"] == arm]
            w["peak_phase_by_arm"][arm] = {
                "per_seed": ph, "mean": float(np.mean(ph)), "sd": float(np.std(ph, ddof=1)),
                "min": int(min(ph)), "max": int(max(ph))}
        out["windows"]["%.2f" % T1] = w

    with io.open(os.path.join(PAPER, "TURN_r260.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, w in out["windows"].items():
        print("=" * 84)
        print("WINDOW [1.00, %s]" % wk)
        print("-- net pelvis rotation per cycle, deg")
        for arm in MR.ARMS:
            v = w["turn_rate_by_arm"][arm]
            print("   %-5s dose %8.3f N   %+7.4f +- %6.4f   range [%+7.4f,%+7.4f]  total %+8.3f"
                  % (arm, v["dose_N"], v["mean"], v["sd"], v["min"], v["max"],
                     v["total_deg_mean"]))
        t = w["turn_vs_ankle_dev80"]
        print("-- does turning explain the 80%% ankle deviation?")
        print("   pearson r(turn, dev80) over 48 cells = %+.4f   r2 = %.4f"
              % (t["pearson_r_all_cells"], t["r2_all"]))
        print("   reflex dev80 raw %+7.4f -> residual after turn %+7.4f   (control raw %+7.4f "
              "-> %+7.4f)" % (t["reflex_mean_raw"], t["reflex_mean_residual_after_turn"],
                              t["control_mean_raw"], t["control_mean_residual_after_turn"]))
        print("   SURVIVES adjustment: %s" % t["survives_adjustment"])
        print("-- phase of peak deviation, per seed")
        for arm in MR.ARMS:
            v = w["peak_phase_by_arm"][arm]
            print("   %-5s %5.1f%% +- %4.1f   range [%3d, %3d]   seeds %s"
                  % (arm, v["mean"], v["sd"], v["min"], v["max"], v["per_seed"]))


if __name__ == "__main__":
    main()
