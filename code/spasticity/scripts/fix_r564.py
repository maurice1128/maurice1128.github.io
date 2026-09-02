# -*- coding: utf-8 -*-
"""r564: rewrite 4.5 so that scope sits inside the claims instead of trailing them."""
import io, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r80_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()
i, j = s.index(u"### 4.5 Limitations"), s.index(u"## 5. Conclusions")
old = s[i:j]

new = u"""### 4.5 Limitations

**1. One model, one controller, and one patient result that runs against the asymmetry.** Everything
here is a property of a single 19-degree-of-freedom model under a single reflex controller, and the
asymmetry between the lesions rests on how much reserve this model's tibialis anterior retains in an
unloaded swing limb. That is a modelling choice no internal control reaches, so the finding is a
hypothesis about human gait rather than a measurement of it.

Chisholm et al. report, in 55 independently ambulating sub-acute stroke survivors, that peak
dorsiflexion during swing was related to isometric dorsiflexor force at r = \u22120.32, p = 0.039 [28]:
an association in patients, at this study's own endpoint, of the size this model calls faint. Only
the published abstract of [28] was retrieved, so we can verify the coefficient, the p value and the
cohort size and nothing else. What we cannot check is the one figure that would settle how far the
result bites, the cohort's dorsiflexor force distribution. Should it overlap the \u00d70.80 to \u00d70.95
window across which this model's weakness ladder spans 0.66\u00b0, the model understates what dorsiflexor
force writes onto swing dorsiflexion, most plausibly because its tibialis anterior keeps more reserve
in an unloaded swing limb than a paretic one does. Should the cohort be weaker than that window, the
two results agree and say only that our ladder stops short of where weakness becomes legible. The
asymmetry should therefore be read as bounded by an unresolved patient result.

A second patient study is often read as contradicting the asymmetry and does not. In 68 chronic
hemiparetic adults, dorsiflexor strength was the strongest determinant of gait velocity and of
temporal symmetry (R\u00b2 = 0.30 and 0.36) while dynamic plantarflexor spasticity was the strongest
determinant of spatial symmetry (R\u00b2 = 0.53) [27]. Those are spatiotemporal parameters from an
instrumented walkway, with no joint kinematics recorded. That weakness might write on timing where it
writes little on sagittal angle is a reasonable reading of the two studies together, and it is a
hypothesis this study did not test, since only sagittal joint angles were scanned.

A third pathway stays open. If dorsiflexor strength governs walking speed [27] and the endpoint
depends on speed at \u22120.563 \u00b0/(m\u00b7s\u207b\u00b9) (\u00a73.3), weakness reaches the endpoint indirectly. The 0.032\u00b0
figure in \u00a73.3 covers this corpus's 0.056 m\u00b7s\u207b\u00b9 arm difference; over the 0.2 to 1.2 m\u00b7s\u207b\u00b9 range a
stroke cohort presents, the same slope propagates about 0.23\u00b0 across a 0.4 m\u00b7s\u207b\u00b9 gap, comparable to
the entire direct weakness effect. Simulated *plantarflexor* weakness, a different muscle group
again, displaces ankle angle at contact by 15 to 16\u00b0 [10].

The blindness claim is accordingly specific in four ways, and holds within them: for tibialis
anterior scaling between \u00d70.60 and \u00d71.00, for sagittal joint angles, for a design in which walking
speed is nearly matched across the arms, and for this model and controller. Outside them it is
contradicted by [28] and untested.

**2. The arms are confounded with simulation survival, and the confound cannot be lifted.** None of
the 23 admitted hyperreflexia cells reaches the simulation horizon and all 36 weakness cells do, so
no arm comparison at matched survival exists on this corpus, for this readout or any other: the
confound belongs to the corpus rather than to the endpoint. Cells of the mixed grid at the two lowest
gains do reach the horizon, which is what makes a survival-matched comparison possible there at all,
but those gains lie below the primary window and the comparison they support is between two gains
rather than between the arms. Two lines of evidence bound the confound without closing it. The
within-dose duration regression gives 3 \u00b1 9 per cent of the arm effect, and is an extrapolation
rather than a bound because no weakness family contributes to its slope. The seventeen non-reflex
fallers of \u00a73.3, dying in the same band with a normal swing ankle, show that short survival is not
sufficient for the effect. Both leave open whether the hyperreflexia arm's own loss of balance
contributes to it, and that arm is laterally divergent inside the measurement window, so it is losing
balance while it is measured, which the admissibility gate does not test for.

**3. The two lesions are imposed independently; in patients they co-occur.** Crossing them to obtain
independent magnitudes is what makes the apportionment question answerable at all, and patients do
not present that way ([4]; \u00a74.2). In a correlated population a readout shown here to be insensitive
to weakness will still track weakness through its association with tone, so a low swing dorsiflexion
cannot be attributed to one component from the reading alone. Since the treatment decision does turn
on which component is present, chemodenervation for overactivity against orthosis or transfer for
weakness (\u00a71.1), this limits the reading's clinical use and not merely the external validation of the
specificity claim.

**4. The model's early-stance ankle trajectory is not physiological.** The unlesioned ankle
reproduces the loading-response plantarflexion trough and the toe-off excursion (\u221219.8\u00b0 at 59.5 to
63 per cent of cycle, against a normal \u221215 to \u221220\u00b0 at 60 to 62 per cent), and reaches its swing peak
at the phase a normal ankle does. Of four landmarks only that last falls where it should. The
loading-response trough is early and shallow, the ankle dorsiflexes to +10.7\u00b0 by 15 per cent of cycle
where a normal one is near neutral, the terminal-stance peak is consequently early, and the swing
peak at 9.5\u00b0 sits above the normal range of 0 to 5\u00b0 entirely. Readouts in mid-to-late stance,
including the two-sided band of \u00a73.1, sit on the descending limb of that non-physiological excursion,
and their phase does not correspond to the same event in a patient. Taking the endpoint in swing
avoids the phase problem and not the value problem: every displacement we report is measured from a
control whose swing peak is itself outside the normal range.

**5. The endpoint was chosen after the data were seen, from a scan of 81 candidates.** No correction
for multiplicity is applied, no analysis here is confirmatory, and the figures for the endpoint are
the maximum of that scan and so an upper estimate of what a pre-specified choice would have found.
The statement that survives the selection is \u00a73.4's, which holds across all 81.

**6. The method is not new.** A reflex-controlled model with graded deficits of known magnitude and
the controller re-optimised per deficit is established [10], as is grading a spindle-feedback gain
inside a gait model [9], which also reports the direction of the swing effect this paper measures.
What neither did is cross two lesions of different kinds against one another and score a readout on
what it says about each.

**7. No patient data.** Every figure bearing on a clinic, the discriminability of \u00a73.5 and the
attenuation of \u00a74.4, combines this study's effect sizes with published between-patient SDs and
reliabilities. Nothing here was measured in a patient.

"""
s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("4.5: %d -> %d words" % (len(old.split()), len(new.split())))
