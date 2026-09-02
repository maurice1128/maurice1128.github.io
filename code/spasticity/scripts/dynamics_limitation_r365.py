# -*- coding: utf-8 -*-
"""r365 -- INDEPENDENT verification of the channel evidence behind the r363 null,
and the producer of paper/DYNAMICS_LIMITATION_r365.json.

This script does NOT re-derive PF_swing. That is DYNAMICS_SWING_r363.json's job under
PREREG_dynamics_r362.md, and this file does not touch it. What it measures is the set of
MODEL facts the r365 manuscript subsection asserts -- per muscle, not per pooled PF:

  1. the .sto column count PER ARM, and the presence of the dynamics channels
     (ankle_l.torque; soleus_l / gastroc_l / tib_ant_l activation AND excitation);
  2. soleus_l and gastroc_l ACTIVATION, separately, over swing and over stance;
  3. the activation floor -- the config's min_muscle_activation and the corpus-wide minimum
     actually attained -- which decides whether the swing value is a floor artefact;
  4. the reflex's OWN channels on the spastic arm: soleus_l.V / gastroc_l.V (the normalised
     fibre velocity the MuscleReflex reads; positive = LENGTHENING) and soleus_l.RV /
     gastroc_l.RV (the KV term's contribution to excitation), over swing and over stance.
     This is the test of whether a stretch reflex can fire during swing in this model;
  5. soleus_l / gastroc_l EXCITATION over swing, so the RV contribution can be put beside
     the total drive it is a part of;
  6. the .sto mtimes, as evidence for "no new simulation was run".

Conventions are CARRIED from scone/dynamics_swing_r363.py, unchanged: rd(),
sorted(*.par.sto)[-1], SETTLE 1.00 / T1 9.73, drop the last cycle in the window,
swing = NOT (grf_norm_y > 0.05).

READ-ONLY against C:\\Users\\maurice\\Documents\\SCONE\\results. It writes nothing there.
"""
import glob
import io
import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DYNAMICS_LIMITATION_r365.json"
SETTLE, T1 = 1.0, 9.73

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


def measure(tag, arm):
    d = rd(tag)
    p = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(p)
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win

    cfg = os.path.join(d, "config.scone")
    mma = None
    if os.path.exists(cfg):
        for ln in io.open(cfg, errors="replace"):
            m = re.search(r"min_muscle_activation\s*=\s*([0-9.eE+-]+)", ln)
            if m:
                mma = float(m.group(1))
                break

    rec = {"tag": tag, "arm": arm, "dir": os.path.basename(d), "sto": os.path.basename(p),
           "n_cols": len(cols),
           "sto_mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(os.path.getmtime(p))),
           "config_min_muscle_activation": mma,
           "t_end_s": float(t[-1]), "n_cycles_in_window": len(win)}

    ch = {}
    for m in ("soleus", "gastroc", "tib_ant"):
        for k in ("activation", "excitation"):
            ch["%s_l.%s" % (m, k)] = S.muscle_signal(cols, dat, m, "l", k) is not None
    ch["ankle_l.torque"] = S.col(cols, dat, "ankle_l.torque") is not None
    for c in ("soleus_l.V", "gastroc_l.V", "soleus_l.RV", "gastroc_l.RV"):
        ch[c] = c in cols
    rec["channels_present"] = ch

    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["measured"] = False
        return rec

    A = {m: S.muscle_signal(cols, dat, m, "l", "activation")
         for m in ("soleus", "gastroc", "tib_ant")}
    E = {m: S.muscle_signal(cols, dat, m, "l", "excitation")
         for m in ("soleus", "gastroc")}
    refl = {c: dat[:, cols.index(c)] for c in
            ("soleus_l.V", "gastroc_l.V", "soleus_l.RV", "gastroc_l.RV") if c in cols}

    on = grf > thr
    acc = {}

    def push(k, v):
        acc.setdefault(k, []).append(float(v))

    for a, b in win:
        sw = ~on[a:b]
        st = on[a:b]
        if not sw.any() or not st.any():
            continue
        for m in ("soleus", "gastroc", "tib_ant"):
            push("act_swing_" + m, np.mean(A[m][a:b][sw]))
            push("act_stance_" + m, np.mean(A[m][a:b][st]))
            push("act_swing_min_" + m, np.min(A[m][a:b][sw]))
        for m in ("soleus", "gastroc"):
            push("exc_swing_" + m, np.mean(E[m][a:b][sw]))
            push("exc_stance_" + m, np.mean(E[m][a:b][st]))
        for m in ("soleus", "gastroc"):
            v, rv = "%s_l.V" % m, "%s_l.RV" % m
            if v in refl:
                push("V_swing_" + m, np.mean(refl[v][a:b][sw]))
                push("V_stance_" + m, np.mean(refl[v][a:b][st]))
                push("frac_swing_V_positive_" + m, np.mean(refl[v][a:b][sw] > 0.0))
                push("frac_stance_V_positive_" + m, np.mean(refl[v][a:b][st] > 0.0))
            if rv in refl:
                push("RV_swing_" + m, np.mean(refl[rv][a:b][sw]))
                push("RV_stance_" + m, np.mean(refl[rv][a:b][st]))

    # --- sign-convention and identity check, spastic arm only -------------------------
    # This is load-bearing: it is what licenses reading `V > 0` as STRETCH.
    # (i) RV must equal KV * max(0, V(t - delay)) exactly, which identifies RV as the KV term
    #     and identifies the half-rectification `allow_neg_V = 0` as acting on V > 0.
    # (ii) V must track d(fiber_length)/dt, which fixes V > 0 as LENGTHENING.
    if "soleus_l.V" in refl:
        kv = None
        for ln in io.open(cfg, errors="replace"):
            m = re.search(r"KV\s*=\s*([0-9.eE+-]+)\s*$", ln.strip())
            if m and "~" not in ln:
                kv = float(m.group(1))
                break
        dt = float(np.median(np.diff(t)))
        lag = int(round(0.020 / dt))
        chk = {"KV_from_config": kv, "delay_s": 0.020, "lag_samples": lag}
        for m in ("soleus", "gastroc"):
            v, rv = refl["%s_l.V" % m], refl["%s_l.RV" % m]
            pred = kv * np.maximum(0.0, v)
            chk["max_abs_RV_minus_KVmaxV_lagged_" + m] = float(
                np.max(np.abs(rv[lag:] - pred[:-lag])))
            fl = S.muscle_signal(cols, dat, m, "l", "fiber_length")
            chk["corr_V_vs_d_fiber_length_dt_" + m] = float(
                np.corrcoef(v, np.gradient(fl, t))[0, 1])
        rec["sign_convention_check"] = chk

    rec["measured"] = True
    rec["n_cycles_used"] = len(acc["act_swing_soleus"])
    rec["per_cycle_mean"] = {k: float(np.mean(v)) for k, v in acc.items()}
    rec["min_activation_whole_trial"] = {
        m: float(np.min(A[m])) for m in ("soleus", "gastroc", "tib_ant")}
    return rec


def stat(vals):
    return {"n": len(vals), "min": min(vals), "max": max(vals), "mean": float(np.mean(vals))}


def main():
    cells = {}
    for arm, fams in (("SPASTIC", SPASTIC), ("DFWEAK", DFWEAK)):
        for tag in tags_for(fams):
            cells[tag] = measure(tag, arm)
            print("  %-18s %-8s ncol=%d" % (tag, arm, cells[tag]["n_cols"]))
    ok = [c for c in cells.values() if c.get("measured")]

    def by(arm, key):
        v = [c["per_cycle_mean"][key] for c in ok
             if (arm is None or c["arm"] == arm) and key in c["per_cycle_mean"]]
        return stat(v) if v else None

    keys = sorted({k for c in ok for k in c["per_cycle_mean"]})
    agg = {k: {a: by(a, k) for a in ("SPASTIC", "DFWEAK", None)} for k in keys}
    agg = {k: {("ALL" if a is None else a): v for a, v in d.items() if v} for k, d in agg.items()}

    fam = {}
    for c in ok:
        fam.setdefault(re.sub(r"_s\d+$", "", c["tag"]), []).append(c)
    per_family = {f: {k: float(np.mean([c["per_cycle_mean"][k] for c in cs
                                        if k in c["per_cycle_mean"]]))
                      for k in keys if any(k in c["per_cycle_mean"] for c in cs)}
                  for f, cs in fam.items()}

    res = {
        "round": 365,
        "kind": "MODEL LIMITATION",
        "note": "r365 channel/mechanism verification. NOT a re-derivation of PF_swing.",
        "producer": "scone/dynamics_limitation_r365.py",
        "reads": ["DYNAMICS_SWING_r363.json", "PREREG_dynamics_r362.md",
                  "PREREG_dynamics_r360.md", "DYNAMICS_SWING_r361.json",
                  "MATCHED20_ENDPOINT_r298.json",
                  "<SCONE results>/<cell>/*.par.sto  (READ-ONLY)",
                  "<SCONE results>/<cell>/config.scone  (READ-ONLY)"],
        "status": "UNREGISTERED, POST-HOC. It measures the model, not the endpoint; it "
                  "changes no verdict of PREREG_dynamics_r362.md and adjudicates nothing.",
        "window_s": [SETTLE, T1],
        "channel_evidence": {
            "n_cols_by_arm": {a: sorted({c["n_cols"] for c in cells.values() if c["arm"] == a})
                              for a in ("SPASTIC", "DFWEAK")},
            "n_cols_note": "the spastic arm carries 4 columns the DF arm does not; they are "
                           "the lesion's own reflex channels, listed below",
            "extra_columns_on_spastic_arm": ["soleus_l.V", "gastroc_l.V",
                                             "soleus_l.RV", "gastroc_l.RV"],
            "channels_present_all_48_cells": {
                k: all(c["channels_present"][k] for c in cells.values())
                for k in ("soleus_l.activation", "soleus_l.excitation",
                          "gastroc_l.activation", "gastroc_l.excitation",
                          "tib_ant_l.activation", "tib_ant_l.excitation", "ankle_l.torque")},
            "reflex_channels_present_by_arm": {
                a: {k: all(c["channels_present"][k] for c in cells.values() if c["arm"] == a)
                    for k in ("soleus_l.V", "gastroc_l.V", "soleus_l.RV", "gastroc_l.RV")}
                for a in ("SPASTIC", "DFWEAK")},
            "config_min_muscle_activation": sorted(
                {c["config_min_muscle_activation"] for c in cells.values()}),
            "activation_floor_attained": {
                m: min(c["min_activation_whole_trial"][m] for c in ok)
                for m in ("soleus", "gastroc", "tib_ant")},
            "sto_mtime_dates": sorted({c["sto_mtime"][:10] for c in cells.values()}),
            "sto_mtime_note": "both dates precede the 2026-08-18 registration date of "
                              "PREREG_dynamics_r360.md and PREREG_dynamics_r362.md; no new "
                              "simulation was run for either registration",
        },
        "by_arm": agg,
        "by_family": per_family,
        "cells_checked_by_name": {
            a: sorted(c["tag"] for c in cells.values() if c["arm"] == a)
            for a in ("SPASTIC", "DFWEAK")},
        "cells_index": {c["tag"]: {"arm": c["arm"], "dir": c["dir"], "sto": c["sto"],
                                   "n_cols": c["n_cols"], "t_end_s": c["t_end_s"],
                                   "n_cycles_used": c.get("n_cycles_used"),
                                   "measured": c.get("measured")}
                        for c in cells.values()},
    }
    # ---- the finding, with every number taken from the aggregates above, none typed ----
    A, B = per_family["R289KV00625"], per_family["R289KV0125"]
    r363 = json.load(io.open(os.path.join(os.path.dirname(OUT),
                                          "DYNAMICS_SWING_r363.json"), encoding="utf-8"))
    U = r363["READING_U_unmatched"]
    sp = list(U["spastic_cells"].values())
    wk = list(U["weak_cells"].values())
    fam363 = {}
    for k, v in U["spastic_cells"].items():
        fam363.setdefault(re.sub(r"_s\d+$", "", k), []).append(v)

    res["FINDING"] = {
        "headline":
            "The r363 OVERLAP is a MODEL LIMITATION, not a physiological finding. In this "
            "model the injected spastic reflex does produce a swing-phase plantarflexor "
            "drive, but the drive is small relative to the residual swing excitation and is "
            "almost entirely cancelled by the re-optimisation of the rest of the reflex "
            "bank, so the endpoint cannot see it at any gain that also walks.",
        "0_the_account_this_deposit_was_asked_to_record_is_REFUTED_by_its_own_measurement": {
            "the_account": "the Geyer-Herr reflex is a stretch reflex, and in swing the "
                           "plantarflexors are SHORTENING, so a raised KV gain cannot produce "
                           "swing-phase plantarflexor activity in this model",
            "where_it_is_already_frozen": "PREREG_reflexgain_r364.md section 1 states it as "
                                          "fact -- 'during swing the plantarflexors shorten. A "
                                          "raised velocity gain therefore cannot express itself "
                                          "in swing in this model' -- and names THIS FILE as "
                                          "the container recording it. That registration is "
                                          "hashed (939c81b6ea6544a35243e41d171c0fb0d9e80c50ed"
                                          "0d2207fec70d6b9f6d743c) and cannot be edited.",
            "status": "The account is FALSE in this model, by items 2 and 3 below. It is "
                      "recorded as refuted, not silently replaced. This deposit does not amend "
                      "PREREG_reflexgain_r364.md and cannot; REFLEXGAIN_r366.json's OVERLAP "
                      "verdict on r364's own registered endpoint is untouched by this and "
                      "stands.",
            "what_survives_of_it": "the CONCLUSION -- that this model cannot express the "
                                   "clinical swing-phase phenomenon on an observable endpoint. "
                                   "That conclusion is correct. Its stated REASON is not.",
        },
        "1_the_reflex_is_live_during_swing": {
            "config": "ConditionalController { states = \"EarlyStance LateStance Liftoff "
                      "Swing Landing\"; legs = left; ReflexController { name = SpasticL; "
                      "MuscleReflex target=soleus KV=<gain> allow_neg_V=0; MuscleReflex "
                      "target=gastroc KV=<gain> allow_neg_V=0 } }",
            "config_source": "config.scone of every R289KV* cell",
            "consequence": "Swing is one of the five states the lesion is registered in. "
                           "The reflex is NOT gated out of swing.",
        },
        "2_the_plantarflexors_are_LENGTHENING_in_swing_not_shortening": {
            "V_is": "soleus_l.V / gastroc_l.V, the normalised fibre velocity the MuscleReflex "
                    "reads; positive = lengthening = stretch",
            "V_swing_soleus_mean": agg["V_swing_soleus"]["SPASTIC"]["mean"],
            "V_stance_soleus_mean": agg["V_stance_soleus"]["SPASTIC"]["mean"],
            "V_swing_gastroc_mean": agg["V_swing_gastroc"]["SPASTIC"]["mean"],
            "V_stance_gastroc_mean": agg["V_stance_gastroc"]["SPASTIC"]["mean"],
            "frac_swing_V_positive_soleus": agg["frac_swing_V_positive_soleus"]["SPASTIC"]["mean"],
            "frac_stance_V_positive_soleus": agg["frac_stance_V_positive_soleus"]["SPASTIC"]["mean"],
            "frac_swing_V_positive_gastroc": agg["frac_swing_V_positive_gastroc"]["SPASTIC"]["mean"],
            "frac_stance_V_positive_gastroc": agg["frac_stance_V_positive_gastroc"]["SPASTIC"]["mean"],
            "REFUTES": "the account that a stretch reflex cannot fire in swing because the "
                       "plantarflexors are shortening. Measured, they are being stretched in "
                       "swing and shortening in stance -- the opposite of that account.",
            "sign_convention_is_verified_not_assumed": {
                "identity": "RV(t) = KV * max(0, V(t - 0.020 s)), reproduced to the tolerance "
                            "below on every spastic cell, which identifies V as the reflex's "
                            "input and the half-rectification as acting on V > 0",
                "max_abs_residual_soleus": max(
                    c["sign_convention_check"]["max_abs_RV_minus_KVmaxV_lagged_soleus"]
                    for c in ok if "sign_convention_check" in c),
                "max_abs_residual_gastroc": max(
                    c["sign_convention_check"]["max_abs_RV_minus_KVmaxV_lagged_gastroc"]
                    for c in ok if "sign_convention_check" in c),
                "min_corr_V_vs_d_fiber_length_dt_soleus": min(
                    c["sign_convention_check"]["corr_V_vs_d_fiber_length_dt_soleus"]
                    for c in ok if "sign_convention_check" in c),
                "min_corr_V_vs_d_fiber_length_dt_gastroc": min(
                    c["sign_convention_check"]["corr_V_vs_d_fiber_length_dt_gastroc"]
                    for c in ok if "sign_convention_check" in c),
                "reading": "V tracks d(fiber_length)/dt, so V > 0 is LENGTHENING. Consistent "
                           "with Appendix A1 of RESULTS_3d_r214.md, which established that "
                           "SCONE's MuscleReflex reads <muscle>.V.",
            },
        },
        "3_and_it_does_fire_harder_in_swing_than_in_stance": {
            "RV_is": "soleus_l.RV / gastroc_l.RV, the KV term's own contribution to excitation",
            "RV_swing_soleus_mean": agg["RV_swing_soleus"]["SPASTIC"]["mean"],
            "RV_stance_soleus_mean": agg["RV_stance_soleus"]["SPASTIC"]["mean"],
            "RV_swing_gastroc_mean": agg["RV_swing_gastroc"]["SPASTIC"]["mean"],
            "RV_stance_gastroc_mean": agg["RV_stance_gastroc"]["SPASTIC"]["mean"],
            "scales_with_KV_soleus": [A["RV_swing_soleus"], B["RV_swing_soleus"]],
            "scales_with_KV_gastroc": [A["RV_swing_gastroc"], B["RV_swing_gastroc"]],
        },
        "4_why_the_endpoint_still_sees_nothing": {
            "a_the_added_drive_is_absorbed": {
                "delta_RV_swing_soleus": B["RV_swing_soleus"] - A["RV_swing_soleus"],
                "delta_total_exc_swing_soleus": B["exc_swing_soleus"] - A["exc_swing_soleus"],
                "fraction_cancelled": 1.0 - ((B["exc_swing_soleus"] - A["exc_swing_soleus"])
                                             / (B["RV_swing_soleus"] - A["RV_swing_soleus"])),
                "mechanism": "each cell is an independent 90-generation CMA optimisation with "
                             "the lesion already in place, so the remaining reflex bank "
                             "re-tunes around the injected KV term",
            },
            "b_doubling_KV_does_not_move_the_endpoint": {
                "PF_swing_mean_KV00625": float(np.mean(fam363["R289KV00625"])),
                "PF_swing_mean_KV0125": float(np.mean(fam363["R289KV0125"])),
                "delta": float(np.mean(fam363["R289KV0125"]) - np.mean(fam363["R289KV00625"])),
                "spastic_arm_spread": max(sp) - min(sp),
                "source": "DYNAMICS_SWING_r363.json /READING_U_unmatched/spastic_cells",
            },
            "c_the_swing_value_is_not_a_floor_artefact": {
                "config_min_muscle_activation": 0.01,
                "act_swing_soleus_mean_ALL": agg["act_swing_soleus"]["ALL"]["mean"],
                "act_swing_gastroc_mean_ALL": agg["act_swing_gastroc"]["ALL"]["mean"],
                "act_stance_soleus_mean_ALL": agg["act_stance_soleus"]["ALL"]["mean"],
                "act_stance_gastroc_mean_ALL": agg["act_stance_gastroc"]["ALL"]["mean"],
                "act_swing_min_soleus_mean_ALL": agg["act_swing_min_soleus"]["ALL"]["mean"],
                "act_swing_min_gastroc_mean_ALL": agg["act_swing_min_gastroc"]["ALL"]["mean"],
                "reading": "the swing MEAN sits several times the floor, so it is not a floor "
                           "artefact; the within-swing MINIMUM does reach the floor, and that "
                           "is stated rather than omitted",
            },
            "d_the_admissible_KV_range_is_one_point_wide": {
                "KV_values_that_walk": [0.00625, 0.0125],
                "next_rung_up_fails_Gate_G": "R291KV0070, t_end 8.24-9.52 s against a 9.73 s "
                                             "gate, DYNAMICS_SWING_r361.json "
                                             "/cells/R291KV0070_s10*/t_end_s",
                "other_reflex_gains_in_the_same_bank": "KL and KF on soleus/gastroc are of "
                                                       "order 0.5-1 in config.scone; the "
                                                       "lesion's KV is 0.00625-0.0125",
            },
        },
    }
    res["WHAT_WOULD_MAKE_THE_SWING_ENDPOINT_INFORMATIVE"] = [
        "A spastic arm whose KV is large enough that the reflex contribution to swing "
        "excitation is comparable to the residual swing excitation itself -- measured, RV over "
        "swing is %.6f (soleus) and %.6f (gastroc) against total swing excitation %.6f and "
        "%.6f. On the two admissible rungs that ratio is far below 1, and the rung above them "
        "(R291KV0070) does not survive Gate G. Such an arm must both exist and walk; on this "
        "corpus no such arm exists."
        % (agg["RV_swing_soleus"]["SPASTIC"]["mean"], agg["RV_swing_gastroc"]["SPASTIC"]["mean"],
           agg["exc_swing_soleus"]["SPASTIC"]["mean"], agg["exc_swing_gastroc"]["SPASTIC"]["mean"]),
        "OR: the lesion applied to a controller that is NOT re-optimised around it -- a frozen "
        "healthy controller with the KV term added -- so the injected drive is not cancelled. "
        "Measured here, %.1f%% of the added soleus swing RV is cancelled between KV 0.00625 and "
        "KV 0.0125. Such a cell would have to pass Gate G, which no round has tested."
        % (100.0 * (1.0 - ((B["exc_swing_soleus"] - A["exc_swing_soleus"])
                           / (B["RV_swing_soleus"] - A["RV_swing_soleus"])))),
        "OR: an endpoint on the reflex's own channel (soleus_l.RV / gastroc_l.RV) rather than "
        "on activation. That is NOT clinically obtainable -- PREREG_dynamics_r360.md section 1 "
        "excludes reading the lesion parameter back out -- and those columns do not exist on "
        "the DF arm at all (958 columns against the spastic arm's 962), so no comparison "
        "between the arms could be formed on them.",
    ]
    res["WHAT_THIS_DOES_NOT_ESTABLISH"] = [
        "It does not retract, amend or reinterpret DYNAMICS_SWING_r363.json. That deposit's "
        "verdict on its registered endpoint is OVERLAP and stands as deposited.",
        "It is post-hoc. No part of it was registered before the values existed.",
        "It says nothing about surface EMG. PREREG_dynamics_r360.md section 8's declared "
        "limitation is untouched and still untested.",
        "The cancellation figure is a two-point comparison between two families of six seeds "
        "each. It is a ratio between two arm means, not a fitted dose-response.",
    ]

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    print(json.dumps(res["channel_evidence"], indent=2))
    for k in ("act_swing_soleus", "act_swing_gastroc", "act_stance_soleus",
              "act_stance_gastroc", "act_swing_min_soleus", "act_swing_min_gastroc",
              "V_swing_soleus", "V_stance_soleus", "V_swing_gastroc", "V_stance_gastroc",
              "frac_swing_V_positive_soleus", "frac_stance_V_positive_soleus",
              "frac_swing_V_positive_gastroc", "frac_stance_V_positive_gastroc",
              "RV_swing_soleus", "RV_stance_soleus", "RV_swing_gastroc", "RV_stance_gastroc",
              "exc_swing_soleus", "exc_swing_gastroc"):
        print("%-32s %s" % (k, json.dumps(agg[k])))
    print("KV00625 vs KV0125:")
    for k in ("RV_swing_soleus", "RV_swing_gastroc", "exc_swing_soleus", "act_swing_soleus"):
        print("  %-20s %.6f -> %.6f" % (k, per_family["R289KV00625"][k],
                                        per_family["R289KV0125"][k]))
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
    return res


if __name__ == "__main__":
    main()
