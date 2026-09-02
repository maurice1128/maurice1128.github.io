"""THE DECISIVE CONTRAST: does adaptation erase the diagnosis?

Every discriminator this project has tried was measured in a gait whose controller had been
RE-OPTIMIZED with the impairment in place. Five candidate features, five failures, and the failures
share a structure: each was sensitive to optimization depth, seed, or the controller's
parameterization -- properties of the OPTIMIZER, not of the impairment. That is what a many-to-one
map looks like: re-optimization minimizes the SAME cost functional in every arm, so impairments
that bind the same bottleneck (both weakness and a plantarflexor velocity reflex make dorsiflexion
expensive) are pulled toward the same accommodation, and the label is destroyed by construction.

So run the contrast that isolates it:

    NAIVE   controller frozen at the HEALTHY optimum, impairment imposed, no re-optimization
            -> clinically: acute, before compensation is learned
    ADAPTED controller re-optimized with the impairment in place (what we already have)
            -> clinically: chronic, compensated

If a discriminator exists NAIVE and vanishes ADAPTED, the result is not "gait cannot distinguish
them" but "ADAPTATION ERASES THE DISTINCTION" -- a positive, mechanistic, testable finding with a
direct clinical corollary (assess early; the signature decays as the patient compensates).

If it is absent in BOTH, the many-to-one hypothesis is wrong and the impairments genuinely are
kinematically degenerate in this model -- also a clean answer, and a stronger negative than
anything obtained so far.

Only the naive arm is computed here; the adapted arm is read from existing converged runs. The
naive arm needs no optimization at all -- it is one replay per condition -- so this is cheap.
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
NAIVE = os.path.join(HERE, "opt_naive")
GEN_CAP = 90

# condition -> (source scenario carrying the impairment, adapted run tag for comparison)
CONDS = {
    "HEALTHY": ("HEALTHY.scone", "DHEALTHY_s1"),
    "PAR40": ("PAR40.scone", "DPAR40_s1"),
    "PAR60": ("PAR60.scone", "DPAR60_s1"),
    "SPAS005": ("SPAS005.scone", "SPAS005"),
    "SPAS01": ("SPAS01.scone", "SPAS01"),
}


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


def main():
    os.makedirs(NAIVE, exist_ok=True)
    for f in (glob.glob(os.path.join(OPT, "*.osim")) + glob.glob(os.path.join(OPT, "*.zml"))):
        dst = os.path.join(NAIVE, os.path.basename(f))
        if not os.path.exists(dst):
            open(dst, "wb").write(open(f, "rb").read())

    # the frozen healthy controller every naive condition will use
    hp, hf, hg = best_par("DHEALTHY_s1")
    if hp is None:
        print("no converged healthy controller to freeze")
        return
    open(os.path.join(NAIVE, "healthy_frozen.par"), "wb").write(open(hp, "rb").read())
    print("frozen healthy controller: fitness %.3f (gen %d)\n" % (hf, hg))

    out = {}
    print("%-9s %-26s %-26s" % ("cond", "NAIVE (frozen healthy ctrl)", "ADAPTED (re-optimized)"))
    for cond, (scen_name, adapted_tag) in CONDS.items():
        src = os.path.join(OPT, scen_name)
        if not os.path.exists(src):
            print("%-9s missing %s" % (cond, scen_name))
            continue
        s = open(src, encoding="utf-8", errors="ignore").read()
        s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = N_" + cond, s, count=1)
        s = re.sub(r"init_file\s*=\s*\S+", "init_file = healthy_frozen.par", s, count=1)
        p = os.path.join(NAIVE, "N_%s.scone" % cond)
        open(p, "w", encoding="utf-8").write(s)

        for old in glob.glob(os.path.join(NAIVE, "*.sto")):
            os.remove(old)
        try:
            # -e evaluates the init_file controller AS IS: no optimization, no adaptation
            subprocess.run([SCONECMD, "-e", p], cwd=NAIVE, capture_output=True, timeout=600)
        except Exception:
            print("%-9s naive replay timeout" % cond)
            continue
        sto = [x for x in glob.glob(os.path.join(NAIVE, "*.sto")) if os.path.getsize(x) > 1000]
        nv = None
        if len(sto) == 1:
            L, R = cycle_features(sto[0], side="l"), cycle_features(sto[0], side="r")
            if L and R:
                nv = {"l": L, "r": R}

        ap, af, ag = best_par(adapted_tag)
        ad = None
        if ap is not None and af < 3.0:
            d = os.path.dirname(ap)
            for old in glob.glob(os.path.join(d, "*.sto")):
                os.remove(old)
            try:
                subprocess.run([SCONECMD, "-e", ap], cwd=d, capture_output=True, timeout=600)
                s2 = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
                if len(s2) == 1:
                    L2, R2 = cycle_features(s2[0], side="l"), cycle_features(s2[0], side="r")
                    if L2 and R2:
                        ad = {"l": L2, "r": R2, "gen": ag, "fitness": af}
            except Exception:
                pass

        out[cond] = {"naive": nv, "adapted": ad}
        def fmt(x):
            if not x:
                return "%-26s" % "FELL / no cycles"
            return "rom %5.2f vel %6.1f L-R%+6.2f" % (
                x["l"]["ank_rom"], x["l"]["ank_vel_max"],
                x["l"]["ank_rom"] - x["r"]["ank_rom"])
        print("%-9s %-26s %-26s" % (cond, fmt(nv), fmt(ad)))

    json.dump(out, open(os.path.join(HERE, "scone_naive_vs_adapted.json"), "w"), indent=2)

    print("\n--- separation in each arm (affected ankle ROM) ---")
    for arm in ("naive", "adapted"):
        vals = {c: v[arm]["l"]["ank_rom"] for c, v in out.items() if v.get(arm)}
        if len(vals) < 3:
            print("  %-8s insufficient data" % arm)
            continue
        sp = [v for c, v in vals.items() if c.startswith("SPAS")]
        wk = [v for c, v in vals.items() if not c.startswith("SPAS")]
        if sp and wk:
            gap = min(wk) - max(sp)
            print("  %-8s spastic %.2f-%.2f | non-spastic %.2f-%.2f | gap %+.2f %s"
                  % (arm, min(sp), max(sp), min(wk), max(wk), gap,
                     "SEPARATED" if gap > 0 else "overlap"))
    print("\nIf NAIVE separates and ADAPTED does not, the finding is: adaptation erases the "
          "diagnosis (assess early).")


if __name__ == "__main__":
    main()
