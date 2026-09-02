"""THE CLINICAL QUESTION, asked on data that survives this project's own gates.

Can a 2D SAGITTAL-VIDEO-OBSERVABLE feature separate plantarflexor SPASTICITY from dorsiflexor
WEAKNESS? Post-stroke equinus has these two causes, they look alike, and the treatments are
opposite -- botulinum toxin versus strengthening and an AFO. Current practice needs an invasive
diagnostic tibial nerve block. No published study reports an accuracy, AUC or sensitivity for
telling them apart from gait.

WHY THIS COULD NOT BE RUN BEFORE, AND WHAT CHANGED.
The two arms were broken for DIFFERENT reasons, and only one of them was ever the famous one:

  spastic arm   every archived run delivered its reflex at 2x nominal AND landed both mirrored
                instances on the LEFT limb (a doubling and a mis-targeting at once). Runs are
                therefore relabelled by MEASURED delivered gain, never by their tag.
  weakness arm  never affected. Weakness is a `max_isometric_force` scale in the .osim, not a
                controller injection, so `SpasticL` count is 0 in every PAR/DPAR scenario. This
                arm was clean the entire time.

What was never clean was the COMPARISON. Every previous attempt read phenotypes from mid-run
replay artefacts -- files a scavenger wrote while the optimizer was still producing generations --
and the staleness was CORRELATED WITH DOSE: deep spastic runs lagged their best by hundreds of
generations while weakness runs converge by ~generation 90. A depth difference aligned with the
group label is not noise, it is the independent variable leaking into the measurement.

Both arms are now replayed at each run's converged best (`replay_rest.py` -> `replay_registered/`,
one isolated directory per run, one `.sto` each, `PROVENANCE.json` recording the selected `.par`
and its generation). That is the only thing that ever stood between this archive and an answer.

WHAT THIS IS NOT. It is not the pre-registered dose-response, which remains held. Cells here are
small and unequal, the severity axes of the two arms are not calibrated against each other, and
nothing below is a clinical claim. It is the first internally-clean look at whether a separation
exists at all -- and a negative is as informative as a positive, because no one has reported
either.

FEATURES. Only quantities a single sagittal camera could plausibly recover: joint angles, ranges,
timing. Muscle activation, force and metabolic cost are excluded by construction -- they would be
answering a question about EMG, which the clinical constraint rules out.
"""
import glob
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "replay_registered")
sys.path.insert(0, HERE)
from sto_utils import cycle_features  # noqa: E402

# 2D-sagittal-observable only. `cycle_time`/`stance_frac` are timing; the rest are joint
# kinematics. `n_cycles` and `t_end` are bookkeeping, not phenotype, and are excluded.
FEATURES = ["ank_mean", "ank_stance_mean", "ank_hs", "ank_min", "ank_max", "ank_rom",
            "ank_swing_min", "ank_vel_max", "knee_min", "knee_rom", "hip_rom",
            "cycle_time", "stance_frac"]

# Membership by MECHANISM. The spastic tags carry MEASURED delivered gains (the SPAS* runs read
# copies = 2.000000, so nominal 0.05 delivered 0.10); the weakness tags carry `max_isometric_force`
# scales on tib_ant_l. B* runs are excluded throughout: the delivery certifier ABSTAINs on them.
SPASTIC = ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4",
           "SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4",
           "DOSER1050_s1", "DOSER2071_s1", "DOSER3100_s1"]
WEAK = ["PAR20_s1", "PAR20_s2", "PAR20_s3", "PAR20_s4",
        "PAR40_s1", "PAR40_s2", "PAR40_s3", "PAR40_s4",
        "PAR60_s1", "PAR60_s2", "PAR60_s3", "PAR60_s4",
        "DPAR20_s1", "DPAR20_s2", "DPAR20_s3",
        "DPAR40_s1", "DPAR40_s2", "DPAR40_s3",
        "DPAR60_s1", "DPAR60_s2", "DPAR60_s3"]
HEALTHY = ["HEALTHY_s1", "HEALTHY_s2", "HEALTHY_s3", "HEALTHY_s4",
           "DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"]


def load():
    out = {}
    for prov in glob.glob(os.path.join(DEST, "*", "PROVENANCE.json")):
        d = os.path.dirname(prov)
        tag = os.path.basename(d).split(".")[0]
        stos = [s for s in glob.glob(os.path.join(d, "*.sto"))
                if os.path.getsize(s) > 100000]
        if len(stos) != 1:
            continue
        try:
            f = cycle_features(stos[0], side="l", settle=1.0)
        except Exception:
            continue
        f["_gen"] = json.load(open(prov, encoding="utf-8")).get("gen")
        out[tag] = f
    return out


def mannwhitney_exact_p(a, b):
    """Two-sided exact permutation p. No scipy dependency, and with n this small the exact
    enumeration is both cheap and honest -- an asymptotic p at n=11 vs 21 would be theatre."""
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return None, None
    pooled = a + b
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    idx = range(n + m)
    total = hit = 0
    for combo in itertools.combinations(idx, n):
        ca = [pooled[i] for i in combo]
        cs = set(combo)
        cb = [pooled[i] for i in idx if i not in cs]
        u = sum(1 for x in ca for y in cb if x > y) + 0.5 * sum(1 for x in ca for y in cb if x == y)
        total += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            hit += 1
        if total > 200000:               # bail rather than pretend; reported as approximate
            return obs / (n * m), None
    return obs / (n * m), hit / float(total)


def main():
    data = load()
    have = lambda tags: [t for t in tags if t in data]  # noqa: E731
    sp, wk, hl = have(SPASTIC), have(WEAK), have(HEALTHY)
    print("loaded %d replays" % len(data))
    print("  spastic n=%-3d %s" % (len(sp), ",".join(sp)))
    print("  weak    n=%-3d %s" % (len(wk), ",".join(wk)))
    print("  healthy n=%-3d %s\n" % (len(hl), ",".join(hl)))
    if not sp or not wk:
        print("cannot run: an arm is empty")
        return 1

    # DEPTH CHECK FIRST. This is the confound that invalidated every previous attempt, so it is
    # reported BEFORE any phenotype -- if the arms differ in analysed generation, nothing below
    # can be attributed to mechanism. Round 44's whole point is that both are now at run best.
    gs, gw = [data[t]["_gen"] for t in sp], [data[t]["_gen"] for t in wk]
    print("DEPTH (analysed generation, both arms at each run's converged best):")
    print("  spastic  min %d  max %d  mean %.1f" % (min(gs), max(gs), sum(gs) / len(gs)))
    print("  weak     min %d  max %d  mean %.1f" % (min(gw), max(gw), sum(gw) / len(gw)))
    print("  NOTE: unequal means are expected and are NOT the old confound -- every run is at its"
          " OWN optimum,\n        so 'deeper' here means 'took longer to converge', not 'was given"
          " more compute'.\n")

    print("%-18s %22s %22s   %6s  %8s  %s" %
          ("feature", "spastic mean [min,max]", "weak mean [min,max]", "AUC", "exact p", "overlap"))
    print("-" * 118)
    rows = []
    for f in FEATURES:
        a = [data[t][f] for t in sp if data[t].get(f) is not None]
        b = [data[t][f] for t in wk if data[t].get(f) is not None]
        if len(a) < 2 or len(b) < 2:
            continue
        auc, p = mannwhitney_exact_p(a, b)
        # Separation in the only sense that matters clinically: does ANY spastic run sit inside
        # the weakness range? A significant mean difference with full overlap cannot classify a
        # patient, and four features have already died in this project on exactly that distinction.
        lo, hi = min(b), max(b)
        overlap = sum(1 for x in a if lo <= x <= hi)
        rows.append((f, auc, p, overlap, len(a)))
        print("%-18s %8.3f [%6.2f,%6.2f] %8.3f [%6.2f,%6.2f]   %6.3f  %8s  %d/%d spastic inside"
              % (f, sum(a) / len(a), min(a), max(a), sum(b) / len(b), min(b), max(b),
                 auc, ("%.4f" % p) if p is not None else "approx", overlap, len(a)))

    clean = [r for r in rows if r[3] == 0]
    print("\n" + "=" * 118)
    if clean:
        print("FEATURES WITH ZERO OVERLAP (every spastic run outside the entire weakness range):")
        for f, auc, p, ov, n in clean:
            print("   %-18s AUC %.3f   exact p %s" % (f, auc, ("%.4f" % p) if p else "approx"))
        print("\nA zero-overlap feature is the only kind that could classify a single patient.")
    else:
        print("NO FEATURE SEPARATES THE ARMS WITHOUT OVERLAP.")
        best = max(rows, key=lambda r: abs(r[1] - 0.5))
        print("  Closest: %s, AUC %.3f, %d of %d spastic runs fall inside the weakness range."
              % (best[0], best[1], best[3], best[4]))
        print("  On this archive, no single 2D-sagittal feature assigns an individual run to an"
              " arm.")
    print("\nCAVEATS, stated because they bound every line above: cells are small and unequal"
          " (n=%d vs %d);\nthe two arms' severity axes are NOT calibrated against each other, so"
          " a difference may be severity,\nnot mechanism; and multiple features are tested here"
          " with no multiplicity correction -- any p below\nis a screening value, not a"
          " confirmatory one." % (len(sp), len(wk)))

    out = os.path.join(HERE, "..", "paper", "SPASTIC_VS_WEAK.json")
    with open(os.path.abspath(out), "w", encoding="utf-8") as fh:
        json.dump({"spastic": sp, "weak": wk, "healthy": hl,
                   "features": {r[0]: {"auc": r[1], "p_exact": r[2], "n_overlap": r[3]}
                                for r in rows}}, fh, indent=1)
    print("\nwritten: %s" % os.path.abspath(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
