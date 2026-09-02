"""Every q-value written in prose must exist in a current artefact.

This is the check that should have existed eight recurrences ago. The pattern each time was the
same, and a watchdog audit named it exactly: everything the pipeline READS is right, everything
typed is stale. Tables 1(c) and 2(c) are generated from the artefacts and have been correct since
they were automated; the sentences beside them are typed by hand and go stale every time a family
is recomputed. Adding one contrast to the interaction family changed every q in it, and eight
manuscript q-values kept their old values while the table beside them updated.

The check is deliberately narrow. It does not try to verify effect sizes or percentages -- at two
decimal places this corpus cannot discriminate, as `provenance.py` reports of itself. It verifies
q-values only, which are three or four decimals, are distinctive, and are exactly the quantity that
goes stale when a family changes size.

A prose q matches if some artefact q rounds to it at the precision it is written to. Anything else
is reported with the nearest artefact values, so the fix is visible rather than a hunt.
"""
import glob
import io
import os
import re

DOCS = ["D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md",
        "D:/ROWV_paper/TABLES_SUBMISSION.md"]
RESULTS = "D:/BioCV"

# "q = 0.004", "q ≤ 0.009", "q = 0.011-0.028" (a range: both ends must exist)
QVAL = re.compile(r"q\s*(?:=|\u2264|<)\s*(\d\.\d{2,4})(?:\s*[\u2013-]\s*(\d\.\d{2,4}))?")
# a q column in a result file: the last two decimals on a verdict line
ARTQ = re.compile(r"(\d\.\d{3,4})\s+(?:SURVIVES|raw only|n\.s\.)")


def artefact_qs():
    out = set()
    for f in glob.glob(os.path.join(RESULTS, "BIOCV_*.txt")):
        if "SUPERSEDED" in f:
            continue
        for m in ARTQ.finditer(io.open(f, encoding="utf-8", errors="replace").read()):
            out.add(float(m.group(1)))
    return sorted(out)


QS = artefact_qs()
if not QS:
    raise SystemExit("no q-values found in any artefact -- check the result-file format")


def matches(text_q):
    dp = len(text_q.split(".")[1])
    target = round(float(text_q), dp)
    return [q for q in QS if round(q, dp) == target]


bad, coarse = [], []
for doc in DOCS:
    for i, line in enumerate(io.open(doc, encoding="utf-8").read().split("\n"), 1):
        for m in QVAL.finditer(line):
            for tq in (g for g in m.groups() if g):
                if len(tq.split(".")[1]) < 3:
                    # At two decimals this corpus cannot discriminate -- most two-decimal
                    # values occur somewhere -- so such a q is unverifiable rather than
                    # verified. Write q to three decimals or more.
                    coarse.append((os.path.basename(doc), i, tq, line.strip()[:74]))
                    continue
                if matches(tq):
                    continue
                near = sorted(QS, key=lambda q: abs(q - float(tq)))[:3]
                bad.append((os.path.basename(doc), i, tq, near, line.strip()[:74]))

print(f"{len(QS)} distinct q-values across the current artefacts")
if coarse:
    print(f"{len(coarse)} q-value(s) written to two decimals, which cannot be verified:")
    for f, i, tq, ctx in coarse:
        print(f"  {f}:{i}  q = {tq}")
        print(f"      {ctx}")
if bad:
    print(f"{len(bad)} q-value(s) in prose that no artefact supports:")
    for f, i, tq, near, ctx in bad:
        print(f"  {f}:{i}  q = {tq}   nearest in artefacts: "
              + ", ".join(f"{n:.4f}" for n in near))
        print(f"      {ctx}")
    raise SystemExit(1)
if coarse:
    raise SystemExit(1)
print("every q-value written in prose is supported by a current artefact")
