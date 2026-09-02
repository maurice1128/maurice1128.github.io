"""bandfill_endpoint_r291.py -- the CONFIRMATORY endpoint of PREREG_bandfill_r291.md rev2
(0b2b7274...), computed only now that the r291 arm has STOPPED on its registered 60-cell cap.

ENDPOINT, carried from r285 section 3 through r287 and r291 unaltered:
  knee_angle_LmR, hipgap_r220.py's convention -- window [1.00, 9.73], cycles wholly inside,
  drop the last, per-cycle mean ROM(l) - ROM(r) in degrees, r281 guard applied.

PREDICTED DIRECTION: weakness POSITIVE, spastic NEGATIVE, ranges disjoint.

section 3a -- TWO READINGS, BOTH REPORTED, NEITHER PRIMARY:
  A  original group: the six R151S KV 0.050 cells vs the in-band weakness cells
  B  widened group : all in-band spastic cells across KV 0.050, 0.035, 0.070, same weakness
  If A and B disagree, the disagreement is the result and neither is chosen.
  A closes GAP 1 only. B is the only one that closes GAP 2.

section 6 -- if fewer than THREE spastic conditions land in band, reading B is NOT available,
the arm reports reading A at whatever in-band n it reached, and reports GAP 2 as STILL OPEN in
the same sentence as the result.

COVERAGE METHOD (SO-27, adopted r305): every count here is computed by measuring .sto over the
corpus. No launcher counter is consulted. run_bandfill_r291.py's coverage() silently skips any
cell deposit lacking a t_end_s key and is blind to 30 r276/r285 deposits; it is an operational
convenience and is not the endpoint.

Nothing here may be changed in response to what it prints. Read-only.
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


def rd(tag):                                    # carried from r290, unaltered
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def measure(tag):                               # carried from r290, unaltered
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


def dirs_for(prefix):
    """Every seed tag on disk for a family prefix."""
    tags = []
    for d in sorted(glob.glob(os.path.join(RES, prefix + "_s*"))):
        b = os.path.basename(d).split(".")[0]
        if b not in tags:
            tags.append(b)
    return tags


def weakness_tags():
    """Every plantarflexor-weakness cell that exists: r276, r285, r287 and now r291."""
    tags = []
    for pre in ("R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"):
        tags += ["%s_s%d" % (pre, s) for s in range(101, 107)]
    for pre in ("R287BF", "R291BF"):
        for d in sorted(glob.glob(os.path.join(RES, pre + "*"))):
            b = os.path.basename(d).split(".")[0]
            if b not in tags:
                tags.append(b)
    return tags


def perm_floor(sp, wk):
    """Exhaustive seed-level permutation on the disjointness gap. Floor, never a p-value."""
    allv = list(sp) + list(wk)
    n1 = len(sp)
    obs = max(min(wk) - max(sp), min(sp) - max(wk))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        a = [allv[i] for i in comb]
        b = [allv[i] for i in range(len(allv)) if i not in comb]
        g = max(min(b) - max(a), min(a) - max(b))
        tot += 1
        if g >= obs - 1e-12:
            cnt += 1
    return {"method": "exhaustive over C(%d,%d)" % (len(allv), n1),
            "assignments": tot, "count_ge_observed": cnt, "floor": 1.0 / tot,
            "floor_str": "1/%d" % tot,
            "note": "reported as a floor, never as a p-value"}


def rung(sp, wk):
    disjoint = (min(wk) > max(sp)) or (min(sp) > max(wk))
    if not disjoint:
        return "4 OVERLAP", False, None
    gap = (min(wk) - max(sp)) if min(wk) > max(sp) else (min(sp) - max(wk))
    if all(v > 0 for v in wk) and all(v < 0 for v in sp):
        return "2 DISJOINT-AS-PREDICTED", True, gap
    return "3 DISJOINT-OPPOSITE", True, gap


def main():
    # ---- spastic side: the original group and the two r291 conditions
    spA = [measure("R151S_s%d" % s) for s in range(101, 107)]           # KV 0.050
    sp35 = [measure(t) for t in dirs_for("R291KV0035")]                 # KV 0.035
    sp70 = [measure(t) for t in dirs_for("R291KV0070")]                 # KV 0.070
    weak = [measure(t) for t in weakness_tags()]

    def inband(rs):
        return [r for r in rs if r.get("measured") and BAND[0] <= r["t_end_s"] <= BAND[1]]

    wk_ib = inband(weak)
    wk = [r[ENDPOINT] for r in wk_ib]

    # ---- coverage, measured from .sto over the corpus (SO-27)
    cond = {}
    for name, rs in (("KV 0.050", spA), ("KV 0.035", sp35), ("KV 0.070", sp70)):
        hits = inband(rs)
        cond[name] = {"n_cells_total": len(rs), "n_in_band": len(hits),
                      "in_band_tags": [r["tag"] for r in hits],
                      "t_end_range": [round(min(r["t_end_s"] for r in rs if r.get("t_end_s")), 2),
                                      round(max(r["t_end_s"] for r in rs if r.get("t_end_s")), 2)]}
    n_cond_in_band = sum(1 for v in cond.values() if v["n_in_band"] > 0)

    res = {
     "round": 306,
     "prereg": "PREREG_bandfill_r291.md rev2",
     "prereg_sha256": "0b2b7274",
     "status": ("CONFIRMATORY. The r291 arm stopped on its registered 60-cell cap (section 5's "
                "second clause, the only one that could fire). Endpoint computed only after."),
     "arm_stop": {"cells_run": 60, "cells_registered": 60,
                  "stop_reason": "REGISTERED STOP -- 60-cell cap",
                  "terminal_record_absent_because": (
                      "the running process loaded run_bandfill_r291.py before the r305 terminal-"
                      "record patch; its absence is explained, not unknown")},
     "COVERAGE_METHOD": ("Measured from .sto over the corpus per SO-27. No launcher counter was "
                         "consulted. run_bandfill_r291.py's coverage() skips deposits lacking a "
                         "t_end_s key and is blind to 30 r276/r285 cells; it reports 6 where the "
                         "corpus has 8."),
     "endpoint": ENDPOINT, "band_s": list(BAND), "guard_t1_s": T1,
     "predicted": "weakness POSITIVE, spastic NEGATIVE, ranges disjoint",
     "n_weakness_total": len(weak), "n_weakness_in_band": len(wk_ib),
     "weakness_in_band": [{"tag": r["tag"], "t_end_s": r["t_end_s"],
                           ENDPOINT: r[ENDPOINT], ALSO: r[ALSO]} for r in wk_ib],
     "spastic_conditions": cond,
     "n_spastic_conditions_in_band": n_cond_in_band,
     "GAP_1": ("CLOSED -- %d in-band weakness cells" % len(wk_ib)),
     "GAP_2": None,
    }

    # ---------------- READING A: the original six R151S, whatever the widening does
    a_meas = [r for r in spA if r.get("measured")]
    spa = [r[ENDPOINT] for r in a_meas]
    A = {"reading": "A -- original group",
         "spastic_group": "the six R151S KV 0.050 cells, exactly as PREREG_bandfill_r285 sec3 names them",
         "n_spastic": len(spa), "n_weakness_in_band": len(wk),
         "spastic_values": spa, "weakness_values": wk,
         "closes": "GAP 1 only -- its spastic side stays one condition"}
    if len(wk_ib) < 3:
        A["RUNG"] = "1 UNINFORMATIVE"
        A["endpoint_evaluated"] = False
    else:
        rg, dj, gap = rung(spa, wk)
        A.update({"RUNG": rg, "endpoint_evaluated": True, "disjoint": dj, "gap": gap,
                  "ranges": {"spastic": [min(spa), max(spa)],
                             "weakness": [min(wk), max(wk)]}})
        if dj:
            A["permutation"] = perm_floor(spa, wk)
    res["READING_A"] = A

    # ---------------- READING B: widened, available only at >= 3 in-band conditions
    B = {"reading": "B -- widened group",
         "spastic_group": "all in-band spastic cells across KV 0.050, 0.035 and 0.070",
         "n_spastic_conditions_in_band": n_cond_in_band,
         "closes": "GAP 2 -- the only reading that can"}
    if n_cond_in_band < 3:
        B["AVAILABLE"] = False
        B["RUNG"] = "NOT AVAILABLE"
        B["why"] = ("Fewer than three spastic conditions landed in band (%d of 3). "
                    "PREREG_bandfill_r291 sec6 pre-registered exactly this branch: reading B is "
                    "not available, the arm reports reading A at whatever in-band n it reached, "
                    "and GAP 2 is reported STILL OPEN in the same sentence as the result."
                    % n_cond_in_band)
        B["empty_conditions"] = [k for k, v in cond.items() if v["n_in_band"] == 0]
        res["GAP_2"] = ("STILL OPEN -- %d of 3 spastic conditions in band. A larger weakness n "
                        "does not close it and may not be presented as though it does."
                        % n_cond_in_band)
    else:
        spb_r = inband(spA) + inband(sp35) + inband(sp70)
        spb = [r[ENDPOINT] for r in spb_r]
        B["AVAILABLE"] = True
        B["n_spastic"] = len(spb)
        B["spastic_values"] = spb
        B["spastic_tags"] = [r["tag"] for r in spb_r]
        B["weakness_values"] = wk
        if len(wk_ib) < 3:
            B["RUNG"] = "1 UNINFORMATIVE"
            B["endpoint_evaluated"] = False
        else:
            rg, dj, gap = rung(spb, wk)
            B.update({"RUNG": rg, "endpoint_evaluated": True, "disjoint": dj, "gap": gap,
                      "ranges": {"spastic": [min(spb), max(spb)],
                                 "weakness": [min(wk), max(wk)]}})
            if dj:
                B["permutation"] = perm_floor(spb, wk)
        res["GAP_2"] = "CLOSED -- 3 spastic conditions in band"
    res["READING_B"] = B

    res["AGREEMENT"] = ("Not evaluable: reading B is unavailable." if not B.get("AVAILABLE")
                        else ("A and B AGREE on rung" if A.get("RUNG") == B.get("RUNG")
                              else "A and B DISAGREE -- per sec3a the disagreement IS the result "
                                   "and neither is chosen"))
    res["hip_secondary"] = {"note": "deposited, NOT the endpoint, not promoted",
                            "spastic_KV0050": [r[ALSO] for r in a_meas],
                            "weakness_in_band": [r[ALSO] for r in wk_ib]}
    res["all_cells"] = {"spastic_KV0050": spA, "spastic_KV0035": sp35,
                        "spastic_KV0070": sp70, "weakness": weak}

    p = os.path.join(PAPER, "BANDFILL_ENDPOINT_r291.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")

    # ---------------- report
    print("ARM: 60 of 60 cells, stopped on the registered cap.")
    print("COVERAGE (from .sto over the corpus, SO-27 -- no launcher counter):")
    for k in sorted(cond):
        v = cond[k]
        print("   %-9s %d of %d in band   t_end %.2f-%.2f  %s"
              % (k, v["n_in_band"], v["n_cells_total"], v["t_end_range"][0],
                 v["t_end_range"][1], v["in_band_tags"]))
    print("   spastic conditions in band: %d of 3" % n_cond_in_band)
    print("   weakness cells in band    : %d of %d measured" % (len(wk_ib), len(weak)))
    print()
    print("WEAKNESS IN BAND [%.2f, %.2f]" % BAND)
    for r in wk_ib:
        print("  %-18s t_end %7.3f  %s %+9.4f   hip %+9.4f"
              % (r["tag"], r["t_end_s"], ENDPOINT, r[ENDPOINT], r[ALSO]))
    print("\nSPASTIC KV 0.050 (reading A group)")
    for r in a_meas:
        print("  %-18s t_end %7.3f  %s %+9.4f   hip %+9.4f"
              % (r["tag"], r["t_end_s"], ENDPOINT, r[ENDPOINT], r[ALSO]))
    print()
    for tag, R in (("READING A", A), ("READING B", B)):
        print("--- %s: %s" % (tag, R.get("RUNG")))
        if R.get("endpoint_evaluated"):
            print("    spastic  %+.4f .. %+.4f" % (R["ranges"]["spastic"][0],
                                                   R["ranges"]["spastic"][1]))
            print("    weakness %+.4f .. %+.4f" % (R["ranges"]["weakness"][0],
                                                   R["ranges"]["weakness"][1]))
            print("    disjoint %s   gap %+.4f" % (R["disjoint"], R["gap"]))
            if "permutation" in R:
                print("    floor %s  (%d of %d assignments)"
                      % (R["permutation"]["floor_str"],
                         R["permutation"]["count_ge_observed"],
                         R["permutation"]["assignments"]))
        elif R.get("why"):
            print("    %s" % R["why"])
    print("\nGAP 1: %s" % res["GAP_1"])
    print("GAP 2: %s" % res["GAP_2"])
    print("\nwrote %s" % p)


if __name__ == "__main__":
    main()
