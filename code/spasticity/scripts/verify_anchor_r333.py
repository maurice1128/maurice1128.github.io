# -*- coding: utf-8 -*-
"""Confirm the r333 anchoring, matching the manuscript reference across BOTH key and value.

r333's own miss came from filtering values only: in CYCLE_CONVENTION_CONTRADICTION_r322.json the
manuscript name is the KEY and the line number is the VALUE, so a value-only scan is blind to it.
This walks key and value together.
"""
import glob, io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
LINE = re.compile(r"[Ll]ines?\s+\d+")
SUB = ("ORIGINAL_WRONG", "SUPERSEDED", "_WRONG", "WERE_WRONG", "CORRECTION", "_note")

rows = []
for f in sorted(glob.glob(os.path.join(P, "*.json"))):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue

    def w(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                # the manuscript may be named in the KEY and the line number in the VALUE
                if "RESULTS_3d_r214" in str(k) and isinstance(v, str) and LINE.search(v):
                    rows.append((os.path.basename(f), p + "/" + str(k), "key=file val=line"))
                w(v, p + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                w(v, p + "[%d]" % i)
        elif isinstance(o, str) and LINE.search(o):
            if "config.scone" in o or ".hfd" in o:
                return
            if "RESULTS_3d_r214" in o or re.search(r"\bsec0c\b|\bsec1\b|\bsec2\b", o):
                rows.append((os.path.basename(f), p, "value"))
    w(d)

print("%-44s %-52s %-18s %s" % ("file", "key path", "form", "status"))
live = set()
for f, p, form in rows:
    sub = any(s in p for s in SUB)
    if not sub:
        live.add(f)
    print("%-44s %-52s %-18s %s" % (f[:44], p[:52], form, "subordinate" if sub else "LIVE"))
print()
print("files with a LIVE manuscript line citation: %d" % len(live))
for f in sorted(live):
    print("   %s" % f)
