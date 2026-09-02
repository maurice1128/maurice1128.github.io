"""dfsevere_result_r303.py -- the registered endpoint of PREREG_dfsevere_r293.md (d4631d00...).

ENDPOINT IS t_end. NO JOINT CHANNEL IS COMPUTED -- section 3 forbids it and this arm is a
duration probe. Cycle count and Gate-G admission are deposited as context.

Ladder, section 6, first match wins:
  1 NOT ADMISSIBLE            the x0.00 condition is rejected by the model
  2 FALLS IN BAND             at least one cell has t_end inside [13.58, 17.85]
  3 FALLS BUT SKIPS THE BAND  cells fall but none lands inside the band
  4 STRUCTURALLY NON-FALLING  every cell at every severity completes 20.000 s

Evaluates each cell to .sto first with `sconecmd -e`, which writes only .sto.
Read-only with respect to every existing cell.
"""
import glob
import io
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
BAND = (13.58, 17.85)
GATE_G = {"min_duration": 9.73, "min_cycles": 5}
FULL = 20.0
SETTLE = 1.0


def evaluate(cd, par):
    if glob.glob(os.path.join(cd, "*.par.sto")):
        return "already"
    if not par:
        return "no par"
    r = subprocess.run([SCONE, "-e", par], cwd=cd, capture_output=True, timeout=900)
    return "rc=%d" % r.returncode


def measure(cd):
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return {"sto": None, "t_end_s": None, "n_cycles": None}
    cols, dat = S.load_sto(stos[-1])
    t = list(S.col(cols, dat, "time"))
    out = {"sto": os.path.basename(stos[-1]), "t_end_s": float(t[-1])}
    try:
        grf, thr = S.grf_vertical(cols, dat, "l")
        idx = S.heel_strikes(t, grf, thresh=thr)
        out["n_cycles"] = len([1 for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE])
    except Exception as e:
        out["n_cycles"] = None
        out["cycle_error"] = str(e)[:100]
    return out


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(PAPER, "RUN_DFSEVERE_r293_cell*.json"))):
        d = json.load(io.open(p, encoding="utf-8"))
        r = {"cell": d.get("cell"), "prefix": d.get("prefix"), "scale": d.get("scale"),
             "seed": d.get("seed"), "wall_clock_s": d.get("wall_clock_s"),
             "terminal_objective": d.get("terminal_objective"),
             "result_dir": d.get("result_dir"),
             "resolved_par": d.get("resolved_par"),
             "n_generations": d.get("n_generations")}
        cd = os.path.join(RES, d["result_dir"]) if d.get("result_dir") else None
        if cd and os.path.isdir(cd):
            r["n_par_files"] = len(glob.glob(os.path.join(cd, "[0-9]*.par")))
            r["eval"] = evaluate(cd, d.get("resolved_par"))
            r.update(measure(cd))
        else:
            r["eval"] = "no result dir"
        te, nc = r.get("t_end_s"), r.get("n_cycles")
        r["gate_G_admitted"] = bool(te is not None and nc is not None
                                    and te >= GATE_G["min_duration"]
                                    and nc >= GATE_G["min_cycles"])
        r["in_band"] = bool(te is not None and BAND[0] <= te <= BAND[1])
        r["completes"] = bool(te is not None and te >= FULL - 1e-6)
        rows.append(r)

    by = {}
    for sc in (0.50, 0.30, 0.10, 0.00):
        sub = [r for r in rows if abs((r["scale"] or -1) - sc) < 1e-9]
        te = [r["t_end_s"] for r in sub if r["t_end_s"] is not None]
        by["x%.2f" % sc] = {
            "n_cells": len(sub), "n_with_sto": len(te),
            "t_end": te, "t_end_range": [min(te), max(te)] if te else None,
            "n_in_band": sum(1 for r in sub if r["in_band"]),
            "n_complete": sum(1 for r in sub if r["completes"]),
            "n_gateG": sum(1 for r in sub if r["gate_G_admitted"]),
            "n_par_files": [r.get("n_par_files") for r in sub],
            "objectives": [r["terminal_objective"] for r in sub]}

    x000 = by["x0.00"]
    not_admissible = (x000["n_with_sto"] == 0 and all(
        (n or 0) == 0 for n in x000["n_par_files"]))
    any_in_band = any(r["in_band"] for r in rows)
    any_fall = any(r["t_end_s"] is not None and r["t_end_s"] < FULL - 1e-6 for r in rows)
    all_complete = all(r["completes"] for r in rows if r["t_end_s"] is not None)

    if not_admissible:
        rung = "1 NOT ADMISSIBLE (x0.00); ladder stands at the other three"
    elif any_in_band:
        rung = "2 FALLS IN BAND"
    elif any_fall:
        rung = "3 FALLS BUT SKIPS THE BAND"
    elif all_complete:
        rung = "4 STRUCTURALLY NON-FALLING"
    else:
        rung = "UNRESOLVED"

    sub_rung = ("2 FALLS IN BAND" if any_in_band else
                ("3 FALLS BUT SKIPS THE BAND" if any_fall else
                 ("4 STRUCTURALLY NON-FALLING" if all_complete else "UNRESOLVED")))

    out = {"round": 303, "prereg": "PREREG_dfsevere_r293.md",
           "prereg_sha256": "d4631d00c7876e3b5f6c7d45d1de3d353f12b8f524b3614e392dc006be7ebedf",
           "endpoint": "t_end", "no_joint_channel_computed": True,
           "band": list(BAND), "gate_G": GATE_G,
           "per_cell": rows, "by_severity": by,
           "x000_not_admissible": bool(not_admissible),
           "x000_evidence": {"n_with_sto": x000["n_with_sto"],
                             "n_par_files_per_cell": x000["n_par_files"],
                             "objectives": x000["objectives"],
                             "wall_clock_s": [r["wall_clock_s"] for r in rows
                                              if abs((r["scale"] or -1)) < 1e-9]},
           "RUNG": rung,
           "RUNG_over_admissible_severities": sub_rung}

    p = os.path.join(PAPER, "DFSEVERE_RESULT_r303.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")

    print("%-18s %6s %5s %9s %6s %7s %8s %s"
          % ("cell", "scale", "seed", "t_end", "cyc", "gateG", "in_band", "eval"))
    for r in rows:
        print("%-18s %6.2f %5d %9s %6s %7s %8s %s"
              % (r["prefix"], r["scale"], r["seed"],
                 ("%.3f" % r["t_end_s"]) if r["t_end_s"] is not None else "-",
                 str(r.get("n_cycles", "-")), str(r["gate_G_admitted"]),
                 str(r["in_band"]), r.get("eval")))
    print()
    for k, v in by.items():
        print("%s  n=%d  with_sto=%d  t_end %s  in_band=%d complete=%d gateG=%d"
              % (k, v["n_cells"], v["n_with_sto"],
                 ("%.3f..%.3f" % tuple(v["t_end_range"])) if v["t_end_range"] else "none",
                 v["n_in_band"], v["n_complete"], v["n_gateG"]))
    print("\nx0.00 NOT ADMISSIBLE: %s" % not_admissible)
    print("RUNG: %s" % rung)
    print("RUNG over admissible severities: %s" % sub_rung)


if __name__ == "__main__":
    main()
