# PREREG — Is β₂ detecting the spasticity or the weakness? (r387)

**Registered:** 2026-08-18, before any value of any endpoint has been computed on `R151C`.

---

## 1. Why this test is necessary, and why it is decisive

`RECTIFIER_r385.json` separated the clinical pair on `BETA_abs` — the |v| coefficient of
`act_soleus_l ~ β₁·v + β₂·|v| + c` — at **all three** measurable rungs, including KV 0.00625 and
KV 0.0125 where every amplitude endpoint in this corpus has OVERLAPPED. Gaps +0.002077,
+0.003076, +0.006436; monotone in KV; design-matrix condition number ≤ 3.

But `PREREG_rectifier_r382.md` §3's prediction **P1 failed**: `BETA_abs` is negative in every
arm, not positive. And the arm means sit like this:

| arm | BETA_abs mean |
|---|---|
| CONTROL `R203*C` (BETWEEN-SCENARIO) | −0.023513 |
| spastic KV 0.00625 | −0.023178 |
| spastic KV 0.0125 | −0.022174 |
| spastic KV 0.035 | −0.018927 |
| dorsiflexor weak | −0.025972 |

**At KV 0.00625 the spastic arm is indistinguishable from control, and it is the WEAKNESS arm
that is displaced.** If that holds, then the low-rung separation is `BETA_abs` detecting the
*dorsiflexor lesion*, not the *reflex lesion*, and the §1 derivation of r382 — that the |v|
component is the uncancellable residue of the spastic rectifier — is **not** what produced it.

That reading cannot be settled from `R203*C`, which sits at `min_velocity` 0.80/1.05/1.30 while
both lesion arms sit at 1.0. **A within-scenario control is required and one exists.**

---

## 2. The control arm, verified on disk before registration

`R151C`, six seeds. Verified by reading `config.scone` and the model file:

- `min_velocity = 1.0` — **the same as both lesion arms, so this comparison is WITHIN-SCENARIO.**
- **Zero** occurrences of `SpasticL`; no added reflex controller.
- Model file differs from `R151W`'s in **exactly one line** — line 388,
  `max_isometric_force` on `tib_ant_l`, **1759** in `R151C` against **1407.2** in `R151W`
  (×0.80). A `diff` of the two EOL-normalised files returns that one line and nothing else.
- `soleus_l` 3549 and `gastroc_l` 2241, both unaltered.

`R151C` is therefore the unlesioned matched control for `R151W`, and a legitimate common
reference for the ladder.

**No value of any endpoint has been computed on any `R151C` cell.** The prediction below is made
blind to it.

---

## 3. Endpoint

**Unchanged from `PREREG_rectifier_r382.md` §2**, carried verbatim: `BETA_abs` = the |v|
coefficient of `act_soleus_l(t) = β₁·v(t−τ) + β₂·|v(t−τ)| + c`, OLS over all samples of the
admissible cycles, whole cycle, v = ankle dorsiflexion angular velocity in rad/s positive for
dorsiflexion, τ = 0.020 s. Gate G unchanged.

This registration adds **no new endpoint**. It adds one arm and asks one question of it.

---

## 4. The registered prediction — binary and decisive

Where `R151C` falls settles which lesion `BETA_abs` responds to.

> **P-SPASTIC.** If `BETA_abs` is a spasticity signature, `R151C` sits **with the dorsiflexor-weak
> arm** (both lack a reflex lesion) and **apart from** the spastic rungs.
>
> **P-WEAK.** If `BETA_abs` is a weakness signature, `R151C` sits **with the spastic arm at low
> KV** and **apart from** the dorsiflexor-weak arm.

**Registered call, made before measurement:** the r385 pattern against the between-scenario
control points to **P-WEAK**, and that is what I predict. If P-SPASTIC obtains instead, the
between-scenario control was misleading and r382's mechanism claim survives.

A third outcome is possible and is registered now so it is not treated as a surprise:
**P-NEITHER**, in which `R151C` sits apart from both arms. That would mean `BETA_abs` responds
to *any* departure from the unlesioned optimum rather than to a specific lesion, and it would
make `BETA_abs` a non-specific abnormality detector, not a discriminator. Under P-NEITHER no
discrimination claim may be made from r385.

---

## 5. Criterion

Disjointness of `R151C`'s six seed means against (a) the dorsiflexor-weak arm's six seed means
and (b) each spastic rung's six seed means, exhaustive permutation floor over C(12, 6) = 924
in each case, reported as a floor and never as a p-value.

**Deciding rule, fixed now:** `R151C` "sits with" an arm when it **OVERLAPS** that arm and is
**disjoint** from the other. If it overlaps both, or is disjoint from both, the outcome is
P-NEITHER.

---

## 6. Secondaries — deposited, never promoted

`RATIO_abs`, β₁, R², the design-matrix condition number, and `BETA_abs` on `gastroc_l` and
`tib_ant_l`, for `R151C`. The `R203*C` between-scenario values are re-reported alongside for
comparison and remain labelled between-scenario.

---

## 7. Uninformative

Fewer than 4 Gate-G seeds in `R151C`. No substitute endpoint, no further arms, no re-fitting
with a different τ, no promotion of a secondary. If this fails it is recorded as a failure and
this registration is not amended.

---

## 8. Declared limitations

1. `activation` is a clean deterministic simulator signal. The timing audit for r386 established
   that **no `NoiseController` exists in any of these families** and that the replay producing
   each `.par.sto` is deterministic, so the only variation across seeds is where the optimiser
   landed. Nothing here speaks to surface-EMG noise, and a real recording would carry more
   variability than anything measured here.
2. Six seeds per arm caps the permutation floor at 1/924.
3. `R151C` is matched to `R151W` exactly, but the other five dorsiflexor-weak families differ
   from `R151W` in lesion magnitude; `R151C` is therefore an exact control for one sixth of that
   arm and an approximate one for the rest. The `R151C` vs `R151W`-only comparison is reported
   separately for that reason.
