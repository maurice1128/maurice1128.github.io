# -*- coding: utf-8 -*-
"""r585: take the narration out of the Background.

Measured against Jansen's introduction, per thousand words: named human actors 0.7 against 0.0,
agentive verbs on abstractions 0.7 against 0.0, non-restrictive which-clauses 4.4 against 1.1,
stakes-and-consequence language 1.5 against 0.0, italic or bold scene labels 2.2 against 0.0. A
supervisor reading this manuscript said the introduction read like a novel, and those five figures
are what that judgement measures.

Jansen's introduction is epidemiology, then what is unknown, then the specific unresolved debate with
both sides cited, then the range of existing models, then the aim. It never tells the reader what is
at stake, never gives an abstraction a verb of agency, and never labels a passage.

Also corrected here: "no antidote" is this paper's gloss, where ref [1] describes the blockade as
reversible and lasting three to six months; a speculation about what a guideline document meant but
did not write; and a dismissive figure of speech about a cited work.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r114_MANUSCRIPT"))
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


# --- stakes-telling: state the treatments and their duration, not the drama
rep(u"""Misapportionment costs more in one direction than the other. Toxin
injected into a triceps surae that is weak rather than overactive removes the plantarflexor drive
the limb uses for knee stability in stance, and the blockade lasts three to six months with no
antidote [1]. Selective neurotomy and tendon lengthening cannot be reversed at all, which is why the
block is used most before surgery.""",
u"""The consequences of an error are asymmetric. Botulinum toxin injected into a triceps surae that is
weak rather than overactive reduces the plantarflexor moment available for knee stability in stance,
and ref [1] describes the blockade as reversible over three to six months. Selective neurotomy and
tendon lengthening are not reversible, and the block is used most often before those procedures.""")

# --- speculation about a source's silence
rep(u"""Both are
approximations, and the guidance retains the block alongside them instead of replacing them with it
[1], which we read as a response to their limitations, although the paper does not say so.""",
u"""Both are approximations, and the guidance retains the block alongside them rather than in place of
them, without stating its reason [1].""")

# --- scene labels
rep(u"**Scope.** This study addresses none of the block's purposes directly.",
    u"This study addresses none of the block's purposes directly.")
rep(u"*Both components.* In 30 chronic stroke patients,", u"In 30 chronic stroke patients,")
rep(u"*Simulation.* Reflex-gain forward simulation", u"Reflex-gain forward simulation")

# --- aphoristic closer
rep(u"""The clinical question is rarely which of the three a limb has, and is usually how much of each.""",
u"""The clinical question is therefore usually one of proportion rather than of which single cause is
present.""")

# --- production jargon and a forensic audit inside the Background
rep(u"""Its coefficients are
less secure: the galley and a machine-readable rendering of the same table disagree, and two of the
five coefficient\u2013p pairs do not imply one another at n = 12, so we rest the null on the p values and
turn no argument on the coefficients.""",
u"""Its reported coefficients are internally inconsistent, two of the five coefficient and p value
pairs not implying one another at n = 12, so we rely on the p values alone.""")

# --- dismissive figure of speech, and a misplaced connective from the r583 pass
rep(u"""under gastrocnemius hyperreflexia. However, the event examined here is not new. That paper also
reaches this study's endpoint and its interpretation.""",
u"""under gastrocnemius hyperreflexia, so the event examined here is not new. That paper also reaches
this study's endpoint and its interpretation.""")
rep(u"""its cross-muscle summary is a table of
qualitative arrows, it simulates no weakness, and it proposes no discriminator.""",
u"""it summarises cross-muscle effects as
directional only, it simulates no weakness, and it proposes no discriminator.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits: %d" % n[0])
