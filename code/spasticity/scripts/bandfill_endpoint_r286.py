# -*- coding: utf-8 -*-
"""THE REGISTERED ENDPOINT of PREREG_bandfill_r285.md (c27a72650f7d2bb1...).

Executes sections 3, 4 and 5 of that registration and nothing else. The ladder is evaluated
mechanically, in order, first match wins, so no reading of the data can choose the rung.

  section 3  endpoint knee_angle_LmR, hipgap_r220.py's convention, window [1.00, 9.73],
             cycles wholly inside it, last dropped, r281 guard (t_end short of 9.73 s -> not
             measured). Comparison: the six spastic cells against plantarflexor-weakness cells
             restricted to t_end inside [13.58, 17.85] s.
             PREDICTED: weakness POSITIVE, spastic NEGATIVE, ranges disjoint.
  section 4  fewer than THREE in-band weakness cells -> UNINFORMATIVE, endpoint NOT evaluated,
             no substitute endpoint, no widened band, no pooling.
  section 5  rung 1 UNINFORMATIVE / 2 DISJOINT-AS-PREDICTED / 3 DISJOINT-OPPOSITE / 4 OVERLAP.
             Null if disjoint: exhaustive permutation of arm labels over the in-band cells,
             reported as a FLOOR, never as a p-value.

hip_flexion_LmR is measured and deposited. Per section 3 it is NOT the endpoint.

Self-check as in r282: the spastic hip values must reproduce LADDER36_r228.json to < 1e-9 deg
or the script refuses to run.
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = "PREREG_bandfill_r285.md"
SETTLE, T1 = 1.0, 9.73
BAND = (13.58, 17.85)          # the observed spastic duration range, section 3
MIN_IN_BAND = 3                # section 4
SEEDS = list(range(101, 107))
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]


def meas(sto):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if not c or t_end < T1:                 # r281 guard
        return None, t_end, len(c)

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in c) / len(c)

    o = {p + "_LmR": rom(p + "_l") - rom(p + "_r") for p in PAIR}
    return o, t_end, len(c)


def find_dir(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    assert len(ds) == 1, "%s resolves to %d directories" % (tag, len(ds))
    return ds[0]


def sto_of(d):
    g = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    return g[-1] if g else None


# ---------------------------------------------------------------- spastic arm + self-check
spastic = []
for s in SEEDS:
    o, te, nc = meas(sto_of(find_dir("R151S_s%d" % s)))
    assert o is not None, "spastic seed %d unmeasurable" % s
    spastic.append({"id": "S_s%d" % s, "t_end_s": te, "n_cycles_in_window": nc, **o})

ref = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))["per_seed_hip_flexion_LmR"]["S"]
bad = [(SEEDS[i], a["hip_flexion_LmR"], b) for i, (a, b) in enumerate(zip(spastic, ref))
       if abs(a["hip_flexion_LmR"] - b) > 1e-9]
if bad:
    print("SELF-CHECK FAILED -- measurement path drifted from the shipped one:")
    for sd, a, b in bad:
        print("  seed %d: %+.12f vs shipped %+.12f" % (sd, a, b))
    sys.exit(1)
print("self-check: spastic hip_flexion_LmR reproduces LADDER36_r228.json to < 1e-9 deg\n")

# ---------------------------------------------------------------- the band-fill arm
weak, excluded = [], []
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_BANDFILL_r285_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    sto = sto_of(d) if os.path.isdir(d) else None
    if not sto:
        excluded.append({"id": "BF_c%02d" % dep["cell"], "f": dep["f"], "seed": dep["seed"],
                         "reason": "no .sto"})
        continue
    o, te, nc = meas(sto)
    rec = {"id": "BF_c%02d" % dep["cell"], "f": dep["f"], "seed": dep["seed"],
           "t_end_s": te, "n_cycles_in_window": nc, "result_dir": dep["result_dir"],
           "terminal_objective": dep.get("terminal_objective")}
    if o is None:
        rec["reason"] = "t_end %.3f s short of the %.2f s window (r281 guard)" % (te, T1)
        excluded.append(rec)
        continue
    rec.update(o)
    rec["in_band"] = bool(BAND[0] <= te <= BAND[1])
    weak.append(rec)

print("%-9s %5s %5s %9s %6s %12s %12s  %s"
      % ("cell", "f", "seed", "t_end", "ncyc", "knee_LmR", "hip_LmR", "in band"))
for r in sorted(weak, key=lambda x: x["t_end_s"]):
    print("%-9s %5.2f %5d %9.3f %6d %+12.4f %+12.4f  %s"
          % (r["id"], r["f"], r["seed"], r["t_end_s"], r["n_cycles_in_window"],
             r["knee_angle_LmR"], r["hip_flexion_LmR"], "YES" if r["in_band"] else ""))
for r in excluded:
    print("%-9s %5.2f %5d %9s %6s %12s %12s  EXCLUDED: %s"
          % (r["id"], r["f"], r["seed"],
             "%.3f" % r["t_end_s"] if "t_end_s" in r else "n/a", "", "", "", r["reason"]))

inband = [r for r in weak if r["in_band"]]

# ---------------------------------------------------------------- section 5, first match wins
sk = [c["knee_angle_LmR"] for c in spastic]
wk = [c["knee_angle_LmR"] for c in inband]

rung, verdict, detail = None, None, {}
if len(inband) < MIN_IN_BAND:
    rung, verdict = 1, "UNINFORMATIVE -- insufficient band coverage"
    detail = {"n_in_band": len(inband), "required": MIN_IN_BAND,
              "endpoint_evaluated": False,
              "section_4": ("no substitute endpoint, no widened band, no pooling with "
                            "out-of-band cells is permitted to rescue it")}
else:
    disjoint = (max(sk) < min(wk)) or (max(wk) < min(sk))
    as_predicted = disjoint and all(x > 0 for x in wk) and all(x < 0 for x in sk)
    if disjoint and as_predicted:
        rung, verdict = 2, "DISJOINT-AS-PREDICTED -- knee_angle_LmR separates lesion type at matched duration"
    elif disjoint:
        rung, verdict = 3, "DISJOINT-OPPOSITE -- the predicted direction was wrong"
    else:
        rung, verdict = 4, "OVERLAP -- knee_angle_LmR does not separate lesion type at matched duration"
    gap = max(min(wk) - max(sk), min(sk) - max(wk))
    detail = {"n_in_band": len(inband), "endpoint_evaluated": True,
              "spastic_range": [min(sk), max(sk)], "weak_in_band_range": [min(wk), max(wk)],
              "disjoint": bool(disjoint), "seed_gap_deg": gap,
              "weak_all_positive": all(x > 0 for x in wk),
              "spastic_all_negative": all(x < 0 for x in sk)}
    if disjoint:
        allv = sk + wk
        n, k = len(allv), len(sk)
        perms = list(itertools.combinations(range(n), k))
        hits = 0
        for sel in perms:
            ss = set(sel)
            a = [allv[i] for i in sel]
            b = [allv[i] for i in range(n) if i not in ss]
            g = max(min(b) - max(a), min(a) - max(b))
            hits += g >= gap - 1e-12
        detail["permutation"] = {
            "method": "exhaustive over C(%d,%d)" % (n, k), "assignments": len(perms),
            "count_ge_observed": hits, "floor": hits / len(perms),
            "reported_as": "a FLOOR, never as a p-value (section 5)"}

out = {
    "registration": PREREG,
    "sha256": "c27a72650f7d2bb13eb6ae3d7f8b876124036270ef105a604bea92dcd73512ab",
    "endpoint": "knee_angle_LmR",
    "endpoint_is_confirmatory": True,
    "self_check": "spastic hip_flexion_LmR reproduces LADDER36_r228.json to < 1e-9 deg",
    "window": [SETTLE, T1], "band_s": list(BAND), "min_in_band_required": MIN_IN_BAND,
    "spastic_cells": spastic,
    "weak_cells_measured": weak,
    "weak_cells_excluded": excluded,
    "n_weak_measured": len(weak), "n_weak_in_band": len(inband), "n_weak_excluded": len(excluded),
    "RUNG": rung, "VERDICT": verdict, "detail": detail,
    "hip_flexion_LmR_note": ("deposited but NOT the endpoint, per section 3; the post-hoc finding "
                             "about the shipped discriminator stays post-hoc"),
}
p = os.path.join(PAPER, "BANDFILL_ENDPOINT_r286.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

print()
print("=" * 84)
print("REGISTERED ENDPOINT  knee_angle_LmR   %s" % PREREG)
print("=" * 84)
print("  spastic  n=%d  %+.4f .. %+.4f   (%s)"
      % (len(sk), min(sk), max(sk), ", ".join("%+.3f" % x for x in sorted(sk))))
print("  weakness in band [%.2f, %.2f] s  n=%d  %s"
      % (BAND[0], BAND[1], len(wk),
         ("%+.4f .. %+.4f   (%s)" % (min(wk), max(wk), ", ".join("%+.3f" % x for x in sorted(wk))))
         if wk else "none"))
print()
print("  RUNG %d -- %s" % (rung, verdict))
if detail.get("endpoint_evaluated"):
    print("  disjoint %s   seed gap %+.4f deg   weak all positive %s   spastic all negative %s"
          % (detail["disjoint"], detail["seed_gap_deg"],
             detail["weak_all_positive"], detail["spastic_all_negative"]))
    if "permutation" in detail:
        pm = detail["permutation"]
        print("  %s over %d assignments: %d reach the observed gap -> floor %.4f"
              % (pm["method"], pm["assignments"], pm["count_ge_observed"], pm["floor"]))
else:
    print("  endpoint NOT evaluated: %d in band, %d required" % (detail["n_in_band"], MIN_IN_BAND))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
