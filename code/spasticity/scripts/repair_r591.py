# -*- coding: utf-8 -*-
"""r591: repair what this session's automated passes broke, and re-home four dropped values.

A blind reader found five mechanical defects, each traceable to one of today's passes: a clause
duplicated inside one sentence when the chaining gloss was expanded; a sentence beginning lowercase
after the gate-to-criterion rename; a paragraph opening on "No candidate mechanism" whose antecedent
was deleted with the hip analysis; an ordinal counting to a third question where no first or second
question survives; and a "By contrast" marking a contrast between a sentence and its own restatement.
He also noted that twenty-two lines break the file's 100-column wrap and that each carries an
inserted caveat, which draws this session's revision history onto the page.

The four values dropped by the r590 compression move to Supplement S4, which already holds the
control workings.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r126_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r127_SUPPLEMENT"))
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


# 1 -- clause duplicated when the chaining gloss was expanded over the original
rep(u"""Severe conditions were reached by warm-start chaining, in which each severity level is seeded from
the previous level's optimum, each level seeded from the previous level's optimum, following Ong et
al. [10].""",
u"""We reached severe conditions by warm-start chaining, seeding each severity level from the previous
level's optimum, following Ong et al. [10].""")

# 2 -- sentence left lowercase by the gate-to-criterion rename
rep(u"""A run is one lesioned simulation under one optimisation seed. criterion G requires""",
    u"""A run is one lesioned simulation under one optimisation seed. Criterion G requires""")

# 3 and 4 -- a paragraph opening on a deleted antecedent, and an ordinal counting deleted items
rep(u"""No candidate mechanism produced an effect exceeding the protocol artefact. A left-minus-right hip
asymmetry was examined and is not reported, for the reasons given in Supplement S11.""",
u"""We searched for a mechanism behind the redistribution and found none whose effect exceeds the
protocol artefact. One candidate, a left-minus-right hip asymmetry, is examined in Supplement S11 and
is not reported here.""")

rep(u"""A third question no control here can reach is whether the separation follows from lesion type or
from the lesion's effect on stability.""",
u"""No control here can reach a third question, whether the separation follows from lesion type or from
the lesion's effect on stability.""")

# 5 -- a connective marking a contrast between a sentence and its own restatement
rep(u"""returns exactly that for each of the thirty candidates whose groups are disjoint. By contrast, it
does not discriminate among them.""",
u"""returns exactly that for each of the thirty candidates whose groups are disjoint, so it does not
discriminate among them.""")

# -- the count the compression dropped
rep(u"""The count of seven does not depend on the selection,""",
    u"""The count of seven of 81 does not depend on the selection,""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("mechanical defects repaired: %d" % n[0])

# ---- the four control values move to S4
q = io.open(Q, encoding="utf-8").read()
anchor = u"**Unlesioned side.**"
add = (u"**The five duration slopes.** Fitted within condition, they are \u22120.006, \u22120.005, +0.128, "
       u"\u22120.433 and +0.112 \u00b0\u00b7s\u207b\u00b9. Their mean is \u22120.041 and the standard error of that mean is 0.102, "
       u"which carries \u00b10.743\u00b0 over the 7.28 s difference in end time between the groups at one standard "
       u"error, and \u00b12.06\u00b0 at 95 per cent on five conditions. Every one of the five comes from a "
       u"hyperreflexia condition, because the rule requires within-condition variation in end time and "
       u"no weakness condition has any.\n\n")
if anchor in q:
    q = q.replace(anchor, add + anchor, 1)
    print("five slopes and the SE placed in S4")
io.open(Q, "w", encoding="utf-8", newline="").write(q)


# ---- re-flow, so the wrap width stops recording the revision history
def wrap(p, w=100):
    out, line = [], ""
    for word in p.split():
        if line and len(line) + 1 + len(word) > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word) if line else word
    if line:
        out.append(line)
    return "\n".join(out)


SKIP = re.compile(r"^\s*(\||#|!|```|\s*$)")
for f in (P, Q):
    t = io.open(f, encoding="utf-8").read()
    tail = ""
    if "## References" in t:
        t, tail = t.split("## References", 1)
        tail = "## References" + tail
    out = []
    for para in t.split("\n\n"):
        first = para.split("\n")[0] if para else ""
        out.append(para if (SKIP.match(first) or "|" in first[:4] or not para.strip())
                   else wrap(para))
    io.open(f, "w", encoding="utf-8", newline="").write("\n\n".join(out) + tail)
    L = [len(x) for x in io.open(f, encoding="utf-8").read().split("\n")]
    over = sum(1 for x in L if x > 105)
    print("%-26s lines over 105 chars: %d" % (f.split("\\")[-1], over))
