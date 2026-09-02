"""The control that breaks the circularity: activation-matched TONIC hypertonia.

THE PROBLEM THIS SOLVES.
In the forward arm the injected reflex produces muscle ACTIVATION, and muscle activation IS the
effort term in the objective (`EffortMeasure { Wang2012 }`). So when the re-optimized controller
reduces ankle angular velocity, two explanations are indistinguishable:

  (A) the reflex is VELOCITY-dependent, so the controller learns not to lengthen the muscle fast
      -- the mechanism we want to demonstrate
  (B) the reflex merely adds an activation cost, and any added cost makes the optimizer reduce
      whatever triggers it -- a property of the cost function, not of velocity dependence

Adversarial review (round 8) correctly judged the current design unable to separate these, which
makes the velocity-suppression result close to a theorem rather than a finding.

THE CONTROL.
Add a TONIC (velocity-independent) excitation to the same muscles, tuned so its mean activation
matches the spastic condition's. Both arms then carry the same activation cost; the only remaining
difference is whether that activation is gated on stretch velocity.

  spastic  != tonic-matched  ->  the difference IS velocity dependence; (B) is excluded
  spastic  ~= tonic-matched  ->  the effect is the activation cost; the finding is an artifact

This also supplies the third arm of the clinical differential that has been missing throughout:
tonic hypertonia is clinically close to contracture, and separating it from velocity-dependent
spasticity is exactly what the Tardieu R1/R2 manoeuvre attempts.

Procedure: measure mean soleus/gastroc activation in the converged spastic runs, build a tonic
scenario whose constant excitation reproduces it, re-optimize under the same budget, replay, and
compare the features on which the spastic arm currently appears to separate.
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
TON = os.path.join(HERE, "opt_tonic")
GEN_CAP = 90
MAX_GEN = 90


def best_par(tag, gen_cap=GEN_CAP):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, 1e9, None
    d = max(ds, key=os.path.getmtime)
    bp, bf, bg = None, 1e9, None
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            g, f = int(b[0]), float(b[2])
        except Exception:
            continue
        if gen_cap is not None and g > gen_cap:
            continue
        if f < bf:
            bp, bf, bg = p, f, g
    return bp, bf, bg


def mean_activation(tag, muscles=("soleus", "gastroc"), side="l"):
    """Cycle-averaged activation of the injected muscles in a converged run."""
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None
    d = max(ds, key=os.path.getmtime)
    s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
    if not s:
        return None
    cols, dd = load_sto(max(s, key=os.path.getmtime))
    if dd.size == 0:
        return None
    t = dd[:, 0]
    grf, thr = grf_vertical(cols, dd, side)
    if grf is None:
        return None
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
    if len(hs) < 3:
        return None
    a0, b0 = hs[0], hs[-1]
    vals = []
    for m in muscles:
        a = muscle_signal(cols, dd, m, side, "activation")
        if a is None:
            return None
        vals.append(float(np.mean(a[a0:b0])))
    return float(np.mean(vals))


def build_tonic(tag, level):
    """Same base scenario, but the injected reflex replaced by a constant excitation."""
    src = os.path.join(OPT, "SPAS005.scone")
    s = open(src, encoding="utf-8", errors="ignore").read()
    # replace the velocity-gated MuscleReflex block with a constant offset on the same muscles
    s = re.sub(r"MuscleReflex\s*\{[^{}]*target\s*=\s*soleus_l[^{}]*\}",
               "MuscleReflex { target = soleus_l delay = 0.020 C0 = %.4f }" % level, s)
    s = re.sub(r"MuscleReflex\s*\{[^{}]*target\s*=\s*gastroc_l[^{}]*\}",
               "MuscleReflex { target = gastroc_l delay = 0.020 C0 = %.4f }" % level, s)
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, s, count=1)
    s = s.replace("min_progress = 1e-4",
                  "min_progress = 1e-7\n\tmax_generations = %d" % MAX_GEN, 1)
    p = os.path.join(TON, tag + ".scone")
    open(p, "w", encoding="utf-8").write(s)
    return p


def main():
    os.makedirs(TON, exist_ok=True)
    for f in (glob.glob(os.path.join(OPT, "*.osim")) + glob.glob(os.path.join(OPT, "*.zml"))
              + glob.glob(os.path.join(OPT, "*.par"))):
        dst = os.path.join(TON, os.path.basename(f))
        if not os.path.exists(dst):
            open(dst, "wb").write(open(f, "rb").read())

    # Match the ADDED activation, not the total. The spastic run's mean activation already
    # contains the baseline drive the healthy controller produces; imposing the total as a
    # constant offset doubles it and the model cannot walk (first attempt: fitness 90-96).
    base = mean_activation("DHEALTHY_s1")
    if base is None:
        print("no healthy baseline activation")
        return
    print("healthy baseline activation = %.4f\n" % base)
    targets = {}
    for src_tag, label in (("SPAS005", "TON005"), ("SPAS01", "TON01")):
        tot = mean_activation(src_tag)
        if tot is None:
            print("%-9s could not measure activation" % src_tag)
            continue
        a = max(tot - base, 0.0)
        targets[label] = (src_tag, a)
        print("%-9s mean soleus/gastroc activation = %.4f -> tonic target %s"
              % (src_tag, a, label))

    launched = 0
    for label, (src_tag, a) in targets.items():
        for seed in (1, 2):
            tag = "%s_s%d" % (label, seed)
            p = build_tonic(tag, a)
            txt = open(p, encoding="utf-8").read()
            if "C0 = " not in txt:
                print("%-11s INJECTION FAILED - not launching" % tag)
                continue
            txt = txt.replace("min_progress = 1e-7",
                              "min_progress = 1e-7\n\trandom_seed = %d" % seed, 1)
            txt = re.sub(r"signature_prefix\s*=\s*\S+",
                         "signature_prefix = " + tag, txt, count=1)
            open(p, "w", encoding="utf-8").write(txt)
            with open(os.path.join(TON, "log_%s.txt" % tag), "w") as lg:
                subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=TON,
                                 stdout=lg, stderr=subprocess.STDOUT)
            launched += 1
            print("  launched %s (tonic level %.4f, matched to %s)" % (tag, a, src_tag))

    json.dump({k: {"source": v[0], "activation": v[1]} for k, v in targets.items()},
              open(os.path.join(HERE, "tonic_targets.json"), "w"), indent=2)
    print("\nlaunched %d activation-matched tonic runs" % launched)
    print("When converged: compare foot-slap velocity and swing activation against the SPASTIC")
    print("arm. If they match, the effect is the activation cost, not velocity dependence.")


if __name__ == "__main__":
    main()
