# PREREG — The rectifier fingerprint: an uncompensatable component (r382)

**Registered:** 2026-08-18, before any |v| regression coefficient was computed on any cell.

---

## 1. The derivation, which is the whole point of this registration

Read from `config.scone` on `R291KV0035_s101`, verified on disk:

```
ReflexController { name = SpasticL
    MuscleReflex { target = soleus   delay = 0.020  KV = 0.035  allow_neg_V = 0 }
    MuscleReflex { target = gastroc  delay = 0.020  KV = 0.035  allow_neg_V = 0 } }
```

Every other velocity feedback term in the same controller carries `allow_neg_V = 1`. **The
spastic lesion is the only half-wave-rectified term in the model.** The weakness lesion is a
pure linear scaling of `max_isometric_force` on `tib_ant_l` and introduces no nonlinearity at
all.

`DYNAMICS_LIMITATION_r365.json` records that re-optimisation cancels
**0.8570823499731588** of the added reflex drive. Re-optimisation adjusts **gains**. Gains are
linear operators. Decompose the added term:

> **max(0, v) = v/2 + |v|/2**

The first half is a plain linear velocity feedback and **can** be cancelled by an opposing
linear velocity gain, which the controller has. The second half is an absolute value.
**No linear combination of length, force and signed-velocity feedbacks can reproduce or cancel
|v|.** It is structurally uncancellable by the compensation mechanism this corpus has measured.

**This explains every failure so far.** Every endpoint tested — mean angle, ROM, peak angle,
mean activation, peak hip flexion — is an **amplitude**, and amplitude is precisely what a gain
adjustment can suppress. `KINPAIR_r379.json` and `COMPENSATION_r381.json` show them all landing
at 0.22–1.21°, against an MDC of 3.8–11.5°.

It also explains why `REFLEXGAIN_r366.json` returned OVERLAP with slopes of the **wrong sign**:
that registration regressed activation on `max(0, v)` as a *single* regressor, so the
cancellable half and the uncancellable half were pooled into one coefficient, and the pooled
coefficient was dominated by force-feedback timing.

**Separating them is the experiment.**

---

## 2. Primary endpoint

Observables only, as at r364 §3: joint kinematics and an EMG-analogue. Nothing muscle-internal.

Let `a(t)` = `ankle_angle_l` in radians, and `v(t) = d a/dt`, signed positive for
**dorsiflexion** (soleus lengthening) — the convention verified against stance kinematics and
recorded at `DYNAMICS_LIMITATION_r365.json`. Apply the model's own reflex delay: use
`v(t − 0.020 s)`, i.e. a 2-sample lag at 100 Hz, exactly as r364 §3 fixed it.

Fit, by ordinary least squares over **all samples of the admissible cycles** (whole cycle, both
phases pooled — the rectifier acts wherever lengthening occurs, so restricting to a phase would
be a choice made for us by convenience):

> **`act_soleus_l(t) = β₁ · v(t−τ) + β₂ · |v(t−τ)| + c`**

**`BETA_abs` = β₂**, in activation per (rad/s). One scalar per cell.
**`RATIO_abs` = β₂ / (|β₁| + |β₂|)**, dimensionless, in [0, 1] — the scale-free form. Reported
alongside; **β₂ is the primary**, `RATIO_abs` is a secondary and may not replace it.

---

## 3. Registered predictions — all three fixed before measurement

**P1 — PRESENCE.** `BETA_abs` is **positive** in every spastic rung and **not distinguishable
from the control arm** in the dorsiflexor-weakness arm. A negative `BETA_abs` in the spastic arm
is a failed prediction.

**P2 — MONOTONICITY.** Arm-mean `BETA_abs` is **non-decreasing** in KV across 0.00625 → 0.0125 →
0.035. Any inversion between adjacent rungs is a failed prediction.

**P3 — THE RISKY ONE, and the reason this registration is worth running.** `BETA_abs` separates
the spastic arm from the dorsiflexor-weakness arm **at KV 0.00625 and KV 0.0125**, the two rungs
at which every amplitude endpoint tested so far has OVERLAPPED
(`DOSELADDER_r371.json`, `KINPAIR_r379.json`, `COMPENSATION_r381.json`).

**If P3 fails, the first-principles argument of §1 is not rescued by anything else in this
registration, and the honest conclusion is that even the mathematically uncancellable component
lies below the noise floor of this model.** That conclusion is to be reported with the same
prominence as a success.

---

## 4. A confound that must be measured, not assumed away

Muscle activation dynamics are themselves nonlinear — activation and deactivation time constants
differ — so a nonzero `BETA_abs` can arise **without any reflex lesion**. The **control arm is
therefore mandatory**, not optional: `R203V080C`, `R203V105C`, `R203V130C`, 18 cells. It defines
the `BETA_abs` a healthy re-optimised controller produces, and every spastic value is read
against it.

⚠ The control arm is at `min_velocity` 0.80/1.05/1.30 while ladder and weakness arms are at 1.0,
so **any statement involving the control arm is BETWEEN-SCENARIO**. The primary spastic-versus-
weakness comparison is within-scenario and carries no such label.

---

## 5. Arms, gate, conventions — carried unaltered from r378 §2

**Spastic ladder:** `R289KV00625`, `R289KV0125`, `R291KV0035`, `R291KV0070`, six seeds each.
**Dorsiflexor weakness:** `R151W`, `R169W090`, `R169W095`, `R174W870`, `R174W892`, `R174W915`.
**Control:** `R203V080C`, `R203V105C`, `R203V130C`.

Gate G unchanged: `t_end` ≥ 9.73 s, ≥ 5 cycles inside [1.00, 9.73] s, last cycle in window
dropped. `R291KV0070` is expected to contribute nothing and is reported UNINFORMATIVE, not
dropped.

---

## 6. Secondaries — deposited, never promoted

`BETA_abs` computed on `gastroc_l.activation` (biarticular, so its length depends on knee as
well as ankle and the ankle-only regressor is mis-specified for it — reported for completeness
and explicitly not interpretable as a clean fingerprint); on `tib_ant_l.activation` as a
negative control; `RATIO_abs` for each; β₁ for each; the regression R²; and `BETA_abs` refitted
on stance samples only and on swing samples only.

**None may become the primary under any outcome.**

---

## 7. Criterion

Disjointness of the rung's six seed means against the weakness arm's six seed means, exhaustive
permutation floor over C(12, 6) = 924, reported as a floor and never as a p-value.

---

## 8. Uninformative

Fewer than 4 Gate-G seeds at a rung: uninformative, reported not dropped. Fewer than 30 pooled
samples in a cell's regression: that cell is dropped and named.

No substitute endpoint, no changed τ, no phase restriction of the primary, no promotion of a
secondary, no pooling of rungs. If this fails it is recorded as a failure and this registration
is not amended.

---

## 9. Declared limitations

1. `activation` is a clean simulator signal; nothing here speaks to surface-EMG noise. **This
   matters more than usual for this endpoint**: β₂ is a second-order shape feature, and shape
   features are ordinarily more noise-sensitive than amplitudes. A positive result in
   simulation is therefore weaker evidence of clinical usability than an amplitude result of
   the same effect size would be, and must be stated that way.
2. OLS on 100 Hz samples treats successive samples as independent when they are not. β₂ is a
   descriptive per-cell statistic; **no SE, CI or p from the regression may be reported.** All
   inference is the seed-level permutation of §7.
3. `|v|` and `v` are correlated over a gait cycle; the design matrix is not orthogonal, and the
   split between β₁ and β₂ is therefore not unique in the presence of noise. The condition
   number of the design matrix is to be deposited per cell, and if it is large the split must be
   reported as unstable.
4. Soleus is uniarticular so ankle velocity is a good proxy for its lengthening velocity;
   gastrocnemius is not, per §6.
5. Six seeds per rung caps the permutation floor at 1/924.
