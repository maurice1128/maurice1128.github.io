# -*- coding: utf-8 -*-
"""Dump every mtime-bearing string in PROVENANCE_STALENESS_r316.json with its key path.

Written to a file rather than passed via -c: the previous inline attempt returned zero matches
for a file that is entirely about timestamps, which is a quoting failure, not a finding.
"""
import io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
F = os.path.join(P, "PROVENANCE_STALENESS_r316.json")
d = json.load(io.open(F, encoding="utf-8"))

MT = re.compile(r"2026-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}")
rows = []


def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + "[%d]" % i)
    elif isinstance(o, str) and MT.search(o):
        rows.append((p, o))


walk(d)
print("mtime-bearing strings: %d" % len(rows))
print()
for p, v in rows:
    tail = p.split("/")[-1]
    cur = ("now" in tail.lower()) or ("actual" in tail.lower()) or ("current" in tail.lower())
    print("%-4s %s" % ("CUR" if cur else "", p[:86]))
    print("       %s" % v[:120])
print()
print("presented-as-current by key wording: %d"
      % sum(1 for p, _ in rows
            if any(s in p.split("/")[-1].lower() for s in ("now", "actual", "current"))))
print("top-level keys: %s" % list(d))
