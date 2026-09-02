"""turn_dose_r262.py -- round 262, registered at PREREG_turn_dose_r262.md.

Does the turning survive the magnitude confound?

The confound's force is "the reflex arm is 5-22x bigger". If turn rate is FLAT across a 4x
weakness dose range, dose is excluded as the explanation of the reflex arm's turning.
It does NOT establish type: with one reflex condition, "reflex-specific" and "specific to
this particular large lesion" remain unseparated. That bound is registered and is restated
in the deposit.

Computed from TURN_r260.json. No .sto reopened.
"""
import io
import json
import math
import os

import numpy as np

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEV = ["W800", "W870", "W892", "W900", "W915", "W950"]
SCALE = {"W800": .800, "W870": .870, "W892": .892, "W900": .900, "W915": .915, "W950": .950}
TIB = 125.85307120231857
REFLEX_DOSE = 136.2663747371695
# two-sided t critical value, df = 34
T34 = 2.032244


def main():
    d = json.load(io.open(os.path.join(PAPER, "TURN_r260.json"), encoding="utf-8"))
    out = {"round": 262, "prereg": "PREREG_turn_dose_r262.md",
           "bound": ("With ONE reflex condition, 'reflex-specific' and 'specific to this "
                     "particular large lesion' remain unseparated. Weakness flatness can "
                     "exclude DOSE as the explanation. It cannot establish TYPE."),
           "mechanism_hypothesis": (
               "UNTESTED: a unilateral velocity-dependent plantarflexor reflex produces "
               "asymmetric push-off and hence a yaw moment; a symmetric loss of dorsiflexor "
               "strength does not. Checked here only for its one falsifiable prediction, that "
               "net rotation is consistently toward the same side across seeds."),
           "windows": {}}

    for wk, w in d["windows"].items():
        T = w["turn_rate_by_arm"]
        x, y = [], []
        for a in SEV:
            dose = (1 - SCALE[a]) * TIB
            for v in T[a]["per_seed_deg_per_cycle"]:
                x.append(dose)
                y.append(v)
        x = np.array(x, float)
        y = np.array(y, float)
        n = len(x)
        m, b = np.polyfit(x, y, 1)
        yhat = m * x + b
        dof = n - 2
        s2 = float(np.sum((y - yhat) ** 2) / dof)
        sxx = float(np.sum((x - x.mean()) ** 2))
        se = math.sqrt(s2 / sxx)
        ci = (m - T34 * se, m + T34 * se)
        r = float(np.corrcoef(x, y)[0, 1])

        # slope needed to reach the reflex arm's observed rate at the reflex dose,
        # starting from the fitted weakness intercept
        s_obs = T["S"]["mean"]
        need = (s_obs - b) / REFLEX_DOSE
        # ...and, more conservatively, from the mildest weakness rung
        x0, y0 = (1 - SCALE["W950"]) * TIB, T["W950"]["mean"]
        need2 = (s_obs - y0) / (REFLEX_DOSE - x0)

        # predicted reflex rate from the weakness line, with its own 95% band on the slope
        pred = m * REFLEX_DOSE + b
        pred_lo = ci[0] * REFLEX_DOSE + b
        pred_hi = ci[1] * REFLEX_DOSE + b

        # ---- seed-level disjointness, reflex vs each weakness arm
        S = T["S"]["per_seed_deg_per_cycle"]
        dis = {}
        for a in SEV:
            v = T[a]["per_seed_deg_per_cycle"]
            dis[a] = {"reflex_range": [min(S), max(S)], "arm_range": [min(v), max(v)],
                      "gap": min(S) - max(v), "disjoint": bool(min(S) > max(v))}
        dis["pooled_weakness"] = {
            "reflex_min": min(S),
            "weak_max": max(max(T[a]["per_seed_deg_per_cycle"]) for a in SEV),
            "gap": min(S) - max(max(T[a]["per_seed_deg_per_cycle"]) for a in SEV),
            "disjoint": bool(min(S) > max(max(T[a]["per_seed_deg_per_cycle"]) for a in SEV))}

        # ---- sign consistency
        sign = {a: {"per_seed": T[a]["per_seed_deg_per_cycle"],
                    "all_same_sign": bool(all(q > 0 for q in T[a]["per_seed_deg_per_cycle"])
                                          or all(q < 0 for q in T[a]["per_seed_deg_per_cycle"])),
                    "n_positive": int(sum(1 for q in T[a]["per_seed_deg_per_cycle"] if q > 0))}
                for a in ["C", "S"] + SEV}

        reading = ("C - dose-driven" if ci[0] > 0 and pred_hi >= s_obs else
                   ("A - dose excluded" if pred_hi < s_obs else "B - underpowered"))
        out["windows"][wk] = {
            "weakness_regression": {
                "n_cells": n, "slope_deg_per_cycle_per_N": float(m), "intercept": float(b),
                "se_slope": se, "ci95_slope": [float(ci[0]), float(ci[1])],
                "pearson_r": r, "r2": r * r,
                "dose_range_N": [float(x.min()), float(x.max())],
                "dose_range_fold": float(x.max() / x.min())},
            "reflex_comparison": {
                "reflex_observed_rate": s_obs,
                "predicted_from_weakness_line": float(pred),
                "predicted_95ci": [float(pred_lo), float(pred_hi)],
                "ci_excludes_reflex_rate": bool(pred_hi < s_obs),
                "slope_required_from_intercept": float(need),
                "slope_required_from_W950": float(need2),
                "required_slope_over_fitted_ci_upper": float(need / ci[1]) if ci[1] else None},
            "disjointness": dis, "sign_consistency": sign, "reading": reading}

    with io.open(os.path.join(PAPER, "TURN_DOSE_r262.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, r in out["windows"].items():
        g = r["weakness_regression"]
        c = r["reflex_comparison"]
        print("=" * 84)
        print("WINDOW [1.00, %s]   READING: %s" % (wk, r["reading"]))
        print("-- turn rate on dose, WEAKNESS ARMS ONLY (%d cells, dose %.2f-%.2f N = %.1fx)"
              % (g["n_cells"], g["dose_range_N"][0], g["dose_range_N"][1], g["dose_range_fold"]))
        print("   slope %+.6f deg/cycle per N   95%% CI [%+.6f, %+.6f]   r %+.4f  r2 %.4f"
              % (g["slope_deg_per_cycle_per_N"], g["ci95_slope"][0], g["ci95_slope"][1],
                 g["pearson_r"], g["r2"]))
        print("-- reflex arm at %.1f N" % REFLEX_DOSE)
        print("   observed %+.4f   predicted from weakness line %+.4f  95%% band [%+.4f, %+.4f]"
              % (c["reflex_observed_rate"], c["predicted_from_weakness_line"],
                 c["predicted_95ci"][0], c["predicted_95ci"][1]))
        print("   CI EXCLUDES the reflex rate: %s   (required slope %+.6f = %.1fx the fitted "
              "CI upper bound)" % (c["ci_excludes_reflex_rate"],
                                   c["slope_required_from_intercept"],
                                   c["required_slope_over_fitted_ci_upper"] or float("nan")))
        print("-- seed-level disjointness of turn rate, reflex vs weakness")
        for a in SEV:
            v = r["disjointness"][a]
            print("   vs %-5s reflex [%+.4f,%+.4f] arm [%+.4f,%+.4f]  gap %+.4f  disjoint=%s"
                  % (a, v["reflex_range"][0], v["reflex_range"][1], v["arm_range"][0],
                     v["arm_range"][1], v["gap"], v["disjoint"]))
        p = r["disjointness"]["pooled_weakness"]
        print("   POOLED 36 weakness cells: gap %+.4f  disjoint=%s" % (p["gap"], p["disjoint"]))
        print("-- sign consistency (is the turn always the same way?)")
        for a in ["C", "S"] + SEV:
            s = r["sign_consistency"][a]
            print("   %-5s %d/6 positive  all_same_sign=%s" % (a, s["n_positive"],
                                                              s["all_same_sign"]))


if __name__ == "__main__":
    main()
