# PREREG — Soleus spasticity slackens gastrocnemius and protects the knee (r418)

**Registered:** 2026-08-26, before any cell named in §4 exists on disk. Every confirmatory cell in
this registration is created AFTER this file is hashed.

---

## 1. Provenance — found by looking, and named as such

Two probes, built for other purposes, point the same way:

| probe | machinery | observation |
|---|---|---|
| `MECHANISM_RESULT_r407.json` | re-optimised controller | gastroc-only survives Gate G **0/6** at every rung and soleus-only 3/6 then 0/6, while **BOTH survives 6/6** at KV 0.050, 0.070, 0.090 and 0.110 |
| `FROZEN_MECHANISM_r410.json` | frozen controller | gastroc-only knee-at-HS **−18.843°**; BOTH **−7.911°**, within 0.06° of unlesioned **−7.850°** |

Adding soleus spasticity on top of gastrocnemius spasticity makes the system **more** stable and
returns the knee to its unlesioned value. Both arms of `R410BOTH` were verified to carry a
`MuscleReflex` — `soleus` and `gastroc`, both `KV = 0.050`, `delay = 0.020`, `allow_neg_V = 0` — so
the label is not a staging error.

**Neither observation may serve as this registration's test.** `FROZEN_MECHANISM_r410` is in any
case retired by `CORRECTION_r416` / `SELF_CORRECTION_r417` and carries no claim.

## 2. The mechanism, stated so it can fail

> **Gastrocnemius is biarticular. Soleus spasticity plantarflexes the ankle, which shortens
> gastrocnemius at its distal end. A shorter gastrocnemius is stretched less during swing, so its
> velocity-dependent reflex produces less drive; because gastrocnemius spans the knee, less drive
> means less opposition to knee extension. Soleus spasticity is therefore partially PROTECTIVE of
> the knee.**

This inverts the clinical intuition that more plantarflexor spasticity is worse for the knee.

## 3. The design, and why it is immune to the confound that killed r410

`CORRECTION_r416` retired the frozen probe partly because its arms differed in survival duration
and could not be matched. **This registration removes that confound by construction.**

- **Gastrocnemius KV is FIXED at 0.050 in every cell.** Only soleus KV varies.
- **PRIMARY ENDPOINT is measured in the FIRST SWING PHASE, inside the first 2.0 s**, which every
  arm reaches — the earliest arm in r410 survived 3.27 s. The primary endpoint therefore cannot
  depend on how long a cell survives, because it is read before any cell falls.
- The controller is FROZEN: the `.par` is the optimised unlesioned `R151C` controller for that
  seed, replayed with `sconecmd -e` and never re-optimised. No optimiser can compensate.

**Ladder:** soleus KV ∈ {0.000, 0.0125, 0.025, 0.050, 0.075, 0.100} × seeds 101–106 = **36 cells**.
The 0.000 rung is gastroc-only and is the reference. Gastroc KV = 0.050 throughout.

**Definitions, fixed here.** First swing = from the first left toe-off after t = 0.5 s to the next
left heel strike, stance = `leg0_l.grf_norm_y > 0.05`, unchanged from the corpus.

- **`GASLEN`** = mean `gastroc_l` muscle–tendon length over first-swing samples, metres.
- **`GASSTRETCH`** = peak-to-trough range of `gastroc_l` length over first swing, metres.
- **`GASDRIVE`** = mean `gastroc_l` activation over first swing.
- **`KNEE_sw`** = minimum `knee_angle_l` over first swing, degrees (most flexed).
- **`KNEE_ic`** = `knee_angle_l` at the heel strike ending first swing, degrees. SECONDARY.
- **`t_end`** = simulation end time. Reported for every cell as the confound check.

## 4. Confirmatory material — it does not exist yet

None of the 36 cells exists at registration time. They are built by copying the `R410*_s{seed}`
staging directory, editing only the soleus `KV` value in `config.scone`, and replaying the same
`FROZEN.par`. The frozen controllers are the six already on disk and are NOT re-optimised, so no
new optimisation and no new search is involved.

`GASLEN`, `GASSTRETCH`, `GASDRIVE` and `KNEE_sw` have never been computed on any cell in this
project, at any round.

## 5. Registered predictions

**P1 — SHORTENING.** `GASLEN` decreases monotonically in the rung means as soleus KV rises from
0.000 to 0.100. A non-monotonic or increasing sequence falsifies the first link.

**P2 — LESS STRETCH.** `GASSTRETCH` at soleus KV 0.100 is **lower** than at 0.000, and the two
rungs' cell ranges are **disjoint**.

**P3 — LESS DRIVE.** `GASDRIVE` at soleus KV 0.100 is **lower** than at 0.000, disjoint.

**P4 — THE KNEE, and the prediction that makes this protective rather than merely mechanical.**
`KNEE_sw` is **less flexed** (less negative) at soleus KV 0.100 than at 0.000, disjoint.
**If the knee becomes MORE flexed as soleus spasticity rises, the protective claim fails** and what
remains is an ordinary additive plantarflexor effect. That is to be reported as a failure.

**P5 — ORDER.** Across all 36 cells, `KNEE_sw` correlates with `GASLEN` at Spearman ρ ≤ −0.5, i.e.
a shorter gastrocnemius goes with a less flexed knee. A ρ near zero means the length change and the
knee change are unrelated even if both occur, and the chain fails.

## 6. The duration control, registered in advance and not optional

For every prediction the within-rung and pooled relationship between `t_end` and the endpoint is
computed by the r417 procedure: per-rung slope, rung-centred pooled slope, Pearson r. **If the
rung-centred pooled slope propagated across the observed between-rung `t_end` span accounts for
more than 50% of a reported effect, that prediction is declared CONFOUNDED and not counted as
holding**, regardless of disjointness. This is the test that retired `FROZEN_MECHANISM_r410`; it
is registered here before the data exist so it cannot be applied selectively.

## 7. What this cannot establish

1. A frozen controller is not a patient. Removing re-optimisation isolates the mechanical
   consequence and simultaneously removes the compensation a nervous system would supply.
2. Every lesioned cell here fails corpus Gate G. **These endpoints are first-swing quantities and
   are NOT the corpus endpoint**; no number from this registration may be pooled with, compared to,
   or substituted for a Gate-G corpus result, and none of it bears on the 6.3919° headline.
3. Six frozen controllers from one control optimisation are not six independent nervous systems.
4. Soleus and gastrocnemius differ in moment arm, fibre length and maximum force as well as in
   articulation, so a length effect is not proof that articulation is what matters.

## 8. Uninformative and prohibitions

A rung with fewer than 4 cells producing a `.sto` is UNINFORMATIVE and is reported, not dropped.
No changed swing window, no substitute muscle, no added rung after seeing a value, no re-fitting of
the ρ ≤ −0.5 threshold. If the predictions fail they are recorded as failures and this registration
is not amended. If an outcome occurs that §5 has no category for — the defect that spoiled r387 §5
and r408 §5 — it is recorded as a REGISTRATION DESIGN DEFECT and the prediction is scored failed as
written.
