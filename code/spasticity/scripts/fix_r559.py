# -*- coding: utf-8 -*-
"""r559: move the r548-r556 apparatus into the supplement, keeping the verdicts in the text."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r71_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r72_SUPPLEMENT"))
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


# --- 3.4: the bar and the rank convention
rep(u"""Neither count is a fixed quantity, and an earlier version of this section presented them as though
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
strongest, and not as the pair 25 and 3.""",
u"""Neither count is a fixed quantity, and an earlier version of this section presented them as though
they were. Two analytic choices move them: which measurement error is used as the bar, where four of
the 81 variables have published errors of their own and we had applied the smallest to all of them,
and whether the rank correlation uses mid-ranks on a tied dose vector, which the helper we first used
did not. Crossing the three defensible bars with the three rank conventions gives nine readings, in
which the tone count ranges from 14 to 28 and the weakness count from 1 to 7. Under the reading this
section's own sentence describes, an ordering of six scalings at the family level where no ties
exist, they are 27 and 7. The ratio ranges from 3.7 to 14.0 across all nine and never inverts. We
therefore report the asymmetry as a direction and an order of magnitude, roughly fourfold at its
weakest and fourteenfold at its strongest, and not as the pair 25 and 3. Supplement S8 gives the nine
readings and the derivation of each bar.""")

# --- 3.2: the selection-valid statistics
rep(u"""Both that figure
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
what the case rests on.""",
u"""Leave-one-family-out
classification is correct on 59 of 59 cells against a 61.0 per cent majority-class baseline. Both
figures are computed for a readout chosen as the maximum of an 81-candidate scan, so we repeated each
with the selection inside the procedure: a max-*T* permutation that rescans all 81 candidates within
each of the 462 relabellings returns the same p of 0.0022, and a nested classification that chooses
the readout from the ten training families inside each fold picks the same readout in all eleven and
returns the same 59 of 59. Neither statistic can fail for a readout whose arms are disjoint, of which
the scan holds thirty, so neither discriminates among them; what separates the reported endpoint is
the size of its gap against its own noise, not either of these gates. Supplement S9 gives the null
distributions and the per-fold selections.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

sup = io.open(Q, encoding="utf-8").read().rstrip() + u"""

## S8. How the counts of \u00a73.4 depend on the bar and the rank convention

Two analytic choices move the counts of readouts that usably grade each lesion, and \u00a73.4 reports the
range they produce rather than a single pair.

**The bar.** A candidate must span more than one clinical measurement error to be called usable. Ref
[15] Table 2 publishes between-session errors for five sagittal variables, four of them members of
the 81: peak ankle angle in swing at 1.77\u00b0, ankle angle at contact at 2.53\u00b0, peak knee flexion in
swing at 2.06\u00b0 and hip angle at toe-off at 4.15\u00b0, each inverted through that paper's own definition
MDC = SEM \u00d7 1.96 \u00d7 \u221a2. An earlier version of \u00a73.4 stated that only two of the 81 variables had
published errors, which is false against this source, and applied the smallest of the four to all 81,
which is the most permissive choice available. Three bars are defensible: the single permissive one,
each variable's own error where one exists, and each joint's largest published error.

**The rank convention.** The helper used to score the ordering computed ranks as the argsort of the
argsort, which assigns distinct ranks inside a tie group broken by array order rather than mid-ranks.
The dose vector is tied by construction, five gains over 23 hyperreflexia cells and six scalings over
36 weakness cells, so this is not Spearman's \u03c1. Correcting it moves the tone correlations by up to
0.12 and the weakness correlations by up to 0.03, in both cases towards a stronger relation. A third
reading is available and is the one \u00a73.4's own sentence describes: a family-level correlation over
the five gains or the six scalings, in which no ties exist at all.

| bar | rank convention | tone | weakness | ratio |
|---|---|---|---|---|
| permissive, 1.77\u00b0 everywhere | as shipped | 25 | 3 | 8.3 |
| permissive, 1.77\u00b0 everywhere | Spearman, cell level | 28 | 4 | 7.0 |
| permissive, 1.77\u00b0 everywhere | family level | 27 | 7 | 3.9 |
| each variable's own error | as shipped | 24 | 3 | 8.0 |
| each variable's own error | Spearman, cell level | 27 | 4 | 6.8 |
| each variable's own error | family level | 26 | 7 | 3.7 |
| each joint's largest error | as shipped | 14 | 1 | 14.0 |
| each joint's largest error | Spearman, cell level | 17 | 2 | 8.5 |
| each joint's largest error | family level | 16 | 4 | 4.0 |

Sweeping a single common bar from 0.3 to 5.0\u00b0 instead, the tone count falls from 31 to 2 and the
weakness count from 7 to 0. Across every combination the ratio lies between 3.7 and 14.0 and never
inverts. The counts also index how much of the cycle each lesion is legible over rather than how many
independent measurements report it, because the candidates are three curves sampled every 5 per cent
plus eighteen landmarks and adjacent samples of one curve are strongly correlated.

## S9. The selection-valid permutation and the nested classification

\u00a73.2 reports a permutation p and a leave-one-family-out accuracy for a readout selected as the
maximum of an 81-candidate scan. Both were recomputed with the selection inside the procedure.

**Max-*T* permutation.** For each of the C(11,5) = 462 assignments of lineage labels, the family-level
standardised separation was recomputed for all 81 candidates and the largest taken. The observed
maximum is 111.3 seed SD, at peak ankle dorsiflexion in swing. The null distribution of the maximum
has a median of 25.6 and a 95th centile of 67.4, and one arrangement of the 462 attains the observed
value, which is the true labelling. The selection-valid p is 0.00216, identical to the naive
single-readout figure, because 1/462 is the floor the design can return.

**Nested leave-one-family-out.** In each of the eleven folds the winning candidate was chosen using
only the ten training families, and the classifying threshold fitted on those ten. Peak ankle
dorsiflexion in swing was selected in all eleven folds, and the accuracy is 59 of 59.

**What neither shows.** The permutation cannot return a value below 1/462 on an eleven-family design
and returns exactly that for each of the thirty candidates whose arms are disjoint; the
classification returns 1.000 for each of them too. Neither statistic discriminates among the
separating readouts and neither can fail for one.
"""
io.open(Q, "w", encoding="utf-8", newline="").write(sup)
print("edits applied: %d" % n[0])
