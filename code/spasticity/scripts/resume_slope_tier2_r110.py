"""Resume the Tier-2 slope launch if its supervisor dies, WITHOUT relaunching what already ran.

WHY THIS FILE EXISTS, BEFORE IT IS NEEDED. `resume_slope_r64.py` was written AFTER the Tier-1
supervisor died with `sconecmd` children still running -- the study would have stalled at 16 of 114
with `LAUNCH_STATUS.json` frozen and still reading "running". That hazard has already fired once on
this machine. It is not covered for Tier 2: `resume_slope_r64.py` iterates `tier1_queue()` over seeds
101-106 and knows nothing about seeds 107-116.

The exposure is larger than Tier 1's was. At the time of writing, the Tier-2 queue exists ONLY inside
the memory of one live supervisor process tree (a `nohup` shim, its python child, and that child's uv
python child), and the two live `sconecmd` runs are children of that uv python -- a FIVE-process
tree, so a tree-kill costs the in-flight cells as well as the queue. What is lost with the supervisor
is the ORDER of the remaining launches, not the queue itself: this script reconstructs the queue from
disk and never reads `LAUNCH_STATUS.json`. What nothing in the corpus would reveal is the STOP:
`history.txt` cannot see a run that has not started, so a killed supervisor looks exactly like a
finished study until the completeness gate refuses.

WHY NOT JUST RERUN `--launch`. `build_tier2()` writes all 120 scenarios and `G60.launch()` has no
skip logic, so rerunning it would relaunch every finished cell. SCONE does not overwrite a result
directory -- it appends " (1)" -- so that would manufacture a duplicate for every completed tag,
which is the hazard gate G5 exists to catch BEFORE launch, and would break the content-based
resolution the corpus depends on.

WHAT IS PRESERVED, AND THE ONE DEVIATION. `_popen`, the concurrency cap, the grade list, the cell
list and the seed list are IMPORTED from `gen_slope_tier2_r87` / `gen_slope_r60`, never restated.

The one deviation, stated because it is a deviation: this script does NOT call `build_tier2()` to
obtain the queue, because `build_tier2()` WRITES 120 scenario files as a side effect. Calling a
producing script merely to read its output is exactly the defect this project registered when an
auditor re-ran an analysis script and silently rewrote a deposited artifact that carried no hash. The
queue is therefore composed from the same imported constants, and `verify_queue()` proves the
composition equivalent to the registered one by comparing it against the `.scone` files that
`build_tier2()` actually wrote. If they differ, this script refuses to run.

THE SKIP RULE. A tag is skipped iff a result directory for it already exists under the results root.
That covers completed runs and runs still in flight -- the latter are alive and will finish, so
relaunching them is precisely what must not happen. It does NOT detect a run that died part-way: such
a tag is skipped while incomplete, so the gap is REPORTED here and must be caught by the analysis
script's own completeness gate, which refuses a partial corpus by design.

CONCURRENCY. The cap is enforced against the live `sconecmd` count on the WHOLE MACHINE, not against
this script's own children. Two consequences, both intended: any orphans left by a dead supervisor are
counted, so nothing is over-subscribed while they drain; and if the USER's own study is running, this
script yields to it rather than competing. The standing rule is that the cell which gives way is ours.

DO NOT PASS --launch WHILE THE ORIGINAL SUPERVISOR IS ALIVE. Two supervisors sharing one queue is a
duplicate-launch hazard: both can pass the skip check for the same tag in the window before either
child creates its directory, and the duplicate directory is unrecoverable. The DRY RUN is safe at any
time -- it is the default, `launch = "--launch" in sys.argv` gates every launch path, and main()
returns before `_popen` when the flag is absent. (An earlier version of this paragraph said DO NOT RUN
THIS, which forbade the dry run too and contradicted the callers that recommend it.)

Before passing --launch, check with a command that shows a COMMAND LINE -- `tasklist` alone shows
image name, PID and memory only, and cannot tell one python from another:

    Get-CimInstance Win32_Process -Filter "(Name='python.exe' OR Name='nohup.exe' OR Name='sconecmd.exe') AND CommandLine LIKE '%slope%'" | Select-Object ProcessId,ParentProcessId,Name | Format-Table -AutoSize

(Typed at a PowerShell prompt. One line: a wrapped line parses as two commands. No `$_`: bash would
expand it. Filters on name AND command line: command line alone also matches the shell you type it
in. An earlier version of this docstring printed a command that executed in no shell at all.)

Nothing under the results root is written, renamed or deleted. Nothing is killed. Nothing is launched
unless --launch is passed; --dry-run is the default.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_slope_r60 as G60
import gen_slope_tier2_r87 as T2

RES = r"C:\Users\maurice\Documents\SCONE\results"
STATUS = os.path.join(G60.OPTDIR, "RESUME_TIER2_STATUS.json")


def tier2_queue():
    """The 120 Tier-2 tags, composed from the IMPORTED constants -- not from build_tier2(), which
    writes files. Order matches build_tier2(): grade outer, cell middle, seed inner."""
    out = []
    for grade in G60.GRADES:
        for cond, _weak, _kv, _n, _role in T2.TIER2_CONDS:
            tag = G60.tag_of(grade, cond)
            for seed in T2.TIER2_SEEDS:
                out.append("%s_s%d" % (tag, seed))
    return out


def verify_queue(queue):
    """Prove the composed queue equals the registered one, by comparing against the .scone files
    build_tier2() wrote. A second implementation of a registered procedure must be checked against
    the first, not trusted because it looks the same."""
    on_disk = set()
    for f in os.listdir(G60.OPTDIR):
        if f.endswith(".scone"):
            stem = f[:-6]
            if "_s" in stem and stem.rsplit("_s", 1)[-1].isdigit():
                if int(stem.rsplit("_s", 1)[-1]) in T2.TIER2_SEEDS:
                    on_disk.add(stem)
    q = set(queue)
    if q != on_disk:
        print("QUEUE MISMATCH -- refusing to proceed.")
        print("  composed but not on disk : %s" % sorted(q - on_disk)[:8])
        print("  on disk but not composed : %s" % sorted(on_disk - q)[:8])
        return False
    print("queue verified against %d scenario files on disk: identical" % len(on_disk))
    return True


def existing_tags():
    """Tags with a result directory. Read from the filesystem, never from a status file."""
    out = set()
    for d in os.listdir(RES):
        if os.path.isdir(os.path.join(RES, d)) and "." in d:
            out.add(d.split(".")[0])
    return out


def live_sconecmd():
    """Count via tasklist. `ps aux | grep` is banned here and would be wrong on Windows."""
    try:
        p = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, timeout=60)
        txt = p.stdout.decode("utf8", "replace")
    except Exception as e:
        print("tasklist failed (%s) -- refusing to launch blind" % e)
        return 10 ** 6                      # fail CLOSED: an unknown count must never permit a launch
    return sum(1 for ln in txt.splitlines() if "sconecmd" in ln.lower())


def main():
    launch = "--launch" in sys.argv
    queue = tier2_queue()
    if not verify_queue(queue):
        return 3

    have = existing_tags()
    todo = [t for t in queue if t not in have]
    skipped = [t for t in queue if t in have]

    print()
    print("registered Tier-2 queue      : %d" % len(queue))
    print("already have a result dir    : %d  (completed or in flight -- NOT relaunched)" % len(skipped))
    print("to launch                    : %d" % len(todo))
    print("live sconecmd on the machine : %d   (cap %d)" % (live_sconecmd(), G60.MAX_CONCURRENT))
    print()

    if not launch:
        print("DRY RUN -- nothing launched. Pass --launch to start, and ONLY after confirming that")
        print("no `gen_slope_tier2_r87.py --launch` supervisor is alive (see this file's docstring).")
        return 0

    started = []
    while todo:
        n = live_sconecmd()
        if n >= G60.MAX_CONCURRENT:
            time.sleep(30)
            continue
        t = todo.pop(0)
        # Re-check immediately before launching: the directory may have appeared since the scan,
        # and a duplicate tag is unrecoverable once SCONE has written " (1)".
        if t in existing_tags():
            print("skip (appeared since scan) %s" % t)
            continue
        pr, _lg = G60._popen(t)
        started.append(t)
        print("launched %-26s pid=%-7d  (%d left)" % (t, pr.pid, len(todo)))
        with open(STATUS, "w", encoding="utf-8") as f:
            f.write('{"phase":"resuming","label":"TIER2","started":%d,"remaining":%d,"skipped":%d,"utc":"%s"}'
                    % (len(started), len(todo), len(skipped),
                       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
        time.sleep(30)                      # let the child register before the next count

    print("all launched; %d started this session" % len(started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
