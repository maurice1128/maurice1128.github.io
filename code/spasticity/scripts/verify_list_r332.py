# -*- coding: utf-8 -*-
"""Independently confirm the r332 revalidated list.

Two checks: which live deposits still cite the manuscript by line number, and whether
VERIFY_R298.json's gap_deg fix from r317 is still in place.
"""
import glob, io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PAT = re.compile(r"(RESULTS_3d_r214[^\"]{0,90}?[Ll]ines?\s+\d+"
                 r"|[Ll]ines?\s+\d+[^\"]{0,70}?RESULTS_3d_r214"
                 r"|sec0c line \d+|sec1 \(lines|sec2 \(line)")

hits = {}
for f in glob.glob(os.path.join(P, "*.json")):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        s = json.dumps(json.load(io.open(f, encoding="utf-8")))
    except Exception:
        continue
    m = PAT.findall(s)
    if m:
        hits[os.path.basename(f)] = len(m)

print("live deposits citing the manuscript by line number:")
for k in sorted(hits):
    print("  %-46s %d" % (k, hits[k]))
print("  total files: %d" % len(hits))
print()

v = json.load(io.open(os.path.join(P, "VERIFY_R298.json"), encoding="utf-8"))
g = [b.get("gap_deg") for b in v.get("blocks", [])]
num = [x for x in g if isinstance(x, (int, float))]
print("VERIFY_R298 gap_deg per block : %s" % g)
print("numeric gap_deg remaining     : %d  -> %s" % (len(num), num))
