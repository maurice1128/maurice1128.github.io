# -*- coding: utf-8 -*-
"""r558: move the measurement-error apparatus of 3.5 into Supplement S1."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r69_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r70_SUPPLEMENT"))
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


# 1 -- the two table conventions
rep(u"""The table follows two conventions. The detection columns score each cell against a threshold built
from the control cells and from the other cells of its own arm, never from itself. An earlier
version of this analysis fitted that threshold on the cells it then classified, which returns 1.000
by construction for any separated arm and inflated the weakness column by 0.19 to 0.27. And the
correlations are signed, so a reversal counts against a readout and not for it: which is why the
weakness column changes sign between the reported endpoint and the others, and why the small
positive and negative values there should be read as no recovery and cannot be read as partial
recovery.""",
u"""Two conventions govern the table and both are permissive in ways a reader should know: no cell
contributes to the threshold that classifies it, and the correlations are signed, so a sign reversal
counts against a readout rather than for it. The small values in the weakness column are therefore no
recovery and not partial recovery. Supplement S1 gives both conventions and the error an earlier
version of this analysis made in the first of them.""")

# 2 -- the two published errors and their caveats
rep(u"""1.8 times the standard error of a single measurement in patients. Ref [15] publishes two errors for this variable, both from treadmill walking and both inverted here through that paper's own definition MDC = SEM \u00d7 1.96 \u00d7 \u221a2: a between-session error of 1.77\u00b0, from sessions twenty days apart and so including marker replacement and day-to-day variation, and a within-session error of 0.32\u00b0, across strides of one recording. Its authors state that neither may be used to interpret overground studies. The 0.66\u00b0 weakness ladder of \u00a73.4 is about twice the within-session error and about a third of the between-session one, so it could in principle be resolved between two conditions recorded in one session, and cannot be resolved by comparing a patient's recording against a normative reference collected separately, which is the comparison a clinic makes. Under noise those""",
u"""1.8 times the standard error of a single measurement in patients, which for this
variable is 1.77\u00b0 between sessions and 0.32\u00b0 within one. The \u00a73.4 weakness ladder of 0.66\u00b0 sits
between the two: resolvable in principle between two conditions recorded in one session, and not
resolvable against a normative reference collected separately, which is the comparison a clinic
makes. Supplement S1 derives both figures and states what their sources permit. Under noise those""")

# 3 -- the caveat paragraph
rep(u"""Both measurement errors carry the same caveat, and it is not a small one. The value for peak swing
dorsiflexion is derived from a treadmill study whose authors state that their figures "may not be
used to interpret studies that measure overground gait" [15]. The value for knee angle at contact
comes from a study that defines its standard error of measurement from the change-score SD, which
already contains a factor of \u221a2, so the figure used here is that paper's own SD_diff divided by \u221a2
rather than its published 1.55\u00b0 [13]. The correction runs against this study rather than for it.
More generally, a systematic review of three-dimensional kinematic reliability concludes that errors
of this size, while "probably acceptable", are "generally not small enough to be ignored during
clinical data interpretation" [24].""",
u"""Both measurement errors carry a caveat that is not small: one is a treadmill figure its authors
forbid applying to overground gait [15], and the other required a correction that runs against this
study rather than for it [13]. Errors of this size are "generally not small enough to be ignored
during clinical data interpretation" [24]. Supplement S1 sets out both derivations.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

sup = io.open(Q, encoding="utf-8").read()
i = sup.index(u"## S2.")
ins = u"""**The two conventions of the \u00a73.5 table.** The detection columns score each cell against a threshold
built from the control cells and from the other cells of its own arm, never from itself. An earlier
version of this analysis fitted that threshold on the cells it then classified, which returns 1.000
by construction for any separated arm and inflated the weakness column by 0.19 to 0.27. The
correlations are signed, so a reversal counts against a readout and not for it, which is why the
weakness column changes sign between the reported endpoint and the others. Those two detection
columns are sensitivities and carry no false-positive rate, because no control cell is classified in
producing them; the balanced figure that does classify the six controls is 0.687 for the endpoint at
3\u00b0.

**The two published measurement errors, and what their sources permit.** Ref [15] publishes two
errors for peak swing dorsiflexion, both from treadmill walking and both inverted here through that
paper's own definition MDC = SEM \u00d7 1.96 \u00d7 \u221a2: a between-session error of 1.77\u00b0, from sessions twenty
days apart and so including marker replacement and day-to-day variation, and a within-session error
of 0.32\u00b0, across strides of one recording. Its authors state that neither may be used to interpret
overground studies. That same table publishes between-session errors for three further sagittal
variables that are members of the 81 scanned in \u00a73.4, namely ankle angle at contact at 2.53\u00b0, peak
knee flexion in swing at 2.06\u00b0 and hip angle at toe-off at 4.15\u00b0; \u00a73.4 reports how the counts move
when each variable is given its own error rather than the smallest of the four. The value used for
knee angle at contact comes from a study that defines its standard error of measurement from the
change-score SD, which already contains a factor of \u221a2, so the figure used here is that paper's own
SD_diff divided by \u221a2, 2.62\u00b0, rather than its published 1.55\u00b0 [13]. That correction runs against this
study rather than for it. A systematic review of three-dimensional kinematic reliability concludes
that errors of this size, while "probably acceptable", are "generally not small enough to be ignored
during clinical data interpretation" [24].

"""
sup = sup[:i] + ins + sup[i:]
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("edits applied: %d" % n[0])
