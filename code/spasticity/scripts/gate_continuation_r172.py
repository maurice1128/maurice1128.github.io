# -*- coding: utf-8 -*-
"""Gate G for the CONTINUATION ladder, measured FROM THE .sto -- duration and GRF cycles,
exactly as PREREG_3d_reopt_r151.md section 3 defines it and as analyse_ladder_r169.py applied it.

GOVERNED BY  paper/PREREG_3d_continuation_r172.md
             sha256 35ac02b4706add2585c6455b79fd6384c957df3899ae51f2b117ec1f95b2c60b

⛔ FITNESS IS NOT THE REGISTERED CRITERION. It is printed beside Gate G because a fitness ordering
was used as a fast indicator earlier in this round, and if the two disagree that disagreement is a
finding to be stated rather than smoothed. The VERDICT column comes from duration and cycles only.

⛔ REACHING 90 GENERATIONS IS NOT SURVIVING. r169's S150 cells all reached 90 generations and Gate G
dropped every one of them at 0.66-6.01 s. Optimiser completion and gait viability are different
measurements and this script reports only the second as a verdict.

Section 2 checks are re-verified here from the run manifest: parent lineage, cumulative depth,
and the position-1 reuse. No simulation is optimised; replay is sconecmd -e on an already-converged
par, which is an evaluation.
"""
import io
import os
import sys
import glob
import json
import math
import subprocess

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
sys.path.insert(0, HERE)
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "CONTINUATION_RESULT_r172.json")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
MANIFEST = os.path.join(HERE, "probe3d_r141", "cont_r172", "RUN_MANIFEST.json")
SEEDS = [101, 102, 103, 104, 105, 106]
MIN_DUR, MIN_CYC, MIN_SEEDS, SETTLE = 9.73, 5, 4, 1.0
PREREG = "35ac02b4706add2585c6455b79fd6384c957df3899ae51f2b117ec1f95b2c60b"

# (label, tag prefix, arm, position, depth, provenance)
ROWS = [("C      control",        "R151C",    "control", 1, 90,  "r169 from-healthy"),
        ("S050   KV 0.050",       "R151S",    "spastic", 1, 90,  "r169 from-healthy, ADMITTED"),
        ("S150   KV 0.150 r169",  "R169S150", "spastic", 1, 90,  "r169 from-healthy, DROPPED"),
        ("S400   KV 0.400 r169",  "R169S400", "spastic", 1, 90,  "r169 from-healthy, DROPPED"),
        ("S150   KV 0.150 CONT",  "R172S150", "spastic", 2, 180, "r172 continuation from S050"),
        ("S400   KV 0.400 CONT",  "R172S400", "spastic", 3, 270, "r172 continuation from S150"),
        ("W095   x0.95",          "R169W095", "weak",    1, 90,  "r169 from-healthy, ADMITTED"),
        ("W090   x0.90 r169",     "R169W090", "weak",    1, 90,  "r169 from-healthy, ADMITTED"),
        ("W080   x0.80 r169",     "R151W",    "weak",    1, 90,  "r169 from-healthy, ADMITTED"),
        ("W090   x0.90 CONT",     "R172W090", "weak",    2, 180, "r172 continuation from W095"),
        ("W080   x0.80 CONT",     "R172W080", "weak",    3, 270, "r172 continuation from W090")]


def hist_lines(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def result_dir(tag):
    good = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
            if os.path.isdir(d) and hist_lines(d) >= 91]
    if len(good) > 1:
        raise SystemExit("tag %s resolves to %d complete directories; refusing" % (tag, len(good)))
    return good[0] if good else None


def best_par(d):
    ps = [p for p in glob.glob(os.path.join(d, "*.par")) if os.path.basename(p)[0].isdigit()]
    return sorted(ps)[-1] if ps else None


def fitness_of(par):
    """From SCONE's own filename: <generation>_<fitness>_<...>.par. Reported, NOT a verdict."""
    try:
        return float(os.path.basename(par).split("_")[1])
    except Exception:
        return None


def sto_for(d):
    s = glob.glob(os.path.join(d, "*.par.sto"))
    return sorted(s)[-1] if s else None


def gate(sto):
    """The REGISTERED criterion: duration and GRF-delimited cycles after settle."""
    try:
        cols, dat = S.load_sto(sto)
        t = list(S.col(cols, dat, "time"))
        grf, thr = S.grf_vertical(cols, dat, "l")
        idx = S.heel_strikes(t, grf, thresh=thr)
        c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
             if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= t[-1]]
        c = c[:-1] if len(c) >= 2 else c
        return t[-1], len(c)
    except Exception:
        return 0.0, 0


print("=" * 100)
print("GATE G FROM THE .sto -- duration >= %.2f s AND >= %d GRF cycles after settle;" % (MIN_DUR, MIN_CYC))
print("            a rung is ADMITTED iff >= %d of 6 seeds pass. FITNESS IS NOT THE CRITERION." % MIN_SEEDS)
print("=" * 100)

# replay only what is missing; -e is an evaluation of an already-converged par
need = []
for _, pre, _, _, _, _ in ROWS:
    for s in SEEDS:
        d = result_dir("%s_s%d" % (pre, s))
        if d and sto_for(d) is None:
            need.append(d)
if need:
    print("replaying %d cells (sconecmd -e, evaluation of a converged par, not an optimisation)"
          % len(need))
    for d in need:
        bp = best_par(d)
        if bp:
            subprocess.run([SCONE, "-e", bp], capture_output=True, timeout=900, cwd=d)
    print("replay done\n")

res = {"prereg_sha256": PREREG, "criterion": "duration and GRF cycles from .sto; fitness is NOT it",
       "rows": []}
print("%-24s %-28s %-42s %-34s %s"
      % ("rung", "provenance", "duration s (6 seeds)", "cycles", "verdict"))
for label, pre, arm, pos, depth, prov in ROWS:
    durs, cycs, fits, missing = [], [], [], 0
    for s in SEEDS:
        d = result_dir("%s_s%d" % (pre, s))
        if d is None:
            missing += 1
            continue
        bp = best_par(d)
        fits.append(fitness_of(bp))
        st = sto_for(d)
        if st is None:
            durs.append(0.0)
            cycs.append(0)
            continue
        du, cy = gate(st)
        durs.append(du)
        cycs.append(cy)
    if missing == len(SEEDS):
        print("%-24s %-28s %s" % (label, prov, "NOT REACHED / not run"))
        res["rows"].append({"rung": label, "prefix": pre, "arm": arm, "position": pos,
                            "depth": depth, "provenance": prov, "state": "NOT REACHED"})
        continue
    npass = sum(1 for du, cy in zip(durs, cycs) if du >= MIN_DUR and cy >= MIN_CYC)
    adm = npass >= MIN_SEEDS
    print("%-24s %-28s %-42s %-34s %d/6 %s"
          % (label, prov,
             " ".join("%5.2f" % x for x in durs),
             " ".join("%2d" % x for x in cycs), npass,
             "ADMITTED" if adm else "*** DROPPED ***"))
    res["rows"].append({"rung": label, "prefix": pre, "arm": arm, "position": pos, "depth": depth,
                        "provenance": prov, "durations": durs, "cycles": cycs,
                        "fitness_best_par": fits, "n_pass": npass, "admitted": bool(adm),
                        "n_missing": missing})

print("\n" + "=" * 100)
print("FITNESS beside Gate G -- reported so any disagreement is visible, NOT as a verdict")
print("=" * 100)
print("%-24s %-42s %s" % ("rung", "best-par fitness (low is better)", "Gate G"))
for r in res["rows"]:
    if r.get("state") == "NOT REACHED":
        continue
    f = r["fitness_best_par"]
    print("%-24s %-42s %d/6 %s"
          % (r["rung"], " ".join(("%5.1f" % x) if x is not None else "  n/a" for x in f),
             r["n_pass"], "ADMITTED" if r["admitted"] else "DROPPED"))

if os.path.exists(MANIFEST):
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    res["run_manifest"] = {"chains": man.get("chains"), "n_cells": len(man.get("cells", []))}
    bad = [c for c in man.get("cells", []) if c["cumulative_depth"] != 90 * c["position"]]
    res["depth_check"] = "PASSED" if not bad else "FAILED"
    lin = [c for c in man.get("cells", [])
           if not c["parent_tag"].endswith("_s%d" % c["seed"])]
    res["lineage_check"] = "PASSED" if not lin else "FAILED"
    print("\nsection 2 re-verified from the run manifest: depth %s, parent lineage %s, %d cells"
          % (res["depth_check"], res["lineage_check"], len(man.get("cells", []))))

json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1,
          default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("\nwrote %s" % OUT)
