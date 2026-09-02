# -*- coding: utf-8 -*-
"""r551: apply round-four council repairs to MANUSCRIPT_r541.md."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r62_MANUSCRIPT"))
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


# 1 -- the measurement-error bar was justified against our own source wrongly
rep(u"""We applied a single bar of 1.77 to every
candidate, because published between-session errors exist for only two of the 81 variables, peak
swing dorsiflexion at 1.77 [15] and knee angle at contact at 2.62 [13]; the swing figure is the
smaller and so the more permissive, and substituting the knee's 2.62 for the knee and hip candidates
removes one of the counts below and none of the three. The same test applied to the hyperreflexia arm
is met by 25 of the 81. Calf overactivity is legible across roughly a third of the sagittal readouts
a gait laboratory produces, at the ankle throughout swing and late stance and at the knee through
loading response, so the finding does not depend on our having chosen the right one. Weakness is
written in an eighth as many places, and far more faintly.""".replace(u"1.77 to every", u"1.77\u00b0 to every").replace(u"at 1.77 [15]", u"at 1.77\u00b0 [15]").replace(u"at 2.62 [13]", u"at 2.62\u00b0 [13]").replace(u"knee's 2.62 for", u"knee's 2.62\u00b0 for"),
u"""The same test applied to the hyperreflexia arm is met by 25.

Neither count is a fixed quantity, and an earlier version of this section presented them as though
they were. Two analytic choices move them. The first is the bar. Ref [15] publishes between-session
errors for five sagittal variables and not two, four of them members of the 81 by our own
construction: peak ankle angle in swing at 1.77\u00b0, ankle angle at contact at 2.53\u00b0, peak knee flexion
in swing at 2.06\u00b0 and hip angle at toe-off at 4.15\u00b0, each inverted through that paper's own
definition. We had applied the smallest of the four to all 81, which is the most permissive choice
available. The second is the rank convention. The helper used to score the ordering assigned distinct
ranks inside a tie group rather than mid-ranks, and the dose vector is tied by construction, five
gains over 23 cells and six scalings over 36. The sentence above describes an ordering of six
scalings, which is a family-level correlation over six points with no ties in it at all, and that is
the quantity we now report.

Crossing the three defensible bars with the three rank conventions gives nine readings. The tone
count ranges from 14 to 28 and the weakness count from 1 to 7. Under the reading the sentence
describes, family-level ordering against the permissive bar, they are 27 and 7. The ratio between
them ranges from 3.7 to 14.0 across all nine and never inverts. We therefore report the asymmetry as
a direction and an order of magnitude, roughly fourfold at its weakest and fourteenfold at its
strongest, and not as the pair 25 and 3.

One further caution belongs with any count over the 81. The candidates are three joint-angle curves
sampled every 5 per cent of the cycle plus eighteen landmarks, so adjacent samples of one curve are
strongly correlated and the denominator is not 81 independent opportunities. Halving the sampling
interval would roughly double both counts and change nothing. The counts index how much of the cycle
each lesion is legible over, not how many separate measurements report it. On that reading calf
overactivity is legible over between a sixth and a third of the sagittal readouts a gait laboratory
produces, at the ankle throughout swing and late stance and at the knee through loading response, so
the finding does not depend on our having chosen the right one, and weakness over a small fraction of
that, and far more faintly.""")

# 2 -- Chisholm: only the abstract was retrieved
rep(u"""Chisholm et
al. measured isometric dorsiflexor force and sagittal ankle kinematics in a cohort of 55 sub-acute
stroke survivors and found peak dorsiflexion during swing associated with that force at a
coefficient of magnitude 0.32 (p = 0.039), on 44 of the 55 who completed the force testing [28].
(The published abstract prints the coefficient as negative. The paper's own discussion describes
greater force accompanying greater swing dorsiflexion, which requires the positive sign, and a
version of the same dataset reports it as positive. Nothing here rests on the sign. The magnitude is
what bears on this study.) That cohort sits inside this model's own weakness window, not outside it.
Its mean paretic-to-non-paretic dorsiflexor force ratio was 0.84: within 0.80 to 0.95 and below
its midpoint, so if anything slightly weaker on average than the arm studied here, over which this
model's weakness ladder spans 0.66. A real association was therefore found in patients precisely
where this model reports almost nothing. If it holds, this model understates what dorsiflexor force
writes onto swing dorsiflexion, and the most likely reason is that its tibialis anterior retains
more reserve in an unloaded swing limb than a paretic one does.

The same cohort also bounds the positive half of the claim: it found no association between
Ashworth-graded spasticity and peak swing dorsiflexion (r = 0.11, p = 0.408) [28]. Neither of this
study's two claims survives that cohort intact.""".replace(u"within 0.80 to 0.95", u"within \u00d70.80 to \u00d70.95").replace(u"spans 0.66.", u"spans 0.66\u00b0.").replace(u"(r = 0.11,", u"(r = \u22120.11,"),
u"""Chisholm et
al. studied 55 independently ambulating sub-acute stroke survivors and report that peak dorsiflexion
during swing was related to isometric dorsiflexor muscle force at r = \u22120.32, p = 0.039 [28]. An
association of that size, between dorsiflexor force and this study's own endpoint, in patients, is
what this model reports as faint. We state the limits of our access to it plainly: only the published
abstract of [28] was retrieved, so the coefficient, its p value and the cohort size are all we can
verify, and the figures that would decide how severely it bears on this study cannot be checked.
Chief among those is the cohort's dorsiflexor force distribution, which determines whether it
overlaps the \u00d70.80 to \u00d70.95 window over which this model's weakness ladder spans 0.66\u00b0 or lies well
below it. If it overlaps, a real association was found in patients where this model reports almost
nothing, the model understates what dorsiflexor force writes onto swing dorsiflexion, and the most
likely reason is that its tibialis anterior retains more reserve in an unloaded swing limb than a
paretic one does. If the cohort is substantially weaker, the two results are compatible and say only
that this study's ladder stops short of the range where weakness becomes legible, which 4.5 concedes
on other grounds. We cannot tell which. A reader should treat the asymmetry as bounded by an
unresolved patient result rather than as unopposed.""".replace(u"which 4.5 concedes", u"which \u00a74.5 concedes"))

# 3 -- the noise model was run on the three; the text says it was not
rep(u"""The three readouts that do grade
weakness on noise-free traces (3.4) are not among the candidates put through this noise model, so
what measurement error leaves of their 2.2 to 2.9 spans is untested; given that those spans are
larger than the 0.66 tested here and that the between-session error is 1.77, the question is open
rather than settled, and a follow-up should close it first.""".replace(u"(3.4)", u"(\u00a73.4)").replace(u"2.9 spans", u"2.9\u00b0 spans").replace(u"the 0.66 tested", u"the 0.66\u00b0 tested").replace(u"is 1.77,", u"is 1.77\u00b0,"),
u"""The three readouts that do grade weakness
on noise-free traces (\u00a73.4) were put through the same model separately and none survives it: their
rank correlations with weakness depth fall from 0.822, 0.900 and 0.820 to 0.707, 0.693 and 0.682 at
3\u00b0 of jitter, below the 0.8 bar \u00a73.4 applies. Under this study's own measurement model the number of
readouts that grade weakness is not three but zero, and the counts in \u00a73.4 should be read as
noise-free throughout.""")

# 4 -- Jansen already reports the swing direction and the attribution
rep(u"""It does not give the
effect an interpretable magnitude: gain factors were chosen arbitrarily, so by that paper's own
statement no claim about absolute effect can be made. Its cross-muscle summary is a table of
qualitative arrows; and it proposes no discriminator and simulates no weakness [9].""",
u"""That paper also reaches this study's endpoint and
its interpretation. Reduced suppression of spindle feedback during swing is reported there to
contribute to increased plantarflexion in the swing phase and so to hampered toe clearance, and its
discussion states that in the literature this deficit is attributed mainly to pretibial weakness,
with the role of hyperreflexia not specifically considered [9]. The qualitative claim that calf
hyperreflexia can write on swing dorsiflexion is therefore not ours. What that paper does not supply
is a magnitude: its gain factors were chosen arbitrarily, so by its own statement no claim about
absolute effect can be made, its cross-muscle summary is a table of qualitative arrows, it simulates
no weakness, and it proposes no discriminator. What is new here is the comparison against a weakness
arm of known depth, not the direction of the effect [9].""")

# 5 -- broken bold
rep(u"### 2.2 Lesions\n\nHyperreflexia**: a `MuscleReflex`",
    u"### 2.2 Lesions\n\n**Hyperreflexia**: a `MuscleReflex`")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits applied: %d" % n[0])
