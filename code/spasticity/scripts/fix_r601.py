# -*- coding: utf-8 -*-
"""r601: the pointer failures and cross-file contradictions of the seventh read.

Twelve pointers name a section that does not hold what is promised, and four statements are asserted
in one file and denied in the other. Every one is a consequence of moving text between the two files;
none touches a result.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r150_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r151_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
q = io.open(Q, encoding="utf-8").read()
n = [0, 0]


def _r(t, o, nn, w):
    pat = re.compile(r"\s+".join(re.escape(x) for x in o.split()))
    ms = list(pat.finditer(t))
    if len(ms) != 1:
        print("  SKIP(%d) %s: %s" % (len(ms), w, o[:50]))
        return t
    n[0 if w == "MS" else 1] += 1
    return t[:ms[0].start()] + nn + t[ms[0].end():]


def rep(o, nn):
    global s
    s = _r(s, o, nn, "MS")


def qrep(o, nn):
    global q
    q = _r(q, o, nn, "SUP")


# ---------------- pointers
# (a) S4 holds four controls, not three, and the selection check is not in it
qrep(u"## S4. The three remaining controls of \u00a73.3, in full",
     u"## S4. The four remaining controls of \u00a73.3, and the faller selection check")
qrep(u"**The five duration slopes.**",
     u"**The faller selection check.** Because that control turns on end time, the rule choosing one run"
     u" directory per chain-seed must not itself select on it. Choosing the directory before applying"
     u" criterion G, as every other analysis in this paper does, and choosing it among the criterion's"
     u" survivors both return the same 17 runs and the same mean of 9.572\u00b0.\n\n**The five duration"
     u" slopes.**")
rep(u"Supplement S4 gives this control's selection check\nand the four remaining controls in full.",
    u"Supplement S4 gives this control's selection check and the four remaining controls in full.")

# (b) nothing in 3.7 marks the post hoc elements; say where they are instead
rep(u"two grid elements\nentered afterwards and are marked where they are used.",
    u"two grid elements entered afterwards, the \u00d70.70 tibialis anterior row and the highest gain column,\n"
    u"and Supplement S10 marks which comparisons rest on them.")
qrep(u"\u00a73.7 marks where the post-hoc elements enter.", u"Supplement S10 marks which comparisons rest on them.")
qrep(u"\u00a73.7 marks where the post hoc elements enter a\ncomparison.",
     u"The \u00d70.70 row and the highest gain column are named here so that any comparison resting on them can\n"
     u"be identified: \u00a73.7's closest different-gain pair, at 0.833\u00b0, is one such comparison, and three of\n"
     u"the four sub-floor same-gain pairs are others.")

# (c) 4.4 does not return to toe clearance; 2.1 should not promise it
rep(u"that absence follows from the objective and is not a result, and \u00a74.4 returns to it.",
    u"that absence follows from the objective and is not a result.")

# (d) Fig. 1 carries no census
rep(u"six weakness conditions and one control chain (Fig. 1).",
    u"six weakness conditions and one control chain.")
rep(u"Every hyperreflexia run is less dorsiflexed than every weakness run (Fig. 2)",
    u"Every hyperreflexia run is less dorsiflexed than every weakness run (Figs. 1 and 2)")

# (e) the rectification argument is in S3, not 3.6
rep(u"while a maximum amplifies it (\u00a73.6) and survives on the size of its\nclean gap",
    u"while a maximum amplifies it (Supplement S3) and survives on the size of its clean gap")

# (f) 22.7 per cent is in 4.1
rep(u"the corresponding single-patient figure is the 22.7 per cent misclassification of \u00a73.5.",
    u"the corresponding single-patient figure is the 22.7 per cent misclassification of \u00a74.1.")

# (g) S1's two wrong section numbers
qrep(u"is the 1.77\u00b0 figure of \u00a73.4 rather than anything in this grid",
     u"is the 1.77\u00b0 figure of \u00a73.5 rather than anything in this grid")
qrep(u"The \u00a73.4 weakness series of 0.66\u00b0", u"The weakness series of 0.66\u00b0 (Supplement S14)")

# (h) the 0.511 floor is defined in S10
qrep(u"against the 0.511\u00b0 floor of \u00a72.4", u"against the 0.511\u00b0 floor of Supplement S10")

# (i) the speed slope is in S4
qrep(u"the endpoint depends on speed at \u22120.563 \u00b0/(m\u00b7s\u207b\u00b9) (\u00a73.3)",
     u"the endpoint depends on speed at \u22120.563 \u00b0/(m\u00b7s\u207b\u00b9) (Supplement S4)")
rep(u"and this endpoint\ndepends on speed at \u22120.563 \u00b0/(m\u00b7s\u207b\u00b9)",
    u"and this endpoint depends on speed at \u22120.563 \u00b0/(m\u00b7s\u207b\u00b9) (Supplement S4)")

# (j) the patient study is proposed in 4.3
qrep(u"not a sample size for the study \u00a74.4 proposes, which is correlational",
     u"not a sample size for the study \u00a74.3 proposes, which is correlational")

# (k) S7 refers to the supplement from inside it
qrep(u"Registrations that failed, and the one that produced no result, are listed in the supplement.",
     u"Registrations that failed, and the one that produced no result, are not separately listed; the\n"
     u"hash audit below covers all 72.")

# (l) S5 is unreachable from the main text
rep(u"Re-running a chain through\nfurther optimisation rounds at unchanged severity displaces this endpoint by at most 0.036\u00b0, against\n0.586\u00b0 for knee angle at contact,",
    u"Re-running a chain through further optimisation rounds at unchanged severity displaces this endpoint\n"
    u"by at most 0.036\u00b0, against 0.586\u00b0 for knee angle at contact (Supplement S5),")

# ---------------- contradictions
# (n) the knee's chaining displacement does grow with depth
rep(u"and those displacements do not grow with chain depth.",
    u"and the endpoint's displacements do not grow with chain depth, although the knee's do, at roughly\n"
    u"0.15\u00b0 per round, which is why its floor and the endpoint's are not interchangeable.")

# (m) where [28] bites: 4.4's reading is the one the evidence supports
qrep(u"Outside them it is contradicted by [28] and untested.",
     u"Outside them it is untested, and inside them it is contested by [28], whose scope \u00a74.4 states.")

# (o) S7 contradicts itself on whether sidecars were re-baselined
qrep(u"and the hash sidecars were re-baselined, so hash verification cannot detect that breach",
     u"so the provenance block for that analysis cannot match and hash verification cannot detect the\n"
     u"breach from the sidecar alone")

# (p) two statements survive the selection, not one
rep(u"The one statement in this paper\nthat does not depend on the selection is \u00a73.4's, which is a property of all 81 candidates rather\nthan of the winner.",
    u"Two statements in this paper do not depend on the selection: \u00a73.1's count of seven of 81, and\n"
    u"\u00a73.4's displacement asymmetry, which is a property of all 81 candidates rather than of the winner.")

io.open(P, "w", encoding="utf-8", newline="").write(s)
io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("manuscript edits: %d;  supplement edits: %d" % (n[0], n[1]))
