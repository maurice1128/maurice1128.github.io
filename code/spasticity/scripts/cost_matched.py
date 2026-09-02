"""Cost-matched contrast: is the separation about MECHANISM, or just about being expensive?

THE PROBLEM THIS DECIDES.
Seven candidate gait features have separated spastic from non-spastic conditions, and all seven
failed on close examination. A watchdog audit then found the reason they keep appearing: the
CMA-ES objective value ALONE separates the classes perfectly (non-spastic 0.601-0.684, spastic
0.731-1.138, no overlap), and fitness pushed through the identical classification pipeline scores
exactly what the 300-dimensional waveform scores (0.857, p = 0.143). The waveform buys nothing over
the cost function.

Mechanistically that is unsurprising: the injected reflex produces muscle activation, and muscle
activation is the EffortMeasure term in the objective. Being labelled "spastic" therefore RAISES
the objective by construction. Any waveform correlate of "this gait was expensive" will classify,
and the arms are matched on nothing.

The analogy: comparing two diseases where one group also happens to be older. A perfect biomarker
proves nothing until you match for age.

THE DESIGN.
Add conditions that fill the fitness gap so the two mechanisms OVERLAP in achieved objective value:
  - milder spasticity  (KV 0.02, 0.03)   -> expected to land near 0.65-0.73
  - heavier weakness   (70 %, 80 % loss) -> expected to land near 0.70-0.80
Then re-run the waveform classification restricted to a matched-fitness band and ask whether the
mechanisms are still separable.

  separable at matched cost  -> the difference is genuinely mechanistic; the earlier signals may be
                               real and the line is worth pursuing
  not separable              -> the seven failures share one cause: every feature was reading cost.
                               This simulation framework cannot answer the clinical question as
                               built, and the modelling of the impairment must change.

Both outcomes are decisive, which is why this is worth the compute before any further feature
search or any expansion of the condition grid.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
CM = os.path.join(HERE, "opt_costmatch")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE_OSIM = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data/H0914M_osim4.osim"
MAX_GEN = 90

# mild spastic gains, to come DOWN into the non-spastic fitness band
SPAS_GAINS = [0.02, 0.03]
# heavy weakness, to come UP into the spastic fitness band
WEAK_LEVELS = [0.70, 0.80]
SEEDS = (1, 2)


def weak_osim(frac):
    s = open(BASE_OSIM, encoding="utf-8", errors="ignore").read()
    m = re.search(r"(<Millard2012EquilibriumMuscle name=\"tib_ant_l\">)(.*?)"
                  r"(</Millard2012EquilibriumMuscle>)", s, re.S)
    body = re.sub(r"(<max_isometric_force>)([0-9.]+)",
                  lambda x: x.group(1) + ("%.4f" % (float(x.group(2)) * (1 - frac))),
                  m.group(2), count=1)
    s = s[:m.start(2)] + body + s[m.end(2):]
    name = "CMW%02d.osim" % round(frac * 100)
    open(os.path.join(CM, name), "w", encoding="utf-8").write(s)
    return name


def launch(tag, scen_text):
    p = os.path.join(CM, tag + ".scone")
    open(p, "w", encoding="utf-8").write(scen_text)
    with open(os.path.join(CM, "log_%s.txt" % tag), "w") as lg:
        subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=CM,
                         stdout=lg, stderr=subprocess.STDOUT)


def main():
    os.makedirs(CM, exist_ok=True)
    for f in (glob.glob(os.path.join(OPT, "*.osim")) + glob.glob(os.path.join(OPT, "*.zml"))
              + glob.glob(os.path.join(OPT, "*.par"))):
        dst = os.path.join(CM, os.path.basename(f))
        if not os.path.exists(dst):
            shutil.copy(f, dst)

    n = 0
    # --- milder spasticity: reuse the VERIFIED SPAS005 scenario, only the gain changes ---
    base_sp = open(os.path.join(OPT, "SPAS005.scone"), encoding="utf-8").read()
    for kv in SPAS_GAINS:
        for sd in SEEDS:
            tag = "CMS%03d_s%d" % (round(kv * 1000), sd)
            s = re.sub(r"KV = 0\.[0-9]+", "KV = %.4f" % kv, base_sp)
            s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, s, count=1)
            s = s.replace("min_progress = 1e-4",
                          "min_progress = 1e-7\n\tmax_generations = %d\n\trandom_seed = %d"
                          % (MAX_GEN, sd), 1)
            if ("KV = %.4f" % kv) not in s:            # verify before launching
                print("%-12s GAIN INJECTION FAILED" % tag)
                continue
            launch(tag, s)
            n += 1
            print("  launched %-12s KV=%.3f" % (tag, kv))

    # --- heavier weakness: plant edit only, same healthy scenario ---
    base_wk = open(os.path.join(OPT, "HEALTHY.scone"), encoding="utf-8").read()
    for frac in WEAK_LEVELS:
        om = weak_osim(frac)
        for sd in SEEDS:
            tag = "CMW%02d_s%d" % (round(frac * 100), sd)
            s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag,
                       base_wk, count=1)
            s = re.sub(r"model_file\s*=\s*\S+", "model_file = " + om, s, count=1)
            s = s.replace("min_progress = 1e-4",
                          "min_progress = 1e-7\n\tmax_generations = %d\n\trandom_seed = %d"
                          % (MAX_GEN, sd), 1)
            launch(tag, s)
            n += 1
            print("  launched %-12s TA -%.0f%%" % (tag, frac * 100))

    print("\nlaunched %d cost-matching conditions" % n)
    print("target: fill the fitness gap between non-spastic (0.601-0.684) and spastic (0.731-1.138)")
    print("then re-run waveform_classify.py restricted to the overlapping band.")


if __name__ == "__main__":
    main()
