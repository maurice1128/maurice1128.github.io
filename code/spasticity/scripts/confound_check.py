"""Is the foot-drop gradient a genuine pathology effect, or just a cadence artifact?

The severity conditions converged to different walking cadences (cycle time 1.17 s -> 0.68 s),
and cadence is itself monotone with severity, so the raw ankle gradient is confounded. Two
tests separate them:

 1. WITHIN-condition correlation: seeds of the SAME condition differ in cadence purely by
    optimizer chance (severity held fixed). If cadence drove the ankle measures, ankle would
    track cadence within a condition too. If that correlation is ~0, cadence is not the cause.
 2. PARTIAL correlation of severity with ankle, controlling for cadence.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEV = {"HEALTHY": 0, "PAR20": 20, "PAR40": 40, "PAR60": 60}


def r(a, b):
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def partial(x, y, z):
    """corr(x, y | z) via residualisation."""
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return r(rx, ry)


def main():
    f = json.load(open(os.path.join(HERE, "scone_seed_features.json")))
    rows = []
    for c, s in SEV.items():
        for k, v in f.items():
            if k.startswith(c + "_s") and v.get("status") == "ok":
                rows.append((s, v["cycle_time"], v["ank_min"], v["ank_hs"]))
    A = np.array(rows)
    S, CT, MN, HS = A[:, 0], A[:, 1], A[:, 2], A[:, 3]
    print("n = %d  (%d conditions x seeds)" % (len(A), len(set(S))))

    # 1. within-condition (severity removed by centering)
    ctw, mnw, hsw = CT.copy(), MN.copy(), HS.copy()
    for s in np.unique(S):
        m = S == s
        ctw[m] -= CT[m].mean(); mnw[m] -= MN[m].mean(); hsw[m] -= HS[m].mean()
    print("\nWITHIN-condition correlation (severity held fixed):")
    print("  cadence vs ank_min : r = %+.3f" % r(ctw, mnw))
    print("  cadence vs ank_hs  : r = %+.3f" % r(ctw, hsw))
    print("  (~0 => cadence does NOT drive the ankle measures)")

    print("\nBETWEEN-condition (raw):")
    print("  severity vs ank_min: r = %+.3f" % r(S, MN))
    print("  severity vs ank_hs : r = %+.3f" % r(S, HS))
    print("  severity vs cadence: r = %+.3f" % r(S, CT))

    print("\nPARTIAL correlation controlling for cadence:")
    print("  severity vs ank_min | cadence : r = %+.3f" % partial(S, MN, CT))
    print("  severity vs ank_hs  | cadence : r = %+.3f" % partial(S, HS, CT))


if __name__ == "__main__":
    main()
