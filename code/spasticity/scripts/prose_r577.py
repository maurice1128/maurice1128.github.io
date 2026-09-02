# -*- coding: utf-8 -*-
"""r577: restore ordinary connectives and hedges, at the density the comparators use.

Measured over the same sections, Jansen carries 7.66 connectives and hedges per thousand words and
Ong 4.00; this manuscript carried 0.17 before r576 and 0.50 after. The ban that produced that was
self-imposed and wider than the instruction, which named "moreover", "furthermore" and "in addition".
Those three stay out. The words the comparators actually lean on are "however", "although",
"whereas", "suggest" and "likely", and 34 of Ong's 39 instances are those five.

Hedges go on inferences and never on measurements. Where two adjacent sentences stood as a statement
and its antithesis, they are joined, which also removes the epigram the cold read flagged.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r96_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:58]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


PAIRS = [
 # --- contrastive pairs joined
 (u"""Knee angle at contact, the endpoint this study began with, is the weakest of the seven.

The largest separation in the whole scan is not in that table.""",
  u"""Knee angle at contact, the endpoint this study began with, is the weakest of the seven.

The largest separation in the whole scan, however, is not in that table."""),

 (u"""No term rewards toe clearance, so nothing in the objective pushes the weakness arm to compensate for a
dropped foot by exaggerated hip and knee flexion. That absence is a property of the objective and
not a result.""",
  u"""No term rewards toe clearance, so nothing in the objective pushes the weakness arm to compensate for
a dropped foot by exaggerated hip and knee flexion. That absence, although consequential for what
follows, is a property of the objective rather than a result."""),

 (u"""Halving the sampling interval would roughly double both counts and change nothing. The counts index how much of the cycle
each lesion is legible over, not how many separate measurements report it.""",
  u"""Halving the sampling interval would roughly double both counts and change nothing, so the counts
index how much of the cycle each lesion is legible over rather than how many separate measurements
report it."""),

 (u"""The two detection columns are also sensitivities rather than accuracies, since no
control cell is classified in producing them: the endpoint's 1.000 for detecting hyperreflexia
becomes 0.687 at 3\u00b0 of jitter once the six control cells are classified too.""",
  u"""The two detection columns are also sensitivities rather than accuracies, since no control cell is
classified in producing them; the endpoint's 1.000 for detecting hyperreflexia becomes 0.687 at 3\u00b0 of
jitter once the six control cells are classified as well."""),

 # --- hedges on inferences
 (u"""Gap-to-noise is a property of the pipeline, and only part of it transfers.""",
  u"""Gap-to-noise is a property of the pipeline, and only part of it is likely to transfer."""),

 (u"""That is where the difficulty lies, and it lies upstream of any measurement.""",
  u"""That is where the difficulty appears to lie, and it lies upstream of any measurement."""),

 (u"""A gait recording grades one component of a spastic equinovarus foot well and
the other faintly, and the difference is not an instrumental limitation a better laboratory would
remove.""",
  u"""A gait recording grades one component of a spastic equinovarus foot well and the other faintly, and
the difference is unlikely to be an instrumental limitation that a better laboratory would remove."""),

 (u"""and the most likely reason is that its tibialis anterior retains more reserve in an
unloaded swing limb than a paretic one does.""",
  u"""and the most likely reason, although we cannot test it here, is that its tibialis anterior retains
more reserve in an unloaded swing limb than a paretic one does."""),

 (u"""That weakness might write on timing where it
writes little on sagittal angle is a reasonable reading of the two studies together, and it is a
hypothesis this study did not test, since only sagittal joint angles were scanned.""",
  u"""Weakness may therefore write on timing where it writes little on sagittal angle, which is a
reasonable reading of the two studies together, although it is a hypothesis this study did not test,
since only sagittal joint angles were scanned."""),

 (u"""It is a hypothesis about human gait rather than a measurement of it.""",
  u"""It should be read as a hypothesis about human gait rather than as a measurement of it."""),

 (u"""A re-optimised body redistributes a local deficit, and a single-joint reading registers the
redistribution along with the deficit.""",
  u"""A re-optimised body appears to redistribute a local deficit, so a single-joint reading is likely to
register the redistribution along with the deficit."""),

 (u"""What it registers is almost entirely a lesion-side displacement.""",
  u"""What it registers, therefore, is almost entirely a lesion-side displacement."""),

 (u"""Better instrumentation would not reduce it, because the limit is set by the
spread between patients and only faintly by the precision of the reading.""",
  u"""Better instrumentation would not reduce it, however, because the limit is set by the spread between
patients and only faintly by the precision of the reading."""),

 (u"""Under noise those values move, and they do not move together.""",
  u"""Under noise those values move, although they do not move together."""),

 (u"""The reading grades calf overactivity as a marker and not as a direct
observation of the calf.""",
  u"""The reading is best understood as grading calf overactivity as a marker rather than as a direct
observation of the calf."""),

 (u"""The apportionment fails at the knee for want of resolution, not for want of signal""",
  u"""The apportionment appears to fail at the knee for want of resolution rather than for want of
signal"""),

 (u"""Both are approximations, and the guidance retains the block alongside them instead of replacing them
with it [1], which we read as a response to their limitations, though the paper does not say so.""",
  u"""Both are approximations, and the guidance retains the block alongside them instead of replacing them
with it [1], which we read as a response to their limitations, although the paper does not say so."""),

 (u"""so the clinical question is rarely which of the three a limb has and usually how much of each.""",
  u"""so the clinical question is rarely which of the three a limb has, and is usually how much of each."""),

 (u"""We read that as a response""", u"""This suggests a response"""),
]

for o, nn in PAIRS:
    rep(o, nn)

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits: %d" % n[0])
