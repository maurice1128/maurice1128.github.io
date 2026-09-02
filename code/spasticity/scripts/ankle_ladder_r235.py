# -*- coding: utf-8 -*-
"""Round 235 -- the SECOND opposed laterality channel on the extended ladder.

Implements PREREG_ankle_ladder_r235.md. READ-ONLY. No simulation.

At r151 the registered (L-R) family produced TWO separating endpoints with identical
statistics -- ankle_angle_LmR and hip_flexion_LmR, both AUC 0.000, p_raw 0.002165,
p_adj x16 0.0346. The narrowing to one was made afterwards on window sensitivity found in
these same cells. ladder36_r228.py computed all sixteen channels and deposited only the hip.

This runs r228's analysis on ankle_angle_LmR, definition transcribed from ladder36_r228.py
lines 24-43 and ASSERTED against that file. ladder36_r228.py is REGISTERED and is NOT edited.
"""
import io
import os
import sys
import glob
import json
import math
import hashlib
import itertools
import collections

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = os.path.join(PAPER, "PREREG_ankle_ladder_r235.md")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ladder36_r228.py")

SETTLE, T1 = 1.0, 9.73
SEEDS = [101, 102, 103, 104, 105, 106]
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
FAMILY = [p + "_LmR" for p in PAIR]
TARGET = "ankle_angle_LmR"
ARMS = collections.OrderedDict([
    ("C", "R151C"), ("S", "R151S"),
    ("W800", "R151W"), ("W870", "R174W870"), ("W892", "R174W892"),
    ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095")])
WEAK = ["W800", "W870", "W892", "W900", "W915", "W950"]


def _sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def assert_definition():
    """The endpoint definition must be ladder36_r228.py's, verbatim."""
    t = io.open(SRC, encoding="utf-8").read()
    need = ["cyc = cyc[:-1] if len(cyc) >= 2 else cyc",
            "return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)",
            "SETTLE, T1 = 1.0, 9.73",
            'PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]']
    miss = [n for n in need if n not in t]
    if miss:
        raise SystemExit("DEFINITION MISMATCH against ladder36_r228.py: %r" % miss)


def meas(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"),
                                     errors="replace")) >= 91]
    assert len(ds) == 1, tag
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(ds[0], "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)
    o = {}
    for p in PAIR:
        o[p + "_LmR"] = rom(p + "_l") - rom(p + "_r")
    return o


def perm_null(sp, wk, chans):
    """Exhaustive over C(12,6)=924, familywise over the channel family, as r228."""
    n_s = len(sp[chans[0]])
    pooled = {c: list(sp[c]) + list(wk[c]) for c in chans}
    n = len(pooled[chans[0]])
    obs = {c: min(wk[c]) - max(sp[c]) for c in chans}
    obs_t = obs[TARGET]
    cnt_t, fw, tot = 0, 0, 0
    reach = collections.Counter()
    for idx in itertools.combinations(range(n), n_s):
        ss = set(idx)
        tot += 1
        best = None
        for c in chans:
            a = [pooled[c][i] for i in range(n) if i in ss]
            b = [pooled[c][i] for i in range(n) if i not in ss]
            g = min(b) - max(a)
            if c == TARGET and g >= obs_t - 1e-12:
                cnt_t += 1
            if g >= obs[c] - 1e-12:
                reach[c] += 1
            best = g if best is None or g > best else best
        if best >= obs_t - 1e-12:
            fw += 1
    return {"observed_gap_deg": obs_t, "n_assignments": tot,
            "target_count": cnt_t, "target_proportion": cnt_t / float(tot),
            "familywise_count": fw, "familywise_proportion": fw / float(tot),
            "channels_reaching_own_observed": dict(reach)}


def main():
    assert_definition()
    V = {a: [meas("%s_s%d" % (p, s)) for s in SEEDS] for a, p in ARMS.items()}
    per = {a: [x[TARGET] for x in V[a]] for a in ARMS}

    sp = per["S"]
    smax = max(sp)
    dis = {}
    for w in WEAK:
        wmin = min(per[w])
        dis[w] = {"weak_min": wmin, "spastic_max": smax,
                  "seed_gap_deg": wmin - smax, "disjoint": bool(wmin > smax),
                  "mean_gap_deg": (sum(per[w]) / 6.0) - (sum(sp) / 6.0)}
    pooled = [v for w in WEAK for v in per[w]]
    pooled_res = {"n": len(pooled), "min": min(pooled), "spastic_max": smax,
                  "seed_gap_deg": min(pooled) - smax,
                  "disjoint": bool(min(pooled) > smax),
                  "mean_gap_deg": (sum(pooled) / float(len(pooled))) - (sum(sp) / 6.0)}

    nulls = {}
    for w in WEAK:
        s_d = {c: [x[c] for x in V["S"]] for c in FAMILY}
        w_d = {c: [x[c] for x in V[w]] for c in FAMILY}
        nulls[w] = perm_null(s_d, w_d, FAMILY)

    n_dis = sum(1 for w in WEAK if dis[w]["disjoint"])
    if pooled_res["disjoint"] and n_dis == 6:
        reading, why = "TWO-CHANNEL", ("ankle_angle_LmR is disjoint at all six severities and "
                                       "pooled 6-vs-36")
    elif n_dis >= 1:
        reading, why = "NARROWING-JUSTIFIED-IN-SAMPLE", (
            "disjoint at %d of 6 severities and %s pooled" % (n_dis,
            "disjoint" if pooled_res["disjoint"] else "NOT disjoint"))
    else:
        reading, why = "NARROWING-CLEAN", "not disjoint at any severity"

    res = {"round": 235, "channel": TARGET, "window": [SETTLE, T1], "family": FAMILY,
           "provenance": {"script": os.path.basename(__file__),
                          "script_sha256": _sha(os.path.abspath(__file__)),
                          "prereg_sha256": _sha(PREREG),
                          "definition_source": os.path.basename(SRC),
                          "definition_source_sha256": _sha(SRC)},
           "per_seed": per, "disjointness": dis, "pooled_36": pooled_res,
           "permutation_null": nulls, "READING": reading, "REASON": why}
    json.dump(res, io.open(os.path.join(PAPER, "ANKLE_LADDER_r235.json"), "w",
                           encoding="utf-8"), indent=1)

    print("channel: %s   window [%.2f, %.2f]\n" % (TARGET, SETTLE, T1))
    print("per-seed values (six seeds each):")
    for a in ARMS:
        print("  %-5s %s" % (a, "  ".join("%+7.4f" % v for v in per[a])))
    print("\n  spastic max %+.4f   control mean %+.4f" % (smax, sum(per["C"]) / 6.0))
    print("\nseverity   weak min    gap        disjoint   mean gap")
    for w in WEAK:
        d = dis[w]
        print("  %-6s %+9.4f  %+9.4f   %-8s %+8.4f"
              % (w, d["weak_min"], d["seed_gap_deg"],
                 "YES" if d["disjoint"] else "no", d["mean_gap_deg"]))
    print("  POOLED  %+9.4f  %+9.4f   %-8s %+8.4f  (n=%d)"
          % (pooled_res["min"], pooled_res["seed_gap_deg"],
             "YES" if pooled_res["disjoint"] else "no",
             pooled_res["mean_gap_deg"], pooled_res["n"]))
    print("\nexhaustive permutation null (924 assignments per severity):")
    for w in WEAK:
        n = nulls[w]
        print("  %-6s obs %+8.4f  target %d/924 = %.4f  familywise %d/924 = %.4f  reaching %s"
              % (w, n["observed_gap_deg"], n["target_count"], n["target_proportion"],
                 n["familywise_count"], n["familywise_proportion"],
                 n["channels_reaching_own_observed"]))
    print("\nREADING = %s\n  %s" % (reading, why))


if __name__ == "__main__":
    main()
