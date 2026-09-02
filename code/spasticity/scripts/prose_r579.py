# -*- coding: utf-8 -*-
"""r579: the wording faults a copy editor would stop at.

A blind read against Jansen, Ong and Mendes-Andrade found eight passages that are outright errors of
register or of grammar rather than matters of taste. Chief among them: four sentences in Results that
narrate this manuscript's own drafting history. No comparator contains one. Correction history
belongs in the response to reviewers and in the supplement, not in a Results section; what a Results
section states is the analysis that stands and why. The withdrawals themselves are kept, in the
supplement, where a reader auditing the work will look for them.

Also fixed here: "write on" as a causal verb, "rectifies"/"recruits" colliding with their EMG senses,
"blindness" colliding with assessor masking, a severed coordination in 1.2, broken list punctuation
in 4.4, and an 80-word sentence whose appositive is separated from its antecedent.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r102_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r103_SUPPLEMENT"))
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


# ---- 1. drafting history out of Results. The withdrawals stay, in the supplement.
rep(u"""Neither count is a fixed quantity, and an earlier version of this section presented them as though
they were. Two analytic choices move them:""",
u"""Neither count is a fixed quantity. Two analytic choices move them:""")

rep(u"""Supplement S1 gives both conventions and the error an earlier
version of this analysis made in the first of them.""",
u"""Supplement S1 gives both conventions.""")

rep(u"""At peak swing dorsiflexion the answer depends on which
pairs are counted, and an earlier version of this section counted only some of them. Among the 96
pairs that differ in reflex gain the closest differ by 0.833\u00b0""",
u"""At peak swing dorsiflexion the answer depends on which pairs are counted. Among the 96 pairs that
differ in reflex gain the closest differ by 0.833\u00b0""")

rep(u"""An earlier version of this section reported that no pair fell within one seed SD,
which was computed on the 96 without saying so; that claim is withdrawn.""", u"")

rep(u"""An earlier version of this section reported a third signature, a left-minus-right hip asymmetry, as
evidence that the redistribution reaches a joint neither lesioned muscle crosses. It is withdrawn.
The comparison rested on one hyperreflexia lineage, so no between-family variance was estimable; its
weakness figure was drawn from an unrecorded three-lineage subset where the container holds six,
whose mean is +0.479\u00b0 rather than the +0.45\u00b0 printed; and the edge gap is 1.7 to 3.3 times the seed
SD depending on which arm's floor is used, not the 2.7 to 3.0 stated. The caution above does not
depend on it. A search over candidate mechanisms returned none that survives the artefact floor.""",
u"""No candidate mechanism produced an effect exceeding the protocol artefact. A left-minus-right hip
asymmetry was examined and is not reported, for the reasons given in Supplement S11.""")

# ---- 2. the closing aphorism
rep(u"""It does not deliver a spasticity meter.""",
    u"""These results do not support using the variable as an absolute measure of tone in an individual
patient.""")

# ---- 3. "write on" as a causal verb
rep(u"""The qualitative claim that calf
hyperreflexia can write on swing dorsiflexion is therefore not ours.""",
u"""The qualitative claim that calf hyperreflexia can reduce swing dorsiflexion is therefore not
ours.""")
rep(u"""the model understates what dorsiflexor force
writes onto swing dorsiflexion""",
u"""the model understates the effect of dorsiflexor force on swing dorsiflexion""")
rep(u"""Weakness may therefore write on timing where it writes little on sagittal angle""",
    u"""Weakness may therefore affect timing where it affects sagittal angle little""")

# ---- 4. "rectifies" and "recruits" collide with their EMG senses
rep(u"""A maximum rectifies noise upward, and the hyperreflexia
peak is flatter than the control's, so it recruits more samples into the maximum and rectifies
harder.""",
u"""Taking a maximum biases the estimate upward under noise, and because the hyperreflexia peak is
flatter than the control's, more samples fall near that maximum and the upward bias is larger.""")

# ---- 5. "something happening at the calf"
rep(u"""The reading therefore separates *something happening at the calf* from dorsiflexor weakness.""",
u"""The reading therefore separates plantarflexor abnormality of any origin, whether hyperreflexia,
cocontraction or shortening, from dorsiflexor weakness.""")

# ---- 6. "blindness" collides with assessor masking
rep(u"""The blindness claim is accordingly specific in four ways, and holds within them:""",
    u"""The insensitivity to weakness is accordingly specific in four ways, and holds within them:""")
rep(u"""And the blindness claim holds where walking speed is nearly matched:""",
    u"""And the insensitivity to weakness holds where walking speed is nearly matched:""")

# ---- 7. severed coordination in 1.2
rep(u"""Reflex-gain forward simulation reproduces hemiparetic-like kinematics, including
increased knee and hip flexion at initial contact under gastrocnemius hyperreflexia, so the event
examined here is not new, and through loading response, stance and swing.""",
u"""Reflex-gain forward simulation reproduces hemiparetic-like kinematics, including increased knee and
hip flexion at initial contact and through loading response, stance and swing under gastrocnemius
hyperreflexia, so the event examined here is not new.""")

# ---- 8. broken list punctuation in 4.4
rep(u"""three measurements per limb: instrumented gait, giving peak dorsiflexion in swing. A graded measure
of calf overactivity, ideally against a diagnostic block in the subgroup receiving one; and
dorsiflexor strength by dynamometry.""",
u"""three measurements per limb: instrumented gait, giving peak dorsiflexion in swing; a graded measure
of calf overactivity, ideally against a diagnostic block in the subgroup receiving one; and
dorsiflexor strength by dynamometry.""")

s = re.sub(r"\n{3,}", "\n\n", s)
io.open(P, "w", encoding="utf-8", newline="").write(s)

# the withdrawn hip analysis moves to the supplement, where an auditor will look for it
q = io.open(Q, encoding="utf-8").read().rstrip() + u"""

## S11. An analysis examined and not reported

An earlier draft reported a third signature of the redistribution described in \u00a73.8: a
left-minus-right hip range-of-motion asymmetry, offered as evidence that the effect reaches a joint
neither lesioned muscle crosses. It is not reported, for three reasons found on audit. The comparison
rested on a single hyperreflexia chain, so no between-condition variance was estimable. Its weakness
figure was drawn from an unrecorded three-chain subset where the deposit holds six, whose mean is
+0.479\u00b0 rather than the +0.45\u00b0 the draft printed. And the edge gap is 1.7 to 3.3 times the seed SD
depending on which group's noise threshold is used, rather than the 2.7 to 3.0 stated. The caution in
\u00a73.8 rests on the unlesioned-side displacement and does not depend on this analysis.

\u00a73.7's earlier statement that no pair of grid cells fell within one seed SD at the reported endpoint
is also not carried in the text as written: it was computed over the 96 pairs differing in reflex
gain, and four of the 24 same-gain pairs fall below the grid threshold, the closest at 0.044\u00b0. The
current text reports all 120.
"""
io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("tier-1 wording faults fixed: %d;  S11 added" % n[0])
