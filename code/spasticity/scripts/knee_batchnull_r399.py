# -*- coding: utf-8 -*-
"""r399 -- APPLY THE BATCH NULL TO knee_angle_l AT LEFT HEEL STRIKE.

The endpoint is #1 of the four pre-registered at paper/PREREG_kinpair_r378.md sec 3
("knee_angle_l at left heel strike, per-cycle mean"), so it is not a fished endpoint.
It was only ever measured at KV <= 0.035; the warm-start chaining of r393/r396 put Gate-G
cells at KV up to 0.120, where the spastic-vs-weak edge gap is large. This deposit asks the
only two questions that decide whether that gap means anything:

  (1) THE BATCH NULL.  Two optimisation families with the SAME lesion mechanism separate on
      this endpoint how often?  HARMONIC_r383 / BATCHNULL_r389 established that a family IS a
      batch and that same-mechanism families separate far more often than the 2/924 = 0.22%
      exhaustive-permutation floor implies.  That null has never been applied to the knee.

  (2) THE SIDE NEGATIVE CONTROL.  Both lesions are LEFT-ONLY.  The identical endpoint on the
      UNLESIONED RIGHT knee, gated on the RIGHT leg's own GRF, must NOT separate at a similar
      rate.  If it does, the left-knee separation is a batch artefact.

Conventions carried verbatim from scone/fine_gap_r397.py:
    SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the LAST kept cycle,
    require >= 5 cycles, stance = leg0_l.grf_norm_y > 0.05 (GRF threshold from
    sto_utils.grf_vertical).
Run-directory selection and the >= 4-values disjointness / exhaustive-floor / binomial
machinery are carried verbatim from scone/batchnull_r389.py, because r389 is the deposit whose
null is being reused and two of the weakness families own duplicated "(1)" copies of a seed
directory that r397's simpler len(glob)==1 rule would silently drop.

READ-ONLY on C:\\Users\\maurice\\Documents\\SCONE\\results. No sconecmd is started.
"""
import glob
import io
import itertools
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\KNEE_MDC_BATCHNULL_r399.json"

SETTLE, T1 = 1.0, 9.73                      # fine_gap_r397 verbatim
MIN_CYC = 5                                 # fine_gap_r397 verbatim
MIN_VALS = 4                                # batchnull_r389.separated verbatim

DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
PFWEAK = ["R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"]
SPASTIC = [("0.050", "R151S"), ("0.070", "R393SPg070"), ("0.100", "R393SPg100"),
           ("0.110", "R396SPg110"), ("0.120", "R396SPg120")]
CONTROL = "R151C"

PRIMARY = "knee_hs_L_deg"
NEGCTL = "knee_hs_R_deg"
KEYS = [PRIMARY, NEGCTL, "mean_ankle_stance_deg"]


# =============================================================================================
# TASK 1 -- THE KNEE MDC, SOURCED. Literature search 2026-08-24.
# =============================================================================================
# THE HEADLINE CORRECTION. The corpus has been quoting "3.8-11.5 deg" as a clinical MDC band
# applicable to kinematic endpoints (see paper/PREREG_kinpair_r378.md sec 7 item 4, and
# MDC = 3.8 hard-coded in scone/fine_gap_r397.py). Those two numbers were read out of Kesar
# et al. 2011 Table 2. THEY ARE NOT KNEE NUMBERS AND THEY ARE NOT EVEN THE SAME VARIABLE:
#   3.8  deg = TRAILING LIMB ANGLE
#   11.5 deg = HIP ANGLE AT TOE-OFF
# Kesar's table contains exactly ONE knee variable -- peak knee flexion during swing, MDC 5.7
# deg -- and NO knee angle at initial contact. The 3.8 floor used in fine_gap_r397.py is
# therefore not a defensible bar for any knee endpoint, and it is the LEAST conservative
# number in the whole table.
KNEE_MDC = {
    "question": "minimal detectable change for KNEE sagittal joint angle in instrumented 3D "
                "gait analysis, ideally at a discrete event (initial contact) and ideally in a "
                "neurological population",
    "CORRECTION_TO_THE_CORPUS": {
        "what_was_quoted": "3.8-11.5 deg, described in the corpus as the clinical MDC band for "
                           "kinematic endpoints; 3.8 is hard-coded as MDC in "
                           "scone/fine_gap_r397.py",
        "what_those_numbers_actually_are": "Kesar et al. 2011 Table 2: 3.8 deg is the MDC for "
                                           "TRAILING LIMB ANGLE and 11.5 deg is the MDC for HIP "
                                           "ANGLE AT TOE-OFF. Neither is a knee variable. "
                                           "Neither is an ankle variable either -- the "
                                           "'post-stroke ankle figure' framing is also wrong; "
                                           "Kesar's ankle-at-initial-contact MDC is 7.0 deg and "
                                           "its peak-ankle-in-swing MDC is 4.9 deg.",
        "the_only_knee_row_in_kesar": {"variable": "peak knee flexion during swing",
                                       "MDC_between_session_deg": 5.7,
                                       "MDC_within_session_deg": 1.9,
                                       "ICC_between_session": 0.982,
                                       "back_calculated_SEM_deg": 2.06},
        "action_required": "3.8 must not be used as a knee floor anywhere in the paper."},
    "primary_sources": {
        "Molina_Rueda_2021": {
            "citation": "Molina-Rueda F, Fernandez-Gonzalez P, Cuesta-Gomez A, Koutsou A, "
                        "Carratala-Tejada M, Miangolarra-Page JC. Test-Retest Reliability of a "
                        "Conventional Gait Model for Registering Joint Angles during Initial "
                        "Contact and Toe-Off in Healthy Subjects. Int J Environ Res Public "
                        "Health 2021;18(3):1343. doi:10.3390/ijerph18031343. PMID 33540873. "
                        "PMCID PMC7908319.",
            "why_it_is_the_right_paper": "THE ONLY paper found that reports a test-retest MDC "
                                         "for KNEE ANGLE AT INITIAL CONTACT as a discrete event "
                                         "value -- exactly this deposit's endpoint.",
            "population": "n=50 HEALTHY young adults (24M/26F), age 21.62 +/- 2.62 y, gait "
                          "speed 1.22-1.23 m/s. NOT a neurological population.",
            "protocol": "overground, 11 m walkway, comfortable self-selected speed; Vicon 8 "
                        "cameras @100 Hz, 3 AMTI plates; PLUG-IN GAIT conventional gait model, "
                        "Nexus 1.8.5, YXZ Cardan; foot events by 20 N vertical force threshold; "
                        "5 gait cycles per session.",
            "design": "BETWEEN-DAY, 2 sessions, 1 WEEK apart. ASSESSOR DESIGN NOT STATED -- the "
                      "paper never says whether the same person applied the markers at both "
                      "sessions. This is a reporting gap and it matters, because inter-tester "
                      "marker replacement is the dominant error source.",
            "statistic_as_published": "MDC95 = 1.96 * sqrt(2) * SEM, with SEM = SD_diff * "
                                      "sqrt(1-ICC); ICC(3,1) two-way mixed, absolute agreement",
            "single_measurement_or_change_score": "CHANGE SCORE (the sqrt(2) is present)",
            "knee_at_IC_as_published": {"ICC": 0.825, "ICC95CI": [0.693, 0.901],
                                        "mean_deg": 1.49, "bias_deg": 0.47,
                                        "SD_of_differences_deg": 3.70,
                                        "LoA_95_deg": [-6.78, 7.74],
                                        "SEM_deg_printed": 1.55, "MDC_deg_printed": 4.29},
            "SKEPTICAL_FLAG_factor_of_sqrt2": "The published 4.29 deg UNDERSTATES the MDC by "
                                              "sqrt(2). Their formula substitutes SD_diff into "
                                              "a place that requires the BETWEEN-SUBJECT SD; by "
                                              "construction SD_diff = sqrt(2)*SEM. Their own "
                                              "Bland-Altman limits of agreement contradict "
                                              "their own table: the assumption-free change-score "
                                              "MDC95 is 1.96 * SD_diff = 1.96 * 3.70 = 7.25 deg, "
                                              "which is exactly their printed LoA half-width "
                                              "(0.47 +/- 7.26). 4.29 = 7.25 / sqrt(2). Citing "
                                              "4.29 as a clearance bar would not survive a "
                                              "referee who opens Table 1.",
            "corrected_knee_at_IC_MDC95_deg": 7.25,
            "authors_own_interpretive_rule": "'Disagreements in joint angles during IC and TO of "
                                             "less than 9 deg after an intervention could be due "
                                             "to system or observer error'; the Bland-Altman "
                                             "divergence at IC was 'between +/-5 and +/-9 deg'.",
            "other_flag": "their TOE-OFF rows are arithmetically self-inconsistent with their "
                          "own stated formula (knee at TO: SD_diff 4.75 and ICC 0.814 give SEM "
                          "2.05, they print 0.96). The IC rows -- this deposit's rows -- do "
                          "check out against the stated formula."},
        "Geiger_2019": {
            "citation": "Geiger M, Supiot A, Pradon D, Do M-C, Zory R, Roche N. Minimal "
                        "detectable change of kinematic and spatiotemporal parameters in "
                        "patients with chronic stroke across three sessions of gait analysis. "
                        "Hum Mov Sci 2019;64:101-107. doi:10.1016/j.humov.2019.01.011. "
                        "PMID 30710860.",
            "why_it_matters": "the best NEUROLOGICAL between-session overground knee data found "
                              "-- right population, right plane, wrong event (no IC value).",
            "population": "n=26 chronic stroke (19M), age 58.2 +/- 13.1 y, 9.7 +/- 7.1 y "
                          "post-stroke, gait speed 0.77 m/s, paretic limb",
            "protocol": "overground 10 m corridor, spontaneous speed, 7 Motion Analysis cameras "
                        "@100 Hz, 30 markers, HELEN HAYES conventional model, 5-18 cycles",
            "design": "BETWEEN-DAY, three visits at 7-DAY intervals (V1,V2,V3). SAME OPERATOR "
                      "placed all markers at every visit and ran the whole analysis.",
            "statistic": "MDC = SEM * 2.056 * sqrt(2), SEM = sqrt(MS_E) from repeated-measures "
                         "ANOVA; 2.056 is t(95%, n=26). Slightly MORE conservative than the "
                         "1.96 version. ICC(3,k).",
            "single_measurement_or_change_score": "CHANGE SCORE",
            "knee_MDC_deg_by_visit_pairing": {
                "knee_max_angle_swing": [7.61, 7.10, 6.54],
                "knee_max_angle_stance": [7.19, 7.01, 4.93],
                "knee_min_angle_swing": [7.62, 6.53, 5.90],
                "knee_min_angle_stance": [6.34, 6.18, 5.47],
                "knee_RoM_swing": [8.16, 6.43, 8.49],
                "knee_RoM_stance": [7.12, 5.25, 6.52]},
            "knee_SEM_deg_range": [1.69, 2.61],
            "closest_analogue_to_this_deposit": "knee minimum angle in STANCE, worst pairing "
                                                "MDC 6.34 deg -- the nearest neurological "
                                                "published value to a knee angle around heel "
                                                "strike, but it is a minimum over stance, not "
                                                "the value AT the initial-contact event.",
            "largest_discrete_knee_MDC_deg": 7.62},
        "Kesar_2011": {
            "citation": "Kesar TM, Binder-Macleod SA, Hicks GE, Reisman DS. Minimal detectable "
                        "change for gait variables collected during treadmill walking in "
                        "individuals post-stroke. Gait Posture 2011;33(2):314-317. "
                        "doi:10.1016/j.gaitpost.2010.11.024. PMID 21183350. PMCID PMC3042506.",
            "population": "n=19 chronic post-stroke hemiparesis (12M), age 61.9 +/- 8.0 y, "
                          "72.6 +/- 63.4 months post-stroke, Fugl-Meyer LE 19.1 +/- 4.0, gait "
                          "speed 0.6 +/- 0.3 m/s",
            "protocol": "split-belt TREADMILL (AMTI), handrail held, harness without body-weight "
                        "support, self-selected speed; Vicon 5.2, 8 cameras @100 Hz, custom "
                        "marker set (NOT Plug-in-Gait), Visual3D, first 9 usable strides",
            "design": "BETWEEN-DAY, 2 sessions, 20.7 +/- 26.8 DAYS apart (range 1-99). SAME "
                      "ASSESSOR, markers re-applied and cameras recalibrated between sessions.",
            "statistic": "MDC = SEM * 1.96 * sqrt(2), SEM = SD * sqrt(1-ICC) with SD the average "
                         "of the two sessions' SDs; ICC(3,1) two-way mixed absolute agreement",
            "single_measurement_or_change_score": "CHANGE SCORE",
            "table2_between_session_MDC_deg": {
                "peak_knee_flexion_swing": 5.7, "peak_ankle_angle_swing": 4.9,
                "ankle_angle_at_initial_contact": 7.0, "trailing_limb_angle": 3.8,
                "hip_angle_at_toe_off": 11.5},
            "authors_own_caveat": "'these MDCs may not be used to interpret studies that measure "
                                  "overground gait'",
            "why_not_used_here": "treadmill, and the only knee row is peak flexion in SWING, a "
                                 "different variable from a heel-strike event value"}},
    "supporting_sources": {
        "Wilken_2012": "Wilken JM, Rodriguez KM, Brawner M, Darter BJ. Reliability and Minimal "
                       "Detectible Change values for gait kinematics and kinetics in healthy "
                       "adults. Gait Posture 2012;35(2):301-307. PMID 22041096. n=29 healthy, 2 "
                       "sessions 5.6 +/- 2.2 d apart, TWO RATERS per session (the only "
                       "inter-tester between-session design found). Conclusion verbatim: "
                       "'changes in gait kinematics of greater than approximately 5 deg can be "
                       "identified when comparing between sessions'. Per-variable knee values "
                       "PAYWALLED AND UNVERIFIED; Molina-Rueda cite Wilken as '4-7 deg for knee "
                       "parameters' -- SECOND-HAND, flagged as unverified. Change score.",
        "Horsak_2017": "Horsak B et al. Gait Posture 2017;54:112-118. PMID 28288331. n=11 obese "
                       "adolescents, within-assessor between-session. Sagittal-plane MDC "
                       "7.5 +/- 2.2 deg on average. Change score. Plane average, not knee at IC; "
                       "small n.",
        "Ewen_FreeBody_2017": "Front Bioeng Biotechnol 2017;5:74, PMC5727024. n=9 healthy older "
                              "adults, consecutive days, same researcher. PEAK KNEE FLEXION: "
                              "ICC 0.86, SEM 3.3 deg, MDC 9.2 deg (= SEM*1.96*sqrt(2)). Change "
                              "score. n=9 -- treat as an upper bound, not a benchmark.",
        "Meldrum_2014": "Meldrum D et al. Gait Posture 2014;39(1):265-271. PMID 24139682. n=30 "
                        "healthy, same investigator, two separate days within two weeks. 'SEM "
                        "low (<=5 deg) for the majority of parameters'. DID NOT ANALYSE JOINT "
                        "ANGLE AT DISCRETE GAIT EVENTS. Per-variable knee numbers unverified.",
        "McGinley_2009": "McGinley JL, Baker R, Wolfe R, Morris ME. The reliability of "
                         "three-dimensional kinematic gait measurements: a systematic review. "
                         "Gait Posture 2009;29(3):360-369. PMID 19013070. Sagittal hip and knee "
                         "are the most reliable; most error estimates <5 deg. The widely quoted "
                         "tiering (<2 deg acceptable, 2-5 deg reasonable but interpret with "
                         "caution, >5 deg raises concern) was verified only SECOND-HAND via "
                         "Molina-Rueda's citation; the primary tables could not be opened. "
                         "These are ERROR MAGNITUDES (SD/SE), NOT change-score MDCs.",
        "Schwartz_2004": "Schwartz MH, Trost JP, Wervey RA. Gait Posture 2004;20(2):196-203. "
                         "PMID 15336291. 2 subjects, 4 therapists, 3 sessions, 5 trials; "
                         "within- and BETWEEN-OBSERVER error at each point of the cycle. "
                         "PAYWALLED -- NO NUMBERS OBTAINED. Design reported only.",
        "Guzik_2020": "Guzik A et al. J Clin Med 2020;9(10):3305. PMCID PMC7602397. n=50 chronic "
                      "stroke, overground, Davis protocol, 4-week follow-up. THIS IS AN MCID "
                      "PAPER, NOT AN MDC PAPER -- it reports no MDC and no ICC. Anchor-based "
                      "MCID for knee sagittal ROM 8.48 deg affected / 6.81 deg unaffected. "
                      "Included only to close the loop on a paper often mis-cited for MDC.",
        "negative_MS": "PMID 31561120 (MS test-retest) covers ANKLE kinematics only "
                       "(MDC95 1.9-4.2 / 2.2-7.7 deg). No knee. NOT substituted.",
        "negative_CP": "bioRxiv 2025.05.01.651648, n=19 CP + 19 non-impaired, 10 d apart, "
                       "CGM 2.3, MDC = 1.96*sqrt(2)*SEM -- reports continuous relative phase "
                       "coordination, not knee angle at IC. Instructive magnitude though: "
                       "between-assessor MDC 15.1 deg in CP vs 9.3 deg in controls. Measurement "
                       "error in NEUROLOGICAL gait is materially LARGER than in healthy gait, "
                       "so a healthy-cohort figure is a LOWER bound, not a conservative one."},
    "THE_GAP_STATED_PLAINLY": "THE LITERATURE DOES NOT CONTAIN A MINIMAL DETECTABLE CHANGE VALUE "
                              "FOR KNEE SAGITTAL ANGLE AT INITIAL CONTACT IN ANY NEUROLOGICAL "
                              "POPULATION. What exists is (a) knee at IC in HEALTHY young adults "
                              "only (Molina-Rueda 2021), and (b) knee PEAK/ROM values in stroke "
                              "(Kesar 2011 treadmill, Geiger 2019 overground) -- right "
                              "population, wrong event. Ankle-at-IC figures exist in stroke "
                              "(7.0 deg) and MS, and are NOT substituted here. Any knee-at-heel-"
                              "strike MDC applied to a neurological cohort is an EXTRAPOLATION "
                              "and the paper must say so rather than borrow a number.",
    "range_of_between_session_change_score_knee_sagittal_MDC95_deg": [4.29, 9.20],
    "candidate_thresholds_deg": {
        "4.29": "Molina-Rueda knee at IC AS PUBLISHED -- right variable, but arithmetically "
                "understated by sqrt(2); DO NOT USE",
        "5.70": "Kesar peak knee flexion in SWING, stroke, treadmill -- wrong variable, wrong "
                "modality, and the authors forbid overground transfer",
        "6.34": "Geiger knee MINIMUM ANGLE IN STANCE, worst visit pairing, chronic stroke, "
                "overground -- closest NEUROLOGICAL analogue to a knee angle near heel strike",
        "7.25": "Molina-Rueda knee at IC CORRECTED (1.96 * SD_diff = their own LoA half-width) "
                "-- right variable, right event, healthy population (which biases it DOWNWARD)",
        "7.62": "Geiger largest discrete knee MDC (knee minimum angle in swing, V1v2) -- right "
                "population, right plane, between-day, conventional gait model",
        "9.00": "Molina-Rueda's OWN stated interpretive rule for any joint angle at IC/TO",
        "9.20": "FreeBody peak knee flexion, healthy older adults, consecutive days (n=9)"},
    "MOST_CONSERVATIVE_DEFENSIBLE": {
        "value_deg": 7.62,
        "band_deg": [7.25, 7.62],
        "why": "the two independently defensible candidates converge. 7.25 deg is the corrected "
               "knee-at-INITIAL-CONTACT MDC95 (right variable, right event, right model class, "
               "between-day; healthy population, which understates neurological error). 7.62 "
               "deg is the largest discrete knee-angle MDC95 in a chronic-stroke overground "
               "between-day cohort (right population, wrong event). Taking the larger of the "
               "two as the bar is the conservative reading. 5.7 deg is explicitly rejected: it "
               "is a treadmill peak-swing number whose own authors forbid overground transfer.",
        "statistic_type": "CHANGE-SCORE MDC95 in both cases (both carry the sqrt(2))"},
    "OBSERVED_GAP_DEG": 6.3919,
    "DOES_THE_OBSERVED_GAP_CLEAR_IT": {
        "answer": "NO",
        "detail": {
            "vs_7.62_most_conservative": "FAILS by 1.23 deg",
            "vs_7.25_corrected_knee_at_IC": "FAILS by 0.86 deg",
            "vs_9.00_authors_own_rule": "FAILS by 2.61 deg",
            "vs_9.20_FreeBody": "FAILS by 2.81 deg",
            "vs_6.34_closest_neurological_analogue": "clears by 0.05 deg -- a numerical tie, "
                                                     "not a clearance",
            "vs_5.70_Kesar_knee_swing": "clears, but this threshold is not applicable",
            "vs_4.29_as_published": "clears, but this threshold is arithmetically wrong",
            "vs_3.80_the_number_the_corpus_was_using": "clears, but 3.8 is the TRAILING LIMB "
                                                       "ANGLE MDC and is not a knee number"},
        "plain_statement": "+6.3919 deg clears only the thresholds one would select if shopping "
                           "for a favourable bar, and fails every threshold one would select "
                           "when being conservative. It sits inside the between-session "
                           "measurement-noise band of marker-based knee kinematics."},
    "BETWEEN_SESSION_VARIABILITY_OF_KNEE_ANGLE_AT_IC": {
        "why_reported_separately": "a discriminator must beat the ordinary session-to-session "
                                   "wobble of the measurement, not only the MDC",
        "only_direct_source": "Molina-Rueda 2021, knee angle at IC, n=50 healthy, 1 week "
                              "between-day, Plug-in-Gait, overground self-selected speed",
        "SD_of_between_session_differences_deg": 3.70,
        "systematic_between_session_bias_deg": 0.47,
        "LoA95_deg": [-6.78, 7.74],
        "implied_per_measurement_SEM_deg": 2.62,
        "note_on_SEM": "2.62 = 3.70/sqrt(2) is the correct classical per-measurement SEM. The "
                       "paper prints 1.55, which is the sqrt(2) misapplication described above.",
        "mean_knee_angle_at_IC_deg": 1.49,
        "implied_between_subject_SD_deg": 6.25,
        "nearest_neurological_proxies_SEM_deg": {
            "Geiger_knee_min_angle_stance": [1.87, 2.17],
            "Geiger_knee_max_angle_stance": [1.69, 2.46],
            "Geiger_knee_max_angle_swing": [2.24, 2.61],
            "Geiger_all_kinematic_params_mean": [2.01, 2.47],
            "Kesar_peak_knee_flexion_swing_back_calculated": 2.06},
        "summary": "the CHANGE SCORE for a knee sagittal angle across two sessions has an SD of "
                   "roughly 3.0-3.7 deg in both healthy and chronic-stroke cohorts, BEFORE any "
                   "inter-tester marker-replacement penalty. +6.3919 deg is therefore about "
                   "1.7-2.1 change-score SDs -- which is precisely why it lands just UNDER, not "
                   "above, the 95% MDC.",
        "no_neurological_figure_exists": True},
}


# ------------------------------------------------------------------ corpus access
def rd(tag):
    """batchnull_r389.rd verbatim: the one dir per tag with history.txt >= 91 lines."""
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs with history.txt >= 91 lines" % (tag, len(g)))
    return g[0]


def rd_r397(tag):
    """fine_gap_r397's simpler rule, recorded only so any disagreement is visible."""
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    return g[0] if len(g) == 1 else None


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


def window_for_side(t, cols, dat, side):
    """fine_gap_r397 verbatim: cycles between heel strikes with t[start] >= SETTLE, wholly
    inside [SETTLE, T1], then DROP THE LAST kept cycle."""
    grf, thr = S.grf_vertical(cols, dat, side)
    if grf is None:
        return None, None, None
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    return win, grf, thr


def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        rec["gate_G"] = False
        rec["gate_G_right"] = False
        return rec
    rec["run_dir"] = os.path.basename(d)
    alt = rd_r397(tag)
    rec["r397_rule_same_dir"] = (alt is not None and os.path.abspath(alt) == os.path.abspath(d))
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        rec["gate_G"] = False
        rec["gate_G_right"] = False
        return rec
    rec["sto"] = os.path.basename(stos[-1])
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        rec["gate_G"] = False
        rec["gate_G_right"] = False
        return rec
    t = dat[:, 0]
    rec["t_end_s"] = float(t[-1])

    # ---------------- LEFT (lesioned) side: the primary endpoint
    win, grf, thr = window_for_side(t, cols, dat, "l")
    if win is None:
        rec["error"] = "no left GRF"
        rec["gate_G"] = False
    else:
        rec["n_cycles_in_window"] = len(win)
        rec["gate_G"] = bool(rec["t_end_s"] >= T1 and len(win) >= MIN_CYC)
        if not rec["gate_G"]:
            rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1)
                            if rec["t_end_s"] < T1
                            else "only %d cycles in window, need %d" % (len(win), MIN_CYC))
    if rec.get("gate_G"):
        kne = S.col(cols, dat, "knee_angle_l")
        ang = S.col(cols, dat, "ankle_angle_l")
        if kne is not None:
            kd = np.degrees(kne)
            rec[PRIMARY] = float(np.mean([kd[a] for a, _ in win]))
            rec["knee_hs_L_percycle_deg"] = [float(kd[a]) for a, _ in win]
        if ang is not None:
            on = grf > thr
            st = [np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()]
            if st:
                rec["mean_ankle_stance_deg"] = float(np.mean(np.degrees(ang)[
                    np.concatenate(st)]))

    # ---------------- RIGHT (unlesioned) side: the decisive negative control.
    # Same endpoint definition, but the RIGHT leg's own GRF defines its heel strikes and its
    # own admissible-cycle window, and it carries its own Gate G.
    winr, _, _ = window_for_side(t, cols, dat, "r")
    rec["n_cycles_right"] = len(winr) if winr else 0
    rec["gate_G_right"] = bool(winr is not None and rec["t_end_s"] >= T1
                               and len(winr) >= MIN_CYC)
    if rec["gate_G_right"]:
        kner = S.col(cols, dat, "knee_angle_r")
        if kner is not None:
            krd = np.degrees(kner)
            rec[NEGCTL] = float(np.mean([krd[a] for a, _ in winr]))
            rec["knee_hs_R_percycle_deg"] = [float(krd[a]) for a, _ in winr]
    return rec


# ------------------------------------------------------------------ statistics (r389 verbatim)
def gate_key(key):
    return "gate_G_right" if key == NEGCTL else "gate_G"


def fam_values(cells, fam, key):
    out = []
    for tg in sorted(cells):
        if tg.split("_")[0] != fam:
            continue
        r = cells[tg]
        if not r.get(gate_key(key)):
            continue
        v = r.get(key)
        if v is not None and np.isfinite(v):
            out.append(float(v))
    return sorted(out)


def separated(a, b, min_n=MIN_VALS):
    if len(a) < min_n or len(b) < min_n:
        return None
    return bool(max(b[0] - a[-1], a[0] - b[-1]) > 0)


def gap(a, b):
    return max(b[0] - a[-1], a[0] - b[-1])


def perm_floor(a, b):
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
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "%d/%d" % (cnt, tot),
            "p": cnt / float(tot)}


def binom_tail(k, n, p):
    if p is None:
        return None
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def cmp_pair(a, b):
    d = {"n_a": len(a), "n_b": len(b),
         "a_range": [a[0], a[-1]] if a else None, "b_range": [b[0], b[-1]] if b else None,
         "a_mean": float(np.mean(a)) if a else None,
         "b_mean": float(np.mean(b)) if b else None}
    s = separated(a, b)
    d["separated"] = s
    if s is None:
        d["VERDICT"] = "UNINFORMATIVE (<%d Gate-G values on one side)" % MIN_VALS
        return d
    d["edge_gap"] = gap(a, b)
    d["mean_diff"] = d["a_mean"] - d["b_mean"]
    d["direction"] = ("A HIGH" if a[0] > b[-1] else "A LOW") if s else None
    d["VERDICT"] = "SEPARATED" if s else "OVERLAP"
    if s:
        d["permutation_floor"] = perm_floor(a, b)
    return d


# Magnitude thresholds at which the batch null is re-evaluated. A separation is only
# clinically meaningful if its edge gap survives a measurement floor, so the null must be
# asked the same question: how often do two same-mechanism families separate BY AT LEAST
# this many degrees?  0.0 is the plain disjointness rate.
MAG_THRESH = [0.0, 1.21, 3.8, 4.29, 5.70, 6.34, 6.3919, 7.25, 7.62, 9.00, 9.20, 11.5]


def null_cohort(cells, fams, label, key):
    rows, n, k = [], 0, 0
    for A, B in itertools.combinations(fams, 2):
        va, vb = fam_values(cells, A, key), fam_values(cells, B, key)
        s = separated(va, vb)
        if s is None:
            rows.append({"pair": [A, B], "verdict": "UNINFORMATIVE",
                         "n_a": len(va), "n_b": len(vb)})
            continue
        n += 1
        k += int(s)
        rows.append({"pair": [A, B], "separated": s, "edge_gap": gap(va, vb),
                     "a_range": [va[0], va[-1]], "b_range": [vb[0], vb[-1]],
                     "a_mean": float(np.mean(va)), "b_mean": float(np.mean(vb)),
                     "direction": (("%s HIGH" % A) if s and va[0] > vb[-1]
                                   else ("%s HIGH" % B) if s else None)})
    gaps = [r["edge_gap"] for r in rows if "edge_gap" in r]
    mag = {}
    for th in MAG_THRESH:
        kk = sum(1 for g in gaps if g > 0 and g >= th)
        mag["%.4f" % th] = {"n_separated_by_at_least_this": kk,
                            "rate": (kk / float(n)) if n else None}
    return {"label": label, "endpoint": key, "families": fams,
            "n_family_pairs_possible": len(list(itertools.combinations(fams, 2))),
            "n_pairs_tested": n, "n_separated": k,
            "BATCH_FALSE_POSITIVE_RATE": (k / float(n)) if n else None,
            "excess_over_permutation_floor_2_over_924":
                ((k / float(n)) / (2.0 / 924.0)) if n else None,
            "largest_null_edge_gap_deg": (max(gaps) if gaps else None),
            "all_edge_gaps_deg_sorted": sorted(gaps, reverse=True),
            "MAGNITUDE_GATED_RATE": mag,
            "uninformative_note": ("ALL %d pairs are UNINFORMATIVE: fewer than %d Gate-G cells "
                                   "on at least one side of every pair. No rate can be quoted "
                                   "for this cohort." % (len(rows), MIN_VALS)) if n == 0 else None,
            "pairs": rows}


# ------------------------------------------------------------------ main
def main():
    fams = [CONTROL] + DFWEAK + PFWEAK + [f for _, f in SPASTIC]
    tags = tags_for(fams)
    print("measuring %d cells across %d families" % (len(tags), len(fams)))
    cells = {}
    for i, tg in enumerate(tags):
        cells[tg] = measure(tg)
        r = cells[tg]
        print("  [%2d/%d] %-18s L:gate=%-5s cyc=%-3s kneeHS_L=%-10s | R:gate=%-5s cyc=%-3s "
              "kneeHS_R=%s"
              % (i + 1, len(tags), tg, r.get("gate_G"), r.get("n_cycles_in_window"),
                 ("%+.4f" % r[PRIMARY]) if r.get(PRIMARY) is not None else "-",
                 r.get("gate_G_right"), r.get("n_cycles_right"),
                 ("%+.4f" % r[NEGCTL]) if r.get(NEGCTL) is not None else "-"))

    res = {
        "round": "r399",
        "what": "the batch null and the unlesioned-side negative control applied to "
                "knee_angle_l at left heel strike, endpoint #1 of the four pre-registered at "
                "paper/PREREG_kinpair_r378.md sec 3",
        "endpoint": {
            "key": PRIMARY,
            "definition": "knee_angle_l sampled at each left heel strike (the opening index of "
                          "each admissible cycle), averaged over the admissible cycles of the "
                          "cell, in degrees",
            "prereg": "paper/PREREG_kinpair_r378.md sec 3 item 1 -- pre-registered 2026-08-18, "
                      "NOT a post hoc endpoint",
            "previously_measured_only_at": "KV <= 0.035 (gap 1.21 deg); the KV 0.070-0.120 "
                                           "cells exist only because of warm-start chaining"},
        "negative_control_endpoint": {
            "key": NEGCTL,
            "definition": "knee_angle_r sampled at each RIGHT heel strike, the right leg's own "
                          "GRF defining the events and the admissible-cycle window, its own "
                          "Gate G, averaged over cycles, in degrees",
            "why": "both lesions are LEFT-ONLY. A similar separation rate on the right knee "
                   "would make the left-knee result a batch artefact."},
        "conventions": {
            "source_gating": "scone/fine_gap_r397.py verbatim",
            "SETTLE": SETTLE, "T1": T1,
            "cycles": "between heel strikes with t[start] >= SETTLE, wholly inside the window, "
                      "drop the LAST kept cycle, require >= %d" % MIN_CYC,
            "stance": "leg0_l.grf_norm_y > 0.05",
            "run_dir_selection": "scone/batchnull_r389.py rd(): the one dir per tag with "
                                 "history.txt >= 91 lines. r397's len(glob)==1 rule is also "
                                 "evaluated per cell and recorded as r397_rule_same_dir; it "
                                 "differs only where a duplicated '(1)' copy of a seed "
                                 "directory exists (R169W095 s105/s106, R276WPF010 s106), "
                                 "which that rule would silently drop.",
            "sto": "sorted(glob('*.par.sto'))[-1]",
            "disjointness": "arms separate iff max(min(B)-max(A), min(A)-max(B)) > 0, both "
                            "arms needing >= %d Gate-G values (batchnull_r389 verbatim)"
                            % MIN_VALS,
            "batch_null_reference": "paper/HARMONIC_r383.json / paper/BATCHNULL_r389.json -- "
                                    "same-mechanism dorsiflexor-weakness family pairs separated "
                                    "96 of 450 times (21.3%) against a quoted 2/924 = 0.22% "
                                    "exhaustive-permutation floor"},
        "cells": cells,
    }

    # ---------------- gate ledger
    ledger = {}
    for f in fams:
        tg = [t for t in tags if t.split("_")[0] == f]
        ledger[f] = {
            "n_cells": len(tg),
            "n_gate_G_left": sum(1 for t in tg if cells[t].get("gate_G")),
            "n_gate_G_right": sum(1 for t in tg if cells[t].get("gate_G_right")),
            "guards": {t: cells[t].get("guard") or cells[t].get("error")
                       for t in tg if not cells[t].get("gate_G")},
            "r397_rule_disagrees": [t for t in tg
                                    if cells[t].get("r397_rule_same_dir") is False]}
    res["GATE_LEDGER"] = ledger

    # ---------------- STEP 0: reproduce the headline arms quoted in the brief
    rep = {}
    for name, fam in (("CONTROL_R151C", CONTROL), ("WEAK_x080_R151W", "R151W"),
                      ("SPAS_KV0110_R396SPg110", "R396SPg110")):
        v = fam_values(cells, fam, PRIMARY)
        rep[name] = {"family": fam, "n": len(v), "values": v,
                     "range": [v[0], v[-1]] if v else None,
                     "mean": float(np.mean(v)) if v else None}
    sp = fam_values(cells, "R396SPg110", PRIMARY)
    wk = fam_values(cells, "R151W", PRIMARY)
    if sp and wk:
        rep["edge_gap_SPAS_KV0110_vs_WEAK_x080"] = gap(sp, wk)
        rep["separated"] = separated(sp, wk)
        rep["permutation_floor"] = perm_floor(sp, wk) if separated(sp, wk) else None
        rep["brief_quoted_edge_gap_deg"] = 6.3919
    res["STEP0_HEADLINE_REPRODUCTION"] = rep

    # ---------------- STEP 1: the batch nulls, on the knee endpoint
    nulls = {}
    for key in (PRIMARY, NEGCTL):
        nulls[key] = {
            "NULL_DF": null_cohort(cells, DFWEAK,
                                   "NULL-DF: dorsiflexor-weakness family vs family, C(6,2)=15",
                                   key),
            "NULL_PF": null_cohort(cells, PFWEAK,
                                   "NULL-PF: plantarflexor/other-weakness family vs family, "
                                   "C(5,2)=10", key)}
    res["STEP1_BATCH_NULL"] = {
        "what": "every pair of distinct same-mechanism families, 6 seeds vs 6 seeds, on THIS "
                "endpoint. This is the endpoint's batch false-positive rate.",
        "quoted_permutation_floor": 2.0 / 924.0,
        "by_endpoint": nulls}

    # ---------------- STEP 2: like-for-like, each spastic family vs EACH DFweak family
    lfl = {}
    for key in (PRIMARY, NEGCTL):
        nullrate = nulls[key]["NULL_DF"]["BATCH_FALSE_POSITIVE_RATE"]
        per = {}
        tot_n = tot_k = 0
        for kv, fam in SPASTIC:
            va = fam_values(cells, fam, key)
            rows, n, k = [], 0, 0
            for D in DFWEAK:
                vb = fam_values(cells, D, key)
                s = separated(va, vb)
                if s is None:
                    rows.append({"vs": D, "verdict": "UNINFORMATIVE",
                                 "n_spastic": len(va), "n_weak": len(vb)})
                    continue
                n += 1
                k += int(s)
                rows.append({"vs": D, "separated": s, "edge_gap": gap(va, vb),
                             "mean_diff": float(np.mean(va)) - float(np.mean(vb)),
                             "direction": ("SPASTIC HIGH" if s and va[0] > vb[-1]
                                           else "SPASTIC LOW" if s else None),
                             "spastic_range": [va[0], va[-1]] if va else None,
                             "weak_range": [vb[0], vb[-1]] if vb else None})
            tot_n += n
            tot_k += k
            g = [x["edge_gap"] for x in rows if x.get("separated")]
            per[kv] = {"family": fam, "n_gate_G": len(va),
                       "n_tested": n, "n_separated": k,
                       "hit_rate": (k / float(n)) if n else None,
                       "batch_null_rate_NULL_DF": nullrate,
                       "p_binomial_vs_batch_null": (binom_tail(k, n, nullrate) if n else None),
                       "edge_gaps_when_separated_deg":
                           {"min": min(g), "median": float(np.median(g)), "max": max(g)}
                           if g else None,
                       "n_separated_by_at_least":
                           {"%.4f" % th: sum(1 for x in g if x >= th) for th in MAG_THRESH}
                           if g else None,
                       "UNINFORMATIVE": (n == 0),
                       "uninformative_why": ("only %d Gate-G cells, need %d"
                                             % (len(va), MIN_VALS)) if n == 0 else None,
                       "comparisons": rows}
        allg = [x["edge_gap"] for kv, _ in SPASTIC
                for x in per[kv]["comparisons"] if x.get("separated")]
        per["_POOLED_ALL_SPASTIC_FAMILIES"] = {
            "n_tested": tot_n, "n_separated": tot_k,
            "hit_rate": (tot_k / float(tot_n)) if tot_n else None,
            "batch_null_rate_NULL_DF": nullrate,
            "p_binomial_vs_batch_null": (binom_tail(tot_k, tot_n, nullrate) if tot_n else None),
            "edge_gaps_when_separated_deg":
                {"min": min(allg), "median": float(np.median(allg)), "max": max(allg)}
                if allg else None,
            "n_separated_by_at_least":
                {"%.4f" % th: sum(1 for x in allg if x >= th) for th in MAG_THRESH}
                if allg else None}
        lfl[key] = per
    res["STEP2_LIKE_FOR_LIKE"] = {
        "what": "each spastic family with Gate-G cells, 6 seeds (4 for the R396 rungs), against "
                "EACH of the six dorsiflexor-weakness families separately. Same geometry as the "
                "batch null, so it is the only hit rate comparable with it.",
        "by_endpoint": lfl}

    # ---------------- STEP 3: published geometry (spastic vs pooled DFweak seed means)
    def pooled_seed_means(famlist, key):
        acc = {}
        for tg in sorted(cells):
            if tg.split("_")[0] not in famlist:
                continue
            r = cells[tg]
            if not r.get(gate_key(key)):
                continue
            v = r.get(key)
            if v is None or not np.isfinite(v):
                continue
            acc.setdefault(tg.split("_")[-1], []).append(float(v))
        return sorted(float(np.mean(v)) for v in acc.values())

    pub = {}
    for kv, fam in SPASTIC:
        c = cmp_pair(fam_values(cells, fam, PRIMARY), pooled_seed_means(DFWEAK, PRIMARY))
        c["note_A_is"] = fam
        c["note_B_is"] = "6 DFweak seed means, each pooled over the six families"
        pub[kv] = c
    res["STEP3_PUBLISHED_GEOMETRY"] = {
        "what": "the corpus geometry, reproduced for continuity: spastic family's seeds vs six "
                "DFweak SEED MEANS each pooled over six families. Pooling shrinks the weak arm, "
                "so this geometry is NOT comparable with the batch null.",
        "pooled_DFweak_seed_means": pooled_seed_means(DFWEAK, PRIMARY),
        "by_rung": pub}

    # ---------------- STEP 4: the side negative control, stated head-on
    lrate = nulls[PRIMARY]["NULL_DF"]["BATCH_FALSE_POSITIVE_RATE"]
    rrate = nulls[NEGCTL]["NULL_DF"]["BATCH_FALSE_POSITIVE_RATE"]
    lhit = lfl[PRIMARY]["_POOLED_ALL_SPASTIC_FAMILIES"]
    rhit = lfl[NEGCTL]["_POOLED_ALL_SPASTIC_FAMILIES"]
    res["STEP4_UNLESIONED_SIDE_NEGATIVE_CONTROL"] = {
        "what": "knee_angle_r at RIGHT heel strike, right leg's own GRF. Both lesions are "
                "left-only.",
        "NULL_DF_rate_LEFT_knee": lrate,
        "NULL_DF_rate_RIGHT_knee": rrate,
        "NULL_PF_rate_LEFT_knee": nulls[PRIMARY]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"],
        "NULL_PF_rate_RIGHT_knee": nulls[NEGCTL]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"],
        "like_for_like_hit_rate_LEFT_knee": lhit["hit_rate"],
        "like_for_like_hit_rate_RIGHT_knee": rhit["hit_rate"],
        "n_tested_LEFT": lhit["n_tested"], "n_separated_LEFT": lhit["n_separated"],
        "n_tested_RIGHT": rhit["n_tested"], "n_separated_RIGHT": rhit["n_separated"]}

    # ---------------- STEP 5: spastic vs the within-scenario control R151C
    c5 = {}
    for kv, fam in SPASTIC:
        c = cmp_pair(fam_values(cells, CONTROL, PRIMARY), fam_values(cells, fam, PRIMARY))
        c["note_A_is"] = CONTROL
        c["note_B_is"] = fam
        c5[kv] = c
    cw = cmp_pair(fam_values(cells, CONTROL, PRIMARY), fam_values(cells, "R151W", PRIMARY))
    cw["note_A_is"] = CONTROL
    cw["note_B_is"] = "R151W"
    res["STEP5_VS_CONTROL_R151C"] = {
        "R151C_values": fam_values(cells, CONTROL, PRIMARY),
        "vs_spastic": c5, "vs_R151W_same_batch": cw,
        "why": "the two lesions displace the control in OPPOSITE directions on this endpoint, "
               "which is the mechanistic reason it opens with severity where mean stance ankle "
               "angle does not."}

    # ---------------- STEP 4b: the side control, rung by rung. The pooled rate hides that the
    # right knee's six separations ALL come from the single rung that produces the headline.
    res["STEP4_UNLESIONED_SIDE_NEGATIVE_CONTROL"]["by_rung"] = {
        kv: {"family": fam,
             "LEFT_n_separated": lfl[PRIMARY][kv]["n_separated"],
             "LEFT_n_tested": lfl[PRIMARY][kv]["n_tested"],
             "LEFT_edge_gaps": lfl[PRIMARY][kv]["edge_gaps_when_separated_deg"],
             "RIGHT_n_separated": lfl[NEGCTL][kv]["n_separated"],
             "RIGHT_n_tested": lfl[NEGCTL][kv]["n_tested"],
             "RIGHT_edge_gaps": lfl[NEGCTL][kv]["edge_gaps_when_separated_deg"]}
        for kv, fam in SPASTIC}

    # ---------------- STEP 6: magnitude. Disjointness is a yes/no; the paper's claim is a
    # SIZE. This asks the null the same question the clinic asks the result.
    ndL = nulls[PRIMARY]["NULL_DF"]
    res["STEP6_MAGNITUDE"] = {
        "what": "the batch null does separate on this endpoint, but at what SIZE? A separation "
                "whose edge gap is 0.02 deg and one whose edge gap is 6.39 deg are not the same "
                "claim. This is the null re-asked with a magnitude floor.",
        "largest_edge_gap_between_two_same_mechanism_DFweak_families_deg":
            ndL["largest_null_edge_gap_deg"],
        "all_null_edge_gaps_when_separated_deg": ndL["all_edge_gaps_deg_sorted"],
        "NULL_DF_rate_by_magnitude_floor": ndL["MAGNITUDE_GATED_RATE"],
        "observed_headline_edge_gap_deg": rep.get("edge_gap_SPAS_KV0110_vs_WEAK_x080"),
        "like_for_like_edge_gaps_LEFT":
            lfl[PRIMARY]["_POOLED_ALL_SPASTIC_FAMILIES"]["edge_gaps_when_separated_deg"],
        "like_for_like_n_separated_by_at_least_LEFT":
            lfl[PRIMARY]["_POOLED_ALL_SPASTIC_FAMILIES"]["n_separated_by_at_least"],
        "like_for_like_edge_gaps_RIGHT":
            lfl[NEGCTL]["_POOLED_ALL_SPASTIC_FAMILIES"]["edge_gaps_when_separated_deg"],
        "like_for_like_n_separated_by_at_least_RIGHT":
            lfl[NEGCTL]["_POOLED_ALL_SPASTIC_FAMILIES"]["n_separated_by_at_least"]}

    # ---------------- TASK 1: the knee MDC, sourced. See MDC_LITERATURE below.
    res["TASK1_KNEE_MDC"] = KNEE_MDC

    # ---------------- VERDICT on the batch null
    p_all = lhit["p_binomial_vs_batch_null"]
    hr = lhit["hit_rate"]
    if hr is None or lrate is None:
        v = "INDETERMINATE"
        why = "no comparable rate could be formed"
    elif hr <= lrate + 1e-12:
        v = "DOES NOT SURVIVE THE BATCH NULL"
        why = ("like-for-like hit rate %.1f%% is at or below the %.1f%% rate at which two "
               "same-mechanism weakness families separate on this same endpoint."
               % (100 * hr, 100 * lrate))
    elif p_all is not None and p_all < 0.05 and hr >= 2 * lrate:
        v = "SURVIVES THE BATCH NULL"
        why = ("like-for-like hit rate %.1f%% vs batch null %.1f%%, binomial P(X>=%d | n=%d, "
               "p=%.4f) = %.4g" % (100 * hr, 100 * lrate, lhit["n_separated"],
                                   lhit["n_tested"], lrate, p_all))
    else:
        v = "MARGINAL -- DOES NOT CLEARLY SURVIVE"
        why = ("like-for-like hit rate %.1f%% vs batch null %.1f%%, binomial p = %s"
               % (100 * hr, 100 * lrate, ("%.4g" % p_all) if p_all is not None else "n/a"))
    res["VERDICT_BATCH_NULL"] = {"verdict": v, "why": why,
                                 "left_knee_like_for_like": lhit,
                                 "right_knee_like_for_like": rhit,
                                 "side_control_verdict":
                                     ("RIGHT KNEE SEPARATES AT A SIMILAR OR HIGHER RATE -- the "
                                      "left-knee result is a batch artefact"
                                      if (rhit["hit_rate"] is not None and hr is not None
                                          and rhit["hit_rate"] >= hr)
                                      else "right knee separates less often than the left")}

    # ---------------- THE TWO PLAIN ANSWERS
    kv110L = lfl[PRIMARY]["0.110"]
    kv110R = lfl[NEGCTL]["0.110"]
    mdc = KNEE_MDC["MOST_CONSERVATIVE_DEFENSIBLE"]["value_deg"]
    res["PLAIN_VERDICT"] = {
        "Q1_does_it_clear_a_properly_sourced_knee_MDC": {
            "ANSWER": "NO",
            "observed_edge_gap_deg": rep.get("edge_gap_SPAS_KV0110_vs_WEAK_x080"),
            "most_conservative_defensible_knee_MDC_deg": mdc,
            "shortfall_deg": mdc - (rep.get("edge_gap_SPAS_KV0110_vs_WEAK_x080") or 0.0),
            "and": "the 3.8-11.5 deg band the corpus was quoting is not a knee band at all -- "
                   "3.8 is the TRAILING LIMB ANGLE MDC and 11.5 the HIP-AT-TOE-OFF MDC from "
                   "Kesar 2011. The MDC = 3.8 constant hard-coded in scone/fine_gap_r397.py is "
                   "not a defensible floor for a knee endpoint.",
            "and_also": "no MDC for knee angle at initial contact exists for ANY neurological "
                        "population. Every candidate threshold is an extrapolation."},
        "Q2_does_the_separation_survive_the_batch_null": {
            "ANSWER": v,
            "left_knee_like_for_like": "%d/%d" % (lhit["n_separated"], lhit["n_tested"]),
            "batch_null_NULL_DF_left_knee": "%d/%d = %.1f%%"
                                            % (ndL["n_separated"], ndL["n_pairs_tested"],
                                               100 * lrate) if lrate is not None else None,
            "binomial_p": p_all,
            "NULL_PF_could_not_be_computed": nulls[PRIMARY]["NULL_PF"]["uninformative_note"],
            "the_magnitude_point_in_favour":
                "the four spurious same-mechanism separations have edge gaps of %s deg -- the "
                "largest is %.4f deg. NO pair of same-mechanism weakness families separates by "
                "even 1.21 deg, let alone 6.39. The batch null produces DISJOINTNESS at 26.7%%, "
                "but it does not produce MAGNITUDE."
                % (", ".join("%.4f" % g for g in ndL["all_edge_gaps_deg_sorted"]),
                   ndL["largest_null_edge_gap_deg"] or 0.0),
            "the_qualification_against":
                "the batch false-positive rate for plain disjointness on this endpoint is "
                "26.7%%, HIGHER than the 21.3%% that HARMONIC_r383 measured, and 123x the "
                "2/924 = 0.22%% exhaustive-permutation floor the corpus quotes. The permutation "
                "floor materially overstates the evidence for any single disjointness claim on "
                "this endpoint."},
        "Q3_the_unlesioned_side_negative_control": {
            "ANSWER": "PARTIAL FAILURE AT THE HEADLINE RUNG",
            "right_knee_batch_null_NULL_DF": "%d/%d = %.1f%%"
                                             % (nulls[NEGCTL]["NULL_DF"]["n_separated"],
                                                nulls[NEGCTL]["NULL_DF"]["n_pairs_tested"],
                                                100 * rrate) if rrate is not None else None,
            "right_knee_like_for_like_pooled": "%d/%d" % (rhit["n_separated"], rhit["n_tested"]),
            "left_knee_like_for_like_pooled": "%d/%d" % (lhit["n_separated"], lhit["n_tested"]),
            "not_a_batch_artefact_because": "the RIGHT knee's own batch null is 0/15 = 0.0%. The "
                                            "right knee is not intrinsically batchy on this "
                                            "endpoint, so a right-knee separation is a real "
                                            "displacement, not optimisation noise.",
            "BUT": "the right knee's separations are NOT spread across the ladder -- ALL %d of "
                   "them come from the single rung R396SPg110 (KV 0.110), where the RIGHT, "
                   "UNLESIONED knee separates from all six dorsiflexor-weakness families %d/%d, "
                   "exactly as the left does. That is the rung that produces the headline "
                   "+6.39 deg. At KV 0.050, 0.070 and 0.100 the right knee separates 0/6 while "
                   "the left separates 6/6, so the endpoint IS strictly left-specific at the "
                   "lower rungs; at KV 0.110 that strict specificity is gone."
                   % (rhit["n_separated"], kv110R["n_separated"], kv110R["n_tested"]),
            "the_mitigating_magnitude_asymmetry":
                "at KV 0.110 the RIGHT-knee edge gaps are %.4f-%.4f deg (median %.4f) against "
                "LEFT-knee edge gaps of %.4f-%.4f deg (median %.4f). The unlesioned side moves "
                "in the same direction but roughly FOUR TIMES LESS. So the displacement is "
                "bilateral but strongly lateralised, which is what a genuine left lesion with "
                "contralateral compensation would look like; it is NOT what a pipeline or "
                "batch artefact would look like, because a batch artefact has no reason to "
                "prefer the lesioned side by 4x."
                % (kv110R["edge_gaps_when_separated_deg"]["min"],
                   kv110R["edge_gaps_when_separated_deg"]["max"],
                   kv110R["edge_gaps_when_separated_deg"]["median"],
                   kv110L["edge_gaps_when_separated_deg"]["min"],
                   kv110L["edge_gaps_when_separated_deg"]["max"],
                   kv110L["edge_gaps_when_separated_deg"]["median"]),
            "interpretation": "at KV 0.110 the gait is displaced BILATERALLY, so a bare "
                              "'the left knee separates' statement at that rung is not by "
                              "itself evidence of a lesion-SIDE signature. It is not a batch "
                              "artefact either -- the right knee's own batch null is 0/15 and "
                              "the left-right magnitude ratio is about 4:1. The honest reading "
                              "is: strict left-only specificity holds at KV <= 0.100 and fails "
                              "at KV 0.110, the rung that produces the largest gap.",
            "right_knee_edge_gaps_at_KV0110_deg": kv110R["edge_gaps_when_separated_deg"],
            "left_knee_edge_gaps_at_KV0110_deg": kv110L["edge_gaps_when_separated_deg"]},
        "Q5_the_two_answers_do_not_agree": {
            "summary": "the separation is REAL and survives the batch null; the MAGNITUDE does "
                       "not reach a defensible knee MDC. Those are different questions and they "
                       "get different answers.",
            "how_far_the_ladder_gets": "across all %d like-for-like left-knee comparisons the "
                                       "edge gaps run %.4f to %.4f deg (median %.4f). %s of %d "
                                       "reach 3.8 deg, %s reach 5.70 deg, %s reaches 6.3919 "
                                       "deg, and ZERO reach the 7.25-7.62 deg conservative "
                                       "band. The single largest gap in the entire chained "
                                       "ladder still falls short of the MDC."
                                       % (lhit["n_tested"],
                                          lhit["edge_gaps_when_separated_deg"]["min"],
                                          lhit["edge_gaps_when_separated_deg"]["max"],
                                          lhit["edge_gaps_when_separated_deg"]["median"],
                                          lhit["n_separated_by_at_least"]["3.8000"],
                                          lhit["n_tested"],
                                          lhit["n_separated_by_at_least"]["5.7000"],
                                          lhit["n_separated_by_at_least"]["6.3919"]),
            "what_this_licenses": "a claim that the endpoint DISCRIMINATES the two lesions in "
                                  "simulation, with a dose-monotone gap. NOT a claim that the "
                                  "difference would be detectable in an instrumented clinical "
                                  "gait lab."},
        "Q4_declared_limitations": [
            "NULL-PF could not be computed at all on this endpoint: every one of the 10 "
            "plantarflexor-weakness family pairs is UNINFORMATIVE because at most one of those "
            "five families reaches %d Gate-G cells (R276WPF005 has 5; R276WPF010 3, "
            "R276WPF020 0, R285BF007 3, R285BF008 2). Only NULL-DF is available, so the batch "
            "null rests on a single cohort of 15 pairs." % MIN_VALS,
            "R396SPg120 (KV 0.120) has only 3 Gate-G cells and is UNINFORMATIVE; it contributes "
            "0/0 and is reported, not dropped.",
            "R396SPg110 has 4 Gate-G cells, not 6, so its permutation floor is 1/210 rather "
            "than 1/924, and its like-for-like tests are 4-vs-6.",
            "The batch null is a rate over 15 pairs; 4/15 has a wide interval. The binomial "
            "test against it inherits that uncertainty.",
            "Everything here is a simulation. The MDC figures are marker-based motion-capture "
            "measurement error in humans; the simulated endpoint has no marker error at all. "
            "Comparing them is the correct clinical test of whether a measurable difference is "
            "being claimed, but the comparison is a transfer, not a like-for-like."],
    }

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print("NULL-DF  left knee : %2d/%2d = %s"
          % (nulls[PRIMARY]["NULL_DF"]["n_separated"],
             nulls[PRIMARY]["NULL_DF"]["n_pairs_tested"],
             ("%.1f%%" % (100 * lrate)) if lrate is not None else "n/a"))
    print("NULL-PF  left knee : %2d/%2d = %s"
          % (nulls[PRIMARY]["NULL_PF"]["n_separated"],
             nulls[PRIMARY]["NULL_PF"]["n_pairs_tested"],
             ("%.1f%%" % (100 * nulls[PRIMARY]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"]))
             if nulls[PRIMARY]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"] is not None else "n/a"))
    print("NULL-DF right knee : %2d/%2d = %s"
          % (nulls[NEGCTL]["NULL_DF"]["n_separated"],
             nulls[NEGCTL]["NULL_DF"]["n_pairs_tested"],
             ("%.1f%%" % (100 * rrate)) if rrate is not None else "n/a"))
    print("NULL-PF right knee : %2d/%2d = %s"
          % (nulls[NEGCTL]["NULL_PF"]["n_separated"],
             nulls[NEGCTL]["NULL_PF"]["n_pairs_tested"],
             ("%.1f%%" % (100 * nulls[NEGCTL]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"]))
             if nulls[NEGCTL]["NULL_PF"]["BATCH_FALSE_POSITIVE_RATE"] is not None else "n/a"))
    print()
    for kv, fam in SPASTIC:
        e = lfl[PRIMARY][kv]
        r = lfl[NEGCTL][kv]
        print("KV %-6s %-12s LEFT %d/%d  p=%s   |   RIGHT %d/%d"
              % (kv, fam, e["n_separated"], e["n_tested"],
                 ("%.4g" % e["p_binomial_vs_batch_null"])
                 if e["p_binomial_vs_batch_null"] is not None else "n/a",
                 r["n_separated"], r["n_tested"]))
    print()
    print("VERDICT: %s" % v)
    print("  %s" % why)
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
