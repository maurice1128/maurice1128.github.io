# -*- coding: utf-8 -*-
"""r557: remove the hip experiment, compress the preregistration, move detail to the supplement."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r67_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r68_SUPPLEMENT"))
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


# --- 3.8: cut the hip experiment; keep the caution, which rests on the leakage comparison
i, j = s.index(u"### 3.8 Mechanism"), s.index(u"\n---\n\n## 4. Discussion")
new38 = u"""### 3.8 What the separation localises, and what it does not

The controller is re-optimised for every lesion, so the joint at which a difference appears does not
identify the muscle responsible. The unlesioned knee is displaced from control by 3.44 and 4.01\u00b0 at
the two deepest gains and carries 35.5 per cent of that endpoint's arm separation (\u00a73.3): a
re-optimised body redistributes a local deficit, and a single-joint reading registers the
redistribution along with the deficit. That a distal constraint displaces proximal kinematics is not
itself surprising, since imposing equinus mechanically on unimpaired adults alters knee kinematics
during gait [19].

The reported endpoint is the least exposed to this of the readouts examined. Its unlesioned-side
leakage is 0.5 per cent against the knee's 35.5, both scored at the unlesioned limb's own contact
(\u00a73.3); scored instead at the lesioned limb's contact the knee figure is 30.8 per cent and the ankle
figure is unchanged. What it registers is almost entirely a lesion-side displacement. The caution
still applies to what the reading means: it grades calf overactivity as a marker and not as a direct
observation of the calf.

An earlier version of this section reported a third signature, a left-minus-right hip asymmetry, as
evidence that the redistribution reaches a joint neither lesioned muscle crosses. It is withdrawn.
The comparison rested on one hyperreflexia lineage, so no between-family variance was estimable; its
weakness figure was drawn from an unrecorded three-lineage subset where the container holds six,
whose mean is +0.479\u00b0 rather than the +0.45\u00b0 printed; and the edge gap is 1.7 to 3.3 times the seed
SD depending on which arm's floor is used, not the 2.7 to 3.0 stated. The caution above does not
depend on it. A search over candidate mechanisms returned none that survives the artefact floor.

Two results do not survive as stated. The ankle-at-contact null fails two of the four decision rules
and is not certified by this design. Knee angle at contact loses lesion-side specificity at the
deeper gains, where the unlesioned knee moves as well (\u00a73.3). A third question no control here can
reach is whether the separation follows from lesion type or from the lesion's effect on stability.

"""
s = s[:i] + new38 + s[j + 1:]
n[0] += 1

# --- 2.5: compress to a disclosure; the detail goes to S7
i = s.index(u"### 2.5 Preregistration")
j = s.index(u"\n## 3. Results")
old25 = s[i:j]
new25 = u"""### 2.5 Preregistration

The analysis of the mixed grid was registered before its results were read, and the registration
does not certify what is reported here. Of its four predictions, two are uninformative as registered,
one was made at an endpoint this paper does not use, and one, P4, was informative and is tested in
\u00a73.7. Two grid elements entered after registration and are marked where they are used. Sixty-one of
the 78 deposited hashes verify; one registration was edited after its result was produced, together
with its analysis script and outputs, and the hash sidecars were re-baselined, so hash verification
cannot detect that breach. We report the registration as a record of what was planned and not as
assurance about any result, and a reader should treat every analysis in this paper as exploratory.
The full text of the predictions, the hash audit and the post hoc elements are in Supplement S7.

"""
s = s[:i] + new25 + s[j + 1:]
n[0] += 1

io.open(P, "w", encoding="utf-8", newline="").write(s)

# --- supplement gains S7
sup = io.open(Q, encoding="utf-8").read()
sup = sup.rstrip() + u"""

## S7. The preregistration, in full

This section carries the material compressed out of \u00a72.5. It is a record of what was planned. It
certifies nothing, and \u00a72.5 says so.

""" + "\n".join(l for l in old25.split("\n")[2:] if l.strip() or True).strip() + u"""

**The hash audit.** Sixty-one of the 78 deposited hashes verify. The seventeen that do not fall into
two groups. Most are files regenerated after a cosmetic change to an analysis script, where the
result is unchanged and the sidecar was not rewritten. One is a genuine breach: a registration was
edited after its result was produced, together with its analysis script and its regenerated outputs,
and the hash sidecars were re-baselined at the same time. Hash verification cannot detect that,
because the baseline moved with the file. We record it here because no automated check in this
repository would surface it, and a reader is entitled to know that the registration's integrity rests
on this disclosure rather than on the hashes.

**Post hoc elements.** Two parts of the mixed grid entered after the registration was hashed: the
\u00d70.70 tibialis anterior row and the highest gain column. Every analysis of the grid uses all 74
admitted cells and \u00a73.7 marks where the post hoc elements enter a comparison.
"""
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("edits applied: %d;  S7 added (%d words moved)" % (n[0], len(old25.split())))
