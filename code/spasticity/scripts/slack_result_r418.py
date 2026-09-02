# -*- coding: utf-8 -*-
"""r418 registered endpoint: does soleus spasticity slacken gastrocnemius and protect the knee?

Registration: paper/PREREG_slack_r418.md, sha256 a908b4b716cf2ac2... hashed before any cell existed.

UNITS NOTE, recorded rather than corrected: PREREG_slack_r418.md section 3 calls GASLEN
"muscle-tendon length ... metres". The available column `gastroc_l.L` is SCONE's NORMALISED MTU
length and is dimensionless. The quantity is the one the registration intended; only its unit label
was wrong. Every registered prediction is directional or a disjointness test, so none depends on the
unit.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

DST = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\slack_r418"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SLACK_RESULT_r418.json"
RUNGS = ["0.000", "0.0125", "0.025", "0.050", "0.075", "0.100"]
SEEDS = [101, 102, 103, 104, 105, 106]
T0 = 0.5


def tag(kv):
    return "sk" + kv.replace(".", "")


def measure(kv, seed):
    d = os.path.join(DST, "R418%s_s%d" % (tag(kv), seed))
    sto = os.path.join(d, "FROZEN.par.sto")
    if not os.path.exists(sto):
        return None
    cols, dat = S.load_sto(sto)
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    on = grf > thr

    # first left toe-off after T0, then the next heel strike
    idx = np.where(t >= T0)[0]
    to = None
    for k in idx[:-1]:
        if on[k] and not on[k + 1]:
            to = k + 1
            break
    if to is None:
        return {"error": "no toe-off after %.2f s" % T0, "t_end": float(t[-1])}
    hs = None
    for k in range(to, len(t) - 1):
        if not on[k] and on[k + 1]:
            hs = k + 1
            break
    if hs is None:
        return {"error": "no heel strike after toe-off", "t_end": float(t[-1]),
                "toe_off_s": float(t[to])}

    sw = np.arange(to, hs)
    L = S.col(cols, dat, "gastroc_l.L")[sw]
    A = S.col(cols, dat, "gastroc_l.activation")[sw]
    K = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return {"t_end": float(t[-1]), "toe_off_s": float(t[to]), "heel_strike_s": float(t[hs]),
            "n_swing_samples": int(len(sw)),
            "GASLEN": float(np.mean(L)), "GASSTRETCH": float(np.max(L) - np.min(L)),
            "GASDRIVE": float(np.mean(A)),
            "KNEE_sw": float(np.min(K[sw])), "KNEE_ic": float(K[hs])}


def rung_stats(cells, key):
    v = [c[key] for c in cells if key in c]
    return {"n": len(v), "mean": float(np.mean(v)), "range": [float(min(v)), float(max(v))]} if v else None


def disjoint(a, b):
    """a and b are [lo, hi]; True if the intervals do not overlap."""
    return a[1] < b[0] or b[1] < a[0]


res = {"round": "SLACK_RESULT_r418", "registration": "PREREG_slack_r418.md",
       "registration_sha256": "a908b4b716cf2ac22b0ff2cfe4c2fe584788484404778e8583724272fc3bdd33",
       "units_note": __doc__.split("UNITS NOTE, recorded rather than corrected: ")[1].strip(),
       "gastroc_KV_fixed_at": 0.050, "cells": {}, "rungs": {}}

by_rung = {}
for kv in RUNGS:
    cells = []
    for s in SEEDS:
        m = measure(kv, s)
        res["cells"]["R418%s_s%d" % (tag(kv), s)] = m
        if m and "error" not in m:
            cells.append(m)
    by_rung[kv] = cells
    res["rungs"][kv] = {"n_with_sto": len(cells),
                        "uninformative": len(cells) < 4,
                        **{k: rung_stats(cells, k) for k in
                           ("GASLEN", "GASSTRETCH", "GASDRIVE", "KNEE_sw", "KNEE_ic", "t_end")}}

print("%-8s %-3s %-9s %-9s %-9s %-10s %-10s %s" %
      ("solKV", "n", "GASLEN", "STRETCH", "DRIVE", "KNEE_sw", "KNEE_ic", "t_end"))
for kv in RUNGS:
    r = res["rungs"][kv]
    if not r["n_with_sto"]:
        print("  %-6s 0   --" % kv)
        continue
    print("  %-6s %-3d %-9.5f %-9.5f %-9.5f %-10.4f %-10.4f [%.2f,%.2f]" %
          (kv, r["n_with_sto"], r["GASLEN"]["mean"], r["GASSTRETCH"]["mean"], r["GASDRIVE"]["mean"],
           r["KNEE_sw"]["mean"], r["KNEE_ic"]["mean"], r["t_end"]["range"][0], r["t_end"]["range"][1]))

lo, hi = RUNGS[0], RUNGS[-1]
P = {}
means = [res["rungs"][k]["GASLEN"]["mean"] for k in RUNGS if res["rungs"][k]["n_with_sto"]]
P["P1_GASLEN_monotone_decreasing"] = {
    "rung_means": means,
    "monotone_decreasing": all(means[i] > means[i + 1] for i in range(len(means) - 1)),
    "VERDICT": "HOLDS" if all(means[i] > means[i + 1] for i in range(len(means) - 1)) else "FAILS"}

for pn, key, want_lower in (("P2_GASSTRETCH", "GASSTRETCH", True),
                            ("P3_GASDRIVE", "GASDRIVE", True),
                            ("P4_KNEE_sw_less_flexed", "KNEE_sw", False)):
    a, b = res["rungs"][lo][key], res["rungs"][hi][key]
    if not (a and b):
        P[pn] = {"VERDICT": "UNINFORMATIVE"}
        continue
    moved = (b["mean"] < a["mean"]) if want_lower else (b["mean"] > a["mean"])
    dj = disjoint(a["range"], b["range"])
    P[pn] = {"rung_%s" % lo: a, "rung_%s" % hi: b, "direction_as_predicted": bool(moved),
             "disjoint": bool(dj), "VERDICT": "HOLDS" if (moved and dj) else "FAILS"}

allc = [c for cs in by_rung.values() for c in cs]
gl = np.array([c["GASLEN"] for c in allc])
ks = np.array([c["KNEE_sw"] for c in allc])
rk = np.argsort(np.argsort(gl)).astype(float)
rj = np.argsort(np.argsort(ks)).astype(float)
rho = float(np.corrcoef(rk, rj)[0, 1])
P["P5_spearman_GASLEN_vs_KNEE_sw"] = {"rho": rho, "n": len(allc), "threshold": -0.5,
                                      "VERDICT": "HOLDS" if rho <= -0.5 else "FAILS"}

# ---- section 6 duration control, registered before the data existed ----
ct, ck, per = [], [], {}
for kv in RUNGS:
    cs = by_rung[kv]
    if len(cs) < 2:
        continue
    tt = np.array([c["t_end"] for c in cs])
    kk = np.array([c["KNEE_sw"] for c in cs])
    if len(set(tt.tolist())) > 1:
        per[kv] = {"slope_deg_per_s": float(np.polyfit(tt, kk, 1)[0]),
                   "pearson_r": float(np.corrcoef(tt, kk)[0, 1]), "n": len(cs)}
    ct += list(tt - tt.mean())
    ck += list(kk - kk.mean())
bw = float(np.polyfit(ct, ck, 1)[0]) if len(set(ct)) > 1 else 0.0
rw = float(np.corrcoef(ct, ck)[0, 1]) if len(set(ct)) > 1 else 0.0
tspan = abs(res["rungs"][hi]["t_end"]["mean"] - res["rungs"][lo]["t_end"]["mean"])
eff = abs(res["rungs"][hi]["KNEE_sw"]["mean"] - res["rungs"][lo]["KNEE_sw"]["mean"])
attrib = abs(bw) * tspan
frac = attrib / eff if eff else float("inf")
res["duration_control"] = {"per_rung": per, "rung_centred_pooled_slope_deg_per_s": bw,
                           "pearson_r": rw, "between_rung_t_end_span_s": tspan,
                           "KNEE_sw_effect_deg": eff, "deg_attributable_to_duration": attrib,
                           "fraction_of_effect": frac, "threshold": 0.50,
                           "CONFOUNDED": bool(frac > 0.50)}
if res["duration_control"]["CONFOUNDED"] and P["P4_KNEE_sw_less_flexed"]["VERDICT"] == "HOLDS":
    P["P4_KNEE_sw_less_flexed"]["VERDICT"] = "CONFOUNDED (section 6); not counted as holding"

res["predictions"] = P
held = [k for k, v in P.items() if v["VERDICT"] == "HOLDS"]
res["VERDICT"] = "%d of %d predictions hold: %s" % (len(held), len(P), ", ".join(held) or "none")

print()
for k, v in P.items():
    print("  %-34s %s" % (k, v["VERDICT"]))
print()
print("duration control: pooled slope %+.4f deg/s (r %+.4f), %.4f deg of %.4f = %.0f%% -> %s"
      % (bw, rw, attrib, eff, 100 * frac, "CONFOUNDED" if frac > 0.5 else "clear"))
print("VERDICT:", res["VERDICT"])
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
