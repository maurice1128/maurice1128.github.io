"""Render Table 2(c) from the artefact so it can never disagree with it.

Table 2(c) was typed by hand and printed 11 of the 19 interactions while its own caption
claimed thirteen survivors -- four survivors were invisible to the reader, including the
frontal-knee criterion interaction that the Discussion's "n.s." sentence brushes past.
Selectively displaying a corrected family is what the correction exists to prevent, so the
table is generated. `python render_table2c.py --write` rewrites it in place.
"""
import io
import re
import sys

SRC = "D:/BioCV/BIOCV_INTERACTION_FDR.txt"
TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"
MINUS = "\u2212"

ROW = re.compile(
    r"^(.+?)\s{2,}([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+(\S.*)$"
)

PRETTY = [
    ("no rejection->objd rejection", "no rejection \u2192 object-space rejection"),
    ("no rejection->reproj rejection", "no rejection \u2192 reprojection rejection"),
    ("reproj->object-space criterion", "reprojection \u2192 object-space criterion"),
    # The arm is c/d. Section 2.3 declares 1/d and c/d as separate arms and writes c/d as
    # "confidence x 1/d" throughout, so rendering this as "1/d weighting" names the other arm --
    # and the sign-reversal claim in 3.1 depends on which one it is.
    ("confidence->1/d weighting", "confidence \u2192 confidence \u00d7 1/*d*"),
    ("uniform->confidence weighting", "uniform \u2192 confidence weighting"),
    ("criterion at matched k=", "criterion at matched *k* = "),
    ("DLT -> GN w^2-matched", "DLT \u2192 Gauss\u2013Newton (*w*\u00b2-matched)"),
    ("DLT -> GN as published (w)", "DLT \u2192 Gauss\u2013Newton (as published, *w*)"),
    ("GN: rejection (w^2-matched)", "Gauss\u2013Newton with rejection (*w*\u00b2-matched)"),
    ("LOO offset correction", "LOO offset correction"),
]
JOINT = {"[knee flex]": "knee flexion", "[hip flex]": "hip flexion",
         "[frontal knee]": "frontal knee"}


def label(raw):
    joint = ""
    for k, v in JOINT.items():
        if raw.endswith(k):
            joint, raw = v, raw[: -len(k)].strip()
    for k, v in PRETTY:
        if raw.startswith(k):
            raw = v + raw[len(k):]
            break
    return f"{raw}, {joint}" if joint else raw


def sgn(x, pct=""):
    return f"{x:+.2f}{pct}".replace("-", MINUS)


def build():
    rows = []
    for line in io.open(SRC, encoding="utf-8"):
        m = ROW.match(line.rstrip())
        if m and m.group(7).strip() in ("SURVIVES", "raw only", "n.s."):
            rows.append((label(m.group(1).strip()), float(m.group(2)), float(m.group(3)),
                         float(m.group(4)), float(m.group(6)), m.group(7).strip(),
                         float(m.group(5))))
    if len(rows) != 20:
        raise SystemExit(f"expected 20 interaction rows, parsed {len(rows)} -- check {SRC}")
    rows.sort(key=lambda r: r[4])
    surv = sum(1 for r in rows if r[5] == "SURVIVES")

    out = ["| intervention | \u0394 position | \u0394 angle | interaction | q |",
           "|---|---|---|---|---|"]
    for lab, dp, da, it, q, v, _p in rows:
        qs = f"**{q:.3f}**" if v == "SURVIVES" else f"{q:.3f}"
        out.append(f"| {lab} | {sgn(dp, '%')} | {sgn(da, '%')} | {sgn(it)} | {qs} |")
    out.append("")
    # r[4] is the CORRECTED q; the unadjusted p is r[6]. Counting survivors here made surv == raw
    # by construction, so the sentence below could never come out false -- which is exactly the
    # failure it was written to prevent, reintroduced by the fix for it.
    raw = sum(1 for r in rows if r[6] < 0.05)
    n_fail = len(rows) - surv
    # Compute this sentence, never assert it: it read "every interaction significant unadjusted
    # also survives" and stayed in the file when a recomputation made it false.
    tail = ("and every interaction significant unadjusted also survives"
            if surv == raw else
            f"and {raw - surv} that was significant unadjusted does not")
    out.append(
        f"All {len(rows)} interactions in the family are listed, survivors in bold. {surv} of "
        f"{len(rows)} survive correction {tail}. The {n_fail} that do not are shown so that the "
        f"family can be audited rather than summarised."
    )
    return "\n".join(out)


block = build()
print(block)
if "--write" in sys.argv:
    t = io.open(TB, encoding="utf-8").read()
    a = t.index("| intervention | \u0394 position |")
    b = t.index("**Scale.**")
    io.open(TB, "w", encoding="utf-8").write(t[:a] + block + "\n\n" + t[b:])
    print("\nWROTE Table 2(c) into", TB)
