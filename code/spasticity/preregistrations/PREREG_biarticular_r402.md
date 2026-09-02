# PREREG — Is the knee signature carried by the biarticular muscle? (r402)

**Registered:** 2026-08-24, before any cell of the R402 series has been staged or run.

---

## 1. The claim this tests, stated so it can fail

`knee_angle_l` at left heel strike separates the two lesions where every ankle endpoint failed:

| arm | n | range (deg) | mean |
|---|---|---|---|
| WEAK ×0.80 | 6 | [−6.2735, −5.3749] | −5.8443 |
| CONTROL R151C | 6 | [−8.2396, −7.5876] | −7.8500 |
| SPAS KV 0.110 | 4 | [−13.7949, −12.6655] | −13.1995 |

Edge gap SPAS KV 0.110 vs WEAK ×0.80 = **+6.3919°**, disjoint, exhaustive permutation 1/210.
The two lesions displace the control in **opposite** directions; the ankle endpoints displace it
in the **same** direction, which is why they only ever reached 0.22–1.42°.

**The proposed explanation is anatomical.** The spastic lesion is applied to soleus **and**
gastrocnemius. Gastrocnemius is **biarticular** — it spans the ankle *and* the knee — so extra
drive to it flexes the knee. The weakness lesion is applied to `tib_ant_l`, which spans the
ankle only and cannot act at the knee at all; the foot drops, contact is made forefoot-first,
and the knee ends up *less* flexed. Hence opposite signs.

**This is currently a story told after seeing the result.** It is testable, and this
registration tests it.

---

## 2. Design

The spastic lesion is decomposed. Three arms, six seeds each, all newly simulated:

- **BOTH** — `MuscleReflex` KV = 0.110 on **soleus and gastrocnemius**, left. Reproduces the
  existing R396SPg110 condition; run again here so all three arms share one staging protocol.
- **SOL only** — KV = 0.110 on **soleus alone**. Uniarticular: spans the ankle, not the knee.
- **GAS only** — KV = 0.110 on **gastrocnemius alone**. Biarticular: spans both.

`delay = 0.020`, `allow_neg_V = 0`, `legs = left`, unchanged. Model file unlesioned
(`tib_ant_l` 1759, `soleus_l` 3549, `gastroc_l` 2241) — this arm carries **no** weakness lesion.

**Chaining:** each arm is warm-started from the same seed's **R396SPg110** solution where that
cell passed Gate G, and from **R393SPg100** otherwise; the parent used is recorded per cell with
its `.par` sha256. Budget 90 generations, as everywhere else.

**Reference arms, not re-run:** CONTROL `R151C` and WEAK `R151W`, both already measured.

---

## 3. Primary endpoint and the registered predictions

**Endpoint:** `knee_angle_l` at left heel strike, per-cycle mean over admissible cycles, degrees.
Corpus convention: SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the last kept
cycle, require ≥ 5, stance = `leg0_l.grf_norm_y > 0.05`.

**P1 — THE MECHANISM.** The knee displacement from control is carried by **gastrocnemius**:
`GAS only` reproduces most of `BOTH`'s knee displacement, and `SOL only` reproduces little of it.
Registered quantitatively before measurement:

> **|Δknee(GAS only)| ≥ 0.6 × |Δknee(BOTH)|  AND  |Δknee(SOL only)| ≤ 0.4 × |Δknee(BOTH)|**,
> where Δknee is the arm mean minus the `R151C` control mean.

**P2 — DIRECTION.** All three spastic arms displace the knee in the **same** direction as
`BOTH` did, i.e. more flexed than control (more negative).

**P3 — THE ANKLE CONTROL, which makes the test specific.** At the **ankle**, `SOL only` and
`GAS only` should both act — both muscles are plantarflexors — so the ankle displacement should
**not** show the same lopsided split. Registered: the soleus share of the ankle displacement is
larger than its share of the knee displacement.

**If P1 fails the anatomical explanation is wrong and must be withdrawn**, whatever else the
data show. A result in which `SOL only` carries the knee signature as strongly as `GAS only`
refutes it outright, and that is to be reported as the finding.

---

## 4. Gate, null, and what this cannot show

Gate G unchanged. A rung with fewer than 4 Gate-G seeds is UNINFORMATIVE, reported not dropped.

⚠ **The batch null applies.** `KNEE_MDC_BATCHNULL_r399.json` measured 4/15 = **26.7%**
separation between two same-mechanism dorsiflexor families on this very endpoint. Verdicts here
are read against that, not against the permutation floor — **and the discriminating feature
there was magnitude, not disjointness**: no same-mechanism pair separated by more than 0.5697°.
Any claim made here must clear that magnitude, not merely be disjoint.

⚠ **This registration does not test clinical detectability and does not bear on it.**
`KNEE_MDC_BATCHNULL_r399.json` establishes that +6.3919° falls short of the conservative knee
MDC band 7.25–7.62° (Molina-Rueda 2021 corrected for a √2 error; Geiger 2019). Confirming the
mechanism does not move that number.

⚠ **The corpus's "3.8–11.5° clinical MDC" is mis-attributed** — 3.8° is trailing limb angle and
11.5° is hip angle at toe-off (Kesar 2010). `PREREG_kinpair_r378.md` §7.4 is hashed and commits
to that wrong figure; it is not edited, and the correction is deposited separately.

---

## 5. Uninformative and prohibitions

Fewer than 4 Gate-G seeds in the `BOTH` arm makes the whole registration UNINFORMATIVE, since
the denominator of P1 is then undefined.

No substitute endpoint, no changed KV, no added arms, no promotion of a secondary, no
re-fitting of the 0.6 / 0.4 thresholds after seeing a value. If this fails it is recorded as a
failure and this registration is not amended.

---

## 6. Declared limitations

1. One reflex gain, one model, one simulator. Nothing here generalises across severities.
2. Gastrocnemius and soleus differ in more than articulation — moment arm, fibre length,
   maximum force, and their optimised baseline reflex gains all differ — so a lopsided split
   is **consistent with** the biarticular explanation without proving it uniquely.
3. Six seeds per arm; the permutation floor is 1/924 and is subordinate to §4's batch null.
4. `activation` and joint angles are clean deterministic simulator signals; the r386 audit
   found no `NoiseController` in any family. Nothing here speaks to marker error or EMG noise.
