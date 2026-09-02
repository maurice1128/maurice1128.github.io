# -*- coding: utf-8 -*-
"""r556: fourth batch of round-four council repairs."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r66_MANUSCRIPT"))
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


# --- selection-valid permutation and nested LOFO
rep(u"""Permuting the eleven lineage labels exhaustively, all C(11,5) = 462 ways, places the observed
split first at p = 0.0022, which is 1/462 and the smallest value the design can return.
Leave-one-family-out classification is correct on 59 of 59 cells against a 61.0 per cent
majority-class baseline.""",
u"""Permuting the eleven lineage labels exhaustively, all C(11,5) = 462 ways, places the observed split
first at p = 0.0022, which is 1/462 and the smallest value the design can return. Both that figure
and the classification below are computed for a readout chosen as the maximum of an 81-candidate
scan, so we repeated each with the selection inside the procedure. Recomputing all 81 candidates
within every one of the 462 relabellings and taking the largest standardised separation in each gives
a null distribution for the maximum of the scan; its median is 25.6 seed SD and its 95th centile
67.4, against an observed 111.3, and one arrangement of the 462 reaches the observed value, which is
the true one. The selection-valid p is therefore 0.0022, unchanged. Leave-one-family-out
classification is correct on 59 of 59 cells against a 61.0 per cent majority-class baseline, and
repeating it with the readout chosen from the ten training families inside each fold returns the same
readout in all eleven folds and the same 59 of 59.

Two cautions attach to those two statistics. The permutation cannot return a value below 1/462 on an
eleven-family design, and it returns exactly that for every candidate in the scan whose arms are
disjoint, of which there are thirty; leave-one-family-out likewise returns 1.000 for any such
candidate. Neither statistic discriminates among the separating readouts, and neither can fail for
one. What separates the reported endpoint from the rest is the size of its gap against its own noise,
not either of these gates. We report them because a reader will ask for them, not because they are
what the case rests on.""")

# --- 3.7: the confusability claim excluded the pairs that produce confusion
rep(u"""At peak swing dorsiflexion no
pair falls within one seed SD. The closest differ by 0.833\u00b0, 9.3 times that endpoint's grid floor of
0.089\u00b0. The two figures are not drawn from the same population of pairs: the knee comparison is
restricted to the registered rungs, six pairs in all, while the ankle comparison runs over all 96
pairs the admitted grid supplies, including the post hoc \u00d70.70 row and the highest gain column.
Restricting the ankle comparison to the registered rungs leaves its closest pair unchanged.""",
u"""At peak swing dorsiflexion the answer depends on which
pairs are counted, and an earlier version of this section counted only some of them. Among the 96
pairs that differ in reflex gain the closest differ by 0.833\u00b0, 9.3 times that endpoint's grid floor
of 0.089\u00b0. The grid supplies 120 pairs, and the 24 remaining ones hold gain fixed and vary
dorsiflexor strength alone. Four of those fall below the floor, the closest at 0.044\u00b0, and all four
are same-gain pairs. So the endpoint does not separate two limbs whose calves are equally overactive
and whose dorsiflexors differ, which is \u00a73.4's asymmetry restated one pair at a time rather than a
result in tension with it. The registered prediction is met at this endpoint for pairs differing in
weakness and fails for pairs differing in tone, and the earlier claim that no pair falls within one
seed SD is withdrawn. The two knee and ankle figures are also not drawn from the same population: the
knee comparison is restricted to the registered rungs, six pairs in all, while the ankle comparison
runs over the whole admitted grid, including the post hoc \u00d70.70 row and the highest gain column.
Restricting the ankle comparison to the registered rungs leaves its closest different-gain pair
unchanged.""")

# --- the faller control's selection order was checked
rep(u"""The archive supplies a stronger and more direct control. Separate lineages carry a
plantarflexor-weakness lesion (neither of the two arms, and no stretch reflex at all) and many of
their cells die early.""",
u"""The archive supplies a stronger and more direct control. Separate lineages carry a
plantarflexor-weakness lesion (neither of the two arms, and no stretch reflex at all) and many of
their cells die early. Because this control turns on end time, we checked that the rule choosing one
run directory per lineage-seed does not itself select on it: choosing the directory before applying
the admissibility gate, as every other analysis in this paper does, and choosing it among the gate's
survivors both return the same 17 cells and the same mean.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits applied: %d" % n[0])
