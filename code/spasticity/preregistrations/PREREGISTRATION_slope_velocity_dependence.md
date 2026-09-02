# Pre-registration — velocity-dependence under task demand

**Written 2026-07-27, BEFORE any slope condition has been analysed.** The downhill (RD2*/RE2*) and
uphill (UPL*) families are running at generation 26–56 and 45–53 respectively; no feature has been
extracted from any of them. This document is timestamped ahead of the data deliberately, because
every previous positive result on this project was chosen after seeing the numbers and none
survived.

---

## Why a pre-registration is required here specifically

Seven hand-picked features separated the classes and all seven died. The unifying cause is now
established: the CMA-ES objective value alone reproduces the entire classification, the
discriminant score tracks fitness at r = 0.932 (n = 22), and regressing the waveform on fitness
collapses accuracy from 0.857 to 0.143 (exact p = 1.0000). The feature space is one-dimensional
and that dimension is cost.

A cross-task difference term (Δankle velocity, Δcost, Δanything between level and slope) is **not
automatically immune**. If severity alone drives everything, Δfeature is still a common monotone
function of Δcost, and a slope experiment would manufacture the same confound with more steps.

So the test below is designed so that **the severity account and the mechanism account predict
different things**, and it is fixed now.

## The two competing accounts

| | prediction for Δfeature across tasks |
|---|---|
| **Severity (null)** | a common monotone function of Δcost, **the same functional form in both arms**. Knowing a run's fitness and its task predicts its feature, regardless of mechanism. |
| **Mechanism (alternative)** | a velocity-dependent reflex must respond **disproportionately to its own cost change** as stretch-velocity demand rises — this is the Tardieu R1/R2 logic, and it is the one property of the Lance definition that a severity axis cannot mimic. |

## Design, fixed in advance

1. **≥ 3 task conditions** spanning stretch-velocity demand, **at constant target walking speed**:
   level 0°, downhill −2°, downhill −5°. Slope is imposed by tilting gravity in the `.osim`, which
   is mechanically equivalent to a constant grade — the terrain `blueprint` property is silently
   ignored by `ModelOpenSim` and must not be used. Downhill is the mechanism-relevant direction:
   it raises plantarflexor stretch velocity at loading response, which is what a velocity-gated
   reflex is defined to respond to.

   **AMENDMENT (2026-07-27, before any slope feature was extracted). Uphill is DROPPED.** The
   original task set was downhill −2° / level / uphill 1.5°. Verified directly from the scenario
   files: `UPL05/UPL10/UPL15` carry `min_velocity = 0.8` (signature `S08W`) while every other
   condition — level, downhill, and all impairment arms — carries `min_velocity = 1.0` (`S10W`).
   Walking speed is the single strongest determinant of walking cost in patients (r = −0.89), so
   one of three task anchors differing in speed would let a **speed** effect enter the residual
   slope as a **task** effect. Every uphill run in this project's history is at reduced speed
   because uphill does not converge at 1.0 m/s. Restarting them would spend compute on a
   permanently confounded anchor.

   Replacing uphill with a second, deeper downhill grade is strictly better: a monotone residual
   slope across three grades **at constant speed** is a cleaner velocity-dependence test than a
   three-point trend containing a speed jump. The −5° arm is warm-started by continuation from the
   converged −2° solutions, the technique that succeeded for the uphill ladder where one-step
   attempts failed.
2. **Identical optimizer settings across every arm AND every task**: `max_generations = 90`,
   `min_progress = 1e-7`, same warm start, same objective. Non-negotiable — the existing level-
   ground dataset is currently unusable precisely because the class label is 100 % predictable
   from the scenario directory's stopping rule.
3. **Per-run convergence verified**, not assumed: a run enters the analysis only if the `.sto`
   analysed comes from the best `.par` (via `replay_cache.py`, which empties the directory,
   replays one `.par`, and asserts exactly one `.sto`) **and** that `.par` is at the run's own
   optimum rather than mid-descent. Equal generation *numbers* are not equal *convergence* —
   class 0 previously sat at its optimum while class 1 was still descending at generation 242–337.
4. **Stale shadow directories deleted first.** Every RD2/RE2 tag currently has two result
   directories (a dead gen 14–17 attempt and the live gen 26–56 run). Any mtime-based selection is
   a live hazard.

## Test statistic, fixed in advance

1. Calibrate `feature ~ f(fitness, task)` **on the non-spastic conditions only**. The spastic
   conditions are never used to fit the cost model.
2. Predict each spastic condition's feature from **its own fitness and its own task**.
3. **Test statistic = the slope of the spastic residual against task demand.**
4. Null distribution by **exact enumeration** over condition-level label assignments. Compute and
   report the attainable p-floor **before** running; if the floor exceeds 0.05 the experiment is
   underpowered by construction and must be enlarged before, not after, seeing the result.

## Decision rule, fixed in advance

**The claim survives only on a significant task × mechanism INTERACTION.**

- A **main effect** — spastic conditions offset from the cost model at every task alike — is a
  severity offset, **not** velocity dependence. It does not count.
- A **flat residual slope** kills the hypothesis regardless of how many conditions are added.
  This is the property the discarded "expand to 12 conditions" plan lacked: adding conditions to
  that design drove a zero-mechanism generative model to median p = 0.0022, certifying the
  confound at publishable significance.

## Mandatory controls, reported alongside every result

| control | required outcome |
|---|---|
| fitness alone through the identical pipeline | must score **below** the feature |
| generation alone (state which: analysed vs max reached) | must be at chance |
| **intact limb** — no lesion, no reflex | **must fail**; if it passes, the result is void |
| sham labelings: every contiguous cut along the cost axis | must score **below** the true labeling |

The sham control is stated precisely because of what was measured on the level-ground data: **every
contiguous cut along the cost axis classified at 0.857, while interleaved cuts scored 0.429.** The
classifier was ranking conditions by cost and cutting the ranking. Any future result must show that
the true labeling beats *all* contiguous cuts, not merely that it beats a random permutation.

## Pre-committed interpretation of a null

If the residual slope is flat, **that is the finding**, and it is reported as such: re-optimized
sagittal gait does not carry a velocity-dependence signature that survives removal of cost. That is
a statement about what CMA-ES re-optimization does to mechanism-specific signatures — it launders
them out, because the controller is assumed to have found a near-optimal compensation — and it is
publishable as a negative result about simulation-based discrimination. It is **not** to be
followed by another feature search.

## Pre-committed interpretation of the cost-matched arms (CMS020/030, CMW70/80)

Registered here so it cannot be re-decided later: **a null from the cost-matched contrast is not
new information.** If the feature space is one-dimensional and that dimension is cost, then
equalising cost drives accuracy to chance *by construction*. The analytical equivalent has already
been performed at zero compute — residualizing on fitness gives 0.143, exact p = 1.0000.

The one narrow thing the cost-matched runs can still add: residualization removes only a **linear**
projection of cost. Mechanism information lying in a direction non-linearly related to cost would
survive it and remain invisible. So a **positive** result from the cost-matched arms would be
informative; a **null** confirms a premise already in hand. They are allowed to finish because they
are also the project's first batch-matched arm (all eight carry `max_generations = 90`,
`min_progress = 1e-7`), but they are not billed as decisive.
