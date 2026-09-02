# -*- coding: utf-8 -*-
"""r456: mechanical consistency check of the manuscript against the deposits and against itself.

Catches the class of defect that three separate cold readers found by hand: a number quoted in one
section that disagrees with the same number elsewhere, an arithmetic relation that does not hold, or
a claim whose supporting value is not in any container. Run before every council round.
"""
import io
import json
import os
import re
import sys

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
M = io.open(os.path.join(PAP, "MANUSCRIPT_r445.md"), encoding="utf-8").read()
fails, warns = [], []


# line wrapping must not hide a required sentence, so required patterns match against a copy with
# runs of whitespace collapsed
MN = re.sub(r"\s+", " ", M)

def has(pat, why):
    if not re.search(pat, MN):
        fails.append("MISSING: %s  (%s)" % (pat, why))


def forbid(pat, why):
    for m in re.finditer(pat, M):
        fails.append("FORBIDDEN: %r  (%s)" % (m.group(0)[:70], why))


def near(a, b, tol, why):
    if abs(a - b) > tol:
        fails.append("ARITHMETIC: %.4f vs %.4f  (%s)" % (a, b, why))


# ---------- 1. core values must match the deposit exactly ------------------------------------
d = json.load(io.open(os.path.join(PAP, "IC_KNEE_VS_ANKLE_r439.json"), encoding="utf-8"))["endpoints"]
core = {
    "5.280": abs(d["knee_ic"]["spastic_minus_weakness_deg"]),
    "0.056": abs(d["ankle_ic"]["spastic_minus_weakness_deg"]),
    "2.342": abs(d["ankle_stance"]["spastic_minus_weakness_deg"]),
    "12.4": d["knee_ic"]["effect_in_seed_SDs"],
    "0.425": d["knee_ic"]["within_cell_seed_SD_deg"],
}
for printed, actual in core.items():
    if printed not in M:
        fails.append("MISSING core value %s (deposit says %.4f)" % (printed, actual))
    near(float(printed), actual, 0.02, "printed %s vs deposit" % printed)

# ---------- 2. values the ledger forbids ------------------------------------------------------
forbid(r"1\.6[0-9] ?× ?10", "the binomial p assuming 24 independent trials is withdrawn")
# 1.7e-14 may appear ONLY inside the sentence withdrawing it
for _m in re.finditer(r"1\.7 ?× ?10⁻¹⁴", M):
    if "withdrawn" not in M[_m.start():_m.start()+400]:
        fails.append("FORBIDDEN: withdrawn p quoted without its withdrawal")
forbid(r"4\.29°[^)]{0,40}MDC", "the as-published MDC must not be used as a bar")
forbid(r"10[–-]25°", "the 10-25 deg equinus figure was withdrawn at r454")
forbid(r"MMT 4\+", "the MMT mapping is an inference, not a measurement")
# Cawood Table 5's tone columns are headed BY MUSCLE (CAWOOD_CORRECTION_r450, read from the
# publisher galley and corroborated by that paper's own abstract and Results prose). The values
# 0.542 / 0.321 / 0.492 / 0.745 / 0.672 come from a JATS-XML rendering whose columns are mis-mapped
# and match NEITHER tone column. They were re-introduced at r491 after this guard was removed, and
# the removal was the error. The guard is restored and must not be removed again: if a future round
# believes these values, it must first reconcile them with the source abstract, which reports
# tibialis anterior tone significant at three phases -- something only the by-muscle reading gives.
forbid(r"0\.542|0\.745|0\.672", "Cawood JATS-XML mis-extraction; see CAWOOD_CORRECTION_r450")
has(r"ρ = 0\.362", "the correct gastrocnemius coefficient at initial contact")
has(r"ρ = 0\.662", "the correct tibialis anterior coefficient at initial contact")
has(r"ρ ≥ 0\.79", "the correct n=12 detectable correlation")
forbid(r"ρ ≥ 0\.82", "0.82 was computed on the mis-extracted values")
has(r"subacute", "Cawood's cohort is subacute, not chronic")
# guards carried forward from earlier rounds that a later round dropped and a regression restored
for _m in re.finditer(r"1\.7[–-]2\.1 SD", M):
    if "earlier revision" not in M[max(0, _m.start() - 300):_m.start() + 300]:
        fails.append("FORBIDDEN: 1.7-2.1 SD outside its withdrawal note "
                     "(the 2.1 end comes from the withdrawn 5.7 bar; see revise_r452)")
forbid(r"most dose-symmetric", "DOSE_r174 registers x0.892 as the match, not x0.80")
has(r"35\.5% of the separation", "the unlesioned-side control on the certification metric")
has(r"divergent inside the measurement window", "lateral divergence must be disclosed")
has(r"survival edge are the same edge", "the window edge / survival edge coincidence")
has(r"2\.99–5\.44°", "the mediation knee range must match the 11 surviving pairs")
has(r"anchors, not thresholds", "Kesar's restriction must be applied symmetrically")
forbid(r"12 chronic hemiparetic adults", "Cawood's median is 4.0 months since stroke")
has(r"two one-sided tests|equivalence", "the ankle null must be tested, not asserted")
has(r"95% CI|95% confidence interval", "family-level CIs must be reported")
has(r"cycles 1.5|per-cycle", "the per-cycle stability check must be reported")

# ---------- 2b. values withdrawn at r481-r485: no primary source could be obtained -------------
# Each may appear ONLY inside the sentence that withdraws it. Note the direction: every one was
# adverse to this study, so re-admitting one silently would flatter the paper, not damage it.
for _pat, _why in [
    (r"6\.34", "Geiger knee-minimum MDC, never verified against the source"),
    (r"7\.62", "Geiger largest-knee MDC, never verified against the source"),
    (r"54[–-]76%", "Zeni event-detection rate, contradicted by the source's own figures"),
    (r"0\.490", "Choi coefficient, paywalled and its deposit is metadata-only"),
    (r"0\.482", "Choi coefficient, paywalled and its deposit is metadata-only"),
]:
    for _m in re.finditer(_pat, M):
        if "withdraw" not in M[max(0, _m.start() - 500):_m.start() + 500].lower():
            fails.append("FORBIDDEN: %r outside its withdrawal note  (%s)" % (_m.group(0), _why))
# the only surviving bar for knee-at-contact is 7.25 deg; 5.7 was reinstated at r484 and withdrawn
# again at r493 because KNEE_MDC_BATCHNULL_r399 had already rejected it (treadmill, peak swing)
has(r"Only one value survives as a bar", "the MDC bar must be the single surviving value")
has(r"falls \*\*1\.97°\*\* short", "the shortfall must be against 7.25, not a lowered edge")
has(r"4\.087°[^.]{0,120}falls \*\*3\.16°\*\* short|falls \*\*3\.16°\*\* short",
    "the deflation policy must be applied to the knee comparison too")
has(r"4\.9° for peak ankle angle in swing|peak ankle angle in swing \| 4\.9",
    "Kesar's swing-ankle MDC exists and must be quoted")
forbid(r"nothing\s+published for swing dorsiflexion", "false: Kesar reports 4.9 deg")
has(r"−182", "the fifth duration slope must be reported")
has(r"four-seed bar", "the true reason KV 0.120 is excluded from the duration control")
has(r"7° to 22°", "the induced-equinus counter-result must be stated at full strength")
has(r"11 of the 30 pairs", "the mediation count must be the one that clears the sham floor")
has(r"mediation is not excluded there", "and must report that mediation survives elsewhere")
has(r"0\.586° sham floor", "the mediation count must be tied to the artefact floor")
has(r"r = \+0\.826", "and must report the across-pair correlation that favours mediation")
has(r"may not be used to interpret studies that measure overground gait",
    "Kesar's own restriction on his MDCs must travel with them")
forbid(r"at most 36%|at most about a third", "36% is a mean of heterogeneous slopes, not a bound")

# ---------- 3. arithmetic relations the text asserts ------------------------------------------
near(5.280 / 0.425, 12.42, 0.1, "5.280 / seed SD = 12.4")
near(5.280 / 2.62, 2.02, 0.02, "5.280 / corrected SEM = 2.0")
near(2.342 / 2.53, 0.93, 0.02, "2.342 / ankle SEM = 0.93")
near(1.96 * 3.70, 7.252, 0.01, "1.96 x SD_diff = 7.25")
near(0.2743 * 7.0 / 5.280 * 100, 36.4, 0.5, "duration control = 36%")
near(0.7268 * 7.0 / 5.280 * 100, 96.3, 0.5, "worst family slope = 96%")
near(9.2 * 0.052 / 5.280 * 100, 9.06, 0.3, "speed control = 9%")
near(1 / 462.0, 0.002165, 1e-5, "family permutation floor")
near(36 / 59.0 * 100, 61.0, 0.1, "majority-class baseline = 61%")

# ---------- 4. claims that must travel with their qualification -------------------------------
pairs = [
    ("p = 0.0022", "smallest", "the permutation p must be flagged as the design's resolution floor"),
    ("26.7%", "over.{0,3}estimate", "the batch rate must carry its over-estimate caveat"),
    ("8.83", "grades", "the swing-ankle result must say it grades rather than discriminates"),
    ("98.3%", "61.0%", "accuracy must appear with the majority-class baseline"),
    ("5.28", "sign reversal", "the magnitude must be subordinated to the sign claim"),
    ("single control", "effective n", "the one-control-lineage caveat must be explicit"),
]
for a, b, why in pairs:
    if re.search(a, M) and not re.search(b, M):
        fails.append("UNPAIRED: %r appears without %r  (%s)" % (a, b, why))

# ---------- 5. structural -----------------------------------------------------------------------
lim = M.split("### 4.5 Limitations")[1].split("\n---")[0]
nums = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", lim)]
if nums != list(range(1, len(nums) + 1)):
    fails.append("Limitations are not contiguous: %s" % nums)
body = M.split("## References")[0]
orph = [n for n in range(1, 25)
        if ("[%d]" % n) not in body and ("[%d," % n) not in body and (" %d]" % n) not in body]
if orph:
    fails.append("references cited nowhere in the body: %s" % orph)
# ---------- 5b. reference list integrity (rebuilt from Europe PMC records at r485) -------------
refsec = M.split("## References")[1]
reflines = [l for l in refsec.split(chr(10)) if re.match(r"^\d+\. ", l)]
if len(reflines) != 24:
    fails.append("reference list has %d entries, expected 24" % len(reflines))
for l in reflines:
    if len(l) < 90:
        fails.append("reference looks incomplete (title missing?): %s" % l[:70])
    if not re.search(r"(doi:|PMID )", l):
        fails.append("reference carries no DOI or PMID: %s" % l[:60])

for sec in ["§3.1", "§3.2", "§3.3", "§3.4", "§3.5", "§3.6", "§3.7", "§4.2", "§4.4"]:
    if sec in M and not re.search(re.escape(sec.replace("§", "")) + r"[ ]", M):
        warns.append("cross-reference %s may not resolve" % sec)

# ---------- report ------------------------------------------------------------------------------
w = len(" ".join(l for l in body.split("\n") if not l.strip().startswith("|")).split())
print("manuscript: %d chars, ~%d body words" % (len(M), w))
print("figures: %d" % len([f for f in os.listdir(os.path.join(PAP, "figures"))
                           if f.endswith(".png")]))
print()
for f in fails:
    print("  FAIL  " + f)
for x in warns:
    print("  warn  " + x)
print()
print("=== %d failures, %d warnings ===" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
