"""Resume the Tier-1 slope launch after the supervisor died, WITHOUT relaunching what already ran.

WHY THIS FILE EXISTS. The supervisor (pid 4908) that `gen_slope_r60.py --tier1` started is gone --
no python process on the box at 02:23 -- while two `sconecmd` children were still running. Those two
finish on their own; nothing else would ever start. The study would have stalled at 16 of 114 with
`LAUNCH_STATUS.json` frozen at 02:10:47 still saying "running", which is the same class as any other
status line that describes a process nobody checked.

WHY NOT JUST RERUN `--tier1`. `tier1_queue()` builds all 114 tags unconditionally and `launch()` has
no skip logic. Rerunning it would relaunch every finished cell, and SCONE does not overwrite a result
directory -- it appends `" (1)"`. That would manufacture a duplicate for every completed tag, which is
precisely the hazard gate G5 is written to catch BEFORE launch, and it would break the content-based
resolution the whole corpus depends on. Restarting the registered launcher would have destroyed the
registered corpus.

WHAT IS PRESERVED. The queue, its order, the scenario files, the budget and the concurrency limit are
imported from `gen_slope_r60` rather than restated. A resumed run that re-implements the launch rule
is a second implementation of a registered procedure, and this project has already paid for one of
those. Nothing here decides anything the registration decides.

THE SKIP RULE. A tag is skipped iff a result directory for it already exists under the results root.
That covers both completed runs and the two still in flight -- the latter are alive and will finish,
so relaunching them is exactly what must not happen. It does NOT attempt to detect a run that died
part-way: such a tag would be skipped while incomplete, so the gap is REPORTED here and must be
caught by the analysis script's own completeness gate, which refuses a partial corpus by design.

CONCURRENCY. The cap is enforced against the live `sconecmd` count on the whole machine, not against
this script's own children. Two consequences, both intended: the two orphans left by the dead
supervisor are counted, so nothing is over-subscribed while they drain; and if the USER's own study
starts running, this script yields to it rather than competing -- the standing rule is that the cell
that gives way is ours.

Nothing under the results root is written, renamed or deleted. Nothing is killed.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_slope_r60 as G

RES = r"C:\Users\maurice\Documents\SCONE\results"
STATUS = os.path.join(G.OPTDIR, "RESUME_STATUS.json")


def existing_tags():
    """Tags that already have a result directory. Read from the filesystem, never from a status file."""
    out = set()
    try:
        for d in os.listdir(RES):
            if os.path.isdir(os.path.join(RES, d)) and "." in d:
                out.add(d.split(".")[0])
    except OSError as e:
        print("cannot read results root: %s" % e)
        raise
    return out


def live_sconecmd():
    """Count via tasklist. `ps aux | grep` is banned in this project and would be wrong on Windows."""
    try:
        p = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, timeout=60)
        txt = p.stdout.decode("utf8", "replace")
    except Exception as e:
        print("tasklist failed (%s) -- refusing to launch blind" % e)
        return 10 ** 6                      # fail CLOSED: an unknown count must never permit a launch
    return sum(1 for ln in txt.splitlines() if "sconecmd" in ln.lower())


def main():
    queue = [t for _grade, t in G.tier1_queue()]
    have = existing_tags()
    todo = [t for t in queue if t not in have]
    skipped = [t for t in queue if t in have]

    print("registered Tier-1 queue      : %d" % len(queue))
    print("already have a result dir    : %d  (completed or in flight -- NOT relaunched)" % len(skipped))
    print("to launch                    : %d" % len(todo))
    print("cap                          : %d live sconecmd on the machine" % G.MAX_CONCURRENT)
    if not todo:
        print("nothing to do")
        return 0

    started = []
    while todo:
        n = live_sconecmd()
        if n >= G.MAX_CONCURRENT:
            time.sleep(30)
            continue
        t = todo.pop(0)
        # Re-check immediately before launching: the directory may have appeared since the scan,
        # and a duplicate tag is unrecoverable once SCONE has written " (1)".
        if t in existing_tags():
            print("skip (appeared since scan) %s" % t)
            continue
        pr, _lg = G._popen(t)
        started.append(t)
        print("launched %-24s pid=%-7d  (%d left)" % (t, pr.pid, len(todo)))
        with open(STATUS, "w", encoding="utf-8") as f:
            f.write('{"phase":"resuming","started":%d,"remaining":%d,"skipped":%d,"utc":"%s"}'
                    % (len(started), len(todo), len(skipped),
                       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
        time.sleep(30)                      # let the child register before the next count

    print("all launched; %d started this session" % len(started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
