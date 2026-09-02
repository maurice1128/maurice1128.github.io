# -*- coding: utf-8 -*-
"""r570: act on structcheck_r569, and correct the two places where it over-reports."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
C = r"C:\Users\maurice\Desktop\spasticity_paper\scone\structcheck_r569.py"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r87_MANUSCRIPT"))
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


# 1 -- 8.57 is load-bearing for d = 0.59 and appears once, in the Discussion. State it in Results.
rep(u"""That figure, 5.55\u00b0, is computed here from the two
subgroup means and SDs, assuming the two subgroups are of equal size, and is not reported in [5].""",
u"""That figure, 5.55\u00b0, is computed here from the two
subgroup means and SDs, assuming the two subgroups are of equal size, and is not reported in [5]. The
same construction applied to knee angle at contact in the same cohort gives 8.57\u00b0, and \u00a74.1 sets the
two against each other.""")

# 2 -- the amplitude ratio in 4.1 is the reciprocal of 3.4's, stated in a second form
rep(u"""and at 0.37 to 0.55 of the amplitude where
it is legible at all.""",
u"""and where it is legible at all it moves the reading
2.2, 2.7 and 1.8 times less far than tone does at the same phase (\u00a73.4).""")

# 3 -- the 0.23 speed propagation is derived here and belongs with the speed control
rep(u"""so the arm difference in walking speed contributes 0.032\u00b0 to the endpoint,""",
u"""so the arm difference in walking speed contributes 0.032\u00b0 to the endpoint. Propagated instead across
the 0.2 to 1.2 m\u00b7s\u207b\u00b9 range a stroke cohort presents, the same slope carries about 0.23\u00b0 over a
0.4 m\u00b7s\u207b\u00b9 difference, which \u00a74.5 sets against the direct weakness effect. Within this corpus,""")

# 4 -- the S8 pointer promises words S8 does not use
rep(u"""Supplement S8 gives the nine
readings and the derivation of each bar.""",
u"""Supplement S8 gives the nine counts, the three bars and the three rank conventions behind them.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("manuscript edits: %d" % n[0])

# ---- the checker over-reported in two ways
c = io.open(C, encoding="utf-8").read()
c = c.replace('        near = v[max(0, m2.start() - 190):m2.end() + 90]',
              '        # a literature value is one whose own sentence, or the sentence before it,\n'
              '        # carries a citation bracket. A fixed character window is too narrow.\n'
              '        lo = max(0, v.rfind(".", 0, max(0, m2.start() - 240)))\n'
              '        near = v[lo:v.find(".", m2.end()) + 1 if v.find(".", m2.end()) > 0 else len(v)]')
c = c.replace('        if re.search(r"\\bet\\s+al$|\\b[A-Z]$|\\bvs$|\\bcf$|\\bFig$|\\bref$", pre, re.I):',
              '        if re.search(r"et\\s+al\\s*$|\\bvs\\s*$|\\bcf\\s*$|\\bFig\\s*$|\\bref\\s*$|'
              '(?<![a-z])[A-Za-z]\\s*$", pre):')
io.open(C, "w", encoding="utf-8", newline="").write(c)
print("checker: citation window widened to the sentence, 'et al.' guard fixed")
