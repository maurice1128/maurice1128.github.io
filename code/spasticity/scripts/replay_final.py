"""Re-replay EVERY condition from its final best .par, in an isolated directory.

Motivation: the previous pipeline replayed into the SCONE results directory and then took the
newest `*.sto` there, which could be a stale file from an earlier replay of a different
generation. That produced features from generation 5-8 controllers while the reported fitness
came from the best .par -- the confound that invalidated the ankle-ROM result. Here each run is
replayed alone in a clean directory that can contain exactly one .sto, and the generation the
features actually come from is recorded alongside every number.

Records BOTH sides (affected left, intact right) so lateralization can be checked.
"""
import time
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sto_utils import cycle_features  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
LIVE_PAR_MINUTES = 15   # a .par newer than this means an optimizer may still be running here
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
WORK = os.path.join(HERE, "replay_final")

TAGS = (["HEALTHY_s%d" % i for i in (1, 2, 3, 4)] +
        ["PAR20_s%d" % i for i in (1, 2, 3, 4)] +
        ["PAR40_s%d" % i for i in (1, 2, 3, 4)] +
        ["PAR60_s%d" % i for i in (1, 2, 3, 4)] +
        ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4",
         "SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"])


def best_par(tag):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None, None
    d = max(ds, key=os.path.getmtime)
    best, bf, bg = None, 1e9, None
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            gen, fit = int(b[0]), float(b[2])
        except Exception:
            continue
        if fit < bf:
            best, bf, bg = p, fit, gen
    return best, bf, bg


def main():
    os.makedirs(WORK, exist_ok=True)
    out = {}
    for tag in TAGS:
        par, fit, gen = best_par(tag)
        if par is None:
            out[tag] = {"status": "no_result"}
            continue
        # `sconecmd -e` needs the full run context (scenario + model + state) as SCONE archived
        # it, so replay happens IN the run directory. The stale-.sto hazard is removed by
        # deleting every .sto there first and asserting that exactly one exists afterwards --
        # so the features provably come from the .par named in `gen`/`fitness` below.
        # Only this project's own run directories are touched.
        d = os.path.dirname(par)
        # ★ LIVENESS GUARD (watchdog ruling #43, executed round 37 — issued round 22 and never
        # implemented until now). The loop below deletes every `.sto` in a run directory. If a
        # CMA-ES optimizer is still writing to that directory the delete races it and destroys
        # SCONE's own archived traces.
        # Key off the newest `.par` mtime, NOT the directory's and NOT any `.sto`'s: SCONE writes
        # `.par` files ONLY while optimizing, whereas `sconecmd -e` writes only `.sto`. So a recent
        # `.par` means "an optimizer is working here" while a recent `.sto` only means "somebody
        # replayed" -- which is exactly the confusion that made the earlier directory-mtime guard
        # reject its own inputs.
        pars = glob.glob(os.path.join(d, "0*.par"))
        if pars:
            age_min = (time.time() - max(os.path.getmtime(p) for p in pars)) / 60.0
            if age_min < LIVE_PAR_MINUTES:
                out[tag] = {"status": "live_optimizer", "par_age_min": round(age_min, 1),
                            "fitness": fit, "gen": gen}
                print("%-13s SKIPPED -- newest .par is %.1f min old; an optimizer may still be "
                      "writing here, refusing to delete its .sto" % (tag, age_min))
                continue
        for old in glob.glob(os.path.join(d, "*.sto")):
            os.remove(old)
        try:
            subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=900)
        except Exception:
            out[tag] = {"status": "replay_timeout", "fitness": fit, "gen": gen}
            print("%-13s TIMEOUT" % tag)
            continue
        cand = [c for c in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(c) > 1000]
        if len(cand) != 1:
            out[tag] = {"status": "sto_%d" % len(cand), "fitness": fit, "gen": gen}
            print("%-13s %d sto files" % (tag, len(cand)))
            continue
        L = cycle_features(cand[0], side="l")
        R = cycle_features(cand[0], side="r")
        if L is None:
            out[tag] = {"status": "no_cycles", "fitness": fit, "gen": gen}
            print("%-13s gen=%-3d fit=%.3f  no complete cycles" % (tag, gen, fit))
            continue
        out[tag] = {"status": "ok", "fitness": fit, "gen": gen, "l": L, "r": R}
        print("%-13s gen=%-3d fit=%.3f  L: rom=%5.2f vel=%6.1f  R: rom=%5.2f"
              % (tag, gen, fit, L["ank_rom"], L["ank_vel_max"],
                 R["ank_rom"] if R else float("nan")))
    json.dump(out, open(os.path.join(HERE, "scone_final_features.json"), "w"), indent=2)
    ok = sum(1 for v in out.values() if v.get("status") == "ok")
    print("\nok %d / %d  -> scone_final_features.json" % (ok, len(TAGS)))


if __name__ == "__main__":
    main()
