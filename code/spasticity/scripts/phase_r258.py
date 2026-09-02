"""phase_r258.py -- round 258. The measurement this project never made.

Every scalar used in this paper collapses the gait cycle to one number, and two different
collapses gave two different answers about which channel discriminates. This deposits the
PHASE-RESOLVED difference curve instead: for every arm, every channel, both windows, the
mean trajectory over the normalised gait cycle and its difference from control.

It also runs the three tests the last cold read established and this project had not:

  T1 OFFSET TEST. A sustained offset (equinus) translates the whole trajectory, so the
     difference curve would be FLAT. Reported as the sd of the difference curve about its
     own mean, against the mean itself.
  T2 DOSE COLLINEARITY. Are the reflex and weakness arms two kinds of thing, or two doses
     of one thing? All arms are put in one table at the phase of maximum deviation, and the
     reflex arm is tested against the weakness dose-response line.
  T3 THE UNREPORTED CHANNEL. Every channel ranked by displacement, to find what the paper
     omitted.

Read-only. Cycle detection taken unchanged from metric_r255.py / channels_g2_r219.py.
"""
import glob
import io
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S
import metric_r255 as MR

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
NP = 101                                    # 0..100 % of cycle
JOINTS = [p + s for p in MR.PAIR for s in ("_l", "_r")] + MR.UNP
SCALE = {"S": None, "W800": .800, "W870": .870, "W892": .892,
         "W900": .900, "W915": .915, "W950": .950}
# force removed by each weakness rung, from VERIFY_F5_r231.json -> tib_ant_mean_force_N
TIB = 125.85307120231857
REFLEX_DOSE = 136.2663747371695             # corrected V-scale, same deposit


def curves(sto, T1):
    """Mean trajectory per channel over the normalised cycle, averaged across cycles."""
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= MR.SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    assert c, "no cycles"
    grid = np.linspace(0.0, 1.0, NP)
    out = {}
    for ch in JOINTS:
        v = np.asarray(S.col(cols, dat, ch), dtype=float)
        acc = np.zeros(NP)
        for a, b in c:
            seg = np.degrees(v[a:b + 1])
            x = np.linspace(0.0, 1.0, len(seg))
            acc += np.interp(grid, x, seg)
        out[ch] = (acc / len(c)).tolist()
    for p in MR.PAIR:
        out[p + "_LmR"] = [l - r for l, r in zip(out[p + "_l"], out[p + "_r"])]
    return out, len(c)


def main():
    out = {"round": 258,
           "what": ("phase-resolved mean trajectory and difference-from-control curve, per arm "
                    "per channel, over the normalised gait cycle (left heel strike to left heel "
                    "strike, 101 points)"),
           "n_points": NP, "read_only": True, "windows": {}}

    for T1 in MR.WINDOWS:
        A = {}
        for arm, pre in MR.ARMS.items():
            per = []
            for s in MR.SEEDS:
                sto = sorted(glob.glob(os.path.join(MR.rd("%s_s%d" % (pre, s)),
                                                    "*.par.sto")))[-1]
                per.append(curves(sto, T1)[0])
            A[arm] = {ch: np.mean([p[ch] for p in per], axis=0)
                      for ch in per[0]}
        CH = list(A["C"].keys())

        w = {"mean_curve": {}, "diff_from_control": {}, "summary": {}}
        for arm in MR.ARMS:
            w["mean_curve"][arm] = {ch: A[arm][ch].tolist() for ch in CH}
            if arm == "C":
                continue
            d = {ch: (A[arm][ch] - A["C"][ch]) for ch in CH}
            w["diff_from_control"][arm] = {ch: d[ch].tolist() for ch in CH}
            s = {}
            for ch in CH:
                dd = d[ch]
                i = int(np.argmax(np.abs(dd)))
                s[ch] = {
                    "mean_of_diff": float(np.mean(dd)),
                    "sd_of_diff": float(np.std(dd)),
                    "max_abs_dev": float(np.abs(dd).max()),
                    "phase_of_max_pct": i,
                    "dev_at_max_phase": float(dd[i]),
                    "dev_at_80pct": float(dd[80]),
                    "dev_at_0pct_heelstrike": float(dd[0]),
                    "range_of_diff": [float(dd.min()), float(dd.max())],
                    # T1: an offset gives sd ~ 0 relative to |mean|
                    "offset_ratio_sd_over_absmean": (float(np.std(dd) / abs(np.mean(dd)))
                                                     if abs(np.mean(dd)) > 1e-9 else None),
                }
            w["summary"][arm] = s

        # ---- T1 offset test, on the lesioned ankle
        w["T1_offset_test"] = {
            ch: {arm: {"mean_of_diff": w["summary"][arm][ch]["mean_of_diff"],
                       "sd_of_diff": w["summary"][arm][ch]["sd_of_diff"],
                       "ratio": w["summary"][arm][ch]["offset_ratio_sd_over_absmean"],
                       "range": w["summary"][arm][ch]["range_of_diff"],
                       "verdict": ("OFFSET-COMPATIBLE"
                                   if (w["summary"][arm][ch]["offset_ratio_sd_over_absmean"] or 9) < 0.25
                                   else "NOT AN OFFSET")}
                 for arm in MR.ARMS if arm != "C"}
            for ch in ("ankle_angle_l", "ankle_angle_LmR")}

        # ---- T2 dose collinearity on the lesioned ankle
        t2 = {}
        for ch in ("ankle_angle_l", "ankle_angle_LmR"):
            rows = {}
            for arm in MR.ARMS:
                if arm == "C":
                    continue
                dose = REFLEX_DOSE if arm == "S" else (1.0 - SCALE[arm]) * TIB
                rows[arm] = {"dose_N": dose,
                             "dev_at_80pct": w["summary"][arm][ch]["dev_at_80pct"],
                             "mean_of_diff": w["summary"][arm][ch]["mean_of_diff"],
                             "max_abs_dev": w["summary"][arm][ch]["max_abs_dev"],
                             "phase_of_max_pct": w["summary"][arm][ch]["phase_of_max_pct"]}
            # fit the weakness dose-response line, then predict the reflex arm
            wk = [k for k in rows if k != "S"]
            x = np.array([rows[k]["dose_N"] for k in wk])
            for key in ("dev_at_80pct", "mean_of_diff", "max_abs_dev"):
                y = np.array([rows[k][key] for k in wk])
                m, b = np.polyfit(x, y, 1)
                pred = m * REFLEX_DOSE + b
                obs = rows["S"][key]
                yhat = m * x + b
                ss = 1 - np.sum((y - yhat) ** 2) / np.sum((y - np.mean(y)) ** 2)
                rows.setdefault("dose_line", {})[key] = {
                    "slope": float(m), "intercept": float(b), "r2_on_weakness": float(ss),
                    "predicted_for_reflex": float(pred), "observed_for_reflex": float(obs),
                    "ratio_obs_over_pred": float(obs / pred) if pred else None,
                    "reflex_on_line_within_25pct": bool(abs(obs - pred) <= 0.25 * abs(pred))}
            t2[ch] = rows
        w["T2_dose_collinearity"] = t2

        # ---- T3 what is the biggest displacement in the corpus
        rank = sorted(((abs(w["summary"]["S"][ch]["mean_of_diff"]), ch) for ch in CH),
                      reverse=True)
        w["T3_channels_ranked_by_reflex_mean_shift"] = [
            {"channel": ch, "abs_mean_shift": a,
             "signed": w["summary"]["S"][ch]["mean_of_diff"],
             "max_abs_dev": w["summary"]["S"][ch]["max_abs_dev"],
             "phase_of_max_pct": w["summary"]["S"][ch]["phase_of_max_pct"]}
            for a, ch in rank]
        out["windows"]["%.2f" % T1] = w

    with io.open(os.path.join(PAPER, "PHASE_r258.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, w in out["windows"].items():
        print("=" * 88)
        print("WINDOW [1.00, %s]" % wk)
        print("-- T1 OFFSET TEST, ankle_angle_l (an offset would give a FLAT difference curve)")
        for arm, v in w["T1_offset_test"]["ankle_angle_l"].items():
            print("   %-5s mean %+7.4f  sd %6.4f  sd/|mean| %6.2f  range [%+7.4f,%+7.4f]  %s"
                  % (arm, v["mean_of_diff"], v["sd_of_diff"],
                     v["ratio"] if v["ratio"] else float("nan"),
                     v["range"][0], v["range"][1], v["verdict"]))
        print("-- T2 all arms on ankle_angle_l, at 80%% of cycle and phase of max")
        r = w["T2_dose_collinearity"]["ankle_angle_l"]
        for arm in ["S", "W800", "W870", "W892", "W900", "W915", "W950"]:
            print("   %-5s dose %8.3f N  dev@80%% %+7.4f  mean %+7.4f  maxdev %+7.4f at %3d%%"
                  % (arm, r[arm]["dose_N"], r[arm]["dev_at_80pct"], r[arm]["mean_of_diff"],
                     r[arm]["max_abs_dev"], r[arm]["phase_of_max_pct"]))
        for key, v in r["dose_line"].items():
            print("   dose-line %-14s r2(weak)=%.4f  predict reflex %+8.4f  observed %+8.4f"
                  "  obs/pred %6.2f  on-line=%s"
                  % (key, v["r2_on_weakness"], v["predicted_for_reflex"],
                     v["observed_for_reflex"], v["ratio_obs_over_pred"] or float("nan"),
                     v["reflex_on_line_within_25pct"]))
        print("-- T3 channels ranked by reflex mean shift (top 6)")
        for x in w["T3_channels_ranked_by_reflex_mean_shift"][:6]:
            print("   %-20s mean %+8.4f  maxdev %+8.4f at %3d%%"
                  % (x["channel"], x["signed"], x["max_abs_dev"], x["phase_of_max_pct"]))


if __name__ == "__main__":
    main()
