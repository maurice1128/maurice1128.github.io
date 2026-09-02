# PREREG_3d_probe_r141.md — P3D-1, the necessary-condition probe, registered before it runs

**Round 141, 2026-08-08.** *Written and hashed BEFORE the baseline 3D gait was replayed or measured.*

## 0. Why this probe exists, and what it is NOT

**Every 2D route is now closed by measurement**, each in a different way and each with its criterion
fixed in advance:

| route | outcome | how it died |
|---|---|---|
| slope, Tier 2, 234 runs | **INDETERMINATE** | β̂_int 0.4978 → **0.1613** as n grew; CI still spans 0 |
| shape / variance / asymmetry, 6 features | **F-ALL fires** | rom + cadence + equinus explain **60–95 %** of every feature |
| sit-to-stand | **NOT ATTAINABLE** | 1000 generations, terminal 14.1× the threshold, last 100 gens fall **0.75 %** |
| slow arm | **NOT ATTAINABLE** | achieved **1.0093 m/s** against a 0.6 target — the floor does not command slowness |

⛔ **The standing confound behind all four: the model is planar.** *`H0914M` has exactly nine sagittal
DoFs. It cannot produce circumduction, hip hiking, pelvic obliquity or trunk lean — the out-of-plane
compensations clinicians actually use to tell these two apart. **A null from a sagittal model is
partly a statement about the model, not only about the biomechanics.***

**This probe tests a NECESSARY condition and nothing more.** ⚠ *If the stock 3D gait barely leaves the
sagittal plane, no injection downstream can recover an out-of-plane signal and the 3D direction dies
cheaply. **If it does leave the plane, that licenses nothing about discrimination** — it only means
the channel exists. Sufficiency is a separate, later, and much more expensive question.*

## 1. What exists on disk, measured before writing this

| | |
|---|---|
| model | `H1922v2n.hfd` — **19 DoF, 22 muscles**, Hyfydy native |
| out-of-plane DoFs present | `pelvis_list`, `pelvis_rotation`, `pelvis_tz`, `hip_adduction_l/r`, `hip_rotation_l/r`, `lumbar_bending`, `lumbar_rotation` |
| injection targets present | **`soleus_l/r` and `tib_ant_l/r` — the same names as the 2D model** |
| weakness injection portable | **yes** — `max_isometric_force` appears 22× as plain text |
| converged warm starts | `H1922GaitRS2Hfd4.par`, `H1922GaitRS2Hfd5.par`, `H1922GaitRS4LHfdS4.par` |
| stock scenarios | `Gait3D - H1922`, `+ Treadmill`, **`+ Uneven Terrain`** |

⚠ **`H1922RS2v3` is NOT `GH2010`.** *The 2D injection was a `MuscleReflex` inside a
`ConditionalController` in a GH2010 tree. Whether that pattern ports to the RS2 controller is **not
tested by this probe** and is registered as open.*

## 2. The measurement

**Replay `init/H1922GaitRS2Hfd5.par` in the stock `Gait3D - H1922 - Hyfydy` scenario, unmodified
except for `init_file`. No optimisation. Measure per-cycle ranges over GRF-delimited cycles,
settle 1.0 s — the same cycle decomposition `cycle_features` uses.**

## 3. ⛔ The criteria, fixed now, with their anchor stated

**Anchored to normal-gait ranges from the clinical literature, at ONE THIRD of normal**, so the bar
is conservative and was not chosen to be cleared:

| DoF | normal total range | **one third** | **registered threshold** |
|---|---|---|---|
| pelvic obliquity (`pelvis_list`) | ≈ 10° | 3.3° | **≥ 3.0°** |
| hip ab/adduction (`hip_adduction`) | ≈ 12° | 4.0° | **≥ 4.0°**, mean of limbs |

| outcome | criterion | consequence |
|---|---|---|
| **PASS** | both thresholds met | the out-of-plane channel exists. **Necessary condition satisfied, nothing more.** Next step is the injection-portability probe, which is a separate decision |
| **FAIL** | either threshold missed | ⛔ **the stock 3D gait is effectively planar and the 3D direction is closed on the same footing as the other four.** Reported as a result |

**REPORTED, not PASS/FAIL:** `pelvis_rotation`, `hip_rotation_l/r`, `lumbar_bending` ranges; the
sagittal `hip_flexion`/`knee_angle`/`ankle_angle` ranges for scale; `n_cycles`; and wall-clock, so
the study can be priced later.

⚠ **A ratio is NOT used as the criterion.** *An out-of-plane range that is a large fraction of a
collapsed sagittal range would pass a ratio test while being absolutely tiny. Absolute degrees,
anchored to human values, cannot be gamed that way.*

## 4. What this probe cannot say, stated before it runs

- **Nothing about discrimination.** *It measures one healthy gait. No lesion, no contrast, no arms.*
- **Nothing about whether the injections port to `H1922RS2v3`.**
- **Nothing about cost at scale.** *One replay is not one optimisation, and 19 DoF is not 9.*
- ⛔ **A PASS is a permission to ask the next question, not evidence for 3D.** *The prior VoI table
  (MK_2D 0.747 → MK_3D 0.819 macro recall) is **not significant at its N** and carries a
  supraphysiological-gain caveat. This probe does not touch that.*

## 5. Discipline carried from the S2 failure, one hour ago

⛔ **A clause that cannot be measured must report UNEVALUABLE, never FAIL.** *S2's first evaluation
returned FAIL on two clauses because no `.sto` existed to measure — a defect in the probe, not in the
arm, and it would have closed the last live 2D route on a script's gap. **This probe asserts a `.sto`
exists and is non-empty before scoring anything, and reports UNEVALUABLE otherwise.***
