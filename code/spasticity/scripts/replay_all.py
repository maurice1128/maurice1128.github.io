"""Replay each converged condition's BEST .par -> .sto, then extract steady-state gait
features on complete cycles only (never a fall transient).

A condition is admitted to the analysis ONLY if it yields >= 2 complete gait cycles after a
settle period AND survives to the end of the sim. Conditions that fall are recorded as
`unstable` and reported honestly rather than silently dropped or averaged over the fall.
"""
# ⛔ STANCE-WINDOW REPAIR (2026-07-28) -- NUMBERS FROM THIS SCRIPT HAVE CHANGED.
#
# This script reads `ank_stance_mean` from sto_utils. That feature USED TO average the first
# 60%% of the STRIDE by index, not the stance phase. Measured stance fraction in this archive is
# 0.553-0.616, so the old value folded up to 5%% of swing into "stance" -- and how much it folded
# in varied with the injected dose, i.e. with the independent variable.
#
# sto_utils now uses the GRF-defined stance mask. Measured difference on GATE2: -8.5874 (old)
# vs -7.9657 (new) = 0.62 deg. Below the 3.8 deg MDC floor, so no qualitative conclusion
# changes AS A RESULT OF THIS DEFECT. That is NOT a statement that the old numbers are
# usable: they remain subject to the separate prohibitions in paper/HANDOFF.md -- the 2x
# delivery relabelling, and the withdrawn CMS-vs-CMW contrast.
# but EVERY NUMBER THIS SCRIPT PRINTED BEFORE 2026-07-28 WAS COMPUTED ON THE WRONG WINDOW and
# must be disclosed as such wherever it was quoted. Do not compare old output to new output.
#
# See paper/HANDOFF.md and paper/REFEREE_methods_contribution.md.

import os, glob, json, subprocess, sys, time, hashlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sto_utils import (cycle_features, load_sto,                       # noqa: E402
                       select_registered_par, RegisteredSelectionError)

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
STO = os.path.join(HERE, "sto")
CONDS = ["HEALTHY", "PAR20", "PAR40", "PAR60",
         "SPAS1", "SPAS2", "SPAS3", "MIX20S2", "MIX40S2", "MIX40S1"]

# =============================================================================================
# THE REGISTERED REPLAY STEP -- PREREGISTRATION_dose_response_v2.md §7.1a
# =============================================================================================
# Registered so that the endpoint has a PRODUCER, not a scavenger. Before round 37 the endpoint
# was read from whichever `*.par.sto` happened to be lying in the run directory; measured, those
# files come from generations 5/6/11/9 while the runs' best `.par` are at 34/34/41/26, three of
# the four anchor directories hold TWO of them, and 148 of 316 non-protected archived result
# directories hold none at all. SCONE's optimizer never writes a `.par.sto`.
#
# ISOLATION IS THE POINT. Replay writes into
#     <scone>/replay_registered/<run-directory-name>/
# and NOTHING under C:\Users\maurice\Documents\SCONE\results\ is ever written, deleted or moved:
# the run directory is opened read-only, its files are COPIED out. This is the opposite of
# `replay_final.py`, which replays in place after deleting the run directory's `.sto` files.
#
# PROVENANCE OF `config.scone`. The scenario copied into the isolated directory is the
# `config.scone` that SCONE ITSELF archived inside the run directory at launch -- not
# `opt_seeds/<TAG>.scone` and not `opt2/<TAG>.scone`, either of which may have been regenerated
# or edited after the run started. Its SHA-256 is recorded in PROVENANCE.json next to the .sto,
# so C1 (block identity) can be re-run later against the exact bytes that were replayed.

REPLAY_ROOT = os.path.join(HERE, "replay_registered")
REPLAY_AUX = ("*.osim", "*.zml", "ResultH0914Gait10.par")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def replay_registered(run_dir, root=REPLAY_ROOT, sconecmd=SCONECMD, timeout=900,
                      dry_run=False):
    """§7.1a. Replay the registered `.par` of `run_dir` in an ISOLATED directory.

    Returns a dict with keys: status, run_dir, work, par, gen, fitness, max_gen, sto,
    config_sha256, cmd. `status` is one of
        "ok"                 exactly one `.sto` was produced and it is the registered one
        "E5_SELECTION"       §4.3 did not select exactly one `.par` (detail in `error`)
        "E5_STO_%d"          the isolated replay produced N != 1 usable `.sto`
        "replay_failed"      sconecmd did not return successfully
    No status other than "ok" may be analysed; every other status is exclusion E5.

    THE EXACT COMMAND, as registered:
        sconecmd.exe -e <work>\\<GGGG_median_best.par>      (cwd = <work>)
    """
    run_dir = os.path.abspath(run_dir)
    tag = os.path.basename(os.path.normpath(run_dir))
    work = os.path.join(root, tag)
    rec = {"run_dir": run_dir, "tag": tag, "work": work, "status": "E5_SELECTION",
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        sel = select_registered_par(run_dir)
    except RegisteredSelectionError as e:
        rec["error"] = str(e)
        return rec
    rec.update({k: sel[k] for k in ("par", "gen", "fitness", "max_gen", "n_par")})

    cfg = os.path.join(run_dir, "config.scone")
    if not os.path.exists(cfg):
        rec["status"] = "E5_SELECTION"
        rec["error"] = "no config.scone archived in %s -- provenance cannot be established" % run_dir
        return rec
    rec["config_sha256"] = _sha256(cfg)

    os.makedirs(work, exist_ok=True)
    # Only the ISOLATED directory is ever cleaned. Never the run directory.
    for old in glob.glob(os.path.join(work, "*.sto")):
        os.remove(old)
    shutil.copy2(cfg, os.path.join(work, "config.scone"))
    for pat in REPLAY_AUX:
        for aux in glob.glob(os.path.join(run_dir, pat)):
            shutil.copy2(aux, os.path.join(work, os.path.basename(aux)))
    par_local = os.path.join(work, os.path.basename(sel["par"]))
    shutil.copy2(sel["par"], par_local)
    rec["cmd"] = "%s -e %s   (cwd=%s)" % (sconecmd, par_local, work)

    if dry_run:
        rec["status"] = "dry_run"
        json.dump(rec, open(os.path.join(work, "PROVENANCE.json"), "w"), indent=2)
        return rec

    try:
        cp = subprocess.run([sconecmd, "-e", par_local], cwd=work,
                            capture_output=True, timeout=timeout)
        rec["returncode"] = cp.returncode
        rec["stdout_tail"] = cp.stdout.decode("utf-8", "ignore")[-2000:]
    except Exception as e:                                        # noqa: BLE001
        rec["status"] = "replay_failed"
        rec["error"] = repr(e)
        json.dump(rec, open(os.path.join(work, "PROVENANCE.json"), "w"), indent=2)
        return rec

    cand = [c for c in glob.glob(os.path.join(work, "*.sto")) if os.path.getsize(c) > 1000]
    if len(cand) != 1:
        rec["status"] = "E5_STO_%d" % len(cand)
        rec["sto_candidates"] = [os.path.basename(c) for c in cand]
    else:
        rec["status"] = "ok"
        rec["sto"] = cand[0]
        rec["sto_sha256"] = _sha256(cand[0])
    json.dump(rec, open(os.path.join(work, "PROVENANCE.json"), "w"), indent=2)
    return rec


def main_registered(dirs, dry_run=False):
    """CLI: python replay_all.py --registered <run-dir> [<run-dir> ...] [--dry-run]"""
    os.makedirs(REPLAY_ROOT, exist_ok=True)
    out = []
    for d in dirs:
        r = replay_registered(d, dry_run=dry_run)
        out.append(r)
        print("%-52s %-14s gen=%-4s fit=%-8s %s"
              % (r["tag"], r["status"], r.get("gen"), r.get("fitness"),
                 os.path.basename(r.get("sto") or r.get("error", ""))[:60]))
    json.dump(out, open(os.path.join(REPLAY_ROOT, "replay_registered.json"), "w"), indent=2)
    return 0 if all(r["status"] in ("ok", "dry_run") for r in out) else 1


def best_par(tag):
    """Lowest-fitness generation par in the newest results dir for this tag."""
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None
    d = max(ds, key=os.path.getmtime)
    pars = glob.glob(os.path.join(d, "0*.par"))
    if not pars:
        return d, None
    def fit(p):
        try:
            return float(os.path.basename(p)[:-4].split("_")[2])
        except Exception:
            return 1e9
    return d, min(pars, key=fit)


def main():
    os.makedirs(STO, exist_ok=True)
    out = {}
    for tag in CONDS:
        d, par = best_par(tag)
        if par is None:
            out[tag] = {"status": "no_result"}
            print("%-9s no result yet" % tag)
            continue
        fit = float(os.path.basename(par)[:-4].split("_")[2])
        # Replay into an ISOLATED directory. Replaying into the results dir and then taking
        # the newest *.sto there can silently pick up a stale file from an earlier replay of a
        # DIFFERENT generation -- which previously caused features to be read from gen-6
        # controllers while the reported fitness came from the best par. Copy the chosen .par
        # plus the model/state files into a clean dir so exactly one .sto can exist.
        work = os.path.join(STO, "replay_" + tag)
        if os.path.isdir(work):
            for old in glob.glob(os.path.join(work, "*.sto")):
                os.remove(old)
        os.makedirs(work, exist_ok=True)
        for aux in glob.glob(os.path.join(d, "*.osim")) + glob.glob(os.path.join(d, "*.zml")):
            dst = os.path.join(work, os.path.basename(aux))
            if not os.path.exists(dst):
                open(dst, "wb").write(open(aux, "rb").read())
        par_local = os.path.join(work, os.path.basename(par))
        open(par_local, "wb").write(open(par, "rb").read())
        subprocess.run([SCONECMD, "-e", par_local], cwd=work,
                       capture_output=True, timeout=900)
        cand = [c for c in glob.glob(os.path.join(work, "*.sto"))
                if os.path.getsize(c) > 1000]
        if not cand:
            out[tag] = {"status": "replay_failed", "fitness": fit}
            print("%-9s replay FAILED" % tag)
            continue
        if len(cand) > 1:  # must never happen in a clean dir; fail loudly rather than guess
            out[tag] = {"status": "ambiguous_sto", "fitness": fit, "n": len(cand)}
            print("%-9s AMBIGUOUS (%d .sto)" % (tag, len(cand)))
            continue
        f = cand[0]
        gen = int(os.path.basename(par)[:4])
        out.setdefault(tag, {})
        feats = cycle_features(f, side="l")
        if feats is None:
            out[tag] = {"status": "unstable_no_cycles", "fitness": fit, "sto": f}
            print("%-9s fit=%-7.3f UNSTABLE (no complete cycles)" % (tag, fit))
        else:
            feats.update(status="ok", fitness=fit, sto=f)
            out[tag] = feats
            print("%-9s fit=%-7.3f cycles=%-2d ank_min=%6.1f ank_stance=%6.1f rom=%5.1f"
                  % (tag, fit, feats["n_cycles"], feats["ank_min"],
                     feats["ank_stance_mean"], feats["ank_rom"]))
    p = os.path.join(HERE, "scone_features.json")
    json.dump(out, open(p, "w"), indent=2)
    print("\nwrote", p)
    return out


if __name__ == "__main__":
    if "--registered" in sys.argv:
        i = sys.argv.index("--registered")
        targets = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        sys.exit(main_registered(targets, dry_run="--dry-run" in sys.argv))
    main()
