# -*- coding: utf-8 -*-
"""r446: correct three places where r445 overstated AGAINST the result.

All three were caught by the user, and all three are confirmed against the deposits:

 1. MDC. KNEE_MDC_BATCHNULL_r399 /PLAIN_VERDICT/Q4_declared_limitations/4 states the comparison
    is "a transfer, not a like-for-like" because the MDC figures are MARKER-BASED error and the
    simulated endpoint has none. The same file records that inter-tester marker replacement is
    "the dominant error source". r445 presented the band as a flat verdict and dropped both facts.
    Also: MDC95 is a single-patient change criterion, not a group-discrimination criterion.

 2. Knee vs ankle. The knee effect is 5.280 deg vs the stance ankle's 2.342 deg -- 2.25x larger in
    degrees and 2.07x larger in clinical SEM units (4.43 vs 2.14). The ankle "wins" only on
    Cohen's d (by 6%) and on seed-SD multiple, both of which are driven by its very small
    simulation-noise denominator (seed SD 0.071 vs 0.425 deg). r445 led with the d comparison,
    which is a reproducibility statistic, not a signal-size one.

 3. Weakness. MIXED_RESULT_r424 READING/P2 says depth "is not readable from this endpoint UNLESS
    spasticity is already substantial" -- and at KV 0.050 the weakness axis spans 1.784 deg = 3.5
    SD, i.e. it IS readable there. Combined with the x0.70 walking ceiling against a clinical
    median MMT of 1, the flat weakness axis is under-sampling, not a demonstrated null.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r446_preuserfix")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# ---- 1. knee vs ankle: lead with the units that carry signal size ---------------------------
rep("""**The third row is the competing readout.** Over stance, the ankle separates the lesions with a
*larger* effect size than the knee at contact (d = −5.61 vs −5.28; 33.0 vs 12.4 seed SD). What
distinguishes them is *what carries the contrast*: over stance weakness moves the ankle by 0.036°,
essentially nothing, and the whole 2.342° is spasticity departing from control. That endpoint
therefore **grades spasticity**, and cannot place a limb on a two-lesion axis. The knee at contact
is the only endpoint here that moves in *opposite directions* under the two lesions. In
clinical-error units the ordering also reverses (2.14 vs 4.43 SEM). A reader wanting a spasticity
meter should use the ankle over stance; a reader wanting to tell the lesions apart cannot.""",
    """**The third row is a competing readout, and it is the smaller one.** Measured over stance the
ankle also separates the lesions, but by **2.342° against the knee's 5.280° — 2.25 times smaller in
degrees, and 2.07 times smaller against clinical measurement error (2.14 versus 4.43 SEM).** Its
nominally larger Cohen's *d* (−5.61 versus −5.28, a 6% difference) and its much larger seed-SD
multiple (33.0 versus 12.4) are both artefacts of a very small denominator: mean ankle angle over
stance reproduces across optimisation seeds to 0.071°, against 0.425° for the knee at contact. Those
are statements about simulation reproducibility, not about signal size, and neither transfers to a
patient.

Two further things separate the endpoints. Over stance, weakness moves the ankle by 0.036° —
essentially nothing — so the whole 2.342° is spasticity departing from control: that endpoint
**grades spasticity** and cannot place a limb on a two-lesion axis. And the knee at contact is the
only endpoint measured here that moves in *opposite directions* under the two lesions. A reader
wanting a spasticity meter may use the ankle over stance; a reader wanting to tell the two lesions
apart cannot.""", "knee vs ankle framing")

# ---- 2. MDC: keep the warning, restore the transfer caveat and the criterion mismatch --------
rep("""**The 5.28° effect does not clear it,** and neither does the underlying ladder: across all 24
like-for-like comparisons the edge gaps run 1.49° to 6.39° (median 4.61°); 14 reach 3.8°, three reach
5.7°, one reaches 6.39°, and **zero reach 7.25°**. The largest gap anywhere still falls short. The
source authors separately state that a between-session difference below **9°** at contact may be
attributable to system or observer error, which the effect also fails.

This manuscript therefore **does not claim clinical detectability**. What the result licenses is that
the endpoint discriminates the two lesions *in simulation*, with a dose-monotone gap. A patient study
must either average far more contacts than a session provides, use a within-patient design where
session-level error cancels, or await a method with smaller between-session error.""",
    """**The 5.28° effect does not clear that band,** and neither does the underlying ladder: across all
24 like-for-like comparisons the edge gaps run 1.49° to 6.39° (median 4.61°); 14 reach 3.8°, three
reach 5.7°, one reaches 6.39°, and **zero reach 7.25°**. In change-score terms 6.39° is 1.7–2.1 SD of
the between-session change, which is why it lands just under rather than far below a 95% threshold.

**Three qualifications keep this from being a verdict.** First, it is a **transfer, not a
like-for-like comparison**: every value in the table is the measurement error of *marker-based 3D*
gait analysis, and the dominant term in that error is inter-tester marker replacement on the thigh
and shank — the very segments whose axes define the knee angle. The simulated endpoint carries no
marker error at all. Second, **the modality this study actually proposes is sagittal video (§3.3),
for which no knee-angle-at-contact error figure exists in the literature at all.** Published
markerless and 2D errors are cycle-averaged (3.7–5.6° MAE in adults, 4.0° in stroke [21, 22]) and
are not decomposed by gait event; whether removing marker placement error while adding
pose-estimation error raises or lowers the bar for *this* endpoint is unknown, and we do not assume
it favours us. Third, **MDC₉₅ is the wrong criterion for the claim being made.** It is the threshold
for being 95% confident that *one individual* has changed between two sessions. The claim here is
group discrimination, for which the relevant quantity is between-group separation relative to
between-patient spread, not within-patient change error.

What this manuscript therefore does **not** claim is that a clinician measuring one patient once
could act on a 5.28° difference. What it claims is that the endpoint discriminates the two lesions
*in simulation*, with a dose-monotone gap, and that the effect sits inside the between-session noise
band of the one measurement modality for which published figures exist. The design that removes the
mismatch is within-patient — the same limb before and after a diagnostic nerve block — where
session-level marker error largely cancels and MDC₉₅ is no longer the governing bar. Establishing
the error of sagittal video at this specific event is a prerequisite for any of it.""",
    "MDC transfer + criterion")

rep("""| source | population | variable | MDC₉₅ (°) |
|---|---|---|---|""",
    """All values below are **marker-based 3D** between-session change-score MDCs:

| source | population | variable | MDC₉₅ (°) |
|---|---|---|---|""", "MDC table header")

# ---- 3. weakness: under-sampled, not refuted ------------------------------------------------
rep("""post-hoc, and an earlier "P2 holds" built on them is withdrawn as a registered result.** What
survives registration is the *direction* of both axes, not the magnitude of the weakness one. The
weakness effect at low spastic gain is the size of re-running the identical lesion with a different
seed.""",
    """post-hoc, and an earlier "P2 holds" built on them is withdrawn as a registered result.** What
survives registration is the *direction* of both axes, not the magnitude of the weakness one.

**The flat weakness axis is a statement about the corner of the space that was sampled, not about
the endpoint.** It is flat at the two *lower* spastic doses, where the whole axis sits at 0.9–1.0
seed SD. At KV 0.050 the same axis spans 1.784° — **3.5 seed SD, and readable.** Weakness also
displaces the knee from control by +1.358° in §3.1, which is 3.2 seed SD, so the endpoint is not
blind to it. The correct reading is the deposit's own: depth of dorsiflexor weakness is not readable
from this endpoint *unless spasticity is already substantial* — which is the condition under which
the clinical question is actually asked. Whether the axis steepens further with deeper weakness is
**untested**, because the model stops walking below ×0.70 (Limitation 8): the sampled range is a
5–30% force deficit against a clinical median of manual muscle test grade 1. **Nothing here shows
that severe dorsiflexor weakness fails to grade the knee; it shows that mild weakness, at low
spastic gain, does not.**""", "weakness under-sampled")

rep("""For a clinician the practical content is narrow but specific: at foot contact, expect the knee to
move toward flexion with plantarflexor spastic severity. The opposite half — extension with
dorsiflexor weakness — is **not supported at usable resolution** by §3.2, where the weakness axis
sits at 0.9–1.0 seed SD at low spastic gain, and the deposit's own reading is that this endpoint is a
spasticity meter rather than a mixture meter.""",
    """For a clinician the practical content is narrow but specific: at foot contact, expect the knee to
move toward flexion with plantarflexor spastic severity. The opposite half — extension with
dorsiflexor weakness — is **supported in direction but not at usable resolution across the range
tested**: the weakness axis sits at 0.9–1.0 seed SD at the two lower spastic doses, rising to 3.5 SD
at the highest. Because the model cannot walk with severe weakness, whether the axis becomes
readable at clinically typical weakness depth is untested rather than excluded, and extending it is
the second experiment this work calls for.""", "4.4 weakness")

rep("""**It cannot produce a severely affected patient**, which is the patient
   who receives a diagnostic block.""",
    """**It cannot produce a severely affected patient**, which is the patient
   who receives a diagnostic block. This ceiling, not a demonstrated property of the endpoint, is why
   the weakness axis of §3.2 is shallow; with the cells that exist the two cannot be separated.""",
    "limitation 8 ceiling")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
