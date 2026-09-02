# -*- coding: utf-8 -*-
"""backup_integrity_r145.py -- the checks `backup_index.py --check` cannot make.

WHY THIS EXISTS
---------------
Round 144 overwrote a retained pre-image (`cp -p` onto an existing `.bak_rNN_` name).
`backup_index.py --check` PASSED, and not by oversight: its pass condition is

    "no backup is meaningfully newer than its live file WHILE DIFFERING FROM IT"

and an overwrite BY the live file makes the backup IDENTICAL to live, which the
condition reads as fine. The failure's signature and the protection's success
criterion are the same bytes.

DEFECT HISTORY OF THIS FILE -- all three found in the ALARM PATH, which only runs
when something is actually wrong, and which every clean run leaves unexercised:

  r148  C3 wrote a manifest and nothing ever compared one to the next: a recorder
        standing in for a detector. C4 added.
  r149  (1) the alarm branch printed a non-ASCII character and died with
            UnicodeEncodeError on a cp950 console -- the tool CRASHED at the moment
            it detected.
        (2) C3 re-baselined unconditionally in the same run that reported the
            overwrite, so the alarm CLEARED ITSELF: one run to see it, gone the next.
        (3) the end state was therefore order-dependent luck -- C3 happening to run
            before the crash is what left the manifest consistent.

  Fixes: ASCII-only alarm path plus a stdout reconfigure; C3 preserves the PRIOR
  baseline for anything C4 flagged, so an overwrite persists until a human retires
  it with --retire; exit status carries C4 alone.

CHECKS
------
C1  IDENTICAL-TO-LIVE   warn only; legitimate when no edit followed the backup.
C2  MTIME MONOTONICITY  heuristic; known false positives from legitimate `cp -p`.
C3  MANIFEST            digests every pre-image; NEVER re-baselines a flagged one.
C4  IMMUTABILITY        a retained pre-image must never change. Hard invariant.

WHAT NOTHING HERE CAN DO: detect an overwrite that happened BEFORE the first
manifest was cut, or a `cp` without -p onto content similar to the original.
"""
import io, os, re, sys, glob, json, hashlib, time

try:                                   # pattern-artifact #341: a cp950 console
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                      # noqa: BLE001 -- old interpreters
    pass

ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"
MANIFEST = os.path.join(ROOT, "paper", "BACKUP_MANIFEST_r145.json")
PAT = re.compile(r"^\.bak_r(\d+)_(.+)$")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def scan():
    out = {}
    for d in (ROOT, os.path.join(ROOT, "paper")):
        for p in glob.glob(os.path.join(d, ".bak_r*")):
            m = PAT.match(os.path.basename(p))
            if not m:
                continue
            out.setdefault((d, m.group(2)), []).append((int(m.group(1)), p))
    for k in out:
        out[k].sort()
    return out


def load_prior():
    if not os.path.exists(MANIFEST):
        return None, {}
    try:
        d = json.load(io.open(MANIFEST, encoding="utf-8"))
        return d.get("entries", {}), d.get("flagged", {})
    except Exception as e:                                   # noqa: BLE001
        print("C4  PRIOR MANIFEST UNREADABLE (%s) -- comparison UNEVALUABLE"
              % e.__class__.__name__)
        return None, {}


def main(argv):
    retire = [a.split("=", 1)[1] for a in argv if a.startswith("--retire=")]
    retire_all = "--retire-all" in argv

    groups = scan()
    tot = sum(len(v) for v in groups.values())
    print("=" * 78)
    print("BACKUP INTEGRITY -- %d pre-images across %d live files" % (tot, len(groups)))
    print("=" * 78)

    prior, prior_flagged = load_prior()
    c1, c2, current = [], [], {}

    for (d, live), lst in sorted(groups.items(), key=lambda kv: kv[0][1]):
        livep = os.path.join(d, live)
        lh = sha(livep) if os.path.exists(livep) else None
        prev_t, prev_n = None, None
        for n, p in lst:
            st = os.stat(p)
            h = sha(p)
            current[os.path.relpath(p, ROOT)] = {"bytes": st.st_size, "sha256": h,
                                                 "mtime": st.st_mtime}
            if lh is not None and h == lh:
                c1.append((os.path.relpath(p, ROOT), st.st_size))
            if prev_t is not None and st.st_mtime < prev_t - 2:
                c2.append((os.path.relpath(p, ROOT), prev_n, n,
                           time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
                           time.strftime("%Y-%m-%d %H:%M", time.localtime(prev_t))))
            prev_t, prev_n = st.st_mtime, n

    print()
    print("C1  IDENTICAL-TO-LIVE  (warn only -- a backup with no edit after it is legitimate)")
    print("    %s" % ("none" if not c1 else ""))
    for r, s in c1:
        print("    %-64s %d B" % (r, s))

    print()
    print("C2  MTIME OUT OF ORDER  (heuristic; legitimate `cp -p` backups land here)")
    print("    %s" % ("none" if not c2 else ""))
    for r, pn, n, t, pt in c2:
        print("    %-52s r%s @ %s is OLDER than r%s @ %s" % (r, n, t, pn, pt))

    # ---------------- C4: the hard invariant -------------------------------
    flagged = dict(prior_flagged)          # persists across runs by design
    vanished, added = [], []
    if prior is not None:
        for k, v in prior.items():
            now = current.get(k)
            if now is None:
                vanished.append(k)
            elif now["sha256"] != v["sha256"]:
                flagged[k] = {"baseline_sha256": v["sha256"], "baseline_bytes": v["bytes"],
                              "observed_sha256": now["sha256"], "observed_bytes": now["bytes"],
                              "first_seen": flagged.get(k, {}).get(
                                  "first_seen", time.strftime("%Y-%m-%dT%H:%M:%S"))}
        added = sorted(set(current) - set(prior))

    # retirement is an explicit human act
    retired = []
    for k in list(flagged):
        if retire_all or k in retire or k.replace("\\", "/") in [r.replace("\\", "/") for r in retire]:
            del flagged[k]
            retired.append(k)

    # re-verify anything still flagged against the CURRENT file
    still = {}
    for k, f in flagged.items():
        now = current.get(k)
        if now is None:
            still[k] = f
        elif now["sha256"] == f["baseline_sha256"]:
            retired.append(k + "  (self-healed: content restored to baseline)")
        else:
            f["observed_sha256"] = now["sha256"]
            f["observed_bytes"] = now["bytes"]
            still[k] = f
    flagged = still

    print()
    print("C4  IMMUTABILITY  (a retained pre-image must never change)  -- ASCII alarm path")
    if prior is None:
        print("    no prior manifest -- first run, nothing to compare")
    elif not flagged:
        print("    OK: none of %d previously recorded pre-images differs from its baseline"
              % len(prior))
    for k, f in sorted(flagged.items()):
        print("    *** OVERWRITTEN ***  %s" % k)
        print("        baseline %s (%d B)" % (f["baseline_sha256"][:16], f["baseline_bytes"]))
        print("        observed %s (%d B)" % (f["observed_sha256"][:16], f["observed_bytes"]))
        print("        first seen %s -- PERSISTS until retired with --retire=<path>"
              % f["first_seen"])
    for k in retired:
        print("    retired: %s" % k)
    if vanished:
        print("    GONE (renamed or deleted):")
        for k in vanished:
            print("      %s" % k)
    if added:
        print("    new since last run: %d" % len(added))

    # ---------------- C3: write, but NEVER re-baseline a flagged entry -----
    entries = dict(current)
    kept = 0
    for k, f in flagged.items():
        if k in entries:
            entries[k] = {"bytes": f["baseline_bytes"], "sha256": f["baseline_sha256"],
                          "mtime": (prior or {}).get(k, {}).get("mtime", 0)}
            kept += 1

    json.dump({"what": "digests of every retained pre-image",
               "scope": ("attests these pre-images have not changed SINCE the run that wrote "
                         "this file; attests NOTHING about their state before, and cannot "
                         "recover the pre-image destroyed in round 144"),
               "note": ("entries listed in `flagged` retain their ORIGINAL baseline digest, "
                        "not the observed one -- an overwrite must not clear itself"),
               "count": len(entries), "flagged": flagged, "entries": entries},
              io.open(MANIFEST, "w", encoding="utf-8"), indent=1, sort_keys=True)

    print()
    print("C3  MANIFEST  wrote %s (%d entries, %d flagged baselines preserved)"
          % (os.path.relpath(MANIFEST, ROOT), len(entries), kept))

    print()
    print("=" * 78)
    print("WHAT THIS CANNOT SEE -- stated rather than implied")
    print("=" * 78)
    print("  * any overwrite that happened BEFORE this manifest was cut")
    print("  * an overwrite by `cp` WITHOUT -p onto content similar to the original")
    print("  * anything about pre-images whose live counterpart no longer exists")
    print("  * C1 and C2 are heuristics over content and mtime, not proof")
    print()
    print("EXIT STATUS carries C4 only (hard invariant: a pre-image is immutable).")
    print("  C1 warnings   : %d" % len(c1))
    print("  C2 warnings   : %d  -- heuristic, known false positives, does NOT fail the run"
          % len(c2))
    print("  C4 overwrites : %d" % len(flagged))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
