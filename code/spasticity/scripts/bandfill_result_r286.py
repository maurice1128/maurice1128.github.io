"""bandfill_result_r286.py -- the CONFIRMATORY analysis registered at PREREG_bandfill_r285.md
(sha256 c27a72650f7d2bb13eb6ae3d7f8b876124036270ef105a604bea92dcd73512ab).

Registered endpoint, section 3: knee_angle_LmR, hipgap_r220.py's convention (window
[1.00, 9.73], cycles wholly inside, drop the last, per-cycle mean ROM(l) - ROM(r), degrees),
with the r281 guard -- a cell whose t_end is short of 9.73 s is NOT measured.

Comparison: seed-level disjointness of the six spastic cells (R151S s101-106, depth 90)
against plantarflexor-weakness cells RESTRICTED to t_end inside [13.58, 17.85] s.

Ladder, section 5, first match wins:
  1 UNINFORMATIVE          fewer than 3 weakness cells in band
  2 DISJOINT-AS-PREDICTED  in-band weakness all positive, spastic all negative, disjoint
  3 DISJOINT-OPPOSITE      disjoint, signs the other way round
  4 OVERLAP                ranges overlap

Nothing in this script may be changed in response to what it prints.
Read-only.
"""
import glob
import io
import itertools
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
BAND = (13.58, 17.85)                      # observed spastic duration range, registered
SEEDS = list(range(101, 107))
ENDPOINT = "knee_angle_LmR"
ALSO = "hip_flexion_LmR"                   # deposited, NOT the endpoint


def rd(tag):
    """Duplicate-directory guard: >= 91 history lines, exactly one match."""
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def measure(tag):
    d = rd(tag)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        return {"tag": tag, "dir": os.path.basename(d), "error": "no .par.sto"}
    cols, dat = S.load_sto(stos[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    allc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in win) / len(win)

    out = {"tag": tag, "dir": os.path.basename(d), "sto": os.path.basename(stos[-1]),
           "t_end_s": t_end, "n_cycles": len(allc), "n_cycles_in_window": len(win)}
    if t_end < T1 or not win:
        out["measured"] = False
        out["guard"] = ("t_end %.3f < %.2f: window truncated by the cell's own collapse"
                        % (t_end, T1)) if t_end < T1 else "no complete cycle in window"
        out[ENDPOINT] = None
        out[ALSO] = None
    else:
        out["measured"] = True
        out[ENDPOINT] = rom("knee_angle_l") - rom("knee_angle_r")
        out[ALSO] = rom("hip_flexion_l") - rom("hip_flexion_r")
    return out


def main():
    spastic = [measure("R151S_s%d" % s) for s in SEEDS]
    weak = []
    for tag, f in (("007", 0.07), ("008", 0.08)):
        for s in SEEDS:
            r = measure("R285BF%s_s%d" % (tag, s))
            r["f"] = f
            r["seed"] = s
            weak.append(r)

    in_band = [r for r in weak
               if r.get("measured") and BAND[0] <= r["t_end_s"] <= BAND[1]]
    sp = [r[ENDPOINT] for r in spastic if r.get("measured")]

    res = {"round": 286, "prereg": "PREREG_bandfill_r285.md",
           "prereg_sha256": "c27a72650f7d2bb13eb6ae3d7f8b876124036270ef105a604bea92dcd73512ab",
           "status": "CONFIRMATORY -- registered before execution, not amended",
           "endpoint": ENDPOINT, "band_s": list(BAND),
           "spastic_cells": spastic, "weakness_cells": weak,
           "n_weakness_in_band": len(in_band),
           "in_band_tags": [r["tag"] for r in in_band]}

    if len(in_band) < 3:
        res["RUNG"] = "1 UNINFORMATIVE"
        res["reason"] = ("fewer than 3 plantarflexor-weakness cells landed inside "
                         "[%.2f, %.2f] s; per section 4 the endpoint is NOT evaluated and no "
                         "substitute endpoint, widened band or pooling is permitted"
                         % BAND)
        res["endpoint_evaluated"] = False
    else:
        wk = [r[ENDPOINT] for r in in_band]
        disjoint = (min(wk) > max(sp)) or (min(sp) > max(wk))
        res["endpoint_evaluated"] = True
        res["weakness_in_band_values"] = wk
        res["spastic_values"] = sp
        res["ranges"] = {"weakness": [min(wk), max(wk)], "spastic": [min(sp), max(sp)]}
        res["disjoint"] = bool(disjoint)
        if disjoint and all(v > 0 for v in wk) and all(v < 0 for v in sp):
            res["RUNG"] = "2 DISJOINT-AS-PREDICTED"
        elif disjoint:
            res["RUNG"] = "3 DISJOINT-OPPOSITE"
        else:
            res["RUNG"] = "4 OVERLAP"
        if disjoint:
            n1, n2 = len(sp), len(wk)
            allv = sp + wk
            obs = min(wk) - max(sp) if min(wk) > max(sp) else min(sp) - max(wk)
            cnt = 0
            tot = 0
            for comb in itertools.combinations(range(n1 + n2), n1):
                a = [allv[i] for i in comb]
                b = [allv[i] for i in range(n1 + n2) if i not in comb]
                g = max(min(b) - max(a), min(a) - max(b))
                tot += 1
                if g >= obs - 1e-12:
                    cnt += 1
            res["permutation"] = {"method": "exhaustive over C(%d,%d)" % (n1 + n2, n1),
                                  "assignments": tot, "count_ge_observed": cnt,
                                  "floor": 1.0 / tot,
                                  "note": "count reported as a floor, never as a p-value"}

    p = os.path.join(PAPER, "BANDFILL_RESULT_r286.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")

    print("%-18s %5s %9s %6s %7s %12s %12s"
          % ("cell", "f", "t_end", "cyc", "in band", ENDPOINT, ALSO))
    for r in spastic:
        print("%-18s %5s %9.3f %6d %7s %12s %12s"
              % (r["tag"], "S", r.get("t_end_s", 0), r.get("n_cycles", 0), "-",
                 ("%+.4f" % r[ENDPOINT]) if r.get(ENDPOINT) is not None else "not measured",
                 ("%+.4f" % r[ALSO]) if r.get(ALSO) is not None else "-"))
    for r in weak:
        ib = r.get("measured") and BAND[0] <= r.get("t_end_s", 0) <= BAND[1]
        print("%-18s %5.2f %9.3f %6d %7s %12s %12s"
              % (r["tag"], r["f"], r.get("t_end_s", 0), r.get("n_cycles", 0),
                 "YES" if ib else "no",
                 ("%+.4f" % r[ENDPOINT]) if r.get(ENDPOINT) is not None else "not measured",
                 ("%+.4f" % r[ALSO]) if r.get(ALSO) is not None else "-"))
    print()
    print("weakness cells inside [%.2f, %.2f] s: %d" % (BAND[0], BAND[1], len(in_band)))
    print("RUNG: %s" % res["RUNG"])
    if res.get("reason"):
        print("  %s" % res["reason"])


if __name__ == "__main__":
    main()
