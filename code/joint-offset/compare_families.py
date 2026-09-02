"""Test the manuscript's claim that growing the contrast family changed no verdict.

Section 2.5 says the family "was not pre-specified: it grew as review identified contrasts a
claim required. At each step the whole family was re-run rather than appended to, and no verdict
changed at any step." A cold reader challenged this, pointing at the superseded family's own
footer, which warns that contrasts surviving at m=33 and not at m=50 "must be reported as having
dropped out, not quietly retained from the smaller family".

The claim is checkable and this checks it. Matching on labels alone is not enough -- 20 of the 33
labels were renamed when the joint sets were made explicit ("3D pos matched-k=1" became
"[pos:AW] matched-k=1"), so a label-based comparison reports 20 spurious dropouts. Contrasts are
therefore matched on (effect, unadjusted p), which renaming cannot alter.

Result as of 2026-08-21: 33 of 33 matched, zero verdict changes.
"""
import io
import re

OLD = "D:/BioCV/_SUPERSEDED_BIOCV_PERM_FINAL.txt"   # m = 33
NEW = "D:/BioCV/BIOCV_PERM_V3.txt"                  # m = 50, authoritative

ROW = re.compile(
    r"^(.{15,72}?)\s{2,}(\d+)\s+([+-]\d+\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+"
    r"(SURVIVES FDR|raw only|n\.s\.)"
)


def rows(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        m = ROW.match(line.rstrip())
        if m:
            out.append((" ".join(m.group(1).split()), float(m.group(3)),
                        float(m.group(4)), float(m.group(5)), m.group(6)))
    return out


old, new = rows(OLD), rows(NEW)
if not old or not new:
    raise SystemExit("could not parse one of the families -- check the file formats")

index = {}
for lab, e, p, q, v in new:
    index.setdefault((round(e, 3), round(p, 4)), []).append((lab, q, v))

changed, lost = [], []
for lab, e, p, q, v in old:
    hit = index.get((round(e, 3), round(p, 4)))
    if not hit:
        lost.append((lab, e, p, v))
    elif hit[0][2] != v:
        changed.append((lab, q, v, hit[0][1], hit[0][2]))

print(f"m={len(old)} family: {OLD}")
print(f"m={len(new)} family: {NEW}")
print(f"matched on (effect, unadjusted p): {len(old) - len(lost)}/{len(old)}")
print(f"verdict changes among matched:     {len(changed)}")

if changed:
    print("\n*** VERDICTS CHANGED -- Section 2.5's claim must be corrected and these listed ***")
    for lab, qo, vo, qn, vn in changed:
        print(f"  {lab[:62]}")
        print(f"     m={len(old)}: q={qo:.4f} {vo}  ->  m={len(new)}: q={qn:.4f} {vn}")
if lost:
    print(f"\n*** {len(lost)} contrast(s) absent from the larger family ***")
    for lab, e, p, v in lost:
        print(f"  {lab[:62]:<64} eff={e:+.3f} p={p:.4f}  {v}")

raise SystemExit(1 if (changed or lost) else 0)
