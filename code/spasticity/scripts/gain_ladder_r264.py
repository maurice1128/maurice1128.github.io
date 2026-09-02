"""gain_ladder_r264.py -- round 264, registered at PREREG_gain_ladder_r264.md.

The reflex gain ladder the manuscript twice said did not exist. KV 0.150 and KV 0.400 are
gate-failed, not missing: 24 directories, each with a .par.sto. Gate G tests duration and
cycle count only (section 7b.6), so a cell that falls at 5.6 s is data about the gain-yaw
relation, not an absence of it.

REPRODUCTION FIRST: the KV 0.050 arm is recomputed here and must match TURN_r260.json per
seed. If it does not, nothing else is reported.

Endpoints, co-primary: net pelvis yaw per gait cycle, and time/cycles to failure.
The two optimisation paths R169 and R172 are never pooled.
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
import metric_r255 as MR

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = list(range(101, 107))

ARMS = [("KV0.050", "R151S", 0.050, "R151"),
        ("KV0.150", "R169S150", 0.150, "R169"),
        ("KV0.150", "R172S150", 0.150, "R172"),
        ("KV0.400", "R169S400", 0.400, "R169"),
        ("KV0.400", "R172S400", 0.400, "R172")]


def cell_dir(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    return sorted(g)[0] if g else None


def measure(sto, T1):
    """Yaw per cycle within the window, plus failure endpoints from the whole trace."""
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    v = np.degrees(np.asarray(S.col(cols, dat, "pelvis_rotation"), dtype=float))

    # failure endpoints: whole trace, no window, no cycle requirement
    t_end = float(t[-1])
    all_cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
               if t[idx[k]] >= MR.SETTLE]
    n_cyc_total = len(all_cyc)

    # yaw: cycles inside the window, exactly as turn_r260.py
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= MR.SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if len(c) < 2:
        return {"t_end": t_end, "n_cycles_total": n_cyc_total,
                "n_cycles_in_window": len(c), "yaw_per_cycle": None,
                "yaw_per_cycle_sd": None, "yaw_total": None}
    per = [float(v[b] - v[a]) for a, b in c]
    return {"t_end": t_end, "n_cycles_total": n_cyc_total,
            "n_cycles_in_window": len(c),
            "yaw_per_cycle": float(np.mean(per)),
            "yaw_per_cycle_sd": float(np.std(per, ddof=1)) if len(per) > 1 else None,
            "yaw_total": float(np.sum(per))}


def main():
    out = {"round": 264, "prereg": "PREREG_gain_ladder_r264.md",
           "registration_is_not_blind": True,
           "bound": ("A gain ladder within ONE lesion type breaks the CARDINALITY confound on the "
                     "reflex axis. It does not buy the 2x2: a plantarflexor-weakness arm and a "
                     "dorsiflexor-reflex arm are runs that do not exist and cannot be substituted "
                     "read-only. No statement about lesion TYPE is available from this corpus."),
           "reproduction": {}, "windows": {}}

    ref = json.load(io.open(os.path.join(PAPER, "TURN_r260.json"), encoding="utf-8"))

    for T1 in MR.WINDOWS:
        rows = []
        for label, pre, kv, path in ARMS:
            for s in SEEDS:
                d = cell_dir("%s_s%d" % (pre, s))
                if d is None:
                    rows.append({"gain": kv, "path": path, "seed": s, "present": False})
                    continue
                stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
                if not stos:
                    rows.append({"gain": kv, "path": path, "seed": s, "present": False})
                    continue
                m = measure(stos[-1], T1)
                m.update({"gain": kv, "path": path, "seed": s, "present": True,
                          "dir": os.path.basename(d)})
                rows.append(m)

        # ---- reproduction gate
        mine = [r["yaw_per_cycle"] for r in rows
                if r.get("present") and r["gain"] == 0.050 and r["path"] == "R151"]
        theirs = ref["windows"]["%.2f" % T1]["turn_rate_by_arm"]["S"]["per_seed_deg_per_cycle"]
        ok = (len(mine) == len(theirs)
              and all(a is not None and abs(a - b) < 1e-9 for a, b in zip(mine, theirs)))
        out["reproduction"]["%.2f" % T1] = {
            "recomputed": mine, "deposited_TURN_r260": theirs, "identical": bool(ok)}
        if not ok:
            print("*** REPRODUCTION FAILED at window %.2f -- nothing reported ***" % T1)
            continue

        # ---- summarise by gain x path, never pooling paths
        grp = {}
        for r in rows:
            if not r.get("present"):
                continue
            k = "KV%.3f_%s" % (r["gain"], r["path"])
            grp.setdefault(k, []).append(r)
        summ = {}
        for k, v in sorted(grp.items()):
            yaws = [x["yaw_per_cycle"] for x in v if x["yaw_per_cycle"] is not None]
            summ[k] = {
                "n_cells": len(v),
                "n_with_usable_cycles": len(yaws),
                "yaw_mean": float(np.mean(yaws)) if yaws else None,
                "yaw_sd_across_seeds": (float(np.std(yaws, ddof=1)) if len(yaws) > 1 else None),
                "yaw_per_seed": yaws,
                "within_cell_yaw_sd": [x["yaw_per_cycle_sd"] for x in v],
                "t_end_per_seed": [x["t_end"] for x in v],
                "t_end_mean": float(np.mean([x["t_end"] for x in v])),
                "t_end_min": float(min(x["t_end"] for x in v)),
                "t_end_max": float(max(x["t_end"] for x in v)),
                "cycles_total_per_seed": [x["n_cycles_total"] for x in v],
                "survivor_bias_note": (
                    "yaw computed on %d of %d cells -- the least destabilised. LOWER BOUND; the "
                    "bias runs toward the null." % (len(yaws), len(v))) if len(yaws) < len(v) else
                    "all cells usable",
            }
        out["windows"]["%.2f" % T1] = {"per_cell": rows, "by_gain_and_path": summ}

    with io.open(os.path.join(PAPER, "GAIN_LADDER_r264.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk in out["windows"]:
        print("=" * 92)
        print("WINDOW [1.00, %s]   reproduction of KV 0.050 identical to TURN_r260: %s"
              % (wk, out["reproduction"][wk]["identical"]))
        print("%-14s %5s %6s  %-22s  %-26s %s"
              % ("gain/path", "cells", "usable", "yaw deg/cycle", "t_end s", "cycles"))
        for k, v in out["windows"][wk]["by_gain_and_path"].items():
            y = ("%+.4f +- %s" % (v["yaw_mean"],
                                  ("%.4f" % v["yaw_sd_across_seeds"])
                                  if v["yaw_sd_across_seeds"] is not None else "n/a")
                 ) if v["yaw_mean"] is not None else "UNDEFINED (no cycles)"
            print("%-14s %5d %6d  %-22s  mean %6.3f [%5.3f,%6.3f]  %s"
                  % (k, v["n_cells"], v["n_with_usable_cycles"], y, v["t_end_mean"],
                     v["t_end_min"], v["t_end_max"], v["cycles_total_per_seed"]))


if __name__ == "__main__":
    main()
