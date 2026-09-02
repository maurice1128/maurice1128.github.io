# -*- coding: utf-8 -*-
"""Are FROZEN_MANIFEST.json's 53 recorded mtimes about frozen artefacts or live files?

A recorded mtime rots only if its subject can still be written. Result-directory artefacts are
frozen once a run ends (r325 established that for config.scone); files under paper\ are live.
This checks each subject's location and compares the recorded value to disk.
"""
import io, json, os, re, time

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RES = r"C:\Users\maurice\Documents\SCONE\results"
F = os.path.join(P, "FROZEN_MANIFEST.json")

d = json.load(io.open(F, encoding="utf-8"))
MT = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

rows = []


def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + "[%d]" % i)
    elif isinstance(o, str) and MT.match(o.strip()):
        rows.append((p, o.strip()))


walk(d)
print("mtime-shaped values in FROZEN_MANIFEST.json : %d" % len(rows))
print()

# what are the subjects? look for sibling filename keys
names = set(re.findall(r"[A-Za-z0-9_\-\.]+\.(?:json|md|py|scone|hfd|par|sto|txt)", json.dumps(d)))
inpaper = sorted(n for n in names if os.path.exists(os.path.join(P, n)))
elsewhere = sorted(n for n in names if n not in inpaper)
print("named files that live in paper\\ (LIVE, can still be written) : %d" % len(inpaper))
for n in inpaper[:12]:
    print("   %s" % n)
if len(inpaper) > 12:
    print("   ... and %d more" % (len(inpaper) - 12))
print()
print("named files not in paper\\ (result-dir / scone artefacts)      : %d" % len(elsewhere))
for n in elsewhere[:8]:
    print("   %s" % n)
if len(elsewhere) > 8:
    print("   ... and %d more" % (len(elsewhere) - 8))
print()
print("FROZEN_MANIFEST.json own mtime : %s"
      % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(F))))
print("top-level keys                 : %s" % list(d)[:10])
