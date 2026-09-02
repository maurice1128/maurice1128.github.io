"""The forward residual test, run against the REGISTERED FILTERED primary. R^2 = 0.8030.

WRITTEN AND RUN 2026-08-03 (round 61), BY THE ROUND-61 AUDITOR.

WHY THIS EXISTS. The manuscripts report the forward residual as R^2 0.8030 / AUC 0.3600 /
p 0.5476, and disclose that the deposited artifact `paper/RESIDUAL_TEST.json` instead records
R^2 0.9809 because the hashed, registered `scone/residual_test.py` runs the UNFILTERED
`ank_vel_max` (the native-rate `np.gradient` peak from `sto_utils.cycle_features`). That
disclosure was correct. What was NOT correct is that `paper/METHODS_contribution.md` Sec.5.1 said
"the corrected script was re-hashed and deposited". Until this file was written there was no
deposited script anywhere in this repository that computes 0.8030, so the filtered figure -- the
one actually reported -- sat in exactly the evidential class the same document criticises: a
number with no artifact behind it. This script closes that gap, three rounds late, and the METHODS
sentence has been corrected to say when the deposit happened.

WHAT IS AND IS NOT NEW HERE. Nothing about the procedure is new or chosen now. The regression,
the covariate set, the unit of analysis and the Bonferroni factor are all taken verbatim from the
registered `residual_test.py`; the only change is the dependent variable, which is swapped from the
unfiltered `ank_vel_max` to the filtered one the registration's PROSE specified:

    30 Hz resample -> 4th-order zero-phase Butterworth low-pass at 6 Hz -> central difference,
    peak absolute value

which is byte-identical in construction to `rom_reanalysis.py`'s `filt_vmax`. This script is
therefore a re-run, not a re-analysis, and it is NOT a second registration. Running it does not
convert the filtered figure into a pre-registered result: the registered artifact remains the
unfiltered one, and both papers say so.

Both variants reach the same verdict -- the residual does not separate the arms -- which is why
this is a bookkeeping repair and not a change to any conclusion. The adjusted R^2 is printed
because at n = 10 with 3 predictors the unadjusted figure is optimistic and both manuscripts quote
the adjusted one alongside it.

Corpus: `scone/replay_crossed`, ten lesioned conditions, CONDITION level.
Writes `paper/RESIDUAL_TEST_FILTERED.json`.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import signal, stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sto_utils as S  # noqa: E402

REPLAY = os.path.join(HERE, "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
SEEDS = 4
FS, CUT, ORDER, SETTLE = 30.0, 6.0, 4, 1.0
BONFERRONI = 2


def filt_vmax(path):
    """The registered PROSE primary: resample to 30 Hz, zero-phase 6 Hz low-pass, differentiate."""
    cols, data = S.load_sto(path)
    t = np.asarray(S.col(cols, data, "time"), float)
    a = np.asarray(S.col(cols, data, "ankle_angle_l"), float)
    if np.nanmax(np.abs(a)) < 3.5:
        a = a * 180.0 / np.pi
    m = t >= SETTLE
    t, a = t[m], a[m]
    g = np.arange(t[0], t[-1], 1.0 / FS)
    ai = np.interp(g, t, a)
    b, aa = signal.butter(ORDER, CUT / (FS / 2.0), btype="low")
    return float(np.max(np.abs(np.gradient(signal.filtfilt(b, aa, ai), 1.0 / FS))))


def main():
    per = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        cond = os.path.basename(d).rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK:
            continue
        sto = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(sto) != 1:
            continue
        f = S.cycle_features(sto[0], side="l", settle=SETTLE)
        if f is None:
            continue
        f["vmax_filt"] = filt_vmax(sto[0])
        per.setdefault(cond, []).append(f)

    short = [(c, len(per.get(c, []))) for c in SPASTIC + WEAK if len(per.get(c, [])) != SEEDS]
    if short:
        raise SystemExit("[BLOCKED] incomplete cells: %s" % short)

    conds = SPASTIC + WEAK
    M = lambda c, k: float(np.mean([r[k] for r in per[c]]))  # noqa: E731
    Y = np.array([M(c, "vmax_filt") for c in conds])
    X = np.column_stack([[M(c, "ank_rom") for c in conds],
                         [M(c, "cycle_time") for c in conds],
                         [M(c, "ank_hs") for c in conds],
                         np.ones(len(conds))])
    lab = np.array([1 if c in SPASTIC else 0 for c in conds])

    print("=" * 78)
    print("FORWARD RESIDUAL TEST, REGISTERED **FILTERED** PRIMARY -- deposited round 61")
    print("  the hashed registered script runs the UNFILTERED variant (R^2 0.9809); this is the")
    print("  filtered re-run whose number both manuscripts actually report")
    print("=" * 78)
    print("\n%-9s %10s %9s %9s %8s" % ("cond", "vmax_filt", "ank_rom", "cyc_time", "ank_hs"))
    for i, c in enumerate(conds):
        print("%-9s %10.2f %9.3f %9.4f %8.3f" % (c, Y[i], X[i, 0], X[i, 1], X[i, 2]))

    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    r2 = float(1.0 - np.var(resid) / np.var(Y))
    n, k = len(conds), 3
    adj = float(1.0 - (1.0 - r2) * (n - 1) / (n - k - 1))

    def contrast(v, name):
        a, b = v[lab == 1], v[lab == 0]
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        auc = float(u.statistic / (len(a) * len(b)))
        ov = int(sum(1 for x in a if b.min() <= x <= b.max()))
        print("\n  %-42s AUC %.4f  p %.6f  p_adj(x%d) %.6f  overlap %d/%d"
              % (name, auc, u.pvalue, BONFERRONI, min(1.0, u.pvalue * BONFERRONI), ov, len(a)))
        return auc, float(u.pvalue), ov

    contrast(Y, "FILTERED ank_vel_max (for reference)")
    print("\n  regression: vmax_filt ~ ank_rom + cycle_time + ank_hs + 1")
    print("  betas: rom %+.4f  cyc %+.4f  hs %+.4f  const %+.4f" % tuple(beta))
    print("  R^2 = %.4f   adjusted R^2 = %.4f   residual df = %d" % (r2, adj, n - k - 1))
    auc, p, ov = contrast(resid, "residual after ROM + cadence + equinus")
    print("\n  At n = 10 with 3 predictors a null residual contrast is close to the expected")
    print("  outcome of the design. This is not evidence about priority in either direction.")

    out = {"computed_utc_date": "2026-08-03", "computed_by": "round-61 audit",
           "preregistered": False,
           "note": "re-run of the registered residual_test.py procedure with the FILTERED primary",
           "conds": conds, "vmax_filt": Y.tolist(), "betas": beta.tolist(),
           "resid": resid.tolist(), "r2": r2, "adj_r2": adj,
           "resid_auc": auc, "resid_p": p, "resid_overlap": ov}
    dst = os.path.abspath(os.path.join(HERE, "..", "paper", "RESIDUAL_TEST_FILTERED.json"))
    json.dump(out, open(dst, "w"), indent=1)
    print("\n  wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
