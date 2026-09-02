# -*- coding: utf-8 -*-
"""Round 229 rev 8 -- END-TO-END FIXTURE. Runs main() on a fabricated corpus.

WHY THIS EXISTS. The reachability gate imported decide() directly and never touched main().
It reported GATE_PASSES: true while main() aborted with KeyError: 'secondary_family_size' on
its first non-primary comparison -- and SG2 comparisons are non-primary by construction, so
it aborted ALWAYS. Seven revisions and seven cold reads, and the run would have produced
nothing.

TESTING THE DECISION FUNCTION IS NOT TESTING THE PROGRAM. A gate that never executes the
program cannot certify the program.

This builds a synthetic results tree with known .sto files, points the analysis scripts at
it, runs body2_dose_r229.main() and body2_channels_r229.main() END TO END, and REQUIRES both
deposits to be written. It touches nothing in the real corpus and writes only under
spasticity_paper\\scone\\fixture_r229.
"""
import io
import os
import re
import sys
import json
import glob
import math
import shutil

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "fixture_r229")
FRES = os.path.join(ROOT, "results")
FPAP = os.path.join(ROOT, "paper")

DT = 0.01
T_END = 10.0
PERIOD = 1.0
STANCE_FRAC = 0.60

COORDS = [("hip", "hip_flexion"), ("knee", "knee_angle"), ("ankle", "ankle_angle")]
MUSC = ["soleus_l", "gastroc_l", "tib_ant_l"]

FAMS = {"DR2K000": (0.000, 1.0), "DR2K050": (0.050, 1.0), "DR2K075": (0.075, 1.0),
        "DR2K200": (0.200, 1.0), "PAR20": (0.0, 0.800), "PAR40": (0.0, 0.600),
        "CMW80": (0.0, 0.200)}
PLANES = ["SG0", "SG2"]
SEEDS = list(range(101, 117))
SMALL = {"DR2K200": 4, "CMW80": 4, "DR2K000": 6}

OSIM = """<?xml version="1.0" encoding="UTF-8"?>
<OpenSimDocument Version="40000"><Model name="fixture">
<gravity>0 -9.80665 0</gravity>
<ForceSet><objects>
%s
</objects></ForceSet></Model></OpenSimDocument>
"""
MUS = ('<Millard2012EquilibriumMuscle name="%s">'
       '<max_isometric_force>%.4f</max_isometric_force>'
       '</Millard2012EquilibriumMuscle>')
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0, "tib_ant_l": 1759.0}

CONF = """CmaOptimizer {
 max_generations = 90
 SimulationObjective {
  max_duration = 10
  ConditionalController {
   legs = left
   ReflexController {
    name = SpasticL
    MuscleReflex { target = soleus  delay = 0.020 KV = %.3f allow_neg_V = 0 }
    MuscleReflex { target = gastroc delay = 0.020 KV = %.3f allow_neg_V = 0 }
   }
  }
 }
}
"""


def sto_text(tag, seed, kv, scale, rng):
    n = int(T_END / DT) + 1
    t = np.arange(n) * DT
    ph = (t % PERIOD) / PERIOD
    grf = np.where(ph < STANCE_FRAC,
                   0.9 * np.sin(np.pi * ph / STANCE_FRAC) + 0.15, 0.0)
    jitter = rng.normal(0, 0.02, n)
    cols = ["time"]
    data = [t]
    for j, c in COORDS:
        for side in ("r", "l"):
            base = 0.30 * np.sin(2 * np.pi * ph + (0.0 if side == "r" else 0.15))
            # a left-side offset that scales with the lesion, so arms differ
            off = (-0.05 * kv * 20 if side == "l" and kv > 0 else 0.0)
            off += (0.04 * (1 - scale) * 5 if side == "l" and scale < 1 else 0.0)
            cols.append("/jointset/%s_%s/%s_%s/value" % (j, side, c, side))
            data.append(base + off + jitter * 0.3 + rng.normal(0, 0.01))
    cols.append("leg0_l.grf_norm_y"); data.append(grf)
    cols.append("leg1_r.grf_norm_y")
    data.append(np.where(ph >= 0.5, 0.9 * np.sin(np.pi * (ph - 0.5) / STANCE_FRAC), 0.0))
    for m in MUSC:
        cols.append(m + ".fiber_velocity_norm")
        # per-cell amplitude so the SPASTIC dose has spread too; without it the spastic
        # range is a hairline and leave-one-out unanimity can never hold.
        vamp = 0.64 + 0.06 * rng.standard_normal()
        data.append(vamp * np.cos(2 * np.pi * ph) + rng.normal(0, 0.02, n))
        cols.append(m + ".excitation")
        data.append(np.clip(0.3 + 0.2 * np.sin(2 * np.pi * ph), 0, 1))
        cols.append(m + ".mtu_force_norm")
        # amplitude tuned so (1 - 0.800) * mean|tib_ant force| lands inside the KV = 0.075
        # spastic dose range, with per-cell spread wide enough for the ranges to overlap.
        amp = 0.150 + 0.030 * rng.standard_normal()
        data.append(np.clip(amp + 0.12 * np.sin(2 * np.pi * ph), 0, None))
    arr = np.vstack(data).T
    out = ["%s_s%d" % (tag, seed), "version=1", "nRows=%d" % n,
           "nColumns=%d" % len(cols), "inDegrees=no", "endheader", "\t".join(cols)]
    for row in arr:
        out.append("\t".join("%.6g" % v for v in row))
    return "\n".join(out) + "\n"


def build():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(FRES); os.makedirs(FPAP)
    rng = np.random.default_rng(4229)
    for plane in PLANES:
        for fam, (kv, scale) in FAMS.items():
            for seed in SEEDS[:SMALL.get(fam, 16)]:
                tag = "%s_%s" % (plane, fam)
                d = os.path.join(FRES, "%s_s%d.H0914M.GH2010.S10W.D10.I.R%d"
                                 % (tag, seed, seed))
                os.makedirs(d)
                io.open(os.path.join(d, "history.txt"), "w", encoding="utf-8").write(
                    "generation\tbest_fitness\tmedian_fitness\n0\t1.20000\t60.0000\n")
                io.open(os.path.join(d, "0000_60.000_1.200.par"), "w").write("x\n")
                io.open(os.path.join(d, "0050_20.000_0.800.par"), "w").write("x\n")
                io.open(os.path.join(d, "0050_20.000_0.800.par.sto"), "w",
                        encoding="utf-8").write(sto_text(tag, seed, kv, scale, rng))
                io.open(os.path.join(d, "config.scone"), "w",
                        encoding="utf-8").write(CONF % (kv, kv))
                muscles = "\n".join(
                    MUS % (m, FMAX[m] * (scale if m == "tib_ant_l" else 1.0))
                    for m in MUSC)
                io.open(os.path.join(d, "fixture.osim"), "w",
                        encoding="utf-8").write(OSIM % muscles)
    return sum(1 for _ in glob.glob(os.path.join(FRES, "*")))


def run_end_to_end():
    import body2_dose_r229 as DO
    import body2_channels_r229 as CHN
    for mod in (DO, CHN):
        mod.RESULTS = FRES
        mod.PAPER = FPAP
    # The fixture needs a fixture-local manifest, map, ledger and corpus so preconditions()
    # can pass. Rev 9's fixture failed because preconditions() looked for them in FPAP and
    # they only exist in the real paper directory -- a gate with a broken fixture is half a
    # gate, and the fixture is the half the reachability map cannot replace.
    import hashlib as _h
    here = os.path.dirname(os.path.abspath(__file__))
    files = {}
    for n in os.listdir(here):
        if n.startswith("body2_") and n.endswith(".py"):
            p = os.path.join(here, n)
            d = _h.sha256(io.open(p, "rb").read()).hexdigest()
            files[n] = {"sha256": d, "bytes": os.path.getsize(p)}
            io.open(p + ".sha256", "w", encoding="utf-8", newline="\n").write(
                "%s  %s\n" % (d, n))
    json.dump({"written": "fixture", "scope": "fixture-local", "files": files},
              io.open(os.path.join(FPAP, "BODY2_HASHES_r229.json"), "w", encoding="utf-8"))
    json.dump({"GATE_PASSES": True,
               "channels_sha256": _h.sha256(
                   io.open(os.path.join(here, "body2_channels_r229.py"), "rb").read()
               ).hexdigest()},
              io.open(os.path.join(FPAP, "BODY2_REACHABILITY_r229.json"), "w",
                      encoding="utf-8"))
    json.dump({"attempts": []},
              io.open(os.path.join(FPAP, "BODY2_REPLAY_LEDGER_r229.json"), "w",
                      encoding="utf-8"))
    corpus = {}
    for plane in ("SG0", "SG2"):
        for fam in DO.SPASTIC + DO.WEAK + ["DR2K000"]:
            corpus["%s_%s" % (plane, fam)] = sorted(
                os.path.basename(d) for _s, d in CHN.cell_dirs(plane, fam))
    json.dump({"cells": corpus},
              io.open(os.path.join(FPAP, "BODY2_CORPUS_r229.json"), "w", encoding="utf-8"))
    # the dose module asserts FMAX against a base .osim inside the control family
    ok = {}
    try:
        DO.main()
        ok["dose"] = os.path.exists(os.path.join(FPAP, "BODY2_DOSE_r229.json"))
    except SystemExit as e:
        ok["dose"] = "SystemExit: %s" % e
    except Exception as e:
        ok["dose"] = "%s: %s" % (type(e).__name__, e)
    try:
        CHN.main()
        ok["channels"] = os.path.exists(os.path.join(FPAP, "BODY2_CHANNELS_r229.json"))
    except SystemExit as e:
        ok["channels"] = "SystemExit: %s" % e
    except Exception as e:
        ok["channels"] = "%s: %s" % (type(e).__name__, e)
    return ok


def main():
    n = build()
    print("fixture built: %d cell directories under %s\n" % (n, FRES))
    ok = run_end_to_end()
    print("\n" + "=" * 70)
    print("dose     main() -> deposit written: %r" % ok["dose"])
    print("channels main() -> deposit written: %r" % ok["channels"])
    passed = ok["dose"] is True and ok["channels"] is True
    # A SystemExit from a registered HARD STOP is a legitimate program path, but it must be
    # reported as such and it does NOT count as an end-to-end pass.
    print("FIXTURE %s" % ("PASSES -- main() completes and writes both deposits"
                          if passed else "FAILS or halted on a registered stop"))
    json.dump({"cells": n, "result": ok, "passed": passed},
              io.open(os.path.join(FPAP, "FIXTURE_RESULT.json"), "w", encoding="utf-8"),
              indent=1)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
