# -*- coding: utf-8 -*-
"""r584: repair six inverted connectives, and turn 4.5 from a numbered list into prose.

Two faults, both introduced by this session's own automated passes.

The connective pass of r583 chose between However and Therefore by testing the following clause for a
negation. That is not what a contrast is. Six of the fourteen sites came out inverted, each one a
consequence written as a concession: "Only the published abstract was retrieved. However, we can
verify the coefficient" should be "so we can verify"; "None of the 23 runs reaches the horizon and
all 36 weakness runs do. However, no group comparison at matched survival exists here" should be
"Therefore, no group comparison...". Each of the fourteen was read in context and only the six wrong
ones are touched.

The limitations section is seven numbered items with bold headings. Jansen's equivalent section uses
plain noun-phrase subheadings over continuous prose, and Ong's uses none at all; neither uses a
numbered list. A supervisor reading this manuscript said the Results and Discussion read as
bullet-point summaries pasted in, and this section is where that is literally true. The seven items
become three subsections of prose. No content is removed.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r113_MANUSCRIPT"))
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


# ---- the six inverted connectives, each a consequence written as a concession
rep(u"do not imply one another at n = 12. However, we rest the null on the p values",
    u"do not imply one another at n = 12, so we rest the null on the p values")
rep(u"they do not grow with chain depth. However, the floor need not be multiplied by the depth",
    u"they do not grow with chain depth, so the floor need not be multiplied by the depth")
rep(u"The controller is re-optimised for every lesion. However, the joint at which a difference appears\ndoes not identify the muscle responsible",
    u"Because the controller is re-optimised for every lesion, the joint at which a difference appears\ndoes not identify the muscle responsible")
rep(u"all 36 weakness runs do. However, no group comparison at matched survival\nexists here",
    u"all 36 weakness runs do. Therefore, no group comparison at matched survival\nexists here")
rep(u"will still track weakness through its association with tone. However, a low swing\ndorsiflexion cannot be attributed to one component from the reading alone.",
    u"will still track weakness through its association with tone, so a low swing dorsiflexion cannot be\nattributed to one component from the reading alone.")
rep(u"median dorsiflexor manual muscle test is 1 of 5 [4]. However, the two series are matched neither in\nsurvival nor in severity.",
    u"median dorsiflexor manual muscle test is 1 of 5 [4], so the two series are matched neither in\nsurvival nor in severity.")

# ---- the numbered list becomes prose under plain subheadings
for old, new in (
    (u"**1. How these lesions are modelled is unsettled, and the asymmetry depends on that choice.** No",
     u"#### The model and its lesions\n\nNo"),
    (u"**4. Unlesioned model ankles depart from normal in this literature, and ours departs in early\nstance.** Predictive",
     u"Predictive"),
    (u"**2. Predictive simulations stop walking under severe impairment, and here that covaries with the\nlesion.** Losing",
     u"#### What the design cannot separate\n\nLosing"),
    (u"**3. The two lesions are imposed independently; in patients they co-occur.** Crossing",
     u"Crossing"),
    (u"**5. The endpoint was chosen after the data were seen, from a scan of 81 candidates.** No correction",
     u"#### The status of the result\n\nThe endpoint was chosen after the data were seen, from a scan of "
     u"81 candidates. No correction"),
    (u"**6. The method is not new.** A reflex-controlled model", u"A reflex-controlled model"),
    (u"**7. No patient data.** Every figure bearing on a clinic", u"Every figure bearing on a clinic"),
):
    rep(old, new)

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits: %d" % n[0])
