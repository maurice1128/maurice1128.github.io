"""fitness_r266.py -- round 266, registered at PREREG_fitness_r266.md.

The optimiser's terminal objective for every cell in the project: the 48 analysed cells and
the 24 gate-failed reflex cells. One column, already on disk, that the manuscript cites only
for a hash.

Then the question that decides whether a lesion comparison is possible at all: do the reflex
and weakness objective distributions OVERLAP? If they do not, conditioning is extrapolation,
not adjustment, and no reflex-versus-weakness difference in this corpus can be separated from
how well its controller was trained.

Read-only.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = list(range(101, 107))

ANALYSED = [("C", "R151C"), ("S", "R151S"), ("W800", "R151W"), ("W870", "R174W870"),
            ("W892", "R174W892"), ("W900", "R169W090"), ("W915", "R174W915"),
            ("W950", "R169W095")]
GATE_FAILED = [("KV0.150_R169", "R169S150"), ("KV0.150_R172", "R172S150"),
               ("KV0.400_R169", "R169S400"), ("KV0.400_R172", "R172S400")]
WEAK = ["W800", "W870", "W892", "W900", "W915", "W950"]


def cell_dir(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    return sorted(g)[0] if g else None


def history(d):
    """generation, best_fitness, fitness_progress from history.txt."""
    p = os.path.join(d, "history.txt")
    if not os.path.exists(p):
        return None
    rows = []
    with io.open(p, encoding="utf-8", errors="replace") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        gi, bi = hdr.index("generation"), hdr.index("best_fitness")
        pi = hdr.index("fitness_progress") if "fitness_progress" in hdr else None
        for ln in f:
            c = ln.rstrip("\n").split("\t")
            if len(c) <= bi:
                continue
            try:
                rows.append((int(float(c[gi])), float(c[bi]),
                             float(c[pi]) if pi is not None and len(c) > pi else None))
            except ValueError:
                continue
    if not rows:
        return None
    # SCONE's best_fitness column is the best of THAT generation, not the running best.
    # The running minimum is the terminal objective and is what the .par filenames carry.
    run, m = [], float("inf")
    for g, bf, pr in rows:
        m = min(m, bf)
        run.append((g, m))
    g0, bf0 = run[0]
    gN, bfN = run[-1]
    pN = rows[-1][2]
    at10 = [v for g, v in run if g <= gN - 10]
    return {"n_generations": len(rows), "gen_first": g0, "gen_last": gN,
            "best_fitness_gen0": bf0, "best_fitness_final": bfN,
            "fitness_progress_final": pN,
            "descent_over_final_10_gens": float((at10[-1] - bfN) if at10 else 0.0),
            "total_descent": float(bf0 - bfN),
            "fraction_of_start_retained": float(bfN / bf0) if bf0 else None,
            "note": "best_fitness_final is the RUNNING MINIMUM over generations"}


def main():
    dep = {}
    p = os.path.join(PAPER, "OPTDIST_r233.json")
    if os.path.exists(p):
        for c in json.load(io.open(p, encoding="utf-8"))["cells"]:
            dep[(c["arm"], c["seed"])] = c.get("fitness")

    out = {"round": 266, "prereg": "PREREG_fitness_r266.md",
           "note": "terminal optimiser objective for all 72 cells; lower is better",
           "analysed_cells": {}, "gate_failed_cells": {}, "overlap": {}}

    for arm, pre in ANALYSED:
        rows = []
        for s in SEEDS:
            d = cell_dir("%s_s%d" % (pre, s))
            h = history(d) if d else None
            rows.append({"seed": s, "deposited_fitness": dep.get((arm, s)),
                         "history": h,
                         "agrees_with_deposit": (
                             None if (h is None or dep.get((arm, s)) is None)
                             else abs(h["best_fitness_final"] - dep[(arm, s)]) < 1e-6)})
        f = [r["history"]["best_fitness_final"] for r in rows if r["history"]]
        out["analysed_cells"][arm] = {
            "per_seed": rows, "final_fitness": f,
            "mean": float(np.mean(f)) if f else None,
            "min": float(min(f)) if f else None, "max": float(max(f)) if f else None,
            "mean_descent_final_10": float(np.mean(
                [r["history"]["descent_over_final_10_gens"] for r in rows if r["history"]])),
            "mean_terminal_progress": float(np.mean(
                [r["history"]["fitness_progress_final"] for r in rows
                 if r["history"] and r["history"]["fitness_progress_final"] is not None]))}

    for label, pre in GATE_FAILED:
        rows = []
        for s in SEEDS:
            d = cell_dir("%s_s%d" % (pre, s))
            rows.append({"seed": s, "history": history(d) if d else None})
        f = [r["history"]["best_fitness_final"] for r in rows if r["history"]]
        f0 = [r["history"]["best_fitness_gen0"] for r in rows if r["history"]]
        out["gate_failed_cells"][label] = {
            "per_seed": rows, "final_fitness": f, "gen0_fitness": f0,
            "final_mean": float(np.mean(f)) if f else None,
            "gen0_mean": float(np.mean(f0)) if f0 else None,
            "mean_total_descent": float(np.mean([a - b for a, b in zip(f0, f)])) if f else None,
            "never_left_starting_basin": bool(
                f and np.mean([a - b for a, b in zip(f0, f)]) < 1.0)}

    # ---- overlap between the reflex arm and the weakness ladder
    S = out["analysed_cells"]["S"]["final_fitness"]
    W = [x for a in WEAK for x in out["analysed_cells"][a]["final_fitness"]]
    C = out["analysed_cells"]["C"]["final_fitness"]
    out["overlap"] = {
        "reflex_range": [min(S), max(S)], "weakness_range": [min(W), max(W)],
        "control_range": [min(C), max(C)],
        "ranges_overlap": bool(min(S) <= max(W) and min(W) <= max(S)),
        "gap_between_ranges": float(min(S) - max(W)),
        "reflex_over_control_mean": float(np.mean(S) / np.mean(C)),
        "weakness_over_control_mean": float(np.mean(W) / np.mean(C)),
        "n_weakness_cells_above_reflex_min": int(sum(1 for x in W if x >= min(S))),
        "common_support": bool(any(min(S) <= x <= max(S) for x in W)),
        "conditioning_possible": bool(any(min(S) <= x <= max(S) for x in W)),
        "verdict": None}
    o = out["overlap"]
    o["verdict"] = ("NO COMMON SUPPORT -- conditioning on terminal objective would be "
                    "extrapolation, not adjustment. The reflex and weakness arms cannot be "
                    "compared after adjustment because no weakness cell lies anywhere near the "
                    "reflex arm's objective range."
                    if not o["common_support"] else
                    "common support exists; conditioning is possible")

    with io.open(os.path.join(PAPER, "FITNESS_r266.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print("%-14s %-28s %-24s %s" % ("arm", "terminal objective", "descent last 10 gens",
                                    "terminal progress"))
    for arm, _ in ANALYSED:
        v = out["analysed_cells"][arm]
        agree = [r["agrees_with_deposit"] for r in v["per_seed"]]
        print("%-14s %8.4f [%8.4f,%8.4f]  %10.4f              %.2e   deposit-agrees %s"
              % (arm, v["mean"], v["min"], v["max"], v["mean_descent_final_10"],
                 v["mean_terminal_progress"],
                 ("%d/6" % sum(1 for a in agree if a)) if any(a is not None for a in agree) else "n/a"))
    print()
    print("%-14s %-24s %-24s %s" % ("gate-failed", "gen0 objective", "final objective",
                                    "total descent"))
    for label, _ in GATE_FAILED:
        v = out["gate_failed_cells"][label]
        print("%-14s %8.4f                 %8.4f                 %8.4f   never-left-basin=%s"
              % (label, v["gen0_mean"], v["final_mean"], v["mean_total_descent"],
                 v["never_left_starting_basin"]))
    print()
    print("OVERLAP: reflex [%.4f, %.4f]   weakness [%.4f, %.4f]   control [%.4f, %.4f]"
          % (o["reflex_range"][0], o["reflex_range"][1], o["weakness_range"][0],
             o["weakness_range"][1], o["control_range"][0], o["control_range"][1]))
    print("   gap between ranges: %+.4f   common support: %s   conditioning possible: %s"
          % (o["gap_between_ranges"], o["common_support"], o["conditioning_possible"]))
    print("   reflex is %.1fx control; weakness is %.2fx control"
          % (o["reflex_over_control_mean"], o["weakness_over_control_mean"]))
    print("   VERDICT: %s" % o["verdict"])


if __name__ == "__main__":
    main()
