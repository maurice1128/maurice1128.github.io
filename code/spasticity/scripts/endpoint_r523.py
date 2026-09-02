# -*- coding: utf-8 -*-
"""r523: consolidate the endpoint scan, and bound what a better readout can buy.

Three questions were open about the readout itself. Does the separation depend on reading the knee
at one instant? Does averaging over a window buy anything? Does the standard clinical
normalisation -- paretic minus non-paretic -- help? WINDOW_r520, PEAK_r522 and LIMBDIFF_r521 answer
the three. This gathers them into one container and adds the quantity that decides whether any of it
matters for a single patient: the misclassification rate a PERFECT instrument would reach.
"""
import io, json, math, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
W = json.load(io.open(os.path.join(P, "WINDOW_r520.json"), encoding="utf-8"))["windows"]
K = json.load(io.open(os.path.join(P, "PEAK_r522.json"), encoding="utf-8"))
L = json.load(io.open(os.path.join(P, "LIMBDIFF_r521.json"), encoding="utf-8"))["scores"]

rows = []
for n, d in W.items():
    rows.append(("window " + n if n != "instant" else "contact instant", d["arm_difference_deg"],
                 d["cell_gap_deg"], d["cells_disjoint"], d["mean_within_cell_seed_SD_deg"],
                 d["gap_in_seed_SD"]))
d = K["scores"]["first_flexion_peak"]
rows.append(("first flexion peak", d["arm_difference_deg"], d["cell_gap_deg"], d["cells_disjoint"],
             d["mean_seed_SD_deg"], d["gap_in_seed_SD"]))
d = L["paretic_minus_nonparetic"]
rows.append(("paretic minus non-paretic", d["arm_difference_deg"], d["cell_gap_deg"],
             d["cells_disjoint"], d["mean_seed_SD_deg"], d["gap_in_seed_SD"]))

print("%-26s %9s %9s %9s %8s %8s" % ("readout", "arm diff", "cell gap", "disjoint", "seed SD", "gap/SD"))
for r in rows:
    print("%-26s %9.3f %9.3f %9s %8.3f %8.2f" % (r[0], r[1], r[2], r[3], r[4], r[5]))

single = [r for r in rows if r[0] != "paretic minus non-paretic"]
print("\nsingle-limb readouts: %d of %d disjoint" % (sum(1 for r in single if r[3]), len(single)))
best = max(single, key=lambda r: r[5])
print("best by gap/SD: %s (%.2f); pre-specified contact instant %.2f; ratio %.2f"
      % (best[0], best[5], W["instant"]["gap_in_seed_SD"], best[5] / W["instant"]["gap_in_seed_SD"]))

# ---- what a perfect instrument would buy ---------------------------------------------------------
Phi = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
SEM = 3.7041 / math.sqrt(2.0)
BIO = {"7.93": 7.93, "9.16": 9.16}
E_INST = abs(W["instant"]["arm_difference_deg"])
E_WIN = abs(W["0-10%"]["arm_difference_deg"])

lim = {}
print("\nmisclassification of one reading, by how much measurement error is removed:")
for bn, b in BIO.items():
    a = Phi(-(E_INST / math.sqrt(b * b + SEM * SEM)) / 2)          # instant, error as published
    c = Phi(-(E_WIN / math.sqrt(b * b + SEM * SEM)) / 2)           # window effect, error unchanged
    z = Phi(-(E_WIN / b) / 2)                                      # window effect, error abolished
    lim[bn] = {"between_patient_SD_deg": b,
               "instant_as_published": a, "window_effect_same_error": c,
               "window_effect_zero_measurement_error": z,
               "total_available_from_the_instrument_pp": 100 * (a - z)}
    print("  between-patient SD %-5s: instant %4.1f%%  ->  0-10%% window %4.1f%%  ->  "
          "perfect instrument %4.1f%%   (the instrument can buy at most %.1f pp)"
          % (bn, 100 * a, 100 * c, 100 * z, 100 * (a - z)))

dep = {
 "id": "ENDPOINT_r523",
 "why": ("Whether the separation is a property of the knee in early stance or an artefact of reading "
         "it at one instant; whether averaging or a limb contrast improves it; and what any "
         "improvement in the readout can be worth for a single patient."),
 "readouts": [{"name": r[0], "arm_difference_deg": r[1], "cell_gap_deg": r[2],
               "cells_disjoint": r[3], "mean_seed_SD_deg": r[4], "gap_in_seed_SD": r[5]}
              for r in rows],
 "single_limb_readouts_all_disjoint": all(r[3] for r in single),
 "n_single_limb_readouts": len(single),
 "best_single_limb": {"name": best[0], "gap_in_seed_SD": best[5],
                      "over_contact_instant": best[5] / W["instant"]["gap_in_seed_SD"]},
 "peak_timing_pct_of_cycle": K["peak_timing_pct_of_cycle"],
 "limb_contrast_by_rung": ("non-monotone: the paretic-minus-non-paretic difference rises to KV 0.200 "
                           "and falls back by KV 0.240, because the unlesioned knee follows the "
                           "lesioned one (SIDE_CONTROL_r496: 35.5 per cent of the separation)"),
 "instrument_ceiling": lim,
 "SELECTION_CAVEAT": ("six windows were scored and the best reported. The 0-10 per cent window's "
                      "advantage over the contact instant is therefore an upper estimate. What is "
                      "not selected is that every one of the seven single-limb readouts separates "
                      "the cells completely; that statement uses the whole scan."),
 "READING": ("The separation is a property of the knee in early stance, not of the contact instant: "
             "all seven single-limb readouts leave the two arms' cells disjoint, over windows from "
             "0-5 to 5-20 per cent of the cycle and at the first flexion peak. Averaging over 0-10 "
             "per cent gives the largest gap-to-noise ratio, 4.05 against 3.08, by lowering the "
             "noise rather than widening the gap. The one readout that fails is the limb contrast, "
             "which is the normalisation a clinician would reach for first: it doubles the "
             "seed-level noise and removes part of the signal, and the two arms' cells overlap. For "
             "a single patient none of this is decisive. Removing measurement error entirely, which "
             "no readout can do better than, moves the misclassification rate by about one "
             "percentage point, because the spread a stroke population presents is three times the "
             "measurement error and it is that spread, not the instrument, that sets the limit."),
}
io.open(os.path.join(P, "ENDPOINT_r523.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> ENDPOINT_r523.json")
