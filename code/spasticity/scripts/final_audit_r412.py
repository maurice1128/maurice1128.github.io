# -*- coding: utf-8 -*-
"""r412 -- writes paper/FINAL_AUDIT_r412.json. READ-ONLY on SCONE results. No sconecmd."""
import glob
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_r412 as A
import audit_checks_r412 as C

PAPER = A.PAPER
OUT = os.path.join(PAPER, "FINAL_AUDIT_r412.json")

DF = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
PF = ["R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"]
SP14 = ["R393SPg070", "R393SPg100", "R396SPg110"]
SPALL = SP14 + ["R396SPg120"]


def gate_vals(fams, side="l"):
    v = []
    for f in fams:
        _, det = A.family_values(f, side=side, require_gate=False)
        for r in det:
            if r.get("gate_G") and r.get("knee_hs_deg") is not None:
                v.append((r["tag"], r.get("t_end_s"), r["knee_hs_deg"]))
    return v


def stat(v):
    x = sorted(k[2] for k in v)
    return {"n": len(x), "range": [x[0], x[-1]] if x else None,
            "mean": float(np.mean(x)) if x else None, "values": x}


def main():
    # --------------------------------------------------------------- claim (a)
    ct, _ = A.family_values("R151C")
    wk, _ = A.family_values("R151W")
    sp, _ = A.family_values("R396SPg110")
    g = A.edge_gap(sp, wk)
    allv = sp + wk
    n_ext = sum(1 for c in itertools.combinations(range(len(allv)), len(sp))
                if A.edge_gap(sorted(allv[i] for i in c),
                              sorted(allv[i] for i in range(len(allv)) if i not in c))
                >= g - 1e-12)

    claim_a = {
        "claim_as_reported": "knee at heel strike, edge gap SPAS KV0.110 vs WEAK x0.80 = "
                             "+6.3919 deg, disjoint, exhaustive permutation 1/210; "
                             "R151C [-8.2396,-7.5876] mean -7.8500; R151W [-6.2735,-5.3749] "
                             "mean -5.8443; R396SPg110 [-13.7949,-12.6655] mean -13.1995",
        "container": "paper/KNEE_MDC_BATCHNULL_r399.json -> /STEP0_HEADLINE_REPRODUCTION",
        "recomputed_from_sto": {
            "R151C": {"n": len(ct), "range": [ct[0], ct[-1]], "mean": float(np.mean(ct))},
            "R151W": {"n": len(wk), "range": [wk[0], wk[-1]], "mean": float(np.mean(wk))},
            "R396SPg110": {"n": len(sp), "range": [sp[0], sp[-1]], "mean": float(np.mean(sp))},
            "edge_gap_deg": g, "disjoint": g > 0,
            "exhaustive_permutation": "%d/%d" % (n_ext, 210)},
        "STATUS": "VERIFIED",
        "note": "every arm reproduces to 10 significant figures from the .par.sto files.",
        "CONTEXT_THE_HEADLINE_MUST_CARRY": "the SAME deposit's /PLAIN_VERDICT/"
            "Q1_does_it_clear_a_properly_sourced_knee_MDC answers NO: 6.3919 deg falls 1.2281 "
            "deg short of 7.62 deg, the most conservative defensible knee MDC. The gap is real "
            "and reproducible; it is not clinically detectable.",
    }

    # --------------------------------------------------------------- claim (b)
    sp14 = gate_vals(SP14)
    spall = gate_vals(SPALL)
    dfv = gate_vals(DF)
    pfv = gate_vals(PF)
    band = [x for x in gate_vals(SPALL) if x[1] and 9.8 <= x[1] <= 17.9]
    dfband = [x for x in gate_vals(DF) if x[1] and 9.8 <= x[1] <= 17.9]
    pfband = [x for x in gate_vals(PF) if x[1] and 9.8 <= x[1] <= 17.9]
    scan = {}
    for f in PAPER, :
        pass
    hits = []
    for p in sorted(glob.glob(os.path.join(PAPER, "*"))):
        b = os.path.basename(p)
        if b.startswith(".bak") or not os.path.isfile(p):
            continue
        try:
            raw = open(p, "r", errors="replace").read()
        except Exception:
            continue
        if "1.8857" in raw or "1.7617" in raw:
            hits.append(b)

    claim_b = {
        "claim_as_reported": "duration-matched comparison, window 9.8-17.9 s: WEAK n=17 "
                             "[-8.806,-6.485] mean -7.488 vs SPAS KV>=0.070 n=14 "
                             "[-13.795,-10.691] mean -12.218, edge gap +1.8857 DISJOINT; "
                             "LEFT/RIGHT negative control: right knee same window gap "
                             "-1.7617 OVERLAP",
        "STATUS": "NO CONTAINER",
        "container_search": {
            "searched": "every non-.bak file in paper/ for the literal strings '1.8857' and "
                        "'1.7617', plus a tree-wide grep of paper/, scone/ and external/ for "
                        "1.8857 / 1.7617 / 'duration_match'",
            "files_containing_either_gap": hits,
            "conclusion": "NO FILE ANYWHERE IN THE PROJECT CONTAINS EITHER NUMBER. There is "
                          "no deposit, no script and no registration for this comparison. "
                          "The only duration-matched machinery in the corpus is "
                          "DYNAMICS_SWING_r361/r363 /READING_M_duration_matched, whose band is "
                          "[13.58, 17.85] and whose verdict is UNINFORMATIVE on 1 spastic and "
                          "0 weak cells, and MEMBERSHIP_AUDIT_r358, which records a different "
                          "duration-matched knee gap of 2.0900 deg on n=11 vs 6."},
        "recompute_attempt": {
            "SPAS_arm_REPRODUCES_EXACTLY": {
                "definition_recovered": "the Gate-G cells of R393SPg070 + R393SPg100 + "
                                        "R396SPg110, i.e. KV 0.070/0.100/0.110 and NOT 0.120",
                "recomputed": stat(sp14),
                "claimed": {"n": 14, "range": [-13.795, -10.691], "mean": -12.218},
                "verdict": "MATCH to 3 decimals on n, both edges and the mean"},
            "WEAK_arm_DOES_NOT_REPRODUCE": {
                "claimed": {"n": 17, "range": [-8.806, -6.485], "mean": -7.488},
                "dorsiflexor_weakness_all_Gate_G": stat(dfv),
                "plantarflexor_weakness_all_Gate_G": stat(pfv),
                "dorsiflexor_weakness_inside_band_9.8_17.9": stat(dfband),
                "plantarflexor_weakness_inside_band_9.8_17.9": stat(pfband),
                "why_it_cannot_be_built": "ALL 36 dorsiflexor-weakness cells have t_end = "
                                          "20.00 s exactly, so a t_end band capped at 17.9 s "
                                          "excludes every one of them. The plantarflexor "
                                          "families supply only 13 Gate-G cells in total and "
                                          "6 inside the band. No subset of the weakness "
                                          "corpus has n=17 with a minimum of -8.806 deg: the "
                                          "value -6.485 is real (R276WPF010_s101) but -8.806 "
                                          "matches no cell in any weakness family under the "
                                          "corpus readout.",
                "verdict": "MISMATCH -- the arm cannot be reconstructed"},
            "NEGATIVE_CONTROL_IS_CONTRADICTED_BY_r399": {
                "claimed": "right knee, same window, gap -1.7617, OVERLAP",
                "what_r399_actually_found": "paper/KNEE_MDC_BATCHNULL_r399.json -> "
                                            "/STEP4_UNLESIONED_SIDE_NEGATIVE_CONTROL/by_rung/"
                                            "0.110 : the UNLESIONED RIGHT knee SEPARATES 6 of "
                                            "6 at the headline rung, edge gaps 0.8766 / "
                                            "1.4276 / 1.6300 deg (min/median/max).",
                "verdict": "the reported 'right knee OVERLAP' is the opposite of the only "
                           "deposited right-knee result at the headline rung. The side "
                           "negative control is CLEAN AT KV 0.050/0.070/0.100 (0/6 each) and "
                           "DIRTY AT KV 0.110 (6/6). The headline rung is the one rung where "
                           "the unlesioned side also separates."},
        },
        "ACTION": "either produce the script and deposit that generated +1.8857 / -1.7617, or "
                  "withdraw both numbers. They must not enter the write-up as they stand.",
    }

    # ------------------------------------------------------- claims c..h from deposits
    def load(f):
        return json.load(open(os.path.join(PAPER, f), errors="replace"))

    r399 = load("KNEE_MDC_BATCHNULL_r399.json")
    r406 = load("SHAM_READOUT_r406.json")
    r405 = load("PUBLICDATA_VALIDATION_r405.json")
    r373 = load("DECOMPOSE_r373.json")
    r397 = load("FINE_GAP_r397.json")
    r392 = load("WARMSTART_PROBE_r392.json")

    claim_c = {
        "claim_as_reported": "same-mechanism dorsiflexor family pairs 4/15 = 26.7%; "
                             "like-for-like 24/24 = 100%; largest same-mechanism spurious "
                             "edge gap 0.5697 deg",
        "container": "paper/KNEE_MDC_BATCHNULL_r399.json -> /STEP1_BATCH_NULL, "
                     "/STEP2_LIKE_FOR_LIKE, /STEP6_MAGNITUDE",
        "deposited": {
            "n_separated": r399["STEP1_BATCH_NULL"]["by_endpoint"]["knee_hs_L_deg"]["NULL_DF"]
                           ["n_separated"],
            "n_pairs_tested": r399["STEP1_BATCH_NULL"]["by_endpoint"]["knee_hs_L_deg"]
                              ["NULL_DF"]["n_pairs_tested"],
            "rate": r399["STEP1_BATCH_NULL"]["by_endpoint"]["knee_hs_L_deg"]["NULL_DF"]
                    ["BATCH_FALSE_POSITIVE_RATE"],
            "largest_null_edge_gap_deg": r399["STEP6_MAGNITUDE"]
                ["largest_edge_gap_between_two_same_mechanism_DFweak_families_deg"],
            "like_for_like": "%d/%d" % (r399["VERDICT_BATCH_NULL"]["left_knee_like_for_like"]
                                        ["n_separated"],
                                        r399["VERDICT_BATCH_NULL"]["left_knee_like_for_like"]
                                        ["n_tested"])},
        "STATUS": "VERIFIED",
        "UNREPORTED_SIBLING_THAT_MUST_TRAVEL_WITH_IT": "the same deposit's "
            "/STEP4/like_for_like_hit_rate_RIGHT_knee is 0.25 (6/24) on the UNLESIONED side, "
            "all six of those hits at the headline rung KV 0.110. Quoting 24/24 on the left "
            "without 6/24 on the right overstates the side control.",
        "NULL_PF_could_not_be_computed": r399["PLAIN_VERDICT"]
            ["Q2_does_the_separation_survive_the_batch_null"]["NULL_PF_could_not_be_computed"],
    }

    claim_d = {
        "claim_as_reported": "sham chain protocol shift: largest 0.5860 deg against a 6.3919 "
                             "headline",
        "container": "paper/SHAM_READOUT_r406.json",
        "deposited": {"largest_protocol_shift_deg": r406["largest_protocol_shift_deg"],
                      "headline_gap_deg": r406["headline_gap_deg"]},
        "STATUS": "VERIFIED",
        "note": "0.5860145801831838 and 6.391931677410274 both present verbatim; the headline "
                "value is byte-identical to the one recomputed from .sto for claim (a).",
    }

    cal = r405["calibration_numbers_LOCKED"]
    cpl = r405["ankle_knee_coupling_for_citation"]
    claim_e = {
        "claim_as_reported": "able-bodied knee at IC 8.2871 +/- 4.7198 (n=138); stroke paretic "
                             "19.9899 +/- 9.0073 (n=50); coupling r=+0.613, rho=+0.639, n=50, "
                             "p=2.25e-06; subgroups +6.31 vs +17.09, difference 10.78, d=1.49",
        "container": "paper/PUBLICDATA_VALIDATION_r405.json -> "
                     "/calibration_numbers_LOCKED and /ankle_knee_coupling_for_citation",
        "deposited": {
            "able_bodied": [cal["able_bodied_knee_flexion_at_initial_contact"]["mean_deg"],
                            cal["able_bodied_knee_flexion_at_initial_contact"]["sd_deg"],
                            cal["able_bodied_knee_flexion_at_initial_contact"]["n"]],
            "stroke_paretic": [cal["stroke_paretic_knee_flexion_at_initial_contact"]["mean_deg"],
                               cal["stroke_paretic_knee_flexion_at_initial_contact"]["sd_deg"],
                               cal["stroke_paretic_knee_flexion_at_initial_contact"]["n"]],
            "pearson_r": cpl["pearson_r"], "pearson_p": cpl["pearson_p"],
            "spearman_rho": cpl["spearman_rho"], "n": cpl["n"],
            "subgroup_deviation_deg": [
                cpl["subgroups_split_at_zero_ankle_angle"]["plantarflexed_at_IC"]
                   ["deviation_from_able_mean_deg"],
                cpl["subgroups_split_at_zero_ankle_angle"]["dorsiflexed_at_IC"]
                   ["deviation_from_able_mean_deg"]],
            "difference_deg": cpl["subgroups_split_at_zero_ankle_angle"]["difference_deg"],
            "cohen_d": cpl["subgroups_split_at_zero_ankle_angle"]["cohen_d"]},
        "STATUS": "VERIFIED",
        "rounding_note": "the deposit carries r = 0.6128 and p = 2.246e-06; the reported "
                         "+0.613 and 2.25e-06 are correct roundings.",
        "caveats_already_in_the_deposit_that_must_be_quoted_with_it": [
            "PLUG_IN_GAIT_OFFSET_WARNING: the absolute able-bodied mean of +8.29 deg is a "
            "marker-model offset, not a physiological value. Only the SD, the group "
            "difference and within-dataset correlations survive it.",
            "POOLED EVENTS: 25 of 50 paretic limbs contact forefoot-first, so 'knee angle at "
            "initial contact' pools two mechanically different events.",
            "NO WALKING SPEED in the dataset: a speed contribution to the +11.70 deg group "
            "offset cannot be excluded."],
    }

    claim_f = {
        "claim_as_reported": "compensation cancelled fraction 0.8570823499731588; "
                             "decomposition RV share 0.34516165584712166",
        "containers": ["paper/DYNAMICS_LIMITATION_r365.json",
                       "paper/DECOMPOSE_r373.json -> /arms/KV0.035/RV_share_of_gap"],
        "deposited": {"RV_share_of_gap_KV0.035":
                      r373["arms"]["KV0.035"]["RV_share_of_gap"],
                      "cancelled_fraction_present_in_r365": "0.8570823499731588" in
                      open(os.path.join(PAPER, "DYNAMICS_LIMITATION_r365.json"),
                           errors="replace").read()},
        "STATUS": "VERIFIED",
        "MATERIAL_CAVEAT_NOT_PREVIOUSLY_REPORTED": {
            "what": "0.3452 is one of three RV shares in DECOMPOSE_r373.json and the only one "
                    "that lies inside [0, 1].",
            "the_other_two": {"KV0.0125": r373["arms"]["KV0.0125"]["RV_share_of_gap"],
                              "KV0.00625": r373["arms"]["KV0.00625"]["RV_share_of_gap"]},
            "why": "the denominator gap_vs_DFweak is 0.0179 at KV 0.035 but 0.0017 and "
                   "-0.0014 at the two lower rungs, so the ratio is unstable and changes "
                   "sign. Quoting 0.3452 alone presents the only well-behaved member of an "
                   "ill-conditioned family as if it were the estimate.",
            "the_deposit_already_says_so": r373["status"]},
    }

    claim_g = {
        "claim_as_reported": "dose-response on mean stance ankle angle: gaps 1.5419 / 1.9406 / "
                             "2.6910 / 3.0092 / 3.2532 at KV 0.050/0.070/0.100/0.110/0.120 "
                             "against WEAK x0.80; fit gap = 24.764*KV + 0.258, r=0.9981",
        "container": "paper/FINE_GAP_r397.json -> /rungs and /fit",
        "deposited": {
            "gaps": [r397["rungs"][k]["gap_vs_x080_mean_deg"]
                     for k in ["0.05", "0.07", "0.1", "0.11", "0.12"]],
            "n_gate_G": [r397["rungs"][k]["n_gate_G"]
                         for k in ["0.05", "0.07", "0.1", "0.11", "0.12"]],
            "fit": r397["fit"], "VERDICT": r397["VERDICT"]},
        "STATUS": "VERIFIED",
        "DEFECT_IN_THE_CONTAINER_ITSELF": {
            "what": "FINE_GAP_r397.json carries MDC_floor_deg = 3.8 and derives KV_for_MDC = "
                    "0.1430 from it.",
            "why_it_is_wrong": "KNEE_MDC_BATCHNULL_r399.json -> /TASK1_KNEE_MDC/"
                               "CORRECTION_TO_THE_CORPUS establishes that 3.8 deg is the MDC "
                               "for TRAILING LIMB ANGLE in Kesar 2011 and is neither a knee "
                               "nor an ankle number. Kesar's ankle-at-initial-contact MDC is "
                               "7.0 deg and its peak-ankle-in-swing MDC is 4.9 deg. r399 "
                               "states 3.8 'must not be used as a knee floor anywhere in the "
                               "paper'; r397's endpoint is an ANKLE endpoint but 3.8 is not "
                               "an ankle number either.",
            "does_the_verdict_flip": "NO, and it cannot: a larger floor makes NOT REACHED more "
                                     "secure. But KV_for_MDC = 0.1430 is understated. Against "
                                     "the correct 4.9 deg ankle floor the fit needs KV 0.1874; "
                                     "against 7.0 deg it needs KV 0.2722. Both are far above "
                                     "the highest KV that walks (0.120).",
            "action": "r397's MDC_floor_deg and KV_for_MDC must not be quoted; quote the "
                      "VERDICT only, or recompute against a sourced ankle floor.",
            "recomputed_KV_for_MDC": {
                "at_4.9_deg": (4.9 - r397["fit"]["intercept_deg"])
                              / r397["fit"]["slope_deg_per_KV"],
                "at_7.0_deg": (7.0 - r397["fit"]["intercept_deg"])
                              / r397["fit"]["slope_deg_per_KV"]},
        },
        "also": "the 0.120 rung has n_gate_G = 3, below the corpus's own 4-cell UNINFORMATIVE "
                "bar, so the fifth point of the five-point fit rests on an UNINFORMATIVE rung.",
    }

    claim_h = {
        "claim_as_reported": "arm A t_end 8.24 s FAIL (bit-identical reproduction of "
                             "R291KV0070_s101), arm B 13.95 s PASS, arm C self-terminated at "
                             "329 of 400 generations, 9.23 s FAIL",
        "container": "paper/WARMSTART_PROBE_r392.json -> /arms, /arm_A_reproduction_check, "
                     "/arm_C_early_stop",
        "deposited": {a["arm"]: {"t_end_s": a["t_end_s"], "passes_gate_9.73":
                                 a["passes_gate_9.73"],
                                 "n_generations": a["n_generations"],
                                 "max_generations": a["max_generations"]}
                      for a in r392["arms"]},
        "arm_A_reproduction": r392["arm_A_reproduction_check"],
        "STATUS": "VERIFIED",
        "note": "all four numbers present verbatim; arm A's par filenames and terminal "
                "objective match R291KV0070_s101 exactly, so 'bit-identical' is supported.",
    }

    r410 = json.load(open(os.path.join(PAPER, "FROZEN_MECHANISM_r410.json"), errors="replace"))
    r411 = json.load(open(os.path.join(PAPER, "FROZEN_WEAKNESS_r411.json"), errors="replace"))

    claim_i = {
        "claim_as_reported": "frozen-controller mechanism, spastic side: NONE -7.8500, SOL "
                             "-7.7371 (delta +0.11), GAS -18.8434 (delta -10.99), BOTH "
                             "-7.9113, all n=6, t_end 3.4-4.5 s so sub-Gate-G",
        "container_BEFORE_this_audit": "NONE -- no deposit existed",
        "container_NOW": "paper/FROZEN_MECHANISM_r410.json (CREATED BY THIS AUDIT)",
        "recomputed": {a: {"mean": v["knee_hs_deg_mean"],
                           "delta_vs_NONE_deg": v.get("delta_vs_NONE_deg"),
                           "n": v["n_seeds_with_a_value"],
                           "t_end_s_range": v["t_end_s_range"],
                           "GATE_G_pass_count": v["GATE_G_pass_count"]}
                       for a, v in r410["arms"].items()},
        "STATUS": "MISMATCH",
        "what_matches": "all four arm means reproduce to 4 decimals: NONE -7.8500, SOL "
                        "-7.7371, GAS -18.8434, BOTH -7.9113, and the deltas +0.1129 and "
                        "-10.9934 round to the reported +0.11 and -10.99. n = 6 in every arm.",
        "what_does_not_match": {
            "the_t_end_range": "reported as '3.4-4.5 s' for all arms. The NONE arm runs "
                               "20.00 s on all six seeds. The lesioned arms span 3.27-4.99 s, "
                               "not 3.4-4.5 s.",
            "the_gate_G_statement": "reported as 'so sub-Gate-G' for all arms. The NONE arm "
                                    "PASSES Gate G on 6 of 6 seeds with 15 admissible cycles "
                                    "each. Only the three lesioned arms are sub-Gate-G.",
            "why_this_is_not_cosmetic": "NONE is the comparator. The deltas therefore subtract "
                                        "a 20 s, 15-cycle, Gate-G-passing steady walk from a "
                                        "3-5 s, 1-2 cycle fall. They are not lesion effect "
                                        "sizes and must not be presented as such. The "
                                        "'GAS carries the signature' reading rests entirely "
                                        "on this non-comparable delta."},
        "ALSO": "the NONE arm's six per-seed values are bit-identical to the six R151C Gate-G "
                "values used in claim (a), confirming R410NONE is a faithful replay of the "
                "control controller and not an independent measurement.",
    }

    claim_j = {
        "claim_as_reported": "frozen-controller, weakness side: NONE -7.8500, TA x0.80 "
                             "-6.5114, TA x0.50 -5.4179, TA x0.30 -8.1763, SOL-weak x0.50 "
                             "-13.3254, GAS-weak x0.50 -5.4803, n=6 each",
        "container_BEFORE_this_audit": "NONE -- no deposit existed",
        "container_NOW": "paper/FROZEN_WEAKNESS_r411.json (CREATED BY THIS AUDIT)",
        "recomputed": {a: {"mean": v["knee_hs_deg_mean"],
                           "delta_vs_NONE_deg": v.get("delta_vs_NONE_deg"),
                           "n": v["n_seeds_with_a_value"],
                           "t_end_s_range": v["t_end_s_range"],
                           "GATE_G_pass_count": v["GATE_G_pass_count"]}
                       for a, v in r411["arms"].items()},
        "STATUS": "VERIFIED",
        "note": "all six arm means reproduce to 4 decimals with n = 6 each. The same "
                "comparator caveat as claim (i) applies: NONE runs 20.00 s and passes Gate G "
                "6/6; every lesioned arm is sub-Gate-G except R411TA_x080_s104 (13.54 s).",
        "THE_FINDING_IN_IT_THAT_WAS_NOT_FLAGGED": {
            "what": "SOL x0.50 -- a pure WEAKNESS lesion with no reflex at all -- moves the "
                    "knee to -13.33 deg, which is MORE flexed than the spastic headline arm "
                    "R396SPg110 (-13.20 deg) and 5.48 deg more flexed than the frozen "
                    "control.",
            "why_it_matters": "the paper's discriminative claim is that spasticity and "
                              "weakness separate on knee-at-heel-strike with spasticity MORE "
                              "flexed. Under a frozen controller a plantarflexor WEAKNESS "
                              "reproduces both the sign and roughly the magnitude of that "
                              "signature. The endpoint is therefore not mechanism-specific in "
                              "the absence of re-optimisation.",
            "what_defuses_it_and_what_does_not": "it is sub-Gate-G and so cannot be quoted "
                                                 "against a Gate-G corpus number. But the "
                                                 "re-optimised answer already exists and "
                                                 "points the other way: the plantarflexor-"
                                                 "weakness families R276WPF005/010/020, "
                                                 "R285BF007/008 give Gate-G knee values in "
                                                 "[-9.154, -6.485], which do NOT reach the "
                                                 "spastic range. The honest statement is that "
                                                 "the discrimination depends on the controller "
                                                 "being re-optimised, and this belongs in the "
                                                 "limitations section.",
        },
    }

    claims = {"a": claim_a, "b": claim_b, "c": claim_c, "d": claim_d, "e": claim_e,
              "f": claim_f, "g": claim_g, "h": claim_h, "i": claim_i, "j": claim_j}
    tally = {"VERIFIED": [], "MISMATCH": [], "NO CONTAINER": []}
    for k, v in claims.items():
        tally[v["STATUS"]].append(k)

    # ------------------------------------------------------------------ checks 1-4
    pre = C.check_preregs()
    jsn = C.json_health()
    prot = C.protected_dirs()

    check1 = {
        "question": "does every PREREG_*.md have a matching .sha256, and does the file still "
                    "hash to it? (the r229 failure mode)",
        "n_registrations": pre["n_registrations"],
        "n_with_sidecar_and_MATCHING_hash": pre["n_match"],
        "n_with_sidecar_and_MISMATCHED_hash": pre["n_mismatch"],
        "n_with_NO_sidecar": pre["n_no_sidecar"],
        "MISMATCHED": pre["hash_mismatch"],
        "NO_SIDECAR": pre["no_sidecar"],
        "VERDICT": "CLEAN ON THE r229 FAILURE MODE. Every one of the %d registrations that "
                   "carries a .sha256 sidecar still hashes to it. Zero mismatches. The %d "
                   "without a sidecar are all pre-r160 or superseded registrations; they were "
                   "never hashed, which is a coverage gap, not a tampering signal."
                   % (pre["n_match"], pre["n_no_sidecar"]),
        "per_registration": pre["registrations"],
    }

    check2 = {
        "question": "does every executed registration have a deposit reporting its outcome, "
                    "including the UNINFORMATIVE ones?",
        "the_four_named": {
            "r402": {"registration": "PREREG_biarticular_r402.md",
                     "deposit": "MECHANISM_RESULT_r402.json",
                     "outcome_recorded": "SOL 0/6 and GAS 0/6 Gate-G, both UNINFORMATIVE",
                     "STATUS": "REPORTED"},
            "r404": {"registration": "NONE FOUND -- there is no PREREG_*_r404.md",
                     "deposit": "WEAKONLY_RESULT_r404.json",
                     "outcome_recorded": "WKHAM060 0/6 and WKHAM040 0/6 Gate-G, both "
                                         "UNINFORMATIVE",
                     "STATUS": "REPORTED, BUT UNREGISTERED"},
            "r407": {"registration": "registration is PREREG_biarticular_r402.md (r407 "
                                     "declares itself the supersession of r402)",
                     "deposit": "MECHANISM_RESULT_r407.json",
                     "outcome_recorded": "overall UNINFORMATIVE; at KV 0.110 GAS and SOL have "
                                         "0 Gate-G seeds",
                     "STATUS": "REPORTED",
                     "TIMING_NOTE": "this deposit was rewritten at 04:14 on 2026-08-26, "
                                    "DURING this audit, when the last cell "
                                    "R407BOTHg110_s106 completed at 04:13. An earlier copy "
                                    "written at 02:21 was stale. The grid is now complete: "
                                    "72 of 72 cell files present, 33 of them BROKEN_PARENT "
                                    "stubs."},
            "r409": {"registration": "PREREG_onedim_r409.md (hashed, sidecar matches)",
                     "deposit": "*** NONE ***",
                     "STATUS": "UNREPORTED RESULT"},
        },
        "r408_AND_r409_ARE_THE_TWO_UNREPORTED_REGISTRATIONS": {
            "r408": {"file": "PREREG_terminalswing_r408.md",
                     "sha256_sidecar": "present and MATCHING",
                     "deposit": "*** NONE ***",
                     "was_it_executed": "YES, apparently. Its outcome is written as prose in "
                                        "a LATER registration: PREREG_onedim_r409.md section "
                                        "1 row 4 records 'KTQ and GAS separated as predicted, "
                                        "but SOL separated too -- r408 section 5 P3 failed as "
                                        "written'. That is a registered prediction failing, "
                                        "recorded nowhere but in the preamble of the next "
                                        "registration.",
                     "what_is_missing": "a deposit carrying KTQ_tsw, GAS_tsw, SOL_tsw and "
                                        "KNEE_ic for R393SPg070, R393SPg100 and the five "
                                        "non-R151W dorsiflexor families, and the P1-P5 "
                                        "verdicts.",
                     "does_it_need_simulation": "NO. Section 4 states the confirmatory arms "
                                                "are 'all already simulated and all Gate-G "
                                                "passing'. Verified: R393SPg070 6/6, "
                                                "R393SPg100 4/6, and the five weakness "
                                                "families 6/6 each. This is analysis only."},
            "r409": {"file": "PREREG_onedim_r409.md",
                     "sha256_sidecar": "present and MATCHING",
                     "deposit": "*** NONE ***",
                     "was_it_executed": "NO EVIDENCE that it was. No script, no stage file, "
                                        "no cell files, no deposit.",
                     "does_it_need_simulation": "NO. Section 4's confirmatory pool is "
                                                "'all already simulated'. Verified below: "
                                                "101 cells exist across the 13 named "
                                                "families, 65 of them Gate-G, against a "
                                                "section-7 UNINFORMATIVE floor of 20. This is "
                                                "analysis only."},
        },
        "other_deposits_with_no_registration_at_all": [
            "SPANNING_MAP_r403.json", "WEAKONLY_RESULT_r404.json",
            "PUBLICDATA_VALIDATION_r405.json", "SHAM_READOUT_r406.json",
            "FROZEN_MECHANISM_r410.json (created by this audit)",
            "FROZEN_WEAKNESS_r411.json (created by this audit)"],
        "note_on_that_list": "these are post-hoc/exploratory and each says so in its own "
                             "status field. That is acceptable provided the write-up never "
                             "presents them as confirmatory.",
        "A_FINDING_ABOUT_HOW_HYPOTHESES_WERE_KILLED": {
            "what": "PREREG_terminalswing_r408.md section 1 and PREREG_onedim_r409.md section "
                    "1 both record hypothesis 2 as killed because 'soleus-only produced 70% "
                    "of the knee displacement at KV 0.050, against a registered ceiling of "
                    "40%'.",
            "the_problem": "that 70% comes from MECHANISM_RESULT_r407.json -> /by_rung/0.050/"
                           "SOL, which has n_gate_G = 3 and carries \"uninformative\": true. "
                           "The r402/r407 registration's own rule is that a rung with fewer "
                           "than 4 Gate-G seeds is UNINFORMATIVE and may not be read.",
            "consequence": "a registered hypothesis was retired on the strength of a cell the "
                           "governing registration declares unreadable. The kill may still be "
                           "right, but it is not evidenced under the corpus's own rules and "
                           "must not be written up as a falsification.",
            "arithmetic": {"BOTH_delta_knee_at_KV0.050_deg": -2.1535497265277863,
                           "SOL_delta_knee_at_KV0.050_deg_n3": -1.5137669088211956,
                           "share": 0.7029170908729718,
                           "SOL_n_gate_G": 3, "registered_minimum": 4},
        },
    }

    check3 = {
        "question": "any NaN, null-where-a-number-belongs, or absent keys other deposits "
                    "reference?",
        "n_json_scanned": jsn["n_json_scanned"],
        "strict_parse_failures": jsn["strict_parse_failures"],
        "empty_files": jsn["empty_files"],
        "files_with_BARE_NaN_JSON_VALUES": {
            "PUBLICDATA_VALIDATION_r405.json": {
                "n_non_finite_values": 122,
                "where": "only inside /step3_extracted_values/per_participant_able_bodied[i] "
                         "and /per_participant_stroke[i], and only in EMG fields "
                         "(TA_mean_swing_peaknorm, GAS_mean_stance_peaknorm, "
                         "GAS_mean_early_stance_0_15pct_peaknorm and their paretic / "
                         "nonparetic variants).",
                "is_it_a_defect_in_the_cited_numbers": "NO. Every kinematic field is finite. "
                                                       "The deposit itself states 'zero "
                                                       "participants were dropped, zero NaNs' "
                                                       "for both knee-at-IC cohorts, and that "
                                                       "the EMG exclusions touch only the EMG "
                                                       "analyses. Claim (e) is unaffected.",
                "is_it_a_defect_at_all": "YES, a portability one. Bare NaN is not valid JSON "
                                         "under RFC 8259. Python's json accepts it, but jq, "
                                         "JavaScript JSON.parse and most strict readers will "
                                         "reject the whole file. If this deposit ships as "
                                         "supplementary material it should emit null."},
            "COST_MATCHED_LEDGER.json": {
                "n_non_finite_values": 1,
                "where": "/bands/0.5/mean_d_ank_rom",
                "assessment": "a single NaN in an old (2026-08-03) ledger. Same RFC 8259 "
                              "portability issue. No current deposit reads this path."},
        },
        "null_where_a_number_is_expected": {
            "assessment": "checked and found to be intentional in every case examined. "
                          "DECOMPOSE_r373.json sets RV_stance / RV_swing to null for the "
                          "DFweak arm because that arm has no reflex term. "
                          "MECHANISM_RESULT_r402/r407 and WEAKONLY_RESULT_r404 set means to "
                          "null exactly where n_gate_G = 0, which is the registered "
                          "UNINFORMATIVE encoding, not missing data.",
        },
        "dangling_cross_references": {
            "checked": "every claim in this audit was resolved to a live file; no deposit "
                       "audited here references a key that its target does not define.",
            "the_one_real_dangling_reference": "claim (b). Two numbers (+1.8857, -1.7617) "
                                               "were reported with no file behind them at "
                                               "all. See /claims/b.",
        },
    }

    check4 = {
        "question": "confirm the 112 protected directories and that none was modified in the "
                    "last 48 hours",
        "regex_used": prot["regex_used"],
        "n_result_dirs_total": prot["n_result_dirs_total"],
        "n_protected": prot["n_protected"],
        "COUNT_CONFIRMED": prot["n_protected"] == 112,
        "n_modified_in_last_48h": prot["n_modified_last_48h"],
        "modified_in_last_48h": prot["modified_last_48h"],
        "VERDICT": "CONFIRMED: exactly 112 protected directories, ZERO modified in the last "
                   "48 hours. This audit opened them read-only and wrote nothing under "
                   "C:\\Users\\maurice\\Documents\\SCONE\\results.",
        "protected_names": prot["protected_names"],
    }

    # ------------------------------------------------------------------ the licence question
    pool = {}
    for f in ["R289KV00625", "R289KV0125", "R291KV0035", "R276WPF005", "R276WPF010",
              "R276WPF020", "R285BF007", "R285BF008", "R287BF007", "R287BF008",
              "R291BF005", "R291BF007", "R291BF008"]:
        _, det = A.family_values(f, require_gate=False)
        pool[f] = {"cells": len(det), "gate_G": sum(1 for r in det if r.get("gate_G"))}
    pool_gg = sum(v["gate_G"] for v in pool.values())

    sims = {
        "ANSWER": "NONE. No simulation must be run before the Hyfydy licence expires on "
                  "2026-08-27. The corpus is complete for every claim the paper makes. What "
                  "is outstanding is ANALYSIS and DEPOSIT work on cells that already exist, "
                  "and analysis does not consume the licence.",
        "how_this_was_established": "every open registration and every threatened claim was "
                                    "traced to the cells it needs, and each of those cells "
                                    "was confirmed present on disk with its Gate-G status "
                                    "recomputed from the .par.sto.",
        "candidates_considered_and_why_each_is_NOT_required": [
            {"rank": 1,
             "candidate": "r409 one-dimensionality confirmation (PREREG_onedim_r409.md)",
             "would_it_need_sconecmd": "NO",
             "evidence": "section 4's confirmatory pool is 13 already-simulated families. "
                         "Recounted from disk: %d cells, %d Gate-G. Section 7's UNINFORMATIVE "
                         "floor is 20 Gate-G cells; the pool clears it by a factor of 3."
                         % (sum(v["cells"] for v in pool.values()), pool_gg),
             "pool_census": pool,
             "what_is_actually_needed": "one analysis script computing the nine terminal-swing "
                                        "predictors and knee-at-IC on those cells, plus a "
                                        "deposit. Estimated 1-2 h of analysis, 0 h of "
                                        "simulation."},
            {"rank": 2,
             "candidate": "r408 terminal-swing confirmation (PREREG_terminalswing_r408.md)",
             "would_it_need_sconecmd": "NO",
             "evidence": "section 4 names R393SPg070 (6 Gate-G), R393SPg100 (4 Gate-G) and "
                         "the five non-R151W dorsiflexor families (6 Gate-G each). All "
                         "present. The probe also appears to have been RUN already -- its "
                         "P3 failure is quoted in PREREG_onedim_r409.md section 1.",
             "what_is_actually_needed": "a deposit recording the P1-P5 verdicts, including "
                                        "the P3 failure. Estimated 1 h of analysis, 0 h of "
                                        "simulation."},
            {"rank": 3,
             "candidate": "top up R396SPg120 (seeds s103, s104 absent) so the KV 0.120 rung "
                          "reaches 4+ Gate-G cells and stops being UNINFORMATIVE",
             "would_it_need_sconecmd": "YES, roughly 2 cells x 5-10 min = 10-20 min",
             "why_it_is_NOT_required": "it cannot improve any claim. The KV 0.120 Gate-G knee "
                                       "values are -12.514 / -13.028 / -14.565, whose edge "
                                       "gap against WEAK x0.80 is about 6.24 deg -- SMALLER "
                                       "than the KV 0.110 headline of 6.3919. Adding cells to "
                                       "an arm can only move its edge toward the comparator, "
                                       "so this can lower the headline and cannot raise it. "
                                       "It also could not close the 1.2281 deg shortfall "
                                       "against the 7.62 deg knee MDC.",
             "recommendation": "DO NOT RUN. Report the 0.120 rung as UNINFORMATIVE, which is "
                               "what FINE_GAP_r397.json already does."},
            {"rank": 4,
             "candidate": "top up R396SPg110 (seeds s103, s104 absent) so the headline arm "
                          "has 6 cells rather than 4",
             "would_it_need_sconecmd": "YES, roughly 2 cells x 5-10 min",
             "why_it_is_NOT_required": "the headline gap is an EDGE gap. Two more cells can "
                                       "only extend the spastic arm's upper edge toward the "
                                       "weakness arm, shrinking 6.3919. Running it after "
                                       "seeing the result, and keeping it only if it helps, "
                                       "is exactly the practice the corpus's registration "
                                       "discipline exists to prevent.",
             "recommendation": "DO NOT RUN. If a referee asks for n=6, that is a post-"
                               "publication question, and the honest answer is that the "
                               "chain broke at s103/s104."},
            {"rank": 5,
             "candidate": "Gate-G soleus-weakness cells to answer the threat raised by "
                          "FROZEN_WEAKNESS_r411 (SOL x0.50 reproduces the spastic sign)",
             "would_it_need_sconecmd": "NO",
             "why_it_is_NOT_required": "the re-optimised answer already exists in the corpus. "
                                       "The plantarflexor-weakness families R276WPF005/010/"
                                       "020 and R285BF007/008 supply 13 Gate-G cells with "
                                       "knee-at-HS in [-9.154, -6.485], which does not reach "
                                       "the spastic range. The r411 result is a statement "
                                       "about FROZEN controllers and belongs in limitations.",
             "recommendation": "DO NOT RUN. Write the limitation."},
            {"rank": 6,
             "candidate": "re-run r410 / r411 with a longer horizon so the lesioned arms "
                          "reach Gate G",
             "would_it_need_sconecmd": "YES, and it would not work",
             "why_it_is_NOT_required": "these arms are frozen-controller replays. They fall at "
                                       "3-5 s because the unmodified control gains cannot "
                                       "stabilise the lesioned plant. A longer horizon does "
                                       "not change the dynamics; the model is already "
                                       "integrating to failure, not being cut short.",
             "recommendation": "DO NOT RUN."},
        ],
        "WHAT_MUST_BE_DONE_BEFORE_WRITE_UP_and_none_of_it_needs_the_licence": [
            "1. Resolve claim (b): produce the script and deposit behind +1.8857 / -1.7617, "
            "or withdraw both numbers. Highest priority -- they are currently uncontained "
            "and the right-knee half is contradicted by KNEE_MDC_BATCHNULL_r399.json.",
            "2. Deposit the r408 outcome, including the P3 failure that is currently recorded "
            "only as prose inside PREREG_onedim_r409.md.",
            "3. Execute and deposit r409 (analysis only, 65 Gate-G cells waiting).",
            "4. Stop quoting FINE_GAP_r397.json's MDC_floor_deg = 3.8 and KV_for_MDC = 0.1430; "
            "r399 has already retired that number.",
            "5. Correct the framing of claim (i): the frozen NONE arm is a 20 s Gate-G walk, "
            "not a 3.4-4.5 s sub-Gate-G one.",
            "6. Retire or re-evidence the 'soleus-only produced 70%' kill of mechanism "
            "hypothesis 2, which rests on an n=3 arm the governing registration marks "
            "UNINFORMATIVE.",
            "7. Carry the r399 PLAIN_VERDICT with the headline everywhere: the 6.3919 deg gap "
            "does not clear a properly sourced knee MDC.",
        ],
    }

    dep = {
        "round": "FINAL_AUDIT_r412",
        "what": "full pre-writeup audit of every number reported to the user during the "
                "session, recomputed from the .sto files where feasible, plus registration, "
                "deposit-coverage, JSON-health and protected-directory checks, plus the "
                "ranked list of simulations still needed before the Hyfydy licence expires "
                "on 2026-08-27.",
        "written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scope_and_safety": {
            "wrote_only_inside": r"C:\Users\maurice\Desktop\spasticity_paper",
            "SCONE_results_treated_as": "READ-ONLY. No directory was created, modified or "
                                        "removed under C:\\Users\\maurice\\Documents\\SCONE\\"
                                        "results.",
            "sconecmd_started_by_this_audit": "NONE",
            "unrelated_sconecmd_observed_running": "at 04:26 on 2026-08-26 a sconecmd process "
                                                   "was observed writing DR2K* result "
                                                   "directories. It was NOT started by this "
                                                   "audit and was NOT interfered with.",
            "python": r"C:\Users\maurice\Desktop\robotic_research\.venv\Scripts\python.exe",
            "scripts_written": ["scone/audit_r412.py", "scone/audit_checks_r412.py",
                                "scone/deposit_r412.py", "scone/final_audit_r412.py"],
        },
        "TALLY": {"VERIFIED": len(tally["VERIFIED"]), "MISMATCH": len(tally["MISMATCH"]),
                  "NO_CONTAINER": len(tally["NO CONTAINER"]),
                  "verified_claims": sorted(tally["VERIFIED"]),
                  "mismatch_claims": sorted(tally["MISMATCH"]),
                  "no_container_claims": sorted(tally["NO CONTAINER"])},
        "THE_TWO_THINGS_YOU_MOST_NEED_TO_KNOW": [
            "claim (b) has NO CONTAINER. +1.8857 and -1.7617 appear in no file anywhere in "
            "the project. Its spastic arm reproduces exactly; its weakness arm cannot be "
            "reconstructed from any weakness family; and its right-knee OVERLAP is the "
            "opposite of the only deposited right-knee result at the headline rung, where "
            "the UNLESIONED side separates 6 of 6.",
            "claim (i)'s numbers are right but its framing is wrong in a way that matters: "
            "the NONE comparator is a 20 s Gate-G-passing walk, not a sub-Gate-G one, so the "
            "GAS delta of -10.99 deg compares a steady gait against a fall.",
        ],
        "deposits_created_by_this_audit": [
            {"file": "paper/FROZEN_MECHANISM_r410.json",
             "bytes": os.path.getsize(os.path.join(PAPER, "FROZEN_MECHANISM_r410.json")),
             "for_claim": "i"},
            {"file": "paper/FROZEN_WEAKNESS_r411.json",
             "bytes": os.path.getsize(os.path.join(PAPER, "FROZEN_WEAKNESS_r411.json")),
             "for_claim": "j"},
        ],
        "claims": claims,
        "CHECK_1_registration_hashes": check1,
        "CHECK_2_deposit_coverage": check2,
        "CHECK_3_json_health": check3,
        "CHECK_4_protected_directories": check4,
        "SIMULATIONS_STILL_NEEDED": sims,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dep, f, indent=1)
    print(OUT, os.path.getsize(OUT), "bytes")
    print("TALLY", json.dumps(dep["TALLY"]))


if __name__ == "__main__":
    main()
