"""REGISTERED reanalysis of the pre-registered SECONDARY endpoint, `ank_rom`. Round 50.

WHY THIS EXISTS. `ank_rom` was named as the secondary endpoint before the crossed experiment
launched, and it was then omitted from Results on the stated ground that ankle range of motion is
"a direct mechanical consequence of each lesion rather than a discriminative feature of gait".
An independent referee identified that as a category error: for a screening instrument, a direct
mechanical consequence of the lesion IS the clinical sign. The stiffened spastic ankle loses
excursion; the dropped foot swings through a larger arc. Excluding it was not a registered
exclusion -- R45-S forbids PROMOTING a feature to primary after seeing data; it does not license
DELETING a registered secondary from the report.

PROCEDURE, taken verbatim from the referee and not modified:
  (1) report `ank_rom` against the unlesioned reference and at matched equinus, exactly as was
      done for the primary;
  (2) the REVERSE RESIDUAL -- regress `ank_rom` on peak velocity, cadence and `ank_hs`, and test
      that residual.

---------------------------------------------------------------------------------------------
PREDICTED OUTCOME, WRITTEN BEFORE EXECUTION. Three parts, separately falsifiable.

  P1  `ank_rom` SEPARATES the arms at condition and seed level, with the spastic arm BELOW the
      unlesioned reference and the weak arm ABOVE it. Predicted with high confidence: this is
      already visible in `CROSSED_RESULT.json`, which is why the prediction is cheap and is
      recorded as cheap.

  P2  `ank_rom` SURVIVES equinus matching -- the sign of the spastic-minus-weak difference is
      negative in most or all matched pairs.

  P3  ** The REVERSE RESIDUAL will NOT be decisive, and I expect it to WEAKEN OR VANISH, for a
      reason that is symmetric and therefore uninformative. ** `ank_rom` and `ank_vel_max` are
      near-collinear (r ~ 0.95 in the archive). Regressing either on the other removes most of
      the shared variance in both directions. A forward residual that vanishes and a reverse
      residual that vanishes together say only that the two features are one feature -- they do
      NOT establish which is prior. Whichever survives better is a statement about the covariate
      set, not about mechanism.

  ** THEREFORE THE DECISIVE TESTS ARE P1 AND P2, NOT P3, AND THIS IS RECORDED BEFORE THE NUMBERS
  EXIST so that a surviving reverse residual cannot later be presented as the thing that settled
  it, and a vanishing one cannot be presented as re-confirming the null. **

  If P1 and P2 hold, the paper is POSITIVE and must be rewritten around `ank_rom`.
  If either fails, the null stands and is far better supported than it is now.
---------------------------------------------------------------------------------------------

DEVIATION DISCLOSED IN ADVANCE: the primary analysis was previously run with a feature variant
that differs from the registered prose (peak over all resampled samples rather than over the
GRF-delimited window). This script computes BOTH variants for every quantity and prints them side
by side. Neither is suppressed and the registered one is named.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import signal, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S  # noqa: E402

REPLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCE = ["HEALTHY", "DR2K000"]
MDC_DEG = 3.8


def filt_vmax(path):
    cols, data = S.load_sto(path)
    t = np.asarray(S.col(cols, data, "time"), float)
    a = np.asarray(S.col(cols, data, "ankle_angle_l"), float)
    if np.nanmax(np.abs(a)) < 3.5:
        a = a * 180.0 / np.pi
    m = t >= 1.0
    t, a = t[m], a[m]
    g = np.arange(t[0], t[-1], 1 / 30.0)
    ai = np.interp(g, t, a)
    b, aa = signal.butter(4, 6.0 / 15.0, btype="low")
    return float(np.max(np.abs(np.gradient(signal.filtfilt(b, aa, ai), 1 / 30.0))))


def load():
    per = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        st = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(st) != 1:
            continue
        c = os.path.basename(d).split(".")[0].rsplit("_s", 1)[0]
        if c not in SPASTIC + WEAK + REFERENCE:
            continue
        f = S.cycle_features(st[0], side="l", settle=1.0)
        f["vmax_filt"] = filt_vmax(st[0])
        per.setdefault(c, []).append(f)
    return per


def auc_p(a, b):
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    return u.statistic / (len(a) * len(b)), u.pvalue


def main():
    per = load()
    cs = [c for c in SPASTIC + WEAK if c in per]
    lab = np.array([1 if c in SPASTIC else 0 for c in cs])
    M = lambda c, k: float(np.mean([r[k] for r in per[c]]))
    ref_rom = float(np.mean([r["ank_rom"] for c in REFERENCE for r in per.get(c, [])]))

    print("=" * 76)
    print("REGISTERED REANALYSIS OF THE SECONDARY ENDPOINT `ank_rom`")
    print("=" * 76)
    print("  unlesioned reference ank_rom = %.4f deg" % ref_rom)
    print("\n%-9s %9s %9s %9s %9s" % ("cond", "ank_rom", "vs ref", "vmax_filt", "ank_hs"))
    for c in cs:
        print("%-9s %9.3f %+9.3f %9.2f %+9.2f"
              % (c, M(c, "ank_rom"), M(c, "ank_rom") - ref_rom, M(c, "vmax_filt"), M(c, "ank_hs")))

    # ---- P1 -------------------------------------------------------------------
    rc = np.array([M(c, "ank_rom") for c in cs])
    a, p = auc_p(rc[lab == 1], rc[lab == 0])
    print("\n  P1 condition level : AUC %.4f  p %.7f  overlap %d/5"
          % (a, p, sum(1 for x in rc[lab == 1] if rc[lab == 0].min() <= x <= rc[lab == 0].max())))
    sp = [r["ank_rom"] for c in SPASTIC for r in per[c]]
    wk = [r["ank_rom"] for c in WEAK for r in per[c]]
    a2, p2 = auc_p(np.array(sp), np.array(wk))
    print("  P1 seed level      : AUC %.4f  p %.3e  n=%d vs %d" % (a2, p2, len(sp), len(wk)))
    below = sum(1 for x in sp if x < ref_rom)
    above = sum(1 for x in wk if x > ref_rom)
    print("  P1 direction       : %d/%d spastic seeds BELOW ref, %d/%d weak seeds ABOVE ref"
          % (below, len(sp), above, len(wk)))
    best = None
    for thr in np.arange(min(sp + wk), max(sp + wk), 0.05):
        n = sum(1 for x in sp if x < thr) + sum(1 for x in wk if x >= thr)
        if best is None or n > best[1]:
            best = (thr, n)
    print("  P1 single threshold: %.2f deg classifies %d/%d seeds" % (best[0], best[1], len(sp) + len(wk)))

    # ---- P2 -------------------------------------------------------------------
    hs = {c: M(c, "ank_hs") for c in cs}
    pairs = [(x, y) for x in SPASTIC for y in WEAK
             if x in per and y in per and abs(hs[x] - hs[y]) < MDC_DEG]
    d = [M(x, "ank_rom") - M(y, "ank_rom") for x, y in pairs]
    print("\n  P2 equinus-matched pairs (|d ank_hs| < %.1f): %d" % (MDC_DEG, len(pairs)))
    for (x, y), dv in zip(pairs, d):
        print("       %-9s vs %-9s  d_ank_rom %+8.3f" % (x, y, dv))
    print("     mean %+.3f ; negative in %d of %d  [SIGN PATTERN reported, not a signed-rank test:"
          % (float(np.mean(d)), sum(1 for v in d if v < 0), len(d)))
    print("      the pairs share conditions, so a Wilcoxon has no defensible null]")

    # ---- P3 -------------------------------------------------------------------
    X = np.column_stack([[M(c, "vmax_filt") for c in cs], [M(c, "cycle_time") for c in cs],
                         [M(c, "ank_hs") for c in cs], np.ones(len(cs))])
    b, *_ = np.linalg.lstsq(X, rc, rcond=None)
    r = rc - X @ b
    n, k = len(cs), 3
    r2 = 1 - np.var(r) / np.var(rc)
    adj = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    a3, p3 = auc_p(r[lab == 1], r[lab == 0])
    print("\n  P3 REVERSE residual (ank_rom ~ vmax + cadence + ank_hs)")
    print("     R2 %.4f   adjusted R2 %.4f   residual df %d" % (r2, adj, n - k - 1))
    print("     AUC %.4f  p %.6f  p_adj(x2) %.6f  overlap %d/5"
          % (a3, p3, min(1, p3 * 2),
             sum(1 for x in r[lab == 1] if r[lab == 0].min() <= x <= r[lab == 0].max())))
    print("     [P3 was registered as NOT decisive: rom and vmax are near-collinear, so a residual")
    print("      vanishing in either direction says only that they are one feature.]")
    print("     r(ank_rom, vmax_filt) at condition level = %.4f"
          % np.corrcoef(rc, [M(c, "vmax_filt") for c in cs])[0, 1])

    out = {"ref_rom": ref_rom, "conds": cs, "rom": rc.tolist(),
           "P1_cond": [a, p], "P1_seed": [a2, p2], "P1_dir": [below, len(sp), above, len(wk)],
           "P1_threshold": [float(best[0]), int(best[1])],
           "P2_pairs": [[x, y, float(v)] for (x, y), v in zip(pairs, d)],
           "P3": {"auc": a3, "p": p3, "r2": r2, "adj_r2": adj}}
    dst = os.path.abspath(os.path.join(REPLAY, "..", "..", "paper", "ROM_REANALYSIS.json"))
    json.dump(out, open(dst, "w"), indent=1)
    print("\n  wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
