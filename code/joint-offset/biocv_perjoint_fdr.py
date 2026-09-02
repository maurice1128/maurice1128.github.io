"""Benjamini-Hochberg correction over the per-joint family.

Table 1b -- and with it the manuscript's headline finding, that the object-space criterion
improves the hip and degrades the knee "both p = 0.002" -- was reported as "exact sign-flip p,
uncorrected, within this analysis". A cold reader pointed out that this leaves the single most
important number in the paper held to a looser standard than every other number in it, and
belonging to no declared family, while the manuscript's own superseded family file states the
rule: "Any claim resting on a 'raw only' contrast must be withdrawn or restated as exploratory."

This script declares that family and corrects within it. The family is the twelve per-joint
tests: four interventions (adaptive criterion, criterion at matched k=1 and k=2, uniform ->
confidence) crossed with the three lower-limb joints (hip, knee, ankle). The pooled `posl` rows
are excluded because they already sit in the m=50 family; including them would double-count.

The per-joint family is kept separate from the m=50 family for the same reason the interaction
family is: it answers a different question -- not "does this intervention help?" but "where does
its effect land?" -- and the manuscript reports the consequence of pooling instead.

Input : D:/BioCV/BIOCV_PERJOINT_GN.txt  (Part 1)
Output: D:/BioCV/BIOCV_PERJOINT_FDR.txt
"""
import io
import re

SRC = "D:/BioCV/BIOCV_PERJOINT_GN.txt"
OUTF = "D:/BioCV/BIOCV_PERJOINT_FDR.txt"

ROW = re.compile(
    r"^(.{10,44}?)\s{2,}(hip|knee|ankle)\s+(\d+\.\d+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+(\d\.\d+)\s*$"
)

txt = io.open(SRC, encoding="utf-8").read()
marker = "=== (1) PER-JOINT"
if marker not in txt:
    raise SystemExit(f"marker {marker!r} not found in {SRC}")
block = txt[txt.index(marker):]
if "=== (2)" in block:
    block = block[: block.index("=== (2)")]

rows = []
for line in block.split("\n"):
    m = ROW.match(line.rstrip())
    if m:
        rows.append((" ".join(m.group(1).split()), m.group(2), float(m.group(3)),
                     float(m.group(4)), float(m.group(5)), float(m.group(6))))

if len(rows) != 12:
    raise SystemExit(f"expected 12 per-joint rows (4 interventions x 3 joints), parsed {len(rows)}")

ps = [r[5] for r in rows]
m = len(ps)
order = sorted(range(m), key=lambda i: ps[i])
q = [0.0] * m
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    k = m - rank + 1
    prev = q[i] = min(prev, ps[i] * m / k)

L = []


def out(s):
    print(s)
    L.append(s)


out("BENJAMINI-HOCHBERG OVER THE PER-JOINT FAMILY")
out(f"Family size m = {m}: four interventions x three lower-limb joints. Exact sign-flip")
out(f"p-values taken verbatim from {SRC} (Part 1). The pooled [pos:HKA] rows are excluded")
out("because they belong to the m=50 family; including them would double-count.")
out("")
out("POSITIVE effect = the second-named arm has the lower error at that joint.")
out("")
out(f"{'intervention':<30}{'joint':>7}{'baseline':>10}{'effect mm':>11}{'rel %':>8}"
    f"{'p':>9}{'BH q':>9}  verdict")
for (lab, joint, base, eff, rel, p), qq in sorted(zip(rows, q), key=lambda t: t[0][5]):
    v = "SURVIVES" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    out(f"{lab:<30}{joint:>7}{base:>10.2f}{eff:>+11.3f}{rel:>+8.2f}{p:>9.4f}{qq:>9.4f}  {v}")

surv = sum(1 for qq in q if qq < 0.05)
raw = sum(1 for p in ps if p < 0.05)
out("")
out(f"{surv} of {m} survive BH; {raw} were significant unadjusted.")
if surv == raw:
    out("Every per-joint effect significant unadjusted also survives correction.")
else:
    out("Contrasts significant unadjusted that do not survive correction are exploratory.")
out("")
out("NOTE ON THE HEADLINE PAIR: the criterion at matched k=2 improves the hip and degrades the")
out("knee, and the manuscript quotes both. Their corrected q-values are printed above and the")
out("manuscript should quote those, not the unadjusted p.")
out("")
out("NOTE ON SIGN: the adaptive criterion and the criterion at matched k=2 act on the knee in")
out("OPPOSITE directions -- adaptive improves it, matched-k degrades it, both at small p. The")
out("mechanism account is therefore specific to the retention rule and the manuscript must say")
out("so wherever it states the mechanism.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
