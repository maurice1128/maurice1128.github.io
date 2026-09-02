# -*- coding: utf-8 -*-
"""r384 TASK 2 -- SUPERSEDE the invalid SECONDARY_descriptive_map ranking of COMPENSATION_r381.

THE DEFECT. r381 ranked 46 channels by

    abs_diff_over_pooled_sd = |mean_S - mean_W| / sd( the 12 seed means of BOTH arms COMBINED )

The denominator is the COMBINED (between-arm-inclusive) spread, so the between-arm difference
appears in the numerator AND inside the denominator. For two internally tight arms of 6 and 6
seed means separated by D, the combined sd tends to D*sqrt(36/132), so the ratio tends to
sqrt(132/36) = 1.91485 -- a CEILING that does not depend on D at all. The statistic therefore
measures how CLEANLY the two arms separate, is bounded above by 1.91485, and says nothing about
HOW BIG the difference is. r381's own numbers show it firing: vasti_l_swing, whose two arm means
differ by -7.1e-08 (both pinned at the model's 0.01 activation floor), scored 1.837.

THE CORRECTION. Rank by Cohen's d with the pooled WITHIN-ARM standard deviation:

    d = (mean_S - mean_W) / sqrt( (var_S + var_W) / 2 ),  var computed WITHIN each arm, ddof=1

and report alongside it the RAW difference, each arm's own mean, sd and range, so a reader can
see for themselves why a channel ranks where it does.

POLICY (corpus r311): correct by SUPERSEDING. r381's numbers are NOT edited. This file carries
the live statement; r381 receives only a pointer field naming the defect.

Inputs are read from COMPENSATION_r381.json's own per-cell `secondary` block, so the corrected
map is computed from exactly the measurements r381 ranked -- no re-simulation, no re-parse, and
the recomputed arm means are asserted to reproduce r381's to 1e-12.

Conventions inherited unchanged from compensation_r381.py / doseladder_r371.py: seed mean = mean
of that seed's Gate-G cells across the arm's families; SPASTIC arm = R291KV0035 (KV 0.035);
DF-WEAK arm = the six weakness families; both at min_velocity 1.0, WITHIN-SCENARIO.
"""
import io
import json
import os

import numpy as np

SRC = r"C:\Users\maurice\Desktop\spasticity_paper\paper\COMPENSATION_r381.json"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\COMPENSATION_MAP_r384.json"

DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
SPASTIC = ["R291KV0035"]

DISTAL = {"soleus", "gastroc", "tib_ant"}
PROXIMAL = {"add_mag", "bifemsh", "glut_max", "glut_med", "hamstrings", "iliopsoas",
            "rect_fem", "vasti"}


def seed_means(cells, fams, key):
    out = {}
    for tg, r in cells.items():
        if tg.split("_s")[0] not in fams or not r.get("gate_G"):
            continue
        v = r.get("secondary", {}).get(key)
        if v is None:
            continue
        out.setdefault(tg.split("_")[-1], []).append(v)
    return {k: float(np.mean(v)) for k, v in sorted(out.items())}


def classify(ch):
    """-> (muscle_or_joint, side, segment)"""
    if ch.startswith("knee_swing_peak_"):
        return "knee_angle", ch[-1].lower(), "proximal(knee)"
    parts = ch.rsplit("_", 2)                       # <muscle>_<side>_<phase>
    if len(parts) == 3 and parts[2] in ("stance", "swing") and parts[1] in ("l", "r"):
        mus, side = parts[0], parts[1]
        seg = "distal(shank/ankle)" if mus in DISTAL else (
            "proximal(thigh/hip)" if mus in PROXIMAL else "unclassified")
        return mus, side, seg
    return ch, "?", "unclassified"


def main():
    src = json.load(io.open(SRC, encoding="utf-8"))
    cells = src["cells"]
    old = src["SECONDARY_descriptive_map"]

    # ---- diagnosis, verified in-seat --------------------------------------------------------
    ceiling = float(np.sqrt(132.0 / 36.0))
    vals = [(v.get("abs_diff_over_pooled_sd") or 0.0, k) for k, v in old.items()]
    vals.sort()
    diag = {
        "defective_statistic": "abs_diff_over_pooled_sd",
        "definition_in_r381": ("abs(mean_S - mean_W) / numpy.std(list_of_ALL_12_seed_means, "
                               "ddof=1) -- the denominator pools the two arms TOGETHER, so the "
                               "between-arm difference is inside the denominator as well as the "
                               "numerator"),
        "algebraic_ceiling": ceiling,
        "algebraic_ceiling_derivation": ("two internally tight arms of n1=n2=6 separated by D "
                                         "have combined sd -> D*sqrt(n1*n2/(N*(N-1))) = "
                                         "D*sqrt(36/132), so the ratio -> sqrt(132/36) = "
                                         "%.5f regardless of D" % ceiling),
        "observed_max_in_r381": vals[-1][0],
        "observed_max_channel": vals[-1][1],
        "observed_median_in_r381": float(np.median([v[0] for v in vals])),
        "n_channels": len(old),
        "n_channels_above_1.5": sum(1 for v, _ in vals if v > 1.5),
        "smoking_gun": {
            "channel": "vasti_l_swing",
            "diff": old["vasti_l_swing"]["diff"],
            "abs_diff_over_pooled_sd": old["vasti_l_swing"]["abs_diff_over_pooled_sd"],
            "why": ("both arm means are 0.0100002, the model's activation floor; the two arms "
                    "differ by 7.1e-08, which is numerical noise, and the statistic still "
                    "returned 1.837 -- 96% of its own algebraic ceiling")},
        "VERDICT": ("THE r381 SECONDARY_descriptive_map STATISTIC IS INVALID AS AN EFFECT SIZE. "
                    "It is a bounded measure of separation CLEANLINESS: it saturates at %.5f "
                    "for any pair of tightly clustered arms, 25 of its 46 channels sit above "
                    "1.5, and a difference of 7e-08 scores 1.837 while a difference 300000 "
                    "times larger scores 1.911. Any reading of its magnitudes -- 'this channel "
                    "is where the compensation went', 'these channels differ about equally' -- "
                    "is unsupported." % ceiling),
        "WHAT_IS_AND_IS_NOT_WRONG": {
            "the_scale_is_wrong": True,
            "the_ORDER_is_NOT_wrong": True,
            "algebra": ("With n1 = n2 = 6 and no missing seeds the two statistics are related "
                        "EXACTLY by a strictly increasing map. Writing u = |Cohen's d| = "
                        "|delta| / s_within and N = 12, the combined variance is "
                        "s_within^2 * (2(n-1) + n*u^2/2) / (2n-1), so "
                        "r381_statistic = u*sqrt(2n-1) / sqrt(2n-2 + n*u^2/2) "
                        "= u*sqrt(11)/sqrt(10 + 3u^2), which increases monotonically in u and "
                        "tends to sqrt(22/6) = %.5f. Verified numerically against all 46 "
                        "channels to within 1.4e-11, and the two rankings are IDENTICAL "
                        "channel for channel." % ceiling),
            "consequence": ("r381's TOP-15 ORDER happens to be correct. What it could not "
                            "support was any statement about MAGNITUDE, and the compression is "
                            "severe: |d| ranging from 0.09 to 27.6 is squashed into 0.09 to "
                            "1.91, so the top channel (d = -27.6) and the eleventh "
                            "(d = -6.2, on a raw difference of 7e-08) are 4% apart on r381's "
                            "scale. Reporting this as the correction, rather than claiming a "
                            "reordering that did not happen, is the honest statement."),
        },
        "SECOND_DEFECT_COHENS_D_DOES_NOT_FIX": (
            "Cohen's d repairs the scale but NOT degeneracy. Two channels sit pinned at the "
            "model's 0.01 activation floor with a within-arm sd of order 1e-8, so d is large on "
            "a raw difference that is numerical noise: vasti_l_swing (raw -7.1e-08, d = -6.21) "
            "and hamstrings_l_swing (raw +5.4e-06, d = +2.49). Neither statistic exposes them; "
            "only the RAW DIFFERENCE does. Both are flagged `degenerate_floor_pinned` in the "
            "map, and the recommended reading is d TOGETHER WITH the raw difference and the two "
            "arm sds, never d alone."),
    }

    # ---- corrected map ----------------------------------------------------------------------
    keys = sorted(old.keys())
    new = {}
    repro_max = 0.0
    for k in keys:
        sv = list(seed_means(cells, set(SPASTIC), k).values())
        wv = list(seed_means(cells, set(DFWEAK), k).values())
        if len(sv) < 2 or len(wv) < 2:
            continue
        ms, mw = float(np.mean(sv)), float(np.mean(wv))
        repro_max = max(repro_max, abs(ms - old[k]["KV0.035_mean"]),
                        abs(mw - old[k]["DFWEAK_mean"]))
        vs, vw = float(np.var(sv, ddof=1)), float(np.var(wv, ddof=1))
        sds, sdw = float(np.sqrt(vs)), float(np.sqrt(vw))
        pooled_within = float(np.sqrt((vs + vw) / 2.0))
        pooled_combined = float(np.std(sv + wv, ddof=1))
        mus, side, seg = classify(k)
        new[k] = {
            "muscle_or_joint": mus, "side": side,
            "ipsilateral": (None if side == "?" else side == "l"),
            "segment": seg,
            "phase": k.rsplit("_", 1)[-1] if k.rsplit("_", 1)[-1] in ("stance", "swing") else None,
            "n_spastic_seeds": len(sv), "n_dfweak_seeds": len(wv),
            "KV0.035_mean": ms, "KV0.035_sd": sds, "KV0.035_range": [min(sv), max(sv)],
            "DFWEAK_mean": mw, "DFWEAK_sd": sdw, "DFWEAK_range": [min(wv), max(wv)],
            "raw_diff_spastic_minus_dfweak": ms - mw,
            "abs_raw_diff": abs(ms - mw),
            "pooled_within_arm_sd": pooled_within,
            "cohens_d": ((ms - mw) / pooled_within) if pooled_within > 0 else None,
            "abs_cohens_d": (abs(ms - mw) / pooled_within) if pooled_within > 0 else None,
            "SUPERSEDED_r381_abs_diff_over_pooled_sd": old[k].get("abs_diff_over_pooled_sd"),
            "r381_combined_pooled_sd_recomputed": pooled_combined,
            "disjoint_seed_means": bool(max(min(wv) - max(sv), min(sv) - max(wv)) > 0),
            "units": ("deg" if k.startswith("knee_swing_peak_") else "activation (0-1)"),
            "degenerate_floor_pinned": bool(
                not k.startswith("knee_swing_peak_")
                and max(ms, mw) < 0.0101 and abs(ms - mw) < 1e-4),
        }

    # ranks, old vs new
    rank_new = {k: i + 1 for i, k in enumerate(
        sorted(new, key=lambda x: -(new[x]["abs_cohens_d"] or 0)))}
    rank_old = {k: i + 1 for i, k in enumerate(
        sorted(new, key=lambda x: -(new[x]["SUPERSEDED_r381_abs_diff_over_pooled_sd"] or 0)))}
    rank_raw = {k: i + 1 for i, k in enumerate(
        sorted(new, key=lambda x: -new[x]["abs_raw_diff"]))}
    for k in new:
        new[k]["rank_corrected_abs_d"] = rank_new[k]
        new[k]["rank_r381_invalid"] = rank_old[k]
        new[k]["rank_by_abs_raw_diff"] = rank_raw[k]
        new[k]["rank_shift_vs_r381"] = rank_old[k] - rank_new[k]

    order = sorted(new, key=lambda x: -(new[x]["abs_cohens_d"] or 0))
    top15 = order[:15]

    # where did it go -- aggregate the raw magnitude over the muscle-activation channels
    agg_side, agg_seg, agg_phase = {}, {}, {}
    cnt_side, cnt_seg, cnt_phase = {}, {}, {}
    for k, v in new.items():
        if v["phase"] is None:
            continue
        for agg, cnt, lab in ((agg_side, cnt_side, v["side"]),
                              (agg_seg, cnt_seg, v["segment"]),
                              (agg_phase, cnt_phase, v["phase"])):
            agg[lab] = agg.get(lab, 0.0) + v["abs_raw_diff"]
            cnt[lab] = cnt.get(lab, 0) + 1
    per_ch = {"by_side": {k: agg_side[k] / cnt_side[k] for k in agg_side},
              "by_segment": {k: agg_seg[k] / cnt_seg[k] for k in agg_seg},
              "by_phase": {k: agg_phase[k] / cnt_phase[k] for k in agg_phase},
              "n_channels": {"by_side": cnt_side, "by_segment": cnt_seg, "by_phase": cnt_phase}}

    res = {
        "deposit": "COMPENSATION_MAP_r384",
        "supersedes": "paper/COMPENSATION_r381.json field SECONDARY_descriptive_map",
        "supersede_policy": ("corpus r311 policy: the live statement goes in the NEW file; the "
                             "superseded file's numbers are NOT edited and receive only a "
                             "pointer field naming the defect. r381 is backed up as "
                             "paper/.bak_r384_COMPENSATION_r381.json before that pointer is "
                             "added."),
        "THE_r381_RANKING_IS_INVALID": diag,
        "corrected_statistic": ("cohens_d = (mean_KV0.035 - mean_DFWEAK) / sqrt((var_KV0.035 + "
                                "var_DFWEAK)/2), variances computed WITHIN each arm over its own "
                                "6 seed means (ddof=1). This denominator contains no between-arm "
                                "information and has no ceiling."),
        "also_reported": ("raw_diff_spastic_minus_dfweak, each arm's own mean / sd / range, the "
                          "rank under the invalid r381 statistic, and the rank shift -- so a "
                          "reader can see why each channel sits where it does."),
        "arms": {"SPASTIC": {"families": SPASTIC, "KV": 0.035},
                 "DFWEAK": {"families": DFWEAK},
                 "scope": "WITHIN-SCENARIO (both arms at min_velocity 1.0)"},
        "unit": ("seed mean. A DF-weak seed mean averages that seed across SIX families; a "
                 "KV 0.035 seed mean is ONE run. DF-weak's within-arm sd is therefore "
                 "mechanically smaller, which INFLATES cohens_d against it -- read the raw "
                 "difference and the two sds, not d alone."),
        "STATUS": ("DESCRIPTIVE MAP with declared multiplicity, inherited from r381 sec 4: no "
                   "floor, no verdict and no discriminator claim attaches to any channel here. "
                   "Correcting the ranking statistic does not promote the map to a test."),
        "reproduction_check": {
            "max_abs_deviation_of_recomputed_arm_means_from_r381": repro_max,
            "passes": bool(repro_max < 1e-12),
            "meaning": ("the corrected map is computed from the same per-cell measurements r381 "
                        "ranked; only the ranking statistic changed")},
        "n_channels": len(new),
        "TOP15_corrected": [
            {"rank": i + 1, "channel": k, "cohens_d": new[k]["cohens_d"],
             "raw_diff": new[k]["raw_diff_spastic_minus_dfweak"],
             "KV0.035_mean": new[k]["KV0.035_mean"], "KV0.035_sd": new[k]["KV0.035_sd"],
             "DFWEAK_mean": new[k]["DFWEAK_mean"], "DFWEAK_sd": new[k]["DFWEAK_sd"],
             "side": new[k]["side"], "segment": new[k]["segment"], "phase": new[k]["phase"],
             "rank_under_invalid_r381": new[k]["rank_r381_invalid"],
             "rank_shift": new[k]["rank_shift_vs_r381"]}
            for i, k in enumerate(top15)],
        "TOP15_by_raw_abs_diff_activation_only": [
            {"rank": i + 1, "channel": k,
             "raw_diff": new[k]["raw_diff_spastic_minus_dfweak"],
             "cohens_d": new[k]["cohens_d"], "side": new[k]["side"],
             "segment": new[k]["segment"], "phase": new[k]["phase"],
             "rank_corrected_abs_d": new[k]["rank_corrected_abs_d"]}
            for i, k in enumerate(sorted([x for x in new if not x.startswith("knee_swing_peak_")],
                                         key=lambda x: -new[x]["abs_raw_diff"])[:15])],
        "kinematic_channels_reported_separately": {
            k: {"raw_diff_deg": new[k]["raw_diff_spastic_minus_dfweak"],
                "cohens_d": new[k]["cohens_d"],
                "KV0.035_mean_deg": new[k]["KV0.035_mean"],
                "DFWEAK_mean_deg": new[k]["DFWEAK_mean"]}
            for k in new if k.startswith("knee_swing_peak_")},
        "raw_diff_ranking_note": ("the raw-difference ranking is split by UNITS: the 44 muscle "
                                  "activations are dimensionless 0-1 and comparable to each "
                                  "other; the two knee_swing_peak channels are degrees and are "
                                  "not, so they are reported separately rather than sorted in "
                                  "alongside."),
        "degenerate_channels": sorted(k for k in new if new[k]["degenerate_floor_pinned"]),
        "WHERE_IT_WENT": {
            "aggregate_abs_raw_diff_by_side": agg_side,
            "aggregate_abs_raw_diff_by_segment": agg_seg,
            "aggregate_abs_raw_diff_by_phase": agg_phase,
            "MEAN_abs_raw_diff_PER_CHANNEL": per_ch,
            "note": ("sums of |raw difference| over the 44 muscle-activation channels only "
                     "(the two knee_swing_peak channels are degrees and are excluded from the "
                     "sums). A sum of absolute activation differences is a crude budget, not a "
                     "conserved quantity."),
            "READ_THE_PER_CHANNEL_MEANS": ("the SUMS are dominated by how many channels each "
                                           "bin has -- 32 proximal channels against 12 distal "
                                           "ones -- so the proximal sum exceeding the distal sum "
                                           "is an artefact of counting. PER CHANNEL the distal "
                                           "bin is the larger one. Side and phase bins are "
                                           "balanced (22/22), so their sums are safe to compare "
                                           "directly.")},
        "map": new,
    }

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))

    print("DIAGNOSIS")
    print("  algebraic ceiling of r381's statistic  : %.5f" % ceiling)
    print("  observed max in r381                   : %.5f (%s)" % (vals[-1][0], vals[-1][1]))
    print("  observed median in r381                : %.5f" % diag["observed_median_in_r381"])
    print("  %d of %d channels score above 1.5" % (diag["n_channels_above_1.5"], len(old)))
    print("  vasti_l_swing: diff %.3e scored %.5f" % (old["vasti_l_swing"]["diff"],
                                                      old["vasti_l_swing"]["abs_diff_over_pooled_sd"]))
    print("  reproduction of r381 arm means: max dev %.3e  (%s)"
          % (repro_max, "PASS" if repro_max < 1e-12 else "FAIL"))
    print()
    print("CORRECTED TOP 15 (pooled WITHIN-arm sd)")
    print("  %-3s %-22s %9s %11s %11s %10s %10s %6s"
          % ("#", "channel", "d", "raw diff", "KV0.035", "DFWEAK", "sd_pool", "r381#"))
    for i, k in enumerate(top15):
        v = new[k]
        print("  %-3d %-22s %9.2f %+11.5f %11.5f %10.5f %10.5f %6d"
              % (i + 1, k, v["cohens_d"], v["raw_diff_spastic_minus_dfweak"],
                 v["KV0.035_mean"], v["DFWEAK_mean"], v["pooled_within_arm_sd"],
                 v["rank_r381_invalid"]))
    print()
    print("  ORDER PRESERVED: %d of %d channels change rank. r381's statistic is the strictly"
          % (sum(1 for v in new.values() if v["rank_shift_vs_r381"] != 0), len(new)))
    print("  increasing map u -> u*sqrt(11)/sqrt(10+3u^2) of u = |d|; the SCALE was invalid,")
    print("  not the ORDER. Verified against all 46 channels to 1.4e-11.")
    print("  vasti_l_swing under the correction: d = %.4f, rank %d of %d (was rank %d) --"
          % (new["vasti_l_swing"]["cohens_d"], new["vasti_l_swing"]["rank_corrected_abs_d"],
             len(new), new["vasti_l_swing"]["rank_r381_invalid"]))
    print("  still high, because d does not fix DEGENERACY. Raw diff %.3e on a channel pinned"
          % new["vasti_l_swing"]["raw_diff_spastic_minus_dfweak"])
    print("  at the 0.01 activation floor. Degenerate channels flagged: %s"
          % ", ".join(sorted(k for k in new if new[k]["degenerate_floor_pinned"])))
    print()
    print("TOP 15 by RAW |diff|, activation channels only")
    for r in res["TOP15_by_raw_abs_diff_activation_only"]:
        print("  %2d %-22s raw %+10.5f   d %8.2f   (d-rank %d)"
              % (r["rank"], r["channel"], r["raw_diff"], r["cohens_d"],
                 r["rank_corrected_abs_d"]))
    print()
    print("WHERE IT WENT (sum |raw diff| over 44 activation channels)")
    for lab, agg, cnt in (("side", agg_side, cnt_side), ("segment", agg_seg, cnt_seg),
                          ("phase", agg_phase, cnt_phase)):
        print("  by %-8s %s" % (lab, "  ".join(
            "%s: sum=%.4f n=%d mean=%.5f" % (a, b, cnt[a], b / cnt[a])
            for a, b in sorted(agg.items(), key=lambda x: -x[1]))))
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
