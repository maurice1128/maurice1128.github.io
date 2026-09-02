# PREREG — The lesion response is one-dimensional (r409)

**Registered:** 2026-08-26, before the confirmatory material in §4 has been measured on these
endpoints.

---

## 1. Why this registration exists: five mechanism hypotheses failed the same way

| # | hypothesis | outcome |
|---|---|---|
| 1 | the |v| component of the reflex is structurally uncancellable and carries the signature | `BETA2CONTROL_r388.json` — the matched control sits BETWEEN the arms; r387 §5 then forbids the claim |
| 2 | gastrocnemius carries the knee signature because it spans the knee, measured at initial contact | soleus-only produced 70% of the knee displacement at KV 0.050, against a registered ceiling of 40% |
| 3 | the spastic limb's shank is decelerated before contact | shank angular velocity: control 66.0, weak 93.6, spastic 83.3–99.7 — no ordering |
| 4 | terminal-swing knee extension deficit mediated by gastrocnemius, with soleus as negative control | `KTQ` and `GAS` separated as predicted, but `SOL` separated too — r408 §5 P3 failed as written |
| 5 | compensation is ankle-targeted, so the biarticular side-effect leaks to the knee | terminal-swing deviation from control was LARGER at the ankle (0.360) than at the knee (0.272), and largest at the hip (0.667) |

Each assumed a separable causal link. An exploratory decomposition then suggested why every one
failed. Pooling 63 Gate-G cells across control, five dorsiflexor-weakness families and five
spastic rungs, and regressing knee angle at initial contact on nine terminal-swing quantities:

- every predictor correlates strongly on its own — |r| from 0.56 to 0.97;
- the joint fit reaches **R² = 0.976**;
- and **no predictor carries unique variance**: dropping any one changes R² by at most 0.0035.

**That exploration is not this registration's evidence.** It was found by looking, and what
follows must be tested on material it did not touch.

---

## 2. The claim

> **The lesion's effect is effectively one-dimensional. Mechanical and neural variables at
> terminal swing move together along a single coordinated direction, so no single muscle,
> joint or torque can be assigned independent responsibility for the knee signature. The
> failure to isolate a mechanism is a property of a re-optimised controller, not a gap in the
> search.**

If true, it also states a limit: **causal decomposition of this kind is not available in a
system whose controller is re-optimised per lesion**, because the optimiser returns a new
coordinated solution rather than a local modification.

---

## 3. Variables and definitions, fixed here

Corpus convention unchanged: SETTLE 1.00 s, T1 9.73 s, cycles wholly inside the window, last
kept cycle dropped, ≥ 5 required, stance = `leg0_l.grf_norm_y > 0.05`. **Terminal swing = the
last 15% of the cycle.**

Nine predictors, all terminal-swing means: `knee_l.torque`, `ankle_l.torque`, `hip_l.torque`,
`gastroc_l` and `soleus_l` and `tib_ant_l` activation, `gastroc_l.F` and `soleus_l.F`, and
`ankle_angle_l`. Target: `knee_angle_l` at heel strike, per-cycle mean.

---

## 4. Confirmatory material — untouched by the exploration

The exploration pooled `R151C`, `R151W`, `R169W090/095`, `R174W870/892/915`, `R151S`,
`R393SPg070/100`, `R396SPg110/120`.

**Confirmation uses cells excluded from that pool**, all already simulated:
`R289KV00625`, `R289KV0125`, `R291KV0035` (spastic ladder rungs) and `R276WPF005/010/020`,
`R285BF007/008`, `R287BF007/008`, `R291BF005/007/008` (plantarflexor-weakness families).
None of the nine terminal-swing quantities has been computed on any of them.

---

## 5. Registered predictions

**P1 — COLLINEARITY REPLICATES.** In the confirmatory pool, the largest unique ΔR² over the
nine predictors is **< 0.05**. A predictor carrying ΔR² ≥ 0.05 falsifies one-dimensionality and
identifies a genuinely separable channel — that would be a better result than P1 holding, and
must be reported as such rather than as a failure.

**P2 — ONE COMPONENT SUFFICES.** A principal-component analysis of the nine standardised
predictors has a first component explaining **≥ 80%** of their variance.

**P3 — THE AXIS IS THE SAME ONE.** The first component's loadings in the confirmatory pool
correlate with those from the exploratory pool at **|r| ≥ 0.8**. If the axis differs between
pools, the finding is pool-specific and does not generalise.

**P4 — IT PREDICTS THE ENDPOINT.** The first component alone predicts knee-at-IC with
**R² ≥ 0.7** in the confirmatory pool.

---

## 6. What this cannot establish

1. **Collinearity is not proof of a single cause.** Several genuinely distinct mechanisms that
   happen to co-vary across these cells would look identical. This registration establishes
   that they are **not separable in this design**, not that they are one thing.
2. Cells within a family share an optimisation lineage, so the 63 cells are not independent.
   `KNEE_MDC_BATCHNULL_r399.json` measured 26.7% separation between same-mechanism families,
   so family structure is real. Effective n is smaller than cell count and no p-value from the
   regression may be reported.
3. This says nothing about patients, and nothing about a system whose controller is **not**
   re-optimised — where a local perturbation might well remain separable.
4. The nine predictors are a choice. A tenth variable outside their span could carry
   independent information.

---

## 7. Uninformative and prohibitions

Fewer than 20 Gate-G cells in the confirmatory pool makes this UNINFORMATIVE. No substitute
predictor set, no changed terminal-swing window, no dropping of a family that weakens the fit,
no re-fitting of the 0.05 / 80% / 0.8 / 0.7 thresholds after seeing a value. If the predictions
fail they are recorded as failures and this registration is not amended.
