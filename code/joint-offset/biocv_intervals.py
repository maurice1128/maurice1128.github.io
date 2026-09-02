"""Exact intervals for the effects the manuscript quotes.

A reviewer's objection: the paper quotes effects to three decimals throughout and puts none of them
in an interval, while the machinery to do so -- inverting the exact sign-flip test -- is already
used for the null angle contrasts of Table S3k. A sign-flip test at the 0.000977 floor certifies
only that all eleven participants agreed in DIRECTION; it says nothing about magnitude, and a
reader deciding whether 0.2 mm matters needs the interval.

Nothing is re-run. `_persubj_round5.pkl` holds, per (outcome, arm), each participant's summed error
and count, which is exactly the inferential unit the paper uses. Subsets are the mean of their
member joints -- verified against the published values: {knee, ankle} at matched k = 2 is
(-0.655 + 0.219) / 2 = -0.218, and {hip, ankle} is (0.530 + 0.219) / 2 = +0.374, both to the digit.

The interval is the set of shifts the exact test does not reject at alpha = 0.10, found by
bisection on each side and checked against a coarse grid, because monotonicity of the sign-flip p
in the shift is assumed rather than proved.

-> D:/BioCV/BIOCV_INTERVALS.txt
"""
import io
import itertools
import pickle

import numpy as np

SRC = "D:/BioCV/_persubj_round5.pkl"
SRC2 = "D:/BioCV/_persubj_v2.pkl"   # holds the lm_* arms of the published GN contrast
OUTF = "D:/BioCV/BIOCV_INTERVALS.txt"

acc = pickle.load(open(SRC, "rb"))
acc2 = {}
import os
if os.path.exists(SRC2):
    acc2 = pickle.load(open(SRC2, "rb"))
    for k, v in acc2.items():
        acc.setdefault(k, v)
# Some contrasts exist in BOTH stores on slightly different observation sets. An interval must
# be computed on the accumulation that produced the PUBLISHED point estimate, or Table S8's
# claim to reproduce those values is false: the matched-k angle rows read -0.089 (p = 0.0068)
# in the m = 50 family and -0.091 (p = 0.0039) in the round-5 store, which is not rounding.
FROM_V2 = {"criterion at matched k=1 [thigh-shank]",
           "criterion at matched k=2 [thigh-shank]",
           "dose k=1, reprojection [thigh-shank]", "dose k=2, reprojection [thigh-shank]",
           "dose k=3, reprojection [thigh-shank]", "dose k=1, object-space [thigh-shank]",
           "dose k=2, object-space [thigh-shank]", "dose k=3, object-space [thigh-shank]"}
SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


_STORE = acc


def sm(key, arm):
    return {p: v[0] / v[1] for p, v in _STORE[(key, arm)].items() if v[1] > 0}


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def exact_ci(d, alpha=0.10):
    """Shifts the test does not reject, by bisection, then checked on a grid for contiguity."""
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
        return (np.nan, np.nan, "point estimate itself rejected")
    hi = edge(mu, mu + span)
    lo = edge(mu, mu - span)
    grid = np.linspace(lo - 0.1 * span, hi + 0.1 * span, 121)
    inside = [ok(g) for g in grid]
    first, last = inside.index(True), len(inside) - 1 - inside[::-1].index(True)
    contiguous = all(inside[first:last + 1])
    return (lo, hi, "" if contiguous else "NON-CONTIGUOUS on the grid check")


def diff(key, a, b):
    ma, mb = sm(key, a), sm(key, b)
    ps = sorted(set(ma) & set(mb))
    return np.array([ma[p] - mb[p] for p in ps])


def subset(js, a, b):
    """A subset effect is the mean over its member joints, per participant."""
    per = [diff(j, a, b) for j in js]
    return np.mean(per, axis=0)


# (label, joints or outcome, arm A, arm B). POSITIVE = the SECOND-NAMED arm is better.
ROWS = [
    ("criterion at matched k=2 [hip]", ("hip",), "mk2_re", "mk2_ob"),
    ("criterion at matched k=2 [knee]", ("knee",), "mk2_re", "mk2_ob"),
    ("criterion at matched k=2 [ankle]", ("ankle",), "mk2_re", "mk2_ob"),
    ("criterion at matched k=2 {hip,knee,ankle}", ("hip", "knee", "ankle"), "mk2_re", "mk2_ob"),
    ("criterion at matched k=2 {knee,ankle}", ("knee", "ankle"), "mk2_re", "mk2_ob"),
    ("criterion at matched k=2 {hip,ankle}", ("hip", "ankle"), "mk2_re", "mk2_ob"),
    ("criterion at matched k=1 {knee,ankle}", ("knee", "ankle"), "mk1_re", "mk1_ob"),
    ("criterion at matched k=1 {hip,ankle}", ("hip", "ankle"), "mk1_re", "mk1_ob"),
    ("adaptive criterion [hip]", ("hip",), "rep_conf", "objd_conf"),
    ("adaptive criterion [knee]", ("knee",), "rep_conf", "objd_conf"),
    ("adaptive criterion [ankle]", ("ankle",), "rep_conf", "objd_conf"),
    ("adaptive criterion [pos:HKA]", ("posl",), "rep_conf", "objd_conf"),
    ("uniform -> confidence [hip]", ("hip",), "noRej_unif", "noRej_conf"),
    ("uniform -> confidence [knee]", ("knee",), "noRej_unif", "noRej_conf"),
    ("uniform -> confidence [ankle]", ("ankle",), "noRej_unif", "noRej_conf"),
    ("uniform -> confidence [pos:HKA]", ("posl",), "noRej_unif", "noRej_conf"),
    # The four the abstract, Results, Discussion and Conclusion are built on. Every one was
    # quoted as a magnitude, three of them bolded, with no interval anywhere in the submission.
    # The two position NULLS the Conclusion converts into "discarding buys no detectable position
    # accuracy under DLT". Accepting a null needs a bound, and these had none anywhere.
    ("adaptive reprojection rejection [pos:HKA]", ("posl",), "noRej_conf", "rep_conf"),
    ("adaptive object-space rejection [pos:HKA]", ("posl",), "noRej_conf", "objd_conf"),
    ("population offset table [pos:HKA]", ("posl",), "noRej_conf", "loo_corr"),
    ("population offset table [knee flex]", ("knee_flex",), "noRej_conf", "loo_corr"),
    ("GN: reprojection rejection [pos:HKA]", ("posl",), "lm_noRej", "lm_repRej"),
    ("GN: reprojection rejection [knee flex]", ("knee_flex",), "lm_noRej", "lm_repRej"),
    # the w^2-matched variant of the same contrast, quoted in Table 2c
    # Every surviving row of Table 2(a). Section 2.5 promises an interval wherever a magnitude is
    # quoted, and these are the magnitudes the Conclusion delivers; they had none at any level.
    ("uniform -> confidence [frontal thigh-shank]", ("knee_abd",), "noRej_unif", "noRej_conf"),
    ("uniform -> confidence [trunk-thigh]", ("hip_flex",), "noRej_unif", "noRej_conf"),
    ("adaptive reproj rejection [thigh-shank]", ("knee_flex",), "noRej_conf", "rep_conf"),
    ("adaptive reproj rejection [trunk-thigh]", ("hip_flex",), "noRej_conf", "rep_conf"),
    ("adaptive objd rejection [thigh-shank]", ("knee_flex",), "noRej_conf", "objd_conf"),
    ("adaptive objd rejection [trunk-thigh]", ("hip_flex",), "noRej_conf", "objd_conf"),
    ("criterion at matched k=1 [thigh-shank]", ("knee_flex",), "mk1_re", "mk1_ob"),
    ("criterion at matched k=2 [thigh-shank]", ("knee_flex",), "mk2_re", "mk2_ob"),
    ("population offset table [frontal thigh-shank]", ("knee_abd",), "noRej_conf", "loo_corr"),
    ("population offset table [trunk-thigh]", ("hip_flex",), "noRej_conf", "loo_corr"),
    # The six dose-response contrasts and the DLT-to-GN estimator change. The Conclusion and
    # Limitations use 0.75-0.80 deg as the largest cumulative effect and 1.384 mm as the estimator
    # cost, and neither had an interval at any level.
    ("dose k=1, reprojection [thigh-shank]", ("knee_flex",), "noRej_conf", "mk1_re"),
    ("dose k=2, reprojection [thigh-shank]", ("knee_flex",), "noRej_conf", "mk2_re"),
    ("dose k=3, reprojection [thigh-shank]", ("knee_flex",), "noRej_conf", "mk3_re"),
    ("dose k=1, object-space [thigh-shank]", ("knee_flex",), "noRej_conf", "mk1_ob"),
    ("dose k=2, object-space [thigh-shank]", ("knee_flex",), "noRej_conf", "mk2_ob"),
    ("dose k=3, object-space [thigh-shank]", ("knee_flex",), "noRej_conf", "mk3_ob"),
    # The abstract compares the offset against "no triangulation change we DECOMPOSED", and the
    # per-joint family of Table S3b contains four interventions -- not the estimator change, which
    # is the largest pooled position effect in the paper. Decomposing it here removes the
    # selection that qualifier was doing.
    ("DLT -> Gauss-Newton [hip]", ("hip",), "noRej_conf", "gn_w"),
    ("DLT -> Gauss-Newton [knee]", ("knee",), "noRej_conf", "gn_w"),
    ("DLT -> Gauss-Newton [ankle]", ("ankle",), "noRej_conf", "gn_w"),
    ("GN rejection, w2-matched [hip]", ("hip",), "gn_w", "gn_rej_w2"),
    ("GN rejection, w2-matched [knee]", ("knee",), "gn_w", "gn_rej_w2"),
    ("GN rejection, w2-matched [ankle]", ("ankle",), "gn_w", "gn_rej_w2"),
    ("DLT -> Gauss-Newton [pos:HKA]", ("posl",), "noRej_conf", "gn_w"),
    ("GN rejection, w2-matched [pos:HKA]", ("posl",), "gn_w", "gn_rej_w2"),
    ("GN rejection, w2-matched [knee flex]", ("knee_flex",), "gn_w", "gn_rej_w2"),
]

L = []


def out(s):
    print(s)
    L.append(s)


out("EXACT INTERVALS FOR THE QUOTED POSITION EFFECTS")
out("")
out("Exact sign-flip over 11 participants (2^11 = 2048 patterns). The interval is the set of")
out("shifts the same test does not reject at alpha = 0.10, obtained by inverting it -- the")
out("procedure already used for the null angle contrasts of Table S3k, applied here to the")
out("effects the manuscript quotes. POSITIVE = the SECOND-NAMED arm has the lower error.")
out("")
out("A subset row is the mean of its member joints, per participant, which is how the subsets are")
out("built throughout; the point estimates reproduce the published values exactly.")
out("")
out(f"{'contrast':<44}{'effect':>9}{'exact 95% CI':>22}{'exact 90% CI':>22}{'exact p':>10}")
for lab, js, a, b in ROWS:
    _STORE = acc2 if (lab in FROM_V2 and acc2) else acc
    d = subset(js, a, b) if len(js) > 1 else diff(js[0], a, b)
    lo5, hi5, n5 = exact_ci(d, alpha=0.05)
    lo, hi, note = exact_ci(d)
    note = note or n5
    out(f"{lab:<44}{d.mean():>+9.3f}   [{lo5:>+7.3f}, {hi5:>+7.3f}]   [{lo:>+7.3f}, {hi:>+7.3f}]"
        f"{exact_p(d):>10.4f}" + (("   " + note) if note else ""))
out("")
out("HOW TO READ THIS. The 95% interval is the one to read beside a 5%-level verdict, and it is")
out("what the manuscript quotes. The 90% interval is kept because it is the equivalence bound: it")
out("is the one that corresponds to two one-sided tests at 5%, and it is what the null rows are")
out("read against. A 90% interval excluding zero corresponds to p < 0.10, NOT p < 0.05 -- the")
out("matched k=2 ankle row excludes zero at p = 0.076 on the 90% interval and not on the 95%.")
out("Where an interval is wide relative to its point estimate, the effect's SIZE is not")
out("established even though its DIRECTION is, and no recommendation should be scaled to the")
out("point estimate.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
