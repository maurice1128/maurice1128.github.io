"""What happens if the five inferential families are pooled into one correction?

The manuscript declares five families and corrects within each: the main contrast family
the main contrasts, the position-versus-angle interactions, the per-joint decomposition,
the posture analysis and the joint-set interactions. Each is defended on the grounds that it
answers a different question. Sizes are counted from the files and printed in the output; naming
them here is what made every earlier copy go stale. A referee will reasonably suspect that
splitting families inflates survival, and the paper should answer that before being asked.

This script recomputes Benjamini-Hochberg over the union and reports exactly which
verdicts change. It does not argue that pooling is correct -- the families test different
questions on partly overlapping observations, and pooling them is conservative to the point of
being wrong in a different way. It reports the consequence so the reader can weigh it.

Note on overlap: the per-joint family already excludes the pooled [pos:HKA] rows because those
live in the m = 50 family, and the joint-set family is computed from the same per-participant
means as the m = 50 family rather than from a separate pass. Pooling therefore double-counts
information in places, which is one reason the manuscript does not adopt it.

Output: D:/BioCV/BIOCV_POOLED_SENSITIVITY.txt
"""
import io
import re

OUTF = "D:/BioCV/BIOCV_POOLED_SENSITIVITY.txt"

FAMILIES = [
    ("main contrasts",       "D:/BioCV/BIOCV_PERM_V3.txt",
     re.compile(r"^(.{15,72}?)\s{2,}\d+\s+([+-]\d+\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+"
                r"(SURVIVES FDR|raw only|n\.s\.)")),
    ("position vs angle",    "D:/BioCV/BIOCV_INTERACTION_FDR.txt",
     re.compile(r"^(.{10,60}?)\s{2,}[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)")),
    ("per-joint",            "D:/BioCV/BIOCV_PERJOINT_FDR.txt",
     re.compile(r"^(.{10,60}?)\s{2,}(?:hip|knee|ankle)\s+\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)")),
    ("posture",               "D:/BioCV/BIOCV_POSTURE_FDR.txt",
     re.compile(r"^\s*(?:hip|knee|ankle)\s+(\S+)\s+[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)\s+"
                r"(SURVIVES|raw only|n\.s\.)")),
    ("joint set vs joint set", "D:/BioCV/BIOCV_JOINTSET_FDR.txt",
     re.compile(r"^(.{10,50}?)\s{2,}\d+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)")),
    # The within-limb control. Its three parts were previously in no family at all -- Part C
    # was printed with uncorrected p -- so "the union of all five" excluded the analysis
    # section 3.1 rests on. Each part is a separate family and all three enter the union.
    ("within-limb: membership, %", "D:/BioCV/BIOCV_SUBSET_CONTROL.txt",
     re.compile(r"^(.{10,34}?)\s{2,}[yn]\s+(\S+)\s{2,}\S+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)"),
     "=== PART A", "=== PART B"),
    ("within-limb: membership, mm", "D:/BioCV/BIOCV_SUBSET_CONTROL.txt",
     re.compile(r"^(.{10,34}?)\s{2,}[yn]\s+(\S+)\s{2,}\S+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)"),
     "=== PART B", "=== PART C"),
    # The dose-response. It was quoted in the Conclusion and in Practical implications with no
    # test at all -- four pooled means, no p, no q, no n -- which two cold readers found
    # independently. Six steps, corrected within themselves, and now inside the union.
    ("dose-response", "D:/BioCV/BIOCV_DOSE_RESPONSE.txt",
     re.compile(r"^(.{10,24}?)\s{2,}\d\s+\d+\.\d+\s+\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)")),
    ("within-limb: subset alone", "D:/BioCV/BIOCV_SUBSET_CONTROL.txt",
     re.compile(r"^(.{10,34}?)\s{2,}[yn]\s+(\S+)\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)"),
     "=== PART C", None),
    # The offset control. It entered the abstract while sitting outside every multiplicity
    # sensitivity, which a reviewer identified as the one uncovered claim in the paper.
    # Both reference arms are pooled into one family here rather than corrected separately,
    # which is stricter than the m = 12 and m = 4 the manuscript declares.
    ("offset control: per-joint", "D:/BioCV/BIOCV_OFFSET_CONFOUND.txt",
     # The declared verdict for this family is the MIDPOINT estimate; the two single-arm columns
     # are the endpoints of a known bias shown for reference, not separate tests, and counting
     # all three tripled this family's size in the correction.
     re.compile(r"^(.{10,60}?\s+(?:hip|knee|ankle)\s+midpoint)\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|n\.s\.)"),
     "=== (A)", "=== (B)"),
    ("offset control: per-subset", "D:/BioCV/BIOCV_OFFSET_CONFOUND.txt",
     re.compile(r"^\s+(\S+\s+[+-]\d+\.\d+\s+(?:1st|2nd) arm)\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|n\.s\.)"),
     "=== (C)", "=== (F)"),
    # The reversal the title asserts, tested as a difference rather than as a pair of verdicts,
    # added in response to review with its reading fixed before the numbers existed.
    ("offset control: reversal test", "D:/BioCV/BIOCV_OFFSET_CONFOUND.txt",
     re.compile(r"^(.{10,60}?\s+(?:hip|knee|ankle))\s+[+-]\d+\.\d+\s+"
                r"[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|n\.s\.)"),
     "=== (G)", None),
    # Declared with the experiments they belong to, after the eleven above, so both sensitivities
    # originally excluded them and the manuscript said so without drawing the consequence. A
    # family of two is barely a family; a reviewer is entitled to see it inside the union.
    ("estimator x rejection", "D:/BioCV/BIOCV_EST_REJ_INTERACTION.txt",
     re.compile(r"^(\S.{6,28}?)\s{2,}\d+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+[+-]\d+\.\d+\s+"
                r"\[[^\]]+\]\s+\[[^\]]+\]\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|n\.s\.)")),
    ("shank-foot angle", "D:/BioCV/BIOCV_HALPE.txt",
     re.compile(r"^(none vs .{4,44}?|uniform vs confidence weighting)\s{2,}[+-]\d+\.\d+\s+"
                r"(\d\.\d+)\s+(\d\.\d+)\s+\d+\s+(SURVIVES|n\.s\.|NO VERDICT.*)")),
]

rows = []
for spec in FAMILIES:
    fam, path, pat = spec[0], spec[1], spec[2]
    # Three families share one artefact and are separated by its PART markers, so a family
    # may carry a (start, end) slice. Without it the within-limb parts would pool into one.
    start, end = (spec[3], spec[4]) if len(spec) == 5 else (None, None)
    text = io.open(path, encoding="utf-8", errors="replace").read()
    if start:
        text = text[text.index(start):]
        if end:
            text = text[: text.index(end)]
    n = 0
    for line in text.splitlines():
        m = pat.match(line.rstrip())
        if not m:
            continue
        g = m.groups()
        label, p, q, verdict = g[0], float(g[-3]), float(g[-2]), g[-1]
        rows.append([fam, " ".join(label.split()), p, q, verdict.startswith("SURVIVES"),

                     verdict.strip()])
        n += 1
    if n == 0:
        raise SystemExit(f"parsed no rows from {path} -- the format must have changed")

# The veto split must precede everything that counts rows: the family sizes, the pooled m, the
# change list and the survivor totals. Splitting it later left the change list and the family
# listing on 229 rows while the totals ran on 227, so the two could not be reconciled.
# A row whose artefact printed NO VERDICT was withheld by a rule declared with the outcome, not
# judged non-significant. An earlier version of this file collapsed the two and reported the
# veto as "the artefact said n.s.", which misattributed the reconciliation gap.
VETO = [r for r in rows if str(r[5]).startswith("NO VERDICT")]
rows = [r for r in rows if not str(r[5]).startswith("NO VERDICT")]

m_tot = len(rows)
ps = [r[2] for r in rows]
order = sorted(range(m_tot), key=lambda i: ps[i])
qq = [0.0] * m_tot
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    k = m_tot - rank + 1
    prev = qq[i] = min(prev, ps[i] * m_tot / k)

L = []


def out(s):
    print(s)
    L.append(s)


sizes = {}
for r in rows:
    sizes[r[0]] = sizes.get(r[0], 0) + 1

out(f"POOLING ALL {len(FAMILIES)} INFERENTIAL FAMILIES INTO ONE BH CORRECTION")
out("")
out(f"The manuscript corrects within {len(FAMILIES)} declared families. This is the consequence of the")
out("alternative convention -- one correction over their union -- reported so that a reader can")
out("judge whether the split inflates survival.")
out("")
for fam, n in sizes.items():
    out(f"  {fam:<30}m = {n}")
out(f"  {'POOLED':<30}m = {m_tot}")
out("")

changed = [(r, q) for r, q in zip(rows, qq) if r[4] != (q < 0.05)]
out(f"{len(changed)} of {m_tot} contrasts change verdict when pooled.")
out("")
if changed:
    out(f"{'family':<30}{'contrast':<50}{'p':>9}{'own q':>9}{'pooled q':>10}")
    for r, q in sorted(changed, key=lambda t: t[0][2]):
        out(f"{r[0]:<30}{r[1][:48]:<50}{r[2]:>9.4f}{r[3]:>9.4f}{q:>10.4f}"
        f"  {'gains' if q < 0.05 else 'loses'}")
    out("")
    out("A row whose q RISES above 0.05 under pooling loses a verdict its own family granted,")
    out("A row whose q FALLS below 0.05 gains a verdict the split correction withheld. Compare")
    out("each row's own q with its pooled q: the two directions are not interchangeable.")

surv_own = sum(1 for r in rows if r[4])
surv_pool = sum(1 for q in qq if q < 0.05)

# Two counts of "survivors within declared families" are possible and they are not the same
# number: the verdict each ARTEFACT printed, and a Benjamini-Hochberg recomputation from the
# raw p within the family this file assigns. Where an artefact corrected over a family of a
# different size from the one declared here, the two disagree, and reporting only one of them
# left this file contradicting Table S5 by two contrasts with no way for a reader to find which.
_byfam = {}
for r in rows:
    _byfam.setdefault(r[0], []).append(r)
surv_recomp, disagree = 0, []
for fam, rs in _byfam.items():
    ps = [r[2] for r in rs]   # r[2] is the raw p; r[3] is the artefact q
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))
    for i, r in enumerate(rs):
        if q[i] < 0.05:
            surv_recomp += 1
        if (q[i] < 0.05) != bool(r[4]):
            disagree.append((fam, r[1], r[2], q[i], bool(r[4])))
out("")
out(f"survivors, as each artefact printed the verdict:            {surv_own}")
out(f"survivors, recomputing BH from p within the declared family: {surv_recomp}")
out(f"survivors under one pooled correction over m = {len(rows)}:            {surv_pool}")
if disagree:
    out("")
    out(f"{len(disagree)} contrast(s) where the artefact's own verdict and the recomputation differ,")
    out("because the artefact corrected over a family of a different size from the one declared here:")
    for fam, lab, pv, qv, printed in disagree:
        out(f"  {fam:<28}{lab[:40]:<42}p={pv:.4f}  recomputed q={qv:.4f}  "
            f"artefact said {'SURVIVES' if printed else 'n.s.'}")
out("")
if VETO:

    out("")

    out(f"{len(VETO)} contrast(s) carry NO VERDICT in their artefact because a rule declared with")

    out("the outcome withheld one, not because any correction disagreed. They are excluded from")

    out("every count above:")

    for r in VETO:

        out(f"  {r[0]:<28}{r[1][:40]:<42}p={r[2]:.4f}  own q={r[3]:.4f}  artefact: {r[5]}")

    out("")

out("CAVEAT ON POOLING. The declared families test different questions on partly overlapping")
out("observations: the per-joint family excludes the pooled [pos:HKA] rows precisely because")
out("those belong to the main family, and the joint-set interactions are computed from the same")
out("per-participant means as the main family rather than from an independent pass. Pooling")
out("therefore double-counts information and is conservative in a way that is not principled,")
out("which is why the manuscript does not adopt it. It is reported because a reader is entitled")
out("to see what the stricter convention would do.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
