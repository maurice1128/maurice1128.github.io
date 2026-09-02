# -*- coding: utf-8 -*-
"""r568: rendering and consistency defects from the round-five cold read."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r84_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r85_SUPPLEMENT"))
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


# 1 -- the unclosed bold: an opener at 2.1 and an orphan closer in 3.5
rep(u"joint-limit penalties on ankle and knee (0.1 each). **No term rewards toe clearance",
    u"joint-limit penalties on ankle and knee (0.1 each). No term rewards toe clearance")
rep(u"but the absolute score is not calibratable without knowing the noise.** *T* separates",
    u"but the absolute score is not calibratable without knowing the noise. *T* separates")

# 2 -- 2.4 named four rules that are not the four in S10
rep(u"""Four decision
rules were fixed before the results were read, covering the noise floor a difference is divided by,
the treatment of the survival confound, the leakage permitted onto the unlesioned side, and what
counts as a failed control. They are stated in full in Supplement S10 and each is referred to by name
where it is applied.""",
u"""Four decision rules were fixed before the results were read: the noise floor a difference is
divided by, the propagation of the survival confound and the fraction of the effect above which it is
declared confounding, the per-cycle stationarity a window mean must report, and the centring of every
displacement on the unlesioned control lineage rather than between arms. Supplement S10 states each
in full.""")

# 3 -- sign of the noise-model rank correlation
rep(u"which is why the rank correlation of \u03c1 = 0.902 survives",
    u"which is why the rank correlation of \u03c1 = \u22120.902 survives")

# 4 -- figure 3 caption disagrees with 3.1's count
rep(u"(\u00a73.1; on sign alone the count is thirty-three rather than eight)",
    u"(\u00a73.1; on sign alone the count is thirty-three rather than seven)")

# 5 -- the balanced figure belongs beside the 1.000 a reader will take as an accuracy
rep(u"""Two conventions govern the table and both are permissive in ways a reader should know: no cell
contributes to the threshold that classifies it, and the correlations are signed, so a sign reversal
counts against a readout rather than for it.""",
u"""Two conventions govern the table and both are permissive. No cell contributes to the threshold that
classifies it, and the correlations are signed, so a sign reversal counts against a readout rather
than for it. The two detection columns are also sensitivities rather than accuracies, since no
control cell is classified in producing them: the endpoint's 1.000 for detecting hyperreflexia
becomes 0.687 at 3\u00b0 of jitter once the six control cells are classified too.""")

# 6 -- unfinished edits
rep(u"and so cannot corroborate it. the corresponding figure",
    u"and so cannot corroborate it. The corresponding figure")

io.open(P, "w", encoding="utf-8", newline="").write(s)

# ---- supplement
q = io.open(Q, encoding="utf-8").read()
m = [0]


def qrep(o, nn):
    global q
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(q))
    if len(ms) != 1:
        print("  SUP SKIP(%d): %s" % (len(ms), o[:56]))
        return
    q = q[:ms[0].start()] + nn + q[ms[0].end():]
    m[0] += 1


# S3: the compression follows from the weakness arm, which S3 never states
qrep(u"""per-frame jitter of 1, 2 and 3\u00b0 biases the reading upward by
1.008, 2.397 and 3.897\u00b0 in the control arm and by 1.477, 3.323 and 5.260\u00b0 in the hyperreflexia arm,
compressing the arm difference from 8.731 to 8.284, 7.840 and 7.431\u00b0""",
u"""per-frame jitter of 1, 2 and 3\u00b0 biases the reading upward by
1.008, 2.397 and 3.897\u00b0 in the control arm, by 1.030, 2.432 and 3.960\u00b0 in the weakness arm, and by
1.477, 3.323 and 5.260\u00b0 in the hyperreflexia arm. The arm difference is set by the second and third
of those, not by the control, and compresses from 8.731 to 8.284, 7.840 and 7.431\u00b0""")

# S8: the sweep is outside the range the next sentence claims to cover
qrep(u"""Across every combination the ratio lies between 3.7 and 14.0 and never
inverts.""",
u"""Across the nine combinations of the table the ratio lies between 3.7 and 14.0 and never inverts.
The sweep is not covered by that statement: above a bar of about 3\u00b0 the weakness count reaches zero
while the tone count is still 14, so the ratio there is unbounded rather than bounded by 14.""")

# S10: the numbered rules run on as one paragraph
qrep(u"""not a global one. 2. Duration control.""", u"""not a global one.\n\n2. Duration control.""")
qrep(u"""declared confounded. 3. Within-window""", u"""declared confounded.\n\n3. Within-window""")
qrep(u"""on the same channel. 4. Centring.""", u"""on the same channel.\n\n4. Centring.""")

# S10: an orphan reference to a census that is not in S10
qrep(u"""**The mixed grid** is a separate corpus and is not part of the 65-cell census above.""",
     u"""**The mixed grid** is a separate corpus and is not part of the 65-cell primary census
summarised in \u00a72.3.""")

io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("manuscript edits: %d;  supplement edits: %d" % (n[0], m[0]))
