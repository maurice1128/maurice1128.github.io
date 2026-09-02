# -*- coding: utf-8 -*-
"""r433: an unbiased screen of EVERY channel in the .sto for spastic-vs-weak signal.

The seven mechanism hypotheses in this corpus were each proposed by hand and tested one at a
time. Six died and the seventh has a mediator at 1.8x its noise floor. This screen asks the
question the other way round: over all ~960 recorded channels, WHERE does the signal actually
live, and how much of it is bigger than that channel's own same-mechanism noise?

EXPLORATORY BY CONSTRUCTION. It selects nothing and proves nothing. Every hit must be confirmed
on material the screen did not touch, and the r424 mixed-lesion grid -- whose endpoints have never
been read -- is reserved for exactly that.

NO SIMULATION. Reads .sto files already on disk.

Per channel, four summaries over the corpus window: mean over stance, mean over terminal swing
(last 15% of cycle), value at heel strike, and peak-to-trough range within the cycle.
The noise floor for each summary is the largest difference between two same-mechanism family
MEANS over the six dorsiflexor-weakness families -- the method of NULL_FLOORS_r428.
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SCREEN_ALL_r433.json"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

WEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
SPAS = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
CTRL = ["R151C"]

SKIP = ("world.", "ground.", "time")


def summarise(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    cols, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return None
    on = grf > thr
    stance = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    tsw = np.concatenate([np.arange(a + int(0.85 * (b - a)), b) for a, b in win])
    ic = np.array([a for a, _ in win])

    out = {}
    for j, c in enumerate(cols):
        if j == 0 or c.startswith(SKIP):
            continue
        v = dat[:, j]
        if not np.all(np.isfinite(v)):
            continue
        out[c + "|stance"] = float(np.mean(v[stance]))
        out[c + "|tsw"] = float(np.mean(v[tsw]))
        out[c + "|ic"] = float(np.mean(v[ic]))
        out[c + "|range"] = float(np.mean([np.ptp(v[a:b]) for a, b in win]))
    return out


def fam(prefixes):
    d = {}
    for f in prefixes:
        cs = [summarise("%s_s%d" % (f, s)) for s in SEEDS]
        cs = [c for c in cs if c]
        if len(cs) >= 4:
            d[f] = cs
    return d


W, SP, C = fam(WEAK), fam(SPAS), fam(CTRL)
print("families: weak %d, spastic %d, control %d" % (len(W), len(SP), len(C)))
keys = sorted(set.intersection(*[set(c) for g in (W, SP) for cs in g.values() for c in cs]))
print("channels x summaries available in every cell: %d" % len(keys))

rows = []
for k in keys:
    wm = [np.mean([c[k] for c in cs]) for cs in W.values()]
    if len(wm) < 2:
        continue
    floor = max(abs(a - b) for a, b in itertools.combinations(wm, 2))
    wmean = float(np.mean([c[k] for cs in W.values() for c in cs]))
    smean = float(np.mean([c[k] for cs in SP.values() for c in cs]))
    diff = smean - wmean
    if floor <= 0:
        # every same-mechanism pair identical: use the largest within-family SD as the floor
        floor = max([np.std([c[k] for c in cs], ddof=1) for cs in W.values()] + [1e-12])
        floor_kind = "within_family_SD"
    else:
        floor_kind = "same_mechanism_mean_difference"
    mult = abs(diff) / floor if floor else float("inf")
    # spastic dose ordering: does it rise or fall monotonically with KV?
    sm = [np.mean([c[k] for c in SP[f]]) for f in SPAS if f in SP]
    mono = (all(sm[i] < sm[i + 1] for i in range(len(sm) - 1))
            or all(sm[i] > sm[i + 1] for i in range(len(sm) - 1))) if len(sm) >= 3 else False
    cmean = (float(np.mean([c[k] for cs in C.values() for c in cs]))
             if C else None)
    ctrl_between = (cmean is not None
                    and min(wmean, smean) < cmean < max(wmean, smean))
    rows.append({"key": k, "weak_mean": wmean, "spastic_mean": smean, "diff": diff,
                 "floor": floor, "floor_kind": floor_kind, "multiple_of_floor": mult,
                 "spastic_dose_monotone": bool(mono),
                 "control_mean": cmean, "control_between_arms": bool(ctrl_between),
                 "spastic_rung_means": sm})

rows.sort(key=lambda r: -r["multiple_of_floor"])
res = {"round": "SCREEN_ALL_r433", "no_simulation_run": True,
       "status": "EXPLORATORY SCREEN. Selects nothing, proves nothing, and may not be cited as "
                 "evidence. Any hit requires confirmation on material this screen did not read; "
                 "the r424 mixed-lesion grid is reserved for that.",
       "n_channels_summarised": len(keys),
       "floor_method": "largest difference between two same-mechanism family MEANS over the six "
                       "dorsiflexor-weakness families; where that is exactly zero the largest "
                       "within-family SD is used instead and flagged",
       "n_above_floor": sum(1 for r in rows if r["multiple_of_floor"] > 1),
       "n_above_5x": sum(1 for r in rows if r["multiple_of_floor"] > 5),
       "n_above_5x_and_dose_monotone": sum(1 for r in rows if r["multiple_of_floor"] > 5
                                           and r["spastic_dose_monotone"]),
       "top_200": rows[:200]}

print()
print("channels above their own floor : %d / %d" % (res["n_above_floor"], len(rows)))
print("above 5x                       : %d" % res["n_above_5x"])
print("above 5x AND dose-monotone     : %d" % res["n_above_5x_and_dose_monotone"])
print()
print("%-46s %-9s %-9s %-7s %s" % ("channel|summary", "diff", "floor", "mult", "mono ctrl-between"))
shown = 0
for r in rows:
    if not (r["multiple_of_floor"] > 5 and r["spastic_dose_monotone"]):
        continue
    print("  %-44s %+9.4g %-9.4g %-7.1f %-5s %s"
          % (r["key"][:44], r["diff"], r["floor"], r["multiple_of_floor"],
             "yes", "IN" if r["control_between_arms"] else "out"))
    shown += 1
    if shown >= 40:
        print("  ... (%d more)" % (res["n_above_5x_and_dose_monotone"] - shown))
        break

io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
