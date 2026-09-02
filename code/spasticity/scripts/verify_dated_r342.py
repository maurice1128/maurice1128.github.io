# -*- coding: utf-8 -*-
"""Confirm the r342 rewrites: no live undated 'not edited' / 'untouched' assertion remains.

Subordinate keys are excluded, because a preserved undated original is required by policy and
counting it as live is the failure I made at r340.
"""
import glob, io, json, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
CLAIM = re.compile(r"not edited|untouched", re.I)
DATED = re.compile(r"2026-[0-9]{2}-[0-9]{2}|as[- ]of|as measured|measured_at", re.I)
SUB = ("UNDATED_ORIGINAL", "ORIGINAL_WRONG", "SUPERSEDED", "_WRONG", "ORIGINAL_STALE")

live, sub = [], 0
for f in sorted(glob.glob(os.path.join(P, "*.json"))):
    if ".bak_" in os.path.basename(f):
        continue
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue

    def walk(o, p=""):
        global sub
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + "[%d]" % i)
        elif isinstance(o, str):
            for m in CLAIM.finditer(o):
                s = max(0, m.start() - 150)
                clause = o[s:m.end() + 90]
                if DATED.search(clause):
                    continue
                if any(x in p for x in SUB):
                    sub += 1
                else:
                    live.append((os.path.basename(f), p[:80], clause[:130]))
                break
    walk(d)

print("live UNDATED assertions : %d" % len(live))
for f, p, c in live:
    print("  %s%s" % (f, p))
    print("     %s" % c)
print("subordinate/preserved   : %d" % sub)
print()
s = json.load(io.open(os.path.join(P, "SCRIPT_HASHES_r307.json"), encoding="utf-8"))
blob = json.dumps(s)
print("SCRIPT_HASHES carries two instants : %s" % ("REVERIFIED_r342" in blob))
print("original measurement retained      : %s" % ("2026-08-18" in blob and blob.count("2026-08-18") >= 2))
