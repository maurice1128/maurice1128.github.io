# -*- coding: utf-8 -*-
"""r552: second batch of round-four council repairs."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r63_MANUSCRIPT"))
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


# 1 -- the two-sidedness bar is 2x seed SD in code and was written as 1x
rep(u"""We required a candidate to clear two bars before considering its separation at all. It has to
displace the lesioned arms from the unlesioned control by more than that candidate's own noise, and
the two arms' cells have to be disjoint. A third property, that the two arms be displaced in
opposite directions from control, was also scored, because a sign reversal is one way (not the only
way) for a single number to say which lesion dominates. Seven of the 81 candidates separate the two
arms with the cells disjoint and both arms displaced from control in opposite directions.""",
u"""We required a candidate to clear two bars before considering its separation at all. It has to
displace the lesioned arms from the unlesioned control by more than twice that candidate's own seed
SD, and the two arms' cells have to be disjoint. A third property, that the two arms be displaced in
opposite directions from control, was also scored, because a sign reversal is one way (not the only
way) for a single number to say which lesion dominates. Seven of the 81 candidates meet all three.
The factor of two is a choice and it halves the count: at one seed SD, which is the bar a reader
would assume from the phrase "more than its own noise", fourteen candidates qualify rather than
seven, and on sign alone with no magnitude condition, thirty-three. We report the strict count and
name the bar because the looser ones change which readouts appear below without changing the
conclusion drawn from them.""")

# 2 -- figure 3 caption states sign only
rep(u"""Rings mark the
candidates that are also two-sided, that is, that displace the two arms to opposite sides of the
unlesioned control.""",
u"""Rings mark the
candidates that are also two-sided, that is, that displace the two arms to opposite sides of the
unlesioned control by more than twice that candidate's own seed SD (\u00a73.1; on sign alone the count is
thirty-three rather than eight).""")

# 3 -- a two-stage estimator WAS tested
rep(u"""A two-stage estimator that grades
tone first and then applies the sign-appropriate weakness relation is not excluded by anything
reported here, and we did not test one.""",
u"""One two-stage estimator was tested: grading gain from
the ankle recovers it at R\u00b2 = 0.95, but reading weakness off the knee residual afterwards recovers
only R\u00b2 = 0.13. What that leaves open is the sign-appropriate variant, which applies a different
weakness relation on each side of the reversal and which we did not test.""")

# 4 -- the two detection columns are sensitivities, and chance is undefined without a specificity
rep(u"""Grading weakness survives nowhere among these four, and detecting an isolated weakness against an
unimpaired limb falls to near chance on all of them, 0.50 to 0.65, which is \u00a73.4's asymmetry
expressed as a detection problem rather than a grading one.""",
u"""Grading weakness survives nowhere among these four, and detecting an isolated weakness against an
unimpaired limb returns 0.50 to 0.65 on all of them, which is \u00a73.4's asymmetry expressed as a
detection problem rather than a grading one. Those two detection figures are sensitivities and not
accuracies: no control cell is classified in producing them, so they carry no false-positive rate and
cannot be read against a chance level, which is undefined without one. They say that half to
two-thirds of isolated weakness cells clear a threshold, not that the readout performs at chance. The
balanced figure, which does classify the six controls, is 0.687 for the endpoint at 3\u00b0 and is
reported here for the first time.""")

# 5 -- the rank correlation: sign, and the convention
rep(u"""of one variable at Spearman \u03c1 = 0.956 over the 23 hyperreflexia cells, with a leave-one-family-out""",
    u"""of one variable at Spearman \u03c1 = \u22121.000 across the five gain levels and \u22120.964 over the 23
hyperreflexia cells, with a leave-one-family-out""")
rep(u"""as anything in the scan, \u03c1 = 0.951, but over a span of 0.66\u00b0, and \u00a73.5 sets that against the two""",
    u"""as anything in the scan, \u03c1 = +1.000 across the six scalings and +0.966 across cells, but over a
span of 0.66\u00b0, and \u00a73.5 sets that against the two""")
rep(u"""dorsiflexion in swing orders reflex gain at \u03c1 = 0.956; against the between-patient spread of a""",
    u"""dorsiflexion in swing orders reflex gain at \u03c1 = \u22121.000 across the five gain levels; against the
between-patient spread of a""")
rep(u"""completely at the cell level, grades the reflex with \u03c1 = 0.956, and does both under a simulated""",
    u"""completely at the cell level, grades the reflex with \u03c1 = \u22121.000 across the five gain levels, and
does both under a simulated""")
rep(u"""and the reflex was graded at \u03c1 = 0.956.""",
    u"""and the reflex was graded at \u03c1 = \u22121.000 across the five gain levels.""")

# 6 -- the noise-model table's rho column uses the uncorrected helper
rep(u"""3\u00b0 of jitter, below the 0.8 bar \u00a73.4 applies. Under this study's own measurement model the number of
readouts that grade weakness is not three but zero, and the counts in \u00a73.4 should be read as
noise-free throughout.""",
u"""3\u00b0 of jitter, below the 0.8 bar \u00a73.4 applies. Under this study's own measurement model the number of
readouts that grade weakness is not three but zero, and the counts in \u00a73.4 should be read as
noise-free throughout. One convention note applies to the \u03c1 column of the table above: it was
computed with the same helper \u00a73.4 describes, which did not use mid-ranks, and correcting that moves
the tone correlations by up to 0.12 in the direction of a stronger relation. The column is therefore
a lower bound on magnitude, which is the conservative direction for the argument it is used in.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits applied: %d" % n[0])
