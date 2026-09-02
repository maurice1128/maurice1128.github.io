# PREREG_permnull_r221.md — pricing "sixteen channels, we picked the best one"

**Round 221.** ⛔ **Registered and hashed BEFORE running. Read-only, zero cells.**
*Where this document and the script disagree, THIS DOCUMENT DECIDES.*

---

## 1. The question

**The finding is one opposed channel out of sixteen, selected after looking.**
⛔ **How often does chance alone produce a channel that good?**

## 2. Exchangeability — decided here, with the reason, before any number

**Under the null "the lesion-type label carries no information about channel values", cells differing
only in label are exchangeable.**

⛔ **POOLING 18 WEAK AGAINST 6 SPASTIC IS NOT EXCHANGEABLE AND IS REJECTED.** *The 18 weak cells are
three different lesions — ×0.870, ×0.892, ×0.915 — and severity demonstrably shifts channel values
(`CHANNELS_G2_r219.json` → `channels.*.W870/W892/W915.mean` differ). **So the weak group carries real
internal structure that the spastic group does not.** A shuffle would redistribute that structure and
the null distribution would be wrong — not because the label matters, but because severity does.*

⭐ **PRIMARY: run it PER SEVERITY, 6 spastic versus 6 weak, three times.** *Within one severity the
twelve cells differ only in label under the null, which is exactly what exchangeability requires.*

⭐ **And because 6 v 6 has only C(12,6) = 924 distinct label assignments, the null is ENUMERATED
EXHAUSTIVELY, not sampled.** *No Monte-Carlo error, no seed, no convergence question. 924 assignments
per severity per channel.*

## 3. The statistic

**For one label assignment and one channel: the two groups of six are SEED-LEVEL DISJOINT if the
minimum of the higher group exceeds the maximum of the lower group; the GAP is that difference.**
*Direction-agnostic — either arm may be higher — because the family-wise question is "any channel this
clean", not "this channel in this direction".*

**Observed gaps to beat, `HIPGAP_r220.json` → `W870/W892/W915.seed_gap_deg`:**
**×0.870 → 1.0128° · ×0.892 → 1.5714° · ×0.915 → 1.2360°.**

⭐ **FAMILY-WISE STATISTIC: the proportion of the 924 assignments in which AT LEAST ONE of the sixteen
channels achieves a disjoint separation with gap ≥ the observed value for that severity.**
*That prices the selection.*

**PER-CHANNEL STATISTIC: the same proportion for `hip_flexion_LmR` alone.**
⭐ **The COST OF THE SELECTION is the difference between the two, and both are reported.**

⚠ *The observed assignment is one of the 924 and is included in the denominator, which is the standard
convention and makes the smallest attainable proportion 1/924 = 0.00108.*

## 4. Both readings, registered before the run

| | condition | registered reading |
|---|---|---|
| **A** | **family-wise proportion is SMALL** | ⭐ **Chance rarely produces a channel this clean even with sixteen tries. The selection is priced and the finding survives it. Say so plainly and without hedging.** |
| **B** | **family-wise proportion is NOT small** | ⛔ **One opposed channel out of sixteen is what sixteen channels look like, and the hip result is not evidence on its own.** ⭐ **REGISTERED NOW: this outcome is written and shipped at full strength.** *It would not delete the finding — the replication on six unseen seeds and the survival of the window change are separate evidence — **but the channel could not stand alone and the paper's claim would rest on those other legs.*** |

⛔ **No threshold for "small" is set here on purpose: the proportion is reported as a number and both
readings are stated so neither can be selected after seeing it.** *A reader applies their own bar.*

## 5. What this cannot establish

- ⛔ **It prices selection across channels. It does not price selection across WINDOWS, severities, or
  the choice of criterion** — those were also chosen after looking, and this test says nothing about them.
- ⛔ **Nothing about patients.** *Optimiser restarts, one model, one controller.*
- ⚠ **Per-severity 6 v 6 is the exchangeable form and it is also the least powerful one.** *A small
  proportion here is therefore harder to obtain than in the pooled form, which is the conservative
  direction.*
