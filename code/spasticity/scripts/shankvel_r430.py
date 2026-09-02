# -*- coding: utf-8 -*-
"""r430: mechanism hypothesis 3, measured properly for the first time.

Hypothesis 3 -- "the spastic limb's shank is decelerated before contact" -- was abandoned on a
line of prose: "shank angular velocity: control 66.0, weak 93.6, spastic 83.3-99.7 -- no
ordering". That sentence appears in the provenance tables of PREREG_terminalswing_r408.md and
PREREG_onedim_r409.md. It has NO DEPOSIT, no window definition, no seed list, no Gate-G
accounting, and no noise floor. It is the only hypothesis in this corpus that was retired without
a container, and RESCORED_r429 has just shown what happens when a number is judged without the
floor for its own endpoint.

NO SIMULATION. Reads .sto files already on disk.

Definitions fixed here, all following corpus convention:
  window          SETTLE 1.00 s, T1 9.73 s, cycles wholly inside, last kept cycle dropped, >= 5
  terminal swing  the last 15% of each cycle, the r408 convention
  shank angle     atan2 of the tibia_l -> calcn_l vector in the sagittal plane, degrees
  SHANKVEL_tsw    mean |d(shank angle)/dt| over terminal-swing samples, deg/s
  SHANKDECEL      (velocity at 85% of cycle) - (velocity at heel strike), deg/s; POSITIVE means
                  the shank slowed down before contact, which is what the hypothesis asserts
The noise floor for every quantity is computed here the same way as NULL_FLOORS_r428: the largest
difference between two same-mechanism family MEANS, over the six dorsiflexor-weakness families.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SHANKVEL_r430.json"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

CONTROL = ["R151C"]
WEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
SPAS = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]


def measure(prefix):
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

    # shank orientation from the tibia -> calcaneus vector, sagittal plane
    tx, ty = S.col(cols, dat, "tibia_l.pos.x"), S.col(cols, dat, "tibia_l.pos.y")
    cx, cy = S.col(cols, dat, "calcn_l.pos.x"), S.col(cols, dat, "calcn_l.pos.y")
    ang = np.degrees(np.arctan2(cx - tx, -(cy - ty)))
    vel = np.gradient(ang, t)

    tsw, at85, athl = [], [], []
    for a, b in win:
        k85 = a + int(0.85 * (b - a))
        tsw.append(np.arange(k85, b))
        at85.append(abs(vel[k85]))
        athl.append(abs(vel[b]))
    tsw = np.concatenate(tsw)
    return {"SHANKVEL_tsw": float(np.mean(np.abs(vel[tsw]))),
            "SHANKVEL_peak_tsw": float(np.mean([np.max(np.abs(vel[a + int(0.85 * (b - a)):b]))
                                                for a, b in win])),
            "SHANKDECEL": float(np.mean(at85) - np.mean(athl)),
            "SHANKVEL_at_HS": float(np.mean(athl)),
            "n_cycles": len(win), "t_end": float(t[-1])}


def fam(prefixes):
    out = {}
    for f in prefixes:
        cs = [measure("%s_s%d" % (f, s)) for s in SEEDS]
        cs = [c for c in cs if c]
        if len(cs) >= 4:
            out[f] = cs
    return out


C, W, SP = fam(CONTROL), fam(WEAK), fam(SPAS)
KEYS = ["SHANKVEL_tsw", "SHANKVEL_peak_tsw", "SHANKDECEL", "SHANKVEL_at_HS"]

print("families with >= 4 Gate-G cells:  control %d   weak %d   spastic %d"
      % (len(C), len(W), len(SP)))
print()

floors = {}
for k in KEYS:
    means = [np.mean([c[k] for c in v]) for v in W.values()]
    floors[k] = float(max(abs(a - b) for a, b in itertools.combinations(means, 2)))
print("同機制(六個背屈無力家族)雜訊底線:")
for k in KEYS:
    print("  %-20s %.4f" % (k, floors[k]))
print()


def arm(group, k):
    v = [c[k] for cs in group.values() for c in cs]
    return {"n": len(v), "mean": float(np.mean(v)),
            "range": [float(min(v)), float(max(v))],
            "family_means": {f: float(np.mean([c[k] for c in cs])) for f, cs in group.items()}}


res = {"round": "SHANKVEL_r430", "no_simulation_run": True,
       "what": "mechanism hypothesis 3 measured with a definition, a window, seed accounting and "
               "a per-endpoint noise floor. The number it was retired on had none of these.",
       "the_retired_prose": "shank angular velocity: control 66.0, weak 93.6, spastic 83.3-99.7 "
                            "-- no ordering",
       "definitions": {"shank_angle": "atan2 of tibia_l -> calcn_l in the sagittal plane, deg",
                       "terminal_swing": "last 15% of each admissible cycle",
                       "SHANKDECEL": "|vel| at 85% of cycle minus |vel| at heel strike, deg/s; "
                                     "POSITIVE means the shank slowed before contact"},
       "noise_floors_same_mechanism": floors, "arms": {}, "tests": {}}

print("%-20s %-9s %-22s %-9s %-22s %s" % ("endpoint", "control", "weak", "", "spastic", ""))
for k in KEYS:
    a_c, a_w, a_s = arm(C, k), arm(W, k), arm(SP, k)
    res["arms"][k] = {"control": a_c, "weak": a_w, "spastic": a_s}
    d_sw = a_s["mean"] - a_w["mean"]
    d_sc = a_s["mean"] - a_c["mean"]
    res["tests"][k] = {
        "spastic_minus_weak": d_sw, "multiple_of_floor_vs_weak": abs(d_sw) / floors[k],
        "real_vs_weak": abs(d_sw) > floors[k],
        "spastic_minus_control": d_sc, "multiple_of_floor_vs_control": abs(d_sc) / floors[k],
        "real_vs_control": abs(d_sc) > floors[k]}
    print("  %-18s %-9.3f [%7.3f,%7.3f] %-9.3f [%7.3f,%7.3f] %-9.3f"
          % (k, a_c["mean"], a_w["range"][0], a_w["range"][1], a_w["mean"],
             a_s["range"][0], a_s["range"][1], a_s["mean"]))
    print("      %-14s spastic-weak %+8.4f (%.1fx floor, %s)   spastic-control %+8.4f (%.1fx, %s)"
          % ("", d_sw, abs(d_sw) / floors[k], "REAL" if abs(d_sw) > floors[k] else "noise",
             d_sc, abs(d_sc) / floors[k], "REAL" if abs(d_sc) > floors[k] else "noise"))

dec = res["tests"]["SHANKDECEL"]
res["HYPOTHESIS_3_VERDICT"] = (
    "SUPPORTED: the spastic shank decelerates before contact more than the weak arm, by %.4f "
    "deg/s, %.1fx the same-mechanism floor." % (dec["spastic_minus_weak"],
                                                dec["multiple_of_floor_vs_weak"])
    if dec["spastic_minus_weak"] > 0 and dec["real_vs_weak"] else
    "NOT SUPPORTED: the spastic-minus-weak deceleration is %+.4f deg/s, %.1fx the floor. %s"
    % (dec["spastic_minus_weak"], dec["multiple_of_floor_vs_weak"],
       "Below the noise floor." if not dec["real_vs_weak"]
       else "Real in magnitude but in the WRONG DIRECTION -- the spastic shank decelerates LESS."))
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("HYPOTHESIS 3:", res["HYPOTHESIS_3_VERDICT"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
