# PREREG — Can the four kinematic endpoints discriminate the clinical pair? (r378)

**Registered:** 2026-08-18, before any of the four kinematic endpoints was computed against the
dorsiflexor-weakness arm.

---

## 1. Why this test exists, and that it is designed to refute our own claim

`EMGVSKIN_r377.json` refuted r376's hypothesis. Against the **control** arm:

| rung | soleus act. | gastroc act. | knee at HS | min ankle | ankle ROM | mean stance ankle |
|---|---|---|---|---|---|---|
| KV 0.00625 | overlap | **separated** | overlap | overlap | overlap | **separated** |
| KV 0.0125 | overlap | **separated** | overlap | **separated** | overlap | **separated** |
| KV 0.035 | **separated** | **separated** | **separated** | **separated** | overlap | **separated** |

`KV_kin` = **0.00625**, tying the best activation channel and beating the pre-registered soleus
endpoint (`KV_act` = 0.035). Activation does **not** detect earlier than kinematics.

The surviving argument for an activation endpoint is that the clinical question is not
*detection* but *discrimination*: `MATCHED20_ENDPOINT_r298.json`
(`/r292_READING_C_clinical_pair/RUNG` = `"4 OVERLAP"`) reports the clinical pair overlapping on
its kinematic channels, while `DOSELADDER_r371.json` reports stance soleus activation
separating the ladder from the dorsiflexor-weakness arm at KV ≥ 0.035.

**But `mean_ankle_stance_deg` was not among the channels r298 tested.** If that endpoint
discriminates the clinical pair, then no activation measurement is required for the clinical
decision and the paper's central claim fails.

**This registration exists to find that out. A result that refutes our own position is the
expected and acceptable outcome and will be reported as the headline if it occurs.**

---

## 2. Arms, gate, conventions — identical to r370 §3 and r376 §3

**Ladder:** `R289KV00625` (KV 0.00625), `R289KV0125` (0.0125), `R291KV0035` (0.035),
`R291KV0070` (0.070), six seeds each.
**Dorsiflexor-weakness arm:** `R151W`, `R169W090`, `R169W095`, `R174W870`, `R174W892`,
`R174W915`, 36 cells — the r298/r362 arm, unchanged.

Both sit at `min_velocity` = 1.0, so unlike r376 **this comparison is WITHIN-SCENARIO.**

**Gate G unchanged:** `t_end` ≥ 9.73 s, ≥ 5 cycles inside [1.00, 9.73] s, last cycle in window
dropped, stance = `leg0_l.grf_norm_y > 0.05`. `R291KV0070` is expected to contribute nothing and
is reported as UNINFORMATIVE, not dropped (r370 §8).

---

## 3. Endpoints — the same four, unchanged from r376 §4, no additions

1. `knee_angle_l` at left heel strike, per-cycle mean.
2. minimum `ankle_angle_l` over the cycle, per-cycle mean.
3. `ankle_angle_l` range of motion over the cycle, per-cycle mean.
4. mean `ankle_angle_l` over stance.

Reported alongside for continuity, not as primary: `soleus_l` and `gastroc_l` stance activation,
whose verdicts against this same arm are already deposited at `DOSELADDER_r371.json`.

**No endpoint may be added, substituted or dropped after seeing a value.** Multiplicity is four.

---

## 4. The registered predictions

**Prediction A (the one that matters).** No kinematic endpoint separates the ladder from the
dorsiflexor-weakness arm at any rung where stance soleus activation does not — i.e.
`KV_kin_pair` ≥ `KV_act_pair` = 0.035.

**Prediction B.** `mean_ankle_stance_deg`, which separated from control at the smallest rung,
does **not** separate the clinical pair at KV 0.00625.

**If either prediction fails, the claim that an activation measurement is necessary for the
clinical decision is refuted, and that is the result.** No reinterpretation is permitted: a
kinematic endpoint separating the pair at or below KV 0.035 means motion capture suffices.

---

## 5. Criterion

Per endpoint and rung: disjointness of the rung's six seed means against the dorsiflexor-weakness
arm's six seed means, with an exhaustive permutation floor over C(12, 6) = 924, reported as a
floor. Gap is the positive one of `min(W) − max(S)` or `min(S) − max(W)`; otherwise **OVERLAP**.

`KV_kin_pair` = the smallest rung at which **any** of the four separates — again deliberately
generous to kinematics, declared here.

---

## 6. Uninformative

Fewer than 4 Gate-G seeds at a rung: that rung is uninformative, reported not dropped. If no
endpoint separates at any rung, the comparison is UNINFORMATIVE and `KV_kin_pair` is undefined.

No substitute endpoint, no added channel, no pooling of rungs, no interpolation. If this fails
it is recorded as a failure and this registration is not amended.

---

## 7. Declared limitations

1. Six seeds per rung against six weakness seed means caps the floor at 1/924.
2. Four kinematic endpoints are not the whole of kinematics; a negative result means *these
   four, at these rungs*.
3. The ladder's three measurable rungs give coarse resolution; no interpolated threshold.
4. Nothing here speaks to surface-EMG noise or to marker-based motion-capture error. In
   particular, **if a kinematic endpoint does separate, its gap must still be read against the
   3.8–11.5° clinical MDC**, which applies to kinematic endpoints and not to activation.
