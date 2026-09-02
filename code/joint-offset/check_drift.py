"""Catch the one defect class this project keeps recommitting: upstream changed, downstream did not.

Four instances so far. A denominator was corrected in the interaction family and not in the eight
prose quantities that quote it. Figure 1's nine rows were hardcoded and kept an abandoned
convention after the family was recomputed. Figure 2 hardcoded twelve unadjusted p-values and went
on marking a contrast significant after the paper had restated it as exploratory. The slide deck
quoted p where the manuscript had moved to q.

Each was found by a person reading, one at a time, a round after the change. This finds them
mechanically: a number that rounds to a SUPERSEDED artefact and to no current one is, by
construction, a value left behind when its family was recomputed.

Rounding must be allowed -- the paper quotes 9.85 for 9.848 and q = 0.006 for 0.0059 -- but only
against current artefacts. That asymmetry is the whole design. It is deliberately not a provenance
check: `provenance.py` answers "does this number exist anywhere?", which at two decimal places this
corpus cannot answer usefully. This answers the narrower and much sharper question "does this
number still exist?".

Layout constants are excluded by construction: in scripts, only numbers inside string literals
count, because a result is something a file SAYS, not something it positions.
"""
import ast
import glob
import io
import os
import re

RESULTS = "D:/BioCV"
DOCS = [
    "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md",
    "D:/ROWV_paper/TABLES_SUBMISSION.md",
    "D:/ROWV_paper/SUPPLEMENT_SUBMISSION.md",
    "D:/ROWV_paper/COVER_LETTER.md",
]
SCRIPTS = [
    "D:/ROWV_paper/biocv_figures.py",
    "D:/ROWV_paper/build_pptx.py",
    "D:/ROWV_paper/build_docx.py",
    "D:/ROWV_paper/render_table2c.py",
]

MINUS = "\u2212"
NUM = re.compile(r"(?<![\w.])[+" + MINUS + r"-]?\d+\.\d{2,4}(?![\w.])")
TOK = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
DOI = re.compile(r"^10\.\d{3,5}$")
# A line may quote a superseded value on purpose, to record what changed. The marker has
# to be in the same line, so a genuine leftover cannot inherit the exemption.
SUPERSESSION = re.compile(r"supersed|earlier version|abandoned|moves from|no longer", re.I)

# Quantities that are real but come from outside the result corpus. Each needs a reason.
KNOWN = {
    "26.0": "hip-centre prediction bound, Bell et al. (1989), read from the paper",
    "33.0": "hip-centre prediction bound, Bell et al. (1989), read from the paper",
    "3.60": "hip joint-centre RMSD, Kanko et al. (2021), read from the paper",
    "2.20": "knee joint-centre RMSD, Kanko et al. (2021), read from the paper",
    "2.40": "ankle joint-centre RMSD, Kanko et al. (2021), read from the paper",
    "4.16": "smallest sagittal knee MDC, Wilken et al. (2012) Table 1, read from the paper",
    "6.39": "largest sagittal knee MDC, Wilken et al. (2012) Table 1, read from the paper",
    "1.4826": "MAD scale constant, defined in the analysis scripts",
    "26.2": "participant age, dataset paper (Evans et al., 2024)",
    "75.3": "participant mass, dataset paper",
    "16.8": "participant mass SD, dataset paper",
    "1.73": "participant stature, dataset paper",
    "0.12": "participant stature SD, dataset paper",
    "3.62": "cross-system alignment error, dataset documentation",
    "10.15125": "dataset DOI fragment",
}


def tokens_of(path):
    return set(TOK.findall(io.open(path, encoding="utf-8", errors="replace").read()))


current, superseded = set(), {}
for _f in glob.glob(os.path.join(RESULTS, "*.txt")):
    _b = os.path.basename(_f)
    if _b.startswith(("_SUPERSEDED", "_OLD_", "_GOLDEN_")):
        for _t in tokens_of(_f):
            superseded.setdefault(_t, []).append(_b)
    elif _b.startswith("BIOCV_"):
        current |= tokens_of(_f)

stale_only = {t: s for t, s in superseded.items() if t not in current}
CUR_F = [float(t) for t in current]
STALE_F = {t: [float(t)] for t in stale_only}


def rounds_into(bare, pool_floats):
    dp = len(bare.split(".")[1])
    target = round(float(bare), dp)
    return any(round(v, dp) == target for v in pool_floats)


def classify(tok):
    bare = tok.lstrip("+" + MINUS + "-")
    if DOI.match(bare) or bare in KNOWN:
        return None
    if bare in current or rounds_into(bare, CUR_F):
        return None
    if bare in stale_only or rounds_into(bare, [v for vs in STALE_F.values() for v in vs]):
        srcs = stale_only.get(bare) or ["a superseded artefact"]
        return "STALE \u2014 matches only " + ", ".join(sorted(set(srcs)))
    return "UNSOURCED \u2014 in no artefact"


def strings_in(script):
    """Every string literal in a Python file, so layout geometry is out of scope."""
    try:
        tree = ast.parse(io.open(script, encoding="utf-8").read())
    except SyntaxError as e:
        return None, str(e)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append((getattr(node, "lineno", 0), node.value))
    return out, None


stale, unsourced, broken = [], [], []

for doc in DOCS:
    if not os.path.exists(doc):
        broken.append((os.path.basename(doc), "file missing"))
        continue
    for i, line in enumerate(io.open(doc, encoding="utf-8").read().split("\n"), 1):
        # A superseded value may be quoted deliberately, to document what changed. That is the
        # opposite of drift and must not be flagged -- but only when the text says so in the
        # same breath, so that an actual leftover cannot hide behind the exemption.
        if SUPERSESSION.search(line):
            continue
        for tok in NUM.findall(line):
            v = classify(tok)
            if v:
                (stale if v.startswith("STALE") else unsourced).append(
                    (os.path.basename(doc), i, tok, v, line.strip()[:78]))

for sc in SCRIPTS:
    if not os.path.exists(sc):
        broken.append((os.path.basename(sc), "file missing"))
        continue
    lits, err = strings_in(sc)
    if err:
        broken.append((os.path.basename(sc), "does not parse: " + err))
        continue
    for lineno, text in lits:
        if not re.search(r"mm|\u00b0|deg|%|[pq] ?= ?", text):
            continue                      # not a stated result
        for tok in NUM.findall(text):
            v = classify(tok)
            if v:
                (stale if v.startswith("STALE") else unsourced).append(
                    (os.path.basename(sc), lineno, tok, v, text.strip()[:78]))

print("=== derived-value drift ===")
print(f"{len(current)} distinct values across the current artefacts; "
      f"{len(stale_only)} exist only in a superseded one")
print()

for title, items in (("STALE \u2014 left behind by a recomputation", stale),
                     ("stated as a result but in no artefact", unsourced)):
    if items:
        print(f"{len(items)} {title}:")
        for f, i, tok, why, ctx in items:
            print(f"  {f}:{i}  {tok}   {why}")
            print(f"      {ctx}")
        print()

if broken:
    print("could not check:")
    for f, why in broken:
        print(f"  {f}: {why}")
    print()

if not stale and not unsourced and not broken:
    print("no downstream file states a result the artefacts no longer support")

# A value stated as a result but present in NO artefact is the most serious of the three
# categories -- it is a number with no provenance at all -- and for a long time it only
# printed, because the exit status omitted it. Every routine "did the checker pass" reading
# of this file, including the injection harness, therefore scored it as clean.
raise SystemExit(1 if (stale or unsourced or broken) else 0)
