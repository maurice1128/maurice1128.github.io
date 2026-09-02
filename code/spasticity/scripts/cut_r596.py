# -*- coding: utf-8 -*-
"""r596: 4.1 to 4.3 to length. The between-patient derivation moves to S15."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r134_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r135_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()

i, j = s.index("### 4.1 Interpretation"), s.index("### 4.4 Limitations")
old = s[i:j]

new = u"""### 4.1 Interpretation

Plantarflexor overactivity is legible over between a sixth and a third of the sagittal variables a
gait laboratory produces, and dorsiflexor weakness over a fraction of that, moving the reading 2.2,
2.7 and 1.8 times less far than tone does at the same phase where it is legible at all (\u00a73.4). A gait
recording grades one component of a spastic equinovarus foot well and the other faintly, and that is
unlikely to be an instrumental limitation a better laboratory would remove.

The instant appears to matter more than the joint. At foot contact the ankle does not separate the
groups and the knee does, which is the comparison we first made and it stands, but it was never the
whole of clinical practice: peak dorsiflexion in swing is already a reported variable, and in a
34-patient chronic stroke cohort it separated the contact-type groups more strongly than the angle at
contact did (p < 0.001 against p = 0.003) [5]. Extended to the whole cycle the ordering reverses. The
best variable in the study is at the ankle in swing, exceeding knee angle at contact by a factor of
twenty-five in gap-to-noise and the best knee variable anywhere in the scan, the knee at 25 per cent
of the cycle at 17.4 seed SD, by a factor of four.

Gap-to-noise is a property of the pipeline and only part of it is likely to transfer. Against the
between-patient spread the ankle gains twice over: the effect is 1.7 times larger and the spread at
its landmark 1.5 times smaller, 5.55\u00b0 against 8.57\u00b0, both reconstructed here from the two subgroups
of ref [5] and not reported there. With a single measurement's error this gives a total SD of 5.82\u00b0,
against which the 8.731\u00b0 effect is *d* = 1.50 and misassigns about 22.7 per cent of single readings,
where knee angle at contact misassigns 38.4 per cent. A two-group comparison at the ankle would
therefore need roughly a sixth the sample it needs at the knee, which is a property of the
discriminability and not a sample size for the correlational study \u00a74.3 proposes. These data support
measuring the ankle in swing instead of at contact; they do not support moving from the ankle to the
knee. Supplement S15 gives the derivation, the cohort's exclusions, and the caveat attaching to the
knee comparator's reliability figure.

A simulation is the instrument this question needs, because the apportionment requires both lesion
magnitudes in one limb at once and the only procedure that supplies either is the diagnostic block,
which is invasive, removes one component and cannot calibrate the other. Supplement S13 sets out that
argument.

### 4.2 Scope of the reading

The lesion imposed here is a velocity-dependent stretch reflex, which is spasticity in the strict
sense, and it is not the only plantarflexor abnormality a hemiparetic limb carries. In eleven
hemiparetic adults, five of whom had undergone tibial neurotomy abolishing plantarflexor spasticity,
plantarflexor cocontraction during swing was present in the operated group and larger than in the
unoperated one, soleus coefficient 1.48 \u00b1 0.2 against 0.95 \u00b1 0.3, and began before any stretch [26].
Against diagnostic nerve block the same conclusion is reached independently: improvement in swing
dorsiflexion after block was associated with soleus cocontraction rather than with Tardieu-graded
spasticity, and although that association is not itself significant (OR 4.72, 95 per cent CI 0.86 to
26.04), the absence of any association between Tardieu-graded spasticity and soleus overactivity
during swing is unambiguous in the same study [3]. Ref [26] reports no ankle kinematics separately
for its two subgroups, so the proposition that abolishing spasticity leaves the dorsiflexion deficit
unchanged is asserted there rather than tested.

That work bounds the interpretation of this variable without contradicting the result. A
velocity-dependent stretch reflex acting alone displaces the variable by 9.161\u00b0 and grades
monotonically with its own strength; what cannot be established from a model containing no other
plantarflexor abnormality is that a low reading in a patient is produced by that reflex rather than by
cocontraction or by shortening. The endpoint should therefore be described as grading calf
overactivity, not spasticity. For the decision it is offered to serve, part of that is not a retreat,
since overactivity from a stretch reflex and overactivity from cocontraction are both treated by
chemodenervation or neurotomy. The retreat is larger, because this model contains no muscle\u2013tendon
shortening: a limb whose calf is short rather than overactive would read low here as well, and
shortening is treated by stretching or lengthening, a distinction the assessment pathway is organised
around [1] and one shown to change the treatment chosen in individual patients [20]. The reading
separates plantarflexor abnormality of any origin from dorsiflexor weakness, and a clinical protocol
using it would still need the passive assessment that separates overactivity from shortening.

### 4.3 A patient study

This study offers a negative with a consequence and a calibration. The negative is that no sagittal
joint angle, alone or in combination, reports dorsiflexor weakness over the range examined once
measurement error is applied (\u00a7\u00a73.4, 3.5). An instrumented assessment that measures gait and infers
strength from it is measuring one component twice, so the two-predictor design a patient study should
use, plantarflexor tone and dorsiflexor strength entered together, is required by the second predictor
being unobtainable from the first's data rather than by statistical prudence.

The calibration is of a variable clinics already record. Peak ankle dorsiflexion in swing orders
reflex gain at \u03c1 = \u22121.000 across the five gain levels; against the between-patient spread of a chronic
stroke cohort it misassigns about one reading in four, its five-level series resolves only one
adjacent pair above the between-session measurement error, and the rectification drift of \u00a73.5 is the
size of the gaps it would have to resolve. It supports a coarse contrast, a limb with substantial calf
overactivity against one without, and not a graded tone score for an individual. Marker-based capture
is required, since reported ankle errors for video-based pose estimation are 6.3 to 7.4\u00b0 depending on
limb and camera view (\u00a73.6).

The study we would run next is cross-sectional with three measurements per limb: instrumented gait
giving peak dorsiflexion in swing; a graded measure of calf overactivity, ideally against a diagnostic
block in the subgroup receiving one; and dorsiflexor strength by dynamometry. The relation to
establish is whether the gait variable tracks graded overactivity once strength is held constant,
which is what this simulation predicts and which the co-occurrence of the two components in patients
([4]; Supplement S13) makes impossible to read off an unadjusted correlation. Detecting a partial
correlation of 0.4 with strength partialled out needs about 50 limbs, and 0.3 needs about 90; one
session's measurement error attenuates such a correlation by 4 to 6 per cent, which is not the
limiting consideration at those sample sizes.

"""
s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)

q = io.open(Q, encoding="utf-8").read().rstrip() + \
    u"\n\n## S15. The transfer to a patient cohort, in full\n\n" + \
    old[old.index(u"Gap-to-noise is a property of the pipeline"):old.index(u"A simulation is the instrument")].strip() + \
    u"\n"
io.open(Q, "w", encoding="utf-8", newline="").write(q)

b = s[s.index("## 1. Background"):s.index("## Figures")]
print("4.1-4.3: %d -> %d words;  body %d" % (len(old.split()), len(new.split()), len(b.split())))
