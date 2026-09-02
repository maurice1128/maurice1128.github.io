"""Check that a printed contrast's label names its arms in the order they were subtracted.

This is the one defect class the provenance check is structurally blind to: the number is
genuine, traces to a real artefact, and is printed with the wrong sign because the row label
names the arms in the opposite order to the subtraction. Layer 0 passes it every time.

It has bitten twice. An earlier round found six labels reversed in a result file. Then Table 1a
was found printing its two rejection rows with the ankles-and-wrists column on one subtraction
order and the hip-knee-ankle column on the other, under a single row label that matched only one
of them -- so the same sign meant opposite things in one row.

The authority is the FAMILY list in biocv_permutation_v2.py, whose tuples are
(level, arm_a, arm_b, label) and whose effect is defined so that POSITIVE means arm_b is better.
This script reads those tuples, works out which arm each label names first, and reports any
label whose wording disagrees with its own subtraction order. It then checks the values printed
in the tables against the artefact, matching on magnitude, and flags any row whose two columns
come from artefact entries with opposite orderings.
"""
import ast
import io
import re

SRC = "D:/ROWV_paper/biocv_permutation_v2.py"
ART = "D:/BioCV/BIOCV_PERM_V3.txt"
TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"

# Which arm name each token in a label refers to. Order matters: longest first.
ARMTOK = [
    ("no rejection", "noRej"), ("none", "noRej"),
    ("object-space rejection", "objd"), ("objd rejection", "objd"),
    ("reprojection rejection", "rep"), ("reproj rejection", "rep"),
    ("object-space criterion", "objd"), ("object-space", "objd"),
    ("reprojection", "rep"), ("reproj", "rep"),
    ("confidence", "conf"), ("uniform", "unif"), ("1/d", "wd"),
]


def family():
    src = io.open(SRC, encoding="utf-8").read()
    start = src.index("FAMILY = [")
    depth, i = 0, start + len("FAMILY = ")
    for j in range(i, len(src)):
        if src[j] == "[":
            depth += 1
        elif src[j] == "]":
            depth -= 1
            if depth == 0:
                return ast.literal_eval(src[i:j + 1])
    raise SystemExit("could not parse FAMILY")


def arm_of(text):
    """The first arm token mentioned in a fragment of label text."""
    best, pos = None, len(text) + 1
    low = text.lower()
    for tok, arm in ARMTOK:
        k = low.find(tok)
        if 0 <= k < pos:
            best, pos = arm, k
    return best


def norm(arm):
    """Collapse an arm identifier such as rep_conf or noRej_unif to its criterion token."""
    if arm is None:
        return None
    a = arm.lower()
    for key in ("norej", "objd", "rep", "conf", "unif", "wd", "gn", "loo", "mk"):
        if a.startswith(key):
            return "noRej" if key == "norej" else key
    return a


# Rows whose label does not name two arms in "A vs B" form cannot be direction-checked from the
# label alone. Silently passing them is what let an inverted 1/d row survive an injected-defect
# test, so they now fail -- unless they appear here, with the manual derivation that settles them.
# An entry is a promise that a person traced the row to its FAMILY tuple and recorded why.
HAND_CHECKED = {
    "uncorrected vs leave-one-participant-out offset correction": {
        "aw": None, "hka": +9.848,
        "why": ("Measured at [pos:HKA] only, from (\"posl\", noRej_conf, loo_corr): POSITIVE means "
                "the corrected arm has the lower error, so +9.848 is the improvement the "
                "correction buys."),
    },
    "DLT vs Gauss–Newton, no rejection": {
        "aw": None, "hka": -1.384,
        "why": ("Measured at [pos:HKA] only, from (\"posl\", noRej_conf, gn_w): POSITIVE would "
                "mean Gauss-Newton has the lower error, so the printed −1.384 says the "
                "estimator change makes position worse. The arms are estimators rather than "
                "rejection or weighting schemes, which is why the label cannot be parsed "
                "automatically."),
    },
    "confidence vs confidence × 1/*d* weighting, no rejection": {
        "aw": +0.256, "hka": -0.691,
        "why": ("AW comes from (\"pos\", conf, conf_d) and HKA from (\"posl\", noRej_conf, "
                "noRej_wd); in both, POSITIVE means the 1/d-weighted arm is better, so +0.256 "
                "(better) and −0.691 (worse) express one convention."),
    },
}

problems = []
for level, arm_a, arm_b, label in family():
    if " vs " not in label:
        continue
    left, right = label.split(" vs ", 1)
    la, lb = arm_of(left), arm_of(right)
    fa, fb = norm(arm_a), norm(arm_b)
    if la and lb and fa and fb and (la, lb) != (fa, fb):
        if (la, lb) == (fb, fa):
            problems.append((label, f"label says {la} vs {lb}; subtraction is {fa} -> {fb} "
                                    f"(POSITIVE means {fb} better) -- label is REVERSED"))

print("=== label vs subtraction order, over the m=50 family ===")
if problems:
    for lab, msg in problems:
        print(f"  REVERSED  {lab}")
        print(f"            {msg}")
else:
    print("  every label names its arms in the order they are subtracted")
print()

# Table 1a: do the two columns of a row come from artefact entries pointing the same way?
art = {}
for line in io.open(ART, encoding="utf-8", errors="replace"):
    # The label may contain digits -- "matched-k=1", "1/d weighting" -- so it must not be matched
    # with [^\d]. That was the bug: seven of Table 1a's eleven rows were silently out of scope,
    # including the 1/d row carrying the paper's only sign-reversal claim, and inverting it by
    # hand still produced "0 disagreeing" and exit 0. The label ends at the two-space column gap.
    m = re.match(r"^(\[pos:(?:AW|HKA)\].{5,70}?)\s{2,}\d+\s+([+-]\d+\.\d+)", line.rstrip())
    if m:
        art[" ".join(m.group(1).split())] = float(m.group(2))

problems_dash = []
# An em dash where a minus sign belongs. Batch edits that build strings from named unicode
# constants get this wrong silently -- the manuscript carried "—1.05%" for a negative
# membership effect -- and it survives every numeric check, because the number is right and
# only its sign glyph is not. A reader sees a dash, and the sign is the whole claim.
# Only the EM dash: an en dash before a digit is a page range or a numeric range and is
# correct. The reference list is skipped for the same reason.
_DASHNUM = re.compile(r"\u2014(?=\d)")
for _f in (TB, "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"):
    _txt = io.open(_f, encoding="utf-8").read()
    _cut = _txt.find("## References")
    if _cut > 0:
        _txt = _txt[:_cut]
    for _i, _l in enumerate(_txt.split(chr(10)), 1):
        if _DASHNUM.search(_l):
            problems_dash.append((_f.split("/")[-1], _i, _l.strip()[:80]))

print("=== Table 1a: are the two columns of each row on the same subtraction order? ===")
# A column may hold an em dash where the contrast was not measured on that joint set. The pattern
# used to require a number in both columns, so every such row was invisible to this check -- which
# is how an injected inversion of the Gauss-Newton row went undetected while the run exited 0.
_CELL = r"(?:\*\*)?([+\u2212-]?[\d.]+|\u2014)"
# A deployability column was added between the label and the first data column. The pattern
# above read that cell AS the first data column, so every Table 1a row silently left scope
# and hand-inverted signs still produced "0 disagreeing" -- the same failure the comment
# above records, reintroduced by a table edit rather than by a regex edit. The optional
# group makes the check survive the column being present or absent.
_DEP = r"(?:(?:y\*?|\*\*n\*\*|n)\s*\| )?"
rows = re.findall(r"^\| ([^|]+?) \| " + _DEP + _CELL + r"[^|]*\| " + _CELL + r"[^|]*\|",
                  io.open(TB, encoding="utf-8").read(), re.M)


def _num(x):
    """A cell value, or None where the table prints an em dash."""
    if x == "\u2014":
        return None
    try:
        return float(x.replace("\u2212", "-"))
    except ValueError:
        return None
checked = mismatched = 0
unchecked = []
for label, aw, hka in rows:
    av, hv = _num(aw), _num(hka)
    if av is None and hv is None:
        continue
    aw_src = ([k for k, v in art.items() if k.startswith("[pos:AW]")
               and abs(abs(v) - abs(av)) < 5e-4] if av is not None else [])
    hk_src = ([k for k, v in art.items() if k.startswith("[pos:HKA]")
               and abs(abs(v) - abs(hv)) < 5e-4] if hv is not None else [])
    # A row measured on only one joint set prints an em dash in the other column. Requiring
    # BOTH columns skipped every such row entirely -- including the Gauss-Newton row, whose
    # sign an injected inversion flipped without detection. One traceable column is enough
    # to check that column against its own label.
    if not aw_src and not hk_src:
        continue
    checked += 1
    # A printed value may legitimately carry the opposite sign to its artefact, when the
    # artefact's own label names the arms in the opposite order to the table's row label. The
    # test is whether BOTH columns end up expressing the row label's direction -- not whether
    # both match their artefact's raw sign.
    def expected(row_label, art_label, art_value):
        rl, al = row_label.lower(), art_label.lower()
        ra, rb = arm_of(rl.split(" vs ")[0]), arm_of(rl.split(" vs ")[-1])
        aa, ab = arm_of(al.split(" vs ")[0]), arm_of(al.split(" vs ")[-1])
        if None in (ra, rb, aa, ab):
            return None
        if (ra, rb) == (aa, ab):
            return art_value
        if (ra, rb) == (ab, aa):
            return -art_value
        return None

    ea = expected(label, aw_src[0], art[aw_src[0]]) if aw_src else "skip"
    eh = expected(label, hk_src[0], art[hk_src[0]]) if hk_src else "skip"
    if ea is None or eh is None:
        # A row whose label does not name its two arms in "A vs B" form cannot be direction-
        # checked this way. Report it: a checker that silently passes what it cannot examine
        # reads as a clean bill of health. This is how an inverted 1/d row -- the paper's only
        # sign-reversal claim -- survived an injected-defect test with "0 disagreeing", exit 0.
        key = label.strip()
        rec = HAND_CHECKED.get(key)
        if rec is None:
            unchecked.append(key[:58])
        elif ((rec["aw"] is not None and (av is None or abs(av - rec["aw"]) > 5e-4))
              or (rec["hka"] is not None and (hv is None or abs(hv - rec["hka"]) > 5e-4))):
            # The record fixes the values a person derived. If the table no longer
            # prints them, the derivation no longer covers what is printed.
            mismatched += 1
            print(f"  MISMATCH  {key[:58]}")
            print(f"            hand-checked as {rec['aw']:+.3f} / {rec['hka']:+.3f}; "
                  f"table prints {av:+.3f} / {hv:+.3f}")
        continue
    # A column is checkable only when the table prints a number there AND that number traced to an
    # artefact entry whose direction could be resolved. Either may be absent for a contrast run on
    # one joint set only, so both are tested before the comparison.
    bad = [(c, p, e) for c, p, e in (("AW", av, ea), ("HKA", hv, eh))
           if p is not None and e not in (None, "skip") and abs(p - e) > 5e-4]
    if bad:
        mismatched += 1
        print(f"  MISMATCH  {label.strip()[:58]}")
        for c, p, e in bad:
            print(f"            {c:<4} printed {p:+.3f} but the row label implies {e:+.3f}")
print(f"  {checked} row(s) traced to both artefact entries; {mismatched} disagreeing with "
      f"their row label")
if HAND_CHECKED:
    print(f"  {len(HAND_CHECKED)} row(s) settled by recorded manual derivation:")
    for k, rec in HAND_CHECKED.items():
        _f = lambda v: "—" if v is None else f"{v:+.3f}"
        print(f"      {k}  ({_f(rec['aw'])} / {_f(rec['hka'])})")
        print(f"        {rec['why']}")
if unchecked:
    print(f"  {len(unchecked)} row(s) NOT direction-checked (label is not in 'A vs B' form) — "
          f"verify these by hand:")
    for u in unchecked:
        print(f"      {u}")



# ---------------------------------------------------------------------------
# The interaction family, whose labels are free text.
#
# A row in that family was labelled "DLT -> GN as published (w)" while its tuple was
# ("gn_w2", "gn_w") -- both arms Gauss-Newton, no DLT arm in it at all. The number was right;
# the label named an arm that was not in the contrast, which made the row read as Table 1a's
# -1.384 mm DLT-versus-GN result and prompted a cold reader to report the table as internally
# irreconcilable. Everything above checks only the m=50 family, so nothing looked here.
#
# The test: every arm token a label names must be present in that row's own tuple.
INTER_SRC = "D:/ROWV_paper/biocv_interaction_fdr.py"

# label token -> the arm-name fragment it promises
ITOK = [
    # The Gauss-Newton arms carry two prefixes: gn_* for the estimator comparison and lm_* for
    # the refined pipeline the rejection contrasts run on. A label saying "GN" is honest for
    # either, so a token may be satisfied by any of several arm fragments.
    ("dlt", ("norej",)), ("gauss-newton", ("gn", "lm")), ("gauss–newton", ("gn", "lm")),
    ("gn", ("gn", "lm")), ("leave-one", ("loo",)), ("loo", ("loo",)),
    ("matched k=1", ("mk1",)), ("matched k=2", ("mk2",)), ("matched k=3", ("mk3",)),
    ("uniform", ("unif",)), ("confidence", ("conf",)), ("1/d", ("wd",)),
    ("object-space", ("objd",)), ("objd", ("objd",)),
    ("reprojection", ("rep",)), ("reproj", ("rep",)),
]


def inter_family():
    src = io.open(INTER_SRC, encoding="utf-8").read()
    start = src.index("INTER = [")
    i = src.index("[", start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "[":
            depth += 1
        elif src[j] == "]":
            depth -= 1
            if depth == 0:
                return ast.literal_eval(src[i:j + 1])
    raise SystemExit("could not parse the interaction family")


print()
print("=== interaction family: does each label name only arms the contrast contains? ===")
ibad = []
for tup in inter_family():
    if len(tup) < 4:
        continue
    arm_a, arm_b, _out, label = tup[0], tup[1], tup[2], tup[3]
    arms = (str(arm_a) + " " + str(arm_b)).lower()
    low = label.lower()
    for tok, frags in ITOK:
        if tok in low and not any(f in arms for f in frags):
            # "gn" appears inside no other arm name, and "conf"/"unif" are substrings of the
            # real arm identifiers, so a miss here is a label naming an absent arm.
            ibad.append((label, tok, f"{arm_a} -> {arm_b}"))
            break
if ibad:
    for label, tok, arms in ibad:
        print(f"  MISLABELLED  {label}")
        print(f"               names \"{tok}\" but the contrast is {arms}")
else:
    print("  every interaction label names only arms present in its own contrast")

if problems_dash:
    print()
    print(f"{len(problems_dash)} line(s) using an em or en dash where a minus sign belongs:")
    for _f, _i, _c in problems_dash:
        print(f"  {_f}:{_i}  {_c}")
else:
    print()
    print("no line uses a dash where a minus sign belongs")

raise SystemExit(1 if (problems or mismatched or unchecked or ibad or problems_dash) else 0)
