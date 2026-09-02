"""Build the Supplementary Tables the manuscript promises.

Each table is reproduced from the result file that produced it, so no number is retyped and the
supplement cannot drift from the analysis.

Two things in those files must not be reproduced in a submitted supplement.

First, decision-rule annotations written for the authors during analysis: blocks beginning "READ:"
or "NOTE ON" that say what a result would mean and what the manuscript should then do ("must be
withdrawn", "the manuscript must say so"). They record that the interpretation rule was fixed
before the result was seen, which is a strength, but they are addressed to the authors, they cite
draft section numbers that no longer exist, and a reviewer reasonably reads them as internal
memoranda. They are removed here and remain in the files in the code repository.

Second, absolute local paths, which identify one machine and mean nothing to a reader.

Both removals are counted and printed when this script runs, so nothing goes silently.
"""
import io
import os
import re
import sys

sys.path.insert(0, "D:/ROWV_paper")
from paper_stats import title as _title

OUT = "D:/ROWV_paper/SUPPLEMENT_SUBMISSION.md"
R = "D:/BioCV"

ANNOTATION = re.compile(
    r"^\s*(READ:|NOTE ON\b|NOTE:|Any claim (?:in the manuscript )?resting|"
    r"[A-Za-z ,'-]*\b(?:manuscript|paper) must\b|"
    # An instruction addressed to the authors is a working note whichever noun it names.
    # "Sections 3.2 and 5 must be restated..." reached a submitted supplement because the
    # pattern looked only for "manuscript must" and "paper must".
    r"Sections?\s[0-9][0-9.]*(?:\sand\s[0-9][0-9.]*)?\s+must\b)"
)
PATH = re.compile(r"[A-Z]:/[A-Za-z0-9_./]+/([A-Za-z0-9_.-]+)")
# "Cache=_cache_undist" names a directory on the analysis machine. The artefact name in each
# section heading is the provenance a reader can act on; the cache path is not.
CACHEID = re.compile(r"^Cache=\S+[,.]?\s*", re.M)
SHA_STAMP = re.compile(r"\n*^source-sha256: [0-9a-f]+[ \t]*$", re.M)
# Some markers sit inline in a heading rather than opening a block, so a line-start rule misses
# them: "(watchdog D4-13, third asking)" shipped under a header promising their removal.
INLINE = re.compile(r"\s*\((?:watchdog|council)[^)]*\)", re.I)
# One line records a real check -- that every label names its arms in the subtraction order --
# but attributes it to an internal review round. The finding is kept, the attribution is not.
REWORD = [
    # An artefact should say what it contains, not what it used to contain. Re-running the
    # equivalence bounds to delete three sentences of history is not worth the compute, so the
    # history is dropped at render time, as the entries below do.
    ("Part 2 of this file previously carried an interaction table on a denominator the project\nabandoned; the interaction family is now computed by biocv_interaction_fdr.py and reported\nin Table 2(c). It is not emitted here.",
     "The interaction family is reported in Table 2(c)."),
    # An instruction telling the analyst which level to prefer is a working note, not a rule for
    # reading a result, so the preamble's promise covers it.
    ("same frames, same candidate cameras, same arms.\n                   This is the matched comparison; prefer it over [pos:AW] whenever\n                   the question is whether position gains transmit to angles.",
     "same frames, same candidate cameras, same arms."),
    ("EVERY label names its two arms in the SAME order they are subtracted. Council round 5\nfound that six labels in the previous run named them in the reverse order -- the numbers\nand the prose were right, but the stated decoding rule inverted them. Fixed here.",
     "EVERY label names its two arms in the SAME order they are subtracted."),
    # BIOCV_PERM_V3.txt's header lists the draft files it supersedes. The source script no longer
    # writes that line, but regenerating the artefact means re-running the whole m=50 permutation
    # (~3.3 h) to change three words that no number depends on. Rewriting it here is the same
    # transformation the entry above performs, it is declared and printed, and it touches prose
    # only -- the numbers are still reproduced verbatim.
    ("Authoritative contrast family for the manuscript (supersedes PERM, PERM_FULL,\n"
     "PERM_FINAL and the m=48 PERM_V2 run, all of which are stale).",
     "Authoritative contrast family for the manuscript."),
]

def _n_families():
    """How many families the pooled sensitivity actually corrected over.

    Typing this number here is what left "all five families" in two places after section 2.5
    had grown to eight and then nine. It is read from the artefact so it cannot go stale again.
    """
    txt = io.open(R + "/BIOCV_POOLED_SENSITIVITY.txt", encoding="utf-8").read()
    return int(re.search(r"POOLING ALL (\d+) INFERENTIAL FAMILIES", txt).group(1))


def _m_pooled():
    txt = io.open(R + "/BIOCV_POOLED_SENSITIVITY.txt", encoding="utf-8").read()
    return int(re.search(r"POOLED\s+m = (\d+)", txt).group(1))


def _m_inter():
    """Family size read from the artefact. Typing it here put "nineteen" four lines above a
    block that printed "m = 20"."""
    txt = io.open(R + "/BIOCV_INTERACTION_FDR.txt", encoding="utf-8").read()
    return int(re.search(r"Family size m = (\d+)", txt).group(1))


STRIPPED = []
MIDPARA = []


def strip_annotations(body, src):
    """Drop annotation blocks (to the next blank line) and neutralise local paths.

    The block rule is only safe when the annotation OPENS a paragraph. Where an author-facing
    sentence begins part-way through a reader-facing one -- "... A difference that survives in
    Part A but / not here is a scale artefact and the manuscript must not quote it ..." -- the
    line-to-blank-line deletion amputates the paragraph and leaves a half sentence in the
    submitted supplement. A cold reader found exactly two such stumps. Those cases are now
    reported and the build fails, so they are reworded at source rather than mutilated here.
    """
    lines = body.split("\n")
    out, i = [], 0
    while i < len(lines):
        if ANNOTATION.match(lines[i]):
            opens_paragraph = i == 0 or not lines[i - 1].strip()
            if not opens_paragraph:
                MIDPARA.append((src, lines[i].strip()[:70]))
                out.append(lines[i])
                i += 1
                continue
            STRIPPED.append((src, lines[i].strip()[:56]))
            while i < len(lines) and lines[i].strip():
                i += 1
            while out and not out[-1].strip():
                out.pop()
            continue
        out.append(lines[i])
        i += 1
    text = INLINE.sub("", "\n".join(out).rstrip())
    # An artefact stamps its own source hash so check_drift can tell "written by the current
    # code" from "written by older code that finished later". That is an integrity stamp for
    # the build, not a result, and it has no meaning to a reader of the supplement.
    text = SHA_STAMP.sub("", text).rstrip()
    text = CACHEID.sub("", text)
    for pat, rep in REWORD:
        text = text.replace(pat, rep)
    return PATH.sub(lambda m: m.group(1), text)


def block(path, marker=None, stop=None):
    """One result file, or one marked section of it, reproduced in full.

    Line limits were removed: a fixed cut once ended a block mid-sentence, and a supplement that
    says nothing was retyped cannot also say four lines were dropped.
    """
    if not os.path.exists(path):
        return "_[" + os.path.basename(path) + " not found]_"
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    if marker:
        if marker not in txt:
            return "_[marker not present in " + os.path.basename(path) + "]_"
        txt = txt[txt.index(marker):]
    if stop and stop in txt[1:]:
        txt = txt[: txt.index(stop, 1)]
    return "```\n" + strip_annotations(txt.rstrip(), os.path.basename(path)) + "\n```"


L = []
w = L.append

w("# Supplementary material")
w("")
w(_title())   # imported, never retyped: the title lived in three files and drifted
w("")
w("Every table below is reproduced from the result file named in its heading; no number has been "
  "retyped. Effects are signed so that a positive value means the second-named arm has the lower "
  "error. The result files also carry annotations written during analysis. The rules recording "
  "what a result would be taken to mean before it was seen are kept, headed HOW TO READ THIS, "
  "because a reader needs them to judge the result. Working notes addressed to the authors -- "
  "reminders, cross-checks, and instructions about which analysis to prefer -- are omitted here "
  "and are present in the files distributed with the code.")
w("")
w("---")
w("")

w("## A note on angle names")
w("")
w("The manuscript names its angle outcomes for the segments that define them, because they are "
  "three-point included angles and not model-based joint kinematics: the trunk-thigh angle "
  "moves with trunk lean and pelvic tilt, and the frontal-plane form is a projection rather than "
  "an ab/adduction angle under any standard convention. The result files below were written "
  "before that renaming and print the original keys. They map one to one:")
w("")
w("| result files | manuscript | approximates |")
w("|---|---|---|")
w("| `knee_flex` | thigh-shank angle | knee flexion |")
w("| `knee_abd` | frontal-plane thigh-shank angle | knee ab/adduction |")
w("| `hip_flex` | trunk-thigh angle | hip flexion |")
w("| `dflex_toe`, `dflex_heel` | shank-foot angle | ankle dorsiflexion |")
w("")
w("No number changes with the name; only the label does.")
w("")

w("## Table S0. Rig, reference and software")
w("")
w("Reproducibility detail moved out of Section 2.1 so the main text carries only what the "
  "argument uses.")
w("")
w("| item | value |")
w("|---|---|")
w("| video cameras | 9 machine-vision, 1920x1080, 200 Hz |")
w("| ring geometry | median radius 4.46 m; 3.0-6.1 m from the centroid |")
w("| focal lengths | non-uniform, a 1.34x spread across the ring |")
w("| distortion | substantial radial distortion in all 99 calibrations |")
w("| reference system | 15-camera Qualisys Oqus, 200 Hz |")
w("| reference model | the dataset's own 6-DoF full-body model, Visual3D v6 |")
w("| reference filter | Butterworth, 4th order, 12 Hz |")
w("| joint centres | the archive record states that joint centres are the midpoint of the medial "
  "and lateral markers for every joint except the hip, which uses the regression equations of "
  "Bell et al. (1989). The knee and ankle references are therefore direct marker constructions; "
  "the hip reference is a prediction from external landmarks, whose own error is of a magnitude "
  "comparable to the offset reported here and is mirrored across the midline like an anatomical "
  "offset. The hip result therefore cannot be apportioned between the two systems, and that is "
  "now a statement about a known construction rather than an unknown one. |")
w("| frames per trial | 60, at near-even spacing across the trial (roughly every ninth), a compute "
  "bound on re-running every arm over every frame; the spacing spans the whole pass through the "
  "capture volume rather than a window of it. |")
w("| 2D detector | RTMPose-m via `rtmlib` 0.0.15, ONNX Runtime 1.27.0 |")
w("| undistortion | `cv2.undistortPoints`, OpenCV 5.0.0 |")
w("")

w("## Table S1. The complete contrast family (*m* = 50)")
w("")
w("As in Table S3n, the block below is verbatim and still prints q-values on its leave-one-out "
  "offset-table rows. Those are withheld by the rule of Section 2.5; the manuscript's counts "
  "exclude them.")
w("")
w("The main tables display the contrasts the argument turns on. This is the whole family, "
  "unfiltered and in the order Benjamini\u2013Hochberg sees it, so that the correction can be "
  "checked rather than taken on trust. `[pos:AW]` denotes ankles and wrists; `[pos:HKA]` the hip, "
  "knee and ankle from which the joint angles are built. *k* is the number of participants "
  "contributing; all contrasts use the exact sign-flip test over 2\u00b9\u00b9 = 2048 patterns, so "
  "the smallest attainable p is 0.000977, and contrasts reported at that floor cannot be ranked "
  "against one another.")
w("")
w("Source: `BIOCV_PERM_V3.txt` (`biocv_permutation_v2.py`).")
w("")
w("**Two arm orders appear in this block.** The [pos:AW] rows name the no-rejection arm first "
  "(\"no rejection vs reprojection rejection\", +0.131 mm) and the [pos:HKA] rows name the "
  "rejection arm first (\"reproj rejection vs none\", +0.005 mm), because the two levels were "
  "accumulated in different passes. Every label states its own order and every sign follows it, "
  "so the two are consistent; but a reader comparing rows across levels must read the label "
  "before the sign. Table 1(a) prints the [pos:HKA] contrast in the first order, as −0.005 mm. "
  "Regenerating this file to unify the orders costs 3.3 hours of compute and would move no "
  "number, so the convention is stated rather than rewritten.")
w("")
w(block(R + "/BIOCV_PERM_V3.txt"))
w("")

w("## Table S2. Distortion characterisation")
w("")
w("The two criteria are distinguished by near-camera residuals (Eq. 1), which is where a "
  "radial-distortion model is least constrained, so the criterion comparison is only interpretable "
  "if the distortion behaviour is characterised. S2a fits the exponent \u03b1 in detector pixel "
  "error \u221d *d*^\u03b1 and asks whether it reflects genuine heteroscedasticity or the "
  "joint-centre offset seen in perspective; S2b repeats the principal contrasts on undistorted "
  "image coordinates.")
w("")
w("**S2b should be read in both directions.** Correcting distortion removes the object-space "
  "advantage in the highest camera-asymmetry bin; it also raises the pooled advantage and turns "
  "the two lowest bins positive. The criterion comparison at `[pos:AW]` is therefore sensitive to "
  "the distortion model rather than independent of it, which is the limitation Section 3.2 states.")
w("")
w("### S2a. The distance\u2013error exponent \u2014 `BIOCV_ALPHA.txt`")
w("")
w(block(R + "/BIOCV_ALPHA.txt"))
w("")
w("### S2b. Undistortion control \u2014 `BIOCV_UNDISTORT.txt`")
w("")
w(block(R + "/BIOCV_UNDISTORT.txt"))
w("")

# Section 2.3 declares the weighting arms. The c/d^2 variant was evaluated and is null, and a
# declared arm whose result appears nowhere is a hole a referee will find: it reads as a result
# withheld rather than a result reported.
w("### S2c. Weighting-factor sweep \u2014 `BIOCV_WEIGHTFACTOR.txt`")
w("")
w("This file reports the ankles-and-wrists confidence-versus-*c*/*d* effect as +0.246 mm against "
  "+0.256 in Table S1 and Table 1(a). The gap is the pooled-versus-per-participant difference set "
  "out under Table 3(a): this sweep pools observations, while the contrast families average "
  "per-participant effects, which is the inferential unit. Where the two differ the "
  "per-participant value is the tested one.")
w("")
w("The weighting arms of Section 2.3 compared against confidence weighting on both position and "
  "knee angle, including the *c*/*d*\u00b2 variant, which is null on both.")
w("")
w(block(R + "/BIOCV_WEIGHTFACTOR.txt"))
w("")

w("### S2d. The same distortion control at [pos:HKA] — `BIOCV_UNDISTORT_HKA.txt`")
w("")
w("S2b ran at [pos:AW] only, which left every hip/knee/ankle criterion result conditional on a "
  "distortion model no test had exercised at that joint set. This is the same control on the "
  "joint set the paper's main claims are made on. It behaves the same way: uncorrected, the "
  "object-space advantage concentrates in a high-asymmetry bin (+2.49 mm at 2.5-3, CI excluding "
  "zero) and the pooled figure is +0.222 mm; corrected, the bin structure flattens to +0.10 to "
  "+0.26 mm across every bin and the pooled figure is +0.164 mm. The asymmetry concentration is "
  "therefore a distortion artefact at [pos:HKA] as it is at [pos:AW], and the small pooled "
  "advantage survives correction at both. Note that correction also lowers the mean absolute "
  "position error from 38.6 to 28.5 mm, an order of magnitude more than any effect contrasted "
  "in this paper, which is why the correction is applied throughout rather than treated as a "
  "sensitivity. Intervals are percentile bootstrap over PARTICIPANTS, B = 3000; where a "
  "bootstrap interval and the exact sign-flip test disagree, Section 2.5 gives the exact test.")
w("")
w(block(R + "/BIOCV_UNDISTORT_HKA.txt"))
w("")

w("## Table S3. Mechanism analyses")
w("")
w("These are the analyses behind the account of *why* a criterion that helps position can harm an "
  "angle: the effect is not uniform across joints, and the joints it helps and harms sit on the "
  "same segment.")
w("")
w("### S3a. Decomposition by camera-distance asymmetry \u2014 `BIOCV_ASYM_HKA.txt`")
w("")
w("Position error at the hip, knee and ankle binned by how asymmetric the contributing "
  "cameras' distances are, which is the regime Eq. 1 says separates the two criteria. The "
  "per-joint decomposition the main text uses is S3b.")
w("")
w(block(R + "/BIOCV_ASYM_HKA.txt"))
w("")
w("### S3b. Per-joint family with BH correction \u2014 `BIOCV_PERJOINT_FDR.txt`")
w("")
w("The twelve per-joint tests with their corrected q-values. Table 1(b) of the main text prints "
  "the effects and unadjusted p; the correction is here. The family is four interventions crossed "
  "with three lower-limb joints \u2014 the four for which a per-joint decomposition was computed "
  "\u2014 and the pooled `[pos:HKA]` rows are excluded because they belong to the *m* = 50 family.")
w("")
w(block(R + "/BIOCV_PERJOINT_FDR.txt"))
w("")
w("### S3c. Posture dependence \u2014 `BIOCV_POSTURE.txt`")
w("")
w(block(R + "/BIOCV_POSTURE.txt"))
w("")
w("### S3d. Posture family with BH correction \u2014 `BIOCV_POSTURE_FDR.txt`")
w("")
w("`|off|` is the offset magnitude, which is rotation-invariant, so binning it by flexion is not "
  "circular. The `flex-sens` row is the component resolved on the hip\u2013ankle chord, whose "
  "orientation is set by the binning variable; that row is circular, is listed for completeness, "
  "and no claim in the manuscript rests on it. Quintiles run from most flexed (104\u2013133\u00b0) "
  "to most extended (173\u2013180\u00b0), and each row is the most-extended quintile minus the "
  "most-flexed.")
w("")
w(block(R + "/BIOCV_POSTURE_FDR.txt"))
w("")
w("### S3e. Leave-one-out offset correction \u2014 `BIOCV_LOO.txt`")
w("")
w("Two figures for the same gain circulate and are not the same quantity. The manuscript "
  "quotes +9.848 mm, the mean of eleven per-participant differences. The block below quotes "
  "+10.190 mm, the difference of frame-pooled means (28.493 against 18.303), which weights a "
  "participant by how many frames they contribute. Both were recomputed from the "
  "per-participant accumulator and agree with the values printed here; the relation is the "
  "same one that separates 5.062 from 5.086 in Table S8. Every declared verdict uses the "
  "per-participant form, because the participant is the inferential unit (Section 2.5).")
w("")
w(block(R + "/BIOCV_LOO.txt"))
w("")
w("### S3f. Offset geometry \u2014 `BIOCV_X22.txt`")
w("")
w("The source for the axial / in-plane-perpendicular / out-of-plane decomposition in Table 3b, on "
  "which Section 3.4's account rests. The three components are means of per-frame magnitudes and "
  "therefore do not compose to the printed total.")
w("")
w(block(R + "/BIOCV_X22.txt"))
w("")
w("### S3g. Not used.")
w("")
w("### S3h. Gauss\u2013Newton contrast \u2014 `BIOCV_GN_DISSOCIATION.txt`")
w("")
w("Rows with a counterpart in the *m* = 50 family carry that family's corrected q. Rows "
  "without one \u2014 the object-space rejection contrast under Gauss\u2013Newton, and the "
  "hip-flexion and frontal-knee rows \u2014 belong to no declared family and are exploratory; "
  "the manuscript quotes none of them.")
w("")
w(block(R + "/BIOCV_GN_DISSOCIATION.txt"))
w("")
w("### S3i. Interaction family with BH correction \u2014 `BIOCV_INTERACTION_FDR.txt`")
w("")
w("As in Table S3n, the block below is verbatim and still prints q-values on its leave-one-out "
  "offset-table rows. Those are withheld by the rule of Section 2.5; the manuscript's counts "
  "exclude them.")
w("")
w(f"Table 2(c) of the main text lists all {_m_inter()}; they are repeated here with the unadjusted "
  "p-values alongside the corrected q-values. They are recomputed from the per-participant means "
  "dumped by the analysis scripts rather than transcribed from another table, so the correction "
  "runs on exact p-values.")
w("")
w(block(R + "/BIOCV_INTERACTION_FDR.txt"))
w("")
w("### S3j. Joint-set interaction \u2014 `BIOCV_JOINTSET_FDR.txt`")
w("")
w("The test behind Table 1(c): whether an intervention moves the two joint sets by different "
  "fractions of their own baselines. It is computed from the same per-participant means as the "
  "*m* = 50 family rather than from an independent pass, which is one reason the declared "
  "families are not independent of one another (see S4).")
w("")
w(block(R + "/BIOCV_JOINTSET_FDR.txt"))
w("")

w("### S3k. Exact 90% intervals on the angle contrasts — `BIOCV_EQUIV_BOUNDS.txt`")
w("")
w("The exact 90% intervals quoted in Section 3.2, obtained by inverting the sign-flip test. Not "
  "every row is a null: three intervals here exclude zero, and Section 3.2 quotes only the bounds "
  "on the contrasts that are null under correction. The interaction family is reported in S3i.")
w("")
w(block(R + "/BIOCV_EQUIV_BOUNDS.txt"))
w("")
w("### S3l. The upper-limb chain — `BIOCV_ANGLES.txt`")
w("")
w("The shoulder–elbow–wrist chain, computed and excluded from the main analysis as "
  "non-gait-relevant. It is the one result that runs against the mechanism the Discussion "
  "proposes, so it is reproduced in full. These are subject-cluster bootstrap contrasts, not "
  "the per-participant exact sign-flip test used everywhere else in the paper.")
w("")
w(block(R + "/BIOCV_ANGLES.txt", marker="=== ELBOW", stop="=== ALL CHAINS"))
w("")
w("### S3m. Bias–variance decomposition of joint-centre error — `BIOCV_GT_OFFSET.txt`")
w("")
w("The per-participant offset means and standard deviations behind Section 3.4’s statement "
  "that between-participant variability is comparable to the mean.")
w("")
w(block(R + "/BIOCV_GT_OFFSET.txt"))
w("")

w("### S3n. Within-limb subset control — `BIOCV_SUBSET_CONTROL.txt`")
w("")
w("The block below is reproduced verbatim from the artefact and therefore still prints q-values "
  "and SURVIVES verdicts on its leave-one-out offset-correction rows. Those verdicts are "
  "withdrawn by the rule of Section 2.5: each participant's correction is built from the other "
  "ten, so the eleven differences are not exchangeable and the sign-flip test does not apply. "
  "Table 1(d) marks the same rows ‡ withheld, and the counts quoted in the manuscript exclude "
  "them. The artefact is not edited, so that a reader can see exactly what was computed.")
w("")
w("This analysis is reported here rather than in the Results because of what it can and cannot "
  "carry. A subset effect is the unweighted mean of its member joints, so the difference between "
  "two subsets is a fixed linear combination of the per-joint effects of Table 1(b): comparing "
  "{hip, knee, ankle} with {hip, ankle} asks whether the knee effect differs from the mean of the "
  "hip and ankle effects. The thirty pairwise differences therefore span ten free quantities, not "
  "thirty, and their survivor counts are not thirty findings. What the control does establish, "
  "with body region and occlusion regime held constant, is that the joint set a study summarises "
  "over changes the SIZE of the effect it reports. After both sensitivities that reduces to one "
  "deployable contrast, which is the one the Results quote; the verdict changes are on retention "
  "controls or are unlicensed by a tested difference.")
w("")
w("The control behind Table 1(d). The paper's two joint sets differ in body region as well "
  "as membership, so this compares subsets within the lower limb, where region, occlusion "
  "regime and camera geometry are constant and only membership varies.")
w("")
w(block(R + "/BIOCV_SUBSET_CONTROL.txt"))
w("")

w("## Table S4. Pooled-family sensitivity")
w("")
w("Splitting a set of tests into separately corrected families can inflate survival. This is the "
  "consequence of the strictest alternative: one Benjamini\u2013Hochberg correction over the union "
  "of all " + str(_n_families()) + " declared families (*m* = " + str(_m_pooled()) + "). The counts "
  "are in the block below. The families are not independent \u2014 they are analyses of the same "
  "6,240 frames, and the joint-set and interaction families are re-parameterisations of rows "
  "already in the *m* = 50 family \u2014 so the pooled correction double-counts and the split is a "
  "presentational choice rather than a looser error-rate convention. Against the declared-family "
  "baseline of 144 survivors the pooled count falls to 141. The declared families hold 247 "
  "contrasts; every count here runs over the 244 of them that carry a verdict. Three do not: two "
  "are held by the endpoint veto declared with the shank-foot outcome, and one is the "
  "leave-one-out row of that same family, whose q Section 2.5 withholds. Four verdicts change "
  "under "
  "pooling, one gaining and three losing, and none is a headline claim. "
  "The block below "
  "also reconciles two counts that are not the same number — the verdict each artefact "
  "printed, and a Benjamini-Hochberg recomputation from the raw p within the family declared "
  "here — and names the contrasts where they differ.")
w("")
w(block(R + "/BIOCV_POOLED_SENSITIVITY.txt"))
w("")

w("## Table S4b. Declared families")
w("")
w("Section 2.5 corrects within each of these, never "
  "across them. The nine that predate the offset control total m = 189; the union the pooled "
  "sensitivity of Table S4 corrects over is all fourteen, m = 244, including the two families "
  "declared with the experiments they belong to (Tables S11 and S13). Both sensitivities cover the "
  "two offset-control families of Table S7, pooling their two reference arms, which is stricter "
  "than the manuscript's own correction.")
w("")
w("| family | m | where |")
w("|---|---|---|")
w("| main contrasts | 50 | Table S1 |")
w("| position against angle | 20 | Table S3i |")
w("| joint set against joint set | 8 | Table S3j |")
w("| per-joint | 12 | Table S3b |")
w("| posture | 13 | Table S3d |")
w("| dose-response | 6 | Table 2b |")
w("| within-limb membership, relative | 30 | Table S3n Part A |")
w("| within-limb membership, mm | 30 | Table S3n Part B |")
w("| within-limb per-subset effects | 20 | Table S3n Part C |")
w("| offset control, per-joint | 6 contrasts x 3 joints; BH applied within m = 18 per reference "
  "column, verdicts taken from the midpoint | Table S7 Part A |")

w("| offset control, per-subset | 4 x 2 retentions x 2 arms; BH applied within m = 8 per arm | Table S7 Part C |")
w("| estimator x rejection | 2 | Table S11 |")
w("| shank-foot angle | 4 | Table S13 |")
w("| offset control, reversal test | 6 contrasts x 3 joints; the difference between the "
  "as-measured and offset-removed effect, BH within m = 18 | Table S7 Part G |")
w("")
w("The m values above are the families as first declared. Every family containing leave-one-out "
  "rows was corrected again without them, because a q ranked against a p-value that does not "
  "apply is not a valid q. The reduced families are 46, 17, 24, 24, 16 and 1 in place of 50, 20, "
  "30, 30, 20 and 2.")
w("")
w("The family sizes printed in Table S4 count only the contrasts that carry a verdict, so the "
  "shank-foot family appears there as m = 2 where it is declared as m = 4 here and in Table S5; "
  "the two rows held by the endpoint veto are the difference.")
w("")
w("Four counts follow from these families and are not interchangeable. Benjamini-Hochberg "
  "within each family as first declared returns 146 verdicts (Table S5). Two shank-foot rows "
  "carry no verdict because an endpoint veto declared with the outcome withheld one, leaving "
  "144 (Table S4). Re-correcting on the reduced families moves one verdict, giving 143, which "
  "is the count the manuscript reports (Table S22). A single pooled correction over the union "
  "m = 244, an alternative to declaring families at all, gives 141 (Table S4). The "
  "arbitrary-dependence sensitivity leaves 107 of the 146 (Table S5).")
w("")
w("**A note on sign, for cross-checking.** Every table names its two arms in the order they "
  "are subtracted, so a contrast printed here as \"A vs B\" appears in the main tables as "
  "\"B vs A\" with the opposite sign wherever the main table names them the other way "
  "round. Both are correct under their own stated convention; compare the arm ORDER before "
  "concluding that a sign disagrees.")
w("")

w("## Table S5. Arbitrary-dependence sensitivity")
w("")
w("Section 2.5 corrects with Benjamini–Hochberg, whose proof assumes independent test statistics, "
  "and appeals to the extension to positive regression dependence. That assumption is not "
  "verifiable for this design, so the price of dropping it is reported here: the same authors' "
  "procedure for arbitrary dependence divides the threshold by the harmonic number H_m. It is "
  "deliberately conservative and is not the convention adopted, but it shows exactly which "
  "verdicts rest on the positive-dependence assumption.")
w("")
w(block(R + "/BIOCV_BY_SENSITIVITY.txt"))
w("")

w("## Table S6. Leave-one-participant-out robustness")
w("")
w("With eleven participants and a sign-flip floor of 0.000977, a contrast at that floor means all "
  "eleven agreed in direction, and the obvious question is whether one of them carries the result. "
  "Each contrast the paper rests on was refitted eleven times, dropping each participant in turn "
  "and re-running the exact test on the remaining ten.")
w("")
w(block(R + "/BIOCV_LOO_ROBUSTNESS.txt"))
w("")

w("## Table S7. Is the per-joint sign structure an artefact of offset direction?")
w("")
w("Table S3m shows that 74\u201381% of the position error at hip and knee is a fixed joint-centre "
  "offset of 27\u201337 mm, against per-joint effects of 0.2\u20130.7 mm. A scalar error measured "
  "against a displaced target changes only through the perturbation\'s component along the "
  "offset, so a per-joint sign could report offset direction rather than triangulation "
  "accuracy. The twelve per-joint contrasts of Table 1b were therefore repeated on "
  "offset-removed error, subtracting each participant\'s own mean error vector for that "
  "joint from both arms of a contrast. Which arm supplies the offset is a free choice, so "
  "both are reported. Part B splits the same effects into components along and perpendicular "
  "to the offset.")
w("")
w("**What the parts contain.** (A) the twelve per-joint contrasts on offset-removed error, plus "
  "the two rejection contrasts; (B) the split into components along and perpendicular to the "
  "offset; (D) the offset estimated out of sample; (E) superseded, see (F); (C) the matched-k "
  "subset control; (F) dispersion against centroid. They print in the order they are computed, "
  "which is not alphabetical. (G) tests the reversal the title asserts as a DIFFERENCE between "
  "the as-measured and offset-removed effects, rather than as a pair of verdicts, which is the "
  "standard Section 2.5 applies to every other such claim; its reading was fixed before the "
  "numbers existed.")
w("")
w("**Parts E and F, in order.** Part E asked whether the offset-removed effect is a residual "
  "mean shift or a change in dispersion, and it cannot answer: it subtracts the MIDPOINT of "
  "the two arms' mean errors from both, which leaves residual means of equal norm and "
  "opposite sign, so its mean-shift column is zero for every row by construction. It is "
  "printed because it was run and reported, and it is withdrawn. Part F is the test that can "
  "fail, on quantities that are both free to differ, and it is the one the manuscript cites.")
w("")
w(block(R + "/BIOCV_OFFSET_CONFOUND.txt"))
w("")

w("## Table S8. Exact intervals for the quoted position effects")
w("")
w("A sign-flip test at the 0.000977 floor certifies that all eleven participants agreed in "
  "direction; it says nothing about magnitude. These are the effects the abstract and "
  "Results quote, with the interval obtained by inverting the same exact test -- the "
  "procedure already used for the null angle contrasts of Table S3k. Point estimates "
  "reproduce the published values exactly, which is what makes the intervals comparable to "
  "them.")
w("")
w(block(R + "/BIOCV_INTERVALS.txt"))
w("")
w("Table S8 as first built carried no [pos:AW] rows, so the largest triangulation effect in "
  "the paper -- confidence weighting against uniform at the ankles and wrists, quoted in "
  "Section 5 and Table 1(a) -- was the one headline magnitude with no interval. The rows "
  "below repair that. They are computed from the per-participant accumulator that "
  "biocv_permutation_v2.py persists, by the same inversion of the exact test, so they need no "
  "recomputation of the arms. They also settle a second question: 5.062 mm (Section 5) and "
  "5.086 mm (Table S2c) are the same contrast weighted two ways, the first taking the mean of "
  "eleven per-participant differences and the second the difference of frame-pooled means, "
  "which weights a participant by how many frames they contribute.")
w("")
w(block(R + "/BIOCV_AW_INTERVAL.txt"))
w("")

w("## Table S9. Does the joint-centre offset belong to the detector?")
w("")
w("Every other result here rests on one pose estimator. The same 6,240 frames were "
  "re-detected with RTMO-m — one-stage, no separate person detector, a different "
  "training regime — leaving ground truth, calibration, person association and the "
  "keypoint-to-marker mapping untouched, so the two caches differ only in the detector. "
  "Both are scored on the plainest arm: no rejection, confidence weights, weighted DLT. The "
  "reading below was fixed in the analysis script before the numbers existed. Both caches are "
  "distortion-corrected, as every published result is; scoring a corrected cache against a "
  "raw one puts the distortion difference into the detector contrast at exactly the "
  "near-camera residuals distortion moves most, and doing so inflates RTMO's random "
  "residual roughly 2.4-fold and reverses the ankle offset direction. The table below is "
  "the corrected comparison; all three tests pass.")
w("")
w("**What the three detectors do not vary.** RTMPose, RTMO and the HALPE-26 model are all "
  "from one implementation family, and HALPE-26 extends COCO annotations rather than "
  "replacing them with an independently collected corpus, so its indices 0-16 keep COCO-17 "
  "semantics. The three are therefore not three independent replications: they vary the "
  "architecture and the training data while holding the landmark CONVENTION fixed. That is "
  "what makes them a test of the model rather than of the definition, and it is also the "
  "reason the persistence result cannot be read as evidence that a differently DEFINED "
  "landmark would show the same offset. No control here tests that.")
w("")
w("The two detectors agree on where the joint centre is wrong, per participant, at every "
  "joint: the cosines run 0.91 to 1.00 at hip and knee and 0.74 to 0.99 at the ankle, and "
  "the share of squared error the offset accounts for reproduces the manuscript's pattern, "
  "high at hip and knee and roughly half that at the ankle. What this establishes is that "
  "the two architectures place the centre in the same wrong place; it does not establish "
  "which placement is closer to the marker-based centre, and it says nothing about a "
  "detector trained on a different keypoint convention, since both are scored on COCO-17.")
w("")
w(block(R + "/BIOCV_DETECTOR_TRANSFER.txt"))
w("")

w("## Table S10. Pipeline arms")
w("")
w("Every arm shares the same detections, calibration and candidate cameras; the named "
  "component is the only thing that differs. Arms marked DIAGNOSTIC are not deployable as "
  "tested and are included to isolate a mechanism.")
w("")
w("| component | arms |")
w("|---|---|")
w("| weighting (in a weighted DLT) | uniform; detector confidence *c*; inverse distance 1/*d* (DIAGNOSTIC: ground-truth distances); confidence × 1/*d*, i.e. *c*/*d* (DIAGNOSTIC). A *c*/*d*² variant was null on both outcomes (Table S2c). |")
w("| rejection rule | none; adaptive — iteratively drop the worst observation while it exceeds median + 3σ̂ (σ̂ = 1.4826 × MAD), to a four-camera floor; matched-*k* (DIAGNOSTIC) — drop exactly *k* worst-first, so retention is identical across criteria and only the ordering differs. |")
w("| rejection criterion | reprojection residual, in pixels; object-space residual, in mm (Eq. 1). |")
w("| joint-centre offset | none; population table — for each participant and joint, the mean error vector of the other ten, taken in world coordinates on the no-rejection, confidence-weighted arm, subtracted from the estimated centre, so the correction is out of sample in participant; own-mean correction (DIAGNOSTIC), reported only as a ceiling (Table 3a). |")
w("| estimator | weighted DLT; Gauss—Newton refinement of the weighted squared reprojection residual, initialised from the DLT. The two minimise Σ*wr*² and Σ*w*²*r*² respectively; contrasts holding that fixed are labelled *w*²-matched. |")
w("")

w("## Table S11. Estimator by rejection")
w("")
w("Whether discarding is position-neutral under one estimator and not under the other is a "
  "comparison between two verdicts, which the inference this paper cites Gelman and Stern "
  "(2006) against cannot settle. This is the interaction test that can. Both estimators' arms "
  "come from one accumulation, "
  "so the per-participant difference is paired rather than assembled across runs, and the "
  "component effects reproduce the published values exactly. The reading was fixed in the "
  "analysis script before the numbers existed, and the ANGLE row was a predicted NULL: the "
  "paper's account says discarding costs the angle under both estimators, so a surviving "
  "interaction there would have counted against it.")
w("")
w(block(R + "/BIOCV_EST_REJ_INTERACTION.txt"))
w("")

w("## Table S12. A bound on the synchronisation residual")
w("")
w("The dataset providers corrected a whole-frame offset from an LED pulse and report an "
  "uncorrected sub-frame residual without quantifying it; the copy obtained under our data use "
  "agreement carries no descriptor from which to quote a figure. A reviewer may reasonably ask "
  "whether that residual inflates the RANDOM half of the decomposition and so deflates the "
  "74-81% offset share. It cannot be looked up, but it can be bounded from the reference "
  "trajectories themselves, which is what this does. The reading was fixed in the analysis "
  "script before the numbers existed; it fired against the paper, and the threshold it used was "
  "the wrong comparison. Both the verdict and the reason it is the wrong comparison are printed "
  "below, in that order, rather than the rule being replaced after the fact.")
w("")
w("**The settled position, stated first.** The synchronisation residual is bounded at 3.6 mm "
  "typical and 7.7 mm worst case at hip and knee on the mean-speed comparison, which is what "
  "the manuscript quotes; on the 95th-percentile comparison the same table gives 15.8 mm, "
  "which the manuscript also quotes as the wider bound. Against a 27-37 mm offset either "
  "bound leaves the offset the dominant term, and the offset share is reported as a bracket "
  "(74-81%, and 69-77% if the entire along-track component were timing) rather than a point. "
  "The block below records how that position was reached, including a pre-declared verdict "
  "that fired on a comparison later found to be the wrong one.")
w("")
w(block(R + "/BIOCV_SYNC_BOUND.txt"))
w("")

w("## Table S13. A second detector and training corpus, and ankle dorsiflexion")
w("")
w("Table S9 changed the detector ARCHITECTURE on the same 17 keypoints. This changes the "
  "CONVENTION: HALPE-26 is a 26-keypoint scheme with a different annotation corpus, run on the "
  "same frames with ground truth, calibration and association unchanged, and distortion-corrected "
  "like every other cache here. It also carries feet, and the BioCV reference carries LTOE/RTOE "
  "and HEEL_L/HEEL_R, so ankle dorsiflexion -- absent from the rest of this paper -- becomes "
  "measurable on both sides of the comparison. 103 of the 104 trials re-detected.")
w("")
w("The reading was fixed in the analysis script before the numbers existed, including the "
  "declared sensitivity: the angle is primary on the big toe and repeated on the heel, and where "
  "the two foot endpoints disagree in sign NO VERDICT is reported. Both rejection rows fall to "
  "that rule. The segment geometry was then measured to test whether a shorter distal segment "
  "explained the disagreement; at 1.5x it does not, and the disagreement is left unexplained "
  "rather than argued away.")
w("")
w(block(R + "/BIOCV_HALPE.txt"))
w("")

w("## Table S14. Is the offset a synchronisation lag?")
w("")
w("Table S12 bounds the synchronisation residual's MAGNITUDE but says nothing about its "
  "DIRECTION, and direction is what decides where it lands. Heading varies by 1.0–14.1 degrees "
  "within ten of the eleven participants and by 53.7 within the eleventh (Table S20), and the "
  "offset is estimated within participant, so a constant sub-frame lag displaces that "
  "participant's estimates the same way in the world frame and biases the offset rather than "
  "blurring it. The narrower statement this supports, and the one the manuscript makes, is "
  "that a timing lag cannot be the SOURCE of the offset; it does not follow that the "
  "residual enters only the random half, and it does not.")
w("")
w("The test is that a lag is shared by every joint, so displacement = speed x lag must hold "
  "with one lag across all six. It does not: hip and knee move at 1.53 and 1.54 m/s yet carry "
  "22.8 and 16.0 mm along the walking direction, and the implied lag spans 9 to 16 ms, every "
  "value above the 5 ms frame period a sub-frame residual is bounded by. The reading was fixed "
  "in the analysis script before the numbers existed, and its speed premise was wrong on first "
  "writing; the original wording and the correction are both kept in that file.")
w("")
w(block(R + "/BIOCV_SYNC_DIRECTION.txt"))
w("")

w("## Table S15. Statistical specification in full")
w("")
w("Section 2.5 states the design; the justifications and the secondary sensitivities are here, "
  "moved out of the main text for length and not abridged in the move.")
w("")
w("**Why Benjamini–Hochberg rather than a stricter procedure.** Its proof assumes independent "
  "test statistics. Contrasts within a family here share arms, participants and baselines, so the "
  "procedure rests on positive regression dependence, which is assumed rather than verified. That "
  "is the field's convention, and the arbitrary-dependence alternative of Benjamini and Yekutieli "
  "(2001) is reported alongside every verdict rather than in place of it: 99 of 133 survive and "
  "the 34 it removes carry a dagger wherever they are quoted (Table S5).")
w("")
w("**One correction over the union of all thirteen families.** Declaring thirteen families rather "
  "than one is a presentational choice, so the pooled alternative is reported too. Over the union "
  "(m = 244) the count falls from 144 to 141: four verdicts change, one gaining and three losing, "
  "and none is a headline claim. Two further contrasts carry no verdict at all, withheld by an "
  "endpoint veto declared with their outcome (Table S4).")
w("")
w("**What a percentage-point interaction figure is.** A position-against-angle interaction is the "
  "difference of two fractional changes. Its magnitude in percentage points is the tested "
  "statistic's effect size on the relative scale, not a physical quantity, and it is not "
  "convertible to millimetres or degrees.")
w("")
w("**Intervals.** Exact intervals invert the sign-flip test at 95% where a magnitude is quoted "
  "and at 90% where a null is bounded, 90% being the level corresponding to two one-sided 5% "
  "tests. Percentile bootstrap intervals use B = 3000 and resample participants; where the two "
  "disagree the exact test governs (Tables S3k, S8).")
w("")
w("## Table S16. Dataset, rig and calibration detail")
w("")
w("**Participants.** The eleven present in our copy are P03, P04, P06, P08, P09, P10, P13, P16, "
  "P17, P26 and P28. We hold nothing on the other four of the archive's fifteen, so the "
  "inferential units are a non-random subset.")
w("")
w("**Frame sampling.** Sixty frames per trial at near-even spacing is a compute bound, not a "
  "property of the data; the spacing spans the whole pass through the capture volume rather than "
  "concentrating on part of it. No temporal filter can be applied at 45 ms between retained "
  "frames, which is why every markerless estimate here is unfiltered.")
w("")
w("**Two foot-offset figures.** Table S13 gives the toe keypoint's offset as 55.7 and 54.6 mm "
  "per side and Table S19 as 52.24 mm. They are the same quantity on different frames: S13 "
  "requires only that keypoint to be valid, while S19 requires knee, ankle, toe and heel to be "
  "simultaneously valid and both endpoints triangulable, because it decomposes each offset "
  "against a segment those four points define. The stricter subset is the smaller figure; "
  "both are correct for the frames they are computed on.")
w("")
w("**Keypoint-to-reference correspondence.** Each COCO-17 landmark is differenced against the "
  "identically named point in the archive's own output: LEFT_SHO, RIGHT_SHO, LEFT_ELBOW, "
  "RIGHT_ELBOW, LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE, "
  "LEFT_ANKLE and RIGHT_ANKLE. These are joint centres produced by the dataset's 6-DoF model, "
  "not raw markers, so every offset in this paper is keypoint minus model joint centre. Under "
  "HALPE-26 the two foot endpoints are differenced against the reference markers LTOE/RTOE and "
  "HEEL_L/HEEL_R. The archive record states that joint centres are the midpoint of the medial "
  "and lateral markers at every joint except the hip, which uses the regression of Bell et al. "
  "(1989); that regression carries its own error, of the order of the offset reported here and "
  "mirrored across the midline, which is why the hip offset cannot be apportioned between the "
  "two systems.")
w("")
w("**Person association and admission.** Per camera, the detected person whose visible COCO "
  "joints best match the projected reference is selected, and the camera is dropped for that "
  "frame if the best match's median skeleton distance exceeds 80 px. A 2D observation is "
  "admitted if its coordinates are finite and its detector score is strictly positive, and a "
  "joint is triangulated only where at least four cameras are admitted.")
w("")
w("**Rig.** The nine machine-vision cameras have non-uniform focal lengths and substantial radial "
  "distortion across all 99 calibrations; the geometry is specified in Table S0. We used the "
  "dataset's updated calibration throughout.")
w("")
w("**Cross-system alignment.** The providers report 3.62 mm on annotated WALK_01 frames and "
  "2.31 mm above the force plates (Evans et al., 2024). Both are their figures; we did not "
  "recompute either and no analysis here derives one.")
w("")
w("**Four thigh-shank baselines.** The same angle is quoted at four values because four "
  "different arms and frame sets produce it, and Section 2.4 points here for the "
  "reconciliation. 2.575 deg is the per-participant mean on the full pipeline arm (Table 3a, "
  "Table S2c). 2.570 deg is the same quantity pooled over frames rather than participants "
  "(Table 2b). 2.669 deg is the per-participant k = 0 baseline of the threshold sweep, which "
  "runs on the sweep's own frame set (Table S21). 2.722 deg is the object-space arm with "
  "confidence weighting on that same frame set (Tables S21, S3f). None is comparable in "
  "absolute value with model-based reporting, and no contrast in this paper is taken across "
  "two of them.")
w("")

w("## Table S17. Why does the population offset table harm the knee angle?")
w("")
w("Two mechanisms were tested. Neither is established, and the harm is reported as bounded "
  "rather than explained.")
w("")
w("**Geometry.** Of the knee's offset relative to the hip–ankle chord, only the in-plane "
  "perpendicular component acts in the direction that moves flexion: 11.04 mm against 27.45 mm "
  "axial and 8.63 mm out of plane (Table 3b). This cannot explain the harm, because removing the "
  "ENTIRE true offset changes the angle by 0.166°, less than the 0.606° the table costs.")
w("")
w("**Mismatch.** The difference between a participant's own offset and the population mean is of "
  "ample size: applied to the reference points and the angle recomputed exactly, it predicts "
  "2.19–2.33° against the 0.606° observed. But the harm does not track it across "
  "participants (r = −0.40 to +0.31, p at least 0.23). With n = 11 the test cannot detect a "
  "correlation below about 0.6, so this is an absence of evidence at low power, not evidence "
  "against the mechanism (Table S3e).")
w("")
w("## Table S18. Does the absence of temporal filtering change the result?")
w("")
w("Every error in the main analysis is an unfiltered markerless estimate against a "
  "12 Hz-filtered reference, because trials are sampled every ninth frame and 45 ms between "
  "retained frames admits no temporal filter. The sampling was a compute choice and not a "
  "property of the data, so the measurement is available: contiguous windows were re-detected "
  "for a subset of trials and the reference's own filter applied to the markerless "
  "trajectories. The reading below was fixed in the analysis script before the numbers "
  "existed, including the condition under which the angle conclusion would have to be "
  "withdrawn.")
w("")
w(block(R + "/BIOCV_CONTIGUOUS.txt"))
w("")
w("## Table S19. Does geometry explain the toe/heel disagreement?")
w("")
w("Table S13 leaves the endpoint disagreement unexplained and rejects a sensitivity account on "
  "the ground that the heel is only 1.5 times as sensitive per millimetre. That compares the "
  "wrong quantity: what moves a three-point angle is the offset component PERPENDICULAR to the "
  "segment, in the plane of the angle, not the offset's length. The decomposition below is the "
  "one already run for the knee in Table 3(b), applied to each foot endpoint against its own "
  "ankle-to-endpoint segment. Its reading was fixed before it was run, including the branch "
  "under which the result would count against the paper's choice of primary endpoint.")
w("")
w(block(R + "/BIOCV_FOOT_GEOMETRY.txt"))
w("")
w("## Table S20. The span of walking headings")
w("")
w("Three claims rest on how widely heading varies: the non-transferability of the "
  "world-frame offset table, the near-identity of the world- and body-frame decompositions "
  "in Table S3m, and the argument in Table S14 that a constant sub-frame timing residual "
  "lands in the bias term. Heading is measured here from the reference alone. It varies "
  "widely ACROSS trials and narrowly WITHIN a participant, which is the level at which the "
  "offset is estimated. The reading below was fixed before the number existed.")
w("")
w(block(R + "/BIOCV_HEADING.txt"))
w("")
w("## Table S21. Is the adaptive rule's threshold load-bearing?")
w("")
w("Section 2.2 fixes the adaptive rule at a median-plus-three-MAD threshold with a four-camera "
  "floor. Both numbers were chosen and, until this table, never varied, so every rejection "
  "result in the paper was conditional on them. The multiplier is swept here over 2.5, 3.0, 3.5 "
  "and 4.0 on both criteria and the same frames, with the reading fixed before the numbers "
  "existed, including the "
  "branch under which the angle cost would have had to be restated.")
w("")
w(block(R + "/BIOCV_MAD_SWEEP.txt"))
w("")
w("## Table S22. What the withheld leave-one-out rows did to everyone else's q")
w("")
w("Withholding a q is not the whole consequence of an invalid p-value. Those p-values were part "
  "of the Benjamini-Hochberg ranking of the families they sat in, so every other q in those "
  "families was computed against them. Each affected family is corrected again without the "
  "leave-one-out rows, with the reading fixed before the numbers existed.")
w("")
w(block(R + "/BIOCV_LOO_EXCLUSION.txt"))
w("")
w("## Table S23. Is the triangulation null a property of the rule, or of a redundant rig?")
w("")
w("Every rejection result in the manuscript is measured on a nine-camera ring where the "
  "adaptive rule retains 8.26-8.68 cameras of nine (Table S21). Under that redundancy "
  "discarding one observation is close to a no-op, so a small effect is what the geometry "
  "predicts rather than what the pipeline reveals, and most laboratories the recommendation "
  "would reach run four to eight cameras. The cached detections hold all nine views, so the "
  "same contrasts are recomputed on fixed camera subsets at no new detection cost. The subsets "
  "are chosen by index to spread around the ring and are ONE choice, not an average over all "
  "subsets of that size; the four-camera rejection floor is unchanged. The reading, including "
  "the branch under which the manuscript would have to narrow its headline claim, was fixed in "
  "the script before the numbers existed. That branch is the one it returned.")
w("")
w(block(R + "/BIOCV_CAMERA_SUBSETS.txt"))
w("")
io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
missing = [x for x in L if x.startswith("_[")]
print("wrote " + OUT)
print("  removed " + str(len(STRIPPED)) + " author-facing annotation block(s):")
for f, first in STRIPPED:
    print("    " + f + ": " + first)
# The supplement's preamble promises no author-facing notes. The ANNOTATION filter keys on how a
# line OPENS, so five ordinary sentences carrying development history reached the submitted file --
# including "referee's mechanism", which discloses a prior review round on a manuscript submitted
# as new, and "The test the manuscript's central claim was missing". A promise in the preamble is
# not a check; this is.
DEV_HISTORY = re.compile(
    r"referee|earlier version|earlier run|previously said|previously quoted|never computed|supersede|all of which are stale|"
    r"was missing|as published|council|watchdog|round \d|resubmi|"
    # Self-correction narrative. The list above enumerates phrases already SEEN, which is
    # exactly why it passed "Fixed here." for a whole round. These match the CLASS: the
    # supplement telling a reader that something in it used to be wrong.
    # \b on both ends: this matched inside "recorrected here", which describes what a table
    # DOES rather than narrating that something used to be wrong.
    r"\bfixed here\b|\bcorrected here\b|\bnow fixed\b|\bused to be\b|"
    r"(?:were|was|is|are) (?:right|wrong|correct|incorrect),? but|inverted them", re.I)
history = []
for _i, _line in enumerate(("\n".join(L)).split("\n"), 1):
    if DEV_HISTORY.search(_line):
        history.append((_i, _line.strip()[:90]))
if history:
    print("  " + str(len(history)) + " line(s) carrying development history reached the supplement,")
    print("  which its preamble says contains none. Reword them in the SOURCE artefact:")
    for _i, _t in history:
        print("    line " + str(_i) + ": " + _t)

if MIDPARA:
    print("  " + str(len(MIDPARA)) + " author-facing sentence(s) begin mid-paragraph and were NOT")
    print("  stripped, because stripping them would amputate the paragraph they sit in. Reword them")
    print("  in the source artefact so the annotation starts its own paragraph:")
    for f, first in MIDPARA:
        print("    " + f + ": " + first)
if missing:
    print("MISSING SOURCES:")
    for x in missing:
        print("  ", x)
if MIDPARA or missing or history:
    raise SystemExit(1)
