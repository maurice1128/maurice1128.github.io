# -*- coding: utf-8 -*-
"""r448: length pass 2. Abstract to JNER's ~350-word structured limit; tighten 3.2 and 3.4.
No fact removed -- checked by the assertion list at the foot of this script.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r448_prelength2")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  cut:", tag)


# ---- Abstract 446 -> ~345. Methods detail moves to §2, which already carries it. -------------
rep("""**Methods.** A 19-degree-of-freedom, 22-muscle model (SCONE 2.4.4 / Hyfydy 1.12.6) under a
Geyer–Herr reflex controller was lesioned two ways: a velocity-dependent stretch reflex on soleus
and gastrocnemius (spasticity), and scaling of tibialis anterior maximum isometric force (weakness).
The controller was re-optimised per lesion by CMA-ES, so each analysed gait is that lesioned
system's own best solution rather than an unadapted perturbation. Because lesion magnitude is set by
the investigator, the true spasticity and weakness of every limb is known — a quantity patient
studies cannot obtain. Predictions were preregistered and hashed before the corresponding
simulations existed.

**Results.** At foot contact the lesions displaced the ankle almost identically (−0.86° weakness,
−0.80° spasticity, versus unlesioned control; difference 0.06°) while displacing the knee in
opposite directions (+1.36° vs −3.92°; difference 5.28°, 12.4 within-cell seed SD). Leave-one-out
classification of lesion type was 50.8% from the ankle (chance) and 98.3% from the knee. The
opposite-sign behaviour was confined to contact and loading response. Measured over stance the ankle
also separates the lesions, but by less (2.34°), and almost entirely because spasticity moves it —
weakness shifts it 0.04° — so that readout grades spasticity rather than discriminating. On a
registered dose grid the knee at contact graded spasticity monotonically, while the registered
weakness-axis prediction was uninformative because its deepest row could not walk. Lesion
combinations produced overlapping readings (starkest registered pair 0.30°). Against a measured
batch false-positive rate of 26.7%, like-for-like comparisons separated 24/24 (p = 1.7 × 10⁻¹⁴).

**Conclusions.** Foot position at contact — the variable clinicians observe — is the variable that
cannot separate these lesions, because both drive the foot into the same plantarflexed position by
different routes; the knee at that instant can. **The effect is not shown to be clinically
detectable**: it sits inside the between-session error band of marker-based knee kinematics
(7.25–7.62°), though that is a transfer from a different measurement modality and MDC₉₅ is a
single-patient criterion rather than a group-discrimination one. The claim supported is
discrimination *in simulation*. The work is exploratory, the arms are confounded with simulation
survival, no contracture condition was modelled, and no mechanism was identified.""",
    """**Methods.** A 19-degree-of-freedom, 22-muscle model under a Geyer–Herr reflex controller was
lesioned two ways: a velocity-dependent stretch reflex on soleus and gastrocnemius (spasticity), and
scaling of tibialis anterior maximum isometric force (weakness). The controller was re-optimised per
lesion by CMA-ES, so each analysed gait is that lesioned system's own best solution rather than an
unadapted perturbation. Because lesion magnitude is set by the investigator, the true spasticity and
weakness of every limb is known — a quantity patient studies cannot obtain. Predictions were
preregistered and hashed before the corresponding simulations existed.

**Results.** At foot contact the lesions displaced the ankle almost identically (−0.86° weakness,
−0.80° spasticity, versus control; difference 0.06°) while displacing the knee in opposite
directions (+1.36° vs −3.92°; difference 5.28°, 12.4 within-cell seed SD). Leave-one-out
classification of lesion type was 50.8% from the ankle (chance) and 98.3% from the knee, and the
opposite-sign behaviour was confined to contact and loading response. Over stance the ankle also
separated the lesions but by less (2.34°), and almost wholly because spasticity moved it — weakness
shifted it 0.04° — so that readout grades spasticity rather than discriminating. On a registered
dose grid the knee at contact graded spasticity monotonically, while the registered weakness-axis
prediction was uninformative because its deepest row could not walk. Lesion combinations gave
overlapping readings (starkest registered pair 0.30°). Against a measured batch false-positive rate
of 26.7%, like-for-like comparisons separated 24/24 (p = 1.7 × 10⁻¹⁴).

**Conclusions.** Foot position at contact — the variable clinicians observe — is the one that cannot
separate these lesions, both driving the foot into the same plantarflexed position by different
routes; the knee at that instant can. **The effect is not shown to be clinically detectable**: it
sits inside the between-session error band of marker-based knee kinematics (7.25–7.62°), though that
is a transfer from another measurement modality and MDC₉₅ is a single-patient rather than a
group-discrimination criterion. The claim supported is discrimination *in simulation*. The work is
exploratory, the arms are confounded with simulation survival, no contracture condition was
modelled, and no mechanism was identified.""", "abstract 2")

# ---- 3.4: 543 -> ~390 -----------------------------------------------------------------------
rep("""Whether a 5.28° difference is visible in a gait laboratory is answered against a **change-score
MDC₉₅**, because every clinical use of this readout is between-session — patient against norm, or
before against after.

All values below are **marker-based 3D** between-session change-score MDCs:""",
    """Whether a 5.28° difference is visible in a gait laboratory is answered against a **change-score
MDC₉₅**, because every clinical use of this readout is between-session. All values below are
**marker-based 3D** between-session change-score MDCs:""", "3.4 opener")

rep("""**The published 4.29° must not be used.** Its formula substitutes SD_diff where the between-subject
SD is required, understating the MDC by √2; the same paper's Bland–Altman limits of agreement
(−6.78° to +7.74°, half-width 7.26°) contradict its own table and confirm 7.25°. Nor may a
between-session SEM be divided by √n contacts: that SEM is already computed from five repetitions
per session and carries marker placement, calibration and observer error, none of which averages
down within one recording.

No knee-**at-contact** MDC exists for a neurological population, but neurological knee MDCs at other
events do [14, 15]. **The most conservative defensible band is 7.25–7.62°**, where two independent
routes converge: the corrected healthy knee-at-contact value (right variable and event, wrong
population — and healthy values understate neurological error) and the largest discrete knee MDC in
chronic stroke (right population, wrong event).

**The 5.28° effect does not clear that band,** and neither does the underlying ladder: across all
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
    """**The published 4.29° must not be used.** Its formula substitutes SD_diff where the between-subject
SD is required, understating the MDC by √2; the same paper's limits of agreement (−6.78° to +7.74°,
half-width 7.26°) contradict its own table and confirm 7.25°. Nor may a between-session SEM be
divided by √n contacts: it is already computed from five repetitions per session and carries marker
placement, calibration and observer error, none of which averages down within one recording. No
knee-**at-contact** MDC exists for a neurological population, though neurological knee MDCs at other
events do [14, 15]. **The most conservative defensible band is 7.25–7.62°**, where two independent
routes converge — the corrected healthy knee-at-contact value (right variable and event, wrong
population, and healthy values understate neurological error) and the largest discrete knee MDC in
chronic stroke (right population, wrong event).

**The 5.28° effect does not clear that band,** nor does the underlying ladder: across 24
like-for-like comparisons the edge gaps run 1.49–6.39° (median 4.61°); 14 reach 3.8°, three reach
5.7°, one reaches 6.39°, and **zero reach 7.25°**. In change-score terms 6.39° is 1.7–2.1 SD, which
is why it lands just under rather than far below a 95% threshold.

**Three qualifications keep this from being a verdict.** (i) It is a **transfer, not a like-for-like
comparison**: every tabulated value is the error of *marker-based 3D* gait analysis, whose dominant
term is inter-tester marker replacement on the thigh and shank — the very segments whose axes define
the knee angle — while the simulated endpoint carries no marker error at all. (ii) **The modality
proposed here is sagittal video (§3.3), for which no knee-angle-at-contact error figure exists in
the literature.** Published markerless and 2D errors are cycle-averaged (3.7–5.6° MAE in adults,
4.0° in stroke [21, 22]) and are not decomposed by event; whether removing marker placement error
while adding pose-estimation error raises or lowers this bar is unknown, and we do not assume it
favours us. (iii) **MDC₉₅ is the wrong criterion for the claim.** It is the threshold for being 95%
confident that *one individual* changed between two sessions, whereas the claim here is group
discrimination, for which the relevant quantity is between-group separation against between-patient
spread.

We therefore do **not** claim that a clinician measuring one patient once could act on a 5.28°
difference. We claim the endpoint discriminates the two lesions *in simulation* with a dose-monotone
gap, and that the effect sits inside the between-session noise band of the one modality for which
published figures exist. The design that removes the mismatch is within-patient — the same limb
before and after a diagnostic nerve block — where session-level marker error largely cancels;
establishing the error of sagittal video at this event is a prerequisite for any of it.""", "3.4")

io.open(P, "w", encoding="utf-8", newline="").write(s)

need = ["0.056", "5.280", "2.342", "0.619", "50.8", "98.3", "9.81", "17.85", "KV 0.110", "26.7",
        "24/24", "7.25", "7.62", "4.29", "0.30", "0.002", "0.613", "6.31", "17.09", "0.433",
        "2.077", "1.784", "3.5 seed SD", "0.586", "1.67", "0.0865", "2.25", "0.071", "0.425",
        "transfer, not a like-for-like", "single-patient", "3.7–5.6", "×0.70", "MMT", "0/15",
        "0.88–1.63", "12 families", "equivalence test", "−13.33", "steppage", "1.49–6.39"]
miss = [n for n in need if n not in s]
print("\nwrote %d chars" % len(s))
print("MISSING FACTS:", miss if miss else "none - all survived")
