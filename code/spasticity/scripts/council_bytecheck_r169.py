# -*- coding: utf-8 -*-
"""Verify byte counts STATED in a council record against what is on disk.

Written round 169 because the fabricated-byte-count class recurred in the round immediately
after it was disclosed and filed. Honesty is not a control; this is.

WHAT IT CHECKS
  Rows of the form   | `path` | 12,345 B |   or   | `path` | **12,345** |
  in a markdown table. The path is resolved against the project root and stat'ed.

WHAT IT CANNOT CHECK, STATED SO THE CONTROL IS NOT OVERSOLD
  1. A fabricated number that names no file. Only counts tied to a path are verifiable.
  2. Historical records. Mutable files (the register, the manuscripts) legitimately differ from
     what an old round stated. Only the CURRENT round's record, and any row naming an immutable
     file (a registration, a .sha256, a .bak_ pre-image), can be checked after the fact.
  3. Whether the right file was named.

Usage:  python council_bytecheck_r169.py <council_record.md> [...]
Exit 0 if every resolvable row matches, 1 otherwise.
"""
import io
import os
import re
import sys

ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"
ROW = re.compile(r"^\|\s*`?([^`|]+?)`?\s*\|\s*\*{0,2}([\d,]+)\*{0,2}\s*B?\s*[^|]*\|")


def resolve(p):
    p = p.strip().replace("\\", "/")
    for cand in (os.path.join(ROOT, p), os.path.join(ROOT, "paper", p), os.path.join(ROOT, "scone", p)):
        if os.path.isfile(cand):
            return cand
    return None


def check(path):
    print("=" * 78)
    print(path)
    print("=" * 78)
    ok = bad = skip = 0
    for ln in io.open(path, encoding="utf-8"):
        m = ROW.match(ln.rstrip("\n"))
        if not m:
            continue
        name, num = m.group(1), m.group(2)
        if "/" not in name and "." not in name:
            continue
        try:
            stated = int(num.replace(",", ""))
        except ValueError:
            continue
        f = resolve(name)
        if f is None:
            print("  SKIP  %-56s stated %-9s (path not resolvable)" % (name, "{:,}".format(stated)))
            skip += 1
            continue
        actual = os.path.getsize(f)
        if actual == stated:
            print("  OK    %-56s %s B" % (name, "{:,}".format(actual)))
            ok += 1
        else:
            print("  FAIL  %-56s stated %s  actual %s"
                  % (name, "{:,}".format(stated), "{:,}".format(actual)))
            bad += 1
    print("\n  %d ok, %d MISMATCHED, %d unresolvable\n" % (ok, bad, skip))
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    sys.exit(1 if sum(check(a) for a in args) else 0)
