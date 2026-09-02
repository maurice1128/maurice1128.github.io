# -*- coding: utf-8 -*-
"""r562: move the corpus and protocol mechanics of 2.3 and 2.4 into a new Supplement S10."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r76_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r77_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
moved = []


def take(first_words):
    """Cut the paragraph that begins with these words and return it."""
    global s
    paras = s.split("\n\n")
    key = " ".join(first_words.split())
    for i, p in enumerate(paras):
        if " ".join(p.split()).startswith(key):
            out = paras.pop(i)
            s = "\n\n".join(paras)
            moved.append(len(out.split()))
            return out
    print("  NOT FOUND: %s" % first_words[:50])
    return ""


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:56]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]


grid = take(u"**The mixed grid** is a separate corpus")
extra = take(u"Five further lesion families exist in the archive")
rules = take(u"1. Noise floor. Differences are divided by")

# replacements for what was cut
rep(u"""Twenty-three hyperreflexia cells, 36 weakness cells and 6 control cells pass, from five
hyperreflexia families, six weakness families and one control lineage.""",
u"""Twenty-three hyperreflexia cells, 36 weakness cells and 6 control cells pass, from five
hyperreflexia families, six weakness families and one control lineage. Five further lesion families
in the archive, carrying plantarflexor-weakness and bifunctional lesions rather than further
hyperreflexia rungs, are admitted at 0 to 5 cells of 6 and are used only as the duration control of
\u00a73.3. A separate 84-cell mixed grid, 74 of them admitted, crosses four tibialis anterior scalings
with four delivered reflex gains and supports \u00a73.4 and \u00a73.7; it is not part of the 65-cell census.
Supplement S10 gives both corpora in full.""")

rep(u"""The unit of analysis is the lesion family, not the cell: cells within a family share an
optimisation lineage and are not independent, giving an effective n of 11, not 59.""",
u"""The unit of analysis is the lesion family, not the cell: cells within a family share an
optimisation lineage and are not independent, giving an effective n of 11, not 59. Four decision
rules were fixed before the results were read, covering the noise floor a difference is divided by,
the treatment of the survival confound, the leakage permitted onto the unlesioned side, and what
counts as a failed control. They are stated in full in Supplement S10 and each is referred to by name
where it is applied.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

sup = io.open(Q, encoding="utf-8").read().rstrip() + u"""

## S10. The two corpora, and the four decision rules in full

**Lesion families outside the primary census.**

""" + extra + u"""

**The mixed grid.**

""" + grid + u"""

**The four decision rules of \u00a72.4.** These were fixed before the results were read. Each is named in
the text where it is applied, and \u00a73.3 reports the verdict of each.

""" + rules + u"""
"""
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("moved %d paragraphs, %d words" % (len(moved), sum(moved)))
