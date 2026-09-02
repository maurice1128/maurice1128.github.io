# -*- coding: utf-8 -*-
"""Resolve the disagreement: classify every line-number citation by KEY PATH, not by presence.

My r332 scan found {BANDFILL, CLASSIFIER, LMRONLY}; the agent found {BANDFILL,
CYCLE_CONVENTION_CONTRADICTION, PROVENANCE_STALENESS}. Only one overlaps. A presence test
cannot separate a LIVE citation from one preserved subordinately after a fix, and it also
misses phrasings that do not name the manuscript adjacently. This walks the key path.
"""
import glob, io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
LINE = re.compile(r"[Ll]ines?\s+\d+")
SUB = ("ORIGINAL_WRONG", "SUPERSEDED", "_WRONG", "WERE_WRONG", "CORRECTION", "r331_note")

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
                w(v, p + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                w(v, p + "[%d]" % i)
        elif isinstance(o, str) and LINE.search(o):
            # only manuscript citations; skip config.scone / .hfd which are frozen artefacts
            if "config.scone" in o or ".hfd" in o:
                kind = "frozen-artefact (legitimate)"
            elif "RESULTS_3d_r214" in o or "sec0c" in o or "sec1" in o or "sec2" in o:
                kind = "manuscript"
            else:
                kind = "manuscript?" if "line" in o.lower() else "other"
            sub = any(s in p for s in SUB)
            rows.append((os.path.basename(f), p, kind, sub))
    w(d)

print("%-42s %-46s %-28s %s" % ("file", "key path", "target", "status"))
live_files = set()
for f, p, kind, sub in rows:
    if kind == "other":
        continue
    status = "subordinate" if sub else "LIVE"
    if status == "LIVE" and kind.startswith("manuscript"):
        live_files.add(f)
    print("%-42s %-46s %-28s %s" % (f[:42], p[:46], kind, status))
print()
print("files with a LIVE manuscript line citation: %d" % len(live_files))
for f in sorted(live_files):
    print("   %s" % f)
