"""If the leave-one-out p-values are invalid, what did they do to everyone else's q?

Section 2.5 withholds the q on every leave-one-participant-out row: each participant's correction
is built from the other ten, the eleven differences are not exchangeable, and the sign-flip test
does not apply. Withholding the q is not the whole consequence. Those p-values were part of the
Benjamini-Hochberg ranking of the families they sit in, so every OTHER q in those families was
computed against them. A ranking that includes an invalid p-value can move the threshold for the
valid ones in either direction.

This recomputes Benjamini-Hochberg for every declared family with the leave-one-out rows removed,
and reports which verdicts move.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) NO VERDICT MOVES. The leave-one-out rows did not affect anyone else's correction. The
      published q-values stand as they are and this file is a null result, reported as one.

  (2) VERDICTS MOVE. Every affected q must be republished on the reduced family, the family
      sizes in Table S4b restated, and the survivor counts in Section 2.5 recomputed. The
      direction is reported whichever way it falls -- verdicts gained are as reportable as
      verdicts lost.

  (3) The comparison is BH against BH on the same p-values, so nothing here depends on the
      sign-flip test being valid for the removed rows; it depends only on their removal.

-> D:/BioCV/BIOCV_LOO_EXCLUSION.txt
"""
import importlib.util
import io
import os
import sys

sys.path.insert(0, "D:/ROWV_paper")

OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_LOO_EXCLUSION.txt")

# The family definitions and their parsers already exist. Import them rather than restate them,
# so this file cannot drift from the families the paper declares.
_spec = importlib.util.spec_from_file_location(
    "_pfs", "D:/ROWV_paper/pooled_family_sensitivity.py")
_mod = importlib.util.module_from_spec(_spec)
_stdout = sys.stdout
sys.stdout = io.StringIO()                      # its module body prints its own report
try:
    _spec.loader.exec_module(_mod)
except SystemExit:
    pass
finally:
    sys.stdout = _stdout

rows = _mod.rows                                # [fam, label, p, own_q, survives, verdict_text]


def bh(ps):
    """Benjamini-Hochberg step-up, the same form pooled_family_sensitivity.py uses inline."""
    m = len(ps)
    q = [0.0] * m
    order = sorted(range(m), key=lambda i: ps[i])
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))
    return q

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


def is_loo(label):
    t = label.lower()
    return "loo" in t or "population offset" in t


fams = {}
for r in rows:
    fams.setdefault(r[0], []).append(r)

out("WHAT THE WITHHELD LEAVE-ONE-OUT ROWS DID TO EVERYONE ELSE'S q")
out("")
out("Benjamini-Hochberg is recomputed within each declared family with the leave-one-out rows")
out("removed. Only rows that REMAIN are compared; the removed rows have no q by the rule of")
out("Section 2.5.")
out("")
out("Survivor counts are over the ROWS THAT REMAIN, so 'with' and 'without' differ only")
out("through the ranking the removed rows imposed. Table captions that quote a survivor count")
out("out of the DECLARED family size are quoting a denominator that includes rows with no q.")
out("")
out(f"{'family':<30}{'m':>4}{'m without LOO':>15}{'surv with':>11}{'surv without':>14}{'verdicts moved':>16}")
moved = []
for fam in sorted(fams):
    rs = fams[fam]
    keep = [r for r in rs if not is_loo(r[1])]
    if len(keep) == len(rs):
        continue
    q_all = bh([r[2] for r in rs])
    q_red = bh([r[2] for r in keep])
    idx = {id(r): k for k, r in enumerate(rs)}
    n = 0
    for k, r in enumerate(keep):
        a = q_all[idx[id(r)]] < 0.05
        b = q_red[k] < 0.05
        if a != b:
            n += 1
            moved.append((fam, r[1], r[2], q_all[idx[id(r)]], q_red[k], a, b))
    sw = sum(1 for r in keep if q_all[idx[id(r)]] < 0.05)
    so = sum(1 for k2, r in enumerate(keep) if q_red[k2] < 0.05)
    out(f"{fam:<30}{len(rs):>4}{len(keep):>15}{sw:>11}{so:>14}{n:>16}")
out("")

# Branch (2) of this file's header requires the survivor counts of Section 2.5 to be
# recomputed, not only the q-values. That half was not done: a reviewer found that the
# published chain counts leave-one-out rows among its survivors, and it does. The counts
# over the set that carries a valid verdict are printed here so the manuscript can quote a
# number this file produced rather than one assembled by hand.
def _has_verdict(r):
    return "NO VERDICT" not in str(r[5]).upper()

allr = list(rows)
verdict_rows = [r for r in allr if _has_verdict(r)]
loo_rows = [r for r in verdict_rows if is_loo(r[1])]
valid_rows = [r for r in verdict_rows if not is_loo(r[1])]

def _surv(subset, reduced):
    by_fam = {}
    for r in subset:
        by_fam.setdefault(r[0], []).append(r)
    n = 0
    for fam, rs in by_fam.items():
        pool = [x for x in rs if not is_loo(x[1])] if reduced else rs
        if not pool:
            continue
        q = bh([x[2] for x in pool])
        n += sum(1 for v in q if v < 0.05)
    return n

surv_declared = _surv(verdict_rows, False)
surv_valid = _surv(valid_rows, True)
loo_surv = 0
for fam, rs in fams.items():
    rs2 = [r for r in rs if _has_verdict(r)]
    if not rs2:
        continue
    q = bh([r[2] for r in rs2])
    loo_surv += sum(1 for k, r in enumerate(rs2) if is_loo(r[1]) and q[k] < 0.05)

out("=== THE SURVIVOR CHAIN OVER ROWS THAT CARRY A VALID VERDICT ===")
out("")
out("A leave-one-out row has no valid q by the rule of Section 2.5, so it can be neither a")
out("survivor nor a denominator. The published chain counted it as both.")
out("")
out(f"  declared contrasts parsed                       {len(allr):>4}")
out(f"  carrying a verdict (endpoint veto removed)      {len(verdict_rows):>4}")
out(f"  of those, leave-one-out rows with no valid q    {len(loo_rows):>4}")
out(f"  counted as BH survivors in the published chain  {loo_surv:>4}")
out(f"  contrasts carrying a VALID verdict              {len(valid_rows):>4}")
out("")
out(f"  BH survivors, families as declared              {surv_declared:>4} of {len(verdict_rows)}")
out(f"  BH survivors, reduced families, valid rows only {surv_valid:>4} of {len(valid_rows)}")
out("")
# The arbitrary-dependence sensitivity is computed on the same rankings, so it inherits the
# same defect: 107 of 146 and "39 fall" both count rows with no valid q.
def _H(m):
    return sum(1.0 / k for k in range(1, m + 1))

def _by(subset, reduced):
    by_fam = {}
    for r in subset:
        by_fam.setdefault(r[0], []).append(r)
    n = 0
    for fam, rs in by_fam.items():
        pool = [x for x in rs if not is_loo(x[1])] if reduced else rs
        if not pool:
            continue
        ps = sorted(x[2] for x in pool)
        m = len(ps)
        h = _H(m)
        k = 0
        for rank, pv in enumerate(ps, start=1):
            if pv <= rank * 0.05 / (m * h):
                k = rank
        n += k
    return n

by_declared = _by(verdict_rows, False)
by_valid = _by(valid_rows, True)
out(f"  BY survivors, families as declared              {by_declared:>4} of {surv_declared}"
    f"  ({surv_declared - by_declared} fall)")
out(f"  BY survivors, reduced families, valid rows only {by_valid:>4} of {surv_valid}"
    f"  ({surv_valid - by_valid} fall)")
# The dagger in Tables 1, 2 and 4 marks a row that survives BH but not BY. If removing the
# leave-one-out rows moves any row across that line, every affected dagger has to be redrawn.
def _by_set(subset, reduced):
    by_fam, keep = {}, set()
    for r in subset:
        by_fam.setdefault(r[0], []).append(r)
    for fam, rs in by_fam.items():
        pool = [x for x in rs if not is_loo(x[1])] if reduced else rs
        if not pool:
            continue
        m = len(pool)
        h = _H(m)
        order = sorted(pool, key=lambda x: x[2])
        k = 0
        for rank, x in enumerate(order, start=1):
            if x[2] <= rank * 0.05 / (m * h):
                k = rank
        for x in order[:k]:
            keep.add((x[0], x[1]))
    return keep

a = _by_set(verdict_rows, False)
b = _by_set(valid_rows, True)
flip = sorted((a ^ b))
flip = [x for x in flip if not is_loo(x[1])]
out(f"=== DAGGERS: rows crossing the BY line when the leave-one-out rows go: {len(flip)} ===")
for fam, lab in flip:
    out(f"    {fam:<30} {lab[:60]:<60} {'gains BY' if (fam, lab) in b else 'loses BY'}")
out("")
out("")
out("")


if not moved:
    out("=== VERDICT (1), against the rule fixed in this file's header ===")
    out("No verdict moves in any family. The leave-one-out rows did not affect the correction")
    out("applied to any other contrast, so every published q outside those rows stands as it is,")
    out("and the survivor counts of Section 2.5 need no change. This is a null result and is")
    out("reported as one.")
else:
    out("=== VERDICT (2), against the rule fixed in this file's header ===")
    out(f"{len(moved)} verdict(s) move when the leave-one-out rows are removed:")
    out("")
    out(f"{'family':<30}{'contrast':<44}{'p':>9}{'q with':>9}{'q without':>11}   change")
    for fam, lab, p, qa, qb, a, b in moved:
        out(f"{fam:<30}{lab[:42]:<44}{p:>9.4f}{qa:>9.4f}{qb:>11.4f}   "
            f"{'gains' if b else 'loses'}")
    out("")
    out("Each of these is published on the reduced family, the sizes are those Table S4b")
    out("states, and the survivor count Section 2.5 reports is the reduced one.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
