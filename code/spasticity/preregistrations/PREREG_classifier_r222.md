# PREREG_classifier_r222.md — does the sixteen-channel vector separate spastic from weak on an unseen seed?

**Round 222.** ⛔ **Registered and hashed BEFORE running. Read-only, zero cells.**
*Where this document and the script disagree, THIS DOCUMENT DECIDES.*

---

## 1. The question

**`PERMNULL_r221.json` priced the single-channel selection at zero cost — no channel other than
`hip_flexion_LmR` reaches the observed gap in any of 924 relabelings, at any severity.**

⛔ **So this is not about rescuing the hip channel. It asks whether the result GENERALISES: from the
full sixteen-channel vector, can a classifier tell a spastic gait from a weak one on a seed it has
never seen?**

## 2. Design

**Leave-one-SEED-out cross-validation. 6 spastic cells against 18 weak cells (×0.870, ×0.892, ×0.915),
window [1.00, 9.73], all sixteen registered channels.**

**Six folds. Fold *k* holds out seed 100+*k* entirely — its spastic cell AND its three weak cells —
and trains on the other five seeds.**

## 3. ⛔ The three guards. Without all three the number is worthless.

⛔ **Sixteen features against twenty-four cells reaches 100 % by memorisation. These are what stop it.**

1. ⛔ **EVERY FITTING STEP INSIDE THE FOLD.** *Feature selection, standardisation and threshold are all
   computed on the training seeds only. **If the hip channel enters because it looked good on all the
   data, the fold is contaminated and the accuracy is fiction.***
2. ⛔ **LEAVE OUT THE SEED, NOT THE CELL.** *A spastic and a weak cell from the same seed share their
   control ancestry and their warm start. Dropping one cell would leave its siblings in training.*
3. ⛔ **A PERMUTATION NULL ON THE WHOLE PROCEDURE.** *Shuffle labels, rerun the ENTIRE cross-validation
   including selection, and report where the observed accuracy sits.*

**Enumeration versus sampling:** *the label space here is C(24,6) = 134,596 assignments of six spastic
labels among twenty-four cells. **That is enumerable and it is enumerated exhaustively.** No sampling,
no seed, no convergence question. If runtime forbids it the result says so and reports the sampled
count instead.*

**Classifier: the simplest thing that can be audited** — *standardise on training seeds; select the
single channel with the largest absolute standardised mean difference between classes in training;
threshold at the midpoint of the two class means. **One feature, one threshold, both chosen inside the
fold.*** ⚠ *A richer model is not registered, because with 24 cells it would be fitting noise and the
guards could not be checked by eye.*

## 4. ⚠ The ceiling, stated before the number exists

⛔ **6 spastic versus 18 weak. The majority-class baseline is 18/24 = 75 %.** *An accuracy below 75 %
is worse than always answering "weak".*
⛔ **Six folds. Whatever comes out is an estimate from six folds and is written as one.**
⚠ *Per-fold accuracy moves in steps of 1/4 within a fold and 1/24 overall; there is no resolution
between adjacent values.*

## 5. The four numbers reported, and nothing else

**(a) the confusion matrix · (b) the accuracy · (c) the permutation-null position of that accuracy ·
(d) how often `hip_flexion_LmR` was chosen across the six folds when selection ran blind.**

⭐ **(d) is the one that matters most: if selection picks it 6 of 6 times without ever seeing the
held-out seed, the channel was chosen by the data and not by us.**

## 6. Both readings, registered before the run

| | condition | registered reading |
|---|---|---|
| **A** | **separates, and the null says chance does not** | ⭐ **That is the paper's headline and the hip channel is the mechanism underneath it. Stated plainly, no hedging.** |
| **B** | **does not separate** | ⛔ **SHIPS AT FULL STRENGTH.** *A channel individually clean at 2/924 does not compose into a usable discriminator — **a real and publishable negative about this whole approach**, and more useful to the field than the positive, because it tells anyone attempting this what breaks.* |
| **C** | **separates but the null says chance does too** | ⛔ **The folding leaked. Say so and say WHERE, rather than reporting the accuracy.** |

⛔ **No threshold for "separates" is set here beyond the 75 % baseline, and no reading may be selected
after seeing the number.**

## 7. What this cannot establish

- ⛔ **Nothing about patients.** *Optimiser restarts of one model, one controller, one objective.*
- ⛔ **It does not price selection across windows, severities or criteria** — *those were chosen after
  looking and this test says nothing about them.*
- ⚠ **Three weakness severities are pooled as one class.** *A classifier that separates spastic from
  weak-in-general is not shown to separate spastic from any particular severity.*
