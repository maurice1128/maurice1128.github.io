# PREREG_3d_speed_r203.md — walking speed as the provocation axis, in 3D

**Registered BEFORE any cell is launched.** This document is written to be self-contained: a reader who
has never seen this project should be able to compute the primary endpoint, apply the decision rule and
reproduce every gate from this file alone. Where a number is a free choice made by this registration, it
is chosen here, stated here, and justified here; nothing is left to be decided after the data exist.

Parents: `PREREG_3d_matched_r174.md`, `PREREG_3d_replication_r179.md`.
Step-1 arithmetic: `paper/SPEED_DOSE_r200.json`, from `scone/speed_dose_r200.py`.
Between-seed spread deposit: `paper/MDD_r203.json`.

Two earlier unhashed drafts of this registration (`PREREG_3d_speed_r201.md`, 9,328 B;
`PREREG_3d_speed_r202.md`, 13,026 B) were rejected by cold reads before hashing. They are kept frozen as
the record and are not edited. This is a new document, not a revision of either.

---

## 1. What this study asks

The injected spastic reflex is velocity-gated by construction. Walking speed is therefore the
mechanism's own signature axis, and it is the only axis that changes the delivered provocation without
touching KV, whose ceiling is already registered. Level walking at a single speed is the only task the
3D corpus contains, so every feature this project has previously buried was measured at one point on
that axis.

The study runs the same three arms at three commanded walking speeds and asks whether the change in
gait kinematics between the slow and fast ends differs between a lesioned arm and control.

---

## 2. Design

| | |
|---|---|
| commanded speeds | **0.80, 1.05, 1.30 m/s** — evenly spaced |
| arms | control · spastic **KV 0.050** · weak **`tib_ant_l` ×0.892** |
| seeds | 101, 102, 103, 104, 105, 106 |
| cells | 3 speeds × 3 arms × 6 seeds = **54** |
| start | from-healthy warm start, identical for all three arms, **no continuation from any existing `.par`** |

No new magnitudes. KV stays 0.050 and the weak scale stays ×0.892; this design changes the task, not the
lesion. r169's depth confound is structurally excluded because every cell runs from-healthy to the same
fixed depth, and r172's path dependence is excluded because no cell continues from another cell's
solution.

**Commanded and achieved speed are different quantities and are never interchanged in this document.**
0.80, 1.05 and 1.30 are commands. The one measured benchmark value, **1.0215 m/s** (per-seed
1.0158–1.0252), is an *achieved* speed produced by a command of 1.0 m/s — a **+0.0215 overshoot**. It was
never a commandable value and it is not one of this study's commands. It is used here only as the single
available measurement of how well this model tracks a speed command.

**Why the midpoint is 1.05 and not 1.0215.** The midpoint's registered job in this design is the
linearity check (§6), and even spacing is what that job wants: with 0.80 and 1.30 as the ends, 1.05 is
their exact arithmetic midpoint, so the chord test is symmetric in the two endpoints. 1.05 is within
0.03 m/s of the measured benchmark, so the same from-healthy warm start remains appropriate.

---

## 3. What step 1 established, and what it did not

**Delivered dose** = `KV × max(0, ce_vel_norm) × Fmax`, summed over `soleus_l` and `gastroc_l`, with the
excitation clamp `min(du, max(0, 1−u))`. The method is taken from `dose_r174.py` unmodified and
reproduces the registered **13.627 N**.

**The clamp never binds.** Tested to a velocity multiplier of 20, nothing saturates anywhere in the
range this study can reach. This is the one clean structural fact step 1 contributes.

**KV 0.150 delivers 40.880 N, and "exactly 3.0000× KV 0.050" is an identity, not a finding.** Dose is
linear in KV by definition and the clamp does not bind, so 3× KV must give 3× dose; as printed,
13.627 × 3 = **40.881**, not 40.880. Nothing was learned from that ratio and it is not reported as a
result.

**The 1.63× provocation span is likewise an identity.** Under the linearity premise the delivered dose
spans **10.67 N to 17.34 N** across the commanded band. 17.34 / 10.67 = 1.6251, i.e. **1.63×** — the
earlier drafts' "1.62×" was arithmetically wrong. But 1.30 / 0.80 = 1.625, so the ratio is the speed
ratio restated. It is an identity under the assumption, not a finding, and it is not reported as one.

**Dose-matching KV 0.150 by speed would need 3.06 m/s — conditionally.** That figure follows only if
dose is linear in speed. Linearity in speed is this study's own untested premise. **A route closed by an
assumption is not closed.** If dose grows superlinearly with speed the required speed is lower and the
closure fails. §10 measures the premise directly, in all three arms. Until then the dose-matching route
is recorded as conditionally closed, and no weight is placed on its closure.

**What "reachable band" means and does not mean.** 0.80–1.30 m/s is a statement about the dose
arithmetic. Whether this model can walk at 0.80 or at 1.30 m/s at all is unknown, and §8 treats failure
to do so as an outcome rather than as an accident.

---

## 4. The sixteen channels, enumerated in full

All sixteen are registered in advance, inherited unchanged from `PREREG_3d_replication_r179.md`. There is
no post-hoc selection and **all sixteen are reported whatever they show.**

**Twelve primitive channels**

1. `ankle_angle_l`
2. `ankle_angle_r`
3. `knee_angle_l`
4. `knee_angle_r`
5. `hip_flexion_l`
6. `hip_flexion_r`
7. `hip_adduction_l`
8. `hip_adduction_r`
9. `pelvis_list`
10. `pelvis_rotation`
11. `lumbar_bending`
12. `cycle_time`

**Four derived channels — deterministic functions of eight of the above**

13. `ankle_angle_LmR` = `ankle_angle_l` − `ankle_angle_r`, pointwise in time
14. `knee_angle_LmR` = `knee_angle_l` − `knee_angle_r`, pointwise in time
15. `hip_flexion_LmR` = `hip_flexion_l` − `hip_flexion_r`, pointwise in time
16. `hip_adduction_LmR` = `hip_adduction_l` − `hip_adduction_r`, pointwise in time

Channels 13–16 are declared here as derived: each is a deterministic pointwise function of two channels
already in the set, and they carry no information the eight parents do not already contain. (Their
*scalars* are not arithmetic functions of the parents' scalars, because a range statistic depends on the
relative phasing of the two parent signals as well as on their individual ranges. That does not make them
independent evidence, and §7 treats them as dependent.)

Units: all angle channels are in radians in the `.sto`; `cycle_time` is in seconds. **All angle-channel
comparisons in this document are performed in degrees**, converted once, so that the registered floor is
a physical quantity rather than a unit artefact. `cycle_time` stays in seconds.

---

## 5. The scalar: one rule for all sixteen channels

**ROM (range of motion): per admitted gait cycle, `max − min` of the channel over that cycle; per cell,
the arithmetic mean of that quantity over the admitted cycles.** One rule, all channels, no per-channel
choices.

**The single exception, named now rather than decided later.** `cycle_time` is already a per-cycle
scalar and has no within-cycle range. Its per-cell value is the **mean duration of the admitted cycles**.
This is the only channel not reduced by `max − min`.

**Mechanistic justification, one sentence.** The injected reflex opposes muscle lengthening, so its
first-order kinematic consequence is a change in excursion, and ROM is excursion while being invariant to
the postural offsets both lesions independently produce — offsets that a mean or a peak would confound
with the effect.

**The counter-case, registered.** ROM is **not sign-committed.** A high-gain stretch reflex can produce
clonus, and clonus *increases* `max − min`. This study therefore does not predict a direction for ROM
and does not claim the reflex can only compress excursion. The decision rule (§7) is two-sided on every
channel.

**Sampling and filtering treatment, registered.** `max − min` is a two-sample range statistic and is
maximally sensitive to single-sample spikes, so the treatment is fixed here:

- Channels are read from the `.sto` at its native output rate. **No resampling, no interpolation, no
  smoothing, no filtering** is applied to any channel, in any arm, at any speed.
- The reason is that this is a deterministic forward simulation with no sensor noise; there is no
  measurement artefact to remove, and any filter would be an additional analysis choice with a free
  cutoff. It is also the treatment under which the spread deposit in `MDD_r203.json` was computed, so
  the endpoint and the bar it is judged against are on the same footing.
- The residual risk is an integrator-step artefact rather than sensor noise. **Registered check:** for
  every cell and channel, the per-cycle `max − min` is reported alongside the per-cycle
  `2nd-largest − 2nd-smallest` sample over the same cycle. If those two differ, on any cell, by more than
  that channel's bar (§6.3), the channel is flagged SPIKE-SENSITIVE in the report and the flag travels
  with every number derived from it. This is a reported check, not a correction; no de-spiking is
  performed.

---

## 6. The primary endpoint

### 6.1 The primary is a DIFFERENCE between the two endpoint speeds

**Primary quantity, per arm `a`, per seed `s`, per channel `c`:**

```
D(a, s, c) = ROM_c(a, s, command 1.30) − ROM_c(a, s, command 0.80)
```

**Arm-level quantity:** `Dbar(a, c)` = arithmetic mean of `D(a, s, c)` over that arm's contributing seeds
(§8, §9).

Units: degrees for the fifteen angle channels, seconds for `cycle_time`.

**It is a difference and it is named a difference.** It is not divided by the achieved speed span, not
divided by anything else, and no line is fitted to the three points. This is not a stylistic choice. With
three speeds, an ordinary-least-squares line gives the midpoint essentially no leverage:

| design | OLS weights (low, mid, high) | midpoint share |
|---|---|---|
| {0.80, 1.02, 1.30} | −1.911, −0.159, +2.070 | 3.85 % |
| **{0.80, 1.05, 1.30}** | −2.000, **0.000**, +2.000 | **0.00 %** |

At the registered spacing the middle cell contributes **exactly nothing** to a fitted line: such a fit is
the two-endpoint difference rescaled, and calling it anything else would misdescribe what was computed.
So the endpoint difference is registered directly, and the middle cell is given the job it can actually
do.

### 6.2 The middle cell is the linearity check — that is its registered job

Calling the ROM–speed relationship linear is exactly the premise step 1 assumed and could not test,
because the corpus contained one speed. The middle cell tests it.

**Per arm, seed and channel**, using **achieved** speeds `v_lo`, `v_mid`, `v_hi` from that seed's three
cells (§8.5):

```
chord(v_mid) = ROM(0.80) + [ROM(1.30) − ROM(0.80)] × (v_mid − v_lo) / (v_hi − v_lo)
K(a, s, c)   = ROM_c(a, s, command 1.05) − chord(v_mid)
```

`K` is the curvature: how far the middle point sits off the chord joining the two endpoints. Arm-level
`Kbar(a, c)` is the mean of `K` over contributing seeds.

**Registered linearity tolerance (free parameter, chosen here).**

> **Linearity is REJECTED for an (arm, channel) pair iff `|Kbar(a, c)| > T(c)`, where `T(c)` is
> numerically the same as that channel's separation bar `Bar(c)` of §6.3 — i.e. 1.000° for fourteen of
> the fifteen angle channels, 1.690° for `pelvis_rotation`, and 0.020 s for `cycle_time` under the
> deposited spread.**

*Justification.* The tolerance must be a curvature magnitude, and the only principled scale available
before the data is the smallest difference this study is willing to call real. A departure from the chord
smaller than that cannot make the linear description wrong for any use this study makes of it, and a
departure larger than that is by the study's own standard a real deviation. Tying the two together also
means the registration commits to one set of numbers rather than two.

### 6.3 What happens when linearity is rejected

The difference is **still computed and still reported** — it is a statement about two measured endpoints
and remains true whatever the path between them looks like. It is reported as a **two-endpoint
difference with a NON-LINEAR flag**, the flag travels with the number wherever it appears, and the
channel remains eligible for the decision rule of §7 (the endpoints are what the rule uses).

**It is never extrapolated.** No ROM at any speed other than the two measured endpoints is inferred from
a flagged channel, no per-(m/s) rate is quoted for it, and no statement about intermediate or higher
speeds is made from it.

---

## 7. The separation bar and the decision rule

### 7.1 The between-seed spread, computed not asserted

From the six existing control cells at benchmark speed, window [1.00, 13.58] s, 9 cycles each. Deposit:
`paper/MDD_r203.json`. Angles in radians, `cycle_time` in seconds; the degree column is the operative one.

| channel | mean ROM | SD (n=6) | CV % | 2×SD_c | in degrees |
|---|---|---|---|---|---|
| ankle_angle_l | 0.5366 | 0.0035 | 0.65 | 0.00694 | 0.398 |
| ankle_angle_r | 0.5397 | 0.0026 | 0.48 | 0.00514 | 0.294 |
| knee_angle_l | 1.0841 | 0.0019 | 0.17 | 0.00378 | 0.217 |
| knee_angle_r | 1.0842 | 0.0021 | 0.20 | 0.00424 | 0.243 |
| hip_flexion_l | 0.9648 | 0.0028 | 0.29 | 0.00559 | 0.320 |
| hip_flexion_r | 0.9647 | 0.0032 | 0.34 | 0.00650 | 0.372 |
| hip_adduction_l | 0.2187 | 0.0065 | 2.99 | 0.01307 | 0.749 |
| hip_adduction_r | 0.2133 | 0.0039 | 1.82 | 0.00776 | 0.444 |
| pelvis_list | 0.1970 | 0.0052 | 2.66 | 0.01047 | 0.600 |
| pelvis_rotation | 0.4741 | 0.0148 | 3.11 | 0.02950 | **1.690** |
| lumbar_bending | 0.1541 | 0.0035 | 2.24 | 0.00692 | 0.396 |
| ankle_angle_LmR | 1.0615 | 0.0043 | 0.41 | 0.00863 | 0.495 |
| knee_angle_LmR | 1.9449 | 0.0046 | 0.24 | 0.00928 | 0.532 |
| hip_flexion_LmR | 1.4423 | 0.0030 | 0.21 | 0.00606 | 0.347 |
| hip_adduction_LmR | 0.4018 | 0.0079 | 1.98 | 0.01589 | 0.911 |
| cycle_time | 1.1919 | 0.0018 | 0.15 | 0.00360 | (s) |

**The decisive fact: 14 of the 15 angle channels have a `2×SD_c` bar below one degree.** Only
`pelvis_rotation`, at 1.690°, exceeds it. A rule that used `2×SD_c` alone would therefore fire on
differences far below any kinematic effect anyone could call meaningful — a fifth of a degree of knee
excursion is not a finding about spasticity, it is the between-seed jitter of an optimiser.

### 7.2 The floor (free parameter, chosen here)

> **FLOOR = 1.000° for every angle channel, and 0.020 s for `cycle_time`.**
>
> **Bar(c) = max(2 × SD_c(c), FLOOR).**

*Justification, angles.* One degree is the conventional resolution limit of marker-based joint-angle
measurement and is the granularity at which joint kinematics are read clinically; a between-arm
difference in excursion change smaller than one degree is not a kinematic claim anyone could act on,
whatever its statistical status. It is a physical quantity fixed before the data and not tuned to any
channel.

*Justification, `cycle_time`.* 0.020 s is 1.7 % of control's 1.1919 s mean cycle at benchmark, which sits
just below the stride-time variability of ordinary human walking, and it is roughly 5.6× the deposited
`2×SD_c` of 0.00360 s. Below that, a change in cycle duration is not distinguishable from normal
step-to-step variation in the system being modelled.

**The floor will bind on nearly every channel, and that is the operative situation, not a formality.**
Against the deposited spread it binds on 14 of the 15 angle channels and on `cycle_time`; only
`pelvis_rotation` is decided by its own `2×SD_c`. In effect this study asks a one-degree question of
almost every channel, and that is what it is registered to ask.

*Stated honestly, not netted:* `SD_c` in the operative rule is the between-seed SD of the **difference**
`D(control, s, c)`, computed from this study's control arm, not the between-seed SD of a single-speed ROM
level that the deposit contains. A difference of two per-cell ROMs will generally have a larger
between-seed SD than one ROM, so the realised `2×SD_c` will generally exceed the table above. The table
is therefore the pre-data illustration of the bar's scale and the basis for the claim that the floor
binds widely; which term of the `max()` wins on a given channel is settled by the data at analysis time,
by the formula registered here and by no other decision.

### 7.3 `SD_c` when control loses seeds

- `SD_c` is computed on the control seeds that contribute (all three of their cells passing all gates),
  `n = 6` only if all six survive.
- With `n = 5`, `SD_c` is computed and every number derived from it is labelled `n=5`.
- **With `n ≤ 4`, `SD_c` is not usable and no separation decision is made at all** (§9.2). An `SD_c`
  estimated from 3 or 4 seeds is close to meaningless: it has almost no precision, and a bar built from
  it is as likely to be far too small as far too large. This is registered as a stopping condition, not
  as a caveat attached to a computed result.

### 7.4 ⭐ WHAT IS REPORTED: 48 NUMBERS, AND NOTHING IS CLASSIFIED

⭐ **For each of the sixteen channels of §4, three numbers are reported, whatever they show:**

```
Δ_s(c) = Dbar(spastic, c)  −  Dbar(control, c)      signed
Δ_w(c) = Dbar(weak,    c)  −  Dbar(control, c)      signed
Bar(c) = the minimum detectable difference of §7.2      per channel
```

*where `Dbar(a,c)` is arm `a`'s mean over contributing seeds of `ROM(1.30) − ROM(0.80)` on channel `c`.*

⛔ **48 numbers. No classification scheme, no 2×2, no excess rule, no row-3 consequence, no
orientation convention, no sign-of-clearing rule.** *Every one of those existed to adjudicate patterns
the 48 numbers show directly.* ⭐ **A reader holding `Δ_s`, `Δ_w` and `Bar` for sixteen channels can
construct any classification they like; a reader holding a verdict and no numbers cannot check it.**

### 7.5 ⭐ THE PRIMARY — one registered binary

> ⭐ **Does any channel satisfy** `|Δ_s(c)| − |Δ_w(c)| ≥ Bar(c)` **?**

**Reported as YES or NO, with the channels that satisfy it named, and with all 48 numbers printed
beside it.**

⭐ **ONE-SIDED BY CONSTRUCTION.** *The spastic arm's speed-response must be LARGER IN MAGNITUDE than
the weak arm's, which is the mechanism's prediction.* ⛔ **It cannot fire when the weak arm dominates,
and there is no outer absolute value that could make it two-sided.** *An earlier version wrote
`|Δ_s − Δ_w| ≥ Bar`, which counted a channel with `Δ_s = +2, Δ_w = +8` — the weak arm four times
larger, same direction — as evidence FOR velocity gating. That form is withdrawn.*

### 7.5a The secondary — separate, and non-inflating

> **Channels where** `sign(Δ_s(c)) ≠ sign(Δ_w(c))` **and both** `|Δ_s(c)| ≥ Bar(c)` **and**
> `|Δ_w(c)| ≥ Bar(c)` — *the two arms respond to speed in OPPOSITE DIRECTIONS.*

⛔ **This is a different claim from "larger". It may not be summed with the primary, combined into a
count with it, or used to rescue it if the primary returns NO.** *It is reported on its own line.*

### 7.5b ⚠ The cost of this design, stated rather than hidden

⚠ **This design does not pre-commit to a conclusion beyond the single binary of §7.5. Richer patterns
in the 48 numbers — which channels, how large, in what direction, whether they cohere anatomically —
will be OBSERVATIONS, not registered findings, and must be labelled as such.**

⭐ **That is the trade, and it is taken deliberately.** *Why, in one line: **five consecutive rounds of
repair in the verdict machinery produced five new defects, and the numbers can do the work the
machinery was doing badly.*** ⛔ **The count rule "4 of 16, at least 3 primitive", the 2×2 assignment
table and the excess rule are all deleted. Nothing replaces them.**

⚠ **What remains true and is not a decision rule:** *the sixteen channels are mechanically coupled and
four are deterministic pointwise functions of eight others, so a channel satisfying §7.5 is not an
independent success. There is no null distribution, no p-value, no coverage claim and no patient-level
inference anywhere in this design.*

### 7.6 The directional prediction, registered before the data

- **SPASTIC is predicted to show the larger speed-response.** Its reflex is velocity-gated; if velocity
  dependence reaches gait kinematics at all, this is the arm in which it should appear.
- **WEAK is predicted not to.** Its parameter, `tib_ant_l` ×0.892, does not change with speed.
- ⚠ **A speed-invariant parameter is not a speed-invariant effect.** *The demand placed on `tib_ant_l`
  changes with speed, so its effect on gait may perfectly well be speed-dependent. The weak arm is a
  comparison arm, not a guaranteed null — which is exactly why the primary is a COMPARISON of
  magnitudes and not a test of the spastic arm alone.*
- **Δ_s, Δ_w and Bar are reported per channel with the arm named.** *No statement of the form "a lesion
  arm responded on N channels" is made without naming which arm.*

## 8. Gates, definitions, and the order they are applied in

All gates are per cell. **The ordering below is the registered ordering and it is non-circular: each step
uses only quantities fixed by earlier steps or by constants registered here. In particular the analysis
window is defined by fixed constants and ground reaction force alone, and achieved speed is measured only
afterwards, over the window the earlier step produced.**

### 8.1 Step 1 — completion gate (G1)

A cell passes iff its `history.txt` has **≥ 91 lines** AND its tag resolves to **exactly one** result
directory. A cell failing either condition is DROPPED and contributes nothing.

### 8.2 Step 2 — which solution is evaluated (G6)

**The final `.par` written by the optimisation at the point where `history.txt` reaches 91 lines is the
solution evaluated.** No earlier best-so-far checkpoint is used, and no solution is chosen by inspecting
outcomes.

*Why:* selecting a checkpoint by objective value would be a lesion-dependent selection, since the
objective differs between arms. A fixed generation count is the same depth rule for every arm, which is
the same construction that excludes r169's depth confound.

### 8.3 Step 3 — cycle detection, and the definitions of "admitted cycles" and "the admitted window" (G5)

These definitions are given here in full. Nothing about them is deferred to another file.

- **Settle time `SETTLE = 1.00 s`. Analysis end `T1 = 13.58 s`.** Both are fixed constants, identical for
  every cell, every arm and every speed. They are the values used for the control cells from which
  `MDD_r203.json` was computed.
- **Heel strike:** the vertical ground reaction force on the left foot crossing **upward** through
  **5 % of body weight** and remaining above it. A refractory of **0.30 s** is applied, so that a
  crossing within 0.30 s of the previous accepted strike is not counted as a new strike. (0.30 s is about
  a quarter of control's benchmark cycle, so it cannot merge two genuine strikes, and it removes force
  chatter at contact.)
- **A gait cycle** runs from one left heel strike to the next left heel strike. Left, because
  `tib_ant_l`, `soleus_l` and `gastroc_l` — the lesioned side — are all on the left.
- **Admitted cycles:** the **first six** complete cycles whose start heel strike is at or after `SETTLE`
  and whose end heel strike is at or before `T1`. Exactly six are used in every cell that passes; a cell
  containing more than six such cycles uses the first six and ignores the rest.
- **The admitted window:** the interval from the start heel strike of the 1st admitted cycle to the end
  heel strike of the 6th admitted cycle. Its duration is the sum of the six cycle durations.

*Why exactly six and not "all that fit":* a fixed-duration window contains fewer cycles at 0.80 m/s than
at 1.30 m/s by construction, so averaging over "all cycles in the window" would give fast cells a quieter
per-cell mean than slow cells — a speed-dependent difference in estimator noise, in the very quantity the
primary differences. Fixing the count at six makes the per-cell averaging identical at every speed.

### 8.4 Step 4 — gait validity gate (G2), free parameter chosen here

> **A cell passes iff at least 6 admitted cycles exist as defined above. Fewer than 6 → DROPPED.**

*Justification, and why it is not speed-confounded.* The window [1.00, 13.58] is 12.58 s long, so six
cycles need SEVEN heel-strike boundaries inside the window, so they fit whenever the mean cycle duration
is at most 12.58 / 7 = **1.797 s**, i.e. up to **1.51×** control's benchmark cycle of 1.1919 s.
⛔ **An earlier version of this paragraph divided by 6 and claimed 2.096 s and 1.76×. That omitted the
lead-in: the first admitted heel strike falls at or after `SETTLE`, so one boundary is spent before the
first complete cycle begins. This registration's own deposit proves it — 12.58 / 1.1919 = 10.55, yet
control yields 9 cycles, exactly one short of the count the wrong arithmetic predicts.**
Control at benchmark yields 9 cycles, so the gate carries three cycles of headroom there, and the true
allowance at 0.80 m/s is a cycle-duration lengthening of up to 51 %, not 76 %. A threshold set at or near 9 would drop slow cells preferentially and would remove the very
low-speed endpoint the primary difference is made of; 6 is chosen to be attainable at 0.80 m/s by any
gait that is walking at all, so that this gate fires on degenerate gait rather than on slowness.

### 8.5 Step 5 — achieved-speed gate (G3), free parameter chosen here

**Achieved speed** = (pelvis anterior translation at the end of the admitted window − pelvis anterior
translation at the start of the admitted window) ÷ (duration of the admitted window). The window is
already fixed by step 3, which used no speed information; this is where the circularity of the earlier
draft is removed.

> **A cell whose achieved speed differs from its own command by more than ±0.05 m/s is DROPPED and is
> not analysed.**

*Justification against the one measurement we have.* The single measured tracking error is a **+0.0215
overshoot** at command 1.0. A ±0.04 budget would be 54 % consumed by that ordinary bias, leaving under
0.019 m/s of headroom, and the gate bites hardest at command 1.30 where tracking is hardest — so ±0.04
would drop cells for the model's habitual bias rather than for failure to perform the task, and would do
so preferentially at one end of the design. ±0.05 leaves 0.0285 m/s of headroom beyond the known bias
(the measured error is 43 % of it), is 10 % of the 0.50 m/s design span, and is still tight enough that
the gate is not vacuous.

*The residual risk, stated as a limitation and not repaired.* The gate is needed because a compressed
achieved-speed interval reads exactly like reduced speed sensitivity, which is this study's headline. At
±0.05 the worst admissible case — the slow cell overshooting and the fast cell undershooting by the full
tolerance — leaves an achieved span of 0.40 m/s against a design span of 0.50, so an endpoint difference
can be attenuated by up to 20 % by speed-tracking error alone. The primary is not rescaled to correct for
this, because rescaling would turn the difference into a rate and reintroduce the quantity §6.1 rejects.
The achieved endpoint speeds and the realised span are reported per seed per arm so the reader can see
the actual spread; a 20 % attenuation ceiling on cross-seed and cross-arm comparability is a limitation
of this design.

### 8.6 Summary of the order

1. G1 completion → 2. fix the evaluated solution → 3. cycle detection on [1.00, 13.58] from GRF, giving
admitted cycles and the admitted window → 4. G2 cycle-count gate → 5. G3 achieved-speed gate → 6. compute
ROM over the six admitted cycles.

No step uses a quantity defined by a later step.

---

## 9. Attrition

### 9.1 Attrition, and the consequence is registered now

⭐ **A seed contributes to an arm if BOTH ENDPOINT cells — 0.80 and 1.30 m/s — pass every gate. The
1.05 cell does not gate that contribution.** ⛔ *An earlier version required all three. That gave the
midpoint cell a veto over the seed while §6.1's own table prints its contribution to the primary as
**0.00 %** — a cell with zero weight in the estimate must not be able to remove the estimate.*

**The 1.05 cell gates the LINEARITY CHECK only**, which is reported separately, per §6.2. ⚠ **The
linearity check is reported only when at least 5 seeds of an arm have a surviving 1.05 cell — the same
minimum §9.2 sets for the primary. Below 5 it is reported as NOT EVALUABLE, not as passing.**

**Per-cell survival therefore enters the primary as its SQUARE, not its cube.** *The required rates,
computed and stated because an earlier version stated none:*

| rule | per-cell survival needed for ≥ 5 contributing control seeds |
|---|---|
| all three cells (withdrawn) | **94.1 %** |
| ⭐ **two endpoint cells (registered)** | **91.3 %** |

**At 85 % per-cell survival, two-endpoint seed survival is 72 %, i.e. about 4.3 seeds per arm** — still
below the §9.2 control threshold of 5. It is registered here, before any data, that a per-cell survival
rate as high as 85 % is already enough for this design to fail to reach its own decision threshold, and
that outcome would be reported as the study's result rather than worked around.

### 9.2 Control-arm attrition has its own rule

**If the control arm contributes fewer than 5 seeds, no separation decision is made, regardless of how
many seeds the lesion arms contribute.** The differences are reported per arm with the floor shown for
reference, the drop counts are reported, and the study's result is the attrition itself.

*Why control specifically:* every bar in §7 is built from control's between-seed spread. A rule that only
halted when *no* arm reached the threshold would permit a control arm at 3 seeds to set the bar for
lesion arms at 6 — a decision resting on a 3-sample SD. That configuration is excluded by this rule
rather than disclosed after the fact.

**If a lesion arm contributes fewer than 4 seeds**, its differences are reported and labelled
UNDERPOWERED and it is not used for the §7.5 primary.
⛔ **AND THE PRIMARY IS THEN NOT EVALUABLE. The §7.5 primary is a TWO-ARM comparison: excluding either
lesion arm makes `|Δ_s| − |Δ_w|` uncomputable, so the primary is reported as NOT EVALUATED —
explicitly NOT as NO, and explicitly not as YES.** *All 48 numbers of §7.4 are still reported for
whatever arms and channels survived, and the drop counts of §9.3 are reported as the study's result.*

### 9.3 Drop counts are a registered reported outcome

The number of dropped cells **per arm per commanded speed, with the reason for each drop** (G1 failure,
G2 cycle count, G3 achieved speed), is a registered outcome and is reported in full whatever it shows,
including in the branches where the primary is not computed.

### 9.4 The selection problem, stated as a limitation

Requiring all three cells to pass is complete-case selection, and cell survival is a descendant of the
lesion. This is collider conditioning: the surviving spastic seeds are plausibly those whose spasticity
did *not* prevent speed tracking — that is, the seeds in which the lesion did least. **The selection
therefore points at the null for the spastic arm.** This is not correctable within this design, no
weighting or imputation is registered, and no analysis in this document removes it. The primary is a
complete-case quantity and is labelled as one wherever it is reported.

### 9.5 Non-comparability rule (free parameter, chosen here)

> **If a lesion arm's dropped-cell count exceeds control's by more than 2 cells (out of 18 cells per
> arm), the primary comparison between that arm and control is labelled NON-COMPARABLE and the
> separation decision is not reported for that arm.**

*Justification.* Each arm has 6 seeds × 3 speeds = 18 cells. Because attrition is cubic, an excess of 3
dropped cells can already remove 3 of an arm's 6 seeds if they fall in different seeds — half the arm.
Setting the margin at 2 makes the label fire before the two arms' surviving-seed sets can differ by more
than a third of the arm, which is the point beyond which the two arms are no longer summarising
comparable populations of optimisations. The differences and drop counts are still reported under the
label; only the between-arm decision is withheld.

---

## 10. The assumption test

The premise that fibre velocity scales with gait speed — the premise that makes speed a dose axis and
that §3's conditional closure rests on — is measured directly.

**For every cell in every arm, including control, compute the mean of `max(0, ce_vel_norm)` over the
admitted window, for `soleus_l` and for `gastroc_l`.** This is a **mean**, not an integral, and it is
reported under that name. Computing it in all three arms — including control, whose KV is 0 and whose
delivered dose is therefore identically zero but whose fibre velocities are not — is what makes any
deviation attributable to an arm rather than to the model in general.

Three registered outcomes, reported whichever occurs:

- **The velocity mean tracks speed proportionally in all three arms** → the time-scaling premise holds,
  speed is a clean dose axis, and §3's conditional closure of the dose-matching route becomes firm.
- **It fails to track in all three arms** → this is a fact about the model's gait strategy, i.e. about
  how this model chooses to go faster. It is not a spastic-specific effect and it is not a failure of
  this design. §3's closure is void.
- **It fails to track only in the spastic arm** → the reflex is altering the gait that generates the
  reflex. That is a mechanism finding in its own right and is reported as one.

**There is no measured-dose fallback.** An earlier draft registered reinterpreting the primary against a
measured-dose x-axis if the premise failed; that fallback is **withdrawn and does not reappear anywhere
in this design**. Control's delivered dose is identically 0 and the weak arm's is speed-invariant, so
neither arm is defined on a dose axis and the between-arm comparison cannot be performed there. Achieved
speed is the axis in every branch; the velocity mean is reported beside it, never in place of it.

---

## 11. The within-seed pairing, and the registered test of it

Each difference is taken within one seed, across two speeds, which would difference out that seed's
optimiser basin **if the three cells of a seed shared a basin.** They may not: the three cells are three
independent optimisations that share a warm start and a seed index, nothing more. If basins re-randomise
per cell, the pairing is cosmetic and the differencing removes nothing.

**This is not asserted either way. It is tested, and the test is registered here as a reported outcome.**

For every arm, compute from the converged parameter vectors of the evaluated solutions:

- `W` = the median pairwise Euclidean distance between the three cells **of the same seed** (three pairs
  per seed), normalised by the number of parameters;
- `B` = the median pairwise Euclidean distance between **different seeds at the same commanded speed**,
  normalised the same way.

**If `W / B ≥ 1`, the pairing is declared COSMETIC** and every claim that the within-seed structure
removes basin variation is withdrawn in the report; the differences are then reported as unpaired
between-cell contrasts. If `W / B < 1` the pairing removed some basin variation and the ratio is
reported as the measure of how much. Either way the ratio is reported.

Even in the favourable branch, differencing removes additive offsets only. A basin that scales a channel
multiplicatively scales its difference too, and that is not removed by any pairing.

---

## 12. ⛔ WHAT THE RESULT MEANS IS NOT REGISTERED, AND THAT IS DELIBERATE

**The primary reports one of three states, with the satisfying channels named:**

| state | condition |
|---|---|
| **YES** | at least one channel satisfies `\|Δ_s(c)\| − \|Δ_w(c)\| ≥ Bar(c)` |
| **NO** | no channel satisfies it, and both lesion arms were evaluable |
| **NOT EVALUATED** | either lesion arm is UNDERPOWERED per §9.2, so the two-arm comparison is uncomputable |

**The 48 numbers of §7.4 are printed in every state. The secondary of §7.5a is reported on its own
line in every state, and rescues nothing.**

⛔ **NO INTERPRETATION OF ANY OF THE THREE STATES IS REGISTERED, AND THE OMISSION IS DELIBERATE.**
*Seven successive attempts to pre-register what a negative result MEANS each produced either an
unassigned case or a claim the evidence did not license — the last of them attaching "the axis the
mechanism is defined by does not carry it" to a failed manipulation check, which is the case that
supports it least.* ⭐ **That is a measurement, not a mood: the meaning of a negative is not
pre-registerable at this level of design, so this registration commits to a MEASUREMENT and a BINARY
and to nothing about interpretation.**

⚠ **The cost, stated plainly: readings of the result will be OBSERVATIONS made after the data, and
must be labelled as such.** *That is a smaller claim than this project wanted. It is the one this
process has demonstrated it can actually hold.*

---

## 13. Cost

The figure supplied to this seat was 79.2 s/cell. **It does not verify and it was wrong.** Measured from
the six completed control cells at identical depth and warm start (`history.txt` mtime minus directory
creation time): **211.7, 213.7, 214.2, 213.4, 185.8, 185.2 s → mean 204.0 s/cell.**

| | |
|---|---|
| 54 cells × 204.0 s | **11,016 s** serial |
| ÷ 2 at concurrency 2 | **5,508 s = 91.8 min** |

**Two caveats, stated separately and deliberately not netted against each other:**

1. The six measured cells are **control arm at benchmark speed only**. Applying 204.0 s to spastic and
   weak cells at 0.80 and 1.30 m/s is an extrapolation across both arm and speed.
2. If those six cells ran under contention, the per-cell figure is inflated — **but in that case the
   ÷2 concurrency gain is not also available.** An earlier draft claimed both at once. They are
   alternatives, not a pair of corrections that can be applied together.

No per-cell timeout is registered. A non-converging cell therefore has unbounded cost and must be killed
by hand if one appears.

---

## 14. Limitations

Stated as limitations. None of them is repaired by being stated, and none is presented as a strength.

1. **Complete-case selection is collider conditioning on a descendant of the lesion, and it points at the
   null for the spastic arm** (§9.4). Not correctable here.
2. **Achieved-speed tolerance permits up to 20 % attenuation of the endpoint difference** through
   interval compression alone (§8.5).
3. **Three speeds, six seeds, one model, one controller, one objective.** The seeds are optimiser
   restarts, not subjects. There is no p-value, no null distribution, no coverage claim and no
   patient-level inference in this design.
4. **Sixteen mechanically coupled channels, four of them pointwise functions of eight others.** The
   §7.5 primary is a decision rule, not evidence about chance.
5. **The endpoint differs from the parent studies'**, which reported the mean level of an `LmR` channel.
   This study reports a change in excursion between two speeds. The numbers are not comparable to the
   parents' and no comparison to them is registered.
6. **The floor, not the between-seed spread, is what almost every channel is judged against** (§7.2). The
   study's sensitivity on 14 of 15 angle channels is set by a chosen physical threshold rather than by
   the data's own variability.
7. **`Bar(c)` uses `SD_c` of the difference, whereas the deposited table is `SD_c` of a single-speed ROM
   level.** The realised bars will generally be larger than the table's (§7.2).
8. **Whether this model can walk at 0.80 or 1.30 m/s at all is unknown before the run.** If an arm cannot,
   that is reported as a viability boundary — a result about the model's range — and if no arm produces a
   usable pair of endpoints, the primary is not computed and the boundary is the study's finding.

---

## 15. Scope and standing

**In scope:** 3 commanded speeds × 3 arms × 6 seeds = **54 cells**. Arms: control, spastic KV 0.050,
weak `tib_ant_l` ×0.892. No new magnitudes. From-healthy warm start, identical for all arms, no
continuation from any existing `.par`. Concurrency 2.

**Out of scope:** sit-to-stand; terrain inclines of any kind; the mirrored-lesion arm; any new KV; any new
weak scale; any new or altered channel set; any continuation run; any document repair while this runs.

**Operational standing.** The 112 protected directories under `C:\Users\maurice\Documents\SCONE\results\`
yield nothing and our cells yield on any conflict. Progress is counted from `history.txt` line counts and
directory mtimes only — `LAUNCH_STATUS.json` is never read. Writes are confined to
`C:\Users\maurice\Desktop\spasticity_paper\` and the 54 new result directories. The frozen manuscripts
are not opened.

---

## 16. Every free parameter, in one place

| # | parameter | registered value | where | one-line reason |
|---|---|---|---|---|
| 1 | FLOOR, angle channels | **1.000°** | §7.2 | conventional resolution of joint-angle measurement; below it there is no kinematic claim to make |
| 2 | FLOOR, `cycle_time` | **0.020 s** | §7.2 | 1.7 % of the 1.1919 s control cycle, just under ordinary stride-time variability |
| 3 | linearity tolerance `T(c)` | **= `Bar(c)`** (1.000° / 1.690° / 0.020 s under the deposit) | §6.2 | curvature is judged on the same scale as the smallest difference the study will call real |
| 4 | achieved-speed tolerance | **±0.05 m/s**, drop gate | §8.5 | the known +0.0215 bias consumes 43 % of it rather than 54 %; 10 % of the 0.50 m/s design span |
| 5 | minimum admitted cycles | **6**, and exactly 6 used | §8.3–8.4 | attainable at 0.80 m/s (needs cycle ≤ 2.096 s = 1.76× benchmark), so the gate fires on degenerate gait, not on slowness |
| 6 | channel count for the decision | ⛔ **DELETED — no count rule. The primary is the single binary of §7.5** | §7.5b | five rounds of repair in the verdict machinery produced five new defects; the 48 reported numbers show the patterns the count was adjudicating |
| 7 | non-comparability margin | **> 2 cells above control's drop count**, of 18 per arm | §9.5 | fires before cubic attrition can make the two arms' surviving-seed sets differ by more than a third |
| 8 | control-arm stop rule | **< 5 contributing control seeds → no separation decision** | §9.2 | an `SD_c` on 3–4 seeds is close to meaningless and must not set the bar for a fuller lesion arm |
