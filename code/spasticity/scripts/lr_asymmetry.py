"""REGISTERED test: within-subject LEFT/RIGHT ankle ROM asymmetry. Round 56.

WHY. The lesion is unilateral and every analysis in this project has used the affected limb only.
A within-subject ratio attacks the three things that killed the previous six candidate features:
it needs no healthy reference (each subject carries their own control), it is immune to camera yaw
and to the pixel-to-degree mapping (both limbs sit in one frame at one scale, which cancels), and
being dimensionless it is not directly subject to the 3.8 deg minimal-detectable-change floor.

THE COUNTER-FACT THAT MUST DECIDE IT. The unlesioned right limb does NOT discriminate on its own
(rom_r AUC 0.480, p 1.000). That is good news for a ratio -- no systematic drift in the denominator
-- but it equally permits the null outcome that the ratio is merely the left signal divided by a
near-constant, adding no information and only changing units. **The discriminating question is not
whether the ratio separates. It is whether the ratio beats LEFT-ONLY AT THE MILD RUNGS**, which is
where this project's problem actually lives.

---------------------------------------------------------------------------------------------
PREDICTIONS, WRITTEN BEFORE EXECUTION. Both outcomes are made readable in advance.

  PR1  The ratio SEPARATES at condition level (AUC 0.0 or 1.0). HIGH confidence and CHEAP --
       left ROM already separates completely, so a near-constant denominator preserves it.
       Recorded as cheap so it cannot later be presented as a discovery.

  PR2  ** THE DECIDING TEST. I predict the ratio does NOT materially beat LEFT-ONLY at the mild
       rungs. ** Specifically: mild-rung seed-level accuracy for the ratio will be within 1 seed
       (0.125 on 8 mild seeds) of left-only. Reason: a denominator that does not discriminate
       (AUC 0.480) cannot add discriminative information; it can only rescale. If PR2 is
       FALSIFIED -- ratio beats left-only by more than one seed at the mild rungs -- that is a
       genuine new result and the paper changes.

  PR3  The ratio's mild-rung margin, expressed in units of its own between-seed SD, will be
       COMPARABLE to left-only's margin in units of left-only's SD (within ~0.5 SD). This is the
       unit-free way to ask whether anything was gained, and it is the test that cannot be gamed
       by the choice of scale.

  PR4  ** The operational advantage is REAL EVEN IF PR2 HOLDS. ** Ratio needs no healthy
       reference and no absolute calibration. So a null on PR2 still leaves a finding: the same
       discrimination, obtained without the two things that broke the absolute feature. That is
       recorded now so a PR2 null is not written up as a total failure, and so the operational
       claim is not smuggled in as if it were a statistical one.

HONEST LIMIT, stated before the numbers: a dimensionless ratio escapes the DEGREE-VALUED MDC but
inherits a test-retest reliability floor of its own, and **this project has no citation for the
reliability of a within-subject sagittal ROM ratio from video.** Dimensionlessness is not a free
pass. Whatever this returns, that gap is real and must be reported.
---------------------------------------------------------------------------------------------
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S  # noqa: E402

REPLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
MILD_SP, MILD_WK = ["DR2K050", "DR2K075"], ["PAR20", "PAR40"]
REFERENCE = ["HEALTHY", "DR2K000"]
NBOOT = 10000
RNG = np.random.default_rng(20260803)


def load():
    out = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        st = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(st) != 1:
            continue
        c = os.path.basename(d).split(".")[0].rsplit("_s", 1)[0]
        if c not in SPASTIC + WEAK + REFERENCE:
            continue
        try:
            fl = S.cycle_features(st[0], side="l", settle=1.0)
            fr = S.cycle_features(st[0], side="r", settle=1.0)
        except Exception as e:
            print("  SKIP %s: %s" % (c, e))
            continue
        if not fl or not fr:
            continue
        out.setdefault(c, []).append({"l": fl["ank_rom"], "r": fr["ank_rom"],
                                      "ratio": fl["ank_rom"] / fr["ank_rom"]})
    return out


def acc(sp, wk):
    """Best single-threshold accuracy, and the AUC. Threshold fitted -- reported as such."""
    v = np.array(sp + wk, float)
    lab = np.array([1] * len(sp) + [0] * len(wk))
    best = 0.0
    for t in np.unique(v):
        for sign in (1, -1):
            pred = ((v < t) if sign > 0 else (v >= t)).astype(int)
            best = max(best, float(np.mean(pred == lab)))
    u = stats.mannwhitneyu(sp, wk, alternative="two-sided")
    return best, u.statistic / (len(sp) * len(wk)), u.pvalue


def report(name, key, sps, wks, per):
    sp = [r[key] for c in sps for r in per[c]]
    wk = [r[key] for c in wks for r in per[c]]
    a, auc, p = acc(sp, wk)
    scm = [float(np.mean([r[key] for r in per[c]])) for c in sps]
    wcm = [float(np.mean([r[key] for r in per[c]])) for c in wks]
    margin = min(wcm) - max(scm)
    sd = float(np.std(sp + wk, ddof=1))
    boot = [np.min([np.mean(RNG.choice([r[key] for r in per[c]], len(per[c]))) for c in wks])
            - np.max([np.mean(RNG.choice([r[key] for r in per[c]], len(per[c]))) for c in sps])
            for _ in range(NBOOT)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("    %-10s acc %.4f  AUC %.4f  p %.6f  margin %+.4f  (%.2f SD)  95%% CI [%+.3f, %+.3f]  P(<=0) %.1f%%"
          % (name, a, auc, p, margin, margin / sd if sd else float("nan"), lo, hi,
             100.0 * float(np.mean(np.array(boot) <= 0))))
    return {"acc": a, "auc": auc, "p": p, "margin": margin, "margin_sd": margin / sd if sd else None,
            "ci": [float(lo), float(hi)], "p_le_0": float(np.mean(np.array(boot) <= 0)),
            "n_sp": len(sp), "n_wk": len(wk)}


def main():
    per = load()
    print("=" * 78)
    print("REGISTERED L/R ASYMMETRY TEST")
    print("=" * 78)
    print("%-9s %8s %8s %8s" % ("cond", "rom_l", "rom_r", "ratio"))
    for c in SPASTIC + WEAK + REFERENCE:
        if c in per:
            print("%-9s %8.3f %8.3f %8.4f"
                  % (c, np.mean([r["l"] for r in per[c]]), np.mean([r["r"] for r in per[c]]),
                     np.mean([r["ratio"] for r in per[c]])))
    out = {}
    print("\n  ALL RUNGS (5 vs 5 conditions, 20 vs 20 seeds)")
    for nm, k in (("left-only", "l"), ("right-only", "r"), ("RATIO", "ratio")):
        out["all_" + k] = report(nm, k, SPASTIC, WEAK, per)
    print("\n  ** MILD RUNGS ONLY (2 vs 2 conditions, 8 vs 8 seeds) -- THE DECIDING TEST **")
    for nm, k in (("left-only", "l"), ("right-only", "r"), ("RATIO", "ratio")):
        out["mild_" + k] = report(nm, k, MILD_SP, MILD_WK, per)
    dl = out["mild_ratio"]["acc"] - out["mild_l"]["acc"]
    print("\n  PR2 VERDICT: ratio - left-only mild accuracy = %+.4f  (one seed = %.4f)"
          % (dl, 1.0 / out["mild_l"]["n_sp"]))
    print("     -> PR2 %s" % ("HOLDS (ratio does NOT materially beat left-only)"
                              if abs(dl) <= 1.0 / out["mild_l"]["n_sp"] + 1e-9
                              else "FALSIFIED (ratio beats left-only by more than one seed)"))
    print("  PR3: mild margin in own-SD units -- left %.2f vs ratio %.2f"
          % (out["mild_l"]["margin_sd"] or float("nan"), out["mild_ratio"]["margin_sd"] or float("nan")))
    print("\n  NOTE: all thresholds above are FITTED on all data and are upper bounds.")
    print("  NOTE: a dimensionless ratio escapes the degree-valued MDC but has its own test-retest")
    print("        reliability floor, for which this project holds NO citation.")
    dst = os.path.abspath(os.path.join(REPLAY, "..", "..", "paper", "LR_ASYMMETRY.json"))
    json.dump(out, open(dst, "w"), indent=1)
    print("\n  wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
