# -*- coding: utf-8 -*-
"""r451: apply the three cold reads of r445. All findings re-derived by me before applying.

THE BIG ONE (clinician cold reader, missed by four previous audits): the model produces NO EQUINUS.
Ankle at contact is -0.656 / -1.516 / -1.460 deg across the three arms -- every arm within 1.5 deg
of neutral, against a clinical spastic equinus of 10-25 deg plantarflexion at contact. So "the ankle
cannot distinguish the two lesions at contact" is not a demonstration that the ankle is uninformative
in an equinus limb; there is no equinus in this model for it to be uninformative about. Verified
directly from the manuscript's own table and from IC_KNEE_VS_ANKLE_r439.

SECOND: a diagnostic tibial nerve block IS the frozen-controller plantarflexor-weakness condition --
acute paresis, no re-optimisation. Limitation 10 records that condition displacing the knee to
-13.33 deg against the spastic arm's -13.20 deg. The within-patient pre/post-block design recommended
in section 4.4 is therefore refuted by this project's own data.

THIRD, and the only good news: I ran the leave-one-FAMILY-out analysis the methods referee correctly
said was owed. It holds -- 98.3% by cell, 100% by family (11/11), family-level permutation
p = 0.0022 on C(11,5) = 462 labellings. That replaces the abstract's p = 1.7e-14, which assumed 24
independent trials.

REJECTED after checking:
 - "Gate G looks tuned to the spastic failure times (9.73 vs earliest 9.81)". The 9.73 s threshold
   appears in PREREG_3d_injection_r145, PREREG_3d_discrimination_r150, PREREG_3d_continuation_r172
   and others, all long predating the r393/r396 spastic cells at issue. Not tuned. But the
   provenance is now stated, because the suspicion is reasonable on the text alone.
 - "the stationarity claim is unsupported". STATIONARITY_r434 has a stated bar (drift ratio ~10x)
   and knee-at-contact is 0.98x, with the raw series oscillating about -13.5 rather than trending.
   The manuscript reported the two drifts without the ratio or the rule, which is what made it look
   unsupported. Fixed by reporting both.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r451_precoldread2")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# =============================================================================================
# 1. THE EQUINUS FAILURE -- abstract, results, and a top limitation
# =============================================================================================
rep("""**Conclusions.** Foot position at contact — the variable clinicians observe — is the one that cannot
separate these lesions; the knee at that instant can. **The effect is not shown to be clinically
detectable**, sitting inside the between-session error band of marker-based knee kinematics
(7.25–7.62°) — though that is a cross-modality transfer, and MDC₉₅ is a single-patient criterion.
The claim supported is discrimination *in simulation*. The work is exploratory, the arms are
confounded with simulation survival, and no contracture arm or mechanism was established.""",
    """**Conclusions.** In this model, foot position at contact does not separate the two lesions and the
knee at that instant does. **Two constraints bound what that means.** The model does not reproduce
clinical equinus: the ankle sits within 1.5° of neutral at contact in every arm, against the 10–25°
of plantarflexion that defines the deformity the diagnostic block is used for — so this is not a
demonstration that the ankle is uninformative in a limb that presents with equinus. And the effect
is not shown to be clinically detectable, sitting inside the between-session error band of
marker-based knee kinematics (7.25–7.62°), though that is a cross-modality transfer and MDC₉₅ is a
single-patient criterion. The claim supported is discrimination *in simulation*, in a model whose
gait is near-normal. The work is exploratory, the arms are confounded with simulation survival, and
no contracture arm or mechanism was established.""", "abstract conclusions equinus")

rep("""The mechanical reading is that both lesions plantarflex the foot at contact — spasticity actively,
weakness passively through foot drop. Different causes, the same angle.""",
    """The mechanical reading is that both lesions move the foot toward plantarflexion at contact by a
similar amount — spasticity actively, weakness passively through dorsiflexor failure — so that the
difference *between* them at the ankle is 0.056°, while the knee separates by 5.280°.

**A limit on how far that reading generalises.** The displacements involved are small in absolute
terms: the ankle sits at −0.656° in control and moves to −1.516° and −1.460° under the two lesions,
so every arm contacts the ground within 1.5° of neutral. Clinical spastic equinus at initial contact
is 10–25° of plantarflexion with forefoot or flat-foot landing, and dorsiflexor paresis produces a
comparable deformity. **This model therefore does not reproduce the deformity that the discrimination
problem is about.** The convergence reported here is a convergence of two small displacements in a
near-normal gait; it is not evidence that the ankle would fail to separate the lesions in a limb that
actually walks in equinus, and a reader cannot distinguish, from these data, between "the ankle
carries no lesion-type information" and "little happened at the ankle". Limitation 3 gives the likely
structural reason.""", "3.1 no equinus")

# =============================================================================================
# 2. Family-level inference replaces the independence-assuming p-value
# =============================================================================================
rep("""and combinations gave overlapping readings.
Against a measured batch false-positive rate of 26.7%, like-for-like comparisons separated 24/24
(p = 1.7 × 10⁻¹⁴).""",
    """and combinations gave overlapping readings.
At the family level — the honest unit of analysis, 5 spastic against 6 weakness optimisation
lineages — 11 of 11 families classified correctly, and a permutation test over all 462 family
labellings gave p = 0.0022.""",
    "abstract family-level inference")

rep("""The unlesioned control contacts with 7.85° of knee flexion and peaks at 64.6° in swing, so the
baseline sits in the normal human range at both landmarks. Leave-one-out classification gave
**50.8% from the ankle at contact — chance — and 98.3% from the knee**; both together 100%.""",
    """The unlesioned control contacts with 7.85° of knee flexion and peaks at 64.6° in swing, so the
knee baseline sits in the normal human range at both landmarks.

**Classification, at both units of analysis.** Leaving out one *cell*, accuracy was **50.8% from the
ankle at contact and 98.3% from the knee**. Cells within a family share an optimisation lineage, so
that fold is optimistic; leaving out a whole *family* gives 98.3% by cell and **11 of 11 families**
classified correctly. A permutation test at the family level — relabelling all C(11,5) = 462 ways of
splitting 11 lineages into 5 spastic and 6 weakness — puts the observed 5.593° family-mean difference
first, **p = 0.0022**. This is the inferential statement this design supports. An earlier draft
quoted p = 1.7 × 10⁻¹⁴ from 24 like-for-like comparisons; that figure assumes 24 independent trials,
which the lineage structure denies, and it is withdrawn.

Two cautions on the accuracies themselves. The classes are unbalanced (23 spastic, 36 weakness), so
the no-information baseline is the majority class at **61.0%**, not 50%: the ankle's 50.8% is
*below* it and the knee's 98.3% must be read against it. And adding the ankle to the knee raises
accuracy from 98.3% to 100%, which sits awkwardly with calling the ankle uninformative — one cell's
worth of change on 59 non-independent cells is as consistent with overfitting as with information,
and we do not treat the 100% as a result.""", "3.1 classification units")

# =============================================================================================
# 3. The nerve-block design is refuted by our own frozen-controller result
# =============================================================================================
rep("""The instant is principled and the direction is predicted; **the size is not detectable** (§3.4). The
useful next step is therefore not a clinical trial but three things: a contracture arm, run at the
one-parameter cost Ong et al. established [10]; replication of §3.1 within a single optimisation
round; and a within-patient design — knee angle at contact before and after a diagnostic nerve block
in the same patient — where session-level measurement error cancels. Using the between-patient SDs
above and a 5.28° difference, a between-group design would need roughly 41 patients per group at 80%
power, which is the study this work does *not* license until the contracture arm exists.""",
    """**This readout must not be used to select patients for injection**, and the reasons are concrete. A
knee flexed at contact after stroke is more often driven by hamstring overactivity or shortening, or
by hip or knee flexion contracture, than by the calf — the closest published precedent for a
knee-at-contact spasticity signal is itself a *hamstring* study [6] — so applying the rule to a
crouched limb would direct toxin into the triceps surae and remove the plantarflexion–knee-extension
couple that limb depends on, which is exactly the asymmetric harm §1.1 identifies. In the other
direction, stance-phase knee hyperextension after stroke is conventionally attributed to
plantarflexor overactivity or shortening, and both plantarflexor spasticity [8] and plantarflexor
weakness [17] are reported to accompany it, so an extended knee does not isolate the dorsiflexor
either.

**The within-patient design this work would otherwise recommend is refuted by its own data.** The
obvious way to cancel session-level measurement error is to measure knee angle at contact before and
after a diagnostic nerve block in the same limb. But an anaesthetic tibial block *is* acute
plantarflexor paresis delivered over minutes, with no opportunity for the motor re-optimisation on
which this entire discrimination depends — which is the frozen-controller condition of Limitation 10,
where a plantarflexor-weakness lesion displaced the knee to −13.33° against the spastic arm's
−13.20°. On this model's own evidence the post-block knee would move *toward* the spastic reading in
a limb from which spasticity had just been removed. The block also removes voluntary plantarflexor
drive and, unless a selective motor-branch block is performed, plantar cutaneous sensation, so it is
not a clean subtraction of spasticity in any case.

What remains, then, is not a clinical study but three modelling steps: a contracture arm at the
one-parameter cost Ong et al. established [10]; a model that walks in equinus, without which the
ankle result has no clinical referent; and replication of §3.1 within a single optimisation round. A
between-group patient study is not licensed — and could not be recruited as designed, because the
cohort in question carries both components in almost every limb [4], so there are no pure-spasticity
and pure-weakness groups to enrol.""", "4.4 rebuilt")

# =============================================================================================
# 4. Clinical factual errors I introduced
# =============================================================================================
rep("""spasticity or dorsiflexor weakness, and mistaking one for the other is costly and irreversible.
Consensus guidance holds that the two produce an indistinguishable foot posture and recommends a
diagnostic nerve block [1].""",
    """spasticity or dorsiflexor weakness. The two are separable on examination, but how much each
contributes to the gait deviation — and whether the dorsiflexors will function once the antagonist is
silenced — is not, which is why a diagnostic motor nerve block is used [1]. Weakening a plantarflexor
that is weak rather than overactive has no antidote and must be waited out over three to four
months.""", "abstract premise")

rep("""Consensus guidance on spastic equinus after stroke states that triceps surae spasticity and
dorsiflexor weakness produce a foot posture that cannot be told apart clinically, and places a
diagnostic motor nerve block in the presurgical pathway [1]; the block predicts botulinum toxin
outcome [2]. Instrumented 3D gait analysis has been tested as a substitute and found not
equivalent [3].

Two clarifications, because the modelling literature misstates this decision. The treatments are
**not mutually exclusive** — toxin and an orthosis are routinely prescribed at the same visit. The
asymmetry is one of **risk**: weakening a plantarflexor that is weak rather than overactive costs
push-off and the plantarflexion–knee-extension couple, for months, irreversibly. And the block is
not used *primarily* to separate dynamic spasticity from fixed contracture — that is usually settled
at the bedside by slow-versus-fast stretch and the Silfverskiöld manoeuvre. It is used to predict
the functional consequence of weakening the triceps surae, to unmask dorsiflexor strength hidden
under antagonist overactivity, to apportion overactivity between muscles, and to choose between
toxin and selective neurotomy. **This study addresses none of those purposes.** Varus is not
modelled; the scope is sagittal-plane equinus.""",
    """Consensus guidance on spastic equinus after stroke places a diagnostic motor nerve block in the
presurgical pathway [1], and the block predicts botulinum toxin outcome [2]. Instrumented 3D gait
analysis has been tested as a substitute and found not equivalent [3].

Three clarifications, because the modelling literature misstates this decision — including, in an
earlier draft, this manuscript.

**What is and is not indistinguishable.** Plantarflexor overactivity and dorsiflexor paresis are
separable at the bedside in most patients: a velocity-dependent catch on fast passive dorsiflexion
that is absent on slow stretch indicates the former, while full soft passive dorsiflexion with an
empty end-feel and absent active dorsiflexion indicates the latter. What examination does not settle
is *how much of the observed gait deviation each contributes*, and whether the dorsiflexors will
function once the antagonist is silenced. The clinical question is rarely "which one" and usually
"how much of each" — and the gait appearance at the foot is similar either way.

**The treatments are not mutually exclusive**; toxin and an orthosis are routinely prescribed at the
same visit. The asymmetry is one of **risk**: weakening a plantarflexor that is weak rather than
overactive costs push-off and the plantarflexion–knee-extension couple. Botulinum toxin is not
irreversible — it wears off over roughly three to four months — but there is no antidote, so a
misdirected injection must be waited out, during which the patient may lose ambulation status. What
is irreversible is selective neurotomy or tendon lengthening, which is why the block matters most
before surgery.

**What the block is for.** It is used to predict the functional consequence of weakening the triceps
surae, to unmask dorsiflexor strength hidden under antagonist overactivity, to apportion overactivity
between individual muscles, and to choose between toxin and neurotomy. Bedside tests address parts
of this — slow-versus-fast stretch (Tardieu R1 vs R2) estimates the dynamic component, and the
Silfverskiöld manoeuvre apportions restriction between gastrocnemius and soleus by comparing passive
dorsiflexion with the knee extended versus flexed — but both are approximations, and where the fixed
component is uncertain the block remains in use. **This study addresses none of those purposes.**
Varus is not modelled, and the block population is predominantly equinovarus, in which tibialis
anterior is often itself overactive rather than simply weak; the scope here is sagittal-plane
equinus only.""", "1.1 clinical corrections")

# =============================================================================================
# 5. Severity anchoring
# =============================================================================================
rep("""to ×0.70 weakness and KV 0.120; beyond, it falls. The weakness axis spans a 5–30% force deficit,
   roughly an order of magnitude milder than the median MMT grade 1 of the clinical population that
   motivates the question [4]. **It cannot produce a severely affected patient**, which is the patient
   who receives a diagnostic block. This ceiling, not a demonstrated property of the endpoint, is why
   the weakness axis of §3.2 is shallow; with the cells that exist the two cannot be separated.""",
    """to ×0.70 weakness and KV 0.120; beyond, it falls. A ×0.70 force scaling is roughly MMT 4+/5− —
   **a deficit a clinician would not record as weakness at all** — against the median MMT grade 1, a
   palpable flicker, in the population that motivates the question [4]. The spastic axis has no
   clinical anchor whatever: KV 0.050–0.120 is never mapped to a Modified Ashworth or Tardieu grade,
   so "severe spasticity" here is not calibrated to anything observable. All three arms walk at about
   1.0 m/s, whereas candidates for a diagnostic block are typically household or limited-community
   ambulators at 0.3–0.7 m/s. **The simulated severity range and the block population do not overlap**
   — on strength, on speed, on contact pattern, or on the presence of a fixed component. This
   ceiling, not a demonstrated property of the endpoint, is also why the weakness axis of §3.2 is
   shallow; with the cells that exist the two cannot be separated.""", "limitation 8 severity")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
