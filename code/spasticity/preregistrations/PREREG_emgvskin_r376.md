# PREREG — Does activation detect a reflex lesion at a smaller dose than kinematics? (r376)

**Registered:** 2026-08-18, before any kinematic endpoint was computed on the KV ladder.

---

## 1. The question, and why it is the one left standing

Three papers were read in full before this registration and each removes a claim that was
previously being considered:

- **Laßmann et al., *J Neuroeng Rehabil* 2023;20:90** (SCONE + Hyfydy + Geyer–Herr + CMA-ES,
  2D 7-DOF, 7 muscles/leg, single seed). Already does full free re-optimisation of all
  non-lesioned controller parameters under a graded velocity-feedback lesion, and already calls
  it *"the rest of the nervous system adapting"*. Already reports stance SOL activation rising
  with gain (rho = 0.95, p < 0.001). Already reports a **kinematic** detection threshold: knee
  angle at heel strike flat for ωh < 53%, rising above. Already reports that weakness is
  *"compensated by other adapting spinal reflexes"*.
- **Bruel et al., *J Physiol* 2022;600(11):2691–2712.** Froze non-lesioned reflex parameters to
  ±5% of healthy *explicitly* "to limit potential compensation from other muscle reflexes", and
  named long-term adaptation and compensation as beyond the state of the art and as planned
  follow-up work. Reports no activation under any lesion.
- **Ong et al., *PLoS Comput Biol* 2019;15(10):e1006993.** Owns the qualitative
  compensation-absorbs-a-deficit observation and the method lineage. Models no reflex lesion,
  quantifies no compensation, reports no deficit-case activation.

**Therefore the following may NOT be claimed as novel and are not claimed here:** that a
re-optimised controller can mask a lesion; that a detection threshold in reflex gain exists;
that stance plantarflexor activation rises with reflex gain.

**What is not in any of the three:** a comparison, *within one model on one set of cells*, of
**how large the lesion must be before an ACTIVATION endpoint separates versus before a
KINEMATIC endpoint separates.** Laßmann's threshold is kinematic; ours so far is activation;
the two sit in different models on non-commensurable gain scales (their ωh = 100% ⇔ KV = 0.12
on a 2D 7-DOF model; ours is KV on a 3D 19-DOF model) so no cross-paper comparison is
admissible. This registration makes the comparison **internal and commensurable**.

---

## 2. Hypothesis

> **An activation endpoint separates the spastic arm from control at a SMALLER reflex gain than
> any kinematic endpoint does.**

If true, the clinically useful statement is that EMG detects the lesion earlier than motion
capture, and the dose gap between the two is the size of that advantage.

**A negative result is equally publishable and must be reported with equal prominence:** if
kinematics separates at the same rung or a smaller one, the claim that EMG is the required
instrument collapses, and that must be stated as the finding.

---

## 3. Arms and gate — carried unaltered from r370 §3

**Ladder:** `R289KV00625` (KV 0.00625), `R289KV0125` (0.0125), `R291KV0035` (0.035),
`R291KV0070` (0.070). Six seeds each.
**Reference:** the R203 control arm, `R203V080C`, `R203V105C`, `R203V130C`, 18 cells.

⚠ The control arm is at three different `min_velocity` settings while the ladder is at
`min_velocity` = 1.0. **This comparison is BETWEEN-SCENARIO** and every statement of the result
must carry that label. It is the same control band already used for the r371 z-scores.

**Gate G unchanged:** `t_end` ≥ 9.73 s, ≥ 5 complete cycles in [1.00, 9.73] s, last cycle in
window dropped, stance = `leg0_l.grf_norm_y > 0.05`.

`R291KV0070` is expected to contribute zero admissible cells (it did at r371, ending
8.24–9.52 s). It is retained in the ladder and reported as UNINFORMATIVE rather than dropped,
per r370 §8.

---

## 4. Endpoints — all fixed here, before measurement

**Activation endpoint (one, already known):** `A` = mean `soleus_l.activation` over stance
samples of admissible cycles. Its rung-wise verdicts against the DF-weak arm are already
deposited at `DOSELADDER_r371.json`. **For this registration it is recomputed against the
CONTROL arm**, which is a different comparison and has not been made.

**Kinematic endpoints (four, fixed now, no others may be added or substituted):**

1. `knee_angle_l` at left heel strike, per-cycle mean — **Laßmann's own endpoint**, chosen
   because it is the one that produced their 53% threshold.
2. minimum `ankle_angle_l` over the cycle (peak plantarflexion), per-cycle mean — their second.
3. `ankle_angle_l` range of motion over the cycle, per-cycle mean.
4. mean `ankle_angle_l` over stance, per-cycle mean.

All in degrees. Four is the whole set; the multiplicity is four and is stated wherever a
result is reported.

---

## 5. The comparison, defined before seeing anything

For each endpoint and each rung, test **disjointness of that rung's six seed means against the
18 control cells' seed means**, with an exhaustive permutation floor.

- **`KV_act`** = the smallest ladder rung at which `A` is disjoint from control.
- **`KV_kin`** = the smallest ladder rung at which **any** of the four kinematic endpoints is
  disjoint from control. Taking the minimum over four endpoints is deliberately **generous to
  kinematics**, and it is declared here so it cannot later be presented as a fair single test.

**Primary reading:** `KV_act` < `KV_kin` supports the hypothesis. `KV_act` ≥ `KV_kin` refutes it.

Because the ladder has only three measurable rungs, the possible outcomes are coarse and are
enumerated now: activation earlier by one rung, by two rungs, equal, or kinematics earlier.
**No interpolated threshold may be reported** — the resolution is the ladder spacing.

---

## 6. What this cannot establish

1. Nothing about surface-EMG noise (r360 §8, unchanged).
2. Nothing cross-paper: Laßmann's 53% is not comparable to any KV here, and no statement of the
   form "we detect at half their threshold" may be made.
3. Between-scenario, per §3.
4. The four kinematic endpoints are not the whole of kinematics. A negative result means *these
   four, at these rungs*, and must be worded that way.
5. Six seeds per rung against 18 control seeds caps the permutation floor; report it as a floor.

---

## 7. Uninformative

Fewer than 4 Gate-G seeds at a rung makes that rung uninformative and it is reported, not
dropped. If **no** endpoint of either kind separates at any rung, the outcome is UNINFORMATIVE
for the comparison and neither `KV_act` nor `KV_kin` is defined.

No substitute endpoint, no added kinematic channel, no interpolation, no pooling of rungs. If
this fails it is recorded as a failure and this registration is not amended.

---

## 8. A known threat, registered rather than discovered later

`DOSELADDER_r371.json` limitation L8 records that `gastroc_l.activation` separates from the
DF-weak arm at **all three** measurable rungs, i.e. it shows no threshold. If the same holds
against control, then "the activation threshold" is a property of the soleus channel and not of
the lesion, and `KV_act` is channel-dependent. **This is registered as a foreseeable outcome
now.** The gastrocnemius version of `A` is therefore computed and reported alongside, and if
soleus and gastrocnemius disagree on `KV_act`, the disagreement is the finding and no single
`KV_act` may be quoted.
