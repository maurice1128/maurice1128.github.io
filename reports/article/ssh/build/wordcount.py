#!/usr/bin/env python3
"""Count words in the SSH manuscript: main text, footnotes, references, total.
Usage: python3 wordcount.py ../manuscript_ssh.md
"""
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
# split off references
m = re.search(r"^#+\s*References\s*$", text, flags=re.M)
body, refs = (text[: m.start()], text[m.end():]) if m else (text, "")
# footnote definitions
notes = "\n".join(re.findall(r"^\[\^[^\]]+\]:.*(?:\n(?: {4}|\t).*)*", body, flags=re.M))
body_wo_notes = re.sub(r"^\[\^[^\]]+\]:.*(?:\n(?: {4}|\t).*)*", "", body, flags=re.M)
# abstract
am = re.search(r"^#+\s*Abstract\s*$(.*?)(?=^#+\s)", body_wo_notes, flags=re.M | re.S)
abstract = am.group(1) if am else ""


def wc(s):
    s = re.sub(r"\[\^[^\]]+\]", "", s)
    s = re.sub(r"[#*_>|`-]", " ", s)
    return len(s.split())


main = wc(body_wo_notes) - wc(abstract)
print(f"abstract: {wc(abstract)}")
print(f"main text (excl. abstract): {main}")
print(f"footnotes: {wc(notes)}")
print(f"references: {wc(refs)}")
print(f"TOTAL text+notes+references (limit 12,000): {main + wc(notes) + wc(refs)}")
