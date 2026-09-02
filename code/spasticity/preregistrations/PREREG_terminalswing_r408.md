# PREREG — Terminal-swing knee extension deficit as the mechanism (r408)

**Registered:** 2026-08-26, before any of the confirmatory cells named in §4 has been measured
on this endpoint.

---

## 1. Provenance — this hypothesis was found by looking, and that is why it must be re-tested

Three earlier mechanism hypotheses were falsified by this corpus's own data:

| # | hypothesis | killed by |
|---|---|---|
| 1 | the |v| component of the reflex is uncancellable and carries the signature | `BETA2CONTROL_r388.json`: the matched control sits BETWEEN the arms, and r387 §5's registered rule then forbids the claim |
| 2 | the signature is carried by gastrocnemius because it spans the knee, tested at initial contact | `MECHANISM_RESULT_r407` / direct readout: soleus-only produced 70% of the knee displacement at KV 0.050, against a registered ceiling of 40% |
| 3 | the spastic limb's shank is decelerated before contact | measured shank angular velocity: control 66.0, weak 93.6, spastic 83.3–99.7 — no ordering |

The present hypothesis was then obtained by **plotting the knee trajectory across the whole
gait cycle and finding where the arms diverge**, rather than by proposing a cause. That is an
exploratory procedure and **nothing measured in the course of finding it can serve as its test.**

**What the exploration found** (100-point cycle averages, CONTROL n=6, WEAK n=6, SPAS KV 0.110
n=4):

- The spastic knee is **less** flexed than control through mid-swing (−43.3° vs −56.0° at 65%
  of cycle) and **more** flexed from 80% onward, reaching −13.2° at contact against −7.9°.
  **The signature is a failure to extend in terminal swing, not a general increase in flexion.**
- Over the last 15% of the cycle: knee extension moment 5.67 (spastic) against 8.17 (control)
  and 8.36 (weak); `gastroc_l` activation 0.0585 against 0.0471 and 0.0417; `soleus_l`
  activation 0.0416 against 0.0473 and 0.0412.

---

## 2. The mechanism, stated so it can fail

> **In terminal swing the spastic plantarflexor reflex keeps gastrocnemius active; because
> gastrocnemius spans the knee, that activity opposes knee extension; the knee therefore
> arrives at initial contact incompletely extended. Soleus, which does not span the knee, shows
> no corresponding terminal-swing difference.**

Every link is separately measurable, and the soleus arm is the negative control that
distinguishes this from a generic plantarflexor effect.

---

## 3. Definitions, fixed here

Cycle from left heel strike to left heel strike, corpus convention: SETTLE 1.00 s, T1 9.73 s,
cycles wholly inside the window, last kept cycle dropped, ≥ 5 required, stance =
`leg0_l.grf_norm_y > 0.05`.

**TERMINAL SWING = the last 15% of the gait cycle**, fixed now and not tunable.

- **`KTQ_tsw`** = mean `knee_l.torque` over terminal-swing samples of the admissible cycles.
- **`GAS_tsw`**, **`SOL_tsw`** = mean `gastroc_l` / `soleus_l` activation over the same samples.
- **`KNEE_ic`** = `knee_angle_l` at heel strike, per-cycle mean, degrees.

---

## 4. Confirmatory material — none of it has been measured on these endpoints

The exploration used CONTROL `R151C`, WEAK `R151W` and SPAS `R396SPg110`. **Those three arms
are spent** and may appear only as the exploratory record.

**Confirmation uses the KV ladder rungs not involved in the exploration**, all already
simulated and all Gate-G passing on the kinematic endpoint:

- **SPASTIC**: `R393SPg070` (KV 0.070, 6 cells) and `R393SPg100` (KV 0.100, 4 cells).
- **WEAKNESS**: `R169W090`, `R169W095`, `R174W870`, `R174W892`, `R174W915` — the five
  dorsiflexor-weakness families other than `R151W`.

`KTQ_tsw`, `GAS_tsw` and `SOL_tsw` have never been computed on any of these.

---

## 5. Registered predictions

**P1 — TORQUE.** `KTQ_tsw` is **lower** in the spastic rungs than in the weakness arm, and the
two are **disjoint** at KV 0.100.

**P2 — THE MEDIATOR.** `GAS_tsw` is **higher** in the spastic rungs than in the weakness arm,
and disjoint at KV 0.100.

**P3 — THE NEGATIVE CONTROL, and the one that makes this a mechanism rather than a
correlation.** `SOL_tsw` **overlaps** between the spastic and weakness arms at KV 0.100.
**If soleus separates as strongly as gastrocnemius, the knee-spanning explanation fails** and
what remains is a generic plantarflexor effect. That outcome is to be reported as a failure of
this registration, not reinterpreted.

**P4 — DOSE.** `GAS_tsw` is non-decreasing and `KTQ_tsw` non-increasing from KV 0.070 to 0.100.

**P5 — ORDER.** Within the spastic arm, across all Gate-G cells pooled, `KNEE_ic` is more
flexed in cells with lower `KTQ_tsw`. Reported as Spearman ρ; a positive ρ (less torque, less
flexion) contradicts the chain.

---

## 6. What this cannot establish

1. **Correlation along a mediation chain is not proof of mediation.** Three quantities moving
   together is consistent with the stated causal path and does not exclude a common cause —
   in particular, the controller is re-optimised per lesion cell, so all three could be joint
   consequences of the re-optimisation rather than a chain.
2. The soleus negative control is the strongest available evidence for the knee-spanning step,
   but soleus and gastrocnemius differ in more than articulation — moment arm, fibre length,
   maximum force and their optimised baseline gains all differ.
3. r407's direct decomposition — lesioning one muscle at a time — is the experiment that would
   settle it. It could not be run: SOL-only and GAS-only cells did not survive Gate G above
   KV 0.050. **This registration does not replace that experiment and does not claim to.**
4. Nothing here speaks to patients, to EMG noise, or to any model but this one.

---

## 7. Uninformative and prohibitions

A rung with fewer than 4 Gate-G cells is UNINFORMATIVE and reported, not dropped. No changed
terminal-swing window, no substitute muscle, no added arm, no promotion of a secondary. If the
predictions fail they are recorded as failures and this registration is not amended.

⚠ The batch null applies: `KNEE_MDC_BATCHNULL_r399.json` measured 26.7% separation between two
same-mechanism weakness families on the knee endpoint, and the discriminating feature there was
**magnitude, not disjointness** — no same-mechanism pair separated by more than 0.5697°.
Verdicts here are read against that, not against the permutation floor.
