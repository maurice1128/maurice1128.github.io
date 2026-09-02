# PREREG_sitstand_r91.md — sit-to-stand as a VELOCITY CONTRAST, registered before any run exists

**Registered 2026-08-04, round 91. NOT LAUNCHED. No run of this design exists at the time of
hashing.** **Where this document and any script disagree, THIS DOCUMENT DECIDES.**

---

## 1. WHY A CONTRAST, AND WHY EVERY PREVIOUS DESIGN FAILED THE SAME WAY

**Spasticity is velocity-dependent. Weakness is not.** Therefore: **a slow rise separates the arms on
weakness alone; a fast rise separates them on weakness plus spasticity; and the difference isolates
the velocity-dependent component.**

This is the **Tardieu** contrast — slow passive stretch against fast, catch-angle difference as the
measure — **and it is the clinical gold standard for exactly this reason. Modified Ashworth's
weakness is that it measures an absolute.**

**Every provocation this project has tried has been an absolute — steeper, faster, a different task —
and all three failed the same way: the manipulation loaded both arms.** The slope study is the worked
example: per-arm responses **+3.2864 weak against +2.7885 spastic**, with the baseline
stretch-velocity gradient **already reversed at 2.8658 (weak) against 2.0520 (spastic)**.

⚠ **A contrast does not need a manipulation that loads only one arm. Whatever loads both cancels in
the difference.** **That is a structural property of the design, not a hope, and it is the first
design in this project to have it.**

---

## 2. DESIGN

- **Task:** sit-to-stand from the shipped deep-crouch initial state (`InitStateJump.zml`:
  `pelvis_ty` 0.75, `pelvis_tilt` −0.611, `hip_flexion` +1.396, `knee_angle` −1.222,
  **`ankle_angle` +0.436 = +25 deg DORSIFLEXION**).
- **Factor: rise duration**, two levels — **SLOW and FAST**, values set by the probe in §5 against
  the criterion in §4.
- **Conditions (5):** `DR2K000` control, `DR2K050` / `DR2K075` spastic, `PAR20` / `PAR40` weak.
- **n = 6, `random_seed` 101–106. 5 × 2 × 6 = 60 runs.**
- **Budget:** `min_progress = 0`, `max_generations = 90`, no warm start, no `_resume.par`.

**PRIMARY — the difference of differences:**

> **beta_STS = [spastic − weak] at FAST, minus [spastic − weak] at SLOW**, on `ank_rom`, seed level.

**The mechanism the crouch exploits:** the rise begins with the plantarflexors **at maximum length**
and is a fast return from there, and **the dorsiflexion is imposed by the task rather than emerging
from a gait pattern the controller is free to reorganise.**

---

## 3. THE 2D CHOICE, REGISTERED AS A CHOICE

Our corpus is **strictly planar** — `pelvis_tilt`, `pelvis_tx`, `pelvis_ty`, `hip_flexion_r/l`,
`knee_angle_r/l`, `ankle_angle_r/l`: **nine DoFs, nothing out of the sagittal plane.**

**This is a deliberate match to the observation modality — a single side-view camera — and not a
limitation to apologise for.** *A 3D model would simulate what the camera cannot see.* **SCONE ships
3D models (H1622, H1922, H3022), so 3D is available; adopting one abandons the calibrated corpus,
every lesion certification, and all 282 runs.** **Registered as a choice with its reason, because a
reader will ask.**

---

## 4. ★ THE RISE DURATIONS ARE NOT REGISTERED AS NUMBERS, AND HERE IS WHY

**The attempt was made and is reported rather than buried.** Peak ankle angular velocity against peak
plantarflexor stretch velocity, over the 20 relevant level runs:

```
ankle rate  : mean 5.575 rad/s, range 2.366 .. 8.528
stretch vel : mean 2.390 norm,  range 1.813 .. 5.559
linear fit  : stretch = 0.1144 * rate + 1.7520   (r = 0.319)
```

Applied to a 25 deg rise this gives implied stretch velocities of **1.852 at T = 0.5 s down to 1.764
at T = 4.0 s — a span of 0.088 across an eightfold change in duration.**

⚠ **That extrapolation is not usable and is rejected.** Sit-to-stand mean ankle rates
(**0.109–0.873 rad/s**) lie **an order of magnitude below the gait data's support (2.366–8.528)**,
the fit is weak (**r = 0.319**), and the mean rate is the wrong statistic for a movement whose peak
rate is several times its mean. *Choosing two registered constants from a fit evaluated far outside
its support is the class of error this project catalogues, and it would have been invisible in the
result.*

**REGISTERED INSTEAD — the criterion, not the constants.** The probe sets SLOW and FAST as:

> **the smallest FAST and largest SLOW rise durations, on the model's own achieved kinematics, whose
> peak plantarflexor stretch velocities differ by AT LEAST A FACTOR OF TWO, with SLOW's value at or
> below the level-gait baseline of 2.0520.**

⚠ **If no such pair exists, the contrast has no lever and the study does not launch.** **That is M0
in §6, and it is checked BEFORE any lesioned cell, not after the interaction is computed.**

---

## 5. FEASIBILITY PROBE — one control cell, and it needs a core

**`DR2K000`, unlesioned, registered budget.** **Criteria, all three:**

1. **At least 2 s of maintained standing** — `pelvis_ty` above the standing target, no termination;
2. **the rise completed** within the tested duration;
3. **terminal best fitness within ONE ORDER OF MAGNITUDE of the gait corpus's 0.59–0.68.**

⚠ **Clause 3 exists because G4 did not have it.** *G4's two-cycle criterion could be satisfied by a
barely-viable gait whose feature was inflated by non-convergence rather than by the manipulation —
this project has that on the record, and the fix is to require convergence explicitly rather than
infer it.*

**If the probe fails, sit-to-stand is NOT ATTAINABLE at this budget and that is the result.**

---

## 6. THE MECHANISM GATE

- **M0 — IS THERE A LEVER?** §4's criterion. **If SLOW and FAST do not separate on plantarflexor
  stretch velocity by a factor of two, the contrast has nothing to contrast. VOID, and no lesioned
  cell runs.**
- **M1 — does the rise load the plantarflexors at all?** Peak stretch velocity in the control must
  exceed the level-gait baseline of **2.0520** at FAST. **If not, VOID rather than null.**
- **M2 — does it load the two arms differently?** **Delta_M = [stretch-velocity increase FAST−SLOW,
  spastic arm] − [same, weak arm]. REGISTERED PREDICTION: Delta_M > 0.**

⚠ **REGISTERED IN ADVANCE — if Delta_M is about zero, beta_STS will be null exactly as the slope
interaction was, and that failure is predicted here rather than discovered.** Reported as
**MECHANISM-NULL: a finding about the provocation, not about the feature.**

---

## 7. FALSIFIERS, AND WHAT MAKES THE NEGATIVE FINAL

- **F1 — beta_STS <= 0.** The contrast moves the arms together or the wrong way.
- **F2 — Delta_M <= 0.** MECHANISM-NULL per §6.
- **F3 — M0 or M1 fails.** VOID, not null.

⚠ **THE EXTENDED CLOSURE CONDITION, fixed now so it cannot be renegotiated after the values are
visible: if F1 and F2 both fire, then FOUR designs on four different mechanistic grounds — steeper
(slope), faster (speed), a different task (sit-to-stand as an absolute), and a velocity CONTRAST
(this one) — have all failed, and `ank_rom` screening for spasticity versus weakness is CLOSED FOR
GOOD, not provisional pending a better provocation.**

---

## 8. POWER — registered honestly, and this is a MECHANISM SCREEN

**Scaled from the slope study's REALISED SE (0.6847 at n = 6), not from a design assumption — that
assumption was wrong by a factor of two.** **A difference of differences carries roughly twice the
variance of a single difference**, so at n = 6 the sampling error on beta_STS is expected to be
**larger than the slope study's**, against an effect no larger.

⚠ **THIS STUDY IS REGISTERED AS A MECHANISM SCREEN, NOT A CLINICAL TEST. No clinical claim may be
made from it at n = 6, in either direction.** **Its informative outputs are M0, M1, M2 and the SIGN
of beta_STS — all large-effect questions.** *Registered before launch precisely so that a null cannot
later be presented as evidence of absence, nor a positive as clinically meaningful.*

---

## 9. THE CONTROLLER DEVIATION, RECORDED AS A SCOPE REDUCTION

`ControllerReflexBalance.scone` targets `rect_fem` and `bifemsh`; **H0914M has neither.**
**Resolution chosen: the four pathways are DROPPED, not mapped.** Recorded in
`scone/sts_r91/ControllerReflexBalance_H0914M.scone`; **the shipped file is not edited.**

**Why dropped and not mapped:** mapping `rect_fem` to `vasti` and `bifemsh` to `hamstrings` would
place **two `MuscleReflex` blocks on the same target — the doubling shape that cost thirty of thirty
historical spastic runs their certification at rho about 2.0.** **A mapping is also a modelling
claim** — that a bi-articular hip-flexor/knee-extensor is substitutable by a mono-articular knee
extensor — **and this build is not entitled to make one.** **This is a scope reduction and is
labelled as one, not presented as an equivalent controller.**

⚠ **A SEPARATE UNRESOLVED PROBLEM, flagged as the highest risk in the build.** The registered
spasticity injection is a `ConditionalController` scoped by **gait state**
(`states = "EarlyStance LateStance Liftoff Swing Landing"`). **The balance controller has ZERO
states, and no shipped tutorial contains a stateless `ConditionalController` to copy.** **The
injection must therefore be restructured, and a restructured injection is exactly what rho
certification exists to catch.**

**RHO CERTIFICATION AT 1.0 ± 0.15 VIA `delivered_gain.py` IS MANDATORY BEFORE ANY LESIONED CELL
RUNS. No argument about controller form substitutes for it.** *The shipped controller's
`symmetric = 1` with unsuffixed targets is the correct shape, and that is an observation, not a
clearance.*

---

## 10. FIXED BY THIS DOCUMENT AND UNABLE TO MOVE AFTERWARDS

1. The primary as a **difference of differences**, and its direction.
2. **M0's factor-of-two lever criterion**, checked before any lesioned cell.
3. **M2's direction** and **what a null means** — MECHANISM-NULL, about the provocation.
4. **The probe's three clauses**, including terminal fitness within one order of magnitude.
5. **The extended closure condition** — F1 and F2 together close `ank_rom` screening for good.
6. **MECHANISM SCREEN, not a clinical test** — no clinical claim at n = 6.
7. **The controller deviation as a scope reduction**, and **rho certification as mandatory**.
8. **The 2D choice**, with its reason.
