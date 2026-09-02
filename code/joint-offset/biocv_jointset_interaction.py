"""Test the manuscript's central dissociation as an interaction, not as two verdicts.

The paper's headline is that the joint set you pool position error over changes the conclusion
of a contrast: significant on ankles and wrists, null on the hip, knee and ankle the angles are
built from. Until now that was established by putting a significant verdict next to a null one
-- which is exactly the inference the manuscript cites Gelman and Stern twice to condemn, and
which Section 2.5 claims every dissociation in the paper avoids. A cold reader found the gap:
of the nineteen interaction tests in the paper, all nineteen compare position against angle and
none compares one joint set against the other.

This runs the missing test. For each intervention available on both joint sets, and for each
participant, we form

    interaction_i = (effect on [pos:AW])_i / (baseline at [pos:AW])_i
                  - (effect on [pos:HKA])_i / (baseline at [pos:HKA])_i

so both arms are expressed as a fraction of that participant's own baseline error and the two
joint sets are on one dimensionless scale. The null is that an intervention changes the two
joint sets by the same fraction. The test is the same exact sign-flip over 2^11 = 2048 patterns
used everywhere else in the paper, and Benjamini-Hochberg is applied within this family.

Reading the result: a surviving interaction means the joint set genuinely changes the size of
the effect, and the manuscript's dissociation is established rather than inferred. A null means
we cannot show the two joint sets differ, and the headline must be restated as what it is -- a
change of verdict driven by precision as well as by effect size. We report whichever it is.

Input : D:/BioCV/_persubj_v2.pkl, written by biocv_permutation_v2.py
Output: D:/BioCV/BIOCV_JOINTSET_FDR.txt
"""
import io
import itertools
import pickle

import numpy as np

PKL = "D:/BioCV/_persubj_v2.pkl"
OUTF = "D:/BioCV/BIOCV_JOINTSET_FDR.txt"

# (label, AW baseline arm, AW treated arm, HKA baseline arm, HKA treated arm)
# The arm pairs are the ones biocv_permutation_v2.FAMILY runs on both levels. Each tuple is
# written so that the SECOND arm of each pair is the one whose error we hope is lower, matching
# the sign convention used throughout: positive effect = second-named arm better.
CONTRASTS = [
    ("uniform vs confidence weighting", "uniform", "conf", "noRej_unif", "noRej_conf"),
    ("matched k=1: reprojection vs object-space", "mk1_re", "mk1_ob", "mk1_re", "mk1_ob"),
    ("matched k=2: reprojection vs object-space", "mk2_re", "mk2_ob", "mk2_re", "mk2_ob"),
    ("matched k=3: reprojection vs object-space", "mk3_re", "mk3_ob", "mk3_re", "mk3_ob"),
    ("adaptive: reprojection vs object-space", "rep_conf", "objd_conf", "rep_conf", "objd_conf"),
    ("no rejection vs reprojection rejection", "conf", "rep_conf", "noRej_conf", "rep_conf"),
    ("no rejection vs object-space rejection", "conf", "objd_conf", "noRej_conf", "objd_conf"),
    # Added after a cold reader pointed out that the paper's only sign-reversal claim -- the
    # one contrast that is a significant GAIN on one joint set and a significant LOSS on the
    # other -- was the single dissociation never tested as an interaction, while the abstract
    # asserted that every claimed dissociation was. The arms are named differently at the two
    # levels but are the same intervention: confidence weighting, then confidence x 1/d.
    ("confidence vs confidence x 1/d weighting", "conf", "conf_d", "noRej_conf", "noRej_wd"),
]

acc = pickle.load(open(PKL, "rb"))
SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def means(level, arm):
    key = (level, arm)
    if key not in acc:
        return None
    return {p: v[0] / v[1] for p, v in acc[key].items() if v[1] > 0}


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    obs = abs(d.mean())
    null = np.abs((S * d).mean(axis=1))
    return float((null >= obs - 1e-15).sum()) / len(S)


rows, skipped = [], []
for label, aw_a, aw_b, hk_a, hk_b in CONTRASTS:
    A0, A1 = means("pos", aw_a), means("pos", aw_b)
    H0, H1 = means("posl", hk_a), means("posl", hk_b)
    if None in (A0, A1, H0, H1):
        missing = [f"{lv}/{arm}" for lv, arm, m in
                   (("pos", aw_a, A0), ("pos", aw_b, A1), ("posl", hk_a, H0), ("posl", hk_b, H1))
                   if m is None]
        skipped.append((label, ", ".join(missing)))
        continue
    pids = sorted(set(A0) & set(A1) & set(H0) & set(H1))
    if len(pids) < 4:
        skipped.append((label, f"only {len(pids)} participants in common"))
        continue
    daw = np.array([(A0[p] - A1[p]) / A0[p] * 100 for p in pids])
    dhk = np.array([(H0[p] - H1[p]) / H0[p] * 100 for p in pids])
    inter = daw - dhk
    rows.append((label, len(pids), daw.mean(), dhk.mean(), inter.mean(), exact_p(inter)))

if not rows:
    raise SystemExit("no contrast could be formed -- check the arm names against the pickle")

ps = [r[5] for r in rows]
m = len(ps)
order = sorted(range(m), key=lambda i: ps[i])
q = [0.0] * m
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    k = m - rank + 1
    prev = q[i] = min(prev, ps[i] * m / k)

L = []


def out(s):
    print(s)
    L.append(s)


out("DOES THE JOINT SET CHANGE THE EFFECT? -- [pos:AW] x [pos:HKA] INTERACTION")
out("")
out("Whether an intervention moves the two joint sets by different amounts. Per participant, the effect on ankles")
out("and wrists minus the effect on hip/knee/ankle, each as a percentage of that participant's")
out("own baseline error at that joint set. Positive interaction = the intervention does more for")
out("[pos:AW] than for [pos:HKA]. Exact sign-flip over 2^11 = 2048 patterns; BH within m = "
    f"{m}.")
out("")
out(f"{'contrast':<44}{'k':>3}{'dAW%':>9}{'dHKA%':>9}{'inter':>9}{'p':>9}{'BH q':>9}  verdict")
for (lab, k, da, dh, it, p), qq in sorted(zip(rows, q), key=lambda t: t[0][5]):
    v = "SURVIVES" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    out(f"{lab:<44}{k:>3}{da:>+9.2f}{dh:>+9.2f}{it:>+9.2f}{p:>9.4f}{qq:>9.4f}  {v}")

surv = sum(1 for qq in q if qq < 0.05)
raw = sum(1 for p in ps if p < 0.05)
out("")
out(f"{surv} of {m} survive BH; {raw} were significant unadjusted.")
if skipped:
    out("")
    out("Not testable from the stored per-participant means:")
    for lab, why in skipped:
        out(f"  {lab}  --  {why}")
out("")
out("HOW TO READ THIS. A surviving interaction means the joint set changes the size of the")
out("effect and the dissociation is established directly. A null means we cannot demonstrate")
out("that the two joint sets differ, and any claim that the joint set 'changes the answer' must")
out("be stated as a change of verdict -- which is a fact about significance, hence about")
out("precision as well as about effect size -- and not as a demonstrated difference in effect.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
