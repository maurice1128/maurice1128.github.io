"""Uphill by gradual continuation (gain-ladder), because jumping straight to 2 deg fails.

Earlier attempts went flat -> 2 deg and flat -> 5 deg in one step and never converged
(fitness 66-94), including after relaxing `min_velocity` to 0.8 and 0.6 -- so the velocity
threshold was NOT the cause. Downhill converges in one step, uphill does not, which is
physically sensible: uphill needs net positive work against gravity and the H0914 model has
limited plantarflexor reserve.

The standard remedy for a hard continuation problem is not a bigger budget, it is a LADDER:
solve an easy nearby problem, then warm-start the next rung from it. Each rung here starts from
the previous rung's converged solution, so the controller is never asked to jump far.

If a rung fails, the ladder stops there and reports the last feasible grade -- that is itself the
answer to "how steep can this model climb", and is reported rather than hidden.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
LAD = os.path.join(HERE, "opt_ladder")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE_OSIM = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data/H0914M_osim4.osim"

RUNGS = [0.5, 1.0, 1.5, 2.0, 3.0]
CONVERGED = 3.0          # fitness below which a rung counts as usable
MAX_GEN = 80
POLL = 90
TIMEOUT_PER_RUNG = 3000  # seconds


def best_of(tag, gen_cap=None):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, 1e9, None
    d = max(ds, key=os.path.getmtime)
    bp, bf, bg = None, 1e9, None
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            g, f = int(b[0]), float(b[2])
        except Exception:
            continue
        if gen_cap is not None and g > gen_cap:
            continue
        if f < bf:
            bp, bf, bg = p, f, g
    return bp, bf, bg


def make_rung(deg, init_par):
    """Uphill: gravity's forward component OPPOSES travel, so gx is negative."""
    g = 9.80665
    th = math.radians(deg)
    gx, gy = -g * math.sin(th), -g * math.cos(th)
    src = open(BASE_OSIM, encoding="utf-8", errors="ignore").read()
    osim = re.sub(r"<gravity>[^<]*</gravity>",
                  "<gravity>%.6f %.6f 0</gravity>" % (gx, gy), src, count=1)
    name = "UPL%02d" % round(deg * 10)
    open(os.path.join(LAD, "%s.osim" % name), "w", encoding="utf-8").write(osim)
    s = open(os.path.join(OPT, "HEALTHY.scone"), encoding="utf-8").read()
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + name, s, count=1)
    s = re.sub(r"model_file\s*=\s*\S+", "model_file = %s.osim" % name, s, count=1)
    s = re.sub(r"init_file\s*=\s*\S+", "init_file = %s" % os.path.basename(init_par), s, count=1)
    # people slow down uphill; holding the flat target is an unreasonable constraint
    s = re.sub(r"min_velocity\s*=\s*[0-9.]+", "min_velocity = 0.8", s, count=1)
    s = s.replace("min_progress = 1e-4",
                  "min_progress = 1e-7\n\tmax_generations = %d" % MAX_GEN, 1)
    p = os.path.join(LAD, "%s.scone" % name)
    open(p, "w", encoding="utf-8").write(s)
    return name, p


def main():
    os.makedirs(LAD, exist_ok=True)
    for f in glob.glob(os.path.join(OPT, "*.osim")) + glob.glob(os.path.join(OPT, "*.zml")):
        shutil.copy(f, LAD)
    # seed the ladder with the converged FLAT solution
    seed, sf, sg = None, 1e9, None
    for t in ("DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"):
        p, f, g = best_of(t)
        if p and f < sf:
            seed, sf, sg = p, f, g
    if not seed:
        print("no flat solution to seed from")
        return
    shutil.copy(seed, os.path.join(LAD, "rung_prev.par"))
    print("ladder seed: flat fitness=%.3f (gen %d)" % (sf, sg))

    log = []
    prev = os.path.join(LAD, "rung_prev.par")
    for deg in RUNGS:
        name, scen = make_rung(deg, prev)
        with open(os.path.join(LAD, "log_%s.txt" % name), "w") as lg:
            subprocess.Popen([SCONECMD, "-o", scen, "-l", "2"], cwd=LAD,
                             stdout=lg, stderr=subprocess.STDOUT)
        t0 = time.time()
        best = 1e9
        while time.time() - t0 < TIMEOUT_PER_RUNG:
            time.sleep(POLL)
            _, f, g = best_of(name)
            if f < best:
                best = f
            if f < CONVERGED:
                break
            if g is not None and g >= MAX_GEN - 1:
                break
        bp, bf, bg = best_of(name)
        ok = bf < CONVERGED
        log.append({"deg": deg, "fitness": bf, "gen": bg, "ok": bool(ok)})
        print("  %+4.1f deg : fitness %8.3f (gen %s) %s"
              % (deg, bf, bg, "OK -> next rung" if ok else "FAILED - ladder stops"))
        if not ok:
            break
        shutil.copy(bp, os.path.join(LAD, "rung_prev.par"))
        prev = os.path.join(LAD, "rung_prev.par")

    json.dump(log, open(os.path.join(HERE, "uphill_ladder.json"), "w"), indent=2)
    top = [r for r in log if r["ok"]]
    print("\nsteepest feasible uphill grade: %s"
          % ("%.1f deg" % top[-1]["deg"] if top else "NONE - model cannot climb at all"))


if __name__ == "__main__":
    main()
