# -*- coding: utf-8 -*-
"""r563: move the per-readout detail of 3.5 into Supplement S1, keeping the verdicts in the text."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r78_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r79_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:56]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


rep(u"""Distinguishing the two lesions survives measurement error on every candidate, and best on the
readouts that take a peak or average a window. The reason is not the same for the two: a window mean
divides zero-mean jitter by the square root of its sample count, whereas a maximum amplifies it
(\u00a73.6) and survives instead because its clean gap-to-noise is 76.5 seed SD rather than because it
handles noise well. Grading tone survives on the ankle, however, and degrades sharply on the knee.
Grading weakness survives nowhere among these four, and detecting an isolated weakness against an
unimpaired limb returns 0.50 to 0.65 on all of them, which is \u00a73.4's asymmetry expressed as a
detection problem rather than a grading one. Those two detection figures are sensitivities and not
accuracies: no control cell is classified in producing them, so they carry no false-positive rate and
cannot be read against a chance level, which is undefined without one. They say that half to
two-thirds of isolated weakness cells clear a threshold, not that the readout performs at chance. The
balanced figure, which does classify the six controls, is 0.687 for the endpoint at 3\u00b0 and is
reported here for the first time. The three readouts that do grade weakness
on noise-free traces (\u00a73.4) were put through the same model separately and none survives it: their
rank correlations with weakness depth fall from 0.822, 0.900 and 0.820 to 0.707, 0.693 and 0.682 at
3\u00b0 of jitter, below the 0.8 bar \u00a73.4 applies. Under this study's own measurement model the number of
readouts that grade weakness is not three but zero, and the counts in \u00a73.4 should be read as
noise-free throughout. One convention note applies to the \u03c1 column of the table above: it was
computed with the same helper \u00a73.4 describes, which did not use mid-ranks, and correcting that moves
the tone correlations by up to 0.12 in the direction of a stronger relation. The column is therefore
a lower bound on magnitude, which is the conservative direction for the argument it is used in. The reported endpoint is not best in two
of the five columns: detecting an isolated weakness against an unimpaired limb, and grading weakness
depth, and in both the reason is \u00a73.4's asymmetry rather than any property of the readout. In the
second of them no candidate is usable, so being beaten there is not informative.""",
u"""The three claims separate cleanly. Distinguishing the two lesions survives measurement error on
every candidate, best on readouts that take a peak or average a window, though for opposite reasons:
a window mean divides zero-mean jitter by the root of its sample count, while a maximum amplifies it
(\u00a73.6) and survives on the size of its clean gap rather than on noise handling. Grading tone survives
on the ankle and degrades sharply on the knee. Grading weakness survives nowhere. The three readouts
that grade it on noise-free traces were put through the same model separately and none clears the 0.8
bar at 3\u00b0 of jitter, so under this study's own measurement model the count of readouts that grade
weakness is zero rather than three, and \u00a73.4's counts should be read as noise-free throughout.

The reported endpoint is not best in two of the five columns, detecting an isolated weakness and
grading weakness depth, and in both the reason is \u00a73.4's asymmetry rather than a property of the
readout; in the second no candidate is usable at all, so being beaten there carries no information.
Supplement S1 gives the per-readout figures, the sense in which the two detection columns are
sensitivities rather than accuracies, and the rank-convention correction that applies to the \u03c1
column.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

sup = io.open(Q, encoding="utf-8").read()
i = sup.index(u"## S2.")
ins = u"""**What the five columns of \u00a73.5 do and do not measure.** The two detection columns are
sensitivities and not accuracies: no control cell is classified in producing them, so they carry no
false-positive rate and cannot be read against a chance level, which is undefined without one. A
value of 0.512 says that half of isolated weakness cells clear a threshold, not that the readout
performs at chance. The balanced figure, which does classify the six control cells, is 0.687 for the
reported endpoint at 3\u00b0 of jitter. Detecting an isolated weakness against an unimpaired limb returns
0.50 to 0.65 across the four candidates tested, which is \u00a73.4's asymmetry expressed as a detection
problem rather than a grading one.

**The three weakness-grading readouts under the noise model.** Their rank correlations with weakness
depth fall from 0.822, 0.900 and 0.820 on noise-free traces to 0.707, 0.693 and 0.682 at 3\u00b0 of
per-frame jitter, all below the 0.8 bar \u00a73.4 applies, over 200 realisations of the same model.

**A convention note on the \u03c1 column.** It was computed with the helper described in \u00a73.4 and
Supplement S8, which did not use mid-ranks on a tied dose vector. Correcting that moves the tone
correlations by up to 0.12 in the direction of a stronger relation, so the column as printed is a
lower bound on magnitude, which is the conservative direction for the argument it supports.

"""
sup = sup[:i] + ins + sup[i:]
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("edits applied: %d" % n[0])
