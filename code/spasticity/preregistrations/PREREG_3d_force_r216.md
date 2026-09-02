# PREREG_3d_force_r216.md — §0 only, and §0 closes the axis

**Round 216.** *`PREREG_3d_force_r213.md` stays frozen and unrun (8,974 B, sha256 `ACCFB24B…F3BA9`).
Its halt is `HALT_3d_force_r215.md`.*

⛔ **§0 was written first and instructed to decide whether the rest gets written. IT RULED (c).
THE REST IS NOT WRITTEN. The force axis is closed on a measurement.**

---

## 0. The prior, and what result would be informative given it

### 0a. The prior, quoted

**`LITERATURE_r213.md` item 3, "Predicting Gait Patterns of Children With Spasticity by Simulating
Hyperreflexia" (2023):** ***"Both velocity-based and force-based hyperreflexia were tested.
Velocity-based proved superior."*** *On a KINEMATIC endpoint. That file's own gloss: "on that endpoint
velocity wins… `KV` is not the wrong signal for kinematics — it is the better-supported one."*

⚠ **One qualification, and it is the strongest thing available to the (a) case: that work FITTED
hyperreflexia values so simulated gait matched observed patterns.** *This project holds the lesion
fixed and re-optimises the controller around it. Fitting-quality superiority is not the same claim as
signature-under-adaptation.*

⚠ **Cannot verify from `LITERATURE_r213.md` whether that model is planar or bilateral**, so it cannot
be established here whether it could produce an `(L−R)` channel at all. *The absence is recorded, not
used.*

### 0b. The three ways this can come out, worked through

**(a) A NULL IS INFORMATIVE.** ⛔ **Rejected.** *The only null that would not restate the prior is "the
null holds under RE-OPTIMISATION, where the 2023 work fitted gains." **But `PREREG_3d_force_r213.md`
E1–E3 already argue the optimiser has a single-parameter route against `KF` unavailable against `KV`,
and that "a larger avoidance is the expected outcome, not a discovery."** A null would then confirm two
priors at once — the literature's and the registration's own mechanism — and neither is tested by it.*

**(b) ONLY A POSITIVE IS INFORMATIVE.** ⛔ **Rejected, and this is the decisive one.** *The positive
worth having is not "KF displaces some channels" — the KV arm already displaces **10 of 16**, so
displacement is the expected background, not a signature. **The project's surviving claim is about
OPPOSITION: `hip_flexion_LmR` is the one channel where the two arms move to opposite sides of the
control band.*** ⛔ **Opposition is a two-arm property. Evaluating it for `KF` requires a weakness arm
dose-matched to `KF`, and no such arm exists or is committed to here. Six `KF` cells can establish
displacement and CANNOT establish opposition.** ⚠ *So the outcome that would matter is not reachable
inside the cells, and the outcome that is reachable is not the one that matters.*

**(c) NEITHER IS INFORMATIVE INSIDE SIX CELLS.** ⭐ **RULED. Both (a) and (b) fail, for different and
independent reasons: the null restates two priors, and the positive cannot address the claim the
project actually holds.**

### 0c. What closing on this costs, stated so it is not mistaken for a preference

⛔ **This is a measured absence, not a judgement that force feedback is uninteresting.** *What would
make the axis informative is nameable and is not six cells: **a `KF` arm AND a weakness arm dose-matched
to it**, so opposition can be evaluated rather than displacement. That is the same structure the
matched study built for `KV`, and it is a new registration of at least twelve cells plus a dose-matching
step.*

⚠ **The eleven remaining requirements from `HALT_3d_force_r215.md` §7 are MOOT.** *They repair a design
whose §0 does not license execution. **Repairing them would have produced a registration that survives
its own cold read because it was written to** — which is the failure mode available to a seat that has
halted eight registrations in eight reads, and it is named here so the ruling can be checked against
it.*

⭐ **The force axis closes the way the speed axis and the depth axis closed: on a measurement.**
⛔ **Zero cells spent on it, in total, across both registrations.**

### 0d. What is NOT claimed by this closure

- ⛔ **Not that force-based hyperreflexia produces no kinematic signature.** *That is the prior, and this
  project has not tested it.*
- ⛔ **Not that the 2023 result is confirmed.** *It was read from a summarising fetch, not from the
  paper's methods, and its dimensionality is unverified.*
- ⚠ **Not that `KF` is unrunnable** — *only that six cells against no matched weakness arm cannot decide
  anything this project needs decided.*
