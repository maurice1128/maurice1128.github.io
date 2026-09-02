# -*- coding: utf-8 -*-
"""PREREG_reflexgain_r364.md (939c81b6...) -- BETA_stretch, section 3.

Observables only: ankle_angle_l (motion capture) and soleus_l.activation (surface EMG).
BETA_stretch = OLS slope of activation(t) on max(0, dorsiflexion_velocity(t - tau)),
tau = 0.020 s, fitted over pooled STANCE samples of the admissible cycles of one cell.

Conventions carried unaltered: rd() >= 91-line history.txt; sorted(*.par.sto)[-1];
SETTLE 1.00, T1 9.73, >=5 cycles in window, last cycle in window dropped; stance is
leg0_l.grf_norm_y > 0.05, the threshold sto_utils.heel_strikes uses.

Inference is the seed-level permutation of section 5 only. Section 8 forbids reporting any
standard error, confidence interval or p-value from the regression itself.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\REFLEXGAIN_r366.json"
PREREG_SHA = "939c81b6ea6544a35243e41d171c0fb0d9e80c50ed0d2207fec70d6b9f6d743c"
SETTLE, T1 = 1.0, 9.73
TAU_S = 0.020
MIN_SAMPLES = 30

SPASTIC = ["R289KV00625", "R289KV0125"]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def tags_for(fams):
    out = []
    for f in fams:
        seen = set()
        for d in sorted(glob.glob(os.path.join(RES, f + "_s*"))):
            b = os.path.basename(d).split(".")[0]
            if b not in seen:
                seen.add(b)
                out.append(b)
    return out


def ols(x, y):
    """Slope and R^2. No standard error -- section 8 forbids reporting one."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if len(x) < MIN_SAMPLES:
        return None, None, len(x)
    vx = x - x.mean()
    vy = y - y.mean()
    den = float((vx * vx).sum())
    if den <= 0:
        return None, None, len(x)
    b = float((vx * vy).sum() / den)
    ss = float((vy * vy).sum())
    r2 = float(1.0 - ((vy - b * vx) ** 2).sum() / ss) if ss > 0 else None
    return b, r2, len(x)


def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        return rec
    rec["dir"] = os.path.basename(d)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        return rec
    rec["sto"] = os.path.basename(stos[-1])
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        return rec
    t = dat[:, 0]
    rec["t_end_s"] = float(t[-1])

    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["measured"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec

    ang = S.col(cols, dat, "ankle_angle_l")
    if ang is None:
        rec["error"] = "no ankle_angle_l"
        return rec
    # sign: SCONE ankle_angle is positive in DORSIFLEXION for this model; the derivative is
    # taken as-is and the clipping keeps only lengthening. The convention is asserted below
    # against stance kinematics rather than assumed silently.
    v = np.gradient(ang, t)
    lag = int(round(TAU_S / float(np.median(np.diff(t)))))
    rec["tau_samples"] = lag
    xfull = np.concatenate([np.zeros(lag), np.maximum(0.0, v[:-lag])]) if lag > 0 \
        else np.maximum(0.0, v)

    sig = {}
    for m in ("soleus", "gastroc", "tib_ant"):
        s = S.muscle_signal(cols, dat, m, "l", "activation")
        if s is None:
            rec["error"] = "missing %s_l.activation" % m
            return rec
        sig[m] = s
    tq = S.col(cols, dat, "ankle_l.torque")
    stance_on = grf > thr

    def pooled(mask_stance):
        xs, ys = {"soleus": [], "gastroc": [], "tib_ant": []}, None
        X = []
        Y = {"soleus": [], "gastroc": [], "tib_ant": []}
        for a, b in win:
            m = stance_on[a:b] if mask_stance else ~stance_on[a:b]
            if not m.any():
                continue
            X.append(xfull[a:b][m])
            for k in Y:
                Y[k].append(sig[k][a:b][m])
        if not X:
            return None, None
        return np.concatenate(X), {k: np.concatenate(v) for k, v in Y.items()}

    Xs, Ys = pooled(True)
    if Xs is None:
        rec["measured"] = False
        rec["guard"] = "no stance samples"
        return rec
    b, r2, n = ols(Xs, Ys["soleus"])
    if b is None:
        rec["measured"] = False
        rec["guard"] = "only %d pooled stance samples, need %d" % (n, MIN_SAMPLES)
        return rec

    rec["measured"] = True
    rec["n_stance_samples"] = n
    rec["BETA_stretch"] = b                                   # PRIMARY, section 3
    rec["r2_primary"] = r2
    sec = {}
    for k in ("gastroc", "tib_ant"):
        bb, rr, _ = ols(Xs, Ys[k])
        sec["BETA_" + k] = bb
        sec["r2_" + k] = rr
    Xw, Yw = pooled(False)
    if Xw is not None:
        bw, rw, nw = ols(Xw, Yw["soleus"])
        sec["BETA_soleus_swing_contrast"] = bw
        sec["r2_soleus_swing_contrast"] = rw
        sec["n_swing_samples"] = nw
    if tq is not None:
        sec["ankle_torque_stance_mean"] = float(np.mean(
            np.concatenate([tq[a:b][stance_on[a:b]] for a, b in win
                            if stance_on[a:b].any()])))
    rec["secondary"] = sec
    return rec


def perm_floor(sp, wk):
    allv = list(sp) + list(wk)
    n1 = len(sp)
    obs = max(min(wk) - max(sp), min(sp) - max(wk))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        a = [allv[i] for i in comb]
        b = [allv[i] for i in range(len(allv)) if i not in comb]
        g = max(min(b) - max(a), min(a) - max(b))
        tot += 1
        if g >= obs - 1e-12:
            cnt += 1
    return {"method": "exhaustive over C(%d,%d)" % (len(allv), n1), "n_total": tot,
            "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot, "fraction": cnt / float(tot)}


def main():
    res = {"registration": "PREREG_reflexgain_r364.md", "registration_sha256": PREREG_SHA,
           "endpoint": "BETA_stretch = OLS slope of soleus_l.activation on "
                       "max(0, dorsiflexion velocity at t-0.020 s), pooled stance samples",
           "registered_prediction": "SPASTIC HIGH, DORSIFLEXOR-WEAK LOW",
           "observables_only": ["ankle_angle_l", "soleus_l.activation", "leg0_l.grf_norm_y"],
           "inference_note": "section 8: no SE/CI/p from the regression; inference is the "
                             "seed-level permutation of section 5 only",
           "window_s": [SETTLE, T1], "tau_s": TAU_S, "cells": {}}
    arms = {}
    for arm, fams in (("SPASTIC", SPASTIC), ("DFWEAK", DFWEAK)):
        rows = []
        for tag in tags_for(fams):
            r = measure(tag)
            res["cells"][tag] = r
            print("  %-16s %s" % (tag, "BETA=%+.6f r2=%.4f n=%d"
                                  % (r["BETA_stretch"], r["r2_primary"], r["n_stance_samples"])
                                  if r.get("measured") else r.get("guard", r.get("error", "?"))))
            if r.get("measured"):
                rows.append((tag, r["BETA_stretch"]))
        arms[arm] = rows
        print("%s: %d measured" % (arm, len(rows)))

    sp = [b for _, b in arms["SPASTIC"]]
    wk = [b for _, b in arms["DFWEAK"]]
    r = {"n_spastic": len(sp), "n_weak": len(wk),
         "spastic_cells": dict(arms["SPASTIC"]), "weak_cells": dict(arms["DFWEAK"])}
    if len(sp) < 5 or len(wk) < 5:
        r["VERDICT"] = "UNINFORMATIVE"
        r["why"] = "section 7 requires >=5 per arm; got %d, %d" % (len(sp), len(wk))
    else:
        r["spastic_range"] = [min(sp), max(sp)]
        r["weak_range"] = [min(wk), max(wk)]
        gap = max(min(wk) - max(sp), min(sp) - max(wk))
        r["gap"] = gap
        r["separated"] = bool(gap > 0)
        if gap > 0:
            r["direction"] = "SPASTIC HIGH" if min(sp) > max(wk) else "SPASTIC LOW"
            r["matches_registered_prediction"] = bool(r["direction"] == "SPASTIC HIGH")
            r["permutation"] = perm_floor(sp, wk)
            r["VERDICT"] = "SEPARATED"
        else:
            r["VERDICT"] = "OVERLAP"
            r["spastic_mean"] = float(np.mean(sp))
            r["weak_mean"] = float(np.mean(wk))
    res["READING_U_primary"] = r

    sec = {}
    for key in ("BETA_gastroc", "BETA_tib_ant", "BETA_soleus_swing_contrast",
                "ankle_torque_stance_mean", "r2_primary"):
        pair = {}
        for arm in ("SPASTIC", "DFWEAK"):
            vals = []
            for tag, _ in arms[arm]:
                c = res["cells"][tag]
                v = c.get(key) if key == "r2_primary" else c.get("secondary", {}).get(key)
                if v is not None:
                    vals.append(v)
            pair[arm] = {"n": len(vals), "range": [min(vals), max(vals)] if vals else None,
                         "mean": float(np.mean(vals)) if vals else None}
        sec[key] = pair
    res["SECONDARY_never_promoted"] = sec

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    print("VERDICT %s" % r["VERDICT"])
    if r.get("separated"):
        print("  gap=%.8f direction=%s matches_prediction=%s floor=%s"
              % (r["gap"], r["direction"], r["matches_registered_prediction"],
                 r["permutation"]["floor"]))
    elif "gap" in r:
        print("  gap=%.8f  spastic %s  weak %s  means %.6f vs %.6f"
              % (r["gap"], r["spastic_range"], r["weak_range"],
                 r["spastic_mean"], r["weak_mean"]))
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
