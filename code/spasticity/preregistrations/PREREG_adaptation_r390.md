# PREREG — Is the lesion visible before compensation completes? (r390)

**Registered:** 2026-08-18, before any cell of the R390ADAPT series has been run.

---

## 1. The question, and why it is the one worth the remaining licence

Everything in this corpus so far gave CMA-ES a full run — 91 generations — with the lesion in
place. That is a **fully compensated** nervous system. Against that background:

- `DYNAMICS_LIMITATION_r365.json` → compensation cancels **0.8570823499731588** of the added
  reflex drive.
- `KINPAIR_r379.json`, `COMPENSATION_r381.json` → every kinematic separation of the clinical
  pair is **0.22–1.21°**, against a post-stroke ankle MDC of **3.8–11.5°**.
- `HARMONIC_r383.json` → comparing two dorsiflexor-weakness families with the *same* lesion
  mechanism, **96 of 450 pairs separate, 21.3%**, against a quoted permutation floor of
  2/924 = 0.22%. The corpus's separation claims are being re-tested against that batch null at
  `BATCHNULL_r389.json`; **until that completes, no separation claim in the dynamics line is
  settled**, and this registration does not assume any of them.

**The untested question is whether the lesion is visible BEFORE compensation completes.**
Generations of CMA-ES stand in for adaptation time: one generation is the acute state, 91 is
the chronic fully-adapted state already measured.

**This is exactly the gap the nearest prior work names and declines to enter.** Bruel et al.
(*J Physiol* 2022;600:2691–2712) froze non-lesioned reflex parameters to ±5% of healthy
*explicitly* "to limit potential compensation from other muscle reflexes", and wrote: "This
topic of long-term adaptation and compensation is of great interest, but the state-of-the-art
in pathological modelling is not at the point to address such complex conditions... We plan to
explore this topic in follow-up studies." Laßmann et al. (*J Neuroeng Rehabil* 2023;20:90) ran
the fully-free case. **Neither swept between them.**

---

## 2. Design

Two lesions × five adaptation budgets × six seeds = **60 cells**, all newly simulated.

**SPASTIC:** the `SpasticL` `ConditionalController`, `MuscleReflex` on soleus and gastrocnemius,
left, `delay = 0.020`, **KV = 0.050**, `allow_neg_V = 0` — the block copied verbatim from an
existing `R203*S` cell, not retyped.

**DFWEAK:** `H1922v7b3.hfd` with `tib_ant_l` `max_isometric_force` **1759 → 1407.2** (×0.80),
`soleus_l` 3549 and `gastroc_l` 2241 asserted unchanged.

**Budgets:** max generations ∈ **{1, 5, 15, 40, 91}**.
**Seeds:** 101–106. **Base cell:** `R151C_s101`, the matched unlesioned control at
`min_velocity` 1.0.

Prefixes `R390ADAPT{S|W}g{001|005|015|040|091}_s{seed}`.

---

## 3. Primary endpoint and the registered prediction

**Endpoint:** the spastic-versus-dorsiflexor-weak **gap** on mean `ankle_angle_l` over stance,
in degrees — a purely kinematic, motion-capture-obtainable quantity, and the one that separated
the clinical pair at the smallest rung in `KINPAIR_r379.json`.

**`GAP(g)`** = that gap computed at adaptation budget `g`, six seeds per arm.

**Registered prediction, before any cell is run:**

> **`GAP(g)` is monotonically DECREASING in g.** The lesion is most visible acutely and is
> progressively hidden as the controller adapts.

**And the quantitative claim that would make this worth publishing:**

> **`GAP(1) ≥ 3.8°`, i.e. above the clinical MDC, while `GAP(91)` is the ~1° already measured.**

If `GAP(1)` is also sub-threshold, the honest conclusion is that the lesion is **never**
clinically visible in this model at this severity, not even before adaptation — and that
conclusion is to be reported with the same prominence as a success.

**Failure modes registered in advance:** if `GAP(g)` is non-monotone, or increases, the
prediction has failed and is reported as failed. No reinterpretation.

---

## 4. Gate, conventions, and the batch null

Gate G unchanged: `t_end` ≥ 9.73 s, ≥ 5 complete cycles inside [1.00, 9.73] s, last cycle in
window dropped, stance = `leg0_l.grf_norm_y > 0.05`.

⚠ **Expected and registered now:** at low budgets the controller has barely adapted and cells
may fall before 9.73 s. A budget at which fewer than 4 seeds per arm pass Gate G is
**UNINFORMATIVE** and is reported, not dropped. **If the acute budgets fall, that is itself the
answer to a different question — the acute state may be unmeasurable because the model cannot
walk — and it must not be presented as a gap measurement.**

⚠ **The batch null applies here too.** Both arms are single families, so a
family-versus-family comparison is exactly the geometry whose null rate `HARMONIC_r383.json`
measured at 21.3%. **Every verdict in this registration must be read against that null, not
against the 1/924 permutation floor**, and the floor may be quoted only alongside it.

---

## 5. Secondaries — deposited, never promoted

`GAP(g)` on: knee angle at heel strike; minimum ankle angle over the cycle; ankle ROM; peak hip
flexion in swing; mean stance soleus activation; and `BETA_abs`. Also the terminal objective
value at each budget, which measures how much of the compensation the optimiser had actually
achieved — the independent variable's own readout.

---

## 6. Uninformative

Fewer than 4 Gate-G seeds per arm at a budget. No substitute endpoint, no added budgets, no
pooling across budgets, no promotion of a secondary. If this fails it is recorded as a failure
and this registration is not amended.

---

## 7. Declared limitations

1. **Generations are not time.** CMA-ES generations are a computational budget, not days of
   neural adaptation, and the mapping between them is unknown and unvalidated. Every statement
   must say "adaptation budget", never "weeks post-stroke".
2. The lesion magnitudes are mild — KV 0.050 and a 20% dorsiflexor force loss. Real foot drop
   is often a 70–100% loss, and `DFSEVERE_RESULT_r303.json` records that at ×0.30 and ×0.10 the
   model falls at 4.2–7.3 s and cannot be measured. **The severe regime is closed by falling,
   and this registration does not reopen it.**
3. `activation` is a clean deterministic simulator signal; the r386 audit established there is
   no `NoiseController` in any family and that each replay is deterministic. Nothing here speaks
   to surface-EMG noise or to marker error, and a real recording carries more variability than
   anything measured here.
4. Six seeds per arm per budget; the permutation floor is 1/924 and is subordinate to the batch
   null of §4.
5. One base cell, one spastic gain, one weakness magnitude. Nothing here establishes that the
   shape of `GAP(g)` generalises across severities.

---

## 8. What a positive result would license

That **the detectability of a neuromuscular lesion in gait is a decreasing function of how much
the controller has been allowed to adapt around it**, quantified, in a model where the lesion is
known exactly. The clinical reading — that the diagnostic window is early, before compensation
consolidates — is a **hypothesis generated by this result, not a finding of it**, and must be
worded that way.
