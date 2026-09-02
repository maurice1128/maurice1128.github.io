# -*- coding: utf-8 -*-
"""Check round four's Defect 9: a registration edited after its results, "and nothing records it".

Two separate questions:
  (a) is the digest/byte mismatch real?
  (b) is it true that NOTHING records it -- or does the manuscript document it?
The session's own history says the r229 breach was documented in the manuscript, so (b) may be
overstated. Round three's check 30 also verified the manuscript's account.
"""
import glob, io, json, os, hashlib, re, time

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
REG = os.path.join(P, "PREREG_2ndbody_r229.md")

b = io.open(REG, "rb").read()
print("PREREG_2ndbody_r229.md on disk : %d bytes  sha256 %s" % (len(b), hashlib.sha256(b).hexdigest()[:16]))
print("  mtime %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(REG))))
print()

print("deposits claiming a prereg digest for it:")
for f in sorted(glob.glob(os.path.join(P, "BODY2_*.json"))):
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue
    s = json.dumps(d)
    if "PREREG_2ndbody_r229" not in s:
        continue
    pv = d.get("provenance", {})
    print("  %-34s prereg_sha256=%s bytes=%s  mtime %s"
          % (os.path.basename(f), str(pv.get("prereg_sha256"))[:16], pv.get("prereg_bytes"),
             time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(f)))))
print()

# (b) does the manuscript record the post-hoc edit?
m = io.open(os.path.join(P, "RESULTS_3d_r214.md"), encoding="utf-8").read()
flat = re.sub(r"\s+", " ", m)
for probe in ("27,260", "27260", "ce572133", "edited after", "after the result", "2ndbody"):
    n = flat.count(probe)
    print("manuscript mentions %-18s : %d" % (repr(probe), n))
i = flat.find("ce572133")
if i > 0:
    print()
    print("context:")
    print("  ..." + flat[max(0, i - 320):i + 120] + "...")
