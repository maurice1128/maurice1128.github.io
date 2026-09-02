"""Has any analysis script been edited without regenerating the artefact it writes?

The recurring defect in this project is "upstream recomputed, downstream not". This is its
mirror image, and it cost a real inconsistency: biocv_equivalence.py expressed its equivalence
bounds as a percentage of a 2 deg minimal detectable change while the manuscript cited Wilken
et al.'s ~5 deg for the same quantity. The denominator was corrected in the script, and nothing
changed in the paper -- because the script wrote BIOCV_EQUIV.txt, a file retired earlier in the
session, while the supplement reads BIOCV_EQUIV_BOUNDS.txt. A live script writing to a dead path
is invisible to every other check here: the artefact is self-consistent, the drift check compares
the paper against the artefact, and the artefact simply never moves.

Two things are checked for every script that declares an output path:

  1. the file it says it writes exists, and is not one of the retired `_SUPERSEDED_` artefacts;
  2. it is newer than the script, so an edit has been followed by a run.

Scripts too slow to sit inside regenerate_all.sh are exactly the ones that go stale, so this is
the check that lets them stay outside it.
"""
import glob
import io
import os
import re

ROOT = "D:/ROWV_paper"

# OUTF = "..." / OUT = "...", and the env-var form OUTF = os.environ.get("VAR", "...").
# The literal-only pattern was silently skipping 17 scripts -- including the sources of
# Tables S3m, S2c, S3l and S7 -- so the one edit-without-regenerate this gate exists to
# catch was invisible to it. A gate is only worth its exit code over the files it can see.
DECL = re.compile(r"^OUTF?\s*=\s*(?:os\.environ\.get\(\s*[\"'][^\"']*[\"']\s*,\s*)?[\"']([^\"']+\.txt)[\"']", re.M)

# Only artefacts the submission actually reads can go stale in a way that matters. Flagging an
# abandoned exploratory branch as well would make this a permanently-red gate, and a gate that is
# always red is one people learn to ignore -- the same reason the provenance false-pass rate was
# demoted from a gate to a printed measurement.
CONSUMERS = ["build_supplement.py", "regenerate_all.sh"] + [
    os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "check_*.py"))
    + glob.glob(os.path.join(ROOT, "render_*.py"))]
# One script is knowingly newer than its artefact: regenerating the m = 50 permutation costs
# about 3.3 hours and the edit was three words of prose that no number depends on, reworded
# at render time by build_supplement.py's REWORD list instead. It is exempted BY NAME and
# printed every run, because a permanently-red gate is one people learn to ignore and a
# silently-skipped one is worse.
EXEMPT = {"biocv_permutation_v2.py": "header prose reworded at render time; "
                                     "regenerating costs ~3.3 h and moves no number"}
exempt = []

consumed = ""
for c in CONSUMERS:
    path = os.path.join(ROOT, c)
    if os.path.exists(path):
        consumed += io.open(path, encoding="utf-8", errors="replace").read()

# An artefact must also be newer than the artefacts it CONSUMES. Comparing an artefact only
# with its own script misses the case that actually occurred: the offset control was rerun
# after a correction, and the two dependence sensitivities that read its p-values were left
# behind, still reporting counts from the superseded computation. Every content check passed,
# because the stale file was internally consistent.
INPUT = re.compile(r"[\"'](D:/BioCV/[A-Za-z0-9_./-]+\.(?:txt|pkl))[\"']")
upstream = []
stale, missing, retired, orphan = [], [], [], []
for src in sorted(glob.glob(os.path.join(ROOT, "*.py"))):
    name = os.path.basename(src)
    if name.startswith(("check_", "measure_", "render_", "build_", "paper_stats")):
        continue
    m = DECL.search(io.open(src, encoding="utf-8", errors="replace").read())
    if not m:
        continue
    out = m.group(1)
    if os.path.basename(src).startswith("_SUPERSEDED_"):
        # A retired script writing to a retired artefact is not the defect this gate is
        # for -- that defect is a LIVE script writing to a dead path. Retirement has to be
        # visible in the filename, so renaming is the declaration.
        continue
    if "_SUPERSEDED_" in out:
        retired.append((name, out))
        continue
    if os.path.basename(out) not in consumed:
        # Nothing in the submission path reads it, so its age cannot affect the paper.
        orphan.append((name, out))
        continue
    if not os.path.exists(out):
        missing.append((name, out))
        continue
    if os.path.getmtime(src) > os.path.getmtime(out) + 1:
        if name in EXEMPT:
            exempt.append((name, out, EXEMPT[name]))
        else:
            stale.append((name, out))
    body = io.open(src, encoding="utf-8", errors="replace").read()
    for dep in sorted(set(INPUT.findall(body))):
        if os.path.normpath(dep) == os.path.normpath(out) or not os.path.exists(dep):
            continue
        if "_SUPERSEDED_" in dep or "_GOLDEN_" in dep or "_progress" in dep:
            # A progress file is written BY the run, not consumed by it, so it is always
            # newer than the artefact and would fire on every script that logs progress.
            continue
        if os.path.getmtime(dep) > os.path.getmtime(out) + 1:
            upstream.append((name, out, dep))

if upstream:
    print(f"{len(upstream)} artefact(s) OLDER THAN AN INPUT THEY READ:")
    for n, o, d in upstream:
        print(f"    {n:<30} {os.path.basename(o)}")
        print(f"        reads {os.path.basename(d)}, which is newer -- rerun {n}")
    print()

print(f"{len(glob.glob(os.path.join(ROOT, '*.py')))} scripts scanned")
if exempt:
    print(f"{len(exempt)} script(s) newer than their artefact BY DECLARED EXEMPTION:")
    for n, o, why in exempt:
        print(f"    {n:<34}-> {o}")
        print(f"        {why}")
if retired:
    print(f"{len(retired)} script(s) writing to a RETIRED artefact -- nothing downstream reads these:")
    for n, o in retired:
        print(f"    {n:<34}-> {o}")
if missing:
    print(f"{len(missing)} script(s) whose declared output does not exist:")
    for n, o in missing:
        print(f"    {n:<34}-> {o}")
if stale:
    print(f"{len(stale)} artefact(s) older than the script that writes them:")
    for n, o in stale:
        print(f"    {n:<34}-> {o}")
    print("\nThe edit has not been run. Anything the paper quotes from these files predates it.")
if orphan:
    print(f"{len(orphan)} script(s) outside the submission path (nothing reads their output; "
          f"not a failure):")
    for n, o in orphan:
        print(f"    {n:<34}-> {o}")
if not (retired or missing or stale):
    print(f"every artefact the submission reads is newer than the script that writes it "
          f"({len(orphan)} script(s) outside that path)")

_fail = False
# --- source-hash stamps ---------------------------------------------------------------
# An artefact newer than its script can still have been written by OLDER code: a long run
# launched before an edit finishes after it, and the timestamp comparison above passes. Where a
# script stamps "source-sha256: <hash of its own file>" into its artefact, that stamp is compared
# against the script's current hash, which catches the case timestamps cannot see.
import hashlib as _hl

_STAMP = re.compile(r"^source-sha256:[ ]*([0-9a-f]{64})[ ]*$", re.M)
_STAMPED = {
    "D:/BioCV/BIOCV_CONTIGUOUS.txt": "D:/ROWV_paper/biocv_contiguous.py",
}
_bad = []
for _art, _scr in _STAMPED.items():
    try:
        _txt = io.open(_art, encoding="utf-8").read()
        _cur = _hl.sha256(io.open(_scr, "rb").read()).hexdigest()
    except OSError:
        continue
    _m = _STAMP.search(_txt)
    if not _m:
        _bad.append((_art, "carries no source stamp"))
    elif _m.group(1) != _cur:
        _bad.append((_art, "was written by a different version of " + _scr.rsplit("/", 1)[-1]))
if _bad:
    print("FAIL: an artefact does not match the code that is supposed to have produced it")
    for _a, _why in _bad:
        print("  ", _a, "--", _why)
    _fail = True

if not _fail:
    print("every stamped artefact matches the current source of its script")

raise SystemExit(1 if (retired or missing or stale or upstream or _fail) else 0)