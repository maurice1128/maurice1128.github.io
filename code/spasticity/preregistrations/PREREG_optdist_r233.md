# PRE-REGISTRATION — is the hip channel an optimiser-distance readout? (round 233)

Registered **before any distance was computed**. Hashed with a `.sha256` sidecar before extraction.

The mechanism line is withdrawn: no measurement in it took a value depending on the thing being
explained. **This tests the rival account instead, because it is more parsimonious than H1 and it
predicts the one fact H1 cannot.**

---

## 1. The rival

`PREREG_mechanism_r230.md` §7 registered it and then called it *"consistent with H1"*. **It is not
consistent — it is a rival that would make H1 unnecessary:**

> The hip channel reads **how far the optimiser had to travel from the shared warm start**, not gait
> physiology. Fitness degrades monotonically with severity, so a severe deficit forces a global
> re-solve while a mild one leaves the control-like solution intact.

⭐ **The evidence already on the table favours it.** `r(scale, EXCURSION_LmR) = +0.8745` — **the mildest
lesion produces the largest deviation.** H1 cannot explain that; this account predicts it directly.

## 2. Why this is testable read-only

**All eight arms share one warm start, byte-identical:** `H1922v7b3-TSG3Dv8g-989_fixed2.par`,
sha256 `32bafa8be2ce6b93…`, present in every cell directory, **95 parameters**. `.par` columns are
`name / value / CMA-mean / CMA-std`.

## 3. ⛔ The metric, fixed before extraction

**Cell vector** `x` = column 2 (parameter **value**) of the cell's selected `.par`, 95 entries in file
order. **Warm start** `w` = column 2 of `H1922v7b3-TSG3Dv8g-989_fixed2.par`. **Scale** `s` = column 4
(**std**) of the *warm start*, which is fixed, shared by every arm, and set before any cell existed.

**PRIMARY metric — normalised parameter distance:**

```
D_norm = sqrt( mean_i( ((x_i - w_i) / s_i)^2 ) )
```

Per-parameter z-scaling by a shared, pre-existing sigma, so no parameter's raw units dominate and the
normalisation cannot be tuned. **SECONDARY, reported alongside:** unnormalised Euclidean
`D_raw = ||x - w||`, and `D_max = max_i |x_i - w_i| / s_i`. **If the three disagree in sign of
correlation, that is reported and no reading is declared.**

**Cell `.par` selection:** lowest field-3, **ties broken by highest generation** — the rule verified in
`RECIPE_AUDIT_r232.json` to reproduce all 48 deposited cells.

**Endpoint:** `EXCURSION_LmR` for `hip_flexion`, the deposited quantity behind the −2.105 headline,
read from `LADDER36_r228.json`. **Not** `ANGLE_LmR`.

**Arms:** `R151C`, `R151S`, `R151W`, `R174W870`, `R174W892`, `R169W090`, `R174W915`, `R169W095`,
six seeds each, 48 cells.

## 4. The three correlations, all reported

1. **Pooled** `r(D_norm, EXCURSION_LmR)` over all 48 cells.
2. **Within-arm**: `r` computed per arm over its six seeds, then the mean and the range.
   ⚠ **Pooled and within-arm answer different questions.** A pooled correlation can be produced
   entirely by arm-level means with no within-arm structure; a within-arm correlation cannot. **Both
   are reported and neither is quoted alone.**
3. **`r(D_norm, fitness)`** — field 3 of the selected `.par`. Fitness degrades monotonically with
   severity and **may be the same axis as distance**; if `|r(D_norm, fitness)| > 0.9` the two are not
   separable in this corpus and that is stated rather than worked around.

Also reported: `r(D_norm, tib_ant scale)` across the six weakness arms, since the rival's mechanism is
that milder lesions stay nearer the warm start.

## 5. ⛔ The two readings, registered before looking

**STRONG — pooled |r| ≥ 0.5 AND mean within-arm |r| ≥ 0.4, same sign.**
⭐ **The channel is substantially an optimiser-distance readout, and the paper's central claim changes
meaning: the arms separate because they required different amounts of re-optimisation, not because the
lesions produce different gait physiology.** The separation stays real and stays a discriminator —
**but a discriminator of how the model adapted, whose transfer to patients is far weaker than the
paper currently implies.** ⛔ **This ships at full strength and would be the most consequential finding
of the project.**

**WEAK — pooled |r| < 0.5 OR mean within-arm |r| < 0.4.**
The rival is **measured and dismissed**. H1 survives **as untested rather than unnecessary**, and the
mechanism question is genuinely open rather than parked.

**SPLIT — pooled and within-arm disagree**, or the three distance metrics disagree in sign. Reported as
such; **neither reading may be declared**, and the disagreement is the result.

⚠ **A correlation is not a direction of causation.** Even STRONG leaves open that the lesion causes
both the distance and the deviation. **What STRONG would establish is that the channel carries
optimiser-distance information the paper attributes entirely to physiology** — which is enough to
change what the paper may claim, and not enough to say the physiology is absent.

## 6. Deposit

`paper/OPTDIST_r233.json` — per cell: the three distances, endpoint, fitness, arm, seed, selected
`.par` and its tie status; all correlations; the reading the rules select. Script
`scone/optdist_r233.py`, recording its own sha256, this registration's, and the warm start's.

⛔ **Where this document and the code disagree, the RUN IS VOID.**
