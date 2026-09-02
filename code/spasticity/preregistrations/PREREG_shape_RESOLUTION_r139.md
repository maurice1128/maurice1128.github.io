# PREREG_shape_RESOLUTION_r139.md — §6 resolved, and what it costs

**Round 139, 2026-08-08.** *Resolves the blocking structural finding in `PREREG_shape_r138.md` §6.
Written and hashed BEFORE any of the six features was computed on any run.*

## 0. State at the time of writing — measured from disk, not remembered

| | value |
|---|---|
| slope corpus | **234 of 234 complete**, every `history.txt` at exactly 91 lines |
| Tier-2 primary analysis | **RUN.** `--run --tier 2`, exit 0, elapsed 1416.4 s |
| Tier-2 verdict | **INDETERMINATE** (β̂_int = +0.1613, SE 0.3775, CI95 [−0.5839, +0.9065]) |
| shape features computed | ⛔ **zero, on either tier, still** |
| `PREREG_shape_r138.md` | sha256 `<recorded below>`, unmodified |
| `scone/residual_test.py` | **unmodified**, and it will stay so |

⛔ **Tier 2 has now been opened for the primary endpoint. It was NOT opened for any feature named in
r138.** *`ank_rom`, `cycle_time` and `ank_hs` were computed; `t*`, phase lag, the two CVs and the two
asymmetries were not. The held-out property r138 was protecting is therefore intact for those six and
gone for the corpus as a whole — and that distinction is why this document exists rather than a
claim that nothing changed.*

## 1. The choice: RESOLUTION 1

**Tier 2 is not a usable confirmatory set for a condition-level test, so the confirmatory arm is
abandoned. All six features are reported as EXPLORATORY, on the corpus the test was validated on.**

**Resolution 2 is refused, and the reason is that it benefits us.** *r138 §6 states it plainly:
changing the unit to the run makes n large and lifts the p-floor, but the spastic runs descend from
**two** distinct lesions, so run-level replicates are pseudo-replicates of 2 conditions, not
independent observations. Taking R2 would buy a publishable p by converting a clean design into a
pseudo-replicated one while keeping the clean design's language.* ⛔ **That is the substitution this
project spent its audit finding. It is not available to us because we would like a result.**

**R1 costs us the confirmatory claim and returns nothing in exchange. That is the whole argument for
believing this choice was not made to reach an outcome.**

## 2. What is run instead, and what it can and cannot say

**The identical test in `scone/residual_test.py`, on `scone/replay_crossed/`** — 12 conditions × 4
seeds, containing the full registered `SPASTIC` (`DR2K050 075 100 150 200`) and `WEAK` (`PAR20 40 60`,
`CMW70 80`) sets, **5 versus 5**, which is the corpus on which `ank_vel_max` produced the reference
numbers 0.3600 / 0.5476 / 4-of-5 / 0.8030.

| | |
|---|---|
| **can say** | whether shape, second moments or limb asymmetry survive the identical adjustment that killed the scalar — **directly comparable, same test, same covariates, same corpus** |
| **cannot say** | anything confirmatory. This corpus is contaminated: it is where `ank_vel_max` was found and killed |

⛔ **No exploratory result may be promoted, then or ever, and none is corrected — r138 §2: exploratory
outputs "carry no correction because they license nothing."** *Raw p is reported. The ×6 that would
have applied is printed alongside for comparability and is NOT an inferential claim.*

## 3. What is NOT changed

- **`scone/residual_test.py` is not modified.** *Its own docstring forbids it "by anyone, for any
  reason", and `BONFERRONI = 2 → 6` is unnecessary under R1 because nothing here is corrected.*
- **The six feature formulas are taken verbatim from r138 §3.** *No feature added, substituted or
  redefined. Six remains six.*
- **The falsifiers FA / FB / FC / F-ALL stand as written**, read against raw p at the exploratory
  level and labelled as such.
- **§8's split-verdict rule stands**: one route surviving is SUGGESTIVE AND NOT CONFIRMATORY; two or
  more is a finding. *Dated before any outcome, and unchanged by this document.*

## 4. The implementation, and why it is a new file

`sto_utils.cycle_features` returns **per-cycle means**. Routes B and C need per-cycle values and both
limbs, which it does not expose. **A new script `scone/shape_test_r139.py` computes the six features
from the same primitives** — `load_sto`, `heel_strikes`, `col`, `grf_vertical` — **mirroring
`cycle_features` conventions exactly: `settle = 1.0`, GRF-delimited cycles between consecutive heel
strikes, last cycle dropped, degrees, same detector threshold.**

⚠ **The lesion is unilateral and the registered analysis reads `side="l"`. Route C therefore treats
LEFT as the lesioned limb and RIGHT as intact.** *If that is wrong, C1 and C2 change sign and nothing
else moves — stated here so the assumption is visible rather than buried.*

## 5. What this document does not do

- **It does not run anything.** *Zero features computed as of this hash.*
- **It does not choose an outcome, predict one, or say which route is likely.**
- **It does not revive the confirmatory arm anywhere else.** *If a genuine held-out set is ever built
  for a condition-level test, it is a new registration, not a resurrection of this one.*
