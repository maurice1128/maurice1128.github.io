# PREREG_lmr_only_r223.md — does the separation survive restriction to the subject-invariant channels?

**Round 223.** ⛔ **Registered and hashed BEFORE running. Read-only, zero cells.**
*Where this document and the script disagree, THIS DOCUMENT DECIDES.*

---

## 1. Why, stated before the number exists

**`CLASSIFIER_r222.json`: blind leave-one-seed-out selection chose `hip_flexion_r` in 6 of 6 folds —
a raw single-limb channel — and `hip_flexion_LmR` in 0 of 6.**

⛔ **Every cell in this corpus is the SAME BODY.** *No height, no leg length, no mass distribution, no
habitual asymmetry differs between cells. They differ only by random seed and by lesion.*

⛔ **The `(L−R)` construction exists to cancel subject-level variation, and this corpus has none to
cancel.** *So a raw channel pays no penalty here that it would pay in a clinic, where a raw hip flexion
ROM sits under between-patient variability that a within-patient difference removes by construction.*

⭐ **That makes r222's result (d) a plausible ARTEFACT OF THE DESIGN rather than a finding about which
channel is better. The only way to tell is to run the comparison.**

## 2. Design — identical to r222 except the feature set

**Leave-one-SEED-out CV, 6 spastic vs 18 weak, window [1.00, 9.73], same classifier: standardise on
training seeds, select the single channel with the largest absolute standardised mean difference in
training, threshold at the midpoint of the class means.**

⛔ **FEATURE SET RESTRICTED TO THE FOUR `(L−R)` CHANNELS:** `ankle_angle_LmR`, `knee_angle_LmR`,
`hip_flexion_LmR`, `hip_adduction_LmR`. **No raw single-limb channel, no `cycle_time`, no unpaired
trunk channel.**

**The three guards are unchanged and all three apply:** *(1) every fitting step inside the fold;
(2) the SEED is held out, not the cell; (3) permutation null over the WHOLE procedure, exhaustive over
C(24,6) = 134,596 assignments.*

⚠ **Baseline unchanged: 18/24 = 0.7500. Six folds. Whatever comes out is an estimate from six folds.**

## 3. Both readings, registered before the run

| | condition | registered reading |
|---|---|---|
| **A** | **still separates, null still excludes chance** | ⭐ **The subject-invariant construction works on its own. The result does not depend on a quantity that inter-subject noise would destroy, and `hip_flexion_r` was merely the more convenient shortcut inside a single-body corpus. That is the stronger paper and it is said plainly.** |
| **B** | **degrades** | ⛔ **SHIPS AT FULL STRENGTH.** *The separation leans on a raw channel whose advantage is an artefact of every cell sharing one body — therefore the result is **LESS LIKELY TO TRANSFER TO PATIENTS than the `LmR` framing implied**. That is the most important thing this project could learn about its own external validity and it must not be softened.* |

⛔ **"Degrades" is read against the 75 % baseline and against r222's 24/24, both stated here in advance.
No reading may be selected after seeing the number.**

## 4. A fact the whole interpretation rests on, and which no container currently states

⛔ **WHICH SIDE CARRIES EACH LESION.** *The reading "the discriminator is the unlesioned limb" is
currently BELIEVED, not RECORDED.*

**This round deposits it as a field with the config paths that establish it:** *the spastic reflex
targets `soleus` and `gastroc` with `legs = left`; the weakness scales `tib_ant_l`.* ⭐ **If both hold,
`hip_flexion_r` is contralateral to both lesions and r222's result is a statement about the unlesioned
limb.** ⛔ **If either does not hold, that reading is withdrawn.**

## 5. What this cannot establish

- ⛔ **It cannot show `(L−R)` would survive real inter-subject variation.** *There is none here to test
  against. It can only show whether `(L−R)` suffices WITHOUT the advantage a raw channel gets from a
  single-body corpus.*
- ⛔ **Nothing about patients.** *Optimiser restarts, one model, one controller, one objective.*
- ⚠ **Four features instead of sixteen is a weaker selection problem**, *so a null proportion here is
  not comparable to r222's and the two must not be quoted as if they were.*
