# -*- coding: utf-8 -*-
"""r598: put back what the compression took, and correct three statements that misreport their own record.

A science audit of the compressed manuscript found the arithmetic sound and the pointing broken. The
three most damaging removals are restored here, along with a Declarations paragraph that misreports
the deposited binding check, a supplement paragraph that labels a one-standard-error interval as a 95
per cent one, and a side control stated one gain level more favourably than its own container.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r139_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r140_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
q = io.open(Q, encoding="utf-8").read()
n = [0, 0]


def _r(txt, o, nn, which):
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(txt))
    if len(ms) != 1:
        print("  SKIP(%d) %s: %s" % (len(ms), which, o[:52]))
        return txt
    n[0 if which == "MS" else 1] += 1
    return txt[:ms[0].start()] + nn + txt[ms[0].end():]


def rep(o, nn):
    global s
    s = _r(s, o, nn, "MS")


def qrep(o, nn):
    global q
    q = _r(q, o, nn, "SUP")


# ---- 1. the measurement error the whole clinical spine rests on
rep(u"""A tone score follows from the same readings, and it is ordinal and not absolute. Taking *T* as the
control mean minus the patient's reading, a threshold at *T* = 4.02\u00b0 separates the two groups with
3.13\u00b0 to spare, 1.8 times the standard error of a single measurement in patients.""",
u"""A tone score follows from the same readings, and it is ordinal and not absolute. The single
measurement error this study uses throughout is 1.77\u00b0, the between-session standard error for peak
ankle angle in swing published for a post-stroke cohort by Kesar et al. and inverted here through
that paper's own definition of minimal detectable change [15]; its authors state that their figures
may not be used to interpret overground gait, and Supplement S1 gives the derivation and the
within-session figure of 0.32\u00b0. Taking *T* as the control mean minus the patient's reading, a
threshold at *T* = 4.02\u00b0 separates the two groups with 3.13\u00b0 to spare, 1.8 times that error.""")

rep(u"""Only one of the four adjacent
gaps exceeds one between-session measurement error, while the series' full span of 4.14\u00b0 is 2.3 errors
wide;""",
u"""Only one of the four adjacent gaps exceeds the 1.77\u00b0
between-session error, while the series' full span of 4.14\u00b0 is 2.3 errors wide;""")

# ---- 2. the patient result that bounds the paper's principal negative
rep(u"""Outside them it is contradicted by [28] and untested.""",
u"""Outside them it is untested, and inside them it is contested: Chisholm et al. report, in 55
independently ambulating sub-acute stroke survivors, that peak dorsiflexion during swing was related
to isometric dorsiflexor force at r = \u22120.32, p = 0.039 [28], which is an association in patients at
this study's own endpoint of a size this model calls faint. Only the published abstract of [28] could
be retrieved, so we cannot check whether that cohort's dorsiflexor forces overlap the range tested
here; Supplement S12 sets out what follows on either reading.""")

# ---- 3. the ratio bound the supplement contradicts
rep(u"""and their ratio from 3.7 to 14.0 without ever inverting (Supplement S8)""",
u"""and their ratio from 3.7 to 14.0 without ever inverting. That upper bound is a property of the nine
readings and not of every threshold: sweeping a single common threshold instead, the weakness count
reaches zero above about 3\u00b0 while the tone count is still 14, so the ratio there is unbounded rather
than bounded by 14 (Supplement S8)""")
rep(u"""a ratio that stays between 3.7 and 14 and never inverts, and under this study's own noise model the
weakness count falls to zero.""",
u"""a ratio that never inverts and that stays between 3.7 and 14 across those nine readings, although it
is unbounded above under a stricter common threshold. Under this study's own noise model the weakness
count falls to zero for the three variables tested.""")
rep(u"""a ratio between 3.7 and 14 that never inverts, and under this study's own noise model the weakness
count falls to zero.""",
u"""a ratio between 3.7 and 14 across those readings that never inverts, and under this study's own noise
model the weakness count falls to zero for the three variables tested.""")

# ---- 4. the two failed decision rules, named
rep(u"""The ankle-at-contact null fails two of the four decision rules
and is not certified by this design,""",
u"""The ankle-at-contact null fails the noise-floor and centring rules of \u00a72.4, so it is not certified by
this design,""")

# ---- 5. the side control, at the gain level its container gives
rep(u"""The unlesioned knee is displaced from control by 3.44 and 4.01\u00b0
at the two deepest gains and carries 35.5 per cent of that endpoint's group separation (\u00a73.3),""",
u"""Scored against the sham artefact, the unlesioned-side control for knee angle at contact fails from
delivered KV 0.100 upward, and at the two deepest gains the unlesioned knee is displaced from control
by 3.44 and 4.01\u00b0, carrying 35.5 per cent of that endpoint's group separation (\u00a73.3),""")

# ---- 6. the Declarations misreport the deposited check
rep(u"""of 218 numeric values in the manuscript and supplement, 204 are carried by a deposited container
whose name relates to the claim, and the remaining 14 are listed in that check's output.""",
u"""of the 218 numeric values of three or more decimals in the manuscript and supplement, 195 are carried
by a deposited container whose name relates to the claim and 23 are not, and that check lists all 23.
Values of fewer than three decimals, which include several of the clinical figures, are outside its
scope.""")

# ---- 7. name the grid, so that x0.60 has an antecedent
rep(u"""A separate 84-cell mixed grid, 74 of them
admitted, crosses four tibialis anterior scalings with four delivered reflex gains and supports \u00a7\u00a73.4
and 3.7.""",
u"""A separate 84-cell mixed grid, 74 of them admitted, crosses four tibialis anterior scalings (\u00d70.60,
\u00d70.70, \u00d70.80 and \u00d71.00) with four delivered reflex gains (0.025, 0.050, 0.100 and 0.220) and supports
\u00a7\u00a73.4 and 3.7.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

# ---- 8. S12 labels a one-standard-error interval as a 95 per cent one
qrep(u"""The within-condition duration regression gives 3 \u00b1 24 per cent of the effect at 95 per cent""",
     u"""The within-condition duration regression gives 3 \u00b1 24 per cent of the effect at 95 per cent""")
qrep(u"""The within-dose duration regression gives 3 \u00b1 9 per cent of the group effect""",
     u"""The within-dose duration regression gives 3 \u00b1 9 per cent of the group effect at one standard error,
or 3 \u00b1 24 per cent at 95 per cent on five conditions""")

# ---- 9. S7's hash count reconciles with nothing
qrep(u"""The remaining 61 verified hashes should be read in that light.""",
     u"""The 55 verified registration hashes should be read in that light.""")

io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("manuscript edits: %d;  supplement edits: %d" % (n[0], n[1]))
