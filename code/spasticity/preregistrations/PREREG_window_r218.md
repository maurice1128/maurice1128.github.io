# PREREG_window_r218.md — is the speed separation an artefact of a data-chosen window?

**Round 218.** ⛔ **Registered BEFORE extraction. Read-only, zero cells.**
*Where this document and any script disagree, THIS DOCUMENT DECIDES.*

---

## 1. ⛔ The circularity being tested

**Every ROM and speed number in this project is measured over `[1.00, 13.58]`.**

⛔ **13.58 is the shortest admitted spastic cell's duration — `S050` seed 103.** *It was set by the
"common window across all admitted arms" rule at r169 and inherited since. **The window's upper bound
is a function of the spastic arm's worst cell**, so a spastic-versus-weak comparison measured on it has
the spastic arm's termination structure built into it by construction.*

⚠ **The cell sitting exactly on the boundary is the cell that DEFINED the boundary. The window was
chosen from the data, from this arm, from its worst seed.**

## 2. ⭐ Why the G2 bound is admissible where 13.58 is not

**Gate G's G2 floor is 9.73 s.** *Provenance: `PREREG_3d_reopt_r151.md` §3, carried from
`PREREG_3d_discrimination_r150.md`:15 — **0.80 × the 12.16 s `bench_D20` baseline**.*

⭐ **It is a fixed fraction of a benchmark measured before any cell in this comparison existed. It is an
ADMISSION THRESHOLD, not a summary of the data it admits, and it is below every admitted cell in both
arms.** ⛔ **That is the whole reason this test buys anything: 13.58 is derived from the six spastic
durations; 9.73 is not derived from them at all.**

⚠ **What it is not: a window anyone chose for measurement quality.** *It is short, it discards the
second half of every weak cell, and its only virtue is that it predates the data. **That virtue is the
one the 13.58 window lacks.***

## 3. ⛔ The readings, fixed before the numbers exist

**Recompute achieved speed on `[1.00, 9.73]`, identical formula, all 42 cells.**

| | condition | registered reading |
|---|---|---|
| **A** | **separation survives, still disjoint** — weak minimum above spastic maximum | ⭐ **Speed is NOT an artefact of termination.** *Both arms read well inside their viable range on a bound predating the data; the finding stands on its own.* |
| **B** | **ranges overlap** | ⛔ **The original number was reading the spastic arm's approach to failure. We have ONE finding and it is DURATION, not speed. The speed framing goes.** |
| **C** | **survives but weakens materially** | ⛔ **Report both windows side by side and let the SMALLER separation be the headline.** *Do not average. Do not pick.* |

⛔ **No fourth reading is added after the numbers.** *If the pattern falls outside all three, the result
says the registration failed to anticipate it.*

## 4. The correlation, registered separately

**Spastic `speed_mps` against `dur_s`, six pairs, Pearson and Spearman, on the ORIGINAL window's
values as already deposited in `SPEED_LADDER_r217.json`.**

⚠ **It answers a different question: whether the cells that lasted longer also walked faster.**
*A strong positive correlation means the speed measure is partly reading termination and that must be
stated wherever the speed number appears — **independently of how §3 comes out**.*
⛔ **Six pairs. No p-value is quoted; the coefficient is descriptive.**

## 5. ⛔ The defect is not confined to speed

**Every per-cycle ROM channel is measured over the same data-chosen window** — *including the primary
`rom(L) − rom(R)`, the 16-channel displacement counts, and the `hip_flexion_LmR` sign reversal.*

⛔ **`RESULTS_3d_r214.md` §8 records the window as an open defect. It does NOT record that the defect
reaches every channel, not only speed.** ⚠ **That is an understatement of scope and it is corrected in
§8 in the same pass as this test.**

⛔ **Recomputing the whole channel set on the G2 window is the obvious follow-on and is NOT registered
here.** *This tests the one quantity that is cheap. If the window does not matter for speed, that is
evidence but not proof it does not matter for ROM; if it does matter, the channel set must be redone.*

## 6. What this cannot establish

- ⛔ **A short window is not a better window.** *Passing on `[1.00, 9.73]` shows the result is not an
  artefact of the LONG window's data-chosen bound. It does not show either window is correct.*
- ⛔ **Nothing about patients**, and no test against control. *Counts of seeds against ranges of seeds.*
- ⚠ **Fewer cycles per cell on the shorter window** — *≈ 7 rather than 9–14 — so every per-cycle mean is
  noisier, in both arms.*
