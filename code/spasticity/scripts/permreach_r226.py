# -*- coding: utf-8 -*-
"""Per-channel reach counts for the r221 permutation null.

PERMNULL_r221.json recorded only familywise and hip-only counts. RESULTS_3d_r214.md section 4 claims
"no channel other than hip_flexion_LmR ever reaches the observed gap", which those two counts do NOT
establish -- equal counts show only that no assignment has another channel reaching WITHOUT hip also
reaching. This records, for every one of the 924 assignments per severity, WHICH channels reach.

Read-only. Same measurement path, window and observed gaps as permnull_r221.py.
"""
import io, os, sys, glob, json, math, itertools, collections
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
       for w in ("W870", "W892", "W915")}


def meas(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
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


def gap(g1, g2):
    a1, b1, a2, b2 = min(g1), max(g1), min(g2), max(g2)
    return a2 - b1 if a2 > b1 else (a1 - b2 if a1 > b2 else 0.0)


out = collections.OrderedDict()
out["what"] = ("For each severity, the number of the 924 label assignments in which EACH channel "
               "reaches the observed hip_flexion_LmR gap. Answers whether any channel other than "
               "hip_flexion_LmR ever reaches it, which familywise+hip-only counts cannot.")
out["window"] = [SETTLE, T1]
out["observed_gaps_deg"] = OBS
sev = collections.OrderedDict()
for w in ("W870", "W892", "W915"):
    pool = {c: [x[c] for x in V["S"]] + [x[c] for x in V[w]] for c in CH}
    obs = OBS[w]
    reach = collections.OrderedDict((c, 0) for c in CH)
    other_only = 0
    for comb in itertools.combinations(range(12), 6):
        i1 = list(comb); i2 = [i for i in range(12) if i not in comb]
        hit = []
        for c in CH:
            v = pool[c]
            if gap([v[i] for i in i1], [v[i] for i in i2]) >= obs:
                reach[c] += 1
                hit.append(c)
        if hit and "hip_flexion_LmR" not in hit:
            other_only += 1
    nz = collections.OrderedDict((c, n) for c, n in reach.items() if n)
    sev[w] = {"observed_gap_deg": obs, "n_assignments": 924,
              "channels_reaching_at_least_once": nz,
              "assignments_where_a_channel_OTHER_than_hip_reaches_without_hip": other_only}
    print("%-6s obs %.4f | channels ever reaching: %s | other-without-hip: %d"
          % (w, obs, dict(nz), other_only))
out["severities"] = sev
allnz = set()
for w in sev:
    allnz |= set(sev[w]["channels_reaching_at_least_once"])
out["any_channel_other_than_hip_ever_reaches"] = bool(allnz - {"hip_flexion_LmR"})
out["channels_other_than_hip_that_ever_reach"] = sorted(allnz - {"hip_flexion_LmR"})
json.dump(out, io.open(os.path.join(PAPER, "PERMREACH_r226.json"), "w", encoding="utf-8"), indent=1)
print("\nany channel other than hip ever reaches:", out["any_channel_other_than_hip_ever_reaches"])
print("which:", out["channels_other_than_hip_that_ever_reach"])
print("deposited paper/PERMREACH_r226.json")
