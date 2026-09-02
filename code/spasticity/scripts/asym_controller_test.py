"""Does the inter-limb signal survive an ASYMMETRIC controller — and does it become lateralized?

The retracted V5 claim rested on affected-minus-intact ankle ROM. Council round 6 showed that
under `symmetric = 1` up to 97 % of that difference came from the INTACT limb moving away from
normal, because a shared-parameter control law applies the adaptation forced by the impaired limb
identically to the sound limb. That makes the "within-subject control limb" premise false.

`symmetric = 0` gives the controller independent per-limb parameters (dim 65 vs 36), so it CAN
tune the affected limb against the reflex and leave the sound limb near its healthy optimum.
Two outcomes, both informative:

  * intact limb returns to ~healthy and the affected limb carries the change
        -> the signal is genuinely lateralized; V5's core objection is answered
  * intact limb still moves, or the difference vanishes
        -> the asymmetry was an artifact of parameter sharing; V5 dies conclusively

Baselines are matched WITHIN controller type: symmetric=0 conditions are compared against the
symmetric=0 healthy runs, never against the symmetric=1 healthy runs.
"""
import glob
import json
import os
import subprocess
import sys
from math import sqrt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import cycle_features  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
CONVERGED = 3.0
#: Depth cap, for the same reason as every other analysis script here: selecting each run's
#: global best .par compares arms at whatever depth they happened to reach, which is the confound
#: that invalidated three earlier versions of this claim.
GEN_CAP = 90

ASYM = {"BHEALTHY_s1": "HEALTHY", "BHEALTHY_s2": "HEALTHY",
        "BSPAS005_s1": "SPAS005", "BSPAS005_s2": "SPAS005",
        "BSPAS01_s1": "SPAS01", "BSPAS01_s2": "SPAS01",
        "BPAR60_s1": "PAR60", "BPAR60_s2": "PAR60"}


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


def ms(a):
    m = sum(a) / len(a)
    return m, (sqrt(sum((x - m) ** 2 for x in a) / (len(a) - 1)) if len(a) > 1 else 0.0)


def main():
    out = {}
    for tag, cond in ASYM.items():
        par, fit, gen = best_par(tag)
        if par is None or fit >= CONVERGED:
            print("%-13s %-8s SKIP (fit=%s)" % (tag, cond, fit))
            continue
        d = os.path.dirname(par)
        for old in glob.glob(os.path.join(d, "*.sto")):
            os.remove(old)
        try:
            subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=900)
        except Exception:
            print("%-13s replay timeout" % tag)
            continue
        s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(s) != 1:
            print("%-13s %d sto" % (tag, len(s)))
            continue
        L, R = cycle_features(s[0], side="l"), cycle_features(s[0], side="r")
        if L is None or R is None:
            print("%-13s no cycles" % tag)
            continue
        out[tag] = {"cond": cond, "fitness": fit, "gen": gen, "l": L, "r": R}
        print("%-13s %-8s gen=%-3d fit=%.3f  L_rom=%5.2f R_rom=%5.2f  L-R=%+6.2f  L_vel=%6.1f"
              % (tag, cond, gen, fit, L["ank_rom"], R["ank_rom"],
                 L["ank_rom"] - R["ank_rom"], L["ank_vel_max"]))

    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "scone_asym_controller.json"), "w"), indent=2)

    heal = [v for v in out.values() if v["cond"] == "HEALTHY"]
    if not heal:
        print("\nno asymmetric-controller healthy baseline yet")
        return
    hl, _ = ms([h["l"]["ank_rom"] for h in heal])
    hr, _ = ms([h["r"]["ank_rom"] for h in heal])
    print("\nsymmetric=0 healthy baseline: L %.2f  R %.2f  (n=%d)" % (hl, hr, len(heal)))
    print("\n%-13s %-10s %-10s %-9s %-22s" %
          ("run", "d_affected", "d_intact", "asym", "share of asym from INTACT"))
    for tag, v in sorted(out.items()):
        if v["cond"] == "HEALTHY":
            continue
        da = v["l"]["ank_rom"] - hl
        di = v["r"]["ank_rom"] - hr
        asym = v["l"]["ank_rom"] - v["r"]["ank_rom"]
        denom = abs(da) + abs(di)
        share = 100.0 * abs(di) / denom if denom else float("nan")
        print("%-13s %+9.2f %+10.2f %+9.2f   %5.1f %%   %s"
              % (tag, da, di, asym, share,
                 "<- signal is on the INTACT limb" if share > 50 else ""))
    print("\nReference: under symmetric=1 the intact-limb share was 28-97 % "
          "(SPAS01_s3 = 97 %, its affected ankle indistinguishable from healthy).")


if __name__ == "__main__":
    main()
