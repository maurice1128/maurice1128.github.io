"""Freeze the evidence base: one manifest, hashed, with its counting rules stated.

WHY THIS EXISTS.
The defect catalogue quotes five mutually inconsistent directory counts -- 243, 315, 327,
"147 of 315" and "233 of 327" -- for one archive, and 7 of 15 `file:line` citations no longer
resolve. Part of that spread is real mutation (the corpus grew while it was being audited) and
part is definitional: nobody wrote down whether protected directories were included, or whether
nested directories were counted. Two auditors following reasonable rules got different numbers
in the same hour.

A bare count is not evidence. This writes the count WITH its rule, and a hash for every file a
published claim may cite, so any number can be re-derived or shown to have moved.

PROTECTED. Directories belonging to the user's own separate study are inventoried but never
read into, modified, or counted as ours. They are listed so their exclusion is auditable.
"""
import hashlib
import json
import os
import re
import sys
import time

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PROJECT = r"C:\Users\maurice\Desktop\spasticity_paper"

# The user's own study. Never touched; excluded from every count that says "ours".
#
# THIS LIST WAS WRONG ON ITS FIRST RUN AND THE ERROR IS INSTRUCTIVE. It was an enumeration of
# the eight tags that happened to have been named in conversation -- KF60L, KE40L, HF60L, DF20L,
# PF20L, s1KF60L, s2KE40L, s2DF20L. The actual study is a full grid: {KF,KE,HF,DF,PF} x {20,40,60}
# x {bare, s1..s4} = 75 tags across 112 result directories. Sixty-seven of the user's own tags
# were therefore counted as ours.
#
# Nothing was damaged -- this module only reads -- but the shape of the mistake is the one that
# destroys data: a protection list built by ENUMERATING WHAT WAS MENTIONED rather than by
# describing the family. `replay_cache.py` reached the same conclusion the hard way and switched
# from a blacklist to a whitelist of THIS project's tags, which is strictly safer because it
# cannot be defeated by a name nobody thought of. This module cannot use that form (it must
# classify every directory, including ones neither party has named), so it matches the user's
# family by PATTERN and treats anything unrecognised as theirs is NOT assumed -- see below.
PROTECTED_PREFIX = ("opt_s1", "opt_s2", "opt_s3", "opt_s4")
# {joint}{severity}L with an optional subject prefix -- the user's grid, described not enumerated.
PROTECTED_PAT = re.compile(r"^(s\d+)?(KF|KE|HF|DF|PF)\d+L(\.|$)", re.I)

# Files a published claim may cite. Hashed. Everything else is counted, not hashed --
# hashing 600k .par files would take hours and no claim rests on an individual .par's bytes.
HASH_EXT = (".py", ".scone", ".md", ".json")

GEN = re.compile(r"^(\d+)_")


def protected(name):
    return (any(name.startswith(p) for p in PROTECTED_PREFIX)
            or bool(PROTECTED_PAT.match(name)))


def sha256(path, cap=64 * 1024 * 1024):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h.update(b)
                if f.tell() > cap:
                    return "OVERSIZE:%d" % f.tell()
    except OSError as e:
        return "UNREADABLE:%s" % e.__class__.__name__
    return h.hexdigest()


def census():
    """Top-level result directories only. The rule is stated in the output, not assumed."""
    out = {"rule": "top-level directories directly under RESULTS; nested dirs NOT counted",
           "results_root": RESULTS,
           "protected_prefixes": list(PROTECTED_PREFIX),
           "protected_pattern": PROTECTED_PAT.pattern,
           "protected": [], "ours": []}
    if not os.path.isdir(RESULTS):
        out["error"] = "results root missing"
        return out
    for name in sorted(os.listdir(RESULTS)):
        p = os.path.join(RESULTS, name)
        if not os.path.isdir(p):
            continue
        if protected(name):
            out["protected"].append(name)
            continue
        try:
            files = os.listdir(p)
        except OSError:
            out["ours"].append({"dir": name, "error": "unlistable"})
            continue
        stos = sorted(f for f in files if f.endswith(".sto"))
        pars = sorted(f for f in files if f.endswith(".par"))

        def gen_of(fn):
            m = GEN.match(fn)
            return int(m.group(1)) if m else -1

        rec = {"dir": name, "n_sto": len(stos), "n_par": len(pars),
               "max_par_gen": max([gen_of(f) for f in pars], default=None),
               "sto": stos}
        # The B2 ambiguity: >1 .sto means "which controller was analysed" has no single answer.
        rec["ambiguous_sto"] = len(stos) > 1
        # An empty launcher log cannot establish absence of a discard warning (see check_unused).
        logs = [f for f in files if f == "optimization.log"]
        if logs:
            rec["optimization_log_bytes"] = os.path.getsize(os.path.join(p, logs[0]))
        out["ours"].append(rec)
    return out


def code_hashes():
    out = []
    for root, dirs, files in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if not f.endswith(HASH_EXT):
                continue
            fp = os.path.join(root, f)
            try:
                st = os.stat(fp)
            except OSError:
                continue
            out.append({"path": os.path.relpath(fp, PROJECT).replace("\\", "/"),
                        "bytes": st.st_size,
                        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                        "sha256": sha256(fp)})
    return sorted(out, key=lambda r: r["path"])


def main():
    c = census()
    ours = [r for r in c["ours"] if "error" not in r]
    summary = {
        "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "counting_rule": c.get("rule"),
        "result_dirs_total": len(c["ours"]) + len(c["protected"]),
        "result_dirs_protected": len(c["protected"]),
        "result_dirs_ours": len(c["ours"]),
        "ours_with_sto": sum(1 for r in ours if r["n_sto"] >= 1),
        "ours_without_sto": sum(1 for r in ours if r["n_sto"] == 0),
        "ours_ambiguous_sto": sum(1 for r in ours if r["ambiguous_sto"]),
        "ours_empty_optimization_log": sum(
            1 for r in ours if r.get("optimization_log_bytes") == 0),
    }
    manifest = {"summary": summary, "census": c, "code": code_hashes()}
    out = os.path.join(PROJECT, "paper", "FROZEN_MANIFEST.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)

    # ------------------------------------------------------------------ round 43
    # THE SIDECAR IS WRITTEN HERE, BY THIS SCRIPT, IN THE SAME BREATH AS THE MANIFEST.
    # Round 38 ruled that "a manifest whose purpose is freezing evidence must itself be hashed or
    # it drifts silently", and the rule was then implemented by hand-writing a .sha256 file once.
    # This script rewrote FROZEN_MANIFEST.json at round 40 and again at round 43 and NEVER TOUCHED
    # THE SIDECAR: on 2026-08-02 22:51 the manifest hashed to 2bd2c8f5... while the sidecar beside
    # it still certified c065d3b9..., the round-38 content, two freezes stale.
    #
    # A stale hash sidecar is strictly worse than no sidecar. No sidecar means "unverified"; a
    # stale one affirmatively certifies content that is not there, and a reader checking the hash
    # gets a MISMATCH they must then diagnose -- or, if they only read the number and cite it,
    # publishes a pin to a file that no longer exists. Same shape as a vacuously passing gate.
    #
    # Written last and read back, so the sidecar can never describe a manifest that was not the
    # one just written.
    digest = sha256(out)
    side = os.path.splitext(out)[0] + ".sha256"
    with open(side, "w", encoding="utf-8") as f:
        f.write("%s  %s\n" % (digest, os.path.basename(out)))
    check = sha256(out)
    if check != digest:
        raise SystemExit("FREEZE ABORTED: manifest changed while its sidecar was written "
                         "(%s -> %s). Nothing here may be cited." % (digest, check))

    for k, v in summary.items():
        print("%-32s %s" % (k, v))
    print("\nambiguous-.sto directories (the complete B2 population):")
    for r in ours:
        if r["ambiguous_sto"]:
            print("  %-52s %d .sto  max_par_gen=%s" % (r["dir"], r["n_sto"], r["max_par_gen"]))
    print("\ncode files hashed: %d" % len(manifest["code"]))
    print("written: %s" % out)
    print("sha256:  %s" % digest)
    print("sidecar: %s" % side)
    return 0


if __name__ == "__main__":
    sys.exit(main())
