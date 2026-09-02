"""Does the optimizer's objective value identify the MECHANISM, or only the severity?

WHY THIS EXISTS.
Seven hand-picked gait features separated spastic from non-spastic conditions and all seven died
on inspection. A watchdog audit then found why they kept reappearing: the CMA-ES objective value
ALONE separated the two classes perfectly (non-spastic 0.601-0.684, spastic 0.731-1.138, no
overlap), and fitness pushed through the identical classification pipeline scored exactly what the
300-dimensional waveform scored. Every feature was a proxy for "this gait was expensive".

That perfect separation had an obvious alternative explanation that the grid could not distinguish:
the objective is a metabolic-cost term, so it tracks HOW BAD the gait is. If the weakness arm
happened to be mild and the spastic arm happened to be severe, the classes separate on severity and
the mechanism label rides along for free.

THE TEST.
Extend each arm along its own severity axis until the ranges are forced to interleave:
  weakness   -70 %, -80 % tibialis anterior  (heavier than the -20/-40/-60 already run)
  spasticity KV 0.02, 0.03                   (milder than the 0.05/0.10 already run)
Nothing else changes -- same model, same warm start, same objective, and the same stopping rule
(max_generations = 90, min_progress = 1e-7) as the original non-spastic arm, which closes the
batch effect that was previously aligned with the class label.

If fitness encodes mechanism, the arms stay separated no matter where on their severity axes they
sit. If fitness encodes severity, they interleave.

READING THE NUMBERS HONESTLY -- AND A RETRACTED ARGUMENT.
The first version of this script argued that one direction of the comparison was "depth-safe":
a spastic run already inside the non-spastic band can only move further in, because fitness falls
monotonically with generation. That argument is INVALID and has been withdrawn. Monotonicity
within a run is true, but it cannot protect SET MEMBERSHIP, because the band's own upper edge is
itself an unconverged run (CMW80_s1 at generation 48 of 90) and therefore also descending. The
boundary moves too. Flagging the reverse claim as provisional for exactly this reason, and not
applying it to the edge that defines "inside", was a convenient exemption.

The replacement is not an argument, it is a constraint: GEN_CAP. Every run is read at the same
generation ceiling, so no arm is credited with compute the others did not get. Two runs previously
placed in a table labelled "depth-safe" were at generation 320 and 337 against a 90-capped arm --
a 2.8x depth advantage, which is the very confound this project has already retracted three
results over.

The script also reports the two CLASS FLOORS separately from the ranges, because the ranges
interleaving and the floors crossing are different claims and only the first one is true.

Reads generation and fitness from the .par FILENAMES, which SCONE writes as
<gen>_<...>_<fitness>.par, so no claim here depends on a summary file or on a replay.
"""
import glob
import os
import re

RES = r"C:\Users\maurice\Documents\SCONE\results"

# mechanism, severity rank, run tags.  label 0 = no spastic component, 1 = spastic component
ARMS = [
    ("weak",  0, 0, "HEALTHY  (intact)",    ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"]),
    ("weak",  1, 0, "TA -20%",              ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"]),
    ("weak",  2, 0, "TA -40%",              ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"]),
    ("weak",  3, 0, "TA -60%",              ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"]),
    ("weak",  4, 0, "TA -70%  (new)",       ["CMW70_s1", "CMW70_s2"]),
    ("weak",  5, 0, "TA -80%  (new)",       ["CMW80_s1", "CMW80_s2"]),
    ("spas",  1, 1, "KV 0.02  (new)",       ["CMS020_s1", "CMS020_s2"]),
    ("spas",  2, 1, "KV 0.03  (new)",       ["CMS030_s1", "CMS030_s2"]),
    ("spas",  3, 1, "KV 0.05",              ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"]),
    ("spas",  4, 1, "KV 0.10",              ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"]),
]


GEN_CAP = 90       # every arm read at the same ceiling; the non-spastic arm stopped at 90


def best_par(tag, gen_cap=GEN_CAP):
    """(fitness, generation) of the best .par at or below the shared generation ceiling."""
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None
    bf, bg = 1e9, None
    for d in ds:                                    # a re-run makes a second directory; scan all
        for p in glob.glob(os.path.join(d, "0*.par")):
            m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
            if not m:
                continue
            g, f = int(m.group(1)), float(m.group(2))
            if gen_cap is not None and g > gen_cap:
                continue
            if f < bf:
                bf, bg = f, g
    return (None, None) if bg is None else (bf, bg)


def main():
    rows = []
    for mech, sev, lab, name, tags in ARMS:
        for t in tags:
            f, g = best_par(t)
            if f is None or f > 5.0:                # >5 means the model never learned to walk
                continue
            rows.append(dict(mech=mech, sev=sev, lab=lab, name=name, tag=t, fit=f, gen=g))

    print("=" * 74)
    print("BEST FITNESS BY CONDITION   (from .par filenames; lower = cheaper gait)")
    print("=" * 74)
    last = None
    for r in sorted(rows, key=lambda r: (r["mech"], r["sev"])):
        if r["name"] != last:
            print()
            last = r["name"]
        print("  %-4s %-18s %-14s fit=%.4f  gen=%d"
              % (r["mech"], r["name"], r["tag"], r["fit"], r["gen"]))

    sp = [r for r in rows if r["lab"] == 1]
    ns = [r for r in rows if r["lab"] == 0]
    sp_lo, sp_hi = min(r["fit"] for r in sp), max(r["fit"] for r in sp)
    ns_lo, ns_hi = min(r["fit"] for r in ns), max(r["fit"] for r in ns)

    print("\n" + "=" * 74)
    print("  spastic      n=%-2d  range %.4f - %.4f" % (len(sp), sp_lo, sp_hi))
    print("  non-spastic  n=%-2d  range %.4f - %.4f" % (len(ns), ns_lo, ns_hi))

    print("  depth: spastic gen %d-%d (mean %.1f) | non-spastic gen %d-%d (mean %.1f)"
          % (min(r["gen"] for r in sp), max(r["gen"] for r in sp),
             sum(r["gen"] for r in sp) / len(sp),
             min(r["gen"] for r in ns), max(r["gen"] for r in ns),
             sum(r["gen"] for r in ns) / len(ns)))

    # ---- claim 1: do the RANGES interleave? ---------------------------------------------------
    cross = ([r for r in sp if r["fit"] <= ns_hi] + [r for r in ns if r["fit"] >= sp_lo])
    print("\n" + "-" * 74)
    print("CLAIM 1 -- do the ranges interleave?")
    if cross:
        print("  YES: %d of %d runs sit inside the other class's range." % (len(cross), len(rows)))
        print("  Cheapest spastic run: %-13s %.4f (gen %d)"
              % (min(sp, key=lambda r: r["fit"])["tag"], sp_lo,
                 min(sp, key=lambda r: r["fit"])["gen"]))
        dearer = sorted([r for r in ns if r["fit"] > sp_lo], key=lambda r: r["fit"])
        print("  Non-spastic runs MORE expensive than it: %d" % len(dearer))
        for r in dearer:
            print("      %-13s %-16s %.4f (gen %d)" % (r["tag"], r["name"], r["fit"], r["gen"]))
        print("  -> a single cost threshold cannot separate the classes. Severity dominates.")
    else:
        print("  NO: still perfectly separated.")

    # ---- claim 2: do the class FLOORS cross? This is the claim that is NOT true. ---------------
    print("\n" + "-" * 74)
    print("CLAIM 2 -- does the spastic floor reach the non-spastic floor?")
    print("  spastic floor      %.4f  (%s, gen %d)"
          % (sp_lo, min(sp, key=lambda r: r["fit"])["tag"],
             min(sp, key=lambda r: r["fit"])["gen"]))
    print("  non-spastic floor  %.4f  (%s, gen %d)"
          % (ns_lo, min(ns, key=lambda r: r["fit"])["tag"],
             min(ns, key=lambda r: r["fit"])["gen"]))
    n_below = len([r for r in sp if r["fit"] < ns_lo])
    print("  spastic runs cheaper than the cheapest non-spastic run: %d of %d" % (n_below, len(sp)))
    if n_below == 0:
        print("  -> NO. Gap = %.4f, uncrossed. The interleaving comes ONLY from severe weakness"
              % (sp_lo - ns_lo))
        print("     exceeding mild spasticity. Cost is NOT mechanism-blind at matched severity,")
        print("     so 'fitness is a severity readout' must NOT be written unqualified.")

    print("\n" + "=" * 74)
    print("VERDICT (both halves, stated together):")
    print("  Cost cannot separate arbitrary conditions, because severity dominates it -- a")
    print("  weak-enough gait outspends a spastic one. But the spastic cost floor sits above")
    print("  the non-spastic floor and is not crossed at any depth tested. Whether that gap is")
    print("  mechanism or residual severity is decided by CMS020/030 vs CMW70/80 at convergence.")
    print("=" * 74)


if __name__ == "__main__":
    main()
