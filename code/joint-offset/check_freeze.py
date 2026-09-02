"""Has anything moved since the freeze?

The project's finding rate stayed flat across six audit cycles, and the cause was not the paper:
it was that the manuscript kept being edited inside the audit windows, so findings went stale and
fixes were never independently checked. This makes the freeze enforceable rather than an intention.
Run it before and after any audit round; a difference means the round's findings may already be
out of date.
"""
import hashlib
import io
import os
import re

MANIFEST = "D:/ROWV_paper/FREEZE_MANIFEST.txt"
ROOT = "D:/ROWV_paper"

if not os.path.exists(MANIFEST):
    raise SystemExit("no freeze manifest -- nothing is frozen")

recorded = {}
for line in io.open(MANIFEST, encoding="utf-8"):
    m = re.match(r"^\s{2}([0-9a-f]{64})\s\s(\S.*)$", line.rstrip())
    if m:
        recorded[m.group(2)] = m.group(1)

changed, missing = [], []
for name, want in recorded.items():
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        path = os.path.join(ROOT, "figures", name)
    if not os.path.exists(path):
        missing.append(name)
        continue
    got = hashlib.sha256(io.open(path, "rb").read()).hexdigest()
    if got != want:
        changed.append(name)

print(f"{len(recorded)} files under freeze")
if missing:
    print(f"{len(missing)} missing: " + ", ".join(missing))
if changed:
    print(f"{len(changed)} changed since the freeze:")
    for c in changed:
        print("    " + c)
    print("\nAny audit started before these changes may be reporting on a version that no longer")
    print("exists. Either re-freeze deliberately, or treat the audit as stale.")
else:
    print("unchanged since the freeze")

raise SystemExit(1 if (changed or missing) else 0)
