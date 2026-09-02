# PREREG_3d_residual_r168.md — the covariate-residual test applied to the two `(L−R)` channels

**Round 168, 2026-08-10.** *Registered and hashed BEFORE the first number of this test exists. Where
this document and any script disagree, **THIS DOCUMENT DECIDES**. It is not edited after execution;
defects found in it go to an errata.*

**Host study:** `PREREG_3d_reopt_r151.md`, sha256 `f6a65408731cc714…`.
**Data under test:** `REOPT3D_RESULT_r151.json` key `registered_asymmetry_endpoints`, deposited
round 167. **No new simulation is run. No `--run`, no `--launch`, no `sconecmd`.**

## 0. The item, quoted from the deposit before anything is done to it

| channel | S mean | W mean | AUC | p_raw | p_adj ×16 |
|---|---|---|---|---|---|
| `ankle_angle_LmR` | −0.179 | +2.308 | **0.000** | 0.002165 | 0.03463 |
| `hip_flexion_LmR` | −2.029 | +0.417 | **0.000** | 0.002165 | 0.03463 |

⛔ **Both are perfect separations that have never been offered to the covariate-residual gate.** *Five
features have died at that gate, including `ank_vel_max`, which was also AUC 0.0000 with zero overlap
before adjustment. `PREREG_3d_reopt_r151.md` §6 registers in advance that the 2D line's central
finding — "the discriminating signal is destroyed by adjustment for ROM, cadence and equinus" —
stands regardless of this study's outcome. That is precisely the adjustment not yet performed here.*

## 1. ⛔ The structural problem, resolved here and not papered over

`residual_test.py` fits at **CONDITION level**: 10 conditions (5 spastic doses `DR2K050…DR2K200`,
5 weak doses `PAR20…CMW80`), each a mean over its seeds, covariates `ank_rom` + `cycle_time` +
`ank_hs` + const — **4 parameters on 10 observations**, and the ten conditions span a **DOSE LADDER**.

This study's units are **6 optimiser seeds per arm within 2 arms**. ⛔ **These are different designs,
and the difference is not the sample size — it is that there is no ladder.** *All within-arm
variation is optimiser-restart noise at one fixed lesion magnitude (`KV = 0.050`; `×0.80`). All
between-arm covariate variation is 100 % confounded with the label, because the arm IS the label.*

**Three candidate designs were on the table. What is registered, and why the others are wrong:**

| | design | verdict registered here |
|---|---|---|
| **(a)** | per-seed fit, `ank_rom` + `cycle_time` + `ank_hs` + const = 4 params on 12 obs | ⛔ **REJECTED — circularity.** For `ankle_angle_LmR` the covariate `ank_rom` is the **left-limb term of the outcome itself**. Regressing `ROM_L − ROM_R` on `ROM_L` is regressing a difference on its own component; it absorbs variance by construction and adjusts for nothing. *This is the failure that "reuse the familiar covariate list" would have produced, and it is why the list is not reused.* |
| **(b)** | ⭐ **per-seed fit, REDUCED and RE-EXPRESSED covariate set** — §3 | ⭐ **REGISTERED as PRIMARY**, subject to the gate in §4 |
| **(c)** | declare the test not applicable at this design | ⛔ **REGISTERED as the outcome the §4 gate returns if common support fails.** *It is not a fallback for a disappointing number; it is triggered by a covariate-only quantity computed before any residual.* |

⚠ **The second reason (a) is wrong, independent of circularity: a `(L−R)` endpoint's nuisance
variable must be a `(L−R)` quantity.** *`ank_hs_l` is a left-limb equinus measure. Two seeds can have
identical left-limb equinus and opposite asymmetry. Adjusting a signed asymmetry for an unsigned
single-limb value does not hold presentation constant; it holds half of it constant.*

## 2. ⭐ The resolution floor at 6 v 6 — computed from the DESIGN, before any data

*Exact enumeration of all C(12,6) = 924 rank assignments. This uses no measurement; it is a property
of n alone. The same code reproduces the registered 5 v 5 floor of |AUC − 0.5| = **0.4200** that
`SCREEN_r153.json` carries, which is how the code is calibrated.*

| n | C | min attainable two-sided p | uncorrected floor \|AUC−0.5\| | ×2 | ×4 | ×13 | ×16 |
|---|---|---|---|---|---|---|---|
| 5 v 5 | 252 | 0.0079365 | **0.4200** *(AUC 0.0800)* | 0.4600 | 0.5000 | ⛔ unreachable | ⛔ unreachable |
| **6 v 6** | **924** | **0.0021645** | **0.3611** *(AUC 0.1389)* | ⭐ **0.4167** *(AUC 0.0833)* | 0.4444 | **0.5000** | **0.5000** |

⛔ **THE CONSEQUENCE, REGISTERED IN ADVANCE BECAUSE IT DEVALUES THIS TEST AND MUST NOT BE DISCOVERED
AFTERWARDS.** *At 6 v 6 under the ×2 correction this test carries, the smallest declarable
\|AUC − 0.5\| is **0.4167** — the residual must retain **at most 3 of 36 pairwise inversions**. The
test can therefore distinguish only **"still essentially perfect"** from **"everything else."***

⚠ **It has NO power to separate "attenuated but real" from "destroyed."** *A residual landing at
AUC 0.25 — a large, obvious attenuation — and a residual landing at AUC 0.50 — nothing left at all —
are the same verdict here. **A residual failure at this n is therefore NOT evidence that the
covariates explain the signal.*** ⭐ **This is registered as a limitation of the instrument, not as a
result, and it is why a null here buys strictly less than the 2D null did.**

⚠ **It is also why the test is still worth running: the SURVIVAL branch is not devalued.** *If a
residual retains \|AUC − 0.5\| ≥ 0.4167 after adjustment, that is a real finding at a stringent bar.
Only the null branch is weak. Registering an asymmetric instrument is legitimate; pretending it is
symmetric afterwards is not.*

## 3. The primary specification

**Level of fit: PER SEED. n = 12 (6 S, 6 W).** *Condition level is unavailable — it would be 2
observations.*

**Covariates, identical for both channels, 2 + const = 3 parameters on 12 observations:**

| covariate | role | why it is admissible here |
|---|---|---|
| `cycle_time` | **cadence** | one bilateral value per seed; already in the deposit; **not a component of either outcome** |
| `ank_hs_LmR` | **equinus presentation, signed** | the 2D presentation confound re-expressed as `(L − R)`; heel-strike ANGLE, **not a range**, so it is not a component of either outcome |

⛔ **`ank_rom` is EXCLUDED, and the exclusion is the point of §1.** *Its `(L−R)` form
`ankle_angle_LmR` **is** channel 1. Including it would guarantee a null on channel 1 by algebra.*

**`ank_hs_LmR` is defined here, once, and this definition governs:** mean over cycles of
`degrees(ankle_angle_l[hs]) − degrees(ankle_angle_r[hs])`, sampled at the **same instants** the
endpoint's own cycles use — **left-GRF heel strikes, settle 1.0 s, common window upper bound T1 taken
from `REOPT3D_RESULT_r151.json` key `window`, last cycle dropped** — i.e. `analyse_reopt_r151.py`'s
cycle convention exactly. ⚠ *The alternative — each limb sampled at its OWN heel strikes — is a
different quantity. It is registered as **NOT computed**, so it cannot be reached for later.*

**Estimation:** ordinary least squares, `numpy.linalg.lstsq`, residual `Y − Xβ`.
**Contrast:** exact two-sided Mann–Whitney on the residuals, S vs W, 6 v 6, by full enumeration of
all 924 splits — the same routine `analyse_reopt_r151.py` used, not a normal approximation.
**Multiplicity: ×2 Bonferroni — two channels, both named above before any residual existed.** *The
pool is 2 and is fixed here. It is not recomputed to a friendlier value afterwards.*

**SENSITIVITY, declared NON-VERDICT-BEARING and uncorrected:** the literal `residual_test.py` analogue
`ank_rom_l` + `cycle_time` + `ank_hs_l` + const (design (a)). ⛔ **It is reported for information only
and is KNOWN IN ADVANCE to be circular for channel 1.** *It exists so the reader can see what the
familiar list would have done, not so a verdict can be taken from it.*

## 4. ⛔ Common-support gate — computed BEFORE any residual, and it can void the test

*Adjustment answers "at matched presentation." If S and W do not overlap on a covariate, there is no
matched presentation; the regression extrapolates into a region containing no observations, and the
residual is a model artefact rather than a measurement.*

**For each covariate independently:** `overlap = [max(min_S, min_W), min(max_S, max_W)]` is non-empty.

| gate outcome | consequence, registered now |
|---|---|
| **both covariates overlap** | proceed to §3; the verdict is the residual verdict |
| **exactly one overlaps** | ⚠ **proceed with that one only**, and the result states which covariate could not be adjusted for and why |
| **neither overlaps** | ⛔ **VERDICT (c): NOT APPLICABLE AT THIS DESIGN.** *No residual is reported, and no residual number appears in the result file — reporting a number here would be reporting an extrapolation.* |

## 5. Calibration gate — refuse to report anything new until something known reproduces

**Before any residual is computed, the script recomputes the four `(L − R)` arm means from
`REOPT3D_RESULT_r151.json` key `endpoints` (per-seed values) and compares them to the round-167
deposit in key `registered_asymmetry_endpoints`.** *Tolerance 1 × 10⁻⁹ absolute.*

⛔ **If any of the four fails to reproduce, the script exits non-zero and writes NOTHING.** *Same
discipline as `residual_cutoff_r153.py`. It is there because r161's deposit script returned 0.500 for
0.420 and was caught only because the answer was already known.*

**Also verified in the same gate:** the window `[1.0, T1]` used for `ank_hs_LmR` equals the deposit's
`window`, and exactly 6 S seeds and 6 W seeds carry values.

## 6. Outcomes, written now so they cannot be restated later

| outcome | fires when | what it licenses |
|---|---|---|
| **SURVIVES** | residual p_adj(×2) < 0.05, i.e. \|AUC−0.5\| ≥ 0.4167 | ⭐ **the asymmetry carries information beyond cadence and equinus presentation** — at a bar only near-perfect separation can clear |
| **UNRESOLVED** | residual p_adj(×2) ≥ 0.05 | ⛔ **NOT "destroyed."** *Per §2 this design cannot tell attenuation from abolition. The result states the residual AUC and states that the number is below the instrument's floor.* |
| **NOT APPLICABLE** | §4 gate returns no overlap | ⛔ **the test cannot be run at this design** — §8 says what would make it runnable |
| **VOID** | §5 calibration fails | nothing is reported |

## 7. What a SURVIVAL is not — registered before it can be claimed

⛔ **A survival here is NOT "we can distinguish spasticity from weakness."** It is:

- **6 optimiser seeds of one optimiser**, warm-started from one benchmark par. ⚠ *`PREREG_3d_reopt_r151.md`
  §4, verbatim: **"Seeds are OPTIMISER RESTARTS, NOT SUBJECTS… No sensitivity, specificity or
  patient-level AUC may be quoted from this study."*** That governs this test too.
- **a `(L − R)` asymmetry**, subject to `PREREG_shape_r138.md` §3's registered confound — *verified in
  that file this round, Route C, verbatim:* ⚠ ***"the intact limb compensates, so it is not a clean
  control, and the compensation may itself scale with impairment. A C-route positive is therefore
  consistent with 'asymmetry tracks impairment severity' as well as with a reflex, and the design
  cannot separate those."*** ⚠ *That was registered for the 2D `H0914M` routes. It is carried here by
  analogy, not by inheritance — this study registered no such clause of its own, which is itself a
  gap and is recorded as one.*
- **one lesion magnitude per arm.** *No dose–response is established, and §1 explains that no dose
  ladder exists in this study to establish one from.*
- ⚠ **still inside `PREREG_3d_reopt_r151.md` §6's out-of-plane caveat** where it touches trunk-adjacent
  channels, and still barred from being pooled with P3D-2 or P3D-3.

## 8. What design WOULD make this test applicable

⭐ **A 3D dose ladder, re-optimised.** *Concretely: ≥ 3 spastic levels (e.g. `KV` ∈ {0.025, 0.050,
0.100}) and ≥ 3 weakness levels (e.g. `×0.90, ×0.80, ×0.70`), each re-optimised with ≥ 6 seeds, and
the levels chosen so the two mechanisms' covariate ranges **overlap** — which the 2D corpus achieved
and which is the only reason "at matched presentation" was answerable there.*

**That is 36+ cells. At the measured 1.1 min/cell of `PREREG_3d_reopt_r151.md` §0 it is under an
hour.** ⚠ *The cost objection does not apply. What applies is that it is a **NEW REGISTRATION**, and
`PREREG_3d_reopt_r151.md` §3 forbids titrating inside an existing one. It is not started here and
nothing in this document authorises it.*

## 9. Constraints this test runs under

⛔ **No simulation. No `sconecmd`. Writes confined to `Desktop\spasticity_paper\`.** *The script reads
`.sto` files under `Documents\SCONE\results\` **read-only** and must never write, move or delete
there; the 112 protected directories are not touched or enumerated.* **`residual_test.py` and
`sto_utils.py` are imported UNMODIFIED — both are registered scripts and editing either is
prohibited.** *If a `.sto` is missing, the script FAILS; it does not replay, and it does not
substitute a value.*
