# PREREG — Where the compensation went: proximal swing-phase signatures (r380)

**Registered:** 2026-08-18, before any proximal or swing-phase hip quantity was computed on any
cell of either arm.

---

## 1. The reasoning, from first principles rather than from the literature

Two facts already deposited generate this test:

- `DYNAMICS_LIMITATION_r365.json` → `/FINDING/4_why_the_endpoint_still_sees_nothing/a_the_added_drive_is_absorbed/fraction_cancelled` = **0.8570823499731588**. The controller cancels 86% of the imposed reflex lesion by re-tuning other reflexes.
- `KINPAIR_r379.json`: every kinematic separation of the clinical pair is **0.22–1.21°**, against a post-stroke ankle MDC of **3.8–11.5°**.

**Every endpoint tested so far has been at or immediately around the lesion — ankle angle, knee
angle, soleus, gastrocnemius, tibialis anterior.** But 86% of the lesion does not vanish; it is
absorbed by *something else*. That absorption is itself a motor output, and nothing in this
corpus has looked for it.

**The control-theoretic statement.** Spasticity is a change in a FEEDBACK LOOP GAIN; dorsiflexor
weakness is a change in PLANT (actuator) GAIN. A redundant controller compensates each by
redistributing effort, but it cannot redistribute them the *same* way, because the two deficits
are functionally different: a stiff, reflexively resisted ankle is a problem of *getting past*
the joint, while a foot that will not lift is a problem of *clearing the ground*.

**The clinical statement, which is older than any of this.** The textbook compensation for foot
drop is **steppage gait** — exaggerated hip and knee flexion in swing to lift the whole limb
over the un-dorsiflexed foot. It is described as characteristic of *weakness*, not of
spasticity, where the foot is held down by reflex resistance rather than failing to be lifted.

**Prediction, therefore, and it is directional and made before measurement:**

> **Peak left hip flexion during SWING is HIGHER in the dorsiflexor-weakness arm than in the
> spastic arm.**

This is a proximal, swing-phase, ipsilateral kinematic quantity. It has never been computed in
this corpus. Every prior hip endpoint here was `hip_flexion_LmR`, a left-minus-right **range of
motion asymmetry over the whole cycle** (`hipgap_r220.py` convention), which is a different
quantity and which §0c of `RESULTS_3d_r214.md` records as a fall signature.

---

## 2. Arms, gate, conventions — carried unaltered from r378 §2

**Spastic ladder:** `R289KV00625` (KV 0.00625), `R289KV0125` (0.0125), `R291KV0035` (0.035),
`R291KV0070` (0.070). Six seeds each.
**Dorsiflexor weakness:** `R151W`, `R169W090`, `R169W095`, `R174W870`, `R174W892`, `R174W915`,
36 cells.

Both at `min_velocity` = 1.0 → **WITHIN-SCENARIO**.

**Gate G unchanged:** `t_end` ≥ 9.73 s, ≥ 5 cycles inside [1.00, 9.73] s, last cycle in window
dropped, stance = `leg0_l.grf_norm_y > 0.05`, swing its complement. `R291KV0070` is expected to
contribute nothing and is reported as UNINFORMATIVE, not dropped (r370 §8).

---

## 3. Primary endpoint — one, fixed here

**`hip_swing_peak_L`** = the per-cycle maximum of `hip_flexion_l`, taken over the **swing**
samples of each admissible cycle, averaged across cycles. Degrees. One scalar per cell.

**Registered prediction: DORSIFLEXOR-WEAK HIGH, SPASTIC LOW.** A separation in the opposite
direction is a **failed prediction** and is reported as one.

**The clinical measurability gate applies and is stated in advance.** This is a kinematic
endpoint, so its gap must be read against a hip-specific minimal detectable change. The
3.8–11.5° figure in this corpus is for the post-stroke **ankle** and may not be transferred to
the hip; the correct hip MDC must be sourced separately, and **until it is, no claim of clinical
measurability may be made from this endpoint**, only a claim about the size of the simulated
difference. A gap below 3.8° will be treated as presumptively sub-threshold pending that source.

---

## 4. Secondaries — deposited, never promoted

Computed in the same run, none of which may become the primary under any outcome:

- `knee_swing_peak_L` — the knee half of the steppage pattern.
- Swing-phase mean activation of the left hip flexors, `iliopsoas_l` and `rectus_femoris_l`, and
  of `hamstrings_l` and `glut_max_l` — the muscular side of the same compensation.
- The contralateral versions of all of the above (`_r`), since compensation may cross sides.
- Stance-phase mean activation of every remaining muscle in the model, both sides, as a
  descriptive map of where the absorbed 86% went.

**The secondary list is broad on purpose and its multiplicity is declared here.** It is a
descriptive map, not a set of tests; no p-value, floor, or verdict may be attached to any
secondary, and no secondary may be reported as a discriminator.

---

## 5. Criterion for the primary

Disjointness of the spastic rung's six seed means against the dorsiflexor-weakness arm's six
seed means, per rung, with an exhaustive permutation floor over C(12, 6) = 924, reported as a
floor and never as a p-value. Gap is the positive one of `min(W) − max(S)` or `min(S) − max(W)`;
otherwise **OVERLAP**.

---

## 6. Uninformative

Fewer than 4 Gate-G seeds at a rung: that rung is uninformative, reported not dropped. If no
rung separates, the outcome is a clean negative and is reported as one.

No substitute endpoint, no promotion of a secondary, no added arm, no pooling of rungs. If this
fails it is recorded as a failure and this registration is not amended.

---

## 7. Declared limitations

1. Six seeds per rung caps the permutation floor at 1/924.
2. The hip MDC is not yet sourced (§3); measurability is therefore unresolved even if the gap
   is large.
3. The lesion here is `tib_ant_l` at ×0.87–×0.915 — a mild dorsiflexor deficit. Textbook
   steppage gait is described for severe foot drop. **A null result may mean the lesion is too
   mild to evoke the compensation, not that the compensation is absent**, and that reading must
   be given equal prominence.
4. This model has no cortical or volitional layer; steppage gait in patients may be partly a
   learned, volitional strategy that a reflex controller cannot produce. **If the prediction
   fails, this is the most likely reason and it must be stated**, not buried.
5. Between-arm comparison only; no control arm enters the primary.
