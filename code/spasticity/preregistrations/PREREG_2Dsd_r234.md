# PRE-REGISTRATION — measuring the 2D between-seed SD (round 234)

Registered **before any replay**. Hashed with a `.sha256` sidecar before extraction.

---

## 1. Why

`PREREG_2ndbody_r229.md` §3 carries a power table and an equivalence margin **δ = 0.65°** derived
entirely from the **3D** body's per-seed SDs (0.157–0.587°, pooled 0.364, central 0.473). **The 2D
between-seed SD has never been measured.** The 2D model has different DOFs, a different objective, a
different horizon and a different CMA-ES landscape. §3's own table shows EQUIV power falling to
**0.532 at 2× the 3D pooled SD** — so **whether this design has 80 % power or 20 % is decided by a
number nobody has.**

## 2. ⛔ Scope — control cells only

**Only `SG0_DR2K000` is replayed: six cells, KV = 0.000, no lesion, level ground.**

**No lesion arm is touched.** Not `SG2` control, not any spastic or weak family. The measurement is a
property of the *unlesioned* 2D corpus, so it cannot contaminate the spastic-versus-weak comparison
the main registration exists to make. **Nothing is learned about any arm that enters that comparison.**

`sconecmd -e` replay only, from the **lowest field-3 `.par`, ties to highest generation**. Defect
register #205 discipline: a replay may be re-run only after a NON-RESULT; every attempt including
failures goes to `paper/BODY2_SD_LEDGER_r234.json`. Machine-wide `sconecmd` must be 0 or we do not
start.

## 3. The statistic

For each admitted control cell: `hip_flexion_LmR` = cycle-averaged (left − right) in degrees, over
left heel-strike cycles fully inside **[1.00, 8.00] s**, last dropped — identical to the main
registration's statistic, so the SD is on the scale δ is expressed in.

**σ₂D = the between-seed sample SD (ddof = 1) of those six values.**

Also reported: per-cell values, cycle counts, Gate-B pass/fail, and `σ₂D / 0.364` (the ratio to the
3D pooled SD) and `σ₂D / 0.473` (to the 3D central case).

⚠ **Six seeds gives a wide interval on an SD.** The χ² 95 % CI for σ on n = 6 spans roughly
0.62σ̂–2.45σ̂, and that interval is reported beside the point estimate. **The recalibration uses the
UPPER bound, not the point estimate** — an under-estimated SD is the failure mode that would let an
underpowered design present as adequately powered.

## 4. ⛔ Recalibration, and the outcome that kills the equivalence arm

`body2_delta_r229.py` is re-run with the 2D σ substituted for the 3D prior, giving EQUIV power at
δ = 0.65 for the measured body.

- **POWER ADEQUATE — EQUIV power at δ = 0.65 ≥ 0.80 using the CI upper bound.** δ = 0.65 stands and
  §3's table is replaced with the 2D-calibrated one.
- **δ RAISED — power < 0.80 at 0.65 but ≥ 0.80 at some δ ≤ 0.25 × Δ₃D.** δ is raised to the smallest
  such value and the change is recorded with both numbers.
- ⛔ **EQUIVALENCE UNREACHABLE — no δ ≤ 0.25 × Δ₃D reaches 0.80.** **The 2D corpus cannot support an
  equivalence claim at n = 16, the EQUIV rung is DELETED from the outcome set, and the registration
  says so** rather than carrying a power figure borrowed from another body. ⭐ **Registered in advance
  as a real and acceptable outcome.** A design that cannot bound the effect must not offer to.

**No outcome may be reclassified after the number is seen**, and δ may not be raised above
0.25 × Δ₃D — beyond that the claim "smaller than a quarter of the 3D effect" is no longer what is
being tested.

## 5. Deposit

`paper/BODY2_SD_r234.json` — per-cell values, σ₂D with its χ² CI, the ratios, the recalibrated power
table, and the outcome. Script `scone/body2_sd_r234.py`, recording its own sha256 and this
registration's. `paper/BODY2_SD_LEDGER_r234.json` — every replay attempt.

⛔ **Where this document and the code disagree, the RUN IS VOID.**
