"""Benjamini-Hochberg over the posture family.

BIOCV_POSTURE.txt runs thirteen sign-flip tests -- the x, y, z components, the magnitude |off|
and, at the knee, the flexion-sensitive component, each as a highest-minus-lowest flexion
quintile difference at hip, knee and ankle. Table 3c, Figure 4 and Section 3.4 quoted the bare
unadjusted p-values from those tests. Every other family in the paper is multiplicity-controlled;
a cold reader pointed out that this was the one place the discipline lapsed, and it supports a
headline sentence ("the offset is not constant within a participant").

The family is the thirteen tests as run. It is corrected separately from the contrast families
because it asks a different question -- whether a nuisance quantity varies with posture -- rather
than whether an intervention helps.

Input : D:/BioCV/BIOCV_POSTURE.txt
Output: D:/BioCV/BIOCV_POSTURE_FDR.txt
"""
import io
import re

SRC = "D:/BioCV/BIOCV_POSTURE.txt"
OUTF = "D:/BioCV/BIOCV_POSTURE_FDR.txt"

JOINT = re.compile(r"^---\s*(hip|knee|ankle)\s*---")
ROW = re.compile(r"most-extended bin minus most-flexed,\s*(\S+):\s*([+-]?\d+\.\d+)\s*mm\s*"
                 r"exact p = (\d\.\d+)")

rows, joint = [], "?"
for line in io.open(SRC, encoding="utf-8", errors="replace"):
    j = JOINT.match(line.strip())
    if j:
        joint = j.group(1)
        continue
    m = ROW.search(line)
    if m:
        rows.append((joint, m.group(1).rstrip(":"), float(m.group(2)), float(m.group(3))))

if len(rows) != 13:
    raise SystemExit(f"expected 13 posture tests, parsed {len(rows)} -- check {SRC}")

ps = [r[3] for r in rows]
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


out("BENJAMINI-HOCHBERG OVER THE POSTURE FAMILY")
out(f"Family size m = {m}: the highest-minus-lowest flexion-quintile difference for each offset")
out("component at each lower-limb joint, exactly as run in BIOCV_POSTURE.txt.")
out("")
out("|off| is the offset MAGNITUDE, which is rotation-invariant: binning it by flexion is not")
out("circular. 'flex-sens' is the component resolved on the hip-ankle chord, whose orientation is")
out("set by the flexion angle used to form the bins, so that row IS circular and is reported here")
out("for completeness rather than as evidence.")
out("")
out(f"{'joint':>7}{'component':>12}{'diff mm':>10}{'p':>9}{'BH q':>9}  verdict")
for (j, comp, d, p), qq in sorted(zip(rows, q), key=lambda t: t[0][3]):
    v = "SURVIVES" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    flag = "  [circular]" if comp.startswith("flex") else ""
    out(f"{j:>7}{comp:>12}{d:>+10.2f}{p:>9.4f}{qq:>9.4f}  {v}{flag}")

surv = sum(1 for qq in q if qq < 0.05)
raw = sum(1 for p in ps if p < 0.05)
out("")
out(f"{surv} of {m} survive BH; {raw} were significant unadjusted.")
out("")
out("Any claim in the manuscript resting on a contrast that does not survive must be restated as")
out("exploratory, and the |off| rows are the ones the posture argument should rest on.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
