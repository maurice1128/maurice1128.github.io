# -*- coding: utf-8 -*-
"""r443: apply the verified findings of the two cold readers to MANUSCRIPT_r442.md.

Every change below corresponds to a finding I re-derived myself from the .sto files or from the
deposit that the finding concerns. Nothing is applied on a reader's say-so alone.
"""
import io

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r442.md"
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# --- abstract opening: treatments are not opposed, they carry asymmetric risk -----------------
rep("""plantarflexor spasticity or from dorsiflexor weakness. The treatments are opposed — botulinum
toxin versus orthosis and strengthening — yet expert consensus states the two produce a clinically
indistinguishable equinus posture, and recommends an invasive diagnostic nerve block to separate
them [LIT: Deltombe 2017]. No kinematic alternative has been established.""",
    """plantarflexor spasticity or from dorsiflexor weakness. The two are not treated identically:
chemically weakening a plantarflexor that is weak rather than overactive costs push-off for months
and cannot be reversed. Expert consensus states the two produce a clinically indistinguishable foot
posture [LIT: Deltombe 2017], and no kinematic alternative to a diagnostic nerve block has been
established.""", "abstract opening")

# --- 3.1: sign convention, noise units, speed, dose asymmetry, rule-4 disclosure ---------------
rep("""Cohen's *d* for lesion type was +0.081 at the ankle and −5.284 at the knee. Leave-one-out
classification (nearest centroid, pooled covariance) gave **50.9% from the ankle — chance — and
98.3% from the knee**; using both gave 100%. The two endpoints correlated at r = 0.18, so the knee
carries information the ankle does not.""",
    """**Sign convention.** Negative is flexion. The unlesioned control contacts the ground with 7.85 deg
of knee flexion and reaches 64.6 deg at the swing peak, so the baseline gait sits in the normal human
range at both landmarks.

**In noise units.** The within-cell seed standard deviation at contact is 0.425 deg for the knee, so
the 5.280 deg lesion difference is **12.4 seed SD**; the 0.056 deg ankle difference is 0.4 seed SD.
Decision rule 1 requires these and an earlier draft omitted them.

**Walking speed.** Mean forward speed was 1.032 +/- 0.003 m/s (control), 1.041 +/- 0.005 (weakness)
and 0.989 +/- 0.024 (spasticity); stride length 1.228, 1.227 and 1.157 m; cycle duration 1.190,
1.179 and 1.171 s. The spastic arm is about 5% slower. Speed is partly pinned by a minimum-velocity
term in the cost function, so these arms are far closer in speed than patients would be. Knee flexion
at contact rises with walking speed, so a patient study must covary for it; this simulation cannot
say how much of a clinical difference would survive that.

**Dose asymmetry, disclosed.** The arms do not span comparable fractions of their severity ranges.
The spastic arm runs KV 0.050-0.120, essentially the full range this model walks with. The weakness
arm runs x0.80-x0.95, the mild end of an axis whose walking ceiling is x0.70. This contrast is
therefore severe spasticity against mild weakness, and some of the 5.280 deg may be dose rather than
lesion type. Section 3.3, where dose is crossed rather than confounded, is the analysis that
addresses this.

Cohen's *d* for lesion type was +0.081 at the ankle and −5.284 at the knee, computed on cells pooled
across dose. **Decision rule 4 forbids judging on a dose-pooled statistic**, so these are reported
and not treated as evidence. Leave-one-out classification — leaving out one *cell*, nearest centroid
with pooled covariance — gave **50.9% from the ankle and 98.3% from the knee** against a 50% chance
baseline for this two-class problem; both together gave 100%. Cells within a family share an
optimisation lineage, so the effective number of independent units is below 59 and these accuracies
are optimistic. The two endpoints correlated at r = 0.18, so the knee is not redundant with the
ankle.""", "3.1 additions")

# --- 3.2: stop selecting the one supporting row -----------------------------------------------
rep("""Only initial contact and loading response separate the lesions **by sign**, and they are also where
the difference is largest in degrees. From midstance onward the weakness displacement approaches
zero (+0.063° at terminal stance) while spasticity continues to act, so later windows grade
spasticity but cannot distinguish it from weakness.""",
    """Only initial contact and loading response separate the lesions **by sign**, and they are also where
the difference is largest in degrees. From midstance onward both lesions displace the knee toward
extension and the lesion difference falls to 0.7-1.7 deg. The weakness displacement is not
uniformly small across those later windows — +0.362 deg at midstance, +0.063 deg at terminal stance,
+0.871 deg at pre-swing — so the defensible statement concerns the loss of the sign contrast, not
weakness disappearing.""", "3.2 selective reading")

# --- 3.6: the SEM was taken from a different source than the table ----------------------------
rep("""Averaged over six contacts, the effective single-limb SEM is 1.12° at the knee. The 5.28° lesion
difference is then 4.7 effective SEM. **However**, the source authors' own guidance is that a
between-session difference below 9° at contact may be attributable to system or observer error —
a threshold the effect does not clear. Both figures are stated; neither is selected.""",
    """Averaging over six contacts reduces the single-measurement SEM by sqrt(6). Using the published knee
SEM of 1.55 deg from the same table as the ICC, that is 0.63 deg, and the 5.28 deg lesion difference
is 8.3 effective SEM. An earlier draft used 2.75 deg, back-derived from a more conservative 7.62 deg
MDC drawn from a different source; mixing two sources was an error and is corrected here.

**However**, the same authors state that a between-session difference below **9 deg** at contact may
be attributable to system or observer error. The 5.28 deg effect does not clear that. The two
thresholds disagree by a factor of two and this manuscript does not choose between them — but any
clinical use of this readout is inherently between-session, patient against norm or before against
after, so the 9 deg figure is the governing one, and by it the effect is **not** detectable.""",
    "3.6 SEM source")

# --- 5: contracture would plausibly reproduce the signature -----------------------------------
rep("""It is not a validated clinical measure. It is not a replacement for a diagnostic nerve block: the
model contains no contracture arm, and dynamic spasticity versus fixed contracture is the main
question the block answers. A velocity-dependence signature tested in this project returned
OVERLAP, so nothing here supports distinguishing reflex from contracture.""",
    """It is not a validated clinical measure, and it is not a replacement for a diagnostic nerve block —
section 1.1 sets out what the block is actually used for, none of which this study addresses.

The absence of a contracture arm is worse than a gap in coverage. A short, stiff triceps surae holds
the foot plantarflexed at contact through the same final common path as reflex overactivity, so
there is every reason to expect contracture would reproduce the knee signature reported here. A
velocity-dependence signature tested elsewhere in this project returned OVERLAP. **Nothing here
establishes that the knee at contact reads reflex overactivity rather than plantarflexor shortness
of any origin**, and until a contracture condition is simulated the finding should be read as being
about plantarflexor over-shortening broadly.

The modelled spasticity is a velocity-dependent stretch reflex — the construct a fast passive
stretch elicits at rest. Spastic dystonia and voluntary co-contraction, at least as often the target
of injection, are not modelled.""", "5 contracture")

# --- new limitation: the weakness arm does not produce steppage -------------------------------
rep("""10. **Sections 3.1, 3.2 and 3.6 are exploratory.**""",
    """10. **The weakness arm does not reproduce steppage, and that is a face-validity failure.**
    Clinically, dorsiflexor weakness provokes increased hip and knee flexion in swing to clear the
    toe. In this model both lesions *reduce* peak swing knee flexion relative to control — weakness
    by 0.433 deg and spasticity by 2.077 deg, i.e. both slightly more extended. The likely cause is
    that the cost function contains no toe-clearance penalty, so the optimiser has no reason to
    adopt a steppage strategy. A clinician will not recognise this half of the discriminator, and it
    should be resolved before any patient study is designed on it.

11. **There is no within-patient formulation.** Every result is a displacement from an unlesioned
    control, which does not exist for a real person; the contralateral limb after stroke is not a
    normal limb. Any clinical translation needs a within-patient design — for example knee angle at
    contact measured before and after a diagnostic nerve block in the same patient.

12. **Practical measurement conditions are not modelled**: ankle-foot orthoses (which sit directly
    on the dependent variable), walking aids, footwear, and forefoot or flat contact, in which the
    heel-strike event is not well defined. Most candidates for this decision present with several of
    these.

13. **No figures.** This draft reports tables only. A claim about a sign reversal in a time-resolved
    signal requires mean knee and ankle traces across the cycle for the three arms with seed bands,
    and that figure is not yet made.

14. **Sections 3.1, 3.2 and 3.6 are exploratory.**""", "new limitations 10-13")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
