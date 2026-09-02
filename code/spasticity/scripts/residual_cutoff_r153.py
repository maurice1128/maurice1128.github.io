"""Does the registered residual verdict depend on the SAMPLING RATE and CUTOFF nobody varied?

WHAT THE REGISTERED PRIMARY ACTUALLY IS. `residual_test_filtered.py` line 53:
`FS, CUT, ORDER, SETTLE = 30.0, 6.0, 4, 1.0` -- resample to **30 Hz**, 4th-order zero-phase
Butterworth at **6 Hz**, central difference, take the max. That pipeline produces the number both
manuscripts report: residual AUC 0.3600, p 0.5476, overlap 4-of-5, R^2 0.8030.

⛔ MY FIRST VERSION OF THIS SCRIPT ASSERTED THE REGISTERED VERDICT WAS COMPUTED UNFILTERED. It is
not, `RESULTS_discrimination.md`:437-455 documents the distinction in detail with its container, and
I wrote the premise without reading it. The calibration gate caught it -- four cells mismatched at
once, which is the signature of a wrong baseline rather than a wrong implementation.

WHY THIS IS WORTH RUNNING ANYWAY, AND IT IS A DIFFERENT QUESTION. r152 measured, on the slap
feature: 30 fps gives 0 % separation AT ZERO NOISE (temporal resolution, not noise), 6 Hz gives 0 %
at every rate and every noise level, and 15-20 Hz beats no filter by 6x at realistic markerless
noise. ⭐ **The registered primary sits at exactly the two settings r152 measured as worst.**

⚠ THE TRANSFER IS NOT AUTOMATIC AND IS NOT ASSUMED. r152's feature is peak PLANTARflexion velocity
at loading on the SPAS/DPAR corpus; this one is peak DORSIflexion velocity on `replay_crossed`.
Different feature, different corpus -- and this one still separates perfectly RAW at 30 Hz / 6 Hz
(AUC 0.0000, 0-of-5), so 6 Hz demonstrably does NOT destroy it. **The open question is narrower:
does the RESIDUAL -- the collinearity with rom, cadence and equinus -- move with the pipeline?**

⛔ THE HARD CONSTRAINT THAT MAKES THIS A 2-D SWEEP. `butter` takes `CUT/(FS/2)`; at FS = 30 the
Nyquist is 15 Hz, so **r152's optimal 15-20 Hz cutoff is unreachable at the registered sampling
rate**. Rate and cutoff are coupled: reaching the good cutoff REQUIRES the higher frame rate.
The sweep therefore varies both, and skips any pair with CUT >= 0.45*FS.

WHAT A CHANGE WOULD AND WOULD NOT MEAN. Filtering removes information; it cannot create any.
⛔ **A lower R^2 at some pipeline means the filter destroyed shared variance, not that the feature
became discriminative. AUC and p are the verdict; R^2 is diagnostic.** A residual AUC that moves
away from 0.5 at a reachable pipeline would be a genuine finding and would need its own
registration before being claimed.

`residual_test.py` and `residual_test_filtered.py` are IMPORTED and never modified.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import signal, stats

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import residual_test as RT           # noqa: E402  -- condition lists only
import residual_test_filtered as RTF # noqa: E402  -- the registered pipeline, unmodified
import sto_utils as S                # noqa: E402

RATES = [30.0, 60.0, 100.0]
CUTS = [6.0, 10.0, 12.0, 15.0, 20.0]
REG = {"auc": 0.3600, "p": 0.5476, "overlap": 4, "r2": 0.8030}
OUT = os.path.abspath(os.path.join(HERE, "..", "paper", "RESIDUAL_CUTOFF_r153.json"))


def vmax(path, fs, cut, order=4, settle=1.0):
    """RTF.filt_vmax with FS and CUT as arguments. Every other line is RTF's."""
    cols, data = S.load_sto(path)
    t = np.asarray(S.col(cols, data, "time"), float)
    a = np.asarray(S.col(cols, data, "ankle_angle_l"), float)
    if np.nanmax(np.abs(a)) < 3.5:
        a = a * 180.0 / np.pi
    m = t >= settle
    t, a = t[m], a[m]
    g = np.arange(t[0], t[-1], 1.0 / fs)
    ai = np.interp(g, t, a)
    b, aa = signal.butter(order, cut / (fs / 2.0), btype="low")
    return float(np.max(np.abs(np.gradient(signal.filtfilt(b, aa, ai), 1.0 / fs))))


def run(fs, cut):
    per = {}
    for d in sorted(glob.glob(os.path.join(RTF.REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        sto = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
        if len(sto) != 1:
            continue
        cond = os.path.basename(d).split(".")[0].rsplit("_s", 1)[0]
        if cond not in RT.SPASTIC + RT.WEAK:
            continue
        cf = S.cycle_features(sto[0], side="l", settle=1.0)
        if cf is None:
            continue
        cf["vmax_filt"] = vmax(sto[0], fs, cut)
        per.setdefault(cond, []).append(cf)

    conds = [c for c in RT.SPASTIC + RT.WEAK if c in per]
    M = lambda c, k: float(np.mean([r[k] for r in per[c]]))  # noqa: E731
    Y = np.array([M(c, "vmax_filt") for c in conds])
    X = np.column_stack([[M(c, "ank_rom") for c in conds],
                         [M(c, "cycle_time") for c in conds],
                         [M(c, "ank_hs") for c in conds],
                         np.ones(len(conds))])
    lab = np.array([1 if c in RT.SPASTIC else 0 for c in conds])

    def contrast(v):
        a, b = v[lab == 1], v[lab == 0]
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        return (float(u.statistic / (len(a) * len(b))), float(u.pvalue),
                int(sum(1 for x in a if b.min() <= x <= b.max())), int(len(a)))

    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    return {"n_cond": len(conds), "raw": contrast(Y), "resid": contrast(resid),
            "r2": float(1.0 - np.var(resid) / np.var(Y))}


def main():
    print("=" * 92)
    print("CALIBRATION GATE -- (FS=30, CUT=6) must reproduce the number both manuscripts report")
    print("=" * 92)
    base = run(30.0, 6.0)
    a, p, ov, n = base["resid"]
    ok = True
    for name, got, want in (("AUC", a, REG["auc"]), ("p", p, REG["p"]),
                            ("overlap", ov, REG["overlap"]), ("R^2", base["r2"], REG["r2"])):
        good = abs(got - want) < 5e-5 if isinstance(want, float) else got == want
        ok &= good
        print("  %-8s mirrored %-11.4f registered %-11.4f %s"
              % (name, got, want, "OK" if good else "*** MISMATCH ***"))
    if not ok:
        print("\nCALIBRATION FAILED -- NOT reporting the sweep.")
        return 1
    print("\n  calibration PASSES -- mirror reproduces the registered filtered verdict exactly\n")

    print("=" * 92)
    print("THE SWEEP -- rate x cutoff. CUT >= 0.45*FS skipped (unreachable below Nyquist).")
    print("=" * 92)
    print("  %-6s %-7s | %-24s | %-24s | %8s" % ("fs", "cut", "RAW AUC / p / overlap",
                                                 "RESID AUC / p / overlap", "R^2"))
    print("  " + "-" * 86)
    res = {}
    for fs in RATES:
        for cut in CUTS:
            if cut >= 0.45 * fs:
                print("  %-6.0f %-7.0f | %s" % (fs, cut, "-- unreachable: cut >= 0.45*Nyquist*2"))
                continue
            r = run(fs, cut)
            ra, rp, rov, rn = r["raw"]
            da, dp, dov, dn = r["resid"]
            star = "  <== registered" if (fs == 30.0 and cut == 6.0) else ""
            print("  %-6.0f %-7.0f | %.4f / %.6f / %d-of-%d | %.4f / %.6f / %d-of-%d | %8.4f%s"
                  % (fs, cut, ra, rp, rov, rn, da, dp, dov, dn, r["r2"], star))
            res["fs%.0f_cut%.0f" % (fs, cut)] = r

    json.dump({"what": "residual verdict vs sampling rate and low-pass cutoff",
               "registered_pipeline": {"fs": 30.0, "cut": 6.0, "order": 4},
               "registered_reference": REG, "sweep": res}, open(OUT, "w"), indent=1)
    print("\n  wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
