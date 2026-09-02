"""Is discarding position-neutral under DLT but not under Gauss-Newton, or are those two estimates?

Section 3.2 said "Discarding is position-neutral only under DLT". That sentence compares a null
(DLT: -0.005 mm, q = 0.964) with a significant effect (GN: +0.858 mm, q = 0.006) and reads the
difference between two verdicts as a difference between two effects -- the exact inference this
paper cites Gelman and Stern (2006) to forbid, and on which its whole interaction apparatus rests.
The claim was removed from the manuscript pending this test. This script runs it.

Both contrasts come from `_persubj_v2.pkl`, which holds the DLT arms and the lm_* Gauss-Newton
arms from ONE accumulation, so the two are on the same observations and the per-participant
difference is paired rather than assembled across runs.

THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.

  FAMILY. Two contrasts, declared here and not extended: the estimator-by-rejection interaction
  on [pos:HKA] position (mm) and on knee flexion (deg). BH within m = 2. This is a twelfth
  declared family and must be added to Table S4b and to the pooled-m sensitivity.

  (1) POSITION. If the interaction survives, "discarding costs position under Gauss-Newton and
      not under DLT" is a tested difference and Section 3.2 may say so. If it does not survive,
      the two estimator results stay as two estimates and the manuscript says only that.

  (2) ANGLE. The same test on knee flexion. The paper's account says discarding costs the angle
      under BOTH estimators, so here the PREDICTION IS A NULL, and a surviving interaction is
      evidence against the paper. It is reported either way.

  (3) SCALE. Both outcomes are absolute (mm, deg) within a single outcome, so no relative-scale
      caveat applies; this is a difference of differences in the outcome's own units.

  (4) DIRECTION. Positive = rejection helps MORE (or hurts LESS) under Gauss-Newton than under
      DLT, matching the sign convention of the component contrasts.

-> D:/BioCV/BIOCV_EST_REJ_INTERACTION.txt
"""
import io
import itertools
import os
import pickle

import numpy as np

SRC = "D:/BioCV/_persubj_v2.pkl"
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_EST_REJ_INTERACTION.txt")

acc = pickle.load(open(SRC, "rb"))


def per(outcome, arm):
    return {p: v[0] / v[1] for p, v in acc[(outcome, arm)].items() if v[1] > 0}


def exact_p(d):
    d = np.asarray(d, float)
    S = np.array(list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def bh(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for r in range(m - 1, -1, -1):
        prev = min(prev, ps[o[r]] * m / (r + 1))
        q[o[r]] = prev
    return q


def exact_ci(d, alpha=0.10):
    d = np.asarray(d, float)
    mu = d.mean()
    span = max(np.abs(d).max() * 3, 1e-9)

    def ok(x):
        return exact_p(d - x) > alpha

    def edge(lo, hi):
        for _ in range(60):
            m = 0.5 * (lo + hi)
            if ok(m):
                lo = m
            else:
                hi = m
        return 0.5 * (lo + hi)

    if not ok(mu):
        return (np.nan, np.nan)
    return (edge(mu, mu - span), edge(mu, mu + span))


ROWS = [("[pos:HKA] position", "posl", "mm"),
        ("knee flexion", "knee_flex", "deg")]

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


out("ESTIMATOR-BY-REJECTION INTERACTION: is discarding position-neutral under DLT ONLY?")
out("")
out("Rejection effect under each estimator, per participant, then the difference of the two.")
out("POSITIVE component = rejection LOWERS the error. POSITIVE interaction = rejection does")
out("better under Gauss-Newton than under DLT. Same accumulation, so the pairing is exact.")
out("")

recs, ps = [], []
for lab, outcome, unit in ROWS:
    dlt_a, dlt_b = per(outcome, "noRej_conf"), per(outcome, "rep_conf")
    gn_a, gn_b = per(outcome, "lm_noRej"), per(outcome, "lm_repRej")
    pids = sorted(set(dlt_a) & set(dlt_b) & set(gn_a) & set(gn_b))
    d_dlt = np.array([dlt_a[p] - dlt_b[p] for p in pids])
    d_gn = np.array([gn_a[p] - gn_b[p] for p in pids])
    inter = d_gn - d_dlt
    recs.append((lab, unit, len(pids), d_dlt, d_gn, inter))
    ps.append(exact_p(inter))
qs = bh(ps)

out(f"{'outcome':<22}{'n':>4}{'DLT':>10}{'GN':>10}{'interaction':>14}"
    f"{'exact 95% CI':>22}{'exact 90% CI':>22}{'p':>9}{'q':>9}   verdict")
for (lab, unit, n, d_dlt, d_gn, inter), p_, q_ in zip(recs, ps, qs):
    lo5, hi5 = exact_ci(inter, alpha=0.05)
    lo, hi = exact_ci(inter)
    v = "SURVIVES" if q_ < 0.05 else "n.s."
    out(f"{lab:<22}{n:>4}{d_dlt.mean():>+10.3f}{d_gn.mean():>+10.3f}{inter.mean():>+14.3f}"
        f"   [{lo5:>+7.3f}, {hi5:>+7.3f}]   [{lo:>+7.3f}, {hi:>+7.3f}]{p_:>9.4f}{q_:>9.4f}   {v}")
out("")
out("Units: position in mm, angle in deg. The 95% interval is the one to read beside a")
out("5%-level verdict; the 90% interval is the equivalence bound for the null row.")
out("BH within a declared family of two, fixed in this file's header before the numbers existed.")
out("")

pos_q, ang_q = qs[0], qs[1]
out("=== VERDICTS, against the rule fixed in this file's header ===")
out(f"(1) POSITION, q = {pos_q:.4f}  ->  "
    + ("the estimator changes what discarding does to position; Section 3.2 may state it as a "
       "tested difference" if pos_q < 0.05 else
       "NOT a tested difference; the two estimator results stay as two estimates"))
out(f"(2) ANGLE, q = {ang_q:.4f}  ->  "
    + ("AGAINST THE PAPER: the angle cost of discarding differs by estimator, which the account "
       "in Section 3.2 does not predict" if ang_q < 0.05 else
       "no evidence the angle cost differs by estimator, as the paper's account predicts"))

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
