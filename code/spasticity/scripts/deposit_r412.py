# -*- coding: utf-8 -*-
"""r412 -- mints FROZEN_MECHANISM_r410.json and FROZEN_WEAKNESS_r411.json.

These two probes were run and reported to the user during the session but NEVER deposited.
This script recomputes every cell from the staged .par.sto files and writes the deposits.
READ-ONLY on C:\\Users\\maurice\\Documents\\SCONE\\results. Starts no sconecmd.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_r412 as A

PAPER = A.PAPER

READOUT = {
    "name": "corpus window with Gate G WAIVED",
    "window": "SETTLE 1.00 s, T1 9.73 s, cycles between left heel strikes wholly inside the "
              "window, LAST kept cycle dropped when >= 2 remain; stance = leg0_l.grf_norm_y "
              "> 0.05 (sto_utils.grf_vertical), heel strikes by sto_utils.heel_strikes.",
    "endpoint": "knee_angle_l at left heel strike, per-cycle mean, degrees",
    "DEVIATION_FROM_CORPUS": "the corpus Gate G (t_end >= 9.73 s AND >= 5 admissible cycles) "
                             "is NOT applied to the arm means below. It CANNOT be applied: "
                             "every lesioned arm dies in 3-5 s with 1-2 cycles. The arm means "
                             "are therefore sub-Gate-G quantities and are reported as such.",
}


def build(stage_name, arms_doc, title, extra):
    cells = A.frozen_cells(os.path.join(A.STAGE, stage_name))
    arms = A.group_arms(cells)
    out = {}
    for a, v in sorted(arms.items()):
        strict = sorted([(s, r["knee_hs_deg"]) for s, r in v["per_seed"].items()
                         if r.get("knee_hs_deg") is not None], key=lambda x: x[1])
        vals = [x[1] for x in strict]
        out[a] = {
            "label": arms_doc.get(a, ""),
            "n_seeds_run": v["n_seeds"],
            "n_seeds_with_a_value": len(vals),
            "knee_hs_deg_mean": float(np.mean(vals)) if vals else None,
            "knee_hs_deg_range": [float(min(vals)), float(max(vals))] if vals else None,
            "knee_hs_deg_by_seed": {s: float(x) for s, x in strict},
            "t_end_s_range": [v["t_end_s_min"], v["t_end_s_max"]],
            "t_end_s_by_seed": {s: r.get("t_end_s") for s, r in sorted(v["per_seed"].items())},
            "n_admissible_cycles_by_seed": {s: r.get("n_cycles_in_window")
                                            for s, r in sorted(v["per_seed"].items())},
            "GATE_G_pass_count": v["n_gate_G_pass"],
            "GATE_G_ALL_FAIL": v["gate_G_all_fail"],
        }
    none = out.get([k for k in out if k.endswith("NONE")][0])
    for a, v in out.items():
        if v["knee_hs_deg_mean"] is not None and none["knee_hs_deg_mean"] is not None:
            v["delta_vs_NONE_deg"] = v["knee_hs_deg_mean"] - none["knee_hs_deg_mean"]
    dep = {
        "round": title,
        "written_by": "scone/deposit_r412.py during the r412 pre-writeup audit",
        "why_this_deposit_exists_late": "the probe was run and its arm means were reported to "
                                        "the user during the session, but no deposit was ever "
                                        "written. This file is that missing container. It is "
                                        "POST-HOC and UNREGISTERED: there is no PREREG for "
                                        "r410 or r411 anywhere in paper/.",
        "status": "UNREGISTERED, POST-HOC, EXPLORATORY. Changes no verdict and may not be "
                  "cited as confirmatory evidence for any mechanism claim.",
        "staged_under": os.path.join(A.STAGE, stage_name),
        "readout": READOUT,
        "GATE_G_WARNING": {
            "HEADLINE": "EVERY LESIONED ARM IN THIS DEPOSIT FAILS GATE G. Not one lesioned "
                        "cell reaches the corpus 9.73 s / 5-cycle bar except where noted "
                        "below. The arm means rest on ONE TO THREE gait cycles per seed.",
            "why_it_matters": "the corpus endpoint is a per-cycle mean over >= 5 steady "
                              "cycles. A mean over 1-2 cycles taken from a model that is "
                              "falling over is not the same quantity, and the corpus has "
                              "never characterised its variance. NONE of the numbers in this "
                              "deposit may be compared with a Gate-G corpus value.",
            "the_comparator_is_not_like_for_like": "the NONE arm is a 20.0 s run that passes "
                                                   "Gate G on all six seeds with 15 cycles. "
                                                   "Every lesioned arm dies in 3-5 s. The "
                                                   "'delta_vs_NONE_deg' figures therefore "
                                                   "compare a steady walk against a fall and "
                                                   "cannot be read as a lesion effect size.",
        },
        "arms": out,
    }
    dep.update(extra)
    return dep


if __name__ == "__main__":
    r410 = build(
        "frozen2_r410",
        {"R410NONE": "no lesion; frozen R151C controller replayed",
         "R410SOL": "soleus-only spastic reflex, frozen controller",
         "R410GAS": "gastrocnemius-only spastic reflex, frozen controller",
         "R410BOTH": "soleus + gastrocnemius spastic reflex, frozen controller"},
        "FROZEN_MECHANISM_r410",
        {"question": "with the control controller FROZEN (no re-optimisation), which "
                     "plantarflexor carries the knee-at-heel-strike displacement?",
         "relation_to_r407": "r407 asked the same question WITH re-optimisation and returned "
                             "UNINFORMATIVE at KV 0.110 (GAS and SOL had 0 Gate-G seeds). This "
                             "probe removes re-optimisation. It does not rescue r407: it "
                             "replaces one UNINFORMATIVE readout with a sub-Gate-G one."})
    r411 = build(
        "frozenweak_r411",
        {"R411NONE": "no lesion; frozen R151C controller replayed",
         "R411TA_x080": "tibialis anterior max isometric force x0.80, frozen controller",
         "R411TA_x050": "tibialis anterior x0.50, frozen controller",
         "R411TA_x030": "tibialis anterior x0.30, frozen controller",
         "R411SOLwk_x050": "soleus x0.50 (weakness, not spasticity), frozen controller",
         "R411GASwk_x050": "gastrocnemius x0.50 (weakness, not spasticity), frozen controller"},
        "FROZEN_WEAKNESS_r411",
        {"question": "with the control controller FROZEN, does WEAKENING a muscle move "
                     "knee-at-heel-strike, and in which direction?",
         "THE_RESULT_THAT_MATTERS": "SOL x0.50 WEAKNESS moves the knee to -13.33 deg, i.e. "
                                    "MORE flexed than the frozen control by 5.48 deg and in "
                                    "the SAME DIRECTION as the spastic headline. A pure "
                                    "weakness lesion reproduces the sign of the spastic "
                                    "signature on this endpoint under a frozen controller. "
                                    "This is a direct threat to the discriminative reading of "
                                    "the knee endpoint and must appear in the paper's "
                                    "limitations, not be omitted. It is sub-Gate-G and cannot "
                                    "be quoted as a Gate-G result either."})
    for name, dep in [("FROZEN_MECHANISM_r410.json", r410),
                      ("FROZEN_WEAKNESS_r411.json", r411)]:
        p = os.path.join(PAPER, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(dep, f, indent=1)
        print("%s  %d bytes" % (p, os.path.getsize(p)))
