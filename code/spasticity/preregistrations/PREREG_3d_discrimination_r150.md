# PREREG_3d_discrimination_r150.md — P3D-3: can the two lesions be told apart in 3D?

**Round 150, 2026-08-10. NOT RUN. No weakness arm exists in 3D at the time of hashing.**
*Where this document and any script disagree, THIS DOCUMENT DECIDES.*

⛔ **This is the first registration in the 3D line that addresses the research question.** *P3D-1
asked whether the out-of-plane channel exists. P3D-2 asked whether ONE lesion's effect is unilateral.
Neither asked whether the TWO lesions differ from each other, and five rounds of instrument repair did
not move that answer either.*

## 0. What exists, measured from disk

| | |
|---|---|
| `bench_D20` baseline | 12.16 s, 7 cycles, per-cycle ankle ROM **L 30.963° / R 31.368°** |
| `bench_D20_kv0p0125` spastic arm | 11.84 s, 8 cycles — **survives**, ⛔ **not unilateral (ratio 1.21)** |
| weakness arm in 3D | ⛔ **does not exist and has never been built** |
| `H1922v7b3.hfd` | 14,259 B, `max_isometric_force` ×22, **`tib_ant_l` at line 385 = 1759** |

⭐ **`tib_ant_l`'s `max_isometric_force` is 1759 in the 3D model — identical to the 2D control value
(`CONDITIONS["DR2K000"]["ta"] = 1759.0`). The weakness parameter transfers EXACTLY, in the same units,
where the spastic gain `KV = 0.050` did not transfer at all.** *Registered here because it is a
structural difference between the two injections and it is measurable before any run.*

## 1. The arms

| arm | injection | how |
|---|---|---|
| **A0** | none | existing `bench_D20` |
| **A1** | spasticity | existing `bench_D20_kv0p0125` — `MuscleReflex` soleus+gastroc, `legs = left`, KV 0.0125 |
| **A2** | weakness, PAR20-equivalent | **model edit**: `tib_ant_l` `max_isometric_force` 1759 → **1407.2** (×0.80) |
| **A3** | weakness, PAR40-equivalent | **model edit**: `tib_ant_l` `max_isometric_force` 1759 → **1055.4** (×0.60) |

**The 2D scale factors are carried unchanged** — *PAR20 = 1759 × 0.80 = 1407.2 and PAR40 = 1759 × 0.60
= 1055.4, exactly the 2D study's `ta` values.* ⛔ **Only `tib_ant_l` changes. `tib_ant_r` stays 1759.
No controller edit in A2/A3; no model edit in A1.**

## 2. ⛔ The gain the comparison uses, and that the comparison is CONDITIONAL on it

**A1 uses `KV = 0.0125`.** *Chosen because it is the HIGHEST gain in the registered ladder that
survives — 11.84 s against the baseline's 12.16 s — so it carries the largest spastic effect available
in a standing model.*

⛔ **Its unilaterality FAILED: |dR|/|dL| = 1.21 against a registered threshold of 0.33. There is no
gain at which the spastic injection is unilateral, so there is no clean gain to choose.**

⚠ **THE COMPARISON IS THEREFORE CONDITIONAL AND IS LABELLED SO IN ADVANCE: A1 is a BILATERAL
perturbation of a nominally unilateral lesion.** *Any separation A1 shows is a separation of "this
bilateral perturbation" from weakness, not of "spasticity" from weakness.* **`KV = 0.050` is NOT
carried: it floors the model at 3.87 s.**

## 3. The endpoint set — fixed now, and it is not ankle ROM alone

⛔ **An endpoint of ankle ROM alone repeats the 2D study in a more expensive model. The entire argument
for 3D was that compensation lives where a sagittal model cannot represent it.**

**Per-limb, per-cycle ROM in degrees, for each of:**

| plane | channel |
|---|---|
| sagittal | `ankle_angle_l` / `_r` |
| **out of plane** | **`hip_adduction_l` / `_r`** — r141 measured 12.30°, human magnitude |
| **out of plane** | **`hip_rotation_l` / `_r`** — r141 measured 14.21 / 14.03° |
| **out of plane, unpaired** | **`pelvis_list`** — r141 measured 11.06° | 
| **out of plane, unpaired** | **`pelvis_rotation`** — r141 measured 27.29°, ⚠ above normal |

**Also reported, not scored:** `knee_angle`, `hip_flexion`, run duration, cycle count.

⚠ **`pelvis_rotation` and `lumbar_rotation` were ABOVE normal in r141, so they are reported with that
caveat attached and no separation on them alone will be called physiological.**

## 4. The metric and the window — both already paid for

⛔ **Metric: MEAN PER-CYCLE ROM.** *GRF-delimited cycles via the project's `heel_strikes`, settle
1.0 s, last cycle dropped, degrees.* **NOT the global range.** *Calibration: r141's independent
30.963° reproduces under per-cycle mean and not under global range, and the global range inflated a
0.405° between-limb difference into 1.934° — a 4.78× artifact of between-cycle drift.*

⛔ **Window: ONE common interval across ALL FOUR arms** — `[1.0 s, min(duration over A0..A3)]`.
*Round 146 established the window was not the cause of that discrepancy; it establishes the
discipline, not an exemption.*

## 5. Survival gate, carried from P3D-2 unchanged

**An arm is admitted only if duration ≥ 9.73 s AND ≥ 5 GRF-delimited cycles after settle.**
⚠ **A weakness injection can floor the model exactly as `KV = 0.050` did. If A2 or A3 fails, it is
reported as NOT ATTAINABLE and is not silently dropped.**

## 6. ★ THE REGISTERED PREDICTION, AND IT IS FALSIFIABLE

**Weakness is unilateral BY CONSTRUCTION: one muscle, one side, scaled. Nothing can leak through the
controller because no controller changed.** *Spasticity's mechanical consequence was measured
bilateral (1.21).*

> **PREDICTION P: the weakness arms are unilateral by the same test the spastic arm failed —
> |dR|/|dL| ≤ 0.33 on ankle ROM — while the spastic arm is not.**

⛔ **If P holds, the DISCRIMINATOR IS NOT THE MAGNITUDE OF ANY CHANNEL BUT THE LATERALITY OF THE
RESPONSE**, and that is a candidate a sagittal model could not have produced.

⚠ **P is falsifiable and may well fail.** *A weakened `tib_ant_l` changes gait, and a changed gait
loads the right limb differently — the same mechanism that made the spastic injection bilateral. **If
weakness is ALSO bilateral, laterality does not discriminate and this line is closed.*** *Registered
now precisely so that outcome cannot be reported as uninformative.*

## 7. Separation criterion — weak on purpose, because n = 1

⛔ **ONE seed, ONE benchmark. There is no variance estimate, so no inferential claim is available and
none will be made.**

**The only noise proxy on disk is the baseline's own left–right asymmetry per channel** — *e.g.
0.405° on ankle ROM.* **A channel is recorded as SEPARATING only if:**

> **| metric(A1) − metric(A2 or A3) | exceeds the baseline's own |L − R| on that same channel.**

⚠ **This is a weak bar and it is labelled weak.** *It says a difference is larger than the within-run
asymmetry of an uninjected model. It does not say the difference is reliable, reproducible, or larger
than seed-to-seed variation, none of which this design can measure.*

## 8. ⛔ What a null would and would not license — fixed before the numbers

**If NO channel separates:**

- ⛔ **It licenses nothing about spasticity versus weakness in 3D.** *The spastic arm is a bilateral
  perturbation at a gain whose unilaterality already failed; a null between a compromised arm and a
  clean one is weak evidence about 3D and strong evidence about nothing.*
- **It DOES license one narrow claim:** *at this gain, on this benchmark, the out-of-plane channels do
  not separate the two injections by a bar set at the baseline's own asymmetry.*
- ⚠ **It does NOT close 3D**, because the spastic arm was never made unilateral. **The honest next step
  after a null is a defensible spastic injection, not another endpoint.**

**If a channel DOES separate:**

- ⛔ **It is a CANDIDATE, not a finding.** *n = 1. Any separation must replicate across seeds before it
  is reported as anything, and this registration does not authorise that claim.*
- ⚠ **A separation on `pelvis_rotation` alone is discounted** — the channel was above normal in r141
  and may be an artefact of the objective rather than of the lesion.

## 9. What is not changed and what is not claimed

- **`H1922v7b3.hfd` in `bench_D20` is NOT edited.** *A2 and A3 get their own copied model files.*
- **No controller edit in the weakness arms; no model edit in the spastic arm.**
- ⚠ **Nothing here says the 2D result is wrong, or that 3D is better.** *It asks one question: at one
  gain, on one benchmark, do the two injections look different — including where a sagittal model
  cannot look.*
