"""Is the spastic arm MULTIMODAL, or just measured at different optimization depths?

THE CLAIM UNDER TEST.
I reported that four seeds of KV 0.05 give mean ankle angles of +1.48, -1.78, -9.96 and -10.00
degrees -- an 11.5 deg spread, larger than the between-condition effect the whole project rests on
-- and concluded the spastic arm is MULTIMODAL: the same lesion lands CMA-ES in qualitatively
different gaits.

I did not exclude the obvious alternative: those four numbers came from runs at different
optimization depths, and deeper optimization systematically removes equinus. If so the spread is a
depth artefact, not multimodality, and the conclusion is wrong.

The numbers cannot settle it as they stand. They were taken from `scone_spastic_seeds.json`, whose
recorded fitnesses (1.045 for s3, 1.072 for s4) do not match those runs' best `.par` (0.667, 0.745)
-- so that file is an OLD, SHALLOW replay, and its seeds are not at a common depth with each other
or with anything else.

THE TEST.
Replay every seed of every condition at a COMMON generation ceiling, from each run's own best
`.par` at or below that ceiling, and report the spread at each ceiling.

  spread persists at a common ceiling      -> genuinely multimodal
  spread collapses at a common ceiling     -> it was depth, and the multimodality claim is wrong
  spread present at one ceiling only       -> depth-dependent; report as such, claim neither

Run at several ceilings so the answer is a curve rather than a single number, since a single
ceiling can always be the lucky one.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay_cache import replay  # noqa: E402
from sto_utils import col, grf_vertical, heel_strikes, load_sto  # noqa: E402

CAPS = [90, 200, None]
CONDS = {
    "HEALTHY": ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"],
    "TA -20%": ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"],
    "TA -40%": ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"],
    "TA -60%": ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"],
    "KV 0.05": ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
    "KV 0.10": ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"],
}


def mean_ankle(sto, side="l"):
    cols, d = load_sto(sto)
    if d.size == 0:
        return None
    t = d[:, 0]
    a = np.degrees(col(cols, d, "ankle_angle_%s" % side))
    grf, thr = grf_vertical(cols, d, side)
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
    if len(hs) < 3:
        return None
    return float(np.mean(a[hs[0]:hs[-1]]))


def main():
    for cap in CAPS:
        label = "gen <= %s" % (cap if cap else "unlimited")
        print("\n" + "=" * 72)
        print("COMMON CEILING: %s" % label)
        print("=" * 72)
        print("%-9s %-6s %-9s %s" % ("condition", "n", "spread", "per-seed mean ankle (gen)"))
        print("-" * 72)
        rows = []
        for cname, tags in CONDS.items():
            vals, detail = [], []
            for t in tags:
                r = replay(t, gen_cap=cap)
                if "error" in r:
                    detail.append("%s:%s" % (t.split("_")[-1], r["error"][:12]))
                    continue
                m = mean_ankle(r["sto"])
                if m is None:
                    detail.append("%s:no-cycles" % t.split("_")[-1])
                    continue
                vals.append(m)
                detail.append("%+.2f(g%d)" % (m, r["gen"]))
            if len(vals) >= 2:
                sp = max(vals) - min(vals)
                rows.append((cname, sp, len(vals)))
                print("%-9s %-6d %-9.2f %s" % (cname, len(vals), sp, "  ".join(detail)))
            else:
                print("%-9s %-6d %-9s %s" % (cname, len(vals), "--", "  ".join(detail)))

        if rows:
            weak = [s for c, s, _ in rows if c.startswith(("HEALTHY", "TA"))]
            spas = [s for c, s, _ in rows if c.startswith("KV")]
            if weak and spas:
                print("\n  weakness/healthy arm  max spread %.2f deg" % max(weak))
                print("  spastic arm           max spread %.2f deg" % max(spas))
                if max(spas) > 2 * max(weak):
                    print("  -> spastic spread exceeds the weakness arm by >2x AT THIS CEILING.")
                else:
                    print("  -> the arms' spreads are comparable at this ceiling; the")
                    print("     multimodality claim is NOT supported here.")

    print("\nRead across ceilings. A spread that survives every common ceiling is multimodality.")
    print("A spread that appears only at the unlimited ceiling is optimization depth.")


if __name__ == "__main__":
    main()
