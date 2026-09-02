"""REGISTERED ANALYSIS for the downhill-provocation study -- paper/PREREG_slope.md.

DEPOSITED 2026-08-03, ROUND 62, **BEFORE THE FIRST CELL OF THE STUDY HAD FINISHED.**
=================================================================================================
At the moment this file was written the results root held FIVE directories of the 114 the study
registers, spanning TWO of its 21 cells, and three of those five had reached the terminal
generation. NO FEATURE HAD BEEN EXTRACTED FROM ANY SLOPE RUN. This file therefore cannot have
been tuned to the data, and that property is the entire reason it is deposited now rather than
when the corpus lands. Its sha256 and byte count are written to
`scone/slope_analysis_r62.py.sha256` immediately after it is written, and it is not edited
afterwards. If the sha256 of this file does not match that deposit, this is NOT the registered
analysis and its output must be discarded.

WHY A SECOND ANALYSIS FILE EXISTS
---------------------------------
`scone/slope_analysis.py` (28933 B, written 2026-08-03 21:02) predates the binding registration
(written 21:12) and implements the SUPERSEDED draft: primary `ank_stance_mean`, unit of analysis
= CONDITION with residual df 8, seven conditions, `PG*` tags. The registration that is hashed at
`paper/PREREG_slope.sha256` registers a DIFFERENT primary (`ank_rom`, raw and unfiltered), a
DIFFERENT unit (SEED level), a DIFFERENT cell list (21 cells, `SG{0,2,5}_<COND>`), a two-tier
stopping rule and four named falsifiers. `slope_analysis.py` is left byte-untouched as the
artifact of the superseded draft; nothing here reads it, and nothing here may be compared with
its output. THIS file implements the registration and only the registration.

THE DEFECT THIS DEPOSIT EXISTS TO PREVENT
-----------------------------------------
`COUNCIL_round50.md` §4.3: a confirmatory test ran on a feature variant that differed from its
own registration, inside a script that had been hashed and called "registered", and it was not
caught until an external referee recomputed from raw trajectories -- *"the reported numbers and
the registered numbers are different numbers, in a paper whose central claim is that they are the
same."* Prose fixes an endpoint; prose does not COMPUTE one. Writing the analysis after the cells
land is how an endpoint drifts without anyone choosing to drift it.

WHERE THIS FILE AND ITS BRIEF DISAGREE, THE REGISTRATION WINS. Every constant below carries the
section of `PREREG_slope.md` it comes from. Nothing here is a new decision.

WHAT IT COMPUTES
----------------
  PRIMARY   sto_utils.cycle_features(sto, side="l", settle=1.0)["ank_rom"]  -- raw, unfiltered,
            100 Hz, left ankle, on the replay of the `select_registered_par` selection. The GRF
            window is whatever THAT FUNCTION computes; it is NOT reimplemented here (§1.1).
  beta_int  the seed-level OLS `ank_rom ~ condition + D + arm:D` on the 12 primary cells (§1.3).
  F1..F4    the four registered falsifiers, exactly as §6.1 writes them.
  attrition the per-cell floor and the study-level VOID rule of §6.2(b).
  two-tier  §6.2(c), ENFORCED IN CODE: Tier 1 may stop for futility and may NEVER declare a
            positive. The check is a raised exception, not a comment.
  cells     resolved by CONTENT (§7.4), including the `<gravity>` vector read from each run's
            OWN archived `.osim`, because the usual key (min_progress / max_generations) is
            IDENTICAL across all 21 cells by design.

TWO THINGS BEYOND THE REGISTRATION, both deliberate and both flagged as such
---------------------------------------------------------------------------
  (A) SELF-TEST ON SYNTHETIC DATA, which must pass BEFORE this file is permitted to open a single
      real directory. It plants a known beta_int and recovers it, plants its negation and recovers
      that, and runs a null many times to confirm the type-I rate sits near alpha. IT PRINTS THE
      PLANTED AND RECOVERED NUMBERS. A self-test that prints "PASSED" and not the numbers is not
      evidence -- that is this project's standing rule and it is honoured literally here.
  (B) FAIL-CLOSED ON A PARTIAL CORPUS. If any cell resolves to fewer runs than it registers, the
      analysis refuses to run and prints found-vs-required per cell. It does NOT analyse whichever
      cells happen to have finished. A partially populated cell silently becomes n < 6 while the
      report still says n = 6; that mechanism produced a 39/40 threshold and seven mutually
      inconsistent values of one quantity in this project's history.
  Neither (A) nor (B) changes any registered quantity. Both are refusals, not choices.

AND ONE COVARIATE, ADDED AT ROUND 62 BEFORE HASHING, FOR VISIBILITY ONLY
-----------------------------------------------------------------------
Read from raw artifacts on 2026-08-03, at n = 1 per cell:

    SG0_DR2K000_s101   gen 0 best 17.2551  -> gen 89 best  0.616297
    SG0_DR2K000_s103   gen 0 best 17.0553  -> gen 89 best  0.633911
    SG5_DR2K000_s101   gen 0 best 93.2379  -> gen 89 best 29.3567  (min 26.2813 at gen 88)

The D0 and D5 control scenarios are byte-identical apart from `signature_prefix` and `model_file`,
so the measure, the budget, the cold start and the seed policy are the same and the only
difference is `<gravity>`. At identical cold-start parameters the 5-degree condition costs 5.4x
more at generation 0 and 90 generations recovers it only to ~26 against ~0.62 on the flat.

THIS IS NOT A DEVIATION AND IT IS NOT GROUNDS TO REOPEN THE REGISTRATION. §5.3 registered it in
advance -- *"Registered consequence: the -5 degree tier may fail to converge from cold. That is
gate G4, with a registered fallback"* -- and §7.1's G4 fallback to {0, 2} is already costed at
1.1124 deg/deg. What the trace DOES expose is the shape of G4's criterion: G4 asks only whether
the D5 control yields >= 2 complete cycles under `cycle_features`, and a run sitting at fitness 26
can stagger through two cycles and pass. The probe did pass, and returned `ank_rom` 35.88 deg
against §3.2's registered prediction of 23.0 [21.5, 24.0] -- which is what a barely-viable gait
looks like, not what a 5-degree decline looks like. A ROM inflated by non-convergence rather than
by slope would be absorbed by the D x condition interaction as if it were the effect. That is
defect A7 (equal generation NUMBERS are not equal CONVERGENCE) arriving through the very gate
written to keep it out.

Therefore terminal `best_fitness`, `best_gen`, terminal `median_fitness` and the GENERATION-0
`best_fitness` are carried per run as first-class columns, read from each run's OWN `history.txt`
and never from `.par` filenames (which are pruned on improvement only), and the interaction is
reported BOTH WITHOUT AND WITH terminal fitness as a covariate. This is the `gen_gap` precedent
from `replay_crossed.py`: an arm-level difference that would be a real confound has to be in the
provenance record, not inferred later by whoever thought to look.

  ** THE REGISTERED PRIMARY IS THE UNADJUSTED beta_int OF §1.3 AND NOTHING ELSE DECIDES. **
  The fitness-adjusted fit is a DIAGNOSTIC. It is printed beside the primary, it is written to the
  JSON, and it is never substituted for it. Fitness NEVER reweights, drops or excludes a seed:
  exclusion is governed solely by §6.2(b)'s registered attrition floor, and adding a
  convergence-based exclusion now would be exactly the post-hoc filter this registration exists
  to forbid. §4.4 already registers the per-seed fitness readout and a `fitness x D` interaction;
  this section is that clause implemented, plus the gen-0 column and the arm-level flag.

USAGE
-----
    python slope_analysis_r62.py --selftest          synthetic self-test only; touches no corpus
    python slope_analysis_r62.py --resolve           self-test + content resolution + completeness
                                                     gate; reads config/history/osim only, no replay
    python slope_analysis_r62.py --run [--tier 1|2]  the full registered analysis

Interpreter: .venv_mm (python 3.11, numpy 2.4.6, scipy 1.17.1) -- the interpreter every other
artifact in this programme was produced under.

NOTHING IN THIS FILE WRITES, MOVES OR DELETES ANYTHING UNDER
`C:\\Users\\maurice\\Documents\\SCONE\\results`. Run directories are opened read-only; the replay
copies their files OUT into `scone/replay_registered/<dir-name>/`, which is
`replay_all.replay_registered`'s registered isolation contract (§1.2). The 112 protected
directories matching `^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L` and `^opt_s[1-4]` are skipped before
their contents are ever opened.
"""

import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys
import time

import numpy as np
from scipy import stats
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sto_utils as S                    # noqa: E402  the registered feature module
import replay_all as R                   # noqa: E402  the registered replay (§1.2)
import delivered_gain as DG              # noqa: E402  the only trusted delivery instrument (G6)
import video_degradation as V            # noqa: E402  §4.2 filter constants, reused not copied

PAPER = os.path.abspath(os.path.join(HERE, "..", "paper"))
RESULTS_ROOT = r"C:\Users\maurice\Documents\SCONE\results"
OUT_JSON = os.path.join(PAPER, "SLOPE_RESULT_r62.json")
OUT_VERIF = os.path.join(PAPER, "SLOPE_VERIFICATION_r62.json")

# =================================================================================================
# SECTION 0 -- THE REGISTRATION THIS FILE IMPLEMENTS
# =================================================================================================
# The hash is quoted from paper/PREREG_slope.sha256 as of 2026-08-03. If the registration on disk
# does not hash to this, the document has been modified after the moment it certified, §8 says the
# registration is invalid, and this script will not analyse a corpus under it.
REG_PATH = os.path.join(PAPER, "PREREG_slope.md")
REG_SHA256 = "678eba3d43d15391feffe53cca3544349daacdb3253eb5b28f2cad55738530a2"
REG_BYTES = 53689

# =================================================================================================
# SECTION 1 -- EVERY REGISTERED CONSTANT, WITH THE SECTION IT COMES FROM
# =================================================================================================
SIDE = "l"                       # §1.1  left = lesioned limb
SETTLE = 1.0                     # §1.1  seconds discarded before the first admissible heel strike
GRADES = (0, 2, 5)               # §5.2  decline MAGNITUDE in degrees; D = 0 is level
D_BAR = 7.0 / 3.0                # §1.3
SXX = 12.666666666666666         # §1.3  Sum (D - D_bar)^2 over {0, 2, 5}; the doc prints 12.6667
G_MAG = 9.80665                  # §5.2  |g| preserved at every grade

# §5.2 cell list. `kv` is the fixed literal KV of the `SpasticL` block; `ta` is tib_ant_l
# max_isometric_force in the model file the run's own config.scone names. Those two numbers, read
# from the run's own artifacts, ARE the condition identity -- §5.2: "No run enters an arm by tag."
DORSIFLEXOR = "tib_ant_l"
CONDITIONS = {
    "DR2K000": {"kv": 0.000, "ta": 1759.0, "role": "CONTROL",         "arm": None},
    "DR2K050": {"kv": 0.050, "ta": 1759.0, "role": "PRIMARY_SPASTIC", "arm": "spastic"},
    "DR2K075": {"kv": 0.075, "ta": 1759.0, "role": "PRIMARY_SPASTIC", "arm": "spastic"},
    "PAR20":   {"kv": 0.000, "ta": 1407.2, "role": "PRIMARY_WEAK",    "arm": "weak"},
    "PAR40":   {"kv": 0.000, "ta": 1055.4, "role": "PRIMARY_WEAK",    "arm": "weak"},
    "DR2K200": {"kv": 0.200, "ta": 1759.0, "role": "MANIP_CHECK",     "arm": None},
    "CMW80":   {"kv": 0.000, "ta": 351.8,  "role": "MANIP_CHECK",     "arm": None},
}
PRIMARY_CONDS = ("DR2K050", "DR2K075", "PAR20", "PAR40")   # §1.3 the 12 primary cells
SPASTIC_ARM = ("DR2K050", "DR2K075")                       # §1.3 A_sp
WEAK_ARM = ("PAR20", "PAR40")                              # §1.3 A_wk
CONTROL_COND = "DR2K000"                                   # §5.2 never in beta_int
MANIP_CONDS = ("DR2K200", "CMW80")                         # §5.2 never in beta_int

# §5.4 seeds per cell, per tier. Tier 1 random_seed 101..106; Tier 2 adds 107..116 for the 12
# primary cells only -- control and manipulation-check cells stay as they are (§6.2c).
FIRST_SEED = 101
N_PER_CELL = {
    1: {"PRIMARY_SPASTIC": 6, "PRIMARY_WEAK": 6, "CONTROL": 6, "MANIP_CHECK": 4},
    2: {"PRIMARY_SPASTIC": 16, "PRIMARY_WEAK": 16, "CONTROL": 6, "MANIP_CHECK": 4},
}
TOTAL_RUNS = {1: 114, 2: 234}          # §5.4 run counts, asserted below against the cell table

# §5.3 the registered budget, identical in every cell, no exceptions
REG_MIN_PROGRESS = "0"
REG_MAX_GENERATIONS = 90
REG_TERMINAL_GEN = 89                  # §6.2(a) terminal generation INDEX
REG_MIN_VELOCITY = "1.0"               # §5.1 S10W everywhere; uphill is dropped entirely
REG_INIT_FILE = "ResultH0914Gait10.par"

# §0.1 / §1.3 / §3.3 the decision arithmetic
MDC_DEG = 3.800                        # the programme's standing decision floor
MARGIN_LEVEL = 1.5752                  # LR_ASYMMETRY.json mild_l.margin = PAR20 - DR2K050
BETA_REQ = 0.4450                      # (3.800 - 1.5752) / 5
GAP_LEVEL_MEASURED = 4.4134            # §1.3 d(0) = 22.0312 - 17.6178, for reference only
SIGMA_HAT = 2.9686                     # §5.4 pooled within-condition SD across the four mild cells
SE_TIER = {1: 0.3405, 2: 0.2085}       # §5.4 registered design SE at n = 6 / n = 16
F1_THRESHOLD = -0.2224                 # §6.1 F1, evaluated at Tier 1
TIER2_POSITIVE = 0.854                 # §6.2(c)
TIER2_NEGATIVE = 0.036                 # §6.2(c)
F4_SLOPE_TOL = 0.2                     # §6.1 F4, deg/deg
MIN_RETAINED_PER_CELL = 4              # §6.2(b) attrition floor
MAX_INDETERMINATE_CELLS = 2            # §6.2(b) of the 15 primary + control cells
SIGMA1_TRIGGER = 3.6                   # §5.4 Tier-2 n recomputation trigger
PRECISION_TARGET = 0.21                # §5.4 SE(beta_int) target if n is recomputed
ALPHA = 0.05                           # §4.6
TOL_RHO = DG.TOL_RHO                   # §5.2 / G6: |rho - 1| <= 0.15, from the instrument itself
NBOOT = 10000                          # §4.1
BOOT_SEED = 20260803                   # §4.1
SELFTEST_SEED = 20260862               # not registered: the self-test's own RNG, fixed so the
                                       # printed planted/recovered numbers are reproducible
SELFTEST_NULL_TRIALS = 2000            # not registered: null replications for the type-I check
LEVEL_REFERENCE = {                    # §4.5 free replication check against ROM_REANALYSIS.json
    "DR2K000": 20.013, "DR2K050": 19.088, "DR2K075": 16.148,
    "PAR20": 20.663, "PAR40": 23.400,
}
PRED_PER_DEGREE = {                    # §3.2 predicted per-degree response, point [lo, hi]
    "DR2K000": (0.60, 0.30, 0.80), "PAR20": (0.80, 0.60, 1.00), "PAR40": (0.80, 0.60, 1.00),
    "DR2K050": (0.10, 0.00, 0.30), "DR2K075": (0.10, 0.00, 0.30),
}
PRED_D5 = {"DR2K000": 23.0, "PAR20": 24.7, "PAR40": 27.4, "DR2K050": 19.6, "DR2K075": 16.6}

# §4.6 the feature set whose correlation spectrum gives n_eff. AMBIGUITY, RECORDED: §4.6 says
# "the registered feature set" and points at the PROCEDURE of COUNCIL_round45 §8.2 without listing
# the columns for THIS study. The list below is exactly the features THIS registration names --
# the §1.1 primary plus the §4.3 presenting-sign readouts plus the §4.4 laundering readouts --
# and it is fixed here, before the corpus exists, so it cannot be chosen after the contrast.
# `n_cycles` is excluded: it is a retention count, not a feature. The procedure itself is
# `crossed_endpoint.py` line 175, re-executed on THIS corpus and never carried across corpora
# (§4.6: CROSSED_RESULT.json's n_eff = 1.1527 "does not transfer to this one").
NEFF_FEATURES = ("ank_rom", "ank_hs", "ank_stance_mean", "cycle_time", "stance_frac")

# 112 protected directories -- never read, never written, never deleted. Copied verbatim from
# gen_slope_r60.PROTECTED_RE rather than imported, because importing that module would pull in
# gen_conditions/gen_seeds and this analysis must be incapable of building or launching anything.
PROTECTED_RE = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L|^opt_s[1-4]")


def _assert_cell_table():
    """The run counts in §5.4 are asserted against the cell table, not trusted from prose."""
    for tier in (1, 2):
        n = sum(N_PER_CELL[tier][CONDITIONS[c]["role"]] for c in CONDITIONS) * len(GRADES)
        if n != TOTAL_RUNS[tier]:
            raise RuntimeError("cell table gives %d runs at Tier %d; §5.4 registers %d"
                               % (n, tier, TOTAL_RUNS[tier]))
    if len(CONDITIONS) * len(GRADES) != 21:
        raise RuntimeError("§5.2 registers exactly 21 cells; the table gives %d"
                           % (len(CONDITIONS) * len(GRADES)))


_assert_cell_table()


# =================================================================================================
# SECTION 2 -- THE TWO-TIER RULE, ENFORCED IN CODE (§6.2c)
# =================================================================================================
# "Tier 1 (n = 6, 114 runs) may STOP the study. It may never declare a positive."
#
# That sentence is not implementable as a comment, so it is implemented as a type. The set of
# verdicts Tier 1 is permitted to emit is a frozenset that does not contain any positive verdict;
# `decide()` raises rather than returns if a Tier-1 call ever reaches one, and `main()` re-checks
# the returned verdict against the same sets immediately before printing. Two independent checks,
# because one of them could be edited out by accident and the second would still fire.

VERDICT_POSITIVE = "POSITIVE_CLINICALLY_SUFFICIENT"
VERDICT_POSITIVE_MECH_ONLY = "POSITIVE_MECHANISM_NEGATIVE_CLINICAL"
VERDICT_INDETERMINATE = "INDETERMINATE"
VERDICT_FINAL_NEGATIVE = "FINAL_NEGATIVE"
VERDICT_FUTILITY_STOP = "FINAL_NEGATIVE_TIER1_FUTILITY_STOP"
VERDICT_ESCALATE = "ESCALATE_TO_TIER2"
VERDICT_VOID_MANIP = "VOID_MANIPULATION_FAILED"
VERDICT_VOID_ATTRITION = "VOID_EXCESS_INDETERMINATE_CELLS"

#: Any verdict that asserts the hypothesis. Tier 1 may not reach any of these, ever.
POSITIVE_VERDICTS = frozenset({VERDICT_POSITIVE, VERDICT_POSITIVE_MECH_ONLY})

#: The complete, closed set Tier 1 may emit. Futility stop, escalation, or a VOID.
TIER1_PERMITTED = frozenset({VERDICT_FUTILITY_STOP, VERDICT_ESCALATE,
                             VERDICT_VOID_MANIP, VERDICT_VOID_ATTRITION})

#: The complete, closed set Tier 2 may emit.
TIER2_PERMITTED = frozenset({VERDICT_POSITIVE, VERDICT_INDETERMINATE, VERDICT_FINAL_NEGATIVE,
                             VERDICT_VOID_MANIP, VERDICT_VOID_ATTRITION})


class TwoTierViolation(RuntimeError):
    """A Tier-1 analysis attempted to emit a positive. §6.2(c) forbids it absolutely."""


def decide(tier, beta_hat, f4_fires, n_indeterminate):
    """§6.2(c). Returns (verdict, reason). Raises TwoTierViolation rather than return a positive
    at Tier 1 -- including in the branch where beta_hat is enormous, which is the branch a future
    editor would be tempted to 'fix'."""
    if tier not in (1, 2):
        raise ValueError("tier must be 1 or 2; §6.2(c) registers no other tier")

    # VOIDs outrank everything: §6.1 F4 and §6.2(b) both void rather than falsify.
    if f4_fires:
        v, why = VERDICT_VOID_MANIP, ("F4: the manipulation-check cells and the control all show "
                                      "|slope response| < %.1f deg/deg -- nothing was provoked in "
                                      "any arm, so the result is VOID, not null (§6.1 F4)"
                                      % F4_SLOPE_TOL)
    elif n_indeterminate > MAX_INDETERMINATE_CELLS:
        v, why = VERDICT_VOID_ATTRITION, ("%d of the 15 primary+control cells are "
                                          "INDETERMINATE-BY-ATTRITION; §6.2(b) voids the study "
                                          "above %d" % (n_indeterminate, MAX_INDETERMINATE_CELLS))
    elif tier == 1:
        if beta_hat <= F1_THRESHOLD:
            v, why = VERDICT_FUTILITY_STOP, (
                "beta_hat = %+.4f <= %.4f, so the two-sided 95%% upper bound "
                "(beta_hat + 1.96 x %.4f = %+.4f) falls below beta_req = %.4f: the clinically "
                "required interaction is excluded outright. STOP, registered as a FINAL negative "
                "(§6.1 F1, §6.2(c), §6.3)."
                % (beta_hat, F1_THRESHOLD, SE_TIER[1], beta_hat + 1.96 * SE_TIER[1], BETA_REQ))
        else:
            v, why = VERDICT_ESCALATE, (
                "beta_hat = %+.4f > %.4f: ESCALATE the 12 primary cells from n = 6 to n = 16 "
                "using random_seed 107-116. TIER 1 MAY NOT DECLARE A POSITIVE AT ANY VALUE OF "
                "beta_hat, however large (§6.2(c)); stopping only for futility cannot inflate "
                "type-I error for the positive claim, it can only cost power."
                % (beta_hat, F1_THRESHOLD))
    else:
        if beta_hat >= TIER2_POSITIVE:
            v, why = VERDICT_POSITIVE, (
                "beta_hat = %+.4f >= %.4f: the lower bound on the D = 5 margin is >= %.3f deg -- "
                "provocation delivers a clinically sufficient effect size (§6.2(c))."
                % (beta_hat, TIER2_POSITIVE, MDC_DEG))
        elif beta_hat < TIER2_NEGATIVE:
            v, why = VERDICT_FINAL_NEGATIVE, (
                "beta_hat = %+.4f < %.4f: the upper bound on the D = 5 margin is < %.3f deg -- "
                "FINAL negative, and §6.3 is the write-up." % (beta_hat, TIER2_NEGATIVE, MDC_DEG))
        else:
            v, why = VERDICT_INDETERMINATE, (
                "%.4f <= beta_hat = %+.4f < %.4f: INDETERMINATE. Neither claim is licensed. The "
                "band is 3.92 x SE wide and does not vanish at any feasible n; §6.2(c) states "
                "this in advance so it is not discovered later."
                % (TIER2_NEGATIVE, beta_hat, TIER2_POSITIVE))

    permitted = TIER1_PERMITTED if tier == 1 else TIER2_PERMITTED
    if tier == 1 and v in POSITIVE_VERDICTS:
        raise TwoTierViolation(
            "TIER 1 REACHED A POSITIVE VERDICT (%s) at beta_hat = %+.4f. §6.2(c) forbids this "
            "absolutely: Tier 1 may stop for futility and may NEVER declare a positive. This is a "
            "hard stop, not a warning." % (v, beta_hat))
    if v not in permitted:
        raise TwoTierViolation("Tier %d emitted %r, which is not in its registered verdict set %s"
                               % (tier, v, sorted(permitted)))
    return v, why


# =================================================================================================
# SECTION 3 -- ORDINARY LEAST SQUARES, AND THE REGISTERED beta_int (§1.3)
# =================================================================================================
def ols(X, y):
    """Plain OLS with an explicit full-rank assertion. Returns beta, cov, se, df, sigma2, resid.

    Written out rather than delegated so that the design matrix of §1.3 is visible in this file
    and cannot be changed by a library upgrade.
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n, p = X.shape
    rank = int(np.linalg.matrix_rank(X))
    if rank != p:
        raise RuntimeError("design matrix is rank %d of %d columns -- the registered model "
                           "`ank_rom ~ condition + D + arm:D` is not identifiable on this corpus, "
                           "which means a cell is missing a grade" % (rank, p))
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    resid = y - X @ beta
    df = n - p
    if df <= 0:
        raise RuntimeError("residual df = %d; refusing to report a standard error" % df)
    sigma2 = float(resid @ resid) / df
    cov = sigma2 * XtXi
    return beta, cov, np.sqrt(np.diag(cov)), df, sigma2, resid


def design_primary(rows, covariate=None):
    """§1.3: `ank_rom ~ condition (4 levels, fixed) + D + arm:D` at SEED level.

    Columns, in this order and no other:
        0  intercept
        1  I(cond == DR2K075)      condition fixed effects, reference cell = DR2K050
        2  I(cond == PAR20)
        3  I(cond == PAR40)
        4  D                       = the spastic arm's slope, because arm_weak is 0 there
        5  D * I(arm == weak)      = BETA_INT, the arm:D contrast, WEAK MINUS SPASTIC
       [6] covariate               optional, DIAGNOSTIC ONLY, never in the registered primary

    The `arm` main effect is deliberately absent: every condition belongs to exactly one arm, so
    an arm dummy is a linear combination of the condition dummies and the model would not be
    identifiable. The arm contrast survives only in the interaction, which is the primary. The
    weak-minus-spastic orientation is §1.3's: "beta_int is the arm:D contrast (weak minus
    spastic)", and the mechanism of §0.2 predicts it POSITIVE.
    """
    ref = PRIMARY_CONDS[0]
    others = PRIMARY_CONDS[1:]
    X, y = [], []
    for r in rows:
        c = r["cond"]
        if c not in PRIMARY_CONDS:
            raise RuntimeError("%s is not one of the 12 primary cells' conditions" % c)
        d = float(r["D"])
        weak = 1.0 if CONDITIONS[c]["arm"] == "weak" else 0.0
        row = [1.0] + [1.0 if c == o else 0.0 for o in others] + [d, d * weak]
        if covariate is not None:
            row.append(float(r[covariate]))
        X.append(row)
        y.append(float(r["ank_rom"]))
    names = (["intercept"] + ["cond[%s]" % o for o in others] + ["D", "arm_weak:D"]
             + ([covariate] if covariate is not None else []))
    if names[4] != "D" or names[5] != "arm_weak:D":
        raise RuntimeError("design column order changed; beta_int is read positionally")
    _ = ref
    return np.array(X, float), np.array(y, float), names


IX_D = 4
IX_INT = 5


def fit_beta_int(rows, covariate=None):
    """Fit §1.3 and return every quantity the registration asks to be reported with it."""
    X, y, names = design_primary(rows, covariate=covariate)
    beta, cov, se, df, sigma2, resid = ols(X, y)
    b_int, se_int = float(beta[IX_INT]), float(se[IX_INT])
    tcrit = float(stats.t.ppf(1.0 - ALPHA / 2.0, df))
    lo, hi = b_int - tcrit * se_int, b_int + tcrit * se_int
    tstat = b_int / se_int if se_int > 0 else float("nan")
    p_two = float(2.0 * stats.t.sf(abs(tstat), df))
    b_sp = float(beta[IX_D])                                  # spastic arm slope
    b_wk = float(beta[IX_D] + beta[IX_INT])                   # weak arm slope
    var_wk = float(cov[IX_D, IX_D] + cov[IX_INT, IX_INT] + 2.0 * cov[IX_D, IX_INT])
    return {
        "names": names,
        "beta": [float(b) for b in beta],
        "se": [float(s) for s in se],
        "beta_int": b_int, "se_int": se_int, "df": int(df),
        "ci95": [float(lo), float(hi)], "t": float(tstat), "p_two_sided": p_two,
        "sigma_resid": float(math.sqrt(sigma2)),
        "slope_spastic": b_sp, "se_slope_spastic": float(math.sqrt(cov[IX_D, IX_D])),
        "slope_weak": b_wk, "se_slope_weak": float(math.sqrt(var_wk)),
        "implied_gap_change_at_D5": 5.0 * b_int,
        "n_obs": int(X.shape[0]), "covariate": covariate,
    }


def cell_slope(rows, cond):
    """Per-condition slope response: OLS of ank_rom on D at seed level, within one condition.

    Used by F2 (§6.1, spastic arm vs the unlesioned control), F4 (§6.1, the manipulation check)
    and §2's arm-specificity requirement. This is a per-CONDITION quantity across grades, so it is
    a two-parameter fit and is reported with its own SE and df.
    """
    sub = [r for r in rows if r["cond"] == cond]
    if len(sub) < 3:
        return None
    D = np.array([float(r["D"]) for r in sub])
    if len(np.unique(D)) < 2:
        return None
    y = np.array([float(r["ank_rom"]) for r in sub])
    X = np.column_stack([np.ones_like(D), D])
    beta, cov, se, df, sigma2, _ = ols(X, y)
    tcrit = float(stats.t.ppf(1.0 - ALPHA / 2.0, df))
    return {"cond": cond, "slope": float(beta[1]), "se": float(se[1]), "df": int(df),
            "ci95": [float(beta[1] - tcrit * se[1]), float(beta[1] + tcrit * se[1])],
            "intercept": float(beta[0]), "n": len(sub),
            "grades": sorted(set(int(d) for d in D))}


def closed_form_beta_int(cell_means):
    """§1.3's closed form on ARM GAPS, as a cross-check on the OLS coefficient.

        beta_int = Sum_D (D - D_bar) d(D) / Sum_D (D - D_bar)^2 ,  d(D) = A_wk(D) - A_sp(D)

    Equal to the OLS coefficient only when the cells are balanced. Printed with that caveat rather
    than quietly, because §2 point 3 is explicit that an order statistic and a linear contrast are
    different estimands and this project has confused them before.
    """
    num = 0.0
    gaps = {}
    for D in GRADES:
        wk = [cell_means[(c, D)] for c in WEAK_ARM if (c, D) in cell_means]
        sp = [cell_means[(c, D)] for c in SPASTIC_ARM if (c, D) in cell_means]
        if len(wk) != len(WEAK_ARM) or len(sp) != len(SPASTIC_ARM):
            return None, {}
        d = float(np.mean(wk) - np.mean(sp))
        gaps[D] = d
        num += (D - D_BAR) * d
    return num / SXX, gaps


def rung_margin(cell_means, D):
    """§4.1, definition FIXED before the data exist so a changed binding pair is a recomputation
    and not a choice: `min over {PAR20, PAR40}` minus `max over {DR2K050, DR2K075}`."""
    wk = [(c, cell_means[(c, D)]) for c in WEAK_ARM if (c, D) in cell_means]
    sp = [(c, cell_means[(c, D)]) for c in SPASTIC_ARM if (c, D) in cell_means]
    if len(wk) != len(WEAK_ARM) or len(sp) != len(SPASTIC_ARM):
        return None
    wmin = min(wk, key=lambda kv: kv[1])
    smax = max(sp, key=lambda kv: kv[1])
    return {"D": D, "margin": float(wmin[1] - smax[1]),
            "binding_weak": wmin[0], "binding_spastic": smax[0]}


def margin_bootstrap(per_cell_vals, D, rng):
    """§4.1: 10 000-resample bootstrap CI on the rung-to-rung margin, using the resampling scheme
    already implemented in `scone/lr_asymmetry.py` `report()` (lines 104-121) -- resample seeds
    WITH replacement WITHIN each cell, recompute min(weak cell means) - max(spastic cell means).
    RNG seed 20260803, as registered."""
    wk = [np.asarray(per_cell_vals[(c, D)], float) for c in WEAK_ARM if (c, D) in per_cell_vals]
    sp = [np.asarray(per_cell_vals[(c, D)], float) for c in SPASTIC_ARM if (c, D) in per_cell_vals]
    if len(wk) != len(WEAK_ARM) or len(sp) != len(SPASTIC_ARM):
        return None
    boot = np.empty(NBOOT, float)
    for i in range(NBOOT):
        boot[i] = (min(float(np.mean(rng.choice(v, len(v)))) for v in wk)
                   - max(float(np.mean(rng.choice(v, len(v)))) for v in sp))
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    return {"ci95": [lo, hi], "p_le_0": float(np.mean(boot <= 0.0)),
            "p_ge_mdc": float(np.mean(boot >= MDC_DEG))}


def n_eff_from(matrix):
    """§4.6 / COUNCIL_round45 §8.2, the PROCEDURE re-executed on THIS corpus. Identical arithmetic
    to `crossed_endpoint.py` line 175: n_eff = (sum lambda)^2 / sum(lambda^2) over the eigenvalues
    of the feature correlation matrix. A constant is never carried across corpora."""
    M = np.asarray(matrix, float)
    if M.shape[0] < 3 or M.shape[1] < 2:
        return None
    C = np.corrcoef(M.T)
    if not np.all(np.isfinite(C)):
        return None
    ev = np.linalg.eigvalsh(C)
    return float(ev.sum() ** 2 / (ev ** 2).sum())


# =================================================================================================
# SECTION 4 -- SELF-TEST ON SYNTHETIC DATA (beyond the registration; a gate, not a claim)
# =================================================================================================
# It runs BEFORE anything is allowed to open a real directory. `_require_selftest()` is called at
# the top of every function that touches the corpus, so the ordering is enforced by the code and
# not by the order of statements in main(). It PRINTS the planted and the recovered numbers.

_SELFTEST_PASSED = False


def _require_selftest():
    if not _SELFTEST_PASSED:
        raise RuntimeError("REFUSING TO READ THE CORPUS: the synthetic self-test has not passed in "
                           "this process. An estimator that has not been shown to recover a "
                           "planted effect is not evidence about a real one.")


def _synth(rng, n_per_cell, beta_plant, sigma, slope_common=0.30,
           cond_offset=None):
    """Seed-level synthetic corpus over the 12 primary cells with a KNOWN beta_int.

    Generating truth, written out so the planted value is unambiguous:

        ank_rom = mu_cond + slope_common * D + beta_plant * D * I(arm == weak) + N(0, sigma^2)

    so the weak arm's slope is (slope_common + beta_plant), the spastic arm's is slope_common, and
    their difference -- the estimand of §1.3 -- is exactly beta_plant.
    """
    if cond_offset is None:
        cond_offset = {"DR2K050": 19.0877, "DR2K075": 16.1478,
                       "PAR20": 20.6629, "PAR40": 23.3995}
    rows = []
    for c in PRIMARY_CONDS:
        weak = 1.0 if CONDITIONS[c]["arm"] == "weak" else 0.0
        for D in GRADES:
            mu = cond_offset[c] + slope_common * D + beta_plant * D * weak
            for k in range(n_per_cell):
                rows.append({"cond": c, "D": D, "seed": FIRST_SEED + k,
                             "ank_rom": float(mu + rng.normal(0.0, sigma))})
    return rows


def selftest(verbose=True):
    """Plant, recover, negate, recover, and measure the type-I rate. PRINTS THE NUMBERS."""
    global _SELFTEST_PASSED
    rng = np.random.default_rng(SELFTEST_SEED)
    n = N_PER_CELL[1]["PRIMARY_SPASTIC"]
    sigma = SIGMA_HAT
    rec = {"rng_seed": SELFTEST_SEED, "n_per_cell": n, "sigma": sigma, "checks": []}

    def head(s):
        if verbose:
            print("\n" + "-" * 96 + "\n" + s + "\n" + "-" * 96)

    if verbose:
        print("=" * 96)
        print("SELF-TEST ON SYNTHETIC DATA -- runs BEFORE any real directory may be opened")
        print("=" * 96)
        print("  This is NOT part of PREREG_slope.md. It is a gate on the estimator, added at the")
        print("  round-62 deposit. It plants a known beta_int and recovers it; plants its negation")
        print("  and recovers that; runs a null %d times and checks the type-I rate against alpha."
              % SELFTEST_NULL_TRIALS)
        print("  Every planted and every recovered number is printed. A self-test that prints")
        print("  'PASSED' and not the numbers is not evidence.")
        print("\n  design    : %d primary cells (4 conditions x 3 grades), n = %d seeds per cell,"
              % (len(PRIMARY_CONDS) * len(GRADES), n))
        print("              sigma = %.4f deg (§5.4 pooled within-condition SD), RNG seed %d"
              % (sigma, SELFTEST_SEED))
        print("  estimator : fit_beta_int() -- THE SAME FUNCTION the real corpus is fitted with")
        print("  registered SE at this n (§5.4 table) : %.4f deg/deg" % SE_TIER[1])

    # ---- (0) NOISELESS: the estimator's arithmetic, separated from the design's precision --------
    head("(0) NOISELESS PLANT -- the estimator ARITHMETIC, with sampling noise removed")
    ok_all = True
    if verbose:
        print("    At sigma = %.4f a single n = %d replicate carries SE %.4f, so a one-shot"
              % (sigma, n, SE_TIER[1]))
        print("    recovery is EXPECTED to miss the planted value by a few tenths. That is the")
        print("    design's precision, not an estimator error, and §5.4 registers it as the reason")
        print("    n = 4 was rejected. To separate the two, the plants below use sigma = 1e-9, so")
        print("    the recovered value must equal the planted one to within floating point.")
    for b_plant in (BETA_REQ, 0.70, TIER2_POSITIVE, -0.70, 0.0, F1_THRESHOLD):
        f = fit_beta_int(_synth(rng, n, b_plant, 1e-9))
        err = f["beta_int"] - b_plant
        ok = abs(err) < 1e-6
        ok_all &= ok
        if verbose:
            print("    planted beta_int = %+.10f   recovered beta_int = %+.10f   error = %+.3e  %s"
                  % (b_plant, f["beta_int"], err, "PASS" if ok else "*** FAIL ***"))
        rec["checks"].append({"kind": "plant_noiseless", "planted": b_plant,
                              "recovered": f["beta_int"], "error": err, "pass": bool(ok)})

    # ---- (1) plant a positive beta_int and recover it -------------------------------------------
    head("(1) PLANT A POSITIVE beta_int AND RECOVER IT AT THE REGISTERED sigma AND n")
    planted_values = [BETA_REQ, 0.70, TIER2_POSITIVE]     # §3.3's threshold, point estimate, and
    for b_plant in planted_values:                        # §6.2(c)'s Tier-2 positive boundary
        fit = fit_beta_int(_synth(rng, n, b_plant, sigma))
        err = fit["beta_int"] - b_plant
        inside = fit["ci95"][0] <= b_plant <= fit["ci95"][1]
        # PASS is |error| < 4 SE, not CI coverage. A 95% CI misses 1 time in 20 BY CONSTRUCTION,
        # so asserting coverage on a handful of single replicates would make this gate fail ~1 run
        # in 4 for a correct estimator -- a flaky gate teaches people to ignore it. Coverage is
        # PRINTED as information; the assertion is the 4-SE band, which a correct estimator misses
        # about 6 times in 100 000.
        ok = abs(err) < 4.0 * fit["se_int"]
        ok_all &= ok
        if verbose:
            print("    planted beta_int = %+.4f    recovered beta_int = %+.4f    error = %+.4f"
                  " = %+.2f SE" % (b_plant, fit["beta_int"], err, err / fit["se_int"]))
            print("        SE %.4f (registered %.4f)  95%% CI [%+.4f, %+.4f]  df %d  t %+.3f  "
                  "p %.4g" % (fit["se_int"], SE_TIER[1], fit["ci95"][0], fit["ci95"][1],
                              fit["df"], fit["t"], fit["p_two_sided"]))
            print("        planted value inside the recovered 95%% CI : %s (reported, not "
                  "asserted)   -> %s" % ("YES" if inside else "NO",
                                         "PASS" if ok else "*** FAIL ***"))
        rec["checks"].append({"kind": "plant_positive", "planted": b_plant,
                              "recovered": fit["beta_int"], "se": fit["se_int"],
                              "ci95": fit["ci95"], "inside": bool(inside), "pass": bool(ok)})

    # ---- (2) plant the NEGATION and recover that ------------------------------------------------
    head("(2) PLANT THE NEGATION OF EACH AND RECOVER THAT")
    if verbose:
        print("    An estimator that recovers +b but not -b has a sign convention error, which is")
        print("    the single most consequential thing that can go wrong here: §1.3 fixes")
        print("    beta_int as WEAK MINUS SPASTIC and §0.2 predicts it POSITIVE, so a flipped sign")
        print("    would turn a refutation into a confirmation.")
    for b_plant in planted_values:
        b_neg = -b_plant
        fit = fit_beta_int(_synth(rng, n, b_neg, sigma))
        err = fit["beta_int"] - b_neg
        inside = fit["ci95"][0] <= b_neg <= fit["ci95"][1]
        # The SIGN of a single replicate is NOT asserted here, and the reason is arithmetic:
        # |b_neg| is 1.3 to 2.5 times the design SE at this n, so a correct estimator
        # returns the wrong sign a substantial fraction of the time on ONE draw. That is the
        # design's precision (§5.4), not a sign-convention error. The sign convention is asserted
        # EXACTLY in section (0) at sigma = 1e-9, and IN THE MEAN in section (2b). Here it is
        # printed only.
        ok = abs(err) < 4.0 * fit["se_int"]
        ok_all &= ok
        if verbose:
            print("    planted beta_int = %+.4f    recovered beta_int = %+.4f    error = %+.4f"
                  " = %+.2f SE" % (b_neg, fit["beta_int"], err, err / fit["se_int"]))
            print("        SE %.4f  95%% CI [%+.4f, %+.4f]  planted inside CI : %s   "
                  "recovered sign NEGATIVE : %s (printed, not asserted -- see (0) and (2b))  -> %s"
                  % (fit["se_int"], fit["ci95"][0], fit["ci95"][1], "YES" if inside else "NO",
                     "YES" if fit["beta_int"] < 0 else "NO", "PASS" if ok else "*** FAIL ***"))
        rec["checks"].append({"kind": "plant_negative", "planted": b_neg,
                              "recovered": fit["beta_int"], "se": fit["se_int"],
                              "ci95": fit["ci95"], "inside": bool(inside), "pass": bool(ok)})

    # ---- (2b) UNBIASEDNESS at the registered sigma: mean recovery over many replications ---------
    head("(2b) MEAN RECOVERY OVER MANY REPLICATIONS AT THE REGISTERED sigma")
    if verbose:
        print("    A one-shot recovery at sigma = %.4f is dominated by sampling noise (section 1)."
              % sigma)
        print("    Averaging shows the estimator is centred on the planted value rather than")
        print("    shifted by it, which is the property a one-shot check cannot demonstrate.")
    for b_plant in (BETA_REQ, 0.70, -0.70):
        bb = np.array([fit_beta_int(_synth(rng, n, b_plant, sigma))["beta_int"]
                       for _ in range(400)], float)
        mean_rec = float(np.mean(bb))
        se_mean = float(np.std(bb, ddof=1) / math.sqrt(len(bb)))
        sign_ok = (mean_rec < 0.0) == (b_plant < 0.0)     # asserted HERE, not on one replicate
        ok = abs(mean_rec - b_plant) <= 4.0 * se_mean and sign_ok
        ok_all &= ok
        if verbose:
            print("    planted beta_int = %+.4f   mean recovered over 400 = %+.4f   "
                  "(SE of the mean %.4f, bias %+.4f, sign matches planted: %s)  %s"
                  % (b_plant, mean_rec, se_mean, mean_rec - b_plant,
                     "YES" if sign_ok else "NO", "PASS" if ok else "*** FAIL ***"))
        rec["checks"].append({"kind": "plant_mean_recovery", "planted": b_plant, "trials": 400,
                              "mean_recovered": mean_rec, "se_of_mean": se_mean,
                              "bias": mean_rec - b_plant, "pass": bool(ok)})

    # ---- (3) per-arm slopes recovered separately ------------------------------------------------
    head("(3) THE TWO ARM SLOPES ARE RECOVERED SEPARATELY, NOT ONLY THEIR DIFFERENCE")
    b_plant, slope_common = 0.70, 0.10          # §3.2: spastic +0.10, weak +0.80 -> beta_int 0.70
    fit = fit_beta_int(_synth(rng, n, b_plant, sigma, slope_common=slope_common))
    ok = (abs(fit["slope_spastic"] - slope_common) < 4.0 * fit["se_slope_spastic"]
          and abs(fit["slope_weak"] - (slope_common + b_plant)) < 4.0 * fit["se_slope_weak"])
    ok_all &= ok
    if verbose:
        print("    planted spastic slope = %+.4f   recovered = %+.4f  (SE %.4f)"
              % (slope_common, fit["slope_spastic"], fit["se_slope_spastic"]))
        print("    planted weak    slope = %+.4f   recovered = %+.4f  (SE %.4f)"
              % (slope_common + b_plant, fit["slope_weak"], fit["se_slope_weak"]))
        print("    planted beta_int      = %+.4f   recovered = %+.4f          -> %s"
              % (b_plant, fit["beta_int"], "PASS" if ok else "*** FAIL ***"))
    rec["checks"].append({"kind": "arm_slopes", "planted_spastic": slope_common,
                          "recovered_spastic": fit["slope_spastic"],
                          "planted_weak": slope_common + b_plant,
                          "recovered_weak": fit["slope_weak"],
                          "planted_beta_int": b_plant, "recovered_beta_int": fit["beta_int"],
                          "pass": bool(ok)})

    # ---- (4) the null: type-I rate near alpha ---------------------------------------------------
    head("(4) NULL: PLANT beta_int = 0 AND MEASURE THE TYPE-I RATE AGAINST alpha")
    rej = 0
    bhats = np.empty(SELFTEST_NULL_TRIALS, float)
    ses = np.empty(SELFTEST_NULL_TRIALS, float)
    for i in range(SELFTEST_NULL_TRIALS):
        f = fit_beta_int(_synth(rng, n, 0.0, sigma))
        bhats[i], ses[i] = f["beta_int"], f["se_int"]
        if not (f["ci95"][0] <= 0.0 <= f["ci95"][1]):
            rej += 1
    rate = rej / float(SELFTEST_NULL_TRIALS)
    mc_se = math.sqrt(ALPHA * (1.0 - ALPHA) / SELFTEST_NULL_TRIALS)
    ok = abs(rate - ALPHA) <= 3.0 * mc_se
    ok_all &= ok
    # a second, independent read on the same replications: the empirical SD of beta_hat must match
    # the registered design SE of §5.4, which is what the n = 6 row of that table asserts.
    emp_sd, mean_se = float(np.std(bhats, ddof=1)), float(np.mean(ses))
    ok_sd = abs(emp_sd - SE_TIER[1]) < 0.05 and abs(mean_se - SE_TIER[1]) < 0.05
    ok_all &= ok_sd
    if verbose:
        print("    planted beta_int = %+.4f   (exactly zero, %d replications)"
              % (0.0, SELFTEST_NULL_TRIALS))
        print("    recovered mean beta_int      = %+.6f   (expected 0)" % float(np.mean(bhats)))
        print("    recovered  sd  beta_int      =  %.6f   empirical" % emp_sd)
        print("    mean recovered SE(beta_int)  =  %.6f   model-based" % mean_se)
        print("    §5.4 registered design SE    =  %.6f   = sigma / sqrt(%.4f x %d)"
              % (SE_TIER[1], SXX, n))
        print("        empirical sd and mean SE both match the registered SE : %s"
              % ("YES" if ok_sd else "*** NO ***"))
        print("    95%% CI excluded 0 in %d / %d replications" % (rej, SELFTEST_NULL_TRIALS))
        print("    measured type-I rate = %.4f   against alpha = %.4f   (Monte-Carlo SE %.4f, "
              "3-SE band [%.4f, %.4f])" % (rate, ALPHA, mc_se, ALPHA - 3 * mc_se,
                                           ALPHA + 3 * mc_se))
        print("        -> %s" % ("PASS" if ok else "*** FAIL ***"))
    rec["checks"].append({"kind": "null_type_I", "planted": 0.0, "trials": SELFTEST_NULL_TRIALS,
                          "mean_recovered": float(np.mean(bhats)), "sd_recovered": emp_sd,
                          "mean_se": mean_se, "registered_se": SE_TIER[1],
                          "rejections": rej, "rate": rate, "alpha": ALPHA, "pass": bool(ok
                                                                                        and ok_sd)})

    # ---- (5) power at the registered threshold, printed because a gate needs both errors ---------
    head("(5) POWER AT THE REGISTERED DECISION VALUES (context for the type-I rate above)")
    for b_plant in (BETA_REQ, TIER2_POSITIVE):
        hit = 0
        for _ in range(400):
            f = fit_beta_int(_synth(rng, n, b_plant, sigma))
            if f["ci95"][0] > 0.0:
                hit += 1
        if verbose:
            print("    planted beta_int = %+.4f  ->  95%% CI excluded 0 in %3d / 400 = %.3f of "
                  "replications at n = %d" % (b_plant, hit, hit / 400.0, n))
        rec["checks"].append({"kind": "power", "planted": b_plant, "trials": 400,
                              "excluded_zero": hit, "rate": hit / 400.0})

    # ---- (6) the two-tier rule cannot be talked into a positive ----------------------------------
    head("(6) THE TWO-TIER RULE (§6.2c) IS TESTED, NOT ASSERTED")
    tier1_ok = True
    probes = [-5.0, F1_THRESHOLD, F1_THRESHOLD + 1e-9, 0.0, BETA_REQ, TIER2_POSITIVE, 5.0, 1e6]
    for b in probes:
        v, _ = decide(1, b, False, 0)
        bad = v in POSITIVE_VERDICTS or v not in TIER1_PERMITTED
        tier1_ok &= not bad
        if verbose:
            print("    Tier 1, beta_hat = %+12.4f -> %-38s %s"
                  % (b, v, "*** POSITIVE AT TIER 1 ***" if bad else "ok (never a positive)"))
    for b in probes:
        v, _ = decide(2, b, False, 0)
        if verbose:
            print("    Tier 2, beta_hat = %+12.4f -> %s" % (b, v))
    if verbose:
        print("    VOID outranks: Tier 1 with F4 firing            -> %s" % decide(1, 5.0, True, 0)[0])
        print("    VOID outranks: Tier 1 with %d indeterminate cells -> %s"
              % (MAX_INDETERMINATE_CELLS + 1,
                 decide(1, 5.0, False, MAX_INDETERMINATE_CELLS + 1)[0]))
        print("    -> Tier 1 emitted only permitted, non-positive verdicts at every probe : %s"
              % ("PASS" if tier1_ok else "*** FAIL ***"))
    ok_all &= tier1_ok
    rec["checks"].append({"kind": "two_tier_rule", "probes": probes, "pass": bool(tier1_ok)})

    # ---- (7) the content-resolution keys are tested on synthetic keys ----------------------------
    head("(7) CONTENT-BASED CELL RESOLUTION (§7.4) IS TESTED ON SYNTHETIC KEYS")
    res_ok = True
    cases = [
        ((0.000, 1759.0), "DR2K000"), ((0.050, 1759.0), "DR2K050"),
        ((0.075, 1759.0), "DR2K075"), ((0.200, 1759.0), "DR2K200"),
        ((0.000, 1407.2), "PAR20"), ((0.000, 1055.4), "PAR40"), ((0.000, 351.8), "CMW80"),
        ((0.050, 1407.2), None),                 # a mixed lesion is not a registered cell
        ((0.100, 1759.0), None),                 # KV 0.100 belongs to the crossed corpus, not here
    ]
    for (kv, ta), want in cases:
        got = condition_from_content(kv, ta)
        good = got == want
        res_ok &= good
        if verbose:
            print("    KV %.3f  tib_ant_l %8.1f N  ->  %-10s (expected %-10s) %s"
                  % (kv, ta, got or "EXCLUDED", want or "EXCLUDED", "ok" if good else "*** FAIL"))
    for gx, want in [(0.0, 0), (0.342247, 2), (0.854706, 5),
                     (-0.854706, None),          # the H0914M_DN5.osim sign -- this is UPHILL
                     (-0.342247, None), (0.5, None)]:
        gy = -math.sqrt(max(G_MAG ** 2 - gx * gx, 0.0))
        got = grade_from_gravity([gx, gy, 0.0])
        good = got == want
        res_ok &= good
        if verbose:
            print("    <gravity> %+.6f %.6f 0  ->  D = %-9s (expected %-9s) %s"
                  % (gx, gy, str(got), str(want), "ok" if good else "*** FAIL"))
    for tier_, role, sd, want in [(1, "PRIMARY_SPASTIC", 101, True), (1, "PRIMARY_SPASTIC", 106, True),
                                  (1, "PRIMARY_SPASTIC", 107, False), (1, "PRIMARY_SPASTIC", 1, False),
                                  (1, "CONTROL", 4, False), (2, "PRIMARY_SPASTIC", 116, True),
                                  (2, "PRIMARY_SPASTIC", 117, False), (2, "CONTROL", 107, False),
                                  (2, "MANIP_CHECK", 105, False)]:
        got = sd in registered_seeds(tier_, role)
        good = got == want
        res_ok &= good
        if verbose:
            print("    Tier %d %-16s random_seed %3d -> admitted = %-5s (expected %-5s) %s"
                  % (tier_, role, sd, got, want, "ok" if good else "*** FAIL"))
    if verbose:
        print("    random_seed 1-4 is the CROSSED corpus. Measured on the live results root while")
        print("    this file was written, `DR2K000_s1..s4` and `HEALTHY_s1..s4 (1)` are")
        print("    content-identical to this study's (DR2K000, D = 0) cell on min_progress,")
        print("    max_generations, terminal generation, min_velocity, init_file, KV, tib_ant_l")
        print("    and <gravity>. Without the seed key they resolve into this study's cell and")
        print("    §7.4's over-population HALT fires forever. §5.3 fixed the range in advance.")
        print("    the -0.854706 row is the gravity vector shipped in the file NAMED")
        print("    `H0914M_DN5.osim`. §7.2 records it as carrying the UPHILL sign. A run built on")
        print("    it must be EXCLUDED, not silently analysed as a downhill cell, and that is what")
        print("    the row above asserts.                                              -> %s"
              % ("PASS" if res_ok else "*** FAIL ***"))
    ok_all &= res_ok
    rec["checks"].append({"kind": "content_resolution", "pass": bool(res_ok)})

    # ---- (8) the falsifiers fire where they are registered to fire -------------------------------
    head("(8) THE FALSIFIERS FIRE WHERE §6.1 REGISTERS THEM TO FIRE")
    f_ok = True
    for b, want in [(-0.5, True), (F1_THRESHOLD, True), (F1_THRESHOLD + 1e-9, False),
                    (0.0, False), (0.70, False)]:
        got = bool(b <= F1_THRESHOLD)
        f_ok &= got == want
        if verbose:
            print("    F1  beta_hat %+8.4f <= %.4f -> fires = %-5s (expected %-5s)  "
                  "95%% upper bound %+.4f vs beta_req %.4f"
                  % (b, F1_THRESHOLD, got, want, b + 1.96 * SE_TIER[1], BETA_REQ))
    for sp, ctl, want in [((0.60, 0.65), 0.60, True), ((0.10, 0.10), 0.60, False),
                          ((0.70, 0.10), 0.60, False)]:
        got = all(s >= ctl for s in sp)
        f_ok &= got == want
        if verbose:
            print("    F2  spastic slopes %s vs control %.2f -> fires = %-5s (expected %-5s)"
                  % (str(sp), ctl, got, want))
    for m0, m5, want in [(1.5752, 1.0, True), (1.5752, 5.0, False)]:
        got = m5 < m0
        f_ok &= got == want
        if verbose:
            print("    F3  margin(D=0) %.4f  margin(D=5) %.4f -> fires = %-5s (expected %-5s)"
                  % (m0, m5, got, want))
    for slopes, want in [((0.05, -0.10, 0.19), True), ((0.05, 0.30, 0.10), False)]:
        got = all(abs(s) < F4_SLOPE_TOL for s in slopes)
        f_ok &= got == want
        if verbose:
            print("    F4  |slopes| %s < %.1f -> VOID = %-5s (expected %-5s)"
                  % (str(slopes), F4_SLOPE_TOL, got, want))
    if verbose:
        print("    -> %s" % ("PASS" if f_ok else "*** FAIL ***"))
    ok_all &= f_ok
    rec["checks"].append({"kind": "falsifiers", "pass": bool(f_ok)})

    # ---- (9) the attrition floor and the completeness gate ---------------------------------------
    head("(9) THE ATTRITION FLOOR (§6.2b) AND THE PARTIAL-CORPUS REFUSAL")
    a_ok = True
    for retained, want in [(6, False), (4, False), (3, True), (0, True)]:
        got = retained < MIN_RETAINED_PER_CELL
        a_ok &= got == want
        if verbose:
            print("    cell retaining %d seeds -> INDETERMINATE-BY-ATTRITION = %-5s (expected %s)"
                  % (retained, got, want))
    for nind, want in [(0, False), (2, False), (3, True)]:
        got = nind > MAX_INDETERMINATE_CELLS
        a_ok &= got == want
        if verbose:
            print("    %d indeterminate cells of 15 -> study VOID = %-5s (expected %s)"
                  % (nind, got, want))
    fake = {(c, D): {"found": N_PER_CELL[1][CONDITIONS[c]["role"]], "required":
                     N_PER_CELL[1][CONDITIONS[c]["role"]]}
            for c in CONDITIONS for D in GRADES}
    if verbose:
        print("    complete corpus (114/114)  -> refuses = %s" % (not corpus_is_complete(fake)))
    a_ok &= corpus_is_complete(fake)
    fake[("PAR40", 5)]["found"] -= 1
    if verbose:
        print("    one cell short (113/114)   -> refuses = %s   <-- THE FAILURE MODE THIS GATE"
              " EXISTS FOR" % (not corpus_is_complete(fake)))
    a_ok &= not corpus_is_complete(fake)
    if verbose:
        print("    -> %s" % ("PASS" if a_ok else "*** FAIL ***"))
    ok_all &= a_ok
    rec["checks"].append({"kind": "attrition_and_completeness", "pass": bool(a_ok)})

    rec["pass"] = bool(ok_all)
    if verbose:
        print("\n" + "=" * 96)
        print("SELF-TEST VERDICT: %s   (%d checks)"
              % ("PASS" if ok_all else "*** FAIL -- THE CORPUS WILL NOT BE OPENED ***",
                 len(rec["checks"])))
        print("=" * 96)
    if not ok_all:
        raise RuntimeError("SELF-TEST FAILED. The estimator did not recover a planted effect, or "
                           "the two-tier rule, the falsifiers, the resolution keys or the "
                           "completeness gate did not behave as registered. Nothing further runs.")
    _SELFTEST_PASSED = True
    return rec


# =================================================================================================
# SECTION 5 -- CONTENT-BASED CELL RESOLUTION (§7.4)
# =================================================================================================
# "Cells are resolved by CONTENT. Never by directory name. Never by mtime."
#
# SCONE appends " (1)" to a colliding directory name rather than overwriting, and tag collisions
# have TWICE silently mixed corpora here (crossed_endpoint.py lines 32-37; COUNCIL_round10.md
# defect #23). The critical point for THIS study, which §7.4 registers because it is easy to get
# wrong: the usual content key -- min_progress == 0 AND max_generations == 90 AND terminal
# generation 89 -- is IDENTICAL ACROSS ALL 21 CELLS BY DESIGN, so it cannot discriminate a slope
# tier from a level tier. The `<gravity>` vector inside the model file the run's OWN archived
# config.scone names is the discriminator, and it is read from the copy of that model archived in
# the run directory itself, never from `scone/opt_slope_r60/`, which could have been regenerated
# after the run started.

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_gravity(path):
    """The single `<gravity>` element of an .osim. More than one -> the file is not resolvable."""
    txt = open(path, encoding="utf-8", errors="ignore").read()
    got = re.findall(r"<gravity>([^<]*)</gravity>", txt)
    if len(got) != 1:
        raise ValueError("%s declares <gravity> %d times" % (path, len(got)))
    v = [float(x) for x in got[0].split()]
    if len(v) != 3:
        raise ValueError("%s: <gravity>%s</gravity> is not a 3-vector" % (path, got[0]))
    return v, got[0]


def read_ta_force(path):
    """`max_isometric_force` of tib_ant_l, read from the model file itself (§5.2, §7.4)."""
    s = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r'name="%s"' % DORSIFLEXOR, s)
    if not m:
        raise ValueError("%s: no %s" % (path, DORSIFLEXOR))
    seg = s[m.end():m.end() + 3000]
    f = re.search(r"<max_isometric_force>\s*([\d.eE+-]+)", seg)
    if not f:
        raise ValueError("%s: no max_isometric_force for %s" % (path, DORSIFLEXOR))
    return float(f.group(1))


def grade_from_gravity(v, tol=1e-4):
    """<gravity> -> the decline magnitude D, or None if it is not a registered downhill vector.

    §5.2 registers gx = +|g| sin(D), gy = -|g| cos(D), |g| = 9.80665 preserved. The x-sign is
    LOAD-BEARING: §7.2 records that the file shipped as `H0914M_DN5.osim` carries gx = -0.854706,
    which is the UPHILL sign, and that a mislabelled sign would run the entire study uphill at
    1.0 m/s "and every number would look normal". A negative gx therefore resolves to nothing and
    the run is excluded, never guessed into a cell.
    """
    gx, gy, gz = float(v[0]), float(v[1]), float(v[2])
    if abs(gz) > 1e-9 or gy >= 0.0:
        return None
    if abs(math.hypot(gx, gy) - G_MAG) > 1e-3:
        return None
    if gx < -tol:
        return None                          # uphill: excluded outright (§5.1, §7.2)
    for D in GRADES:
        if (abs(gx - G_MAG * math.sin(math.radians(D))) <= tol
                and abs(gy + G_MAG * math.cos(math.radians(D))) <= tol):
            return D
    return None


def condition_from_content(kv, ta, kv_tol=1e-6, ta_tol=1e-3):
    """(injected KV, tib_ant_l max_isometric_force) -> condition, or None.

    §5.2: "No run enters an arm by tag." A pair that matches no registered cell returns None and
    the directory is EXCLUDED, not guessed (§7.4: "A directory that does not resolve to exactly
    one cell on the full key is excluded, not guessed").
    """
    hits = [c for c, spec in CONDITIONS.items()
            if abs(kv - spec["kv"]) <= kv_tol and abs(ta - spec["ta"]) <= ta_tol]
    return hits[0] if len(hits) == 1 else None


def parse_config(path):
    """Read the registered budget keys and the injected KV from a run's OWN archived config.scone.

    Comments are stripped with `delivered_gain.strip_comments`, the parser this project already
    trusts for SCONE scenario text (it will not cut inside a double-quoted value such as
    "*_tx*;*_ty*;*_u;*/speed").
    """
    raw = open(path, encoding="utf-8", errors="ignore").read()
    s = DG.strip_comments(raw)

    def one(key):
        m = re.findall(r"^[ \t]*%s[ \t]*=[ \t]*(\S+)[ \t]*$" % key, s, re.M)
        return m[0] if len(m) == 1 else None

    out = {"min_progress": one("min_progress"), "max_generations": one("max_generations"),
           "min_velocity": one("min_velocity"), "init_file": one("init_file"),
           "random_seed": one("random_seed"), "model_file": one("model_file"),
           "signature_prefix": one("signature_prefix"),
           "mentions_resume_par": ("_resume.par" in s)}

    # The injected KV lives in the `ReflexController { name = SpasticL ... }` block, as a LITERAL
    # (free parameters are written `KV = "~0.4<-10,10>"` and cannot match the pattern below).
    # §7.4 names "injected KV value (scenario lines 164/170)" as the spastic-rung discriminator.
    i = s.find("name = SpasticL")
    if i < 0:
        i = s.find("name=SpasticL")
    if i < 0:
        out["kv"] = None
        return out
    depth, j = 1, i
    while j < len(s) and depth > 0:
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
        j += 1
    seg = s[i:j]
    kvs = [float(m.group(1)) for m in re.finditer(r"KV[ \t]*=[ \t]*([-+0-9.eE]+)[ \t\r\n]", seg)]
    out["kv_values"] = kvs
    out["kv"] = kvs[0] if (len(kvs) == 2 and kvs[0] == kvs[1]) else None
    return out


def read_history(path):
    """Terminal generation and the FITNESS COLUMNS, from the run's own `history.txt`.

    Round-62 addition, §4.4 implemented plus the gen-0 column: terminal `best_fitness`, the
    generation at which the minimum `best_fitness` occurs, terminal `median_fitness`, and the
    GENERATION-0 `best_fitness` (the cold-start cost under that gravity). Read HERE and never from
    `.par` filenames, which are pruned on improvement only and therefore cannot report either the
    cold-start cost or a terminal value that did not improve.
    """
    lines = [l for l in open(path, encoding="utf-8", errors="ignore").read().splitlines()
             if l.strip()]
    if len(lines) < 2:
        raise ValueError("%s has %d non-empty lines" % (path, len(lines)))
    hdr = [c.strip() for c in lines[0].split("\t")]
    rows = []
    for l in lines[1:]:
        parts = l.split("\t")
        if len(parts) < 2:
            continue
        try:
            rows.append([float(x) for x in parts])
        except ValueError:
            continue
    if not rows:
        raise ValueError("%s has no parseable data rows" % path)
    A = np.array([r[:len(hdr)] for r in rows if len(r) >= len(hdr)], float)
    ig = hdr.index("generation") if "generation" in hdr else 0
    ib = hdr.index("best_fitness") if "best_fitness" in hdr else 1
    im = hdr.index("median_fitness") if "median_fitness" in hdr else 2
    gen = A[:, ig]
    best = A[:, ib]
    k = int(np.argmin(best))
    g0 = np.where(gen == 0)[0]
    return {"terminal_gen": int(gen[-1]), "n_generations": int(A.shape[0]),
            "terminal_best_fitness": float(best[-1]),
            "terminal_median_fitness": float(A[-1, im]),
            "min_best_fitness": float(best[k]), "best_gen": int(gen[k]),
            "gen0_best_fitness": float(best[g0[0]]) if len(g0) else float(best[0]),
            "columns": hdr}


def registered_seeds(tier, role):
    """§5.3: `random_seed = 101 .. 116  (crossed with cell; never aliased with slope)`, and
    §6.2(c): Tier 2 escalates the 12 primary cells "using random_seed 107-116" while the control
    and manipulation-check cells "stay as they are".

    WHY THIS IS A RESOLUTION KEY AND NOT A CONVENIENCE FILTER, recorded because it is the one
    place a reader will suspect a name-based shortcut has crept in:

    Measured against the live results root while this file was being written, the CROSSED corpus's
    level runs are CONTENT-IDENTICAL to this study's D = 0 cells on every other key in §7.4's
    table -- `min_progress = 0`, `max_generations = 90`, terminal generation 89,
    `min_velocity = 1.0`, `init_file = ResultH0914Gait10.par`, KV = 0.000, tib_ant_l = 1759 N, and
    a level `<gravity>`. `DR2K000_s1..s4` and `HEALTHY_s1..s4 (1)` therefore resolve to cell
    (DR2K000, D = 0) exactly as `SG0_DR2K000_s101..s106` do, and §7.4's "a cell that resolves to
    more directories than it has registered seeds HALTS the analysis" fires permanently. That is
    the correct behaviour of the halt and the wrong behaviour of the key: those directories are on
    disk for good and the analysis could never run.

    `random_seed` is READ FROM THE RUN'S OWN ARCHIVED config.scone and is fixed by §5.3 in advance
    of the corpus. The crossed corpus used seeds 1-4; this study uses 101 upward. Resolving on it
    is reading a registered budget constant out of the run's own artifact -- the same class of key
    as `min_progress` -- and is not resolution by directory name or by mtime, both of which remain
    forbidden. §7.4's own table already lists `random_seed | run's own config.scone | seed identity
    within a cell` as a resolution key; this uses it for exactly that.
    """
    return set(range(FIRST_SEED, FIRST_SEED + N_PER_CELL[tier][role]))


def resolve_directory(d, tier):
    """Resolve ONE result directory to a cell on the full §7.4 key, or return why it is excluded.

    Returns a dict with `resolved` True/False. Every key is read from the run's OWN artifacts.
    """
    rec = {"dir": d, "name": os.path.basename(os.path.normpath(d)), "resolved": False,
           "reasons": []}
    cfg = os.path.join(d, "config.scone")
    if not os.path.isfile(cfg):
        rec["reasons"].append("no config.scone -- provenance cannot be established")
        return rec
    try:
        c = parse_config(cfg)
    except Exception as e:                                       # noqa: BLE001
        rec["reasons"].append("config.scone unparseable: %r" % (e,))
        return rec
    rec["config_sha256"] = sha256_of(cfg)
    rec.update({k: c.get(k) for k in ("min_progress", "max_generations", "min_velocity",
                                      "init_file", "random_seed", "model_file",
                                      "signature_prefix", "kv", "kv_values",
                                      "mentions_resume_par")})

    if c["min_progress"] != REG_MIN_PROGRESS:
        rec["reasons"].append("min_progress = %r, registration requires %r (§5.3)"
                              % (c["min_progress"], REG_MIN_PROGRESS))
    if c["max_generations"] != str(REG_MAX_GENERATIONS):
        rec["reasons"].append("max_generations = %r, registration requires %d (§5.3)"
                              % (c["max_generations"], REG_MAX_GENERATIONS))
    if c["min_velocity"] != REG_MIN_VELOCITY:
        rec["reasons"].append("min_velocity = %r, registration requires %r (S10W, §5.1)"
                              % (c["min_velocity"], REG_MIN_VELOCITY))
    if c["init_file"] != REG_INIT_FILE:
        rec["reasons"].append("init_file = %r, registration requires the cold start %r (§5.3)"
                              % (c["init_file"], REG_INIT_FILE))
    if c["mentions_resume_par"]:
        rec["reasons"].append("config names a *_resume.par -- warm start, defect A7 (§5.3)")
    if c["kv"] is None:
        rec["reasons"].append("no single literal KV pair in the `SpasticL` block (found %r)"
                              % (c.get("kv_values"),))

    hist = os.path.join(d, "history.txt")
    if not os.path.isfile(hist):
        rec["reasons"].append("no history.txt -- the stopping rule cannot be read back (§7.3.5)")
    else:
        try:
            h = read_history(hist)
            rec["history"] = h
            if h["terminal_gen"] != REG_TERMINAL_GEN:
                rec["reasons"].append(
                    "terminal generation index %d, registration requires %d -- a run whose "
                    "terminal generation is not %d is not a retained seed (§6.2a)"
                    % (h["terminal_gen"], REG_TERMINAL_GEN, REG_TERMINAL_GEN))
        except Exception as e:                                   # noqa: BLE001
            rec["reasons"].append("history.txt unparseable: %r" % (e,))

    mf = c["model_file"]
    if not mf:
        rec["reasons"].append("config.scone names no single model_file")
    else:
        mp = os.path.join(d, mf)
        if not os.path.isfile(mp):
            rec["reasons"].append("the model file %r the run's own config names is not archived "
                                  "in the run directory; a copy from elsewhere is not this run's "
                                  "plant and will not be substituted" % mf)
        else:
            try:
                v, raw = read_gravity(mp)
                ta = read_ta_force(mp)
                rec["gravity"] = v
                rec["gravity_raw"] = raw
                rec["ta_force"] = ta
                rec["model_sha256"] = sha256_of(mp)
                D = grade_from_gravity(v)
                if D is None:
                    rec["reasons"].append(
                        "<gravity>%s</gravity> is not a registered DOWNHILL vector for D in "
                        "{0, 2, 5} at |g| = %.5f. A negative gx is the UPHILL sign (§7.2) and "
                        "uphill is dropped entirely (§5.1)." % (raw, G_MAG))
                else:
                    rec["D"] = D
                if c["kv"] is not None:
                    cond = condition_from_content(c["kv"], ta)
                    if cond is None:
                        rec["reasons"].append(
                            "KV = %.6g with tib_ant_l max_isometric_force = %.4f N matches no "
                            "registered cell (§5.2); excluded, not guessed (§7.4)"
                            % (c["kv"], ta))
                    else:
                        rec["cond"] = cond
                        rec["role"] = CONDITIONS[cond]["role"]
                        rec["arm"] = CONDITIONS[cond]["arm"]
            except Exception as e:                               # noqa: BLE001
                rec["reasons"].append("model file unreadable: %r" % (e,))

    try:
        rec["seed"] = int(c["random_seed"]) if c["random_seed"] is not None else None
    except ValueError:
        rec["seed"] = None
    if rec.get("seed") is None:
        rec["reasons"].append("no single integer random_seed (§7.4 seed identity)")
    elif "cond" in rec:
        allowed = registered_seeds(tier, CONDITIONS[rec["cond"]]["role"])
        if rec["seed"] not in allowed:
            rec["reasons"].append(
                "random_seed = %d is outside this study's registered range for a %s cell at "
                "Tier %d (§5.3 registers 101..116; §6.2(c) gives the 12 primary cells 101-%d at "
                "this tier and leaves control and manipulation-check cells at 101-%d). The "
                "crossed corpus's level runs used seeds 1-4 and are content-identical to this "
                "study's D = 0 cells on every other key, so this is the key that separates them."
                % (rec["seed"], CONDITIONS[rec["cond"]]["role"], tier,
                   FIRST_SEED + N_PER_CELL[tier]["PRIMARY_SPASTIC"] - 1,
                   FIRST_SEED + N_PER_CELL[tier]["CONTROL"] - 1))

    rec["resolved"] = (not rec["reasons"]) and ("cond" in rec) and ("D" in rec)
    return rec


class CorpusHalt(RuntimeError):
    """§7.4: a cell resolving to more directories than it has registered seeds HALTS the analysis."""


def resolve_corpus(tier, results_root=RESULTS_ROOT, verbose=True):
    """Scan the results root and resolve every directory by content. Read-only throughout."""
    _require_selftest()
    all_dirs = sorted(d for d in glob.glob(os.path.join(results_root, "*")) if os.path.isdir(d))
    protected = [d for d in all_dirs if PROTECTED_RE.match(os.path.basename(d))]
    paren = [d for d in all_dirs if " (1)" in os.path.basename(d)]
    candidates = [d for d in all_dirs if d not in set(protected)]

    if verbose:
        print("=" * 96)
        print("CONTENT-BASED CELL RESOLUTION (§7.4) -- never by name, never by mtime")
        print("=" * 96)
        print("  results root                          : %s" % results_root)
        print("  directories present                   : %d" % len(all_dirs))
        print("  matching the protected pattern        : %d  (skipped before anything is opened)"
              % len(protected))
        print("  carrying ' (1)' in the name           : %d  (SCONE's collision suffix; the name "
              "is not consulted either way)" % len(paren))
        print("  directories offered to the resolver   : %d" % len(candidates))
        print("\n  The usual key -- min_progress = %s AND max_generations = %d AND terminal "
              "generation %d --" % (REG_MIN_PROGRESS, REG_MAX_GENERATIONS, REG_TERMINAL_GEN))
        print("  is IDENTICAL across all 21 cells by design (§7.4), so it cannot tell a slope "
              "tier from a")
        print("  level tier. The discriminator is the <gravity> vector inside the model file each "
              "run's OWN")
        print("  archived config.scone names, read from the copy archived in that run directory.")
        print("\n  And gravity is not sufficient at D = 0: the CROSSED corpus's level runs are")
        print("  content-identical to this study's D = 0 cells on every other key. The key that")
        print("  separates them is `random_seed`, fixed by §5.3 at 101..116 in advance of the")
        print("  corpus and read from each run's own config.scone -- Tier %d admits %s for the"
              % (tier, sorted(registered_seeds(tier, "PRIMARY_SPASTIC"))))
        print("  primary cells and %s for control / manipulation-check cells."
              % sorted(registered_seeds(tier, "CONTROL")))

    recs = [resolve_directory(d, tier) for d in candidates]
    resolved = [r for r in recs if r["resolved"]]
    rejected = [r for r in recs if not r["resolved"]]

    cells = {}
    for r in resolved:
        cells.setdefault((r["cond"], r["D"]), []).append(r)

    # §7.4: duplicate seed identity within a cell, or more directories than registered seeds,
    # HALTS. It does not pick one.
    halts = []
    for (cond, D), rs in sorted(cells.items()):
        need = N_PER_CELL[tier][CONDITIONS[cond]["role"]]
        if len(rs) > need:
            halts.append("cell %s D=%d resolved to %d directories but registers %d seeds: %s"
                         % (cond, D, len(rs), need,
                            ", ".join(x["name"] for x in rs)))
        seen = {}
        for x in rs:
            seen.setdefault(x["seed"], []).append(x["name"])
        for sd, names in sorted(seen.items()):
            if len(names) > 1:
                halts.append("cell %s D=%d has %d directories claiming random_seed %s: %s"
                             % (cond, D, len(names), sd, ", ".join(names)))

    counts = {}
    for cond in CONDITIONS:
        for D in GRADES:
            need = N_PER_CELL[tier][CONDITIONS[cond]["role"]]
            counts[(cond, D)] = {"found": len(cells.get((cond, D), [])), "required": need}

    if verbose:
        print("\n  resolved to a registered cell         : %d" % len(resolved))
        print("  rejected (excluded, never guessed)    : %d" % len(rejected))
        if rejected:
            print("\n  %-56s %s" % ("directory", "first reason for exclusion"))
            print("  " + "-" * 92)
            for r in rejected[:200]:
                print("  %-56s %s" % (r["name"][:56], r["reasons"][0][:100] if r["reasons"]
                                      else "did not resolve to exactly one cell"))
            if len(rejected) > 200:
                print("  ... and %d more" % (len(rejected) - 200))
    if halts:
        for h in halts:
            print("\n  *** HALT: %s" % h)
        raise CorpusHalt("§7.4 halts the analysis: %d cell(s) resolve ambiguously. Resolve the "
                         "collision before any feature is extracted; do not pick one."
                         % len(halts))
    return {"cells": cells, "counts": counts, "resolved": resolved, "rejected": rejected,
            "n_protected": len(protected), "n_paren": len(paren), "tier": tier}


def corpus_is_complete(counts):
    """True only if EVERY cell has found == required. Never 'most cells are there'."""
    return all(v["found"] == v["required"] for v in counts.values())


def print_completeness(counts, tier):
    """Print found vs required PER CELL, and total. This table is printed whether it passes or
    fails -- the count is the evidence, not the verdict word."""
    print("\n" + "=" * 96)
    print("CORPUS COMPLETENESS GATE (Tier %d) -- FAIL CLOSED" % tier)
    print("=" * 96)
    print("  A partially populated cell silently becomes n < %d while the report still says n = %d."
          % (N_PER_CELL[tier]["PRIMARY_SPASTIC"], N_PER_CELL[tier]["PRIMARY_SPASTIC"]))
    print("  That mechanism produced a 39/40 threshold and seven mutually inconsistent values of")
    print("  one quantity in this project's history. This analysis therefore does NOT analyse")
    print("  whichever cells happen to have finished.\n")
    print("  %-10s %-18s %6s %6s %8s %s" % ("cond", "role", "D", "found", "required", "status"))
    print("  " + "-" * 76)
    tot_f = tot_r = 0
    short = []
    for cond in CONDITIONS:
        for D in GRADES:
            v = counts[(cond, D)]
            tot_f += v["found"]
            tot_r += v["required"]
            ok = v["found"] == v["required"]
            if not ok:
                short.append((cond, D, v["found"], v["required"]))
            print("  %-10s %-18s %6d %6d %8d %s"
                  % (cond, CONDITIONS[cond]["role"], D, v["found"], v["required"],
                     "complete" if ok else ("*** SHORT BY %d ***" % (v["required"] - v["found"])
                                            if v["found"] < v["required"]
                                            else "*** OVER BY %d ***"
                                                 % (v["found"] - v["required"]))))
    print("  " + "-" * 76)
    print("  %-10s %-18s %6s %6d %8d  (§5.4 registers %d runs at Tier %d)"
          % ("TOTAL", "", "", tot_f, tot_r, TOTAL_RUNS[tier], tier))
    if short:
        print("\n  %d cell(s) incomplete. THE ANALYSIS WILL NOT RUN." % len(short))
    return not short


# =================================================================================================
# SECTION 6 -- THE PRIMARY, EXTRACTED PER SEED (§1.1, §1.2)
# =================================================================================================
def extract_seed(rec, do_replay=True, verbose=True):
    """One seed: registered .par selection -> registered replay -> the registered feature.

    §1.2 forbids reading whatever `.sto` happens to sit in a run directory: `sto_utils.py` lines
    17-43 record that not one of four audited anchor directories contained a `.sto` belonging to
    its own best controller, and that 148 of 316 archived directories contain no `.sto` at all.
    The `.sto` must be PRODUCED, by `replay_all.replay_registered`, which copies the run's OWN
    archived config.scone into an empty isolated directory under `scone/replay_registered/` and
    asserts exactly one `.sto` results. NOTHING under the results root is written or moved.

    THE FEATURE IS `sto_utils.cycle_features(sto, side="l", settle=1.0)["ank_rom"]`, RAW AND
    UNFILTERED, and the GRF window is whatever THAT FUNCTION computes (sto_utils.py lines 202-308:
    grf_norm_y at 0.05 BW or grf_y at 20.0 N; upward crossings that stay loaded >= 0.15 s; events
    within 0.3 s merged; strikes at t >= 1.0 s only; >= 3 strikes; consecutive pairs with the last
    dropped; >= 2 surviving cycles or None). It is NOT reimplemented here, and §1.1 forbids mixing
    it with the filtered §4.2 variant inside one table.
    """
    out = dict(rec)
    out["excluded"] = None
    try:
        sel = S.select_registered_par(rec["dir"])
    except S.RegisteredSelectionError as e:
        out["excluded"] = "E5_SELECTION"
        out["exclusion_detail"] = str(e)
        return out
    out.update({"par": os.path.basename(sel["par"]), "par_gen": sel["gen"],
                "par_fitness": sel["fitness"], "par_median": sel["median"],
                "par_max_gen": sel["max_gen"], "n_par": sel["n_par"]})
    if sel["gen"] != sel["max_gen"]:                       # select_registered_par already raises;
        out["excluded"] = "E5_SELECTION"                   # asserted again because §7.3.7 asks for
        return out                                         # the assertion to be RECORDED

    if not do_replay:
        out["excluded"] = "NOT_REPLAYED"
        return out

    rep = R.replay_registered(rec["dir"])
    out["replay_status"] = rep["status"]
    out["config_sha256_replayed"] = rep.get("config_sha256")
    if rep["status"] != "ok":
        out["excluded"] = "E5_REPLAY_%s" % rep["status"]
        out["exclusion_detail"] = rep.get("error", "")
        return out
    sto = rep["sto"]
    out["sto"] = sto
    out["sto_sha256"] = rep.get("sto_sha256")

    feats = S.cycle_features(sto, side=SIDE, settle=SETTLE)
    if feats is None:
        out["excluded"] = "NO_CYCLES"
        out["exclusion_detail"] = ("cycle_features returned None: fewer than 2 complete cycles "
                                   "after settle = %.1f s, i.e. not steady gait (§6.2b)" % SETTLE)
        return out
    out["features"] = {k: (float(v) if isinstance(v, (int, float)) else v)
                       for k, v in feats.items()}
    out["ank_rom"] = float(feats["ank_rom"])

    # G6 (§5.2, §7.3.4): arm membership for the spastic arm is by MEASURED delivered gain, not by
    # tag. delivered_gain.py is this project's only trusted delivery instrument and 30 of 30
    # historical spastic runs failed it at rho ~ 2.0. It reads the config and the .sto; it runs no
    # simulation. The replayed .sto is passed explicitly with allow_external_sto=True because it
    # lives in the isolated replay directory, not beside the config.
    if CONDITIONS[rec["cond"]]["kv"] > 0.0:
        try:
            g = DG.verify(rec["dir"], sto_path=sto, allow_external_sto=True)
            rhos = {}
            for e in g.get("gains", []):
                for term, rho in e.get("rho", {}).items():
                    rhos["%s.%s" % (e["target"], term)] = float(rho)
            out["delivered_gain"] = {"verdict": g["verdict"], "rho": rhos,
                                     "reasons": g.get("reasons", [])}
            bad = [k for k, r in rhos.items() if not np.isfinite(r) or abs(r - 1.0) > TOL_RHO]
            if g["verdict"] != "PASS" or bad or not rhos:
                out["excluded"] = "G6_DELIVERY"
                out["exclusion_detail"] = (
                    "delivered_gain verdict %s; rho %s. §5.2: no run enters the spastic arm by "
                    "tag -- membership is certified delivery, rho within %.2f of 1.0."
                    % (g["verdict"], rhos or "none computable", TOL_RHO))
        except Exception as e:                             # noqa: BLE001
            out["excluded"] = "G6_DELIVERY"
            out["exclusion_detail"] = "delivered_gain raised %r" % (e,)
    if verbose:
        print("    %-46s %-14s rom=%s"
              % (rec["name"][:46], out["excluded"] or "retained",
                 "%8.4f" % out["ank_rom"] if out.get("ank_rom") is not None else "     n/a"))
    return out


# ---- §4.2, the clinically observable margin --------------------------------------------------
def video_rom(sto):
    """§4.2: the SAME feature through the registered video-degradation pipeline at the BASELINE
    cell -- 30 Hz resample, 4th-order zero-phase 6 Hz Butterworth, sagittal projection at yaw 0,
    noise 0.

    Every constant and every transform is TAKEN FROM `video_degradation.py` (V.FS_LIST[0], V.FC,
    V.BUTTER_ORDER, V.SETTLE, V.prepare, V.project, V.rom_matrix), not re-derived here, so this
    cannot drift from the registered pipeline.

    SCOPE, STATED RATHER THAN IMPLIED: §4.2 also asks for the same yaw/noise grid used in
    RESULTS_discrimination.md §7. That grid is produced by RE-RUNNING `video_degradation.py`
    against this corpus, which is the registered instrument for it; this function reproduces only
    the yaw-0, noise-0 baseline cell, which is the one the primary is compared against. The grid
    is a required secondary and its absence from a Results section is a protocol violation (§4);
    it is not reimplemented here because a second implementation of a registered pipeline is how
    two variants of one quantity get reported as one.
    """
    cols, data = S.load_sto(sto)
    t = np.asarray(data[:, 0], float)
    pel = S.col(cols, data, "pelvis_tilt")
    hip = S.col(cols, data, "hip_flexion_l")
    kne = S.col(cols, data, "knee_angle_l")
    ank = S.col(cols, data, "ankle_angle_l")
    if any(x is None for x in (pel, hip, kne, ank)):
        return None
    q_shank = np.asarray(pel, float) + np.asarray(hip, float) + np.asarray(kne, float)   # A1
    q_foot = q_shank + np.asarray(ank, float)                                            # A1
    grf, thr = S.grf_vertical(cols, data, SIDE)
    if grf is None:
        return None
    hs = [i for i in S.heel_strikes(t, grf, thresh=thr) if t[i] >= V.SETTLE]
    cyc = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]                           # A5
    if len(cyc) < 2:
        return None
    run = {"t": t, "q_shank": q_shank, "q_foot": q_foot,
           "cyc_t": [(float(t[a]), float(t[b])) for a, b in cyc]}
    fs = V.FS_LIST[0]
    grid, qs, qf, wins = V.prepare(run, fs)
    if len(wins) < 2:
        return None
    b, a = signal.butter(V.BUTTER_ORDER, V.FC / (fs / 2.0), btype="low")
    ang = V.project(qs, qf, 1.0)[None, :]        # yaw 0 -> cos(theta) = 1
    return float(V.rom_matrix(ang, wins, b, a)[0])


# =================================================================================================
# SECTION 7 -- THE ANALYSIS
# =================================================================================================
def analyse(tier=1, do_replay=True, results_root=RESULTS_ROOT):
    _require_selftest()
    t_start = time.time()
    out = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tier": tier,
           "registration": {"path": REG_PATH, "sha256": REG_SHA256, "bytes": REG_BYTES},
           "script_sha256": sha256_of(os.path.abspath(__file__))}

    res = resolve_corpus(tier, results_root=results_root)
    complete = print_completeness(res["counts"], tier)
    out["counts"] = {"%s_D%d" % k: v for k, v in res["counts"].items()}
    if not complete:
        out["verdict"] = "REFUSED_PARTIAL_CORPUS"
        json.dump(out, open(OUT_JSON, "w"), indent=1)
        raise SystemExit(
            "\nREFUSING TO ANALYSE A PARTIAL CORPUS. The counts above are found-vs-required per "
            "cell.\nAnalysing whichever cells happen to have finished is how a cell silently "
            "becomes n < %d\nwhile the report still says n = %d. Re-run when every cell is "
            "complete.\n" % (N_PER_CELL[tier]["PRIMARY_SPASTIC"],
                             N_PER_CELL[tier]["PRIMARY_SPASTIC"]))

    # ---- per-seed extraction ---------------------------------------------------------------
    print("\n" + "=" * 96)
    print("PER-SEED EXTRACTION -- registered .par selection (§1.2) -> registered replay -> "
          "cycle_features")
    print("=" * 96)
    seeds = []
    for (cond, D) in sorted(res["cells"]):
        print("  cell %s  D = %d" % (cond, D))
        for r in sorted(res["cells"][(cond, D)], key=lambda x: (x["seed"], x["name"])):
            seeds.append(extract_seed(r, do_replay=do_replay))
    out["n_seeds_examined"] = len(seeds)

    retained = [s for s in seeds if s["excluded"] is None]
    excluded = [s for s in seeds if s["excluded"] is not None]

    # ---- the attrition floor (§6.2b) -------------------------------------------------------
    print("\n" + "=" * 96)
    print("PER-CELL ATTRITION FLOOR (§6.2b) -- exclusions are COUNTED, never silently dropped")
    print("=" * 96)
    print("  A seed is excluded if select_registered_par raises E5, if cycle_features returns None")
    print("  (fewer than 2 complete cycles), or -- for the spastic arm -- if G6 cannot certify")
    print("  delivery within %.2f of 1.0 (§5.2). A cell retaining fewer than %d seeds is reported"
          % (TOL_RHO, MIN_RETAINED_PER_CELL))
    print("  INDETERMINATE-BY-ATTRITION and contributes nothing. If more than %d of the 15"
          % MAX_INDETERMINATE_CELLS)
    print("  primary + control cells are indeterminate, the study is VOID, not null.\n")
    print("  %-10s %3s %8s %9s %9s %s" % ("cond", "D", "launched", "retained", "excluded",
                                          "status / reasons"))
    print("  " + "-" * 90)
    cell_rows, indeterminate = {}, []
    for cond in CONDITIONS:
        for D in GRADES:
            rs = [s for s in retained if s["cond"] == cond and s["D"] == D]
            ex = [s for s in excluded if s["cond"] == cond and s["D"] == D]
            cell_rows[(cond, D)] = rs
            ind = len(rs) < MIN_RETAINED_PER_CELL
            if ind and CONDITIONS[cond]["role"] != "MANIP_CHECK":
                indeterminate.append((cond, D))
            why = ", ".join(sorted(set(s["excluded"] for s in ex))) if ex else ""
            print("  %-10s %3d %8d %9d %9d %s"
                  % (cond, D, res["counts"][(cond, D)]["found"], len(rs), len(ex),
                     ("*** INDETERMINATE-BY-ATTRITION *** " if ind else "") + why))
    n_ind = len(indeterminate)
    print("\n  INDETERMINATE-BY-ATTRITION cells among the 15 primary + control : %d (limit %d)"
          % (n_ind, MAX_INDETERMINATE_CELLS))
    out["indeterminate_cells"] = ["%s_D%d" % k for k in indeterminate]
    out["n_excluded"] = len(excluded)
    out["exclusions"] = [{"name": s["name"], "cond": s.get("cond"), "D": s.get("D"),
                          "seed": s.get("seed"), "reason": s["excluded"],
                          "detail": s.get("exclusion_detail", "")} for s in excluded]

    # ---- the convergence covariate (round-62 addition; §4.4 implemented, plus gen 0) ---------
    print("\n" + "=" * 96)
    print("CONVERGENCE READBACK -- terminal fitness as a FIRST-CLASS COLUMN (round-62 addition)")
    print("=" * 96)
    print("  Read from each run's OWN history.txt, never from .par filenames (pruned on")
    print("  improvement only). §5.3 registered in advance that the -5 degree tier may fail to")
    print("  converge from cold; G4's criterion is >= 2 complete cycles, which a barely-viable")
    print("  gait can satisfy while its ROM is inflated by non-convergence rather than by slope.")
    print("  That is defect A7 arriving through the gate written to keep it out. It is reported")
    print("  as a covariate and a flag. IT NEVER REWEIGHTS, DROPS OR EXCLUDES A SEED: exclusion")
    print("  is governed solely by the registered attrition floor above.\n")
    print("  %-10s %3s %5s %14s %14s %14s %10s"
          % ("cond", "D", "n", "gen0 best", "terminal best", "min best", "best_gen"))
    print("  " + "-" * 80)
    for s in retained:
        h = s.get("history") or {}
        s["gen0_best_fitness"] = h.get("gen0_best_fitness", float("nan"))
        s["terminal_best_fitness"] = h.get("terminal_best_fitness", float("nan"))
        s["terminal_median_fitness"] = h.get("terminal_median_fitness", float("nan"))
        s["min_best_fitness"] = h.get("min_best_fitness", float("nan"))
        s["best_gen"] = h.get("best_gen", -1)
    fitness_table = {}
    for cond in CONDITIONS:
        for D in GRADES:
            rs = cell_rows[(cond, D)]
            if not rs:
                continue
            g0 = np.array([r["gen0_best_fitness"] for r in rs], float)
            tb = np.array([r["terminal_best_fitness"] for r in rs], float)
            mb = np.array([r["min_best_fitness"] for r in rs], float)
            fitness_table[(cond, D)] = {"n": len(rs), "gen0_mean": float(np.mean(g0)),
                                        "terminal_mean": float(np.mean(tb)),
                                        "terminal_sd": float(np.std(tb, ddof=1)) if len(tb) > 1
                                        else float("nan"),
                                        "terminal_min": float(np.min(tb)),
                                        "terminal_max": float(np.max(tb))}
            print("  %-10s %3d %5d %14.4f %14.4f %14.4f %10.1f"
                  % (cond, D, len(rs), float(np.mean(g0)), float(np.mean(tb)), float(np.mean(mb)),
                     float(np.mean([r["best_gen"] for r in rs]))))
    print("\n  per (D, arm) mean terminal best_fitness, and the order-of-magnitude flag:")
    print("  %-4s %-10s %5s %14s %14s %14s %14s"
          % ("D", "arm", "n", "mean", "sd", "min", "max"))
    print("  " + "-" * 80)
    arm_fit = {}
    for D in GRADES:
        for armname, conds in (("spastic", SPASTIC_ARM), ("weak", WEAK_ARM),
                               ("control", (CONTROL_COND,)), ("manip", MANIP_CONDS)):
            vals = [r["terminal_best_fitness"] for r in retained
                    if r["D"] == D and r["cond"] in conds]
            if not vals:
                continue
            v = np.array(vals, float)
            arm_fit[(D, armname)] = float(np.mean(v))
            print("  %-4d %-10s %5d %14.4f %14.4f %14.4f %14.4f"
                  % (D, armname, len(v), float(np.mean(v)),
                     float(np.std(v, ddof=1)) if len(v) > 1 else float("nan"),
                     float(np.min(v)), float(np.max(v))))
    flags = []
    for D in GRADES:
        a, b = arm_fit.get((D, "spastic")), arm_fit.get((D, "weak"))
        if a and b and max(a, b) / max(min(a, b), 1e-12) > 10.0:
            flags.append("D = %d: the two arms' mean terminal fitness differ by %.1fx "
                         "(spastic %.4f vs weak %.4f)" % (D, max(a, b) / min(a, b), a, b))
    for armname in ("spastic", "weak", "control"):
        vals = [(D, arm_fit[(D, armname)]) for D in GRADES if (D, armname) in arm_fit]
        if len(vals) > 1:
            lo, hi = min(v for _, v in vals), max(v for _, v in vals)
            if hi / max(lo, 1e-12) > 10.0:
                flags.append("%s arm: mean terminal fitness varies %.1fx across grades (%s)"
                             % (armname, hi / lo, ", ".join("D=%d:%.4f" % kv for kv in vals)))
    if flags:
        print("\n  *** CONVERGENCE FLAG -- ORDER-OF-MAGNITUDE DIFFERENCE ***")
        for f in flags:
            print("      %s" % f)
        print("      A systematic between-arm or between-grade convergence difference of this size")
        print("      is a candidate confound on the interaction (defect A7). It is REPORTED, not")
        print("      acted on: no seed is excluded for it, and the registered primary below is")
        print("      the UNADJUSTED beta_int.")
    else:
        print("\n  no arm or grade differs from another by more than an order of magnitude.")
    out["fitness"] = {"%s_D%d" % k: v for k, v in fitness_table.items()}
    out["fitness_flags"] = flags

    # ---- §4.6 multiplicity, computed BEFORE the contrast ------------------------------------
    print("\n" + "=" * 96)
    print("§4.6 MULTIPLICITY -- computed on THIS corpus, BEFORE the contrast")
    print("=" * 96)
    print("  The procedure of COUNCIL_round45 §8.2 RE-EXECUTED (crossed_endpoint.py line 175:")
    print("  n_eff = (sum lambda)^2 / sum(lambda^2) over the eigenvalues of the feature")
    print("  correlation matrix). Never a constant carried across corpora: CROSSED_RESULT.json's")
    print("  n_eff = 1.1527 belongs to the crossed corpus and does not transfer to this one.")
    print("  Feature set (fixed in this file before the corpus existed): %s"
          % ", ".join(NEFF_FEATURES))
    M = [[s["features"].get(f, float("nan")) for f in NEFF_FEATURES] for s in retained]
    M = [row for row in M if all(np.isfinite(row))]
    n_eff = n_eff_from(M) if len(M) >= 3 else None
    print("  rows used: %d of %d retained seeds" % (len(M), len(retained)))
    print("  n_eff = %s" % ("%.4f" % n_eff if n_eff is not None else "not computable"))
    out["n_eff"] = n_eff
    out["n_eff_features"] = list(NEFF_FEATURES)

    # ---- cell means, arm means, arm gaps (§1.3) ---------------------------------------------
    print("\n" + "=" * 96)
    print("PRIMARY FEATURE -- sto_utils.cycle_features(sto, side=\"l\", settle=1.0)[\"ank_rom\"]")
    print("=" * 96)
    print("  RAW and UNFILTERED, 100 Hz native rate, left ankle, degrees. The GRF window is")
    print("  whatever that function computes (sto_utils.py lines 202-308); it is not")
    print("  reimplemented here. §1.1 forbids mixing this with the filtered §4.2 variant in one")
    print("  table, and the §4.2 baseline is printed in its own table below.\n")
    print("  %-10s %-18s %3s %4s %10s %9s %9s %10s   %s"
          % ("cond", "role", "D", "n", "mean", "sd", "sem", "predicted", "per-seed"))
    print("  " + "-" * 118)
    cell_means, per_cell_vals = {}, {}
    for cond in CONDITIONS:
        for D in GRADES:
            rs = cell_rows[(cond, D)]
            if len(rs) < MIN_RETAINED_PER_CELL:
                print("  %-10s %-18s %3d %4d %10s   INDETERMINATE-BY-ATTRITION (contributes "
                      "nothing)" % (cond, CONDITIONS[cond]["role"], D, len(rs), "--"))
                continue
            v = np.array([r["ank_rom"] for r in rs], float)
            cell_means[(cond, D)] = float(np.mean(v))
            per_cell_vals[(cond, D)] = v
            pred = ("%10.3f" % PRED_D5[cond]) if (D == 5 and cond in PRED_D5) else (
                "%10.3f" % LEVEL_REFERENCE[cond] if (D == 0 and cond in LEVEL_REFERENCE) else
                "%10s" % "--")
            print("  %-10s %-18s %3d %4d %10.4f %9.4f %9.4f %s   %s"
                  % (cond, CONDITIONS[cond]["role"], D, len(v), float(np.mean(v)),
                     float(np.std(v, ddof=1)), float(np.std(v, ddof=1) / math.sqrt(len(v))),
                     pred, " ".join("%.2f" % x for x in v)))
    print("\n  (the `predicted` column is §3.2's registered prediction at D = 5 and §4.5's level")
    print("   reference at D = 0 -- printed beside the measurement, never instead of it)")

    # pooled within-cell SD -> §5.4's Tier-2 n recomputation rule
    ss, df = 0.0, 0
    for k, v in per_cell_vals.items():
        ss += float(np.sum((v - v.mean()) ** 2))
        df += len(v) - 1
    sigma1 = math.sqrt(ss / df) if df > 0 else float("nan")
    print("\n  pooled within-cell SD sigma_1 = %.4f deg on %d df   (§5.4 measured level-ground "
          "sigma_hat = %.4f)" % (sigma1, df, SIGMA_HAT))
    if sigma1 > SIGMA1_TRIGGER:
        n_new = math.ceil(sigma1 ** 2 / (SXX * PRECISION_TARGET ** 2))
        print("  sigma_1 exceeds the registered trigger %.1f: §5.4 recomputes Tier 2's n as"
              % SIGMA1_TRIGGER)
        print("    n = ceil(sigma_1^2 / (%.4f x %.2f^2)) = ceil(%.4f / %.4f) = %d"
              % (SXX, PRECISION_TARGET, sigma1 ** 2, SXX * PRECISION_TARGET ** 2, n_new))
        out["tier2_n_recomputed"] = int(n_new)
    else:
        print("  sigma_1 is at or below the registered trigger %.1f: Tier 2 stays at n = %d"
              % (SIGMA1_TRIGGER, N_PER_CELL[2]["PRIMARY_SPASTIC"]))
    out["sigma_within_cell"] = sigma1
    out["cell_means"] = {"%s_D%d" % k: v for k, v in cell_means.items()}

    # ---- arm means and gaps -----------------------------------------------------------------
    print("\n  %-4s %12s %12s %12s   %s" % ("D", "A_sp", "A_wk", "d(D)=A_wk-A_sp", "control"))
    print("  " + "-" * 68)
    gaps = {}
    for D in GRADES:
        sp = [cell_means[(c, D)] for c in SPASTIC_ARM if (c, D) in cell_means]
        wk = [cell_means[(c, D)] for c in WEAK_ARM if (c, D) in cell_means]
        ct = cell_means.get((CONTROL_COND, D))
        if len(sp) == len(SPASTIC_ARM) and len(wk) == len(WEAK_ARM):
            gaps[D] = float(np.mean(wk) - np.mean(sp))
            print("  %-4d %12.4f %12.4f %12.4f   %s"
                  % (D, float(np.mean(sp)), float(np.mean(wk)), gaps[D],
                     "%12.4f" % ct if ct is not None else "%12s" % "--"))
        else:
            print("  %-4d %12s %12s %12s   %s" % (D, "--", "--", "--", "--"))
    out["arm_gaps"] = {str(k): v for k, v in gaps.items()}
    print("  (§1.3 measured d(0) on the level corpus = %.4f; this study re-runs level rather than"
          % GAP_LEVEL_MEASURED)
    print("   re-using it, because level is the reference level of the primary predictor and a")
    print("   batch term would alias perfectly with D = 0 -- defect A6, §5.2)")

    # ---- THE PRIMARY: beta_int (§1.3) --------------------------------------------------------
    prim_rows = [{"cond": s["cond"], "D": s["D"], "ank_rom": s["ank_rom"],
                  "terminal_best_fitness": s["terminal_best_fitness"]}
                 for s in retained if s["cond"] in PRIMARY_CONDS
                 and (s["cond"], s["D"]) in per_cell_vals]
    print("\n" + "=" * 96)
    print("PRIMARY -- beta_int, the seed-level OLS `ank_rom ~ condition + D + arm:D` (§1.3)")
    print("=" * 96)
    if len(prim_rows) < 12:
        print("  fewer than 12 usable primary observations; beta_int is not estimable.")
        out["verdict"] = VERDICT_VOID_ATTRITION
        json.dump(out, open(OUT_JSON, "w"), indent=1)
        raise SystemExit("beta_int not estimable on the retained corpus.")
    fit = fit_beta_int(prim_rows)
    print("  model     : ank_rom ~ condition (4 levels, fixed) + D + arm:D, unit = SEED")
    print("  columns   : %s" % ", ".join(fit["names"]))
    print("  n         : %d seed observations over the 12 primary cells, residual df %d"
          % (fit["n_obs"], fit["df"]))
    print("  reference : condition %s; arm_weak = 1 for {%s}, 0 for {%s}"
          % (PRIMARY_CONDS[0], ", ".join(WEAK_ARM), ", ".join(SPASTIC_ARM)))
    print("\n  %-16s %12s %12s" % ("coefficient", "estimate", "SE"))
    print("  " + "-" * 42)
    for nm, b, se in zip(fit["names"], fit["beta"], fit["se"]):
        print("  %-16s %12.5f %12.5f" % (nm, b, se))
    print("\n  ** beta_int (arm:D, WEAK MINUS SPASTIC) = %+.4f deg of arm gap per degree of "
          "decline **" % fit["beta_int"])
    print("     SE %.4f   (§5.4 registered design SE at Tier %d: %.4f)"
          % (fit["se_int"], tier, SE_TIER[tier]))
    print("     95%% CI [%+.4f, %+.4f]   t(%d) = %+.3f   two-sided p = %.5g"
          % (fit["ci95"][0], fit["ci95"][1], fit["df"], fit["t"], fit["p_two_sided"]))
    print("     implied change in the arm gap over D = 5 : %+.4f deg" % fit["implied_gap_change_at_D5"])
    print("     beta_req = %.4f deg/deg = (%.3f - %.4f) / 5, the value the rung-to-rung margin "
          "needs" % (BETA_REQ, MDC_DEG, MARGIN_LEVEL))
    print("     beta_int >= beta_req : %s" % ("YES" if fit["beta_int"] >= BETA_REQ else "NO"))
    print("\n  per-arm slope responses (§2: the divergence must be arm-specific in the predicted")
    print("  direction; a gap that grows because the WEAK arm alone rises, with the spastic arm")
    print("  tracking the unlesioned control, is a weak-arm finding and is reported as such):")
    print("     spastic arm slope : %+.4f  (SE %.4f)" % (fit["slope_spastic"],
                                                         fit["se_slope_spastic"]))
    print("     weak    arm slope : %+.4f  (SE %.4f)" % (fit["slope_weak"], fit["se_slope_weak"]))
    cf, cf_gaps = closed_form_beta_int(cell_means)
    if cf is not None:
        print("\n  cross-check, §1.3's closed form on ARM GAPS:")
        print("     beta_int = Sum_D (D - %.4f) d(D) / %.4f = %+.4f" % (D_BAR, SXX, cf))
        print("     (equal to the OLS coefficient only when the cells are balanced; §2 point 3")
        print("      is explicit that an order statistic and a linear contrast are different")
        print("      estimands, and the OLS value above is the registered primary)")
    out["primary"] = fit
    out["closed_form_beta_int"] = cf

    # fitness-adjusted diagnostic -- printed beside, never instead
    fit_adj = None
    try:
        fit_adj = fit_beta_int(prim_rows, covariate="terminal_best_fitness")
        print("\n  DIAGNOSTIC ONLY -- the same model with terminal best_fitness as a covariate")
        print("  (round-62 addition; §4.4 registers that if beta_int is positive a fitness x D")
        print("   interaction of the same shape must be reported alongside it, because the whole")
        print("   history of this project says cost is the default explanation):")
        print("     beta_int | fitness = %+.4f  (SE %.4f)  95%% CI [%+.4f, %+.4f]"
              % (fit_adj["beta_int"], fit_adj["se_int"], fit_adj["ci95"][0], fit_adj["ci95"][1]))
        print("     coefficient on terminal best_fitness = %+.5f (SE %.5f)"
              % (fit_adj["beta"][-1], fit_adj["se"][-1]))
        print("     shift from the unadjusted primary    = %+.4f deg/deg"
              % (fit_adj["beta_int"] - fit["beta_int"]))
        print("     ** THE REGISTERED PRIMARY IS THE UNADJUSTED VALUE ABOVE. This line does not")
        print("        decide anything and does not exclude anything. **")
    except Exception as e:                                       # noqa: BLE001
        print("\n  fitness-adjusted diagnostic not estimable: %r" % (e,))
    out["primary_fitness_adjusted"] = fit_adj

    # ---- per-condition slope responses (feeds F2, F4, §2) ------------------------------------
    print("\n" + "=" * 96)
    print("PER-CONDITION SLOPE RESPONSE  d(ank_rom)/dD, seed level, within condition")
    print("=" * 96)
    print("  %-10s %-18s %4s %10s %9s %20s %20s"
          % ("cond", "role", "n", "slope", "SE", "95% CI", "§3.2 predicted"))
    print("  " + "-" * 96)
    slopes = {}
    seed_rows_all = [{"cond": s["cond"], "D": s["D"], "ank_rom": s["ank_rom"]}
                     for s in retained if (s["cond"], s["D"]) in per_cell_vals]
    for cond in CONDITIONS:
        sl = cell_slope(seed_rows_all, cond)
        slopes[cond] = sl
        if sl is None:
            print("  %-10s %-18s %4s %10s" % (cond, CONDITIONS[cond]["role"], "--",
                                              "not estimable"))
            continue
        p = PRED_PER_DEGREE.get(cond)
        pred = "%+.2f [%+.2f, %+.2f]" % p if p else "--"
        print("  %-10s %-18s %4d %10.4f %9.4f  [%+8.4f, %+8.4f] %20s"
              % (cond, CONDITIONS[cond]["role"], sl["n"], sl["slope"], sl["se"],
                 sl["ci95"][0], sl["ci95"][1], pred))
    out["cell_slopes"] = {k: v for k, v in slopes.items()}

    # ---- §4.1 the marginal claim, and §4.2 the observable one --------------------------------
    print("\n" + "=" * 96)
    print("§4.1 SECONDARY -- the rung-to-rung mild margin (the DECISION quantity, never the test)")
    print("=" * 96)
    print("  min over {%s} of cell mean  MINUS  max over {%s} of cell mean."
          % (", ".join(WEAK_ARM), ", ".join(SPASTIC_ARM)))
    print("  The min/max definition is fixed in the registration, so a changed binding pair is a")
    print("  recomputation and not a choice made after seeing the data. Bootstrap: %d resamples,"
          % NBOOT)
    print("  the scheme of scone/lr_asymmetry.py report() lines 104-121, RNG seed %d." % BOOT_SEED)
    print("\n  %-4s %10s %14s %14s %24s %10s" % ("D", "margin", "binding weak", "binding spastic",
                                                 "95% bootstrap CI", "P(<= 0)"))
    print("  " + "-" * 84)
    rng = np.random.default_rng(BOOT_SEED)
    margins = {}
    for D in GRADES:
        m = rung_margin(cell_means, D)
        if m is None:
            print("  %-4d %10s" % (D, "--"))
            continue
        bs = margin_bootstrap(per_cell_vals, D, rng)
        margins[D] = {**m, **(bs or {})}
        print("  %-4d %10.4f %14s %14s   [%+8.4f, %+8.4f] %9.1f%%"
              % (D, m["margin"], m["binding_weak"], m["binding_spastic"],
                 bs["ci95"][0] if bs else float("nan"), bs["ci95"][1] if bs else float("nan"),
                 100.0 * bs["p_le_0"] if bs else float("nan")))
    print("\n  level-ground reference margin (LR_ASYMMETRY.json mild_l.margin) = %.4f deg"
          % MARGIN_LEVEL)
    print("  the margin must reach the standing MDC of %.3f deg to be a screening instrument"
          % MDC_DEG)
    if 5 in margins:
        print("  margin at D = 5 reaches the MDC : %s"
              % ("YES" if margins[5]["margin"] >= MDC_DEG else "NO"))
    out["margins"] = {str(k): v for k, v in margins.items()}

    print("\n" + "=" * 96)
    print("§4.2 SECONDARY -- the same margin through the registered video pipeline, BASELINE cell")
    print("=" * 96)
    print("  %.0f Hz resample, %d-order zero-phase %.1f Hz Butterworth, sagittal projection at "
          "yaw 0, noise 0." % (V.FS_LIST[0], V.BUTTER_ORDER, V.FC))
    print("  Constants and transforms taken from video_degradation.py, not re-derived. THE FULL")
    print("  YAW/NOISE GRID OF §4.2 IS PRODUCED BY RE-RUNNING video_degradation.py AGAINST THIS")
    print("  CORPUS -- it is a required secondary and its absence from a Results section is a")
    print("  protocol violation (§4); it is not duplicated here because a second implementation")
    print("  of a registered pipeline is how two variants of one quantity get reported as one.")
    vid_cells = {}
    for cond in CONDITIONS:
        for D in GRADES:
            vals = []
            for s in cell_rows[(cond, D)]:
                if s.get("sto"):
                    try:
                        v = video_rom(s["sto"])
                    except Exception:                            # noqa: BLE001
                        v = None
                    if v is not None:
                        s["video_rom"] = v
                        vals.append(v)
            if len(vals) >= MIN_RETAINED_PER_CELL:
                vid_cells[(cond, D)] = float(np.mean(vals))
    print("\n  %-4s %10s %14s %14s %12s" % ("D", "margin", "binding weak", "binding spastic",
                                            "clean margin"))
    print("  " + "-" * 60)
    vid_margins = {}
    for D in GRADES:
        m = rung_margin(vid_cells, D)
        if m is None:
            print("  %-4d %10s" % (D, "--"))
            continue
        vid_margins[D] = m
        print("  %-4d %10.4f %14s %14s %12s"
              % (D, m["margin"], m["binding_weak"], m["binding_spastic"],
                 "%12.4f" % margins[D]["margin"] if D in margins else "--"))
    print("\n  §7.3 of RESULTS_discrimination.md records that this filter removes 5.9-10.6 deg")
    print("  from the weak arm against 0.8-1.5 deg from every spastic condition, so it is")
    print("  expected to REDUCE whatever the clean margin gives. THIS IS THE QUANTITY THAT MUST")
    print("  CLEAR %.3f deg, and the clean margin above is the registered PRIMARY's companion,"
          % MDC_DEG)
    print("  not a substitute for it.")
    out["video_margins"] = {str(k): v for k, v in vid_margins.items()}
    out["video_cell_means"] = {"%s_D%d" % k: v for k, v in vid_cells.items()}

    # ---- §4.3 the presenting sign, §4.4 the laundering readouts ------------------------------
    print("\n" + "=" * 96)
    print("§4.3 / §4.4 SECONDARIES -- reported whatever they show (a registered secondary absent")
    print("from the Results is a protocol violation, §4)")
    print("=" * 96)
    sec_keys = ("ank_hs", "ank_stance_mean", "cycle_time", "stance_frac", "n_cycles",
                "ank_vel_max")
    print("  %-10s %3s %4s" % ("cond", "D", "n") + "".join("%16s" % k for k in sec_keys))
    print("  " + "-" * (19 + 16 * len(sec_keys)))
    sec = {}
    for cond in CONDITIONS:
        for D in GRADES:
            rs = cell_rows[(cond, D)]
            if len(rs) < MIN_RETAINED_PER_CELL:
                continue
            row = {}
            for k in sec_keys:
                v = [r["features"].get(k) for r in rs]
                v = [float(x) for x in v if x is not None and np.isfinite(float(x))]
                row[k] = float(np.mean(v)) if v else float("nan")
            sec[(cond, D)] = row
            print("  %-10s %3d %4d" % (cond, D, len(rs))
                  + "".join("%16.4f" % row[k] for k in sec_keys))
    out["secondaries"] = {"%s_D%d" % k: v for k, v in sec.items()}
    print("\n  §4.4: if beta_int is flat these say whether the optimizer absorbed the decline")
    print("  (§3.4's registered competing account: CMA-ES re-optimises at every grade and can")
    print("  shorten the step, flex the knee or slow the loading, avoiding the provoking velocity")
    print("  without the reflex being any less velocity-dependent).")

    # ---- §4.5 free replication check ----------------------------------------------------------
    print("\n" + "=" * 96)
    print("§4.5 SECONDARY -- free replication check of the level corpus at fresh optimizer seeds")
    print("=" * 96)
    print("  %-10s %14s %14s %12s" % ("cond", "this study D=0", "ROM_REANALYSIS", "difference"))
    print("  " + "-" * 54)
    rep_out = {}
    for cond, ref in LEVEL_REFERENCE.items():
        got = cell_means.get((cond, 0))
        if got is None:
            print("  %-10s %14s %14.3f %12s" % (cond, "--", ref, "--"))
            continue
        rep_out[cond] = {"fresh": got, "reference": ref, "diff": got - ref}
        print("  %-10s %14.4f %14.3f %12.4f" % (cond, got, ref, got - ref))
    out["replication_check"] = rep_out

    # ---- §4.6 inference caveat ----------------------------------------------------------------
    print("\n" + "=" * 96)
    print("§4.6 INFERENCE CAVEAT -- computed and stated before running, as COUNCIL_round10 §Q2")
    print("requires")
    print("=" * 96)
    print("  With two conditions per arm the exact condition-level permutation null has only")
    print("  C(4,2)/2 = 3 distinct arm assignments, so its attainable two-sided p-floor is 1/3 =")
    print("  %.4f -- it cannot clear alpha = %.2f under any outcome. The condition-level"
          % (1.0 / 3.0, ALPHA))
    print("  permutation is therefore REPORTED BUT IS NOT THE INFERENTIAL BASIS; inference rests")
    print("  on the seed-level CI above.")
    print("  SEEDS ARE OPTIMIZER RESTARTS, NOT SUBJECTS. No sensitivity, specificity or")
    print("  patient-level AUC may be quoted from this study's standard errors.")
    out["perm_p_floor"] = 1.0 / 3.0

    # ---- FALSIFIERS (§6.1) --------------------------------------------------------------------
    print("\n" + "=" * 96)
    print("FALSIFIERS (§6.1) -- evaluated exactly as the registration writes them")
    print("=" * 96)
    b = fit["beta_int"]
    f1 = bool(b <= F1_THRESHOLD)
    print("  F1  THE PRIMARY FALSIFIER, QUANTITATIVE")
    print("      registered: beta_hat_int <= %.4f deg/deg at Tier 1." % F1_THRESHOLD)
    print("      measured  : beta_hat_int = %+.4f" % b)
    print("      at that value the two-sided 95%% upper bound (beta_hat + 1.96 x %.4f) = %+.4f,"
          % (SE_TIER[1], b + 1.96 * SE_TIER[1]))
    print("      against beta_req = %.4f, so the clinically required interaction %s excluded."
          % (BETA_REQ, "IS" if b + 1.96 * SE_TIER[1] < BETA_REQ else "is NOT"))
    print("      F1 FIRES: %s" % ("YES" if f1 else "no"))

    sp_sl = [slopes[c] for c in SPASTIC_ARM]
    ct_sl = slopes.get(CONTROL_COND)
    f2 = bool(ct_sl and all(s is not None and s["slope"] >= ct_sl["slope"] for s in sp_sl))
    print("\n  F2  THE SIGN FALSIFIER, INDEPENDENT OF n")
    print("      registered: the spastic arm's ROM response to decline is at least as large as the")
    print("      unlesioned control's, in BOTH mild spastic cells.")
    if ct_sl:
        print("      control %s slope = %+.4f" % (CONTROL_COND, ct_sl["slope"]))
        for c in SPASTIC_ARM:
            s = slopes.get(c)
            print("      %-8s slope = %s   >= control : %s"
                  % (c, "%+.4f" % s["slope"] if s else "n/a",
                     "YES" if (s and s["slope"] >= ct_sl["slope"]) else "no"))
    print("      F2 FIRES: %s%s" % ("YES" if f2 else "no",
                                    "  -- the reflex contributes nothing to the loading-phase "
                                    "excursion and the §0.2 mechanism is refuted as stated"
                                    if f2 else ""))

    f3 = bool(5 in margins and 0 in margins and margins[5]["margin"] < margins[0]["margin"])
    print("\n  F3  THE DIRECTION FALSIFIER")
    print("      registered: the rung-to-rung mild margin at D = 5 is smaller than at D = 0.")
    if 0 in margins and 5 in margins:
        print("      margin(D=0) = %+.4f   margin(D=5) = %+.4f"
              % (margins[0]["margin"], margins[5]["margin"]))
    print("      F3 FIRES: %s   (F3 alone is not decisive -- it is the marginal claim, §2 -- but"
          % ("YES" if f3 else "no"))
    print("      combined with F1 it closes the question)")

    manip_ok = all(slopes.get(c) is not None for c in MANIP_CONDS) and ct_sl is not None
    f4 = bool(manip_ok
              and all(abs(slopes[c]["slope"]) < F4_SLOPE_TOL for c in MANIP_CONDS)
              and abs(ct_sl["slope"]) < F4_SLOPE_TOL)
    print("\n  F4  THE MANIPULATION FALSIFIER, WHICH VOIDS RATHER THAN FALSIFIES")
    print("      registered: |slope response| < %.1f deg/deg at KV 0.200 AND at TA x0.20 AND in"
          % F4_SLOPE_TOL)
    print("      the unlesioned control. Then nothing was provoked in any arm, the decline did not")
    print("      reach the ankle, and the result is VOID, not null.")
    for c in list(MANIP_CONDS) + [CONTROL_COND]:
        s = slopes.get(c)
        print("      %-8s slope = %s   |slope| < %.1f : %s"
              % (c, "%+.4f" % s["slope"] if s else "n/a", F4_SLOPE_TOL,
                 "YES" if (s and abs(s["slope"]) < F4_SLOPE_TOL) else "no"))
    print("      F4 FIRES: %s%s" % ("YES" if f4 else "no",
                                    "  -- given the gravity-sign defect in §7.2 this is the first "
                                    "thing to suspect" if f4 else ""))
    out["falsifiers"] = {"F1": f1, "F2": f2, "F3": f3, "F4": f4}

    # ---- §2's split verdict and the two-tier decision (§6.2c) ---------------------------------
    print("\n" + "=" * 96)
    print("VERDICT -- §6.2(c), the two-tier rule, ENFORCED IN CODE")
    print("=" * 96)
    print("  Tier 1 (n = %d, %d runs) may STOP the study. It may never declare a positive."
          % (N_PER_CELL[1]["PRIMARY_SPASTIC"], TOTAL_RUNS[1]))
    print("  This analysis is running at TIER %d. Permitted verdicts at this tier: %s"
          % (tier, ", ".join(sorted(TIER1_PERMITTED if tier == 1 else TIER2_PERMITTED))))
    verdict, why = decide(tier, b, f4, n_ind)
    # Second, independent enforcement -- see SECTION 2. One of these could be edited out by
    # accident; the other still fires.
    if tier == 1 and verdict in POSITIVE_VERDICTS:
        raise TwoTierViolation("Tier 1 produced %r. §6.2(c) forbids it absolutely." % verdict)
    if verdict not in (TIER1_PERMITTED if tier == 1 else TIER2_PERMITTED):
        raise TwoTierViolation("Tier %d produced %r, outside its registered verdict set."
                               % (tier, verdict))
    print("\n  ** VERDICT: %s **" % verdict)
    print("     %s" % why)

    print("\n  §2's REGISTERED SPLIT, so a mechanism positive is not reported as a clinical one:")
    mech = fit["ci95"][0] > 0.0
    clin = bool(5 in margins and margins[5]["margin"] >= MDC_DEG)
    print("     mechanism claim (beta_int's 95%% CI excludes 0 from below) : %s"
          % ("POSITIVE" if mech else "not supported"))
    print("     clinical claim  (rung-to-rung margin at D = 5 >= %.3f deg) : %s"
          % (MDC_DEG, "POSITIVE" if clin else "NEGATIVE"))
    if mech and not clin:
        print("     -> 'interaction confirmed, margin still under the MDC' is registered in §2 as")
        print("        a POSITIVE for the mechanism claim and a NEGATIVE for the clinical claim,")
        print("        TO BE WRITTEN UP AS BOTH.")
    if mech and ct_sl and slopes.get("DR2K050") and slopes.get("DR2K075"):
        near = all(abs(slopes[c]["slope"] - ct_sl["slope"]) < 0.2 for c in SPASTIC_ARM)
        if near:
            print("     -> §2: the spastic arm tracks the unlesioned control while the gap grows.")
            print("        A beta_int > 0 produced entirely by the weak arm IS A WEAK-ARM FINDING")
            print("        and is reported as such, not as evidence of a velocity-dependent reflex.")
    out["mechanism_positive"] = bool(mech)
    out["clinical_positive"] = bool(clin)
    out["verdict"] = verdict
    out["verdict_reason"] = why

    if verdict in (VERDICT_FUTILITY_STOP, VERDICT_FINAL_NEGATIVE):
        print("\n  §6.3 -- WHAT THIS NULL BUYS, stated in the registration before the data existed:")
        print("     the standing objection ('you did not challenge the system') is removed; the")
        print("     negative stops being provisional because it becomes bounded; it does NOT show")
        print("     the modelled reflex is not velocity-dependent -- it is, by construction -- it")
        print("     says re-optimised gait does not EXPRESS that dependence as a detectable ROM")
        print("     divergence, and it is to be written as a statement about simulation-based")
        print("     discrimination. §6.2(e): nothing is added after the data are seen, and this is")
        print("     NOT to be followed by another feature search.")

    out["elapsed_s"] = time.time() - t_start
    json.dump(out, open(OUT_JSON, "w"), indent=1)
    json.dump({"seeds": [{k: v for k, v in s.items() if k != "features"} for s in seeds],
               "resolution_rejected": [{"name": r["name"], "reasons": r["reasons"]}
                                       for r in res["rejected"]]},
              open(OUT_VERIF, "w"), indent=1, default=str)
    print("\n  wrote %s" % OUT_JSON)
    print("  wrote %s" % OUT_VERIF)
    print("  script sha256 : %s" % out["script_sha256"])
    return out


# =================================================================================================
# SECTION 8 -- ENTRY POINT
# =================================================================================================
def check_registration(strict):
    print("=" * 96)
    print("REGISTRATION IDENTITY")
    print("=" * 96)
    print("  document : %s" % REG_PATH)
    if not os.path.isfile(REG_PATH):
        print("  *** NOT FOUND ***")
        if strict:
            raise SystemExit("the registration this analysis implements is not on disk")
        return
    got, n = sha256_of(REG_PATH), os.path.getsize(REG_PATH)
    print("  bytes    : %d   (registered %d)  %s" % (n, REG_BYTES,
                                                     "match" if n == REG_BYTES else "*** DIFFER ***"))
    print("  sha256   : %s" % got)
    print("  expected : %s" % REG_SHA256)
    ok = (got == REG_SHA256 and n == REG_BYTES)
    print("  -> %s" % ("MATCH: this is the document that was hashed before the study existed."
                       if ok else
                       "*** MISMATCH: §8 says any modification after the hashing moment "
                       "invalidates the registration. ***"))
    if not ok and strict:
        raise SystemExit("registration hash mismatch; refusing to analyse a corpus under it")


def main(argv=None):
    ap = argparse.ArgumentParser(description="registered analysis for PREREG_slope.md")
    ap.add_argument("--selftest", action="store_true",
                    help="synthetic self-test only; touches no corpus")
    ap.add_argument("--resolve", action="store_true",
                    help="self-test + content resolution + completeness gate; no replay")
    ap.add_argument("--run", action="store_true", help="the full registered analysis")
    ap.add_argument("--tier", type=int, default=1, choices=(1, 2),
                    help="1 = n 6 per primary cell (114 runs); 2 = n 16 (234 runs)")
    ap.add_argument("--results-root", default=RESULTS_ROOT)
    a = ap.parse_args(argv)
    if not (a.selftest or a.resolve or a.run):
        print(__doc__)
        return 2

    check_registration(strict=(a.resolve or a.run))
    st = selftest(verbose=True)
    if a.selftest:
        json.dump(st, open(os.path.join(PAPER, "SLOPE_SELFTEST_r62.json"), "w"), indent=1)
        print("\n  wrote %s" % os.path.join(PAPER, "SLOPE_SELFTEST_r62.json"))
        print("  script sha256 : %s" % sha256_of(os.path.abspath(__file__)))
        return 0

    if a.resolve:
        res = resolve_corpus(a.tier, results_root=a.results_root)
        ok = print_completeness(res["counts"], a.tier)
        print("\n  corpus complete : %s" % ("YES" if ok else "NO -- the analysis would refuse"))
        return 0 if ok else 1

    analyse(tier=a.tier, results_root=a.results_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
