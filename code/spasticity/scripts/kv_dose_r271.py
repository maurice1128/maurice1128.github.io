"""kv_dose_r271.py -- round 271, required by PREREG_2x2_r270.md section 2a (rev 2, cb9925ea...).

Delivered newtons per unit reflex gain KV for tib_ant_l, measured read-only on the six
control cells, so the SPASTIC-DF arm's dose points can be set to registered fractions
instead of assuming the plantarflexors' constant.

dose(KV) = KV * mean(max(0, V)) * Fmax,  where V is the muscle's <name>.V, which SCONE's
MuscleReflex reads and which equals fiber_velocity_norm (VERIFY_F5_r231.json: V/
fiber_velocity_norm = 1.000000, V = 10 * ce_vel_norm).

SELF-TEST FIRST: the same code path applied to soleus_l + gastroc_l at KV 0.050 must
reproduce VERIFY_F5_r231.json's corrected spastic dose of 136.2663747 N. If it does not,
nothing is reported.
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
TARGET = 136.2663747371695          # VERIFY_F5_r231.json -> spastic_dose_corrected_V_N
PF_ACH, DF_ACH = 663.4508, 129.2395  # PREREG_2x2_r270.md section 2, frozen references


def per_cell(seed):
    d = MR.rd("R151C_s%d" % seed)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    # dose_r174.py / body2_dose_r229.py average over the GAIT-CYCLE SPAN, first cycle start
    # to last cycle end, not the raw window. Reproduce that exactly.
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(list(t), grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= WIN[0] and t[idx[k + 1]] <= WIN[1]]
    assert len(cyc) >= 2, "no cycles"
    i0, i1 = cyc[0][0], cyc[-1][1]
    out = {}
    for m in FMAX:
        v = np.asarray(S.col(cols, dat, m + ".fiber_velocity_norm"), dtype=float)[i0:i1 + 1]
        ce = np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), dtype=float)[i0:i1 + 1]
        pos = np.maximum(0.0, v)
        out[m] = {"mean_rectified_V": float(pos.mean()),
                  "N_per_unit_KV": float(pos.mean() * FMAX[m]),
                  "V_over_ce_vel_norm": float(np.mean(v[np.abs(ce) > 1e-9]
                                                      / ce[np.abs(ce) > 1e-9]))}
    return out


def main():
    cells = {s: per_cell(s) for s in range(101, 107)}
    agg = {}
    for m in FMAX:
        npk = [cells[s][m]["N_per_unit_KV"] for s in cells]
        agg[m] = {"per_seed_N_per_unit_KV": npk, "mean": float(np.mean(npk)),
                  "sd": float(np.std(npk, ddof=1)),
                  "mean_rectified_V": float(np.mean([cells[s][m]["mean_rectified_V"]
                                                     for s in cells])),
                  "V_over_ce_vel_norm": float(np.mean([cells[s][m]["V_over_ce_vel_norm"]
                                                       for s in cells]))}
    pf_npk = agg["soleus_l"]["mean"] + agg["gastroc_l"]["mean"]
    selftest = pf_npk * 0.050
    ok = abs(selftest - TARGET) / TARGET < 0.02

    df_npk = agg["tib_ant_l"]["mean"]
    doses = {}
    for f in (0.10, 0.20, 0.40):
        doses["f=%.2f" % f] = {
            "target_newtons": f * DF_ACH,
            "KV_required": (f * DF_ACH) / df_npk,
            "PF_equivalent_newtons": f * PF_ACH,
            "PF_KV_required": (f * PF_ACH) / pf_npk}

    out = {"round": 271, "prereg": "PREREG_2x2_r270.md rev 2 sha256 cb9925ea",
           "window": list(WIN), "read_only": True,
           "self_test": {"pf_N_per_unit_KV": pf_npk,
                         "dose_at_KV_0.050": selftest, "target_VERIFY_F5": TARGET,
                         "rel_error": abs(selftest - TARGET) / TARGET, "passed": bool(ok)},
           "per_muscle": agg,
           "tib_ant_l_N_per_unit_KV": df_npk,
           "ratio_PF_over_DF_per_unit_KV": pf_npk / df_npk,
           "SPASTIC_DF_dose_points": doses,
           "caveat": ("nominal commanded dose computed on CONTROL kinematics. The achieved dose "
                      "after re-optimisation will differ, in both arms, and is reported separately.")}

    with io.open(os.path.join(PAPER, "KV_DOSE_r271.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print("SELF-TEST  PF at KV 0.050 -> %.6f N   target %.6f   rel err %.5f   PASSED=%s"
          % (selftest, TARGET, out["self_test"]["rel_error"], ok))
    if not ok:
        print("*** self-test failed, nothing reported ***")
        return
    print()
    for m in FMAX:
        a = agg[m]
        print("%-11s mean rectified V %8.5f   Fmax %7.1f   N per unit KV %10.4f  (sd %.4f)"
              % (m, a["mean_rectified_V"], FMAX[m], a["mean"], a["sd"]))
    print()
    print("PLANTARFLEXORS  %10.4f N per unit KV" % pf_npk)
    print("tib_ant_l       %10.4f N per unit KV   -> ratio PF/DF = %.4f"
          % (df_npk, pf_npk / df_npk))
    print()
    print("SPASTIC-DF dose points (fraction of tib_ant control achieved force %.4f N):" % DF_ACH)
    for k, v in doses.items():
        print("   %-8s target %8.4f N  ->  KV = %.6f      [PF at same f: KV = %.6f]"
              % (k, v["target_newtons"], v["KV_required"], v["PF_KV_required"]))


if __name__ == "__main__":
    main()
