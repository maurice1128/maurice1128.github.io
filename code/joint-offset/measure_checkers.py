"""Measure what each standing checker actually catches, by injecting the defect it exists to find.

A checker that has never been shown to fail is not evidence of anything. Two of this project's
checkers reported clean for a whole round while blind to the exact class they were written for:
`provenance.py` passed 96% of fabricated numbers, and `check_signs.py` passed an inverted 1/d row
in the same run whose comment claimed that row was now covered.

This injects one defect at a time into a copy of the real files, runs the checker, restores, and
reports the detection rate. Restoration is in a finally block and the freeze is verified after
every case, so a crash cannot leave the manuscript modified.

Run it after any change to a checker, and read the rate rather than the exit code.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = "D:/ROWV_paper"
PY = "C:/Users/maurice/miniforge3/envs/stroke-gait/python.exe"
MS = os.path.join(ROOT, "MANUSCRIPT_SUBMISSION.md")
TB = os.path.join(ROOT, "TABLES_SUBMISSION.md")

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def run(script):
    r = subprocess.run([PY, os.path.join(ROOT, script)], capture_output=True, env=ENV, cwd=ROOT)
    return r.returncode


def inject(path, old, new):
    """Replace once; return False if the anchor is absent so a silent no-op cannot count as a pass."""
    s = io.open(path, encoding="utf-8").read()
    if old not in s:
        return False
    io.open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return True


# (checker, target file, anchor, corrupted form, what the defect is)
INTER = os.path.join(ROOT, "biocv_interaction_fdr.py")
SUBSET = os.path.join(ROOT, "biocv_subset_control.py")
TRANSFER = os.path.join(ROOT, "biocv_detector_transfer.py")
HALPE = os.path.join(ROOT, "biocv_halpe.py")
# The supplement is assembled from the ARTEFACTS, not from the scripts, so a leak has
# to be injected where build_supplement.py actually reads.
ARTEFACT = "D:/BioCV/BIOCV_SUBSET_CONTROL.txt"

COVER = os.path.join(ROOT, "COVER_LETTER.md")

CASES = [
    # The cover letter quotes the title. It went stale twice while every checker passed,
    # because no checker read the cover letter until check_title.py.
    # "Table S15" was captured as "S1" on both sides of check_xrefs.py, so every two-digit
    # supplement reference validated against a section it does not name.
    # A long run launched before an edit finished after it and overwrote this artefact with
    # output from older code. check_stale.py passed it -- the file WAS newer than the script --
    # and only check_drift.py caught it, downstream, after the numbers reached the manuscript.
    ("check_stale.py", "D:/BioCV/BIOCV_CONTIGUOUS.txt", "source-sha256: ",
     "source-sha256: 0000000000000000000000000000000000000000000000000000000000000000",
     "an artefact written by a superseded version of its script"),
    # S19 was a real section by the time this ran, so the injected pointer resolved and the case
    # silently stopped testing anything. Aim at a number the supplement will not reach.
    # The anchor was "Table S12", which compression left only in the plural form "Tables S12,
    # S14"; a singular-form anchor goes stale silently. Anchored on a pointer that stands alone.
    ("check_xrefs.py", MS, "Table S21", "Table S97",
     "a two-digit supplement pointer that resolves nowhere"),
    # Anchored on the phrase, not on the title text: the title has changed four times and an
    # anchor naming one of them goes stale silently, reported as ANCHOR ABSENT rather than as a
    # miss.
    ("check_title.py", COVER, "enclosed manuscript, *",
     "enclosed manuscript, *A superseded title ", "a cover letter quoting a superseded title"),
    ("check_prose_q.py", MS, "q = 0.006)", "q = 0.0063)", "a 4-dp q no artefact supports"),
    ("check_prose_q.py", MS, "q = 0.002)", "q = 0.017)", "a 3-dp q no artefact supports"),
    ("check_prose_q.py", MS, "q = 0.004)", "q = 0.07)", "a 2-dp q no artefact supports"),
    ("check_xrefs.py", MS, "Table S3b", "Table S3zz", "a supplement pointer that resolves nowhere"),
    ("check_xrefs.py", MS, "Fig. 2", "Fig. 9", "a figure reference with no caption"),
    ("check_citations.py", MS, "(Gelman and Stern, 2006)", "(Gelman and Stern, 2007)",
     "a citation whose year matches no entry"),
    # 55.98 was a poor choice: it exists in a CURRENT artefact, so injecting it is not drift.
    ("check_drift.py", TB, "+34.04%", "+37.77%", "a stated result in no artefact"),
    ("check_signs.py", TB, "| +0.148, q = 0.009 |", "| \u22120.148, q = 0.009 |",
     "an inverted sign in a Table 1a row"),
    ("check_signs.py", TB, "**+0.858, q = 0.006**", "**\u22120.858, q = 0.006**",
     "an inverted sign in the Gauss-Newton row"),
    ("check_signs.py", TB, "| +0.463, n.s. |", "| \u22120.463, n.s. |",
     "an inverted sign in a rejection row"),
    ("check_signs.py", TB, "| +0.256, q = 0.038\u2020 |", "| \u22120.256, q = 0.038\u2020 |",
     "an inverted sign in the 1/d row"),
    # An interaction row whose label names an arm the contrast does not contain. One such row
    # -- "DLT -> GN as published (w)" on the tuple ("gn_w2", "gn_w"), both arms Gauss-Newton --
    # sat in the family unnoticed until a cold reader could not reconcile Table 2(c) with the
    # Limitations. Everything else in check_signs.py covers the m=50 family only.
    (INTER, "\"GN objective: w^2-matched -> unmatched (w) [knee flex]\"",
     "\"DLT -> GN unmatched (w) [knee flex]\"",
     "an interaction label naming an arm the contrast lacks", "check_signs.py"),
    # A reference to a table PANEL that does not exist. "Table 1d" was cited three times and
    # never written, and check_xrefs.py passed it because the pattern kept only the digit.
    (TB, "**(d) Within one limb", "**(e) Within one limb", "a table panel that does not exist",
     "check_xrefs.py"),
    # A self-correction narrative reaching the supplement. The DEV_HISTORY guard was built from
    # phrases already seen ("council", "round 5", "supersede"), so it passed "Fixed here." for a
    # whole round while a REWORD entry stripped only the first two thirds of the very sentence it
    # was written to remove. A guard assembled from instances cannot catch the next instance.
    (ARTEFACT, "=== PART A", "=== PART A (an earlier run had this backwards; fixed here)",
     "a self-correction narrative reaching the reader", "build_supplement.py"),
    # A script edited without regenerating the artefact it writes. This is the mirror of the
    # project's recurring defect and is invisible to every content check: the artefact stays
    # internally consistent, it simply never moves.
    (SUBSET, "\"\"\"Is it the joint SET", "\"\"\"EDITED FOR THE INJECTION TEST\n\nIs it the joint SET",
     "a script edited without regenerating its artefact", "check_stale.py"),
    # An em dash where a minus sign belongs. Every numeric check passes: the number is right
    # and only its sign glyph is wrong, so nothing but a glyph-level check can see it.
    ("check_signs.py", MS, "[−0.932, −0.287]", "[—0.932, −0.287]",
     "an em dash standing in for a minus sign"),
    # An analysis scoring a distortion-CORRECTED cache against a RAW one. Table S9 did this for a
    # whole round: the offset share read 40% instead of 82% and the ankle offset direction
    # reversed, and every other checker passed the table because its numbers were internally
    # consistent and correctly transcribed. No content check can see WHICH CACHE a number came
    # from, which is why check_caches.py exists and why it has to be shown to fail.
    (TRANSFER, '"RTMO (one-stage)": "D:/BioCV/_cache_rtmo_undist"',
     '"RTMO (one-stage)": "D:/BioCV/_cache_rtmo"',
     "an analysis mixing corrected and raw detections", "check_caches.py"),
    # The same defect reached through the OTHER cache of the pair, to check the rule is
    # symmetric rather than keyed to one directory name.
    (HALPE, 'COCO_CACHE = "D:/BioCV/_cache_undist"', 'COCO_CACHE = "D:/BioCV/_cache_balanced"',
     "the mixed-footing defect injected through the other cache", "check_caches.py"),
]

# The cases above are written in two shapes; normalise to (script, path, old, new, what).
CASES = [c if len(c) == 5 and c[0].endswith(".py") and not c[0].startswith("D:")
         else (c[4], c[0], c[1], c[2], c[3]) for c in CASES]


def main():
    paths = {c[1] for c in CASES}
    originals = {p: io.open(p, encoding="utf-8").read() for p in paths}
    # Restoring the text is not enough for check_stale.py, which compares modification times:
    # rewriting a script leaves it newer than its artefact and the check would stay red after
    # the run. A measurement harness that damages the thing it measures is worse than none.
    mtimes = {p: (os.path.getatime(p), os.path.getmtime(p)) for p in paths}
    results = []
    try:
        for script, path, old, new, what in CASES:
            if not inject(path, old, new):
                results.append((script, what, "ANCHOR ABSENT"))
                continue
            code = run(script)
            io.open(path, "w", encoding="utf-8").write(originals[path])
            results.append((script, what, "caught" if code != 0 else "MISSED"))
    finally:
        for p, s in originals.items():
            io.open(p, "w", encoding="utf-8").write(s)
            os.utime(p, mtimes[p])

    by = {}
    for script, what, verdict in results:
        by.setdefault(script, []).append((what, verdict))

    print("injected-defect detection\n")
    for script in sorted(by):
        cases = by[script]
        hit = sum(1 for _, v in cases if v == "caught")
        print(f"  {script}   {hit}/{len(cases)}")
        for what, verdict in cases:
            mark = "  " if verdict == "caught" else ">>"
            print(f"  {mark}   {verdict:<14}{what}")
        print()

    missed = [r for r in results if r[2] != "caught"]
    print(f"{len(results) - len(missed)}/{len(results)} injected defects detected")
    if missed:
        print("A checker that misses its own defect class must not be cited as evidence.")

    # Restoring the mutated ARTEFACT is not enough. Each case runs build_supplement.py, which
    # writes SUPPLEMENT_SUBMISSION.md from whatever the artefact said AT THAT MOMENT, so after
    # this harness finishes the submitted supplement still carries the LAST injected defect.
    # Two reviewers read "(an earlier run had this backwards; fixed here)" in a submitted
    # supplement because of exactly this. The rebuild below restores it from clean sources.
    run("build_supplement.py")

    code = run("check_freeze.py")
    print("\nfreeze after restoration: " + ("intact" if code == 0 else "VIOLATED"))
    return 1 if (missed or code != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
