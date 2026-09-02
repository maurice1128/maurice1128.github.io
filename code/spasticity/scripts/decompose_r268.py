"""decompose_r268.py -- round 268, registered at PREREG_decompose_r268.md.

Is the reflex arm's terminal objective a FALL PENALTY or a TRAINING DEFICIT?

Decomposes each analysed cell's cost into its non-GaitMeasure components, evaluated over a
COMMON INTERVAL that every one of the 48 cells completes, so no term is inflated by a longer
trace and none is a function of when the model fell.

Directory resolution uses the same guard as the kinematic scripts (>= 91 history lines,
exactly one match) -- fitness_r266.py and gain_ladder_r264.py used a bare sorted(g)[0] and
read two W950 cells from a truncated duplicate.

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

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = list(range(101, 107))
ARMS = [("C", "R151C"), ("S", "R151S"), ("W800", "R151W"), ("W870", "R174W870"),
        ("W892", "R174W892"), ("W900", "R169W090"), ("W915", "R174W915"),
        ("W950", "R169W095")]
WEAK = ["W800", "W870", "W892", "W900", "W915", "W950"]
SETTLE = 1.0

COMPONENTS = {
    "Effort": ["Effort.effort"],
    "MuscleActivation": ["MuscleActivation.effort"],
    "DofLimits": ["ankle_angle_l.position_penalty", "ankle_angle_r.position_penalty",
                  "knee_angle_l.limit_torque_penalty", "knee_angle_r.limit_torque_penalty"],
    "GRF": ["GRF.load_penalty"],
}


def rd(tag):
    """Same guard as channels_g2_r219.py / metric_r255.py: >= 91 history lines, unique."""
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def load(tag):
    d = rd(tag)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    return cols, dat, t, os.path.basename(d)


def main():
    # ---- pass 1: durations, to fix the common interval from the data
    cells = {}
    for arm, pre in ARMS:
        for s in SEEDS:
            cols, dat, t, dname = load("%s_s%d" % (pre, s))
            cells[(arm, s)] = {"cols": cols, "dat": dat, "t": t, "dir": dname,
                               "t_end": float(t[-1])}
    T_COMMON = min(v["t_end"] for v in cells.values())

    out = {"round": 268, "prereg": "PREREG_decompose_r268.md",
           "common_interval": [SETTLE, T_COMMON],
           "common_interval_note": ("upper bound is the minimum t_end over all 48 analysed cells, "
                                    "so every cell contributes the full interval"),
           "t_end_by_arm": {}, "components": {}, "per_cell": []}

    for arm, _ in ARMS:
        te = [cells[(arm, s)]["t_end"] for s in SEEDS]
        out["t_end_by_arm"][arm] = {"per_seed": te, "mean": float(np.mean(te)),
                                    "min": float(min(te)), "max": float(max(te))}

    # ---- pass 2: components over the common interval
    for arm, _ in ARMS:
        for s in SEEDS:
            c = cells[(arm, s)]
            cols, dat, t = c["cols"], c["dat"], c["t"]
            i0 = int(np.searchsorted(t, SETTLE))
            i1 = int(np.searchsorted(t, T_COMMON))
            rec = {"arm": arm, "seed": s, "dir": c["dir"], "t_end": c["t_end"]}
            for name, colnames in COMPONENTS.items():
                tot = 0.0
                miss = []
                for cn in colnames:
                    try:
                        v = np.asarray(S.col(cols, dat, cn), dtype=float)
                    except Exception:
                        miss.append(cn)
                        continue
                    seg = v[i0:i1 + 1]
                    # SCONE writes these as running/cumulative measures; take the increment
                    # across the interval if monotone non-decreasing, else the mean.
                    mono = bool(np.all(np.diff(seg) >= -1e-9))
                    tot += float(seg[-1] - seg[0]) if mono else float(np.mean(seg))
                    rec.setdefault("_monotone", {})[cn] = mono
                rec[name] = tot
                if miss:
                    rec.setdefault("_missing", []).extend(miss)
            out["per_cell"].append(rec)

    for name in COMPONENTS:
        by = {}
        for arm, _ in ARMS:
            v = [r[name] for r in out["per_cell"] if r["arm"] == arm]
            by[arm] = {"per_seed": v, "mean": float(np.mean(v)),
                       "min": float(min(v)), "max": float(max(v))}
        Cm = by["C"]["mean"]
        Sm = by["S"]["mean"]
        Wall = [x for a in WEAK for x in by[a]["per_seed"]]
        Sall = by["S"]["per_seed"]
        by["_summary"] = {
            "reflex_over_control": float(Sm / Cm) if Cm else None,
            "weakness_over_control": float(np.mean(Wall) / Cm) if Cm else None,
            "reflex_range": [min(Sall), max(Sall)],
            "weakness_range": [min(Wall), max(Wall)],
            "control_range": by["C"]["min"] and [by["C"]["min"], by["C"]["max"]],
            "reflex_overlaps_weakness": bool(min(Sall) <= max(Wall) and min(Wall) <= max(Sall)),
            "reflex_overlaps_control": bool(min(Sall) <= by["C"]["max"]
                                            and by["C"]["min"] <= max(Sall)),
        }
        out["components"][name] = by

    with io.open(os.path.join(PAPER, "DECOMPOSE_r268.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump({k: v for k, v in out.items()}, f, indent=1)
        f.write("\n")

    print("COMMON INTERVAL [%.2f, %.2f] s  (min t_end over all 48 analysed cells)"
          % (SETTLE, T_COMMON))
    print("t_end by arm: " + "  ".join("%s %.2f" % (a, out["t_end_by_arm"][a]["mean"])
                                       for a, _ in ARMS))
    print()
    for name in COMPONENTS:
        b = out["components"][name]
        sm = b["_summary"]
        print("== %s" % name)
        for arm, _ in ARMS:
            print("   %-5s %14.5f  [%12.5f, %12.5f]" % (arm, b[arm]["mean"], b[arm]["min"],
                                                        b[arm]["max"]))
        print("   reflex/control %.3fx   weakness/control %.3fx   reflex overlaps control: %s"
              " | weakness: %s"
              % (sm["reflex_over_control"], sm["weakness_over_control"],
                 sm["reflex_overlaps_control"], sm["reflex_overlaps_weakness"]))


if __name__ == "__main__":
    main()
