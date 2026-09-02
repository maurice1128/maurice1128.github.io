# PREREG_decompose_r268.md — is the reflex arm's objective a fall penalty or a training deficit?

**Written BEFORE the decomposition was computed, round 268.** ⛔ **Not blind:** *a first-time reader has
already reported that terminal objective regresses on simulated duration at r = −0.9982, R² = 0.9964
across 70 cells, fit by `objective ≈ 100 × (1 − t_end/20) + 2.9`, and that the objective is dominated by
`GaitMeasure { weight = 100, termination_height = 0.85 }`. That is recorded here rather than presented
as a prediction. The component decomposition has not been run.*

---

## 1. What r266 concluded and why it is in doubt

`FITNESS_r266.json` reported control 0.9873, weakness 1.0084–1.0487, reflex 19.3815–38.5324, and the
manuscript concluded that the arms are **not comparable optimisation outcomes** and that every
reflex-versus-weakness difference is confounded with **how well the controller was trained**.

⛔ **If the objective is dominated by a termination penalty, that conclusion is a category error: the
reflex objective would be high BECAUSE THE REFLEX MODEL FALLS, and falling is the lesion's effect, not
a nuisance covariate.** *An outcome of the treatment adjusted for as though it were a confounder is
post-treatment adjustment.*

## 2. What is computed

**Read-only, from each analysed cell's best `.par.sto`.** *The four non-`GaitMeasure` components are
present as columns: `Effort.effort`, `MuscleActivation.effort`, the `DofLimits` terms
(`*.position_penalty`, `*.limit_torque_penalty`) and `GRF.load_penalty`.*

**Evaluated over a COMMON INTERVAL that every one of the 48 analysed cells completes** — determined
from the data as [1.00 s, min over cells of `t_end`], so that no cell contributes a partial interval and
no term is inflated by a longer trace.

*Reported per cell and per arm, with the reflex arm compared against control and against the weakness
ladder on each component separately.*

## 3. Readings, registered in advance

**A — the reflex arm's non-termination cost sits at CONTROL LEVEL on the common interval.**
⛔ **Then the 19–38 objective is entirely fall penalty. §M3's fifth non-comparability collapses and is
withdrawn, "the arms were not optimised to comparable objective values" is withdrawn, and the corpus's
finding is the destabilisation result of §7c** — *a graded, monotone destabilisation with reflex gain,
which needs no weakness arm and survives the other four non-comparabilities.*
⚠ **§7c's own numbers would then need restating as destabilisation rather than as optimiser failure,
reversing the withdrawal made at r267.**

**B — the reflex arm's non-termination cost is GENUINELY ELEVATED.**
*Then the training confound survives and is for the first time **quantified rather than asserted**, on
the component that is not a function of fall time. Conditioning may become defensible on that component
if it has common support.*

**C — mixed: some components at control level, others elevated.** *Reported component by component with
no summary verdict, because a composite would re-create the very conflation this test exists to break.*

## 4. What this cannot address, fixed in advance

⚠ **It cannot tell whether 90 generations leaves the reflex arm further from ITS OWN optimum than the
weakness arms are from theirs.** *That needs the attainable optimum of the lesioned problem, which
requires the same seeds run with the generation cap raised until the running minimum is flat. **No cell
on disk contains it — every cell was stopped at generation 89 — and no read-only analysis substitutes.***

## 5. Defects repaired in this round, recorded because they are the analyst's own

1. ⛔ **`fitness_r266.py` and `gain_ladder_r264.py` resolve directories with a bare `sorted(g)[0]`**,
   which reads `R169W095_s105/_s106` from a **truncated duplicate** (80 generations, no `.par.sto`) that
   every kinematic script excludes via its `>= 91` history-line filter. *Fixed here to the same guard.*
2. ⛔ **Registered Reading D of `PREREG_fitness_r266.md` fired at 46 of 48 cells and was reported as
   `.par`-filename rounding.** *For `R169W095_s105` and `_s106` it was not rounding; it was defect 1.*
3. ⛔ **§7c.2's "5.31× and 3.36×" both divide by the KV 0.050 arm, which exists only in the R151 path**,
   inside a subsection titled "the two optimisation paths never pooled".
4. ⛔ **`never_left_starting_basin` is a hard-coded unregistered threshold (`< 1.0`)** — the same defect
   withdrawn one round earlier for `survives_adjustment`, and this time load-bearing for a withdrawal.
   *Withdrawn as a criterion; the raw descents are reported instead.*
