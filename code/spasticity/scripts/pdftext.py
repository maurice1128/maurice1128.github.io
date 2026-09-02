# -*- coding: utf-8 -*-
"""Extract full text from a downloaded reference PDF so citations can be checked against the
primary source rather than against an abstract or an agent's summary. Writes refs/<name>.txt.

Ligatures and soft hyphens are normalised: during the r481 reference audit three sentences that are
present verbatim in their sources were briefly reported as "not found" because the PDF stored them
with U+FB01 and end-of-line hyphenation.
"""
import io
import os
import re
import sys

from pypdf import PdfReader

OUT = r"C:\Users\maurice\Desktop\spasticity_paper\refs"
FIX = [("\ufb01", "fi"), ("\ufb02", "fl"), ("\ufb00", "ff"), ("\ufb03", "ffi"),
       ("\ufb04", "ffl"), ("\u00ad", ""), ("\u2010", "-"), ("\u2011", "-")]


def extract(pdf, name):
    r = PdfReader(pdf)
    parts = []
    for i, p in enumerate(r.pages):
        try:
            t = p.extract_text() or ""
        except Exception as e:
            t = "[page %d extraction failed: %s]" % (i + 1, e)
        parts.append("\n\n===== PAGE %d =====\n" % (i + 1) + t)
    s = "".join(parts)
    for a, b in FIX:
        s = s.replace(a, b)
    s = re.sub(r"-\n(?=[a-z])", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    dst = os.path.join(OUT, name + ".txt")
    io.open(dst, "w", encoding="utf-8", newline="").write(s)
    print("%s: %d pages, %d chars -> %s" % (name, len(r.pages), len(s), dst))
    return dst


if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
