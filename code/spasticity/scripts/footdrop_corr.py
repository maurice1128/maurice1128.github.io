"""r(`ank_rom`, `ank_swing_min`) at seed level, under BOTH swing-window definitions.

WRITTEN AND RUN 2026-08-03 (round 61), BY THE ROUND-61 AUDITOR. Not pre-registered.

WHY THIS EXISTS. `paper/RESULTS_discrimination.md` Sec.3.1 carried r = -0.981, relayed from a
referee report with an unstated swing window and with no artifact in this repository. It also
carried an "independent recomputation" of -0.976 described as "taking the swing window as the last
40 % of the GRF-delimited cycle". That window is NOT the project's swing window. It is the
pre-repair definition that `scone/sto_utils.py` itself records as:

    DEFECT 3 REPAIR (2026-07-28, PREREGISTRATION_dose_response.md Sec.4).
    `ank_stance_mean` used to average `ank[a : a + int(0.6*(b-a))]` -- the first 60% of the
    STRIDE by sample index -- and `ank_swing_min` the last 40% by index. Neither is a phase.

The reason it was retired is the reason it must not be used to check a correlation: the 0.6 index
proxy folds up to 5 % of swing into "stance", AND THE AMOUNT IT FOLDS IN VARIES WITH THE DOSE,
because the dose changes the stance fraction. Its bias is a function of the axis being measured.
So the earlier recomputation checked a relayed number against a definition the project had already
retired, three weeks earlier, in a repair note in the very module it imported.

Both values are computed here and both are printed. The REPAIRED one is the reportable one.
The retired one is retained only so the audit trail shows what the earlier figure actually was.

Corpus: `scone/replay_crossed` (48 runs). Reported at SEED level over the 40 lesioned seeds, and
again over all 48 including the 8 reference seeds (HEALTHY, DR2K000). Writes
`paper/FOOTDROP_CORR.json`.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sto_utils as S  # noqa: E402

REPLAY = os.path.join(HERE, "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCE = ["HEALTHY", "DR2K000"]
SEEDS = 4


def retired_swing_min(path, side="l", settle=1.0):
    """The RETIRED pre-DEFECT-3 window: minimum over the last 40 % of the stride BY SAMPLE INDEX.

    Reproduced verbatim from the definition sto_utils.py's repair note describes. Not used for
    any reported quantity. Present only to identify what the earlier -0.976 figure was.
    """
    cols, d = S.load_sto(path)
    t = d[:, 0]
    ank = np.degrees(S.col(cols, d, "ankle_angle_%s" % side))
    grf, thr = S.grf_vertical(cols, d, side)
    hs = [i for i in S.heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    cycles = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    v = [float(np.min(ank[a + int(0.6 * (b - a)):b])) for a, b in cycles]
    return float(np.mean(v))


def main():
    per = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        cond = os.path.basename(d).rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK + REFERENCE:
            continue
        sto = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(sto) != 1:
            continue
        f = S.cycle_features(sto[0], side="l", settle=1.0)
        if f is None:
            continue
        f["retired_swing_min"] = retired_swing_min(sto[0])
        per.setdefault(cond, []).append(f)

    short = [(c, len(per.get(c, []))) for c in SPASTIC + WEAK + REFERENCE
             if len(per.get(c, [])) != SEEDS]
    if short:
        raise SystemExit("[BLOCKED] incomplete cells: %s" % short)

    def r_of(conds, key):
        x = [r["ank_rom"] for c in conds for r in per[c]]
        y = [r[key] for c in conds for r in per[c]]
        return float(np.corrcoef(x, y)[0, 1]), len(x)

    les = SPASTIC + WEAK
    out = {"computed_utc_date": "2026-08-03", "computed_by": "round-61 audit",
           "preregistered": False, "corpus": "replay_crossed"}

    print("=" * 78)
    print("r(ank_rom, ank_swing_min), SEED LEVEL -- computed round 61, not pre-registered")
    print("=" * 78)
    for label, key, reportable in (
            ("REPAIRED  GRF-defined swing (sto_utils, post-2026-07-28)", "ank_swing_min", True),
            ("RETIRED   last 40 % of stride by sample index (DEFECT 3)", "retired_swing_min",
             False)):
        r40, n40 = r_of(les, key)
        rall, nall = r_of(les + REFERENCE, key)
        print("\n  %s" % label)
        print("    lesioned only  n=%2d   r = %+.4f" % (n40, r40))
        print("    incl. refs     n=%2d   r = %+.4f" % (nall, rall))
        print("    %s" % ("<- REPORTABLE" if reportable else "<- NOT reportable; retired window"))
        out[key] = {"lesioned": {"n": n40, "r": r40}, "with_references": {"n": nall, "r": rall},
                    "reportable": reportable}

    print("\n  The manuscript's relayed -0.981 has no artifact and is not reproduced by either")
    print("  window. The earlier 'independent recomputation' of -0.976 is the RETIRED window.")

    dst = os.path.abspath(os.path.join(HERE, "..", "paper", "FOOTDROP_CORR.json"))
    json.dump(out, open(dst, "w"), indent=1)
    print("\n  wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
