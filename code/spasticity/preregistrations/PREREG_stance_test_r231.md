# PRE-REGISTRATION — settling the stance account by measurement (round 231)

Registered **before extraction**. The stance mechanism was declared refuted by comparing an **impulse
fraction** against a **duration fraction**, which is not a test of it. Rev 2 of the mechanism
registration rests on that sentence, so nothing downstream is settled until this is.

---

## 1. Why the earlier comparison was not a test

Rev 1 predicted the reflex **resists dorsiflexion in stance**. What was measured was *where the
lengthening impulse falls* (0.26 soleus / 0.12 gastroc in stance, against stance occupying 0.59 of the
cycle). **A mechanism can act in a phase that holds a small share of total lengthening**, if the
resistance it produces there is large relative to what the limb is doing. Share-of-impulse cannot
decide that. **Neither "refuted" nor "supported" is currently established.**

## 2. The statistic — what rev 1's mechanism actually predicts

Computed on the **six control cells** (un-re-optimised, so this is where the lesion *would* act, not
where the optimiser moved it), window [1.00, 9.73], left heel-strike cycles, last dropped.

At the **corrected ×1.0 scale** (`V = fiber_velocity_norm`, established in `F5_DEPENDENCY_r231.md`):

```
du   = min( KV · max(0, fiber_velocity_norm),  1 − u )      added excitation, KV = 0.050
gain = mtu_force_norm / max(u, 0.01)                        current force per unit excitation
F_add = du · FMAX · gain                                    added muscle force, newtons
F_base = mtu_force_norm · FMAX                              baseline force, newtons
```

Summed over `soleus_l` + `gastroc_l`.

⚠ **The ankle plantarflexor moment is `F · r`. The moment arm `r` is not in the `.sto`, so ratios of
added-to-baseline moment equal ratios of added-to-baseline FORCE only under a constant moment arm
within a phase.** That assumption is stated here and the analysis reports **forces**, not moments,
with the assumption carried at the claim.

**Reported per normalised-cycle bin (20 bins of 5 %) and per window:**
`F_add`, `F_base`, their ratio, the added excitation `du` against baseline `u`, and the **ankle's
direction of travel** (sign of `d(ankle_angle_l)/dt`, with the convention read from `H1922v7b3.hfd`
before any number is interpreted).

**Windows:** **LR = 0–15 %** of cycle (loading response, where the earlier breakdown put essentially
all stance lengthening) and **ES = early swing**, defined as the first 15 % of cycle *after* toe-off.

## 3. ⛔ The three outcomes, registered before extraction

**S1 — STANCE SUPPORTED.** `F_add` in the LR window is a **large fraction of `F_base` there** (≥ 20 %)
**and** the ankle is **dorsiflexing** through it. Rev 1's account is supported, rev 2's swing account is
at best incomplete, and the mechanism section is rewritten around **both** windows.

**S2 — STANCE REFUTED, for the right reason.** `F_add` in LR is **negligible in absolute newtons**
(< 5 % of the peak `F_add` anywhere in the cycle) **despite** a large ratio, because the baseline there
is near zero — the ×11.3 figure is against a baseline excitation `u` of 0.010, and **×11.3 of almost
nothing is almost nothing.** Rev 1 is refuted properly this time and rev 2 stands.
⚠ *This is the outcome the coordinator considers most likely. It is registered as a prediction, and it
must be measured, not assumed.*

**S3 — NOT PHASE-LOCALISED.** LR and ES carry **comparable** absolute `F_add` (neither below half the
other). **Both rev 1 and rev 2 are wrong**, the reflex acts throughout the cycle, and **the phase story
is abandoned entirely.** ⛔ Registered at full strength: this is the costliest outcome and it is
entirely plausible.

**S4 — indeterminate.** Fewer than 4 of 6 control seeds usable, or fewer than 2 cycles in a majority.
No claim.

## 4. What happens next, fixed now

Whichever fires, **`PREREG_mechanism_r230.md` is rewritten from it** — §1's kill sentence replaced by
what was measured, and H1 kept, narrowed, or dropped accordingly. **No surrounding section is repaired
before this measurement is in**, because they are all built on the sentence being settled.

Deposit `paper/STANCE_TEST_r231.json`; script `scone/stance_test_r231.py`, recording its own sha256 and
this registration's. Where document and code disagree, the run is void.
