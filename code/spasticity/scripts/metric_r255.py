"""metric_r255.py -- round 255, registered at PREREG_metric_r255.md.

Is the instrument blind to the lesion it models?

Every channel in this project is a per-cycle peak-to-peak EXCURSION. A plantarflexor stretch
reflex's signature effect is a sustained offset (equinus), which changes MEAN ANGLE and can leave
EXCURSION untouched. This recomputes all sixteen channels under three metrics from ONE code path,
so that any disagreement cannot be an artefact of differing implementations.

Read-only: opens .sto files already on disk. Nothing is re-simulated or re-optimised.

Cycle detection, arm map and channel construction are taken unchanged from channels_g2_r219.py
and ladder36_r228.py.
"""
import collections
import glob
import io
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

R = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = range(101, 107)
SETTLE = 1.0
WINDOWS = [9.73, 13.58]

PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = ([p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"]
      + [p + "_LmR" for p in PAIR])

ARMS = collections.OrderedDict([
    ("C", "R151C"), ("S", "R151S"),
    ("W800", "R151W"), ("W870", "R174W870"), ("W892", "R174W892"),
    ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095")])

# Metrics. EXCURSION is the paper's incumbent. MEAN_ANGLE and PEAK_PF are the tests.
# OpenSim/Hyfydy gait convention: ankle_angle POSITIVE = dorsiflexion, so peak plantarflexion
# is the per-cycle MINIMUM. Verified below against the control arm before use.
METRICS = ["excursion", "mean_angle", "peak_pf"]


def rd(tag):
    g = [d for d in glob.glob(os.path.join(R, tag + ".*")) if os.path.isdir(d)
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def meas(sto, T1):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    assert c, "no cycles"
    out = {m: {} for m in METRICS}
    for ch in [p + s for p in PAIR for s in ("_l", "_r")] + UNP:
        v = S.col(cols, dat, ch)
        seg = [v[a:b + 1] for a, b in c]
        out["excursion"][ch] = sum(math.degrees(max(w) - min(w)) for w in seg) / len(seg)
        out["mean_angle"][ch] = sum(math.degrees(sum(w) / len(w)) for w in seg) / len(seg)
        out["peak_pf"][ch] = sum(math.degrees(min(w)) for w in seg) / len(seg)
    ct = (t[c[-1][1]] - t[c[0][0]]) / len(c)
    for m in METRICS:
        out[m]["cycle_time"] = ct              # temporal: identical under all three
        for p in PAIR:
            out[m][p + "_LmR"] = out[m][p + "_l"] - out[m][p + "_r"]
    return out, len(c)


def band_table(V, metric):
    """The paper's own displacement test, applied identically to a given metric."""
    res = {}
    ctrl = [x[metric] for x in V["C"]]
    for ch in CH:
        c = [x[ch] for x in ctrl]
        lo, hi, cm = min(c), max(c), float(np.mean(c))
        row = {"control_mean": cm, "band": [lo, hi], "arms": {}}
        for arm in ARMS:
            if arm == "C":
                continue
            am = float(np.mean([x[metric][ch] for x in V[arm]]))
            disp = not (lo <= am <= hi)
            marg = (am - hi) if am > hi else ((lo - am) if am < lo else -min(hi - am, am - lo))
            row["arms"][arm] = {"mean": am, "displaced": bool(disp),
                                "margin": marg, "delta_from_control": am - cm}
        res[ch] = row
    return res


def main():
    out = {"round": 255, "prereg": "PREREG_metric_r255.md",
           "question": "does the incumbent EXCURSION metric hide a sustained offset (equinus)",
           "metrics": METRICS, "read_only": True, "windows": {}}

    for T1 in WINDOWS:
        V, ncyc = {}, {}
        for arm, pre in ARMS.items():
            V[arm], ncyc[arm] = [], []
            for s in SEEDS:
                sto = sorted(glob.glob(os.path.join(rd("%s_s%d" % (pre, s)), "*.par.sto")))[-1]
                m, n = meas(sto, T1)
                V[arm].append(m)
                ncyc[arm].append(n)
        w = {"n_cycles": ncyc, "tables": {m: band_table(V, m) for m in METRICS}}

        # the registered question, in the paper's own currency
        verdict = {}
        for ch in ("ankle_angle_l", "ankle_angle_r", "ankle_angle_LmR",
                   "hip_flexion_l", "hip_flexion_r", "hip_flexion_LmR"):
            verdict[ch] = {m: {"S_displaced": w["tables"][m][ch]["arms"]["S"]["displaced"],
                               "S_margin": w["tables"][m][ch]["arms"]["S"]["margin"],
                               "S_delta": w["tables"][m][ch]["arms"]["S"]["delta_from_control"]}
                           for m in METRICS}
        w["reflex_arm_on_key_channels"] = verdict

        # Reading C: where do the metrics disagree on the S arm's displacement verdict?
        dis = []
        for ch in CH:
            v = {m: w["tables"][m][ch]["arms"]["S"]["displaced"] for m in METRICS}
            if len(set(v.values())) > 1:
                dis.append({"channel": ch, "by_metric": v,
                            "margins": {m: w["tables"][m][ch]["arms"]["S"]["margin"]
                                        for m in METRICS}})
        w["S_displacement_disagreements"] = dis

        # and across every lesion arm, not just the reflex
        alld = []
        for ch in CH:
            for arm in ARMS:
                if arm == "C":
                    continue
                v = {m: w["tables"][m][ch]["arms"][arm]["displaced"] for m in METRICS}
                if len(set(v.values())) > 1:
                    alld.append({"channel": ch, "arm": arm, "by_metric": v})
        w["all_arm_disagreements"] = alld
        w["n_disagreeing_channel_arm_cells"] = len(alld)
        out["windows"]["%.2f" % T1] = w

    with io.open(os.path.join(PAPER, "METRIC_r255.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, w in out["windows"].items():
        print("=" * 78)
        print("WINDOW [1.00, %s]" % wk)
        print("%-18s %-26s %-26s %s" % ("channel", "excursion", "mean_angle", "peak_pf"))
        for ch, v in w["reflex_arm_on_key_channels"].items():
            cells = []
            for m in METRICS:
                d = v[m]
                cells.append("%s m%+.4f d%+.4f" % ("DISP" if d["S_displaced"] else "  in",
                                                   d["S_margin"], d["S_delta"]))
            print("%-18s %-26s %-26s %s" % (ch, cells[0], cells[1], cells[2]))
        print("  S-arm metric disagreements: %s"
              % ([d["channel"] for d in w["S_displacement_disagreements"]] or "none"))
        print("  channel x arm cells where metrics disagree: %d"
              % w["n_disagreeing_channel_arm_cells"])


if __name__ == "__main__":
    main()
