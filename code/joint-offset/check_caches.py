"""Does any analysis compare two detection caches that are not on the same distortion footing?

Table S9 compared RTMPose against RTMO and reported that the offset's share of squared error did
not transfer (40% against 74-81%) and that the ankle offset direction reversed. Both were artefacts:
`_cache_undist` holds distortion-corrected detections and `_cache_rtmo` held raw ones, so the
difference between the two caches contained the distortion difference as well as the detector
difference -- landing on exactly the near-camera residuals Section 3.5 says distortion moves most.
Every other check passed on that table. The numbers were internally consistent, reproduced from the
artefact, and wrong.

No existing check looks at WHICH CACHE a number came from, so this one does. The rule:

  a script that reads more than one detection cache must read caches that are all corrected or all
  raw, unless it is on the exemption list below and says why.

The footing is decided by directory name, because that is what the pipeline itself uses:
`_cache_undist` and anything ending `_undist` are corrected; every other `_cache_*` is raw.
"""
import glob
import io
import os
import re
import sys

ROOT = "D:/ROWV_paper"

# Scripts that legitimately hold both footings at once, with the reason. A script may only be
# exempt because the distortion difference IS its subject, or because it converts one to the other.
EXEMPT = {
    "biocv_make_undist_cache.py": "converts raw to corrected; holding both is its job",
    "biocv_undistort_test.py": "the distortion difference is the measurement (Table S2b)",
    "biocv_controls.py": "runs the same analysis on both footings as a control (Table S2a-b)",
    "biocv_detect_rtmo.py": "reads a raw cache for frame indices and writes a raw cache",
    "biocv_detect_halpe.py": "reads a raw cache for frame indices and writes a raw cache",
    "biocv_halpe_gt.py": "merges reference markers into a raw cache; reads no second cache",
    "measure_checkers.py": "holds the mixed-footing defect as an injection case",
    "check_caches.py": "this file names both footings in order to check them",
}

CACHE = re.compile(r"D:/BioCV/(_cache_[A-Za-z0-9_]+)")


def corrected(name):
    return name.endswith("_undist")


def main():
    problems = []
    checked = 0
    for path in sorted(glob.glob(f"{ROOT}/*.py")):
        base = os.path.basename(path)
        if base.startswith("_SUPERSEDED_"):
            continue
        src = io.open(path, encoding="utf-8", errors="replace").read()
        # Only lines that are code, so a docstring naming a cache does not raise a false alarm.
        code = "\n".join(l for l in src.split("\n")
                         if not l.lstrip().startswith("#"))
        body = code.split('"""')
        code = "".join(body[0::2]) if len(body) > 1 else code
        names = sorted(set(CACHE.findall(code)))
        if len(names) < 2:
            continue
        checked += 1
        footings = {corrected(n) for n in names}
        if len(footings) == 1:
            continue
        if base in EXEMPT:
            continue
        problems.append((base, names))

    print(f"{checked} script(s) read more than one detection cache")
    print("")
    print("exempt, with the reason each is allowed to hold both footings:")
    for k, v in sorted(EXEMPT.items()):
        if os.path.exists(os.path.join(ROOT, k)):
            print(f"    {k:<32} {v}")
    print("")
    if not problems:
        print("no analysis compares a distortion-corrected cache with a raw one")
        return 0
    print(f"{len(problems)} script(s) mix corrected and raw detections:")
    for base, names in problems:
        print(f"    {base}")
        for n in names:
            print(f"        {n}   ({'corrected' if corrected(n) else 'RAW'})")
    print("")
    print("Run the raw one through biocv_make_undist_cache.py with BIOCV_UNDIST_SRC/DST and")
    print("re-point the analysis, or add the script to EXEMPT with the reason it is allowed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
