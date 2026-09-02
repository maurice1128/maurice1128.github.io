# -*- coding: utf-8 -*-
"""r454: withdraw three over-corrections that r451 introduced AGAINST the paper.

All three came from accepting a cold reader's adverse claim without checking it against material
this project already held. That is the same failure as trusting an agent summary of a paper, with
the sign flipped. Authority for the corrected values is paper/FACTS_LEDGER.md.

1. EQUINUS. r451 wrote "clinical equinus at contact is 10-25 deg; the model produces none."
   RELATED_WORK_r440 already held the measured comparator: Mendes-Andrade 2025, n=34 chronic
   spastic hemiparetic in a 3D gait lab, ankle at IC = -3.67 +/- 5.38 (rearfoot group) and
   +2.00 +/- 4.96 (forefoot group). Patients measured at the initial-contact EVENT also sit within
   a few degrees of neutral. The model under-produces -- its lesion shift is 0.86 deg against a
   5.67 deg between-group difference in those patients -- but "produces no equinus at all against
   10-25 deg" is wrong and is withdrawn.

2. FROZEN CONTROLLER. r451 used -13.33 vs -13.20 as a measured result. FROZEN_WEAKNESS_r411 states
   "EVERY LESIONED ARM IN THIS DEPOSIT FAILS GATE G", the arms "die in 3-5 s" on 1-2 cycles, and
   "NONE of the numbers in this deposit may be compared with a Gate-G corpus value". It is a
   concern the design cannot currently test, not a result.

3. MDC. "The effect is not clinically detectable" applies a single-patient change criterion to a
   group-discrimination claim. Three separate true statements exist and only the third is that one.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r454_preundo")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# ---- 1. Abstract conclusions: accurate comparison + the three MDC statements -------------------
rep("""**Conclusions.** In this model, foot position at contact does not separate the two lesions and the
knee at that instant does. **Two constraints bound what that means.** The model does not reproduce
clinical equinus: the ankle sits within 1.5° of neutral at contact in every arm, against the 10–25°
of plantarflexion that defines the deformity the diagnostic block is used for — so this is not a
demonstration that the ankle is uninformative in a limb that presents with equinus. And the effect
is not shown to be clinically detectable, sitting inside the between-session error band of
marker-based knee kinematics (7.25–7.62°), though that is a cross-modality transfer and MDC₉₅ is a
single-patient criterion. The claim supported is discrimination *in simulation*, in a model whose
gait is near-normal. The work is exploratory, the arms are confounded with simulation survival, and
no contracture arm or mechanism was established.""",
    """**Conclusions.** In this model, foot position at contact does not separate the two lesions and the
knee at that instant does. The 5.28° difference is **2.0 times the single-measurement standard error
of knee angle at contact** and would need roughly 41 patients per group to detect as a group
difference; it is below the 7.25–7.62° threshold for declaring change in a single individual across
two sessions, which is a stricter and different question. The model's gait is milder than the target
population's — its lesions shift the ankle at contact by 0.9°, against a 5.7° between-group
difference among chronic hemiparetic patients measured at the same event — and it reproduces neither
steppage nor stiff-knee gait. The work is exploratory, the arms are confounded with simulation
survival, and no contracture arm or mechanism was established.""", "abstract conclusions")

# ---- 2. Section 3.1's equinus paragraph --------------------------------------------------------
rep("""**A limit on how far that reading generalises.** The displacements involved are small in absolute
terms: the ankle sits at −0.656° in control and moves to −1.516° and −1.460° under the two lesions,
so every arm contacts the ground within 1.5° of neutral. Clinical spastic equinus at initial contact
is 10–25° of plantarflexion with forefoot or flat-foot landing, and dorsiflexor paresis produces a
comparable deformity. **This model therefore does not reproduce the deformity that the discrimination
problem is about.** The convergence reported here is a convergence of two small displacements in a
near-normal gait; it is not evidence that the ankle would fail to separate the lesions in a limb that
actually walks in equinus, and a reader cannot distinguish, from these data, between "the ankle
carries no lesion-type information" and "little happened at the ankle". Limitation 3 gives the likely
structural reason.""",
    """**A limit on how far that reading generalises.** The displacements are small in absolute terms: the
ankle sits at −0.656° in control and moves to −1.516° and −1.460° under the two lesions, an
excursion of about 0.9°. The comparator is not the static equinus posture described clinically but
the sagittal ankle angle measured *at the initial-contact event*, and in chronic spastic hemiparetic
patients recorded in a gait laboratory that also sits within a few degrees of neutral: −3.67 ± 5.38°
in a rearfoot-contact group against +2.00 ± 4.96° in a forefoot-contact group, a between-group
difference of 5.67° [5]. **The model is therefore in the right region but under-produces the
excursion by roughly a factor of six.** The convergence reported here is a convergence of two
sub-degree displacements; whether the ankle would still fail to separate the lesions in a limb whose
contact angle varies over the patient range is untested, and a reader cannot distinguish, from these
data alone, between "the ankle carries no lesion-type information" and "little happened at the
ankle".""", "3.1 equinus corrected")


# ---- 3. Frozen controller: a concern, not a result ---------------------------------------------

rep("""**The within-patient design this work would otherwise recommend is refuted by its own data.** The
obvious way to cancel session-level measurement error is to measure knee angle at contact before and
after a diagnostic nerve block in the same limb. But an anaesthetic tibial block *is* acute
plantarflexor paresis delivered over minutes, with no opportunity for the motor re-optimisation on
which this entire discrimination depends — which is the frozen-controller condition of Limitation 10,
where a plantarflexor-weakness lesion displaced the knee to −13.33° against the spastic arm's
−13.20°. On this model's own evidence the post-block knee would move *toward* the spastic reading in
a limb from which spasticity had just been removed. The block also removes voluntary plantarflexor
drive and, unless a selective motor-branch block is performed, plantar cutaneous sensation, so it is
not a clean subtraction of spasticity in any case.""",
    """**The obvious within-patient design carries an unresolved risk.** Measuring knee angle at contact
before and after a diagnostic nerve block in the same limb would cancel session-level measurement
error, which §3.4 identifies as the main obstacle. But a block is acute plantarflexor paresis with no
opportunity for motor re-optimisation, and §3.7 records a frozen-controller probe in which weakness
moved the knee in the same direction as spasticity. That probe's cells do not walk and cannot be
compared with the main result, so this is a risk rather than a refutation — but it should be resolved
in simulation before a patient is recruited. The block also removes voluntary plantarflexor drive
and, unless a selective motor-branch block is used, plantar cutaneous sensation, so it is not a clean
subtraction of spasticity in any case.""", "4.4 block design")

# ---- 4. MMT mapping is an inference, not a measurement -----------------------------------------
rep("""to ×0.70 weakness and KV 0.120; beyond, it falls. A ×0.70 force scaling is roughly MMT 4+/5− —
   **a deficit a clinician would not record as weakness at all** — against the median MMT grade 1, a
   palpable flicker, in the population that motivates the question [4].""",
    """to ×0.70 weakness and KV 0.120; beyond, it falls. The weakness axis spans a 5–30% force deficit,
   against a median dorsiflexor MMT grade of 1 — a palpable flicker, i.e. a deficit above 90% — in
   the population that motivates the question [4]. (Manual muscle test grades are not a linear scale
   of force, so the two are not directly convertible; the point is the direction and size of the
   gap.)""", "limitation 8 MMT")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
for bad in ["10–25°", "MMT 4+", "−13.33° against the spastic arm's"]:
    assert bad not in s, "STILL PRESENT: %s" % bad
print("withdrawn claims: none remain")
