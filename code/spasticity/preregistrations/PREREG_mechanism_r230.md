# PRE-REGISTRATION — the two-window mechanism (round 230, rev 3)

Rev 1 proposed a stance mechanism and was declared refuted. **That declaration was wrong.** Rev 2 was
built on it. Rev 3 is written from `STANCE_TEST_r231.json`, the measurement that should have been made
before either.

Not hashed until cold-read again.

---

## 0. ⚠ Status of every claim here — at the claim, not in a limitations paragraph

Every arm was **RE-OPTIMISED** after its lesion. What is measured is **what the optimiser found for
this model**. The clinical reading is a **hypothesis this generates**, not a result it establishes.

---

## 1. ⛔ What was actually measured, replacing rev 2's kill sentence

**Rev 1 was declared refuted on a statistic that did not test it.** The test compared *where the
lengthening impulse falls* (0.26 soleus / 0.12 gastroc in stance, against stance occupying 0.59 of the
cycle) with a duration fraction. Rev 1 predicted **resistance to dorsiflexion**, which that comparison
cannot address.

**The correct test — added plantarflexor force against the local baseline, six control cells,
corrected ×1.0 scale — PARTIALLY VINDICATES rev 1.**

| window | added force | local baseline | **ratio** | frac of cycle peak | ankle |
|---|---|---|---|---|---|
| **LR, 0–15 %** | 373.7 N | 258.3 N | **1.447** | 0.127 | **dorsiflexing** (+0.617) |
| **ES, toe-off + 15 %** | 1957.5 N | 178.2 N | **10.985** | 0.663 | **dorsiflexing** (+0.910) |

⭐ **The ratio is the robust quantity and the newtons are not, and that belongs here rather than in a
note.** `added/baseline` reduces algebraically to `du/u`, which cancels the force-gain proxy entirely —
so **1.447 and 10.985 are solid**. The absolute newton figures carry `gain = f / max(u, 0.01)`, which is
unstable exactly where excitation is lowest, and the 2949 N cycle peak sits at `u = 0.0200`. **The
absolute early-swing magnitude is probably inflated; the ratios are not.**

**The honest shape is neither rev 1 nor rev 2: the reflex acts in TWO separate dorsiflexion windows,
and early swing is much the larger** — by **7.6× on the robust ratio** and 5.2× on the absolute
reading. Per-bin: active 0–15 %, **silent 15–60 %**, large 60–80 %.

⚠ **S3 ("not phase-localised") failed to fire only because the two windows are 5.2× apart rather than
within 2×.** The phase story is **a matter of degree, not a clean dichotomy**, and it was close to
collapsing entirely.

⛔ **The ×11.3-versus-×3.7 sub-phase figure that reopened this does not reproduce.** Measured:
**1.45 in loading response against 11.0 in early swing** — the reverse.

⛔ **AND THERE IS A THIRD REGION THAT "TWO DORSIFLEXION WINDOWS" DOES NOT COVER.** Bins 80–85 %
carry **271.2 N** of added force — *more than the 243.4 N at 0–5 % that §1 counts as an active
window* — and **`d(ankle)` there is NEGATIVE: the ankle is PLANTARFLEXING while the reflex adds
force.** That is not possible under a pure stretch account, it weakens the "two dorsiflexion
windows" framing, and **it undercuts §3's derivation of the dorsiflexion sign from the coincidence
of added force with positive `d(ankle)`** — the coincidence does not hold in this region. Stated
rather than omitted; it is unexplained and is carried as such.

---

## 2. H1, NARROWED — and the narrowing is on the record

**Both lesions load the swing phase**, where the reflex is dominant and the weakened `tib_ant_l` cannot
supply the dorsiflexor drive that toe clearance requires. **The plantarflexor reflex ADDITIONALLY acts
in loading response**, where dorsiflexor weakness also acts eccentrically.

⛔ **Rev 2 did not predict the loading-response window and must not be read as having done so.** Rev 2
asserted the reflex fires in early swing *because stance was refuted*; the stance window is a **new
measured finding that rev 2 excluded**. The narrowed H1 does not reabsorb it as a success.

**If H1 explains the parallelism finding, it now does so through two shared windows rather than one.**

---

## 3. ⚠ Declared deviation from a registered procedure — carried forward, not buried

`PREREG_stance_test_r231.md` §2 said the ankle sign convention would be **read from
`H1922v7b3.hfd`** before any number was interpreted. The `.hfd` gives
`ankle_angle_l source = ankle_rz_l`, which establishes that left and right are **unmirrored** but
**not which sign is dorsiflexion**.

The convention was instead **derived**: plantarflexors lengthen only in dorsiflexion, and the added
force coincides with positive `d(ankle)`. **The derivation is sound and the internal check is good. It
is still a deviation from a registered procedure and it stays visible.**

---

## 4. ⛔ Two DIFFERENT quantities have been called `hip_flexion_LmR`

- **EXCURSION-LmR** — `rom(hip_flexion_l) − rom(hip_flexion_r)`, where `rom` is the mean per-cycle
  **peak-to-peak excursion**. This is what `LADDER36_r228.json` deposits and what the **−2.105
  headline and all disjointness claims** are.
- **ANGLE-LmR** — the cycle mean of the point-wise difference `hip_flexion_l − hip_flexion_r`.

**They are not the same quantity and are opposite in sign for every weakness arm.** Rev 2's script
computed ANGLE-LmR while citing EXCURSION-LmR results.

⛔ **P3, P4 and P6 test ANGLE-LmR, NOT the paper's endpoint — and the reason is that they cannot test
the endpoint.**

**`EXCURSION-LmR` is a per-cycle SCALAR.** It is one number per cycle — a difference of two
peak-to-peak ranges. **It has no phase distribution and does not decompose into stance and swing
parts, so `stance_share` on it is a category error, not a bug.** No repair makes it computable; the
quantity simply does not have the structure the statistic requires.

**So the mechanism line uses the phase-resolved ANGLE deviation, which is computable.**

⛔ **STATED AT THE PREDICTIONS, NOT IN A LIMITATIONS NOTE: `ANGLE-LmR` is a DIFFERENT QUANTITY from the
paper's endpoint, and the two are opposite in sign for every weakness arm. A mechanism result on
`ANGLE-LmR` DOES NOT TRANSFER to `EXCURSION-LmR` without an argument that has not been made and is not
attempted here.** Whatever P3, P4 and P6 return explains the behaviour of a channel the paper does not
report. **That is a real limitation of this mechanism line and it is better stated than engineered
around.**

Any `EXCURSION-LmR` figure is reported under its own name, per cycle, and never given a phase share.

---

## 5. Predictions and kill conditions

⚠ **Phase-normalise before averaging.** A 0.4–0.7-point shift in stance fraction alone moves a
phase-share statistic with the kinematics untouched. Every phase statistic is computed **per cycle on
a normalised 0–100 % axis**, then averaged across cycles — never by pooling raw samples.

⛔ **P1 IS DELETED. Three revisions, three unfailable versions.**

Rev 1's P1 asked whether swing held the majority of an impulse already measured at 0.74/0.88. Rev 2's
was the same test reworded. **Rev 3's — `du/u` in ES exceeding LR by ≥ 2× — was written after the
statistic had been measured on those same six cells at 7.46–7.71, and the 2× threshold was chosen
knowing the answer was 7.6×.** A threshold selected from the observed value is not a prediction.

**No principled threshold exists.** Nothing outside this corpus fixes how much larger early-swing
reflex action *should* be than loading-response action, so any number would be fitted. **Deleting it
is the honest move.**

⚠ **Consequence, stated rather than engineered around: H1-REFUTED is no longer gated on P1, and the
outcome set must say plainly what can still refute the account.** See §6 — refutation now runs through
**P3 and P4**, which compare two arms against each other and can fail in either direction without any
threshold chosen after the fact. **If P3 and P4 both hold, no prediction in this registration can
refute H1**, and that is a limitation of the design rather than a property of the world.

**P2 — realised firing differs from counterfactual firing.** In spastic cells the `RV` distribution
over normalised phase differs from the control-trajectory `du` distribution by a measurable shift.
⛔ *Killed by:* no measurable difference → outcome **AVOIDANCE-NULL**; the optimiser absorbed the
reflex rather than relocating the gait.

**P3 — weak-arm ANGLE-LmR deviation is swing-concentrated** *(ANGLE, not the paper's endpoint — §4)*, `stance_share < 0.5` in ≥ 4 of 6
severities. ⛔ *Killed by:* stance concentration, which breaks the shared-phase account.

**P4 — spastic ANGLE-LmR deviation is ALSO swing-concentrated** *(ANGLE, not the paper's endpoint — §4)*. ⛔ *Killed by:* stance
concentration. **This remains the test most likely to fail**, and given §1 it may now fail *legitimately*
— the reflex does act in stance.

**P5 — ankle signature:** reduced swing dorsiflexion in both arms relative to control, by opposite
routes. ⛔ *Killed by:* the arms differing in direction.

**P6 — contralateral compensation:** the right hip's swing deviation is opposite in sign to the left's.
⛔ *Killed by:* both limbs deviating in the same direction.

---

## 6. Outcomes — exhaustive by construction, evaluated in order

1. **M-UNDERPOWERED** — < 4 of 6 seeds usable in any arm, or < 2 cycles in a majority.
2. **H1-REFUTED** — P1 fails. No phase account survives; the paper reports a measured separation with
   an explicitly unknown cause. **Ships at full strength.** *(Now reachable — see P1.)*
3. **PHASE-SPLIT** — P3 and P4 disagree: the arms load different phases. The shared-phase account fails
   and the parallelism finding keeps its present status as an unexplained regularity.
4. **AVOIDANCE-NULL** — P2 fails while P1, P3, P4 hold. Informative, not a failure.
5. **H1-SUPPORTED** — P1, P2, P3, P4 hold.
6. **H1-PARTIAL** — anything else: any other combination of P1–P6 outcomes, named explicitly in the
   report. ⚠ **This rung exists so the outcome set is exhaustive**; rev 2's set had no home for the most
   likely actual result.

---

## 7. ⛔ The open anomaly — and a correction to my own claim

**Hip, EXCURSION-LmR:** `r(scale, mean) = +0.8745`. **The mildest weakness produces the largest
deviation.**

⛔ **I previously claimed the speed result independently agreed. It does not, and the ⭐ is withdrawn.**
Measured directly:

| arm | ×0.800 | ×0.870 | ×0.892 | ×0.900 | ×0.915 | ×0.950 |
|---|---|---|---|---|---|---|
| mean speed (m/s) | 1.03998 | 1.03471 | 1.03316 | 1.03341 | 1.03123 | 1.02671 |

`r(scale, speed) = −0.9803`.

⛔ **CORRECTION TO MY OWN §7.** A previous revision stated control mean speed as **1.03150** and
concluded deviation from control was **non-monotone**. **Both were wrong.** `SPEED_LADDER_r217.json`
contains **no control arm**, so that figure was unsourced; it came from computing `com_x` over
**[1.00, 9.73]** while the registered method is **`pelvis_tx` displacement over the GRF-delimited
window [1.00, 13.58]** (`SPEED_LADDER_r217.json` → `method`). Recomputed under the registered method
on the six `R151C` cells: **control mean = 1.02173 m/s** (range 1.01601–1.02541).

**Control sits BELOW the entire weak range** (slowest weak arm ×0.950 = 1.02671), so deviation from
control is **MONOTONE**: ×0.800 **+0.01825**, ×0.870 +0.01298, ×0.892 +0.01143, ×0.900 +0.01168,
×0.915 +0.00950, ×0.950 **+0.00498**. **The SEVEREST weakness deviates most — the OPPOSITE ordering to
the hip result.**

⭐ **But the conclusion does not rest on the control figure, and the better argument needs no control
arm at all.** Within-arm seed spreads from the deposit are **0.00666–0.01798 m/s**, and several —
×0.800 at 0.01798 and ×0.900 at 0.01591 — **exceed the 0.01327 between-arm spread of means.** That is
the conservative comparison besides: a spread of *means* against a spread of *singletons*. **The
between-arm speed signal is at or below within-arm noise.** Speed is also a child of achieved gait, so
it is not an independent readout in any case.

**Net: speed points the opposite way to the hip ordering, and it is noise-scale. It corroborates
nothing in either direction.**

⚠ *The relayed figures −0.769 and "0.6 % spread" do not reproduce either; measured −0.9803 and 1.28 %.*

**Registered alternative account, to be tested rather than assumed:** fitness degrades monotonically
with severity, so **a severe deficit forces a global re-solve while a mild one leaves the control-like
solution intact**, and a mild lesion's effect then shows up undiluted in a single channel. ⭐ **This is
consistent with H1 and explains the hip ordering without contradicting it.** It is registered
alongside the anomaly, not in place of it, and it is **reported under every outcome**.

---

## 8. Corpus, selection and quarantine

Arms: `R151C`; `R151S` (**KV = 0.050**, read from `config.scone` and asserted); `R151W` ×0.800,
`R174W870`, `R174W892`, `R169W090`, `R174W915`, `R169W095`. Six seeds each.

⛔ **Cell resolution is not `sorted()[0]`.** Where a tag matches more than one directory, the cell is
the one with a terminal `history.txt` **and** a non-empty `.sto`; a duplicate resolving to an empty
directory is a **quarantine**, reported by name, never a silent drop.
⛔ **Exact fitness ties in `.par` field 3 are resolved by lowest generation, and the tie is reported.**
⛔ **`E5_STO_0` quarantines come from the replay ledger, not from `os.path.exists`.**
⚠ **`W950` stands at exactly four usable seeds** — on the underpowered boundary by accident, not by
design. Its n is reported beside every figure that uses it.

`.sto` selection: replay of the lowest field-3 `.par`. Window [1.00, 9.73]; left heel-strike cycles
fully inside, last dropped; stance = `leg0_l.grf_norm_y > 0.05`. `RV` exists **only in spastic cells**,
so P2 is spastic-only by construction.

---

## 9. Deposits

`paper/MECHANISM_r230.json` — per cell and phase-normalised bin: counterfactual and realised firing,
their difference, `stance_share` per arm per channel for **EXCURSION-LmR**, per-limb deviations, cycle
counts, ties and quarantines by name, the derived ankle convention with its derivation, the asserted
`KV`, the severity anomaly with the speed correction, and the outcome the ladder selects.

Script `scone/mechanism_r230.py` — **stale: written against rev 1 and must be rewritten before use** —
recording its own sha256, this registration's, and every module and input it reads.

⛔ **Where this document and the code disagree, the RUN IS VOID.** The document governs.
