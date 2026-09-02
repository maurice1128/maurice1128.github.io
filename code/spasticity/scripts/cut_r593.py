# -*- coding: utf-8 -*-
"""r593: 3.4 to its findings. The scoring apparatus is already in S8; the mechanism goes to S14.

Section 3.4 ran to about 1,160 words, of which roughly half was apparatus: how the counts move under
three measurement-error thresholds and three rank conventions, which Supplement S8 already tabulates
in full; why the denominator is not 81 independent opportunities; the ceiling on a five-level rank
correlation; and the per-gain dose response behind the sign reversal. The findings are the
displacement asymmetry, the count of variables that grade each lesion, the failure of every tone-blind
estimator, and the sign reversal that explains it.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r130_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r131_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()

i, j = s.index("### 3.4 Displacement and grading"), s.index("### 3.5 Detection")
full = s[i:j]

new = u"""### 3.4 Displacement and grading across the scan

Against the unlesioned control, plantarflexor hyperreflexia displaces peak swing dorsiflexion by
\u22129.161\u00b0 and dorsiflexor weakness displaces the same variable by \u22120.430\u00b0, a ratio of 21 to 1. That
ratio is particular to this variable, although the asymmetry itself is not: across the 81 candidates
the median displacement is 0.49\u00b0 for weakness against 1.90\u00b0 for hyperreflexia, weakness reaches 3.95\u00b0
at the knee in early swing, and on ten of the 81 it displaces more than hyperreflexia does. The
direction and the order of magnitude generalise; the factor of 21 does not.

Three variables order the six tibialis anterior scalings at |\u03c1| \u2265 0.8 over spans wider than one
clinical measurement error: the ankle at 75, 80 and 90 per cent of the cycle, at \u03c1 = +0.822, +0.900
and \u22120.820 across 2.870, 2.208 and 2.272\u00b0. Applying the same test to the hyperreflexia group, we find
25. Neither count is fixed. Which published measurement error serves as the threshold, and whether
the rank correlation uses mid-ranks on a tied dose vector, move them: across three defensible
thresholds and three rank conventions the tone count ranges from 14 to 28 and the weakness count from
1 to 7, and their ratio from 3.7 to 14.0 without ever inverting (Supplement S8). We therefore report
the asymmetry as a direction and an order of magnitude, roughly fourfold at its weakest and
fourteenfold at its strongest, and not as a pair of counts. The denominator is not 81 independent
opportunities either, since adjacent samples of one curve are strongly correlated, so the counts index
how much of the cycle each lesion is legible over: calf overactivity over between a sixth and a third
of the sagittal variables a gait laboratory produces, and weakness over a small fraction of that.

The three variables that grade weakness grade tone more strongly at the same phase, their
hyperreflexia spans of 6.308, 6.055 and 4.148\u00b0 standing against weakness spans of 2.870, 2.208 and
2.272\u00b0, larger by 2.2, 2.7 and 1.8 times. A reading taken there moves for two reasons at once.

Weakness depth is not recovered from a reading that does not already know the tone. On the mixed grid
it is recovered neither by knee angle at contact, nor by peak swing dorsiflexion, nor by the two
together, nor by the two with their interaction: every leave-one-weakness-level-out coefficient of
determination is negative, so each does worse than reporting the mean. The fold is demanding but
passable, since the parallel leave-one-gain-level-out folds return R\u00b2 between 0.64 and 0.82 for reflex
gain. Reflex gain is recovered from one reading of one variable at \u03c1 = \u22121.000 across the five gain
levels and \u22120.964 over the 23 hyperreflexia runs, with a leave-one-condition-out calibration error of
0.0062 in delivered gain, 4.5 per cent of the series' range; that condition-level correlation is 1.00
by construction on five ordered levels, and what the run-level figure adds is that the ordering
survives seed-to-seed dispersion. We ran that regression on four feature sets and not on all 81, and
tested one two-stage estimator, which recovers gain at R\u00b2 = 0.946 and then weakness from the knee
residual at R\u00b2 = 0.129.

The failure has a mechanism. Holding reflex gain fixed on the mixed grid and varying tibialis anterior
scaling, the weakness levels are ordered perfectly at delivered KV 0.025 (\u03c1 = +1.000, span 1.201\u00b0),
flat at KV 0.050 (\u03c1 = \u22120.400, span 0.191\u00b0), and ordered perfectly with the opposite sign at KV 0.100
(\u03c1 = \u22121.000, span 1.449\u00b0) and KV 0.220 (\u03c1 = \u22121.000, span 0.753\u00b0). Whether weakening the dorsiflexors
raises or lowers peak swing dorsiflexion therefore depends on how hard the plantarflexors pull against
them, with the crossover near KV 0.050. An estimator blind to the tone cannot use a signal whose sign
it cannot predict. Supplement S14 gives the dose response in full.

A gait recording can report how overactive the calf is. It reports how weak the dorsiflexors are in
three of 81 places, over spans a half to a third the size of the tone signal at the same phase, and,
once tone is present, only in a direction that depends on how much of it there is. In any limb with
calf overactivity a strength measurement is therefore the only available source of the second
quantity.

"""
s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)

q = io.open(Q, encoding="utf-8").read().rstrip() + \
    u"\n\n## S14. The dose response behind the sign reversal, and the ceiling on the rank correlation\n\n" + \
    re.sub(r"^### 3\.4 [^\n]*\n\s*", "", full).strip() + u"\n"
io.open(Q, "w", encoding="utf-8", newline="").write(q)

b = s[s.index("## 1. Background"):s.index("## Figures")]
print("3.4: %d -> %d words;  body %d" % (len(full.split()), len(new.split()), len(b.split())))
