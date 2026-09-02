"""Layer 0: trace every figure quoted in the submission back to the file that produced it.

Rewritten after a watchdog audit measured the previous version and found it useless: fed
fabricated two-decimal numbers, 96% of them passed as "sourced". The causes were an
unanchored substring search (0.53 matching inside 10.5301), a rounding test that accepted
any coincidence across 43 files, and an abstract that was silently never scanned.

This version:
  * matches whole numeric tokens only, never substrings
  * scans the abstract and the tables under the same rule as the body
  * ignores superseded result files
  * reports ambiguous attribution instead of silently taking the first hit
  * runs the INVERSE check this project actually keeps failing: figures that exist in a
    result file, are significant, and are NOT printed anywhere in the submission
  * measures and prints its own false-pass rate, so a "clean" verdict can be weighed

Exit code 1 on an actionable failure: a figure with no source, or a significant result on disk
that the submission never prints. The false-pass rate is REPORTED, not gated -- it is a property
of the corpus (2 dp in [0,1) has 100 possible values, most of which occur somewhere), so gating
on it would leave the pipeline permanently red and train everyone to ignore it.
"""
import collections
import glob
import io
import os
import random
import re

MS = "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"
TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"
SUP = "D:/ROWV_paper/SUPPLEMENT_SUBMISSION.md"
RESULTS = "D:/BioCV"

# a decimal figure as it appears in prose: 2-4 dp, optionally signed
NUM = re.compile(r"(?<![\w.])[+\u2212-]?\d+\.\d{2,4}(?![\w.])")
# a whole numeric token inside a result file
TOK = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
DOI_FRAG = re.compile(r"^10\.\d{3,5}$")

KNOWN = {
    "1.4826": "MAD scale constant, defined in the analysis scripts",
    "1.73": "participant stature, participantData.csv",
    "0.175": "distortion coefficient range, .calib files",
    "0.135": "distortion coefficient range, .calib files",
    "1.110": "derived: 3.651 - 2.541, both printed in BIOCV_LOO.txt",
    "0.018": "derived: 0.005 / 28.5 baseline",
    "0.013": "derived: mean objd-vs-reproj cosine gap at matched k, BIOCV_DECORR.txt",
}

PRODUCER = {}
for sc in glob.glob("D:/ROWV_paper/biocv_*.py"):
    src = io.open(sc, encoding="utf-8", errors="replace").read()
    for m in re.finditer(
        r'(?:OUTF|OUT)\s*=\s*(?:os\.environ\.get\([^,]+,\s*)?["\'](D:/BioCV/[^"\']+)["\']', src
    ):
        PRODUCER[os.path.basename(m.group(1))] = os.path.basename(sc)

# superseded outputs must not be able to source a claim
CORPUS = {}
for f in glob.glob(f"{RESULTS}/BIOCV_*.txt"):
    b = os.path.basename(f)
    if b.startswith("_SUPERSEDED") or "SUPERSEDED" in b:
        continue
    CORPUS[b] = io.open(f, encoding="utf-8", errors="replace").read()

TOKENS = {f: set(TOK.findall(c)) for f, c in CORPUS.items()}
ALL_TOKENS = set().union(*TOKENS.values()) if TOKENS else set()


def sources(tok):
    """Files containing tok as a whole token, or as the exact value it rounds from."""
    bare = tok.lstrip("+\u2212-")
    exact = [f for f, ts in TOKENS.items() if bare in ts]
    if exact:
        return exact, "exact"
    dp = len(bare.split(".")[1])
    rounded = [f for f, ts in TOKENS.items()
               if any(round(float(t), dp) == round(float(bare), dp) and len(t.split(".")[1]) > dp
                      for t in ts)]
    return rounded, "rounded"


def scan(path, label):
    text = io.open(path, encoding="utf-8").read()
    found, rounded, ambiguous, known, missing = (
        collections.Counter(), collections.Counter(), [], [], [])
    for tok in sorted(set(NUM.findall(text))):
        bare = tok.lstrip("+\u2212-")
        if DOI_FRAG.match(bare):
            continue
        if bare in KNOWN:
            known.append(bare)
            continue
        srcs, kind = sources(tok)
        if not srcs:
            missing.append(tok)
        else:
            (found if kind == "exact" else rounded)[srcs[0]] += 1
            if len(srcs) > 1:
                ambiguous.append((tok, len(srcs)))
    return found, rounded, ambiguous, known, missing


def false_pass_rate(dp, lo, hi, n=400, seed=7):
    """How often does an invented number pass as sourced?

    An earlier version skipped draws that happened to exist in the corpus, on the reasoning
    that they were "accidentally real". That deflated the figure from 95% to 13% twice over:
    the skipped draws were dropped from the numerator but left in the denominator, and --
    worse -- a fabricated number coinciding with a real token IS the failure mode being
    measured, not an artefact of the measurement. At 2 dp in [0,1) there are only 100 possible
    values and 83 of them occur somewhere in 43 result files, so the check cannot discriminate
    at all in that band. It is measured honestly here and reported as a caveat on the result above.
    """
    rng = random.Random(seed)
    hits = sum(1 for _ in range(n) if sources(f"{rng.uniform(lo, hi):.{dp}f}")[0])
    return hits / n


def unprinted_survivors():
    """The inverse check: BH survivors in a result file that appear nowhere in the paper."""
    # The supplement counts as printed: S1 lists the whole m=50 family verbatim, which is
    # where contrasts the main tables do not display are meant to be auditable.
    printed = "".join(io.open(p, encoding="utf-8").read() for p in (MS, TB, SUP)
                      if os.path.exists(p))
    out = []
    for f in ("BIOCV_INTERACTION_FDR.txt", "BIOCV_PERM_V3.txt"):
        if f not in CORPUS:
            continue
        for line in CORPUS[f].split("\n"):
            if "SURVIVES" not in line:
                continue
            nums = TOK.findall(line)
            if not nums:
                continue
            eff = nums[-3] if len(nums) >= 3 else nums[0]
            label = " ".join(line.split()[:5])
            if eff not in printed and eff.lstrip("0") not in printed:
                out.append((f, label, eff))
    return out


exit_code = 0
for path, label in [(MS, "MANUSCRIPT (incl. abstract)"), (TB, "TABLES")]:
    found, rounded, ambiguous, known, missing = scan(path, label)
    total = sum(found.values()) + sum(rounded.values()) + len(known) + len(missing)
    print(f"=== {label}: {total} distinct decimal figures ===")
    for f, n in found.most_common():
        print(f"  {n:>4} exact   {f:<30}({PRODUCER.get(f, 'producer unknown')})")
    for f, n in rounded.most_common():
        print(f"  {n:>4} rounded {f}")
    if known:
        print(f"  {len(known):>4} documented constants / non-result sources")
    if ambiguous:
        print(f"  {len(ambiguous):>4} match more than one result file (attribution not unique)")
    if missing:
        exit_code = 1
        print(f"  {len(missing):>4} *** NO SOURCE FOUND ***")
        print("       " + ", ".join(missing))
    else:
        print("     0 with no source")
    print()

print("=== discriminating power of this checker (fabricated numbers that pass) ===")
worst = 0.0
for dp, lo, hi, what in [(2, 0, 1, "2 dp, 0-1   (angle effects, %)"),
                         (2, 0, 10, "2 dp, 0-10  (mm effects)"),
                         (3, 0, 1, "3 dp, 0-1"),
                         (4, 0, 1, "4 dp, 0-1   (q-values)")]:
    r = false_pass_rate(dp, lo, hi)
    worst = max(worst, r)
    flag = "  <- weak" if r > 0.25 else ""
    print(f"  {what:<32}{r:>6.0%}{flag}")
if worst > 0.25:
    print()
    print("  READ THIS BEFORE QUOTING THE RESULT ABOVE. At these bands the check cannot")
    print("  discriminate: 2 dp in [0,1) has only 100 possible values and most of them occur")
    print("  somewhere in the corpus, so '0 with no source' is close to unfalsifiable there.")
    print("  It is a property of the corpus, not a defect to fix, so it does not fail this")
    print("  run -- but a clean Layer 0 is NOT evidence for any 2-3 dp figure. Those need")
    print("  check_signs.py and a line-by-line read of prose against artefacts.")
print()

print("=== inverse check: significant results present on disk but absent from the paper ===")
un = unprinted_survivors()
if un:
    exit_code = 1
    for f, lab, eff in un:
        print(f"  {eff:>10}  {lab:<46}({f})")
else:
    print("  none")

raise SystemExit(exit_code)
