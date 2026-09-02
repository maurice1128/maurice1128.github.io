# PREREG_3d_reopt_r151.md — 3D with RE-OPTIMISATION, registered before any run exists

**Round 151, 2026-08-10.** *Hashed before a single scenario was built. Where this and any script
disagree, THIS DOCUMENT DECIDES.*

## 0. The measurement that makes this possible, taken first

**3D re-optimisation is ~12× CHEAPER than the 2D corpus, not more expensive.**

| | model | solver | 90 generations |
|---|---|---|---|
| 2D slope corpus | `H0914M`, 9 DoF | **`ModelOpenSim4`** | **13.7 min** *(measured, 234 cells)* |
| **3D benchmark** | `H1922v7b3`, **19 DoF** | ⭐ **`ModelHyfydy`** | ⭐ **1.1 min** *(measured: 90 gens in 65 s, 0.73 s/gen)* |

⛔ **The 2D study was slow because of its SOLVER, not its dimensionality.** *The cost objection to 3D
rested on an assumption nobody had measured. It is false.*

## 1. ⛔ The defect in P3D-2 and P3D-3 that this exists to fix

**Every 3D arm so far was a `sconecmd -e` EVALUATION: one parameter vector, tuned for the healthy
model, dropped onto a lesioned model or controller.** *No 3D arm has ever been re-optimised.*

⛔ **The 2D study re-optimised every cell.** *That is where "the optimiser avoids the provocation"
came from — the finding that β_int vanishes under fitness adjustment is a finding ABOUT adaptation.*

**A stroke survivor has adapted to their lesion. The 2D study modelled that by re-optimising. The 3D
probes did not.** *So "A2 weak falls at 6.93 s" may mean only "a healthy-tuned controller cannot cope
with a weakened muscle" — expected, and nearly silent on whether an ADAPTED 3D gait differs.*
⛔ **P3D-2 and P3D-3 were not the same experiment as the 2D study, and their nulls do not transfer.**

## 2. Design — 3 arms × 6 seeds = 18 runs, every one re-optimised

| arm | injection | mechanism |
|---|---|---|
| **C** control | none | baseline |
| **S** spastic | `MuscleReflex` on `soleus`+`gastroc`, `legs = left`, `KV = 0.050`, `allow_neg_V = 0` | CONTROLLER |
| **W** weak | `tib_ant_l` `max_isometric_force` × 0.80 | MODEL |

⭐ **Magnitudes are the 2D REGISTERED values, unchanged — `KV = 0.050` and PAR20's ×0.80.** *P3D-2
showed 0.050 floors an un-adapted 3D model at 3.87 s. **That is the prediction under test: if
re-optimisation lets it survive, the earlier probes were measuring adaptation failure, not the
lesion.** Lowering the magnitude now would search for a value that works, which is what §6 of r150
refused and this document also refuses.*

Seeds **101–106**, warm-started from the converged benchmark par, `max_generations = 90`.
**Estimated cost: 18 × 1.1 min ≈ 20 min single, ~10 min at 2 concurrent.**

## 3. ⛔ Gate G — registered before the endpoint, because it can void the study

**An arm is ADMITTED iff ≥ 4 of its 6 seeds each reach ≥ 9.73 s and ≥ 5 GRF cycles after settle.**
*Same viability bar as P3D-2, same 80 %-of-baseline logic, and the 4-of-6 floor is the 2D
registration's own attrition rule.*

| outcome | meaning |
|---|---|
| **all three admitted** | proceed to §4 |
| **S or W not admitted** | ⛔ **the 2D magnitude is not viable in 3D even with adaptation.** A result, and it closes this design. **Do NOT titrate — that is a new registration.** |

## 4. The endpoint — out-of-plane INCLUDED, or 3D was pointless

**Per-cycle mean, over a COMMON window across all admitted arms, GRF-delimited, settle 1.0 s.**
⛔ **NOT global range** — that metric inflated a 0.405° difference into 1.934° at r145 and is
forbidden here.

**Sagittal:** `ankle_angle_l/r` ROM, `knee_angle_l/r` ROM, `hip_flexion_l/r` ROM, `cycle_time`.
**Out of plane:** `pelvis_list` ROM, `hip_adduction_l/r` ROM, `pelvis_rotation` ROM, `lumbar_bending` ROM.
**Asymmetry:** for each, `(L − R)`, signed.

**PRIMARY: does any endpoint separate S from W across seeds, two-sided Mann–Whitney, 6 v 6?**
Minimum attainable two-sided p at 6 v 6 is **2/C(12,6) = 0.00216**. **13 endpoints ⇒ Bonferroni ×13**;
a perfect separation reaches **p_adj = 0.0281**, which clears 0.05. **The pool is 13 and fixed here.**

⚠ **Seeds are OPTIMISER RESTARTS, NOT SUBJECTS** — the 2D registration's caveat, carried verbatim.
**No sensitivity, specificity or patient-level AUC may be quoted from this study.**

## 5. Falsifiers

| | fires when | consequence |
|---|---|---|
| **FS** | no endpoint reaches p_adj < 0.05 | **3D with adaptation does not separate the two lesions on this endpoint set.** *Given 2D also failed, that is convergent evidence and the strongest negative this project can produce.* |
| **FG** | S or W fails Gate G | the design is void, not negative — §3 |
| **FC** | control C fails Gate G | ⛔ **the benchmark itself does not survive re-optimisation; nothing is interpretable** |

## 6. Registered in advance so it cannot be claimed later

- ⛔ **A positive here is a MECHANISM result on optimiser restarts. It is not a clinical claim and not
  a screening claim**, and the 2D line's central finding stands regardless: the discriminating signal
  is destroyed by adjustment for ROM, cadence and equinus.
- ⛔ **If S separates from W only on out-of-plane channels, that is the registered hypothesis for
  doing 3D at all** — and it must then be tested against the r141 caveat that this model's
  `pelvis_rotation` (27.3°) and `lumbar_rotation` (23.7°) exceed normal, so an out-of-plane positive
  may live in an over-rotating trunk.
- ⛔ **No result from P3D-2 or P3D-3 may be pooled with this one.** *Those are evaluations; these are
  re-optimisations. Mixing them is the compression defect.*
