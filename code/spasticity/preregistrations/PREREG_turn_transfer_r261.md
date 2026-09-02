# PREREG_turn_transfer_r261.md — does progressive turning explain the failed transfer?

**Written BEFORE the detrended hip result was computed, round 261.** *`turn_r260.py` was already
running when this was written; it deposits `hip_dev80` per cell but performs the turn-adjustment
regression only for the ankle. The hip adjustment has not been run.*

---

## 1. The hypothesis, and who produced it

⚠ **This hypothesis was handed to the analyst by the coordinating seat, complete, and it resolves two
open problems at once.** *That is precisely the condition under which a confirming result gets found.*
⛔ **The tidiness of an explanation is not evidence for it, and this registration exists because the
explanation is tidy.**

**The hypothesis.** `PHASE_r258.json` shows the 3D reflex arm accumulates ≈1.37°/1.56° of pelvis
rotation per cycle against ≈0.17°/0.09° in control — the model is progressively turning.
`MODEL_DESCRIPTORS_r253.json` establishes that the 2D body is the sagittal reduction and has **no
frontal or transverse degree of freedom**: no `pelvis_rotation`, no `pelvis_list`, no `hip_adduction`,
no `lumbar_bending`. **The 2D model physically cannot turn.**

*So if the 3D headline channel `hip_flexion_LmR` is substantially reading a transverse-plane
instability, the second body could not express it, and the transfer outcome `D1` and the channel
disagreement would have a mechanistic explanation about the MODELS rather than about the design.*

## 2. What is computed

**Identical in form to the ankle adjustment already run in `turn_r260.py`, and applied to
`hip_flexion_LmR`:** across all 48 cells, regress the cell's `hip_dev80` (deviation from the control
mean curve at 80 % of cycle) on the cell's net rotation per cycle; report the correlation, the
reflex-arm mean before and after adjustment, and the same for the peak deviation. Both windows.

*No curve surgery: the turn enters as a covariate, not as a subtraction from the trajectory.*

## 3. The readings, registered in advance

**READING A — the hip channel's displacement is SUBSTANTIALLY REDUCED by adjustment.**
⭐ *Then the 3D headline channel was, in material part, reading a transverse-plane instability the 2D
body cannot have, and the failed transfer is **explained** rather than merely reported.* ⚠ **It would
still not rescue the discrimination claim** — an artefact-driven channel is not a biomarker — *and the
paper must say that the explanation of the transfer failure and the failure of the claim are the same
fact.*

**READING B — the hip channel's displacement SURVIVES adjustment substantially intact.**
⛔ *Then turning is a **separate validity problem** and the transfer failure remains **unexplained**.
This must be reported as plainly as Reading A would be, and the hypothesis recorded as tested and not
supported.*

**READING C — the adjustment is uninformative** because turning and arm are collinear (the reflex arm
being both the most turning and the most displaced), so the regression cannot separate them.
⚠ **This is the most likely outcome with n = 8 arms and one reflex condition, and it must be reported
as "cannot be separated in this corpus" rather than resolved toward either branch.** *Diagnostic fixed
in advance: if the reflex arm's residual is small BUT the control and weakness arms also carry large
residuals of the same sign, the model is fitting arm identity through the turn covariate and the test
is void.*

## 4. Bounds fixed in advance

- ⛔ **A covariate adjustment on observational cells does not establish causation in either direction.**
  Turning may cause the channel displacement, the channel displacement may be part of how the model
  turns, or a third feature of the re-optimised controller may cause both.
- ⛔ **Even Reading A does not repair the transfer.** *The registration governing the second body is
  void, its executed revision unrecoverable, and its outcome was `D1` for reasons of comparison
  formation, not channel behaviour. An account of why a channel might not transport is not the same
  object as a valid transfer test.*
- ⚠ **`pelvis_rotation` itself remains unreported in the manuscript**, and that defect is independent
  of how this test comes out.
