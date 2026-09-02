# -*- coding: utf-8 -*-
"""Is hip_flexion_LmR a lesion-type signal, or a precursor of collapse?

CONFOUND_DURATION_r277.json showed the shipped comparison's two arms are disjoint in
simulated duration, so type and falling are the same partition there. WPF_HIPGAP_r278.json
showed a pure weakness cell that fell reads inside the spastic range while three cells with
IDENTICAL anatomy and dose that stayed up read inside the weakness range.

That leaves a sharper question, and it is answerable from .sto files already on disk.

The shipped window is [1.00, 9.73] s. The spastic cells fall at 13.58-17.85 s, so the shipped
measurement ENDS 4-8 s before their collapse. WEAK-PF cell 0 fell at 16.21 s -- again 6.5 s
after its window closed. So the deviation is not an artefact of the collapse transient. The
live hypothesis is stronger and more interesting: hip_flexion_LmR measured EARLY is a
precursor that predicts how long the model will stay up, in which case it is one variable
across all lesions and lesion type adds nothing to it.

Measured per cell, all from existing .sto, nothing re-simulated and nothing re-optimised:

  LmR_window     the shipped measurement, hipgap_r220.py's code verbatim, window [1.00, 9.73]
  LmR_first3     the first three complete cycles after settle -- is the deviation there from
                 the start, or does it grow?
  LmR_last3      the last three complete cycles before t_end, wherever that falls
  slope          least-squares slope of per-cycle LmR against cycle index, deg per cycle
  series         every per-cycle value with its end time and its time-to-end

Then, pooled across every cell of every arm, the association between the EARLY measurement
and t_end. If that association is strong and does not depend on which lesion produced it,
the channel is a fall-time predictor.

UNREGISTERED, POST-HOC. Read-only. No registration amended.
"""
import io, os, sys, glob, json, math
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = list(range(101, 107))
ARMS = [("C", "R151C", "control"), ("S", "R151S", "spastic KV 0.050"),
        ("W800", "R151W", "weak tib_ant x0.800"), ("W870", "R174W870", "weak tib_ant x0.870"),
        ("W892", "R174W892", "weak tib_ant x0.892"), ("W900", "R169W090", "weak tib_ant x0.900"),
        ("W915", "R174W915", "weak tib_ant x0.915"), ("W950", "R169W095", "weak tib_ant x0.950")]


def find_dir(tag):
    """hipgap_r220.py's selection: a directory whose history.txt shows a completed run."""
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    return ds[0] if ds else None


def lmr_over(cols, dat, cyc):
    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)
    return rom("hip_flexion_l") - rom("hip_flexion_r")


def slope(y):
    """Least-squares slope against index. None when fewer than three points."""
    n = len(y)
    if n < 3:
        return None
    x = list(range(n))
    mx, my = sum(x) / n, sum(y) / n
    den = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den if den else None


def cell(d):
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    allc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE]
    if len(allc) < 4:
        return {"t_end_s": t_end, "n_cycles": len(allc), "insufficient_cycles": True}
    per = [lmr_over(cols, dat, [c]) for c in allc]
    ends = [float(t[b]) for _, b in allc]

    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    out = {
        "t_end_s": t_end,
        "n_cycles": len(allc),
        "window_reaches_T1": bool(t_end >= T1),
        # r281 GUARD, aligned with wpf_hipgap_r278.py so the two cannot disagree:
        # a cell whose trace ends before T1 has had the shipped window truncated by its own
        # collapse. Measuring it there compares a full window against a partial one, so it is
        # NOT measured. r279 originally lacked this and measured WPF cell03 (t_end 7.460 s)
        # inside a window its own fall had shortened.
        "LmR_window": (lmr_over(cols, dat, win) if (win and t_end >= T1) else None),
        "LmR_window_guard": ("measured" if (win and t_end >= T1)
                             else ("t_end %.3f < T1 %.2f: window truncated by the cell's own "
                                   "collapse, not measured" % (t_end, T1) if t_end < T1
                                   else "no complete cycle inside the window")),
        "n_cycles_in_window": len(win),
        "LmR_first3": float(np.mean(per[:3])),
        "LmR_last3": float(np.mean(per[-3:])),
        "slope_deg_per_cycle": slope(per),
        "series": [{"i": i, "end_s": round(e, 4), "time_to_end_s": round(t_end - e, 4),
                    "LmR": round(v, 5)} for i, (e, v) in enumerate(zip(ends, per))],
    }
    out["growth_last3_minus_first3"] = out["LmR_last3"] - out["LmR_first3"]
    return out


rows = {}
print("%-6s %-5s %8s %6s %10s %10s %10s %10s" %
      ("arm", "seed", "t_end", "ncyc", "LmR_win", "first3", "last3", "slope"))
for key, pref, _desc in ARMS:
    rows[key] = {}
    for s in SEEDS:
        d = find_dir("%s_s%d" % (pref, s))
        if not d:
            print("%-6s %-5d  MISSING" % (key, s)); continue
        r = cell(d)
        rows[key][str(s)] = r
        if r.get("insufficient_cycles"):
            print("%-6s %-5d %8.3f %6d  too few cycles" % (key, s, r["t_end_s"], r["n_cycles"]))
            continue
        print("%-6s %-5d %8.3f %6d %10s %+10.4f %+10.4f %10s" % (
            key, s, r["t_end_s"], r["n_cycles"],
            "n/a" if r["LmR_window"] is None else "%+.4f" % r["LmR_window"],
            r["LmR_first3"], r["LmR_last3"],
            "n/a" if r["slope_deg_per_cycle"] is None else "%+.4f" % r["slope_deg_per_cycle"]))

# WEAK-PF, whatever has landed so far.
rows["WPF"] = {}
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_WEAKPF_r276_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    if not os.path.isdir(d) or not glob.glob(os.path.join(d, "*.par.sto")):
        continue
    r = cell(d)
    r.update({"f": dep["f"], "seed": dep["seed"], "cell": dep["cell"]})
    rows["WPF"]["cell%02d" % dep["cell"]] = r
    if r.get("insufficient_cycles"):
        print("%-6s c%-4d %8.3f %6d  too few cycles" % ("WPF", dep["cell"], r["t_end_s"], r["n_cycles"]))
        continue
    print("%-6s c%-4d %8.3f %6d %10s %+10.4f %+10.4f %10s" % (
        "WPF", dep["cell"], r["t_end_s"], r["n_cycles"],
        "n/a" if r["LmR_window"] is None else "%+.4f" % r["LmR_window"],
        r["LmR_first3"], r["LmR_last3"],
        "n/a" if r["slope_deg_per_cycle"] is None else "%+.4f" % r["slope_deg_per_cycle"]))


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    rx, ry = rank(x), rank(y); n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else None


# Pooled: does the EARLY measurement predict how long the model stays up, across all lesions?
pool = []
for k, cells in rows.items():
    for sid, r in cells.items():
        if r.get("insufficient_cycles") or r.get("LmR_window") is None:
            continue
        pool.append({"arm": k, "id": sid, "LmR_window": r["LmR_window"],
                     "LmR_first3": r["LmR_first3"], "t_end_s": r["t_end_s"]})

fell = [p for p in pool if p["t_end_s"] < 20.0]
full = [p for p in pool if p["t_end_s"] >= 20.0]

summary = {
    "n_cells": len(pool), "n_fell": len(fell), "n_full_duration": len(full),
    "pooled_all": {
        "spearman_LmRwindow_vs_tend": spearman([p["t_end_s"] for p in pool],
                                               [p["LmR_window"] for p in pool]),
        "spearman_LmRfirst3_vs_tend": spearman([p["t_end_s"] for p in pool],
                                               [p["LmR_first3"] for p in pool]),
        "caveat": "most cells are censored at exactly 20.00 s, so this is a heavily tied variable",
    },
    "fallers_only": {
        "n": len(fell),
        "spearman_LmRwindow_vs_tend": spearman([p["t_end_s"] for p in fell],
                                               [p["LmR_window"] for p in fell]),
        "arms_represented": sorted(set(p["arm"] for p in fell)),
        "note": "the uncensored subset; this is where the association is actually estimable",
    },
    "separation_check": {
        "fell_LmR_range": ([min(p["LmR_window"] for p in fell),
                            max(p["LmR_window"] for p in fell)] if fell else None),
        "full_LmR_range": ([min(p["LmR_window"] for p in full),
                            max(p["LmR_window"] for p in full)] if full else None),
        "question": "if fell-vs-full separates as cleanly as spastic-vs-weak did, the channel is about falling",
    },
}

out = {
    "question": "is hip_flexion_LmR a lesion-type signal or a precursor of collapse",
    "status": "UNREGISTERED, POST-HOC; read-only; nothing re-simulated",
    "shipped_window": [SETTLE, T1],
    "why_not_a_collapse_artefact": (
        "the shipped window closes at 9.73 s while the spastic cells fall at 13.58-17.85 s and "
        "WEAK-PF cell 0 fell at 16.21 s, so the deviation is measured 4-8 s BEFORE collapse"),
    "per_cell": rows,
    "summary": summary,
    "incomplete": "WEAK-PF is a run in progress; its cells here are whatever had landed.",
}
p = os.path.join(PAPER, "PERCYCLE_r279.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

print()
print("=" * 78)
print("POOLED: does the EARLY measurement predict how long the model stays up?")
print("=" * 78)
print("cells %d   fell %d   ran full 20.00 s %d" % (len(pool), len(fell), len(full)))
for lbl, v in (("all cells, LmR_window vs t_end", summary["pooled_all"]["spearman_LmRwindow_vs_tend"]),
               ("all cells, LmR_first3 vs t_end", summary["pooled_all"]["spearman_LmRfirst3_vs_tend"]),
               ("fallers only, LmR_window vs t_end", summary["fallers_only"]["spearman_LmRwindow_vs_tend"])):
    print("  %-38s rho = %s" % (lbl, "undefined" if v is None else "%+.4f" % v))
sc = summary["separation_check"]
if sc["fell_LmR_range"] and sc["full_LmR_range"]:
    print("\n  cells that FELL     LmR %+.4f .. %+.4f  (n=%d)" % (sc["fell_LmR_range"][0], sc["fell_LmR_range"][1], len(fell)))
    print("  cells that ran FULL LmR %+.4f .. %+.4f  (n=%d)" % (sc["full_LmR_range"][0], sc["full_LmR_range"][1], len(full)))
    disj = sc["fell_LmR_range"][1] < sc["full_LmR_range"][0]
    print("  disjoint on FELL vs FULL: %s%s" % (disj, "   gap %+.4f deg" % (sc["full_LmR_range"][0] - sc["fell_LmR_range"][1]) if disj else ""))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
