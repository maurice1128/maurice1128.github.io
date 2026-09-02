# -*- coding: utf-8 -*-
"""ZERO-COST RECONNAISSANCE, r212 -- availability census only.

⛔ NOT A REGISTERED STUDY. This script REPLAYS NOTHING, LAUNCHES NOTHING and COMPUTES NO ENDPOINT.
It lists which intermediate CMA-ES .par files already exist in the two arms, so it can be decided
whether a partial-adaptation pilot is even possible. Nothing here may be cited as evidence for or
against any hypothesis.

Read-only. Writes exactly one file, under spasticity_paper.
"""
import io, os, re, glob, json

R = r"C:\Users\maurice\Documents\SCONE\results"
DST = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DEPTH_CENSUS_r212.json"
ARMS = {"S": "R151S", "W892": "R174W892"}
SEEDS = range(101, 107)
# SCONE writes <gen>_<fitness_a>_<fitness_b>.par on every improvement.
PAR = re.compile(r"^(\d{4})_([0-9.]+)_([0-9.]+)\.par$")


def rd(tag):
    """Same resolution rule as pb_r179.py / analyse_ladder_r169.py: >= 91 history lines, unique."""
    g = [d for d in glob.glob(os.path.join(R, tag + ".*")) if os.path.isdir(d)
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, tag
    return g[0]


out = {"label": "RECONNAISSANCE CENSUS -- availability only, nothing replayed, nothing computed",
       "arms": {}}

for arm, pre in ARMS.items():
    out["arms"][arm] = {}
    print("=" * 78); print("ARM %s  (%s)" % (arm, pre)); print("=" * 78)
    for s in SEEDS:
        tag = "%s_s%d" % (pre, s)
        d = rd(tag)
        hist = sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace"))
        rows = []
        for f in sorted(os.listdir(d)):
            m = PAR.match(f)
            if m:
                rows.append({"gen": int(m.group(1)), "f1": float(m.group(2)),
                             "f2": float(m.group(3)), "file": f,
                             "sto": os.path.exists(os.path.join(d, f + ".sto"))})
        gens = [r["gen"] for r in rows]
        out["arms"][arm][tag] = {"dir": os.path.basename(d), "history_lines": hist,
                                 "n_par": len(rows), "gens": gens,
                                 "n_sto": sum(1 for r in rows if r["sto"]), "rows": rows}
        print("%-18s hist=%-5d n_par=%-3d n_sto=%-2d gens=%s"
              % (tag, hist, len(rows), sum(1 for r in rows if r["sto"]), gens))

# coverage of the nominal decade grid, per cell -- nearest available generation to each anchor
GRID = [0, 10, 30, 50, 70, 90]
print("\nNEAREST AVAILABLE GENERATION TO EACH GRID ANCHOR (|delta| in brackets)")
print("%-18s %s" % ("cell", "  ".join("%4d" % g for g in GRID)))
out["grid"] = {"anchors": GRID, "nearest": {}}
for arm in ARMS:
    for tag, rec in out["arms"][arm].items():
        gens = rec["gens"]
        near = [min(gens, key=lambda x: abs(x - g)) for g in GRID]
        out["grid"]["nearest"][tag] = near
        print("%-18s %s" % (tag, "  ".join("%4d" % n for n in near)))

# how many DISTINCT generations each arm can offer that are shared-ish across seeds
for arm in ARMS:
    allg = sorted({g for rec in out["arms"][arm].values() for g in rec["gens"]})
    out["arms"][arm + "_union_gens"] = allg
    inter = set.intersection(*[set(rec["gens"]) for rec in out["arms"][arm].values()
                               if isinstance(rec, dict) and "gens" in rec])
    out["arms"][arm + "_common_gens"] = sorted(inter)
    print("\nARM %s: union of generations = %d distinct; COMMON to all six seeds = %s"
          % (arm, len(allg), sorted(inter)))

json.dump(out, io.open(DST, "w", encoding="utf-8", newline="\n"), indent=1)
print("\nwrote DEPTH_CENSUS_r212.json")
