# -*- coding: utf-8 -*-
"""r590: 3.1 and 3.3 to their results. Rationale to Methods, control detail to the supplement.

Section 3.1 spent 223 words justifying the choice of starting variable, which belongs in the
Background and is already made there, and 242 words arguing for the endpoint against the two-sided
candidates, which is interpretation. Section 3.3 stated four confounds and then worked each through
in full, where Supplement S4 already carries the workings.

Both keep every number that a reader needs to follow the argument; the derivations behind them stay
in S4 and S5, and the self-check and binding check fail on anything dropped.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r125_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()

i, j = s.index("### 3.1 The candidate scan"), s.index("### 3.2 Peak ankle")
tab_i = s.index("| variable | control", i)
tab_j = s.index("\n\n", s.index("| knee at contact (0%)", i))
table = s[tab_i:tab_j]

new31 = u"""### 3.1 The candidate scan

Clinical work on this apportionment has most often reported the angle at foot contact, although it is
one point on one of three curves and had never been compared with the rest of them. We therefore
scored 81 candidate variables on the same runs: knee, ankle and hip at every five per cent of the
gait cycle, together with the landmarks a gait report already contains, the peak and trough within
stance and within swing, the angle at toe-off, and the range of motion.

A candidate had to clear two criteria before we considered its separation at all. It has to displace
the lesioned groups from the unlesioned control by more than twice that candidate's own seed SD, and
the two groups' runs have to be disjoint. We also scored a third property, that the two groups be
displaced in opposite directions from control, because a sign reversal is one way, though not the
only way, for a single number to say which lesion dominates. Seven of the 81 meet all three, and they
are not scattered: a contiguous band of the ankle trace in mid-to-late stance (40, 45 and 50 per cent
of the cycle), a single point in mid-swing (85 per cent), and the knee near contact (0, 5 and 100 per
cent). The factor of two halves the count; at one seed SD fourteen candidates qualify, and on sign
alone thirty-three. Knee angle at contact, the endpoint this study began with, is the weakest of the
seven.

""" + table + u"""

The largest separation in the scan is not in that table. Peak ankle dorsiflexion during swing
separates the groups by 8.731\u00b0 with a run-level gap of 6.265\u00b0, which is 76.5 times its own seed SD
and twenty-five times the multiple the contact instant achieves. It is excluded because both groups
are displaced from control in the same direction, hyperreflexia by \u22129.161\u00b0 and weakness by \u22120.430\u00b0,
so it carries no sign reversal. We report it as the endpoint nonetheless. A sign reversal is one way
of saying which lesion dominates and a large dynamic range is another, and on this dataset the second
works better: against the candidates displaced to opposite sides of control, peak swing dorsiflexion
separates the groups more completely, survives measurement error better, displaces the unlesioned
side less, and is stationary within the window where that band is not (\u00a7\u00a73.3, 3.5). It gives up
something we report in \u00a73.4, and the loss is not small: it cannot distinguish an isolated weakness
from an unimpaired limb. We scanned 81 candidates and report the best, so every figure for peak swing
dorsiflexion below is the maximum of that scan. The count of seven does not depend on the selection,
and the pattern running through all 81 is the subject of \u00a73.4.

"""
s = s[:i] + new31 + s[j:]

i, j = s.index("### 3.3 Controls"), s.index("### 3.4 Displacement")
new33 = u"""### 3.3 Controls

The separation could arise without the lesion producing it: from drift under continued optimisation,
from the difference in survival between the groups, from a bilateral re-solution instead of a
lesion-side displacement, or from the choice of admissibility criterion. Re-running a chain through
further optimisation rounds at unchanged severity displaces this endpoint by at most 0.036\u00b0, against
0.586\u00b0 for knee angle at contact, and those displacements do not grow with chain depth. We report
every effect below as a multiple of 0.0358\u00b0, printed here as 0.036\u00b0. Hyperreflexia displaces the
endpoint by \u22129.161\u00b0, 256 times that floor, and weakness by \u22120.430\u00b0, twelve times it. Both lesions
move the ankle the same way and differ only in how far, so the endpoint reports how overactive the
calf is and nothing about which side of normal the limb has ended up on.

Simulation duration is the confound we cannot close. Every weakness run reaches the 20 s horizon and
every hyperreflexia run ends between 9.81 and 17.85 s. The regression our decision rules prescribe
gives a slope of \u22120.041 \u00b0\u00b7s\u207b\u00b9 and propagates 0.298\u00b0 over the 7.28 s difference, 3.4 per cent of the
effect, but that is not a bound: the rule requires within-condition variation in end time, which no
weakness condition has, so all five contributing conditions are hyperreflexia conditions and the
slope is extrapolated into a regime containing none of them. Across those five the standard error of
the mean is 0.102, and we read the regression as 0.30 \u00b1 0.74\u00b0 at one standard error, or 3 \u00b1 24 per
cent of the effect at 95 per cent. Pooling all runs across both groups instead gives 1.101 \u00b0\u00b7s\u207b\u00b9 and
propagates 92 per cent of the effect, but that estimator is circular, since pooling across groups
recovers the group difference the regression is meant to test.

The archive supplies a more direct control. Separate chains carry a plantarflexor-weakness lesion,
which is neither of the two groups and involves no stretch reflex, and many of their runs die early.
Seventeen end between 9.93 and 17.56 s, inside the hyperreflexia group's own band, and their swing
ankle is normal: mean 9.572\u00b0, displaced 0.017\u00b0 from the unlesioned control, which is 0.47 times this
endpoint's artefact floor, with a range of [9.512, 9.673] disjoint from the hyperreflexia group's
[\u22121.974, 2.404] by 7.108\u00b0. They fail to produce the knee signature too, at \u22127.488\u00b0 against control's
\u22127.850\u00b0 and hyperreflexia's \u221211.772\u00b0. Short survival by itself does not make a limb look
hyperreflexic. Whether the hyperreflexia group's own loss of balance adds something on top of the
reflex we cannot say, and no design here could. Supplement S4 gives this control's selection check
and the four remaining controls in full.

Of those four, the per-cycle group difference keeps one sign across the five analysed cycles with a
spread of 0.276\u00b0, 3 per cent of the window mean, against 14 per cent for knee angle at contact and 55
per cent for the two-sided ankle band of \u00a73.1. On the unlesioned right ankle the group difference is
0.047\u00b0, 0.5 per cent of the lesioned side, where knee angle at contact carries 35.5 per cent of its
group separation on the unlesioned side. Walking speed differs between the groups by 0.056 m\u00b7s\u207b\u00b9 and
propagates 0.032\u00b0. Raising the admissibility criterion from 9.73 s to 13.00 s removes 12 of the 23
hyperreflexia runs and none of the 36 weakness runs while the run-level gap rises from 6.265 to
6.302\u00b0.

"""
s = s[:i] + new33 + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
b = s[s.index("## 1. Background"):s.index("## Figures")]
print("3.1 -> %d words, 3.3 -> %d words, body %d"
      % (len(new31.split()), len(new33.split()), len(b.split())))
