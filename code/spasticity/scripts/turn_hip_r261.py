"""turn_hip_r261.py -- round 261, registered at PREREG_turn_transfer_r261.md (sha256 91c40979...).

Two tests, both from TURN_r260.json. No .sto is reopened.

  1. THE REGISTERED TEST. Does hip_flexion_LmR's displacement survive adjustment for the
     model's progressive turning? The 2D body has no transverse DOF and physically cannot
     turn, so a hip channel that is substantially a turning artefact would explain why the
     transfer did not reproduce.
  2. Does turning also explain the PHASE of peak deviation, which is the one qualitative
     result the corpus has produced?

Reading C of the registration is the collinearity failure mode and is tested explicitly:
if the reflex arm's residual shrinks but control/weakness residuals are large, the
regression is fitting arm identity through the turn covariate and the test is void.
"""
import io
import json
import os

import numpy as np

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEV = ["W800", "W870", "W892", "W900", "W915", "W950"]


def adjust(rows, key):
    x = np.array([r["turn"] for r in rows], float)
    y = np.array([r[key] for r in rows], float)
    m, b = np.polyfit(x, y, 1)
    res = y - (m * x + b)
    r = float(np.corrcoef(x, y)[0, 1])
    by = {}
    for arm in ["C", "S"] + SEV:
        sel = np.array([q["arm"] == arm for q in rows])
        by[arm] = {"raw_mean": float(y[sel].mean()),
                   "residual_mean": float(res[sel].mean()),
                   "turn_mean": float(x[sel].mean())}
    S, C = by["S"], by["C"]
    frac = 1.0 - abs(S["residual_mean"]) / abs(S["raw_mean"]) if S["raw_mean"] else None
    # Reading C diagnostic, fixed in advance
    other = max(abs(by[a]["residual_mean"]) for a in ["C"] + SEV)
    return {"pearson_r_turn_vs_measure": r, "r2": r * r,
            "slope": float(m), "by_arm": by,
            "reflex_raw": S["raw_mean"], "reflex_residual": S["residual_mean"],
            "fraction_of_reflex_effect_removed": frac,
            "largest_nonreflex_residual": other,
            "reading_C_collinearity_flag": bool(other >= 0.5 * abs(S["residual_mean"])),
            "turn_range_overlap": {
                "reflex_min_turn": min(q["turn"] for q in rows if q["arm"] == "S"),
                "nonreflex_max_turn": max(q["turn"] for q in rows if q["arm"] != "S")}}


def main():
    d = json.load(io.open(os.path.join(PAPER, "TURN_r260.json"), encoding="utf-8"))
    out = {"round": 261, "prereg": "PREREG_turn_transfer_r261.md",
           "prereg_sha256_prefix": "91c409795c9f4f202089462e",
           "note": "computed from TURN_r260.json; no .sto reopened",
           "windows": {}}

    for wk, w in d["windows"].items():
        rows = w["per_cell"]
        r = {"hip_flexion_LmR_dev80": adjust(rows, "hip_dev80"),
             "ankle_angle_l_dev80": adjust(rows, "ank_dev80"),
             "peak_phase": adjust(rows, "ank_peak_phase")}
        # phase separation, reflex vs every weakness arm, at seed level
        ph = {a: [q["ank_peak_phase"] for q in rows if q["arm"] == a] for a in ["C", "S"] + SEV}
        r["phase_disjointness"] = {
            a: {"reflex_range": [min(ph["S"]), max(ph["S"])],
                "arm_range": [min(ph[a]), max(ph[a])],
                "gap": min(ph["S"]) - max(ph[a]),
                "disjoint": min(ph["S"]) > max(ph[a])}
            for a in SEV}
        r["phase_disjoint_vs_all_weakness"] = all(
            v["disjoint"] for v in r["phase_disjointness"].values())
        out["windows"][wk] = r

    with io.open(os.path.join(PAPER, "TURN_HIP_r261.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, r in out["windows"].items():
        print("=" * 84)
        print("WINDOW [1.00, %s]" % wk)
        for k in ("hip_flexion_LmR_dev80", "ankle_angle_l_dev80", "peak_phase"):
            v = r[k]
            print("-- %s" % k)
            print("   r(turn, measure) %+.4f  r2 %.4f | reflex raw %+8.4f -> residual %+8.4f"
                  "  (%.1f%% removed)"
                  % (v["pearson_r_turn_vs_measure"], v["r2"], v["reflex_raw"],
                     v["reflex_residual"],
                     100 * v["fraction_of_reflex_effect_removed"]
                     if v["fraction_of_reflex_effect_removed"] is not None else float("nan")))
            print("   largest non-reflex residual %+.4f | READING C collinearity flag: %s"
                  % (v["largest_nonreflex_residual"], v["reading_C_collinearity_flag"]))
            o = v["turn_range_overlap"]
            print("   turn overlap: reflex min %.4f vs non-reflex max %.4f -> %s"
                  % (o["reflex_min_turn"], o["nonreflex_max_turn"],
                     "OVERLAP" if o["reflex_min_turn"] < o["nonreflex_max_turn"] else "SEPARATED"))
        print("-- phase of peak deviation, reflex vs each weakness arm (seed level)")
        for a, v in r["phase_disjointness"].items():
            print("   S %s vs %-5s %s  gap %+d  disjoint=%s"
                  % (v["reflex_range"], a, v["arm_range"], v["gap"], v["disjoint"]))
        print("   disjoint vs ALL weakness arms: %s" % r["phase_disjoint_vs_all_weakness"])


if __name__ == "__main__":
    main()
