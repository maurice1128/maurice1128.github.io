# -*- coding: utf-8 -*-
"""PRIMARY B, per PREREG_3d_replication_r179.md c42f3386289487c0...
BOOKKEEPING: the answer was determinable from data on disk before the rule was written
(PREREG_3d_replication_r179.md section 2a). This closes the registered loop; it is not discovery."""
import io, os, sys, glob, json, math
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S
R = r"C:\Users\maurice\Documents\SCONE\results"; SEEDS = range(101, 107)
SETTLE, T1 = 1.0, 9.73
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = [p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"] + [p + "_LmR" for p in PAIR]
ARMS = {"C": "R151C", "S": "R151S", "W870": "R174W870", "W892": "R174W892", "W915": "R174W915"}
def rd(tag):
    g = [d for d in glob.glob(os.path.join(R, tag + ".*")) if os.path.isdir(d)
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, tag
    return g[0]
def meas(sto):
    cols, dat = S.load_sto(sto); t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l"); idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k+1]) for k in range(len(idx)-1) if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    o = {}
    for ch in [p+s for p in PAIR for s in ("_l","_r")] + UNP:
        v = S.col(cols, dat, ch)
        o[ch] = sum(math.degrees(max(v[a:b+1])-min(v[a:b+1])) for a,b in c)/len(c)
    o["cycle_time"] = (t[c[-1][1]] - t[c[0][0]]) / len(c)
    for p in PAIR: o[p+"_LmR"] = o[p+"_l"] - o[p+"_r"]
    return o
V = {}
for a, pre in ARMS.items():
    V[a] = [meas(sorted(glob.glob(os.path.join(rd("%s_s%d" % (pre, s)), "*.par.sto")))[-1]) for s in SEEDS]
out = {"prereg": "c42f3386289487c0", "label": "BOOKKEEPING", "channels": {}}
print("%-20s %8s %8s %8s | %8s %8s %8s %8s" % ("channel","C mean","lo","hi","S","W870","W892","W915"))
nA = 0; opp = {r: [] for r in ("W870","W892","W915")}; par = {r: 0 for r in opp}; both = {r: 0 for r in opp}
for ch in CH:
    c = [x[ch] for x in V["C"]]; lo, hi, cm = min(c), max(c), float(np.mean(c))
    sm = float(np.mean([x[ch] for x in V["S"]]))
    dS = not (lo <= sm <= hi); nA += dS
    row = {"control_seeds": c, "control_mean": cm, "band": [lo, hi], "S_mean": sm, "S_displaced": bool(dS)}
    ws = []
    for r in ("W870","W892","W915"):
        wm = float(np.mean([x[ch] for x in V[r]])); ws.append(wm)
        dW = not (lo <= wm <= hi)
        o = bool(dS and dW and (sm-cm)*(wm-cm) < 0)
        if dS and dW:
            both[r] += 1
            if o: opp[r].append(ch)
            else: par[r] += 1
        row[r] = {"mean": wm, "displaced": bool(dW), "opposed": o}
    out["channels"][ch] = row
    print("%-20s %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f %8.3f%s" % (ch,cm,lo,hi,sm,ws[0],ws[1],ws[2],
          "  <-- OPPOSED" if row["W892"]["opposed"] else ("  disp" if dS else "")))
print("\nPRIMARY A (spastic displaced, description not test): %d of 16" % nA)
for r in ("W870","W892","W915"):
    print("PRIMARY B %s: OPPOSED %d %s | both-displaced %d, parallel %d, parallel fraction %.2f"
          % (r, len(opp[r]), opp[r], both[r], par[r], par[r]/both[r] if both[r] else float('nan')))
out["primary_A_displaced_count"] = nA
out["primary_B"] = {r: {"opposed": opp[r], "both_displaced": both[r], "parallel": par[r]} for r in opp}
json.dump(out, io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\CHANNELS_G2_r219.json","w",encoding="utf-8"), indent=1)
print("\nwrote CHANNELS_G2_r219.json")
