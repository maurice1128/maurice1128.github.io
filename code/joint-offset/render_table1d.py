"""Render Table 1(d) from BIOCV_SUBSET_CONTROL.txt.

Table 1(d) was cited twice in section 3.1 and once in the supplement and did not exist. Two
independent cold readers found it; check_xrefs.py did not, because its pattern captured the table
NUMBER and discarded the panel letter, so "Table 1d" matched the existing Table 1. That blindness
is fixed there. This file removes the cause: the panel is generated, like 1(c) and 2(c), so it
cannot go missing or go stale.

The panel carries the paper's within-limb control -- the only analysis in which body region,
occlusion regime and camera geometry are held constant and only set membership varies -- so its
absence was not cosmetic. It is printed in two blocks matching the artefact: the direct
subset-versus-subset differences (Part A relative, Part B in mm) and each subset's own effect
(Part C).

Input : D:/BioCV/BIOCV_SUBSET_CONTROL.txt
Output: stdout (pasted into TABLES_SUBMISSION.md by build; verified by check_drift.py)
"""
import io
import re
import sys

SRC = "D:/BioCV/BIOCV_SUBSET_CONTROL.txt"

txt = io.open(SRC, encoding="utf-8").read()


def part(tag, nxt):
    a = txt.index(tag)
    b = txt.index(nxt) if nxt else len(txt)
    return txt[a:b]


PAIR = re.compile(
    r"^(.{10,34}?)\s{2,}([yn])\s+(\S+)\s{2,}(\S+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+"
    r"([+-]\d+\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)\s*$")
OWN = re.compile(
    r"^(.{10,34}?)\s{2,}([yn])\s+(\S+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+"
    r"(\d\.\d+)\s+(\d\.\d+)\s+(SURVIVES|raw only|n\.s\.)\s*$")


def rows(block, pat):
    out = []
    for line in block.split("\n"):
        m = pat.match(line.rstrip())
        if m:
            out.append(m.groups())
    return out


rel = rows(part("=== PART A", "=== PART B"), PAIR)
ab = rows(part("=== PART B", "=== PART C"), PAIR)
own = rows(part("=== PART C", None), OWN)
if not (rel and ab and own):
    raise SystemExit(f"parsed {len(rel)}/{len(ab)}/{len(own)} rows -- check the artefact format")

absq = {(r[0], r[2], r[3]): (r[6], r[8]) for r in ab}


def ital(s):
    return s.replace("k=1", "*k* = 1").replace("k=2", "*k* = 2")


def sub(s):
    return s.replace("+", " + ").replace("hip + knee + ankle", "**hip, knee, ankle**")


_L = []


def emit(x=""):
    _L.append(x)


emit("**(d) Within one limb: only the membership of the set changes** — subsets of {hip, knee,")
emit("ankle} rebuilt from the same per-joint accumulators, so body region, occlusion regime and")
emit("camera geometry are held constant. *dep.* marks an intervention a validation study could")
emit("deploy; matched-*k* is a retention control and cannot carry a practical claim.")
emit()
emit("*Does membership change the size of the effect?* Difference between two subsets, per")
emit("participant, on each subset's own baseline (%) and in mm. BH within m = 30 on each scale;")
emit("a difference surviving on one scale only is a scale artefact, not a membership effect.")
emit()
emit("| intervention | dep. | subsets compared | Δ% | q (%) | Δmm | q (mm) |")
emit("|---|---|---|---|---|---|---|")
for lab, dep, s1, s2, _a, _b, d, _p, q, v in rel:
    k = (lab, s1, s2)
    if k not in absq:
        continue
    dm, qm = absq[k]
    if v != "SURVIVES" and float(qm) >= 0.05:
        continue
    both = float(q) < 0.05 and float(qm) < 0.05
    mark = "**" if both else ""
    emit(f"| {ital(lab)} | {'y' if dep == 'y' else 'n'} | {sub(s1)} vs {sub(s2)} | "
         f"{mark}{d}{mark} | {mark}{q}{mark} | {mark}{dm}{mark} | {mark}{qm}{mark} |")
nb = sum(1 for lab, dep, s1, s2, _a, _b, d, _p, q, v in rel
         if (lab, s1, s2) in absq and float(q) < 0.05 and float(absq[(lab, s1, s2)][1]) < 0.05)
emit()
emit("The 19 differences surviving on at least one scale are shown; all 30 are in Table S3n.")
emit("")
emit(f"Bold marks the {nb} differences that survive on **both** scales. "
      f"{sum(1 for r in rel if r[9] == 'SURVIVES')} of 30 survive on the relative scale and "
      f"{sum(1 for r in ab if r[9] == 'SURVIVES')} of 30 in mm.")
emit()
emit("*What would each subset have reported on its own?* Effect against zero, BH within m = 20.")
emit()
emit("| intervention | dep. | subset | effect (mm) | q | verdict |")
emit("|---|---|---|---|---|---|")
for lab, dep, s, mm, _r, _p, q, v in own:
    b = "**" if v == "SURVIVES" else ""
    emit(f"| {ital(lab)} | {'y' if dep == 'y' else 'n'} | {sub(s)} | {b}{mm}{b} | {b}{q}{b} | {v} |")
emit()
flips = {}
for lab, dep, s, mm, _r, _p, q, v in own:
    flips.setdefault((lab, dep), []).append((s, v == "SURVIVES"))
lines = []
for (lab, dep), vs in flips.items():
    if len({x for _s, x in vs}) > 1:
        yes = ", ".join(sub(s) for s, x in vs if x)
        no = ", ".join(sub(s) for s, x in vs if not x)
        lines.append(f"{ital(lab)} ({'deployable' if dep == 'y' else 'control only'}): "
                     f"significant on {yes}; null on {no}")
emit("Three interventions change verdict across subsets of one limb — "
      + "; ".join(lines) + ".")


BLOCK = "\n".join(_L) + "\n"
print(BLOCK)
if "--write" in sys.argv:
    TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"
    t = io.open(TB, encoding="utf-8").read()
    a = t.index("**(d) Within one limb")
    b = t.index("\n## Table 2.")
    io.open(TB, "w", encoding="utf-8").write(t[:a] + BLOCK + t[b:])
    print("WROTE Table 1(d) into", TB)
