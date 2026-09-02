# -*- coding: utf-8 -*-
"""r586: the Background as one argument, without internal headings.

Ong's introduction is 793 words in five paragraphs and Jansen's 951 in seven; neither carries a
subsection heading, and each paragraph closes on what the work it has just described cannot settle.
Ong: "However, these muscular deficits often co-occur with other abnormalities, making it difficult
to assess the independent contributions"; "Although this experiment helps to establish a cause-effect
relationship, nerve blocks are invasive and thus difficult to repeat"; "however, since these studies
tracked experimental data from patients with a combination of deficits, the independent effects
cannot be assessed". The gap is not announced once at the end. It accumulates.

This Background was three headed subsections totalling 1,360 words, each self-contained. It becomes
seven paragraphs of continuous argument. Every citation, every number and every qualification is
carried over; what goes is the partitioning and the repetition it required.
"""
import io, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r116_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()
i, j = s.index("## 1. Background"), s.index("## 2. Methods")
old = s[i:j]

new = u"""## 1. Background

Spastic equinovarus foot after stroke has three treatable causes: calf spasticity, shortening of the
triceps surae\u2013Achilles complex, and dorsiflexor weakness. They take opposite treatments,
chemodenervation or neurotomy for overactivity, stretching or lengthening for shortening, and
orthosis, stimulation or tendon transfer for weakness, and the consequences of assigning them wrongly
are asymmetric [1]. Botulinum toxin injected into a triceps surae that is weak rather than overactive
reduces the plantarflexor moment available for knee stability in stance, and ref [1] describes that
blockade as reversible over three to six months; selective neurotomy and tendon lengthening are not
reversible, and the block is used most often before those procedures. Published practical guidance
calls the diagnostic motor nerve block "a mandatory step" in deciding which cause a given limb has,
and uses it alongside clinical examination rather than in place of it [1]. However, the block is
itself invasive, and it is used because no non-invasive measurement apportions.

Bedside tests address parts of the problem. Slow-versus-fast stretch (Tardieu R1 versus R2) estimates
the dynamic component, and the Silfversk\u00f6ld manoeuvre separates gastrocnemius from soleus restriction
by comparing passive dorsiflexion with the knee extended and flexed. Both are approximations, and the
guidance retains the block alongside them rather than in place of them, without stating its reason
[1]. A retrospective series of 50 chronic stroke patients supports the block as a screening tool
before botulinum toxin, although the block itself improved every outcome more than the subsequent
injection did and therefore overestimates what the toxin will achieve [2]. In 40 adults with brain or
spinal-cord injury, instrumented gait analysis and the tibial block carried distinct information and
proved complementary rather than interchangeable [3].

The present study addresses none of the block's purposes directly. Varus is not modelled, and the
block population is predominantly equinovarus, in which tibialis anterior is often itself overactive
rather than simply weak [3, 20]; the scope here is sagittal-plane equinus only. The components also
co-occur. In 42 stroke patients with dynamic ankle spasticity, affected dorsiflexor strength had a
median manual muscle test grade of 1 (IQR 0 to 4) against 5 (3 to 5) in propensity-matched stroke
patients without spasticity (p < 0.001), and affected *plantarflexor* strength was reduced in the
same limbs (4 versus 5, p < 0.001) [4]. The clinical question is therefore usually one of proportion
rather than of which single cause is present.

Two groups have measured the ankle at contact in this population. Ouyang et al. measured ankle angle
at four gait events, initial contact, toe-off, maximum dorsiflexion and maximum plantarflexion, and
no knee kinematics at all; ankle angle at contact differed between the spastic and matched
non-spastic groups, and of five variables entered into their model and four retained, the two that
remained *significantly* associated with spasticity were bedside measures and not gait variables,
namely passive plantarflexion range and dorsiflexor strength [4]. Mendes-Andrade et al. grouped 34
chronic hemiparetic patients by forefoot versus rearfoot contact and found ankle-at-contact differing
between groups (\u22123.67\u00b0 versus +2.00\u00b0, p = 0.003), a grouping variable that is itself ankle position at
contact [5]. Neither study, therefore, reports a gait variable that carries the apportionment.

The knee has been read at the same instant with the opposite outcome. Mendes-Andrade et al. report
knee angle at contact (8.30\u00b0 versus 8.03\u00b0, p = 0.929) as a descriptive variable rather than a
discriminator [5], although in 30 ambulatory children with spastic cerebral palsy both knee flexion
at contact and maximal knee extension in stance correlated significantly and positively with graded
hamstring spasticity on the Modified Tardieu Scale, with R1 and with |R2\u2212R1| but not with R2 [6],
which establishes that knee-at-contact can index the velocity-dependent component of spasticity in a
muscle crossing the knee directly. Only one study has attempted the equivalent reading in adult
stroke. That pilot related graded ankle muscle tone to hemiparetic knee angle through stance in 12
hemiparetic adults at a median 4.0 months since stroke (range 0.25 to 13.0), which we treat as
subacute, using the Modified Tardieu Scale and 2D video [7]. Its positive finding is a dorsiflexor
one, tibialis anterior tone correlating with knee angle at initial contact (\u03c1 = 0.662, p = 0.019),
terminal stance and pre-swing, while gastrocnemius tone, the muscle class lesioned here, was not
significantly related to knee angle at any stance phase (p = 0.22 at initial contact, then 0.45,
0.24, 0.48 and 0.85). Those five p values are verbatim in that paper's Results and none is
significant on any reading; its reported coefficients are internally inconsistent, two of the five
coefficient and p value pairs not implying one another at n = 12, so we rely on the p values alone.
Nine of the 12 participants had any gastrocnemius tone at all.

Where both components have been measured together, they move the same joint. In 30 chronic stroke
patients, peak stance knee hyperextension related weakly to gastrocnemius spasticity and moderately
to dorsiflexor and knee-flexor strength [8], and plantarflexor weakness is separately associated with
the same deviation (n = 20, p = 0.044) [17]. Both are associations at an event rather than
discriminations between causes. A six-patient series found dynamic EMG changing the treatment
hypothesis in post-stroke equinus, two patients whose clinical assessment agreed showing different
swing-phase patterns and focal inhibition being withdrawn in one, and it documents the barriers
keeping that method out of routine use [20]. Where contractures of different muscles are
distinguished, in ten healthy adults wearing an exoskeleton, the knee is a *common* feature rather
than the discriminating variable, discrimination being carried by the hip, pelvis and ankle [18].

Simulation can set a deficit of known magnitude and read what follows. Reflex-gain forward simulation
reproduces hemiparetic-like kinematics, including increased knee and hip flexion at initial contact
and through loading response, stance and swing under gastrocnemius hyperreflexia, so the event
examined here is not new; that paper reaches this study's endpoint as well, reporting that reduced
suppression of spindle feedback during swing contributes to increased plantarflexion and so to
hampered toe clearance, and noting that the literature attributes that deficit mainly to pretibial
weakness with the role of hyperreflexia not specifically considered [9]. The qualitative claim that
calf hyperreflexia can reduce swing dorsiflexion is therefore not ours. What that paper does not
supply is a magnitude: its gain factors were chosen arbitrarily, so by its own statement no claim
about absolute effect can be made, it summarises cross-muscle effects as directional only, it
simulates no weakness, and it proposes no discriminator. Plantarflexor weakness and contracture have
been simulated with per-condition re-optimisation [10], plantarflexor hyperreflexia has been
contrasted against plantarflexor weakness [11], and ground-truth impairments propagated to kinematics
in personalised cerebral-palsy models explained on average 17 per cent of deviation and never more
than 39, contracture having the largest single effect [12]. However, each of these introduces one
impairment at a time, so none of them addresses an apportionment.

In this study a reflex-controlled musculoskeletal model was lesioned in two ways, by a
velocity-dependent stretch reflex on soleus and gastrocnemius and by scaling of tibialis anterior
force, with the controller re-optimised for each lesion so that both magnitudes are known exactly.
Eighty-one candidate sagittal variables were then scored across three joints and the whole gait
cycle, in degrees and against a published motion-capture error, to establish which of them separates
the two lesions, which grades each of them, and what remains recoverable when both are present. The
two severity series are themselves unmatched in a way that bears on the comparison, which \u00a74.5
returns to.

"""
s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("Background: %d -> %d words, 3 subsections -> 0" % (len(old.split()), len(new.split())))
