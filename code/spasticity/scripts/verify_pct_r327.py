# -*- coding: utf-8 -*-
"""Independently recompute the three unlesioned-share percentages from METRIC_r255.json.

The manuscript labels them DERIVABLE BUT NOT DEPOSITED. This checks that the derivation
actually reproduces the quoted figures from the deposited deltas, so the label is earned.
Share of the UNLESIONED limb = |r| / (|l| + |r|).
"""
import io, json, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
m = json.load(io.open(os.path.join(P, "METRIC_r255.json"), encoding="utf-8"))

CASES = [("excursion", "9.73", 84.22), ("mean_angle", "9.73", 44.32), ("mean_angle", "13.58", 41.58)]

for table, win, quoted in CASES:
    t = m["windows"][win]["tables"][table]
    l = t["hip_flexion_l"]["arms"]["S"]["delta_from_control"]
    r = t["hip_flexion_r"]["arms"]["S"]["delta_from_control"]
    share = abs(r) / (abs(l) + abs(r)) * 100.0
    print("%-11s %-6s  l=%+.10f  r=%+.10f  share=%.4f %%  quoted %.2f %%  %s"
          % (table, win, l, r, share, quoted, "OK" if abs(share - quoted) < 0.01 else "MISMATCH"))
