# PREREG — Swing-phase plantarflexor activation as a clinical discriminator (r360)

**Registered:** 2026-08-18, before any value of the endpoint was computed.
**Status at registration:** the channels were confirmed to EXIST on disk (census only — column
names and per-cell presence). No endpoint value, no arm mean, no difference has been computed.

---

## 1. Why this endpoint, and why it is not the previous ones

Every measurement in this corpus so far has been **kinematic** — joint angles and their
ranges. Both lesions modelled here converge on the same kinematic outcome (equinus / foot
drop), because a joint angle is the doubly-integrated downstream of both a reflex excess and
a force deficit. That is a structural reason for the failures already recorded, not bad luck:

- `hip_flexion_LmR` separated only as a **fall signature** (§0c of `RESULTS_3d_r214.md`).
- At matched completion the clinical pair reads **OVERLAP** on both channels
  (`MATCHED20_ENDPOINT_r298.json`, `/r292_READING_P_anatomy_matched/gap` = 0.861753734019743).
- The one surviving separation, `knee_angle_LmR` at 2.0899552309869094°
  (`BANDFILL_ENDPOINT_r291.json`), is **below the MDC floor of 3.8–11.5°** for post-stroke
  ankle and is not the clinical pair.

This registration moves to the layer **upstream of the confluence**, and picks the specific
quantity that the existing clinical test proxies.

**The clinical decision this addresses.** Plantarflexor spasticity and dorsiflexor weakness
both produce foot drop in swing. Treatment is opposite — botulinum toxin versus AFO and
strengthening. The current discriminator is a **diagnostic nerve block**: silence the reflex,
and see whether the foot still drops. What the block tests is whether the plantarflexors are
*active* during swing.

- **Spasticity** — a velocity-dependent hyperactive stretch reflex — predicts plantarflexor
  activity **present** during swing, when those muscles should be quiescent.
- **Dorsiflexor weakness** predicts the plantarflexors **quiescent**; the foot falls passively
  because `tib_ant` cannot lift it.

**Clinical obtainability is a constraint, not an afterthought.** The primary endpoint is
restricted to quantities a gait laboratory can measure non-invasively. Muscle activation is
the simulation's analogue of a **surface EMG envelope**; `ankle_l.torque` is obtainable by
**inverse dynamics**. Explicitly EXCLUDED from the primary endpoint, because they are not
clinically obtainable and because reading them would approach reading the lesion parameter
back out: `mtu_force`, `fiber_length`, `max_isometric_force`, and any reflex-gain parameter.

---

## 2. Data

Existing `.sto` deposits only. **No new simulation is run for this registration.** Sampling is
100 Hz (Nyquist 50 Hz), which bounds every transient feature reported here.

**SPASTIC arm** (reflex `MuscleReflex` KV on soleus/gastroc, left):
`R289KV00625`, `R289KV0125`, `R291KV0035`, `R291KV0070` — seeds s101–s106 per family.

**DORSIFLEXOR-WEAK arm** (`max_isometric_force` scaling on `tib_ant_l`):
`R293DFs010`, `R293DFs030`, `R293DFs050` — seeds s101–s106 per family.

`R293DFs000` is **excluded**: the ×0.00 rung was ruled NOT ADMISSIBLE at r303
(`DFSEVERE_RESULT_r303.json`). It is not re-admitted here under any reading.

**Gate G, unchanged:** a cell is measured only if `t_end` ≥ **9.73 s** and it yields ≥ **5**
complete gait cycles in the window. A cell failing Gate G is not measured and is not
substituted.

**Measurement window:** [1.00, 9.73] s. Per-cycle means; **the last cycle is dropped**
(`hipgap_r220.py` convention, unchanged).

---

## 3. Primary endpoint — fixed here, before measurement

**`PF_swing`** = the per-cycle mean of `(soleus_l.activation + gastroc_l.activation) / 2`,
taken over samples in the **swing phase of the left leg**, then averaged across the admissible
cycles of that cell. One scalar per cell. Dimensionless, 0–1.

**Swing detection:** left leg is in swing when `leg0_l.grf_norm_y` < **0.05**. This threshold
is fixed now and may not be tuned after seeing any endpoint value. Cycles are delimited by
left heel strike (the upward crossing of that threshold).

**Predicted direction, declared before measurement:**

> **SPASTIC HIGH, DORSIFLEXOR-WEAK LOW.**

A separation in the **opposite** direction does not support the hypothesis and must be
reported as a **failed prediction**, not as a discovery.

---

## 4. The duration-invariance test — this decides which reading is primary

`CONFOUND_DURATION_r277.json` established that spastic cells fall (13.58–17.85 s) while
weakness cells complete (20.00 s), zero overlap, and that within the spastic arm
ρ(`hip_flexion_LmR`, `t_end`) = **+0.7143**. Any endpoint that scales with trial length
re-creates that artifact.

`PF_swing` is a **per-cycle** quantity over a **fixed** window, so it should be
duration-invariant by construction. **That is a hypothesis, not a licence.** It is tested:

> Compute Spearman ρ(`PF_swing`, `t_end`) **within each arm separately**.
> - If **|ρ| < 0.5 in both arms** → the endpoint is duration-invariant. **READING U**
>   (unmatched, all Gate-G cells) is the **PRIMARY** reading.
> - If **|ρ| ≥ 0.5 in either arm** → the endpoint is duration-contaminated. **READING U is
>   NOT ADMISSIBLE** and may not be reported as a result. Only **READING M** — restricted to
>   cells inside the duration band [13.58, 17.85] — may be read, and if fewer than **3** cells
>   per arm fall in that band the outcome is **UNINFORMATIVE**.

Both readings are computed and deposited either way. Which one is primary is decided by the
ρ test above and by nothing else.

---

## 5. Separation criterion

Disjointness of the two arms' ranges on `PF_swing`, plus an **exhaustive seed-level
permutation floor** over C(n_spastic + n_weak, n_spastic), reported as a floor and never as a
p-value. The gap is `min(weak) − max(spastic)` or `min(spastic) − max(weak)`, whichever is
positive; if neither is, the verdict is **OVERLAP**.

---

## 6. Secondary endpoints — deposited, never promoted

Computed and deposited in the same run. **None of these may become the primary endpoint under
any outcome**, and no result may be reported from them alone:

- `ankle_l.torque`, mean over swing (inverse-dynamics obtainable).
- `tib_ant_l.activation`, mean over swing.
- Co-contraction index over swing: `min(PF, tib_ant) / max(PF, tib_ant)`.
- The same four quantities over **stance**, for contrast.

---

## 7. What would make this UNINFORMATIVE

- Fewer than **5** Gate-G-passing cells in either arm under READING U.
- Fewer than **3** per arm in band under READING M when READING M is primary.
- Any need to change the swing threshold, the window, the cycle convention, or the arm
  membership after seeing a value.

**No substitute endpoint. No widened band. No pooling of the two weakness lesions. No
promotion of a secondary.** If this fails, it is recorded as a failure and the registration is
not amended.

---

## 8. Declared limitation, registered now rather than added later

Simulation `activation` is a clean 0–1 signal. Surface EMG carries noise, crosstalk from
neighbouring muscles, and electrode-placement variance. **A separation observed here does not
establish that the same separation survives at surface-EMG noise levels**, and this corpus
cannot test that. Any clinical claim arising from this endpoint must be stated as conditional
on that untested step. This limitation stands whatever the result.

---

## 9. Licence context

The Hyfydy licence expires **2026-08-27**. This registration deliberately requires **zero new
simulation** — every `.sto` it reads already exists on disk — so it is executable within that
window and its executability does not depend on the licence.
