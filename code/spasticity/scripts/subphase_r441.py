# -*- coding: utf-8 -*-
"""r441: which stance sub-phase carries the knee signal — does the model agree with Cawood 2023?

WHY. Cawood C, Mashola K, S Afr J Physiother 2023;79(1):1926 (PMID 38059056, n=12 adult hemiparetic
stroke, Modified Tardieu, 2D Kinovea) correlated graded PLANTARFLEXOR tone against hemiparetic knee
angle at five stance sub-phases. Table 5, read verbatim from the journal's JATS XML:

    sub-phase          rho     p
    initial contact   0.542   0.069     (not significant)
    loading response  0.321   0.309
    midstance         0.492   0.104
    terminal stance   0.745   0.005  **
    pre-swing         0.672   0.017  *

So in real patients the graded tone-to-knee relationship is STRONGEST AT TERMINAL STANCE, and
initial contact is only a trend. This round asks the same question of the model, on the same five
windows, so the two can be compared instead of assumed to agree.

STATUS: EXPLORATORY. No registration. Chosen after reading Cawood's Table 5. NO SIMULATION IS RUN.

Two quantities per window:
  (a) DOSE: Spearman rho between spastic gain and knee angle, across the chained spastic ladder --
      the direct analogue of Cawood's correlation.
  (b) SEPARATION: spastic-vs-weakness effect in units of the within-cell seed SD for that window --
      the quantity this project actually claims.
Sub-phases are fractions of the STANCE period (Perry's divisions are % of gait cycle; using stance
fractions keeps the windows comparable across cells whose stance ratio differs).
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUBPHASE_r441.json"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

# fraction of the stance period; "initial contact" is the contact sample itself
WINDOWS = [("initial_contact", None, None),
           ("loading_response", 0.00, 0.20),
           ("midstance", 0.20, 0.50),
           ("terminal_stance", 0.50, 0.80),
           ("pre_swing", 0.80, 1.00)]

SPAS = [("R151S", 0.050), ("R393SPg070", 0.070), ("R393SPg100", 0.100),
        ("R396SPg110", 0.110), ("R396SPg120", 0.120)]
WEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CTRL = ["R151C"]


def cell(prefix):
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
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))

    out = {}
    for name, lo, hi in WINDOWS:
        vals = []
        for a, b in win:
            idx = np.arange(a, b)[on[a:b]]          # stance samples of this cycle
            if idx.size == 0:
                continue
            if lo is None:
                vals.append(kn[a])                  # the contact sample itself
            else:
                n = len(idx)
                seg = idx[int(lo * n):max(int(hi * n), int(lo * n) + 1)]
                if seg.size:
                    vals.append(float(np.mean(kn[seg])))
        out[name] = float(np.mean(vals)) if vals else None
    out["n_cycles"] = len(win)
    return out


def pool(prefixes):
    out = []
    for f in prefixes:
        for s in SEEDS:
            c = cell("%s_s%d" % (f, s))
            if c:
                c["family"] = f
                out.append(c)
    return out


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


# spastic ladder with its dose, weakness pool, control pool
sp_cells = []
for fam, kv in SPAS:
    for s in SEEDS:
        c = cell("%s_s%d" % (fam, s))
        if c:
            c["KV"] = kv
            c["family"] = fam
            sp_cells.append(c)
wk_cells, ct_cells = pool(WEAK), pool(CTRL)

res = {"round": "SUBPHASE_r441", "no_simulation_run": True,
       "status": "EXPLORATORY. No registration. The window set was chosen to match Cawood & "
                 "Mashola 2023 Table 5 after reading it.",
       "cawood_table5_plantarflexor_tone_vs_knee": {
           "source": "Cawood C, Mashola K. S Afr J Physiother 2023;79(1):1926; PMID 38059056; "
                     "read verbatim from the journal JATS XML galley",
           "n": 12, "modality": "2D video (Kinovea), Modified Tardieu plantarflexor tone",
           "initial_contact": {"rho": 0.542, "p": 0.069},
           "loading_response": {"rho": 0.321, "p": 0.309},
           "midstance": {"rho": 0.492, "p": 0.104},
           "terminal_stance": {"rho": 0.745, "p": 0.005},
           "pre_swing": {"rho": 0.672, "p": 0.017}},
       "n_cells": {"spastic": len(sp_cells), "weakness": len(wk_cells), "control": len(ct_cells)},
       "windows": {}}

print("spastic %d   weakness %d   control %d" % (len(sp_cells), len(wk_cells), len(ct_cells)))
print()
print("%-18s %-10s %-10s %-11s %-9s %s"
      % ("window", "dose rho", "Cawood rho", "spas-weak", "seed SD", "in seed SDs"))
for name, _, _ in WINDOWS:
    sv = [c[name] for c in sp_cells if c.get(name) is not None]
    kv = [c["KV"] for c in sp_cells if c.get(name) is not None]
    wv = [c[name] for c in wk_cells if c.get(name) is not None]
    cv = [c[name] for c in ct_cells if c.get(name) is not None]
    if len(sv) < 4 or len(wv) < 4:
        continue
    rho = spearman(np.array(kv), np.array(sv))

    # within-cell seed SD for this window, over every spastic family and every weakness family
    sds = []
    for fam, _ in SPAS:
        v = [c[name] for c in sp_cells if c["family"] == fam and c.get(name) is not None]
        if len(v) >= 4:
            sds.append(np.std(v, ddof=1))
    for fam in WEAK:
        v = [c[name] for c in wk_cells if c["family"] == fam and c.get(name) is not None]
        if len(v) >= 4:
            sds.append(np.std(v, ddof=1))
    sd = float(np.mean(sds))
    diff = float(np.mean(sv) - np.mean(wv))

    res["windows"][name] = {
        "spastic": {"n": len(sv), "mean": float(np.mean(sv))},
        "weakness": {"n": len(wv), "mean": float(np.mean(wv))},
        "control": {"n": len(cv), "mean": float(np.mean(cv)) if cv else None},
        "dose_spearman_rho_KV_vs_knee": rho,
        "spastic_minus_weakness_deg": diff,
        "within_cell_seed_SD_deg": sd,
        "separation_in_seed_SDs": abs(diff) / sd if sd else None,
        "displacement_from_control": {
            "weakness": float(np.mean(wv) - np.mean(cv)) if cv else None,
            "spastic": float(np.mean(sv) - np.mean(cv)) if cv else None}}
    e = res["windows"][name]
    cw = res["cawood_table5_plantarflexor_tone_vs_knee"][name]["rho"]
    print("  %-16s %+9.3f %+10.3f %+10.3f  %-9.3f %.1f"
          % (name, rho, cw, diff, sd, e["separation_in_seed_SDs"]))

print()
print("=== 相對對照的位移(度)===")
print("%-18s %-12s %s" % ("window", "weakness", "spastic"))
for name in res["windows"]:
    d = res["windows"][name]["displacement_from_control"]
    if d["weakness"] is not None:
        print("  %-16s %+11.3f %+11.3f" % (name, d["weakness"], d["spastic"]))

best_dose = max(res["windows"], key=lambda k: abs(res["windows"][k]["dose_spearman_rho_KV_vs_knee"]))
best_sep = max(res["windows"], key=lambda k: res["windows"][k]["separation_in_seed_SDs"])
res["model_strongest_dose_window"] = best_dose
res["model_strongest_separation_window"] = best_sep
res["cawood_strongest_window"] = "terminal_stance"
res["AGREEMENT"] = ("model and patients agree" if best_dose == "terminal_stance"
                    else "model and patients DISAGREE: the model's strongest dose window is %s, "
                         "Cawood's is terminal_stance" % best_dose)
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("model strongest DOSE window       : %s" % best_dose)
print("model strongest SEPARATION window : %s" % best_sep)
print("Cawood strongest window (patients): terminal_stance")
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
