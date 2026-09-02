# -*- coding: utf-8 -*-
"""r541: mechanical contract for MANUSCRIPT_r541.md.

selfcheck_r500.py policed the knee-at-contact manuscript. Its contract locks values that the r541
framing supersedes, so it cannot simply be pointed at the new file. This is its replacement, built
on the same three ideas: a list of load-bearing values that may not silently disappear, a list of
withdrawn values that may not silently reappear, and arithmetic that must hold between values that
are stated separately.

Rule carried from the old file and worth restating: when a guard has to change because a value was
retired, the guard is REPLACED by a ban on the retired value, never deleted. Deleting a guard to let
new text through is the failure this file exists to prevent.
"""
import io, json, os, re, sys

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
MS = os.path.join(PAP, "MANUSCRIPT_r541.md")
S = io.open(MS, encoding="utf-8").read()
# the supplement is part of the submission; a value moved there for length is still deposited,
# so the contract is checked against both files while every other test reads the manuscript alone
SUP = os.path.join(PAP, "SUPPLEMENT_r541.md")
SUPTXT = io.open(SUP, encoding="utf-8").read() if os.path.exists(SUP) else ""
MN = re.sub(r"\s+", " ", S + " " + SUPTXT)
fails, warns, notes = [], [], []


def has(v, why=""):
    if re.sub(r"\s+", " ", v) not in MN:
        fails.append("MISSING: %r %s" % (v, why))


DISCLOSURE = re.compile(
    r"earlier version|earlier draft|is withdrawn|that claim is withdrawn|which is false|"
    r"was false|we had applied|stated that|is retracted|no longer", re.I)


def forbid(pat, why):
    """Scan the manuscript AND the supplement.

    Two design faults are fixed here. Until r561 this scanned only the manuscript, so every retired
    claim could survive in the supplement with the checker reporting no failures. And a bare string
    ban cannot distinguish making a claim from disclosing that an earlier version made it, which
    would force a correction to be hidden rather than stated. A match inside a window that carries
    disclosure language is therefore allowed, and reported so the exemption itself is visible."""
    for lab, txt in (("manuscript", S), ("supplement", SUPTXT)):
        for m in re.finditer(pat, txt):
            a, b = max(0, m.start() - 200), min(len(txt), m.end() + 120)
            if DISCLOSURE.search(txt[a:b]):
                notes.append("disclosure exemption in %s: %r (%s)" % (lab, m.group(0), why[:44]))
                continue
            fails.append("FORBIDDEN in %s: %r found (%s)" % (lab, m.group(0), why))
            break


def near(a, b, tol, why):
    if abs(a - b) > tol:
        fails.append("ARITHMETIC: %s -> %.4f vs %.4f" % (why, a, b))


# ---------------------------------------------------------------- load-bearing values
CONTRACT = [
    # the reported endpoint
    "9.555", "9.125", "0.394", "8.731", "6.265", "76.5", "0.036", "0.082",
    "9.161", "0.430", "9.117", "7.008", "11.226", "4.12", "462", "0.0022", "59 of 59", "61.0",
    # its controls
    "0.033", "0.018", "3.4 per cent", "8.930", "8.654", "0.276", "0.047", "0.5 per cent",
    "0.056", "0.563", "0.4 per cent", "6.302", "9.73",
    # the scan
    "81", "seven of 81", "32.12", "10.66", "9.59", "6.52", "4.36", "4.19", "3.08",
    "5.033", "8.155", "1.492", "5.280",
    # the asymmetry, which is the principal result
    "8.210", "1.449", "−1.000", "4.5 per cent", "−0.964", "0.66", "1.77",
    # motion capture
    "0.995", "0.902", "0.939", "0.672", "0.988", "0.650", "0.512",
    "0.535", "0.537", "0.766", "0.963", "0.227", "0.330",
    # r545: the rectification drift that makes the tone score ordinal rather than absolute
    "0.158", "0.251", "10.3", "1.477", "3.323", "5.260", "8.284", "7.840", "7.431",
    "85 per cent", "1.505", "250 realisations",
    # r544: the non-reflex faller control, and the duration regression stated with its uncertainty
    "9.572", "0.017", "0.47 times", "7.108", "9.512", "9.673", "seventeen", "17.56",
    "0.128", "0.433", "0.102", "0.743", "3 ± 9 per cent", "−7.488",
    "22.7", "38.4", "5.55", "4.20", "4.21",
    # the tone score
    "7.245", "11.381", "4.02", "3.13", "1.086", "1.869", "0.378", "0.803", "4.14",
    # limitations that must not quietly weaken
    "admitted hyperreflexia runs reaches the simulation horizon",
    "all 36 weakness runs do",
    # r541 council round 1: the mixed grid, specified after the cold reader found it unspecified
    "×0.60, ×0.70, ×0.80, ×1.00", "74 pass the same",
    "21 of 21", "11 of 21", "0.49", "1.90", "2.870", "3.95", "ten of the 81",
    "5.82", "7.23", "0.0062", "1.00 by construction", "about 50 limbs", "8.761",
    "0.32", "0.039", "0.30", "0.36", "0.53", "15 to 16", "10.7", "59.5",
    "1.48", "0.95", "0.81", "0.50",
    # r543: the weakness-grading test run on all 81, replacing the untested "no readout" claim
    "three of the 81", "14 to 28", "0.822", "0.900", "0.820", "2.870", "2.208", "2.272",
    "6.308", "6.055", "4.148", "−0.32", "+0.966",
]
for v in CONTRACT:
    has(v, "(load-bearing)")

# ---------------------------------------------------------------- values that must not come back
forbid(r"0\.542|0\.745|0\.672\u00b0", "Cawood JATS-XML mis-extraction; see CAWOOD_CORRECTION_r450")
forbid(r"6\.34|7\.62", "Geiger MDC values, never verified against the source")
forbid(r"54[\u2013-]76%", "Zeni event-detection rate, contradicted by the source's own figures")
forbid(r"7\.25|3\.163|change threshold for this|below the .{0,20}change threshold",
       "minimal detectable change, retired at r523 in favour of the discriminability of section 3.5")
forbid(r"most dose-symmetric", "DOSE_r174 registers x0.892 as the match, not x0.80")
forbid(r"MMT 4\+", "the MMT mapping is an inference, not a measurement")
forbid(r"nothing\s+published for swing dorsiflexion", "false: Kesar reports 4.9 deg")
# r541 additions: claims made and withdrawn during the endpoint pivot
forbid(r"32\.5:1|specificity of 32\.5",
       "the additive model's weakness coefficient is near zero only because the effect reverses "
       "sign; the defensible worst-case ratio is 1.11:1 (SWINGSPEC_r529)")
forbid(r"immune to weakness|insensitive to weakness depth",
       "the weakness slope reverses sign rather than vanishing; say the endpoint does not RECOVER "
       "weakness, not that it is immune to it")
forbid(r"escapes? (the )?survival|independent of cells dying",
       "ARMSURV_r538: no hyperreflexia family survives intact, so no readout escapes the confound")
forbid(r"weakness arm sits on control|not displaced from control",
       "the weakness arm is displaced 0.430 deg, 12x this endpoint's artefact floor; the issue is "
       "the SIGN, not the magnitude")
forbid(r"no readout (and no combination )?(recovers|grades) (how weak|dorsiflexor weakness)(?!.{0,120}both lesions)",
       "GRADEALL_r543: three of 81 candidates grade weakness usably in the pure arm. The null is "
       "specific to the mixed grid, where both lesions are present, and must be stated that way")
forbid(r"0\.801|0\.734|0\.736|0\.724(?!.{0,40}chance)",
       "the pre-r544 detect-isolated-weakness column, produced by a threshold fitted on the cells "
       "it scored; the held-out values are 0.51 to 0.65")
forbid(r"(?<!not )(?<!ordinal and not )absolute tone score|(?<!not )places a patient on (that|the) (ladder|series)",
       "DRIFT_r545: rectification moves T by up to 1.505 deg, more than three of the four rung "
       "gaps. The score is ordinal; it does not place a patient on the ladder")
forbid(r"first to (simulate|vary|grade)",
       "the method is not new: [10] is the template and [9] already graded a spindle gain")

# --- round four (r548-r552): claims retired after the cold-read council
forbid(r"only two of the 81 variables|published between-session errors exist for only two|legible across a third of the sagittal",
       "false against ref [15]: Kesar Table 2 publishes five, four of them members of the 81; "
       "see BAR_r548")
forbid(r"44 of the 55|force ratio was 0\.84|r = −0\.11, p = 0\.408",
       "not present in the retrieved source for [28], which is the abstract only")
forbid(r"and we did not test one",
       "pair_r533 tested a two-stage estimator: R2 0.95 then 0.13; only the sign-appropriate "
       "variant is untested")
forbid(r"falls to near chance on all of them",
       "the two detection columns are sensitivities with no specificity term; chance is undefined")
forbid(r"are not among the candidates put through this noise model",
       "WEAKNOISE_r546 puts all three through it; none survives at 3 deg")
forbid(r"by more than that candidate.s own noise",
       "sweep_r532.py codes twice the seed SD; the 1x reading gives 14 candidates, not 7")
forbid(r"(written|legible) in an eighth as many|\b25 grade the reflex|three grade dorsiflexor weakness",
       "BARTIE_r550: the ratio spans 3.7 to 14.0 over bar and rank convention")
forbid(r"no pair falls within one seed SD",
       "withdrawn: AUDIT_r554 finds 4 pairs below the grid floor, all same-gain; closest 0.044 deg")

# ---------------------------------------------------------------- arithmetic
near(6.2651 / 0.0819, 76.50, 0.6, "cell gap / seed SD = 76.5")
near(6.2651 / 0.0358, 175.0, 2.0, "cell gap / artefact floor = 175")
near(9.5552 - 0.3940, 9.1612, 0.002, "control - hyperreflexia = 9.161")
near(9.5552 - 9.1251, 0.4301, 0.002, "control - weakness = 0.430")
near(9.1251 - 0.3940, 8.7311, 0.002, "arm difference = 8.731")
near(9.161 / 0.430, 21.3, 0.6, "the 21-fold ratio between the two displacements")
near(0.298 / 8.731, 0.0341, 0.002, "duration regression = 3.4 per cent as a point estimate")
near(0.743 / 8.731, 0.0851, 0.003, "one SE of that slope is 9 per cent of the effect")
near(9.572 - 9.5552, 0.0168, 0.002, "the fallers sit +0.017 deg from control")
near(0.0168 / 0.0358, 0.47, 0.03, "which is 0.47 x the artefact floor")
near(0.276 / 8.731, 0.0316, 0.003, "stationarity spread = 3 per cent of the window mean")
near(0.047 / 8.731, 0.0054, 0.002, "unlesioned side = 0.5 per cent")
near(0.032 / 8.731, 0.0037, 0.002, "speed control = 0.4 per cent")
near(11.381 - 7.245, 4.136, 0.01, "tone series span = 4.14 deg")
near(4.136 / 1.768, 2.34, 0.05, "the series is 2.3 measurement errors wide")
near((11.249 + 6.985) / 2, 9.117, 0.01, "the Welch interval is centred on 9.117")

# ---------------------------------------------------------------- reference integrity
refs = re.findall(r"^(\d+)\.\s+(.+?)$", S[S.index("## References"):], re.M)
n = len(refs)
if n != 28:
    fails.append("REFERENCES: %d entries, expected 28" % n)
for num, txt in refs:
    if "doi:" not in txt.lower() and "PMID" not in txt:
        fails.append("REFERENCE %s carries neither DOI nor PMID" % num)
body = S[:S.index("## References")]
cited = set(int(x) for x in re.findall(r"\[(\d+)(?:,\s*\d+)*\]", body))
for m in re.finditer(r"\[([\d,\s]+)\]", body):
    for x in m.group(1).split(","):
        if x.strip().isdigit():
            cited.add(int(x.strip()))
orphans = sorted(set(range(1, n + 1)) - cited)
if orphans:
    warns.append("references never cited in the body: %s" % orphans)
over = sorted(x for x in cited if x > n)
if over:
    fails.append("citations to nonexistent references: %s" % over)

# ---------------------------------------------------------------- cross-references and figures
for m in re.finditer(r"\u00a7(\d+(?:\.\d+)?)", body):
    t = m.group(1)
    if not re.search(r"^#{2,3} %s\b" % re.escape(t), S, re.M):
        fails.append("dangling cross-reference to section %s" % t)
figdir = os.path.join(PAP, "figures")
pngs = sorted(f for f in os.listdir(figdir) if f.endswith(".png")) if os.path.isdir(figdir) else []
called = sorted(set(re.findall(r"Fig\. (\d)", body)))
caps = re.findall(r"\*\*Fig\. (\d)\*\*", S)
if called != sorted(set(caps)):
    fails.append("figure callouts %s do not match captions %s" % (called, sorted(set(caps))))
if called and called != [str(i) for i in range(1, len(called) + 1)]:
    fails.append("figure callouts are not in ascending order: %s" % called)

# ---------------------------------------------------------------- containers exist
for c in ("SWEEP_r532", "GATES_r534", "SWINGFULL_r530", "SWINGDF_r525", "MIXEDSWING_r526",
          "SWINGSPEC_r529", "PAIR_r533", "CLAIMS_r537", "INDEX_r536", "ARMSURV_r538",
          "ANKLESHAPE_r539"):
    if not os.path.exists(os.path.join(PAP, c + ".json")):
        fails.append("MISSING CONTAINER: %s.json" % c)

# ---------------------------------------------------------------- report
w = len(body[body.index("## 1. Background"):].split())
a = S[S.index("## Abstract"):S.index("## 1. Background")]
print("manuscript: %d chars, ~%d body words, abstract %d words" % (len(S), w, len(a.split())))
print("figures on disk: %d  (%s)" % (len(pngs), ", ".join(pngs)))
ab = len(a.replace("## Abstract", "").split()) - 16   # less the keywords line
if ab > 350:
    warns.append("abstract is %d words; JNER's limit is 350" % ab)
# JNER publishes no word limit for research articles. The comparison is three JNER papers in this
# reference list, which run 7,916 / 9,468 / 11,747 body words -- a sample of three, not a rule.
if w > 12000:
    warns.append("body is %d words, beyond the longest JNER article in this reference list "
                 "(11,747); consider moving material to the supplement" % w)
print()
for f in fails:
    print("  FAIL  %s" % f)
for x in warns:
    print("  warn  %s" % x)
for x in notes:
    print("  note  %s" % x)
print("\n=== %d failures, %d warnings, %d disclosure exemptions ===" % (len(fails), len(warns), len(notes)))
sys.exit(1 if fails else 0)
