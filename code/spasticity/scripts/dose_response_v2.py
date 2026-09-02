"""Registered analysis for the dose-response study. Blocker B8.

WHY THIS FILE EXISTS, AND WHY IT IS PART OF THE PRE-REGISTRATION RATHER THAN A LATER STEP.

Every defect that has cost this project a retraction lived in the analysis, not in the simulation:
a phenotype compared across two different measures; a `.sto` chosen non-deterministically from a
directory holding more than one; a cell mean whose membership was never written down. A
pre-registration whose analysis code is written after the data arrive is not pre-registered in the
part that matters, because the part that matters is exactly where the discretion is.

So the registration is this file. The tuple that has produced SIX mutually inconsistent values for
one quantity -- Delta_EQ at true KV 0.100 -- is fixed here as constants, not as prose:

    MEASURE          which phenotype column
    SIGN_CONVENTION  whether positive means more equinus
    BASELINE         what the difference is taken against
    CELLS            the exact run tags in each cell

Prose can leave those ambiguous. Code cannot: it either names a tag or it does not.

DRY RUN. `python dose_response_v2.py --dry-run` executes the whole pipeline against the archived
converged-best replays in `replay_registered/`. It is not a test of the science -- the archive is
underpowered and its cells are not the registered cells -- it is a test that every registered
quantity is computable, that no exclusion or falsifier crashes, and that the tuple is honoured.
Anything the dry run cannot compute is a defect in this file, to be fixed before launch, not after.

FAIL CLOSED. Every ambiguity raises. A cell that cannot be resolved is not silently skipped, a
missing channel is not silently zero-filled, and a directory holding two `.sto` is an error rather
than a coin flip. The one thing this file must never do is produce a number it cannot justify.
"""
import os
import re
import sys
import glob
import json
import hashlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import cycle_features  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
REPLAY_ROOT = os.path.join(HERE, "replay_registered")

# ---------------------------------------------------------------------------
# THE REGISTERED TUPLE.  Changing any line below changes what the study measures.
# ---------------------------------------------------------------------------

#: Phenotype column. `ank_mean` averages the whole gait cycle; `ank_stance_mean` averages the
#: MEASURED stance phase only (vertical GRF above the heel-strike threshold). They differ by
#: 0.5-2 deg and MUST NEVER be compared across -- doing so is what produced the retracted claim
#: that a set of published values "reproduced nowhere".
MEASURE = "ank_stance_mean"

#: Raw ankle angle is negative when plantarflexed. The document reports equinus as a POSITIVE
#: shift, so the reported quantity is the negative of the raw difference.
SIGN_CONVENTION = "positive_is_more_equinus"

#: What Delta_EQ is a difference FROM. The healthy POOL and the KV=0 control differ by
#: 0.8178 deg in `ank_stance_mean` (the registered measure) and 0.5831 deg in `ank_mean`, on the
#: converged-best replays -- so this choice alone moves every reported value.
#:
#: ROUND 43: this comment previously said "0.62 deg", inherited verbatim from the document section
#: whose subject is that `ank_mean` and `ank_stance_mean` must never be compared across. 0.62 is
#: the WHOLE-CYCLE figure. The prohibition propagated its own violation into the registered code.
#:
#: `healthy` MEANS THE 8-TAG POOL IN `ARCHIVE_HEALTHY`, never the single run whose tag is the bare
#: word `HEALTHY`. That run reads +0.2081 stance against the pool's -0.9472; taking it as "the"
#: healthy baseline gives 0.3375 instead of 0.8178, and two separate readers did exactly that
#: tonight before the pool was checked. `analyse()` averages the pool -- read it there, not here.
BASELINE = "control"          # "control" (the KV=0 cell) or "healthy" (the 8-tag pool)

#: Decision threshold, degrees. Post-stroke ankle MDC in this literature is 3.8-11.5; the low end
#: is used throughout this document and is reused here so no new free parameter is introduced.
THRESHOLD_DEG = 3.8

#: F4 / H2 saturation falsifier: fires when the LOWER bound of the cell's 95% CI on discarded
#: injected drive exceeds this. Interval, not point estimate -- see the duty-CI rule.
SATURATION_FRAC = 0.15

#: E4: a seed is excluded only if it failed to reach this generation index in `history.txt`.
#: The former "improvement over 199->249 exceeds 5%" clause is REMOVED: it was symmetric in form
#: and asymmetric in effect, dropping the one archived top-rung run that showed no equinus.
MIN_GENERATION_INDEX = 249

#: E6: delivery gate, and the abscissa. The +-0.15 rho tolerance admits a 26% span in delivered
#: gain, wider than the rung spacing, so the ANALYSIS USES MEASURED K_hat as the x-axis and this
#: gate serves only as an outlier screen.
RHO_TOL = 0.15
COPIES_TOL = 1e-3
USE_MEASURED_KHAT_AS_ABSCISSA = True

#: Registered cells: nominal true KV -> exact run tags. At launch these are the DR2K tags.
#: For the dry run over the archive, `--dry-run` substitutes ARCHIVE_CELLS below.
#:
#: SEED SUFFIX IS UNPADDED. This read `_s%02d` and the generator writes `_s1`, not `_s01`
#: (verified: 80 files in `opt_seeds/`, `DR2K000_s1.scone` ... `DR2K000_s16.scone`). Every one of
#: the 80 cells and the baseline would have raised at analysis time -- after eleven days of
#: compute, returning nothing. That is defect #125 (64 cells queued against an uncomputable
#: endpoint) with a far longer fuse, and a two-character format string is the whole of it.
#:
#: The format is not the real fix; `assert_tags_exist()` below is. A convention that has to be
#: kept in agreement by hand across two files WILL drift again -- so the tags are checked against
#: the filesystem before any cell is read, and a missing tag is a loud pre-launch failure rather
#: than a silent post-launch one.
CELLS = {
    0.000: ["DR2K000_s%d" % i for i in range(1, 17)],
    0.050: ["DR2K050_s%d" % i for i in range(1, 17)],
    0.100: ["DR2K100_s%d" % i for i in range(1, 17)],
    0.150: ["DR2K150_s%d" % i for i in range(1, 17)],
}

#: H2 (saturation) is a SEPARATE hypothesis, not a dose rung. It is reported unconditionally and
#: never enters the dose-response sequence.
H2_CELL = {0.200: ["DR2K200_s%d" % i for i in range(1, 7)]}

#: Scenario directory the generator writes to. Checked, not assumed.
OPT_SEEDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opt_seeds")


def assert_tags_exist(cells, h2, healthy=(), opt_seeds=OPT_SEEDS):
    """Fail LOUDLY, before launch, if a registered tag has no scenario on disk.

    The padding mismatch above was invisible to every existing gate: the scenarios were correct,
    the generator was correct, the analysis was correct, and they disagreed only about a string.
    Nothing in the pipeline compared the two until the endpoint was computed -- which is after
    the compute is spent. This is the comparison, and it costs milliseconds.

    Reports EVERY missing tag, not the first: a single missing tag is a typo, eighty missing tags
    is a convention mismatch, and the count is what tells them apart.
    """
    want = [t for tags in cells.values() for t in tags]
    want += [t for tags in h2.values() for t in tags]
    want += list(healthy)
    if not os.path.isdir(opt_seeds):
        raise SystemExit("PRE-LAUNCH: scenario directory does not exist: %s" % opt_seeds)
    have = {f[:-6] for f in os.listdir(opt_seeds) if f.endswith(".scone")}
    missing = [t for t in want if t not in have]
    if missing:
        raise SystemExit(
            "PRE-LAUNCH FAILURE: %d of %d registered tags have no scenario in %s\n"
            "  missing: %s%s\n"
            "  on disk: %s\n"
            "If MOST tags are missing this is a naming-convention mismatch between the generator "
            "and this script, not a typo -- compare the seed suffix format."
            % (len(missing), len(want), opt_seeds,
               ", ".join(missing[:6]), " ..." if len(missing) > 6 else "",
               ", ".join(sorted(have)[:6]) + (" ..." if len(have) > 6 else "")))
    return len(want)

def assert_cell_counts(cells, h2, healthy=(), opt_seeds=OPT_SEEDS):
    """Reconcile the REGISTERED launch set against what the generator actually wrote.

    `assert_tags_exist` answers "does every registered tag have a scenario?". It cannot answer the
    question that bit this study: "does every scenario belong to a registered cell?". Those are
    different failures. The generator wrote SIXTEEN seeds at DR2K200 for a cell re-registered as a
    SIX-seed separate hypothesis, and nothing anywhere would have noticed ten surplus scenarios
    sitting in the launch directory next to seventy registered ones.

    Surplus is not harmless. Every seed is n; uneven n across rungs is forbidden outright by the
    design; and a launcher that globs the directory rather than reading the registration would
    have run all sixteen and reported a rung with n = 16 beside rungs with n = 16 and an H2 cell
    with n = 16 that was registered at 6. That is not a crash, it is a different study.

    Reports BOTH directions and both counts, because shortfall and surplus have opposite causes
    and opposite fixes.
    """
    want = {t for tags in cells.values() for t in tags}
    want |= {t for tags in h2.values() for t in tags}
    want |= set(healthy)
    have = {f[:-6] for f in os.listdir(opt_seeds) if f.endswith(".scone")}
    # Only DR2K* are this study's launch set; HEALTHY/PAR* in that directory are archive arms.
    have_ours = {t for t in have if t.startswith("DR2K")}
    surplus = sorted(have_ours - want)
    missing = sorted(want - have_ours)
    if surplus or missing:
        raise SystemExit(
            "PRE-LAUNCH FAILURE: registered launch set and generated scenarios disagree.\n"
            "  registered: %d tags     generated (DR2K*): %d scenarios\n"
            "  SURPLUS on disk, not registered (%d): %s\n"
            "  MISSING from disk, registered (%d): %s\n"
            "Surplus means scenarios exist that no cell claims -- do not launch until every "
            "scenario maps to a registered cell or is moved out of %s."
            % (len(want), len(have_ours), len(surplus), ", ".join(surplus) or "none",
               len(missing), ", ".join(missing) or "none", opt_seeds))
    return len(want)


#: LAUNCH HEALTHY CELL: EMPTY, DELIBERATELY, AND THIS IS THE RECONCILIATION OF THREE CELL COUNTS.
#:
#: Round 43 found three artifacts describing three different studies:
#:   generator (`opt_seeds/*.scone`)  5 DR2K cells x 16 = 80, INCLUDING DR2K200_s1..s16
#:   this file                        4 dose cells x 16 + H2 x 6 + a 16-seed `DR2KHEALTHY`
#:   document Section 3.3             "5 cells x 16 = 80 optimizations"
#: and `DR2KHEALTHY` was never generated -- it existed in this line and nowhere else in the
#: project, not in the document, not on disk. Launching it would have added 16 unregistered runs
#: to a study already short of power at the n it does register.
#:
#: THE ENDPOINT DOES NOT USE IT. `BASELINE = "control"`, and Delta_EQ is defined against the KV=0
#: cell. The healthy pool is an ARCHIVE reference for placing rungs (Section 2.1), not a launch
#: cell. So the reconciliation is: registered launch set = 4 dose cells x 16 + H2 x 6 = 70 runs,
#: no healthy cell. `analyse()` raises if anyone sets BASELINE="healthy" with this empty -- the
#: choice is blocked, not silently defaulted.
#:
#: Surplus on disk, recorded so it cannot be launched by accident: the generator wrote
#: DR2K200_s1..s16; H2 registers SIX. `DR2K200_s7..s16` are 10 scenarios that must NOT run.
#: `assert_cell_counts` fails on surplus as well as shortfall, because "extra cells quietly ran"
#: is how uneven n enters, and uneven n across rungs is forbidden outright.
LAUNCH_HEALTHY = []

#: Archive membership for the dry run. Declared explicitly BECAUSE the sign of the
#: 0.100 -> 0.200 increment is positive in seven of eight (membership x measure) combinations and
#: negative in one; naming the tags is the only way that claim becomes checkable.
#:
#: ROUND 43: REPLACED with the SECTION 2.1 REGISTERED MEMBERSHIP -- the same cells
#: `rebuild_s21.py` uses, which is membership by MEASURED delivered gain (`copies = 2.000000` on
#: the archived SPAS* form, so a nominal 0.05 delivered a true 0.100), never by tag. The previous
#: lists above were an ad-hoc subset invented for the dry run and never registered anywhere; the
#: `SD_plan = 3.7776` they produced rested on ONE cell of n=3 and is withdrawn. The four B* runs
#: stay excluded because `delivered_gain.py` ABSTAINs on them (side unresolvable) and E6 admits
#: only PASS -- a run cannot anchor a rung it is not certified to sit in.
ARCHIVE_CELLS = {
    0.000: ["DOSER0000_s1"],
    0.050: ["DOSER1050_s1"],
    0.071: ["DOSER2071_s1"],
    0.100: ["DOSER3100_s1", "SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
}
ARCHIVE_H2 = {0.200: ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"]}
ARCHIVE_HEALTHY = ["HEALTHY_s1", "HEALTHY_s2", "HEALTHY_s3", "HEALTHY_s4",
                   "DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3", "HEALTHY"]


class Unresolved(Exception):
    """Raised whenever a registered quantity cannot be computed. Never caught to produce a default."""


# ---------------------------------------------------------------------------

def wilson(k, n, z=1.959963984540054):
    """Two-sided Wilson interval for a proportion. Finite width at k=0 and k=n, unlike the
    normal approximation, which is why it is used wherever a proportion is compared to a bound."""
    if n <= 0:
        raise Unresolved("wilson: n=0")
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - h) / d), min(1.0, (c + h) / d)


def locate(tag, root):
    """The single .sto for a tag, or raise. Never picks between candidates.

    EXACT MATCH, NOT PREFIX (round 43). The previous form globbed `tag + "*"`, so the tag
    `HEALTHY` matched FIVE directories -- `HEALTHY`, `HEALTHY_s1`..`HEALTHY_s4` -- and the whole
    healthy baseline cell was silently thrown into `excluded` with the reason
    "5 directories match; ambiguous". Fail-closed behaviour saved it from becoming a wrong number,
    but the baseline the entire endpoint is a difference FROM was simply absent from the dry run.
    A SCONE result directory is `<tag>.<model>.<...>` -- the tag is the component before the first
    `.`, so it is exactly recoverable and there is no reason to pattern-match at all.
    Every syntactic heuristic in this project has been defeated by a syntax it did not anticipate.
    """
    dirs = [d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d)
            and os.path.basename(d).split(".")[0] == tag]
    dirs = [d for d in dirs if "VOID" not in os.path.basename(d)
            and "STALE" not in os.path.basename(d)]
    if not dirs:
        raise Unresolved("%s: no directory under %s" % (tag, root))
    if len(dirs) > 1:
        raise Unresolved("%s: %d directories match; ambiguous" % (tag, len(dirs)))
    stos = [s for s in glob.glob(os.path.join(dirs[0], "*.sto")) if os.path.getsize(s) > 1000]
    if len(stos) != 1:
        # E5. Two .sto in one directory is how two auditors read two different controllers.
        raise Unresolved("%s: expected exactly one .sto, found %d" % (tag, len(stos)))
    return dirs[0], stos[0]


def phenotype(tag, root):
    """The registered phenotype for one run. Raises rather than returning a default."""
    d, sto = locate(tag, root)
    feats = cycle_features(sto, side="l")
    if not feats:
        raise Unresolved("%s: no complete gait cycles" % tag)
    if MEASURE not in feats:
        raise Unresolved("%s: measure %r absent" % (tag, MEASURE))
    val = feats[MEASURE]
    if not np.isfinite(val):
        raise Unresolved("%s: measure %r is not finite" % (tag, MEASURE))
    return {"tag": tag, "dir": os.path.basename(d), "sto": os.path.basename(sto),
            "raw": float(val), "n_cycles": int(feats["n_cycles"])}


def delta_eq(cell_vals, baseline_val):
    """Delta_EQ in the registered sign convention."""
    m = float(np.mean(cell_vals))
    d = m - baseline_val
    return -d if SIGN_CONVENTION == "positive_is_more_equinus" else d


def analyse(cells, h2_cell, healthy_tags, root, label):
    out = {"label": label, "registration": {
        "MEASURE": MEASURE, "SIGN_CONVENTION": SIGN_CONVENTION, "BASELINE": BASELINE,
        "THRESHOLD_DEG": THRESHOLD_DEG, "MIN_GENERATION_INDEX": MIN_GENERATION_INDEX,
        "abscissa": "measured_K_hat" if USE_MEASURED_KHAT_AS_ABSCISSA else "nominal_KV",
        "cells": {str(k): v for k, v in cells.items()},
        "h2_cell": {str(k): v for k, v in h2_cell.items()},
        "healthy": healthy_tags}, "runs": [], "cells": {}, "excluded": []}

    def collect(tags):
        vals, kept = [], []
        for t in tags:
            try:
                r = phenotype(t, root)
            except Unresolved as e:
                out["excluded"].append({"tag": t, "reason": str(e)})
                continue
            out["runs"].append(r)
            vals.append(r["raw"])
            kept.append(t)
        return vals, kept

    hv, hk = collect(healthy_tags)
    ctrl_kv = min(cells) if cells else None
    cv, ck = collect(cells[ctrl_kv]) if ctrl_kv is not None else ([], [])

    if BASELINE == "healthy":
        if not hv:
            raise Unresolved("baseline 'healthy' selected but no healthy run resolved")
        base, base_from = float(np.mean(hv)), hk
    else:
        if not cv:
            raise Unresolved("baseline 'control' selected but the KV=0 cell resolved no run")
        base, base_from = float(np.mean(cv)), ck
    out["baseline"] = {"value": base, "from": base_from, "kind": BASELINE}

    treated_sd = []          # (sd, n) for TREATED cells only -- see SD_plan note below
    all_sd = []
    for kv in sorted(cells):
        vals, kept = (cv, ck) if kv == ctrl_kv else collect(cells[kv])
        if not vals:
            out["cells"][str(kv)] = {"status": "EMPTY"}
            continue
        d = delta_eq(vals, base)
        sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else None
        if sd is not None:
            all_sd.append(sd)
            if kv != ctrl_kv:
                treated_sd.append((sd, len(vals)))
        out["cells"][str(kv)] = {"n": len(vals), "tags": kept, "mean_raw": float(np.mean(vals)),
                                 "delta_eq": d, "sd": sd,
                                 # SIGNED, not |d|. Delta_EQ is registered as POSITIVE = more
                                 # equinus than baseline, so `abs(d)` counts a cell that is
                                 # 3.8 deg MORE DORSIFLEXED as having reached the equinus
                                 # threshold -- it would report a transition rung on a result
                                 # that refutes the hypothesis. Not hypothetical: `SPAS01_s3`
                                 # sits at +2.6563 (dorsiflexed) at a certified delivered gain
                                 # of 0.2041, so a cell can genuinely land the wrong way.
                                 # A two-sided magnitude test is right for "is there an effect";
                                 # this is "is there EQUINUS", which is one-sided by definition.
                                 "exceeds_threshold": bool(d >= THRESHOLD_DEG),
                                 "reverse_exceeds_threshold": bool(-d >= THRESHOLD_DEG)}

    # SD_plan.  ROUND 43 -- THE CODE AND THE DOCUMENT DISAGREED, AND THE DOCUMENT IS OLDER.
    # Section 3.1 registers SD_plan as "pooled across the two spastic cells (df = 10)", with the
    # healthy cell "deliberately EXCLUDED" because it is 3-5x tighter and pooling a tight cell
    # into a contrast that always has a variable cell on one side is what made n = 6 look adequate
    # when it was not.  The code computed instead the ROOT-MEAN-SQUARE of every cell SD INCLUDING
    # THE KV = 0 CONTROL -- a different estimator, unweighted by df, over a different set.  At
    # launch the control cell is n = 16 of low variance by construction, so the shipped code would
    # have deflated the very quantity the seed count is derived from.
    #
    # Disclosed, because the direction is the suspicious one: the pooled figure is SMALLER than
    # the RMS figure (5.2270 vs 5.4141 on the rebuilt archive), i.e. this correction moves the
    # number in the direction that makes the study look better.  It is adopted anyway, on two
    # grounds that do not depend on which way it moved: it is what Section 3.1 registered before
    # any of these values were seen, and df-weighted pooling is the standard estimator for a
    # common within-cell SD.  Both are emitted so the choice stays auditable.
    if treated_sd:
        num = sum((n - 1) * s * s for s, n in treated_sd)
        den = sum((n - 1) for _, n in treated_sd)
        out["SD_plan"] = float(np.sqrt(num / den)) if den > 0 else None
        out["SD_plan_df"] = int(den)
    else:
        out["SD_plan"] = None
        out["SD_plan_df"] = 0
    out["SD_plan_estimator"] = "pooled_by_df_over_treated_cells (Section 3.1)"
    out["SD_rms_all_cells_SUPERSEDED"] = (float(np.sqrt(np.mean(np.square(all_sd))))
                                          if all_sd else None)

    # transition: FIRST rung in ascending order whose SIGNED Delta_EQ clears the threshold in the
    # equinus direction. Fixed here so it cannot be chosen after the data are seen.
    trans = None
    for kv in sorted(cells):
        c = out["cells"].get(str(kv), {})
        if c.get("exceeds_threshold"):
            trans = kv
            break
    out["transition_rung"] = trans
    # A cell that clears the threshold in the WRONG direction is a reportable finding, not a
    # transition, and it must not be silently absent from the output. Under `abs()` these cells
    # were indistinguishable from equinus; listing them separately is what makes the one-sided
    # rule auditable rather than merely correct.
    out["reverse_rungs"] = [kv for kv in sorted(cells)
                            if out["cells"].get(str(kv), {}).get("reverse_exceeds_threshold")]

    # H2, reported unconditionally and outside the sequence.
    for kv in sorted(h2_cell):
        vals, kept = collect(h2_cell[kv])
        out["H2"] = {"kv": kv, "n": len(vals), "tags": kept,
                     "delta_eq_vs_baseline": delta_eq(vals, base) if vals else None,
                     "note": "separate hypothesis; NOT a dose rung; saturation test requires "
                             "per-seed discard fractions, supplied by delivered_gain.py"}
    return out


def main():
    dry = "--dry-run" in sys.argv
    root = REPLAY_ROOT if dry else REPLAY_ROOT
    # Unpadded, for the same reason as CELLS above. This line was missed by the first pass of the
    # padding fix -- one of three occurrences, and the one furthest from the others.
    cells, h2, healthy = ((ARCHIVE_CELLS, ARCHIVE_H2, ARCHIVE_HEALTHY) if dry
                          else (CELLS, H2_CELL, LAUNCH_HEALTHY))
    # PRE-LAUNCH GATE. Runs before a single .sto is read, on the live path only (the dry run
    # reads the archive, which has its own tags). See assert_tags_exist for why the format fix
    # alone is not the fix.
    if not dry:
        assert_tags_exist(cells, h2, healthy)
        assert_cell_counts(cells, h2, healthy)
    res = analyse(cells, h2, healthy, root, "DRY RUN over archived replays" if dry else "REGISTERED")

    print("=" * 78)
    print(res["label"])
    print("  measure=%s  sign=%s  baseline=%s(%.4f)  threshold=%.1f"
          % (MEASURE, SIGN_CONVENTION, BASELINE, res["baseline"]["value"], THRESHOLD_DEG))
    print("=" * 78)
    print("%-8s %4s  %-46s %10s %8s %6s" % ("trueKV", "n", "tags", "Delta_EQ", "SD", ">thr"))
    for kv in sorted(float(k) for k in res["cells"]):
        c = res["cells"][str(kv)]
        if c.get("status") == "EMPTY":
            print("%-8.3f   -- EMPTY" % kv)
            continue
        print("%-8.3f %4d  %-46s %+10.4f %8s %6s"
              % (kv, c["n"], ",".join(t[:14] for t in c["tags"])[:46], c["delta_eq"],
                 ("%.4f" % c["sd"]) if c["sd"] is not None else "  n/a", "YES" if c["exceeds_threshold"] else "no"))
    print("\n  SD_plan          = %s   (%s, df=%d)"
          % (("%.4f" % res["SD_plan"]) if res["SD_plan"] else "n/a",
             res["SD_plan_estimator"], res["SD_plan_df"]))
    print("  SD rms all cells = %s   [SUPERSEDED estimator, printed to keep the change visible]"
          % (("%.4f" % res["SD_rms_all_cells_SUPERSEDED"])
             if res["SD_rms_all_cells_SUPERSEDED"] else "n/a"))
    # The printed rule is part of the registration -- it is what a reader checks the number
    # against. It said "|Delta_EQ|" while the code now tests the SIGNED value, and a printout
    # that describes a different rule from the one that ran is how an unnoticed change survives.
    print("  transition rung  = %s   (first rung with SIGNED Delta_EQ >= %.1f toward equinus, "
          "fixed in advance)" % (res["transition_rung"], THRESHOLD_DEG))
    if res.get("reverse_rungs"):
        print("  ** REVERSE-DIRECTION rungs (>= %.1f deg MORE DORSIFLEXED than baseline): %s **"
              % (THRESHOLD_DEG, res["reverse_rungs"]))
        print("     Reported, never counted as a transition. Under the previous abs() rule these "
              "were indistinguishable from equinus.")
    if "H2" in res:
        h = res["H2"]
        print("  H2 (separate)    = KV %.3f  n=%d  Delta_EQ %s"
              % (h["kv"], h["n"], ("%+.4f" % h["delta_eq_vs_baseline"]) if h["delta_eq_vs_baseline"] is not None else "n/a"))
    if res["excluded"]:
        print("\n  EXCLUDED (%d):" % len(res["excluded"]))
        for e in res["excluded"]:
            print("    %-16s %s" % (e["tag"], e["reason"]))

    out = os.path.join(HERE, "dose_response_v2_dryrun.json" if dry else "dose_response_v2_result.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    src = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    print("\n  wrote %s" % os.path.basename(out))
    print("  THIS SCRIPT sha256 = %s" % src)
    print("  (hash this into the pre-registration; a later edit changes it and is detectable)")


if __name__ == "__main__":
    main()
