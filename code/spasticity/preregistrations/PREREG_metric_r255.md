# PREREG_metric_r255.md — is the instrument blind to the lesion it models?

**Written BEFORE any mean-angle value was computed, round 255.** *All readings are recorded here with
their consequences, so none can be selected after the numbers are seen.*

---

## 1. The objection

**Every channel in this project is a per-cycle peak-to-peak EXCURSION (range of motion).**
`RESULTS_3d_r214.md` §M5; `channels_g2_r219.py`.

⛔ **A plantarflexor stretch reflex's signature clinical effect is a sustained offset — equinus — which
changes the MEAN ANGLE of the joint and can leave its EXCURSION untouched.** *So the finding that the
reflex lesion "does not displace the ankle it acts on" (§6b) may be nothing more than what an
offset-blind metric returns.*

⚠ **§M5 already states that the `(L−R)` construction differs in sign from a point-wise left-minus-right
angle difference for every weakness arm. That warning has been in the Methods since it was written and
its consequence was never drawn.**

⭐ **Equinus is the presenting sign of plantarflexor spasticity — the thing this project set out to
detect. If the corpus cannot see it, the corpus has been measuring the quantity least sensitive to the
lesion it models.**

## 2. What is computed

**Read-only, from the `.sto` files already on disk. Nothing is re-simulated and no controller is
re-optimised.** For every arm and every cell, on **both** windows [1.00, 9.73] and [1.00, 13.58]:

1. **Per-cycle MEAN ANGLE**, per channel, averaged over the cycles in the window.
2. **Per-cycle PEAK PLANTARFLEXION** for the ankle channels.
3. **Per-cycle EXCURSION** — recomputed here rather than read from the deposits, so the three metrics
   come from one code path and any disagreement cannot be a difference of implementation.
4. **The control-band displacement test applied identically to all three**, the band being
   [min, max] over the six control seeds, exactly as §M7 defines it.

*The `(L−R)` channels are formed within each metric: `mean_angle(l) − mean_angle(r)`, and so on.*

## 3. The readings, registered in advance

**READING A — the left ankle IS displaced in mean angle.**
⛔ **§6b's contralateral headline is dead.** *The honest statement becomes: the reflex displaces the
limb it acts on, in a metric this study did not use, and the contralateral emphasis was an artefact of
the metric.* ⭐ **This is the largest single finding available tonight and it ships at full strength.
It means the corpus has been measuring the quantity least sensitive to the lesion it models, and every
channel result in the paper is contingent on an unregistered metric choice.**

**READING B — the left ankle is NOT displaced in mean angle either.**
⭐ **The contralateral observation survives a metric change and is materially stronger than before**,
because the obvious objection has been measured and excluded rather than argued away. *The paper must
then state that it was tested, and report the margin.*

**READING C — mean angle and excursion disagree on OTHER channels.**
⚠ **Every channel where they disagree is a channel whose reported result depends on a metric choice
nobody registered.** *All such channels are named, with the size of the disagreement, whichever way
Reading A or B falls. This reading is not exclusive with either.*

⚠ **A fourth outcome is possible and is registered too: the mean-angle computation may not be
well-defined for `cycle_time`, which is temporal, or for channels whose sign convention differs between
limbs. Any channel for which the metric is not meaningful is reported as NOT APPLICABLE and is not
quietly dropped.**

## 4. The separate question about the lesion itself

⚠ **The second-body deposit records the reflex as a `ConditionalController` named `SpasticL`.** *A
phase-gated reflex active only in certain gait states is a materially different lesion from a
continuous stretch reflex, and the manuscript describes it as neither.* **The controller definition is
read from the config and reported as written, whichever it turns out to be.**

## 5. What this does NOT decide

*Nothing here touches the magnitude confound, the cardinality confound, the antagonist confound, or the
second-body outcome. A metric change cannot repair a design that lacks the 2 × 2.*
