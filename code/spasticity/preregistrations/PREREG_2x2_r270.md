# PREREG_2x2_r270.md — the crossed design: lesion TYPE against MUSCLE GROUP

## REVISION 3

| rev | sha256 | status |
|---|---|---|
| 1 | `622dd809af19bd57587b2e74147b57a2f10ae6ef02782c69a0069a4867c1b9b3` | superseded |
| 2 | `cb9925eac6e5895415c6decb6be8255877a8ba21334f3153a6b953aa61151393` | superseded |
| 3 | `09180446d26c2f5d6b9eba78b13b4f704bf0d1253d951fcc88c2a2ad355d775e` | superseded |
| 4 | `25b9a12f89bd9591a5f291f01c9022a329a71ebc2c867987709188734b06a17e` | superseded |
| **5** | **this document** | current |

⭐ **NO CELL HAS RUN. NO RESULT EXISTS.** *A registration whose result has been produced is frozen at
that digest; this one has produced nothing, so revision is legitimate — but each revision is recorded
with its predecessor's digest and what changed. **That distinction is what r229 lost.***

**REV 5 — two decisions, taken on arithmetic done before any 2 x 2 data exists.**

1. ⭐ **SEED COUNT RAISED TO n = 14 PER ARM.** *144 new cells, **5.90 h** at 147.6 s/cell (§2c).*
2. ⛔ **δ IS RE-REGISTERED AS A FIXED MULTIPLE OF THE CONTROL σ — 2.534 σ — AND NO LONGER TRACKS THE
   CONTROL RANGE.** *The range's expectation grows with n, so the old definition made the equivalence
   margin move with sample size: at n = 14 the control band is **34 % wider** than at n = 6, which
   tightens the interaction test and loosens every band-based rung at the same time. **A margin defined
   by an estimator whose expectation depends on sample size is not a margin.** The defect existed at
   n = 6; it simply never varied. Numerically δ is unchanged — frozen at the sixteen n = 6 band
   widths — but it is now invariant to n (§6b).*
3. **§6a's channel count corrected: 8 of 16 clear the separation threshold, not 7** — `ankle_angle_l`
   at 0.984 δ was missed counting by eye. *The "only 3 clear the ratio boundary" figure stands at
   n = 6 and becomes **6** at n = 14.*

**REV 4 responded to the reachability gate of §8, which FAILED on its first run against rev 3's
ladder.** *5,088 of 190,512 attainable configurations — 2.67 % — reached no rung: §6's ladder was not
exhaustive. **The gate was not patched to pass.** A terminal `INCONCLUSIVE` rung is added (§6), and the
detectable interaction effect size is registered next to α (§6a). `NEITHER` is deliberately NOT widened:
1,296 of the uncovered configurations have arm means **outside** the control band, and calling those
"nothing happened" would be false.*

**Rev 3 responded to a five-way parallel audit of rev 2. What changed then:**

1. ⛔ **Both footing constants were wrong and had no source.** *Rev 2 used DF 129.2395 and PF 663.4508,
   computed without the validated drop-last-cycle rule. **Corrected to DF 125.85307120 and PF
   684.78256379**, each with its source, and every derived figure recomputed (§2).*
2. ⛔ **Two statements about cardinality were false** — `SPASTIC-PF` does not exist at one gain (§1).
3. ⛔ **f = 0.40 was claimed to extend beyond the existing range; it does not** (§2b).
4. ⛔ **The dose grid closed the 2 × 2 at one dose of three; it now closes at all three** (§2b).
5. ⛔ **The heading criterion was collinear with the reflex arm, so its stratification was undefined.
   The binary flag is withdrawn** (§4).
6. ⛔ **The self-test in the gating script could not fail. Rebuilt** (§2a).
7. ⛔ **§6 registered no α, no channel list, no multiplicity rule, no equivalence margin and no rung
   order, and two rungs fired on the same case. All specified** (§6).
8. ⛔ **A reachability deposit and gate are now required before any cell runs** (§8).
9. **Cost arithmetic corrected, and the add-versus-remove asymmetry added to the limits** (§0, §7).

---

## 0. Why this design, and why 3D

⛔ **Every claim about lesion TYPE in this project has been defeated by the same gap: no cell crosses
site with mechanism.** *The corpus holds a plantarflexor reflex and a dorsiflexor weakness, so any sign
difference may be plantarflexor-versus-dorsiflexor rather than reflex-versus-weakness (§M3 item 4).*

**Body chosen on measured cost** (`COST_r270.json`): *3D `ModelHyfydy` **147.6 s/cell** against 2D
`ModelOpenSim4` **1646.1 s/cell** — 11.2× — at equal generations and half the simulated duration in 2D.*
⚠ *An earlier plan had 2D first at "0.54× the cost". Wrong by ~20×, withdrawn.*
⛔ **2D also has no frontal or transverse DOF (§M1), so it cannot see `pelvis_rotation`, the largest
displacement in this corpus. A screen blind to the biggest effect is not a screen.**

**Cost of this design: 144 new cells at n = 14.** *At the corpus-wide 147.6 s/cell, **5.90 h**
sequential.*
⚠ **RUN YIELD, BINDING ON THE RUNNER AND NOT ON GOOD INTENTIONS: if the user's own SCONE work is
running, our cells give way.** *The launcher checks for competing SCONE processes before each cell and
suspends rather than competing. This is a property of the runner, not a note in a registration.* ⚠ **Rev 2's "36 cells = 2.04 h" mixed a 36-cell count
with the 204 s control rate; 36 × 147.6 s is 1.48 h. Corrected.** *Destabilising arms cost less, because
trials terminate early.*
⚠ **`COST_r270.json`'s 74-cell census omits `R172W080` and `R172W090`; the per-cell rates above are
unaffected, and the census is corrected when that deposit is next written.**

## 1. The four cells of the 2 × 2

| | **plantarflexors** (`soleus_l`, `gastroc_l`) | **dorsiflexor** (`tib_ant_l`) |
|---|---|---|
| **reflex** | **SPASTIC-PF** — exists at **three gains** | ⭐ **SPASTIC-DF — NEW** |
| **weakness** | ⭐ **WEAK-PF — NEW** | **WEAK-DF** — exists at six rungs |

⛔ **CORRECTED AT REV 3. `SPASTIC-PF` is NOT a single condition.** *KV 0.050 (6 seeds, admitted), KV
0.150 and KV 0.400 (6 seeds each per optimisation path, 24 cells, gate-failed but on disk with full
91-line histories) — `GAIN_LADDER_r264.json`.* ⚠ **Rev 2 wrote "exists (`R151S`, KV 0.050)" and "no arm
is a single condition again", and both were false against a deposit this project made two rounds
earlier. The cardinality confound was already broken on the reflex-PF axis before this design.**

**Implementations:**

- **WEAK-PF** — `max_isometric_force` scaled on **both** `soleus_l` and `gastroc_l` by the same factor.
  *Model-file edit only, no controller change, exactly as `WEAK-DF` is implemented.*
- **SPASTIC-DF** — a `ConditionalController` / `ReflexController` block on `tib_ant_l` **byte-matching
  the existing `SpasticL` block** in every field but target: `delay = 0.020`, `allow_neg_V = 0`,
  `legs = left`, `states = "EarlyStance LateStance Liftoff Swing Landing"`.

⭐ *Audit finding retained: the existing lesion configs are clean — a diff of control against spastic
returns only the signature prefix and the 20-line controller block, and the `.hfd` is byte-identical.*
⚠ *`SpasticL` targets two muscles; `SPASTIC-DF` targets one. An anatomical asymmetry, not a design
choice, and not removable.*

## 2. ⛔ THE DOSE FOOTING — corrected constants, and what cannot be matched

**Validated path** (`FOOTING_r272.json`, `scone/footing_r272.py`): *`body2_dose_r229.py`'s `cycles_of()`
— cycles wholly inside [1.00, 13.58], **then drop the last**. Omitting the drop is what put rev 2's
constants out.*

| group | `Fmax` | **achieved mean force** | source |
|---|---|---|---|
| plantarflexors (`soleus_l` + `gastroc_l`) | 5790.0 N | ⭐ **684.78256379 N** | `FOOTING_r272.json`; no prior deposit carried it |
| dorsiflexor (`tib_ant_l`) | 1759.0 N | ⭐ **125.85307120 N** | `VERIFY_F5_r231.json` / `DOSE_r174.json` → `tib_ant_mean_force_N`, **reproduced here to zero error** |
| **ratio PF / DF** | **3.2916** | ⛔ **5.44113** | |

⛔ **THREE FOOTINGS, NO TWO MATCHABLE SIMULTANEOUSLY:** *(1) absolute newtons; (2) fraction of the
group's own `Fmax`, differing from (1) by **3.2916×**; (3) fraction of the group's own achieved
operating force, differing from (1) by **5.44113×** and from (2) by **1.653×**.*

⭐ **REGISTERED CHOICE: footing (3)**, references frozen at the two values above. *Argument, in advance:
the question is whether type separates independently of muscle group, so dose must be expressed in the
quantity that determines the functional perturbation — how much of the force the muscle was actually
producing is added or removed. `Fmax` footing would make a dorsiflexor lesion of "equal dose" a far
larger functional insult, because the dorsiflexor operates at a lower fraction of capacity.*

⛔ **WHAT THE CHOICE COSTS, STATED NOW SO IT CANNOT BE DISCOVERED LATER:** *the arms are **not** matched
in absolute newtons — a plantarflexor lesion at fraction f perturbs **5.44×** the force a dorsiflexor
lesion at the same f perturbs. **Any result turning on absolute force magnitude stays confounded with
muscle group, and this design cannot fix it.** All three footings are reported for every dose point, and
any claim surviving on only one is reported as footing-dependent.*
⚠ *The existing corpus's magnitude ratio is already footing-dependent **in direction** — 5.41×–21.65× on
achieved force against 0.387×–1.549× on `Fmax` (`DOSE_FOOTING_r267.json`). This clause exists to stop
that recurring.*

### 2a. Newtons per unit KV — measured, and the gating script rebuilt

**Measured on the same validated path** (`FOOTING_r272.json`):

| group | **N per unit KV** |
|---|---|
| plantarflexors | **2725.3275** |
| `tib_ant_l` | ⭐ **543.5133** |
| ratio | **5.01428** |

⛔ **The dorsiflexor's constant is a fifth of the plantarflexors' and could not have been assumed.**
*`tib_ant_l` operates at a lower rectified lengthening velocity.*

⛔ **The rev-2 gating script's self-test could not fail** — *it wrote its deposit before the guard, used
a 2 % tolerance looser than the 2.69 % error it needed to catch, and tested only the plantarflexor
path.* **Rebuilt in `footing_r272.py`: the guard precedes the write, and BOTH constants are tested —
`tib_ant_l` achieved force against the deposited value at rel tol 1e-9, and the plantarflexor dose at
KV 0.050 against `VERIFY_F5_r231.json` at rel tol 1e-3. Both pass at zero error.**

### 2b. The dose grid — the square must close at more than one point

⛔ **REV 2'S GRID CLOSED THE 2 × 2 AT ONE DOSE OF THREE**, which is the cardinality defect this design
exists to remove, in a new place. **Corrected grid: f = 0.05, 0.10, 0.20.**

| f | WEAK-DF | SPASTIC-PF | WEAK-PF | SPASTIC-DF |
|---|---|---|---|---|
| **0.05** | exists (×0.950) | **NEW**, KV = 0.012563 | **NEW**, scale 0.950 | **NEW**, KV = 0.011578 |
| **0.10** | exists (×0.900) | **NEW**, KV = 0.025127 | **NEW**, scale 0.900 | **NEW**, KV = 0.023155 |
| **0.20** | exists (×0.800) | **exists**, KV 0.050 → f = 0.19899 | **NEW**, scale 0.800 | **NEW**, KV = 0.046311 |

⭐ **The square closes 4-of-4 at all three doses**, so the interaction is estimable at three dose points
rather than one. ⚠ *The KV 0.050 cell sits at f = 0.19899 against a target of 0.20 — a **0.5 %**
mismatch, accepted rather than re-run, and reported at every use.*

**Cells: 4 arms × 3 doses = 12 arm-dose combinations × 14 seeds = 168 total. 24 already exist
(`WEAK-DF` at three rungs and `SPASTIC-PF` at KV 0.050, six seeds each), so **144 are new**.**

### 2c. ⛔ The seed count was costed at six points; n = 14 chosen, n = 12 rejected on arithmetic

*Thresholds in units of each channel's control σ, so they move with n and the observed effects do not.
`hw = 1.96 σ √(2/n)`; rung 3 needs the groups' type effects to differ by more than 2 hw, and at the
2× ratio boundary the larger must exceed 4 hw. Channel counts use the |S − W892| proxy of §6a.*

| n | 2 hw/σ | 4 hw/σ | clears 2 hw | **clears 4 hw** | new cells | hours | **`ankle_angle_LmR`** |
|---|---|---|---|---|---|---|---|
| 6 | 2.2632 | 4.5264 | 8 | 3 | 48 | 1.97 | no |
| 8 | 1.9600 | 3.9200 | 9 | 4 | 72 | 2.95 | no |
| 10 | 1.7531 | 3.5062 | 9 | 5 | 96 | 3.94 | no |
| **12** | 1.6003 | 3.2007 | 9 | **5** | 120 | 4.92 | ⛔ **no** |
| ⭐ **14** | **1.4816** | **2.9632** | **9** | ⭐ **6** | **144** | **5.90** | ⭐ **YES** |
| 16 | 1.3859 | 2.7719 | 10 | 7 | 168 | 6.89 | yes |

⛔ **n = 12 is the worst point on the table and is rejected on arithmetic, not preference: 4.92 h, +2
testable channels over n = 6, and it misses `ankle_angle_LmR` — the channel the seed question was asked
about — by 2.8 % (3.1124 σ observed against a 3.2007 σ requirement).** *The channel crosses at n = 14.*

⚠ **A second alternative rejected on arithmetic: extending only the new arms to 14 seeds while leaving
the existing arms at 6 gives an interval governed by √(1/6 + 1/14), not √(2/14). At 12 seeds that
shortcut was exactly a balanced n = 8 — 96 cells and 3.94 h purchasing what 72 cells and 2.95 h
purchase. Unbalanced designs are not costed again.**

⭐ *Recorded because "we considered more seeds" is worth nothing and "we costed six points and here is
why we chose the fifth" is worth something.*

⛔ **CORRECTED: f = 0.40 does NOT extend beyond the existing reflex range and rev 2's claim that it did
was false.** *On this footing the existing `SPASTIC-PF` gains sit at **f = 0.19899 (KV 0.050), 0.59698
(KV 0.150), 1.59194 (KV 0.400)**. The reflex axis already spans to f ≈ 1.59; a new point at 0.40 lies
inside it. **The grid therefore does not claim to extend any range — it claims to CLOSE the square,
which is a different and achievable thing.***

## 3. Both metrics, both windows

⛔ **Every channel is computed under per-cycle EXCURSION and per-cycle MEAN ANGLE, and both are reported
for every result. Neither is primary.** *The metric was unregistered in the existing corpus and
determined which channel appeared to discriminate (§6 of the manuscript).* **Both measurement windows
are reported for every result.**

## 4. ⛔ Heading — the binary criterion is WITHDRAWN

⭐ **Rev 2 registered a 0.5 deg/cycle flag intended not to repeat Gate G selecting its own conclusion.
The audit measured it: at that threshold the reflex arm is 6/6 flagged on both windows, so the
unflagged stratum contains zero reflex cells and the stratification is undefined.** ⛔ **The criterion
had the very property it was built to avoid.**

⚠ **And the threshold was window-specific**: *control's maximum is **0.3753** deg/cycle at [1.00, 9.73]
and **0.2029** at [1.00, 13.58]. A bound calibrated on one window was to be applied to both.*

⭐ **REGISTERED INSTEAD: net pelvis yaw per gait cycle is a CONTINUOUS DEPENDENT VARIABLE**, deposited
per cell, reported per arm and per dose alongside every kinematic outcome, and never used to include or
exclude a cell or to define a stratum.
⛔ **General statement, registered: in a design where heading is an outcome of the lesion, NO heading
threshold can stratify it — any threshold that separates control from the lesioned arm is collinear
with the arm.** *This is the same defect as Gate G, and the fix is not a better threshold; it is not
having one.*

## 5. ⛔ Terminal objective is an OUTCOME

**Deposited per cell before any analysis:** *terminal objective (running minimum), generation-0 value,
descent over the final ten generations, terminal `fitness_progress`, the full `history.txt`, and the
four non-`GaitMeasure` components over a common interval (as `DECOMPOSE_r268.json`).*

⛔ **Reported as a DEPENDENT VARIABLE, never as a covariate.** *The objective is dominated by
`GaitMeasure { weight = 100, termination_height = 0.85 }`; adjusting kinematics for it is post-treatment
adjustment.* ⚠ **No analysis in this design conditions on terminal objective.**
⚠ *The prose figure r ≈ −0.998 for objective against duration is not yet in any deposit; it is deposited
with the first analysis run and is not cited until it is.*

⛔ **Every cell runs the same 90-generation budget, and this must be VERIFIED per cell rather than
assumed** — *duplicate directories exist in the results tree (`R169W095_s105/_s106` at 79 and 69
generations beside 91-generation copies), and two existing deposits read different copies. Every script
in this design uses the `>= 91` history-line guard with `assert len(g) == 1`, and the resolved directory
is deposited per cell.*

## 6. Primary endpoint, statistics, and the ladder

**PRIMARY ENDPOINT: the interaction** — does lesion TYPE displace a channel differently once MUSCLE
GROUP is crossed with it?

**Channels:** the sixteen of `MODEL_DESCRIPTORS_r253.json` → `channels_16`. **No primary channel is
pre-specified**; pre-specifying one was the old design's error.

**Effect measure, per channel × metric × window × dose:** *the arm mean's signed displacement from the
control band, the band being [min, max] over the six control cells, as §M7.*

**α = 0.05, two-sided. Multiplicity: Bonferroni over the sixteen channels within each
metric × window × dose family → α' = 0.003125.** *Families are not pooled across metrics or windows;
both are reported in full.*

**Null:** *exhaustive permutation of arm labels within each 2 × 2 cell at each dose, as
`PERMNULL_r221.json`.* ⛔ **Attainable floors are reported as floors. A count at its floor is never
reported as a p-value.**

**Equivalence margin: δ = 2.534 σ per channel, σ being that channel's control standard deviation.**
*Numerically this equals the sixteen measured n = 6 control-band widths and is frozen at those values.*
⛔ **See §6b: δ is deliberately NOT the control range.**

**THE LADDER — evaluated in this fixed order, first match wins:**

| # | rung | criterion |
|---|---|---|
| 1 | **FAILURE-DOMINATED** | any arm has < 2 cells completing ≥ 2 gait cycles → kinematics undefined; **time-to-failure becomes primary and the kinematic question is not answered** |
| 2 | **UNDERPOWERED** | any arm has < 5 usable cells, or the exhaustive floor for that family exceeds α' → **reported as underpowered, never as NEITHER** |
| 3 | **INTERACTION** | the type effect differs in **sign** between muscle groups, or in magnitude by > 2× with non-overlapping HL intervals → ⛔ **type is confounded with group; the discrimination question is answered NO** |
| 4 | **GROUP-ONLY** | channels separate by muscle group and the type effect is within δ in **both** groups → **the corpus was measuring anatomy** |
| 5 | **TYPE-CONSISTENT** | the type effect exceeds δ with the **same sign** in both groups → ⭐ **the first evidence in this project that type separates from group** |
| 6 | **NEITHER** | all four arm means lie within the control band on every channel, and each family's count is at its floor → **a clean negative, shipped as the result** |
| 7 | ⭐ **INCONCLUSIVE** | **terminal.** Reached only when every rung above has declined → **at n = 6 this channel's effects are too small or too imprecise to assign to type, to group, or to neither** |

⛔ **TYPE-CONSISTENT is one rung of seven and the only one favourable to the project's original claim.
Rungs 3, 4 and 6 each terminate the discrimination claim and each ships at full strength as the headline
if it fires. No rung is a fallback for another.**

⭐ **`INCONCLUSIVE` IS AN OUTCOME, NOT A BIN, AND ITS COUNT IS REPORTED.** *It is last, after every
substantive rung, so it can never absorb a case that should fire another — verified by re-running the
gate and confirming the other six counts are unchanged. **A design that returns INCONCLUSIVE on most
channels is telling us what six seeds can resolve, and the paper reports the number of channels on each
rung as a primary result.***
⚠ *It exists because the gate found 5,088 attainable configurations with no rung. Two patterns, and they
are the same statement twice: **1,296** where both type effects are within δ, the signs agree and group
does not separate — too small to classify; and **3,792** where one effect exceeds δ and the other does
not but the HL intervals overlap so the interaction test cannot fire — too imprecise to classify.*

### 6b. ⛔ WHY δ IS A FIXED MULTIPLE OF σ AND NOT THE CONTROL RANGE

*Rev 4 defined δ as the width of the control band — the range of the control seeds.* ⛔ **The expected
range of n normals grows with n: 2.534 σ at n = 6, 3.258 at n = 12, 3.407 at n = 14, 3.532 at n = 16.
So that definition made the equivalence margin a function of sample size — raising n would
simultaneously TIGHTEN rung 3, whose threshold scales as 1/√n, and LOOSEN rungs 4, 5 and 6, whose
threshold is δ, making `NEITHER` easier to reach for a reason having nothing to do with the data.**

⭐ **δ is therefore fixed at 2.534 σ, its n = 6 value, and does not move with n.** *The numbers are
unchanged; the dependence is removed. The defect was present at n = 6 and invisible only because n
never varied.*

### 6a. ⛔ WHAT THE INTERACTION TEST CAN ACTUALLY DETECT AT n = 6

*Registered here beside α, not in a limitations note, because it bounds the primary endpoint.*

**At the registered n = 14 the HL95 half-width for a difference of two arms is `hw ≈ 0.29235 δ`**
*(σ = δ/2.534; hw = 1.96 σ √(2/14))*. **At n = 6 it was 0.44657 δ.**

⛔ **Rung 3 requires non-overlapping HL intervals, so it cannot fire unless the two groups' type
effects differ by more than `2 hw`. At n = 14 that is `0.58470 δ`, and at the 2× ratio boundary the
larger effect must exceed `1.16940 δ`.** *At n = 6 the same thresholds were 0.8931 δ and 1.7863 δ.*

⚠ **Measured against the effect sizes this corpus has actually produced** — using |S − W892| per
channel as an order-of-magnitude proxy, which is the existing diagonal rather than a within-group type
effect — **at n = 6, 8 of 16 channels cleared the separation threshold and only 3 cleared the ratio
boundary.** *(Rev 4 said 7 for the first count; `ankle_angle_l` at 0.984 δ was missed counting by eye.)*
⭐ **At the registered n = 14, 9 of 16 clear the separation threshold and 6 clear the ratio boundary:**
`hip_flexion_r` (17.65 σ), `hip_flexion_LmR` (16.07 σ), `hip_adduction_r` (5.45 σ), `knee_angle_l`
(4.05 σ), `cycle_time` (3.73 σ) and ⭐ **`ankle_angle_LmR` (3.11 σ against a 2.9632 σ requirement)**.

⛔ **So on ten of the sixteen channels the interaction test is still not expected to fire at
corpus-typical effect sizes.** ⭐ **But `ankle_angle_LmR` — the channel carrying the clearest
dose-response in the existing corpus — now crosses, and bringing it across is the whole reason n = 14
was chosen over n = 12.** ⭐ **Registered before the compute: if the design returns INCONCLUSIVE on most
channels, that was predicted here and is a finding about fourteen-seed power, not a disappointment.**

## 7. What this design still cannot do

- ⚠ **It does not make the two lesions equivalent.** *Two muscles against one; 3.2916× the `Fmax`;
  5.44113× the operating force. Footing (3) matches the functional fraction and nothing else.*
- ⛔ **ADD VERSUS REMOVE.** *The reflex **adds** force during lengthening; the weakness **removes**
  force capacity. These are not the same operation with opposite sign, and no dose footing makes them
  so. **A type effect may be an add-versus-remove effect, and this design cannot separate them.***
- ⚠ **It does not establish the attainable optimum of any lesioned problem.** *Every cell runs the same
  90-generation budget as the existing corpus, for comparability. Whether that leaves a destabilising
  lesion further from its own optimum is not answerable within this design and is not claimed.*
- ⛔ **One model, one body, six optimiser seeds. Nothing here becomes a statement about people.**

## 8. ⛔ Reachability gate — required before the first cell runs

**Before any cell of this design is generated, a reachability deposit and script must exist**, to the
r229 precedent (`BODY2_REACHABILITY_r229.json`):

- **every rung of §6 has a generated witness** — a coherent configuration that returns it;
- **the prose ladder is asserted against the code ladder**, in order, and any mismatch fails the gate;
- **attainable-halfwidth bounds** are computed and deposited, so a rung that cannot fire is caught
  before the run rather than after;
- **message-truth is checked over all outcomes**, so no rung's message can assert something its own
  criterion does not establish.

⛔ **If any rung has no witness, the ladder is wrong and the run does not start.** *r229's reachability
gate caught an unreachable rung on first run; this design does not proceed without the equivalent.*
