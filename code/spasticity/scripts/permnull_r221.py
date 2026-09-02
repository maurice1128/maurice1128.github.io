# -*- coding: utf-8 -*-
"""PREREG_permnull_r221.md  sha256 384579cc23e5ad529cab (prefix)
Exhaustive permutation null, per severity, 6 v 6, all C(12,6)=924 label assignments.
Read-only. Recomputes all 16 channels from .sto on window [1.00, 9.73]."""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S
RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = [p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"] + [p + "_LmR" for p in PAIR]
ARMS = {"S": "R151S", "W870": "R174W870", "W892": "R174W892", "W915": "R174W915"}
OBS = {w: json.load(io.open(os.path.join(PAPER, "HIPGAP_r220.json"), encoding="utf-8"))[w]["seed_gap_deg"]
       for w in ("W870", "W892", "W915")}   # EXACT values, read from the deposit

def meas(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(ds[0], "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k+1]) for k in range(len(idx)-1)
           if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b+1]) - min(v[a:b+1])) for a, b in cyc) / len(cyc)
    o = {c: rom(c) for c in [p+s for p in PAIR for s in ("_l","_r")] + UNP}
    o["cycle_time"] = (t[cyc[-1][1]] - t[cyc[0][0]]) / len(cyc)
    for p in PAIR:
        o[p+"_LmR"] = o[p+"_l"] - o[p+"_r"]
    return o

V = {a: [meas("%s_s%d" % (p, s)) for s in SEEDS] for a, p in ARMS.items()}

def gap(g1, g2):
    """direction-agnostic seed-level disjointness gap; <=0 if the groups overlap"""
    a1, b1, a2, b2 = min(g1), max(g1), min(g2), max(g2)
    return a2 - b1 if a2 > b1 else (a1 - b2 if a1 > b2 else 0.0)

out = {"prereg": "PREREG_permnull_r221.md sha256 384579cc23e5ad529cab",
       "design": "per severity, 6 v 6, EXHAUSTIVE over all C(12,6)=924 label assignments",
       "window": [SETTLE, T1], "n_channels": len(CH), "severities": {}}
print("severity  observed_gap  familywise(any of 16)   hip_flexion_LmR alone   selection cost")
for w in ("W870", "W892", "W915"):
    pool = {c: [x[c] for x in V["S"]] + [x[c] for x in V[w]] for c in CH}
    obs = OBS[w]
    fam = hip = 0
    for comb in itertools.combinations(range(12), 6):
        idx1 = list(comb); idx2 = [i for i in range(12) if i not in comb]
        anyc = False
        for c in CH:
            v = pool[c]
            g = gap([v[i] for i in idx1], [v[i] for i in idx2])
            if g >= obs:
                anyc = True
                if c == "hip_flexion_LmR":
                    hip += 1
                    break
                break
        # hip counted separately, exhaustively
        if anyc: fam += 1
    hip = 0
    for comb in itertools.combinations(range(12), 6):
        idx1 = list(comb); idx2 = [i for i in range(12) if i not in comb]
        v = pool["hip_flexion_LmR"]
        if gap([v[i] for i in idx1], [v[i] for i in idx2]) >= obs: hip += 1
    N = 924
    out["severities"][w] = {"observed_gap_deg": obs, "n_assignments": N,
                            "familywise_count": fam, "familywise_proportion": fam / N,
                            "hip_only_count": hip, "hip_only_proportion": hip / N,
                            "selection_cost": (fam - hip) / N}
    print("%-9s %10.4f   %6d/924 = %.4f      %6d/924 = %.4f      %+.4f"
          % (w, obs, fam, fam/N, hip, hip/N, (fam-hip)/N))
json.dump(out, io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\PERMNULL_r221.json",
                       "w", encoding="utf-8"), indent=1)
print("\ndeposited paper/PERMNULL_r221.json")
