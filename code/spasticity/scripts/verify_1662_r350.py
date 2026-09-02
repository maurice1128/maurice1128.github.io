# -*- coding: utf-8 -*-
"""Round-four Defect 16 worst case: where does the headline 1.662 deg actually live?

String grep cannot answer this. A float 1.6615... serializes as "1.6615" and never
matches the literal "1.662"; a rounded 1.662 in prose never matches a float scan.
Both resolvers are run here and reported separately, because disagreement between
them IS the finding.
"""
import glob, io, json, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
TOL = 0.0006          # anything that rounds to 1.662 at three decimals


def numeric_hits(obj):
    out = []

    def w(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                w(v, p + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                w(v, p + "[%d]" % i)
        elif isinstance(o, bool):
            pass
        elif isinstance(o, (int, float)):
            if abs(float(o) - 1.662) < TOL:
                out.append((p, repr(o)))
        elif isinstance(o, str):
            if "1.662" in o or "1.661" in o:
                out.append((p, o[:110]))
    w(obj)
    return out


rows = []
for f in sorted(glob.glob(os.path.join(P, "*.json"))):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue
    h = numeric_hits(d)
    if h:
        rows.append((os.path.basename(f), os.path.getsize(f), h))

print("JSON deposits carrying a value that rounds to 1.662 : %d" % len(rows))
for name, size, h in rows:
    print()
    print("  %s  (%d B)  %d hit(s)" % (name, size, len(h)))
    for p, v in h[:10]:
        print("      %s = %s" % (p[:110], v))

print()
print("--- prose ---")
for f in sorted(glob.glob(os.path.join(P, "*.md"))):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        s = io.open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if "1.662" not in s:
        continue
    lines = [l for l in s.splitlines() if "1.662" in l]
    print("  %s  (%d B)  %d line(s)" % (os.path.basename(f), os.path.getsize(f), len(lines)))
    for l in lines[:6]:
        print("      %s" % l.strip()[:150])
