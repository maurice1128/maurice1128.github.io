"""REGISTERED residual test. Round 47. Written BEFORE it was run; hash recorded before execution.

THE PROCEDURE, QUOTED VERBATIM FROM THE FRESH-EYES REFEREE, WHO SPECIFIED IT BEFORE EITHER THE
COORDINATOR OR THE WATCHDOG HAD SEEN THE EQUINUS PAIRING:

    test `ank_vel_max` as a residual after regressing out `ank_rom` and `cycle_time`,
    on equinus-matched gaits.

That provenance is the whole reason this is admissible. R45-S forbids promoting a feature after
seeing data; the referee's specification predates the observation that near-matched equinus pairs
exist in this corpus, so executing it is not selection. **It must not be modified after seeing what
it produces, by anyone, for any reason.** If it returns nothing, that is the result.

----------------------------------------------------------------------------------------------
WHY "EQUINUS-MATCHED" IS IMPLEMENTED AS A COVARIATE AND NOT AS A LIST OF PAIRS

The instruction was to write the matching as a RULE, never as chosen pairs, because a list of pairs
selected after seeing the table is exactly how a sixth feature would die the way the fifth just did.
Two implementations are registered here, both parameter-free or fixed in advance:

  PRIMARY (no free parameter at all): `ank_hs` enters as a third regressor alongside `ank_rom` and
  `cycle_time`. "Matched on equinus" becomes "adjusted for equinus". There is no tolerance to
  choose, no pair to pick, and every condition contributes. This is the most defensible reading and
  it is the one the verdict rests on.

  SENSITIVITY (one constant, fixed long before this round): condition pairs whose `ank_hs` differ by
  less than 3.8 deg -- the post-stroke ankle MDC used as the decision threshold throughout this
  project since round 27, and registered in the dose-response pre-registration as THRESHOLD_DEG. It
  is not a number chosen for this test. Reported alongside; it does not override the primary.

Both are computed and both are printed. Neither is selected after the fact.

----------------------------------------------------------------------------------------------
WHAT EACH OUTCOME MEANS, STATED NOW SO IT CANNOT BE RESTATED LATER

  Residual SEPARATES  -> a real emergent finding: peak ankle velocity carries information beyond
                         amplitude and cadence at matched presentation.
  Residual VANISHES   -> the honest paper is the negative one, and it is the earned result under
                         R45-S: at matched presentation, 2D sagittal kinematics do not separate
                         plantarflexor spasticity from dorsiflexor weakness; the apparent
                         separation is ankle ROM, a direct mechanical consequence of each lesion
                         rather than a discriminative gait sign.

The second is predicted by the referee's own `v*T/ROM` result (AUC 0.480, p = 1.0000). Predicting
the outcome in advance is what makes running it a measurement rather than a search.

MULTIPLICITY: x2 Bonferroni (one primary, one secondary named in advance; the 13-feature screen ran
on a different corpus). Not recomputed here to a friendlier value.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils  # noqa: E402

REPLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
MDC_DEG = 3.8                      # fixed since round 27; NOT chosen for this test
BONFERRONI = 2


def cells():
    out = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        sto = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
        if len(sto) != 1:
            continue
        tag = os.path.basename(d).split(".")[0]
        cond = tag.rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK:
            continue
        f = sto_utils.cycle_features(sto[0], side="l", settle=1.0)
        out.setdefault(cond, []).append(f)
    return out


def main():
    raw = cells()
    conds = [c for c in SPASTIC + WEAK if c in raw]
    def cm(c, k):
        return float(np.mean([r[k] for r in raw[c]]))
    Y = np.array([cm(c, "ank_vel_max") for c in conds])
    X = np.column_stack([[cm(c, "ank_rom") for c in conds],
                         [cm(c, "cycle_time") for c in conds],
                         [cm(c, "ank_hs") for c in conds],
                         np.ones(len(conds))])
    lab = np.array([1 if c in SPASTIC else 0 for c in conds])

    print("=" * 74)
    print("REGISTERED RESIDUAL TEST -- procedure specified by the referee before the pairing")
    print("=" * 74)
    print("%-9s %8s %8s %8s %8s" % ("cond", "vel_max", "ank_rom", "cyc_time", "ank_hs"))
    for i, c in enumerate(conds):
        print("%-9s %8.2f %8.2f %8.3f %8.2f" % (c, Y[i], X[i, 0], X[i, 1], X[i, 2]))

    def contrast(v, name):
        a, b = v[lab == 1], v[lab == 0]
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        auc = u.statistic / (len(a) * len(b))
        ov = int(sum(1 for x in a if b.min() <= x <= b.max()))
        print("\n  %-46s AUC %.4f  p %.6f  p_adj(x%d) %.6f  overlap %d/%d"
              % (name, auc, u.pvalue, BONFERRONI, min(1.0, u.pvalue * BONFERRONI), ov, len(a)))
        return auc, u.pvalue

    contrast(Y, "RAW ank_vel_max (for reference)")
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    print("\n  regression: vel_max ~ ank_rom + cycle_time + ank_hs + 1")
    print("  betas: rom %+.4f  cyc %+.4f  hs %+.4f  const %+.4f" % tuple(beta))
    ss = 1.0 - np.var(resid) / np.var(Y)
    print("  R^2 = %.4f  -> the three covariates explain %.1f%% of condition-level vel_max"
          % (ss, 100 * ss))
    contrast(resid, "PRIMARY: residual (rom + cycle_time + ank_hs partialled)")

    # SENSITIVITY: pairs within the pre-fixed MDC on ank_hs. A rule, not a list.
    hs = X[:, 2]
    pairs = [(conds[i], conds[j], abs(hs[i] - hs[j]))
             for i in range(len(conds)) for j in range(len(conds))
             if lab[i] == 1 and lab[j] == 0 and abs(hs[i] - hs[j]) < MDC_DEG]
    print("\n  SENSITIVITY: spastic/weak condition pairs within %.1f deg on ank_hs (rule, not a list)"
          % MDC_DEG)
    print("    %d qualifying pairs" % len(pairs))
    if pairs:
        d_raw = [cm(a, "ank_vel_max") - cm(b, "ank_vel_max") for a, b, _ in pairs]
        ri = {c: resid[i] for i, c in enumerate(conds)}
        d_res = [ri[a] - ri[b] for a, b, _ in pairs]
        for (a, b, dh), dr, ds in zip(pairs, d_raw, d_res):
            print("      %-9s vs %-9s  d_ank_hs %5.2f   d_vel_raw %+8.2f   d_vel_resid %+8.2f"
                  % (a, b, dh, dr, ds))
        w = stats.wilcoxon(d_res) if len(d_res) > 5 else None
        print("      mean d_vel_resid %+.3f%s"
              % (np.mean(d_res), ("   Wilcoxon p %.4f" % w.pvalue) if w else "   (n too small for a test)"))

    out = {"conds": conds, "raw_vel": Y.tolist(), "resid": resid.tolist(),
           "betas": beta.tolist(), "r2": float(ss),
           "n_pairs_within_mdc": len(pairs), "mdc_deg": MDC_DEG}
    p = os.path.join(os.path.dirname(REPLAY), "..", "paper", "RESIDUAL_TEST.json")
    json.dump(out, open(os.path.abspath(p), "w"), indent=1)
    print("\n  wrote %s" % os.path.abspath(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
