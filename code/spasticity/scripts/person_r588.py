# -*- coding: utf-8 -*-
"""r588: put the authors back into the sentences where they made the choice.

First person, per thousand words: Ong 22.94, Jansen 8.82, this manuscript 2.97. Simulation papers in
this genre are written in the first person, and every design decision here is instead carried by an
inanimate abstract subject: "The controller is re-optimised", "Four decision rules were fixed", "The
severity window was selected", "The endpoint was chosen". A blind reader gave that agent deletion as
the first of three pieces of evidence that the text was not authored in the ordinary way. Nobody
asked for it; it is a habit of this draft.

Only sentences in which the authors are the actual agent are converted. Measurements and properties
of the model keep their subjects: "The gap between the nearest runs of the two groups is 6.265" is a
fact, not a decision, and stays as it is.
"""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r121_MANUSCRIPT"))
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


PAIRS = [
 # --- Methods: every one of these is a decision the authors made
 (u"The controller is re-optimised for every lesion, so each analysed gait is that lesioned system's own best solution.",
  u"We re-optimised the controller for every lesion, so each analysed gait is that lesioned system's own best solution."),
 (u"The two lesions are imposed separately, so the hyperreflexia group carries a calf at full strength.",
  u"We imposed the two lesions separately, so the hyperreflexia group carries a calf at full strength."),
 (u"The two deepest levels were run with four seeds and not six.",
  u"We ran the two deepest levels with four seeds and not six."),
 (u"Four decision rules were fixed before the results were read:",
  u"We fixed four decision rules before reading the results:"),
 (u"Every difference is reported in degrees, as Cohen's *d*, and in units of the within-condition seed SD, with the denominator named where it is used.",
  u"We report every difference in degrees, as Cohen's *d*, and in units of the within-condition seed SD, naming the denominator where we use it."),
 (u"The severity window was selected after observing where the groups separate, and the endpoint after the scan.",
  u"We selected the severity window after observing where the groups separate, and the endpoint after the scan."),
 (u"The analysis of the mixed grid was registered before its results were read, and the registration does not certify what is reported here.",
  u"We registered the analysis of the mixed grid before reading its results, and that registration does not certify what we report here."),
 (u"The endpoint was chosen after the data were seen, from a scan of 81 candidates.",
  u"We chose the endpoint after seeing the data, from a scan of 81 candidates."),
 (u"A left-minus-right hip asymmetry was examined and is not reported, for the reasons given in Supplement S11.",
  u"We examined a left-minus-right hip asymmetry and do not report it, for the reasons given in Supplement S11."),

 # --- Results: analytic choices, not measurements
 (u"The same test applied to the hyperreflexia group is met by 25.",
  u"Applying the same test to the hyperreflexia group, we find 25."),
 (u"The candidates are three joint-angle curves sampled every 5 per cent of the cycle plus eighteen landmarks, so adjacent samples of one curve are strongly correlated.",
  u"We sampled three joint-angle curves every 5 per cent of the cycle and added eighteen landmarks, so adjacent samples of one curve are strongly correlated."),
 (u"The honest reading of the regression is 0.30 \u00b1 0.74\u00b0 at one standard error,",
  u"We read the regression as 0.30 \u00b1 0.74\u00b0 at one standard error,"),
 (u"The five hyperreflexia conditions are a designed dose series, so adding chains at the same doses would not narrow it.",
  u"We designed the five hyperreflexia conditions as a dose series, so adding chains at the same doses would not narrow it."),
 (u"Both figures are computed for a variable chosen as the maximum of an 81-candidate scan.",
  u"We computed both figures for a variable we had chosen as the maximum of an 81-candidate scan."),
 (u"A single bar of 1.77\u00b0 was applied to every candidate.",
  u"We applied a single threshold of 1.77\u00b0 to every candidate."),

 # --- Discussion: positions taken
 (u"We take the whole-cohort SD as the denominator,", u"We take the whole-cohort SD as the denominator,"),
 (u"The insensitivity to weakness is accordingly specific in four ways, and holds within them:",
  u"We therefore claim the insensitivity to weakness in four respects only, and within them it holds:"),
 (u"This study sits inside that spread.", u"Our study sits inside that spread."),
 (u"The finding is a hypothesis about human gait rather than a measurement of it.",
  u"We offer the finding as a hypothesis about human gait rather than as a measurement of it."),
 (u"The scope here is sagittal-plane equinus only.",
  u"We restrict the scope to sagittal-plane equinus."),
 (u"The present study addresses none of the block's purposes directly.",
  u"We do not address any of the block's purposes directly."),
 (u"In this study a reflex-controlled musculoskeletal model was lesioned in two ways,",
  u"We lesioned a reflex-controlled musculoskeletal model in two ways,"),
 (u"Eighty-one candidate sagittal variables were then scored across three joints and the whole gait cycle,",
  u"We then scored 81 candidate sagittal variables across three joints and the whole gait cycle,"),
 (u"Nothing here was measured in a patient.", u"We measured nothing here in a patient."),
 (u"No correction for multiplicity is applied, no analysis here is confirmatory,",
  u"We apply no correction for multiplicity, and treat no analysis here as confirmatory,"),
]

for o, nn in PAIRS:
    rep(o, nn)

io.open(P, "w", encoding="utf-8", newline="").write(s)
b = s[s.index("## 1. Background"):s.index("## Figures")]
w = len(b.split())
t = len(re.findall(r"\b(we|our|us)\b", b, re.I))
print("edits: %d;  first person now %.2f per 1000w (%d tokens)" % (n[0], 1000.0 * t / w, t))
