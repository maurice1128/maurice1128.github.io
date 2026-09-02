"""bistability_r288.py -- round 288. Is plantarflexor weakness graded, or a branch?

POST-HOC. Not registered. It reports a property of the model that does not depend on how
the r287 endpoint comes out, and it reads t_end only -- no channel column is opened, so it
cannot touch the r287 endpoint.

Every plantarflexor-weakness cell run so far: r276 at f = 0.05, 0.10, 0.20 and r285 at
f = 0.07, 0.08. Duration per cell, per dose, with the histogram.

Read-only.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
GUARD = 9.73
BAND = (13.58, 17.85)
FULL = 20.0


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def t_end(tag):
    d = rd(tag)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
    return float(list(S.col(cols, dat, "time"))[-1])


def main():
    arms = []
    for tag, f in (("R276WPF005", 0.05), ("R285BF007", 0.07), ("R285BF008", 0.08),
                   ("R276WPF010", 0.10), ("R276WPF020", 0.20)):
        vals = []
        for s in range(101, 107):
            try:
                v = t_end("%s_s%d" % (tag, s))
            except AssertionError as e:
                v = None
            vals.append({"seed": s, "t_end_s": v})
        arms.append({"prefix": tag, "f": f, "cells": vals,
                     "durations": [v["t_end_s"] for v in vals if v["t_end_s"] is not None]})

    allv = sorted(x for a in arms for x in a["durations"])
    # histogram, 1 s bins from 6 to 21
    edges = list(range(6, 22))
    hist = []
    for lo in edges[:-1]:
        n = sum(1 for v in allv if lo <= v < lo + 1)
        hist.append({"bin_s": [lo, lo + 1], "n": n})
    # gap: widest empty run between the lowest and highest observation
    gaps = []
    for i in range(len(allv) - 1):
        if allv[i + 1] - allv[i] > 1.0:
            gaps.append({"from": allv[i], "to": allv[i + 1],
                         "width_s": allv[i + 1] - allv[i]})

    for a in arms:
        d = a["durations"]
        a["n"] = len(d)
        a["n_short"] = sum(1 for v in d if v < GUARD)
        a["n_full"] = sum(1 for v in d if v >= FULL - 0.5)
        a["n_in_band"] = sum(1 for v in d if BAND[0] <= v <= BAND[1])
        a["range"] = [min(d), max(d)] if d else None
        a["is_split"] = bool(a["n_short"] > 0 and a["n_full"] > 0)

    out = {"round": 288, "status": "POST-HOC, not registered",
           "reads": "t_end only; no channel column is opened, so this cannot touch the "
                    "r287 endpoint",
           "claim": ("in this model plantarflexor weakness does not produce graded gait "
                     "deterioration; it produces a branch. The seed picks which."),
           "arms": arms, "n_cells": len(allv),
           "all_durations_sorted": allv,
           "histogram_1s_bins": hist,
           "gaps_wider_than_1s": gaps,
           "band": list(BAND), "guard_s": GUARD}
    io.open(os.path.join(PAPER, "BISTABILITY_r288.json"), "w",
            encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")

    print("%-14s %5s %3s %28s  short full band split" % ("arm", "f", "n", "durations (s)"))
    for a in arms:
        print("%-14s %5.2f %3d %28s  %5d %4d %4d %s"
              % (a["prefix"], a["f"], a["n"],
                 " ".join("%.2f" % v for v in sorted(a["durations"])),
                 a["n_short"], a["n_full"], a["n_in_band"], a["is_split"]))
    print()
    print("histogram, 1 s bins, all %d cells:" % len(allv))
    for h in hist:
        if h["n"] or (h["bin_s"][0] >= int(min(allv)) and h["bin_s"][0] <= int(max(allv))):
            print("  %2d-%2d s  %s %d" % (h["bin_s"][0], h["bin_s"][1], "#" * h["n"], h["n"]))
    print()
    print("empty runs wider than 1 s:")
    for g in gaps:
        print("  %.2f -> %.2f  (%.2f s)" % (g["from"], g["to"], g["width_s"]))


if __name__ == "__main__":
    main()
