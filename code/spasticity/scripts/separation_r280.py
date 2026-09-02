# -*- coding: utf-8 -*-
"""What does hip_flexion_LmR actually separate: lesion type, or falling?

Reads PERCYCLE_r279.json only. Computes no new measurement. Two jobs:

1. FIXES AN INCONSISTENCY I INTRODUCED. `wpf_hipgap_r278.py` refuses to measure a cell whose
   t_end falls short of the registered window end 9.73 s. `percycle_r279.py` did not carry
   that guard, so WPF cell03 (t_end 7.460 s) was measured over a window truncated to its own
   collapse. That cell is the one nearest the fell/full boundary, so the reported gap of
   0.1206 deg depended on it. Both figures are given below and the truncated cell is excluded
   from the headline, matching r278's rule rather than r279's silence.

2. Reports the separation three ways, on the same 53 cells, so they can be compared directly:
      by LESION TYPE   spastic vs every weakness cell   -- what the manuscript ships
      by OUTCOME       fell vs ran the full 20.00 s
      within WEAK-PF   one lesion, one dose, six seeds, split by whether the model stayed up

The third is the one that carries the argument, because lesion, muscle, dose, body and
optimiser are all held constant across it and only the outcome differs.

UNREGISTERED, POST-HOC. Read-only.
"""
import io, json, os

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
d = json.load(open(os.path.join(PAPER, "PERCYCLE_r279.json")))
T1 = 9.73

cells = []
for arm, cs in d["per_cell"].items():
    for sid, r in cs.items():
        if r.get("insufficient_cycles") or r.get("LmR_window") is None:
            continue
        cells.append({
            "arm": arm, "id": sid, "t_end_s": r["t_end_s"],
            "LmR_window": r["LmR_window"], "LmR_first3": r["LmR_first3"],
            "f": r.get("f"), "seed": r.get("seed"),
            # The guard r278 applies and r279 omitted.
            "window_truncated_by_collapse": bool(r["t_end_s"] < T1),
        })

trunc = [c for c in cells if c["window_truncated_by_collapse"]]
ok = [c for c in cells if not c["window_truncated_by_collapse"]]


def rng(xs):
    return [min(xs), max(xs)] if xs else None


def split(group_a, group_b, name_a, name_b):
    a = [c["LmR_window"] for c in group_a]
    b = [c["LmR_window"] for c in group_b]
    if not a or not b:
        return {"n_%s" % name_a: len(a), "n_%s" % name_b: len(b), "disjoint": None}
    disj = max(a) < min(b)
    return {"n_" + name_a: len(a), "n_" + name_b: len(b),
            name_a + "_range": rng(a), name_b + "_range": rng(b),
            "disjoint": bool(disj),
            "gap_deg": (min(b) - max(a)) if disj else None,
            "overlap_deg": None if disj else (max(a) - min(b))}


WEAK_ARMS = {"W800", "W870", "W892", "W900", "W915", "W950", "WPF"}

by_type = split([c for c in ok if c["arm"] == "S"],
                [c for c in ok if c["arm"] in WEAK_ARMS], "spastic", "weakness")
by_type_dorsi = split([c for c in ok if c["arm"] == "S"],
                      [c for c in ok if c["arm"] in WEAK_ARMS - {"WPF"}], "spastic", "weakness")
by_outcome = split([c for c in ok if c["t_end_s"] < 20.0],
                   [c for c in ok if c["t_end_s"] >= 20.0], "fell", "full")
by_outcome_incl = split([c for c in cells if c["t_end_s"] < 20.0],
                        [c for c in cells if c["t_end_s"] >= 20.0], "fell", "full")

wpf = [c for c in ok if c["arm"] == "WPF"]
wpf_split = split([c for c in wpf if c["t_end_s"] < 20.0],
                  [c for c in wpf if c["t_end_s"] >= 20.0], "fell", "full")

out = {
    "question": "does hip_flexion_LmR separate lesion type, or outcome",
    "status": "UNREGISTERED, POST-HOC; reads PERCYCLE_r279.json only; no new measurement",
    "window_guard": {
        "rule": "a cell whose t_end is short of the registered window end 9.73 s is NOT measured",
        "source": "wpf_hipgap_r278.py; percycle_r279.py omitted this guard",
        "cells_excluded_here": [{"arm": c["arm"], "id": c["id"], "t_end_s": c["t_end_s"],
                                 "LmR_window_in_truncated_window": c["LmR_window"]}
                                for c in trunc],
        "why_it_matters": ("the excluded cell sits nearest the fell/full boundary, so the "
                           "headline gap depends on whether the guard is applied"),
    },
    "n_cells_total": len(cells), "n_cells_after_guard": len(ok),
    "separations": {
        "by_lesion_type_spastic_vs_all_weakness": by_type,
        "by_lesion_type_spastic_vs_dorsiflexor_weakness_only": by_type_dorsi,
        "by_outcome_fell_vs_full": by_outcome,
        "by_outcome_fell_vs_full_WITHOUT_the_guard": by_outcome_incl,
        "within_WEAK_PF_only": wpf_split,
    },
    "within_WEAK_PF_cells": sorted(
        [{"cell": c["id"], "f": c["f"], "seed": c["seed"], "t_end_s": c["t_end_s"],
          "LmR_window": c["LmR_window"], "LmR_first3": c["LmR_first3"],
          "fell": bool(c["t_end_s"] < 20.0)} for c in wpf],
        key=lambda x: x["t_end_s"]),
    "incomplete": "WEAK-PF is still running; only the cells with a .sto at the time are here.",
}
p = os.path.join(PAPER, "SEPARATION_r280.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

W = 78
print("=" * W)
print("WHAT DOES hip_flexion_LmR SEPARATE?   %d cells, %d after the window guard"
      % (len(cells), len(ok)))
print("=" * W)
for c in trunc:
    print("EXCLUDED by the guard: %s %s  t_end %.3f s, short of the %.2f s window"
          % (c["arm"], c["id"], c["t_end_s"], T1))
print()
lbl = [("by LESION TYPE  spastic vs all weakness", by_type, "spastic", "weakness"),
       ("by LESION TYPE  spastic vs dorsiflexor only", by_type_dorsi, "spastic", "weakness"),
       ("by OUTCOME      fell vs ran full 20.00 s", by_outcome, "fell", "full"),
       ("within WEAK-PF  fell vs full, one lesion", wpf_split, "fell", "full")]
for name, s, a, b in lbl:
    if s.get("disjoint") is None:
        print("%-44s  n=%d/%d  not evaluable" % (name, s.get("n_" + a, 0), s.get("n_" + b, 0)))
        continue
    print("%-44s  n=%d vs %d" % (name, s["n_" + a], s["n_" + b]))
    print("%-44s    %-8s %+.4f .. %+.4f" % ("", a, s[a + "_range"][0], s[a + "_range"][1]))
    print("%-44s    %-8s %+.4f .. %+.4f" % ("", b, s[b + "_range"][0], s[b + "_range"][1]))
    print("%-44s    %s%s" % ("", "DISJOINT" if s["disjoint"] else "OVERLAP",
                             "  gap %+.4f deg" % s["gap_deg"] if s["disjoint"]
                             else "  overlap %.4f deg" % s["overlap_deg"]))
    print()
print("WEAK-PF, one lesion and one dose, ordered by how long it stayed up:")
print("  %-8s %8s %10s %10s  %s" % ("cell", "t_end", "LmR_win", "first3", "fell"))
for c in out["within_WEAK_PF_cells"]:
    print("  %-8s %8.3f %+10.4f %+10.4f  %s" % (c["cell"], c["t_end_s"], c["LmR_window"],
                                                c["LmR_first3"], c["fell"]))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
