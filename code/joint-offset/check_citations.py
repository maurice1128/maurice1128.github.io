"""Check the reference list and the text against each other, in both directions.

Written after a length edit deleted the only citation to Kanko et al. (2021b) while leaving the
entry in the reference list. Four attempts were needed and each failed differently, which is why
the checks below are shaped the way they are:

1. Matching only the four-digit year let "Kanko et al., 2021a" in the text satisfy the 2021b
   entry. Same-author same-year pairs are exactly the ones a careless edit orphans, so the letter
   suffix is part of the key.
2. Parsing citations out of the running text failed on the narrative form "Das et al. (2023)" and
   truncated multi-word surnames ("Della Croce" became "Croce").
3. Checking only list-to-text left the opposite direction blind, and Benjamini and Hochberg
   (1995) -- the source of every q-value in the paper -- sat uncited in the text with no entry in
   the list for an entire round.
4. The fix for (3) was patched in through a shell heredoc, which ate the escapes: the citation
   regex compiled but matched nothing, so the new check reported clean on a manuscript with the
   defect deliberately reinjected. It is written as a file now, and the self-test below runs the
   regex against known citation forms so a silent zero-match cannot happen again.
"""
import io
import re
import sys

sys.path.insert(0, "D:/ROWV_paper")
from paper_stats import references

MS = "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"

# Matches both citation styles: "(Das et al., 2023)" and "Das et al. (2023)", with optional
# "and"/"&" second author, and a year that may carry a disambiguating letter.
CITE = re.compile(
    r"([A-Z][A-Za-z\u00c0-\u024f'\-]+(?: (?:and|&) [A-Z][A-Za-z\u00c0-\u024f'\-]+)?)"
    r"(?: et al\.)?,? \(?((?:19|20)\d\d[a-z]?)\)?"
)

_SELFTEST = [
    ("(Das et al., 2023)", "Das", "2023"),
    ("Das et al. (2023)", "Das", "2023"),
    ("(Kanko et al., 2021b)", "Kanko", "2021b"),
    ("(Gelman and Stern, 2006)", "Gelman and Stern", "2006"),
    ("(Benjamini and Hochberg, 1995)", "Benjamini and Hochberg", "1995"),
    ("(Della Croce et al., 2005)", "Croce", "2005"),   # multi-word surname: first word is lost
    ("(Varcin and Boocock, 2026)", "Varcin and Boocock", "2026"),
]


def self_test():
    """A regex that silently matches nothing reports a clean manuscript. Prove it matches."""
    fail = []
    for text, who, year in _SELFTEST:
        m = CITE.search(text)
        if not m or m.group(1).split()[-1] != who.split()[-1] or m.group(2) != year:
            fail.append((text, m.groups() if m else None))
    return fail


def surname_of(entry):
    return entry.split(",")[0].strip()


def year_of(entry):
    m = re.search(r"\b((?:19|20)\d\d[a-z]?)\.", entry)
    return m.group(1) if m else None


def main():
    fail = self_test()
    if fail:
        print("CITATION REGEX SELF-TEST FAILED -- this check cannot be trusted:")
        for text, got in fail:
            print(f"    {text!r} -> {got}")
        return 1

    s = io.open(MS, encoding="utf-8").read()
    body = " ".join(s[: s.index("## References")].split())
    refs = references()

    problems = []

    # Direction 1: every entry in the list must be cited in the text.
    for r in refs:
        sn, yr = surname_of(r), year_of(r)
        if yr is None:
            problems.append((r[:44], "no year found in the entry"))
            continue
        pat = re.escape(sn) + r".{0,40}?" + re.escape(yr) + r"(?![a-z0-9])"
        if not re.search(pat, body):
            problems.append((f"{sn}, {yr}", "in the list, never cited in the text"))

    # Direction 2: every citation in the text must have an entry. Compare on the LAST word of
    # the surname so that "Della Croce" in the list matches "Croce" as the regex sees it.
    listed = {(surname_of(r).split()[-1].lower(), year_of(r)) for r in refs if year_of(r)}
    seen = set()
    for m in CITE.finditer(body):
        who = m.group(1).split(" and ")[0].split(" & ")[0].split()[-1].lower()
        key = (who, m.group(2))
        if key in listed or key in seen:
            continue
        seen.add(key)
        problems.append((f"{m.group(1)}, {m.group(2)}", "cited in the text, no entry in the list"))

    print(f"{len(refs)} references in the list; regex self-test passed "
          f"({len(_SELFTEST)} citation forms)")
    if problems:
        print(f"{len(problems)} problem(s):")
        for who, why in problems:
            print(f"    {who:<40}{why}")
        return 1
    print("both directions clean: every entry is cited and every citation has an entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
