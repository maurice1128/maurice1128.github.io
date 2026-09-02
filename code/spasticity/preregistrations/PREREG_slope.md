# PRE-REGISTRATION — downhill provocation as a test of velocity dependence

**Status: REGISTRATION ONLY. Written 2026-08-03, BEFORE any slope scenario has been generated,
before any slope cell has been launched, and before any feature has been extracted from any slope
run in this project.**

This document registers a study. It does not launch one. No `.scone`, no `.osim` and no result
directory was created by the act of writing it.

> **SUPERSESSION NOTICE.** An earlier draft occupied this path (11,477 B, 2026-08-03 20:57) and is
> replaced in full. It is superseded for cause, and the causes are recorded here rather than
> deleted, because its numbers must not be quoted:
> 1. **It conflated two different margins.** It predicted a level-ground spastic arm mean of
>    ≈ 18.4° and a weak arm mean of ≈ 20.0° for a gap of "+1.6° (measured: +1.575°)". The measured
>    arm means are **17.618°** and **22.031°**, an arm-mean gap of **4.413°**. The 1.5752° figure is
>    the **rung-to-rung** margin (`PAR20` 20.6629 − `DR2K050` 19.0877), which is a different
>    quantity. Both quantities are real and both are registered here (§1.3, §4.1), but they are not
>    interchangeable and §7.2 of `RESULTS_discrimination.md` says explicitly which one binds.
> 2. **It carried no hash section**, which is the one item that makes a registration a registration.
> 3. Its primary endpoint did not name a computable function, its n = 4 was not justified against
>    any measured dispersion, and its falsifier ("the CI includes zero") is not a condition stated
>    in units that can be checked against this design's precision.
>
> Its three good ideas are retained below and attributed: the effective-test-count rule (§4.6), the
> "a registered secondary absent from Results is a protocol violation" rule (§4), and the deviations
> log (§10).

> **Deliberate non-reading, recorded so it cannot be claimed later.** The `RD2*` / `RE2*` −2°
> downhill family exists on disk in `scone/opt_slope/` and has never had a feature extracted from
> it (`PREREGISTRATION_slope_velocity_dependence.md`, 2026-07-27). **This registration did not read
> it, and the study excludes it** — those runs carry `init_file = D2HEALTHY_resume.par`,
> `min_progress = 1e-7` and `max_generations = 60` (verified this round from
> `scone/opt_slope/RD2HEALTHY.scone` lines 3–5), a different budget and a warm start, and are
> therefore inadmissible under §5.3 regardless of what they contain. Reading them first would have
> made every prediction below unfalsifiable.

---

## 0. Why this study exists, and what it is allowed to conclude

### 0.1 The problem it addresses

A completed 48-run level-ground study (`COUNCIL_round48.md`, `CROSSED_RESULT.json`,
`ROM_REANALYSIS.json`, `COUNCIL_round50.md`) established that plantarflexor spasticity and
tibialis-anterior weakness are **statistically separable** on left-ankle range of motion
(`ank_rom`): condition-level AUC 0.0000, exact p 0.0079365, overlap 0/5; seed-level AUC 0.0125,
MWU p 1.43 × 10⁻⁷ on 20 vs 20; the two lesions move the feature in **opposite directions** about an
unlesioned reference of 20.0134°.

It equally established that this is **clinically undetectable at mild severity**. The binding
quantity is the rung-to-rung gap between the mild rungs of the two arms:

| quantity | value | source |
|---|---|---|
| mild rung-to-rung margin, clean kinematics | **1.5752°** | `LR_ASYMMETRY.json` `mild_l.margin`; = `PAR20` 20.6629 − `DR2K050` 19.0877 (`ROM_REANALYSIS.json`) |
| same margin through the registered video pipeline, baseline | 2.392° | `RESULTS_discrimination.md` §7.3 caveat |
| **largest value that margin takes across all 120 observation cells** | **2.84°** | `RESULTS_discrimination.md` §7.2 (30 Hz, fixed yaw 30°, σ = 2°) |
| smallest value across those cells | 0.75° | §7.2 |
| *(mild **arm-mean** gap, clean — the non-binding alternative)* | *4.413°* | computed from the four mild condition means |
| **post-stroke ankle minimal detectable change (MDC)** | **3.800°** | the programme's standing decision floor |

`RESULTS_discrimination.md` §7.2 states which one binds and why, unprompted: *"The rung-to-rung gap
is the binding quantity for a screening decision, because a patient presents at one severity and not
as an average over a severity range."* **Six candidate features have now died at this floor.** The
margin has never reached the MDC under any observation condition tested. `ank_rom` is the sixth.

### 0.2 The mechanism this study registers as its rationale

Post-stroke equinus has two causes requiring opposite treatments — plantarflexor **spasticity** (a
velocity-dependent stretch reflex, modelled here as a soleus `MuscleReflex` gain `KV` on the left
limb) and tibialis-anterior **weakness** (modelled as scaled `max_isometric_force` in the `.osim`).
Both produce equinus; neither is distinguishable from the other by the presenting sign
(`RESULTS_negative.md` §1, p = 0.69 on equinus itself).

**Downhill walking drives faster loading-phase dorsiflexion.** On a decline the centre of mass falls
further during stance, so the shank rotates over the foot further and faster. That is precisely the
stimulus a velocity-dependent stretch reflex is *defined* to resist: a velocity-gated plantarflexor
reflex will clip the loading-phase dorsiflexion excursion, and clip it harder as the decline
steepens. **A weak tibialis anterior is not provoked by the same demand** — TA weakness limits the
ability to *raise* the foot, not the ability to be *stretched*; a decline adds eccentric TA demand,
which if anything permits a larger, faster, less-controlled excursion.

**So the two arms should diverge more as slope steepens.** That is the entire content of the
hypothesis, and it is Tardieu R1/R2 logic: the one property of the Lance definition that a severity
axis cannot mimic is a *disproportionate* response to *stretch velocity*.

### 0.3 What this study may and may not conclude

It may conclude something about **whether a provocation manoeuvre raises the effect size in this
simulation**. It may not conclude anything about patients: the replication unit here is a CMA-ES
optimizer seed, not a person, and §4.5 registers that limitation in force.

---

## 1. PRIMARY ENDPOINT — exact function, exact window, computable today

### 1.1 The feature

**`sto_utils.cycle_features(path, side="l", settle=1.0)["ank_rom"]`**

where `sto_utils` is `C:\Users\maurice\Desktop\spasticity_paper\scone\sto_utils.py` and `path` is
the single `.sto` produced by a registered replay (§1.2).

This is the raw, native-rate (100 Hz), **unfiltered** left-ankle range of motion in degrees. It is
the same variant that produced 20.0134 / 19.0877 / 16.1478 / 20.6629 / 23.3995 in
`ROM_REANALYSIS.json`.

**The window, stated exactly as the function computes it** (`sto_utils.py` lines 202–308), because
this project has already lost a result to feature-definition drift (`COUNCIL_round50.md` §4.3):

1. Vertical GRF for leg `_l` is taken by `grf_vertical(cols, data, "l")`, which returns
   (`*_l.grf_norm_y`, threshold **0.05** BW) if present, else (`*_l.grf_y`, threshold **20.0** N).
2. Heel strikes are upward crossings of that threshold, kept only if the foot **stays loaded for
   ≥ 0.15 s**, with events closer than **0.3 s** merged (`heel_strikes`, `min_stance = 0.15`).
3. Only strikes at **t ≥ 1.0 s** are used (`settle = 1.0`). A run needs **≥ 3** such strikes.
4. Cycles are consecutive heel-strike pairs, **with the last one dropped**. A run needs **≥ 2**
   surviving complete cycles or the function returns `None` → the seed is **excluded**.
5. `ank_rom` = mean over those cycles of `float(np.ptp(ank[a:b]))`, in degrees, left side.

**No filtering, no resampling, no projection is applied to the primary.** The 30 Hz + 4th-order
zero-phase 6 Hz Butterworth video pipeline is a registered *secondary* (§4.2). Mixing the two
variants inside one table is defect §4.3 of round 50 and is forbidden here by name.

*(The superseded draft registered the filtered 30 Hz variant as its primary. The choice is reversed
here deliberately: the clean variant is the one every published number in `ROM_REANALYSIS.json` and
`COUNCIL_round50.md` was computed on, so registering it keeps the slope cells commensurable with the
level result; and §7.3 of `RESULTS_discrimination.md` shows the 6 Hz filter is itself the single
largest degradation, removing 5.9–10.6° from the weak arm against 0.8–1.5° from every spastic
condition — a transformation that large belongs in a named secondary, not inside the primary.)*

### 1.2 How the `.sto` is produced

Never read whatever `.sto` happens to sit in a run directory — `sto_utils.py` lines 17–43 document
that not one of four audited anchor directories contained a `.sto` belonging to its own best
controller, and that 148 of 316 archived directories contain no `.sto` at all.

Per seed: `sto_utils.select_registered_par(run_dir)` selects the **minimum-fitness `.par`,
asserted to be the maximum-generation `.par`**; disagreement raises `RegisteredSelectionError` and
the seed is excluded under **E5**. That `.par` is then replayed by
`replay_all.replay_registered`, which copies the run's **own archived `config.scone`** into an
empty isolated directory and asserts exactly one `.sto` results.

### 1.3 The primary statistic

Let cell `(c, g)` be condition `c` at grade `g`. Write the **decline magnitude**
`D ∈ {0, 2, 5}` (degrees of downhill; `D = 0` is level), so that the mechanism predicts a
**positive** coefficient.

- Cell mean `ȳ(c, D)` = mean `ank_rom` over that cell's retained seeds.
- Arm means: `A_sp(D)` = mean of `ȳ` over {`DR2K050`, `DR2K075`}; `A_wk(D)` = mean over
  {`PAR20`, `PAR40`}.
- Arm gap `d(D) = A_wk(D) − A_sp(D)`.  Measured at level: `d(0) = 22.0312 − 17.6178 = 4.4134`.

**PRIMARY = β_int, the slope of the arm gap against decline:**

```
β_int  =  Σ_D (D − D̄) · d(D)  /  Σ_D (D − D̄)²        D̄ = 7/3 ,  Σ (D − D̄)² = 12.6667
```

estimated at seed level by OLS on the 12 primary cells with

```
ank_rom  ~  condition (4 levels, fixed)  +  D  +  arm : D
```

`β_int` is the `arm:D` contrast (weak minus spastic), in **degrees of arm gap per degree of
decline**. Reported with its standard error, its 95 % CI, and the implied gap at `D = 5`.

Everything in §1 is computable today: every function named exists on disk and was used to produce
the numbers in `ROM_REANALYSIS.json`.

---

## 2. THE PRIMARY IS AN INTERACTION, NOT "THE MARGIN GETS BIGGER"

**Registered: the claim survives only on a slope × mechanism INTERACTION.** `β_int > 0`, with the
unlesioned control's own slope-response reported alongside it. The marginal claim — *the mild
margin at −5° is larger than the mild margin at level* — is registered here as **insufficient**,
and it is a registered secondary (§4.1), never the primary.

**Three reasons it is insufficient, each grounded in a failure this project has already had:**

1. **A level shift is the default, not a finding.** This programme's established structure is that
   the feature space is one ordered axis and that axis is cost: discriminant score against fitness
   `r = 0.932` (n = 22); regressing the waveform on fitness collapses accuracy to 0.143, exact
   p = 1.0000; **every contiguous cut along the cost ordering classifies at 0.857 and every
   interleaved cut fails at 0.429** (`COUNCIL_round10.md` Part 1 A4). Adding a slope raises task
   cost in *both* arms. A margin that grows because both arms slid along the same cost axis is the
   severity account, not the mechanism account, and only the interaction — against a control that
   carries no lesion at all — separates them.

2. **A two-condition margin moves by corpus coincidence.** `RESULTS_discrimination.md` §7.3 records
   exactly this, unprompted: the 6 Hz filter *improves* the mild margin 1.575° → 2.392°, purely
   because `DR2K050` is attenuated 1.47° while `PAR20` is attenuated 0.65°. The draft's own words:
   **"That is a corpus coincidence, not a property of the feature."** A bare "the margin got bigger
   at −5°" is the same shape of claim and deserves the same treatment.

3. **The rung-to-rung margin is an order statistic** (`min` over weak cells minus `max` over
   spastic cells). Its sampling distribution is skewed and it can move because the *binding pair
   changed*, not because either arm moved. `β_int` is a linear contrast on arm means and is
   estimable; the margin is the decision quantity but not a sound test statistic.

**And, registered before the data exist so it cannot be spun afterwards: a positive `β_int` does
not by itself deliver a clinically usable instrument.** The binding quantity is the rung-to-rung
margin at `D = 5` reaching 3.800°. The study can return *"interaction confirmed, margin still under
the MDC"*, and that outcome is hereby registered as a **POSITIVE for the mechanism claim and a
NEGATIVE for the clinical claim**, to be written up as both. Registering the split now is what
stops a mechanism positive being reported as a clinical one.

**Also registered: the divergence must be arm-specific in the predicted direction.** A gap that
grows because the **weak arm alone** rises, with the spastic arm tracking the unlesioned control,
is a weak-arm finding and not evidence of a velocity-dependent reflex. The per-arm slope responses
of §3.2 are reported individually against the control's, and a `β_int > 0` produced entirely by the
weak arm is reported as such.

---

## 3. PREDICTED DIRECTION AND MAGNITUDE, PER ARM, PER SLOPE

### 3.1 Honesty preamble on where these numbers come from

**This project holds no verified citation for the magnitude of ankle-ROM change in downhill
walking**, in humans or in this model, and the citation quarantine imposed at `COUNCIL_round10.md`
§Q3 is binding. **No slope run in this project has ever had a feature extracted** (§0). Therefore
the numbers below are **mechanically reasoned ranges, not empirical extrapolations**, and the
reasoning is given so a referee can attack the reasoning rather than the number.

**The mechanical basis.** A decline of `D` degrees adds approximately `D` degrees of additional
shank-over-foot rotation during stance *if step geometry is preserved*. It will not be preserved:
CMA-ES re-optimises the controller at each grade and can absorb the demand at the knee, at the hip,
or by shortening the step. So the ankle absorbs somewhere between 0 % and 100 % of `D`. The point
estimates below assume the intact ankle absorbs roughly **60 %**.

### 3.2 Predictions

Level-ground `ank_rom` values are measured (`ROM_REANALYSIS.json`). Slope values are predicted.

| cell | `ank_rom` at D = 0 (**measured**) | predicted D = 2 | predicted D = 5 | predicted per-degree response |
|---|---|---|---|---|
| `DR2K000` control (no lesion) | **20.013** | 20.8 [20.4, 21.6] | 23.0 [21.5, 24.0] | **+0.60 [+0.30, +0.80]** |
| `PAR20` (TA ×0.80) | **20.663** | 22.3 [21.9, 22.7] | 24.7 [23.7, 25.7] | **+0.80 [+0.60, +1.00]** |
| `PAR40` (TA ×0.60) | **23.400** | 25.0 [24.6, 25.4] | 27.4 [26.4, 28.4] | **+0.80 [+0.60, +1.00]** |
| `DR2K050` (KV 0.050) | **19.088** | 19.3 [19.1, 19.7] | 19.6 [19.1, 20.6] | **+0.10 [0.00, +0.30]** |
| `DR2K075` (KV 0.075) | **16.148** | 16.3 [16.1, 16.8] | 16.6 [16.1, 17.6] | **+0.10 [0.00, +0.30]** |

**Reasoning per arm.**

- **Control** — an unlesioned ankle has no reflex clipping it and no force deficit; it takes most of
  the added demand. Predicted the largest response of any non-weak cell, and it is the reference
  against which "the reflex clips it" means anything.
- **Weak arm** — TA weakness does not resist stretch. A decline adds *eccentric* TA demand at
  loading, which a weakened TA controls worse, so the foot lowers further and faster. Predicted
  **at or slightly above** the control's response. The two weak rungs are predicted to respond alike
  because the deficit is in a muscle that is not the one being stretched.
- **Spastic arm** — this is the whole hypothesis. A velocity-gated soleus reflex opposes exactly the
  excursion the decline demands, and it engages harder as the excursion gets faster. Predicted
  **near-zero** response: the ankle is already at its reflex-limited excursion at level, and the
  decline is spent against the reflex rather than in the joint. **The interval is bounded at 0 below
  because I am not willing to predict a decrease without a mechanism for one** — the superseded
  draft predicted the spastic arm falling at −0.5°/degree, i.e. `DR2K075` reaching ≈ 13.6° at −5°,
  and no artifact in this project supports a ROM *reduction* of that size under any manipulation.

### 3.3 The implied primary, and its own uncertainty straddles the decision threshold

`β_int` = (weak response) − (spastic response):

| | weak | spastic | **β_int** | gap change over D = 5 | implied rung-to-rung margin at D = 5 |
|---|---|---|---|---|---|
| point estimate | +0.80 | +0.10 | **+0.70 °/deg** | +3.50° | 1.575 + 3.50 = **5.08°** |
| pessimistic end of my own range | +0.60 | +0.30 | **+0.30 °/deg** | +1.50° | **3.08°** |
| optimistic end | +1.00 | 0.00 | **+1.00 °/deg** | +5.00° | **6.58°** |

**The margin must reach 3.800°, which requires `β_int ≥ 0.4450 °/deg`**
( (3.800 − 1.5752) / 5 ).

**Stated plainly before any data exist: my point estimate clears the threshold and the pessimistic
end of my own range does not.** I am registering a prediction whose declared uncertainty band
straddles the decision line. That is the honest state of knowledge, it is why the study is worth
running, and it is why §5.4 registers a two-tier sample size rather than a single guess.

*(Carrying the rung-to-rung margin forward with `β_int` assumes the binding pair stays
`PAR20` vs `DR2K050`. It may not — §4.1 fixes the `min`/`max` definition now so the recomputation is
registered rather than chosen later.)*

### 3.4 The leading competing account for a null, registered now

**CMA-ES re-optimises at every grade.** This programme's own pre-committed reading of a null
(`PREREGISTRATION_slope_velocity_dependence.md`, closing section) is that re-optimised gait
**launders out** mechanism-specific signatures, because the controller is assumed to have found a
near-optimal compensation. A spastic controller facing a decline can shorten its step, flex the knee
more, or slow its loading — any of which avoids the provoking velocity and flattens `β_int` without
the reflex being any less velocity-dependent. **The model's reflex is velocity-dependent by
construction** (`KV` on soleus, set in the scenario at lines 164/170 of
`scone/opt_seeds/DR2K050_s1.scone`). So a flat `β_int` is a statement about **simulation-based
discrimination under re-optimisation**, not about spasticity. §4.4 registers the cadence and
stance-fraction readouts that let this account be checked rather than asserted.

---

## 4. SECONDARY ENDPOINTS

Registered here so that none can be promoted to primary later (rule R45-S), and every one of them
is reported whatever it shows. **A registered secondary that is absent from the Results is a
protocol violation, not an editorial choice** — `ank_rom` was itself registered as the crossed
study's secondary and then deleted from that study's Results when it showed something unexpected
(`COUNCIL_round50.md` §3). That is the reason this clause exists.

**4.1 The marginal claim.** Rung-to-rung mild margin at each `D`:
`min over {PAR20, PAR40} of ȳ` − `max over {DR2K050, DR2K075} of ȳ`, with a 10 000-resample
bootstrap CI using the resampling scheme already implemented in `scone/lr_asymmetry.py`
(`report()`, lines 104–121), RNG seed 20260803. **The `min`/`max` definition is fixed now**, so that
if the binding pair changes at some grade the recomputation is the registered definition and not a
choice made after seeing the data.

**4.2 The clinically observable margin.** The same quantity through the registered video-degradation
pipeline — 30 Hz resample, 4th-order zero-phase 6 Hz Butterworth, sagittal projection — which is
**the quantity that must clear 3.800°**. Reported at yaw 0 and on the same yaw/noise grid used in
`RESULTS_discrimination.md` §7. The §7.3 finding that this filter removes 5.9–10.6° from the weak
arm and 0.8–1.5° from every spastic condition applies here and is expected to *reduce* whatever the
clean margin gives.

**4.3 The presenting sign.** `ank_hs` and `ank_stance_mean` slope-responses per cell, to report what
the manoeuvre did to equinus itself.

**4.4 The laundering readouts** (§3.4): `cycle_time`, `stance_frac`, `n_cycles` per cell, and the
best-`.par` fitness per seed. If `β_int` is flat, these say whether the optimizer absorbed the
decline. If `β_int` is positive, a `fitness × D` interaction of the same shape must be reported
alongside it, because the whole history of this project says cost is the default explanation.

**4.5 Independent replication check, free.** The fresh level-ground cells (§5.2 re-runs them rather
than re-using the existing ones) reproduce or fail to reproduce 19.088 / 16.148 / 20.663 / 23.400 /
20.013 at fresh optimizer seeds. Registered in advance as a check on the level corpus itself.

**4.6 Multiplicity — computed on this corpus, before the contrast.** Effective independent test
count from the eigenvalue spectrum of the correlation matrix of the registered feature set,
computed on the **slope** corpus by the procedure registered in `COUNCIL_round45.md` §8.2 — **the
procedure re-executed, never a constant carried across corpora.** The same figure has been computed
as 1.15, 2.35 and 3.19 by three parties on three feature sets; `CROSSED_RESULT.json` carries
`n_eff = 1.1527` for the crossed corpus and **that number does not transfer to this one.**

**Inference caveat, registered.** With two conditions per arm, the exact condition-level permutation
null has only `C(4,2)/2 = 3` distinct arm assignments, so its **attainable two-sided p-floor is
1/3** — it cannot clear α = 0.05 under any outcome. Computed and stated before running, as
`COUNCIL_round10.md` §Q2 item 4 requires. **The condition-level permutation is therefore reported
but is not the inferential basis**; inference rests on the seed-level CI in §1.3. Consequently:
**seeds are optimizer restarts, not subjects. No sensitivity, specificity, or patient-level AUC may
be quoted from this study's standard errors.**

---

## 5. DESIGN

### 5.1 Uphill is DROPPED ENTIRELY, and this is the reason

**No uphill cell will be generated, launched, analysed or cited.**

Verified again this round from the scenario files themselves:

| family | model | `min_velocity` |
|---|---|---|
| level (`opt_seeds/*`) | `H0914M_osim4.osim`, `H0914_PAR*.osim` | **1.0** (`S10W`) |
| downhill −2° (`opt_slope/RD2*.scone`) | `DN2_*.osim` | **1.0** (`S10W`) |
| uphill (`opt_slope/UPU5V6.scone` line 157) | `H0914M_U5V6.osim` | **0.6** |
| uphill (`UPL05/10/15`, per `COUNCIL_round10.md`) | — | **0.8** (`S08W`) |

Every uphill run in this project's history is at a reduced walking speed, because uphill does not
converge at 1.0 m/s while `GaitMeasure` enforces `min_velocity = 1.0` irrespective of grade.
Walking speed is the dominant determinant of walking cost, and a speed effect at one of three task
anchors would enter the residual slope as a task effect — the defect found at `COUNCIL_round10.md`
§"NEW DEFECT in the pre-registration", which is why the arm was abandoned. Including uphill would
reproduce that confound exactly.

**Honesty note on the supporting figure.** The `r = −0.89` speed–cost correlation quoted throughout
this project is under the **binding citation quarantine** of `COUNCIL_round10.md` §Q3 and has not
been independently fetched. **The exclusion of uphill does not depend on it**: it rests on the
directly verified fact that the uphill scenarios carry a different `min_velocity` from every other
cell in the design, which makes the arm confounded on its face.

Uphill is also the mechanism-*irrelevant* direction: it reduces, not raises, loading-phase
dorsiflexion velocity. Dropping it costs the design nothing.

### 5.2 Conditions, grades, and cells

**Grades: level (D = 0), −2° (D = 2), −5° (D = 5), ALL at `min_velocity = 1.0` (`S10W`).**
Slope is imposed by tilting the gravity vector in the `.osim`. The terrain `blueprint` property is
silently ignored by `ModelOpenSim` and must not be used.

Required gravity vectors (|g| = 9.80665 preserved):

| D | gravity | already on disk as |
|---|---|---|
| 0 | `0 −9.806650 0` | `H0914M_osim4.osim`, `H0914M_ZERO.osim` |
| 2 | `+0.342247 −9.800676 0` | `H0914M_DN2.osim`, `DN2_HEALTHY.osim`, `DN2_PAR40.osim`, `DN2_PAR60.osim` |
| 5 | `+0.854706 −9.769333 0` | **see gate G3 — the file named `H0914M_DN5.osim` does NOT carry this vector** |

**Cell list — exactly 21 cells. Mild rungs are prioritised because that is where the problem is.**

| set | conditions | lesion | tags | cells |
|---|---|---|---|---|
| **PRIMARY** (enters `β_int`) | `DR2K050` (soleus `KV = 0.050`), `DR2K075` (`KV = 0.075`) | mild spasticity | `SG{0,2,5}_DR2K050`, `SG{0,2,5}_DR2K075` | 6 |
| **PRIMARY** (enters `β_int`) | `PAR20` (TA `max_isometric_force` 1759 → **1407.2 N**, ×0.80), `PAR40` (→ **1055.4 N**, ×0.60) | mild weakness | `SG{0,2,5}_PAR20`, `SG{0,2,5}_PAR40` | 6 |
| **CONTROL** (never in `β_int`) | `DR2K000` (`KV = 0.000`, structurally isomorphic zero-gain block) | none | `SG{0,2,5}_DR2K000` | 3 |
| **MANIPULATION CHECK** (never in `β_int`) | `DR2K200` (`KV = 0.200`), `CMW80` (TA ×0.20) | severe | `SG{0,2,5}_DR2K200`, `SG{0,2,5}_CMW80` | 6 |

The TA forces are read directly from the model files: intact `tib_ant_l`
`max_isometric_force = 1759`, `H0914_PAR20.osim` = 1407.2, `H0914_PAR40.osim` = 1055.4.

**No run enters an arm by tag.** Arm membership is by **measured delivered gain** for the spastic
arm (`delivered_gain.py`, ρ within 0.15 of 1.0 — gate G6) and by `max_isometric_force` read from the
model file the run's own archived `config.scone` names, for the weak arm.

**Why mild only in the primary.** `RESULTS_discrimination.md` §7.2: the severe gap never falls
below 7.28° and minimum severe LOSO across 120 cells is 0.938 — *"a tool that works only where
screening is unnecessary is not a screening tool."* The severe pair is retained solely as a
manipulation check: if the decline does not move `ank_rom` even at KV 0.200 and TA ×0.20, the
manipulation failed and the study is **VOID, not null** (§6.3, falsifier F4).

**Why the level tier is re-run rather than re-used.** The existing level cells in `scone/opt_seeds/`
carry the identical registered budget and could be re-used, saving 20 runs — this is what the
superseded draft did. They are **not** re-used here: they were launched in a different batch at a
different time, and level is the **reference level of the primary predictor**, so a batch term would
alias perfectly with `D = 0` and bias `β_int` directly. That aliasing is defect **A6**
(`COUNCIL_round10.md` Part 1), which cost this project its entire first dataset. The 20 runs are
paid. Separately, `opt_seeds/` holds only 4 scenario files for `DR2K075`, `PAR20`, `PAR40` and
`CMW80`, so the tier could not reach n = 6 by re-use in any case. The existing level cells become
the free replication check of §4.5.

**Models to be generated (8 new `.osim`, none created by this document):** each of
`H0914M_osim4.osim` (used by `DR2K000`, `DR2K050`, `DR2K075`, `DR2K200`), `H0914_PAR20.osim`,
`H0914_PAR40.osim`, `H0914_CMW80.osim` re-emitted with the D = 2 and D = 5 gravity vectors, with
**no other byte changed**. A byte-diff against the level parent showing exactly one changed line is
launch gate G7.

### 5.3 Budget — identical in every cell, no exceptions

```
min_progress    = 0
max_generations = 90          (terminal generation index 89)
init_file       = ResultH0914Gait10.par      (cold start, identical in all 21 cells)
random_seed     = 101 .. 116                 (crossed with cell; never aliased with slope)
min_velocity    = 1.0
```

`min_progress = 0` makes the stopping generation a **design constant** rather than a random variable
that depends on a fitness landscape which differs by dose and by grade. This is the same budget the
48-run level study ran under; it is asserted, not assumed, by
`gen_seeds.assert_registered_stopping_rule()` before launch (gate G8) and read back from each run's
own artifacts after (§7.3 item 5).

**No warm start.** The historical downhill family warm-started from `D2HEALTHY_resume.par` /
`flat_best.par`. Reusing that would give the −5° tier a warm start the level tier does not have —
reintroducing defect **A7** (equal generation *numbers* are not equal *convergence*; class 0 sat at
its optimum while class 1 was still descending at generation 242–337). Registered consequence: the
−5° tier may fail to converge from cold. That is gate **G4**, with a registered fallback.

### 5.4 Seeds per cell, justified against the level-ground within-condition SD

**The dispersion figure.** No JSON in `paper/` contains a within-condition SD for `ank_rom`. It was
therefore **recomputed for this registration** from the frozen crossed replays in
`scone/replay_crossed/`, using the registered function `sto_utils.cycle_features(..., side="l",
settle=1.0)` — read-only, nothing written to the corpus:

| cell | n | mean `ank_rom` | SD |
|---|---|---|---|
| `DR2K000` / `HEALTHY` | 4 | 20.0134 | 1.3423 |
| `DR2K050` | 4 | 19.0877 | 1.8028 |
| `DR2K075` | 4 | 16.1478 | 1.9618 |
| `PAR20` | 4 | 20.6629 | 1.9859 |
| `PAR40` | 4 | 23.3995 | 4.9201 |

**Pooled within-condition SD across the four mild cells: σ̂ = 2.9686° (12 df).** (Mild spastic alone
1.8840; mild weak alone 3.7517; all ten lesion cells 2.7577. `PAR40` is the dispersion outlier at
4.92 and is the reason the weak arm dominates the pooled figure.)

*Cross-checks that this is the right order of magnitude:* `COUNCIL_round48.md` §3 measures the
pooled within-rung SD on the budget-matched crossed corpus at **3.0247°** for `ank_stance_mean`;
`LR_ASYMMETRY.json` `mild_l.margin_sd = 0.41517` against a margin of 1.5752 implies a pooled
across-arm seed SD of 3.794°, larger because it includes between-condition variance.

*Incidental confirmation:* `DR2K000` and `HEALTHY` return identical values to four decimals,
confirming `COUNCIL_round50.md` §4 — they are **one optimization**, not two.

**Precision of `β_int`.** With 2 conditions per arm, `n` seeds per cell, three grades:

```
SE(β_int) = σ / sqrt( n · Σ(D − D̄)² )  =  σ / sqrt( 12.6667 · n )
```

| n per cell | SE(β_int) °/deg | 95 % half-width | excludes β_req = 0.445 when β̂ = 0? |
|---|---|---|---|
| 4 | 0.4171 | 0.818 | no |
| **6 (Tier 1)** | **0.3405** | 0.667 | no |
| 10 | 0.2638 | 0.517 | no |
| 14 | 0.2229 | 0.437 | marginal |
| **16 (Tier 2)** | **0.2085** | **0.409** | **yes** |

**Registered: n = 6 at Tier 1, n = 16 at Tier 2 for the 12 primary cells.**
Control cells n = 6; manipulation-check cells n = 4 (they never enter `β_int`).

**n = 4 is registered as inadequate here, with the reason.** At n = 4 the half-width on `β_int` is
0.818 °/deg — nearly twice the entire effect the study needs to resolve. This is the same arithmetic
that made every crossed rung INDETERMINATE-BY-ATTRITION on D's registered endpoint
(`COUNCIL_round48.md` §2: CI half-width 5.233° against a 3.800° threshold at n = 4). Repeating n = 4
here would guarantee an indeterminate answer.

`n = 16` is not a new number: `COUNCIL_round48.md` §3 retires the round-43 blocker that had called
16 under-powered and concludes **"At the clean SD, the originally registered n = 16 is adequate."**
It is adopted here for the same reason and against a directly measured σ̂.

**Run counts.** Tier 1 = 12×6 + 3×6 + 6×4 = **114 runs**. Tier 2 adds 12×10 = **120 runs**. Full
corpus if escalated = **234 runs**, against the completed level study's 48.

**σ̂ is an assumption and the registered quantity is precision, not n.** σ̂ = 2.9686 was measured on
level ground; slope may inflate it. **Registered rule, fixed now:** if the Tier-1 pooled within-cell
SD `σ̂₁` exceeds 3.6°, Tier 2's n is recomputed as
`n = ceil( σ̂₁² / (12.6667 × 0.21²) ) = ceil( σ̂₁² / 0.5586 )`, preserving the precision target
`SE(β_int) ≤ 0.21 °/deg`. At σ̂ = 2.9686 this returns 16; at σ̂ = 3.6 it returns 24.

**Why three grades and not two.** For the linear trend alone, two grades {0, 5} carry
Σ(D−D̄)² = 12.5 against three grades' 12.6667 — statistically identical information for 1.5× the
runs. The third point is bought deliberately, to test **monotonicity**: the hypothesis is that the
arms diverge *more as slope steepens*, and a gap that jumps at −2° and then stops, or reverses, is a
different finding from a linear divergence. Registered before the data so the mid-point cannot be
dropped afterwards if it is inconvenient.

---

## 6. FALSIFIERS, STOPPING RULE, AND WHAT A NULL BUYS

### 6.1 Falsifiers — conditions that can actually occur with these cells and this n

**F1 — the primary falsifier, quantitative.** `β̂_int ≤ −0.2224 °/deg` at Tier 1. At that value the
two-sided 95 % upper bound (β̂ + 1.96 × 0.3405) falls below `β_req = 0.4450`, so the clinically
required interaction is excluded outright. **This can actually occur:** if the true `β_int` is
exactly 0, Tier 1 returns β̂ ≤ −0.2224 with probability Φ(−0.2224 / 0.3405) = Φ(−0.653) ≈ **26 %**.
It is not a threshold set where nothing can land.

**F2 — the sign falsifier, independent of n.** *The spastic arm's ROM response to decline is at
least as large as the unlesioned control's, in **both** mild spastic cells.* If a KV-0.050 and a
KV-0.075 ankle open up under decline exactly as much as an ankle with no reflex at all, the reflex
contributes nothing to the loading-phase excursion and the mechanism in §0.2 is refuted as stated.
This is a sign pattern over 2 comparisons, computable at any n, and it is the cheapest way the
hypothesis can die.

**F3 — the direction falsifier.** *The rung-to-rung mild margin at D = 5 is smaller than at D = 0.*
The arms converge under provocation. Under a true `β_int` of 0 this occurs roughly half the time, so
it is a live outcome, not a rhetorical one. F3 alone is not decisive (it is the marginal claim, §2)
but combined with F1 it closes the question.

**F4 — the manipulation falsifier, which voids rather than falsifies.** The manipulation-check cells
show no `ank_rom` response to decline either — `|` slope response `|` < 0.2 °/deg at KV 0.200 **and**
at TA ×0.20 **and** in the unlesioned control. Then nothing was provoked in any arm, the decline did
not reach the ankle, and the result is **VOID, not null**. Given the gravity-sign defect in §7.2,
this is the first thing to suspect if it fires.

### 6.2 Stopping rule

**(a) Per run — the optimizer stopping rule.** `min_progress = 0`, `max_generations = 90`, terminal
generation index 89, identical in all 21 cells including the control. Asserted before launch by
`gen_seeds.assert_registered_stopping_rule()`; read back afterwards from each run's own archived
`config.scone` and `history.txt` (§7.3 item 5). A run whose terminal generation is not 89 is not a
retained seed.

**(b) Per cell — the attrition floor.** A seed is excluded if `select_registered_par` raises E5, or
if `cycle_features` returns `None` (fewer than 2 complete cycles, i.e. not steady gait). **A cell
retaining fewer than 4 seeds is reported INDETERMINATE-BY-ATTRITION** and contributes nothing — the
rule amended at `COUNCIL_round43` §3.3, which `COUNCIL_round48.md` §4 records as standing on its own
merits for any future study. **If more than 2 of the 15 primary + control cells are indeterminate,
the study is VOID, not null.** Exclusions are counted in the Results, never silently dropped.

**(c) Per study — the two-tier rule, and it is asymmetric on purpose.**

> **Tier 1 (n = 6, 114 runs) may STOP the study. It may never declare a positive.**
>
> - **`β̂_int ≤ −0.2224`** → **STOP. Registered as a FINAL negative** (§6.3). The upper 95 % bound
>   excludes the clinically required interaction.
> - **`β̂_int > −0.2224`** → **ESCALATE** the 12 primary cells from n = 6 to n = 16 (Tier 2), using
>   `random_seed` 107–116. Control and manipulation-check cells stay as they are.
>
> Stopping only for futility does not inflate type-I error for the positive claim; it can only cost
> power. That asymmetry is the reason the rule is written this way and it is registered now.

**Tier 2 (n = 16) decision, three-way, fixed in advance** (SE = 0.2085, half-width 0.409):

| Tier-2 outcome | verdict |
|---|---|
| `β̂_int ≥ 0.854` | lower bound on the D = 5 margin ≥ 3.800°: **provocation delivers a clinically sufficient effect size** |
| `0.036 ≤ β̂_int < 0.854` | **INDETERMINATE.** Report β̂ and its CI; neither claim is licensed. The band is 3.92 × SE wide and does not vanish at any feasible n; stated now so it is not discovered later |
| `β̂_int < 0.036` | upper bound on the D = 5 margin < 3.800°: **FINAL negative** (§6.3) |

**(d) Council override.** If a council round finds a fatal defect in this study before its primary
is computed, the study stops and no scientific conclusion is drawn from it.

**(e) Nothing is added after the data are seen.** No extra grade, no extra condition, no extra
feature, no extra seed beyond the registered escalation, no substitution of the primary. If the
falsifier fires the hypothesis is abandoned — **not re-membered, not re-sliced by slope, not
replaced by a secondary.** If Tier 1 stops for futility the study is closed and §6.3 is the write-up.

### 6.3 WHAT A NULL BUYS — stated in advance, before the data exist

**If the mild margin does not grow with slope, the effect size is not recoverable by provocation and
the negative becomes FINAL rather than provisional. That is a publishable outcome and it is
registered here as one.**

The precise content of that finality:

1. **The standing objection is removed.** Six features have died at the 3.8° MDC on level ground.
   The standing objection to every one of those deaths has been *"you did not challenge the system —
   a velocity-dependent mechanism needs a velocity-dependent task."* This study is that challenge,
   in the mechanism-relevant direction, at constant speed, at a matched budget, with a zero-gain
   control at every grade. **A null here removes the objection.** The claim becomes: *plantarflexor
   spasticity and dorsiflexor weakness are statistically separable and clinically indistinguishable
   at mild severity in re-optimised sagittal gait, and that remains true under the manoeuvre
   specifically designed to provoke the velocity-dependent mechanism.*

2. **The negative stops being provisional because it becomes bounded.** It is currently provisional
   in exactly one respect — the untested provocation. After this study it is bounded: the registered
   Tier-2 upper bound excludes an interaction large enough to lift the margin to the MDC. A bounded
   negative is a result; an untested one is an open question wearing a conclusion.

3. **What it does NOT license.** It does not show the modelled reflex is not velocity-dependent — it
   is, by construction (§3.4). It says re-optimised gait does not *express* that dependence as a
   detectable ROM divergence. **It is a statement about simulation-based discrimination and is to be
   written as one.** And it is **not** to be followed by another feature search; that is the standing
   pre-commitment of `PREREGISTRATION_slope_velocity_dependence.md` and it is renewed here.

4. **The publishable object.** A registered, hashed, pre-predicted negative with a stated bound —
   the property that separates it from the four features in this programme that died by post-hoc
   audit, and the property `COUNCIL_round48.md` §5 already identifies as the abstract's third
   sentence.

**Saying this before the data exist is the entire point of saying it.** Written down now, a null
cannot be re-described afterwards as "inconclusive, pending a steeper grade / another feature / more
seeds"; and a positive cannot be re-described as having been expected all along.

---

## 7. PER-CELL VERIFICATION ARTIFACTS

Nothing below is optional and none of it may be summarised in place of the real output. Every item
is recorded **per cell**, verbatim, in a per-cell verification record.

### 7.1 Pre-launch gates — these run on the CONTROL cell before any real cell

| gate | what it does | pass condition |
|---|---|---|
| **G1** | `check_structure.py SG{0,2,5}_DR2K000_s101.scone --name SpasticL --expect-reflexes 2 --expect-kv 0.000` **on the CONTROL cell**, plus one treated cell | `status == "OK"`, `failures == []`, and the `could_not_verify` list **recorded verbatim** and never read as a pass. The module fails closed on a missing file, a parse error, a BOM, an unresolved `<<` include, or an unrecognised parent chain. **The structural certification of a control is what the previous pre-registration died without** |
| **G2** | `check_unused.py` **on the CONTROL cell's** launcher log, from a discarded 2-generation `GATE_`-prefixed throwaway launch | per-tag `ok` and the final line `PASSED: no injected block was reported as unused.` The throwaway directory is deleted and is excluded by content anyway (`max_generations != 90`). Its own caveat travels with the verdict: this proves the block was **ACCEPTED, not that it was delivered ONCE** |
| **G3** | **GRAVITY-SIGN GATE — blocking.** See §7.2 | resolved before any −5° cell is generated |
| **G4** | −5° convergence probe: does the control cell at D = 5 yield ≥ 2 complete gait cycles under `cycle_features`? | if no, the −5° tier is reported **NOT ATTAINABLE at S10W from a cold start** and the design reduces to {0, 2} — fallback below |
| **G5** | **tag-collision check, before launch rather than after** | for all 21 tags, **no** existing directory under the results root resolves to that signature prefix, and **no** directory named `… (1)` exists for any tag. A colliding tag is renamed **before** launch, never after |
| **G6** | `delivered_gain.py` on each spastic cell (`DR2K050`, `DR2K075`, `DR2K200`) at each grade | certified **ρ within 0.15 of 1.0** unilateral delivery. This is the project's only trusted delivery instrument, and 30 of 30 historical spastic runs failed it at ρ ≈ 2.0 |
| **G7** | byte-diff each generated slope `.osim` against its level parent | **exactly one changed line**, the `<gravity>` line |
| **G8** | `gen_seeds.assert_registered_stopping_rule()` over all built scenarios; plus a grep readback | every scenario carries `min_progress = 0`, `max_generations = 90`, `min_velocity = 1.0`, `init_file = ResultH0914Gait10.par`, a `random_seed` distinct within its condition, and **no `_resume.par` anywhere**. The declared slope differs between the D = 2 and D = 5 sets |

**G4 fallback, registered in advance with its power consequence.** If the −5° tier is unattainable,
the design becomes {0, 2}, and the required interaction rises from 0.4450 to
(3.800 − 1.5752)/2 = **1.1124 °/deg**. At n = 16 with two grades, SE = σ·√(2/n) = 1.0496, so a β̂
near 0 still excludes 1.1124 comfortably — **the reduced design remains decisive for the negative**
and is weaker for the positive. Stated now so the fallback is not treated as a failure of the study.

### 7.2 G3 — the gravity-sign gate, in full, because the file on disk is wrong

Gravity vectors read directly from `scone/opt_slope/` this round:

| file | `<gravity>` | x-sign |
|---|---|---|
| `H0914M_ZERO.osim` | `-0.000000 -9.806650 0` | — |
| `H0914M_DN2.osim` (downhill 2°) | `0.342247 -9.800676 0` | **+** |
| `DN2_HEALTHY / PAR40 / PAR60 / SPAS01.osim` (downhill 2°) | `0.342247 -9.800676 0` | **+** |
| `H0914M_UP1.osim` (uphill 1°) | `-0.171150 -9.805156 0` | − |
| `H0914M_UP2.osim` (uphill 2°) | `-0.342247 -9.800676 0` | − |
| `H0914M_U2V6.osim`, `H0914M_U2V8.osim` (uphill 2°) | `-0.342247 -9.800676 0` | − |
| `H0914M_U5V6.osim` (uphill 5°) | `-0.854706 -9.769333 0` | − |
| **`H0914M_DN5.osim`** (named downhill 5°) | **`-0.854706 -9.769333 0`** | **− ← the uphill sign** |
| **`H0914M_UP5.osim`** (named uphill 5°) | **`0.854706 -9.769333 0`** | **+ ← the downhill sign** |

**On this project's own convention, established consistently at 1° and 2°, `H0914M_DN5.osim` and
`H0914M_UP5.osim` are name-swapped, and `H0914M_DN5.osim` is gravity-identical to the uphill model
`H0914M_U5V6.osim`.** Magnitudes are correct in both files (|g| = 9.8067, angle 5.000°); only the
sign is in question.

**No −5° cell may be launched until this is settled by a physical test, not by reading a filename:**
replay one fixed controller in the level model and in the candidate −5° model and confirm the pelvis
vertical coordinate **decreases** over the trial (descent). **Registered default if the test is not
conclusive:** generate the −5° models fresh from their level parents with
`<gravity>0.854706 -9.769333 0</gravity>` — the vector that currently sits in the file named
`H0914M_UP5.osim` — and never use either shipped 5° file.

This gate exists because a mislabelled sign would run the entire study **uphill**, at 1.0 m/s, in
the direction the design explicitly excludes, and every number would look normal.

### 7.3 Per-cell verification record — required for all 21 cells

For **every seed** of every cell, the record contains:

1. **Launcher log present, non-empty, and reaching launch.** The log file exists, is > 0 bytes, and
   contains `Creating folder` or `Starting optimization`. `check_unused.py` line 157 fails closed on
   exactly this condition, because an earlier version printed `PASSED: no injected block was
   reported as unused` for a **0-byte log**.
2. **`check_unused.py` real verdict**, per tag, quoted: `ok`, or the `*** … ***` failure text. Never
   "clean" as a summary. The module's own note travels with the verdict.
3. **`check_structure.py` real verdict** on that seed's own scenario file: `status`, the full
   `failures` list, and the full `could_not_verify` list. A `PASS` with a non-empty
   `could_not_verify` is recorded as such — the module cannot see a misspelled property name, a
   parser disagreement, per-side multiplicity, delivered gain, or anything in the `.osim`.
4. **`delivered_gain.py` ρ**, for every spastic cell, at every grade.
5. **Stopping-rule readback**, from the run's **own** archived artifacts, not from the scenario the
   launcher thinks it used: `min_progress == 0` and `max_generations == 90` from the run directory's
   `config.scone`, and **terminal generation index 89** from its `history.txt`.
6. **Content-based cell resolution** — §7.4.
7. **The selected `.par`**: filename, generation, fitness and `n_par` as returned by
   `select_registered_par`, with the assertion that minimum-fitness == maximum-generation.
8. **The replayed `.sto` and its sha256.**

**A cell without its artifacts is excluded, and the exclusion is counted in the Results.**

### 7.4 Content-based directory resolution — and why the usual key is NOT sufficient here

**Cells are resolved by CONTENT. Never by directory name. Never by mtime.**

SCONE appends `" (1)"` to a colliding directory name rather than overwriting, and tag collisions
have **twice** silently mixed corpora in this project:

- `crossed_endpoint.py` lines 32–37: *seven of twelve conditions collided with archive runs*, and
  `CMW70` / `CMW80`'s archive copies also ran at 90 generations and also stopped at 89, so
  `min_progress` was the **only** discriminator. Resolving by name or mtime would have given those
  two cells n = 6 — four crossed seeds plus two archive runs at a different budget — reintroducing
  the budget confound in the arm added to remove it.
- `COUNCIL_round10.md` defect #23: every `RD2` / `RE2` tag had two directories, and an mtime-resolved
  audit read the **stale** ones and reported live runs as dead.

**The critical point for THIS study, registered because it is easy to get wrong:** the usual content
key — `min_progress == 0` ∧ `max_generations == 90` ∧ terminal generation 89 — is **identical across
all 21 cells by design**, so it **cannot discriminate a slope tier from a level tier**. Resolution
therefore requires, from each run's **own archived `config.scone`**:

| key | read from | discriminates |
|---|---|---|
| `min_progress`, `max_generations` | run's own `config.scone` | this study vs. any other corpus |
| terminal generation index | run's own `history.txt` | completed vs. truncated |
| `model_file` name **and the `<gravity>` vector inside that model file** | run's own `config.scone` → `.osim` | **the slope tier** |
| injected `KV` value (scenario lines 164/170) | run's own `config.scone` | spastic rung vs. control |
| `tib_ant_l` `max_isometric_force` in the referenced `.osim` | model file | weak rung |
| `min_velocity` | run's own `config.scone` | S10W vs. any speed-confounded run |
| `random_seed` | run's own `config.scone` | seed identity within a cell |

A directory that does not resolve to exactly one cell on the full key is **excluded**, not guessed.
A cell that resolves to more directories than it has registered seeds **halts the analysis**.

---

## 8. HASH

**The sha256 of this file, together with its byte count, is written to
`paper\PREREG_slope.sha256` immediately after this document is written and before any slope
scenario, model file, or result directory is created.**

**The hash covers this registration as of that moment** — the moment before the study exists. It
certifies the predictions in §3, the falsifiers in §6.1, the stopping rule in §6.2 and the
pre-committed reading of a null in §6.3 as having been fixed in writing ahead of the data, which is
the only property that distinguishes this document from a post-hoc rationalisation.

**Any modification after that moment invalidates the registration.** Amendments are appended to §10,
never edited into the text above, and `PREREG_slope.sha256` is re-issued carrying **both** hashes
with their dates. A registration whose hash silently changes is worse than no registration, and this
project has already recorded one case where the hashed script was not the script that produced the
reported numbers (`COUNCIL_round50.md` §4.3: *"the reported numbers and the registered numbers are
different numbers, in a paper whose central claim is that they are the same"*).

---

## 9. WHAT THIS DOCUMENT COULD NOT GROUND IN AN EXISTING ARTIFACT

Listed because a registration that hides its own soft spots is not a registration.

1. **Downhill ankle-ROM magnitudes.** No verified citation is held by this project, in humans or in
   this model, and no slope run here has ever had a feature extracted. **Every number in §3.2 is a
   mechanically reasoned range, not an extrapolation from data.** This is the weakest part of the
   document and the ranges are wide on purpose.
2. **The `r = −0.89` speed–cost figure** (§5.1) is under the binding citation quarantine of
   `COUNCIL_round10.md` §Q3 and has not been independently fetched. The uphill exclusion is written
   so that it does not depend on it.
3. **The 3.800° MDC** is the programme's standing floor and is used here as such; its primary source
   was not re-verified in writing this document.
4. **The within-condition `ank_rom` SD is not in any JSON.** σ̂ = 2.9686° was recomputed for this
   registration from `scone/replay_crossed/` with `sto_utils.cycle_features`, read-only. The
   per-cell values are printed in §5.4 so the pooling can be checked.
5. **Whether −5° converges at S10W from a cold start is unknown.** No artifact bears on it; the only
   historical −5° model is the one under the sign dispute of §7.2, and the historical downhill runs
   were warm-started at a different budget. Registered as gate G4 with a fallback.
6. **The gravity sign at 5° is unresolved on disk** (§7.2) and is a blocking gate, not a caveat.
7. **Wall-clock cost was not measured.** Run counts are registered (114 / 234); hours are not,
   because no artifact was read that would ground them. The superseded draft asserted ~5.5 h per run
   and ~1.8 days at 4-way concurrency; **that figure is not adopted here because its source was not
   identified.** The compute is ~2.4× to ~4.9× the completed 48-run study and that is the binding
   practical risk to this design.
8. **The −2° `RD2*` / `RE2*` runs were deliberately not read** (§0). Their contents are unknown to
   this document.
9. **Seed-level standard errors describe optimizer-restart variability, not between-patient
   variability** (§4.6 caveat). No clinical performance figure may be derived from them.
10. **The effective-test count for this corpus does not exist yet** and must be computed on the slope
    corpus before the contrast (§4.6). `CROSSED_RESULT.json`'s `n_eff = 1.1527` belongs to a
    different corpus and does not transfer.

---

## 10. DEVIATIONS FROM THIS DOCUMENT

Any deviation is recorded here with its date, its reason, and **whether it was made before or after
the primary was computed. A deviation made after seeing the outcome is a deviation; one made before
is a correction, and the distinction is the whole point of the timestamp.**

*(none at time of registration)*
