"""The cutoff sweep COUNCIL_round8 named as "the one remaining route" and nobody ran.

ROUND 8, PART C, VERBATIM: "A higher cutoff (12-20 Hz) was NOT tested by either script. That is the
one remaining route and it must be run before any measurability claim is made in either direction."

That was written on 2026-07-2x. This is 2026-08-10. It has never been run.

WHY IT MATTERS. `slap_noise_test.py` shows a 6 Hz zero-lag low-pass -- what every clinical gait
pipeline applies before differentiating -- collapses the spastic/non-spastic separation to 0 % at
EVERY noise level INCLUDING ZERO. The filter attenuates the sharp healthy transient (~40 ms) far
more than the slow spastic one. If a higher cutoff preserves the transient while still suppressing
markerless noise, the feature is measurable with a real pipeline; if no cutoff does, it is not, and
that is a disqualifying result for any pipeline that filters -- which is all of them.

WHY A COMPANION AND NOT AN EDIT. `slap_noise_test.py` hardcodes `FC = 6.0` at module level, and
`slap()` calls `lowpass(a, dt)` with no `fc`, so the default binds to 6.0 AT DEFINITION TIME.
Monkey-patching `M.FC` would silently do nothing -- the exact class of defect this project has been
cataloguing. `slap()` is therefore mirrored here with an explicit `fc`, and everything else --
`load_trial`, `lowpass`, the tag lists, the noise ladder, the bootstrap count, the separation rule
-- is IMPORTED, not restated.

CALIBRATION FIRST, AND IT IS NOT OPTIONAL. A mirrored function is a second implementation of a
procedure, and this project has paid for one of those. Before any new cutoff is reported, this
reproduces the ORIGINAL's two supported settings -- no filter and 6 Hz -- against the numbers
already recorded in `slap_noise_results.json`. If they do not reproduce, the sweep is not run.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import slap_noise_test as M  # noqa: E402  -- imported, never modified

CUTOFFS = [None, 6.0, 10.0, 12.0, 15.0, 20.0, 30.0, 50.0]
OUT = os.path.join(HERE, "..", "paper", "SLAP_CUTOFF_SWEEP_r152.json")


def slap_fc(tag, sd, rng, fc, correlated=False):
    """M.slap, mirrored with an explicit cutoff. Every other line is M's."""
    tr = M.load_trial(tag)
    if tr is None:
        return None, None
    t = tr["t"]
    dt = float(np.median(np.diff(t)))
    vals = {}
    for side in ("l", "r"):
        ang, wins = tr[side]
        a = ang
        if sd > 0:
            if correlated:
                rho = 0.9
                e = rng.normal(0.0, sd * np.sqrt(1 - rho ** 2), size=ang.shape)
                n = np.empty_like(e)
                n[0] = rng.normal(0.0, sd)
                for i in range(1, len(e)):
                    n[i] = rho * n[i - 1] + e[i]
                n = n + rng.normal(0.0, sd * 0.5)
                a = ang + n
            else:
                a = ang + rng.normal(0.0, sd, size=ang.shape)
        if fc is not None:
            a = M.lowpass(a, dt, fc)
        v = np.gradient(a, t)
        vals[side] = float(np.mean([-np.min(v[i:j]) for i, j in wins]))
    return vals["l"], (vals["l"] / vals["r"] if vals["r"] > 1e-9 else np.nan)


def sep_ladder(sp, ns, fc):
    """The whole noise ladder under ONE rng stream, exactly as M.main() consumes it.

    r152 DEFECT, found by the calibration gate: the first version created a fresh
    `default_rng(0)` per noise level. M.main() creates ONE rng and consumes it continuously
    across the ladder, so only the FIRST level after a fresh seed can agree. Measured:
    sd=1.5 matched to 98.33 vs 98.3 while sd=2.5/3.5 diverged 45.0/31.7 and 10.0/5.0 --
    a clean signature of a stream offset rather than a logic error. Corrected here.
    """
    rng = np.random.default_rng(0)
    out = []
    for sd in M.NOISE:
        n = M.NBOOT if sd > 0 else 1
        hit = 0
        for _ in range(n):
            rs = [slap_fc(t, sd, rng, fc) for t in sp]
            rn = [slap_fc(t, sd, rng, fc) for t in ns]
            a_s = [x[0] for x in rs if x[0] is not None]
            a_n = [x[0] for x in rn if x[0] is not None]
            if a_s and a_n and max(a_s) < min(a_n):
                hit += 1
        out.append(100.0 * hit / n)
    return out


def main():
    for tag in M.SPAS + M.NONSPAS:
        M.load_trial(tag)
    sp = [t for t in M.SPAS if M._CACHE.get(t)]
    ns = [t for t in M.NONSPAS if M._CACHE.get(t)]
    print("spastic n=%d  non-spastic n=%d   noise ladder %s   nboot %d"
          % (len(sp), len(ns), M.NOISE, M.NBOOT))

    # r152: calibrate against the ORIGINAL RUN LIVE, not against slap_noise_results.json.
    # That file does not reproduce from the script that claims to produce it -- measured
    # 2026-08-10: JSON 93.33/18.33/1.67 vs the script today 98.3/31.7/5.0, and
    # COUNCIL_round8's table quotes a THIRD set (90/22/1). `load_trial` reads the NEWEST
    # .sto per tag and replays have been re-run since, so the corpus underneath moved.
    # Calibrating against a stale artifact would validate the mirror against a number
    # nothing on disk currently produces.
    print("\n" + "=" * 78)
    print("CALIBRATION -- mirror vs the ORIGINAL EXECUTED NOW (not the stale JSON)")
    print("=" * 78)
    ok = True
    for fc in (None, 6.0):
        rng = np.random.default_rng(0)
        want = []
        for sd in M.NOISE:
            n = M.NBOOT if sd > 0 else 1
            hit = 0
            for _ in range(n):
                rs = [M.slap(t, sd, rng, False, fc is not None) for t in sp]
                rn = [M.slap(t, sd, rng, False, fc is not None) for t in ns]
                a_s = [x[0] for x in rs if x[0] is not None]
                a_n = [x[0] for x in rn if x[0] is not None]
                if a_s and a_n and max(a_s) < min(a_n):
                    hit += 1
            want.append(100.0 * hit / n)
        got = sep_ladder(sp, ns, fc)
        for sd, g, w in zip(M.NOISE, got, want):
            good = abs(g - w) < 1e-9
            ok &= good
            print("  fc=%-5s sd=%.1f   mirror %6.2f%%   original %6.2f%%   %s"
                  % (fc, sd, g, w, "OK" if good else "*** MISMATCH ***"))
    if not ok:
        print("\nCALIBRATION FAILED -- the mirror is not the original. Sweep NOT run.")
        return 1
    print("\n  calibration PASSES -- mirror == original, same rng stream discipline")

    print("\n" + "=" * 78)
    print("THE SWEEP -- run-level separation (%), the clinically relevant row")
    print("=" * 78)
    hdr = "  %-8s" % "cutoff" + "".join("%9s" % ("sd=%.1f" % s) for s in M.NOISE)
    print(hdr)
    res = {}
    for fc in CUTOFFS:
        row = sep_ladder(sp, ns, fc)
        res["none" if fc is None else "%.0fHz" % fc] = dict(zip([str(s) for s in M.NOISE], row))
        print("  %-8s" % ("none" if fc is None else "%.0f Hz" % fc)
              + "".join("%8.1f%%" % v for v in row))

    p = os.path.abspath(OUT)
    json.dump({"what": "cutoff sweep named in COUNCIL_round8 Part C and never run until r152",
               "n_spastic": len(sp), "n_nonspastic": len(ns),
               "noise_sd_deg": list(M.NOISE), "nboot": M.NBOOT,
               "separation_pct_run_level": res}, open(p, "w"), indent=1)
    print("\n  wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
