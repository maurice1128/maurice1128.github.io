# -*- coding: utf-8 -*-
"""r450: CORRECT THE CAWOOD NUMBERS. They were wrong in every draft of this manuscript.

WHAT HAPPENED. subphase_r441.py recorded Cawood & Mashola 2023 Table 5 as a PLANTARFLEXOR-tone
column with values (IC 0.542/0.069, LR 0.321/0.309, MS 0.492/0.104, TS 0.745/0.005, PS 0.672/0.017).
Read today from the publisher's own HTML galley (sajp.co.za/index.php/sajp/article/view/1926/3461),
Table 5's tone columns are headed by MUSCLE, not by movement direction, and the true values are:

    phase              TA rho   TA p    GAS rho  GAS p
    initial contact    0.662    0.019   0.362    0.22
    loading response   0.489    0.10    0.278    0.45
    midstance          0.440    0.15    0.350    0.24
    terminal stance    0.695    0.01    0.290    0.48
    pre-swing          0.718    0.01    0.065    0.85

The recorded values match NEITHER column: the original extraction mis-mapped columns in the JATS
XML. Three consequences, all against this manuscript:

  1. Cawood is NOT a null at initial contact. TA tone is significant there (p = 0.019).
  2. GASTROCNEMIUS tone -- the muscle this project lesions -- is not significantly related to knee
     angle at ANY stance phase. That is the comparison relevant to our spastic arm, and it is a
     null in patients.
  3. The claim that Cawood's abstract and Table 5 contradict each other IS FALSE. Abstract, Results
     text and Table 5 all agree. That charge was ours in error and is withdrawn.

Verified from three mutually corroborating parts of the same galley: the abstract, the Results
prose ("Gastrocnemius muscle tone was not significantly related to the knee angles during any of
the stages ... (p = 0.22) ... (p = 0.45) ... (p = 0.24) ... (p = 0.48) ... (p = 0.85)"), and Table 5.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r450_precawood")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# ---- 1.2: the pilot is a DORSIFLEXOR-tone finding, not the plantarflexor version --------------
rep("""*The plantarflexor version, in adults.* One pilot has attempted it. In 12 chronic hemiparetic adults
measured with 2D video, nothing reached significance at initial contact (plantarflexion-direction
tone r = 0.542, p = 0.069; dorsiflexor strength r = −0.382, p = 0.220; four further variables
p ≥ 0.276); significance appeared only at terminal stance (r = 0.745, p = 0.005) and pre-swing
(r = 0.672, p = 0.017) [7]. ⚠ That paper's Results text and its Table 5 disagree, and its abstract
describes a six-participant subgroup absent from the article; we cite it as a null at contact with
that contradiction disclosed. **Which muscle's tone carries its two significant correlations is not
settled in our reading and is treated here as an open question** (Limitation 11).""",
    """*The adult pilot, and what it actually found.* One pilot has related graded ankle muscle tone to
hemiparetic knee angle through stance in 12 chronic hemiparetic adults, using the Modified Tardieu
Scale and 2D video [7]. Its positive finding is a **dorsiflexor** one: tibialis anterior tone
correlated with knee angle at initial contact (ρ = 0.662, p = 0.019), terminal stance (ρ = 0.695,
p = 0.01) and pre-swing (ρ = 0.718, p = 0.01), but not at loading response (p = 0.10) or midstance
(p = 0.15). **Gastrocnemius tone — the muscle class lesioned in the present study — was not
significantly related to knee angle at any stance phase** (ρ = 0.362, 0.278, 0.350, 0.290, 0.065;
p = 0.22, 0.45, 0.24, 0.48, 0.85). Ankle strength and range of motion were likewise unrelated to knee
angle at every phase. Only 9 of 12 participants had any gastrocnemius tone and 6 any tibialis
anterior tone, on an ordinal 0–5 scale, so the study is a feasibility pilot and its authors present
it as one.""", "1.2 Cawood corrected")

# ---- 4.2: the reconciliation mapped the wrong muscle. Rebuild it around the gastroc null ------
rep("""### 4.2 Reconciliation with the one adult-stroke attempt

Cawood and Mashola found no significant relationship at initial contact in 12 patients, with
significance only at terminal stance and pre-swing [7].

**Every patient in a stroke cohort carries both components.** If the two lesions displace the knee in
opposite directions at contact, correlating one component against knee angle while the other varies
freely attenuates the association toward zero; §3.2's cancellation is the mechanism. Concretely, a
limb with severe spasticity and severe weakness reads at the knee much like one with mild spasticity
and mild weakness, so a correlation against spasticity alone in a mixed cohort is flat by
construction. On this reading their null at contact is what this model predicts for a mixed cohort.

**The agreement does not extend to where significance landed, and our own analysis scored this a
disagreement.** The model's strongest dose window is loading response; theirs is terminal stance. A
more parsimonious account of the null should also be stated first: with 12 participants, a six-level
ordinal tone grade and 2D video, that study is underpowered, and its authors say so. The
between-patient spread alone — knee-at-contact SD 7.93° and 9.16° in comparable cohorts [5] — makes a
5.28° signal invisible at n = 12 for reasons requiring no mechanism at all.

⚠ This is a post-hoc interpretation of another group's data offered as consistent, **not** a
demonstration. It generates a specific test: in a mixed cohort, a bivariate model containing both a
spasticity and a strength term should recover at contact what single-variable correlation cannot.""",
    """### 4.2 The one adult-stroke attempt does not support this model, and says so at the relevant muscle

The comparison that matters is the gastrocnemius column of Cawood and Mashola [7], because
gastrocnemius is one of the two muscles lesioned here. **In those 12 patients, gastrocnemius tone was
not significantly related to knee angle at any stance phase, initial contact included (ρ = 0.362,
p = 0.22).** This model predicts the opposite: that knee angle at contact grades plantarflexor
spastic severity, and grades it strongly (§3.2). The only patient dataset that has measured exactly
that relationship does not find it. We state this plainly rather than reconciling it away.

Three things bear on how much weight the null carries. It is a feasibility pilot of 12 participants
of whom only 9 had any gastrocnemius tone, graded on an ordinal 0–5 scale against 2D video, and its
authors present it as underpowered. Between-patient spread in comparable cohorts — knee-at-contact SD
7.93° and 9.16° [5] — would hide a 5.28° signal at n = 12 for reasons requiring no mechanism at all.
And the cancellation demonstrated in §3.2 predicts attenuation specifically in mixed cohorts: if the
two lesions displace the knee in opposite directions, correlating one component while the other
varies freely pulls the association toward zero, so that a limb with severe spasticity and severe
weakness reads at the knee much like one with mild spasticity and mild weakness.

⚠ Those three are reasons the null is weak evidence, not reasons to set it aside. **As things stand,
the single most relevant patient comparison available runs against the spastic arm of this model.**

The pilot's positive finding is orthogonal to ours rather than confirmatory: tibialis anterior tone
related to knee angle at contact, terminal stance and pre-swing. Tibialis anterior is the muscle this
study lesions by *weakening*, not by adding tone, so the two results concern different perturbations
of the same muscle and cannot be compared directly. It is nonetheless the second independent
indication in this manuscript — with the patient dataset of Limitation 5 — that the dorsiflexor side
of the ankle, not the plantarflexor side, is what visibly moves the knee in real hemiparetic gait.

This generates the specific test: in a mixed cohort, a model containing both a plantarflexor
spasticity term and a dorsiflexor term should recover at contact what single-variable correlation
cannot — and should be powered against the between-patient spread above, roughly 41 per group.""",
    "4.2 rebuilt on gastroc null")

# ---- 3.2 sub-phase: the model/patient window comparison was against the wrong column ----------
rep("""Only contact and loading response separate the lesions **by sign**. From midstance both displace the
knee toward extension and the difference falls to 0.7–1.7°; the defensible statement concerns loss
of the sign contrast, not weakness disappearing.""",
    """Only contact and loading response separate the lesions **by sign**. From midstance both displace the
knee toward extension and the difference falls to 0.7–1.7°; the defensible statement concerns loss
of the sign contrast, not weakness disappearing. The model's strongest *dose* window is loading
response. No patient comparison is available for that ordering: the one study to grade plantarflexor
tone against knee angle across these same five windows found no significant relationship in any of
them (§4.2), so the model's window profile is at present untested rather than confirmed or
contradicted.""", "3.2 window comparison")

# ---- Limitation 11: resolved, against us -----------------------------------------------------
rep("""11. **One literature point is unresolved.** Which muscle's tone carries the two significant
    correlations in [7] is not settled in our reading; if they are dorsiflexor rather than
    plantarflexor tone, §4.2's mapping onto a plantarflexor dose curve does not hold. We flag this
    rather than assert either reading.""",
    """11. **The most relevant patient comparison is adverse, and earlier drafts of this manuscript
    misreported it.** Gastrocnemius tone is unrelated to knee angle at every stance phase in [7],
    against this model's central dose prediction (§4.2). Earlier drafts attributed that paper's
    significant correlations to plantarflexor tone and described it as reporting a null at initial
    contact; both were extraction errors on our part, and the accompanying charge that its abstract
    and table contradict each other is withdrawn — they agree. The values now reported are read from
    the publisher's HTML galley and corroborated by the paper's abstract and Results prose.""",
    "limitation 11 resolved")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
for bad in ["0.542", "0.069", "0.745", "p = 0.005", "0.672", "plantarflexion-direction tone",
            "The plantarflexor version"]:
    assert bad not in s, "STALE CAWOOD VALUE STILL PRESENT: %s" % bad
print("stale Cawood values: none remain")
