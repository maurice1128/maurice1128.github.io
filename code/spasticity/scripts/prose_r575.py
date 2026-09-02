# -*- coding: utf-8 -*-
"""r575: open each paragraph on its finding rather than on the move that produced it.

The comparators open on the result: "With increased soleus feedback, ankle dorsiflexion decreased
during mid and terminal stance" (Jansen); "Our results showed that the model could walk without
significant adaptations unless both plantarflexors were moderately or severely weakened" (Ong).
This manuscript opens on the procedure: "We take those in order", "Three do", "The three claims
separate cleanly", "Two results do not survive as stated". The scaffolding announces, counts and
characterises the paper's own moves, and it stands where the evidence should. This removes it.

No number, citation or claim changes. Only the sentences that talk about the paper.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r94_MANUSCRIPT"))
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


# --- 3.3: the paragraph announces its own order
rep(u"""We take those in order, and only the second cannot be closed.""", u"")

# --- 3.3: disclosure ritual addressed to a hypothetical reader
rep(u"""That figure is circular, because pooling across arms recovers the arm difference the
regression is meant to test, and we do not use it. A reader should know it exists and why it is not
the number reported.""",
u"""That figure is circular, because pooling across arms recovers the arm difference the regression is
meant to test.""")

# --- 3.4: a two-word clincher standing where the finding should
rep(u"""Does any of the 81 grade weakness? Three do. Scoring inside the pure weakness arm, by whether a
readout orders the six tibialis anterior scalings at |\u03c1| \u2265 0.8 *and* spans more than one clinical
measurement error, three of the 81 qualify: the ankle at 75, 80 and 90 per cent of the cycle, at \u03c1 = +0.822,
+0.900 and \u22120.820 over spans of 2.870, 2.208 and 2.272\u00b0.""",
u"""Three of the 81 order the six tibialis anterior scalings at |\u03c1| \u2265 0.8 and span more than one clinical
measurement error: the ankle at 75, 80 and 90 per cent of the cycle, at \u03c1 = +0.822, +0.900 and
\u22120.820 over spans of 2.870, 2.208 and 2.272\u00b0.""")

# --- 3.4: announces a caution instead of stating it
rep(u"""One further caution belongs with any count over the 81. The candidates are three joint-angle curves
sampled every 5 per cent of the cycle plus eighteen landmarks, so adjacent samples of one curve are
strongly correlated and the denominator is not 81 independent opportunities.""",
u"""The denominator is not 81 independent opportunities. The candidates are three joint-angle curves
sampled every 5 per cent of the cycle plus eighteen landmarks, so adjacent samples of one curve are
strongly correlated.""")

# --- 3.5: announces the structure of what follows
rep(u"""The three claims separate cleanly. Distinguishing the two lesions survives measurement error on
every candidate, best on readouts that take a peak or average a window, though for opposite reasons:""",
u"""Distinguishing the two lesions survives measurement error on every candidate, best on readouts that
take a peak or average a window, though for opposite reasons:""")

# --- 3.5: announces a convention rather than applying it
rep(u"""Two conventions govern the table and both are permissive. No cell contributes to the threshold that
classifies it, and the correlations are signed, so a sign reversal counts against a readout rather
than for it.""",
u"""The table is permissive in two ways. No cell contributes to the threshold that classifies it, and
the correlations are signed, so a sign reversal counts against a readout rather than for it.""")

# --- 3.6: announces that something is important
rep(u"""One consequence does not belong in a supplement. Published sagittal errors for markerless video""",
u"""Published sagittal errors for markerless video""")

# --- 3.8: announces a count of what follows
rep(u"""Two results do not survive as stated. The ankle-at-contact null fails two of the four decision rules
and is not certified by this design.""",
u"""The ankle-at-contact null fails two of the four decision rules and is not certified by this design.""")

# --- 4.5: announces two lines of evidence before giving them
rep(u"""Two lines of evidence bound the confound without closing it. The
within-dose duration regression gives 3 \u00b1 9 per cent of the arm effect, and is an extrapolation
rather than a bound because no weakness family contributes to its slope.""",
u"""The within-dose duration regression gives 3 \u00b1 9 per cent of the arm effect, and is an extrapolation
rather than a bound because no weakness family contributes to its slope.""")

# --- 5: announces a count of conditions
rep(u"""Four conditions define where the result holds. Both lesion magnitudes are known here and in no
patient.""",
u"""Both lesion magnitudes are known here and in no patient.""")

# --- 4.3: announces a qualification
rep(u"""One qualification belongs with [26].""", u"")

s = re.sub(r"\n{3,}", "\n\n", s)
s = re.sub(r"[ \t]+\n", "\n", s)
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("scaffolding sentences removed or folded: %d" % n[0])
