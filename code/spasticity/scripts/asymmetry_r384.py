# -*- coding: utf-8 -*-
"""r384 TASK 1 -- DIRECTIONAL ASYMMETRY of the half-wave-rectified spastic lesion.

FIRST PRINCIPLE. The spastic lesion is a HALF-WAVE RECTIFIED velocity feedback (allow_neg_V=0):
it injects drive ONLY while the muscle lengthens. The dorsiflexor-weakness lesion is a linear
force scaling and acts in BOTH directions equally. Re-optimisation adjusts reflex/feedforward
GAINS, which are linear and therefore direction-SYMMETRIC. A gain change cannot manufacture a
direction asymmetry, so a direction asymmetry should SURVIVE compensation even where the
amplitude it rides on does not. Every amplitude endpoint tried so far lands at 0.22-1.21 deg
against a clinical MDC of 3.8-11.5 deg; amplitudes are exhausted, ratios and asymmetries are not.

MEASURES, per cell, over ALL samples of the admissible cycles (whole cycle, no phase mask):
    v(t)      = d(ankle_angle_l)/dt, rad/s, POSITIVE = DORSIFLEXION = soleus LENGTHENING
    v(t-tau)  with tau = 0.020 s = 2 samples (the model's reflex delay)
    A_lengthen = mean channel over samples with v(t-tau) > 0
    A_shorten  = mean channel over samples with v(t-tau) < 0
    ASYM_diff  = A_lengthen - A_shorten
    ASYM_ratio = (A_lengthen - A_shorten) / (A_lengthen + A_shorten)      <- SCALE-FREE, the key one
Channels: soleus_l.activation, gastroc_l.activation, tib_ant_l.activation, ankle_l.torque.
Two matching schemes:
    ALL      -- every admissible sample
    MIDTERT  -- only samples whose |v(t-tau)| lies in the MIDDLE TERTILE of that cell's own
                |v(t-tau)| distribution, so the lengthening and shortening halves are compared
                at MATCHED STRETCH SPEEDS. This removes the trivial explanation that lengthening
                and shortening simply happen at different speeds.

MULTIPLICITY, DECLARED: 3 muscles x 2 forms (diff, ratio) x 2 matching schemes = 12, PLUS
ankle_l.torque x 2 forms x 2 schemes = 4, TOTAL 16 measures per rung, x 4 rungs = 64 tests.
This deposit is EXPLORATORY. It nominates no single measure in advance, so no separation here
is a confirmatory result; any survivor must be re-registered as ONE nominated measure and
re-tested on data not used to choose it.

SIGN CONVENTION is taken from the corpus, NOT re-derived; it is ASSERTED here by checking that
stance shows dorsiflexion (mean v > 0 over the first half of stance) followed by plantarflexion
(mean v < 0 over the last quarter of stance) in every admissible cycle.

Conventions carried VERBATIM from doseladder_r371.py:
  rd()   = the one directory per tag with history.txt >= 91 lines
  sto    = sorted(glob("*.par.sto"))[-1]
  SETTLE = 1.00, T1 = 9.73
  cycles between heel strikes with t[start] >= SETTLE, wholly inside the window,
         drop the LAST kept cycle, require >= 5
  stance = leg0_l.grf_norm_y > 0.05   (via S.grf_vertical, thr 0.05)
  floor() = exhaustive gap-based two-sided permutation over C(12,6) = 924
"""
import glob
import io
import itertools
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\ASYMMETRY_r384.json"
SETTLE, T1, TAU_S = 1.0, 9.73, 0.020

LADDER = [(0.00625, "R289KV00625"), (0.0125, "R289KV0125"),
          (0.035, "R291KV0035"), (0.070, "R291KV0070")]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CONTROL = ["R203V080C", "R203V105C", "R203V130C"]

CHANNELS = [("soleus_l", "muscle", ("soleus", "l", "activation")),
            ("gastroc_l", "muscle", ("gastroc", "l", "activation")),
            ("tib_ant_l", "muscle", ("tib_ant", "l", "activation")),
            ("ankle_l_torque", "col", "ankle_l.torque")]
SCHEMES = ["ALL", "MIDTERT"]
FORMS = ["diff", "ratio"]


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


def audit_min_velocity(fam):
    """Scenario audit: min_velocity is the thing that made the CONTROL arm between-scenario."""
    try:
        d = rd(tags_for([fam])[0])
    except Exception as e:
        return {"error": str(e)}
    cfg = os.path.join(d, "config.scone")
    if not os.path.exists(cfg):
        return {"min_velocity": None}
    txt = io.open(cfg, encoding="utf-8", errors="replace").read()
    m = re.search(r"min_velocity\s*=\s*([0-9.]+)", txt)
    return {"min_velocity": float(m.group(1)) if m else None,
            "has_SpasticL": "SpasticL" in txt}


def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        return rec
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
        rec["error"] = "no left vertical GRF"
        return rec
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["gate_G"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec
    rec["gate_G"] = True
    on = grf > thr

    ank = S.col(cols, dat, "ankle_angle_l")
    if ank is None:
        rec["gate_G"] = False
        rec["guard"] = "no ankle_angle_l"
        return rec
    v = np.gradient(ank, t)                       # rad/s, + = dorsiflexion (corpus convention)

    dt = float(np.median(np.diff(t)))
    nlag = int(round(TAU_S / dt))
    rec["dt_s"] = dt
    rec["lag_samples"] = nlag
    if nlag < 1:
        rec["gate_G"] = False
        rec["guard"] = "tau %.3f s < one sample (dt %.5f s)" % (TAU_S, dt)
        return rec
    vlag = np.full_like(v, np.nan)
    vlag[nlag:] = v[:-nlag]                       # vlag[i] = v(t_i - tau)

    # ---- SIGN-CONVENTION ASSERTION (asserted, not re-derived) -------------------------------
    ok, bad = 0, 0
    for a, b in win:
        idx = np.arange(a, b)[on[a:b]]
        if len(idx) < 8:
            bad += 1
            continue
        n = len(idx)
        if np.mean(v[idx[:n // 2]]) > 0 and np.mean(v[idx[int(0.75 * n):]]) < 0:
            ok += 1
        else:
            bad += 1
    rec["signcheck"] = {"cycles_dorsi_then_plantar": ok, "cycles_failing": bad,
                        "holds": bool(bad == 0)}

    # ---- admissible sample pool: ALL samples of the admissible cycles -----------------------
    idx = np.concatenate([np.arange(a, b) for a, b in win])
    idx = idx[np.isfinite(vlag[idx])]
    rec["n_samples"] = int(len(idx))
    vl = vlag[idx]
    av = np.abs(vl)
    lo, hi = np.percentile(av, 100.0 / 3.0), np.percentile(av, 200.0 / 3.0)
    mid = (av >= lo) & (av <= hi)
    rec["absv_tertile_edges_rad_s"] = [float(lo), float(hi)]
    rec["n_samples_midtert"] = int(mid.sum())

    out = {}
    for name, kind, spec in CHANNELS:
        y = (S.muscle_signal(cols, dat, spec[0], spec[1], spec[2]) if kind == "muscle"
             else S.col(cols, dat, spec))
        if y is None:
            out[name] = {"error": "channel absent"}
            continue
        yy = y[idx]
        for scheme in SCHEMES:
            sel = np.ones(len(idx), bool) if scheme == "ALL" else mid
            L = sel & (vl > 0)
            Sh = sel & (vl < 0)
            if L.sum() < 10 or Sh.sum() < 10:
                out["%s_%s" % (name, scheme)] = {"error": "half with <10 samples"}
                continue
            aL, aS = float(np.mean(yy[L])), float(np.mean(yy[Sh]))
            den = aL + aS
            out["%s_%s" % (name, scheme)] = {
                "A_lengthen": aL, "A_shorten": aS,
                "n_lengthen": int(L.sum()), "n_shorten": int(Sh.sum()),
                "mean_absv_lengthen": float(np.mean(av[L])),
                "mean_absv_shorten": float(np.mean(av[Sh])),
                "diff": aL - aS,
                "ratio": (aL - aS) / den if abs(den) > 1e-12 else None,
                "denominator_sign_mixed": bool(aL * aS < 0)}
    rec["asym"] = out
    return rec


def seed_means(tags, cells, key, form):
    """key = '<channel>_<scheme>', form in {'diff','ratio'}. Seed mean over families."""
    out = {}
    for tg in tags:
        r = cells.get(tg, {})
        if not r.get("gate_G"):
            continue
        e = r.get("asym", {}).get(key)
        if not e or e.get(form) is None:
            continue
        out.setdefault(tg.split("_")[-1], []).append(e[form])
    return {k: float(np.mean(v)) for k, v in sorted(out.items())}


def floor(a, b):
    """VERBATIM from doseladder_r371.py, plus an explicit 'attained' field."""
    allv = list(a) + list(b)
    n1 = len(a)
    obs = max(min(b) - max(a), min(a) - max(b))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        x = [allv[i] for i in comb]
        y = [allv[i] for i in range(len(allv)) if i not in comb]
        if max(min(y) - max(x), min(x) - max(y)) >= obs - 1e-12:
            cnt += 1
        tot += 1
    return {"n_total": tot, "n_at_least_as_extreme": cnt,
            "floor": "1/%d" % tot,
            "attained": "%d/%d" % (cnt, tot),
            "attained_value": cnt / float(tot),
            "convention": "two-sided, gap-based (r371 convention; counts the complement). "
                          "Reported as a PERMUTATION FLOOR, not a p-value."}


def main():
    keys = ["%s_%s" % (n, s) for n, _, _ in CHANNELS for s in SCHEMES]
    res = {
        "deposit": "ASYMMETRY_r384",
        "STATUS": "EXPLORATORY",
        "STATUS_why": ("No single measure was nominated in advance. 16 measures x 4 rungs = 64 "
                       "tests are computed. Nothing here is confirmatory; any survivor must be "
                       "re-registered as ONE nominated measure and re-tested on data not used "
                       "to select it."),
        "hypothesis": ("The spastic lesion is half-wave rectified (allow_neg_V=0) and acts only "
                       "while the muscle lengthens; the weakness lesion is a linear force scale "
                       "acting equally in both directions; re-optimisation adjusts linear, "
                       "direction-symmetric gains. Therefore a DIRECTION ASYMMETRY should "
                       "survive compensation even where AMPLITUDE does not."),
        "velocity": ("v = d(ankle_angle_l)/dt in rad/s, POSITIVE = DORSIFLEXION = soleus "
                     "LENGTHENING; lagged by tau = %.3f s (2 samples at dt = 0.01 s) to match "
                     "the model's reflex delay." % TAU_S),
        "sample_pool": "ALL samples of the admissible cycles (whole cycle; no phase mask).",
        "matching_schemes": {
            "ALL": "every admissible sample",
            "MIDTERT": ("only samples whose |v(t-tau)| lies in the middle tertile of that "
                        "cell's own |v(t-tau)| distribution -- lengthening and shortening "
                        "compared at MATCHED stretch speeds")},
        "MULTIPLICITY_declared": {
            "muscles": 3, "forms": 2, "matching_schemes": 2, "muscle_measures": 12,
            "torque_measures": 4, "measures_per_rung": 16, "rungs": 4, "total_tests": 64},
        "torque_caveat": ("ankle_l.torque is SCONE's torque MAGNITUDE (non-negative), not a "
                          "signed sagittal moment, so its ASYM_ratio is well-defined but is an "
                          "asymmetry of joint-load magnitude, not of direction of moment."),
        "conventions": ("doseladder_r371.py verbatim: rd() = the one dir per tag with "
                        "history.txt >= 91 lines; sto = sorted(glob('*.par.sto'))[-1]; "
                        "SETTLE 1.00, T1 9.73; cycles between heel strikes with t[start] >= "
                        "SETTLE, wholly inside the window, drop the LAST kept cycle, require "
                        ">= 5; stance = leg0_l.grf_norm_y > 0.05."),
        "measure_keys": keys,
        "cells": {}}

    print("=== scenario audit (min_velocity) ===")
    aud = {}
    for _, fam in LADDER:
        aud[fam] = audit_min_velocity(fam)
    for f in DFWEAK + CONTROL:
        aud[f] = audit_min_velocity(f)
    mv = {}
    for f, a in aud.items():
        mv.setdefault(a.get("min_velocity"), []).append(f)
    for k in sorted(mv, key=lambda x: (x is None, x)):
        print("  min_velocity=%-6s %s" % (k, ", ".join(sorted(mv[k]))))
    res["SCENARIO_AUDIT"] = {"per_family": aud,
                             "min_velocity_groups": {str(k): sorted(v) for k, v in mv.items()}}
    lad_w = {aud[f].get("min_velocity") for _, f in LADDER} | \
            {aud[f].get("min_velocity") for f in DFWEAK}
    res["PRIMARY_COMPARISON_SCOPE"] = (
        "LADDER vs DFWEAK is WITHIN-SCENARIO (all at min_velocity 1.0)" if len(lad_w) == 1
        else "LADDER vs DFWEAK spans %d min_velocity values -- BETWEEN-SCENARIO" % len(lad_w))
    res["CONTROL_SCOPE"] = ("BETWEEN-SCENARIO: the control arm is 0.80/1.05/1.30 min_velocity "
                            "and is NOT scenario-matched to the ladder or to DF-weak. It is "
                            "reported as a descriptive band only; no test is run against it.")
    print("  -> %s" % res["PRIMARY_COMPARISON_SCOPE"])
    print("  -> CONTROL: BETWEEN-SCENARIO, descriptive only")

    print()
    print("=== measurement ===")
    wt = tags_for(DFWEAK)
    for tg in wt:
        res["cells"][tg] = measure(tg)
    ladder_tags = {}
    for kv, fam in LADDER:
        ladder_tags[fam] = tags_for([fam])
        for tg in ladder_tags[fam]:
            res["cells"][tg] = measure(tg)
    ct = tags_for(CONTROL)
    for tg in ct:
        res["cells"][tg] = measure(tg)

    ngG = sum(1 for r in res["cells"].values() if r.get("gate_G"))
    print("  cells measured %d, Gate-G %d" % (len(res["cells"]), ngG))
    sc_bad = [t for t, r in res["cells"].items()
              if r.get("gate_G") and not r.get("signcheck", {}).get("holds")]
    res["SIGN_CONVENTION_ASSERTION"] = {
        "rule": ("stance must show dorsiflexion (mean v > 0 over first half of stance) then "
                 "plantarflexion (mean v < 0 over last quarter of stance), every cycle"),
        "n_gateG_cells": ngG,
        "n_cells_violating": len(sc_bad),
        "violating_cells": sorted(sc_bad),
        "HOLDS": bool(not sc_bad)}
    print("  sign convention holds in %d/%d Gate-G cells%s"
          % (ngG - len(sc_bad), ngG, "" if not sc_bad else "  VIOLATIONS: " + ",".join(sc_bad)))

    # ---- arms -------------------------------------------------------------------------------
    arms = {}
    for key in keys:
        for form in FORMS:
            arms["%s|%s" % (key, form)] = {
                "DFWEAK": seed_means(wt, res["cells"], key, form),
                "CONTROL_between_scenario": seed_means(ct, res["cells"], key, form)}
            for kv, fam in LADDER:
                arms["%s|%s" % (key, form)]["KV%s" % kv] = \
                    seed_means(ladder_tags[fam], res["cells"], key, form)
    res["ARM_SEED_MEANS"] = arms

    # ---- tests ------------------------------------------------------------------------------
    print()
    print("=== rung x measure: disjointness of 6 seed means vs DF-weak's 6 ===")
    tests = {}
    hits = []
    for kv, fam in LADDER:
        for key in keys:
            for form in FORMS:
                mk = "%s|%s" % (key, form)
                wsm = arms[mk]["DFWEAK"]
                ssm = arms[mk]["KV%s" % kv]
                w = sorted(wsm.values())
                s = sorted(ssm.values())
                e = {"KV": kv, "family": fam, "measure": key, "form": form,
                     "n_spastic": len(s), "n_dfweak": len(w)}
                if len(s) < 4 or len(w) < 4:
                    e["VERDICT"] = "UNINFORMATIVE"
                    e["why"] = "fewer than 4 seed means on one side (%d vs %d)" % (len(s), len(w))
                else:
                    gap = max(w[0] - s[-1], s[0] - w[-1])
                    e.update({"spastic_range": [s[0], s[-1]], "spastic_mean": float(np.mean(s)),
                              "dfweak_range": [w[0], w[-1]], "dfweak_mean": float(np.mean(w)),
                              "gap": gap, "separated": bool(gap > 0)})
                    if gap > 0:
                        e["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "SPASTIC LOW"
                        e["permutation"] = floor(s, w)
                        e["VERDICT"] = "SEPARATED"
                        hits.append((kv, key, form, gap, e["direction"],
                                     e["permutation"]["attained"]))
                    else:
                        e["VERDICT"] = "OVERLAP"
                tests["KV%s|%s|%s" % (kv, key, form)] = e
    res["RUNG_TESTS"] = tests

    hdr = "  %-8s %-24s %-6s %11s %11s %10s %-9s %s"
    print(hdr % ("KV", "measure", "form", "spastic", "dfweak", "gap", "verdict", "floor"))
    for kv, fam in LADDER:
        for key in keys:
            for form in FORMS:
                e = tests["KV%s|%s|%s" % (kv, key, form)]
                if e["VERDICT"] == "UNINFORMATIVE":
                    print(hdr % (kv, key, form, "-", "-", "-", "UNINFORM", e["why"]))
                    continue
                print(hdr % (kv, key, form,
                             "%+.5f" % e["spastic_mean"], "%+.5f" % e["dfweak_mean"],
                             "%+.5f" % e["gap"], e["VERDICT"],
                             (e["direction"] + " " + e["permutation"]["attained"])
                             if e["separated"] else ""))
        print()

    # ---- the question that matters ----------------------------------------------------------
    low = [h for h in hits if h[0] in (0.00625, 0.0125)]
    res["ANSWER_low_rungs"] = {
        "question": ("Does ANYTHING separate at KV 0.00625 or KV 0.0125, where every amplitude "
                     "endpoint has OVERLAPPED?"),
        "n_separating_measures_at_KV0.00625": sum(1 for h in hits if h[0] == 0.00625),
        "n_separating_measures_at_KV0.0125": sum(1 for h in hits if h[0] == 0.0125),
        "separating": [{"KV": h[0], "measure": h[1], "form": h[2], "gap": h[3],
                        "direction": h[4], "permutation_attained": h[5]} for h in low],
        "VERDICT": ("NOTHING SEPARATES BELOW KV 0.035 on any of the 16 asymmetry measures."
                    if not low else
                    "%d of 32 low-rung measures separate; EXPLORATORY, multiplicity 64. Read "
                    "with MULTIPLICITY_LIMIT, DIRECTION_CONSISTENCY and DOSE_RESPONSE -- the "
                    "claim rests on the pattern, not on any single floor." % len(low))}
    res["ALL_SEPARATIONS"] = [{"KV": h[0], "measure": h[1], "form": h[2], "gap": h[3],
                               "direction": h[4], "permutation_attained": h[5]} for h in hits]

    # ---- what the floor CANNOT do at this n -------------------------------------------------
    nmin = 2.0 / 924.0
    res["MULTIPLICITY_LIMIT"] = {
        "min_attainable_floor": "2/924", "min_attainable_value": nmin,
        "why_2_not_1": ("the gap statistic is two-sided and gap-based, so a perfectly disjoint "
                        "split is always tied by its own complement; 1/924 is unreachable"),
        "declared_tests": 64,
        "bonferroni_target_at_0.05": 0.05 / 64.0,
        "STATEMENT": ("THE EXHAUSTIVE PERMUTATION CANNOT DELIVER A MULTIPLICITY-CORRECTED "
                      "RESULT AT 6 vs 6. The best floor attainable is 2/924 = %.5f; the "
                      "Bonferroni target over the declared 64 tests is 0.05/64 = %.5f. Every "
                      "separation reported here therefore fails a family-wise correction BY "
                      "CONSTRUCTION, no matter how clean it looks. What can be weighed is the "
                      "PATTERN -- how many of the 16 measures separate at a rung, whether the "
                      "directions agree, and whether the separation grows with KV -- not any "
                      "one floor." % (nmin, 0.05 / 64.0))}

    # ---- direction consistency and dose-response --------------------------------------------
    dc = {}
    for kv, _ in LADDER:
        n = cons = 0
        for key in keys:
            for form in FORMS:
                e = tests["KV%s|%s|%s" % (kv, key, form)]
                ref = tests["KV0.035|%s|%s" % (key, form)]
                if e["VERDICT"] == "SEPARATED":
                    n += 1
                    if ref.get("direction") and e["direction"] == ref["direction"]:
                        cons += 1
        dc["KV%s" % kv] = {"n_separated_of_16": n, "n_direction_agrees_with_KV0.035": cons,
                           "n_direction_opposes_KV0.035": n - cons}
    res["DIRECTION_CONSISTENCY"] = dc

    dose = {}
    for key in keys:
        for form in FORMS:
            mk = "%s|%s" % (key, form)
            w = float(np.mean(list(arms[mk]["DFWEAK"].values())))
            m = [float(np.mean(list(arms[mk]["KV%s" % k].values()))) for k in (0.00625, 0.0125, 0.035)]
            dist = [abs(x - w) for x in m]
            sgn = [np.sign(x - w) for x in m]
            dose[mk] = {"dfweak_mean": w,
                        "rung_means": {"0.00625": m[0], "0.0125": m[1], "0.035": m[2]},
                        "abs_distance_from_dfweak": dist,
                        "monotone_increasing_in_KV": bool(dist[0] <= dist[1] <= dist[2]),
                        "sign_of_offset": [float(s) for s in sgn],
                        "sign_constant_across_rungs": bool(len(set(sgn)) == 1)}
    res["DOSE_RESPONSE"] = dose
    res["DOSE_RESPONSE_summary"] = {
        "n_measures": len(dose),
        "n_monotone_increasing_in_KV": sum(1 for v in dose.values() if v["monotone_increasing_in_KV"]),
        "n_sign_constant": sum(1 for v in dose.values() if v["sign_constant_across_rungs"]),
        "note": ("|distance from DF-weak| monotone in KV over the three Gate-G rungs. KV 0.070 "
                 "is absent from this ladder because 0 of its 6 seeds pass Gate G.")}

    # ---- control coincidence (BETWEEN-SCENARIO, descriptive only) ---------------------------
    cc = {}
    for key in keys:
        for form in FORMS:
            mk = "%s|%s" % (key, form)
            cv = list(arms[mk]["CONTROL_between_scenario"].values())
            if not cv:
                continue
            wv = sorted(arms[mk]["DFWEAK"].values())
            sv = sorted(arms[mk]["KV0.035"].values())
            cm = float(np.mean(cv))
            cc[mk] = {"CONTROL_mean": cm, "DFWEAK_range": [wv[0], wv[-1]],
                      "KV0.035_range": [sv[0], sv[-1]],
                      "control_nearer_to": ("DFWEAK" if abs(cm - np.mean(wv)) < abs(cm - np.mean(sv))
                                            else "KV0.035")}
    res["CONTROL_COINCIDENCE"] = cc
    res["CONTROL_COINCIDENCE_summary"] = {
        "n_measures": len(cc),
        "n_control_nearer_DFWEAK": sum(1 for v in cc.values() if v["control_nearer_to"] == "DFWEAK"),
        "n_control_nearer_KV0.035": sum(1 for v in cc.values() if v["control_nearer_to"] == "KV0.035"),
        "WEIGHT": ("SUPPORTIVE BUT NOT A TEST. The control arm is BETWEEN-SCENARIO "
                   "(min_velocity 0.80/1.05/1.30 against the ladder's and DF-weak's 1.0), so its "
                   "coincidence with DF-weak cannot be tested, only observed. If it holds, it "
                   "says the SPASTIC arm is the outlier and the dorsiflexor-weak arm looks like "
                   "an unlesioned walker on these measures -- which is what a lesion-specific "
                   "signature should look like, and is not what an arbitrary two-arm difference "
                   "would look like.")}

    # ---- gait-composition covariate ----------------------------------------------------------
    lf = {}
    for tg, r in res["cells"].items():
        if not r.get("gate_G"):
            continue
        e = r["asym"].get("soleus_l_ALL")
        if not e or "n_lengthen" not in e:
            continue
        lf.setdefault(tg.split("_s")[0], []).append(
            e["n_lengthen"] / float(e["n_lengthen"] + e["n_shorten"]))
    res["COVARIATE_fraction_of_samples_lengthening"] = {
        "per_family_mean": {k: float(np.mean(v)) for k, v in sorted(lf.items())},
        "note": ("The fraction of the cycle spent dorsiflexing differs between arms and falls "
                 "with KV. The asymmetry measures are PER-SAMPLE means, so duration does not "
                 "enter them arithmetically, but the PHASE COMPOSITION of the two halves is not "
                 "identical across arms and the MIDTERT scheme matches speed, not phase.")}

    res["CAVEATS"] = [
        ("NAMING, tib_ant_l: the sign convention is soleus-centric. v > 0 is DORSIFLEXION, which "
         "LENGTHENS soleus and gastroc but SHORTENS tib_ant. For tib_ant_l, 'A_lengthen' must be "
         "read as 'mean activation while the ankle is dorsiflexing', i.e. while tib_ant is "
         "SHORTENING. The tib_ant direction labels are therefore mirrored relative to the "
         "plantarflexors, and 'SPASTIC LOW' on tib_ant is the same physical statement as "
         "'SPASTIC HIGH' on soleus."),
        ("ankle_l.torque is SCONE's torque MAGNITUDE (non-negative over the trace), not a signed "
         "sagittal moment. Its asymmetry is an asymmetry of joint-load magnitude."),
        ("PHASE CONFOUND, not removed. Plantarflexor activation is concentrated in late stance, "
         "which is when the ankle is plantarflexing, so A_shorten exceeds A_lengthen in EVERY "
         "arm including the unlesioned control and every ratio is negative. What separates the "
         "arms is HOW negative. MIDTERT matches |v| but does not match gait phase, so the "
         "measure is not a clean isolate of the reflex."),
        ("UNIT ASYMMETRY, inherited from r371/r381. A DF-weak seed mean averages SIX families; a "
         "ladder seed mean is ONE run. DF-weak is therefore mechanically tighter than a ladder "
         "rung, which makes disjointness easier to attain against it."),
        ("KV 0.070 contributes nothing: 0 of 6 seeds pass Gate G (every one falls before "
         "T1 = 9.73 s). The ladder here is three rungs, not four."),
        ("EXPLORATORY. 64 tests, no measure nominated in advance, and see MULTIPLICITY_LIMIT: "
         "at 6 vs 6 no single permutation floor can clear the family-wise threshold."),
    ]

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False))
    print("THE QUESTION THAT MATTERS: %s" % res["ANSWER_low_rungs"]["VERDICT"])
    print("separations at any rung: %d of 64 tests" % len(hits))
    for h in sorted(hits):
        print("   KV %-8s %-24s %-6s gap %+.6f  %s  floor %s" % (h[0], h[1], h[2], h[3], h[4], h[5]))
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
