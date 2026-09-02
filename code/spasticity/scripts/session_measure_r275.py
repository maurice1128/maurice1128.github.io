"""session_measure_r275.py -- round 275.

Deposits the reachability self-consistency measurements that PREREG_weakpf_r274.md quoted
as if sourced. They were real in-session measurements over reach_2x2_r273.py's own config
space, but they appeared in no file, which is the failure mode that registration warns
about. This makes them citable.

Also deposits the corrected completion census for the cost figure, and the two cells that
fail the registered .par tie rule.

Read-only.
"""
import glob
import io
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import reach_2x2_r273 as R

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RES = r"C:\Users\maurice\Documents\SCONE\results"


def sgn(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


def main():
    HWD = 1.96 * math.sqrt(2.0 / R.N_SEEDS) / 2.534
    sign_route = sign_overlap = 0
    consistent = total = 0
    r1_total = r1_consistent = 0
    inc_p1 = inc_p2 = inc_neither = inc_total = 0

    for c in R.configs():
        total += 1
        rung = R.decide(c)

        cons = True
        if abs(c["hw"] - HWD * c["delta"]) > 1e-9 * max(1.0, c["delta"]):
            cons = False                      # hw is a deterministic function of delta
        if min(c["n_usable"]) > min(c["n_2cyc"]):
            cons = False                      # cannot have more usable cells than cycling ones
        if not (c["hl_df"][0] <= c["t_df"] <= c["hl_df"][1]):
            cons = False                      # an interval must contain its own estimate
        if c["all_within_band"] and max(abs(c["t_pf"]), abs(c["t_df"])) > c["delta"]:
            cons = False                      # four means inside a band of width delta
        if cons:
            consistent += 1

        if rung == "FAILURE-DOMINATED":
            r1_total += 1
            if cons:
                r1_consistent += 1

        if rung == "INTERACTION":
            sPF, sDF = sgn(c["t_pf"]), sgn(c["t_df"])
            if sPF != 0 and sDF != 0 and sPF != sDF:
                sign_route += 1
                disj = (c["hl_pf"][1] < c["hl_df"][0]) or (c["hl_df"][1] < c["hl_pf"][0])
                if not disj:
                    sign_overlap += 1

        if rung == "INCONCLUSIVE":
            inc_total += 1
            d = c["delta"]
            a, b = abs(c["t_pf"]), abs(c["t_df"])
            same = sgn(c["t_pf"]) == sgn(c["t_df"])
            ov = not ((c["hl_pf"][1] < c["hl_df"][0]) or (c["hl_df"][1] < c["hl_pf"][0]))
            if a <= d and b <= d and same and not c["group_separates"]:
                inc_p1 += 1
            elif ((a > d) != (b > d)) and ov:
                inc_p2 += 1
            else:
                inc_neither += 1

    # ---- corrected completion census
    def rate(pre):
        ds = [d for d in glob.glob(os.path.join(RES, pre + "_s1*.*")) if os.path.isdir(d)]
        out = []
        for d in ds:
            c1 = os.path.join(d, "config.scone")
            h1 = os.path.join(d, "history.txt")
            if os.path.exists(c1) and os.path.exists(h1):
                out.append(os.path.getmtime(h1) - os.path.getmtime(c1))
        return (sum(out) / len(out)) if out else None

    completing = ["R151C", "R151S", "R151W", "R174W870", "R174W892", "R174W915",
                  "R169W090", "R169W095", "R172W090", "R172W080"]
    rates = {a: rate(a) for a in completing}
    rates = {k: v for k, v in rates.items() if v}
    mean10 = sum(rates.values()) / len(rates)

    out = {
        "round": 275,
        "why": ("PREREG_weakpf_r274.md quoted these as sourced when they existed only as "
                "in-session measurements. Depositing them makes the citations honest."),
        "source": "reach_2x2_r273.py configs() and decide(), N_SEEDS=%d" % R.N_SEEDS,
        "self_consistency_rule": [
            "hw must equal %.5f * delta (it is a deterministic function of delta at this n)" % HWD,
            "an arm cannot have more usable cells than cells completing >= 2 cycles",
            "an HL interval must contain its own point estimate",
            "four arm means inside a band of width delta force |effect| <= delta"],
        "n_configurations": total,
        "n_self_consistent": consistent,
        "pct_self_consistent": 100.0 * consistent / total,
        "pct_physically_impossible": 100.0 * (total - consistent) / total,
        "FAILURE_DOMINATED": {"total": r1_total, "self_consistent": r1_consistent},
        "INTERACTION_sign_route": {"total": sign_route,
                                   "with_overlapping_HL_intervals": sign_overlap},
        "INCONCLUSIVE_split": {"total": inc_total, "pattern_1": inc_p1,
                               "pattern_2": inc_p2, "matching_neither": inc_neither,
                               "registered_in_2x2_rev4": [1296, 3792]},
        "completion_census": {
            "note": ("COST_r270.json tabulated 8 arms and omitted R172W090 and R172W080, "
                     "which also completed 6/6 seeds at 20.0 s and 14 cycles"),
            "arms_completing": sorted(rates),
            "n_arms": len(rates),
            "s_per_cell": rates,
            "mean_s_per_cell": mean10,
            "hours_for_18_cells": 18 * mean10 / 3600.0},
    }

    p = os.path.join(PAPER, "SESSION_MEASURE_r275.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print("self-consistent %d of %d = %.2f%%  (impossible %.2f%%)"
          % (consistent, total, out["pct_self_consistent"], out["pct_physically_impossible"]))
    print("FAILURE-DOMINATED: %d total, %d self-consistent" % (r1_total, r1_consistent))
    print("INTERACTION sign route: %d, overlapping HL: %d" % (sign_route, sign_overlap))
    print("INCONCLUSIVE %d = %d / %d / %d (neither)" % (inc_total, inc_p1, inc_p2, inc_neither))
    print("completion census: %d arms, mean %.2f s/cell, 18 cells = %.4f h"
          % (len(rates), mean10, out["completion_census"]["hours_for_18_cells"]))


if __name__ == "__main__":
    main()
