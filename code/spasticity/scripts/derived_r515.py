# -*- coding: utf-8 -*-
"""r515: deposit the quantities that recompute exactly from other deposits but that no container
held. A verification pass named nine; this covers the eight that need no .sto access.

It also records the two margins a referee asked for against the quantity the title actually claims:
the artefact floor is 5.1x the nearest FAMILY-MEAN gap but only 2.5x the CELL-LEVEL gap, and the
nearest control-to-arm cell gap is smaller still.
"""
import io, json, os
import numpy as np

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
L = lambda f: json.load(io.open(os.path.join(PAP, f), encoding="utf-8"))

fam = L("FAMILY_LEVEL_r494.json")["families"]
med = L("ANKLE_MEDIATION_r488.json")
SHAM = L("SHAM_READOUT_r406.json")["largest_protocol_shift_deg"]
SEED = L("FLOOR_CORRECTION_r436.json")["THE_CORRECT_NOISE_SCALE"]["typical_value_deg"]
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
KV = [0.100, 0.140, 0.200, 0.220, 0.240]                       # delivered

kn_h = [fam[f]["mean_knee_ic_deg"] for f in HY]
kn_w = [fam[f]["mean_knee_ic_deg"] for f in WK]
cache = L("CELL_CACHE_r501.json")
ank = {f: cache[f]["ankle_mean"] for f in HY + WK
       if cache.get(f, {}).get("ankle_mean") is not None}

nearest_family_gap = min(kn_w) - max(kn_h)
cell_gap = 1.4918560478057357            # KNEE_MDC_BATCHNULL_r399 STEP6 like_for_like min
dep = {
 "id": "DERIVED_r515",
 "why": ("These recompute exactly from other deposits but were held in no container, so a reader "
         "auditing the archive by field name would score them missing."),
 "nearest_family_mean_gap_deg": nearest_family_gap,
 "artefact_floor_deg": SHAM,
 "MARGINS_AGAINST_THE_ARTEFACT_FLOOR": {
    "family_mean_gap": {"gap_deg": nearest_family_gap,
                        "multiple_of_artefact": nearest_family_gap / SHAM},
    "cell_level_gap": {"gap_deg": cell_gap, "multiple_of_artefact": cell_gap / SHAM,
                       "artefact_as_fraction_of_gap": SHAM / cell_gap},
    "NOTE": ("The title's claim is CELL-LEVEL non-overlap. Against that gap the artefact floor is "
             "39% of the margin, i.e. 2.5x, not the 5.1x that the family-mean gap gives. Both must "
             "be reported wherever the 5.1x appears.")},
 "majority_class_baseline": {"n_weakness_cells": 36, "n_total": 59, "baseline": 36 / 59.0},
 "dose_response": {
    "knee_r": float(np.corrcoef(KV, kn_h)[0, 1]),
    "knee_total_rise_deg": float(max(kn_h) - min(kn_h)),
    "ankle_r": (float(np.corrcoef(KV, [ank[f] for f in HY])[0, 1]) if len(ank) >= 5 else None),
    "note": "hyperreflexia family means against DELIVERED gain"},
 "registered_x080_span": {
    "effect_deg": 3.5250409970706498,
    "seed_SD_scale_deg": SEED,
    "in_seed_SD": 3.5250409970706498 / SEED,
    "note": ("the x0.80 spastic-axis span over the THREE REGISTERED rungs. The 15.7 SD figure in "
             "FLOOR_CORRECTION_r436 runs to a fourth gain column added after hashing.")},
 "survival_matched_multiples": {
    "x1.00_deg": 0.628369880399446, "x0.80_deg": 0.8443212066239916,
    "scale_deg": SEED,
    "in_seed_SD": [0.628369880399446 / SEED, 0.8443212066239916 / SEED],
    "against_the_sham_floor": [0.628369880399446 / SHAM, 0.8443212066239916 / SHAM],
    "note": ("MIXED_RESULT_r424 lists these under P4 overlapping_pairs. Against the 0.586 deg sham "
             "rather than the 0.511 deg seed scale they are 1.07x and 1.44x.")},
 "between_patient_SDs_are_literature_values": {
    "7.93_and_9.16_deg": "Mendes-Andrade [5], two 17-patient subgroups of one 34-patient cohort",
    "4.72_deg": ("computed by us on the Van Criekinge able-bodied set in "
                 "PUBLICDATA_VALIDATION_r405; NOT a published figure, and that deposit notes it "
                 "mixes between-subject and between-limb variance")},
}
io.open(os.path.join(PAP, "DERIVED_r515.json"), "w", encoding="utf-8", newline="").write(
    json.dumps(dep, indent=1, ensure_ascii=False))
print(json.dumps({k: dep[k] for k in ("nearest_family_mean_gap_deg",
                                      "MARGINS_AGAINST_THE_ARTEFACT_FLOOR", "majority_class_baseline",
                                      "dose_response", "registered_x080_span")},
                 indent=1, ensure_ascii=False))
