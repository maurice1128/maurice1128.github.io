"""metric_ladder_r256.py -- round 256, registered at PREREG_ladder_metric_r256.md.

Runs the paper's core analyses on MEAN ANGLE, beside the incumbent EXCURSION values.
Nothing is switched: both are computed here from one code path and reported together.

Read-only. Reuses meas() from metric_r255.py so the three metrics cannot differ by
implementation.
"""
import glob
import io
import json
import os
import sys
from itertools import permutations

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import metric_r255 as MR

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEV = ["W800", "W870", "W892", "W900", "W915", "W950"]
SCALE = {"W800": .800, "W870": .870, "W892": .892, "W900": .900, "W915": .915, "W950": .950}
METRICS = ["excursion", "mean_angle"]


def spearman_rho(v):
    n = len(v)
    rk = [sorted(v).index(x) + 1 for x in v]
    x = list(range(1, n + 1))
    d2 = sum((a - b) ** 2 for a, b in zip(rk, x))
    rho = 1 - 6.0 * d2 / (n * (n * n - 1))
    cnt = 0
    for p in permutations(range(1, n + 1)):
        s = sum((a - b) ** 2 for a, b in zip(p, x))
        r = 1 - 6.0 * s / (n * (n * n - 1))
        if (r >= rho - 1e-12) if rho > 0 else (r <= rho + 1e-12):
            cnt += 1
    return rho, cnt, len(list(permutations(range(1, n + 1))))


def main():
    out = {"round": 256, "prereg": "PREREG_ladder_metric_r256.md",
           "order_disclosure": ("EXCURSION was run first, for the whole project. MEAN ANGLE is run "
                                "second, after excursion produced a null on the lesioned ankle. Any "
                                "mean-angle result here was obtained with a metric adopted after the "
                                "first one failed."),
           "metric_was_never_registered": True,
           "windows": {}}

    for T1 in MR.WINDOWS:
        V = {}
        for arm, pre in MR.ARMS.items():
            V[arm] = []
            for s in MR.SEEDS:
                sto = sorted(glob.glob(os.path.join(MR.rd("%s_s%d" % (pre, s)), "*.par.sto")))[-1]
                V[arm].append(MR.meas(sto, T1)[0])
        w = {}
        for m in METRICS:
            per_seed = {a: [c[m]["hip_flexion_LmR"] for c in V[a]] for a in MR.ARMS}
            per_seed_ank = {a: [c[m]["ankle_angle_LmR"] for c in V[a]] for a in MR.ARMS}

            # ---- seed-level disjointness, reflex vs each rung (the test of section 3 / 6b)
            def disj(ps):
                smax, smin = max(ps["S"]), min(ps["S"])
                r = {}
                for k in SEV:
                    wmin, wmax = min(ps[k]), max(ps[k])
                    gap = wmin - smax if (sum(ps[k]) / 6.0) > (sum(ps["S"]) / 6.0) else smin - wmax
                    r[k] = {"weak_min": wmin, "weak_max": wmax,
                            "spastic_max": smax, "spastic_min": smin,
                            "seed_gap_deg": gap, "disjoint": gap > 0,
                            "weak_mean": float(np.mean(ps[k]))}
                allw = [x for k in SEV for x in ps[k]]
                pooled_gap = (min(allw) - smax) if np.mean(allw) > np.mean(ps["S"]) else (smin - max(allw))
                r["pooled_36"] = {"seed_gap_deg": pooled_gap, "disjoint": pooled_gap > 0,
                                  "spastic_mean": float(np.mean(ps["S"])),
                                  "weak_mean": float(np.mean(allw))}
                return r

            hip_d, ank_d = disj(per_seed), disj(per_seed_ank)

            # ---- margins ladder + rho (the test of 6b)
            def ladder(ch):
                c = [x[m][ch] for x in V["C"]]
                lo, hi = min(c), max(c)
                mg = {}
                for a in ["S"] + SEV:
                    am = float(np.mean([x[m][ch] for x in V[a]]))
                    mg[a] = (am - hi) if am > hi else ((lo - am) if am < lo else -min(hi - am, am - lo))
                seq = [mg[k] for k in SEV]
                rho, cnt, tot = spearman_rho(seq)
                return {"band": [lo, hi], "margins": mg, "rho_vs_severity": rho,
                        "rho_exact_p": float(cnt) / tot,
                        "monotone_decreasing": all(seq[i] > seq[i + 1] for i in range(5))}

            # ---- opposed-channel test (the test of section 6), 16 channels
            opp, disp_both = [], 0
            for ch in MR.CH:
                c = [x[m][ch] for x in V["C"]]
                lo, hi, cm = min(c), max(c), float(np.mean(c))
                sm = float(np.mean([x[m][ch] for x in V["S"]]))
                dS = not (lo <= sm <= hi)
                for k in ("W870", "W892", "W915"):
                    wm = float(np.mean([x[m][ch] for x in V[k]]))
                    dW = not (lo <= wm <= hi)
                    if dS and dW:
                        if k == "W892":
                            disp_both += 1
                            if (sm - cm) * (wm - cm) < 0:
                                opp.append(ch)
            w[m] = {"hip_flexion_LmR": {"per_seed": per_seed, "disjointness": hip_d,
                                        "ladder": ladder("hip_flexion_LmR")},
                    "ankle_angle_LmR": {"per_seed": per_seed_ank, "disjointness": ank_d,
                                        "ladder": ladder("ankle_angle_LmR")},
                    "opposed_channels_at_W892": opp,
                    "n_opposed": len(opp),
                    "n_both_displaced_at_W892": disp_both}
        out["windows"]["%.2f" % T1] = w

    with io.open(os.path.join(PAPER, "METRIC_LADDER_r256.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    for wk, w in out["windows"].items():
        print("=" * 76)
        print("WINDOW [1.00, %s]" % wk)
        for m in METRICS:
            b = w[m]
            print("  --- %s" % m)
            for ch in ("hip_flexion_LmR", "ankle_angle_LmR"):
                d = b[ch]["disjointness"]
                nd = sum(1 for k in SEV if d[k]["disjoint"])
                L = b[ch]["ladder"]
                print("      %-16s disjoint %d/6, pooled=%s (gap %+.4f) | rho %+.4f p=%.4f"
                      % (ch, nd, d["pooled_36"]["disjoint"], d["pooled_36"]["seed_gap_deg"],
                         L["rho_vs_severity"], L["rho_exact_p"]))
            print("      opposed channels at W892: %d %s (both-displaced %d)"
                  % (b["n_opposed"], b["opposed_channels_at_W892"], b["n_both_displaced_at_W892"]))


if __name__ == "__main__":
    main()
