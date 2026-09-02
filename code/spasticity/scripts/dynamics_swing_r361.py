# -*- coding: utf-8 -*-
"""PREREG_dynamics_r360.md (a62573f5...) -- swing-phase plantarflexor activation.

Primary endpoint PF_swing, section 3, fixed before any value was computed:
  per-cycle mean of (soleus_l.activation + gastroc_l.activation)/2 over SWING samples,
  averaged over admissible cycles. One scalar per cell.

Conventions are CARRIED, not re-invented:
  rd()              -- history.txt >= 91 lines, exactly one dir per tag   (from r290/r291)
  sorted(*.par.sto)[-1]                                                   (from r290/r291)
  SETTLE 1.00, T1 9.73, drop the last cycle in window                     (hipgap_r220)
  swing = NOT (grf_norm_y > 0.05); the 0.05 comes from sto_utils.grf_vertical,
          which is the same threshold heel_strikes uses -- section 3's fixed value
          and the corpus convention agree, so no amendment was needed.

Secondaries (section 6) are deposited and may never be promoted.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DYNAMICS_SWING_r361.json"
SETTLE, T1 = 1.0, 9.73
BAND = (13.58, 17.85)

SPASTIC = ["R289KV00625", "R289KV0125", "R291KV0035", "R291KV0070"]
DFWEAK = ["R293DFs010", "R293DFs030", "R293DFs050"]      # DFs000 excluded, r303 NOT ADMISSIBLE


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
    if grf is None:
        rec["error"] = "no grf"
        return rec
    rec["grf_threshold"] = thr
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles"] = len(allc)
    rec["n_cycles_in_window"] = len(win)

    # Gate G, section 2
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["measured"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec

    sig = {}
    for m in ("soleus", "gastroc", "tib_ant"):
        v = S.muscle_signal(cols, dat, m, "l", "activation")
        if v is None:
            rec["error"] = "missing %s_l.activation" % m
            return rec
        sig[m] = v
    tq = S.col(cols, dat, "ankle_l.torque")

    stance_on = grf > thr
    pf_sw, ta_sw, cc_sw, tq_sw = [], [], [], []
    pf_st, ta_st, tq_st = [], [], []
    for a, b in win:
        sw = ~stance_on[a:b]
        st = stance_on[a:b]
        if not sw.any() or not st.any():
            continue
        pf = (sig["soleus"][a:b] + sig["gastroc"][a:b]) / 2.0
        ta = sig["tib_ant"][a:b]
        p, q = float(np.mean(pf[sw])), float(np.mean(ta[sw]))
        pf_sw.append(p)
        ta_sw.append(q)
        cc_sw.append(min(p, q) / max(p, q) if max(p, q) > 0 else float("nan"))
        pf_st.append(float(np.mean(pf[st])))
        ta_st.append(float(np.mean(ta[st])))
        if tq is not None:
            tq_sw.append(float(np.mean(tq[a:b][sw])))
            tq_st.append(float(np.mean(tq[a:b][st])))

    if not pf_sw:
        rec["measured"] = False
        rec["guard"] = "no cycle with both a stance and a swing sample"
        return rec

    def mean(x):
        x = [v for v in x if np.isfinite(v)]
        return float(np.mean(x)) if x else None

    rec["measured"] = True
    rec["n_cycles_used"] = len(pf_sw)
    rec["PF_swing"] = mean(pf_sw)                       # PRIMARY, section 3
    rec["secondary"] = {                                # section 6, never promoted
        "tib_ant_swing": mean(ta_sw),
        "cocontraction_swing": mean(cc_sw),
        "ankle_torque_swing": mean(tq_sw) if tq_sw else None,
        "PF_stance": mean(pf_st),
        "tib_ant_stance": mean(ta_st),
        "ankle_torque_stance": mean(tq_st) if tq_st else None,
    }
    return rec


def spearman(x, y):
    n = len(x)
    if n < 3:
        return None

    def rank(v):
        o = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[o[j + 1]] == v[o[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[o[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return float(num / den) if den else None


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
    return {"method": "exhaustive over C(%d,%d)" % (len(allv), n1),
            "n_total": tot, "n_at_least_as_extreme": cnt,
            "floor": "1/%d" % tot, "fraction": cnt / float(tot)}


def reading(name, sp, wk):
    """sp, wk are lists of (tag, value, t_end)."""
    r = {"name": name, "n_spastic": len(sp), "n_weak": len(wk),
         "spastic_cells": {a: b for a, b, _ in sp},
         "weak_cells": {a: b for a, b, _ in wk}}
    if len(sp) < 1 or len(wk) < 1:
        r["VERDICT"] = "UNINFORMATIVE"
        r["why"] = "an arm is empty"
        return r
    s = [b for _, b, _ in sp]
    w = [b for _, b, _ in wk]
    r["spastic_range"] = [min(s), max(s)]
    r["weak_range"] = [min(w), max(w)]
    gap = max(min(w) - max(s), min(s) - max(w))
    r["gap"] = gap
    r["separated"] = bool(gap > 0)
    if gap > 0:
        r["direction"] = "SPASTIC HIGH" if min(s) > max(w) else "SPASTIC LOW"
        r["matches_registered_prediction"] = bool(r["direction"] == "SPASTIC HIGH")
        r["permutation"] = perm_floor(s, w)
        r["VERDICT"] = "SEPARATED"
    else:
        r["VERDICT"] = "OVERLAP"
    return r


def main():
    res = {"registration": "PREREG_dynamics_r360.md",
           "registration_sha256":
               "a62573f5049825e0adb8c11618f2b19d4ae5b315723a67c13c87f26261ad19de",
           "endpoint": "PF_swing = mean over swing of (soleus_l.activation+gastroc_l.activation)/2",
           "registered_prediction": "SPASTIC HIGH, DORSIFLEXOR-WEAK LOW",
           "window_s": [SETTLE, T1], "band_s": list(BAND), "cells": {}}

    arms = {}
    for arm, fams in (("SPASTIC", SPASTIC), ("DFWEAK", DFWEAK)):
        rows = []
        for tag in tags_for(fams):
            rec = measure(tag)
            res["cells"][tag] = rec
            print("  %-18s %s" % (tag, "PF_swing=%.6f t_end=%.2f n=%d"
                                  % (rec["PF_swing"], rec["t_end_s"], rec["n_cycles_used"])
                                  if rec.get("measured") else
                                  rec.get("guard", rec.get("error", "?"))))
            if rec.get("measured"):
                rows.append((tag, rec["PF_swing"], rec["t_end_s"]))
        arms[arm] = rows
        print("%s: %d measured" % (arm, len(rows)))

    # section 4 -- the duration-invariance test decides which reading is primary
    rho = {}
    for arm, rows in arms.items():
        rho[arm] = spearman([b for _, b, _ in rows], [c for _, _, c in rows]) if len(rows) >= 3 else None
    res["duration_invariance"] = {
        "spearman_rho_PFswing_vs_tend": rho,
        "threshold": 0.5,
        "contaminated": any(r is not None and abs(r) >= 0.5 for r in rho.values()),
    }

    res["READING_U_unmatched"] = reading("U (unmatched, all Gate-G cells)",
                                         arms["SPASTIC"], arms["DFWEAK"])
    inb = {k: [r for r in v if BAND[0] <= r[2] <= BAND[1]] for k, v in arms.items()}
    res["READING_M_duration_matched"] = reading("M (duration-matched, band %s)" % (list(BAND),),
                                                inb["SPASTIC"], inb["DFWEAK"])
    if len(inb["SPASTIC"]) < 3 or len(inb["DFWEAK"]) < 3:
        res["READING_M_duration_matched"]["VERDICT"] = "UNINFORMATIVE"
        res["READING_M_duration_matched"]["why"] = (
            "section 4 requires >=3 per arm in band; got %d spastic, %d weak"
            % (len(inb["SPASTIC"]), len(inb["DFWEAK"])))

    contaminated = res["duration_invariance"]["contaminated"]
    res["PRIMARY_READING"] = "READING_M_duration_matched" if contaminated else "READING_U_unmatched"
    res["why_primary"] = (
        "section 4: |rho| >= 0.5 in at least one arm, so READING U is NOT ADMISSIBLE"
        if contaminated else
        "section 4: |rho| < 0.5 in both arms, so the endpoint is duration-invariant "
        "and READING U is primary")

    # secondaries, deposited, never promoted
    sec = {}
    for key in ("tib_ant_swing", "cocontraction_swing", "ankle_torque_swing",
                "PF_stance", "tib_ant_stance", "ankle_torque_stance"):
        pair = {}
        for arm in ("SPASTIC", "DFWEAK"):
            vals = [res["cells"][t]["secondary"][key] for t, _, _ in arms[arm]
                    if res["cells"][t]["secondary"].get(key) is not None]
            pair[arm] = {"n": len(vals),
                         "range": [min(vals), max(vals)] if vals else None,
                         "mean": float(np.mean(vals)) if vals else None}
        sec[key] = pair
    res["SECONDARY_never_promoted"] = sec

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    print("rho spastic=%s  weak=%s  contaminated=%s"
          % (rho["SPASTIC"], rho["DFWEAK"], contaminated))
    print("PRIMARY = %s" % res["PRIMARY_READING"])
    p = res[res["PRIMARY_READING"]]
    print("  %s  n=%d vs %d  gap=%s" % (p["VERDICT"], p["n_spastic"], p["n_weak"], p.get("gap")))
    if p.get("separated"):
        print("  direction=%s  matches prediction=%s  floor=%s"
              % (p["direction"], p["matches_registered_prediction"], p["permutation"]["floor"]))
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
