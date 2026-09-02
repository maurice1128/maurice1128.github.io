"""What survives if the dependence among our tests is arbitrary rather than positive?

Section 2.5 controls multiplicity with Benjamini-Hochberg. BH's 1995 proof assumes independent
test statistics; our contrasts within a family share arms, participants and baselines, so they are
dependent by construction. Section 2.5 appeals to the extension to positive regression dependence
(Benjamini and Yekutieli, 2001), and a cold reader made the fair objection that PRDS is asserted
there rather than shown -- and that it is load-bearing, because the same family mixes position and
angle contrasts that the paper's central claim says move in OPPOSITE directions.

We cannot verify PRDS for this design. What we can do is report the price of not assuming it. The
same paper gives a procedure valid under ARBITRARY dependence: multiply the BH threshold by
H_m = sum_{i=1..m} 1/i. That is very conservative -- H_50 is about 4.50 -- and it is not what the
manuscript adopts. It is computed here so that a reader can see exactly which claims rest on BH
alone, rather than being told the dependence question has been settled.

Output: D:/BioCV/BIOCV_BY_SENSITIVITY.txt
"""
import glob
import io
import os
import re

RES = "D:/BioCV"
OUTF = "D:/BioCV/BIOCV_BY_SENSITIVITY.txt"

FAMILIES = {
    "BIOCV_PERM_V3.txt": "main contrasts",
    "BIOCV_INTERACTION_FDR.txt": "position vs angle",
    "BIOCV_JOINTSET_FDR.txt": "joint set vs joint set",
    "BIOCV_PERJOINT_FDR.txt": "per-joint",
    "BIOCV_POSTURE_FDR.txt": "posture",
    "BIOCV_DOSE_RESPONSE.txt": "dose-response",
    # Declared with the experiments they belong to, after the eleven above, so both
    # sensitivities originally excluded them. A family of two is barely a family, and a
    # reviewer is entitled to see what arbitrary dependence does to it.
    "BIOCV_EST_REJ_INTERACTION.txt": "estimator x rejection",
    "BIOCV_HALPE.txt": "shank-foot angle",
}
# The within-limb artefact holds three families separated by PART markers.
PARTS = [("within-limb: membership, %", "=== PART A", "=== PART B"),
         ("within-limb: membership, mm", "=== PART B", "=== PART C"),
         ("within-limb: subset alone", "=== PART C", None)]
# The offset control lives in its own artefact and is sliced the same way. Both reference
# arms are pooled into one family here rather than corrected separately, which is stricter
# than the m = 12 and m = 4 the manuscript declares.
# Part (C) prints before (F) and (G) in the artefact, so an open-ended (C) slice swallowed the
# reversal test added in response to review and inflated this family from 16 rows to 34.
OFFSET_PARTS = [("offset control: per-joint", "=== (A)", "=== (B)"),
                ("offset control: per-subset", "=== (C)", "=== (F)"),
                ("offset control: reversal test", "=== (G)", None)]

VERDICT = re.compile(r"^(.*?)\s{2,}([+-]?\d+\.\d+)\s+(\d\.\d{3,4})\s+(\d\.\d{3,4})\s+"
                     r"(SURVIVES(?: FDR)?|raw only|n\.s\.)\s*(\[[^\]]+\])?\s*$")


# Two artefacts declared after the eleven print their rows in a different order: the
# estimator-by-rejection table puts BOTH intervals between the effect and the p, and the
# shank-foot table puts an n column between the q and the verdict and can say "NO VERDICT".
# A family the extractor silently cannot read is a family excluded from the sensitivity
# without anyone saying so, which is how these two came to sit outside it in the first place.
VERDICT2 = re.compile(r"^(.*?)\s{2,}(?:\d+\s+)?(?:[+-]?\d+\.\d+\s+)*"
                      r"(?:\[[^\]]+\]\s*)*(\d\.\d{3,4})\s+(\d\.\d{3,4})\s+"
                      r"(?:\d+\s+)?(SURVIVES(?: FDR)?|raw only|n\.s\.|NO VERDICT.*)\s*$")


def rows_from(text):
    out = []
    for line in text.split(chr(10)):
        m = VERDICT.match(line.rstrip())
        if m:
            out.append((" ".join(m.group(1).split()), float(m.group(3))))
            continue
        m = VERDICT2.match(line.rstrip())
        if m and m.group(1).strip():
            out.append((" ".join(m.group(1).split()), float(m.group(2))))
    return out


def bh(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))
    return q


fams = []
for fn, name in FAMILIES.items():
    path = os.path.join(RES, fn)
    if not os.path.exists(path):
        continue
    fams.append((name, rows_from(io.open(path, encoding="utf-8", errors="replace").read())))

sub = io.open(os.path.join(RES, "BIOCV_SUBSET_CONTROL.txt"), encoding="utf-8",
              errors="replace").read()
for name, a, b in PARTS:
    t = sub[sub.index(a):]
    if b:
        t = t[: t.index(b)]
    fams.append((name, rows_from(t)))

off = io.open(os.path.join(RES, "BIOCV_OFFSET_CONFOUND.txt"), encoding="utf-8",
              errors="replace").read()
def nl_join(xs):
    return chr(10).join(xs)

for name, a, b in OFFSET_PARTS:
    t = off[off.index(a):]
    if b:
        t = t[: t.index(b)]
    # Part A prints each contrast three times -- midpoint, ref=1st arm, ref=2nd arm -- but the
    # declared verdict is the midpoint; the other two are the endpoints of a known estimator
    # bias, shown for reference. Counting all three tripled this family in the correction.
    if "per-joint" in name:
        t = nl_join([ln for ln in t.splitlines()
                     if " 1st arm" not in ln and " 2nd arm" not in ln])
    fams.append((name, rows_from(t)))

L = []


def out(s):
    print(s)
    L.append(s)


out("BENJAMINI-YEKUTIELI SENSITIVITY: THE PRICE OF NOT ASSUMING POSITIVE DEPENDENCE")
out("")
out("Section 2.5 corrects with Benjamini-Hochberg within each declared family and appeals to the")
out("positive-regression-dependence extension (Benjamini and Yekutieli, 2001) because the")
out("contrasts in a family share arms, participants and baselines. PRDS is assumed there, not")
out("shown. This is what the same authors' ARBITRARY-dependence procedure gives instead: the BH")
out("threshold divided by H_m = sum_{i=1..m} 1/i. It is deliberately conservative and is NOT the")
out("convention the manuscript adopts; it is reported so a reader can see which verdicts depend on")
out("the positive-dependence assumption.")
out("")
out(f"{'family':<30}{'m':>4}{'H_m':>7}{'BH':>6}{'BY':>6}  contrasts losing significance under BY")
total_bh = total_by = 0
lost_all = []
for name, rows in fams:
    if not rows:
        continue
    ps = [p for _lab, p in rows]
    m = len(ps)
    H = sum(1.0 / i for i in range(1, m + 1))
    q_bh = bh(ps)
    q_by = [min(1.0, q * H) for q in q_bh]
    nbh = sum(1 for q in q_bh if q < 0.05)
    nby = sum(1 for q in q_by if q < 0.05)
    total_bh += nbh
    total_by += nby
    lost = [rows[i][0] for i in range(m) if q_bh[i] < 0.05 <= q_by[i]]
    lost_all += [(name, x) for x in lost]
    out(f"{name:<30}{m:>4}{H:>7.2f}{nbh:>6}{nby:>6}  {len(lost)}")

out("")
out(f"{'TOTAL':<30}{'':>4}{'':>7}{total_bh:>6}{total_by:>6}")
out("")
out("Verdicts that hold under BH and not under BY, i.e. those resting on the positive-dependence")
out("assumption:")
for name, lab in lost_all:
    out(f"  {name:<30}{lab}")
out("")
out("Verdicts holding under BOTH are those whose p reaches the sign-flip floor or close to it, and")
out("are unaffected by which dependence assumption is made.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
