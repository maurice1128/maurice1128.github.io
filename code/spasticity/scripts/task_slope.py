"""Cross-task response: does ankle behaviour change DIFFERENTLY with task demand for
spasticity vs weakness?

Rationale. Spasticity is defined by velocity dependence, so the discriminating quantity should
not be a static feature at one walking condition -- it should be how the ankle responds as the
task raises dorsiflexion-velocity demand. That is what the Tardieu test does (compare R1 at fast
stretch with R2 at slow). A slope across tasks is also computed WITHIN a subject, so systematic
measurement bias partly cancels -- unlike the absolute inter-limb margin (1.25 deg) that sits
3-9x below post-stroke ankle MDC.

Prediction under test:
  spastic  -> response degrades NON-linearly as the task demands faster dorsiflexion (reflex fires)
  weakness -> response degrades roughly linearly with task difficulty (force deficit, velocity-independent)

Tasks available: level ground and 2 deg downhill (uphill pending).
Everything is replayed with the CORRECTED heel_strikes (minimum stance duration), and BOTH limbs
are reported, because the retracted V5 claim turned out to be driven by the unlesioned limb.
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import cycle_features  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"

# tag -> (task, condition)
RUNS = {
    # level ground (depth-matched weakness arm + spastic + the newly converged mixed)
    "DHEALTHY_s1": ("level", "HEALTHY"), "DHEALTHY_s2": ("level", "HEALTHY"),
    "DHEALTHY_s3": ("level", "HEALTHY"),
    "DPAR40_s1": ("level", "PAR40"), "DPAR40_s2": ("level", "PAR40"),
    "DPAR40_s3": ("level", "PAR40"),
    "DPAR60_s1": ("level", "PAR60"), "DPAR60_s2": ("level", "PAR60"),
    "DPAR60_s3": ("level", "PAR60"),
    "SPAS005": ("level", "SPAS005"), "SPAS005_s2": ("level", "SPAS005"),
    "SPAS005_s3": ("level", "SPAS005"), "SPAS005_s4": ("level", "SPAS005"),
    "SPAS01": ("level", "SPAS01"), "SPAS01_s2": ("level", "SPAS01"),
    "SPAS01_s3": ("level", "SPAS01"), "SPAS01_s4": ("level", "SPAS01"),
    "DPAR20_s1": ("level", "PAR20"), "DPAR20_s2": ("level", "PAR20"),
    "DPAR20_s3": ("level", "PAR20"),
    # Mixed reached fitness 1.08/1.18 at generation 79-86 -- ~1.8x the healthy cost (0.60), so it
    # is admitted here as a candidate only. Gait validity (complete cycles, duty factor) is checked
    # on replay below; it is NOT yet described as converged.
    "MMIX20S01_s1": ("level", "MIX20S01"), "MMIX20S01_s2": ("level", "MIX20S01"),
    # 2 deg downhill
    "D2HEALTHY": ("down2", "HEALTHY"), "D2PAR40": ("down2", "PAR40"),
    "D2PAR60": ("down2", "PAR60"),
    "E2SPAS005": ("down2", "SPAS005"), "E2SPAS01": ("down2", "SPAS01"),
    "E2MIX40S01": ("down2", "MIX40S01"),
}


#: Hard depth cap. Selecting each run's global best .par re-imports the exact confound that
#: invalidated three previous versions of this claim: the spastic runs keep optimizing (their best
#: .par sits at generation 242-337) while the weakness arm was capped at max_generations = 90, so
#: an uncapped "best" comparison is a ~3.4x depth mismatch, not a pathology comparison. Every arm
#: is therefore compared at its best .par AT OR BELOW a common generation. Set to None only after
#: the weakness arm has actually been extended to matching depth.
GEN_CAP = 90


def best_par(tag, gen_cap=GEN_CAP):
    """Best .par at or below `gen_cap` generations, so arms are compared at common depth."""
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None, None
    d = max(ds, key=os.path.getmtime)
    best, bf, bg = None, 1e9, None
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            g, f = int(b[0]), float(b[2])
        except Exception:
            continue
        if gen_cap is not None and g > gen_cap:
            continue
        if f < bf:
            best, bf, bg = p, f, g
    return best, bf, bg


def main():
    out = {}
    for tag, (task, cond) in RUNS.items():
        par, fit, gen = best_par(tag)
        if par is None or fit >= 3.0:
            out[tag] = {"status": "unconverged", "fitness": fit, "task": task, "cond": cond}
            print("%-14s %-7s %-9s SKIP (fit=%s)" % (tag, task, cond, fit))
            continue
        d = os.path.dirname(par)
        for old in glob.glob(os.path.join(d, "*.sto")):
            os.remove(old)          # guarantee the .sto matches the .par we name
        try:
            subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=900)
        except Exception:
            out[tag] = {"status": "timeout", "task": task, "cond": cond}
            continue
        s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(s) != 1:
            out[tag] = {"status": "sto_%d" % len(s), "task": task, "cond": cond}
            continue
        L = cycle_features(s[0], side="l")
        R = cycle_features(s[0], side="r")
        if L is None:
            out[tag] = {"status": "no_cycles", "task": task, "cond": cond}
            print("%-14s %-7s %-9s no cycles" % (tag, task, cond))
            continue
        out[tag] = {"status": "ok", "task": task, "cond": cond, "fitness": fit,
                    "gen": gen, "l": L, "r": R}
        print("%-14s %-7s %-9s gen=%-4d fit=%.3f  L_rom=%5.2f L_vel=%6.1f  L-R=%+6.2f"
              % (tag, task, cond, gen, fit, L["ank_rom"], L["ank_vel_max"],
                 L["ank_rom"] - R["ank_rom"]))
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "scone_tasks.json"), "w"), indent=2)
    ok = sum(1 for v in out.values() if v.get("status") == "ok")
    print("\nok %d / %d -> scone_tasks.json" % (ok, len(RUNS)))


if __name__ == "__main__":
    main()
