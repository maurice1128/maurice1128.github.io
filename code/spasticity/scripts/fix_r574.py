# -*- coding: utf-8 -*-
"""r574: the closing list. Abstract to length, claims to what was tested, S7 to the registration."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r91_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r92_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
q = io.open(Q, encoding="utf-8").read()
n = [0, 0]


def _rep(txt, o, nn, which):
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(txt))
    if len(ms) != 1:
        print("  SKIP(%d) %s: %s" % (len(ms), which, o[:52]))
        return txt
    n[0 if which == "MS" else 1] += 1
    return txt[:ms[0].start()] + nn + txt[ms[0].end():]


def rep(o, nn):
    global s
    s = _rep(s, o, nn, "MS")


def qrep(o, nn):
    global q
    q = _rep(q, o, nn, "SUP")


# ---- 1. the title states as physiology what is a comparison of two graded ladders
rep(u"# Calf overactivity is written on the sagittal ankle several times more strongly than dorsiflexor weakness: an 81-readout search in a ground-truth gait simulation",
    u"# Graded calf hyperreflexia is written on the sagittal ankle several times more strongly than graded dorsiflexor weakness: an 81-readout search in a ground-truth gait simulation")

# ---- 2. the abstract: to length, and to what was tested
i, j = s.index(u"## Abstract"), s.index(u"**Keywords.**")
s = s[:i] + u"""## Abstract

**Background.** Apportioning a spastic equinovarus foot between calf overactivity and dorsiflexor
weakness decides between opposite treatments, and the procedure that does it, a diagnostic nerve
block, is invasive because no non-invasive measurement apportions. Which gait reading carries the
apportionment has not been asked where both magnitudes are known.

**Methods.** We lesioned a 19-degree-of-freedom, 22-muscle reflex-controlled model by a
velocity-dependent stretch reflex on soleus and gastrocnemius and by scaling of tibialis anterior
force, re-optimising the controller for each lesion so that both magnitudes are known exactly. Eleven
lesion families and one control lineage passed a fixed admissibility gate, and a separate 84-cell
grid crossed the lesions. Rather than assume an endpoint we scored 81 candidate sagittal readouts,
across three joints and the whole cycle.

**Results.** Peak ankle dorsiflexion in swing separated the two lesions completely: the cell-level gap
was 6.265\u00b0, 175 times the largest measured protocol artefact, and it graded the reflex at \u03c1 = \u22121.000
across the five gain levels. Seventeen cells carrying a third lesion and dying in the same time band
read as unimpaired at this landmark, so short survival does not produce the signature. Under 3\u00b0 of
simulated jitter the lesions remained distinguished at 0.995 accuracy against 0.939 for knee angle at
contact. The asymmetry runs through the whole scan, though its size depends on how it is scored:
across three measurement-error bars and three rank conventions, 14 to 28 of the 81 candidates grade
calf overactivity usably against 1 to 7 for weakness, a ratio between 3.7 and 14 that never inverts,
and under the study's own noise model the weakness count falls to zero. On the mixed grid, no readout
or combination of the four we tested recovers weakness without first knowing the tone, because the
weakness signal reverses direction across the gain range.

**Conclusions.** Moving from the knee at contact to the ankle in swing raises the standardised effect
against the spread a stroke cohort presents from *d* = 0.59 to 1.50 and cuts the misassignment of a
single reading from 38 to 23 per cent, on a variable gait laboratories already record. It is a
group-level calibration and not a test for an individual. Both magnitudes are known here and in no
patient; the reading grades calf overactivity and not its mechanism; the weakness ladder stops at
\u00d70.80 where patients reach far lower; and one patient cohort reports an association with dorsiflexor
force of the size this model calls faint.

""" + s[j:]

# ---- 3. 4.1 and 4.4 disagree on which design the sample size is for
rep(u"""A correlational study of the size proposed in \u00a74.4 therefore
needs roughly a sixth the sample at the ankle that it would need at the knee, so the choice of
instant decides whether the patient study is affordable.""",
u"""A two-group comparison at the ankle would therefore need roughly a sixth the sample it needs at the
knee. That ratio is a property of the discriminability and not a sample size for the study \u00a74.4
proposes, which is correlational and needs its own arithmetic; what transfers is that the choice of
instant decides whether a patient study is affordable.""")

# ---- 4. the four-seed bar is a registered rule for the grid, and 2.3 does not say so
rep(u"""A separate 84-cell mixed grid, 74 of them admitted, crosses four tibialis anterior scalings
with four delivered reflex gains and supports \u00a73.4 and \u00a73.7; it is not part of the 65-cell census.""",
u"""A separate 84-cell mixed grid, 74 of them admitted, crosses four tibialis anterior scalings with
four delivered reflex gains and supports \u00a73.4 and \u00a73.7; it is not part of the 65-cell census. Its
registration restricts reading to grid cells where at least four of six seeds pass gate G, and cells
below that bar are reported as uninformative rather than dropped. That bar is a registered rule for
the grid and is not applied to the primary corpus, whose families are admitted at whatever count they
reach.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

# ---- 5. S1 promises a table the manuscript already carries
s2 = io.open(P, encoding="utf-8").read()
s2 = s2.replace(
 u"Supplement S1 gives the per-readout figures, the sense in which the two detection columns are\nsensitivities rather than accuracies, and the rank-convention correction that applies to the \u03c1\ncolumn.",
 u"Supplement S1 sets out the sense in which the two detection columns are sensitivities rather than\naccuracies, what the noise model does and does not stress, and the rank-convention correction that\napplies to the \u03c1 column.")
io.open(P, "w", encoding="utf-8", newline="").write(s2)

# ---- 6. S7 gives the registration in full, with all four predictions labelled
qrep(u"""**Post hoc elements.** Two parts of the mixed grid entered after the registration was hashed: the
\u00d70.70 tibialis anterior row and the highest gain column. Every analysis of the grid uses all 74
admitted cells and \u00a73.7 marks where the post hoc elements enter a comparison.""",
u"""**The four predictions, as registered.** All four were made about knee angle at initial contact on
the mixed grid, which is why none of them is a registered test of the endpoint this paper reports.
They are translated here from the registration, which is written in Chinese.

*P1, the spasticity axis is monotone.* At each level of weakness, the cell mean of knee angle at
contact becomes more flexed, that is more negative, as the reflex gain rises, monotonically across
three rungs.

*P2, the weakness axis is monotone and runs the other way.* At each reflex gain, knee angle at contact
becomes more extended, that is more positive, as weakness deepens.

*P3, mixed lesions can be ordered.* This was designated the key prediction. A fixed threshold exists
that separates the spasticity-dominant cells (gain 0.050 with \u00d71.00 or \u00d70.80) from the
weakness-dominant cell (gain 0.0125 with \u00d70.60) without overlap. Should they overlap, knee angle
cannot order mixed lesions and the clinical claim fails, which the registration requires be reported
as such.

*P4, cancellation exists.* At least one pair of cells at different combinations of gain and weakness
has overlapping ranges of knee angle at contact, so a single knee reading cannot uniquely determine
the lesion combination. The registration marks this as an expected limitation rather than a failure,
and states that if it does not hold, the knee is a fully invertible readout and that is the stronger
result.

**How each stands.** P1 and P2 are uninformative as registered: both are monotonicity statements over
three rungs on an axis this paper reports over more. P3 cannot be evaluated because its
weakness-dominant cell sits on the \u00d70.60 row, which exists at three seeds and so reaches the
registered four-of-six bar in no cell; it is excluded by the seed bar and not by gate G, which it
passes in 10 of 12. P4 was informative and is tested in \u00a73.7, where it holds at the knee for the six
registered pairs and, at the reported endpoint, holds for pairs differing in weakness and fails for
pairs differing in tone.

**Two further registered controls.** The duration control was enforced on P1 to P3, with a
propagation above 50 per cent of the effect declaring the result confounded. And a batch null was
fixed in advance: the largest boundary difference measured between families of the same mechanism was
0.5697\u00b0, and no gap between cells smaller than that may be called a separation.

**Post hoc elements.** Two parts of the mixed grid entered after the registration was hashed: the
\u00d70.70 tibialis anterior row and the highest gain column. Every analysis of the grid uses all 74
admitted cells unless stated otherwise, and \u00a73.7 marks where the post hoc elements enter a
comparison.""")

io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("manuscript edits: %d;  supplement edits: %d" % (n[0], n[1]))
