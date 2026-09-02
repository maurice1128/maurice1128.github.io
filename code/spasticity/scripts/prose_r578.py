# -*- coding: utf-8 -*-
"""r578: reframe three limitations outward, as Jansen 2014 frames its own.

Read end to end, Jansen's Limitations section opens each item on an unresolved question in the field
and only then says what that means for the model: "In the literature, a large ambiguity exists on the
contribution of length and velocity feedback... Contributions of soleus velocity feedback range from
no [51] or weak contribution [39], to percentages of 30% to 60% [52]." Five sources disagreeing, then
the consequence.

This manuscript's limitations open on the authors instead: "Everything here is a property of a single
model", "An earlier version of this section justified it wrongly". Both are honest. Only the second
is the genre's convention, and the first framing is also the more accurate one, because in each of
these three cases the uncertainty genuinely belongs to the field and not to this study alone.

Nothing is removed. Every number, every withdrawal and every self-correction stays. Only the order
changes: the open question first, this study's position within it second.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r98_MANUSCRIPT"))
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


# --- limitation 1: how to model these two lesions is unsettled in the field
rep(u"""**1. One model, one controller, and one patient result that runs against the asymmetry.** Everything
here is a property of a single 19-degree-of-freedom model under a single reflex controller, and the
asymmetry between the lesions rests on how much reserve this model's tibialis anterior retains in an
unloaded swing limb. That is a modelling choice no internal control reaches, so it should be read as
a hypothesis about human gait rather than as a measurement of it.""",
u"""**1. How these lesions are modelled is unsettled, and the asymmetry depends on that choice.** No
convention governs how spasticity and weakness enter a musculoskeletal simulation. Jansen et al.
represent spasticity as increased length and velocity feedback with gains chosen arbitrarily, and
state that no claim about absolute effect follows from them [9]; Ong et al. scale maximum isometric
force for weakness and shorten tendon slack length for contracture, re-optimising per condition [10];
a further model contrasts plantarflexor hyperreflexia against plantarflexor weakness in two
dimensions [11]; and in personalised cerebral-palsy models, impairments of known magnitude explain on
average 17 per cent of the kinematic deviation and never more than 39 [12]. The scale of what these
representations recover therefore varies widely, and the choice is not settled by any of them.

This study sits inside that spread. Everything reported here is a property of a single
19-degree-of-freedom model under a single reflex controller, and the asymmetry between the lesions
rests on how much reserve this model's tibialis anterior retains in an unloaded swing limb. That is a
modelling choice no internal control reaches, so it should be read as a hypothesis about human gait
rather than as a measurement of it.""")

# --- limitation 2: losing stability under severe impairment is a known property of these models
rep(u"""**2. The arms are confounded with simulation survival, and the confound cannot be lifted.** None of
the 23 admitted hyperreflexia cells reaches the simulation horizon and all 36 weakness cells do, so
no arm comparison at matched survival exists on this corpus, for this readout or any other: the
confound belongs to the corpus rather than to the endpoint.""",
u"""**2. Predictive simulations stop walking under severe impairment, and here that covaries with the
lesion.** Losing gait under a sufficiently deep deficit is a property of this class of model rather
than of this study: Ong et al. report that theirs walks without substantial adaptation until both
plantarflexors are moderately or severely weakened [10], and severity and survival are therefore
coupled wherever a predictive simulation is driven to the edge of its stable range. In this corpus
the coupling falls along the lesion axis. None of the 23 admitted hyperreflexia cells reaches the
simulation horizon and all 36 weakness cells do, so no arm comparison at matched survival exists here,
for this readout or any other: the confound belongs to the corpus rather than to the endpoint.""")

# --- limitation 4: unlesioned model ankles depart from normal in this literature too
rep(u"""**4. The model's early-stance ankle trajectory is not physiological.** The unlesioned ankle
reproduces the loading-response plantarflexion trough and the toe-off excursion (\u221219.8\u00b0 at 59.5 to
63 per cent of cycle, against a normal \u221215 to \u221220\u00b0 at 60 to 62 per cent), and reaches its swing peak
at the phase a normal ankle does.""",
u"""**4. Unlesioned model ankles depart from normal in this literature, and ours departs in early
stance.** Predictive simulations reproduce the gross shape of the ankle trajectory and not its
detail: the unlesioned model of Ong et al. contacts the ground at 15 to 16\u00b0 of dorsiflexion [10],
outside the normal range at that instant, and displacements in such studies are measured from a
baseline that is itself only approximately physiological. The same holds here, in a different part of
the cycle. Our unlesioned ankle reproduces the loading-response plantarflexion trough and the toe-off
excursion (\u221219.8\u00b0 at 59.5 to 63 per cent of cycle, against a normal \u221215 to \u221220\u00b0 at 60 to 62 per
cent), and reaches its swing peak at the phase a normal ankle does.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("limitations reframed: %d" % n[0])
