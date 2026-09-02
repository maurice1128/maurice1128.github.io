# PREREG — Velocity-dependence as the discriminator (r368)

**Registered:** 2026-08-18, before any endpoint value below was computed for any cell of the
R203 grid. At the time of registration the only R203 facts consulted were **design** facts read
from `config.scone` and `H1922v7b3.hfd` — which condition carries which lesion, and what
`min_velocity` each arm was optimised against — plus a Gate-G feasibility count. **No
activation, torque, angle or endpoint value from any R203 cell had been computed.**

---

## 1. Why this is a different test from everything before it, and why it should have been first

Spasticity is **defined** as a *velocity-dependent* increase in the stretch reflex. Weakness has
no such property. Every measurement in this corpus so far — kinematic and dynamic alike — has
been taken at a **single** walking speed, where a velocity-dependent phenomenon and a
velocity-independent one can produce the same instantaneous picture. Three registered nulls
have now been recorded on single-speed endpoints:

| registration | endpoint | outcome | deposit |
|---|---|---|---|
| r360 | swing-phase plantarflexor activation | UNINFORMATIVE (arm mis-specified) | `DYNAMICS_SWING_r361.json` |
| r362 | swing-phase plantarflexor activation, correct arm | OVERLAP | `DYNAMICS_SWING_r363.json` |
| r364 | stance stretch-velocity slope of soleus activation | OVERLAP | `REFLEXGAIN_r366.json` |

This registration tests the property that **defines** the disease, using material that already
exists.

**The clinical analogue is exact.** The Tardieu test distinguishes spasticity from contracture
by stretching the muscle *slowly* and then *fast* and comparing. The test registered here is
that comparison, transplanted into gait: **walk slowly, walk fast, and compare.** Both
conditions are recorded with surface EMG and motion capture in any instrumented gait
laboratory. If it separates, a two-speed walking protocol substitutes for a diagnostic nerve
block.

---

## 2. The design, as read from disk

`R203` is a complete 3 × 3 grid, six seeds per cell, already simulated:

- **Speeds:** `min_velocity` = **0.80 / 1.05 / 1.30** m/s, the only difference between speed
  arms of the same condition (verified by diffing `config.scone`; the diff is that one line).
- **C — control:** no lesion.
- **S — spastic:** an added `ConditionalController` over states
  `EarlyStance LateStance Liftoff Swing Landing`, left leg, holding a `ReflexController` named
  `SpasticL` with `MuscleReflex target=soleus delay=0.020 KV=0.050 allow_neg_V=0` (and the
  companion gastrocnemius reflex). Model file byte-identical to control.
- **W — dorsiflexor weakness:** `config.scone` byte-identical to control except the signature;
  the lesion is in the **model file**, `H1922v7b3.hfd` line 388, `max_isometric_force` on
  `tib_ant_l` **1759 → 1569.0**, i.e. **×0.892**. Identical across all three speeds.

⚠ **Declared before measuring:** the nine cells are **separately optimised**. Seed s101 at 0.80
and seed s101 at 1.30 share a random seed, not a controller. A within-seed difference across
speed therefore confounds *the response to speed* with *a different optimum having been found*.
**The control arm C exists precisely to bound that confound** and is reported alongside; C is
what the speed response of an unlesioned model looks like under the same re-optimisation.

---

## 3. Primary endpoint — fixed here, before measurement

Observables only, as at r364 §3: joint kinematics, ground reaction force, inverse-dynamics
joint torque, and surface-EMG analogues. Excluded: `fiber_length`, `fiber_velocity`,
`mtu_force`, `tendon_length`, any muscle-internal `*_norm` channel, and every controller
parameter.

For one cell, let **`A`** = the mean of `soleus_l.activation` over the **stance** samples of the
admissible cycles, stance being `leg0_l.grf_norm_y > 0.05`.

**`SLOPE_v`** = the ordinary-least-squares slope of `A` on `min_velocity` across the three
speeds **0.80, 1.05, 1.30**, fitted **within one seed and one condition** — three points, one
scalar per seed per condition. Units: activation per (m/s).

**A seed contributes only if all three of its speed cells pass Gate G.** A seed with a missing
or failing speed cell yields no slope and is not partially imputed.

**Primary comparison:** **S versus W**, six seeds each at most.

**Predicted direction, declared before measurement:**

> **SPASTIC HIGH, DORSIFLEXOR-WEAK LOW.**
> Additionally predicted, and reported but not primary: **W ≈ C**, since a dorsiflexor force
> deficit carries no velocity-dependent term.

A separation in the opposite direction is a **failed prediction** and is reported as one.

---

## 4. Gate, window, conventions — carried unaltered

Gate G: `t_end` ≥ **9.73** s and ≥ **5** complete cycles inside the window **[1.00, 9.73] s**;
cycles delimited by left heel strike via `sto_utils.heel_strikes`; the last cycle in the window
dropped. Cell selection: the single directory whose `history.txt` has ≥ 91 lines;
`sorted(glob("*.par.sto"))[-1]`.

⚠ The three speed arms will have different cycle counts in a fixed 8.73 s window because they
walk at different speeds. That is expected and is not corrected for: `A` is a per-sample mean
over stance, not a per-cycle sum, so it does not scale with the number of cycles.

---

## 5. Separation criterion

Disjointness of the S and W ranges on `SLOPE_v`, plus an exhaustive seed-level permutation
floor over **C(12, 6) = 924**. **The floor is 1/924 and cannot be smaller**; this is stated now
so that a separation is not later reported as though it carried more resolution than six seeds
per arm can provide. Gap is the positive one of `min(W) − max(S)` or `min(S) − max(W)`; if
neither is positive the verdict is **OVERLAP**.

---

## 6. Secondaries — deposited, never promoted

`SLOPE_v` computed on `gastroc_l.activation`; on `tib_ant_l.activation`; on mean stance
`ankle_l.torque`; on ankle dorsiflexion ROM; and on peak stance dorsiflexion angle. The arm C
values for all of the above. The three per-speed `A` values themselves for every cell.
**None may become the primary endpoint under any outcome.**

---

## 7. Uninformative

Fewer than **4** contributing seeds in either the S or the W arm. No substitute endpoint, no
added speeds, no pooling of S with any other spastic family, no pooling of W with the
plantarflexor-weakness arm, no promotion of a secondary, no imputation of a missing speed cell.
If this fails it is recorded as a failure and this registration is not amended.

---

## 8. Declared limitations

1. r360 §8 unchanged: simulation `activation` is a clean 0–1 signal; separation here does not
   establish survival at surface-EMG noise levels, and this corpus cannot test that.
2. §2's re-optimisation confound: the arms are separately optimised at each speed. C bounds it;
   it is not eliminated.
3. Three points per slope. The slope is a descriptive per-seed statistic; **no standard error,
   confidence interval or p-value computed from that three-point fit may be reported.** All
   inference is the seed-level permutation of §5.
4. The spastic lesion here is KV = 0.050 on the left soleus and gastrocnemius only, and the
   weakness is ×0.892 on the left tibialis anterior only. Neither is a severity ladder, so this
   registration says nothing about dose.

---

## 9. What a positive result would license, and what it would not

**Would license:** the claim that a two-speed instrumented walking protocol carries information
that distinguishes a velocity-dependent plantarflexor lesion from a dorsiflexor force deficit,
in this model, conditional on §8.1.

**Would not license:** any claim about patients, about severities other than those in §8.4, or
about the size of the effect relative to the 3.8–11.5° clinical MDC — which is a kinematic
threshold and does not apply to an activation endpoint. If a kinematic secondary separates, the
MDC gate does apply to it and must be reported against it.
