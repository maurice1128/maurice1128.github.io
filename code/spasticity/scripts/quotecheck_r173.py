# -*- coding: utf-8 -*-
"""Verify QUOTED STRINGS that name a container against the container they name.

Written round 173, in the round that discovered the class, and the reason is stated rather than
assumed: unlike SO-8's vocabulary lint this instrument has GROUND TRUTH -- a quoted string either
appears in the named file or it does not -- which is exactly council_bytecheck's shape. Its
false-positive rate is therefore measurable in the same round, by running it over the existing
corpus, and that measurement is reported alongside the catches.

WHAT IT CHECKS
  A line containing BOTH (a) an attribution -- a section reference like "section 2" / a backticked
  filename -- and (b) a quoted span of >= MINW words, is treated as a quotation with a named
  container. The span is then searched in that container.
    * backticked filename in the line  -> that file
    * otherwise a bare section ref     -> the SAME document
  Whitespace and the markdown emphasis characters are normalised before comparison, because a
  quotation re-wrapped across lines or bolded mid-span is still the same quotation.

WHAT IT CANNOT DO, stated so it is not oversold
  1. It cannot tell a fabricated quotation from a coined phrase an author put in quotes for
     emphasis. Those are the false positives, and they are counted, not hidden.
  2. It cannot check a quotation whose container is not on disk or not named.
  3. It cannot tell whether the quotation is from the RIGHT part of the named file.

Usage:  python quotecheck_r173.py <file.md> [...]
Exit 0 if every resolvable quotation is found in its container, 1 otherwise.
"""
import io
import os
import re
import sys

ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"
MINW = 5
QUOTED = re.compile(r"[\u201c\"]([^\u201c\u201d\"]{20,400})[\u201d\"]")
FILEREF = re.compile(r"`([A-Za-z0-9_.\-]+\.(?:md|py|json|scone|txt))`")
SECREF = re.compile(r"(?:\u00a7|section\s)\s?\d")
EMPH = re.compile(r"[*_`\u2014\u2013]+")
WS = re.compile(r"\s+")
BQ = re.compile(r"(?m)^\s*>\s?")          # markdown blockquote markers are not part of a quotation
ELIDE = re.compile(r"\u2026|\.\.\.")      # an elided quotation is verified segment by segment


def norm(s):
    return WS.sub(" ", EMPH.sub(" ", BQ.sub(" ", s))).strip().lower()


def section_of(lines, num):
    """Body of '## <num>. ...' up to the next '## '. Returns None if absent."""
    start = None
    for j, l in enumerate(lines):
        if re.match(r"^#+\s*%s[.\s]" % re.escape(num), l):
            start = j
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return norm(" ".join(lines[start:end]))


def resolve(name):
    for sub in ("", "paper", "scone"):
        p = os.path.join(ROOT, sub, name)
        if os.path.isfile(p):
            return p
    return None


def check(path):
    lines = io.open(path, encoding="utf-8").read().splitlines()
    body = norm(io.open(path, encoding="utf-8").read())
    found = missing = unres = 0
    print("=" * 78)
    print(os.path.basename(path))
    print("=" * 78)
    for i, ln in enumerate(lines):
        # a quotation may be wrapped; join this line with the next two for span extraction
        window = " ".join(BQ.sub("", x) for x in lines[i:i + 3])
        for m in QUOTED.finditer(window):
            span = m.group(1)
            if len(span.split()) < MINW:
                continue
            fr = FILEREF.search(ln)
            if not fr and not SECREF.search(ln):
                continue
            if fr:
                tgt = resolve(fr.group(1))
                tname = fr.group(1)
                if tgt is None:
                    print("  UNRESOLVED  line %-5d container %-34s not on disk" % (i + 1, tname))
                    unres += 1
                    continue
                hay = norm(io.open(tgt, encoding="utf-8").read())
            else:
                # SAME-DOCUMENT section reference. The document contains the quotation itself, so
                # searching the whole file always succeeds -- that self-satisfying check is what
                # let the round-169 fabrication through. Extract the NAMED SECTION and search only
                # there, with the quoting line's own section excluded by construction.
                sm = re.search(r"(?:§|section\s)\s?(\d+)", ln)
                tname = "(this file, section %s)" % sm.group(1)
                hay = section_of(lines, sm.group(1))
                if hay is None:
                    print("  UNRESOLVED  line %-5d container %-34s section not found"
                          % (i + 1, tname))
                    unres += 1
                    continue
            # an elided quotation ("A ... B") is verified segment by segment
            segs = [norm(x) for x in ELIDE.split(span)]
            segs = [s for s in segs if len(s.split()) >= 4]
            if not segs:
                continue
            ok = all((s in hay) or (" ".join(s.split()[:8]) in hay) for s in segs)
            if ok:
                found += 1
            else:
                print("  NOT FOUND   line %-5d container %-34s" % (i + 1, tname))
                print("              %s" % (span[:110] + ("..." if len(span) > 110 else "")))
                missing += 1
    print("\n  %d quotations verified, %d NOT FOUND, %d unresolvable container\n"
          % (found, missing, unres))
    return missing


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    sys.exit(1 if sum(check(a) for a in args) else 0)
