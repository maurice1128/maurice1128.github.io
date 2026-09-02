# -*- coding: utf-8 -*-
"""Re-verify SCRIPT_HASHES_r307.json against the scripts on disk.

Its assertion about files being unchanged is perishable by construction: any later write
falsifies it and nothing re-checks. This recomputes every digest it records.
"""
import hashlib, io, json, os, re, time

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
S = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
d = json.load(io.open(os.path.join(P, "SCRIPT_HASHES_r307.json"), encoding="utf-8"))

HEX = re.compile(r"^[0-9a-f]{16,64}$")
pairs = []


def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.endswith(".py") and isinstance(v, str) and HEX.match(v.strip()):
                pairs.append((k, v.strip(), p + "/" + k))
            elif k.endswith(".py") and isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, str) and HEX.match(vv.strip()):
                        pairs.append((k, vv.strip(), p + "/" + k + "/" + kk))
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + "[%d]" % i)


walk(d)
print("script digests recorded: %d" % len(pairs))
print()
bad = 0
for name, dig, path in pairs:
    f = os.path.join(S, name)
    if not os.path.exists(f):
        print("  %-34s MISSING ON DISK" % name)
        bad += 1
        continue
    actual = hashlib.sha256(io.open(f, "rb").read()).hexdigest()
    ok = actual.startswith(dig) or dig.startswith(actual[:len(dig)])
    if not ok:
        bad += 1
    print("  %-34s %-8s recorded %s  actual %s  mtime %s"
          % (name, "MATCH" if ok else "MISMATCH", dig[:16], actual[:16],
             time.strftime("%m-%d %H:%M:%S", time.localtime(os.path.getmtime(f)))))
print()
print("mismatches: %d" % bad)
print("deposit mtime: %s"
      % time.strftime("%Y-%m-%d %H:%M:%S",
                      time.localtime(os.path.getmtime(os.path.join(P, "SCRIPT_HASHES_r307.json")))))
