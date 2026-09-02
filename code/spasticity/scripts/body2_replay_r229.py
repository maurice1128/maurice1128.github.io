# -*- coding: utf-8 -*-
"""Round 229 rev 5 -- produce phenotypes for the 2D H0914M second-body replication.

REPLAY ONLY. `sconecmd -e <best.par>` writes only .sto and never .par, so this cannot
disturb the archived optima and cannot re-draw an optimum. No optimisation is launched;
no --run and no --launch is passed to anything.

FIELD CONVENTION (registration rev 2 section 1). SCONE writes
    <generation>_<median_fitness>_<best_fitness>.par
so the best-fitness field is FIELD 3, not field 2. The two readings select a different .par
for 41 of 78 SG2 cells including 4 of 6 controls, and section 3c forbids re-running a replay
that produced a .sto -- so the wrong field would have permanently fixed the phenotype of most
of the control arm. assert_field_convention() checks this against history.txt and aborts if
it does not hold.

Registered replay discipline (defect register #205):
  * a replay may be re-run ONLY after a NON-RESULT (absent/zero-length .sto, or a crash);
  * re-running a replay that produced a .sto is FORBIDDEN whatever the value in it;
  * every attempt, including failures, is written to the ledger.

Concurrency is capped against the MACHINE-WIDE sconecmd count. If the user's own study is
running, our cells give way.
"""
import io
import os
import re
import sys
import glob
import json
import time
import subprocess

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
LEDGER = os.path.join(PAPER, "BODY2_REPLAY_LEDGER_r229.json")

FIT_GATE = 1.5
MAX_OURS = 3
MACHINE_CAP = 4

PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")

# Planes are SLOPES, implemented as tilted gravity, read from the base .osim:
#   SG0 gravity (0, -9.80665, 0)          = 0.0000 deg  -- LEVEL, PRIMARY
#   SG2 gravity (0.342247, -9.800676, 0)  = 2.0000 deg  -- secondary
#   SG5 gravity (0.854706, -9.769333, 0)  = 5.0000 deg  -- EXCLUDED, 24/78 admitted
# CMW80 (x0.200) is included: it is a genuine weakness severity and rev 2 omitted it
# with no stated reason.
FAMILIES = [
    "SG0_DR2K000", "SG0_DR2K050", "SG0_DR2K075", "SG0_DR2K200",
    "SG0_PAR20", "SG0_PAR40", "SG0_CMW80",
    "SG2_DR2K000", "SG2_DR2K050", "SG2_DR2K075", "SG2_DR2K200",
    "SG2_PAR20", "SG2_PAR40", "SG2_CMW80",
]



# --- provenance: every deposit records the sha256 of the script that produced it and
# --- of the registration it implements. Revisions 1-4 asserted this while no script
# --- contained the string "sha256"; with no digest on disk every registered constant
# --- was silently mutable after reading a deposit.
PREREG = os.path.join(r"C:\Users\maurice\Desktop\spasticity_paper\paper",
                      "PREREG_2ndbody_r229.md")


def _sha256(path):
    import hashlib
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def provenance():
    me = os.path.abspath(__file__)
    return {"script": os.path.basename(me), "script_sha256": _sha256(me),
            "script_bytes": os.path.getsize(me),
            "prereg": os.path.basename(PREREG), "prereg_sha256": _sha256(PREREG),
            "prereg_bytes": os.path.getsize(PREREG),
            "scope": "baseline forward only (defect register #534, #539)"}


def machine_sconecmd():
    """Machine-wide sconecmd count. tasklist, never `ps aux | grep` -- this is Windows."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return 999
    return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())


def cells(fam):
    out = []
    for d in sorted(glob.glob(os.path.join(RESULTS, fam + "_s*.H0914M.*"))):
        if not os.path.isdir(d):
            continue
        m = re.match(r"^" + fam + r"_s(\d+)\.", os.path.basename(d))
        if m:
            out.append((int(m.group(1)), d))
    return sorted(out)


def assert_field_convention():
    """Field 3 is best_fitness, field 2 is median. Verified against history.txt.

    For each probe cell, generation 0's .par filename must carry history.txt's
    generation-0 best_fitness in FIELD 3 and median_fitness in FIELD 2.
    """
    checked = 0
    for fam in FAMILIES:
        for seed, d in cells(fam)[:1]:
            h = os.path.join(d, "history.txt")
            if not os.path.exists(h):
                continue
            rows = io.open(h, encoding="utf-8", errors="replace").read().splitlines()
            if len(rows) < 2:
                continue
            f = rows[1].split("\t")
            best, med = float(f[1]), float(f[2])
            g0 = [x for x in os.listdir(d) if PAR_RE.match(x) and
                  int(PAR_RE.match(x).group(1)) == 0]
            if not g0:
                continue
            m = PAR_RE.match(g0[0])
            f2, f3 = float(m.group(2)), float(m.group(3))
            if abs(f3 - best) > 1e-2 or abs(f2 - med) > 1e-1:
                raise SystemExit(
                    "FIELD CONVENTION VIOLATED in %s: file %s gives f2=%.4f f3=%.4f but "
                    "history.txt gen 0 gives best=%.5f median=%.5f"
                    % (os.path.basename(d), g0[0], f2, f3, best, med))
            checked += 1
    if checked < 6:
        raise SystemExit("field convention checked on only %d cells -- too few" % checked)
    print("field convention asserted on %d cells: field3=best, field2=median" % checked)
    return True


def best_par(d):
    """Lowest FIELD-3 (best fitness) .par. Returns (path, best_fitness, generation)."""
    best = None
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if not m:
            continue                      # excludes ResultH0914Gait10.par
        fit = float(m.group(3))           # FIELD 3
        if best is None or fit < best[1]:
            best = (os.path.join(d, f), fit, int(m.group(1)))
    return best


def sto_ok(par):
    p = par + ".sto"
    return os.path.exists(p) and os.path.getsize(p) > 0


def main():
    assert_field_convention()

    ledger = []
    if os.path.exists(LEDGER):
        ledger = json.load(io.open(LEDGER, encoding="utf-8"))["attempts"]

    queue, skipped = [], []
    for fam in FAMILIES:
        for seed, d in cells(fam):
            b = best_par(d)
            if b is None:
                skipped.append((fam, seed, "no conforming .par"))
                continue
            par, fit, gen = b
            if fit >= FIT_GATE:
                skipped.append((fam, seed, "gate A: best fitness %.3f" % fit))
                continue
            if sto_ok(par):
                skipped.append((fam, seed, "already has .sto -- re-run forbidden (#205)"))
                continue
            queue.append((fam, seed, d, par, fit, gen))

    print("admitted and queued : %d" % len(queue))
    print("skipped             : %d" % len(skipped))
    for s in skipped[:10]:
        print("   skip %-14s s%-4s %s" % s)
    if len(skipped) > 10:
        print("   ... and %d more" % (len(skipped) - 10))

    n0 = machine_sconecmd()
    print("machine-wide sconecmd before start: %d" % n0)
    if n0 > 0:
        print("NOT STARTING -- the user's study appears to be running. Our cells give way.")
        return 2

    live, t0 = [], time.time()
    for (fam, seed, d, par, fit, gen) in queue:
        while len([p for p in live if p[0].poll() is None]) >= MAX_OURS \
                or machine_sconecmd() >= MACHINE_CAP:
            time.sleep(0.2)
        p = subprocess.Popen([SCONECMD, "-e", os.path.basename(par)], cwd=d,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        live.append((p, fam, seed, par))
    for p in live:
        p[0].wait()

    ok = 0
    for (fam, seed, d, par, fit, gen) in queue:
        good = sto_ok(par)
        ok += good
        ledger.append({"family": fam, "seed": seed, "par": os.path.basename(par),
                       "best_fitness_field3": fit, "generation": gen,
                       "outcome": "ok" if good else "E5_STO_0",
                       "sto_bytes": os.path.getsize(par + ".sto") if good else 0,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    json.dump({"provenance": provenance(), "note": "every attempt including failures (#205); field3=best_fitness",
               "fit_gate": FIT_GATE, "attempts": ledger},
              io.open(LEDGER, "w", encoding="utf-8"), indent=1)
    print("\nreplayed ok %d / %d in %.1f s" % (ok, len(queue), time.time() - t0))
    print("wrote %s" % LEDGER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
