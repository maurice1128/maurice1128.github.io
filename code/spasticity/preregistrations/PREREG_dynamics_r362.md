# PREREG — Swing-phase plantarflexor activation, correct dorsiflexor arm (r362)

**Registered:** 2026-08-18, before any `PF_swing` value was computed for any cell of the
dorsiflexor arm named below.

---

## 1. Why a new registration rather than an amendment

`PREREG_dynamics_r360.md` (`a62573f5049825e0adb8c11618f2b19d4ae5b315723a67c13c87f26261ad19de`)
was executed as written. Its outcome is **UNINFORMATIVE** and is deposited unretracted at
`DYNAMICS_SWING_r361.json` (25,469 B): the dorsiflexor arm it named — `R293DFs010`,
`R293DFs030`, `R293DFs050` — has **zero** cells passing Gate G. Those cells end at
0.52–7.30 s against a 9.73 s gate.

**The cause was a mis-specified arm, not a mis-specified endpoint.** r360 §2 named the r293
*severity ladder*, which was built to probe how hard a dorsiflexor lesion has to be before the
model falls. The established dorsiflexor-weakness arm — the one `MATCHED20_ENDPOINT_r298.json`
compares against spasticity, at `/cells/DF` — is a different set of families, and all 36 of
its cells complete at 20.00 s.

An arm is registered material. It is not corrected in place after a result is seen, so r360 is
left standing and this is a separate registration.

**What is carried over unchanged, verbatim, from r360:** §3 the primary endpoint `PF_swing`
and its swing detection; §3 the predicted direction; §4 the duration-invariance test and its
0.5 threshold; §5 the separation criterion; §6 the secondaries and the prohibition on
promoting them; §7 the uninformative criteria and the prohibitions; §8 the declared
surface-EMG limitation; §9 the licence context.

**Nothing about the prediction is retrofitted.** No `PF_swing` value exists for any cell of
the dorsiflexor arm named below, in this or any prior deposit. The direction below is the same
one registered at r360 before any measurement of any kind.

---

## 2. Arms

**SPASTIC** (reflex `MuscleReflex` KV on soleus/gastroc, left) — the r298 spastic arm exactly:
`R289KV00625`, `R289KV0125`.

Values for these twelve cells are already known from the r361 run and are **not re-derived**:
they lie in [0.050950, 0.052273]. This is stated because concealing it would be worse; it does
not license any change to the prediction, which was fixed before any value existed.

**DORSIFLEXOR-WEAK** (`max_isometric_force` scaling on `tib_ant_l`) — the r298 DF arm exactly:
`R151W`, `R169W090`, `R169W095`, `R174W870`, `R174W892`, `R174W915`.

`R291KV0035` and `R291KV0070` are **not** included: r298's spastic arm does not contain them,
and adding families to widen an arm is the move §7 forbids. `R293DFs*` is not re-admitted.

**Gate G unchanged:** `t_end` ≥ 9.73 s and ≥ 5 complete cycles in the window [1.00, 9.73] s,
per-cycle means, last cycle in window dropped.

---

## 3. Prediction — identical to r360 §3, restated so this file stands alone

> **SPASTIC HIGH, DORSIFLEXOR-WEAK LOW.**

Spasticity predicts plantarflexor activity *present* during swing; dorsiflexor weakness
predicts the plantarflexors *quiescent* while the foot falls passively. A separation in the
opposite direction is a **failed prediction**, reported as such.

---

## 4. Readings and which is primary

Unchanged from r360 §4. Spearman ρ(`PF_swing`, `t_end`) within each arm; |ρ| < 0.5 in both
arms makes **READING U** primary; otherwise READING U is inadmissible and only the
duration-matched **READING M** may be read, becoming UNINFORMATIVE below 3 cells per arm.

⚠ **Registered in advance, because it is foreseeable:** both arms here are expected to sit at
or near `t_end` = 20.00 s. If every admissible cell in an arm has the *same* `t_end`, ρ is
undefined or degenerate for that arm. In that case the duration confound cannot act — there is
no duration variation for the endpoint to track — and READING U is primary by that fact. This
is recorded now so it cannot be presented later as a discovery.

---

## 5. Uninformative

Fewer than **5** Gate-G cells in either arm. No substitute endpoint, no widened gate, no
pooling of the dorsiflexor and plantarflexor weakness arms, no promotion of a secondary. If
this fails it is recorded as a failure and this registration is not amended either.

---

## 6. Declared limitation

r360 §8 applies unchanged: simulation `activation` is a clean 0–1 signal; surface EMG carries
noise, crosstalk and placement variance. A separation here does **not** establish that it
survives at surface-EMG noise levels, and this corpus cannot test that. Any clinical claim
must be stated as conditional on that untested step.
