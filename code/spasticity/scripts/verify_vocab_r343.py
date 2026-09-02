# -*- coding: utf-8 -*-
"""Spot-check the r343 census: is the convention documented anywhere, and how many marking keys?

Deliberately uses a NARROW, unambiguous pattern rather than a broad one — the agent's broad
pattern over-matched, and adding more terms is the failure this whole census is about. A narrow
pattern under-counts honestly; a broad one over-counts invisibly.
"""
import glob, io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
NARROW = re.compile(r"(_SUPERSEDED|_ORIGINAL_WRONG|_ORIGINAL_STALE|_ORIGINAL_REFUTED"
                    r"|_PREMISE_REFUTED|_UNDATED_ORIGINAL|_DEFECTIVE|_RETIRED|_WITHDRAWN)$")

keys, files = {}, set()
total = 0
for f in sorted(glob.glob(os.path.join(P, "*.json"))):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue

    def walk(o):
        global total
        if isinstance(o, dict):
            for k, v in o.items():
                total += 1
                if NARROW.search(str(k)):
                    keys[k] = keys.get(k, 0) + 1
                    files.add(os.path.basename(f))
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)

print("keys walked                       : %d" % total)
print("marking keys (narrow pattern)     : %d distinct, %d occurrences, %d files"
      % (len(keys), sum(keys.values()), len(files)))
print()
suf = {}
for k, n in keys.items():
    m = NARROW.search(k)
    suf[m.group(1)] = suf.get(m.group(1), 0) + n
for s in sorted(suf, key=lambda x: -suf[x]):
    print("   %-24s %d" % (s, suf[s]))
print()

# is the convention documented?
DOC = re.compile(r"suffix|naming convention|marks a field|not-live|subordinate key", re.I)
hits = []
for f in sorted(glob.glob(os.path.join(P, "*.json"))) + [os.path.join(P, "RESULTS_3d_r214.md")]:
    if ".bak_" in os.path.basename(f):
        continue
    try:
        s = io.open(f, encoding="utf-8").read()
    except Exception:
        continue
    if DOC.search(s):
        hits.append(os.path.basename(f))
print("files mentioning a naming/suffix convention: %d" % len(hits))
for h in hits[:10]:
    print("   %s" % h)
