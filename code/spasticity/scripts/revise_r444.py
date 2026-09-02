# -*- coding: utf-8 -*-
"""r444: apply the findings of three cold audits to MANUSCRIPT_r442.md.

Every change below was re-derived by me from the deposit it concerns before being applied.
Three auditor claims were CHECKED AND REJECTED and are NOT applied:

  (a) "the cross-joint spanning verdict was withdrawn in the strong form" -- the auditors quoted
      CORRECTION_r427, which r428 itself withdrew. SPANNING_RESULT_r421 /
      CORRECTION_r427_IS_ITSELF_WITHDRAWN_r428 / FINAL reads "ALL THREE JOINTS SEPARATE ... THE
      ORIGINAL r421 VERDICT STANDS AND CORRECTION_r427 IS WITHDRAWN." Section 3.7 is correct.
  (b) "registered-only weakness spans are 0.518 / 0.302 / 1.263" -- that is an auditor's own
      recomputation and appears in no deposit. REGISTERED_ONLY_P2 says UNINFORMATIVE at every
      dose, so no registered span exists to quote. The numbers are labelled post-hoc instead.
  (c) "Cawood's significant correlations are tibialis anterior tone" -- NOT VERIFIED. Web access
      was rate-limited before I could read the galley myself. I have been wrong on this
      literature four times by trusting summaries, so nothing is changed on this point and it is
      recorded as an open item.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r442.md"
shutil.copyfile(P, P.replace("MANUSCRIPT_r442.md", "MANUSCRIPT_r442.md.bak_r444_precouncil2"))
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# =============================================================================================
# ABSTRACT
# =============================================================================================
rep("""classification of lesion type was 50.9% from ankle angle at contact — chance — and 98.3% from knee
angle at the same instant; the two variables correlated at r = 0.18, so the knee is not redundant
with the ankle. The opposite-sign behaviour was confined to contact and loading response; from
midstance onward both lesions displaced the knee in the same direction. Across a 96-cell grid
spanning four weakness depths and four spastic gains, knee angle at contact graded spasticity
monotonically, but the weakness axis was the size of re-running an identical lesion with a
different optimisation seed. Different lesion combinations produced identical readings, the
starkest pair differing by 0.002°. Under a simulated sagittal video pipeline with per-frame
keypoint noise, camera yaw and event-detection error, lesion type was classified at 97% for
isolated lesions and spastic severity at 83% across mixed lesions.""",
    """classification of lesion type was 50.8% from ankle angle at contact — chance — and 98.3% from knee
angle at the same instant. The opposite-sign behaviour was confined to contact and loading response;
from midstance onward both lesions displaced the knee in the same direction. **Over stance rather
than at contact, the ankle does separate the two lesions** (2.34°, d = −5.61), but almost entirely
because spasticity moves it — weakness shifts it 0.04° — so that readout grades spasticity rather
than discriminating the two lesions. On a registered 3 × 3 dose grid, knee angle at contact graded
spasticity monotonically, while the registered weakness-axis prediction was UNINFORMATIVE because
its deepest row could not walk. Different lesion combinations produced overlapping readings, the
starkest registered pair differing by 0.30°. Under a simulated sagittal video pipeline, lesion type
was classified at 97% for isolated lesions and spastic severity at 83% across mixed lesions.

**The displacement is not large enough to be measured.** Against the most conservative defensible
knee threshold — a 7.25–7.62° change-score MDC₉₅ band, one value the arithmetically corrected
healthy knee-at-contact figure and the other the largest discrete knee MDC in chronic stroke — the
5.28° effect does not clear either bound, and neither does any of the 24 like-for-like comparisons
in the underlying ladder.""", "abstract results")

rep("""Three qualifications belong with that sentence rather than after it. **The comparison was
exploratory**: contact was examined because a stance-mean ankle result and a contact-instant ankle
result disagreed, not because it was nominated in advance. **The sign reversal depends on the
controller being re-optimised**: with the controller frozen, an isolated soleus-weakness condition
displaced the knee to -13.33 deg against the spastic arm's -13.20 deg, matching it in sign and
magnitude. And **the muscle-level cause is unknown** — seven preregistered mechanism hypotheses were
tested and all were retired. This is a hypothesis-generating simulation with a testable prediction
attached, not a validated clinical measure.""",
    """This licenses a claim that the endpoint **discriminates the two lesions in simulation**. It does
not license a claim that the difference would be detectable in an instrumented clinical gait lab.

Five qualifications belong with that sentence rather than after it. **The comparison was
exploratory**: contact was examined because a stance-mean ankle result and a contact-instant ankle
result disagreed, not because it was nominated in advance. **The two arms are perfectly separated on
survival time** — every control and weakness cell walks the full 20 s, every spastic cell falls
between 9.8 and 17.9 s — so the contrast is between a gait that never falls and one that always
does, and this design cannot decide how much of the effect that accounts for. **The sign reversal
depends on the controller being re-optimised**: with the controller frozen, an isolated
soleus-weakness condition displaced the knee to −13.33° against the spastic arm's −13.20°, matching
it in sign and magnitude. **There is no contracture arm**, and contracture holds the foot
plantarflexed at contact by the same final common path, so nothing here shows the readout is
specific to reflex overactivity. And **the muscle-level cause is unknown** — seven preregistered
mechanism hypotheses were tested, six were retired outright and the seventh survives only as a
mechanical fact whose functional consequence is refuted. This is a hypothesis-generating simulation
with a testable prediction attached, not a validated clinical measure.""", "abstract conclusion")

# =============================================================================================
# 3.1 — the omitted third endpoint, the correct judging correlation, the survival confound,
#       the unlesioned-side control, and the uneven rungs
# =============================================================================================
rep("""| endpoint at foot contact | control | weakness | spasticity | weakness − control | spasticity − control | lesion difference |
|---|---|---|---|---|---|---|
| ankle angle (°) | −0.656 | −1.516 | −1.460 | **−0.860** | **−0.804** | **0.056** |
| knee angle (°) | −7.850 | −6.492 | −11.772 | **+1.358** | **−3.922** | **5.280** |""",
    """| endpoint | control | weakness | spasticity | weakness − control | spasticity − control | lesion difference | *d* |
|---|---|---|---|---|---|---|---|
| ankle angle at contact (°) | −0.656 | −1.516 | −1.460 | **−0.860** | **−0.804** | **0.056** | +0.08 |
| knee angle at contact (°) | −7.850 | −6.492 | −11.772 | **+1.358** | **−3.922** | **5.280** | −5.28 |
| ankle angle over stance (°) | +4.485 | +4.521 | +2.179 | **+0.036** | **−2.306** | **2.342** | −5.61 |

**The third row is the competing readout, and it must be read carefully.** Over stance rather than
at the contact instant, the ankle separates the two lesions with a *larger* Cohen's *d* than the
knee at contact (−5.61 against −5.28) and at 33.0 within-cell seed SD against the knee's 12.4. It is
omitted from no analysis here and it is not weaker than the headline in simulation units. What
distinguishes the two is *what carries the contrast*: over stance, weakness displaces the ankle by
0.036° — essentially nothing — and the entire 2.342° is spasticity moving away from control. That
endpoint therefore **grades spasticity**; it does not respond to both lesions, so it cannot place a
limb on a two-lesion axis. The knee at contact is the only endpoint measured here that moves in
*opposite directions* under the two lesions. In clinical-error units the ordering also reverses
(2.14 versus 4.43 SEM). A reader who wants a spasticity meter should use the ankle over stance; a
reader who wants to tell the two lesions apart cannot.""", "3.1 ankle_stance row")

rep("""Cohen's *d* for lesion type was +0.081 at the ankle and −5.284 at the knee, computed on cells pooled
across dose. **Decision rule 4 forbids judging on a dose-pooled statistic**, so these are reported
and not treated as evidence. Leave-one-out classification — leaving out one *cell*, nearest centroid
with pooled covariance — gave **50.9% from the ankle and 98.3% from the knee** against a 50% chance
baseline for this two-class problem; both together gave 100%. Cells within a family share an
optimisation lineage, so the effective number of independent units is below 59 and these accuracies
are optimistic. The two endpoints correlated at r = 0.18, so the knee is not redundant with the
ankle.""",
    """Cohen's *d* for lesion type was +0.081 at the ankle and −5.284 at the knee, computed on cells pooled
across dose. **Decision rule 4 forbids judging on a dose-pooled statistic**, so these are reported
and not treated as evidence. Leave-one-out classification — leaving out one *cell*, nearest centroid
with pooled covariance — gave **50.8% from the ankle and 98.3% from the knee** against a 50% chance
baseline for this two-class problem; both together gave 100%. Cells within a family share an
optimisation lineage, so the effective number of independent units is far below 59 — there are 12
families, not 59 independent systems — and these accuracies are correspondingly optimistic.

**Redundancy, judged under rule 4.** The pooled correlation between the two contact endpoints is
r = 0.18. That is the dose-pooled statistic the rule forbids judging on; the within-dose-centred
correlation, which the rule mandates, is **r = 0.619**. The two endpoints therefore share about 38%
of their variance within lesion type, and an earlier draft quoted only the pooled figure and
concluded the knee "is not redundant with the ankle". The defensible statement is weaker: the knee
is *not a mirror* of the ankle, and it separates the lesions where the ankle at that instant does
not, but the two are substantially coupled.

**Survival is perfectly confounded with lesion type.** All 6 control and all 36 weakness cells reach
the 20 s simulation horizon; all 23 spastic cells fall, between 9.81 and 17.85 s. The two arms do
not overlap on end time at all. Decision rule 2 requires a within-dose regression of the endpoint on
end time to be propagated into any reported effect — **and that control cannot be computed for this
contrast**, because there is no shared range over which to estimate it. Where the control *can* be
run, on the mixed grid of §3.3 where both axes vary within cells that all walk, the within-dose
slope is −0.0865 °/s and accounts for 9% of the span, below the 50% bar
[`MIXED_RESULT_r424.json`, `HEADLINE_DURATION_QUANT_r417.json`]. Applying that slope across the
roughly 7 s gap between the arms would account for about 0.6°, some 12% of the 5.280°. That is an
extrapolation across a gap, not a control: **the honest statement is that the two arms separate on
knee angle at contact and also differ in survival, and this design cannot decide how much of the
first is the second.**

**Unlesioned-side negative control, and where it fails.** Both lesions are left-only, so the right
knee should not separate. Pooled over the ladder it separates 6 of 24 times against the left knee's
24 of 24 — but those 6 are not spread across the ladder. At KV 0.050, 0.070 and 0.100 the right knee
separates 0/6 while the left separates 6/6. **All six right-knee separations come from the single
rung KV 0.110**, the rung that produces the largest left-knee gap. At that rung the displacement is
bilateral. It is not a pipeline artefact — the right knee's own batch false-positive rate on this
endpoint is 0/15 — and it is strongly lateralised, the right-knee edge gaps being 0.88–1.63° against
the left's 5.46–6.39°, about four times less. The honest reading is that **strict lesion-side
specificity holds at KV ≤ 0.100 and fails at KV 0.110** [`KNEE_MDC_BATCHNULL_r399.json`].

**The pooled spastic arm is uneven.** Of the five spastic families, R151S and R393SPg070 contribute
6 Gate-G cells each, R393SPg100 four, R396SPg110 four, and R396SPg120 only three — below the
four-cell bar, so that rung is UNINFORMATIVE on its own and is reported, not dropped. Gate-G
admissibility is itself lesion-dependent, so the 23-versus-36 sample is differentially filtered.""",
    "3.1 rule 4 + duration + side control")

# =============================================================================================
# 3.3 / 3.4 — post-hoc labelling, and the registration's own critical prediction
# =============================================================================================
rep("""| axis | effect (°) | in within-cell seed SD |
|---|---|---|
| spastic axis, ×1.00 (KV 0.0125 → 0.050) | 4.270 | 8.3 |
| spastic axis, ×0.80 | 3.525 | ~7 |
| spastic axis, ×0.70 (post-hoc row) | 3.007 | ~6 |
| weakness axis at KV 0.0125 | 0.520 | **1.0** |
| weakness axis at KV 0.025 | 0.458 | **0.9** |
| weakness axis at KV 0.050 | 1.784 | 3.5 |

Registered P1 (spastic axis monotone, more flexed with rising gain) **holds** on the three
registered rungs in every judgeable row. Registered P2 (weakness axis monotone) is
**UNINFORMATIVE**: the registered ×0.60 row has no cell reaching the four-seed bar under either
chaining route [`RESCUE_RESULT_r426.json`]. The weakness effect at low spastic gain is the size of
re-running the identical lesion with a different optimisation seed.""",
    """| axis | effect (°) | in within-cell seed SD | status |
|---|---|---|---|
| spastic axis, ×1.00 (KV 0.0125 → 0.050) | 4.270 | 8.3 | registered |
| spastic axis, ×0.80 | 3.525 | ~7 | registered |
| spastic axis, ×0.70 | 3.007 | ~6 | **post-hoc row** |
| weakness axis at KV 0.0125 | 0.520 | **1.0** | **computed through the post-hoc ×0.70 row** |
| weakness axis at KV 0.025 | 0.458 | **0.9** | **computed through the post-hoc ×0.70 row** |
| weakness axis at KV 0.050 | 1.784 | 3.5 | **computed through the post-hoc ×0.70 row** |

Registered P1 (spastic axis monotone, more flexed with rising gain) **holds** on the three
registered rungs in every judgeable row. The fourth spastic gain, KV 0.110, is an unregistered
column added after hashing and is excluded from every figure above; with it included the ×0.80 span
becomes −8.033° rather than −3.525°, and that larger post-hoc number travelled into earlier
summaries of this project before the deviation was caught [`REGISTRATION_DEVIATIONS_r438`].

Registered P2 (weakness axis monotone) is **UNINFORMATIVE at every dose**: the registered rows are
×1.00 / ×0.80 / ×0.60, and the ×0.60 row has no cell reaching the four-seed bar under either
chaining route [`RESCUE_RESULT_r426.json`]. The three weakness-axis numbers above all run
×1.00 → ×0.80 → ×0.70 and therefore depend on a substituted row; **they are post-hoc, and an earlier
"P2 holds" built on them is withdrawn as a registered result.** What survives registration is the
*direction* of both axes, not the magnitude of the weakness one.

**The registration's own critical prediction was not judgeable.** `PREREG_mixed_r424.md` §5 marks P3
— that mixed lesions are rankable by dominant component — as 關鍵預測, the key prediction, and states
that if it fails the clinical claim fails. Its registered weakness-dominant cell is KV 0.0125 at
×0.60, the row that cannot walk, and §8 forbids substituting another. **P3 is therefore
UNINFORMATIVE as registered**, and the only version of it that can be evaluated uses the post-hoc
×0.70 substitute, where spasticity-dominant and weakness-dominant cells separate by 2.67° and 2.51°.
That substitute carries the deposit's own caveat: the separation is achieved because spasticity
moves the readout, not because both lesions are measured
[`MIXED_RESULT_r424.json`]. The weakness effect at low spastic gain is the size of re-running the
identical lesion with a different optimisation seed.""", "3.3 post-hoc labels + P3")

rep("""Registered P4 predicted that cancellation would exist, and it does: of 45 comparable cell pairs,
15 overlap. The starkest is ×0.80 and ×0.70 weakness at KV 0.0125 — two different weakness depths
differing by **0.002°** at the knee. A single reading cannot recover the lesion combination.""",
    """Registered P4 predicted that cancellation would exist, and it does. Counting registered cells only,
**6 of 15 comparable pairs overlap, the starkest differing by 0.30°** (×1.00 and ×0.80 weakness at
KV 0.025). Including the post-hoc ×0.70 row and KV 0.110 column the count is 15 of 45 and the
starkest pair differs by 0.002° — but that pair *is* the post-hoc row, and 0.002° is in any case
three orders of magnitude below this endpoint's convention sensitivity: resampling the same
simulation output onto a uniform 60 Hz grid before reading the same endpoint moves it by 0.52° with
no noise added at all [`VIDEOKNEE_r422.json`]. **Quantities from this endpoint are reported to one
decimal place; 0.002° should not be read as a measurement.** The registered finding stands on the
0.30° figure: a single reading cannot recover the lesion combination.""", "3.4 registered-only")

# =============================================================================================
# 3.6 — rebuilt on the band the project itself settled on
# =============================================================================================
rep("""Back-deriving a single-measurement standard error from published minimal detectable change
(MDC₉₅ = 1.96·√2·SEM):

| | knee at contact | ankle at contact |
|---|---|---|
| healthy adults, ICC | 0.825 | 0.774 |
| SEM (°) | 1.55 | 1.27 |
| MDC₉₅ (°) | 4.29 | 3.52 |
| Bland–Altman LoA (°) | −6.78 to +7.74 | −4.54 to +5.93 |

[LIT: Molina-Rueda F et al. *Int J Environ Res Public Health* 2021;18(3):1343, verified].
No equivalent exists for either angle at contact in any neurological population; the only
neurological value located is ankle-at-contact MDC 7.0° in chronic stroke [LIT: Kesar TM et al.
*Gait Posture* 2011;33(2):314–317], which reports no knee-at-contact figure.

Averaging over six contacts reduces the single-measurement SEM by sqrt(6). Using the published knee
SEM of 1.55 deg from the same table as the ICC, that is 0.63 deg, and the 5.28 deg lesion difference
is 8.3 effective SEM. An earlier draft used 2.75 deg, back-derived from a more conservative 7.62 deg
MDC drawn from a different source; mixing two sources was an error and is corrected here.

**However**, the same authors state that a between-session difference below **9 deg** at contact may
be attributable to system or observer error. The 5.28 deg effect does not clear that. The two
thresholds disagree by a factor of two and this manuscript does not choose between them — but any
clinical use of this readout is inherently between-session, patient against norm or before against
after, so the 9 deg figure is the governing one, and by it the effect is **not** detectable.""",
    """The question is whether a 5.28° difference could be seen in a gait laboratory. It is answered
against a **change-score MDC₉₅**, because every clinical use of this readout is between-session —
patient against norm, or before against after an intervention.

| source | population | variable | MDC₉₅ (°) |
|---|---|---|---|
| Molina-Rueda 2021, as published | healthy adults | knee at contact | 4.29 |
| Molina-Rueda 2021, **corrected** | healthy adults | knee at contact | **7.25** |
| Geiger 2019 | chronic stroke, between-day | knee minimum in stance | 6.34 |
| Geiger 2019 | chronic stroke, between-day | largest discrete knee MDC | **7.62** |
| Kesar 2011 | chronic stroke | peak knee flexion in swing | 5.7 |
| Kesar 2011 | chronic stroke | ankle at contact | 7.0 |

**The published 4.29° must not be used.** Its formula substitutes SD_diff where the between-subject
SD is required, understating the MDC by √2; the same paper's own Bland–Altman limits of agreement
(−6.78° to +7.74°, half-width 7.26°) contradict its table and confirm the corrected value of 7.25°
[LIT: Molina-Rueda F et al. *Int J Environ Res Public Health* 2021;18(3):1343, Table 1 read
directly]. A previous draft of this manuscript tabulated 4.29° without the flag, and a further draft
divided a between-session SEM by √6 to obtain an "effective" figure of 0.63°. **Both are withdrawn.**
The √n step is invalid here: the published SEM is a *between-session* quantity already computed from
five repetitions per session, so it carries marker placement, calibration and observer error, none
of which averages down over contacts within a single recording.

Limitation 7 of an earlier draft asserted that no knee MDC exists for a neurological population.
That is **false as written** and is corrected here: no knee-**at-initial-contact** MDC exists in a
neurological population, but neurological knee MDCs do — Geiger 2019 in chronic stroke, between-day,
overground [LIT: Geiger M et al. *Hum Mov Sci* 2019;64:101–107], and Kesar 2011's swing figure
[LIT: Kesar TM et al. *Gait Posture* 2011;33(2):314–317].

**The most conservative defensible band is 7.25–7.62°**, where two independent routes converge: the
corrected healthy knee-at-contact value (right variable, right event, wrong population — and healthy
values understate neurological error) and the largest discrete knee MDC in chronic stroke (right
population, wrong event).

**The 5.28° effect does not clear it.** Nor does the underlying ladder: across all 24 like-for-like
comparisons the edge gaps run 1.49° to 6.39°, median 4.61°; 14 reach 3.8°, three reach 5.7°, one
reaches 6.39°, and **zero reach 7.25°** [`KNEE_MDC_BATCHNULL_r399.json`]. The single largest gap
anywhere in the chained ladder still falls short. Separately, the source authors state that a
between-session difference below **9°** at contact may be attributable to system or observer error,
which the effect also fails.

This manuscript therefore does not claim clinical detectability. What the result licenses is that
**the endpoint discriminates the two lesions in simulation, with a dose-monotone gap**; it does not
license a claim that the difference would be detectable in an instrumented clinical gait lab. Any
patient study must either average many more contacts than a standard session provides, use a
within-patient design where session-level error cancels, or wait for a measurement method with a
smaller between-session error than marker-based gait analysis currently has.""", "3.6 rebuilt")

# =============================================================================================
# 3.8 — the inferential backbone, with its own qualification attached
# =============================================================================================
rep("""### 3.7 No mechanism was found, and the search is documented **[REG]**""",
    """### 3.7a The separation survives a measured batch null **[EXP]**

Disjointness between two arms is a weak statistic if optimisation batches routinely produce it. It
was therefore measured. Among the six dorsiflexor-weakness families — which share a mechanism and a
severity range, and so *should not* separate from one another — 4 of 15 pairs separate on knee angle
at contact, a batch false-positive rate of **26.7%**. Against that null, the like-for-like spastic
versus weakness comparisons separate **24 of 24** (binomial p = 1.67 × 10⁻¹⁴)
[`KNEE_MDC_BATCHNULL_r399.json`]. The four spurious same-mechanism separations have edge gaps of at
most 0.57°, against a median 4.61° for the real contrast: **the batch null produces disjointness but
not magnitude.**

⚠ Two qualifications travel with this. First, 26.7% is *higher* than the 21.3% measured on a
different endpoint in this project, and it is **123 times** the 2/924 = 0.22% exhaustive-permutation
floor the project quoted for most of its life. The permutation floor materially overstates the
evidence for any single disjointness claim on this endpoint, and this manuscript does not use it.
Second, the null rests on a single cohort of 15 pairs; the corresponding plantarflexor-weakness
cohort could not be computed at all, because at most one of those five families reaches four Gate-G
cells.

A sham control addresses the obvious objection to warm-start chaining: reading the endpoint across a
protocol change with no lesion difference shifts it by 0.586°, against the 6.39° that the chained
ladder produces [`SHAM_READOUT_r406.json`]. Chaining cannot account for the gap.

### 3.7 No mechanism was found, and the search is documented **[REG]**""", "3.7a batch null")

rep("""Seven mechanism hypotheses were preregistered and tested; all are retired
[`MECHANISM_SCOREBOARD_r430.json`].""",
    """Seven mechanism hypotheses were preregistered and tested. Six are dead outright and the seventh
survives only as a mechanical fact whose functional consequence is refuted; none is live
[`MECHANISM_SCOREBOARD_r430.json`, `FINAL_r431`]. One of the seven was wrongly retired, reinstated,
and then properly retired at ten times the power — the sequence is in the deposit.""",
    "3.7 seven retired")

# =============================================================================================
# 4.2 — the deposit scored this DISAGREE
# =============================================================================================
rep("""angle while the other varies freely will attenuate the association toward zero. The cancellation
demonstrated in §3.4 is the mechanism by which that would happen. On this reading Cawood's null at
contact is what the present model predicts for a mixed cohort, and their significant late-stance
result matches §3.2, where both lesions displace the knee in the *same* direction and the readout
grades spasticity rather than distinguishing it.""",
    """angle while the other varies freely will attenuate the association toward zero. The cancellation
demonstrated in §3.4 is the mechanism by which that would happen. Concretely: a limb with severe
spasticity and severe weakness reads at the knee much like one with mild spasticity and mild
weakness, so a correlation against spasticity alone in a mixed cohort is flat by construction. On
this reading Cawood's null at contact is what the present model predicts for a mixed cohort.

**The agreement does not extend to where significance landed, and the analysis that produced §3.2
scored this as a disagreement.** The model's strongest dose window is loading response; Cawood's is
terminal stance. `SUBPHASE_r441.json` records the verdict verbatim: *"model and patients DISAGREE:
the model's strongest dose window is loading_response, Cawood's is terminal_stance."* What is
reconciled is the *null at contact*, not the location of the significant result. A more parsimonious
account of the null should also be stated: with 12 participants, a six-level ordinal tone grade and
2D video, the study is underpowered, and its authors say so.""", "4.2 disagreement")

# =============================================================================================
# 6.1 — the patient data say more than "cannot test", and half of it is adverse
# =============================================================================================
rep("""1. **Simulation only.** No patient data. A public stroke gait dataset was examined and found
   structurally unable to test this discrimination — no spasticity scale, no strength scale, no
   soleus channel, no MVC normalisation, no walking speed [`PUBLICDATA_VALIDATION_r405.json`].""",
    """1. **Simulation only, and the one real-patient dataset examined is half against us.** A public
   dataset of 50 stroke survivors was examined. It cannot test the discrimination — no spasticity
   scale, no strength scale, no soleus channel, no MVC normalisation, no walking speed — but on the
   one relation it can speak to it is **not neutral** [`PUBLICDATA_VALIDATION_r405.json`]. Ankle
   angle at contact and knee deviation from the able-bodied norm correlate at r = +0.613
   (p = 2.2 × 10⁻⁶, n = 50), and limbs contacting plantarflexed sit 6.31° from the norm against
   17.09° for limbs contacting dorsiflexed — a 10.8° separation, twice the effect claimed here.
   **That is the model's weakness mechanism visible in real patients**: dorsiflexor failure →
   plantarflexed contact → less knee flexion. **It simultaneously contradicts the spastic arm.**
   Spastic plantarflexor overactivity should produce plantarflexed contact *and more* knee flexion;
   in these data plantarflexed contact goes with *less*. Without a severity measure the two
   subgroups cannot be shown to be distinct phenotypes rather than milder versus more severe, and
   no speed control is available — but the direction is adverse and is reported as such.

1a. **Half of real paretic limbs do not heel-strike.** In the same 50 limbs, 25 contact the ground
   plantarflexed, i.e. forefoot- or flatfoot-first. The initial-contact *event* remains valid (the
   authors detected it from force plates and marker trajectories, not by assuming a heel strike),
   but "knee angle at initial contact" then **pools two mechanically different events** — and the
   pooling is not random, since contact type is itself downstream of the lesion. §4.4 asks
   clinicians to measure at foot contact; in half the target population that instant is a different
   event, and this must be resolved before any such measurement is attempted.""", "6.1 public data")

rep("""7. **Reliability figures are extrapolations.** No knee-at-contact MDC exists for any neurological
   population; healthy-adult values are a lower bound because measurement error is larger in
   neurological gait.""",
    """7. **Reliability figures are extrapolations.** No knee-**at-contact** MDC exists for any
   neurological population, though neurological knee MDCs at other events do (§3.6); healthy-adult
   values are a lower bound because measurement error is larger in neurological gait.""",
    "limitation 7 corrected")

rep("""14. **Sections 3.1, 3.2 and 3.6 are exploratory.** The contact-versus-stance comparison was chosen
    after observing that a stance-mean ankle result and a contact-instant ankle result disagreed.
    They require confirmation on untouched material before carrying a confirmatory claim.""",
    """14. **Sections 3.1, 3.2 and 3.6 are exploratory.** The contact-versus-stance comparison was chosen
    after observing that a stance-mean ankle result and a contact-instant ankle result disagreed.
    They require confirmation on untouched material before carrying a confirmatory claim.

15. **The one time this project ran a confirmatory test on untouched material, it did not
    replicate.** A registered one-dimensionality structure that explained 95% of the knee variance
    in the exploratory pool explained 0.17% in a 64-cell confirmatory pool, and all four registered
    predictions failed [`ONEDIM_RESULT_r409.json`]. That was a different claim from the one made
    here, but it is the project's only exploratory-to-confirmatory transfer and it went badly. It is
    the reason limitation 14 is not a formality.

16. **Reflex gains in this project are recorded at half their effective value.** Every KV quoted
    here is a nominal gain; the delivered gain is exactly twice it, measured structurally as a copy
    count of 2.000000 ± 7 × 10⁻⁶ across 102 measurements [`KV_RELABELLING_NOTE.md`]. Nominal values
    are retained throughout for consistency with the deposits, and anyone re-implementing the model
    must apply the factor of two.""", "limitations 15-16")

# =============================================================================================
# 7 — the data statement claims something about figures that do not exist
# =============================================================================================
rep("""All simulation outputs, preregistrations with hashes, analysis scripts, correction records and
defect registers are in `spasticity_paper/`. Every figure in this manuscript names the deposit it
comes from.""",
    """All simulation outputs, preregistrations with hashes, analysis scripts, correction records and
defect registers are in `spasticity_paper/`. Every number in this manuscript names the deposit it
comes from; this draft contains no figures (limitation 13). Of 1129 run directories, 1113 hold both
the parameter file and its replayed output [`INSURANCE_REPLAY_r415.json`]. Hyfydy is commercial
software and the licence under which these simulations were produced expired on 2026-08-27, which
is a reproducibility constraint a reader should know about.""", "7 data statement")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars (was 34196)" % len(s))
