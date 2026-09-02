"""footing_r272.py -- round 272. The footing constants and KV constants on the VALIDATED path.

Fixes V-1/V-2/V-3 and V-16 of the r271 audit.

The validated cycle rule is body2_dose_r229.py's cycles_of(): cycles wholly inside the
window, then DROP THE LAST ONE. Omitting the drop is what put the r270 constants 0.08 %
and 3 % out. With it, tib_ant_l reproduces VERIFY_F5_r231.json's deposited
tib_ant_mean_force_N = 125.85307120231857 to zero error.

SELF-TESTS, ALL of which gate the deposit (V-16: the guard precedes the write, the
tolerance is tight, and BOTH paths are tested):
  1. tib_ant_l achieved force == 125.85307120231857   (rel tol 1e-9)
  2. plantarflexor dose at KV 0.050 == 136.2663747371695 (rel tol 1e-3)

Read-only.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S
import metric_r255 as MR

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0, "tib_ant_l": 1759.0}
WIN = (1.0, 13.58)
DF_DEPOSITED = 125.85307120231857        # VERIFY_F5_r231.json / DOSE_r174.json
PF_DOSE_AT_KV050 = 136.2663747371695     # VERIFY_F5_r231.json -> spastic_dose_corrected_V_N


def cell(seed):
    d = MR.rd("R151C_s%d" % seed)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(list(t), grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= WIN[0] and t[idx[k + 1]] <= WIN[1]]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc          # THE VALIDATED RULE
    a, b = cyc[0][0], cyc[-1][1]
    out = {}
    for m, fm in FMAX.items():
        f = np.abs(np.asarray(S.col(cols, dat, m + ".mtu_force_norm"),
                              dtype=float)[a:b]) * fm
        v = np.asarray(S.col(cols, dat, m + ".fiber_velocity_norm"), dtype=float)[a:b]
        out[m] = {"achieved_N": float(f.mean()),
                  "N_per_unit_KV": float(np.maximum(0.0, v).mean() * fm)}
    return out


def main():
    cells = {s: cell(s) for s in range(101, 107)}
    ach = {m: float(np.mean([cells[s][m]["achieved_N"] for s in cells])) for m in FMAX}
    npk = {m: float(np.mean([cells[s][m]["N_per_unit_KV"] for s in cells])) for m in FMAX}
    PF_ACH = ach["soleus_l"] + ach["gastroc_l"]
    DF_ACH = ach["tib_ant_l"]
    PF_NPK = npk["soleus_l"] + npk["gastroc_l"]
    DF_NPK = npk["tib_ant_l"]

    st = {"tib_ant_achieved_vs_deposit": {
              "computed": DF_ACH, "deposited": DF_DEPOSITED,
              "rel_err": abs(DF_ACH - DF_DEPOSITED) / DF_DEPOSITED,
              "passed": bool(abs(DF_ACH - DF_DEPOSITED) / DF_DEPOSITED < 1e-9)},
          "pf_dose_at_KV050_vs_deposit": {
              "computed": PF_NPK * 0.050, "deposited": PF_DOSE_AT_KV050,
              "rel_err": abs(PF_NPK * 0.050 - PF_DOSE_AT_KV050) / PF_DOSE_AT_KV050,
              "passed": bool(abs(PF_NPK * 0.050 - PF_DOSE_AT_KV050)
                             / PF_DOSE_AT_KV050 < 1e-3)}}
    ok = all(v["passed"] for v in st.values())

    # ---- V-16: the guard PRECEDES the write
    if not ok:
        print("*** SELF-TEST FAILED -- nothing deposited ***")
        for k, v in st.items():
            print("   %-34s computed %.8f  deposited %.8f  rel_err %.3e  %s"
                  % (k, v["computed"], v["deposited"], v["rel_err"],
                     "PASS" if v["passed"] else "FAIL"))
        return 1

    GRID = [0.05, 0.10, 0.20]
    existing_weak_df = {"x0.950": 0.050, "x0.900": 0.100, "x0.800": 0.200}
    existing_spastic_pf = {kv: PF_NPK * kv / PF_ACH for kv in (0.050, 0.150, 0.400)}

    out = {"round": 272,
           "supersedes": "the r270 rev-2 constants DF 129.2395 and PF 663.4508, which had no "
                         "source on disk and were computed without the drop-last-cycle rule",
           "validated_path": ("body2_dose_r229.py cycles_of(): cycles wholly inside the window, "
                              "then drop the last. Window [1.00, 13.58]."),
           "self_tests": st,
           "achieved_force_N": {"per_muscle": ach, "plantarflexors": PF_ACH,
                                "dorsiflexor": DF_ACH,
                                "ratio_PF_over_DF": PF_ACH / DF_ACH,
                                "dorsiflexor_source": "VERIFY_F5_r231.json / DOSE_r174.json "
                                                      "-> tib_ant_mean_force_N (reproduced here "
                                                      "to zero error)",
                                "plantarflexor_source": "computed here; no prior deposit carried it"},
           "newtons_per_unit_KV": {"per_muscle": npk, "plantarflexors": PF_NPK,
                                   "dorsiflexor": DF_NPK,
                                   "ratio_PF_over_DF": PF_NPK / DF_NPK},
           "existing_arms_on_this_footing": {
               "WEAK_DF": existing_weak_df,
               "SPASTIC_PF_by_KV": existing_spastic_pf,
               "note": ("SPASTIC-PF exists at THREE gains, not one: KV 0.050, 0.150 and 0.400, "
                        "six seeds each, 24 gate-failed cells at the upper two "
                        "(GAIN_LADDER_r264.json). f = 0.40 lies BELOW the KV 0.150 point.")},
           "dose_grid": GRID,
           "cells_required": {},
           }
    for f in GRID:
        out["cells_required"]["f=%.2f" % f] = {
            "WEAK_DF": "EXISTS (%s)" % [k for k, v in existing_weak_df.items()
                                        if abs(v - f) < 1e-9][0],
            "SPASTIC_PF": ("EXISTS at KV 0.050 (f=%.5f)" % existing_spastic_pf[0.050]
                           if abs(existing_spastic_pf[0.050] - f) < 0.01
                           else "NEW, KV = %.6f" % (f * PF_ACH / PF_NPK)),
            "WEAK_PF": "NEW, scale = %.6f" % (1.0 - f),
            "SPASTIC_DF": "NEW, KV = %.6f" % (f * DF_ACH / DF_NPK),
            "DF_target_N": f * DF_ACH, "PF_target_N": f * PF_ACH,
            "absolute_force_ratio_PF_over_DF": PF_ACH / DF_ACH}

    with io.open(os.path.join(PAPER, "FOOTING_r272.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")

    print("SELF-TESTS PASSED")
    for k, v in st.items():
        print("   %-34s rel_err %.3e" % (k, v["rel_err"]))
    print()
    print("achieved force N   PF %.8f   DF %.8f   ratio %.5f" % (PF_ACH, DF_ACH, PF_ACH / DF_ACH))
    print("N per unit KV      PF %.4f   DF %.4f   ratio %.5f" % (PF_NPK, DF_NPK, PF_NPK / DF_NPK))
    print("SPASTIC-PF existing gains on this footing: " +
          "  ".join("KV %.3f -> f %.5f" % (k, v) for k, v in existing_spastic_pf.items()))
    print()
    for f in GRID:
        c = out["cells_required"]["f=%.2f" % f]
        print("f=%.2f  WEAK-DF %-22s SPASTIC-PF %-26s WEAK-PF %-22s SPASTIC-DF %s"
              % (f, c["WEAK_DF"], c["SPASTIC_PF"], c["WEAK_PF"], c["SPASTIC_DF"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
