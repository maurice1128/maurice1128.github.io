"""Rebuild the three anchor rows of the pre-registration from CONVERGED replays.

WHAT THIS REPLACES, AND WHY IT IS THE MOST UPSTREAM FIX AVAILABLE.
`PREREGISTRATION_dose_response_v2.md` §0.4 proved that every archived `.sto` is a mid-run replay
artefact -- a file written by a scavenger while the optimizer was still producing generations, not
by a producer at the run's converged best. It then withdrew ONE row of §2.1 and left three:

    healthy   n=8   -1.263 +/- 0.850
    KV 0.100  n=6   -3.638 +/- 4.502
    KV 0.200  n=6   -9.223 +/- 2.678

Those three rows are the SOLE source of SD_plan (3.7043), of Delta_alt (7.96), of the argument for
keeping the top rung, and of F5's reference value -- i.e. of the seed count, the power, and the
ladder. The document proved its own foundations invalid and left the foundations in place.

Four council rounds then argued about what Delta_EQ "is" and produced five different values,
because the measurement underneath did not exist. It exists now: 23 runs replayed at each run's
converged best into isolated directories (`replay_rest.py`, `replay_registered/`).

THE TUPLE. Every dispute in those four rounds came from leaving one of these implicit. All four
are stated here, in code, and reported in the output:

  measure     ank_stance_mean (GRF-defined stance) AND ank_mean (whole cycle) -- both, never mixed
  sign        SCONE convention, negative = plantarflexed = more equinus
  baseline    reported against BOTH the healthy pool and the KV=0 control; they differ, and which
              one is meant changed the answer by 0.62 deg in an earlier round
  membership  by MEASURED delivered gain where certified, never by tag; listed per cell in the
              output so the reader can see exactly which runs are in which rung

No number here is quotable without the tuple that produced it. That is the whole lesson.
"""
import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "replay_registered")
sys.path.insert(0, HERE)
import sto_utils  # noqa: E402

# Membership by MEASURED delivered gain, not by tag. The SPAS* runs are the archived 2x form:
# `delivered_gain.py` reads copies = 2.000000 on them, so a nominal 0.05 delivered 0.10. That is
# a measurement, not a relabelling convention. The B* runs are EXCLUDED: the certifier ABSTAINs
# on them ("side-generic target with symmetric=0: side unresolvable"), so their true gain is not
# established, and E6 excludes any treatment seed whose verdict is not PASS. A run cannot anchor
# a rung it is not certified to sit in.
CELLS = {
    "healthy_0.000": ["HEALTHY_s1", "HEALTHY_s2", "HEALTHY_s3", "HEALTHY_s4",
                      "DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3", "HEALTHY"],
    "control_0.000": ["DOSER0000_s1"],
    "kv_0.050": ["DOSER1050_s1"],
    "kv_0.071": ["DOSER2071_s1"],
    "kv_0.100": ["DOSER3100_s1", "SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
    "kv_0.200": ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"],
}
# ROUND 43 -- THE `BSPAS005_s2` EXCLUSION REASON WAS WRONG ON BOTH HALVES. Settled by reading
# `history.txt`, which sits in the same directory the selector was already looking at.
#
# (1) THERE IS NO TIE. The two `.par` filenames read `0093_59.089_0.780` and `0096_10.003_0.780`,
#     and the selector -- correctly, given only filenames -- refused to guess. But `history.txt`
#     carries SIX significant figures for the same quantity: generation 93 = 0.779924,
#     generation 96 = 0.779612. Generation 96 is better by 0.000312. The "genuine fitness tie"
#     that stayed open for two council rounds is an artefact of the THREE-DECIMAL ROUNDING IN THE
#     FILENAME, and the file that disambiguates it was never opened.
#     Standing rule, and it generalises past this run: `history.txt` is the authoritative fitness
#     record; a `.par` FILENAME is a 3-decimal rendering of it. Never select on the rendering when
#     the record is on disk beside it. (Same shape as the startup-log finding: the tool was
#     already reporting the answer in plain text.)
#     Tie-break, registered for the case where `history.txt` itself ties exactly: SCONE emits a
#     `.par` only when the best-so-far IMPROVES, so of two files with equal recorded fitness the
#     LATER GENERATION is the operative best. Deterministic, no discretion.
#
# (2) E5 WAS NEVER THE OPERATIVE EXCLUSION ANYWAY. `BSPAS005_s2`'s `config.scone` is structurally
#     the same form as its three B* siblings -- `symmetric = 0` at line 24 with side-free targets
#     (`target = soleus`, `target = gastroc`) -- which is exactly the construction
#     `delivered_gain.py` ABSTAINs on. E6 admits only PASS, so this run is excluded on delivery
#     grounds like the other three, whether or not the selection is resolvable. The tie-break
#     question was never load-bearing for cell membership, and two rounds were spent on it.
EXCLUDED = {"BSPAS005_s1": "E6 -- delivered_gain ABSTAIN, side unresolvable (symmetric=0, side-free target)",
            "BSPAS005_s2": "E6 -- delivered_gain ABSTAIN, side unresolvable (same config form as its "
                           "three B* siblings). NOTE: the earlier 'E5_SELECTION, 0.780 tie at gen "
                           "93/96' reason is WITHDRAWN -- history.txt gives 0.779924 vs 0.779612, "
                           "not a tie; gen 96 is the best. E5 was never the operative exclusion.",
            "BSPAS01_s1": "E6 -- delivered_gain ABSTAIN, side unresolvable (symmetric=0, side-free target)",
            "BSPAS01_s2": "E6 -- delivered_gain ABSTAIN, side unresolvable (symmetric=0, side-free target)"}


def load():
    """{tag: {measure: value, gen, fitness}} from the replay directories' own provenance."""
    out = {}
    for prov_path in glob.glob(os.path.join(DEST, "*", "PROVENANCE.json")):
        prov = json.load(open(prov_path, encoding="utf-8"))
        # NORMALISE THE KEY. The eleven replays made earlier tonight wrote `tag` as the full
        # directory name (`SPAS005_s3.H0914M.GH2010.R4.S10W.D10.I.R3`); `replay_rest.py` writes
        # the short tag. Keying on the raw field silently dropped 9 of 23 runs and printed
        # cells of n=2 that looked like real cells -- a missing-data failure wearing the costume
        # of a result, which is this project's signature defect. Derive the tag from the
        # DIRECTORY, which both forms agree on.
        prov["tag"] = os.path.basename(os.path.dirname(prov_path)).split(".")[0]
        sto = prov.get("sto")
        if not sto or not os.path.exists(sto):
            # The earlier runs recorded an absolute path that may since have moved; fall back to
            # the single oversized .sto sitting beside this provenance file.
            cands = [s for s in glob.glob(os.path.join(os.path.dirname(prov_path), "*.sto"))
                     if os.path.getsize(s) > 100000]
            if len(cands) != 1:
                continue
            sto = cands[0]
        try:
            f = sto_utils.cycle_features(sto, side="l", settle=1.0)
        except Exception as e:
            out[prov["tag"]] = {"error": "%s: %s" % (e.__class__.__name__, e)}
            continue
        out[prov["tag"]] = {"ank_stance_mean": f.get("ank_stance_mean"),
                            "ank_mean": f.get("ank_mean"),
                            "gen": prov.get("gen"), "fitness": prov.get("fitness")}
    return out


def stats(vals):
    if not vals:
        return None, None
    if len(vals) == 1:
        return vals[0], None
    return statistics.mean(vals), statistics.stdev(vals)


def main():
    data = load()
    print("loaded %d replays from %s\n" % (len(data), DEST))
    missing = [t for c in CELLS.values() for t in c if t not in data]
    if missing:
        print("NOT REPLAYED (cells are incomplete): %s\n" % ", ".join(missing))

    report = {"measure_note": "SCONE sign; negative = plantarflexed = more equinus",
              "cells": {}}
    for measure in ("ank_stance_mean", "ank_mean"):
        print("=" * 78)
        print("MEASURE: %s   (negative = plantarflexed)" % measure)
        print("=" * 78)
        print("  %-16s %3s  %9s %9s   %s" % ("cell", "n", "mean", "sd", "members"))
        cell_stats = {}
        for name, tags in CELLS.items():
            vals = [data[t][measure] for t in tags
                    if t in data and data[t].get(measure) is not None]
            got = [t for t in tags if t in data and data[t].get(measure) is not None]
            m, sd = stats(vals)
            cell_stats[name] = (m, sd, len(vals))
            print("  %-16s %3d  %9s %9s   %s"
                  % (name, len(vals),
                     "%.4f" % m if m is not None else "--",
                     "%.4f" % sd if sd is not None else "--",
                     ",".join(got)))
        # Delta_EQ against BOTH baselines. Which baseline was meant has already changed an
        # answer by 0.62 deg in this project; reporting one alone is how that happened.
        print("\n  Delta_EQ = EQ(cell) - EQ(baseline), EQ = -%s, positive = MORE equinus" % measure)
        for base in ("healthy_0.000", "control_0.000"):
            bm = cell_stats[base][0]
            if bm is None:
                continue
            row = []
            for name in ("kv_0.050", "kv_0.071", "kv_0.100", "kv_0.200"):
                m = cell_stats[name][0]
                row.append("%s %+.3f" % (name.replace("kv_", ""), -(m) - -(bm))
                           if m is not None else "%s --" % name)
            print("    vs %-14s %s" % (base, "   ".join(row)))
        # The quantity four rounds were spent arguing about.
        a, b = cell_stats["kv_0.100"][0], cell_stats["kv_0.200"][0]
        if a is not None and b is not None:
            print("    0.200 - 0.100 increment: %+.3f  (positive = monotone)" % (-(b) - -(a)))
        # SD_plan: pooled across the two treated cells, healthy EXCLUDED. The healthy pool is
        # 3-5x tighter, and pooling it into a contrast against a far more variable spastic cell
        # is what made n=6 look adequate when it was not.
        sds = [cell_stats[c][1] for c in ("kv_0.100", "kv_0.200") if cell_stats[c][1]]
        ns = [cell_stats[c][2] for c in ("kv_0.100", "kv_0.200") if cell_stats[c][1]]
        if len(sds) == 2:
            pooled = (((ns[0] - 1) * sds[0] ** 2 + (ns[1] - 1) * sds[1] ** 2)
                      / (ns[0] + ns[1] - 2)) ** 0.5
            print("    POOLED SD (treated cells only, healthy excluded): %.4f"
                  "   [document registers 3.7043]" % pooled)
        report["cells"][measure] = {k: {"mean": v[0], "sd": v[1], "n": v[2]}
                                    for k, v in cell_stats.items()}
        print()

    report["excluded"] = EXCLUDED
    report["membership"] = CELLS
    out = os.path.join(HERE, "..", "paper", "S21_REBUILT.json")
    with open(os.path.abspath(out), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print("excluded from all cells:")
    for t, why in EXCLUDED.items():
        print("  %-14s %s" % (t, why))
    print("\nwritten: %s" % os.path.abspath(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
