"""Replay every remaining archived run at its CONVERGED BEST, into an isolated directory.

WHY. Round 40's reviewer established that §2.1's three surviving rows -- healthy n=8, true KV
0.100 n=6, true KV 0.200 n=6 -- are read from the same mid-run replay artefacts that §0.4 already
proved invalid, and that those rows are the sole source of SD_plan, Delta_alt and n. Four
consecutive council rounds were then spent arbitrating what Delta_EQ "is", producing five
different values, because the underlying measurement did not exist. Each replay takes ~10 s.

The arbitration was more expensive than the measurement. This is the measurement.

SELECTION RULE (§4.3, asserted not merely stated). The replayed `.par` is the MINIMUM-FITNESS
`.par` in the run directory, and the module ASSERTS that it is also the MAXIMUM-GENERATION `.par`.
When those disagree the run is reported E5_SELECTION and skipped -- it is not guessed. Two
independent auditors previously read different controllers out of the same directories; a rule
that two competent readers apply differently is not a rule, so it is enforced in code.

ISOLATION. SCONE's optimizer does not write `*.par.sto`; every archived one is a later replay
artefact, and replaying in place silently picks up a stale file from a DIFFERENT generation. Each
run therefore gets a clean directory containing exactly one `.par`, so exactly one `.sto` can
exist. Nothing under RESULTS is written or deleted.

CONCURRENCY. Two agents running sconecmd in one tree manufactured both a false failure
(DOSER1050 produced no output) and a false success (DOSER0000 printed "ok" naming a `.sto` that
was never written) earlier tonight. Both re-ran clean on a quiet tree, which is what proved they
were artefacts. This module runs strictly serially and STATS every file it claims to have made --
a tool's own success report is a claim, and claims get verified.
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
DEST = os.path.join(HERE, "replay_registered")

PAR_RE = re.compile(r"^(\d+)_([0-9.]+)_([0-9.]+)\.par$")

# The runs §2.1's three rows are built from, plus the two B-series the reviewer could not certify.
# Named explicitly: a glob would sweep in the user's separate study, which shares this directory.
WANTED = [
    "HEALTHY_s1", "HEALTHY_s2", "HEALTHY_s3", "HEALTHY_s4",
    "DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3",
    "SPAS005", "SPAS005_s2",
    "SPAS01", "SPAS01_s2",
    "BSPAS005_s2", "BSPAS01_s1",
    # ---- THE WEAKNESS ARM ----------------------------------------------------------------
    # Added because the clinical question -- can 2D sagittal video tell plantarflexor SPASTICITY
    # from dorsiflexor WEAKNESS -- has never once been asked on data that survives its own gates,
    # and the two halves failed for DIFFERENT reasons that have both now been removed:
    #
    #   spastic arm  every run delivered 2x and unilaterally mis-targeted (defect #49) -- fixed,
    #                and the archived runs are relabelled by MEASURED delivered gain
    #   weakness arm never affected: `SpasticL` count is 0 in every PAR/DPAR scenario, because
    #                weakness is a `max_isometric_force` scale in the .osim, not a controller
    #                injection. The arm was CLEAN the whole time.
    #
    # What was never clean was the COMPARISON: every previous attempt read phenotypes from
    # mid-run replay artefacts, and the staleness was correlated with dose (deep spastic runs
    # lagged their best by hundreds of generations; weakness runs converge by ~gen 90). Replaying
    # BOTH arms at each run's converged best is what removes that, and it is the only thing that
    # was ever standing between this archive and an answer.
    "PAR20_s1", "PAR20_s2", "PAR20_s3", "PAR20_s4",
    "PAR40_s1", "PAR40_s2", "PAR40_s3", "PAR40_s4",
    "PAR60_s1", "PAR60_s2", "PAR60_s3", "PAR60_s4",
    "DPAR20_s1", "DPAR20_s2", "DPAR20_s3",
    "DPAR40_s1", "DPAR40_s2", "DPAR40_s3",
    "DPAR60_s1", "DPAR60_s2", "DPAR60_s3",
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_pars(run_dir):
    out = []
    for p in glob.glob(os.path.join(run_dir, "*.par")):
        m = PAR_RE.match(os.path.basename(p))
        if m:
            out.append((int(m.group(1)), float(m.group(3)), p))
    return out


def select_registered_par(run_dir):
    """(par_path, gen, fitness, max_gen) or raise. §4.3, with the assertion enforced."""
    pars = parse_pars(run_dir)
    if not pars:
        raise ValueError("E5_NO_PAR: no parseable .par in %s" % run_dir)
    best = min(pars, key=lambda t: t[1])
    max_gen = max(t[0] for t in pars)
    ties = [t for t in pars if abs(t[1] - best[1]) < 1e-12]
    if len(ties) > 1:
        raise ValueError("E5_SELECTION: %d .par tie at fitness %.6f (generations %s) -- "
                         "the converged controller is not uniquely determined; register a "
                         "tie-break before using this run"
                         % (len(ties), best[1], sorted(t[0] for t in ties)))
    if best[0] != max_gen:
        raise ValueError("E5_SELECTION: min-fitness .par is generation %d but the run reaches "
                         "%d -- best and deepest disagree, so 'converged best' is undefined "
                         "for this run" % (best[0], max_gen))
    return best[2], best[0], best[1], max_gen


def replay(tag):
    dirs = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not dirs:
        return {"tag": tag, "status": "NO_RESULT_DIR"}
    if len(dirs) > 1:
        return {"tag": tag, "status": "AMBIGUOUS_DIR", "n": len(dirs),
                "dirs": [os.path.basename(d) for d in dirs]}
    run_dir = dirs[0]
    try:
        par, gen, fit, max_gen = select_registered_par(run_dir)
    except ValueError as e:
        return {"tag": tag, "status": str(e).split(":")[0], "detail": str(e)}

    work = os.path.join(DEST, os.path.basename(run_dir))
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    aux_files = (glob.glob(os.path.join(run_dir, "*.osim"))
                 + glob.glob(os.path.join(run_dir, "*.zml"))
                 + glob.glob(os.path.join(run_dir, "*.hfd"))
                 + glob.glob(os.path.join(run_dir, "config.scone")))
    # The WARM-START `.par` -- any `.par` NOT matching the generation pattern. `config.scone`
    # names it (`ResultH0914Gait10.par`) and SCONE aborts without it:
    #     Could not find any of the following files: [ ResultH0914Gait10.par ... ]
    # Omitting it produced E5_STO_0 on 12 of 13 runs -- a total failure that looked exactly like
    # a modelling problem and was a missing-file problem. The four runs replayed earlier tonight
    # succeeded only because that file had been copied in by hand.
    aux_files += [p for p in glob.glob(os.path.join(run_dir, "*.par"))
                  if not PAR_RE.match(os.path.basename(p))]
    for aux in aux_files:
        shutil.copy2(aux, work)
    local_par = os.path.join(work, os.path.basename(par))
    shutil.copy2(par, local_par)

    t0 = time.time()
    pr = subprocess.run([SCONECMD, "-e", local_par], cwd=work,
                        capture_output=True, timeout=900)
    # STAT the output. Do not trust the exit code or any printed "ok".
    stos = [s for s in glob.glob(os.path.join(work, "*.sto"))
            if os.path.getsize(s) > 100000]
    if len(stos) != 1:
        return {"tag": tag, "status": "E5_STO_%d" % len(stos), "rc": pr.returncode,
                "work": work, "stderr": pr.stderr.decode("utf8", "replace")[-300:]}

    prov = {"tag": tag, "run_dir": run_dir, "par": par, "gen": gen, "fitness": fit,
            "max_gen": max_gen, "n_par": len(parse_pars(run_dir)),
            "sto": stos[0], "sto_bytes": os.path.getsize(stos[0]),
            "sto_sha256": sha256(stos[0]),
            "config_sha256": (sha256(os.path.join(work, "config.scone"))
                              if os.path.exists(os.path.join(work, "config.scone")) else None),
            "cmd": "%s -e %s (cwd=%s)" % (SCONECMD, local_par, work),
            "seconds": round(time.time() - t0, 1),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "ok"}
    with open(os.path.join(work, "PROVENANCE.json"), "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=1)
    return prov


def main():
    os.makedirs(DEST, exist_ok=True)
    results = []
    for tag in WANTED:
        r = replay(tag)
        results.append(r)
        if r["status"] == "ok":
            print("  %-14s ok    gen=%-4d fit=%.4f  %d KB  %.0fs"
                  % (tag, r["gen"], r["fitness"], r["sto_bytes"] // 1024, r["seconds"]))
        else:
            print("  %-14s %s   %s" % (tag, r["status"], r.get("detail", "")[:90]))
    # APPEND to the ledger, never overwrite -- the previous manifest held 2 entries while 11
    # directories existed, because each run rewrote it.
    led = os.path.join(DEST, "replay_ledger.json")
    old = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else []
    with open(led, "w", encoding="utf-8") as f:
        json.dump(old + results, f, indent=1)
    ok = sum(1 for r in results if r["status"] == "ok")
    print("\n%d/%d replayed -> %s" % (ok, len(results), DEST))
    return 0


if __name__ == "__main__":
    sys.exit(main())
