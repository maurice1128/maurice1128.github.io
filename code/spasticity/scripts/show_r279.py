# -*- coding: utf-8 -*-
"""Read-only reader for PERCYCLE_r279.json. Lists every cell that fell, and the boundary
cells on either side of the fell/full split. Computes nothing new."""
import json, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\PERCYCLE_r279.json"
d = json.load(open(P))

rows = []
for arm, cells in d["per_cell"].items():
    for sid, r in cells.items():
        if r.get("insufficient_cycles"):
            rows.append((arm, sid, r["t_end_s"], None, None, None, "too few cycles"))
            continue
        rows.append((arm, sid, r["t_end_s"], r["LmR_window"], r["LmR_first3"],
                     r["slope_deg_per_cycle"],
                     "" if r["LmR_window"] is not None else "short of window"))
rows.sort(key=lambda x: (x[2], 9 if x[3] is None else x[3]))

print("EVERY CELL THAT DID NOT REACH 20.00 s, plus the five lowest full-duration cells")
print("%-6s %-8s %8s %10s %10s %9s  %s" % ("arm", "id", "t_end", "LmR_win", "first3", "slope", "note"))
fell = [r for r in rows if r[2] < 20.0]
full = sorted([r for r in rows if r[2] >= 20.0], key=lambda x: 9 if x[3] is None else x[3])
for a, s, te, lw, f3, sl, n in fell:
    print("%-6s %-8s %8.3f %10s %10s %9s  %s" % (
        a, s, te, "n/a" if lw is None else "%+.4f" % lw,
        "n/a" if f3 is None else "%+.4f" % f3,
        "n/a" if sl is None else "%+.4f" % sl, n))
print("  --- boundary ---")
for a, s, te, lw, f3, sl, n in full[:5]:
    print("%-6s %-8s %8.3f %10s %10s %9s  %s" % (
        a, s, te, "n/a" if lw is None else "%+.4f" % lw,
        "n/a" if f3 is None else "%+.4f" % f3,
        "n/a" if sl is None else "%+.4f" % sl, n))

print()
print("cells in file : %d" % sum(len(c) for c in d["per_cell"].values()))
s = d["summary"]
print("measured      : %d   fell %d   full %d" % (s["n_cells"], s["n_fell"], s["n_full_duration"]))
print("arms among fallers : %s" % ", ".join(s["fallers_only"]["arms_represented"]))
print("rho(LmR_window, t_end) all cells   : %s" % s["pooled_all"]["spearman_LmRwindow_vs_tend"])
print("rho(LmR_first3,  t_end) all cells  : %s" % s["pooled_all"]["spearman_LmRfirst3_vs_tend"])
print("rho(LmR_window, t_end) fallers only: %s" % s["fallers_only"]["spearman_LmRwindow_vs_tend"])
sc = s["separation_check"]
print("fell  LmR range : %s" % sc["fell_LmR_range"])
print("full  LmR range : %s" % sc["full_LmR_range"])
