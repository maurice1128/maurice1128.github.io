"""Every Table S / Figure / section reference must point at something that exists.

Added after the supplement was renumbered (superseded tables dropped, S3 reordered) and three
main-text pointers were left aiming at sections that no longer existed. A cold reader also found
three references inside the supplement itself aimed at draft section numbers -- "section 3.6",
"Section 3.5's fixed offset" -- that had moved. Cross-references are the one kind of claim a
reader checks for free, so a broken one is unusually cheap to find and unusually damaging.
"""
import io
import re

MS = "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"
TB = "D:/ROWV_paper/TABLES_SUBMISSION.md"
SUP = "D:/ROWV_paper/SUPPLEMENT_SUBMISSION.md"

ms = io.open(MS, encoding="utf-8").read()
tb = io.open(TB, encoding="utf-8").read()
sup = io.open(SUP, encoding="utf-8").read()

# "S15" was captured as "S1" on BOTH sides -- the heading pattern and the reference pattern --
# so every two-digit reference validated against a section it does not name, and a pointer to a
# section that does not exist (S19) would have passed. The + makes both read the whole number.
sup_sections = set(re.findall(r"^#{2,3} (?:Table )?(S\d+[a-z]*)", sup, re.M))
main_sections = set(re.findall(r"^#{2,3} (\d(?:\.\d)?)", ms, re.M))
tables = set(re.findall(r"^## Table (\d)", tb, re.M))
panels = set()
_cur = None
for _line in tb.split("\n"):
    _t = re.match(r"^## Table (\d)", _line)
    if _t:
        _cur = _t.group(1)
    _p = re.match(r"^\*\*\((\w)\)", _line)
    if _p and _cur:
        panels.add((_cur, _p.group(1)))
figures = set(re.findall(r"^\*\*Fig\. (\d)\.\*\*", ms, re.M))

problems = []

# The supplement was not scanned at all until now: 29 reader-visible sections of prose that
# reference main tables and each other, none of it checked. Renaming a main-table panel broke
# every supplement reference to it while this file reported "everything points at something".
for name, text in (("manuscript", ms), ("tables", tb), ("supplement", sup)):
    # A supplement reference is not always written "Table Sx". It appears in comma lists
    # ("Tables S1, S3b, S3d and S3n") and bare in parentheses ("corrected q in S3b"), and a
    # pattern anchored on the word "Table" sees neither -- which is how trimming "Table S3b"
    # to "S3b" silently removed a reference from this checker's scope.
    # Two patterns are needed. The explicit one catches a malformed suffix ("Table S3zz");
    # the bare one catches references the explicit one cannot see. Replacing rather than
    # adding lost the first class -- the injected-defect measurement caught that immediately.
    for m in re.finditer(r"Tables?\s+(S\d+[A-Za-z-]*)", text):
        if m.group(1).rstrip("-") not in sup_sections:
            problems.append((name, "Table " + m.group(1), "no such supplement section"))
    for m in re.finditer(r"S\d[a-z]?", text):
        if m.group(0) not in sup_sections:
            problems.append((name, m.group(0), "no such supplement section"))
    for m in re.finditer(r"Fig\.\s+(\d)[a-z]?", text):
        if m.group(1) not in figures:
            problems.append((name, "Fig. " + m.group(1), "no such figure caption"))
    # The panel letter must be checked, not discarded: capturing only the digit is how
    # "Table 1d" -- cited three times, never written -- passed this check.
    # Main-table references appear in the same forms as supplement ones: singular ("Table 1b"),
    # plural comma lists ("Tables 1a, 1c, 1d") and mixed lists that also name S-tables. A pattern
    # anchored on singular "Table\s+\d" sees none of the plural forms, so every reference the
    # manuscript makes as "Tables 1a, 1c, 1d" went unchecked -- the same blind spot that let
    # "Table 1d" be cited three times before it was written, reintroduced by pluralisation.
    # The panel may be written bare ("Table 1b") or parenthesised ("Table 1(d)"). The
    # supplement uses the parenthesised form throughout, and a pattern accepting only the
    # bare one captured "Table 1" and discarded the panel -- so renaming a panel broke every
    # parenthesised reference to it while this check passed.
    # This block was indented one level too deep and so ran INSIDE the figure loop above,
    # executing once per "Fig. N" match and not at all in a document containing none. The
    # supplement contains none, which is why a renamed panel passed while every reference to it
    # broke. It is a loop over `text`, not over figure matches, and belongs at this level.
    for mt_ in re.finditer(r"Tables?\s+((?:\d\(?[a-z]?\)?|S\d+[A-Za-z-]*)"
                           r"(?:\s*(?:,|and)\s*(?:\d\(?[a-z]?\)?|S\d+[A-Za-z-]*))*)", text):
        for tok in re.split(r"\s*(?:,|and)\s*", mt_.group(1)):
            mt = re.fullmatch(r"(\d)\(?([a-z])?\)?", tok.strip())
            if not mt:
                continue                          # an S-table, handled by the pattern above
            num, panel = mt.group(1), mt.group(2)
            if num not in tables:
                problems.append((name, "Table " + num, "no such table"))
            elif panel and (num, panel) not in panels:
                problems.append((name, f"Table {num}{panel}", "no such table panel"))
    for m in re.finditer(r"\u00a7(\d(?:\.\d)?)", text):
        if m.group(1) not in main_sections:
            problems.append((name, "\u00a7" + m.group(1), "no such section"))

# The supplement must not point at manuscript sections that do not exist either.
for m in re.finditer(r"[Ss]ection (\d(?:\.\d)?)", sup):
    if m.group(1) not in main_sections:
        problems.append(("supplement", "Section " + m.group(1), "no such manuscript section"))

print(f"manuscript sections: {len(main_sections)}   figures: {len(figures)}   "
      f"tables: {len(tables)}   supplement sections: {len(sup_sections)}")
if problems:
    print(f"{len(problems)} dangling cross-reference(s):")
    for where, what, why in sorted(set(problems)):
        print(f"    {where:<11}{what:<14}{why}")
    raise SystemExit(1)
print("every cross-reference points at something that exists")
