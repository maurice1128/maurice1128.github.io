"""The Gauss-Newton rejection contrast, with the baselines the manuscript quotes.

A numeric audit found that the manuscript asserted in four places that discarding observations
is "position-neutral", while its own m = 50 family contains

    [pos:HKA] GN: no rejection vs reprojection rejection   +0.858   q = 0.0061   SURVIVES
    knee flex GN: no rejection vs reprojection rejection   -0.169   q = 0.0282   SURVIVES

The FAMILY tuple is ("posl", "lm_noRej", "lm_repRej"), so a positive effect means the rejection
arm has the lower error: with the estimator changed from weighted DLT to Gauss-Newton, rejection
significantly IMPROVES lower-limb position and significantly DEGRADES knee flexion, on the same
trials. That is the paper's thesis in its cleanest form and it was not being claimed; the four
"position-neutral" statements are specific to the DLT estimator.

Section 3.2 now quotes these effects as percentages of their own baselines. This script emits
those baselines so the figures have a producer instead of being computed by hand.

Input : D:/BioCV/_persubj.pkl, _persubj_round5.pkl, _persubj_v2.pkl (whichever hold the lm_* arms)
Output: D:/BioCV/BIOCV_GN_DISSOCIATION.txt
"""
import io
import itertools
import pickle

import numpy as np

OUTF = "D:/BioCV/BIOCV_GN_DISSOCIATION.txt"
PKLS = ["D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl", "D:/BioCV/_persubj_v2.pkl"]

# (level, baseline arm, treated arm, unit, label)
CONTRASTS = [
    ("posl", "lm_noRej", "lm_repRej", "mm", "[pos:HKA] GN: no rejection vs reprojection rejection"),
    ("posl", "lm_noRej", "lm_objdRej", "mm", "[pos:HKA] GN: no rejection vs object-space rejection"),
    ("knee_flex", "lm_noRej", "lm_repRej", "deg", "knee flexion, GN: no rejection vs reprojection"),
    ("knee_flex", "lm_noRej", "lm_objdRej", "deg", "knee flexion, GN: no rejection vs object-space"),
    ("hip_flex", "lm_noRej", "lm_repRej", "deg", "hip flexion, GN: no rejection vs reprojection"),
    ("knee_abd", "lm_noRej", "lm_repRej", "deg", "frontal knee, GN: no rejection vs reprojection"),
]

acc = {}
for f in PKLS:
    try:
        acc.update(pickle.load(open(f, "rb")))
    except OSError:
        pass

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


L = []


def out(s):
    print(s)
    L.append(s)


out("GAUSS-NEWTON REJECTION CONTRAST -- BASELINES AND RELATIVE EFFECTS")
out("")
out("POSITIVE effect = the rejection arm has the LOWER error, matching the FAMILY tuple")
out("(level, lm_noRej, lm_repRej) in biocv_permutation_v2.py. q-values are those of the m = 50")
out("family in BIOCV_PERM_V3.txt; the p reprinted here is recomputed from the per-participant")
out("means as a check that the same contrast is being described.")
out("")
out(f"{'contrast':<54}{'baseline':>10}{'effect':>10}{'rel %':>9}{'p':>9}")

missing = []
for level, a, b, unit, label in CONTRASTS:
    if (level, a) not in acc or (level, b) not in acc:
        missing.append(label)
        continue
    A = {p: v[0] / v[1] for p, v in acc[(level, a)].items() if v[1] > 0}
    B = {p: v[0] / v[1] for p, v in acc[(level, b)].items() if v[1] > 0}
    ps = sorted(set(A) & set(B))
    base = np.mean([A[p] for p in ps])
    eff = np.mean([A[p] - B[p] for p in ps])
    rel = np.mean([(A[p] - B[p]) / A[p] for p in ps]) * 100
    p = exact_p(np.array([A[q] - B[q] for q in ps]))
    out(f"{label:<54}{base:>10.3f}{eff:>+10.3f}{rel:>+9.2f}{p:>9.4f}")

out("")
if missing:
    out("Not available in the stored per-participant means:")
    for x in missing:
        out("  " + x)
    out("")
out("READ: the first and third rows are the pair Section 3.2 quotes. Position improves and the")
out("knee angle degrades, both surviving multiplicity correction in the m = 50 family, under the")
out("same estimator on the same trials. The four statements elsewhere in the paper that discarding")
out("is position-neutral hold for weighted DLT and not for this estimator.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
