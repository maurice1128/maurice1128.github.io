# -*- coding: utf-8 -*-
"""r589: 3.5 to its verdicts. The derivations go to the supplement, the patient transfer to 4.1.

Section 3.5 ran to 1,438 words and carried three things that are not results of the simulation: the
holding-out conventions behind its table, the derivation of the tone score and its noise behaviour,
and the transfer of the effect onto a patient cohort using between-patient SDs from ref [5]. The
third of those is derived a second time in 4.1, so the same five numbers are produced twice in one
paper. It moves to 4.1 and is deleted here; the first two move to Supplement S1 and S3, which already
hold the material they belong with.

Nothing is lost. Every number kept its container, and the self-check and the binding check would fail
on any that went missing.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r123_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r124_SUPPLEMENT"))
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


# --- opening: the scoring conventions go to S1
rep(u"""A clinician would make three claims of this variable, and they are separable and not equally
supportable. We scored each on the noise-free simulation and again under the measurement model of
\u00a73.6 (per-frame Gaussian jitter, frame-rate resampling, out-of-plane yaw and event-frame error) at
100 Hz, yaw \u2264 10\u00b0, event error \u2264 1 frame, over 60 noise realisations per condition. Every column of
the table below is computed on the full primary dataset: all 23 hyperreflexia, 36 weakness and 6
control runs, from eleven chains plus control, and not on the ten-cell subset of \u00a73.6. The two
detection columns are leave-one-run-out and the group column is leave-one-condition-out. No cell is
scored by a threshold it helped set, but in the detection columns the other cells of its own chain
do enter that threshold, so those two columns are held out at cell level and not at chain level;
since cells within a chain are not independent (\u00a72.4), they are the more permissive of the two
schemes.""",
u"""Three separable claims can be made for this variable: that it detects a lesion, that it distinguishes
the two, and that it grades either. We scored each on the noise-free simulation and again under the
measurement model of \u00a73.6, at 100 Hz with yaw \u2264 10\u00b0 and event error \u2264 1 frame, over 60 noise
realisations of the full primary dataset. Supplement S1 gives the holding-out scheme for each column
and the two respects in which it is permissive.""")

# --- the table conventions paragraph, now in S1
rep(u"""The table is permissive in two ways. No cell contributes to the threshold that
classifies it, and the correlations are signed, so a sign reversal counts against a variable rather
than for it. The two detection columns are also sensitivities rather than accuracies, since no
control cell is classified in producing them; the endpoint's 1.000 for detecting hyperreflexia
becomes 0.687 at 3\u00b0 of jitter once the six control cells are classified as well.""",
u"""The correlations are signed, so a sign reversal counts against a variable. The two detection columns
are sensitivities and not accuracies, since no control run is classified in producing them: the
endpoint's 1.000 for detecting hyperreflexia becomes 0.687 once the six control runs are classified
as well.""")

# --- the tone score: keep the verdict, move the derivation
rep(u"""A tone score follows, but it is ordinal and not absolute. Taking *T* as the control mean minus the
patient's reading, the five hyperreflexia doses give *T* = 7.245 \u00b1 0.064, 8.331 \u00b1 0.079, 10.200 \u00b1
0.101, 10.578 \u00b1 0.293 and 11.381 \u00b1 0.146\u00b0 on noise-free traces, and the weakness group gives *T*
below 0.886\u00b0. A threshold at *T* = 4.02\u00b0 separates the two groups with 3.13\u00b0 to spare on the nearer
side, 1.8 times the standard error of a single measurement in patients, which for this variable is
1.77\u00b0 between sessions and 0.32\u00b0 within one. The \u00a73.4 weakness series of 0.66\u00b0 sits between the two:
resolvable in principle between two conditions recorded in one session, and not resolvable against a
normative reference collected separately, which is the comparison a clinic makes. Supplement S1
derives both figures and states what their sources permit. Under noise those values move, although
they do not move together. Taking a maximum biases the estimate upward under noise, and because the
hyperreflexia peak is flatter than the control's, more samples fall near that maximum and the upward
bias is larger. At 3\u00b0 of per-frame jitter the reading is biased upward by 5.260\u00b0 in the
hyperreflexia group against 3.960\u00b0 in the weakness group, which is the pair that sets the group
difference, compressing it from 8.731 to 7.431\u00b0 (the control group's bias, 3.897\u00b0, is close to the
weakness group's and is what Fig. 5 plots), or 85 per cent of its clean value, and moving the five
*T* values down by up to 1.505\u00b0. That drift exceeds three of the four gaps between adjacent levels
(1.086, 1.869, 0.378 and 0.803\u00b0). The measurement is set out in Supplement S3.""",
u"""A tone score follows from the same readings, and it is ordinal and not absolute. Taking *T* as the
control mean minus the patient's reading, a threshold at *T* = 4.02\u00b0 separates the two groups with
3.13\u00b0 to spare, which is 1.8 times the standard error of a single measurement in patients. Under
noise the five *T* values move down by up to 1.505\u00b0, which exceeds three of the four gaps between
adjacent levels, because taking a maximum biases the reading upward and the flatter hyperreflexia
peak is biased more; the group difference compresses from 8.731 to 7.431\u00b0, 85 per cent of its clean
value. Supplements S1 and S3 give the five *T* values, the two published measurement errors and the
rectification measurement in full.""")

# --- the patient transfer moves wholesale to 4.1
i = s.index(u"These figures contain no between-patient variance")
j = s.index(u"Both measurement errors carry a caveat that is not small")
moved = s[i:j]
s = s[:i] + u"""These figures carry no between-patient variance and are not clinical accuracies; they describe how
well the pipeline resolves runs of a simulation under added noise. What the effect is worth against
the spread a patient population presents is set out in \u00a74.1.

""" + s[j:]
n[0] += 1

rep(u"""Both measurement errors carry a caveat that is not small: one is a treadmill figure its authors
forbid applying to overground gait [15], and the other required a correction that runs against this
study rather than for it [13]. Errors of this size are "generally not small enough to be ignored
during clinical data interpretation" [24]. Supplement S1 sets out both derivations.""",
u"""Errors of this size are "generally not small enough to be ignored during clinical data
interpretation" [24], and both carry caveats that Supplement S1 sets out with their derivations.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\_moved_transfer.txt",
        "w", encoding="utf-8", newline="").write(moved)
b = s[s.index("## 1. Background"):s.index("## Figures")]
sec = s[s.index("### 3.5"):s.index("### 3.6")]
print("edits: %d;  3.5 now %d words;  body %d" % (n[0], len(sec.split()), len(b.split())))
print("the moved block is parked in paper/_moved_transfer.txt (%d words) for insertion into 4.1"
      % len(moved.split()))
