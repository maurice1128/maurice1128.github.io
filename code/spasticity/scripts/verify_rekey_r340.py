# -*- coding: utf-8 -*-
"""Confirm the r340 re-key: zero mtime facts presented as current.

Run from a file, not via -c: two inline probes returned false negatives on this same file
because the quoting layer ate the regex backslashes.

A fact is "presented as current" when the clause stating the value uses now/current/actual
WITHOUT an as-of instant inside that same clause.
"""
import io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
F = os.path.join(P, "PROVENANCE_STALENESS_r316.json")
d = json.load(io.open(F, encoding="utf-8"))

MT = re.compile(r"2026-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}")
CUR = re.compile(r"\bnow\b|\bcurrent\b|\bactual\b", re.I)
ASOF = re.compile(r"as[- ]of|as measured|measured_at|measured\s+2026|frozen_at", re.I)

rows, flagged = [], []


def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + "[%d]" % i)
    elif isinstance(o, str) and MT.search(o):
        rows.append((p, o))
        tail = p.split("/")[-1]
        cur_key = bool(CUR.search(tail)) and not ASOF.search(tail)
        # the clause carrying the value
        for m in MT.finditer(o):
            s = max(0, m.start() - 160)
            clause = o[s:m.end() + 60]
            if CUR.search(clause) and not ASOF.search(clause):
                flagged.append((p, clause[:150]))
                break
        else:
            if cur_key and not ASOF.search(o):
                flagged.append((p, o[:150]))


walk(d)
print("mtime-bearing strings        : %d" % len(rows))
print("presented as current         : %d" % len(flagged))
for p, c in flagged:
    print("  %s" % p[:90])
    print("     %s" % c)
print()
print("keys retired?")
blob = json.dumps(d)
for k in ("actual_values_now", "what_the_OK_verdicts_now_rest_on",
          "deposit_mtimes_measured", "OK_verdicts_basis_measured"):
    print("  %-36s present: %s" % (k, ('"%s"' % k) in blob))
