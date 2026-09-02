"""Re-run the spastic arm under the SAME stopping rule as the non-spastic arm.

BLOCKER R10-2. The level-ground dataset cannot support any classification claim as it stands,
because the class label is 100 % predictable from the optimizer settings:

    class 0 (HEALTHY, PAR20/40/60)   opt_deep      max_generations = 90   min_progress = 1e-7
    class 1 (SPAS005, SPAS01)        opt2/opt_spseed   NO max_generations  min_progress = 1e-4

That is a batch effect perfectly aligned with the outcome, and no within-batch cross-validation can
detect a confound that is constant within a class. It is also why the two arms ended up at wildly
different convergence states: class 0 sat at its own optimum (analysed .par == best .par, 12/12),
while class 1 was still descending at generation 242-337.

WHAT THIS SCRIPT DOES, AND WHAT IT DELIBERATELY DOES NOT.
It changes three optimizer lines and nothing else. Verified before launching:

  * `symmetric = 1` sits inside GaitStateController in both arms (line 22-24), and inside the
    DofLimits measure in both. A previous blanket replace flipped the measure's flag too and
    silently changed the problem dimension from 36 to 65.
  * both arms carry 36 free parameters. The injected SpasticL reflex uses FIXED gains (KV = 0.05,
    no `~`), so it adds no dimensions -- the optimization problem is identical.
  * the only remaining differences are min_progress, max_generations and random_seed.

3 seeds per condition, matching class 0's 3 seeds. Tagged D* to match the class-0 naming.

After this completes the level-ground dataset has, for the first time, one stopping rule across
every arm: DHEALTHY/DPAR20/40/60 + CMW70/80 (non-spastic) vs CMS020/030 + DSPAS005/DSPAS01
(spastic), all at max_generations = 90, min_progress = 1e-7.
"""
import glob
import os
import re
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "opt2")
DST = os.path.join(HERE, "opt_deep_spas")
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
MAX_GEN = 90
SEEDS = (1, 2, 3)
BASES = {"DSPAS005": ("SPAS005.scone", 0.05), "DSPAS01": ("SPAS01.scone", 0.10)}


def main():
    os.makedirs(DST, exist_ok=True)
    for f in (glob.glob(os.path.join(SRC, "*.osim")) + glob.glob(os.path.join(SRC, "*.zml"))
              + glob.glob(os.path.join(SRC, "*.par"))):
        d = os.path.join(DST, os.path.basename(f))
        if not os.path.exists(d):
            shutil.copy(f, d)

    n = 0
    for label, (base, kv) in BASES.items():
        src = os.path.join(SRC, base)
        if not os.path.exists(src):
            print("%-13s MISSING %s" % (label, base))
            continue
        raw = open(src, encoding="utf-8").read()
        for sd in SEEDS:
            tag = "%s_s%d" % (label, sd)
            s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, raw, count=1)
            s = s.replace("min_progress = 1e-4",
                          "min_progress = 1e-7\n\tmax_generations = %d\n\trandom_seed = %d"
                          % (MAX_GEN, sd), 1)

            # --- verify, do not assume. Silent injection failure is on this project's record. ---
            checks = {
                "reflex present": "name = SpasticL" in s,
                "KV correct": len(re.findall(r"KV = %.3f" % kv, s)) == 2,
                "soleus+gastroc targeted": ("target = soleus_l" in s and "target = gastroc_l" in s),
                "min_progress matched": "min_progress = 1e-7" in s and "1e-4" not in s,
                "max_generations set": "max_generations = %d" % MAX_GEN in s,
                "seed set": "random_seed = %d" % sd in s,
                "symmetric intact": s.count("symmetric = 1") == 2,
            }
            bad = [k for k, v in checks.items() if not v]
            if bad:
                print("  %-13s NOT LAUNCHED -- failed: %s" % (tag, ", ".join(bad)))
                continue

            p = os.path.join(DST, tag + ".scone")
            open(p, "w", encoding="utf-8").write(s)
            with open(os.path.join(DST, "log_%s.txt" % tag), "w") as lg:
                subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=DST,
                                 stdout=lg, stderr=subprocess.STDOUT)
            n += 1
            print("  launched %-13s KV=%.3f  seed=%d  max_gen=%d" % (tag, kv, sd, MAX_GEN))

    print("\nlaunched %d matched-batch spastic runs" % n)
    print("These close blocker R10-2: after they converge, every arm in the level-ground")
    print("dataset shares max_generations=90 / min_progress=1e-7.")


if __name__ == "__main__":
    main()
