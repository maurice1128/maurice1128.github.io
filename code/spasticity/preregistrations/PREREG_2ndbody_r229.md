# PRE-REGISTRATION — second-body replication in the 2D H0914M corpus (round 229, rev 8)

Seventh cold read of this document, seventh halt; fifteenth registration cold read on this project,
fifteenth halt. **Nine halts on this document in total.**

⛔ **Three revisions in a row shipped machinery that could not fire** — rev 3 had no reachable state
that was both computable and claimable; rev 5's rung 9 was a rubber stamp; rev 6's one substantive
addition never fired on the inputs it was written for. **Reading a ladder does not catch this.
Driving it does.** Rev 7's central change is not a rung: it is a gate that makes the ladder's
well-formedness a computation instead of a claim.

Hashed after a seventh cold read. Not edited after hashing — defects go to an errata.

---

## 0. ⛔ WHAT THE 3D DATA PREDICTS AT THE ONLY COMPARABLE SEVERITY — and what this design cannot buy

**The 2D weakness scales are ×0.800, ×0.600, ×0.200. The 3D ladder is ×0.800–×0.950. They overlap at
exactly ONE point: ×0.800** — the *severest* 3D severity.

⭐ **At ×0.800 the 3D data shows BOTH laterality channels disjoint**, and the ankle channel's gap is
its largest of all six severities:

| channel at ×0.800 (3D) | seed gap | disjoint |
|---|---|---|
| `hip_flexion_LmR` | +1.2319 | YES |
| `ankle_angle_LmR` | **+1.5039** | YES |

**So "both channels separate" is the REGISTERED PREDICTION at the only severity the two bodies share.
It is not a consolation outcome.** ⛔ Every earlier draft of rung A — *"the hip channel separates and
the others do not"* — **would have called the predicted result a failure to replicate, and would have
failed on the 3D data itself** at ×0.870 and ×0.892 too, where the ankle is also disjoint.

### 0a. ⚠ THE BOUND ON WHAT THIS REPLICATION CAN BUY, stated before the run

The fact that actually justifies preferring the hip channel is **dose-dependence**: across
×0.800→×0.950 the ankle gap runs +1.5039 → +0.5642 → +0.4093 → +0.0737 → −0.0583 → −0.5560 and washes
out, while the hip stays disjoint at all six and reaches 1/924 at every severity including ×0.950.

⛔ **That contrast CANNOT BE TESTED IN 2D AT ALL.** The mild end where the ankle washes out has **no 2D
counterpart** — the next 2D severity below ×0.800 is ×0.600, further from the wash-out region, not
nearer.

**Therefore: this experiment can test whether the channels separate in a second body. It CANNOT test
whether the hip is the better channel.** That is a real bound, it follows from the corpus and not from
the analysis, and it is registered here rather than discussed afterwards.

---

## 0b. ⛔ WHAT MAY AND MAY NOT BE CLAIMED FROM THE RESULT — fixed before the run

⭐ **Written before the run and taken verbatim from an adversarial reader who recommended running it.**
A claim list fixed in advance is worth more than any amount of post-hoc care about wording.

**MAY claim:**
- That the same two laterality channels, measured by the same statistic under the same window rule,
  separate the same two lesion types in a **planar** model with different degrees of freedom, a
  different objective, a different simulation horizon and a different CMA-ES landscape.
- That the **direction** is preserved (spastic below weak).
- **The effect magnitude and the between-seed variance in the second body** — neither of which
  anything in the corpus predicts, and the second of which decides whether §6's cut was legitimate.
- That the outcome was **pre-registered as the prediction** and the registration said so before the
  run. That is a claim about process, and it is the one thing here that is genuinely scarce.

**MAY NOT claim:**
- ⛔ **Independent replication.** Same author, same script lineage, same lab, same objective family,
  one model. The body changes; nothing else does.
- ⛔ **That the channel selection is validated.** §8, verbatim: it is *not* a second confirmation that
  selecting that channel from sixteen was cheap.
- ⛔ **That the hip is the better channel** (§0a).
- ⛔ **That the effect is absent**, if EQUIV fires. EQUIV bounds; it does not show absence.
- ⛔ **That "A" is a surprise.** It is registered as the expected outcome, and it fires at
  1.000 / 0.980 / 0.827 / 0.087 at σ = 0.1757 / 0.4309 / 0.5276 / 1.2939. **The honest sentence is:
  "We pre-registered A as the expected outcome at the only severity the two bodies share, and A is
  what we got. The informative content is the effect size and the between-seed variance, not the
  label."**

---

## 1. ⭐ THE REACHABILITY MAP IS A PRECONDITION OF HASHING

`scone/body2_reachability_r229.py` imports the **real** `decide()` — never a copy — and drives it over
**8064 COHERENT configurations** spanning the significance branch, both CI bounds relative to δ and Δ₃D, the
SMD sign, `planes_agree ∈ {True, False, None}`, the n-floor, the Gate-B rate and the partial-match
flag, plus degenerate inputs. Physically impossible combinations are REJECTED before driving (complementary p-values, SMD sign tied to the CI centre), because a witness that cannot occur is not evidence a rung is right; and each outcome's message is asserted against EVERY configuration reaching it, not one witness. It deposits `paper/BODY2_REACHABILITY_r229.json`.

**Every outcome named in this document must appear there with a WITNESS — a concrete configuration
that reaches it.** Any outcome without one is deleted or fixed before hashing.

| outcome | count |
|---|---|
| D2 | 4032 |
| F | 2016 |
| C | 672 |
| E | 672 |
| A-MIXED | 180 |
| D4 | 180 |
| B-reversed | 80 |
| A-ANKLE-ONLY | 68 |
| EQUIV | 68 |
| A | 48 |
| A-HIP-ONLY | 48 |
| D1 | 2 |

`declared but never reached: []` · `reachable but not declared: []` · **GATE PASSES**

### 1a. ⭐ The registered form of the gate is the WITNESS COLUMN, not the coverage list

**A reachability check that only reported coverage would have PASSED rev 6.** Rev 6's ATTENUATED was
reachable — its witness was `ci = −3.20 ± 0.15`, an interval lying **wholly below zero**, while the
rung printed *"the 2D effect is SMALLER than the 3D one"*. Reading that one line is what exposed the
defect.

**So the gate is not satisfied by an empty missing-list.** It requires, for each outcome, that the
witness be inspected and be *sensible for that outcome*. A future revision may not satisfy this gate
by counting.

### 1b. ⚠ WHAT THE GATE'S ATTAINABILITY FILTER ASSUMES, and what it does not certify

The generator now refuses CI half-widths outside **[0.054, 0.476]**, derived by simulation at **n = 16**
over σ ∈ {0.1097, 0.1757, 0.4309, **0.5276**}. ⛔ **The last of those is not measured.** It transports a
3.0× lesion-vs-control inflation ratio from the 3D body onto the 2D control SD; **the 2D lesion-arm
variance has never been measured.**

**So the gate's guarantee is conditional**, and the condition is now recorded in the deposit
(`attainable_halfwidth_lo/hi`, `attainability_sigmas`, `attainability_n`, `attainability_caveat`)
rather than left implicit: *every declared outcome has a witness, **provided** σ_lesion ≤ 0.5276 and
Gate-B attrition is small.* At the registration's own pessimistic σ = 1.2939 the ladder degenerates to
`{A, A-MIXED, D4}` and **EQUIV becomes unreachable** — which would invalidate §6's stated reason for
deleting five rungs. ⭐ **The run measures that σ. Until it does, §6's cut is provisional.**

### 1c. Any edit to `decide()` voids the run until the map is regenerated

The deposit records the `channels_sha256` it was driven against. **If `body2_channels_r229.py` changes
and the map is not regenerated, the run is void.** This is a hashing precondition, not advice.

---

## 2. Provenance and hashing

Revisions 1–4 asserted sidecars existed; none did. Rev 5's hashing still omitted `sto_utils.py`, which
carries **Gate B's entire operational definition**. Now hashed targets: this document and
`body2_replay`, `body2_dose`, `body2_channels`, `body2_convention`, `body2_delta`, `body2_hash`,
`body2_reachability`, **`sto_utils.py`, `dose_r174.py`**. `provenance()` records every imported module
and every input deposit.

⛔ **§8 requires the sidecars to be VERIFIED before the run, not merely to exist** —
`sha256sum -c` on every sidecar, all `OK`, as a precondition. Rev 6 required only existence.

⛔ **The INPUT DEPOSITS are now hashed too, and this was the largest remaining hole.**
`body2_channels_r229.py` reads **`DELTA_EQUIV` from `BODY2_DELTA_r229.json`** and **`DELTA_3D_HL` from
`LADDER36_r228.json`** at run time. Neither was a hashed target. **Changing `DELTA_EQUIV` from 0.65 to
1.20 flips ATTENUATED to EQUIV — the headline outcome — with no code change, no sidecar break, and
nothing on disk to record it.** Both are now in `TARGETS`.

⚠ **FOUR DEPOSITS ARE UNCOVERED, named rather than left implicit:** `BODY2_CONVENTION_r229.json`,
`BODY2_DELTA_r229.json` and `BODY2_REACHABILITY_r229.json` each record a
`script_sha256` but **none records a `prereg_sha256`**, so none can be tied to a specific revision of
this document. The three the run produces — `BODY2_DOSE`, `BODY2_CHANNELS`, `BODY2_REPLAY_LEDGER` —
do carry it through `provenance()`. **The three predate that mechanism and are not retro-stamped**,
because stamping them now would attest a relationship that was never established.

⚠ **Errata — the re-stamp gaps, BOTH of them.** The baseline was written at 20:45; a hashed target was
edited at 21:33 to fix CRLF sidecars `sha256sum -c` could not read, and the whole baseline was
re-written. **A SECOND re-stamp followed at 22:17:26**, recorded in the manifest and **absent from
rev 7's description, which named only the first.** The audit trail therefore has two gaps, not one:
20:45 → 21:33 and 21:33 → 22:17. Per #534/#539 a digest is a **baseline forward only**; per #540
nothing is written into this document.

**Rev 2 does not exist on disk** — `.bak_r229_rev2` is sha256-identical to rev 3 — so "rev 3 was a
redesign, not an edit" is **not independently checkable**.

### 2a. Disclosure

Seen: directory names, `.par` fitness fields, `config.scone`, model structure, `.sto` headers, mtimes,
gravity vectors, Gate-A distributions; `LADDER36_r228.json` for direction, Δ₃D and the variance prior;
3D channels on `R151C_s101`; reflex outputs on five non-`SG*` 2D cells; five rows of a `CMW70_s1`
`.sto`. ⛔ **CORRECTED — this sentence was true when written and is now false in this document.** §3 prints
six `SG0_DR2K000` `hip_flexion_LmR` values and `BODY2_SD_r234.json` holds them to full precision.
**What remains true, and is what matters: no cell of any LESION arm — spastic or weak, either plane —
has been inspected on any channel.** The six inspected cells are unlesioned controls in a family that
enters no comparison; `body2_channels_r229.py` reads only `SPASTIC + WEAK`.

---

## 3. ⛔ Three honest limits, in the document and not only in a deposit

1. **n = 16 is the PRE-Gate-B count.** No `.par.sto` exists yet, so post-gate arm size is
   **unmeasured**. Every power figure below **assumes zero attrition** and is an upper bound.
2. ⭐ **THE VARIANCE PRIOR IS NO LONGER BORROWED — the 2D SD is MEASURED.** Rev 8's δ and its entire
   power table descended from the **3D** body's per-seed SDs, so whether this design had 80 % power or
   20 % was decided by a number nobody had. Measured on the six **control-only** `SG0_DR2K000` cells
   (`PREREG_2Dsd_r234.md`, hashed before the replay; no lesion arm touched):

   | seed | s101 | s102 | s103 | s104 | s105 | s106 |
   |---|---|---|---|---|---|---|
   | `hip_flexion_LmR` (deg) | +0.2552 | −0.0817 | +0.0712 | +0.0563 | −0.0490 | −0.2682 |

   **σ₂D = 0.1757°**, χ² 95 % CI **[0.1097, 0.4309]**.

   ⛔ **CORRECTION — a previous revision called the borrowed prior "conservative". That was wrong,
   and it compared a 2D CONTROL arm against 3D LESIONED arms.** Like-for-like, control against
   control: **3D 0.1575 against 2D 0.1757 — the 2D body is 1.116× MORE variable.** In 3D the lesion
   arms inflate variance ~3.0× over control (spastic alone 3.73×), so the implied 2D
   spastic-vs-weak σ is near **0.528° — ABOVE the 0.4309 upper bound the recalibration used as its
   pessimistic case.**

   | σ (deg) | basis | EQUIV power at δ = 0.65 |
   |---|---|---|
   | 0.1757 | 2D control, point | **1.000** |
   | 0.4309 | 2D control, chi2 upper | **0.978** |
   | 0.5276 | implied 2D spastic-vs-weak (3.0x transport) | **0.892** |
   | 1.2939 | implied, on the chi2 upper | **0.012** |

   ⭐ **Every row is now DEPOSITED** (`BODY2_POWERTABLE_r238.json`), not hand-carried. An earlier
   revision printed two rows no script produced and a third that disagreed with its own deposit.

   ⚠ **The measurement stands; the inference from it did not.** Power at δ = 0.65 is adequate at the
   implied lesion-arm σ (0.906) but **the lesion-arm variance has NOT been measured** — only the
   control arm has. Every figure here is conditional on the 3D inflation ratio transferring.

3. **The reachability map is a precondition of hashing** (§1b).

---

## 4. What this design can and cannot conclude

⛔ **The body-specificity claim is DELETED from the outcome set.** Rev 5's rung fired **100 % on a true
zero AND 100 % on a genuine quarter-magnitude effect**, at every variance scenario — no discrimination
at all. Accepting a null requires excluding effects near **zero**; that rung excluded the 3D point
estimate instead. **A design that cannot support a conclusion must not list it as an outcome; that is
how "we failed to detect" becomes "it is not there."**

**δ = 0.65°** registered (§3). If the TOST passes, the design may say **any 2D effect is smaller than
0.65°, about a quarter of the 3D effect.** It may **not** say the effect is absent.

**Δ₃D = +2.585°**, range **[2.490, 2.728]** — the HL shifts of W870/W915/W892. ⚠ **The range is used,
not merely computed:** every outcome depending on Δ₃D is re-evaluated at both endpoints and the
deposit records whether the label is stable across them. Rev 6 computed the range and never touched it.

---

## 5. Measurement

**Statistic:** cycle-averaged (L−R) in degrees over left heel-strike cycles fully inside
**[1.00, 8.00] s**, last dropped. **Adjudicating statistic:** standardised mean difference on
`hip_flexion_LmR`; HL shift with percentile bootstrap CIs (95 % for attenuation, **90 % for TOST**;
B = 10,000, seed 229229). Disjointness is reported and **adjudicates nothing**.
**α = 0.025 per direction, total 0.05.** Null: `math.comb` decides before any loop; exhaustive if
≤ 200,000, else Monte Carlo B = 100,000, seed 229229, `p = (k+1)/(B+1)`.

⚠ **Gate B's operational definition lives in `sto_utils.py` and is stated here, not only hashed:**
heel strikes are upward crossings of vertical GRF with **`min_stance = 0.15 s`** and a **0.3 s
bounce-merge**; thresholds 0.05 (body-weight-normalised) or 20 N. **Changing `min_stance` changes
usable-cycle counts → Gate B → arm sizes → the imbalance rate → the outcome.**

**Gate A** at fitness < 1.5 (`.par` **field 3**; SCONE writes `<gen>_<median>_<best>`): SG0
[0.588, 1.043], **78/78 at every threshold 1.1–10.0 — inert on the primary plane**; SG2
[0.574, 1.154], **76/78 at 1.1**, so not strictly inert there.

**Gate B**: t ≥ 8.00 s and **≥ 2** usable cycles, applied to the control arm too.

⛔ **F6 — replay failures are QUARANTINED, and membership comes from the LEDGER, not the filesystem.**
An absent or empty `.sto` is an infrastructure non-result (#205's `E5_STO_0`), not evidence the gait
failed. Rev 6 booked it as Gate-B attrition, so a `sconecmd` crash could inflate the imbalance rate and
VOID the null via rung F. **Rev 7 fixed the booking but decided membership with `os.path.exists`,
which is worse: DELETING one `.sto` moved a spastic exclusion rate from 0.250 to 0.200 and converted a
voided null into a live substantive rung, with nothing on disk recording it.** Membership now comes
from `BODY2_REPLAY_LEDGER_r229.json`'s `E5_STO_0` entries. **The ledger is the record; the filesystem
is not.** With no ledger the run halts rather than falling back.

⛔ **THE DOSE CONSTRUCTION CITES A SCRIPT THAT NOW CARRIES A PUBLIC ERRATA, AND THE RELATIONSHIP IS
STATED RATHER THAN LEFT BARE.** `dose_r174.py` reads `<muscle>.ce_vel_norm`; SCONE's `MuscleReflex`
reads `<muscle>.V`, and **`V = 10.000000 × ce_vel_norm`**. In the 3D corpus the spastic dose was
therefore computed at one tenth of the reflex's true input, the matching scale `s*` is **negative**
once corrected, and every "dose-matched" claim built on it is void
(`ERRATA_dose_scale_r231.md`, 2026-08-16).
⭐ **This 2D design is UNAFFECTED, and not by luck.** It uses `fiber_velocity_norm × 1.0`, established
here from `RV / (KV · fiber_velocity_norm) ≈ 1.0` on 2D cells and confirmed from the opposite direction
by `V / fiber_velocity_norm = 1.000000` on 3D cells. **The reflex input is `fiber_velocity_norm` in
both engines**; `ce_vel_norm` is a 0.1-scaled variant present only in Hyfydy files, and `dose_r174.py`
picked it from the two available. **What is transcribed here is the FORMULA, evaluated on the correct
channel.** A reader who checks the citation will find a script with an errata against it; this
paragraph is why that does not propagate.

⛔ **F7 — the `.sto` is selected by the registered rule.** Rev 6 took `sorted(glob("*.par.sto"))[-1]`,
whichever filename sorts last. The phenotype is now the replay of the **lowest field-3 `.par`**, which
is the rule the replay script uses; a mismatch yields `REPLAY_MISSING` and quarantine.

**Constants** are read and asserted from **every cell** in each family, not one probe. **Δ₃D and δ are
read from their deposits at run time** (`LADDER36_r228.json`, `BODY2_DELTA_r229.json`), not
hand-transcribed as in rev 6.

### 5a. Supporting facts, stated at the strength they actually have

- **The velocity convention is ×1.0**, measured from `<m>.RV` against `KV·max(0, fiber_velocity_norm)`
  in five non-`SG*` cells at four declared `KV` — **75 variants, median 0.981, range [0.480, 1.061]**.
  The two discrimination quantities are now distinguished: worst-**fitting** variant vs ×1.0 =
  **2.08×**; minimum separation from ×0.1 = **4.80×**, from ×10 = **9.42×**. Rev 5 reported `min` for
  both and mislabelled the result "worst-case".
  ⚠ **The mask levels are not equally informative and the spread is driven by the lossy ones:**
  mask 0.00 keeps **30/30** variants with range **[0.849, 1.061]**; mask 0.05 keeps 30/30, range
  [0.486, 1.057]; **mask 0.20 keeps only 15 of 30**, range [0.480, 1.030]; **mask 0.50 keeps none.**
  The tightest evidence comes from the variant that discards nothing.
- ⚠ **`.F ≡ mtu_force_norm` is a 3D check that CANNOT be repeated in the 2D body.** It was verified on
  `R151C_s101`, where both channels exist, as **aggregate agreement at zero lag** — mean absolute
  difference 2.4 × 10⁻⁵ (`soleus_l`) and 7.6 × 10⁻⁵ (`tib_ant_l`) on signals of range ~0.2, with
  isolated larger excursions. It is **not** a bit-identity, and in 2D `tib_ant_l.F` does not exist, so
  **the substitution is transferred on the 3D check alone and cannot be confirmed where it is used.**

---

## 6. THE LADDER, CUT TO WHAT THE DATA CAN REACH — strict precedence, first match wins

⛔ **Rev 9 declared fifteen rungs. Five could not fire at any σ this corpus supports and are
DELETED, not carried:** `ATTENUATED`, `ATTENUATED-reversed`, `CONSISTENT-WITH-3D`, `D5` and the
old wide-interval `D4`. A non-significant SMD bounds |HL| small enough that the 90 % interval always
lies inside ±δ, so **EQUIV absorbs the entire non-significant branch before any of them is reached.**
⭐ *A four-way partition the data can land in one cell of is theatre. The rungs below are the ones a
2D result can actually produce.*

1. **D1** — no primary comparison object (no pair, or no HL interval).
2. **D2** — fewer than 5 cells per arm after Gate B.
3. **F** — Gate-B exclusion rates differ by > 20 points. The null is **void**.
4. **E** — planes disagree in SMD sign for the same pair, SG2 supported.
5. **C** — relative mean-dose difference > 25 %. Suggestive, never the replication.
6. **B-reversed-BOTH** — **both** channels separate in the **opposite** direction (p < 0.025 each).
7. **B-reversed** — the hip separates in the opposite direction.
8. **B-reversed-ANKLE** — the ankle separates in the opposite direction.
   ⭐ **All three are evaluated BEFORE the A-family**, and the ankle arm is new. Rev 9 placed hip
   reversal after, so a *significant* hip reversal co-occurring with a forward-separating ankle was
   relabelled `A-ANKLE-ONLY` while the message asserted the hip "does not separate" at
   `p_rev = 0.005`. ⛔ **Rev 10 fixed that for the hip and left it for the ankle**, so a significant
   ankle reversal at p = 0.001 was booked `A-MIXED` — *"neither significant nor bounded, no claim
   about the quiet channel"* — about a channel separating at p = 0.001. **It is not exotic: the 3D
   ankle gap goes NEGATIVE at ×0.915 (−0.0583) and ×0.950 (−0.5560).**
9. **A** — **both** `hip_flexion_LmR` and `ankle_angle_LmR` separate in the predicted direction.
   **The replication**, and what the 3D data shows at ×0.800.
10. **A-HIP-ONLY** — the hip separates **and the ankle's HL 90 % CI is bounded inside ±0.65°**.
11. **A-ANKLE-ONLY** — the ankle separates **and the hip's HL 90 % CI is bounded inside ±0.65°**.
   The site channel transfers and the compensation channel is bounded.
12. **A-MIXED** — one channel separates and the other is **neither significant nor bounded**.
    **No claim may be made about the quiet channel.**
13. **EQUIV** — neither separates and **both** are bounded inside ±0.65°.
14. **D5** — HL 95 % CI lies entirely **above** Δ₃D with a non-significant SMD. Internally
    inconsistent; investigated, not reported.
15. **ATTENUATED-reversed** — HL 95 % CI lies entirely **below zero**. The 2D effect runs opposite
    to the 3D one, SMD non-significant.
16. **ATTENUATED** — HL 95 % CI is **positive** and bounded above by Δ₃D. Smaller than the 3D
    effect, and **not absent**.
17. **CONSISTENT-WITH-3D** — HL 95 % CI wholly positive and reaching or exceeding Δ₃D. **The
    interval** is consistent with a 3D-sized effect.
18. **D4** — neither separates, the interval spans zero, and at least one channel is unbounded.
    Uninformative.

⛔ **RUNGS 14–17 WERE DELETED AT r237 AND ARE RESTORED HERE. The premise for deleting them failed.**
They were cut on the argument that a non-significant SMD always bounds |HL| inside ±δ, so `EQUIV`
would absorb the whole non-significant branch. §1b registered that cut as **provisional pending a
measurement of the 2D lesion-arm variance**. **The measurement came back: the primary-channel HL 95 %
CI is [−1.3914, −0.2473], half-width 0.572, ABOVE the 0.476 the attainability filter had called the
ceiling.** In that regime `EQUIV` is unreachable and these four rungs are precisely what the
non-significant branch requires. ⭐ **The advisory filter flagged rather than refused, and the flag
fired — demoting it from a refusal is why the run produced a measurement instead of a halt.**

⛔ **Rungs 8 and 9 require a BOUND, not a failure.** Rev 9 licensed "the ankle does not transfer" on a
bare `p ≥ 0.025` — **the same "we failed to detect" becomes "it is not there" structure §4 deleted an
entire outcome to prevent.** With n = 16 and σ₂D = 0.1757, a bare non-significant result means only
*"below about 7 % of its 3D value"*, which is far weaker than the words suggest. The equivalence
condition makes the claim quantitative or `A-MIXED` refuses it.

## 7. Exchangeability, multiplicity, and design

Gate B attrition breaks exchangeability and biases the null toward non-separation. **If F fires the
null is void** — which is why F precedes every substantive rung. The cycle-count-matched analysis is
**descriptive only and adjudicates nothing**: it selects on a post-treatment variable, and
`dose_r174.py`'s own header says matching on a child of achieved gait "partially blocks the very path
L → G → Y that the experiment measures."

⛔ **F10 — the channel factor is no longer double-counted.** `familywise_p` is already a max over the
three channels, so the secondary Bonferroni is over **pairs only**. Rev 6 multiplied by
pairs × 3 channels.

**Primary plane SG0** — level ground (gravity `0 −9.80665 0` = 0.0000°; SG2 = 2.0000° uphill,
secondary; SG5 = 5.0000°, excluded, 24/78 admitted). The swap from SG2 was made because that choice
was unpriced, **not because SG0 looked better — nothing had been looked at.**
**Pairs:** `{DR2K050, DR2K075, DR2K200} × {PAR20, PAR40, CMW80}`; primary = overlapping pair with ≥ 5
cells per arm minimising **relative** mean-dose difference; leave-one-out overlap must be unanimous.

---

## 8. What a 2D result replicates, deposits, and the tie-break

**A 2D result replicates the channel's BEHAVIOUR, not the SELECTION PROCEDURE.** The 3D result priced
the choice of `hip_flexion_LmR` against a 16-channel family. That pricing cannot be reproduced here,
because this body does not have sixteen channels to choose from. Whatever the 2D number turns out to
be, it is evidence that the channel behaves the same way in a second body; it is **not** a second
confirmation that selecting that channel from sixteen was cheap. *(Retained verbatim from rev 1.)*

**Deposits:** `BODY2_REACHABILITY_r229.json`, `BODY2_CONVENTION_r229.json`, `BODY2_DELTA_r229.json`,
`BODY2_DOSE_r229.json`, `BODY2_CHANNELS_r229.json`, `BODY2_REPLAY_LEDGER_r229.json`,
`BODY2_HASHES_r229.json`, and **`LADDER36_r228.json`** — an input, not an output, but it fixes Δ₃D and
the variance prior and was absent from rev 6's list.

⛔ **Preconditions of the run — EXECUTABLE, at the top of `main()`, not asserted in prose.**
`preconditions()` runs before any cell is read and halts on failure: **(a)** every hashed target in
`BODY2_HASHES_r229.json` is re-hashed and compared, and a mismatch or missing target voids the run;
**(b)** the reachability map must report `GATE_PASSES` **and** its recorded `channels_sha256` must
equal this file's current digest, so a stale map cannot pass; **(c)** machine-wide `sconecmd` must be
0 or our cells give way.
⚠ *Rev 7 required all three in the document and checked only (c) in code. A precondition that lives in
prose is a hope.*

⛔ **Where this document and the code disagree, the RUN IS VOID and the disagreement goes to an
errata.** The document governs; divergence is a defect in the run, not an amendment to the plan.
