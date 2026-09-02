# Council audit (2026-07-17) — two adversarial reviewers. MUST address before submission.

The previous paper's council caught real errors; this one did too. Both agents' full
findings below, with my disposition. **Bottom line: the first-pass numbers are NOT
trustworthy** — a velocity-independent pedestal confounds the core mechanism claim, and
CI/feature-leakage bugs inflate the statistics. Fixing + re-running.

## A. FATAL / must-fix bugs (code)
1. **Reflex tonic pedestal (biomech #1, reproducibility #9).** `pos(x)=0.5(x+√(x²+ε²))`
   with ε=0.05 has `pos(0)=ε/2=0.025` → at thr=0.02,G=12 the activation floor is ~0.20
   **at zero stretch velocity**. The reported "soleus 0.05→0.20 during stance stretch" is
   largely this velocity-INDEPENDENT pedestal, i.e. a tonic co-contraction, not a
   velocity-dependent reflex. FIX: offset-correct `pos(x)=0.5(x+√(x²+ε²))−ε/2` (so
   pos(0)=0, non-binding below threshold) and shrink ε to ~0.01–0.02. Also: METHODS says
   v_thr=0.05 but the generator used 0.02 and the code default is 0 — reconcile (runs used
   0.02). REQUIRES RE-RUN of all reflex sims.
2. **Wilson CI on N=350 not N=35 (stats #1).** `main()` pools cor/tot across 10 seeds
   (35 conditions × 10) before `wilson()` → CIs ~3.2× too narrow. The 10 seeds re-score the
   SAME 35 conditions (not independent). Correct N=35 → all level CIs overlap → the VoI
   ordering (MK_3D vs MK_3D_V vs Lab) is NOT significant. FIX: Wilson on condition count;
   report seed variation separately; bootstrap over subjects/conditions.
3. **Scalar features stored noise-free (stats #2).** `_add_noise` only perturbs `_p*` keys;
   `_min/_max/_range` (incl. the ankle-minimum discriminator) and C:: scalars are exact
   simulator outputs → leakage (same class as the previous paper's). FIX: add measurement
   noise at the SOURCE waveform so every feature (points + scalars) is measured
   consistently. REQUIRES RE-RUN of analysis (features).

## B. SERIOUS framing / honesty (mostly writing, some verification)
4. **Imbalance-inflated accuracy; wrong chance (stats #3).** Paretic=51% majority and
   trivially separable → micro-acc 0.774/0.846 flattered. Majority baseline=0.514 (not
   uniform 0.33). Report MACRO recall (MK_3D 0.62, Lab 0.75) + per-class recall as primary.
5. **Near-inverse-crime (stats #4).** 6 "subjects" = ±5% fibre/tendon perturbations of ONE
   base skeleton → LOSO tests noise-robustness, not between-subject generalization. Must
   caveat as "identifiability-in-principle / robustness", not generalization. Ideally
   perturb skeletal geometry/mass too.
6. **Velocity-VoI not significant (stats #6).** MK_3D 0.774→MK_3D_V 0.797 (Δ0.023, CIs
   overlap) and Lab_V(0.840)<Lab(0.846) → adding V:: to lab HURTS ⇒ V:: contribution is
   noise at this N. Downgrade to "mechanism-plausible, not yet statistically supported."
7. **Mixed 0.50 is an N=4 artifact (stats #5).** Literally 2/4; invariant across levels;
   contradicts the §3.4 prose (which cites the 3-class diagonal 10→20). Report raw counts +
   huge Wilson CI; reconcile the two "recover mixed" operationalizations.
8. **Heel-strike clamp / threshold-retry phase confound (biomech #2).** Clamp fired 0 times
   (verified) — good. BUT the lower-threshold RETRY for low-GRF spastic gaits could still
   shift detected heel-strike phase systematically vs paretic. VERIFY: which conditions used
   a lower threshold; cross-tab by class; re-run with a phase-invariant check. Also: never
   let HS1 default silently.
9. **Acceptable-termination under-reported (biomech #3).** Accepted runs are primal-feasible
   (valid gaits) but dual-inf ~1e-2 (not proven-optimal); stopping may correlate with reflex
   stiffness. `stats` is saved per run → BUILD a convergence table (return_status, dual inf)
   and re-run identifiability restricted to Solve_Succeeded; report acceptable-only count +
   class distribution.
10. **Floor ≠ additive reflex drive (biomech #4).** A floor contributes nothing where
    voluntary drive already exceeds it (push-off) → suppresses reflex exactly where real
    hyperreflexia is most additive; bites mainly in low-drive phases. Either reframe as
    "involuntary minimum activation" OR implement additively (e_total=e_vol+G·pos(v)).
11. **Supraphysiological gain / Falisse-2020 sidestepped (biomech #7).** G=6/12/18 not
    calibrated to Tardieu/EMG; effect may only appear at supraphysiological gain → the
    "barely changes kinematics" caution is sidestepped, not rebutted. Calibrate G to spastic
    EMG magnitudes (Van Criekinge 2023) or a target Tardieu R1; report peak reflex
    activations/moments and argue physiological range.
12. **v_MT proxy over-reads fiber velocity; PF-group reintroduces gastroc knee-coupling
    (biomech #5).** Report per-muscle (soleus vs gastroc) contribution; consider
    soleus-primary with PF-group as sensitivity. State v_MT over-estimates afferent drive in
    fast loading.
13. **Paretic-by-absence is circular (biomech #6).** With healthy excluded, "absence of
    equinus"→paretic only by construction; paretic≈healthy kinematically (−1.6° vs −0.9° <<
    3.5° noise). Cap claim to sub-typing within known-stroke, not screening/weakness-detection.
14. **No-delay precedent overstated (biomech #8).** Cited refs (van der Krogt/Falisse/Geyer)
    mostly INCLUDE ~30ms delay. Soften "many models omit delay"; add a delayed variant as
    robustness (V:: is most delay-sensitive).

## C. Genuinely sound (keep / defend)
- Impaired-only ranked classification — correctly avoids the previous "none"-threshold
  artifact. Condition-aggregation mechanics correct. Per-replicate noise correct (except the
  scalar leak). Reflex constraint placement correct + non-gameable as a minimum. Accepted
  solutions primal-feasible (real gaits). `stats` persisted (audit-able). Inverse-crime
  ±5% control present.

## Disposition / plan
- FIX 1,2,3 in code now (pedestal, CI, source-noise). Reconcile thr. Re-validate corrected
  reflex effect size on base G6/G12/G18 → decide gains (may need higher without pedestal;
  if effect vanishes, that is the honest Falisse-2020-confirming finding). Re-sweep.
- Build convergence table (#9) + threshold-use cross-tab (#8) from saved logs/stats.
- Rewrite RESULTS/METHODS/DISCUSSION for #4,5,6,7,10,11,12,13,14 (macro recall, majority
  baseline, non-sig VoI, robustness-not-generalization, floor-not-drive, supraphysiological
  gain honesty, paretic-by-absence, delay).
