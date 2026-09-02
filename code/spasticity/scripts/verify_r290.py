# -*- coding: utf-8 -*-
"""Independent recomputation of the r290 confirmatory endpoint.

Does not read BANDFILL_ENDPOINT_r290.json. Resolves the three named in-band cells and the six
spastic cells by directory tag, re-measures knee_angle_LmR and hip_flexion_LmR from their .sto
using hipgap_r220.py's convention, and re-evaluates PREREG_bandfill_r285.md section 5's ladder
from scratch. The point is to reach the verdict by a second path before it is relayed.

Self-check as before: the spastic hip values must reproduce LADDER36_r228.json to < 1e-9 deg.
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
BAND = (13.58, 17.85)
SEEDS = list(range(101, 107))
CLAIMED = ["R276WPF005_s101", "R285BF008_s105", "R287BF007_s109"]


def resolve(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    assert len(ds) == 1, "%s resolves to %d complete directories" % (tag, len(ds))
    return ds[0]


def measure(tag):
    d = resolve(tag)
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    assert c and t_end >= T1, "%s not measurable: t_end %.3f, %d cycles" % (tag, t_end, len(c))

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in c) / len(c)

    return {"tag": tag, "dir": os.path.basename(d), "t_end_s": t_end, "n_cycles": len(c),
            "knee_angle_LmR": rom("knee_angle_l") - rom("knee_angle_r"),
            "hip_flexion_LmR": rom("hip_flexion_l") - rom("hip_flexion_r")}


spastic = [measure("R151S_s%d" % s) for s in SEEDS]
ref = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))["per_seed_hip_flexion_LmR"]["S"]
bad = [(SEEDS[i], a["hip_flexion_LmR"], b) for i, (a, b) in enumerate(zip(spastic, ref))
       if abs(a["hip_flexion_LmR"] - b) > 1e-9]
assert not bad, "SELF-CHECK FAILED: %s" % bad
print("self-check: spastic hip_flexion_LmR reproduces LADDER36_r228.json to < 1e-9 deg\n")

weak = [measure(t) for t in CLAIMED]
print("%-20s %9s %6s %12s %12s  %s" % ("cell", "t_end", "ncyc", "knee_LmR", "hip_LmR", "in band"))
for r in weak:
    r["in_band"] = BAND[0] <= r["t_end_s"] <= BAND[1]
    print("%-20s %9.3f %6d %+12.4f %+12.4f  %s"
          % (r["tag"], r["t_end_s"], r["n_cycles"], r["knee_angle_LmR"], r["hip_flexion_LmR"],
             "YES" if r["in_band"] else "NO -- CLAIMED IN BAND BUT IS NOT"))
print()
for r in spastic:
    print("%-20s %9.3f %6d %+12.4f %+12.4f" % (r["tag"], r["t_end_s"], r["n_cycles"],
                                               r["knee_angle_LmR"], r["hip_flexion_LmR"]))

inband = [r for r in weak if r["in_band"]]


def verdict(key):
    sv = [c[key] for c in spastic]
    wv = [c[key] for c in inband]
    if len(inband) < 3:
        return {"rung": 1, "verdict": "UNINFORMATIVE", "n_in_band": len(inband)}
    disj = (max(sv) < min(wv)) or (max(wv) < min(sv))
    pred = disj and all(x > 0 for x in wv) and all(x < 0 for x in sv)
    gap = max(min(wv) - max(sv), min(sv) - max(wv))
    r = {"rung": (2 if pred else 3 if disj else 4),
         "verdict": ("DISJOINT-AS-PREDICTED" if pred else
                     "DISJOINT-OPPOSITE" if disj else "OVERLAP"),
         "spastic_range": [min(sv), max(sv)], "weak_range": [min(wv), max(wv)],
         "disjoint": bool(disj), "seed_gap_deg": gap}
    if disj:
        allv = sv + wv
        n, k = len(allv), len(sv)
        perms = list(itertools.combinations(range(n), k))
        hits = 0
        for sel in perms:
            ss = set(sel)
            a = [allv[i] for i in sel]
            b = [allv[i] for i in range(n) if i not in ss]
            g = max(min(b) - max(a), min(a) - max(b))
            hits += g >= gap - 1e-12
        r["permutation"] = {"assignments": len(perms), "count_ge_observed": hits,
                            "floor": hits / len(perms)}
    return r


ke = verdict("knee_angle_LmR")
hi = verdict("hip_flexion_LmR")

out = {"what": "independent recomputation of the r290 endpoint; BANDFILL_ENDPOINT_r290.json not read",
       "registration": "PREREG_bandfill_r285.md section 3 and 5, carried unchanged by r287",
       "cells_claimed_in_band": CLAIMED, "n_in_band_verified": len(inband),
       "spastic": spastic, "weak_in_band": weak,
       "ENDPOINT_knee_angle_LmR": ke, "SECONDARY_hip_flexion_LmR": hi}
p = os.path.join(PAPER, "VERIFY_R290.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

print()
for name, v in (("ENDPOINT  knee_angle_LmR", ke), ("SECONDARY hip_flexion_LmR", hi)):
    print("=" * 78)
    print("%s -> RUNG %d, %s" % (name, v["rung"], v["verdict"]))
    if v["rung"] != 1:
        print("  spastic  %+.4f .. %+.4f" % tuple(v["spastic_range"]))
        print("  weakness %+.4f .. %+.4f" % tuple(v["weak_range"]))
        print("  disjoint %s   gap %+.4f deg" % (v["disjoint"], v["seed_gap_deg"]))
        if "permutation" in v:
            pm = v["permutation"]
            print("  exhaustive C(9,6)=%d: %d reach the gap -> floor %.6f"
                  % (pm["assignments"], pm["count_ge_observed"], pm["floor"]))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
