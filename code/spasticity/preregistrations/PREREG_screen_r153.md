# PREREG_screen_r153.md — the exhaustive screen: does ANY feature survive adjustment?

**Round 153, 2026-08-10. NOT RUN. Registered and hashed before any statistic is computed.**
*Where this document and any script disagree, THIS DOCUMENT DECIDES.*

## 0. What this replaces

**Five separate findings now share one shape:** *`ank_vel_max` (raw AUC 0.0000 → residual 0.3600,
R² 0.8030); r139's six shape/variance/asymmetry features (all dead, R² 0.60–0.95); r153's thirteen
measurement pipelines (raw 0.0000 in every one, residual null in every one, R² 0.77–0.90); r152's two
hip channels and their asymmetry (raw near chance, residual null, R² 0.68–0.91).*

⛔ **That is five anecdotes. The paper can say "we tried five things and they failed." It cannot say
what is true, which is stronger: whether ANY feature this corpus can produce survives.**

## 1. ⛔ THE POOL, ENUMERATED NOT CHOSEN, AND FIXED HERE

**`sto_utils.cycle_features` returns 15 keys. Two are not kinematic features and are excluded by
definition, not by preference:** *`n_cycles` (a count) and `t_end` (run duration).*

**The remaining 13:** `ank_hs`, `ank_max`, `ank_mean`, `ank_min`, `ank_rom`, `ank_stance_mean`,
`ank_swing_min`, `ank_vel_max`, `cycle_time`, `hip_rom`, `knee_min`, `knee_rom`, `stance_frac`.

### 1a. ⛔ The three covariates are IN the feature set — decided now, before looking

**`ank_rom`, `cycle_time` and `ank_hs` are the adjustment covariates.** *Regressing a covariate on
itself is degenerate: the residual is numerically zero and the test is meaningless.*

⛔ **THEY ARE EXCLUDED FROM THE TESTED POOL AND REPORTED SEPARATELY AS TRIVIALLY DEGENERATE.**
*Their RAW separation is still reported, because it is meaningful and it is part of the exhaustiveness
claim. Their residual is not tested and will be printed as `DEGENERATE`.*

⚠ **This is decided in advance precisely because deciding it after seeing which features survive is
the failure this register exists to catch.**

### 1b. The forms, and the pool size

**10 testable features × 2 sides (l, r) = 20**, plus **10 signed `L − R` asymmetries = 10.**

> ⛔ **POOL = 30. Fixed here, before any result is seen.**

## 2. ⛔ THE SCREEN CANNOT FIND ANYTHING, AND THAT IS STATED BEFORE IT RUNS

**At 5 conditions versus 5, the minimum attainable two-sided exact p is `2/C(10,5)` = **0.007937**.**

**Bonferroni ×30 gives a corrected floor of `30 × 0.007937` = **0.2381**.**

⛔ **NOTHING CAN REACH p_adj < 0.05, NOT EVEN A PERFECT SEPARATION. Beyond 6 features the design is
arithmetically incapable of a corrected positive — `PREREG_shape_r138.md` §4 measured this and it
applies here with full force.**

⭐ **So what is this screen FOR? It is an EXHAUSTIVENESS ARGUMENT, not a discovery instrument.**

*It converts "five features failed" into "no feature this corpus can produce survives adjustment for
ankle ROM, cadence and equinus" — a bounded, enumerable, referee-checkable claim about the model
class.* ⛔ **A screen that cannot find anything must say so up front or it is theatre. This one says
so.**

**Reported quantities are therefore DESCRIPTIVE, not inferential:** *raw AUC and uncorrected p;
residual AUC, uncorrected p and R²; and the joint distribution of those across all 30.*

## 3. Procedure — identical to the registered residual test

**Corpus `scone/replay_crossed`, 10 conditions × 4 seeds, condition-level means, 5 spastic v 5 weak.**
*Exact two-sided Mann–Whitney, AUC = U/25, overlap as `residual_test.py` counts it. Adjustment:
regress on `ank_rom + cycle_time + ank_hs + 1`, same three covariates, same OLS, taken from side `l`
for every quantity so the adjustment is identical across the pool.* ⛔ **`residual_test.py` is READ and
NOT modified.**

## 4. ⚠ THE PREDICTION, REGISTERED SO THE SCREEN CAN FALSIFY IT

> ⭐ **`ank_rom` is not a nuisance covariate. It is the lesion's DIRECT MECHANICAL CONSEQUENCE — a
> stiff plantarflexor and a weak dorsiflexor both change ankle range, by construction. So anything
> that tracks lesion severity necessarily tracks `ank_rom`, and adjusting for it removes the lesion
> along with the confound.**

**If that is right, the screen MUST come out null, and the null is a statement about the EXPERIMENTAL
DESIGN rather than about kinematics.**

**Falsifiable form, fixed now:** *if the prediction holds, features that separate raw should be
precisely the features with high R² on the covariates.* **Registered test: the rank correlation
between raw separation strength `|AUC − 0.5|` and covariate R², across all 30.**

| outcome | reading |
|---|---|
| **strong positive correlation** | ⭐ **the prediction holds: separation IS covariate structure** |
| **no correlation** | ⛔ **the prediction is FALSE** — separation and covariate-explicability are independent, and the nulls need a different explanation |
| **a feature with high raw separation and LOW R² and a surviving residual** | ⛔ **the prediction is falsified by counterexample** |

## 5. What a survivor would and would not be

⛔ **If any feature shows a residual AUC ≤ 0.1 or ≥ 0.9 with uncorrected p < 0.05, it is flagged as a
CANDIDATE — a hypothesis for a NEW registration, never a result.** *It came out of a 30-way screen
whose correction cannot license anything, and §2 says so in advance.*

⚠ **No sensitivity, specificity or patient-level AUC may be quoted from this study.** *Seeds are
optimiser restarts, not subjects; conditions are lesion magnitudes, not patients.*

## 6. What a clean null licenses

⭐ **"No feature that `cycle_features` can produce, in either limb or as a left–right asymmetry,
separates plantarflexor spasticity from dorsiflexor weakness after adjustment for ankle ROM, cadence
and equinus."**

⚠ **Bounded exactly:** *it is a claim about THIS corpus, THIS feature set and THESE three covariates.
It is not a claim about gait analysis, about other models, or about features nobody has computed.*
⛔ **And per §4, if the prediction holds, the null is a statement about the design — the adjustment
removes the lesion — not evidence that the lesions are kinematically identical.**
