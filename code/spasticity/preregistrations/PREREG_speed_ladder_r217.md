# PREREG_speed_ladder_r217.md — does the weakness ladder reach the spastic arm's free-running speed?

**Round 217.** ⛔ **Registered BEFORE extraction. Read-only, zero cells, no simulation.**
*Where this document and any script disagree, THIS DOCUMENT DECIDES.*

---

## 0. Why this is registered rather than just run

**Check 1 found complete separation between the spastic and weak arms on free-running gait speed —
6 v 6, no overlap, at all three commanded levels.** *If that survives, it is a stopwatch-measurable
discriminator.*

⛔ **The strongest objection, stated before the data: the two arms were matched on lesion dose evaluated
on the CONTROL trajectory, deliberately upstream of gait to avoid conditioning on a collider.
Input-matching does not equalise functional severity — that was the point of moving upstream. So "the
spastic arm walks slower" may be nothing more than "we injected a functionally larger lesion on the
spastic side", and a referee will say so in one sentence.**

⚠ **This registration exists because a particular answer is wanted here, and that is exactly the
condition under which this project has twice promoted a finding on framing rather than a check.**

## 1. What is extracted

**Achieved gait speed, per seed, for six weakness severities already on disk:**
`R151W` (×0.80), `R174W870` (×0.870), `R174W892` (×0.892), `R169W090` (×0.90), `R174W915` (×0.915),
`R169W095` (×0.95) — **36 cells**, against the spastic arm `R151S` at KV 0.050.

⛔ **ADMITTED/RUN IS CARRIED PER SEVERITY FROM THE START, not retrofitted.** *Check 3 established that a
mean over cells that failed a gate is a number that is true with a label that is not. Every speed below
is reported beside the count of cells behind it.*

**Method: read-only from each cell's `.sto`, the same code path that produced the r203 speeds.
No `sconecmd`, no optimisation.**

## 2. ⛔ The three outcomes, fixed before the numbers exist

| | condition | registered reading |
|---|---|---|
| **A** | **the ladder brackets ~0.99 m/s** — some `s` puts the weak arm at the spastic arm's free-running speed | ⭐ **Then run the 16 channels at that `s` against the spastic arm.** *If the channels still separate, the finding is severity-independent and real.* ⛔ *If the arms become indistinguishable across the board, **speed WAS the severity axis and check 1 is our own dose choice read back to us** — and that is written as plainly as the other branch.* |
| **B** | **the ladder does not reach 0.99** — even ×0.80 leaves the weak arm faster than the spastic arm | ⭐ **Not a failed test. The strongest available version of the result:** *a weakness lesion at the edge of this corpus still walks faster than a spastic lesion at the only KV that survives.* ⛔ **State the margin — ×0.80's speed minus 0.99 — because the size of that gap IS the finding.** |
| **C** | **speed barely moves across ×0.80 → ×0.95** | ⭐ **Stronger than A or B.** *Weakness severity does not drive speed in this model, so speed cannot be the severity axis for the weak arm at all — **the two lesion types differ in HOW severity maps onto speed**, not merely in how much lesion was injected.* |

⛔ **No fourth outcome may be added after seeing the numbers.** *If the data falls somewhere none of the
three anticipates, the result reports that **this registration failed to anticipate it** and describes
the pattern. It does not retrofit a reading that fits.*

⚠ **A and C are not mutually exclusive** — *a flat ladder that happens to sit at 0.99 satisfies both. If
that occurs, C governs, because it is the stronger claim and it subsumes A's test.*

## 3. ⛔ The structural asymmetry, recorded before a referee writes it for us

**The weakness arm has a severity ladder. The spastic arm does not, and never will in this corpus.**

*`R169S150`, `R169S400`, `R172S150` and `R172S400` are all **0/6** at Gate G on two independent
optimisation paths, and no admitted cell exists at any KV below 0.050. The spastic axis is one point
wide.*

⛔ **Therefore the severity control is ONE-SIDED and permanently so. Every version of this claim can ask
whether a SLOWED WEAK ARM still separates, and can never ask whether a FASTER SPASTIC ARM still
separates.** ⚠ *That limits outcome A most: showing separation persists at matched speed demonstrates it
is not weakness-severity driven, and says nothing about whether it is spastic-severity driven.*

## 4. What this cannot establish

- ⛔ **Nothing about patients.** *Optimiser restarts, one model, one controller, one objective.*
- ⛔ **No test against control.** *Counts of seeds against ranges of seeds; no null, no p-value.*
- ⚠ **Speed here is achieved speed under a commanded-velocity objective**, *not free-living walking
  speed, and the r203 tracking gate showed the command was only tracked at one of three levels.*
- ⛔ **A one-sided severity control cannot exclude that the spastic lesion is simply functionally larger
  at KV 0.050.** *It can only show whether weakness severity reproduces the effect.*
