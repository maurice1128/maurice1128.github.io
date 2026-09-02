# PREREG_pairing_r251.md — is the permutation null in this paper the right null?

**Written BEFORE any correlation or paired null was computed, round 251.** *Both readings are recorded
here with their consequences, so that neither can be selected after the numbers are seen.*

---

## 1. The objection

Every permutation null in `RESULTS_3d_r214.md` is **unpaired**. §4's per-severity channel criterion and
§6b's per-severity counts are exhaustive over **C(12,6) = 924** label assignments, 6 reflex cells
against 6 weakness cells.

But the cells are **four arms × the same six optimiser seeds** — `R151C_s101`–`s106`,
`R151S_s101`–`s106`, `R174W892_s101`–`s106`. Seed `s101` appears once in every arm.

⛔ **If the shared seed induces genuine correlation between arms, the cells are paired, and the correct
null permutes WITHIN seed** — for each seed independently, swap the arm label. **That is 2⁶ = 64
assignments, not 924**, and the attainable floor is **1/64 = 0.015625**, not **1/924 = 0.001082**.

## 2. The prior question, which is measurable and is decided first

⚠ **Pairing may not be the right model.** *The six seeds are optimiser restarts, not subjects. `s101` in
the control arm and `s101` in the reflex arm share a random seed and a warm start — but they are not
repeated measures on one individual, and the controller is fully re-optimised after the lesion is
applied. **Re-optimisation may destroy whatever the shared seed induced.***

**This is measured, not argued.** *Statistic: the correlation across the six seeds between arms, on
`hip_flexion_LmR` and `ankle_angle_LmR`, for every arm pair — Pearson and Spearman, reported in full
with no selection among pairs.*

## 3. The decision rule, fixed in advance

- **If the cross-arm per-seed correlations are broadly null** — centred near zero with no consistent
  sign across pairs — **the unpaired C(12,6) null is CORRECT, the objection dissolves, and nothing in
  §4 or §6b changes.** *This is recorded as a live possibility, not a formality.*
- **If they are substantially positive and consistent** — the shared seed survives re-optimisation —
  **pairing is required and the paired null must be computed and reported.**

⚠ *No threshold is set, because a single fixed cut on six points would be arbitrary. **The full matrix
is reported and the reading is stated against it**, including if it is ambiguous — "ambiguous" is a
permitted outcome and must be reported as such rather than resolved toward either branch.*

## 4. Both consequences, registered now

**BRANCH A — the paired null still places the observed assignment at or near its floor.**
The claims **survive at weaker p-values**. Every "2/924 = 0.0022, at the arithmetic floor" statement in
the paper is **restated at the paired floor**, and the paper says so at every number. *§4's selection
pricing becomes a statement about 64 assignments, not 924, and its language must change accordingly:
"no other channel ever reaches the observed gap across all 924" becomes a claim about 64.*

**BRANCH B — it does not.**
⛔ **§4's selection pricing goes the way §1's and §2's went: the channel selection is UNPRICED.** *That
would leave **the contralateral finding of §6b and the ankle dose-response** as the only results in this
paper with a defensible null. **That is a much smaller paper, and it is the outcome this registration
exists to make reportable rather than avoidable.***

⚠ **A third outcome is possible and is registered too:** *the paired null may be computable for §6b's
per-severity counts but not for §4's selection criterion, if the criterion's definition does not carry
over to a within-seed swap. **If so, that is reported as "not computable under pairing", which is a
form of Branch B for §4 and must not be presented as Branch A.***

## 5. What is NOT decided by this

*Nothing here touches the contralateral finding (§6b), which rests on band membership and
mean displacement, not on a permutation null. Nothing here touches the ankle's ρ = −1.0000, whose
p = 1/720 is a rank-permutation floor over severities and does not involve the seed pairing.*
