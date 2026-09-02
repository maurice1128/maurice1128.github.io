"""The position-versus-angle interaction family, recomputed and BH-corrected.

The family size is whatever INTER below contains and is printed in the output; it is not
restated in prose here, because every place it was restated went stale when the family grew.

This replaces a version that read pre-computed effect sizes out of two result files. A cold
reader found two defects in that arrangement, and recomputing from the per-participant means
fixes both:

1. WRONG DENOMINATOR. `biocv_equivalence.py` formed each participant's relative effect as
   (a - b) / b -- dividing by the TREATED arm. Table 2(c)'s own scale note says the effects are
   "each participant's effect divided by that participant's own BASELINE error", and
   `biocv_jointset_interaction.py` divides by the baseline arm. The same contrast therefore
   appeared as +3.21% in one table and +3.10% in another, with a note describing only one of
   them. Dividing by the baseline arm is the stated convention and the one used here; because
   the interaction is a difference of two such ratios and the p-value is computed on that
   difference, the denominator affects the test and not only the presentation.

2. BH ON ROUNDED p. The old version parsed p-values already rounded to four decimals out of a
   text file, so q = 0.0020 x 19/5 = 0.0076 was printed where the exact 4/2048 gives 0.0074.
   The other three families were corrected on exact p. All four now share one routine.

The family is kept separate from the m = 50 contrasts because it answers a different question --
not "is there an effect on this outcome?" but "do the two outcomes move differently?". The
consequence of pooling all four families instead is reported by pooled_family_sensitivity.py.

Inputs : D:/BioCV/_persubj.pkl, D:/BioCV/_persubj_round5.pkl (per-participant means)
Output : D:/BioCV/BIOCV_INTERACTION_FDR.txt
"""
import io
import itertools
import pickle

import numpy as np

OUTF = "D:/BioCV/BIOCV_INTERACTION_FDR.txt"
PKLS = ["D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl",
        "D:/BioCV/_persubj_v2.pkl"]   # the lm_* Gauss-Newton arms live here

# (baseline arm, treated arm, angle level, label)
INTER = [
    ("noRej_unif", "noRej_conf", "knee_flex", "uniform->confidence weighting [knee flex]"),
    ("noRej_unif", "noRej_conf", "knee_abd", "uniform->confidence weighting [frontal knee]"),
    ("noRej_unif", "noRej_conf", "hip_flex", "uniform->confidence weighting [hip flex]"),
    ("rep_conf", "objd_conf", "knee_flex", "reproj->object-space criterion [knee flex]"),
    ("rep_conf", "objd_conf", "knee_abd", "reproj->object-space criterion [frontal knee]"),
    ("mk1_re", "mk1_ob", "knee_flex", "criterion at matched k=1 [knee flex]"),
    ("mk2_re", "mk2_ob", "knee_flex", "criterion at matched k=2 [knee flex]"),
    ("mk3_re", "mk3_ob", "knee_flex", "criterion at matched k=3 [knee flex]"),
    ("noRej_conf", "noRej_wd", "knee_abd", "confidence->confidence x 1/d [frontal knee]"),
    ("noRej_conf", "noRej_wd", "hip_flex", "confidence->confidence x 1/d [hip flex]"),
    ("noRej_conf", "rep_conf", "knee_flex", "no rejection->reproj rejection [knee flex]"),
    ("noRej_conf", "objd_conf", "knee_flex", "no rejection->objd rejection [knee flex]"),
    ("noRej_conf", "objd_conf", "hip_flex", "no rejection->objd rejection [hip flex]"),
    ("noRej_conf", "loo_corr", "knee_flex", "LOO offset correction [knee flex]"),
    ("noRej_conf", "loo_corr", "knee_abd", "LOO offset correction [frontal knee]"),
    ("noRej_conf", "loo_corr", "hip_flex", "LOO offset correction [hip flex]"),
    ("gn_w", "gn_rej_w2", "knee_flex", "GN: rejection (w^2-matched) [knee flex]"),
    # Both arms are Gauss-Newton; only the objective differs. The old label said "DLT -> GN",
    # which named an arm the tuple does not contain and made the row look like Table 1a's
    # -1.384 mm DLT-versus-GN contrast, which is not in this family at all.
    ("gn_w2", "gn_w", "knee_flex", "GN objective: w^2-matched -> unmatched (w) [knee flex]"),
    ("noRej_conf", "gn_w2", "knee_flex", "DLT -> GN w^2-matched [knee flex]"),
    # The Gauss-Newton pair the Results and Discussion actually describe is lm_noRej ->
    # lm_repRej. A watchdog audit found that what had been enrolled in this family was
    # gn_w -> gn_rej_w2 -- same baseline arm, DIFFERENT treated arm -- so the dissociation
    # the paper reports had never been interaction-tested while the abstract said every
    # claimed dissociation had been. The described pair is added here.
    ("lm_noRej", "lm_repRej", "knee_flex", "GN: no rejection -> reproj rejection [knee flex]"),
]

acc = {}
for f in PKLS:
    try:
        acc.update(pickle.load(open(f, "rb")))
    except OSError:
        pass

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def sm(level, arm):
    key = (level, arm)
    if key not in acc:
        return None
    return {p: v[0] / v[1] for p, v in acc[key].items() if v[1] > 0}


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    obs = abs(d.mean())
    return float((np.abs((S * d).mean(axis=1)) >= obs - 1e-15).sum()) / len(S)


rows, skipped = [], []
for base, trt, ang, label in INTER:
    pa, pb = sm("posl", base), sm("posl", trt)
    aa, ab = sm(ang, base), sm(ang, trt)
    if None in (pa, pb, aa, ab):
        skipped.append(label)
        continue
    ps = sorted(set(pa) & set(pb) & set(aa) & set(ab))
    if len(ps) < 4:
        skipped.append(label + f" (only {len(ps)} participants)")
        continue
    # divide by the BASELINE arm, as Table 2(c) states
    rp = np.array([(pa[p] - pb[p]) / pa[p] for p in ps])
    ra = np.array([(aa[p] - ab[p]) / aa[p] for p in ps])
    dif = rp - ra
    rows.append((label, 100 * rp.mean(), 100 * ra.mean(), 100 * dif.mean(), exact_p(dif)))

if skipped:
    raise SystemExit("could not form: " + "; ".join(skipped))
if len(rows) != 20:
    raise SystemExit(f"expected 20 interactions, formed {len(rows)}")

ps_ = [r[4] for r in rows]
m = len(ps_)
order = sorted(range(m), key=lambda i: ps_[i])
q = [0.0] * m
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    k = m - rank + 1
    prev = q[i] = min(prev, ps_[i] * m / k)

L = []


def out(s):
    print(s)
    L.append(s)


out("BENJAMINI-HOCHBERG OVER THE INTERACTION FAMILY")
out(f"Family size m = {m}. Recomputed from the per-participant means in {', '.join(PKLS)},")
out("so the correction runs on exact sign-flip p-values rather than on values already rounded")
out("to four decimals, matching the other three families.")
out("")
out("Interaction = relative position effect minus relative angle effect, per participant, each")
out("expressed as a fraction of that participant's own BASELINE error -- the arm named first in")
out("the contrast. Position is measured at [pos:HKA], the hip, knee and ankle the angle is built")
out("from.")
out("")
out(f"{'intervention':<48}{'dpos%':>8}{'dang%':>8}{'inter':>8}{'p':>9}{'BH q':>9}  verdict")
for (lab, dp, da, it, p), qq in sorted(zip(rows, q), key=lambda t: t[0][4]):
    v = "SURVIVES" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    out(f"{lab:<48}{dp:>+8.2f}{da:>+8.2f}{it:>+8.2f}{p:>9.4f}{qq:>9.4f}  {v}")

surv = sum(1 for qq in q if qq < 0.05)
raw = sum(1 for p in ps_ if p < 0.05)
out("")
out(f"{surv} of {m} survive BH; {raw} were significant unadjusted.")
if surv == raw:
    out("Every interaction significant unadjusted also survives correction.")
else:
    out("Contrasts significant unadjusted that do not survive correction are exploratory.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
