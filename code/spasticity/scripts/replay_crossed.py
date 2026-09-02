"""Replay the crossed lesion x budget cells at their best parameter set, into isolated directories.

WHY A SEPARATE SCRIPT FROM `replay_rest.py`. Two things differ, and both are traps.

TRAP 1 -- THE NAMESPACE COLLISION. SCONE does not overwrite a result directory; it appends
`" (1)"`. Seven of the twelve crossed conditions share a tag with an archive run, so a prefix glob
returns BOTH, and resolving by mtime is defect #23 verbatim. Worse, the obvious discriminator
fails on the two conditions that matter most: `CMW70`/`CMW80`'s archive copies were themselves run
at `max_generations = 90` and ALSO terminate at generation 89. Had this gone uncaught those two
cells would each have carried n = 6 -- four crossed seeds plus two archive runs at
`min_progress = 1e-7` -- REINTRODUCING THE BUDGET CONFOUND IN THE ARM ADDED TO REMOVE IT, in
precisely the two conditions whose purpose was to hold the primary contrast above alpha. So the
directory is identified by all three of its own artifacts, never by name, mtime or position:

    min_progress == 0   AND   max_generations == 90   AND   terminal generation == 89

TRAP 2 -- "BEST" IS NOT "DEEPEST" HERE, AND THAT IS BY DESIGN. `replay_rest.py` selects the
minimum-fitness `.par` and ASSERTS it is also the maximum-generation `.par`, refusing to guess
when they disagree. That assertion is correct for runs that stopped on their own convergence
criterion: best-and-deepest disagreeing means the run was still improving when it was cut, so
"converged best" is undefined. Under a UNIFORM HARD CAP the situation inverts. Every run stops at
89 whether or not it has converged, so best and deepest routinely differ -- and that difference
carries no confound, because the cap is identical across every cell. Applying the old assertion
here would reject most of the experiment for exhibiting exactly the property the design intends.

The rule is therefore relaxed FOR THIS STUDY ONLY, and the relaxation is recorded rather than
assumed: both generations are written into every `PROVENANCE.json`, so a reader can see how far
each run's optimum sat from its cap, and a systematic difference BETWEEN ARMS -- which would be a
real confound -- is visible instead of hidden. Flagged for ratification: this is a selection-rule
change made by the executor, and it must be signed off or replaced.

Nothing under RESULTS is written or deleted. Runs still being written are skipped, not waited on
(#172: two writers in one tree manufactured both a false failure and a false success in one night).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "replay_crossed")

PAR_RE = re.compile(r"^(\d+)_([0-9.]+)_([0-9.]+)\.par$")
REGISTERED = {"min_progress": "0", "max_generations": "90"}
TERMINAL_GEN = 89

TAGS = ["HEALTHY", "DR2K000",
        "PAR20", "PAR40", "PAR60", "CMW70", "CMW80",
        "DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
SEEDS = 4


def prop(txt, key):
    m = re.search(r"^[ \t]*%s[ \t]*=[ \t]*(\S+)[ \t]*$" % key, txt, re.M)
    return m.group(1) if m else None


def parse_pars(d):
    out = []
    for p in glob.glob(os.path.join(d, "*.par")):
        m = PAR_RE.match(os.path.basename(p))
        if m:
            out.append((int(m.group(1)), float(m.group(3)), p))
    return out


def is_crossed(d):
    """All three artifacts, read from the run's own files. Name and mtime are never consulted."""
    cfg = os.path.join(d, "config.scone")
    if not os.path.exists(cfg):
        return False, "no config.scone"
    txt = open(cfg, encoding="utf-8", errors="ignore").read()
    for k, want in REGISTERED.items():
        got = prop(txt, k)
        if got != want:
            return False, "%s = %r (registered %r)" % (k, got, want)
    pars = parse_pars(d)
    if not pars:
        return False, "no .par"
    # TERMINAL GENERATION COMES FROM `history.txt`, NOT FROM `.par` FILENAMES.
    # SCONE writes a `.par` only on IMPROVEMENT, so the highest `.par` generation is the last
    # generation that improved -- not the last generation that RAN. `CMW70_s2` reached 89 with
    # its final improvement at 72; testing the `.par` maximum rejected it, and 42 of 48 cells
    # with it. `history.txt` has exactly one row per generation, indexed from 0, so the terminal
    # index is (rows - 1) after the header.
    #
    # This project established the same thing at round 39 -- ".par files are pruned, E4 must read
    # history.txt" -- and I wrote the pruned quantity into the rule anyway. A known defect
    # repeated in a new file is the cheapest kind to prevent and the easiest to miss: the
    # catalogue is only protective where someone remembers to consult it.
    hist = os.path.join(d, "history.txt")
    if not os.path.exists(hist):
        return False, "no history.txt -- terminal generation cannot be established"
    with open(hist, encoding="utf-8", errors="ignore") as f:
        rows = sum(1 for ln in f if ln.strip())
    term = rows - 2                      # minus header, minus 1 for 0-indexing
    if term != TERMINAL_GEN:
        return False, "terminal generation %d (registered %d)" % (term, TERMINAL_GEN)
    return True, "ok"


def resolve(tag):
    """(dir, note). Raises if the three-part rule leaves anything other than exactly one."""
    cands = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    hits, why = [], []
    for d in cands:
        ok, note = is_crossed(d)
        (hits if ok else why).append((d, note))
    if len(hits) == 1:
        return hits[0][0], "1 of %d candidates" % len(cands)
    if not hits:
        raise ValueError("%s: no candidate satisfies the crossed rule; rejected -> %s"
                         % (tag, "; ".join("%s: %s" % (os.path.basename(d), n) for d, n in why)))
    raise ValueError("%s: %d candidates satisfy the crossed rule -- ambiguous, refusing to guess"
                     % (tag, len(hits)))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def replay(tag):
    try:
        run_dir, note = resolve(tag)
    except ValueError as e:
        return {"tag": tag, "status": "UNRESOLVED", "detail": str(e)}

    # Skip anything still being written. Do not wait: a writer in the tree is what manufactured
    # both a false failure and a false success on 2026-08-02.
    newest = max((os.path.getmtime(p) for p in glob.glob(os.path.join(run_dir, "*.par"))),
                 default=0)
    if time.time() - newest < 120:
        return {"tag": tag, "status": "LIVE", "detail": "a .par was written %.0fs ago"
                % (time.time() - newest)}

    pars = parse_pars(run_dir)
    best = min(pars, key=lambda t: t[1])
    max_gen = max(t[0] for t in pars)
    ties = [t for t in pars if abs(t[1] - best[1]) < 1e-12]
    if len(ties) > 1:
        return {"tag": tag, "status": "TIE",
                "detail": "fitness %.6f at generations %s" % (best[1], sorted(t[0] for t in ties))}

    work = os.path.join(DEST, tag)
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    aux = (glob.glob(os.path.join(run_dir, "*.osim")) + glob.glob(os.path.join(run_dir, "*.zml"))
           + glob.glob(os.path.join(run_dir, "config.scone"))
           + [p for p in glob.glob(os.path.join(run_dir, "*.par"))
              if not PAR_RE.match(os.path.basename(p))])      # the warm-start .par
    for a in aux:
        shutil.copy2(a, work)
    local = os.path.join(work, os.path.basename(best[2]))
    shutil.copy2(best[2], local)

    pr = subprocess.run([SCONECMD, "-e", local], cwd=work, capture_output=True, timeout=900)
    stos = [s for s in glob.glob(os.path.join(work, "*.sto")) if os.path.getsize(s) > 100000]
    if len(stos) != 1:
        return {"tag": tag, "status": "STO_%d" % len(stos), "rc": pr.returncode,
                "stderr": pr.stderr.decode("utf8", "replace")[-200:]}

    prov = {"tag": tag, "run_dir": run_dir, "resolved": note,
            "par": best[2], "best_gen": best[0], "fitness": best[1],
            # BOTH generations, always. The gap between them is the only way a reader can see
            # whether an arm systematically sat further from its cap than the other.
            # GAP IS AGAINST THE CAP, NOT AGAINST THE LAST `.par`. This read
            # `max_gen - best[0]`, and fitness falls monotonically, so the minimum-fitness `.par`
            # IS the last `.par` -- the difference was structurally 0 in every run and could
            # never have been anything else. An instrument reporting a quantity that cannot vary
            # is worse than no instrument: it occupies the slot where a real check would go and
            # reads as evidence. The informative gap is how many capped generations produced no
            # improvement at all (DR2K150_s3: best at 49, ran to 89 -> 40 wasted generations).
            "last_par_gen": max_gen, "terminal_gen": TERMINAL_GEN,
            "gen_gap": TERMINAL_GEN - best[0], "n_par": len(pars),
            "sto": stos[0], "sto_sha256": sha256(stos[0]),
            "config_sha256": sha256(os.path.join(work, "config.scone")),
            "min_progress": REGISTERED["min_progress"],
            "max_generations": REGISTERED["max_generations"],
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": "ok"}
    with open(os.path.join(work, "PROVENANCE.json"), "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=1)
    return prov


def main():
    os.makedirs(DEST, exist_ok=True)
    want = ["%s_s%d" % (t, s) for t in TAGS for s in range(1, SEEDS + 1)]
    rows = []
    for tag in want:
        r = replay(tag)
        rows.append(r)
        if r["status"] == "ok":
            print("  %-16s ok   best gen %-3d of %d  (%2d capped gens with no improvement)  "
                  "fit %.4f"
                  % (tag, r["best_gen"], r["terminal_gen"], r["gen_gap"], r["fitness"]))
        else:
            print("  %-16s %-12s %s" % (tag, r["status"], r.get("detail", "")[:80]))
    ok = sum(1 for r in rows if r["status"] == "ok")
    with open(os.path.join(DEST, "ledger.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    print("\n%d/%d replayed -> %s" % (ok, len(rows), DEST))
    gaps = [r["gen_gap"] for r in rows if r["status"] == "ok"]
    if gaps:
        print("best-to-cap gap: min %d  max %d  mean %.1f   (under a uniform cap this is expected;"
              " a systematic difference BETWEEN ARMS would not be)"
              % (min(gaps), max(gaps), sum(gaps) / len(gaps)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
