# -*- coding: utf-8 -*-
"""r447: length only. Compress toward JNER scale (~5000 words) WITHOUT dropping a single
disclosure. Every fact, number, caveat and adverse finding in r445+r446 survives verbatim in
substance; only wording is cut. Sections touched: Abstract, 1.2, 3.1, 3.2, 3.4, 4.2, 5.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r447_prelengthcut")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  cut:", tag)


# ---------------- Abstract: 461 -> ~350 ------------------------------------------------------
rep("""**Background.** After stroke, restricted ankle dorsiflexion in gait may arise from plantarflexor
spasticity or dorsiflexor weakness. The two are not treated identically: chemically weakening a
plantarflexor that is weak rather than overactive costs push-off for months and is irreversible.
Consensus guidance holds that the two produce a clinically indistinguishable foot posture and
recommends a diagnostic motor nerve block [1]; no kinematic alternative is established. We asked
whether an instant exists at which the two lesions displace a joint angle in *opposite* directions,
and whether that displacement is large enough to measure.

**Methods.** A 19-degree-of-freedom, 22-muscle model (SCONE 2.4.4 / Hyfydy 1.12.6) under a
Geyer–Herr reflex controller was lesioned two ways: a velocity-dependent stretch reflex on soleus
and gastrocnemius (spasticity), and scaling of tibialis anterior maximum isometric force (weakness).
The controller was re-optimised per lesion by CMA-ES, so each analysed gait is that lesioned
system's own best solution rather than an unadapted perturbation. Because lesion magnitude is set by
the investigator, the true spasticity and weakness of every limb is known — a quantity patient
studies cannot obtain. Predictions were preregistered and hashed before the corresponding
simulations existed.

**Results.** At foot contact the two lesions displaced the ankle almost identically (−0.86° weakness,
−0.80° spasticity, relative to unlesioned control; difference 0.06°) while displacing the knee in
opposite directions (+1.36° vs −3.92°; difference 5.28°, 12.4 within-cell seed SD). Leave-one-out
classification of lesion type was 50.8% from the ankle (chance) and 98.3% from the knee. The
opposite-sign behaviour was confined to contact and loading response. Measured over stance instead,
the ankle *does* separate the lesions (2.34°, d = −5.61) — but weakness moves it only 0.04°, so that
readout grades spasticity rather than discriminating the two. On a registered 3 × 3 dose grid the
knee at contact graded spasticity monotonically, while the registered weakness-axis prediction was
uninformative because its deepest row could not walk. Lesion combinations produced overlapping
readings (starkest registered pair 0.30°). Against a measured batch false-positive rate of 26.7%,
like-for-like comparisons separated 24/24 (p = 1.7 × 10⁻¹⁴).

**Conclusions.** Foot position at contact — the variable clinicians observe — is the variable that
cannot separate these lesions, because both drive the foot into the same plantarflexed position by
different routes; the knee at that instant can. **The effect is not, however, clinically
detectable**: against a 7.25–7.62° between-session knee MDC₉₅ band the 5.28° difference does not
clear either bound, and no comparison in the underlying ladder reaches 7.25°. The finding is that
the endpoint *discriminates the two lesions in simulation*, not that the difference is measurable in
a gait laboratory. It is exploratory, the arms are confounded with simulation survival, no
contracture condition was modelled, and no mechanism was identified.""",
    """**Background.** After stroke, restricted ankle dorsiflexion in gait may arise from plantarflexor
spasticity or dorsiflexor weakness. Weakening a plantarflexor that is weak rather than overactive
costs push-off for months and is irreversible. Consensus guidance holds that the two produce a
clinically indistinguishable foot posture and recommends a diagnostic motor nerve block [1]; no
kinematic alternative is established. We asked whether an instant exists at which the two lesions
displace a joint angle in *opposite* directions, and whether that displacement is measurable.

**Methods.** A 19-degree-of-freedom, 22-muscle model (SCONE 2.4.4 / Hyfydy 1.12.6) under a
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
survival, no contracture condition was modelled, and no mechanism was identified.""", "abstract")

# ---------------- 3.1: 812 -> ~590 -----------------------------------------------------------
rep("""**The third row is a competing readout, and it is the smaller one.** Measured over stance the
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
apart cannot.

**Redundancy, judged under rule 4.** The pooled correlation between the two contact endpoints is
r = 0.18 — the dose-pooled statistic rule 4 forbids judging on. The within-dose-centred correlation,
which the rule mandates, is **r = 0.619**: the endpoints share about 38% of variance within lesion
type. The defensible statement is that the knee is not a *mirror* of the ankle and separates the
lesions where the ankle at that instant does not — not that it is non-redundant.

**Survival is perfectly confounded with lesion type.** All 6 control and all 36 weakness cells reach
the 20 s horizon; all 23 spastic cells fall, between 9.81 and 17.85 s. The arms do not overlap on
end time at all, so **decision rule 2 cannot be computed for this contrast** — there is no shared
range over which to estimate the slope. Where it can be run, on the mixed grid of §3.2 where all
cells walk, the within-dose slope is −0.0865 °/s and accounts for 9% of the span, well below the 50%
bar; extrapolating it across the ~7 s gap would account for about 0.6°, some 12% of the 5.280°. That
is an extrapolation, not a control. **The honest statement is that the arms separate on knee angle
at contact and also differ in survival, and this design cannot decide how much of the first is the
second.**

**Unlesioned-side negative control, and where it fails.** Both lesions are left-only, so the right
knee should not separate. Pooled it separates 6 of 24 times against the left's 24 of 24 — but those
six are not spread across the ladder. At KV 0.050, 0.070 and 0.100 the right knee separates 0/6
while the left separates 6/6; **all six right-knee separations come from the single rung KV 0.110**,
which also produces the largest left-knee gap. At that rung displacement is bilateral. It is not a
pipeline artefact — the right knee's own batch false-positive rate is 0/15 — and it is strongly
lateralised, right-knee edge gaps of 0.88–1.63° against the left's 5.46–6.39°. **Strict lesion-side
specificity holds at KV ≤ 0.100 and fails at KV 0.110.**

**The pooled spastic arm is uneven.** Of five spastic families, two contribute 6 Gate-G cells, two
contribute 4, and one contributes only 3 — below the four-cell bar, so that rung is uninformative
alone and is reported, not dropped. Gate-G admissibility is itself lesion-dependent, so the 23-vs-36
sample is differentially filtered.

**Mean walking speed** was 1.032 ± 0.003 m/s (control), 1.041 ± 0.005 (weakness) and 0.989 ± 0.024
(spasticity); the spastic arm is ~5% slower. Speed is partly pinned by the cost function's
minimum-velocity term, so these arms are far closer in speed than patients would be. Knee flexion at
contact is speed-dependent, so a patient study must covary for it.

**Dose asymmetry.** The arms do not span comparable fractions of their severity ranges: the spastic
arm covers essentially the full range this model walks with, the weakness arm only the mild end of
an axis whose walking ceiling is ×0.70. The contrast is therefore severe spasticity against mild
weakness, and some of the 5.280° may be dose rather than lesion type. §3.2 crosses dose rather than
confounding it.""",
    """**The third row is a competing readout, and it is the smaller one.** Over stance the ankle also
separates the lesions, but by **2.342° against the knee's 5.280° — 2.25× smaller in degrees and
2.07× smaller against clinical measurement error (2.14 vs 4.43 SEM).** Its nominally larger Cohen's
*d* (−5.61 vs −5.28, a 6% difference) and larger seed-SD multiple (33.0 vs 12.4) are artefacts of a
small denominator: the stance ankle mean reproduces across seeds to 0.071°, the knee to 0.425°.
Those describe simulation reproducibility, not signal size, and neither transfers to a patient.
Over stance, moreover, weakness moves the ankle by 0.036° — essentially nothing — so the whole
2.342° is spasticity departing from control: that endpoint **grades spasticity** and cannot place a
limb on a two-lesion axis. The knee at contact is the only endpoint here moving in *opposite
directions* under the two lesions.

**Redundancy, judged under rule 4.** The pooled correlation between the contact endpoints is
r = 0.18 — the dose-pooled statistic rule 4 forbids judging on. The within-dose-centred correlation
the rule mandates is **r = 0.619**, so the endpoints share ~38% of variance within lesion type. The
defensible statement is that the knee is not a *mirror* of the ankle and separates the lesions where
the ankle at that instant does not — not that it is non-redundant.

**Survival is perfectly confounded with lesion type.** All 6 control and 36 weakness cells reach the
20 s horizon; all 23 spastic cells fall, at 9.81–17.85 s. With no overlap in end time, **decision
rule 2 cannot be computed for this contrast.** Where it can be run — the mixed grid of §3.2, where
all cells walk — the within-dose slope is −0.0865 °/s, 9% of the span, well below the 50% bar;
extrapolated across the ~7 s gap it would account for ~0.6°, some 12% of the 5.280°. That is an
extrapolation, not a control. **The arms separate on knee angle at contact and also differ in
survival, and this design cannot decide how much of the first is the second.**

**Unlesioned-side negative control, and where it fails.** Both lesions are left-only, so the right
knee should not separate. Pooled it separates 6 of 24 times against the left's 24 of 24 — but not
spread across the ladder: at KV 0.050, 0.070 and 0.100 the right separates 0/6 while the left
separates 6/6, and **all six right-knee separations come from the single rung KV 0.110**, which also
gives the largest left-knee gap. There, displacement is bilateral. It is not a pipeline artefact —
the right knee's own batch false-positive rate is 0/15 — and it is strongly lateralised (right edge
gaps 0.88–1.63° against the left's 5.46–6.39°). **Strict lesion-side specificity holds at
KV ≤ 0.100 and fails at KV 0.110.**

**Three further characteristics of the sample.** (i) The spastic arm is uneven: of five families two
contribute 6 Gate-G cells, two contribute 4 and one only 3 — below the four-cell bar, so that rung is
uninformative alone and is reported, not dropped; Gate-G admissibility is itself lesion-dependent, so
the 23-vs-36 sample is differentially filtered. (ii) Mean walking speed was 1.032 ± 0.003 m/s
(control), 1.041 ± 0.005 (weakness) and 0.989 ± 0.024 (spasticity), the spastic arm ~5% slower;
speed is partly pinned by the cost function's minimum-velocity term, so the arms are far closer in
speed than patients would be, and since knee flexion at contact is speed-dependent a patient study
must covary for it. (iii) The arms span unequal fractions of their severity ranges — the spastic arm
essentially all of it, the weakness arm only the mild end of an axis ceilinged at ×0.70 — so this is
severe spasticity against mild weakness, and some of the 5.280° may be dose rather than lesion type.
§3.2 crosses dose rather than confounding it.""", "3.1")

# ---------------- Limitations: 953 -> ~640 ---------------------------------------------------
rep("""3. **No contracture arm, and this is the leading alternative explanation.** A short, stiff triceps
   surae holds the foot plantarflexed at contact through the same final common path as reflex
   overactivity; contracture is a one-parameter change in this paradigm [10] and severe plantarflexor
   contracture there produced excessive knee flexion in stance — the same direction attributed here
   to spasticity. In personalised models contracture had the largest effect of any modelled
   impairment [12], and mechanically induced equinus alters knee kinematics in healthy people with
   contracture and spasticity deliberately excluded [19]. A velocity-dependence signature tested here
   returned overlap. **Nothing establishes that this readout reads reflex overactivity rather than
   plantarflexor shortness of any origin**, and it should be read as being about plantarflexor
   over-shortening broadly. The modelled construct is a velocity-dependent stretch reflex; spastic
   dystonia and voluntary co-contraction, at least as often the target of injection, are not modelled.
4. **Protocol deviations.** A fourth spastic gain (KV 0.110) was added to a registered 3 × 3 grid
   after hashing, which the registration forbids; a substitute weakness row (×0.70) replaced a
   registered ×0.60 row that failed Gate G. Both are labelled post-hoc at every point of use. One
   registration was edited after its result was produced in an earlier phase of this project, along
   with its analysis script and regenerated outputs, and the hash sidecars were re-baselined, so hash
   verification cannot detect that breach; the revision the run executed under is not recoverable.
   Four registrations had a category set that did not contain the outcome that occurred, and are
   recorded as design defects. One registration produced no result.
5. **Simulation only, and the one real-patient dataset examined is half against us.** A public
   dataset of 50 stroke survivors cannot test this discrimination — no spasticity or strength scale,
   no soleus channel, no MVC normalisation, no speed — but on the one relation it addresses it is not
   neutral. Ankle angle at contact and knee deviation from the able-bodied norm correlate at
   r = +0.613 (p = 2.2 × 10⁻⁶, n = 50), and limbs contacting plantarflexed sit 6.31° from norm against
   17.09° for limbs contacting dorsiflexed — the model's **weakness** mechanism visible in patients.
   **It simultaneously contradicts the spastic arm**: spastic overactivity should give plantarflexed
   contact *and more* knee flexion, whereas in these data plantarflexed contact goes with *less*.
6. **Half of real paretic limbs do not heel-strike.** In those same 50 limbs, 25 contact
   plantarflexed. The event remains well defined, but "knee angle at initial contact" then pools two
   mechanically different events, and the pooling is not random since contact type is downstream of
   the lesion. §4.4 asks clinicians to measure at foot contact; in half the target population that
   instant is a different event.""",
    """3. **No contracture arm, and this is the leading alternative explanation.** A short, stiff triceps
   surae holds the foot plantarflexed at contact through the same final common path as reflex
   overactivity; contracture is a one-parameter change in this paradigm [10], and severe
   plantarflexor contracture there produced excessive stance knee flexion — the direction attributed
   here to spasticity. Contracture had the largest effect of any modelled impairment in personalised
   models [12], and mechanically induced equinus alters knee kinematics in healthy people with
   contracture and spasticity excluded [19]. A velocity-dependence signature tested here returned
   overlap. **Nothing establishes that this readout reads reflex overactivity rather than
   plantarflexor shortness of any origin**; it should be read as being about plantarflexor
   over-shortening broadly. The modelled construct is a stretch reflex — spastic dystonia and
   voluntary co-contraction, as often the target of injection, are not modelled.
4. **Protocol deviations.** A fourth spastic gain (KV 0.110) was added to a registered 3 × 3 grid
   after hashing, which the registration forbids, and a substitute weakness row (×0.70) replaced a
   registered ×0.60 row that failed Gate G; both are labelled post-hoc at every point of use. In an
   earlier phase of this project one registration was edited after its result was produced, together
   with its analysis script and regenerated outputs, and the hash sidecars were re-baselined — so
   hash verification cannot detect that breach and the revision the run executed under is not
   recoverable. Four registrations had a category set not containing the outcome that occurred, and
   are recorded as design defects. One registration produced no result.
5. **Simulation only, and the one real-patient dataset examined is half against us.** A public
   dataset of 50 stroke survivors cannot test this discrimination — no spasticity or strength scale,
   no soleus channel, no MVC normalisation, no speed — but on the one relation it addresses it is not
   neutral. Ankle angle at contact and knee deviation from the able-bodied norm correlate at
   r = +0.613 (p = 2.2 × 10⁻⁶, n = 50), and limbs contacting plantarflexed sit 6.31° from norm against
   17.09° for those contacting dorsiflexed — the model's **weakness** mechanism visible in patients.
   **It simultaneously contradicts the spastic arm**: spastic overactivity should give plantarflexed
   contact *and more* knee flexion, whereas here plantarflexed contact goes with *less*. In those
   same limbs 25 of 50 contact plantarflexed, so "knee angle at initial contact" pools two
   mechanically different events — and not at random, contact type being downstream of the lesion.
   §4.4 asks clinicians to measure at foot contact; in half the target population that instant is a
   different event.""", "limitations 3-6")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
