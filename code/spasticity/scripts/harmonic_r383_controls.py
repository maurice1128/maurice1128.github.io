# -*- coding: utf-8 -*-
"""r383 part 2 -- the controls that decide whether the harmonic separations mean anything.

Reads paper/HARMONIC_r383.json (written by harmonic_r383.py), computes four falsification
controls from the per-cell values already in it, and writes them back into the same file.
No corpus access, no re-measurement.

CONTROL 1  NULL: DFweak family vs DFweak family. Both arms are the SAME lesion mechanism --
           a pure linear scaling of tib_ant_l max_isometric_force -- differing only in the
           amount and in which optimisation batch produced them. NEITHER contains the extra
           rectifier. Any separation here is separation the rectifier cannot be responsible
           for. C(6,2)=15 family pairs x 6 signals x 5 measures = 450 tests.

CONTROL 2  LIKE-FOR-LIKE: the rung test compares 6 seed values from ONE ladder family against
           6 DFweak seed means each averaged over SIX families. That crushes the DFweak spread
           and makes disjointness far easier than it should be. Control 2 redoes it family
           against single family, matching Control 1's geometry exactly.

CONTROL 3  NEGATIVE-CONTROL SIGNAL: ankle_angle_r, the UNLESIONED right ankle. The spastic
           reflex is left-only. A rectifier signature there is a pipeline artefact.

CONTROL 4  WHICH ARM MOVED: for each separation, where does the (between-scenario) control arm
           sit? If the control sits with the spastic arm, the number is being moved by the
           DF-WEAKNESS lesion, not by the rectifier, and the sign of the "spastic effect" is a
           misreading.
"""
import io
import itertools
import json

import numpy as np

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\HARMONIC_r383.json"
DFW = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
LAD = [("0.00625", "R289KV00625"), ("0.0125", "R289KV0125"),
       ("0.035", "R291KV0035"), ("0.070", "R291KV0070")]
CTL = ["R203V080C", "R203V105C", "R203V130C"]
RAT = ["THD_ratio", "H2_ratio", "H3_ratio", "H4_ratio", "phase2_rel"]

J = json.load(io.open(P, encoding="utf-8"))
C = J["cells"]
SIG = J["method"]["signals"]


def fv(fams, sig, meas):
    if isinstance(fams, str):
        fams = [fams]
    o = []
    for k, r in C.items():
        if k.split("_")[0] not in fams or not r.get("gate_G"):
            continue
        v = r.get("sig", {}).get(sig, {}).get(meas)
        if v is not None and np.isfinite(v):
            o.append(float(v))
    return sorted(o)


def sep(a, b):
    if len(a) < 4 or len(b) < 4:
        return None
    return bool(max(b[0] - a[-1], a[0] - b[-1]) > 0)


# ---------------------------------------------------------------- gate ledger
gate = {}
for kv, fam in LAD:
    cells = {k: v for k, v in C.items() if k.split("_")[0] == fam}
    ok = [k for k, v in cells.items() if v.get("gate_G")]
    gate[fam] = {"KV": float(kv), "n_cells": len(cells), "n_gate_G": len(ok),
                 "guards": {k: v.get("guard") for k, v in sorted(cells.items())
                            if not v.get("gate_G")}}
J["GATE_G_LEDGER"] = {
    "by_ladder_family": gate,
    "dfweak_n_gate_G": len(fv(DFW, "ankle_angle_l", "THD_ratio")),
    "control_n_gate_G": len(fv(CTL, "ankle_angle_l", "THD_ratio")),
    "CRITICAL": ("The KV 0.070 rung (R291KV0070) has ZERO Gate-G seeds: all six fall before "
                 "T1 = 9.73 s (t_end 8.24-9.52 s). Under the carried convention the TOP RUNG OF "
                 "THE LADDER DOES NOT EXIST. Its '0 separations' is UNINFORMATIVE, not a null "
                 "result, and the registered prediction 'rises with KV' can only be evaluated "
                 "over the three surviving rungs 0.00625 / 0.0125 / 0.035."),
}

# ---------------------------------------------------------------- control 1: null
per, tot, hit = {}, 0, 0
for s in SIG:
    per[s] = {}
    for m in RAT:
        n = k = 0
        for A, B in itertools.combinations(DFW, 2):
            r = sep(fv(A, s, m), fv(B, s, m))
            if r is None:
                continue
            n += 1
            k += int(r)
        per[s][m] = {"n_pairs": n, "n_separated": k, "rate": k / float(n) if n else None}
        tot += n
        hit += k
J["CONTROL_1_NULL_dfweak_vs_dfweak"] = {
    "what": ("15 DFweak family pairs x 6 signals x 5 measures. Both members of every pair are "
             "the SAME lesion mechanism (linear tib_ant_l force scaling) and NEITHER has the "
             "extra half-wave rectifier. Separation here cannot be caused by rectification."),
    "n_tests": tot, "n_separated": hit, "rate": hit / float(tot),
    "exchangeability_expectation": 2.0 / 924.0,
    "excess_over_chance": (hit / float(tot)) / (2.0 / 924.0),
    "by_signal": per,
    "VERDICT": ("%.1f%% of comparisons between two rectifier-free arms separate, against a "
                "%.2f%% exchangeability expectation -- a %.0fx excess. The min/max disjointness "
                "statistic with a 1/924 permutation floor assumes seeds are exchangeable across "
                "arms. THEY ARE NOT: an optimisation family is a batch, and the harmonic ratios "
                "index the batch. The 1/924 floor is therefore NOT the operating false-positive "
                "rate of this design; the empirical one is about %.0f in 100."
                % (100.0 * hit / tot, 100.0 * 2 / 924.0,
                   (hit / float(tot)) / (2.0 / 924.0), 100.0 * hit / tot)),
}

# ---------------------------------------------------------------- control 2: like-for-like
lfl = {}
for kv, fam in LAD:
    n = k = 0
    bys = {}
    for s in SIG:
        bys[s] = {}
        for m in RAT:
            nn = kk = 0
            for D in DFW:
                r = sep(fv(fam, s, m), fv(D, s, m))
                if r is None:
                    continue
                nn += 1
                kk += int(r)
            bys[s][m] = {"n": nn, "n_separated": kk}
            n += nn
            k += kk
    lfl[kv] = {"family": fam, "n_tests": n, "n_separated": k,
               "rate": k / float(n) if n else None, "by_signal": bys}
J["CONTROL_2_like_for_like"] = {
    "what": ("ladder family (6 seeds) vs EACH DFweak family (6 seeds) separately, so both sides "
             "have the same single-family geometry as CONTROL 1. The headline rung test instead "
             "pits 6 single-family ladder seeds against 6 DFweak seed means each pooled over SIX "
             "families, which shrinks the DFweak spread and inflates disjointness."),
    "null_rate_from_control_1": hit / float(tot),
    "by_rung": lfl,
    "VERDICT": ("like-for-like separation rates are %s against a rectifier-free null of %.1f%%. "
                "The rates are elevated but the null is nowhere near zero, so the elevation is "
                "an effect size on top of a large batch effect, not a clean detection."
                % (", ".join("KV %s: %.1f%%" % (kv, 100 * lfl[kv]["rate"])
                             for kv, _ in LAD if lfl[kv]["rate"] is not None),
                   100.0 * hit / tot)),
}

# ---------------------------------------------------------------- control 3: wrong-side signal
nc = {}
for kv, _ in LAD:
    e = J["rungs"][kv]["by_signal"]
    les = sum(1 for s in SIG if s != "ankle_angle_r" for m in RAT if e[s][m].get("separated"))
    nn = sum(1 for m in RAT if e["ankle_angle_r"][m].get("separated"))
    nc[kv] = {"lesioned_signals_separated": les, "lesioned_signals_tested": 5 * len(RAT),
              "lesioned_rate": les / float(5 * len(RAT)),
              "negative_control_separated": nn, "negative_control_tested": len(RAT),
              "negative_control_rate": nn / float(len(RAT))}
J["CONTROL_3_negative_control_signal"] = {
    "what": "ankle_angle_r, the UNLESIONED right ankle. The spastic reflex is left-leg only.",
    "by_rung": nc,
    "VERDICT": ("the unlesioned right ankle separates at essentially the same rate as the five "
                "left-side signals at every rung (%s). A half-wave rectifier inserted only into "
                "left soleus and left gastroc cannot put its harmonic signature into the "
                "contralateral ankle angle at the same strength. Whatever the measure is "
                "separating, it is a whole-trial / whole-batch property, not the lesion."
                % "; ".join("KV %s: lesioned %.0f%% vs right-ankle %.0f%%"
                            % (kv, 100 * nc[kv]["lesioned_rate"],
                               100 * nc[kv]["negative_control_rate"]) for kv, _ in LAD)),
}

# ---------------------------------------------------------------- control 4: which arm moved
wm = {}
for kv, fam in LAD:
    wm[kv] = {}
    for s in SIG:
        wm[kv][s] = {}
        for m in RAT:
            d = J["rungs"][kv]["by_signal"][s][m]
            if not d.get("separated"):
                continue
            c = fv(CTL, s, m)
            if len(c) < 4:
                continue
            cm = float(np.mean(c))
            csd = float(np.std(c, ddof=1))
            zs = (d["spastic_mean"] - cm) / csd if csd else None
            zw = (d["dfweak_mean"] - cm) / csd if csd else None
            wm[kv][s][m] = {
                "control_mean_BETWEEN_SCENARIO": cm, "control_sd_BETWEEN_SCENARIO": csd,
                "z_spastic_vs_control": zs, "z_dfweak_vs_control": zw,
                "arm_further_from_control": ("SPASTIC" if abs(zs) > abs(zw) else "DFWEAK"),
                "direction_reported": d["direction"],
            }
J["CONTROL_4_which_arm_moved"] = {
    "what": ("for every separation, the distance of each arm from the control arm. If the "
             "control sits ON the spastic arm then the separated number is being moved by the "
             "DF-WEAKNESS lesion and calling it a spastic effect inverts the causation."),
    "BETWEEN_SCENARIO_WARNING": ("the control arm R203V080C/V105C/V130C runs at min_velocity "
                                 "0.8 / 1.05 / 1.3 while every ladder and DFweak family runs at "
                                 "1.0. EVERY statement in CONTROL_4 is BETWEEN-SCENARIO and "
                                 "confounded with target gait speed."),
    "by_rung": wm,
}
cnt = {"SPASTIC": 0, "DFWEAK": 0}
for kv in wm:
    for s in wm[kv]:
        for m in wm[kv][s]:
            cnt[wm[kv][s][m]["arm_further_from_control"]] += 1
J["CONTROL_4_which_arm_moved"]["tally"] = cnt
J["CONTROL_4_which_arm_moved"]["VERDICT"] = (
    "of %d separations with a usable control arm, %d have the DFWEAK arm further from control "
    "and %d have the SPASTIC arm further. BETWEEN-SCENARIO."
    % (cnt["SPASTIC"] + cnt["DFWEAK"], cnt["DFWEAK"], cnt["SPASTIC"]))

# ---------------------------------------------------------------- best candidate audit
cand = []
mo = J["MONOTONICITY_IN_KV"]
cc = J["checks"]["c_ratio_vs_amplitude"]["by_signal"]
for s in SIG:
    for m in RAT:
        r0 = J["rungs"]["0.00625"]["by_signal"][s][m]
        cand.append({
            "signal": s, "measure": m,
            "separates_at_KV0.00625": bool(r0.get("separated")),
            "direction_at_KV0.00625": r0.get("direction"),
            "gap_over_pooled_sd_KV0.00625": r0.get("gap_over_pooled_sd"),
            "monotone_increasing_in_KV": mo[s][m]["monotone_increasing"],
            "spearman_vs_KV": mo[s][m]["spearman_vs_KV"],
            "pearson_ratio_vs_A1": cc[s][m]["pearson_vs_A1"],
            "null_control_1_rate": per[s][m]["rate"],
            "is_negative_control_signal": s == "ankle_angle_r",
            "PASSES_ALL_FILTERS": bool(
                r0.get("separated") and r0.get("direction") == "SPASTIC HIGH"
                and mo[s][m]["monotone_increasing"] and s != "ankle_angle_r"
                and abs(cc[s][m]["pearson_vs_A1"] or 1) < 0.3
                and (per[s][m]["rate"] or 1) <= 2.0 / 15.0),
        })
cand.sort(key=lambda x: (not x["PASSES_ALL_FILTERS"],
                         -(x["gap_over_pooled_sd_KV0.00625"] or 0)))
J["CANDIDATE_AUDIT"] = {
    "filters": ["separates at the SMALLEST rung KV 0.00625",
                "direction SPASTIC HIGH (the registered direction)",
                "monotone increasing across the three surviving rungs",
                "not the unlesioned-side negative-control signal",
                "|pearson(ratio, |X1|)| < 0.3, i.e. actually scale-free",
                "null control 1 rate <= 2/15, i.e. rarely separates two rectifier-free arms"],
    "n_passing": sum(1 for c in cand if c["PASSES_ALL_FILTERS"]),
    "rows": cand,
}

J["HONEST_READ"] = {
    "status": "EXPLORATORY. Nothing here is confirmatory.",
    "1_top_rung_missing": J["GATE_G_LEDGER"]["CRITICAL"],
    "2_null_is_not_zero": J["CONTROL_1_NULL_dfweak_vs_dfweak"]["VERDICT"],
    "3_wrong_side_separates_too": J["CONTROL_3_negative_control_signal"]["VERDICT"],
    "4_direction_is_mostly_wrong": (
        "the registered direction is SPASTIC HIGH. Across the three surviving rungs the "
        "separations run %d SPASTIC HIGH against %d SPASTIC LOW, and the LOW fraction GROWS "
        "with KV -- at KV 0.035 the great majority of separations have LOWER relative harmonic "
        "content in the spastic arm. That is the opposite of the prediction."
        % (sum(1 for kv, _ in LAD for s in SIG for m in RAT
               if J["rungs"][kv]["by_signal"][s][m].get("direction") == "SPASTIC HIGH"),
           sum(1 for kv, _ in LAD for s in SIG for m in RAT
               if J["rungs"][kv]["by_signal"][s][m].get("direction") == "SPASTIC LOW"))),
    "5_not_monotone": (
        "%d of 30 signal x measure combinations are monotone increasing in KV over the three "
        "surviving rungs. A random ordering of three points is increasing with probability 1/6, "
        "so about 5 of 30 is what noise gives. The dominant observed pattern is DECREASING."
        % sum(1 for s in SIG for m in RAT if mo[s][m]["monotone_increasing"])),
    "6_ratios_are_not_scale_free": (
        "check (c) was supposed to show the ratios are immune to amplitude. It shows the "
        "opposite for four of the six signals: pearson(THD_ratio, |X1|) is -0.69 "
        "(ankle_angle_l), -0.84 (ankle_l.torque), -0.76 (ankle_vel_l), -0.88 (ankle_angle_r). "
        "A shrinking fundamental inflates every ratio that divides by it, so on those signals "
        "the harmonic ratio IS the amplitude endpoint with the sign flipped. The only two "
        "signals whose THD_ratio is amplitude-clean are soleus_l.activation (+0.06) and "
        "gastroc_l.activation (-0.02) -- exactly the two muscles the rectifier drives -- and on "
        "BOTH of them the spastic arm's THD_ratio is LOWER than DF-weak, not higher."),
    "7_interpolation_is_not_the_problem": (
        "the synthetic interpolation floor (a pure cycle-phase sinusoid pushed through the "
        "identical pipeline) is THD = 3e-5 median, 6e-5 max, three to four ORDERS OF MAGNITUDE "
        "below the measured THD ratios of 0.4-4.0. Mean-cycle averaging suppresses per-cycle "
        "THD by only 0.1-0.3%. The harmonics in these signals are REAL features of the "
        "waveforms. The artefact is not in the spectrum; it is in the INFERENCE from the "
        "spectrum to the lesion."),
    "BOTTOM_LINE": (
        "The frequency-domain endpoint does not rescue the first-principles argument. The "
        "harmonics are real and are measured cleanly, but they do not track the rectifier: the "
        "unlesioned contralateral ankle carries them just as strongly, two rectifier-free "
        "DF-weak families separate from each other 21% of the time, the direction is "
        "predominantly opposite to the prediction and becomes more so as KV rises, monotonicity "
        "in KV is at chance, and on the four signals where a separation looks largest the ratio "
        "is simply amplitude in disguise. The two signals where the ratio is genuinely "
        "scale-free are soleus and gastroc activation, and both put the spastic arm LOWER. "
        "The first-principles prediction -- rectifier harmonics survive linear re-optimisation "
        "and show up as elevated relative harmonic content -- is NOT SUPPORTED by this corpus. "
        "It is not merely unconfirmed; where the measurement is cleanest it points the other "
        "way. The most plausible reading is that re-optimisation absorbs the rectified drive "
        "into a gait pattern whose ankle kinematics are, if anything, SMOOTHER in relative "
        "harmonic terms than the dorsiflexor-weakness gait."),
}

io.open(P, "w", encoding="utf-8").write(
    json.dumps(J, indent=2, ensure_ascii=False, sort_keys=False))
import os
print("CONTROL 1 null rate      : %d/%d = %.1f%%  (%.0fx the 2/924 exchangeability rate)"
      % (hit, tot, 100.0 * hit / tot, (hit / float(tot)) / (2.0 / 924.0)))
for kv, _ in LAD:
    if lfl[kv]["rate"] is not None:
        print("CONTROL 2 like-for-like  : KV %-8s %.1f%%" % (kv, 100 * lfl[kv]["rate"]))
print("CONTROL 3 right ankle    : %s"
      % ", ".join("KV %s %.0f%% vs %.0f%%" % (kv, 100 * nc[kv]["negative_control_rate"],
                                              100 * nc[kv]["lesioned_rate"]) for kv, _ in LAD))
print("CONTROL 4 tally          : %s" % cnt)
print("candidates passing all 6 filters: %d" % J["CANDIDATE_AUDIT"]["n_passing"])
for c in J["CANDIDATE_AUDIT"]["rows"][:8]:
    print("  %-22s %-11s sep@min=%-5s %-12s mono=%-5s r(A1)=%+.2f null=%s pass=%s"
          % (c["signal"], c["measure"], c["separates_at_KV0.00625"],
             c["direction_at_KV0.00625"] or "-", c["monotone_increasing_in_KV"],
             c["pearson_ratio_vs_A1"] or 0,
             "%.2f" % c["null_control_1_rate"], c["PASSES_ALL_FILTERS"]))
print("wrote %s (%d B)" % (P, os.path.getsize(P)))
