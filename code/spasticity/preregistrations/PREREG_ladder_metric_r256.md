# PREREG_ladder_metric_r256.md — the core analysis on mean angle, beside excursion

**Written BEFORE any mean-angle ladder value was computed, round 256.**

---

## 1. Why this is being run, and the order it was run in

**`METRIC_r255.json` established that the incumbent EXCURSION metric does not see the lesion's
principal effect**: the reflex arm holds the left ankle ≈1.5° more plantarflexed on both windows
(equinus), against a control band 0.058° wide, and excursion registers no displacement at all.

⛔ **THE ORDER MATTERS AND IS RECORDED HERE BEFORE THE NUMBERS EXIST.** *Excursion was run first, for
the whole project. Mean angle is being run second, after excursion produced a null on the lesioned
ankle. **Any result that mean angle produces is therefore a result found by a metric adopted after the
first one failed**, and it must be reported as such at the number, however it turns out.*

⭐ **The metric was never registered.** *Excursion was inherited from `channels_g2_r219.py` and never
chosen against an alternative. The physiological argument for mean angle on a tonic lesion — a stretch
reflex produces a sustained offset, which is what mean angle measures — **was available before the data
and nobody made it.***

## 2. The decision that is NOT open

⛔ **The paper does not switch metrics. Both are reported, everywhere, for every result in §1–§7.**
*Switching after seeing that the first metric gave a null is the forking path in its purest form. The
resolution is disclosure, not selection.*

## 3. What is computed

Read-only, from `.sto` files on disk, on both windows, for the control arm, the reflex arm and all six
weakness rungs, per seed:

1. **Per-seed `hip_flexion_LmR` and `ankle_angle_LmR` under mean angle**, beside the excursion values
   already deposited.
2. **Seed-level disjointness** of the reflex arm against each weakness rung, and pooled — the test §3
   and §6b use.
3. **The opposed-channel test of §6** under mean angle: how many of the sixteen channels are displaced
   in opposite directions from the control band by the two lesions.
4. **The six-rung margin ladder and its Spearman ρ** under mean angle, the test §6b uses.

## 4. The readings, registered in advance

**READING A — mean angle gives a CLEANER separation than excursion** (more disjoint rungs, more
opposed channels, or a monotone hip ladder where excursion had none).
⭐ **Reported at full strength AND labelled at the number as a result obtained from a metric adopted
after the first one failed.** ⚠ *It is not less true for how it was found, but a reader must be told
the order, in the same sentence as the number.*

**READING B — mean angle gives a WEAKER or equal separation.**
**Reported unchanged.** *This would mean the excursion result was not merely metric-contingent but the
more favourable of the two, which is itself worth stating.*

**READING C — the two metrics disagree about WHICH channel is the opposed one.**
⛔ **Then "one channel of sixteen opposes" is a statement about a metric, not about the model, and the
paper must say so in those words.**

**READING D — no channel opposes under mean angle.**
⛔ **The paper's central §6 result exists only under excursion, and that must be stated as plainly as
the result itself.**

## 5. What this does not decide

*The magnitude, cardinality, site and antagonist confounds are untouched by any metric. So is the
second-body outcome. A metric change cannot repair a design that lacks the 2 × 2.*
