# -*- coding: utf-8 -*-
"""hip_flexion_LmR on the WEAK-PF cells, computed by the SHIPPED method, unmodified.

The cycle selection, the window [1.00, 9.73], the per-cycle mean ROM(l) - ROM(r) in degrees
and the drop of the final cycle are copied verbatim from `hipgap_r220.py`, which produced the
values the manuscript ships. Nothing about the measurement is new; only the cells are.

Why this exists. CONFOUND_DURATION_r277.json established that the shipped comparison's two
arms are disjoint in simulated duration -- every weakness cell runs 20.00 s, no spastic cell
reaches it -- so "spastic" and "fell early" are the same partition and duration is an
unexcluded rival explanation for the hip separation. The WEAK-PF arm is the first weakness
arm containing cells that FALL. A WEAK-PF cell that falls at a spastic-like duration is
therefore the direct test:

  lands in the SPASTIC range (-1.21 .. -2.77)  -> the channel is tracking the fall
  lands in the WEAKNESS range (-0.20 .. +1.10) -> the channel is tracking lesion type,
                                                  demonstrated against the confound

Cells whose t_end < 9.73 s cannot be measured in the registered window and are reported as
NOT ADMITTED with no value, rather than measured in a shortened one.

`sconecmd -e` writes only .sto, never .par, so evaluating a cell cannot disturb its
optimisation record. Only R276WPF* cells are touched.

UNREGISTERED, POST-HOC: added after cell 0 was measured at 16.21 s. No registration amended.
"""
import io, os, sys, glob, json, math, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.0, 9.73          # verbatim from hipgap_r220.py
MIN_DUR, MIN_CYC = 9.73, 5      # gate G

# Reference ranges, read from the shipped deposit rather than typed in.
r228 = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))
SPAS = r228["per_seed_hip_flexion_LmR"]["S"]
WEAK = [v for k in ("W800", "W870", "W892", "W900", "W915", "W950")
        for v in r228["per_seed_hip_flexion_LmR"][k]]


def measure(d, par_name):
    """hipgap_r220.val() applied to one directory, with t_end and cycle count returned too."""
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not sto:
        r = subprocess.run([SCONECMD, "-e", par_name], cwd=d, capture_output=True, timeout=900)
        sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))
        if not sto:
            return {"error": "no sto produced, rc=%d" % r.returncode}
    sto = sto[-1]
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    n_all = len([1 for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE])
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    res = {"sto": os.path.basename(sto), "t_end_s": t_end,
           "cycles_after_settle": n_all, "cycles_in_window": len(cyc),
           "gateG_admitted": bool(t_end >= MIN_DUR and n_all >= MIN_CYC)}
    if t_end < T1 or not cyc:
        res["hip_flexion_LmR"] = None
        res["not_measured_reason"] = (
            "t_end %.3f s is short of the registered window end %.2f s" % (t_end, T1)
            if t_end < T1 else "no complete cycle inside the registered window")
        return res

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)

    res["hip_flexion_LmR"] = rom("hip_flexion_l") - rom("hip_flexion_r")
    return res


rows = []
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_WEAKPF_r276_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    if not os.path.isdir(d):
        continue
    pars = sorted(glob.glob(os.path.join(d, "[0-9]*.par")))
    last = os.path.basename(pars[-1]) if pars else None
    r = measure(d, dep["resolved_par"])
    r.update({"cell": dep["cell"], "prefix": dep["prefix"], "f": dep["f"],
              "seed": dep["seed"], "terminal_objective": dep["terminal_objective"],
              "resolved_par": dep["resolved_par"],
              "last_par_equals_resolved": (last == dep["resolved_par"])})
    rows.append(r)
    print("cell %2d  f=%.2f s%d  obj=%9.4f  t_end=%6.3f  cyc=%2d  gateG=%-5s  LmR=%s"
          % (r["cell"], r["f"], r["seed"], r["terminal_objective"],
             r.get("t_end_s", float("nan")), r.get("cycles_after_settle", -1),
             r["gateG_admitted"],
             "not measured" if r.get("hip_flexion_LmR") is None
             else "%+8.4f" % r["hip_flexion_LmR"]), flush=True)

meas = [r for r in rows if r.get("hip_flexion_LmR") is not None]
fallers = [r for r in meas if r["t_end_s"] < 20.0]

out = {
    "method": "verbatim from hipgap_r220.py: per-cycle mean ROM(l)-ROM(r) deg, window [1.00, 9.73], final cycle dropped",
    "status": "UNREGISTERED, POST-HOC; added after WEAK-PF cell 0 measured 16.21 s",
    "why": "CONFOUND_DURATION_r277.json: the shipped arms are disjoint in duration; WEAK-PF is the first weakness arm that falls",
    "reference_ranges_from_LADDER36_r228": {
        "spastic_n": len(SPAS), "spastic_min": min(SPAS), "spastic_max": max(SPAS),
        "weakness_n": len(WEAK), "weakness_min": min(WEAK), "weakness_max": max(WEAK),
        "shipped_seed_gap_deg": min(WEAK) - max(SPAS),
    },
    "n_cells_available": len(rows), "n_cells_measured": len(meas),
    "cells": rows,
    "fallers_only": {
        "n": len(fallers),
        "note": "cells with t_end < 20.0 s; these are the ones the confound test turns on",
        "values": [{"cell": r["cell"], "f": r["f"], "seed": r["seed"],
                    "t_end_s": r["t_end_s"], "hip_flexion_LmR": r["hip_flexion_LmR"],
                    "in_spastic_range": bool(min(SPAS) <= r["hip_flexion_LmR"] <= max(SPAS)),
                    "in_weakness_range": bool(min(WEAK) <= r["hip_flexion_LmR"] <= max(WEAK))}
                   for r in fallers],
    },
    "incomplete": "This is a partial read of a run still in progress; it is not the registered analysis.",
}
p = os.path.join(PAPER, "WPF_HIPGAP_r278.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

print()
print("shipped reference   spastic %+.4f .. %+.4f   weakness %+.4f .. %+.4f   (seed gap %+.4f)"
      % (min(SPAS), max(SPAS), min(WEAK), max(WEAK), min(WEAK) - max(SPAS)))
if fallers:
    print("\nWEAK-PF cells that FELL -- the cells the confound test turns on:")
    for r in out["fallers_only"]["values"]:
        print("  cell %2d f=%.2f s%d  t_end %6.3f s  LmR %+8.4f   spastic-range=%s  weakness-range=%s"
              % (r["cell"], r["f"], r["seed"], r["t_end_s"], r["hip_flexion_LmR"],
                 r["in_spastic_range"], r["in_weakness_range"]))
else:
    print("\nno measured faller yet")
print("\nwrote %s (%d bytes)  [PARTIAL: %d of 18 cells]" % (p, os.path.getsize(p), len(rows)))
