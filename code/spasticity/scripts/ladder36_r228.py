# -*- coding: utf-8 -*-
"""PREREG_ladder36_r228.md  sha256 ab738d522a4ad937ce2d (prefix)
Sixteen channels for the three unlooked-at severities, on the G2 window [1.00, 9.73].
Then disjointness at all six severities, and the exhaustive permutation null at the three new ones.
Read-only. Same measurement path as channels_g2_r219.py."""
import io, os, sys, glob, json, math, itertools, collections
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = list(range(101, 107))
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = [p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"] + [p + "_LmR" for p in PAIR]
ARMS = collections.OrderedDict([
    ("C", "R151C"), ("S", "R151S"),
    ("W800", "R151W"), ("W870", "R174W870"), ("W892", "R174W892"),
    ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095")])
NEW = ["W800", "W900", "W950"]
ALLW = ["W800", "W870", "W892", "W900", "W915", "W950"]


def meas(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
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
    o = {c: rom(c) for c in [p + s for p in PAIR for s in ("_l", "_r")] + UNP}
    o["cycle_time"] = (t[cyc[-1][1]] - t[cyc[0][0]]) / len(cyc)
    for p in PAIR:
        o[p + "_LmR"] = o[p + "_l"] - o[p + "_r"]
    return o


V = {a: [meas("%s_s%d" % (p, s)) for s in SEEDS] for a, p in ARMS.items()}
HF = "hip_flexion_LmR"
out = collections.OrderedDict()
out["prereg"] = "PREREG_ladder36_r228.md sha256 ab738d522a4ad937ce2d"
out["window"] = [SETTLE, T1]
out["newly_computed"] = NEW
out["per_seed_hip_flexion_LmR"] = {a: [x[HF] for x in V[a]] for a in ARMS}

# ---- disjointness at all six severities and pooled
smax = max(x[HF] for x in V["S"])
print("spastic hip_flexion_LmR: %s   max %+.4f"
      % (" ".join("%+.4f" % x for x in sorted(v[HF] for v in V["S"])), smax))
print()
dis = collections.OrderedDict()
for w in ALLW:
    vals = sorted(x[HF] for x in V[w])
    gap = min(vals) - smax
    dis[w] = {"seeds": vals, "min": min(vals), "mean": float(np.mean(vals)),
              "seed_gap_deg": gap, "disjoint": bool(gap > 0), "newly_computed": w in NEW}
    print("%-5s %s  min %+.4f  gap %+.4f  %s%s"
          % (w, " ".join("%+.4f" % x for x in vals), min(vals), gap,
             "DISJOINT" if gap > 0 else "*** OVERLAP ***", "   <-- NEW" if w in NEW else ""))
pool = [x[HF] for w in ALLW for x in V[w]]
out["disjointness"] = dis
out["pooled_36"] = {"n": len(pool), "min": min(pool), "spastic_max": smax,
                    "seed_gap_deg": min(pool) - smax, "disjoint": bool(min(pool) > smax),
                    "mean_gap_deg": float(np.mean(pool) - np.mean([x[HF] for x in V["S"]]))}
print("\nPOOLED 36 weak vs 6 spastic: min %+.4f  gap %+.4f  %s"
      % (min(pool), min(pool) - smax, "DISJOINT" if min(pool) > smax else "*** OVERLAP ***"))

# ---- exhaustive permutation null at the three new severities
def gapfun(g1, g2):
    a1, b1, a2, b2 = min(g1), max(g1), min(g2), max(g2)
    return a2 - b1 if a2 > b1 else (a1 - b2 if a1 > b2 else 0.0)


print("\nexhaustive permutation null, 924 assignments, at the three NEW severities")
perm = collections.OrderedDict()
for w in NEW:
    obs = dis[w]["seed_gap_deg"]
    if obs <= 0:
        perm[w] = {"skipped": "no observed disjointness to test"}
        print("  %-5s observed gap %+.4f -- not disjoint, null not run" % (w, obs))
        continue
    pooled = {c: [x[c] for x in V["S"]] + [x[c] for x in V[w]] for c in CH}
    fam = hip = 0
    reach = collections.OrderedDict((c, 0) for c in CH)
    for comb in itertools.combinations(range(12), 6):
        i1 = list(comb); i2 = [i for i in range(12) if i not in comb]
        any_ = False
        for c in CH:
            v = pooled[c]
            if gapfun([v[i] for i in i1], [v[i] for i in i2]) >= obs:
                reach[c] += 1; any_ = True
                if c == HF: hip += 1
        fam += any_
    nz = collections.OrderedDict((c, n) for c, n in reach.items() if n)
    perm[w] = {"observed_gap_deg": obs, "n_assignments": 924,
               "familywise_count": fam, "familywise_proportion": fam / 924.0,
               "hip_only_count": hip, "hip_only_proportion": hip / 924.0,
               "channels_reaching_at_least_once": nz}
    print("  %-5s obs %+.4f  familywise %d/924 = %.4f  hip %d/924  channels reaching: %s"
          % (w, obs, fam, fam / 924.0, hip, dict(nz)))
out["permutation_null_new_severities"] = perm
json.dump(out, io.open(os.path.join(PAPER, "LADDER36_r228.json"), "w", encoding="utf-8"), indent=1)
print("\ndeposited paper/LADDER36_r228.json")
