"""Render Table 1(c) from the joint-set interaction artefact.

Table 1(c) was inserted once by hand. The family then grew from seven contrasts to eight when the
inverse-distance contrast was added -- the paper's only sign-reversal claim, and the one
dissociation that had never been interaction-tested while the abstract said every one had. A table
written once by hand cannot follow a change like that, which is the defect class this project
keeps recommitting, so it is generated. `python render_table1c.py --write` rewrites it in place.
"""
import io
import re
import sys

SRC = "D:/BioCV/BIOCV_JOINTSET_FDR.txt"
TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"
MINUS = "\u2212"

ROW = re.compile(r"^(.{10,50}?)\s{2,}(\d+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+"
                 r"(\d\.\d+)\s+(\d\.\d+)\s+(\S+)")

PRETTY = {
    "uniform vs confidence weighting": "uniform vs confidence weighting",
    "matched k=1: reprojection vs object-space": "criterion at matched *k* = 1",
    "matched k=2: reprojection vs object-space": "criterion at matched *k* = 2",
    "matched k=3: reprojection vs object-space": "criterion at matched *k* = 3",
    "adaptive: reprojection vs object-space": "criterion, adaptive rejection",
    "no rejection vs reprojection rejection": "no rejection vs reprojection rejection",
    "no rejection vs object-space rejection": "no rejection vs object-space rejection",
    "confidence vs confidence x 1/d weighting": "confidence vs confidence \u00d7 1/*d* weighting",
}


def sgn(x, pct=""):
    return f"{x:+.2f}{pct}".replace("-", MINUS)


def build():
    rows = []
    for line in io.open(SRC, encoding="utf-8"):
        m = ROW.match(line.rstrip())
        if m:
            lab = " ".join(m.group(1).split())
            rows.append((PRETTY.get(lab, lab), float(m.group(3)), float(m.group(4)),
                         float(m.group(5)), float(m.group(7)), m.group(8)))
    if not rows:
        raise SystemExit("no rows parsed from " + SRC)
    rows.sort(key=lambda r: r[4])
    surv = sum(1 for r in rows if r[5] == "SURVIVES")
    n = len(rows)

    out = ["**(c) Does the joint set change the effect?** \u2014 per participant, the effect on ankles "
           "and wrists minus\nthe effect on hip/knee/ankle, each as a percentage of that "
           "participant's own baseline at that joint\nset; BH-corrected within the family of "
           f"{n}",
           "",
           "| contrast | \u0394 [pos:AW] | \u0394 [pos:HKA] | interaction | q |",
           "|---|---|---|---|---|"]
    for lab, da, dh, it, q, v in rows:
        qs = f"**{q:.3f}**" if v == "SURVIVES" else f"{q:.3f}"
        out.append(f"| {lab} | {sgn(da, '%')} | {sgn(dh, '%')} | {sgn(it)} | {qs} |")
    fails = n - surv
    out += ["",
            f"All {n} are listed. {surv} survive correction, including all three matched-retention "
            f"contrasts that\nthe Section 3.1 result rests on and the confidence × 1/*d* contrast that "
            f"carries the sign reversal. The\n{fails} that do not are the rejection-versus-none "
            f"contrasts, which are null on both joint sets. This interaction is run on the relative\n"
            f"scale only, so by Section 2.5's rule it is scale-dependent; the within-limb control of\n"
            f"panel (d), run on both scales, carries the claim."]
    return "\n".join(out)


block = build()
print(block)
if "--write" in sys.argv:
    t = io.open(TB, encoding="utf-8").read()
    a = t.index("**(c) Does the joint set change the effect?**")
    b = t.index("\n---\n\n**(d) Within one limb")
    io.open(TB, "w", encoding="utf-8").write(t[:a] + block + "\n" + t[b:])
    print("\nWROTE Table 1(c) into", TB)
