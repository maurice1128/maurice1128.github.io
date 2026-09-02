# -*- coding: utf-8 -*-
"""Independently reproduce the r326 value search.

Parses every live JSON in paper\ (excluding .bak_) and counts float leaves within tolerance of
each of the five figures the manuscript attributed to VERIFY_F5_r231.json. The point is not
only whether a container exists but how many coincidental hits each value attracts — a high
coincidence rate is why a numeric match cannot establish provenance.
"""
import io, json, os, glob

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
TARGETS = [1071.0, 0.1458, 0.6569, 0.1246, 0.2793]
TOL = 5e-4

files = [f for f in glob.glob(os.path.join(P, "*.json")) if ".bak_" not in os.path.basename(f)]
hits = {t: [] for t in TARGETS}
parsed = 0


def walk(o, path, src):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k), src)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i, src)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        for t in TARGETS:
            if abs(float(o) - t) <= TOL:
                hits[t].append((os.path.basename(src), path))


for f in files:
    try:
        walk(json.load(io.open(f, encoding="utf-8")), "", f)
        parsed += 1
    except Exception:
        pass

print("live JSON parsed : %d of %d   tolerance %.0e" % (parsed, len(files), TOL))
print()
for t in TARGETS:
    h = hits[t]
    print("%-10s %3d matches" % (("%g" % t), len(h)))
    for src, path in h[:3]:
        print("     %s%s" % (src, path))
    if len(h) > 3:
        print("     ... and %d more" % (len(h) - 3))
