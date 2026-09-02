# PREREG_speed_r89.md — walking speed as a provocation, registered before any run exists

**Registered 2026-08-04, round 89. NOT LAUNCHED. No run of this design exists at the time of
hashing.** This registration is hashed before a single scenario is executed, as
`slope_analysis_r62.py` was.

**Where this document and any analysis script disagree, THIS DOCUMENT DECIDES.**

---

## 1. THE QUESTION, AND WHY SPEED RATHER THAN SOMETHING ELSE

The slope study raised ankle excursion in **both arms nearly equally** — per-arm slope responses
**+2.7885** (spastic) and **+3.2864** (weak). **Downhill is a global effect on ankle excursion, not a
spasticity-specific one**, and the registered interaction was correspondingly small and
indistinguishable from noise.

**Spasticity's definitional property is a velocity-dependent stretch reflex.** A provocation must
therefore raise **plantarflexor stretch velocity**, not ankle range. **Speed does that directly.** It
is also a **scenario parameter, not a model change** — no new terrain, no new task definition, and no
new convergence regime to discover.

---

## 2. THE GROUND, MEASURED BEFORE REGISTERING ANYTHING

**(a) Speed has never been manipulated in this corpus.** 1,228 scenarios at `min_velocity = 1.0`,
16 at 1.2, 5 at 0.8, 4 at 0.6; **the entire slope corpus is 1.0** (255 scenario files).

**(b) The controller sits ON the threshold, it does not exceed it.** Achieved forward pelvis velocity
over the 48 level runs, settle 1.0 s:

| | mean | min | max |
|---|---|---|---|
| corpus-wide (n = 48) | **1.005** | **0.956** | **1.070** |

**Headroom over the registered threshold: +0.005 m/s mean, +0.070 m/s at the single fastest run.**
⚠ **1.4 m/s is +31 % over the fastest speed this corpus has ever produced; 1.8 m/s is +68 %.**

**(c) The mechanism channel exists and its baseline is measured.** Peak plantarflexor stretch
velocity, `max(gastroc_l, soleus_l) fiber_velocity_norm`, settle 1.0 s, at `min_velocity = 1.0`:

| cond | arm | mean | min | max |
|---|---|---|---|---|
| DR2K000 | CONTROL | 2.1121 | 2.0180 | 2.2659 |
| DR2K050 | spastic | 2.2140 | 1.9209 | 2.9009 |
| DR2K075 | spastic | 1.8899 | 1.8132 | 2.0036 |
| PAR20 | weak | 2.5247 | 2.0050 | 3.7149 |
| PAR40 | weak | 3.2068 | 2.2487 | 5.5591 |

**Spastic arm mean 2.0520, weak arm mean 2.8658, difference +0.8138.** ⚠ **At baseline the WEAK arm
already has the higher plantarflexor stretch velocity.** That is registered here because it is the
opposite of the naive expectation and it sets the direction the manipulation must change.

---

## 3. DESIGN

- **Factor:** `min_velocity` ∈ **{1.0, 1.4, 1.8} m/s**, subject to §5's feasibility gate.
- **Conditions (5):** `DR2K000` (control), `DR2K050`, `DR2K075` (spastic), `PAR20`, `PAR40` (weak).
- **n = 6 per cell, `random_seed` 101–106.**
- **Budget identical to the slope study:** `min_progress = 0`, `max_generations = 90`,
  `init_file = ResultH0914Gait10.par`, **no warm start, no `_resume.par`**.
- **Model:** the level parent **of each condition's family**, all of which already exist:
  `H0914_SGM_BASE_D0.osim` for `DR2K000` / `DR2K050` / `DR2K075`, and
  `H0914_SGM_PAR20_D0.osim` / `H0914_SGM_PAR40_D0.osim` for the weak conditions, which carry
  weakened `tib_ant` and therefore have their own parents. **No model file is created by this
  study.** ⚠ *An earlier draft of this line said the model was `BASE_D0` for all five conditions.
  The build-time budget assertion failed on 36 files and that is how the error was found — before
  this document was hashed, which is the only reason it could be corrected rather than registered.*

**REUSE OF THE 1.0 ARM.** The slope study's D = 0 cells are the same five conditions at
`min_velocity = 1.0` on the same model at the same budget with the same seeds. **They are reusable
only if a generated v = 1.0 scenario is byte-identical to the corresponding `SG0_*` scenario apart
from `signature_prefix`.** **This is verified by content at build time, not assumed.**

- **If verified: 60 new runs** (5 conditions × 2 new levels × 6 seeds).
- **If any other difference is found: the 1.0 arm is NOT reusable and the study is 90 runs.**
  **Registered now so the larger number cannot later be presented as scope creep.**

---

## 4. ★ THE MECHANISM GATE — registered in advance, which the slope study lacked

**The slope study could only discover after 21 hours that its manipulation was not
mechanism-specific.** This one states the check first.

**M1 — DOES SPEED RAISE PLANTARFLEXOR STRETCH VELOCITY AT ALL?**
Peak `fiber_velocity_norm` (max of `gastroc_l`, `soleus_l`, settle 1.0 s) must rise monotonically
with `min_velocity` in the **control** condition `DR2K000`. **If it does not, the manipulation does
not do the thing it was chosen for, and the study is VOID rather than negative.**

**M2 — DOES IT LOAD THE TWO ARMS DIFFERENTLY?** The registered mechanism quantity is

> **Δ_M = [stretch velocity slope vs speed, spastic arm] − [same, weak arm]**

**REGISTERED PREDICTION: Δ_M > 0.** The spastic arm's reflex is velocity-dependent, so raising
stretch velocity should load it *more*.

⚠ **REGISTERED IN ADVANCE — WHAT FOLLOWS IF Δ_M ≈ 0.** If speed raises stretch velocity **equally in
both arms**, then **the interaction on `ank_rom` will fail exactly as downhill's did, and this
registration predicts that failure now rather than discovering it later.** In that case the study is
reported as **MECHANISM-NULL**: the provocation was global, not spasticity-specific, and **the
finding is about the provocation, not about the feature.** *This is the sentence the slope
registration did not contain.*

**M3 — the two are not interchangeable.** M1 failing voids the study. M2 failing does not void it:
it yields a reportable negative with a named mechanism.

---

## 5. FEASIBILITY GATE FOR 1.8, AND ITS REGISTERED FALLBACK

**The 5° lesson: a manipulation level the controller cannot solve produces convergence failure
dressed as an effect.** At 5° the cold-start cost was 92.9–94.5 against 16.6–19.4 at level and half
the control seeds failed to converge.

**S1 — FEASIBILITY PROBE, RUN FIRST AND ALONE.** One cell, `DR2K000` at `min_velocity = 1.8`, seed
101. **Criterion: ≥ 2 complete GRF-delimited gait cycles under `cycle_features`, AND achieved
forward pelvis velocity ≥ 1.6 m/s, AND terminal best fitness within one order of magnitude of the
matched v = 1.0 cell.**

⚠ **The third clause exists because G4 did not have it.** *G4's two-cycle criterion can be satisfied
by a barely-viable gait whose feature is inflated by non-convergence rather than by the
manipulation — this project has that on the record, and the fix is to require convergence explicitly
rather than infer it from cycle count.*

**REGISTERED FALLBACK.** If S1 fails, **the 1.8 arm is not launched**, the design reduces to
**{1.0, 1.4}**, and that reduction is reported as **NOT ATTAINABLE**, not as a design choice. **Its
power consequence is costed in §7 in advance.**

---

## 6. PRIMARY, FALSIFIERS, AND WHAT MAKES THE NEGATIVE FINAL

**Primary:** `β_speed` = the arm × speed interaction on `ank_rom`, seed-level OLS
`ank_rom ~ condition + v + arm:v`, **weak minus spastic**, exactly the slope study's form with `v`
in place of `D`.

**Required effect,** derived as `beta_req` was: the rung-to-rung mild margin must reach the standing
**3.800°** MDC from its level value **1.5752°**, across the manipulated range.

| design | range | **`beta_req`** |
|---|---|---|
| {1.0, 1.4, 1.8} | 0.8 m/s | **2.7810 ° per m/s** |
| {1.0, 1.4} fallback | 0.4 m/s | **5.5620 ° per m/s** |

**F1 — PRIMARY FALSIFIER.** `β_speed ≤ 0` — the manipulation moves the arms together or the wrong
way. **If F1 fires, the negative is FINAL and no further provocation of this kind is registered.**

**F2 — MECHANISM FALSIFIER.** M2's `Δ_M ≤ 0`. **Fires MECHANISM-NULL per §4.**

**F3 — MANIPULATION FALSIFIER, VOIDS RATHER THAN FALSIFIES.** M1 fails: stretch velocity does not
rise with speed in the control. **VOID, not null.**

⚠ **WHAT MAKES THE NEGATIVE FINAL, fixed now so it cannot be renegotiated after the values are
visible:** **if F1 and F2 both fire, the conclusion is that neither slope nor speed provokes a
spasticity-specific ankle-excursion difference, and the screening approach via `ank_rom` is closed —
not "provisional pending a better provocation".** *Two provocations chosen on opposite mechanistic
grounds, both global, is a result about the feature and not about the provocations.*

---

## 7. ★ POWER, REGISTERED HONESTLY BEFORE LAUNCH

Scaled from the slope study's **realised** SE — 0.6847 at n = 6 with Σ(D−D̄)² = 12.6667 — not from a
design assumption, because that assumption was wrong by a factor of two last time.

| design | Σ(v−v̄)² | projected SE(β_speed) at n = 6 | `beta_req` | **required effect in SE** |
|---|---|---|---|---|
| {1.0, 1.4, 1.8} | 0.3200 | **4.308 ° per m/s** | 2.7810 | **0.65 SE** |
| {1.0, 1.4} | 0.0800 | **8.616 ° per m/s** | 5.5620 | **0.65 SE** |

⚠ **AT n = 6 THIS STUDY CANNOT DETECT THE CLINICALLY REQUIRED INTERACTION. The required effect is
0.65 of one standard error under both designs. Reaching half-SE precision would need 58 seeds per
cell.**

**Therefore this study is REGISTERED AS A MECHANISM SCREEN, NOT A CLINICAL TEST.** Its informative
outputs are **M1, M2 and F1's sign** — all of which are large-effect questions — **and it is
registered now that a null on the clinical margin carries almost no information at this n.** ⚠ **No
clinical claim may be made from this design at n = 6, in either direction.** *Registered before
launch precisely so that a null cannot later be presented as evidence of absence, and a positive
cannot be presented as clinically meaningful.*

---

## 8. GATES BEFORE LAUNCH

- **G5 tag collision**, against a results root now holding 491+ directories of which **43 already
  carry `" (1)"`. SCONE appends rather than overwrites.**
- **Budget assertion** read back from every generated file: the six registered properties.
- **Reuse verification** per §3, by content.
- **No edit to `gen_slope_r60.py` or `gen_slope_tier2_r87.py`.** A companion generator only.
- **112 protected directories untouchable; our cells yield at BELOW_NORMAL, concurrency 2, machine-wide
  `sconecmd` count.**
- ⚠ **Tier 2 finishes first. Nothing in this study launches while it holds the cores.**

---

## 9. WHAT IS FIXED BY THIS DOCUMENT AND CANNOT MOVE AFTERWARDS

Following the §4.4 precedent, whose value was that a line's status was fixed **before** its number
was visible:

1. **The mechanism gate's direction** (Δ_M > 0) and **what a null means** (MECHANISM-NULL, a finding
   about the provocation).
2. **The 1.8 feasibility criterion, all three clauses**, and the fallback's identity as NOT
   ATTAINABLE.
3. **`beta_req` under both designs**, derived from the standing MDC before any datum exists.
4. **The power statement** — 0.65 SE, 58 seeds for half-SE — and the consequence that **no clinical
   claim is available at n = 6**.
5. **What makes the negative final** (F1 ∧ F2).
6. **The run count under both reuse outcomes**, 60 or 90.
