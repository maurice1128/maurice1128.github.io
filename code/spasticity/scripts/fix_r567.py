# -*- coding: utf-8 -*-
"""r567: closing repairs from the round-five cold read."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r82_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r83_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn, txt=None):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:56]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


# 1 -- the two-stage estimator belongs in Results, and its fold must be named
rep(u"""Of the one two-stage estimator tested, grading gain from the ankle recovers it at R\u00b2 = 0.95 and
reading weakness off the knee residual afterwards recovers R\u00b2 = 0.13; the sign-appropriate variant,
applying a different weakness relation on each side of the reversal, remains open.""",
u"""Of the one two-stage estimator tested (\u00a73.4), grading gain from the ankle recovers it well and
reading weakness off the knee residual afterwards does not; the sign-appropriate variant, applying a
different weakness relation on each side of the reversal, remains open.""")

rep(u"""We ran that regression on four feature sets and not on all 81.""",
u"""We ran that regression on four feature sets and not on all 81. One two-stage estimator was also
tested on the same grid: grading delivered gain from peak swing dorsiflexion recovers it at R\u00b2 =
0.946 under leave-one-cell-out, and regressing the knee-at-contact residual on weakness afterwards
recovers R\u00b2 = 0.129. The first figure is not comparable to the 0.640 to 0.821 above, which are
leave-one-gain-level-out and therefore a harder fold. What remains untested is the sign-appropriate
variant, which would apply a different weakness relation on each side of the reversal.""")

# 2 -- one source, three conditions, quoted as if one quantity
rep(u"""6.3\u00b0 post-stroke [22]""",
    u"""6.3 to 7.4\u00b0 post-stroke depending on limb and camera view [22]""")
rep(u"""reported ankle errors for video-based pose estimation are 6.8 to 7.4\u00b0""",
    u"""reported ankle errors for video-based pose estimation are 6.3 to 7.4\u00b0 depending on limb and
camera view""")

# 3 -- the abstract claims a class where four models were tested, on the wrong range
rep(u"""Over the \u00d70.80 to \u00d70.95 dorsiflexor range tested, no estimator blind to the tone recovers
weakness, because the weakness signal reverses direction between the two lowest reflex gains.""",
u"""On the mixed grid, which crosses dorsiflexor scalings of \u00d70.60 to \u00d71.00 with four reflex gains, no
readout or combination we tested recovers weakness without first knowing the tone, because the
weakness signal reverses direction between the two lowest gains.""")

# 4 -- 4.4 states unconditionally what 3.4 and 3.5 state conditionally
rep(u"""no sagittal joint angle, alone or in combination, reports dorsiflexor weakness over the range
examined.""",
u"""no sagittal joint angle, alone or in combination, reports dorsiflexor weakness over the range
examined once measurement error is applied. Three do on noise-free traces, seven if the ordering is
scored at the family level, and none survives 3\u00b0 of simulated jitter (\u00a7\u00a73.4, 3.5).""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

# 5 -- S9's 111.3 shares a denominator with 76.5 and differs in numerator; say so
sup = io.open(Q, encoding="utf-8").read()
sup = sup.replace(
 u"The observed maximum is 111.3 seed SD, at peak ankle dorsiflexion in swing.",
 u"The observed maximum is 111.3 seed SD, at peak ankle dorsiflexion in swing. That figure and "
 u"\u00a73.1's 76.5 share a denominator, the 0.0819\u00b0 within-lineage seed SD, and differ in the numerator: "
 u"76.5 divides the cell-level gap of 6.265\u00b0, which is the distance between the nearest cells of the "
 u"two arms, and 111.3 divides the family-level mean difference of 9.117\u00b0. The permutation uses the "
 u"family-level statistic because the unit of analysis is the family.")
sup = sup.replace(u"up to 6.8\u00b0 post-stroke [22]",
                  u"6.3 to 7.4\u00b0 post-stroke depending on limb and camera view [22]")
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("manuscript edits: %d" % n[0])
