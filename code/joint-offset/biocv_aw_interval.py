"""The largest triangulation effect in this paper is quoted without an interval.

Section 5 quotes 5.062 mm for confidence weighting against uniform at [pos:AW] -- the one
triangulation effect here that is not small -- and Table S8, which carries the exact intervals,
has no [pos:AW] rows at all. Every other headline magnitude is quoted with one. A second number
for the same contrast, 5.086 mm with an interval, appears in Table S2c, and nothing in the
submission says how the two relate.

Both are computable from the per-participant accumulator biocv_permutation_v2.py persists
(_persubj_v2.pkl), so neither needs the 3.3-hour rerun that regenerating that file would cost.
The interval is constructed by INVERTING the exact sign-flip test, which is the construction
Table S8 already uses: the set of shifts mu for which the two-sided exact p on (d - mu) is above
0.05, found by bisection on each side of the observed mean.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) REPRODUCES. If the mean of the eleven per-participant differences agrees with the published
      5.062 mm to within 0.01 mm, the exact interval computed here is reported and Table S8 gains
      its [pos:AW] rows.

  (2) DOES NOT REPRODUCE. If it disagrees by more than 0.01 mm, the disagreement is reported and
      the manuscript must say which number stands. A published figure that its own persisted
      accumulator does not reproduce is a defect whichever way it falls.

  (3) THE TWO NUMBERS. 5.086 is predicted here to be the difference of FRAME-POOLED means, which
      weights each participant by frame count, against 5.062 as the mean of eleven per-participant
      differences, which weights each participant equally. If the pooled computation returns
      5.086, that relation is established and both documents may state it. If it returns anything
      else, the relation is NOT established and the submission must say the two are unreconciled
      rather than assert a reconciliation that was not found.

  (4) An interval that excludes zero adds nothing to a verdict the sign-flip test already gave;
      it is reported for its WIDTH, which is what a reader needs and does not currently have.

-> D:/BioCV/BIOCV_AW_INTERVAL.txt
"""
import io
import itertools
import os
import pickle

import numpy as np

ACC = os.environ.get("BIOCV_PERSUBJ", "D:/BioCV/_persubj_v2.pkl")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_AW_INTERVAL.txt")
PUB_EFFECT = 5.062                 # Section 5 and Table 1(a)
PUB_POOLED = 5.086                 # Table S2c
ALPHA = 0.05

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


acc = pickle.load(open(ACC, "rb"))
SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def exact_p(d, mu=0.0):
    d = np.asarray(d, float) - mu
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    obs = abs(d.mean())
    return float((np.abs((S * d).mean(axis=1)) >= obs - 1e-15).sum()) / len(S)


def invert(d, alpha=ALPHA):
    """The shifts mu whose two-sided exact p exceeds alpha. Bisection each side of the mean."""
    d = np.asarray(d, float)
    c = float(d.mean())
    span = 4.0 * (np.abs(d - c).max() + abs(c) + 1.0)
    lo, hi = c - span, c
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if exact_p(d, m) > alpha:
            hi = m
        else:
            lo = m
    left = 0.5 * (lo + hi)
    lo, hi = c, c + span
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if exact_p(d, m) > alpha:
            lo = m
        else:
            hi = m
    return left, 0.5 * (lo + hi)


PAIRS = [("pos", "uniform", "conf", "[pos:AW] uniform vs confidence weighting", PUB_EFFECT),
         ("pos", "inv_d", "conf", "[pos:AW] 1/d alone vs confidence", 4.971),
         ("pos", "conf", "conf_d", "[pos:AW] does 1/d refine confidence?", 0.256),
         ("pos", "rep_conf", "objd_conf", "[pos:AW] reprojection vs object-space criterion", 0.332)]

out("EXACT INTERVALS FOR THE [pos:AW] CONTRASTS, FROM THE PERSISTED ACCUMULATOR")
out("")
out("Effect = first arm minus second, the order each label names, in millimetres. Intervals are")
out("exact 95%, constructed by inverting the two-sided sign-flip test over all 2^11 = 2048 sign")
out("patterns -- the same construction as Table S8.")
out("")
out(f"{'contrast':<54}{'n':>3}{'effect':>9}{'published':>11}{'exact 95% interval':>26}{'width':>8}")

rows = []
for lev, a, b, lab, pub in PAIRS:
    ma, mb = acc[(lev, a)], acc[(lev, b)]
    pids = sorted(set(ma) & set(mb))
    d = np.array([ma[p][0] / ma[p][1] - mb[p][0] / mb[p][1] for p in pids], float)
    lo, hi = invert(d)
    rows.append((lab, len(d), float(d.mean()), pub, lo, hi, d, pids))
    out(f"{lab:<54}{len(d):>3}{d.mean():>+9.3f}{pub:>+11.3f}"
        f"{f'[{lo:+.3f}, {hi:+.3f}]':>26}{hi - lo:>8.3f}")

out("")
lab, n, eff, pub, lo, hi, d, pids = rows[0]
out("=== VERDICT (1)/(2), against the rule fixed in this file's header ===")
if abs(eff - pub) <= 0.01:
    out(f"(1) REPRODUCES: {eff:+.3f} against the published {pub:+.3f}, within 0.01 mm. The exact")
    out(f"    95% interval on the paper's largest triangulation effect is [{lo:+.3f}, {hi:+.3f}] mm,")
    out(f"    a width of {hi - lo:.3f} mm, and Table S8 gains its [pos:AW] rows.")
else:
    out(f"(2) DOES NOT REPRODUCE: {eff:+.3f} against the published {pub:+.3f}, a gap of")
    out(f"    {abs(eff - pub):.3f} mm. The manuscript must say which number stands.")

# ---- the second number: frame-pooled rather than per-participant ----
ma, mb = acc[("pos", "uniform")], acc[("pos", "conf")]
pids = sorted(set(ma) & set(mb))
pool_a = sum(ma[p][0] for p in pids) / sum(ma[p][1] for p in pids)
pool_b = sum(mb[p][0] for p in pids) / sum(mb[p][1] for p in pids)
pooled = pool_a - pool_b
out("")
out("=== VERDICT (3): are 5.062 and 5.086 the same contrast weighted two ways? ===")
out(f"Frame-pooled means: uniform {pool_a:.3f} mm, confidence {pool_b:.3f} mm, difference "
    f"{pooled:+.3f} mm.")
out(f"Per-participant mean of differences: {eff:+.3f} mm.")
if abs(pooled - PUB_POOLED) <= 0.01:
    out(f"ESTABLISHED: the pooled computation returns {pooled:.3f}, matching the {PUB_POOLED} of")
    out("    Table S2c. The two published figures are the same contrast under two weightings of")
    out("    the participants -- equally, and by frame count -- and both documents may say so.")
else:
    out(f"NOT ESTABLISHED: the pooled computation returns {pooled:.3f}, not the {PUB_POOLED} of")
    out("    Table S2c. The relation is not what this file predicted, so the submission must")
    out("    report the two figures as unreconciled rather than assert a reconciliation.")

out("")
out(f"{'participant':>12}{'uniform mm':>12}{'confidence mm':>15}{'difference':>12}")
for p in pids:
    out(f"{p:>12}{ma[p][0] / ma[p][1]:>12.3f}{mb[p][0] / mb[p][1]:>15.3f}"
        f"{ma[p][0] / ma[p][1] - mb[p][0] / mb[p][1]:>+12.3f}")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
