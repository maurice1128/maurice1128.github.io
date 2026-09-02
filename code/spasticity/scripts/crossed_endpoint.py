"""The crossed experiment's REGISTERED endpoint, computed. Nothing here was chosen after the data.

REGISTERED 2026-08-03 00:14; first cell launched 00:21:11; all 48 finished 16:55.
Every constant below was fixed before the first cell ran and is reproduced verbatim:

    PRIMARY    filtered `ank_vel_max` -- left ankle angle resampled to 30 Hz, 4th-order
               ZERO-PHASE Butterworth low-pass at 6 Hz, central-difference differentiated,
               peak over complete GRF-delimited cycles after settle = 1.0 s
    SECONDARY  `ank_rom`, and it stays secondary whichever performs better (R45-S)
    ARMS       spastic DR2K050/075/100/150/200  x  weak PAR20/40/60/CMW70/CMW80
    NOT ARMS   HEALTHY and DR2K000 are references. A control counted as a condition inflates
               the degrees of freedom the 5x5 design was corrected to protect.
    UNIT       CONDITION, not seed. Seeds are replicate searches of one physics, not subjects.
    ALPHA      0.05 after multiplicity correction, effective test count computed BEFORE the
               contrast from the correlation structure -- not after seeing which feature wins.

R45-S, binding on the FIRST look: **no feature may be promoted to primary after the data are
seen.** If the primary fails alpha after correction the discrimination claim is ABANDONED --
not re-membered, not re-filtered, not swapped for the secondary.

WHY THE RAW SIGNAL IS NOT USED. The round-44 referee showed `np.gradient` at the native 100 Hz
is both less defensible and WEAKER than 30 Hz + 6 Hz low-pass -- what a real camera and a
standard gait-lab cutoff actually see. Registered before launch on that reasoning.

TWO RATIFICATION CONDITIONS, reported in the output rather than only in the document:
  (a) the fifth spastic rung was placed at 0.075 KNOWING from archive data that separation is
      greatest at the mild end. Pre-data and declared; it still favours the hypothesis.
  (b) leave-one-out sensitivity is reported as AUC and overlap ONLY, never a p-value: at 4x5
      the exact floor is 0.0506, so no LOO contrast can clear alpha even under perfect
      separation. Stated in advance so absent p-values are not read as suppression.

CELL RESOLUTION. Directories are identified by CONTENT -- `min_progress == 0` AND
`max_generations == 90` AND terminal generation 89 from `history.txt`. SCONE appends " (1)"
rather than overwriting, and seven of twelve conditions collide with archive runs; `CMW70`/
`CMW80`'s archive copies also ran at 90 and also stop at 89, so `min_progress` is the only
discriminator. Resolving by name or mtime would have given those two cells n = 6 -- four crossed
seeds plus two archive runs at a different budget -- reintroducing the budget confound in the arm
added to remove it.
"""
import glob
import json
import os
import sys
from itertools import combinations

import numpy as np
from scipy.signal import butter, filtfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sto_utils  # noqa: E402

REPLAY = os.path.join(HERE, "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCES = ["HEALTHY", "DR2K000"]
SEEDS = 4
FS, CUT, ORDER, SETTLE = 30.0, 6.0, 4, 1.0
ALPHA = 0.05


def filtered_features(sto):
    """(ank_vel_max_filtered, ank_rom). The registered pipeline, in registered order."""
    cols, data = sto_utils.load_sto(sto)
    t = sto_utils.col(cols, data, "time")
    ang = sto_utils.col(cols, data, "ankle_angle_l") * 180.0 / np.pi
    if abs(ang).max() < 3.0:                       # already degrees in some files
        ang = sto_utils.col(cols, data, "ankle_angle_l")
    # `grf_vertical` returns (signal, threshold) -- the threshold differs by channel
    # (0.05 for body-weight-normalised, 20.0 N for raw), so it must be carried through to
    # `heel_strikes` rather than left at the default. Unpacking it as a bare array silently
    # indexes a tuple; using the default threshold on a normalised channel would silently find
    # no heel strikes at all, which is the quieter of the two failures.
    grf, thresh = sto_utils.grf_vertical(cols, data, "l")
    if grf is None:
        return None, None

    keep = t >= SETTLE
    t, ang, grf = t[keep], ang[keep], grf[keep]
    # Resample to 30 Hz FIRST, then filter: a camera samples then the lab filters, and doing it
    # in the other order would low-pass a signal the camera never delivered.
    tr = np.arange(t[0], t[-1], 1.0 / FS)
    ar = np.interp(tr, t, ang)
    b, a = butter(ORDER, CUT / (FS / 2.0), btype="low")
    af = filtfilt(b, a, ar)                        # zero-phase: forward and backward
    vel = np.gradient(af, tr)                      # central difference

    hs = sto_utils.heel_strikes(t, grf, thresh=thresh)
    if len(hs) < 3:
        return None, None
    # Complete cycles only, and the LAST is dropped by sto_utils' own convention.
    lo, hi = t[hs[0]], t[hs[-1]]
    m = (tr >= lo) & (tr <= hi)
    if m.sum() < 10:
        return None, None
    return float(np.abs(vel[m]).max()), float(af[m].max() - af[m].min())


def auc(a, b):
    """P(a > b) with ties at 0.5. 0 means every a below every b."""
    n, m = len(a), len(b)
    g = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    return g / (n * m)


def exact_p(a, b):
    """Two-sided exact Mann-Whitney by full enumeration. n=5,5 -> C(10,5)=252 splits."""
    pool = list(a) + list(b)
    n, m = len(a), len(b)
    obs = abs(auc(a, b) * n * m - n * m / 2.0)
    idx, hit, tot = range(n + m), 0, 0
    for c in combinations(idx, n):
        cs = set(c)
        ca = [pool[i] for i in c]
        cb = [pool[i] for i in idx if i not in cs]
        u = sum(1 for x in ca for y in cb if x > y) + 0.5 * sum(1 for x in ca for y in cb if x == y)
        tot += 1
        if abs(u - n * m / 2.0) >= obs - 1e-9:
            hit += 1
    return hit / float(tot)


def main():
    runs = {}
    for prov in glob.glob(os.path.join(REPLAY, "*", "PROVENANCE.json")):
        p = json.load(open(prov, encoding="utf-8"))
        stos = [s for s in glob.glob(os.path.join(os.path.dirname(prov), "*.sto"))
                if os.path.getsize(s) > 100000]
        if len(stos) != 1:
            continue
        v, r = filtered_features(stos[0])
        if v is None:
            continue
        runs[p["tag"]] = {"vel": v, "rom": r, "best_gen": p["best_gen"],
                          "gap": p.get("gen_gap"), "fit": p["fitness"]}

    print("=" * 92)
    print("CROSSED EXPERIMENT -- REGISTERED ENDPOINT")
    print("  endpoint fixed 2026-08-03 00:14 | first cell 00:21:11 | all 48 done 16:55")
    print("  primary = ank_vel_max, %.0f Hz resample + %.0f Hz zero-phase Butterworth (order %d)"
          % (FS, CUT, ORDER))
    print("  unit = CONDITION (seeds are replicate searches, not subjects)")
    print("=" * 92)

    # FAIL CLOSED. A partial corpus is how a cell silently becomes n<4 while the report says n=4.
    incomplete = []
    for cond in SPASTIC + WEAK + REFERENCES:
        got = [k for k in runs if k.rsplit("_s", 1)[0] == cond]
        if len(got) != SEEDS:
            incomplete.append((cond, len(got)))
    if incomplete:
        print("\n[BLOCKED] incomplete cells: %s" % ", ".join("%s %d/%d" % (c, n, SEEDS)
                                                            for c, n in incomplete))
        return 2

    def cond_mean(cond, key):
        return float(np.mean([runs["%s_s%d" % (cond, s)][key] for s in range(1, SEEDS + 1)]))

    print("\n  %-10s %14s %14s   %s" % ("condition", "ank_vel_max", "ank_rom", "per-seed vel"))
    print("  " + "-" * 88)
    for cond in SPASTIC + WEAK + REFERENCES:
        vs = [runs["%s_s%d" % (cond, s)]["vel"] for s in range(1, SEEDS + 1)]
        print("  %-10s %14.2f %14.2f   %s"
              % (cond, cond_mean(cond, "vel"), cond_mean(cond, "rom"),
                 " ".join("%6.1f" % v for v in vs)))

    sv = [cond_mean(c, "vel") for c in SPASTIC]
    wv = [cond_mean(c, "vel") for c in WEAK]
    sr = [cond_mean(c, "rom") for c in SPASTIC]
    wr = [cond_mean(c, "rom") for c in WEAK]

    # Effective test count from the CORRELATION STRUCTURE, computed before the contrast is read.
    M = np.array([[runs[k]["vel"], runs[k]["rom"]] for k in sorted(runs)])
    ev = np.linalg.eigvalsh(np.corrcoef(M.T))
    n_eff = float(ev.sum() ** 2 / (ev ** 2).sum())

    print("\n  %-24s %8s %10s %10s" % ("contrast (condition-level)", "AUC", "exact p", "overlap"))
    print("  " + "-" * 60)
    out = {}
    for name, a, b in (("PRIMARY  ank_vel_max", sv, wv), ("secondary ank_rom", sr, wr)):
        A, P = auc(a, b), exact_p(a, b)
        lo, hi = min(b), max(b)
        ov = sum(1 for x in a if lo <= x <= hi)
        print("  %-24s %8.4f %10.4f %6d/%d" % (name, A, P, ov, len(a)))
        out[name.split()[-1]] = {"auc": A, "p_exact": P, "overlap": ov}

    p_primary = out["ank_vel_max"]["p_exact"]
    p_adj = p_primary * n_eff
    print("\n  effective tests (from correlation structure, computed before the contrast): %.2f"
          % n_eff)
    print("  PRIMARY exact p = %.4f  ->  x %.2f = %.4f   %s alpha = %.2f"
          % (p_primary, n_eff, p_adj, "PASSES" if p_adj < ALPHA else "FAILS", ALPHA))
    print("  (exact floor at 5v5 is 2/C(10,5) = %.4f -- this design cannot report a smaller p)"
          % (2.0 / 252))

    # (b) leave-one-out: AUC and overlap ONLY. Registered in advance.
    print("\n  LEAVE-ONE-OUT (condition dropped in turn) -- AUC and overlap only, NEVER a p-value:")
    print("     at 4v5 the exact floor is 0.0506, so no LOO contrast can clear alpha even under")
    print("     perfect separation. Registered in advance so absent p-values are not suppression.")
    for i, cond in enumerate(SPASTIC):
        sub = [v for j, v in enumerate(sv) if j != i]
        lo, hi = min(wv), max(wv)
        print("     drop %-9s AUC %.4f   overlap %d/%d"
              % (cond, auc(sub, wv), sum(1 for x in sub if lo <= x <= hi), len(sub)))

    print("\n  RATIFICATION CONDITION (a): the fifth spastic rung was placed at KV 0.075 KNOWING")
    print("     from archive data that separation is greatest at the mild end. Pre-data and")
    print("     declared -- it still favours the hypothesis, and that is stated, not hidden.")

    verdict = "PASSES" if p_adj < ALPHA else "FAILS -- discrimination claim ABANDONED per R45-S"
    print("\n" + "=" * 92)
    print("  PRIMARY VERDICT: %s" % verdict)
    print("=" * 92)

    res = {"primary": out["ank_vel_max"], "secondary": out["ank_rom"],
           "n_eff": n_eff, "p_adjusted": p_adj, "alpha": ALPHA, "verdict": verdict,
           "spastic_means": dict(zip(SPASTIC, sv)), "weak_means": dict(zip(WEAK, wv)),
           "references": {c: cond_mean(c, "vel") for c in REFERENCES}}
    o = os.path.abspath(os.path.join(HERE, "..", "paper", "CROSSED_RESULT.json"))
    json.dump(res, open(o, "w", encoding="utf-8"), indent=1)
    print("\nwritten: %s" % o)
    return 0


if __name__ == "__main__":
    sys.exit(main())
