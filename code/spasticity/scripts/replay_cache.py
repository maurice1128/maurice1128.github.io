"""Provably-sourced replay: every waveform traceable to a named .par, or it does not exist.

THE DEFECT THIS REMOVES.
Analysis scripts have repeatedly picked their `.sto` by modification time out of the SCONE results
directory (`newest_sto()`). That directory accumulates files from every earlier replay, so the
newest one is whatever was replayed last -- not the best controller. Council round 9 measured the
damage: 12/12 non-spastic runs were being analysed at their final generation while 8/10 spastic
runs were analysed at generation 59-83 although their optimizations had reached 103-337. The
classes were being compared at different optimization depths, which is the exact confound that
already forced three retractions on this project.

THE FIX.
For each run: find the best `.par` by fitness, delete every `.sto` in that run directory, replay
that one `.par`, and assert exactly one `.sto` results. The waveform is then provably the named
controller's. Generation and fitness are recorded in the manifest beside every entry, so any
downstream table can be checked for depth matching without re-reading SCONE.

Results are cached in `replay_manifest.json` keyed by (tag, generation, fitness): a run that has
progressed since the last replay gets re-replayed automatically, an unchanged one does not.

SAFETY: only touches run directories whose tag appears in the caller's list. The user's own
separate study (opt_s1*-opt_s4*, KF60L, KE40L, HF60L) is never named by this project and is never
enumerated here.
"""
import glob
import json
import os
import re
import subprocess
import time

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "replay_manifest.json")

# --- DESTRUCTION GUARD -------------------------------------------------------------------------
# `replay()` DELETES every .sto in the target run directory before replaying. The SCONE results
# directory is SHARED with the user's own separate study, so a mistyped or mis-generated tag here
# destroys their outputs. The guard is therefore a WHITELIST of this project's tag prefixes, not a
# blacklist: an earlier blacklist (`opt_s\d|KF\d|KE\d|HF\d`) missed DF20L, PF20L, s1KF60L and
# every other family they own, and a blacklist can only ever protect the names already thought of.
ALLOWED = re.compile(
    r"^(DHEALTHY|DPAR\d+|DSPAS\d+|SPAS0\d+|CMS\d+|CMW\d+|EQS\d+|EQW\d+|MMIX\w+"
    r"|RD2\w+|RE2\w+|D2\w+|E2\w+|UPL\d+|UPU\w+|TON\d+|B[A-Z]+)(_s\d+)?$", re.I)


def _check_tag(tag):
    if not ALLOWED.match(tag):
        raise ValueError(
            "refusing to touch %r: not a recognised tag of this project. replay() deletes .sto "
            "files, and the SCONE results directory is shared with the user's separate study "
            "(opt_s*, KF*/KE*/HF*, DF*/PF*, s1KF60L...). Add the prefix to ALLOWED only if the "
            "run is genuinely this project's." % tag)


def best_par(tag, gen_cap=None):
    """(path, fitness, generation) of the best .par SCONE wrote for this run.

    gen_cap enforces depth matching: pass the same cap for every arm and each run is read at a
    common generation ceiling, so no arm is credited with compute the others did not get.
    """
    _check_tag(tag)
    ds = sorted(d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d))
    if not ds:
        return None, None, None
    if len(ds) > 1:
        # A shadow directory's .par would otherwise win on fitness and then be replayed against
        # THAT directory's own config.scone and .osim -- a different model wearing this tag.
        raise RuntimeError("%r resolves to %d directories; rename the stale ones before running:"
                           "\n  %s" % (tag, len(ds), "\n  ".join(os.path.basename(x) for x in ds)))
    # A warm-started run has its init_file COPIED into the results directory by SCONE, keeping the
    # donor's `<gen>_<sigma>_<fitness>.par` name. Observed: EQS010_s1 (launched seconds earlier,
    # max_generations = 90) contained `0333_0.813_0.790.par` from its SPAS01_s3 warm start, next
    # to its own 0000 and 0002. A plain `0*.par` scan selects the DONOR's controller, then replays
    # it in this directory against this model, and labels the result with this tag.
    # Any .par whose generation exceeds the run's own max_generations is definitionally foreign.
    cap = _scenario_max_gen(ds[0])
    setup_t = _setup_time(ds[0])
    bp, bf, bg = None, 1e9, None
    for d in ds:
        for p in sorted(glob.glob(os.path.join(d, "0*.par"))):
            m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
            if not m:
                continue
            g, f = int(m.group(1)), float(m.group(2))
            # Two independent tests for a foreign warm-start copy. The generation test alone is
            # NOT sufficient: EQW60_s1 was warm-started from DPAR60_s3's `0085_...par`, and 85 is
            # below its own cap of 90, so it looks like a legitimate late generation. The
            # timestamp test catches it -- SCONE copies init_file during setup, BEFORE it writes
            # config.scone, whereas every .par the run itself produces is written afterwards.
            if cap is not None and g > cap:
                continue
            if setup_t is not None and os.path.getmtime(p) <= setup_t:
                continue
            if gen_cap is not None and g > gen_cap:
                continue
            if f < bf:
                bp, bf, bg = p, f, g
    return bp, bf, bg


def _setup_time(run_dir):
    """When SCONE finished writing this run's setup files. Anything older is not the run's output.

    Verified on EQS010_s1: warm-start copy 05:56:35, model 05:56:34, config.scone 05:56:43, and
    the run's own first .par at 05:59:07. The warm start predates config.scone; every generation
    the run actually produces follows it.
    """
    cfg = os.path.join(run_dir, "config.scone")
    return os.path.getmtime(cfg) if os.path.exists(cfg) else None


def _scenario_max_gen(run_dir):
    """max_generations declared in the run's OWN archived config.scone, or None if absent."""
    cfg = os.path.join(run_dir, "config.scone")
    if not os.path.exists(cfg):
        return None
    m = re.search(r"max_generations\s*=\s*(\d+)",
                  open(cfg, encoding="utf-8", errors="ignore").read())
    return int(m.group(1)) if m else None


LIVE_SECONDS = 900     # a run touched within this window is treated as still optimizing


def is_live(tag):
    """Is this optimization still running? Replaying a live run is unsafe and unreproducible.

    SCONE writes into the same directory it is optimizing in, so a replay races the optimizer:
    the .sto can be deleted mid-read (observed: FileNotFoundError on CMS030_s1), and the best .par
    changes between the moment it is chosen and the moment it is replayed. Worse, any number
    obtained this way is irreproducible -- it depends on when the script happened to be launched.
    """
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return False
    # Watch history.txt ONLY. The first version watched the newest mtime of anything in the
    # directory, which meant MY OWN replay -- which writes a .sto there -- made the run look live
    # for the next 15 minutes. That silently excluded SPAS005_s2/s3/s4 and SPAS01 from
    # seed_spread.py at the deeper ceilings, leaving those rows with n=0-1 and no warning.
    # `sconecmd -e` never writes history.txt; only an optimization in progress does. So it is a
    # clean discriminator between "still optimizing" and "I just replayed here".
    # ...and history.txt is BUFFERED and lags: EQS010_s1 showed a 20.7-minute-old history.txt while
    # sconecmd was demonstrably still optimizing it -- the opposite failure, letting a live run
    # through. The correct key is the newest `.par`: SCONE writes `.par` ONLY while optimizing, and
    # replay (`sconecmd -e`) writes only `.sto`. That separates "optimizer working" from "I just
    # replayed here" exactly, with no buffering lag and no dependence on enumerating processes.
    pars = [os.path.getmtime(p) for d in ds for p in glob.glob(os.path.join(d, "0*.par"))]
    if pars and (time.time() - max(pars)) < LIVE_SECONDS:
        return True
    # Secondary guard only: a live sconecmd on this scenario, for a run that has not yet improved
    # (so has written no .par). Never trusted to prove a run is DEAD -- see _optimizing_tags.
    t = _optimizing_tags()
    return bool(t is not None and tag.lower() in t)


_TAGS_CACHE = [None, 0.0]


def _optimizing_tags(ttl=20.0):
    """Lower-cased scenario stems of every sconecmd currently running, or None if unknowable.

    Returns None rather than an empty set when the query fails, so a failure to enumerate is never
    mistaken for 'nothing is running' -- that would re-open the exact hazard this guards.
    """
    if _TAGS_CACHE[0] is not None and (time.time() - _TAGS_CACHE[1]) < ttl:
        return _TAGS_CACHE[0]
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"name='sconecmd.exe'\" "
             "| Select-Object -ExpandProperty CommandLine"],
            capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return None
        tags = set()
        for m in re.finditer(r"([A-Za-z0-9_]+)\.scone", out.stdout):
            tags.add(m.group(1).lower())
        _TAGS_CACHE[0], _TAGS_CACHE[1] = tags, time.time()
        return tags
    except Exception:
        return None


def replay(tag, gen_cap=None, force=False, timeout=900, allow_live=False):
    """Replay the best .par and return {sto, fitness, gen} -- or {error} explaining why not."""
    cache = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    if not allow_live and is_live(tag):
        return {"error": "run is still optimizing -- refusing to replay live data"}
    par, fit, gen = best_par(tag, gen_cap)
    if par is None:
        return {"error": "no .par" + ("" if gen_cap is None else " at gen<=%d" % gen_cap)}

    key = "%s|%s|%s" % (tag, gen, fit)
    hit = cache.get(key)
    if hit and not force and hit.get("sto") and os.path.exists(hit["sto"]):
        return hit

    d = os.path.dirname(par)
    # A swallowed delete failure is the dangerous case: if a stale .sto is locked (SCONE Studio
    # open on the directory) AND the replay then fails, the post-replay scan finds exactly one
    # file and the STALE waveform is accepted and recorded under the new .par's key -- a manifest
    # asserting a provenance that is false. Fail loudly instead.
    for old in glob.glob(os.path.join(d, "*.sto")):
        try:
            os.remove(old)
        except OSError as e:
            return {"error": "could not clear stale .sto (%s)" % e, "fitness": fit, "gen": gen}
    try:
        proc = subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"error": "replay timeout", "fitness": fit, "gen": gen}
    if proc.returncode != 0:
        return {"error": "sconecmd exit %d" % proc.returncode, "fitness": fit, "gen": gen}
    cand = [c for c in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(c) > 1000]
    if len(cand) != 1:
        # more than one means something else wrote here concurrently; refuse to guess which
        return {"error": "%d sto after replay" % len(cand), "fitness": fit, "gen": gen}

    rec = {"sto": cand[0], "fitness": fit, "gen": gen, "par": os.path.basename(par)}
    cache[key] = rec
    json.dump(cache, open(MANIFEST, "w"), indent=2)
    return rec


def replay_all(tags, gen_cap=None, verbose=True):
    """Replay a list of runs; returns {tag: record}. Prints the depth spread, which is the
    number that has to be checked before any cross-arm comparison is legitimate."""
    out = {}
    for t in tags:
        r = replay(t, gen_cap=gen_cap)
        out[t] = r
        if verbose:
            if "error" in r:
                print("  %-14s FAILED: %s" % (t, r["error"]))
            else:
                print("  %-14s gen=%-4d fit=%.4f" % (t, r["gen"], r["fitness"]))
    ok = [r for r in out.values() if "error" not in r]
    if verbose and ok:
        gs = [r["gen"] for r in ok]
        print("  -> %d/%d replayed, generation %d-%d" % (len(ok), len(tags), min(gs), max(gs)))
    return out
