# -*- coding: utf-8 -*-
"""r453: STRUCTURAL REFRAME, not more caveats.

Diagnosis of why the audit loop was not converging: every round added qualifying prose behind a
claim that was stronger than the evidence, and the next round of readers attacked the new prose.
Three consecutive reader panels made the same structural recommendation -- move the disqualifying
findings OUT of Limitations and INTO Results, and make the title match what is supported. This
round does that. It ADDS almost no new text; it moves existing text and changes the claims.

Four changes:
  1. Title and section headings state what is shown, not an absolute null.
  2. A new section 3.7 "What the model does not reproduce" carries, in Results, the three findings
     readers kept discovering in Limitations: no equinus, the frozen-controller collapse, and the
     adverse patient data. Those three Limitations entries are reduced to pointers.
  3. Section 4.1's "the field has been looking at the ankle" claim is withdrawn -- with no equinus
     in the model it is not supported.
  4. Conclusions rewritten to the supported claim.
"""
import io
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r453_prereframe")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# ---- 1. Title ---------------------------------------------------------------------------------
rep("""# At foot contact the ankle cannot distinguish plantarflexor spasticity from dorsiflexor weakness, but the knee can: a ground-truth simulation study""",
    """# Knee angle at foot contact separates plantarflexor spasticity from dorsiflexor weakness in a re-optimised musculoskeletal model, and why that does not yet transfer to patients""",
    "title")

rep("""### 3.1 At foot contact the ankle is blind to lesion type and the knee is not **[exploratory]**""",
    """### 3.1 At foot contact the knee separates the two lesions and the ankle does not **[exploratory]**""",
    "3.1 heading")

# ---- 2. New Results section carrying the three disqualifying findings --------------------------
rep("""---

## 4. Discussion""",
    """### 3.7 What the model does not reproduce **[exploratory]**

Three negative characterisations belong with the results rather than after them, because each bounds
what the preceding sections can mean.

**No equinus, and no foot drop.** The ankle at contact is −0.656° in control and −1.516° and −1.460°
under the two lesions: every arm lands within 1.5° of neutral. Clinical spastic equinus at initial
contact is 10–25° of plantarflexion with forefoot or flat-foot landing, and dorsiflexor paresis
produces a comparable deformity. The model reproduces neither. A likely structural reason is that the
modelled construct is a velocity-dependent stretch reflex, which is largely silent through swing
while the triceps surae is shortening and is loaded mainly after contact; the equinus posture *at*
contact in patients is set principally by fixed shortening and by non-velocity-dependent swing-phase
plantarflexor activity, neither of which is modelled. **Consequently §3.1's ankle result cannot be
read as evidence that ankle position is uninformative in a limb presenting with equinus.** It is a
convergence of two sub-degree displacements in a near-normal gait.

The same applies to the rest of the hemiparetic phenotype. Peak swing knee flexion is *reduced* in
both arms relative to control — by 0.433° under weakness and 2.077° under spasticity — so the model
produces neither steppage nor stiff-knee gait, the two mechanisms by which patients actually fail to
clear the toe. There is no circumduction, hip hitching or trunk compensation, and the contralateral
limb is unaffected except at KV 0.110. A clinician shown these kinematics blind would not identify
them as hemiparetic.

**The discrimination requires re-optimisation, and the clinical test that would validate it removes
exactly that.** With the controller frozen rather than re-optimised, an isolated soleus-*weakness*
condition displaced the knee to −13.33°, against −13.20° for the spastic arm: same sign, same
magnitude. Those cells fail Gate G and so do not enter §3.1, but they establish that the endpoint is
not mechanism-specific in the absence of re-optimisation. This is not a remote scenario. A diagnostic
tibial motor block — the procedure this readout would have to be validated against — is acute
plantarflexor paresis delivered over minutes, with no opportunity for motor re-learning. It is the
frozen-controller condition. On the model's own evidence the post-block knee would move *toward* the
spastic reading in a limb from which spasticity had just been removed.

**The one patient dataset examined supports the weakness arm and contradicts the spastic one.** In 50
stroke survivors, ankle angle at contact and knee deviation from the able-bodied norm correlate at
r = +0.613 (p = 2.2 × 10⁻⁶), and limbs contacting plantarflexed sit 6.31° from norm against 17.09° for
limbs contacting dorsiflexed. That is this model's weakness chain — dorsiflexor failure, plantarflexed
contact, less knee flexion — visible in patients. It is also the opposite of what the spastic arm
predicts: plantarflexor overactivity should give plantarflexed contact *and more* knee flexion, and in
these data plantarflexed contact goes with *less*. The dataset carries no spasticity or strength
scale and no speed control, so it cannot test the discrimination itself; on the one relation it can
address, half of it runs against the model. Separately, 25 of those 50 limbs contact plantarflexed,
so "knee angle at initial contact" pools two mechanically different events in half the target
population — and not at random, since contact type is downstream of the lesion.

---

## 4. Discussion""", "3.7 new section")

# ---- 3. Reduce the three Limitations entries to pointers --------------------------------------
rep("""5. **Simulation only, and the one real-patient dataset examined is half against us.** A public
   dataset of 50 stroke survivors cannot test this discrimination — no spasticity or strength scale,
   no soleus channel, no MVC normalisation, no speed — but on the one relation it addresses it is not
   neutral. Ankle angle at contact and knee deviation from the able-bodied norm correlate at
   r = +0.613 (p = 2.2 × 10⁻⁶, n = 50), and limbs contacting plantarflexed sit 6.31° from norm against
   17.09° for those contacting dorsiflexed — the model's **weakness** mechanism visible in patients.
   **It simultaneously contradicts the spastic arm**: spastic overactivity should give plantarflexed
   contact *and more* knee flexion, whereas here plantarflexed contact goes with *less*. In those
   same limbs 25 of 50 contact plantarflexed, so "knee angle at initial contact" pools two
   mechanically different events — and not at random, contact type being downstream of the lesion.
   §4.4 asks clinicians to measure at foot contact; in half the target population that instant is a
   different event.""",
    """5. **Simulation only**; no patient data were generated. The single public dataset examined is
   reported in §3.7, where half of what it shows runs against the model.""", "limitation 5 to pointer")

rep("""6. **The weakness arm does not reproduce steppage.** Clinically, dorsiflexor weakness provokes
   increased hip and knee flexion in swing to clear the toe. Here both lesions *reduce* peak swing
   knee flexion relative to control — weakness by 0.433°, spasticity by 2.077°. The likely cause is
   that the cost function contains no toe-clearance penalty. A clinician will not recognise this half
   of the discriminator, and it should be resolved before any patient study is designed on it.""",
    """6. **The model does not reproduce equinus, foot drop, steppage or stiff-knee gait** (§3.7). For the
   swing-phase failures the likely proximate cause is that the cost function contains no
   toe-clearance penalty.""", "limitation 6 to pointer")

rep("""9. **The discrimination depends on re-optimisation, which has no clinical counterpart.** With the
   controller frozen, a pure soleus-weakness condition displaced the knee to −13.33°, matching the
   spastic arm's −13.20° in sign and magnitude. Those cells fail Gate G, but the endpoint is not
   mechanism-specific in the absence of re-optimisation — and no patient re-optimises their
   controller between a clinician's two measurements.""",
    """9. **The discrimination depends on re-optimisation, which has no clinical counterpart** (§3.7).""",
    "limitation 9 to pointer")

# ---- 4. Withdraw the unsupported 4.1 framing ---------------------------------------------------
rep("""### 4.1 Why the field has been looking at the ankle

Both the variable clinicians observe and the variable recent instrumented studies analyse is foot or
ankle position at contact [4, 5]. These results suggest contact is the one instant at which the ankle
carries the *least* lesion-type information, because both lesions drive the foot into the same
plantarflexed position by different routes. This is an observation about convergence, not an
explanation of why the knee responds as it does — §3.6 establishes that joint-level anatomical
inference does not work in this system.""",
    """### 4.1 What the ankle result can and cannot say about clinical practice

Both the variable clinicians observe and the variable recent instrumented studies analyse is foot or
ankle position at contact [4, 5]. It is tempting to read §3.1 as showing that this is the least
informative instant at the ankle, and an earlier draft of this manuscript did so. **That reading is
not available here.** Because the model produces no equinus (§3.7), its ankle result describes the
convergence of two sub-degree displacements in a near-normal gait, not the behaviour of an ankle in a
limb that presents with the deformity. What the results do support is narrower and internal: within
this model, at this instant, the ankle carries no lesion-type information that the knee does not, and
the knee carries information the ankle does not. Whether that ordering survives in a limb with
10–25° of equinus is untested, and is the first thing a follow-up should establish.""",
    "4.1 withdrawn")

# ---- 5. Conclusions to the supported claim -----------------------------------------------------
rep("""At the instant of foot contact, plantarflexor spasticity and dorsiflexor weakness drive the ankle to
the same position by different routes, and the knee in opposite directions. In a ground-truth
simulation the knee at that instant classifies lesion type where the ankle performs at chance. The
displacement is nonetheless smaller than the between-session error of marker-based knee kinematics,
so the claim supported is discrimination *in simulation*, not clinical detectability. The result is
exploratory, confounded with simulation survival, unaccompanied by a contracture control, and
unexplained mechanistically. Its value is a specific, falsifiable prediction for a within-patient
patient study, and a clear statement of what would have to be true for that study to be worth running.""",
    """In a musculoskeletal model whose controller is re-optimised for every lesion, knee angle at the
instant of foot contact separates plantarflexor spasticity from dorsiflexor weakness — the two
lesions displace it in opposite directions by 5.28° — while ankle angle at the same instant does not.
The separation holds at the honest unit of analysis, classifying 11 of 11 optimisation lineages with
a family-level permutation p = 0.0022, and it survives a measured batch false-positive rate of 26.7%.
Within the model, the result is solid.

It does not currently transfer. The effect is smaller than the between-session error of marker-based
knee kinematics; the model produces no equinus, foot drop, steppage or stiff-knee gait, so its gait
is not the gait in question; the simulated severity does not reach the patients who receive
diagnostic blocks; the discrimination disappears when the controller is not re-optimised, which is
the state a diagnostic nerve block produces; and the one patient dataset examined supports the
weakness arm while contradicting the spastic one. No mechanism was identified, and no contracture
condition was modelled, though contracture would plausibly reproduce the same knee signature.

The contribution is therefore twofold and neither part is a clinical measure. First, a demonstration
that at one instant two lesions with a shared final common path at the ankle are separable at a
neighbouring joint, in a system where the true magnitude of each lesion is known — a comparison no
patient study can construct. Second, an accounting of the five specific things that stand between
that demonstration and a patient, each stated with the measurement that establishes it. The next step
is not a trial. It is a contracture arm, a model that walks in equinus, and replication within a
single optimisation round.""", "conclusions")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))
