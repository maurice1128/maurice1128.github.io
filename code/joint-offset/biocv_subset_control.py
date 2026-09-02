"""Is it the joint SET, or is it arms versus legs?

The paper contrasts [pos:AW] (ankles + wrists) with [pos:HKA] (hip, knee, ankle) and concludes
that the joint set on which position error is summarised decides the verdict. A cold reader
pointed out that those two sets differ in more than membership: upper versus lower limb, different
occlusion and distance regimes, and baselines of 16.6 against 28.5 mm with the hip at 37.7-39.3 mm
dominating one of them. Every joint-set interaction in the paper is therefore confounded with body
region, and the inverse-distance sign reversal is exactly what a geometry story would predict --
distal peripheral keypoints helped, deep hip centres harmed.

This is the control. It compares subsets WITHIN the lower limb, so body region, occlusion regime
and camera geometry are held constant and only the membership of the set changes:

    {hip, knee, ankle}   the set the paper uses
    {knee, ankle}        drop the hip
    {hip, knee}          drop the ankle
    {hip, ankle}         drop the knee

Three parts, each its own declared multiplicity family.

PART A tests every pair of subsets against every other, not only each reduced set against the full
one. The earlier version tested only the 15 full-versus-reduced differences, which meant the
manuscript sentence "harmful on knee+ankle, beneficial on hip+ankle" was resting on a comparison of
two separate significance verdicts -- exactly what section 2.5 forbids, citing Gelman and Stern
(2006), and exactly what the paper accuses the field of doing. The direct contrast is now tested.
Six pairs x five interventions = 30.

PART B repeats Part A on the absolute effect in mm rather than on each subset's own baseline. A
relative-effect contrast has an arbitrary denominator, and its null -- equal FRACTIONAL change --
has no mechanical warrant; an intervention with an identical absolute effect at two subsets with
different baselines produces a nonzero relative interaction by construction. The mm version has no
denominator. Where the two disagree, the difference is a scale artefact and must be reported as one.

PART C tests each subset's own effect against zero: what a validation study would report had it
chosen that subset. This was previously printed with uncorrected p and belonged to no declared
family, which put the paper's own headline numbers to a looser standard than everything else in it.
Twenty tests, corrected within themselves.

Output: D:/BioCV/BIOCV_SUBSET_CONTROL.txt
"""
import io
import itertools
import pickle

import numpy as np

OUTF = "D:/BioCV/BIOCV_SUBSET_CONTROL.txt"
PKLS = ["D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl", "D:/BioCV/_persubj_v2.pkl"]

SUBSETS = [
    ("hip+knee+ankle", ("hip", "knee", "ankle")),
    ("knee+ankle", ("knee", "ankle")),
    ("hip+knee", ("hip", "knee")),
    ("hip+ankle", ("hip", "ankle")),
]

# (label, baseline arm, treated arm) -- the interventions for which per-joint accumulators exist.
# DEPLOYABLE marks an arm a validation study could actually run: matched-k is a retention control
# and the 1/d arms use ground-truth distances, so a verdict change on those cannot carry the
# paper's practical claim. Reviewer 2 found that every verdict change in Table 1(a) sits on a
# non-deployable arm; whether any deployable arm changes verdict is settled here, not asserted.
CONTRASTS = [
    ("uniform vs confidence weighting", "noRej_unif", "noRej_conf", True),
    ("criterion, adaptive rejection", "rep_conf", "objd_conf", True),
    ("criterion at matched k=1", "mk1_re", "mk1_ob", False),
    ("criterion at matched k=2", "mk2_re", "mk2_ob", False),
    ("LOO offset correction", "noRej_conf", "loo_corr", True),
]
DEPLOYABLE = {c[0]: c[3] for c in CONTRASTS}

acc = {}
for f in PKLS:
    try:
        acc.update(pickle.load(open(f, "rb")))
    except OSError:
        pass

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def subset_means(joints, arm):
    """Per-participant mean error over a set of joints, weighted by observation count."""
    if any((j, arm) not in acc for j in joints):
        return None
    pids = set.intersection(*[set(acc[(j, arm)]) for j in joints])
    out = {}
    for p in pids:
        s = sum(acc[(j, arm)][p][0] for j in joints)
        n = sum(acc[(j, arm)][p][1] for j in joints)
        if n:
            out[p] = s / n
    return out


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def bh(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))
    return q


# Per intervention, per subset: the per-participant effect on that subset, both as a fraction of
# that participant's own baseline for that subset (rel) and in mm (abs).
eff_rel, eff_abs, skipped = {}, {}, []
for label, a, b, _dep in CONTRASTS:
    for sname, joints in SUBSETS:
        A, B = subset_means(joints, a), subset_means(joints, b)
        if A is None or B is None:
            skipped.append(f"{label} / {sname}")
            continue
        pids = sorted(set(A) & set(B))
        if len(pids) < 4:
            skipped.append(f"{label} / {sname} (only {len(pids)} participants)")
            continue
        eff_rel[(label, sname)] = {p: (A[p] - B[p]) / A[p] * 100 for p in pids}
        eff_abs[(label, sname)] = {p: A[p] - B[p] for p in pids}

PAIRS = [(x[0], y[0]) for x, y in itertools.combinations(SUBSETS, 2)]


def pairwise(store):
    """Every pair of subsets, per intervention, on whichever scale `store` holds."""
    rows = []
    for label, _a, _b, _dep in CONTRASTS:
        for s1, s2 in PAIRS:
            if (label, s1) not in store or (label, s2) not in store:
                continue
            pids = sorted(set(store[(label, s1)]) & set(store[(label, s2)]))
            if len(pids) < 4:
                continue
            d = np.array([store[(label, s1)][p] - store[(label, s2)][p] for p in pids])
            rows.append((label, s1, s2,
                         float(np.mean([store[(label, s1)][p] for p in pids])),
                         float(np.mean([store[(label, s2)][p] for p in pids])),
                         float(d.mean()), exact_p(d)))
    return rows


rel_rows = pairwise(eff_rel)
abs_rows = pairwise(eff_abs)
if not rel_rows:
    raise SystemExit("no subset contrast could be formed -- check the arm names against the pickles")
rel_q = bh([r[6] for r in rel_rows])
abs_q = bh([r[6] for r in abs_rows])

# PART C: each subset's own effect against zero.
own_rows = []
for label, _a, _b, _dep in CONTRASTS:
    for sname, _joints in SUBSETS:
        if (label, sname) not in eff_abs:
            continue
        d = np.array(list(eff_abs[(label, sname)].values()))
        r = float(np.mean(list(eff_rel[(label, sname)].values())))
        own_rows.append((label, sname, float(d.mean()), r, exact_p(d)))
own_q = bh([r[4] for r in own_rows])

L = []


def out(s):
    print(s)
    L.append(s)


def verdict(p, q):
    return "SURVIVES" if q < 0.05 else ("raw only" if p < 0.05 else "n.s.")


out("IS IT THE JOINT SET, OR IS IT ARMS VERSUS LEGS?")
out("")
out("Subsets of the SAME lower limb, so body region, occlusion regime and camera geometry are held")
out("constant and only the membership of the set changes. Every subset, including the full")
out("three-joint one, is rebuilt from the same per-joint accumulators. Exact sign-flip over")
out("2^11 = 2048 sign patterns throughout. 'dep' marks an intervention a validation study could")
out("actually run: matched-k is a retention control and is not deployable.")
out("")
out(f"=== PART A. DOES MEMBERSHIP CHANGE THE EFFECT? relative scale, BH within m = {len(rel_rows)} ===")
out("Each participant's effect as a percentage of that participant's own baseline for that subset;")
out("the tested quantity is the difference between two subsets. Every pair is tested, so the")
out("manuscript never has to compare two separate significance verdicts (Gelman and Stern, 2006).")
out("")
out(f"{'intervention':<34}{'dep':>4}  {'subset A':<16}{'subset B':<16}"
    f"{'A%':>8}{'B%':>8}{'diff':>8}{'p':>9}{'BH q':>9}  verdict")
for (lab, s1, s2, v1, v2, d, p), qq in sorted(zip(rel_rows, rel_q), key=lambda t: t[0][6]):
    out(f"{lab:<34}{('y' if DEPLOYABLE[lab] else 'n'):>4}  {s1:<16}{s2:<16}"
        f"{v1:>+8.2f}{v2:>+8.2f}{d:>+8.2f}{p:>9.4f}{qq:>9.4f}  {verdict(p, qq)}")
out("")
out(f"{sum(1 for q in rel_q if q < 0.05)} of {len(rel_rows)} survive BH.")
out("")

out(f"=== PART B. THE SAME CONTRASTS IN mm, BH within m = {len(abs_rows)} ===")
out("Part A's null is equal FRACTIONAL change, which has no mechanical warrant: two subsets with")
out("different baselines can differ fractionally while the intervention moves them by identical")
out("absolute amounts. This part removes the denominator. A difference that survives in Part A but")
out("not here is a scale artefact rather than a membership effect.")
out("")
out(f"{'intervention':<34}{'dep':>4}  {'subset A':<16}{'subset B':<16}"
    f"{'A mm':>8}{'B mm':>8}{'diff':>8}{'p':>9}{'BH q':>9}  verdict")
for (lab, s1, s2, v1, v2, d, p), qq in sorted(zip(abs_rows, abs_q), key=lambda t: t[0][6]):
    out(f"{lab:<34}{('y' if DEPLOYABLE[lab] else 'n'):>4}  {s1:<16}{s2:<16}"
        f"{v1:>+8.3f}{v2:>+8.3f}{d:>+8.3f}{p:>9.4f}{qq:>9.4f}  {verdict(p, qq)}")
out("")
out(f"{sum(1 for q in abs_q if q < 0.05)} of {len(abs_rows)} survive BH.")

agree = dis = 0
qa = {(r[0], r[1], r[2]): q for r, q in zip(abs_rows, abs_q)}
scale_only = []
for r, q in zip(rel_rows, rel_q):
    k = (r[0], r[1], r[2])
    if k not in qa:
        continue
    if (q < 0.05) == (qa[k] < 0.05):
        agree += 1
    else:
        dis += 1
        if q < 0.05:
            scale_only.append(k)
out(f"Parts A and B agree on {agree} of {agree + dis} contrasts.")
if scale_only:
    out("Surviving on the relative scale only -- report these as scale-dependent, not as membership")
    out("effects:")
    for lab, s1, s2 in scale_only:
        out(f"  {lab}: {s1} vs {s2}")
out("")

out(f"=== PART C. EACH SUBSET'S OWN EFFECT, BH within m = {len(own_rows)} ===")
out("What a validation study would report had it chosen that subset. Parts A and B test whether")
out("subsets DIFFER; this tests whether the intervention has an effect on each subset alone. A")
out("verdict that changes across rows of one intervention is the paper's claim in its most direct")
out("form -- and needs Part A to license it, since two verdicts are not a difference.")
out("")
out(f"{'intervention':<34}{'dep':>4}  {'subset':<16}{'effect mm':>11}{'rel %':>8}{'p':>9}{'BH q':>9}"
    f"  verdict")
for (lab, sname, mm, r, p), qq in zip(own_rows, own_q):
    out(f"{lab:<34}{('y' if DEPLOYABLE[lab] else 'n'):>4}  {sname:<16}{mm:>+11.3f}{r:>+8.2f}"
        f"{p:>9.4f}{qq:>9.4f}  {verdict(p, qq)}")
out("")

flips = []
for label, _a, _b, dep in CONTRASTS:
    vs = [(s, q < 0.05) for (l, s, _mm, _r, _p), q in zip(own_rows, own_q) if l == label]
    if len({v for _s, v in vs}) > 1:
        yes = [s for s, v in vs if v]
        no = [s for s, v in vs if not v]
        flips.append((label, dep, yes, no))
out(f"{sum(1 for q in own_q if q < 0.05)} of {len(own_rows)} survive BH.")
if flips:
    out("")
    out("VERDICT CHANGES WITHIN THE LOWER LIMB (anatomy constant, only membership varies):")
    for label, dep, yes, no in flips:
        out(f"  [{'deployable' if dep else 'control only'}] {label}")
        out(f"      significant on: {', '.join(yes)}")
        out(f"      null on:        {', '.join(no)}")
else:
    out("")
    out("NO intervention changes verdict across lower-limb subsets. The paper's claim must then")
    out("retreat to 'measure on the joints the reported outcome uses'.")

if skipped:
    out("")
    out("Not testable from the stored per-participant means:")
    for x in sorted(set(skipped)):
        out("  " + x)

out("")
out("HOW TO READ THIS. A surviving difference in Part A AND Part B means that dropping one joint")
out("from a lower-limb set changes the reported effect with anatomy held constant -- membership is")
out("doing the work, not upper-versus-lower limb. A verdict change in Part C on a DEPLOYABLE")
out("intervention bears on practice; a verdict change on matched-k arms, which are controls,")
out("shows the artefact rather than the behaviour of a deployed rule.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
