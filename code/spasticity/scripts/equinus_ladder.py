"""Build both arms along the PHENOTYPE axis (equinus), not along the cost axis.

WHY EVERY PREVIOUS GRID WAS THE WRONG EXPERIMENT.
Severity has been dialled by mechanism strength -- KV for spasticity, tibialis anterior force loss
for weakness -- and the arms were then compared, or matched on the optimizer's objective value.
`verify_equinus.py` shows what that produced:

    TA -20 %   +2.22 deg vs healthy   MORE dorsiflexed -- no equinus
    TA -40 %   -0.24                  ambiguous
    KV 0.02    +3.68                  MORE dorsiflexed -- no equinus
    KV 0.03    -0.50                  ambiguous
    KV 0.05    -0.40                  marginal; below the 3.8-11.5 deg MDC for post-stroke ankle
    TA -60 %   -4.70   TA -70 % -3.96   TA -80 % -10.51   KV 0.10 -11.34   <- only these are real

Only TWO of ten conditions produce clinically real equinus, one per mechanism. Everything else is
a gait that does not have the sign the clinical question is about. A classifier trained across that
grid separates "foot drops" from "foot does not drop" -- the presenting sign a clinician can
already see -- and calls it mechanism discrimination.

The clinical question is the opposite situation: a patient PRESENTS with equinus, and the clinician
must decide whether it is spasticity (botulinum toxin) or weakness (strengthening / AFO), because
the treatments are opposite. The discriminative task is therefore defined ON the equinus-positive
population, matched for how much equinus there is.

THE DESIGN.
Tile both arms across the SAME range of ankle-angle deficit, then ask whether gait separates the
mechanism within matched bands. Selection is on the phenotype, which a clinician and a video camera
can both observe, rather than on CMA-ES fitness, which neither can.

WHY A CONTINUATION LADDER.
Direct high-gain attempts do not converge: SPAS02 (KV 0.2) ended at fitness 32.99, SPAS05 at 57.73,
SPAS10 at 49.14 -- the model falls over. Each rung is therefore warm-started from the converged
solution of the rung below, the technique that worked for the uphill ladder where one-step attempts
failed at 66-95. The weakness arm is warm-started the same way for symmetry of treatment: any
difference in warm-start policy between arms would be a new batch effect, and this project already
has one of those.

MATCHED SETTINGS, so no batch effect can align with the label:
  max_generations = 90, min_progress = 1e-7, seeds 1/2/3, identical objective, both arms.

WHAT THIS SCRIPT DOES NOT DO.
It does not decide which rungs are analysed. Rung selection happens AFTER convergence, by matching
measured equinus across arms, and the matching rule is pre-registered separately. This script only
generates the ladder densely enough that a matched pair exists to be found.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "opt2")
DEEP = os.path.join(HERE, "opt_deep")
EQ = os.path.join(HERE, "opt_equinus")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE_OSIM = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data/H0914M_osim4.osim"
MAX_GEN = 90
SEEDS = (1, 2, 3)

# Rungs chosen to BRACKET the equinus-producing region from below, so the ladder can climb into it.
# KV 0.10 gives -11.34 deg; higher gains are needed to tile above it, and they only converge by
# continuation. TA -60/-70/-80 already span -4.70 to -10.51; -90 extends the top of the range.
SPAS_RUNGS = [0.10, 0.15, 0.22, 0.30]
WEAK_RUNGS = [0.60, 0.70, 0.80, 0.90]

# Warm start for the FIRST rung of each arm: an already-converged run of that same mechanism, so
# neither arm starts from a solution belonging to the other.
SPAS_SEED_TAG = "SPAS01_s3"        # KV 0.10, converged
WEAK_SEED_TAG = "DPAR60_s3"        # TA -60 %, converged


# A warm start inherits its parent's optimization depth. The first attempt at this ladder took the
# spastic parent from SPAS01_s3 at generation 333 and the weakness parent from DPAR60_s3 at
# generation 85 -- a 3.9x depth asymmetry baked into the STARTING POINT, which no per-run
# generation cap can remove. A matched continuation *policy* is not a matched starting *depth*.
# Both parents are therefore truncated to a common ceiling: at 85 they are generation 79 and 85.
WARM_CAP = 85


def best_par(tag, cap=None):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None
    bp, bf, bg = None, 1e9, None
    for d in ds:
        for p in sorted(glob.glob(os.path.join(d, "0*.par"))):
            m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
            if not m:
                continue
            g, f = int(m.group(1)), float(m.group(2))
            if cap is not None and g > cap:
                continue
            if f < bf:
                bp, bf, bg = p, f, g
    return bp, bg


def weak_osim(frac):
    s = open(BASE_OSIM, encoding="utf-8", errors="ignore").read()
    m = re.search(r"(<Millard2012EquilibriumMuscle name=\"tib_ant_l\">)(.*?)"
                  r"(</Millard2012EquilibriumMuscle>)", s, re.S)
    body = re.sub(r"(<max_isometric_force>)([0-9.]+)",
                  lambda x: x.group(1) + ("%.4f" % (float(x.group(2)) * (1 - frac))),
                  m.group(2), count=1)
    s = s[:m.start(2)] + body + s[m.end(2):]
    name = "EQW%02d.osim" % round(frac * 100)
    open(os.path.join(EQ, name), "w", encoding="utf-8").write(s)
    return name


def build(tag, base_text, init_par, mutate):
    s = mutate(base_text)
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, s, count=1)
    s = re.sub(r"init_file\s*=\s*\S+", "init_file = " + init_par, s, count=1)
    s = re.sub(r"min_progress\s*=\s*\S+", "min_progress = 1e-7", s, count=1)
    if "max_generations" not in s:
        s = s.replace("min_progress = 1e-7",
                      "min_progress = 1e-7\n\tmax_generations = %d" % MAX_GEN, 1)
    else:
        s = re.sub(r"max_generations\s*=\s*\d+", "max_generations = %d" % MAX_GEN, s, count=1)
    return s


def launch(tag, text, checks):
    bad = [k for k, v in checks.items() if not v]
    if bad:
        print("  %-14s NOT LAUNCHED -- failed: %s" % (tag, ", ".join(bad)))
        return False
    p = os.path.join(EQ, tag + ".scone")
    open(p, "w", encoding="utf-8").write(text)
    with open(os.path.join(EQ, "log_%s.txt" % tag), "w") as lg:
        subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=EQ,
                         stdout=lg, stderr=subprocess.STDOUT)
    return True


def main():
    rung = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    os.makedirs(EQ, exist_ok=True)
    for src in (SRC, DEEP):
        for f in (glob.glob(os.path.join(src, "*.osim")) + glob.glob(os.path.join(src, "*.zml"))
                  + glob.glob(os.path.join(src, "*.par"))):
            d = os.path.join(EQ, os.path.basename(f))
            if not os.path.exists(d):
                shutil.copy(f, d)

    if rung >= len(SPAS_RUNGS):
        print("ladder complete (%d rungs)" % len(SPAS_RUNGS))
        return

    kv, frac = SPAS_RUNGS[rung], WEAK_RUNGS[rung]
    print("=== rung %d:  spastic KV=%.2f   weakness TA -%.0f%% ===" % (rung, kv, frac * 100))

    # warm start: previous rung's best if it exists, else the seed run for that arm
    sp_prev = "EQS%03d_s1" % round(SPAS_RUNGS[rung - 1] * 100) if rung else SPAS_SEED_TAG
    wk_prev = "EQW%02d_s1" % round(WEAK_RUNGS[rung - 1] * 100) if rung else WEAK_SEED_TAG
    sp_par, sp_g = best_par(sp_prev, cap=WARM_CAP)
    wk_par, wk_g = best_par(wk_prev, cap=WARM_CAP)
    if sp_par is None or wk_par is None:
        print("  missing warm start: spastic=%s weak=%s" % (sp_par, wk_par))
        return
    # Refuse to build an arm on a parent that had substantially more optimization than the other.
    if abs(sp_g - wk_g) > 0.15 * max(sp_g, wk_g):
        print("  ABORT: warm-start depths %d vs %d differ by more than 15%%. Matched continuation "
              "policy does not fix a mismatched starting depth." % (sp_g, wk_g))
        return
    print("  warm-start depth  spastic gen %d  |  weakness gen %d  (cap %d)"
          % (sp_g, wk_g, WARM_CAP))
    # Rename the warm start so it CANNOT match a `0*.par` scan. SCONE copies init_file into the
    # results directory verbatim; if it keeps its donor `<gen>_<sigma>_<fitness>.par` name it sits
    # there looking like one of this run's own generations. Observed on rung 0: EQS010_s1, seconds
    # after launch and capped at 90 generations, contained `0333_0.813_0.790.par` from SPAS01_s3.
    # A scan would have selected the DONOR's controller and labelled it EQS010.
    sp_init = "warmstart_spas_rung%d.par" % rung
    wk_init = "warmstart_weak_rung%d.par" % rung
    shutil.copy(sp_par, os.path.join(EQ, sp_init))
    shutil.copy(wk_par, os.path.join(EQ, wk_init))
    print("  warm start  spastic <- %s\n              weakness <- %s" % (sp_init, wk_init))

    spas_base = open(os.path.join(SRC, "SPAS01.scone"), encoding="utf-8").read()
    weak_base = open(os.path.join(DEEP, "DHEALTHY_s1.scone"), encoding="utf-8").read()
    om = weak_osim(frac)
    n = 0

    for sd in SEEDS:
        tag = "EQS%03d_s%d" % (round(kv * 100), sd)
        s = build(tag, spas_base, sp_init, lambda t: re.sub(r"KV = 0\.[0-9]+", "KV = %.4f" % kv, t))
        s = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % sd, s, count=1)
        if "random_seed" not in s:
            s = s.replace("min_progress = 1e-7", "min_progress = 1e-7\n\trandom_seed = %d" % sd, 1)
        n += launch(tag, s, {
            "reflex present": "name = SpasticL" in s,
            "KV set on both muscles": len(re.findall(r"KV = %.4f" % kv, s)) == 2,
            "symmetric intact": s.count("symmetric = 1") == 2,
            "max_generations": "max_generations = %d" % MAX_GEN in s,
            "warm start": sp_init in s,
        })

    for sd in SEEDS:
        tag = "EQW%02d_s%d" % (round(frac * 100), sd)
        s = build(tag, weak_base, wk_init,
                  lambda t: re.sub(r"model_file\s*=\s*\S+", "model_file = " + om, t, count=1))
        s = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % sd, s, count=1)
        n += launch(tag, s, {
            "no reflex injected": "SpasticL" not in s,
            "weak model wired": om in s,
            "symmetric intact": s.count("symmetric = 1") == 2,
            "max_generations": "max_generations = %d" % MAX_GEN in s,
            "warm start": wk_init in s,
        })

    print("\nlaunched %d runs for rung %d." % (n, rung))
    print("When they converge, run verify_equinus.py on EQS*/EQW* and advance:")
    print("    python equinus_ladder.py %d" % (rung + 1))


if __name__ == "__main__":
    main()
