"""Parse SCONE/OpenSim .sto files and extract gait-cycle features.

Fixes the earlier parse bug: SCONE .sto has a variable-length header terminated by a line
`endheader`, after which the FIRST line is the tab-separated column names. Blindly looking
for a line starting with `time` fails when the header contains other tokens.
"""
import glob
import os
import re

import numpy as np


# =============================================================================================
# REGISTERED CONTROLLER SELECTION -- PREREGISTRATION_dose_response_v2.md §4.3 / §7.1a
# =============================================================================================
# WHY THIS LIVES IN CODE AND NOT ONLY IN PROSE (referee blockers B1+B2, round 37).
#
# The endpoint used to be read from whatever `*.par.sto` happened to sit in a run directory.
# Measured on the four anchor directories on 2026-08-02:
#
#   directory                     .sto present (generation)   best .par (generation)
#   DOSER0000_s1...               0005, 0009                  0034_0.827_0.628.par   (gen 34)
#   DOSER1050_s1...               0006                        0034_7.066_0.791.par   (gen 34)
#   DOSER2071_s1...               0011, 0012                  0041_0.912_0.772.par   (gen 41)
#   DOSER3100_s1...               0009, 0011                  0026_31.656_0.853.par  (gen 26)
#
# Not one of those `.sto` belongs to the run's best controller, and their mtimes fall INSIDE the
# optimizer's own writing window (DOSER3100: `.sto` at 03:20:36 and 03:24:19 while `.par` files
# kept being written until 03:44:10). They are artefacts of a replay that ran while the optimizer
# was still improving. SCONE's optimizer writes `.par`, `history.txt`, `config.scone` and
# `optimization.log`; it does NOT write `.par.sto`. 148 of the 316 non-protected archived result
# directories contain no `.sto` at all, so "read the `.sto` in the directory" is not a procedure
# that can be applied to a fresh run.
#
# Therefore: the analysed `.sto` must be PRODUCED by a registered replay of a registered `.par`
# (see `replay_all.replay_registered`), and the `.par` is chosen by the rule below.
#
# THE ASSERTION. SCONE writes a `.par` only when the running best improves, so in an untampered
# run directory the minimum-fitness `.par` is necessarily the last one written, i.e. the
# maximum-generation one. If those two disagree the directory is not a monotone best-so-far
# series -- files were copied in, deleted, or two processes wrote there -- and the record is
# ambiguous. That is exclusion E5, and it is raised, never warned.

PAR_RE = re.compile(r"^(\d+)_([-0-9.eE+]+)_([-0-9.eE+]+)\.par$")


class RegisteredSelectionError(Exception):
    """§4.3 did not select exactly one `.par`. The seed is excluded under E5."""


def par_index(path):
    """`0026_31.656_0.853.par` -> (generation=26, median=31.656, best_fitness=0.853).

    The third underscore-delimited field is the best fitness; the first is the generation.
    Returns None for any filename that does not match, so foreign files cannot enter the
    selection silently.
    """
    m = PAR_RE.match(os.path.basename(path))
    if not m:
        return None
    try:
        return int(m.group(1)), float(m.group(2)), float(m.group(3))
    except ValueError:
        return None


def select_registered_par(run_dir):
    """§4.3: the MINIMUM-FITNESS `.par`, ASSERTED to be the MAXIMUM-GENERATION `.par`.

    -> {"par", "gen", "fitness", "median", "max_gen", "n_par", "run_dir"}
    Raises RegisteredSelectionError (= exclusion E5) if
      * the directory holds no parseable `.par`;
      * the minimum fitness is attained by more than one `.par` (no tie-break is registered --
        a tie means two distinct controllers claim the same best fitness, which the run is not
        supposed to be able to produce);
      * the minimum-fitness `.par` is not also the maximum-generation `.par`.
    """
    cand = []
    for p in sorted(glob.glob(os.path.join(run_dir, "*.par"))):
        ix = par_index(p)
        if ix is not None:
            cand.append((ix[0], ix[1], ix[2], p))
    if not cand:
        raise RegisteredSelectionError(
            "E5 AMBIGUOUS RECORD: no parseable `GGGG_median_best.par` in %s" % run_dir)
    best_fit = min(c[2] for c in cand)
    best = [c for c in cand if c[2] == best_fit]
    if len(best) != 1:
        raise RegisteredSelectionError(
            "E5 AMBIGUOUS RECORD: %d `.par` files share the minimum fitness %.6g in %s: %s"
            % (len(best), best_fit, run_dir,
               ", ".join(os.path.basename(c[3]) for c in best)))
    gen, median, fit, par = best[0]
    max_gen = max(c[0] for c in cand)
    if gen != max_gen:
        raise RegisteredSelectionError(
            "E5 AMBIGUOUS RECORD: the minimum-fitness `.par` in %s is %s (generation %d, "
            "fitness %.6g) but the maximum generation present is %d (%s). SCONE writes a `.par` "
            "only on an improvement, so the best must also be the last; these disagree, so the "
            "directory is not a monotone best-so-far series and the seed is excluded under E5."
            % (run_dir, os.path.basename(par), gen, fit, max_gen,
               os.path.basename(max(cand, key=lambda c: c[0])[3])))
    return {"run_dir": os.path.abspath(run_dir), "par": os.path.abspath(par), "gen": gen,
            "fitness": fit, "median": median, "max_gen": max_gen, "n_par": len(cand)}


def load_sto(path):
    """-> (cols:list[str], data:np.ndarray). Robust to the endheader block."""
    lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    hi = None
    for i, l in enumerate(lines):
        if l.strip().lower() == "endheader":
            hi = i + 1
            break
    if hi is None:  # fall back: first line whose first field is exactly 'time'
        for i, l in enumerate(lines):
            if l.split("\t")[0].strip().lower() == "time":
                hi = i
                break
    if hi is None:
        raise ValueError("no header found in " + path)
    cols = [c.strip() for c in lines[hi].split("\t")]
    body = [r for r in lines[hi + 1:] if r.strip()]
    if not body:
        return cols, np.empty((0, len(cols)))
    # Parse with numpy rather than a Python float() per cell. These files are ~1000 x 420,
    # i.e. >400k conversions; the pure-Python loop took ~22 s per file and made every analysis
    # that touched more than a handful of trials time out.
    try:
        data = np.fromstring("\t".join(body), sep="\t")
        if data.size % len(cols) == 0 and data.size:
            return cols, data.reshape(-1, len(cols))
    except Exception:
        pass
    rows = []                                   # fallback: ragged/malformed rows
    for r in body:
        parts = r.split("\t")
        if len(parts) != len(cols):
            continue
        try:
            rows.append([float(x) for x in parts])
        except ValueError:
            continue
    return cols, np.array(rows)


def col(cols, data, name):
    """Fetch a column by exact name, else by suffix/substring match.

    SCONE's OpenSim-4 output uses path-style names
    (`/jointset/ankle_l/ankle_angle_l/value`), so a plain `ankle_angle_l` lookup must fall
    back to matching the path tail.
    """
    if name in cols:
        return data[:, cols.index(name)]
    for suf in ("/%s/value" % name, "%s/value" % name):
        for i, c in enumerate(cols):
            if c.endswith(suf):
                return data[:, i]
    for i, c in enumerate(cols):
        if c == name or c.endswith("/" + name) or c.endswith("." + name):
            return data[:, i]
    return None


def muscle_signal(cols, data, muscle, side, kind="activation"):
    """Per-muscle channel, tolerant of both naming conventions SCONE emits.

    OpenSim-4 output uses `/forceset/soleus_l/activation`; other channels appear as
    `soleus_l.input` / `soleus_l.mtu_force_norm`. A plain `soleus_l.activation` lookup finds
    neither, which silently returned None and made an entire analysis report empty groups.
    """
    m = "%s_%s" % (muscle, side)
    for want in ("/forceset/%s/%s" % (m, kind), "%s.%s" % (m, kind)):
        for i, c in enumerate(cols):
            if c == want:
                return data[:, i]
    for i, c in enumerate(cols):          # last resort: both tokens present
        if m in c and c.rstrip("/").endswith(kind):
            return data[:, i]
    return None


def grf_vertical(cols, data, side):
    """Vertical ground-reaction force for a side. SCONE names legs leg0_l / leg1_r and
    provides both raw (`grf_y`, N) and body-weight-normalised (`grf_norm_y`) channels.
    Returns (signal, threshold)."""
    for i, c in enumerate(cols):
        if c.endswith("_%s.grf_norm_y" % side):
            return data[:, i], 0.05
    for i, c in enumerate(cols):
        if c.endswith("_%s.grf_y" % side):
            return data[:, i], 20.0
    for i, c in enumerate(cols):
        lc = c.lower()
        if "grf" in lc and lc.endswith("_y") and ("_%s." % side) in lc:
            return data[:, i], 20.0
    return None, None


def heel_strikes(t, grf_y, thresh=20.0, min_stance=0.15):
    """Indices of heel-strike events = upward crossings of a vertical-GRF threshold.

    A scuffing or dropped foot briefly crosses the threshold mid-swing without truly loading,
    which previously produced TWO 'strides' per real stride (e.g. alternating 0.46 s / 0.91 s
    cycles with 4% / 89% loaded, against ~1.35 s contralaterally). Averaging a per-cycle
    quantity over those windows is meaningless, and it inflated the most extreme asymmetry
    values in the retracted V5 analysis. Fix: an upward crossing only counts as a heel strike
    if the foot then STAYS loaded for at least `min_stance` seconds.
    """
    if grf_y is None:
        return []
    on = grf_y > thresh
    idx = np.where((~on[:-1]) & (on[1:]))[0] + 1
    dt = float(np.median(np.diff(t))) if len(t) > 2 else 0.01
    need = max(int(round(min_stance / dt)), 1)
    real = []
    for i in idx:
        seg = on[i:i + need]
        if len(seg) == need and seg.all():
            real.append(i)
    # drop events closer than 0.3 s (bounce within a single contact)
    keep = []
    for i in real:
        if not keep or (t[i] - t[keep[-1]]) > 0.3:
            keep.append(i)
    return keep


def cycle_features(path, side="l", settle=1.0):
    """Steady-state gait features for one side, computed on COMPLETE gait cycles only,
    discarding the first `settle` seconds and never including a fall transient.

    Returns dict with n_cycles, and per-cycle-averaged ankle/knee/hip metrics. Returns
    None if fewer than 2 complete cycles survive (i.e. not a valid steady gait).
    """
    cols, d = load_sto(path)
    if d.size == 0:
        return None
    t = d[:, 0]
    ank = col(cols, d, "ankle_angle_%s" % side)
    kne = col(cols, d, "knee_angle_%s" % side)
    hip = col(cols, d, "hip_flexion_%s" % side)
    if ank is None:
        return None
    ank, kne, hip = [np.degrees(x) if x is not None else None for x in (ank, kne, hip)]

    grf, thr = grf_vertical(cols, d, side)
    if grf is None:
        return None
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    if len(hs) < 3:
        return None

    # complete cycles between consecutive heel strikes; drop the LAST one (may be truncated
    # by a fall) for safety
    cycles = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    if len(cycles) < 2:
        return None

    def per_cycle(f):
        return float(np.mean([f(a, b) for a, b in cycles]))

    # DEFECT 3 REPAIR (2026-07-28, PREREGISTRATION_dose_response.md §4).
    # `ank_stance_mean` used to average `ank[a : a + int(0.6*(b-a))]` -- the first 60% of the
    # STRIDE by sample index -- and `ank_swing_min` the last 40% by index. Neither is a phase.
    # Measured true stance fraction in this model runs 0.553-0.616, so the 0.6 proxy folds up to
    # 5% of swing into "stance" AND THE AMOUNT IT FOLDS IN VARIES WITH THE DOSE, because the dose
    # changes the stance fraction. That makes the proxy's bias a function of the axis being
    # measured. Stance is now the MEASURED stance: the samples of that cycle whose vertical GRF
    # exceeds the same threshold the heel-strike detector used. Swing is its complement.
    # A cycle with an empty stance or swing mask contributes nothing rather than a fabricated
    # index-based value.
    stance_on = grf > thr

    def _stance_mean(a, b):
        m = stance_on[a:b]
        return float(np.mean(ank[a:b][m])) if m.any() else float("nan")

    def _swing_min(a, b):
        m = ~stance_on[a:b]
        return float(np.min(ank[a:b][m])) if m.any() else float("nan")

    def _stance_frac(a, b):
        return float(np.mean(stance_on[a:b])) if b > a else float("nan")

    def per_cycle_nan(f):
        v = [f(a, b) for a, b in cycles]
        v = [x for x in v if np.isfinite(x)]
        return float(np.mean(v)) if v else float("nan")

    feats = {
        "n_cycles": len(cycles),
        "t_end": float(t[-1]),
        # equinus indicators (stance = GRF-defined, NOT a fixed fraction of the stride)
        "ank_min": per_cycle(lambda a, b: float(np.min(ank[a:b]))),
        "ank_max": per_cycle(lambda a, b: float(np.max(ank[a:b]))),
        "ank_mean": per_cycle(lambda a, b: float(np.mean(ank[a:b]))),
        "ank_rom": per_cycle(lambda a, b: float(np.ptp(ank[a:b]))),
        "ank_hs": per_cycle(lambda a, b: float(ank[a])),          # at heel strike
        "ank_stance_mean": per_cycle_nan(_stance_mean),
        "ank_swing_min": per_cycle_nan(_swing_min),
        "stance_frac": per_cycle_nan(_stance_frac),
        # peak dorsiflexion velocity (the reflex trigger)
        "ank_vel_max": per_cycle(
            lambda a, b: float(np.max(np.gradient(ank[a:b], t[a:b])))),
        "cycle_time": per_cycle(lambda a, b: float(t[b] - t[a])),
    }
    if kne is not None:
        feats["knee_min"] = per_cycle(lambda a, b: float(np.min(kne[a:b])))
        feats["knee_rom"] = per_cycle(lambda a, b: float(np.ptp(kne[a:b])))
    if hip is not None:
        feats["hip_rom"] = per_cycle(lambda a, b: float(np.ptp(hip[a:b])))
    return feats
