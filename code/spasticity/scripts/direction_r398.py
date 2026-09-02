# -*- coding: utf-8 -*-
"""Which endpoints move the two lesions in OPPOSITE directions?

mean stance ankle angle is driven the SAME way by both lesions -- more spasticity and more
dorsiflexor weakness both plantarflex the ankle -- so its gap grows only with the DIFFERENCE
in rate, which is why FINE_GAP_r397 reaches only 86% of the 3.8 deg MDC at the highest rung
the model can still walk (KV 0.120). An endpoint the two lesions push in opposite directions
would open from both ends under paired escalation instead of partly cancelling.

This measures, for every candidate endpoint, the signed displacement of each lesion arm from
the matched unlesioned control R151C, and flags the ones with opposite signs.

EXPLORATORY. No endpoint was nominated in advance; nothing here is confirmatory and any
survivor has to be pre-registered and re-tested. Conventions carried unaltered.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DIRECTION_r398.json"
SETTLE, T1 = 1.0, 9.73


def measure(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if len(g) != 1:
        return None
    stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
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
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    sw = [np.arange(a, b)[~on[a:b]] for a, b in win if (~on[a:b]).any()]
    sw = np.concatenate(sw) if sw else None
    ank = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
    hip = np.degrees(S.col(cols, dat, "hip_flexion_l"))
    o = {}
    o["ank_stance_mean"] = float(np.mean(ank[st]))
    o["ank_swing_mean"] = float(np.mean(ank[sw])) if sw is not None else None
    o["ank_min_cycle"] = float(np.mean([np.min(ank[a:b]) for a, b in win]))
    o["ank_max_cycle"] = float(np.mean([np.max(ank[a:b]) for a, b in win]))
    o["ank_rom_cycle"] = float(np.mean([np.ptp(ank[a:b]) for a, b in win]))
    o["ank_at_heelstrike"] = float(np.mean([ank[a] for a, _ in win]))
    o["knee_at_heelstrike"] = float(np.mean([kne[a] for a, _ in win]))
    o["knee_min_cycle"] = float(np.mean([np.min(kne[a:b]) for a, b in win]))
    o["knee_rom_cycle"] = float(np.mean([np.ptp(kne[a:b]) for a, b in win]))
    o["hip_max_swing"] = float(np.mean([np.max(hip[a:b][~on[a:b]])
                                        for a, b in win if (~on[a:b]).any()]))
    o["hip_rom_cycle"] = float(np.mean([np.ptp(hip[a:b]) for a, b in win]))
    o["stance_frac"] = float(np.mean([np.mean(on[a:b]) for a, b in win]))
    o["cycle_time_s"] = float(np.mean([t[b] - t[a] for a, b in win]))
    return o


def arm(prefixes):
    vals = {}
    for p in prefixes:
        r = measure(p)
        if r:
            for k, v in r.items():
                if v is not None:
                    vals.setdefault(k, []).append(v)
    return vals


ARMS = {
    "CONTROL_R151C": ["R151C_s%d" % s for s in range(101, 107)],
    "WEAK_x080": ["R151W_s%d" % s for s in range(101, 107)],
    "WEAK_x060": ["R393WK060_s%d" % s for s in range(101, 107)],
    "SPAS_KV050": ["R151S_s%d" % s for s in range(101, 107)],
    "SPAS_KV100": ["R393SPg100_s%d" % s for s in range(101, 107)],
    "SPAS_KV120": ["R396SPg120_s%d" % s for s in (101, 102, 105, 106)],
}
data = {k: arm(v) for k, v in ARMS.items()}
for k, v in data.items():
    n = len(next(iter(v.values()))) if v else 0
    print("  %-14s n=%d" % (k, n))
print()

keys = sorted(data["CONTROL_R151C"].keys())
res = {"status": "EXPLORATORY -- no endpoint nominated in advance; nothing confirmatory",
       "control": "R151C, matched unlesioned, min_velocity 1.0",
       "arms_n": {k: (len(next(iter(v.values()))) if v else 0) for k, v in data.items()},
       "endpoints": {}}
print("%-20s %10s %10s %10s   %s" % ("endpoint", "d_WEAK", "d_SPAS", "|sum|/|diff|", "verdict"))
opp = []
for k in keys:
    c = data["CONTROL_R151C"].get(k)
    w = data["WEAK_x060"].get(k) or data["WEAK_x080"].get(k)
    s = data["SPAS_KV120"].get(k) or data["SPAS_KV100"].get(k)
    if not (c and w and s):
        continue
    cm = float(np.mean(c))
    dw = float(np.mean(w)) - cm
    ds = float(np.mean(s)) - cm
    opposite = (dw * ds) < 0
    sep = abs(float(np.mean(w)) - float(np.mean(s)))
    res["endpoints"][k] = {"control_mean": cm, "d_weak": dw, "d_spastic": ds,
                           "opposite_direction": bool(opposite),
                           "arm_separation": sep}
    if opposite:
        opp.append((k, dw, ds, sep))
    print("  %-18s %+10.4f %+10.4f %10s   %s"
          % (k, dw, ds, "", "OPPOSITE" if opposite else "same side"))
print()
print("endpoints where the two lesions move OPPOSITE ways: %d" % len(opp))
for k, dw, ds, sep in sorted(opp, key=lambda x: -x[3]):
    print("   %-20s weak %+.4f  spastic %+.4f   arm separation %.4f"
          % (k, dw, ds, sep))
res["opposite_direction_endpoints"] = [k for k, _, _, _ in opp]
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
