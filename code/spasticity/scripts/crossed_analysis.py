"""Registered analysis for the CROSSED budget-matched experiment. Round 46.

THE ENDPOINT BELOW WAS FIXED ON 2026-08-03 AT 00:14, BEFORE ANY CELL LAUNCHED (00:21:11), and is
reproduced here unchanged. R45-S binds: no feature may be promoted to primary after the data are
seen. If the primary fails alpha after multiplicity correction, the discrimination claim is
ABANDONED -- not re-analysed, not re-membered, not rescued by a feature chosen afterwards.

----------------------------------------------------------------------------------------------
WHY CELL RESOLUTION IS BY CONTENT AND NEVER BY NAME.  <-- read this before changing anything

The crossed experiment wrote into a namespace that ALREADY CONTAINED same-named archive runs.
SCONE does not overwrite; it appends " (1)". So on disk:

    PAR20_s1.H0914M.GH2010.S10W.D10.I.R1        archive, terminal generation 19, 2026-07-26
    PAR20_s1.H0914M.GH2010.S10W.D10.I.R1 (1)    crossed, terminal generation 89, 2026-08-03

Seven of twelve conditions collide this way: PAR20, PAR40, PAR60, HEALTHY (4 archive dirs each)
and CMW70, CMW80 (2 archive dirs each). ANY prefix glob returns both. Resolving by mtime is
defect #23 verbatim -- duplicate shadow directories where `max(key=getmtime)` read the stale one.

And the obvious content rule is NOT sufficient. `CMW70`/`CMW80`'s archive copies were themselves
run at `max_generations = 90` and reach terminal generation 89, so terminal generation alone
CANNOT separate archive from crossed for exactly the two conditions the design added to protect
the primary test's degrees of freedom. Measured:

    CMW70_s1 ... .R1        min_progress = 1e-7   max_generations = 90   gen 89   (ARCHIVE)
    CMW70_s1 ... .R1 (1)    min_progress = 0      max_generations = 90   gen 89   (CROSSED)

`min_progress` is the discriminator, and it is the one field the crossed registration pinned to a
value no archive batch used. The rule is therefore all three, from the run's own artifacts:

    min_progress == 0  AND  max_generations == 90  AND  terminal generation == 89

Verified to select exactly 48 directories. Had this been resolved by name, the CMW70 and CMW80
cells would have silently carried n = 6 -- four crossed seeds plus two 1e-7 archive runs --
reintroducing the budget confound in the one arm added to remove it, in the two conditions whose
whole purpose was to keep the condition-level contrast above alpha.
----------------------------------------------------------------------------------------------
"""
import glob
import os
import re
import sys

import numpy as np
from scipy import signal, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils  # noqa: E402

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"

# ---- THE REGISTERED TUPLE (fixed 2026-08-03 00:14, before launch) -----------------------------
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCES = ["HEALTHY", "DR2K000"]      # in NEITHER arm -- a control counted as a condition
                                          # inflates the df the design was corrected to protect
PRIMARY = "ank_vel_max_filt"
SECONDARY = "ank_rom"
FILT_HZ, FILT_ORDER, RESAMPLE_HZ = 6.0, 4, 30.0
ALPHA = 0.05
SEEDS = 4

#: Registered feature set. The effective independent test count is computed from the correlation
#: matrix of THIS set, BEFORE the group contrast is run -- not after, and not from a set trimmed
#: once the answers are visible.
FEATURES = ["ank_mean", "ank_stance_mean", "ank_hs", "ank_min", "ank_max", "ank_rom",
            "ank_swing_min", "ank_vel_max", "knee_min", "knee_rom", "hip_rom",
            "cycle_time", "stance_frac"]

REQ_MIN_PROGRESS, REQ_MAX_GEN, REQ_TERMINAL_GEN = "0", "90", 89


class Unresolved(Exception):
    """Raised when a registered quantity cannot be computed. Never caught to produce a default."""


def _prop(text, key):
    m = re.search(r"%s\s*=\s*(\S+)" % re.escape(key), text)
    return m.group(1) if m else None


def crossed_dirs():
    """Every crossed result directory, by CONTENT. See the module docstring."""
    out = {}
    for d in glob.glob(os.path.join(RESULTS, "*")):
        if not os.path.isdir(d):
            continue
        cfg, hist = os.path.join(d, "config.scone"), os.path.join(d, "history.txt")
        if not (os.path.exists(cfg) and os.path.exists(hist)):
            continue
        txt = open(cfg, encoding="utf-8", errors="replace").read()
        if _prop(txt, "min_progress") != REQ_MIN_PROGRESS:
            continue
        if _prop(txt, "max_generations") != REQ_MAX_GEN:
            continue
        try:
            last = int(open(hist, encoding="utf-8").read().strip().splitlines()[-1].split("\t")[0])
        except Exception:
            continue
        if last != REQ_TERMINAL_GEN:
            continue
        out.setdefault(os.path.basename(d).split(".")[0], []).append(d)
    return out


def filtered_ank_vel_max(sto_path):
    """The REGISTERED primary: 4th-order zero-phase Butterworth low-pass at 6 Hz on the left
    ankle angle resampled to 30 Hz, central-difference differentiated, peak over complete
    GRF-delimited cycles after settle = 1.0 s.

    Raw np.gradient on the native sample rate was the pre-registration's own finding to be
    inferior AND less defensible: 30 Hz with a 6 Hz cutoff is what a real camera and a standard
    gait-lab cutoff actually see. Registered before launch, not chosen now.
    """
    t, ang = sto_utils.series(sto_path, "ankle_angle_l") if hasattr(sto_utils, "series") else (None, None)
    if t is None:
        raise Unresolved("%s: sto_utils exposes no series() accessor" % os.path.basename(sto_path))
    t, ang = np.asarray(t, float), np.asarray(ang, float)
    keep = t >= 1.0
    t, ang = t[keep], ang[keep]
    if t.size < 20:
        raise Unresolved("%s: fewer than 20 samples after settle" % os.path.basename(sto_path))
    grid = np.arange(t[0], t[-1], 1.0 / RESAMPLE_HZ)
    a = np.interp(grid, t, ang)
    b, aa = signal.butter(FILT_ORDER, FILT_HZ / (RESAMPLE_HZ / 2.0), btype="low")
    af = signal.filtfilt(b, aa, a)
    v = np.gradient(af, 1.0 / RESAMPLE_HZ)
    i = int(np.argmax(np.abs(v)))
    return float(np.max(np.abs(v))), float((grid[i] - grid[0]) / (grid[-1] - grid[0]))


def effective_tests(matrix):
    """Cheverud-Nyholt effective independent test count. Computed BEFORE the group contrast."""
    c = np.corrcoef(np.asarray(matrix, float).T)
    c = np.nan_to_num(c, nan=0.0)
    ev = np.linalg.eigvalsh(c)
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def contrast(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    auc = u.statistic / (len(a) * len(b))
    ov = int(sum(1 for x in a if b.min() <= x <= b.max()))
    return auc, float(u.pvalue), ov


def main():
    found = crossed_dirs()
    want = SPASTIC + WEAK + REFERENCES
    print("=" * 78)
    print("CROSSED EXPERIMENT -- registered analysis")
    print("  endpoint fixed 2026-08-03 00:14; first cell launched 00:21:11")
    print("=" * 78)
    print("  cell resolution: min_progress=%s AND max_generations=%s AND terminal gen=%d"
          % (REQ_MIN_PROGRESS, REQ_MAX_GEN, REQ_TERMINAL_GEN))
    tot = sum(len(v) for k, v in found.items() if k.rsplit("_s", 1)[0] in want)
    print("  crossed directories resolved: %d\n" % tot)

    missing = []
    for cond in want:
        got = [k for k in found if k.rsplit("_s", 1)[0] == cond]
        if len(got) != SEEDS:
            missing.append((cond, len(got)))
    if missing:
        print("  [FAIL] INCOMPLETE CELLS (expected %d seeds each):" % SEEDS)
        for c, n in missing:
            print("     %-9s %d/%d" % (c, n, SEEDS))

    # E5 / B1: the optimizer NEVER writes .par.sto. Every trajectory is a replay artefact.
    nosto = [k for k, v in found.items()
             if k.rsplit("_s", 1)[0] in want and not glob.glob(os.path.join(v[0], "*.sto"))]
    if nosto:
        print("\n  [BLOCKED] BLOCKED: %d of %d resolved cells contain ZERO .sto." % (len(nosto), tot))
        print("     SCONE's CMA-ES loop does not produce `*.par.sto` -- every trajectory in this")
        print("     project is a later replay artefact. Run the REGISTERED isolated replay path")
        print("     (`replay_all.py`, which copies the chosen .par into a clean scratch dir so")
        print("     exactly one .sto can exist) over all %d cells, THEN re-run this script." % tot)
        print("     No endpoint is computed on a partially-replayed corpus: that is how a cell")
        print("     silently becomes n<4 while the report still says n=4.")
        return 2

    print("\n  (endpoint computation proceeds only once every cell has exactly one replayed .sto)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
