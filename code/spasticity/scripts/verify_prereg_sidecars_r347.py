# -*- coding: utf-8 -*-
"""Check the two registration sidecars round four/r347 report as false.

A registration's sidecar is what fixes what was registered. If it diverges, either the file was
edited after hashing (the r229 failure) or the sidecar was written against something else.
Reports mtime ordering too, since that is what distinguishes the two cases.
"""
import hashlib, io, os, re, time

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
TARGETS = ["PREREG_3d_replication_r179.md", "PREREG_3d_specificity_r178.md"]


def stamp(p):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p)))


for name in TARGETS:
    f = os.path.join(P, name)
    for sc in (f + ".sha256", os.path.join(P, name.replace(".md", ".PREREAD.sha256"))):
        if not os.path.exists(sc):
            continue
        txt = io.open(sc, encoding="utf-8", errors="replace").read()
        m = re.search(r"\b([0-9a-f]{64})\b", txt)
        rec = m.group(1) if m else None
        act = hashlib.sha256(io.open(f, "rb").read()).hexdigest() if os.path.exists(f) else None
        print("%s" % name)
        print("   sidecar        : %s  (mtime %s)" % (os.path.basename(sc), stamp(sc)))
        print("   recorded digest: %s" % (rec[:32] if rec else "unparseable"))
        print("   actual  digest : %s" % (act[:32] if act else "file missing"))
        print("   file mtime     : %s   bytes %d" % (stamp(f), os.path.getsize(f)))
        print("   MATCH          : %s" % (rec == act))
        print("   file newer than sidecar: %s"
              % (os.path.getmtime(f) > os.path.getmtime(sc)))
        print()
