"""bandfill_endpoint_r290.py -- the CONFIRMATORY endpoint of PREREG_bandfill_r285.md /
PREREG_bandfill_r287.md, computed only now that the r287 arm has STOPPED.

r285 (c27a7265...) returned rung 1 on 1 in-band cell and is reported as rung 1 permanently.
r287 (580ec823...) continued the sampling with the endpoint, band, guard, comparison and
predicted direction carried from r285 section 3 unaltered, and stopped on COVERAGE when the
third in-band cell appeared. Its stopping rule read t_end only; no channel column was opened
by the launcher.

ENDPOINT, carried unaltered:
  knee_angle_LmR, hipgap_r220.py's convention -- window [1.00, 9.73], cycles wholly inside,
  drop the last, per-cycle mean ROM(l) - ROM(r) in degrees, r281 guard applied.
  Seed-level disjointness of the six spastic cells (R151S s101-106) against the pooled
  plantarflexor-weakness cells RESTRICTED to t_end inside [13.58, 17.85] s.

PREDICTED DIRECTION: weakness POSITIVE, spastic NEGATIVE, ranges disjoint.

LADDER, first match wins:
  1 UNINFORMATIVE  fewer than 3 in-band weakness cells
  2 DISJOINT-AS-PREDICTED
  3 DISJOINT-OPPOSITE
  4 OVERLAP

Nothing here may be changed in response to what it prints.
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
BAND = (13.58, 17.85)
ENDPOINT = "knee_angle_LmR"
ALSO = "hip_flexion_LmR"


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def measure(tag):
    try:
        d = rd(tag)
    except AssertionError as e:
        return {"tag": tag, "error": str(e)}
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
    out = {"tag": tag, "dir": os.path.basename(d), "t_end_s": t_end,
           "n_cycles": len(allc), "n_cycles_in_window": len(win)}
    if t_end < T1 or not win:
        out["measured"] = False
        out["guard"] = "t_end %.3f < %.2f" % (t_end, T1) if t_end < T1 else "no cycle in window"
        out[ENDPOINT] = None
        out[ALSO] = None
        return out

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in win) / len(win)

    out["measured"] = True
    out[ENDPOINT] = rom("knee_angle_l") - rom("knee_angle_r")
    out[ALSO] = rom("hip_flexion_l") - rom("hip_flexion_r")
    return out


def weakness_tags():
    """Every plantarflexor-weakness cell that exists, across r276, r285 and r287."""
    tags = []
    for pre in ("R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"):
        tags += ["%s_s%d" % (pre, s) for s in range(101, 107)]
    for d in sorted(glob.glob(os.path.join(RES, "R287BF*"))):
        b = os.path.basename(d).split(".")[0]
        if b not in tags:
            tags.append(b)
    return tags


def main():
    spastic = [measure("R151S_s%d" % s) for s in range(101, 107)]
    weak = [measure(t) for t in weakness_tags()]

    in_band = [r for r in weak if r.get("measured")
               and BAND[0] <= r["t_end_s"] <= BAND[1]]
    sp = [r[ENDPOINT] for r in spastic if r.get("measured")]
    wk = [r[ENDPOINT] for r in in_band]

    res = {"round": 290,
           "prereg_r285": "c27a72650f7d2bb13eb6ae3d7f8b876124036270ef105a604bea92dcd73512ab",
           "prereg_r287": "580ec8230a76c051e069f8a2d790dedd1199b95ac7b5fb1a1a509758570a4fcf",
           "status": "CONFIRMATORY. Endpoint computed only after the r287 arm stopped on its "
                     "registered coverage rule, which read t_end only.",
           "endpoint": ENDPOINT, "band_s": list(BAND),
           "predicted": "weakness POSITIVE, spastic NEGATIVE, ranges disjoint",
           "spastic_cells": spastic, "weakness_cells": weak,
           "n_weakness_total": len(weak),
           "n_weakness_in_band": len(in_band),
           "in_band": [{"tag": r["tag"], "t_end_s": r["t_end_s"],
                        ENDPOINT: r[ENDPOINT], ALSO: r[ALSO]} for r in in_band]}

    if len(in_band) < 3:
        res["RUNG"] = "1 UNINFORMATIVE"
        res["endpoint_evaluated"] = False
    else:
        disjoint = (min(wk) > max(sp)) or (min(sp) > max(wk))
        res["endpoint_evaluated"] = True
        res["spastic_values"] = sp
        res["weakness_in_band_values"] = wk
        res["ranges"] = {"spastic": [min(sp), max(sp)], "weakness": [min(wk), max(wk)]}
        res["disjoint"] = bool(disjoint)
        res["gap"] = (min(wk) - max(sp)) if min(wk) > max(sp) else (
            (min(sp) - max(wk)) if min(sp) > max(wk) else None)
        if disjoint and all(v > 0 for v in wk) and all(v < 0 for v in sp):
            res["RUNG"] = "2 DISJOINT-AS-PREDICTED"
        elif disjoint:
            res["RUNG"] = "3 DISJOINT-OPPOSITE"
        else:
            res["RUNG"] = "4 OVERLAP"
        if disjoint:
            allv = sp + wk
            n1 = len(sp)
            obs = res["gap"]
            tot = cnt = 0
            for comb in itertools.combinations(range(len(allv)), n1):
                a = [allv[i] for i in comb]
                b = [allv[i] for i in range(len(allv)) if i not in comb]
                g = max(min(b) - max(a), min(a) - max(b))
                tot += 1
                if g >= obs - 1e-12:
                    cnt += 1
            res["permutation"] = {"method": "exhaustive over C(%d,%d)" % (len(allv), n1),
                                  "assignments": tot, "count_ge_observed": cnt,
                                  "floor": 1.0 / tot,
                                  "note": "reported as a floor, never as a p-value"}
        # the deposited secondary
        res["hip_secondary"] = {
            "note": "deposited, NOT the endpoint, not promoted",
            "spastic": [r[ALSO] for r in spastic if r.get("measured")],
            "weakness_in_band": [r[ALSO] for r in in_band]}

    io.open(os.path.join(PAPER, "BANDFILL_ENDPOINT_r290.json"), "w",
            encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")

    print("SPASTIC (n=%d)" % len(sp))
    for r in spastic:
        print("  %-16s t_end %7.3f  %s %+9.4f   hip %+9.4f"
              % (r["tag"], r["t_end_s"], ENDPOINT, r[ENDPOINT], r[ALSO]))
    print("\nWEAKNESS IN BAND [%.2f, %.2f] (n=%d of %d cells)"
          % (BAND[0], BAND[1], len(in_band), len(weak)))
    for r in in_band:
        print("  %-16s t_end %7.3f  %s %+9.4f   hip %+9.4f"
              % (r["tag"], r["t_end_s"], ENDPOINT, r[ENDPOINT], r[ALSO]))
    print()
    if res.get("endpoint_evaluated"):
        print("spastic range  %+.4f .. %+.4f" % (min(sp), max(sp)))
        print("weakness range %+.4f .. %+.4f" % (min(wk), max(wk)))
        print("disjoint: %s   gap: %s" % (res["disjoint"],
              ("%+.4f" % res["gap"]) if res["gap"] is not None else "-"))
        if "permutation" in res:
            p = res["permutation"]
            print("permutation: %d of %d, floor 1/%d"
                  % (p["count_ge_observed"], p["assignments"], p["assignments"]))
    print("\nRUNG: %s" % res["RUNG"])


if __name__ == "__main__":
    main()
