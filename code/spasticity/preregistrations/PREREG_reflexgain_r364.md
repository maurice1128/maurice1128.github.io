# PREREG — Recovering the stretch-reflex gain from clinically observable signals (r364)

**Registered:** 2026-08-18, before any value of the endpoint below was computed for any cell.

---

## 1. What changed, and why this is not the previous endpoint

`DYNAMICS_SWING_r363.json` returned **OVERLAP** on swing-phase plantarflexor activation, and
the reason is mechanical, not statistical: the Geyer–Herr controller's plantarflexor reflex is
driven by **stretch**, and during swing the plantarflexors **shorten**. A raised velocity gain
therefore cannot express itself in swing in this model. Swing-phase plantarflexor EMG — the
thing the diagnostic nerve block actually probes in patients — is **not reproducible in this
model at all**. That is recorded as a model limitation at `DYNAMICS_LIMITATION_r365.json`.

Stretch of the plantarflexors happens in **stance**, while the shank rotates forward over the
planted foot and the ankle dorsiflexes. That is where a velocity-dependent reflex must appear
if it appears anywhere.

This registration therefore measures, in stance, **the quantity that spasticity is defined
as**: the dependence of plantarflexor activation on the *velocity* of its stretch.

---

## 2. Declared circularity, stated before measuring rather than after

The SPASTIC lesion in this corpus is literally a `MuscleReflex` **KV** term — a velocity
feedback gain — on soleus and gastrocnemius. An endpoint that estimates a velocity-dependent
activation gain is therefore **aimed directly at the lesion parameter**. This must not be
presented as discovering a mechanism.

**What the measurement can legitimately establish is OBSERVABILITY:** whether that gain is
recoverable from signals a gait laboratory can actually record — joint kinematics from motion
capture and an EMG envelope from surface electrodes — in the presence of everything else the
controller is doing, and whether the recovered quantity separates the two lesions that require
opposite treatments. In a patient the gain cannot be read off; only these observables exist.

A **positive** result means the clinically observable signals carry the information.
A **negative** result means they do not, even when the underlying difference is known to exist
by construction — which is a stronger negative than any obtained so far in this corpus.

---

## 3. Primary endpoint — fixed here, before measurement

Observables only. Motion-capture analogue: `ankle_angle_l`. Surface-EMG analogue:
`soleus_l.activation`. Nothing else enters the primary endpoint. Explicitly excluded, as at
r360 §1: `fiber_length`, `fiber_velocity`, `mtu_force`, `max_isometric_force`, and every
controller parameter.

Let `v(t)` = dorsiflexion angular velocity of the left ankle = the time derivative of
`ankle_angle_l`, signed so that **positive means dorsiflexion** (plantarflexor lengthening),
computed by `numpy.gradient` on the 100 Hz samples.

Let `x(t) = max(0, v(t − τ))` with the neural delay **τ = 0.020 s** (2 samples at 100 Hz),
fixed now and not tunable after any value is seen. Negative velocities are clipped to zero
because a stretch reflex responds to lengthening only.

**`BETA_stretch`** = the ordinary-least-squares slope of `soleus_l.activation(t)` on `x(t)`,
fitted over the **stance** samples of all admissible cycles of that cell pooled together.
Stance is `leg0_l.grf_norm_y > 0.05`, the same threshold `sto_utils.heel_strikes` uses. One
scalar per cell, in units of activation per rad/s.

**Predicted direction, declared before measurement:**

> **SPASTIC HIGH, DORSIFLEXOR-WEAK LOW.**

A separation in the opposite direction is a **failed prediction** and is reported as one.

---

## 4. Arms, gate, window — carried unchanged from r362 §2

**SPASTIC:** `R289KV00625`, `R289KV0125` (12 cells).
**DORSIFLEXOR-WEAK:** `R151W`, `R169W090`, `R169W095`, `R174W870`, `R174W892`, `R174W915`
(36 cells).

`R293DFs*` is not admitted; `R291KV*` is not added. Gate G unchanged: `t_end` ≥ 9.73 s and ≥ 5
complete cycles inside [1.00, 9.73] s, last cycle in window dropped.

Both arms are expected at `t_end` = 20.00 s, so the r360 §4 duration-invariance test is
degenerate here for the same reason recorded at r362 §4: with no duration variation the
duration confound cannot act, and READING U is primary by that fact. This is written down now
so it cannot be presented later as a discovery.

---

## 5. Separation criterion

Disjointness of the two arms' ranges on `BETA_stretch`, plus an exhaustive seed-level
permutation floor over C(48, 12), reported as a floor and never as a p-value. Gap is the
positive one of `min(weak) − max(spastic)` or `min(spastic) − max(weak)`; if neither is
positive the verdict is **OVERLAP**.

---

## 6. Secondaries — deposited, never promoted

`BETA_stretch` computed on `gastroc_l.activation`; on `tib_ant_l.activation` (expected near
zero, as a negative control); the regression `R²` for each; the same slope fitted over
**swing** rather than stance, as a contrast; and the mean `ankle_l.torque` over stance.

**None may become the primary endpoint under any outcome.**

---

## 7. Uninformative

Fewer than **5** Gate-G cells in either arm; or a primary regression with fewer than 30 pooled
stance samples in any admissible cell. No substitute endpoint, no changed τ, no changed
stance threshold, no pooling of the two weakness lesions, no promotion of a secondary. If this
fails it is recorded as a failure and this registration is not amended.

---

## 8. Declared limitations

r360 §8 applies unchanged: simulation `activation` is a clean 0–1 signal, and a separation
here does not establish that it survives at surface-EMG noise levels.

Additionally, and specific to this endpoint: **OLS on pooled stance samples treats successive
100 Hz samples as independent when they are not.** The slope estimate is used only as a
descriptive per-cell statistic, and all inference is by the seed-level permutation of §5,
which does not rest on that assumption. No standard error, confidence interval or p-value
computed from the regression may be reported.

---

## 9. Clinical translation, if it separates

`BETA_stretch` is estimable in a gait laboratory from motion capture plus surface EMG, without
a nerve block. If it separates, the claim available is that **the information needed to choose
between botulinum toxin and an AFO is present in a standard instrumented gait analysis**,
conditional on §8's untested noise step. Nothing stronger.
