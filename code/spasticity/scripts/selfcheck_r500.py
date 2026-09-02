# -*- coding: utf-8 -*-
"""r500: mechanical check of the cut manuscript against its deposits, its supplement and itself.

The r445 manuscript was 16,212 words and carried its own revision history in the text. It was cut to
~6,100 words at r500 and the full working text moved to SUPPLEMENT_r500.md. Nothing was withdrawn in
that cut, so this check enforces a contract: every load-bearing number and every concession that was
in the long text must still be in the short one. It also carries forward every forbidden value from
earlier rounds, because the single worst error of this project was a round that removed a guard in
order to let its own new text through.
"""
import io
import json
import os
import re
import sys

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
M = io.open(os.path.join(PAP, "MANUSCRIPT_r500.md"), encoding="utf-8").read()
MN = re.sub(r"\s+", " ", M)                    # line wrapping must not hide a required string
BODY = M.split("## References")[0]
fails, warns = [], []


def has(pat, why):
    if not re.search(pat, MN):
        fails.append("MISSING: %s  (%s)" % (pat, why))


def forbid(pat, why, unless=None):
    for m in re.finditer(pat, MN):
        w = MN[max(0, m.start() - 400):m.start() + 400]
        if unless and re.search(unless, w):
            continue
        fails.append("FORBIDDEN: %r  (%s)" % (m.group(0)[:60], why))


def near(a, b, tol, why):
    if abs(a - b) > tol:
        fails.append("ARITHMETIC: %.4f vs %.4f  (%s)" % (a, b, why))


# ---------- 1. core values must still match their deposits ------------------------------------
d = json.load(io.open(os.path.join(PAP, "IC_KNEE_VS_ANKLE_r439.json"), encoding="utf-8"))["endpoints"]
for printed, actual, what in [
        ("5.280", abs(d["knee_ic"]["spastic_minus_weakness_deg"]), "knee at contact"),
        ("0.056", abs(d["ankle_ic"]["spastic_minus_weakness_deg"]), "ankle at contact"),
        ("2.342", abs(d["ankle_stance"]["spastic_minus_weakness_deg"]), "ankle over stance"),
        ("12.4", d["knee_ic"]["effect_in_seed_SDs"], "knee in seed SD")]:
    if printed not in MN:
        fails.append("MISSING core value %s (%s; deposit %.4f)" % (printed, what, actual))
    near(float(printed), actual, 0.02, "printed %s vs deposit" % printed)

f = json.load(io.open(os.path.join(PAP, "FAMILY_LEVEL_r494.json"), encoding="utf-8"))
near(abs(f["difference_deg"]), 5.593, 0.002, "family-level difference")
near(f["permutation"]["p"], 1 / 462.0, 1e-5, "family permutation p = 1/462")
near(f["leave_one_family_out"]["accuracy"], 58 / 59.0, 1e-4, "leave-one-family-out accuracy")

# ---------- 2. the load-bearing numbers the cut must not have dropped --------------------------
CONTRACT = [
    # separation
    "5.280", "0.056", "2.342", "12.4", "0.37", "1.49", "2.99", "5.1", "0.586",
    "5.59", "3.81", "7.38", "462", "0.0022", "98.3", "61.0", "4.087", "2.419", "0.908",
    # dose and sub-phase
    "1.358", "3.922", "0.993", "0.981", "3.437", "0.628", "0.844", "17%",
    # r508: "2.7 to 7.3" / "0.4 to 1.6" were computed on NULL_FLOORS_r428's family-based floor,
    # which FLOOR_CORRECTION_r436 retires as circular (101% of its spread is weakness depth).
    # The live values are scored on the 0.511 deg within-cell seed SD.
    # r510: the 15.7 span runs to a gain column added after hashing; only the registered
    # spans (8.3 at x1.00, 6.9 at x0.80) may be quoted as registered
    "8.3 seed SD", "6.9 at", "0.9 to 3.5", "0.511",
    # controls
    "0.211", "1.375", "190", "0.274", "0.690", "0.963", "0.296", "0.393", "0.303", "5.016", "5.134", "0.118",
    "1.985", "35.5", "0.875", "0.484", "26.7", "8\u201355", "0.57", "13.63", "25.17", "3.420",
    # measurability
    # r521: the MDC comparison is replaced by the discriminability it should always have
    # been (DISCRIMINABILITY_r519). The replacement is HARSHER, not kinder: a
    # misclassification rate near chance rather than a threshold missed by 1.97 deg.
    "3.70", "5.7", "4.9", "7.0", "2.0 measurement SEM", "0.6 total SD", "2.62",
    "7.93", "9.16", "4.72",
    # patient data and the proposed study
    "0.362", "0.662", "0.019", "0.79", "62", "104", "1860", "51", "66", "89",
    "0.613", "6.31", "17.09", "42",
    # contracture and mediation
    "7\u00b0 to 22\u00b0", "11 of the 30", "17 of the remaining 19", "0.826",
    # lateral divergence
    "0.051", "0.0005", "6.2 to 12.0", "5.4 to 10.9",
    # r504-r505 additions: the recomputed controls, swing dorsiflexion, and the hip
    "8.73", "0.43", "4.9%", "0.988", "1.041", "2.7, not the factor of 94", "1.518",
    "0.73°", "0.422", "thirteen times", "2.11", "1.01", "5.7 within-cell", "9.81",
    # r523 endpoint scan (ENDPOINT_r523 / WINDOW_r520 / PEAK_r522 / LIMBDIFF_r521).
    # The load-bearing claim is the DISJOINTNESS across all seven single-limb readouts, which is
    # unselected; the 4.05 is the maximum of a six-window scan and is quoted as an upper estimate.
    "4.05", "3.08", "1.557", "6.049", "5.406", "4.422", "3.143", "2.156", "4.216",
    "1.115", "8.1%", "3.26", "0.385",
    # the limb contrast, the one readout that fails
    "1.291", "0.909", "1.777", "3.388", "1.641", "3.651",
    # instrument ceiling on a single-patient reading
    "36.7", "38.4", "37.6", "39.1", "one percentage point",
]
for v in CONTRACT:
    if v not in MN:
        fails.append("CONTRACT: load-bearing value %r dropped in the cut" % v)

# ---------- 3. concessions that must survive into the main text -------------------------------
CONCESSIONS = [
    (r"post-observation", "the window and endpoint were chosen after seeing the data"),
    (r"survival edge coincide", "the window's lower edge is the survival edge"),
    (r"cannot bound the confound", "the duration control is inconclusive"),
    (r"divergent inside the measurement window", "the hyperreflexia arm loses lateral balance"),
    (r"not purely lesion-side", "the unlesioned side moves too above the lower gains"),
    (r"No contracture arm", "the leading alternative explanation"),
    (r"mediation is not excluded", "ankle mediation survives in most pairs"),
    # r502: the guard here previously required "cannot recover the mixture", which encoded an
    # OVERSTATEMENT introduced in the r500 rewrite. MIXED_RESULT_r424's own reading is that the
    # endpoint responds to the hyperreflexia axis at 2.7-7.3x its floor and to the weakness axis at
    # 0.4-1.6x, the latter below the floor at the two lower gains -- asymmetric resolution, not
    # cancellation. The concession that must survive is that weakness depth is not readable.
    (r"not readable from this endpoint", "weakness depth is not resolved by the knee readout"),
    (r"grades hyperreflexia against an unknown", "what the endpoint does report"),
    (r"not a spasticity meter", "the readout is not a per-patient instrument"),
    (r"shortness of any origin", "the construct is plantarflexor over-shortening broadly"),
    (r"do not overlap", "the simulated severity range and the block population"),
    (r"did not replicate", "the one exploratory-to-confirmatory transfer failed"),
    (r"No correction is applied", "multiplicity is stated, not corrected"),
    (r"un-re-optimised state", "the frozen-controller concern"),
    (r"delivered", "gains are reported as delivered, not nominal"),
    (r"not significantly related to knee angle at any stance phase", "the Cawood null"),
    (r"cannot adjudicate", "neither patient dataset can settle it"),
    (r"binding constraint is biological", "the limit on a per-patient reading is not the instrument"),
    (r"two readings in five", "the misclassification rate against real between-patient spread"),
    (r"4 to 6% of its size", "what measurement error costs a correlational design"),
    (r"hash sidecars were re-baselined", "the registration edited after its result"),
    (r"uninformative as registered", "P2 and P3 as registered"),
    # r518: recomputed on the current 23-cell corpus, the raw control fails at 95%, not 65%
    (r"95% of the effect", "the raw duration control fails its own bar"),
    (r"7\.28 s", "the measured arm end-time gap, not the rounded 7 s"),
    (r"fall like all the others", "round 151 does not remove the survival confound"),
    (r"107% of its own", "rule 3's control-referenced half is unstable"),
    (r"0\.52°", "the resampling convention sensitivity"),
    (r"thirteen times", "the ankle duration control fails by 13x, per ANKLE_CONTROLS_HIP_r510"),
    (r"correction runs against this study", "the SEM correction is adverse to us and must say so"),
    # r516: the concession is the same, stated without narrating the revision history
    (r"that column is post hoc", "the 15.7 span depends on an unregistered column"),
]
for pat, why in CONCESSIONS:
    if not re.search(pat, MN):
        fails.append("CONCESSION dropped: %s  (%s)" % (pat, why))

# ---------- 4. values withdrawn in earlier rounds, carried forward -----------------------------
# Each of these was adverse to this study, so re-admitting one would flatter the paper. The Cawood
# guard in particular was removed at r491 to let a wrong reading through; it must not be removed.
forbid(r"0\.542|0\.745|0\.672", "Cawood JATS-XML mis-extraction; see CAWOOD_CORRECTION_r450")
forbid(r"6\.34|7\.62", "Geiger MDC values, never verified against the source")
forbid(r"54[\u2013-]76%", "Zeni event-detection rate, contradicted by the source's own figures")
forbid(r"r = 0\.490|r = 0\.482", "Choi coefficients, paywalled and deposit is metadata-only")
forbid(r"1\.7[\u2013-]2\.1 SD", "the 2.1 end comes from the withdrawn 5.7 bar")
forbid(r"most dose-symmetric", "DOSE_r174 registers x0.892 as the match, not x0.80")
forbid(r"10[\u2013-]25\u00b0", "the equinus figure withdrawn at r454")
forbid(r"MMT 4\+", "the MMT mapping is an inference, not a measurement")
forbid(r"12 chronic hemiparetic adults", "Cawood's cohort is subacute, median 4.0 months")
forbid(r"nothing\s+published for swing dorsiflexion", "false: Kesar reports 4.9 deg")
forbid(r"\u03c1 \u2265 0\.82", "0.82 was computed on mis-extracted values; 0.79 is correct")

# ---------- 5. arithmetic the text asserts ------------------------------------------------------
near(5.280 / 0.4253, 12.42, 0.05, "5.280 / knee seed SD = 12.4")
# r523: the 7.25 deg bar is a minimal detectable change (1.96 x SD_diff). Section 3.5 argues that
# a change threshold answers whether one patient CHANGED, not which lesion they have, and replaces
# it throughout with the discriminability. The arithmetic checks that policed the retired bar are
# replaced by a ban on the values themselves, which is stricter than checking them.
forbid(r"7\.25|1\.97°|3\.163|change threshold for this|below the .{0,20}change threshold",
       "minimal detectable change, retired at r523 in favour of the discriminability of section 3.5")
near(1 / 462.0, 0.002165, 1e-5, "family permutation floor")
near(36 / 59.0 * 100, 61.0, 0.1, "majority-class baseline")
near(4 / 15.0 * 100, 26.67, 0.05, "batch null rate")
near(1.985 / 5.593 * 100, 35.5, 0.1, "unlesioned share of the separation")

# ---------- 6. structure ------------------------------------------------------------------------
if "\u26a0" in BODY:
    fails.append("the warning glyph is not a JNER convention and must not return")
for pat in [r"earlier (draft|revision)", r"intermediate revision", r"revision before"]:
    if re.search(pat, BODY, re.I):
        fails.append("the main text narrates its own revision history again: %s" % pat)

refsec = M.split("## References")[1]
reflines = [l for l in refsec.split("\n") if re.match(r"^\d+\. ", l)]
N_REFS = 25   # r504 added [25], the able-bodied reference dataset behind the 4.72 deg SD
if len(reflines) != N_REFS:
    fails.append("reference list has %d entries, expected %d" % (len(reflines), N_REFS))
for l in reflines:
    if len(l) < 90:
        fails.append("reference looks incomplete (title missing?): %s" % l[:70])
    if not re.search(r"(doi:|PMID )", l):
        fails.append("reference carries no DOI or PMID: %s" % l[:60])

cited = set()
for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", BODY):
    for x in m.group(1).split(","):
        cited.add(int(x.strip()))
orph = [n for n in range(1, N_REFS + 1) if n not in cited]
if orph:
    fails.append("references cited nowhere in the body: %s" % orph)

heads = set(re.findall(r"(?m)^#{2,3} (\d+(?:\.\d+)?)", BODY))
xref = set(re.findall(r"\u00a7(\d+(?:\.\d+)?)", BODY))
if xref - heads:
    fails.append("cross-references to sections that do not exist: %s" % sorted(xref - heads))

sup = os.path.join(PAP, "SUPPLEMENT_r500.md")
if not os.path.exists(sup):
    fails.append("the supplement is missing; the cut material has no home")
elif os.path.getsize(sup) < 80000:
    fails.append("the supplement looks truncated (%d bytes)" % os.path.getsize(sup))

# ---------- report --------------------------------------------------------------------------------
w = len(" ".join(l for l in BODY.split("\n") if not l.strip().startswith("|")).split())
print("manuscript: %d chars, ~%d body words (measured JNER norm 7900-11700)" % (len(M), w))
print("supplement: %d bytes" % (os.path.getsize(sup) if os.path.exists(sup) else 0))
print("figures: %d" % len([x for x in os.listdir(os.path.join(PAP, "figures"))
                           if x.endswith(".png")]))
# measured against the journal itself: three JNER research articles in this reference list run
# 7,916 / 9,468 / 11,747 body words, so the earlier 6,000 target was tighter than the norm
if w > 9500:
    warns.append("body is %d words, above the 9,500 soft target "
                 "(measured JNER range 7,916-11,747, so this is inside the norm)" % w)
print()
for x in fails:
    print("  FAIL  " + x)
for x in warns:
    print("  warn  " + x)
print()
print("=== %d failures, %d warnings ===" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
