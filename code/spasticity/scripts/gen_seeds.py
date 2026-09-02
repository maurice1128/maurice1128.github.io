"""Multi-seed replication for the converged conditions.

Why. A single CMA-ES run per condition gives one local optimum, and those optima differ in
walking speed/cadence (observed: cycle time 1.38 s for HEALTHY vs 0.65 s for PAR40). With N=1
per condition, a between-condition ankle difference is inseparable from "the optimizer happened
to land at a different cadence". Running several random seeds per condition yields a
DISTRIBUTION of converged gaits, so the pathology effect can be compared against seed-to-seed
variability -- and supplies a legitimate N for statistics.

Seeds are the unit of replication here; they are NOT independent subjects (same body model), so
any generalization claim must still be scoped as within-model robustness, exactly as the council
required for the OCP arm.

Usage:  python gen_seeds.py [--launch] [--tags HEALTHY,PAR20,...] [--seeds 5]
                            [--max-concurrent N]

THE REGISTERED LAUNCH COMMAND for PREREGISTRATION_dose_response_v2.md is

    python gen_seeds.py --tags DR2K000,DR2K050,DR2K100,DR2K150,DR2K200 \\
                        --seeds 16 --max-concurrent 4 --launch

`--tags` IS MANDATORY WITH `--launch` (blocker B6). It used to be optional, and the registered
command omitted it, so the study would have silently launched DEFAULT_TAGS -- HEALTHY, PAR20,
PAR40, PAR60 -- 16 seeds each: 64 optimizations of the wrong conditions, all of them looking
perfectly normal. A default that can be wrong is not a default, it is a trap; `--launch` now
refuses to guess.

`--max-concurrent` IS ALSO MANDATORY WITH `--launch`. The old loop `Popen`-ed every scenario
back to back with no wait, so the registered command would have started 80 CMA-ES optimizations
at once on a machine whose own budget arithmetic (§3.4: 12.6-14.1 h per run, "80 runs at 4-way
concurrency") assumes four.
"""
import os, re, sys, shutil, subprocess, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
SEEDDIR = os.path.join(HERE, "opt_seeds")
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"

DEFAULT_TAGS = ["HEALTHY", "PAR20", "PAR40", "PAR60"]

# Registered constants, kept in one place and imported rather than retyped.
try:
    from gen_conditions import (REGISTERED_MAX_GENERATIONS,      # noqa: F401
                                REGISTERED_MIN_PROGRESS, DR2K_TAGS)
except Exception:                                                # pragma: no cover
    REGISTERED_MAX_GENERATIONS, REGISTERED_MIN_PROGRESS = 250, "0"
    DR2K_TAGS = ["DR2K000", "DR2K050", "DR2K100", "DR2K150", "DR2K200"]


def arg(name, default):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


SEED_RE = re.compile(r"^[ \t]*random_seed[ \t]*=[ \t]*(-?\d+)[ \t]*$", re.M)


def read_seed(txt):
    """-> the single declared random_seed, or None. Raises if more than one is declared."""
    m = SEED_RE.findall(txt)
    if len(m) > 1:
        raise RuntimeError("scenario declares %d random_seed lines: %r" % (len(m), m))
    return int(m[0]) if m else None


def set_seed(txt, s):
    """Write `random_seed = s` STRUCTURALLY, and prove it landed.

    DEFECT 2 REPAIR (2026-07-28, PREREGISTRATION_dose_response.md §6 Gate G).
    The old code inserted the seed by string-replacing the literal `min_progress = 1e-4`:

        txt = txt.replace("min_progress = 1e-4",
                          "min_progress = 1e-4\\n\\trandom_seed = %d" % s, 1)

    `str.replace` on an absent needle is a SILENT NO-OP. Under any stopping rule that does not
    contain that exact byte string -- and this study registers `min_progress = 0` -- no
    `random_seed` was ever written, CMA-ES fell back to its default seed, and all N "seeds" of a
    rung were one identical optimization repeated. The seed spread would have read 0.0 and the
    study would have reported fabricated precision.

    The seed is now written by locating the CmaOptimizer's opening brace and inserting a
    `random_seed` line as its first property (or by rewriting an existing one). The write is
    then READ BACK and asserted, so a failure raises instead of passing silently.
    """
    if SEED_RE.search(txt):
        txt = SEED_RE.sub("\trandom_seed = %d" % s, txt, count=1)
    else:
        m = re.search(r"CmaOptimizer\s*\{", txt)
        if not m:
            raise RuntimeError("no CmaOptimizer block: cannot place random_seed")
        txt = txt[:m.end()] + ("\n\trandom_seed = %d" % s) + txt[m.end():]
    got = read_seed(txt)
    if got != s:
        raise RuntimeError("random_seed write did not land: wanted %d, scenario says %r" % (s, got))
    return txt


def assert_distinct_seeds(built):
    """Every generated scenario must carry a random_seed, and no two may share one.

    This is Gate G at generation time. It fails loudly on exactly the condition the old
    string-replacement produced silently: N scenarios with no seed at all (all None), or N
    scenarios sharing one seed.

    Distinctness is required WITHIN a condition (the replicate set whose spread is the
    statistic), matching Gate G's wording "the cell's scenario contains random_seed = k for its
    own k". Seed k of condition A and seed k of condition B are deliberately the same integer:
    that is a paired design across conditions, not a collapse within one.
    """
    groups, seen_any = {}, 0
    for t2, p in built:
        s = read_seed(open(p, encoding="utf-8", errors="ignore").read())
        if s is None:
            raise RuntimeError("%s carries NO random_seed -- the seed write was a no-op" % t2)
        seen_any += 1
        tag = re.sub(r"_s\d+$", "", t2)
        g = groups.setdefault(tag, {})
        if s in g:
            raise RuntimeError("%s and %s share random_seed = %d -- seeds are not distinct"
                               % (g[s], t2, s))
        g[s] = t2
    for tag, g in sorted(groups.items()):
        print("seed check: %-10s %d scenarios, %d distinct random_seed %s"
              % (tag, len(g), len(g), sorted(g)))
    print("seed check: %d/%d scenarios carry a random_seed" % (seen_any, len(built)))
    return True


PROP_RE = {
    "min_progress": re.compile(r"^[ \t]*min_progress[ \t]*=[ \t]*(\S+)[ \t]*$", re.M),
    "max_generations": re.compile(r"^[ \t]*max_generations[ \t]*=[ \t]*(\S+)[ \t]*$", re.M),
}


def assert_registered_stopping_rule(built):
    """PRE-LAUNCH GATE (PREREGISTRATION_dose_response_v2.md §6; blocker B7).

    Every generated scenario must declare, EXACTLY ONCE each:
        min_progress    = 0
        max_generations = 250
        random_seed     = k, present and DISTINCT within its condition

    Why this is a separate gate and not a comment in the template. Before round 37
    `TEMPLATE_working.scone` carried `min_progress = 1e-4` and NO `max_generations` and NO
    `random_seed`, while §6 registered `0` / `250` / `1..16`. Nothing compared the two. A
    scenario that silently kept `1e-4` stops when the landscape flattens -- and the landscape
    flattens at a different generation for every dose, which is precisely the depth confound
    §6 exists to remove. A gate that is not executed is not a gate.

    Raises on the first violation. Returns True.
    """
    bad = []
    for t2, p in built:
        txt = open(p, encoding="utf-8", errors="ignore").read()
        for key, want in (("min_progress", str(REGISTERED_MIN_PROGRESS)),
                          ("max_generations", str(REGISTERED_MAX_GENERATIONS))):
            got = PROP_RE[key].findall(txt)
            if len(got) != 1:
                bad.append("%s declares %s %d times (want exactly 1): %r"
                           % (t2, key, len(got), got))
            elif got[0] != want:
                bad.append("%s has %s = %s, registered value is %s" % (t2, key, got[0], want))
    if bad:
        raise RuntimeError("REGISTERED STOPPING RULE VIOLATED -- refusing to launch:\n  "
                           + "\n  ".join(bad))
    assert_distinct_seeds(built)          # random_seed present + distinct within condition
    print("stopping-rule check: %d/%d scenarios carry min_progress = %s and "
          "max_generations = %d (terminal generation index %d)"
          % (len(built), len(built), REGISTERED_MIN_PROGRESS, REGISTERED_MAX_GENERATIONS,
             REGISTERED_MAX_GENERATIONS - 1))
    return True


def launch_throttled(built, max_concurrent, seeddir=SEEDDIR, sconecmd=SCONECMD, poll=10.0):
    """Start every scenario, never more than `max_concurrent` at a time.

    Blocker B6: the previous loop `Popen`-ed all of them back to back. stdout AND stderr are
    redirected to `log_<TAG>.txt` and `-q` is NOT passed -- both are required for §7C2 (the
    startup log is the only place SCONE reveals `Warning, unused properties:`).
    """
    if max_concurrent < 1:
        raise ValueError("--max-concurrent must be >= 1, got %r" % max_concurrent)
    running, started = [], 0
    for t2, p in built:
        while len([q for q in running if q[0].poll() is None]) >= max_concurrent:
            time.sleep(poll)
            running = [q for q in running if q[0].poll() is None]
        lg = open(os.path.join(seeddir, "log_%s.txt" % t2), "w")
        pr = subprocess.Popen([sconecmd, "-o", p, "-l", "2"], cwd=seeddir,
                              stdout=lg, stderr=subprocess.STDOUT)
        running.append((pr, t2, lg))
        started += 1
        print("launched %-14s (%d/%d, %d running, cap %d) -> log_%s.txt"
              % (t2, started, len(built),
                 len([q for q in running if q[0].poll() is None]), max_concurrent, t2))
    return started


def main():
    tags_arg = arg("--tags", None)
    if "--launch" in sys.argv and tags_arg is None:
        raise SystemExit(
            "REFUSING TO LAUNCH WITHOUT --tags. The registered command is\n"
            "  python gen_seeds.py --tags %s --seeds 16 --max-concurrent 4 --launch\n"
            "Falling back to DEFAULT_TAGS (%s) here would launch the wrong conditions and "
            "nothing downstream would notice." % (",".join(DR2K_TAGS), ",".join(DEFAULT_TAGS)))
    tags = (tags_arg or ",".join(DEFAULT_TAGS)).split(",")
    nseed = int(arg("--seeds", "5"))
    max_conc = arg("--max-concurrent", None)
    if "--launch" in sys.argv and max_conc is None:
        raise SystemExit(
            "REFUSING TO LAUNCH WITHOUT --max-concurrent. %d scenarios started at once would "
            "oversubscribe the machine by ~%dx against the registered 4-way concurrency of "
            "§3.4." % (len(tags) * nseed, max(1, len(tags) * nseed // 4)))
    os.makedirs(SEEDDIR, exist_ok=True)
    for f in glob.glob(os.path.join(OPT, "*.osim")) + \
             glob.glob(os.path.join(OPT, "*.zml")) + \
             glob.glob(os.path.join(OPT, "*.par")):
        shutil.copy(f, SEEDDIR)

    built = []
    for tag in tags:
        src = os.path.join(OPT, tag + ".scone")
        if not os.path.exists(src):
            print("%-10s missing scenario" % tag)
            continue
        base = open(src, encoding="utf-8", errors="ignore").read()
        for s in range(1, nseed + 1):
            t2 = "%s_s%d" % (tag, s)
            txt = re.sub(r"signature_prefix\s*=\s*\S+",
                         "signature_prefix = %s" % t2, base, count=1)
            txt = set_seed(txt, s)
            p = os.path.join(SEEDDIR, t2 + ".scone")
            open(p, "w", encoding="utf-8").write(txt)
            built.append((t2, p))
    assert_registered_stopping_rule(built)      # includes assert_distinct_seeds
    print("built %d seed scenarios" % len(built))

    if "--launch" in sys.argv:
        launch_throttled(built, int(max_conc))
        print("launched %d at concurrency %s" % (len(built), max_conc))
    return built


if __name__ == "__main__":
    main()
