"""Find the impairment severity at which an UN-ADAPTED controller can still walk.

The naive-vs-adapted contrast could not be run at the severities used so far: with the controller
frozen at the healthy optimum, every impaired condition (40/60 % weakness, KV 0.05/0.10) fell.
That is itself informative -- those impairments require adaptation to walk at all -- but it also
means the severities are unrealistic for the comparison we want, because real acute stroke patients
DO walk, badly, before they have compensated.

So sweep severity downward until the frozen healthy controller still produces a gait, separately
for each mechanism. The output is two things:

  1. the "walkable-without-adaptation" ceiling for each mechanism -- a mechanistic result in its own
     right, and a fair way to match the two arms on functional severity rather than on arbitrary
     parameter values (weakness fraction and reflex gain are not on a common scale)
  2. at those severities, the naive-vs-adapted contrast that tests whether adaptation erases the
     diagnosis

Note this also addresses a standing criticism: weakness (TA force x 0.8/0.6/0.4) and spasticity
(KV 0.05/0.10) have no common severity scale, so every between-arm comparison so far has been
confounded with functional severity. "Steepest impairment still walkable un-adapted" is a common
anchor derived from the model rather than assumed.
"""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import cycle_features  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
NL = os.path.join(HERE, "opt_naive_ladder")
BASE_OSIM = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data/H0914M_osim4.osim"

WEAK_LADDER = [0.30, 0.20, 0.15, 0.10, 0.05]      # fraction of TA force removed
KV_LADDER = [0.04, 0.03, 0.02, 0.01, 0.005]       # reflex gain


def best_par(tag, gen_cap=90):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, 1e9
    d = max(ds, key=os.path.getmtime)
    bp, bf = None, 1e9
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            g, f = int(b[0]), float(b[2])
        except Exception:
            continue
        if g > gen_cap:
            continue
        if f < bf:
            bp, bf = p, f
    return bp, bf


def weak_osim(frac):
    s = open(BASE_OSIM, encoding="utf-8", errors="ignore").read()
    m = re.search(r"(<Millard2012EquilibriumMuscle name=\"tib_ant_l\">)(.*?)"
                  r"(</Millard2012EquilibriumMuscle>)", s, re.S)
    body = re.sub(r"(<max_isometric_force>)([0-9.]+)",
                  lambda x: x.group(1) + ("%.4f" % (float(x.group(2)) * (1 - frac))),
                  m.group(2), count=1)
    s = s[:m.start(2)] + body + s[m.end(2):]
    name = "NW%03d.osim" % round(frac * 100)
    open(os.path.join(NL, name), "w", encoding="utf-8").write(s)
    return name


def run_naive(tag, src_scone, model_file=None, kv=None):
    s = open(src_scone, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, s, count=1)
    s = re.sub(r"init_file\s*=\s*\S+", "init_file = healthy_frozen.par", s, count=1)
    if model_file:
        s = re.sub(r"model_file\s*=\s*\S+", "model_file = " + model_file, s, count=1)
    if kv is not None:
        s = re.sub(r"KV = 0\.[0-9]+", "KV = %.4f" % kv, s)
    p = os.path.join(NL, tag + ".scone")
    open(p, "w", encoding="utf-8").write(s)
    for old in glob.glob(os.path.join(NL, "*.sto")):
        os.remove(old)
    try:
        subprocess.run([SCONECMD, "-e", p], cwd=NL, capture_output=True, timeout=600)
    except Exception:
        return None
    sto = [x for x in glob.glob(os.path.join(NL, "*.sto")) if os.path.getsize(x) > 1000]
    if len(sto) != 1:
        return None
    L, R = cycle_features(sto[0], side="l"), cycle_features(sto[0], side="r")
    return {"l": L, "r": R} if (L and R) else None


def main():
    os.makedirs(NL, exist_ok=True)
    for f in glob.glob(os.path.join(OPT, "*.osim")) + glob.glob(os.path.join(OPT, "*.zml")):
        dst = os.path.join(NL, os.path.basename(f))
        if not os.path.exists(dst):
            open(dst, "wb").write(open(f, "rb").read())
    hp, hf = best_par("DHEALTHY_s1")
    open(os.path.join(NL, "healthy_frozen.par"), "wb").write(open(hp, "rb").read())
    print("frozen healthy controller fitness %.3f\n" % hf)

    out = {"weak": {}, "spas": {}}

    print("--- WEAKNESS: how much TA loss can a frozen healthy controller tolerate? ---")
    for frac in WEAK_LADDER:
        om = weak_osim(frac)
        r = run_naive("NLW%03d" % round(frac * 100), os.path.join(OPT, "HEALTHY.scone"),
                      model_file=om)
        ok = r is not None
        out["weak"]["%.2f" % frac] = r and {"rom": r["l"]["ank_rom"],
                                            "vel": r["l"]["ank_vel_max"],
                                            "lr": r["l"]["ank_rom"] - r["r"]["ank_rom"]}
        print("  TA -%2.0f%%  %s" % (frac * 100,
              ("rom %5.2f  vel %6.1f  L-R %+6.2f" % (r["l"]["ank_rom"], r["l"]["ank_vel_max"],
               r["l"]["ank_rom"] - r["r"]["ank_rom"])) if ok else "FELL"))
        if ok:
            break

    print("\n--- SPASTICITY: how much reflex gain can it tolerate? ---")
    for kv in KV_LADDER:
        r = run_naive("NLS%03d" % round(kv * 1000), os.path.join(OPT, "SPAS005.scone"), kv=kv)
        ok = r is not None
        out["spas"]["%.4f" % kv] = r and {"rom": r["l"]["ank_rom"],
                                          "vel": r["l"]["ank_vel_max"],
                                          "lr": r["l"]["ank_rom"] - r["r"]["ank_rom"]}
        print("  KV %.3f  %s" % (kv,
              ("rom %5.2f  vel %6.1f  L-R %+6.2f" % (r["l"]["ank_rom"], r["l"]["ank_vel_max"],
               r["l"]["ank_rom"] - r["r"]["ank_rom"])) if ok else "FELL"))
        if ok:
            break

    json.dump(out, open(os.path.join(HERE, "scone_naive_ladder.json"), "w"), indent=2)
    w = [k for k, v in out["weak"].items() if v]
    s = [k for k, v in out["spas"].items() if v]
    print("\nwalkable un-adapted: weakness up to TA -%s ; spasticity up to KV %s"
          % (w[0] if w else "NONE", s[0] if s else "NONE"))


if __name__ == "__main__":
    main()
