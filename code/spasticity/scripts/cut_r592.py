# -*- coding: utf-8 -*-
"""r592: the Discussion to comparator length. The apparatus moves; the argument stays.

Of 11,355 body words, the primary result occupies 605. The Discussion occupies 3,601 against
Jansen's 1,991 and Ong's 1,499, and 4.5 alone runs to about 1,500 in a paper whose comparators give
limitations 300 and 250. Section 4.2 argues why a simulation is the right instrument, which both
comparators place in their introduction and which reads in the Discussion as a defence; it folds into
4.1 in two sentences. Section 4.5 keeps each limitation in one paragraph and its workings move to a
new Supplement S12.

Nothing is withdrawn. Every limitation is still stated in the main text, and the reasoning behind
each is one click away instead of on the page.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r128_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r129_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()

# --- 4.5 moves out whole; a compressed version stays
i, j = s.index("### 4.5 Limitations"), s.index("## 5. Conclusions")
full45 = s[i:j]

new45 = u"""### 4.5 Limitations

**The model and its lesions.** No convention governs how spasticity and weakness enter a
musculoskeletal simulation: gains chosen arbitrarily [9], force and tendon slack scaled per condition
[10], hyperreflexia set against plantarflexor weakness in two dimensions [11], and in personalised
cerebral-palsy models impairments of known magnitude explaining on average 17 per cent of the
kinematic deviation and never more than 39 [12]. Our study sits inside that spread, and the asymmetry
we report rests on how much reserve this model's tibialis anterior retains in an unloaded swing limb,
which no internal control reaches. Ours is also a shallow weakness range: Ong et al. model mild,
moderate and severe plantarflexor weakness at 25, 12.5 and 6.25 per cent of maximum isometric force
[10], where our deepest is 60 per cent and the primary series runs from \u00d70.80 to \u00d70.95. We could not
go deeper and keep a walking model under this controller. The unlesioned ankle is also only
approximately physiological, dorsiflexing to +10.7\u00b0 by 15 per cent of cycle where a normal one is
near neutral, and reaching a swing peak of 9.5\u00b0 above the normal range of 0 to 5\u00b0; taking the endpoint
in swing avoids the phase problem and not the value problem.

**What the design cannot separate.** Predictive simulations stop walking under a deep enough deficit,
which is a property of this class of model rather than of this study [10], and here that coupling
falls along the lesion axis: none of the 23 admitted hyperreflexia runs reaches the horizon and all 36
weakness runs do, so no group comparison at matched survival exists. The within-condition duration
regression gives 3 \u00b1 24 per cent of the effect at 95 per cent and is an extrapolation rather than a
bound; the seventeen non-reflex fallers show that short survival is not sufficient for the effect;
neither settles whether the hyperreflexia group's own loss of balance contributes to it. Separately,
we imposed the two lesions independently, and patients do not present that way ([4]; \u00a74.2). In a
correlated population a variable insensitive to weakness will still track it through its association
with tone, so a low swing dorsiflexion cannot be attributed to one component from the reading alone.
Since the treatment decision does turn on which component is present, this limits the reading's
clinical use and not merely the external validation of the specificity claim.

**The status of the result.** We chose the endpoint after seeing the data, from a scan of 81
candidates; we apply no correction for multiplicity, treat no analysis as confirmatory, and report
the endpoint's figures as the maximum of that scan. The statement that survives the selection is
\u00a73.4's, which holds across all 81. The method is not new: a reflex-controlled model with graded
deficits and per-deficit re-optimisation is established [10], as is grading a spindle-feedback gain
inside a gait model [9], which also reports the direction of the swing effect. What neither did is
cross two lesions of different kinds and score a variable on what it says about each. And every
figure bearing on a clinic combines this study's effect sizes with published between-patient SDs and
reliabilities. We measured nothing here in a patient.

The insensitivity to weakness holds in four respects only: for tibialis anterior scaling between
\u00d70.60 and \u00d71.00, for sagittal joint angles, for a design in which walking speed is nearly matched, and
for this model and controller. Outside them it is contradicted by [28] and untested. Supplement S12
gives each limitation with its workings, including the patient results that bound the asymmetry and
the three pathways by which weakness may still reach the endpoint.

"""
s = s[:i] + new45 + s[j:]

# --- 4.2 folds into 4.1
i2 = s.index("### 4.2 The case for a simulation")
j2 = s.index("### 4.3 Scope of the reading")
full42 = s[i2:j2]
s = s[:i2] + s[j2:]

rep_target = u"These data support measuring the ankle in swing instead of at contact; they do not support moving from the ankle to the knee."
add = (u"These data support measuring the ankle in swing instead of at contact; they do not support moving "
       u"from the ankle to the knee.\n\nA simulation is the instrument this question needs because the "
       u"apportionment requires both lesion magnitudes in one limb at once, and the only procedure that "
       u"supplies either is the diagnostic block, which is invasive, removes one component, and cannot "
       u"calibrate the other. Supplement S13 sets out that argument in full.")
pat = re.compile(r"\s+".join(re.escape(w) for w in rep_target.split()))
ms = list(pat.finditer(s))
if len(ms) == 1:
    s = s[:ms[0].start()] + add + s[ms[0].end():]
else:
    print("  SKIP: 4.1 closing sentence matched %d times" % len(ms))

io.open(P, "w", encoding="utf-8", newline="").write(s)

q = io.open(Q, encoding="utf-8").read().rstrip() + u"\n\n## S12. The limitations of \u00a74.5, with their workings\n\n" \
    + re.sub(r"^### 4\.5 Limitations\s*", "", full45).strip() \
    + u"\n\n## S13. Why this question needs a simulation\n\n" \
    + re.sub(r"^### 4\.2 The case for a simulation\s*", "", full42).strip() + u"\n"
io.open(Q, "w", encoding="utf-8", newline="").write(q)

b = s[s.index("## 1. Background"):s.index("## Figures")]
print("4.5: %d -> %d words;  4.2: %d moved;  body %d"
      % (len(full45.split()), len(new45.split()), len(full42.split()), len(b.split())))
