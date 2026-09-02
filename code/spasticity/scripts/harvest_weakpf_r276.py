"""harvest_weakpf_r276.py -- round 276. Per-cell measurement for PREREG_weakpf_r274.md rev 2.

For each of the 18 WEAK-PF cells: simulated duration, gait-cycle count, net pelvis yaw per
cycle, terminal objective, and the resolved .par with its tie-break.

Then rung 1 FAILURE-DOMINATED evaluated against the REGISTERED criterion, per dose:
"fewer than 2 WEAK-PF cells complete >= 2 gait cycles at this dose".

Duration is measured from the .sto, not inferred from the objective.
Read-only with respect to SCONE\\results.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE = 1.0
T1_R220 = 9.73          # hipgap_r220.py window, reproduced exactly
GATE_G = {"min_duration": 9.73, "min_cycles": 5}
DOSES = [("005", 0.05), ("010", 0.10), ("020", 0.20)]
SEEDS = list(range(101, 107))


def measure(cd):
    """Duration, cycles and yaw from the best .par.sto. Replay may not exist."""
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return {"sto": None, "t_end": None, "n_cycles": None, "yaw_per_cycle": None,
                "note": "no .par.sto -- optimisation wrote no replay"}
    sto = stos[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    out = {"sto": os.path.basename(sto), "t_end": float(t[-1])}
    try:
        grf, thr = S.grf_vertical(cols, dat, "l")
        idx = S.heel_strikes(list(t), grf, thresh=thr)
        cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
               if t[idx[k]] >= SETTLE]
        out["n_cycles"] = len(cyc)
        if len(cyc) >= 2:
            v = np.degrees(np.asarray(S.col(cols, dat, "pelvis_rotation"), dtype=float))
            per = [float(v[b] - v[a]) for a, b in cyc]
            out["yaw_per_cycle"] = float(np.mean(per))
            out["yaw_total"] = float(np.sum(per))
        else:
            out["yaw_per_cycle"] = None
    except Exception as e:
        out["cycle_error"] = str(e)[:120]
    return out



def spearman(x, y):
    """rho and n. No p-value: n is small and the design registers none."""
    n = len(x)
    if n < 3:
        return None, n
    def rank(v):
        o = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[o[j + 1]] == v[o[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[o[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return (num / (dx * dy) if dx and dy else None), n


def load_hip():
    """hip_flexion_LmR per cell from WPF_HIPGAP_r278.json.

    NOT reimplemented here. wpf_hipgap_r278.py runs hipgap_r220.py's code verbatim, skips
    cells whose trace is short of the [1.00, 9.73] window rather than measuring them in a
    shortened one, and is re-run over all 18 cells before this harvest.
    """
    p = os.path.join(PAPER, "WPF_HIPGAP_r278.json")
    if not os.path.exists(p):
        return {}
    d = json.load(io.open(p, encoding="utf-8"))
    out = {}
    for rec in (d.get("cells") or d.get("per_cell") or []):
        k = rec.get("prefix") or rec.get("cell") or rec.get("name")
        if k is not None:
            out[str(k)] = rec
    return out


def main():
    hip = load_hip()
    rows = []
    for tag, f in DOSES:
        for s in SEEDS:
            pre = "R276WPF%s_s%d" % (tag, s)
            dep = os.path.join(PAPER, "RUN_WEAKPF_r276_cell%02d.json"
                               % (DOSES.index((tag, f)) * 6 + SEEDS.index(s)))
            r = {"prefix": pre, "f": f, "seed": s}
            if os.path.exists(dep):
                d = json.load(io.open(dep, encoding="utf-8"))
                r.update({k: d.get(k) for k in
                          ("status", "wall_clock_s", "terminal_objective",
                           "descent_final_10_gens", "n_generations",
                           "resolved_par", "tie_break", "result_dir")})
            g = [x for x in glob.glob(os.path.join(RES, pre + ".*")) if os.path.isdir(x)]
            if g:
                cd = sorted(g)[0]
                r.update(measure(cd))
                r["gate_G"] = {
                    "duration_ok": (r.get("t_end") or 0) >= GATE_G["min_duration"],
                    "cycles_ok": (r.get("n_cycles") or 0) >= GATE_G["min_cycles"],
                    "admitted": ((r.get("t_end") or 0) >= GATE_G["min_duration"]
                                 and (r.get("n_cycles") or 0) >= GATE_G["min_cycles"])}
            hr = hip.get(pre) or hip.get(str(DOSES.index((tag, f)) * 6 + SEEDS.index(s)))
            if hr:
                r["hip_flexion_LmR"] = hr.get("hip_flexion_LmR", hr.get("value"))
                r["hip_source"] = "WPF_HIPGAP_r278.json"
                if r["hip_flexion_LmR"] is None:
                    r["hip_not_measured_reason"] = hr.get(
                        "note", "trace short of the [1.00, 9.73] window")
            rows.append(r)

    # ---- rung 1, against the registered criterion, per dose
    rung1 = {}
    for tag, f in DOSES:
        sub = [r for r in rows if r["f"] == f]
        ok = [r for r in sub if (r.get("n_cycles") or 0) >= 2]
        rung1["f=%.2f" % f] = {
            "cells": len(sub), "cells_with_2plus_cycles": len(ok),
            "criterion": "fewer than 2 cells complete >= 2 gait cycles",
            "FAILURE_DOMINATED": bool(len(ok) < 2),
            "durations": [r.get("t_end") for r in sub],
            "cycles": [r.get("n_cycles") for r in sub]}

    ref = {}
    hp = os.path.join(PAPER, "HIPGAP_r220.json")
    if os.path.exists(hp):
        d = json.load(io.open(hp, encoding="utf-8"))["per_seed"]
        ref = {k: {"per_seed": sorted(v), "min": min(v), "max": max(v)} for k, v in d.items()}

    # ---- UNREGISTERED, POST-HOC: does the hip channel move with duration?
    dur_hip = {}
    pool_x, pool_y = [], []
    for tag, f in DOSES:
        sub = [r for r in rows if r["f"] == f
               and r.get("t_end") is not None
               and r.get("hip_flexion_LmR") is not None]
        x = [r["t_end"] for r in sub]
        y = [r["hip_flexion_LmR"] for r in sub]
        rho, n = spearman(x, y)
        dur_hip["f=%.2f" % f] = {"n": n, "t_end": x, "hip_flexion_LmR": y,
                                 "spearman_hip_vs_t_end": rho}
        pool_x += x
        pool_y += y
    rho, n = spearman(pool_x, pool_y)
    dur_hip["_pooled_WEAKPF"] = {"n": n, "spearman_hip_vs_t_end": rho}

    FULL = 20.0
    def grp(r):
        te = r.get("t_end")
        if te is None:
            return "no_trace"
        return "completer" if te >= FULL - 1e-6 else "faller"
    for r in rows:
        r["duration_group"] = grp(r)

    contrast = {}
    for tag, f in DOSES:
        sub = [r for r in rows if r["f"] == f and r.get("hip_flexion_LmR") is not None]
        fa = [r for r in sub if r["duration_group"] == "faller"]
        co = [r for r in sub if r["duration_group"] == "completer"]
        def mm(v):
            return {"n": len(v), "hip": [x["hip_flexion_LmR"] for x in v],
                    "t_end": [x["t_end"] for x in v],
                    "hip_mean": (sum(x["hip_flexion_LmR"] for x in v) / len(v)) if v else None}
        contrast["f=%.2f" % f] = {
            "fallers": mm(fa), "completers": mm(co),
            "within_dose_difference_of_means": (
                (mm(fa)["hip_mean"] - mm(co)["hip_mean"])
                if fa and co else None),
            "note": ("same anatomy, same dose, same body, same optimiser; the arms of this "
                     "contrast differ only in whether the model stayed up")}

    excluded = [{"prefix": r["prefix"], "f": r["f"], "seed": r["seed"],
                 "t_end": r.get("t_end"), "n_cycles": r.get("n_cycles"),
                 "gate_G": r.get("gate_G"),
                 "reason": r.get("hip_not_measured_reason",
                                 "fails Gate G" if not (r.get("gate_G") or {}).get("admitted")
                                 else "")}
                for r in rows
                if r.get("hip_flexion_LmR") is None
                or not (r.get("gate_G") or {}).get("admitted")]

    gg = [r for r in rows if r.get("gate_G", {}).get("admitted")]
    out = {"round": 276, "prereg": "PREREG_weakpf_r274.md rev 2 sha256 9338ce8a",
           "UNREGISTERED_POST_HOC": {
               "what": "hip_flexion_LmR per WEAK-PF cell, hipgap_r220.py convention",
               "added": "after cell 0, before the batch completed",
               "reason": ("cell 0 falls at 16.21 s. Every dorsiflexor-weakness cell ever "
                          "shipped ran the full 20.0 s at 14 cycles, and the spastic arm falls "
                          "at 13.58-17.85 s. So the shipped 3D comparison had duration and "
                          "cycle count perfectly separated between its two arms, and any "
                          "channel responding to falling would separate them without being "
                          "about lesion type. WEAK-PF is the first weakness arm that falls."),
               "status": "NOT registered in PREREG_weakpf_r274.md rev 2. The registration was "
                         "NOT amended; this is recorded as post-hoc instead.",
               "no_verdict": "numbers deposited beside the r220 reference values, side by "
                             "side. No hypothesis test and no verdict is attached."},
           "r220_reference": ref,
           "UNREGISTERED_POST_HOC_2": {
               "what": "hip_flexion_LmR against t_end, within WEAK-PF and across the corpus",
               "added": "after cell 01, which walked the full duration at the same dose and "
                        "seed-adjacent to cell 00, which fell at 16.21 s",
               "reason": ("f = 0.05 produces both fallers and completers, so the channel can "
                          "be regressed on duration WITHIN one arm at one dose - same lesion, "
                          "same severity, same body, same optimiser, differing only in whether "
                          "the model stayed up. A between-arm comparison can be answered with "
                          "'the arms differ in some other way'; a within-arm one cannot."),
               "no_verdict": "coefficients and n only. No p-value, no verdict, both readings "
                             "ship."},
           "hip_vs_duration_WEAKPF": dur_hip,
           "faller_vs_completer_by_dose": contrast,
           "recorded_exclusions": {
               "cells": excluded,
               "policy": ("a cell excluded by a duration gate is exactly what this analysis "
                          "is about, so exclusions are recorded with their reason and are "
                          "never dropped silently or measured in a shortened window")},
           "n_cells_analysed": sum(1 for r in rows if r.get("hip_flexion_LmR") is not None),
           "NOT_SETTLED": ("duration is the variable of interest; dose is only the instrument "
                           "that generates duration variance. No verdict is attached and none "
                           "is available until the fallers at f = 0.10 and f = 0.20 are in."),
           "hip_vs_duration_corpus": {
               "computed_elsewhere": "CONFOUND_DURATION_r277.json",
               "note": ("the corpus half was computed independently and is NOT recomputed "
                        "here. Key facts carried for reading side by side: all 36 weakness "
                        "cells sit at exactly 20.00 s; no spastic cell reaches it "
                        "(13.58-17.85 s); the arms do not overlap by one sample; within the "
                        "spastic arm rho(hip, t_end) = +0.7143 at n = 6.")},
           "cost_tracks_duration": {
               "note": ("cell 00 fell at 16.21 s and cost 79.85 s; cell 01 walked and cost "
                        "376.78 s. Cost tracks simulated duration, which is the twelfth cost "
                        "figure in this project and the first that explains the earlier "
                        "eleven.")},
           "gate_G_criterion": GATE_G,
           "gate_G_admitted": len(gg),
           "arm": "WEAK-PF: max_isometric_force scaled on soleus_l and gastroc_l, left",
           "cells": rows, "rung1_by_dose": rung1,
           "all_doses_failure_dominated": all(v["FAILURE_DOMINATED"]
                                              for v in rung1.values())}
    p = os.path.join(PAPER, "WEAKPF_RESULT_r276.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")

    print("%-18s %5s %5s %8s %6s %6s %10s %10s %s"
          % ("cell", "f", "seed", "t_end", "cyc", "gateG", "objective", "hip_LmR", "group"))
    for r in rows:
        print("%-18s %5.2f %5d %8s %6s %6s %10s %10s %s"
              % (r["prefix"], r["f"], r["seed"],
                 ("%.3f" % r["t_end"]) if r.get("t_end") is not None else "-",
                 str(r.get("n_cycles", "-")),
                 str((r.get("gate_G") or {}).get("admitted", "-")),
                 ("%.4f" % r["terminal_objective"]) if r.get("terminal_objective") is not None else "-",
                 ("%+.4f" % r["hip_flexion_LmR"]) if r.get("hip_flexion_LmR") is not None else "-",
                 r.get("duration_group", "-")))
    print()
    for k, v in rung1.items():
        print("%s: %d of %d cells reach >= 2 cycles -> FAILURE-DOMINATED = %s"
              % (k, v["cells_with_2plus_cycles"], v["cells"], v["FAILURE_DOMINATED"]))
    print("all doses failure-dominated: %s" % out["all_doses_failure_dominated"])
    print()
    for k, v in contrast.items():
        fa, co = v["fallers"], v["completers"]
        print("%s  fallers n=%d mean %s | completers n=%d mean %s | diff %s"
              % (k, fa["n"], ("%+.4f" % fa["hip_mean"]) if fa["hip_mean"] is not None else "-",
                 co["n"], ("%+.4f" % co["hip_mean"]) if co["hip_mean"] is not None else "-",
                 ("%+.4f" % v["within_dose_difference_of_means"])
                 if v["within_dose_difference_of_means"] is not None else "-"))
    print("recorded exclusions: %d" % len(excluded))


if __name__ == "__main__":
    main()
