# -*- coding: utf-8 -*-
"""r576: flatten the essay apparatus. Headings name their contents; connectives return.

A blind cold read against Jansen, Ong and Mendes-Andrade identified four devices that no comparator
uses: headings built as an antithesis and reused seven times, a figurative title, a closing epigram
delivered at near-constant rate, and zero-exception avoidance of ordinary connectives and hedges
across 12,000 words. The last of those is an over-application of a house rule: the instruction was to
avoid "moreover", "furthermore" and "in addition", and it was extended to a general ban that produced
prose no person writes. Comparator counts in the same sections: Jansen uses "Furthermore" eight times
and "suggest" fourteen; Ong uses "likely" twelve times.

Headings here become noun labels naming their contents, as in all three comparators. The title becomes
a method statement. A small number of ordinary connectives and hedges are restored where the sentence
was already doing that work implicitly. No number, citation or claim changes.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r95_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:58]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


# --- the title: a method statement, as the comparators write them
rep(u"# Graded calf hyperreflexia is written on the sagittal ankle several times more strongly than graded dorsiflexor weakness: an 81-readout search in a ground-truth gait simulation",
    u"# Distinguishing graded plantarflexor hyperreflexia from graded dorsiflexor weakness in simulated post-stroke gait: a search over 81 sagittal kinematic readouts")

# --- headings name their contents
for old, new in (
    (u"### 1.2 What has been measured", u"### 1.2 Previous measurements"),
    (u"### 2.4 Analysis, and four decision rules fixed before the results were read",
     u"### 2.4 Analysis and decision rules"),
    (u"### 3.1 Choosing the readout", u"### 3.1 The candidate scan"),
    (u"### 3.4 What tone writes, and what weakness writes",
     u"### 3.4 Displacement and grading across the scan"),
    (u"### 3.5 Detecting, distinguishing, grading, and what motion capture leaves of each",
     u"### 3.5 Detection, discrimination and grading under measurement error"),
    (u"### 3.6 The measurement model, and the modality it requires",
     u"### 3.6 The measurement model and the recording modality"),
    (u"### 3.8 What the separation localises, and what it does not",
     u"### 3.8 Localisation of the separation"),
    (u"### 4.1 What the result says", u"### 4.1 Interpretation"),
    (u"### 4.2 Why this question needs a simulation", u"### 4.2 The case for a simulation"),
    (u"### 4.3 What the reading means, and what it does not", u"### 4.3 Scope of the reading"),
    (u"### 4.4 What this offers, and the study it defines", u"### 4.4 A patient study"),
):
    rep(old, new)

# --- the abstract epigram
rep(u"It calibrates a group; it does not test an individual.",
    u"The figures calibrate a group and do not constitute a test for an individual patient.")

# --- a stale cross-reference: 1.77 is introduced in 3.5, not 3.4
rep(u"so the error that governs interpreting a patient's reading is the 1.77\u00b0 of \u00a73.4 and not anything in",
    u"so the error that governs interpreting a patient's reading is the 1.77\u00b0 of \u00a73.5 and not anything in")

# --- restore ordinary connectives and hedges where the sentence already implied them
rep(u"""The failure has a mechanism behind it.""",
    u"""The failure appears to have a mechanism behind it.""")
rep(u"""Grading tone survives on the ankle and degrades sharply on the knee. Grading weakness survives
nowhere.""",
u"""Grading tone survives on the ankle, although it degrades sharply on the knee. Grading weakness
survives nowhere among the candidates tested.""")
rep(u"""That ratio is particular to this readout. The asymmetry is not.""",
    u"""That ratio is particular to this readout, although the asymmetry itself is not.""")
rep(u"""The direction and the order of magnitude generalise. The factor of 21 does not.""",
    u"""The direction and the order of magnitude generalise, however, whereas the factor of 21 does not.""")
rep(u"""A sign reversal is a way of saying which lesion dominates. A large dynamic range is another, and
on this corpus the second works better than the first.""",
u"""A sign reversal is one way of saying which lesion dominates and a large dynamic range is another,
and on this corpus the second works better.""")
rep(u"""The difference is resolution, not excursion.""",
    u"""The difference is one of resolution rather than of excursion.""")
rep(u"""The instant matters more than the joint.""",
    u"""The instant appears to matter more than the joint.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits: %d" % n[0])
