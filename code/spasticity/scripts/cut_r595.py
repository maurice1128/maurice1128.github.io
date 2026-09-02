# -*- coding: utf-8 -*-
"""r595: 3.5 and the Background to length. Three duplicated pointers to S1 collapse into one."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r133_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()


def swap(start, stop, new, label):
    global s
    i, j = s.index(start), s.index(stop)
    old = s[i:j]
    s = s[:i] + new + s[j:]
    print("%-14s %4d -> %4d" % (label, len(old.split()), len(new.split())))


i, j = s.index("| at 3\u00b0 of per-frame jitter"), s.index("\n\n", s.index("| knee at contact | 0.766"))
table = s[i:j]

swap("### 3.5 Detection", "### 3.6 The measurement model", u"""### 3.5 Detection, discrimination and grading under measurement error

Three separable claims can be made for this variable: that it detects a lesion, that it distinguishes
the two, and that it grades either. We scored each on the noise-free simulation and again under the
measurement model of \u00a73.6, at 100 Hz with yaw \u2264 10\u00b0 and event error \u2264 1 frame, over 60 noise
realisations of the full primary dataset.

""" + table + u"""

Distinguishing the two lesions survives measurement error on every candidate, best on variables that
take a peak or average a window, though for opposite reasons: a window mean divides zero-mean jitter
by the root of its sample count, while a maximum amplifies it (\u00a73.6) and survives on the size of its
clean gap. Grading tone survives on the ankle and degrades sharply on the knee. Grading weakness
survives nowhere: the three variables that grade it on noise-free traces were put through the same
model separately and none clears the 0.8 criterion at 3\u00b0 of jitter, so under this study's own
measurement model that count falls from three to zero, and \u00a73.4's counts should be read as noise-free
throughout. The endpoint is not best in the two weakness columns, and in both the reason is \u00a73.4's
asymmetry rather than a property of the variable.

Two conventions govern the table and Supplement S1 sets out both with the noise model's own limits.
The correlations are signed, so a sign reversal counts against a variable and the small values in the
weakness column are no recovery rather than partial recovery. The two detection columns are
sensitivities and not accuracies, since no control run is classified in producing them: the endpoint's
1.000 for detecting hyperreflexia becomes 0.687 once the six control runs are classified as well.

A tone score follows from the same readings, and it is ordinal and not absolute. Taking *T* as the
control mean minus the patient's reading, a threshold at *T* = 4.02\u00b0 separates the two groups with
3.13\u00b0 to spare, 1.8 times the standard error of a single measurement in patients. Under noise the five
*T* values move down by up to 1.505\u00b0, which exceeds three of the four gaps between adjacent levels,
because taking a maximum biases the reading upward and the flatter hyperreflexia peak is biased more;
the group difference compresses from 8.731 to 7.431\u00b0, 85 per cent of its clean value. The ordering
itself is unaffected, which is why the rank correlation of \u03c1 = \u22120.902 survives, but *T* ranks severity
without placing a patient on the series, and a recording with 3\u00b0 of jitter would place one up to three
levels low. Supplements S1 and S3 give the five *T* values, the two published measurement errors and
the rectification measurement.

The grading is bounded twice over, and the two bounds are independent. Only one of the four adjacent
gaps exceeds one between-session measurement error, while the series' full span of 4.14\u00b0 is 2.3 errors
wide; and the rectification drift is of the same size as the gaps it would have to resolve. Errors of
this size are "generally not small enough to be ignored during clinical data interpretation" [24]. The
variable supports a coarse contrast, substantial calf overactivity against little, and not a
continuous or absolute tone scale. These figures carry no between-patient variance and are not
clinical accuracies; what the effect is worth against the spread a patient population presents is set
out in \u00a74.1.

""", "3.5")

io.open(P, "w", encoding="utf-8", newline="").write(s)
b = s[s.index("## 1. Background"):s.index("## Figures")]
print("body %d" % len(b.split()))
