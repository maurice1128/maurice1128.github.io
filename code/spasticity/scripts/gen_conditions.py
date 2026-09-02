"""Generate SCONE impaired-gait conditions using the PROVEN converging recipe.

Recipe (reverse-engineered from converged reference scenarios):
  * controller stays `symmetric = 1` with the FULL GH2010 written INLINE with `~v<lo,hi>`
    free parameters -> warm-start parameter names match the healthy ResultH0914Gait10.par
    exactly, so `init_file` actually applies (this was the convergence blocker: an
    asymmetric/composite controller renames the parameters and silently cold-starts).
  * impairment is imposed on the PLANT (unilateral modified .osim), not the controller.
    Physiologically: the CNS control law is bilaterally symmetric; the muscle is weak.
  * spasticity (a genuine controller asymmetry) is added as a SEPARATE reflex controller
    with NO free parameters, so it does not perturb the warm-start parameter layout.

Conditions (affected side = LEFT = stroke):
  healthy | paretic (tib_ant_l weak) | spastic (KV on soleus_l/gastroc_l) | mixed (both)

Usage:  python gen_conditions.py            # writes models/ + opt2/*.scone
        python gen_conditions.py --launch    # ...and launches the optimizations
"""
import os, re, sys, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
OPT = os.path.join(HERE, "opt2")
DATA = r"C:\Program Files\SCONE\scone\scenarios\Examples2\data"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE_OSIM = os.path.join(MODELS, "H0914M_osim4.osim")
TEMPLATE = os.path.join(OPT, "TEMPLATE_working.scone")

# affected side = left (stroke hemiparesis)
DORSIFLEXOR = "tib_ant_l"
PLANTARFLEXORS = ("soleus_l", "gastroc_l")

# ---- REGISTERED STOPPING RULE (PREREGISTRATION_dose_response_v2.md §6; blocker B7) ----------
# These are constants of the design, not defaults. Every generated scenario must carry them,
# and `make_scenario` READS THEM BACK and raises if the write did not land -- the same
# fail-loudly discipline `gen_seeds.set_seed` had to adopt after a silent `str.replace` no-op
# wrote no `random_seed` at all.
#
# GENERATION CONVENTION, MEASURED, NOT ASSUMED (blocker B8). Across 107 archived runs that
# declare an explicit `max_generations`, every run that reached its cap has a `history.txt`
# with EXACTLY `max_generations` data rows, indexed 0 .. max_generations-1
# (e.g. CMW70_s1 / DHEALTHY_s1..s3 / EQS010_s1: max_generations=90 -> 90 rows, last index 89).
# So `max_generations = 250` means the TERMINAL GENERATION INDEX IS 249, and generation 250
# NEVER EXISTS. Any gate written against "generation 250" is unsatisfiable.
# TWO STUDIES, TWO BUDGETS, ONE GLOBAL. This constant was 250 -- the dose-response LADDER's
# budget -- while the crossed lesion x budget experiment registers 90. `make_scenario` reads it
# at call time (line ~74), so generating the crossed set would have written 250 into all 48
# scenarios: 740 CPU-hours instead of 266, and, far worse, a DIFFERENT BUDGET FROM THE ONE
# REGISTERED -- in an experiment whose entire purpose is that every condition runs at ONE
# identical budget. It would have completed successfully and answered a different question.
#
# WHY NO GATE CAUGHT IT, WHICH IS THE INSTRUCTIVE PART. `assert_tags_exist` checks tag
# membership, `assert_cell_counts` checks cell composition, `check_structure` checks the
# controller tree, `check_unused` checks acceptance. NONE of them reads the stopping rule. Every
# one of those gates was built FROM the defect catalogue, so they cover the catalogue -- and this
# constant was never in it. A control set validated against known failure modes, then trusted
# against an unknown one, is the recurring shape of this project's worst defects.
#
# The readback gate (V7) does check it, but it runs AFTER generation; if the cells had launched
# first it becomes #10 verbatim -- a constant corrected in source while the job running the old
# value keeps going.
STUDY = "crossed"                    # "crossed" | "ladder" -- set deliberately, never inferred
_BUDGET = {"crossed": 90, "ladder": 250}
REGISTERED_MAX_GENERATIONS = _BUDGET[STUDY]
REGISTERED_MIN_PROGRESS = "0"
REGISTERED_TERMINAL_GENERATION = REGISTERED_MAX_GENERATIONS - 1        # crossed: 89


def _optimizer_property(text, key, value):
    """Write `key = value` as a property of the CmaOptimizer block, and prove it landed.

    Rewrites an existing top-level declaration if there is one, otherwise inserts the property
    immediately after `CmaOptimizer {`. Read back and asserted -- never a silent no-op.
    """
    rx = re.compile(r"^([ \t]*)%s[ \t]*=[ \t]*(\S+)[ \t]*$" % re.escape(key), re.M)
    if rx.search(text):
        text = rx.sub(lambda m: "%s%s = %s" % (m.group(1), key, value), text, count=1)
    else:
        m = re.search(r"CmaOptimizer\s*\{", text)
        if not m:
            raise RuntimeError("no CmaOptimizer block: cannot place %s" % key)
        text = text[:m.end()] + ("\n\t%s = %s" % (key, value)) + text[m.end():]
    got = rx.findall(text)
    if len(got) != 1 or got[0][1] != str(value):
        raise RuntimeError("%s write did not land: scenario says %r, wanted %r"
                           % (key, got, value))
    return text


def apply_registered_stopping_rule(text):
    """§6: identical stopping rule in every cell, asserted at generation time."""
    text = _optimizer_property(text, "min_progress", REGISTERED_MIN_PROGRESS)
    text = _optimizer_property(text, "max_generations", str(REGISTERED_MAX_GENERATIONS))
    return text


def make_osim(tag, weak_map):
    """Write an impaired .osim: weak_map = {muscle_name: retained_force_fraction}."""
    s = open(BASE_OSIM, encoding="utf-8", errors="ignore").read()
    for mus, frac in weak_map.items():
        m = re.search(r'name="%s"' % mus, s)
        if not m:
            raise RuntimeError("muscle not found: " + mus)
        seg_start = m.end()
        seg = s[seg_start:seg_start + 3000]
        f = re.search(r"(<max_isometric_force>\s*)([\d.eE+-]+)", seg)
        if not f:
            raise RuntimeError("no max_isometric_force for " + mus)
        newval = float(f.group(2)) * frac
        seg_new = seg[:f.start()] + f.group(1) + ("%.1f" % newval) + seg[f.end():]
        s = s[:seg_start] + seg_new + s[seg_start + 3000:]
    p = os.path.join(MODELS, "H0914_%s.osim" % tag)
    open(p, "w", encoding="utf-8").write(s)
    return os.path.basename(p)


def spastic_block(kv):
    """Unilateral velocity-dependent plantarflexor stretch reflex (Lance), 1.0x delivery.

    FIXED 2026-07-27, verified on a structurally-checked test scenario:
      soleus_l  K_hat/K_declared = 0.9975 (was 2.000000) | gastroc_l 0.9959
      soleus_r / gastroc_r  max|input-RF| = 0.000e+00  -- right leg untouched
      parameters 36, unchanged; no unused-property warning.
      The 0.25-0.4%% deficit is 10 ms trapezoid sampling, not a loss.

    WHY THE OLD FORM DOUBLED. A bare ReflexController sits at a side-unscoped Location, so SCONE
    builds each declared reflex once per side; GetSidedName returns a target already ending in
    `_l` unchanged, so BOTH constructions landed on the LEFT muscle -- a doubling and a
    mis-targeting at once. `legs = left` gives the enclosing ConditionalController a definite
    side, so it is built for the left leg only, and the target resolves to soleus_l exactly once.

    ⛔ A four-row probe table stood here and has been DELETED. It asserted specific fitness and
    `copies` values for four (legs, target-suffix) combinations. The only preserved artifact with
    that geometry is `legs_calibration/legstest/results/V_left_suffixed...`, whose best `.par` is
    `0000_97.293_96.419.par` and which THIS PROJECT'S OWN INSTRUMENT reads as
    `copies = 3.371973 / 7.989809, ABSTAIN` -- not the `1.000000` the table claimed. (That probe
    is itself confounded: it also side-suffixed two BASE GH2010 reflexes, so it does not refute
    the table either. The point is that the artifact preserved to support the claim cannot support
    it, and no other artifact does.)

    That was defect #96 -- an uncontrolled inference written into documentation as established
    fact -- recurring inside the docstring written to retract #96. Documentation is where these
    calcify: a docstring outlives the reasoning that produced it and is read as settled.

    WHAT REMAINS SUPPORTED, and it is the only reason side-free targets are used here:
    `V_left_suffixed` and `V_right_suffixed` -- declaring OPPOSITE legs, both with `_l` suffixed
    targets -- produce identical fitness and identical `copies`/`rho` to six digits, and emit only
    `soleus_l.RV`/`gastroc_l.RV`. **An explicit `_l` suffix overrides `legs`.** A block declared
    `legs = right` therefore drives the LEFT muscles, silently. Writing the target side-free makes
    `legs` the single source of truth for which limb is lesioned, so the two can never disagree.

    Whether `legs` alone would suffice for the 1.0x is NOT established here and is not claimed.

    `legs` is undocumented (no shipped scenario, not in resources/help/keywords.txt) but is a
    real typed property in sconelib.dll; `legs = banana` raises
    `Could not convert "banana" to enum scone::Side`.

    NEVER USE `legs = opposite` OR `legs = other`. The enum accepts them but they select NO leg;
    SCONE then reports the whole child ReflexController as unused and the injection is silently
    lost -- the 0x failure this project already suffered twice (SPASpf, SPASpf2).

    ⚠ UNVERIFIED AS OF 2026-08-03 (round 61). DO NOT READ THE PARAGRAPH BELOW AS CURRENT.

    THE CLAIM, as it stood: "delivered_gain.py CANNOT SEE THIS FIX: it identifies an injection by
    a target ending in `_l`/`_r`, the exact syntax removed here, so it returns
    NO_INJECTION_DECLARED_AND_NONE_DELIVERED on a correct unilateral delivery."

    WHY IT IS NOW IN DOUBT. `delivered_gain.py` no longer matches on target syntax. It declares
    `INJ_MARKER = "SPASTIC"` and selects injected reflexes by the ENCLOSING controller's name --
    `(r.get("cname") or "").upper().startswith(INJ_MARKER)` -- and its own comment at that line
    says the target-suffix heuristic was removed for precisely the failure this paragraph
    describes. The block below writes `name = SpasticL`, which uppercases to `SPASTICL` and would
    match. On a reading of the two sources the claim looks obsolete.

    WHY IT IS NOT BEING CORRECTED. A reading of two sources is not a delivery certificate, and
    this docstring's own history is the argument against treating one as such: the four-row probe
    table deleted above was an uncontrolled inference written into documentation as established
    fact, inside the docstring written to retract the previous such inference (defect #96). What
    is NOT established by reading the code is whether the parser in `delivered_gain.py` actually
    populates `cname` with `SpasticL` for a MuscleReflex nested two levels down
    (ConditionalController -> ReflexController -> MuscleReflex), which is the structure this
    function emits. If `cname` resolves to the ConditionalController, or to nothing, the marker
    does not match and the old claim still holds.

    WHAT WOULD SETTLE IT, and nothing short of this may be used to amend this paragraph: run
    `delivered_gain.py` end to end on a COMPLETED spastic cell -- a real optimization directory
    with a `.par` and an `.sto`, not a hand-built test scenario -- and read the verdict. A PASS
    with `copies` inside TOL_COPIES retires the claim. A
    NO_INJECTION_DECLARED_AND_NONE_DELIVERED confirms it. No spastic cell has completed since the
    marker change, which is the entire reason this is unresolved; the slope study running at the
    time of writing is expected to produce the first one.

    UNTIL THEN, TREAT DELIVERY AS UNCERTIFIED FOR SCENARIOS BUILT BY THIS FUNCTION. That is the
    conservative reading and it is the project's standing rule: every abnormal or ambiguous
    condition returns FAIL or ABSTAIN, never PASS, and an unverified docstring is an ambiguous
    condition.
    """
    L = ["				ConditionalController {",
         '					states = "EarlyStance LateStance Liftoff Swing Landing"',
         "					legs = left",
         "					ReflexController {",
         "						name = SpasticL"]
    for mus in PLANTARFLEXORS:
        L += ["						MuscleReflex {",
              "							target = %s" % mus.replace("_l", "").replace("_r", ""),
              "							delay = 0.020",
              "							KV = %.3f" % kv,
              "							allow_neg_V = 0",
              "						}"]
    L += ["					}", "				}"]
    return chr(10).join(L)


def make_scenario(tag, osim_file, kv=0.0):
    """Build a scenario from the proven template: swap prefix/model, apply the registered
    stopping rule, and splice the fixed spastic reflex in as one more `ConditionalController`
    INSIDE `GaitStateController / ConditionalControllers`.

    IT IS NEVER WRAPPED IN A `CompositeController`. See the block comment below: that placement
    is parsed, named in `Warning, unused properties:` and DISCARDED."""
    s = open(TEMPLATE, encoding="utf-8-sig", errors="ignore").read()  # -sig: a BOM in the
    # template makes SCONE reject EVERY generated scenario with "Invalid label CmaOptimizer".
    # A Jul-27 edit introduced one and it went unnoticed until the pipeline gate.
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % tag, s, count=1)
    s = re.sub(r"model_file\s*=\s*\S+", "model_file = %s" % osim_file, s, count=1)
    s = apply_registered_stopping_rule(s)     # §6 / blocker B7 -- asserted, not hoped for

    if kv is not None:
        # DEFECT 1 REPAIR (2026-07-28, PREREGISTRATION_dose_response.md §1.1).
        # This branch used to read `if kv > 0:`, which OMITTED THE ENTIRE ConditionalController
        # at KV = 0. The KV = 0 control then carried 5 ConditionalControllers while every
        # treatment cell carried 6: a different controller topology, a different emitted .sto
        # channel set, and a control on which the three verification instruments cannot be run
        # identically. §1.1 requires the control to contain the block with the gain set to zero.
        # The block is now ALWAYS emitted; `kv = 0.0` yields `KV = 0.000` inside an otherwise
        # byte-identical block. Pass kv=None only if a caller genuinely wants no block at all
        # (no condition in this file does).
        #
        # ★ PLACEMENT IS LOAD-BEARING AND WAS WRONG. The block must go INSIDE
        # `GaitStateController / ConditionalControllers`, appended as one more
        # `ConditionalController`. It must NOT be wrapped in a `CompositeController`.
        #
        # `ConditionalController` is not a valid child of `CompositeController`: SCONE parses it,
        # names the entire subtree in `Warning, unused properties:`, and CONTINUES AS A WARNING.
        # The previous version of this function did exactly that, so every scenario it generated
        # was a KV = 0 run wearing a SPAS label -- no crash, no loud warning, nothing abnormal in
        # the output. Empirically established by a four-way placement probe:
        #
        #   ConditionalController{legs} under CompositeController          -> DISCARDED
        #   ConditionalController{legs} inside ConditionalControllers      -> ACCEPTED, 1.0x
        #   bare ReflexController, target = soleus_l (the old form)        -> ACCEPTED, 2.0x
        #   bare ReflexController carrying `legs` itself                   -> `legs` DISCARDED,
        #                                                                     bilateral 2.0x
        #
        # The 0.9975 / 0.9959 figures in spastic_block's docstring were measured on the second
        # form -- a hand-built scenario -- and then this function wrote the block into the first.
        # The fix was validated somewhere the generator never put it.
        i = s.index("ConditionalControllers {")
        depth, k = 0, s.index("{", i)
        while True:
            if s[k] == "{":
                depth += 1
            elif s[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        # k is the closing brace of ConditionalControllers; splice in just before it
        s = s[:k] + spastic_block(kv) + "\n\t\t\t" + s[k:]

    p = os.path.join(OPT, "%s.scone" % tag)
    open(p, "w", encoding="utf-8").write(s)
    return p


# ---- condition grid: affected = LEFT ------------------------------------------------
# paretic  = dorsiflexor (tib_ant_l) weakness  -> foot drop
# spastic  = velocity stretch reflex on plantarflexors -> equinus
# mixed    = both (the clinically common, hardest-to-separate case)
CONDITIONS = [
    ("HEALTHY",  {},                        0.0),
    ("PAR20",    {DORSIFLEXOR: 0.80},       0.0),
    ("PAR40",    {DORSIFLEXOR: 0.60},       0.0),
    ("PAR60",    {DORSIFLEXOR: 0.40},       0.0),
    # KV ladder starts mild: a reflex severe enough to topple even an ADAPTED controller is
    # not a spastic-gait model (real spastic patients walk). Milder gains give CMA-ES a
    # reachable stable pathological gait; the ladder then shows the severity gradient.
    ("SPAS02",   {},                        0.2),
    ("SPAS05",   {},                        0.5),
    ("SPAS10",   {},                        1.0),
    ("SPAS20",   {},                        2.0),
    ("MIX20S05", {DORSIFLEXOR: 0.80},       0.5),
    ("MIX40S05", {DORSIFLEXOR: 0.60},       0.5),
    ("MIX40S02", {DORSIFLEXOR: 0.60},       0.2),
    ("MIX20S10", {DORSIFLEXOR: 0.80},       1.0),

    # ---- REGISTERED DOSE-RESPONSE LADDER (PREREGISTRATION_dose_response_v2.md §2.2) ---------
    # Blocker B6: §11 registered a launch command naming DR2K scenarios that DID NOT EXIST --
    # neither in this table nor in opt2/, so `gen_seeds.py --tags DR2K...` would have printed
    # "missing scenario" five times and launched nothing (or, with the old default tags, would
    # have launched HEALTHY/PAR20/PAR40/PAR60 instead). The five cells are now generated here,
    # which is the only place `spastic_block()` is written into a scenario.
    # All values are TRUE DELIVERED gain: the current block delivers 1.0x (§0.2), so the
    # declared KV and the true KV are the same number.
    ("DR2K000",  {},                        0.000),   # control: block present, gain zero
    ("DR2K050",  {},                        0.050),
    ("DR2K100",  {},                        0.100),
    ("DR2K150",  {},                        0.150),
    ("DR2K200",  {},                        0.200),   # ladder top

    # ---- CROSSED LESION x BUDGET EXPERIMENT (COUNCIL_round45.md) ---------------------------
    # The round-44 fresh-eyes referee showed that FIVE of thirteen candidate features separate
    # perfectly between `HEALTHY_s1..s4` (stopped at generation 20) and `DHEALTHY_s1..s3`
    # (stopped at 90) -- runs with NO lesion at all, differing only in optimizer budget. Six
    # features therefore leave the paper. `ank_vel_max` and `ank_rom` survive that control, but
    # NO contrast in the archive is clean on depth and settings simultaneously, and none can be
    # made so: the archive contains three different stopping rules distributed non-randomly
    # across the arms. Only new runs at ONE budget fix it.
    #
    # WHY THESE TWO TAGS AND NOT NONE. Unifying the budget MERGES `PAR*` with `DPAR*`, because
    # they share a `model_file` and differ ONLY in budget -- exactly what makes the control valid
    # and what breaks the design. The weak arm would collapse 6 conditions -> 3, and the
    # condition-level exact-test floor would rise 0.0043 -> 0.0357; times 3.19 effective tests
    # that is 0.1139, and the headline becomes non-significant WITHOUT the effect changing.
    # A control that removes a confound by merging conditions also removes the degrees of freedom
    # the primary test runs on. Restoring the weak arm to 5 levels costs these two tags.
    ("CMW70",    {DORSIFLEXOR: 0.30},       0.0),     # tib_ant_l -70%
    ("CMW80",    {DORSIFLEXOR: 0.20},       0.0),     # tib_ant_l -80%
    # The FIFTH spastic dose, and it is arithmetic rather than taste. The registered ladder has
    # four gains (0.050/0.100/0.150/0.200). Against a five-level weak arm that is a 4x5
    # condition-level contrast, whose two-sided exact Mann-Whitney floor is 2/C(9,4) = 0.0159;
    # multiplied by the 3.19 effective tests it becomes 0.0507 and FAILS alpha = 0.05 -- with a
    # perfect separation, before any data exist. 5x5 gives 2/C(10,5) = 0.0079 -> 0.0253, which
    # passes. One extra condition is the difference between an experiment that can reach
    # significance and one that provably cannot.
    #
    # 0.075 rather than a new extreme: it fills the widest gap in the ladder, and the referee
    # showed separation DEGRADES as spasticity worsens (KV 0.05 -> 115 deg/s, 0.10 -> 172,
    # running toward the weak group), so resolution is worth more at the mild end -- which is
    # also where a screening tool would be used.
    #
    # FLAGGED FOR RATIFICATION: this is a design choice made by the executor. R45-S forbids
    # promoting a feature to primary after seeing data; it does not cover adding a condition
    # before any data exist, but the watchdog must sign this off or replace it.
    ("DR2K075",  {},                        0.075),
]

DR2K_TAGS = ["DR2K000", "DR2K050", "DR2K100", "DR2K150", "DR2K200"]

#: The crossed experiment's 12 conditions. Weak arm 5 levels, spastic arm 5 levels (the DR2K
#: ladder at true delivered gain), the structurally-isomorphic zero-gain control, and healthy.
#: EVERY cell runs at ONE budget -- `min_progress = 0`, `max_generations = 90` -- with no
#: exceptions, which is the entire point of the design.
CROSSED_TAGS = ["HEALTHY", "DR2K000",
                "PAR20", "PAR40", "PAR60", "CMW70", "CMW80",
                "DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]

#: The primary contrast's two arms, named explicitly. `DR2K000` is the zero-gain control and
#: `HEALTHY` the unlesioned reference -- NEITHER is in an arm, because a control that is counted
#: as a condition inflates the very df the design was corrected to protect.
CROSSED_SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
CROSSED_WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]


def main():
    os.makedirs(MODELS, exist_ok=True); os.makedirs(OPT, exist_ok=True)
    # SCONE resolves relative paths from the scenario dir -> stage what it needs there.
    for f in ("InitStateGait10.zml", "ResultH0914Gait10.par"):
        src = os.path.join(DATA, f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OPT, f))
    # ---------------------------------------------------------------- round 45: --gate
    # `--gate TAG` builds ONE condition at max_generations = 1 and launches it through the
    # IDENTICAL `Popen` + redirect block below. It exists because the alternative -- invoking
    # sconecmd by hand and inspecting the log -- is exactly the defect it is meant to close.
    #
    # The launcher redirect was written at round 34 and reported closed at round 43 on the
    # strength of `scone/launchlog_gate/`, which was produced by an ad-hoc invocation: no
    # checked-in script references it and `opt2/launch_logs/` did not exist. That is the rule
    # "a fix verified anywhere other than the shipped path is not verified", committed while
    # quoting that rule. This flag makes the demonstration run on the shipped path or not at all.
    #
    # It does NOT add a second launch path: it filters `made` and lowers one constant. Every line
    # that actually starts a process is the same code `--launch` runs.
    global REGISTERED_MAX_GENERATIONS, REGISTERED_TERMINAL_GENERATION
    gate_tag = None
    if "--gate" in sys.argv:
        i = sys.argv.index("--gate")
        gate_tag = sys.argv[i + 1] if i + 1 < len(sys.argv) else "HEALTHY"
        REGISTERED_MAX_GENERATIONS = 1
        REGISTERED_TERMINAL_GENERATION = 0
        print("GATE MODE: %s only, max_generations=1, shipped launch path" % gate_tag)

    made = []
    for tag, weak, kv in CONDITIONS:
        if gate_tag is not None and tag != gate_tag:
            continue
        osim = make_osim(tag, weak) if weak else "H0914M_osim4.osim"
        if not weak:
            shutil.copy(BASE_OSIM, os.path.join(OPT, "H0914M_osim4.osim"))
        else:
            shutil.copy(os.path.join(MODELS, osim), os.path.join(OPT, osim))
        p = make_scenario(tag, osim, kv)
        made.append((tag, p))
        print("built %-9s osim=%-22s KV=%.3f  (min_progress=%s max_generations=%d)"
              % (tag, osim, kv, REGISTERED_MIN_PROGRESS, REGISTERED_MAX_GENERATIONS))

    if "--launch" in sys.argv:
        # ★ LOG CAPTURE IS NOT OPTIONAL. Two independent defects here destroyed the startup log
        # for every run this launcher ever started, and the startup log is THE ONLY place SCONE
        # reveals that it silently discarded a controller subtree ("Warning, unused properties:").
        # Measured: 60 of 60 archived `optimization.log` files are ZERO BYTES, so for those runs
        # there is no structural evidence at all -- and `check_unused.py` was returning PASS on
        # that absence, certifying nothing as clean.
        #   (1) `-q` suppressed the console output, and
        #   (2) `Popen` had no `stdout`/`stderr` redirect, so whatever survived went nowhere.
        # `gen_seeds.py` (which omits `-q` and redirects) produced usable 32-43 kB logs from the
        # same binary, which is how we know both changes are needed rather than either alone.
        # Do not re-add `-q`, and do not drop the redirect.
        logdir = os.path.join(OPT, "launch_logs")
        os.makedirs(logdir, exist_ok=True)
        for tag, p in made:
            lg = open(os.path.join(logdir, "log_%s.txt" % tag), "w")
            subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=OPT,
                             stdout=lg, stderr=subprocess.STDOUT,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            print("launched", tag, "-> launch_logs/log_%s.txt" % tag)
    return made


if __name__ == "__main__":
    main()
