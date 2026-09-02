# -*- coding: utf-8 -*-
"""Locate every live occurrence of '48 of 60' and classify each by whether it is a live claim
or a subordinate/explanatory mention. Counting occurrences cannot answer that; the key path can.
"""
import io, json, os, glob

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SUB = ("ORIGINAL_WRONG", "SUPERSEDED", "_WRONG", "CORRECTION", "D14", "r331", "r321", "note_48")

hits = []
for f in glob.glob(os.path.join(P, "*.json")):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue

    def w(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                w(v, p + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                w(v, p + "[%d]" % i)
        elif isinstance(o, str) and "48 of 60" in o:
            hits.append((os.path.basename(f), p))
    w(d)

print("occurrences of '48 of 60' : %d" % len(hits))
live = 0
for src, path in hits:
    sub = any(s in path for s in SUB)
    live += (not sub)
    print("  %-34s %-58s %s" % (src, path[:58], "subordinate" if sub else "LIVE CLAIM"))
print()
print("live claims: %d" % live)

c = json.load(io.open(os.path.join(P, "COVERAGE_RECONCILE_r305.json"), encoding="utf-8"))
n = c.get("SUPERSEDED_BY_r306", {}).get("note", "")
print("r305 live note says 47 : %s" % ("47 of 60" in n))
print("r305 live note says 48 : %s" % ("48 of 60" in n))
print("D14 block retained     : %s" % ("D14_internal_inconsistency" in c.get("SUPERSEDED_BY_r306", {})))
