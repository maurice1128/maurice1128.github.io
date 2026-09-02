# PREREG_3d_injection_r145.md — P3D-2, the KV titration, registered before any run

**Round 145, 2026-08-09. NOT RUN. No titration cell exists at the time of hashing.**
*Where this document and any script disagree, THIS DOCUMENT DECIDES.*

## 0. What is established, verified from the files rather than from the report

| | measured this round |
|---|---|
| baseline `bench_D20/230119.H1922v7b3.D20.par.sto` | **12.16 s**, 1,217 rows, 958 columns |
| injected `bench_D20_spasL/…par.sto` | **3.87 s**, 388 rows, 962 columns |
| configs | baseline **8,657 B** (CRLF), injected **8,700 B** (LF) |
| content difference | ⛔ **exactly one hunk: the injected `ConditionalController`. Nothing else.** |

⚠ **The coordinator's account said the baseline config was 8,286 B. It is 8,657 B on disk.** *Both are
right about different things: the baseline is CRLF over 371 lines, and 8,657 − 371 = **8,286**, the
LF-normalised size. **The two configs differ in line endings throughout**, so they are identical in
content and different in every byte — recorded because it defeats any byte-level comparison.*

**The injected block, read from the file:** `states = "EarlyStance LateStance Liftoff Swing Landing"`,
**`legs = left`**, `ReflexController { name = SpasticL, MuscleReflex soleus + gastroc, delay = 0.020,
KV = 0.050, allow_neg_V = 0 }`.

⛔ **Established: the 2D unilateral scoping property `legs = left` PARSES, LOADS, and has a mechanical
effect in the 19-DoF 3D model.**

⛔ **NOT established: that the effect is unilateral.** *The injected run lasts **3.87 s** against the
baseline's **12.16 s**. Everything after a fall moves both limbs, so "leaked to the right" and "the
model is falling" are not separable in that record.* ⚠ **And the log route is closed: SCONE does not
name controllers in its output; `SpasticL` appears zero times.**

## 1. The design

**Titrate KV downward. At each rung, one evaluation of `bench_D20_spasL` with KV changed in BOTH
`MuscleReflex` blocks (soleus and gastroc) and nothing else changed.**

**Ladder, fixed now: `0.050` (done) → `0.025` → `0.0125` → `0.00625` → `0.003125`.**
*Halving, five rungs. **Stop at the first rung that SURVIVES**; if none survives, the ladder is
exhausted and §4 applies.*

## 2. ⛔ "SURVIVES" — fixed before any rung is run

**A rung SURVIVES if and only if BOTH hold:**

1. **Simulated duration ≥ 9.73 s** — *80 % of the baseline's measured 12.16 s.*
2. **≥ 5 complete GRF-delimited gait cycles after `settle = 1.0 s`** — *the baseline yields 7.*

⚠ **The baseline itself terminates at 12.16 s against a `max_duration = 20` budget, so it is not a
20-second stable gait and the criterion is deliberately relative to it, not absolute.**

⚠ **Two clauses, because r141's own two-cycle criterion is too weak here:** *a limb-asymmetry
comparison needs a window, and G4's lesson is on the record — a two-cycle criterion can be satisfied by
a barely-viable gait whose feature is inflated by non-convergence.*

## 3. ⛔ "UNILATERAL" — fixed before any rung is run

**Measured over a COMMON window: `settle = 1.0 s` to the minimum of the two runs' durations.**
*Comparing over different windows is exactly what contaminated the first attempt.*

**For each metric m ∈ { soleus mean activation, ankle ROM }, per limb:**

> **Δ_L = | m_L(injected) − m_L(baseline) |**, **Δ_R = | m_R(injected) − m_R(baseline) |**

**A rung is UNILATERAL if and only if BOTH metrics satisfy `Δ_R / Δ_L ≤ 0.33`,** *and the direction is
correct — left soleus activation rises relative to right.*

⛔ **This threshold is not guaranteed to pass, and that is the point. Applied to the contaminated
KV = 0.050 record it gives soleus Δ_R/Δ_L = 0.0080 / 0.0348 = **0.23** (passes) and ankle ROM
6.93 / 10.28 = **0.67** (FAILS).** *So the criterion already discriminates on the data that exists, and
it was chosen for that reason rather than to be clearable.*

## 4. The registered outcomes

| outcome | what it means |
|---|---|
| **a rung SURVIVES and is UNILATERAL** | **the injection ports in practice.** *The KV that achieves it is reported, and if it is far below 0.050 that is a finding in its own right (§5)* |
| **a rung SURVIVES but is NOT unilateral at any surviving KV** | ⛔ **`legs = left` does not scope the effect in 3D.** The property is syntactically portable and semantically inert |
| **NO rung survives down to 0.003125** | ⛔ **the injection is PORTABLE IN SYNTAX AND USELESS IN PRACTICE**, and **3D closes on the same footing as slope, shape and slow: by measurement, not by preference** |

⚠ **All three are results. None is a failure of the probe.**

## 5. ⛔ The confound this probe exists to test, registered as such

**`KV = 0.050` was tuned for a 9-DoF planar model. Carrying it unchanged to a 19-DoF 3D model is
cross-operation borrowing of a numeric constant — the compression defect in numeric form.**

⛔ **The registered reading: if the surviving KV is far below 0.050, the value does NOT transfer, and
any 3D result obtained at 0.050 — including r141b's — is a result about an over-driven model rather
than about spasticity.** *Registered now so that a low surviving KV cannot later be presented as a
minor calibration detail.*

## 6. What is NOT changed, and what would need authorisation

- **`bench_D20/config.scone` is not touched.** *The baseline is the comparison and must not move.*
- **Only the two `KV = ` values change per rung.** *No other edit — not `delay`, not `allow_neg_V`, not
  `legs`, not `states`.*
- ⚠ **Each rung requires a SCONE evaluation, which is a launch.** ⛔ **Nothing is launched by this
  document. Authorisation to run the ladder is requested separately, and the thresholds above are
  fixed whether or not it is granted.**

## 7. What this document does not claim

⚠ **It does not predict which outcome occurs, and no rung is described as likely.**
⚠ **It does not revisit r141's P3D-1 PASS**, which established that the out-of-plane channel exists and
explicitly did not establish that the motion is realistic — *`pelvis_rotation` 27.29° and
`lumbar_rotation` 23.68° are both above normal, and that caveat stands.*
⚠ **It says nothing about discrimination.** *A portable injection is a precondition for asking, not
evidence for 3D.*
