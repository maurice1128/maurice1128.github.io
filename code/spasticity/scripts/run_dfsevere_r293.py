"""run_dfsevere_r293.py -- launcher for PREREG_dfsevere_r293.md (d4631d00...).

DURATION PROBE: max_isometric_force scaled on tib_ant_l ALONE (dorsiflexor), left, four
severities x0.50 x0.30 x0.10 x0.00, six seeds each = 24 cells.

ENDPOINT IS t_end. NO JOINT CHANNEL IS COMPUTED HERE.

RESOLVER FIX (r302): best_par selects by HIGHEST GENERATION among the run's own outputs, and
excludes the staged warm-start file by name. Selecting by the objective encoded in the
filename is UNSAFE whenever the warm start was optimised under a different objective or a
different lesion -- it can score lower than every genuine result and be picked as "best".
That defect corrupted both r294 deposits.

SCOPE OF THE CLEARANCE, ENFORCED IN CODE:
  * writes ONLY into a new staging tree under spasticity_paper, and SCONE writes ONLY new
    directories under SCONE\\results;
  * the 112 protected directories and every existing cell are never opened for write;
  * YIELD: before each cell, count sconecmd processes. If any is running that is not ours,
    suspend and report rather than compete.

Usage:  python run_weakpf_r276.py --stage        build the scenarios, run nothing
        python run_weakpf_r276.py --cell N       run one cell (0-based) and deposit
        python run_weakpf_r276.py --rest         run the remaining cells in order
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC = os.path.join(ROOT, "reopt_r151", "R151C_s101")          # unlesioned reference cell
STAGE = os.path.join(ROOT, "dfsevere_r293")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

FMAX = {"tib_ant_l": 1759.0}
DOSES = [("s050", 0.50), ("s030", 0.30), ("s010", 0.10), ("s000", 0.00)]
SEEDS = list(range(101, 107))
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def cells():
    out = []
    for tag, f in DOSES:
        for s in SEEDS:
            out.append({"tag": tag, "f": f, "scale": f, "seed": s,
                        "prefix": "R293DF%s_s%d" % (tag, s)})
    return out


def scale_hfd(src, dst, scale):
    """Scale tib_ant_l only. The plantarflexors must remain at base."""
    txt = io.open(src, encoding="utf-8").read()
    n = 0
    for m, base in FMAX.items():
        pat = re.compile(r"(name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*)([0-9.]+)",
                         re.S)
        new = "%.6g" % (base * scale)
        txt, k = pat.subn(lambda g: g.group(1) + new, txt, count=1)
        n += k
    assert n == 1, "expected 1 substitution, made %d" % n
    io.open(dst, "w", encoding="utf-8", newline="\n").write(txt)

    chk = io.open(dst, encoding="utf-8").read()
    got = float(re.search(r"name\s*=\s*tib_ant_l\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                          chk, re.S).group(1))
    want = 1759.0 * scale
    assert abs(got - want) < 1e-6, "tib_ant_l wanted %s, wrote %s" % (want, got)
    for m, base in (("soleus_l", 3549.0), ("gastroc_l", 2241.0)):
        v = float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                            chk, re.S).group(1))
        assert abs(v - base) < 1e-9, "%s must remain %s, found %s" % (m, base, v)

def stage():
    os.makedirs(STAGE, exist_ok=True)
    for c in cells():
        d = os.path.join(STAGE, c["prefix"])
        os.makedirs(os.path.join(d, "models"), exist_ok=True)
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        os.makedirs(os.path.join(d, "par"), exist_ok=True)
        scale_hfd(os.path.join(SRC, "H1922v7b3.hfd"),
                  os.path.join(d, "models", "H1922v7b3.hfd"), c["scale"])
        shutil.copyfile(os.path.join(SRC, "InitStateH0918Gait10ActA.zml"),
                        os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
        shutil.copyfile(os.path.join(SRC, "par", "H1922v7b3-TSG3Dv8g-989_fixed2.par"),
                        os.path.join(d, "par", "H1922v7b3-TSG3Dv8g-989_fixed2.par"))
        cfg = io.open(os.path.join(SRC, "config.scone"), encoding="utf-8").read()
        cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, count=1)
        cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                     cfg, count=1)
        io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8",
                newline="\n").write(cfg)
    print("staged %d cells under %s" % (len(cells()), STAGE))


def competing():
    """sconecmd processes not started by us."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return -1
    return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())


def existing_dirs():
    return set(os.listdir(RES))


def run_cell(i):
    c = cells()[i]
    d = os.path.join(STAGE, c["prefix"])
    assert os.path.isdir(d), "not staged: " + d

    n = competing()
    if n > 0:
        print("YIELD: %d sconecmd process(es) already running. Suspending, not competing." % n)
        return {"cell": i, "prefix": c["prefix"], "status": "YIELDED", "competing": n}

    before = existing_dirs()
    t0 = time.time()
    p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                       capture_output=True, text=True, cwd=d)
    wall = time.time() - t0
    after = existing_dirs()
    new = sorted(after - before)
    # never touch anything protected or pre-existing
    for nd in new:
        assert not PROTECTED.match(nd), "refusing: protected name created " + nd

    rec = {"cell": i, "prefix": c["prefix"], "f": c["f"], "scale": c["scale"],
           "seed": c["seed"], "wall_clock_s": wall, "returncode": p.returncode,
           "new_result_dirs": new,
           "stdout_tail": (p.stdout or "")[-400:], "stderr_tail": (p.stderr or "")[-400:]}
    if not new:
        rec["status"] = "NO_OUTPUT_DIR"
    else:
        rec["status"] = "OK" if p.returncode == 0 else "NONZERO_EXIT"
        rec.update(harvest(os.path.join(RES, new[0])))
    io.open(os.path.join(PAPER, "RUN_DFSEVERE_r293_cell%02d.json" % i), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    return rec


def best_par_by_generation(cd, warm_basename=None):
    """Highest generation among the run's own .par outputs, excluding the staged warm start.

    r302: selecting by the filename's objective field is unsafe when the warm start was
    optimised under a different objective -- it can be the numeric minimum in the directory
    and get picked as the run's result. Generation is monotone in SCONE's output and is not
    comparable across objectives, so it is the safe key.
    """
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) != (warm_basename or "")]
    if not pars:
        return None
    return max(pars, key=lambda p: int(os.path.basename(p).split("_")[0]))


def harvest(cd):
    """Per-cell deposit required by PREREG section 5."""
    out = {"result_dir": os.path.basename(cd)}
    h = os.path.join(cd, "history.txt")
    if os.path.exists(h):
        rows = []
        with io.open(h, encoding="utf-8", errors="replace") as f:
            hdr = f.readline().rstrip("\n").split("\t")
            gi, bi = hdr.index("generation"), hdr.index("best_fitness")
            pi = hdr.index("fitness_progress") if "fitness_progress" in hdr else None
            for ln in f:
                cc = ln.rstrip("\n").split("\t")
                if len(cc) > bi:
                    rows.append((int(float(cc[gi])), float(cc[bi]),
                                 float(cc[pi]) if pi is not None and len(cc) > pi else None))
        if rows:
            run, m = [], float("inf")
            for g, bf, _ in rows:
                m = min(m, bf)
                run.append((g, m))
            at10 = [v for g, v in run if g <= run[-1][0] - 10]
            out["terminal_objective"] = run[-1][1]
            out["objective_gen0"] = run[0][1]
            out["descent_final_10_gens"] = (at10[-1] - run[-1][1]) if at10 else 0.0
            out["terminal_fitness_progress"] = rows[-1][2]
            out["n_generations"] = len(rows)
    pars = sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
    if pars:
        def key(p):
            b = os.path.basename(p).split("_")
            return (float(b[2].replace(".par", "")), -int(b[0]))
        best = min(pars, key=key)
        ties = [os.path.basename(p) for p in pars
                if abs(key(p)[0] - key(best)[0]) < 1e-12]
        out["resolved_par"] = os.path.basename(best)
        out["tie_break"] = ("highest generation among %d tied files" % len(ties)
                            if len(ties) > 1 else "unique minimum")
        out["tied_files"] = ties if len(ties) > 1 else []
    return out



def write_terminal(arm, n_ran, n_registered, stop_reason, extra=None):
    """r305. Absence of this file means the launcher did not reach its own exit."""
    import datetime
    rec = {"arm": arm, "cells_run": n_ran, "cells_registered": n_registered,
           "complete": bool(n_ran >= n_registered),
           "stop_reason": stop_reason,
           "written_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "note": ("A partially-run arm leaves valid deposits and a consistent results tree; "
                    "only the absence of a live process reveals it. This file is the explicit "
                    "signal. If it is missing, the launcher was interrupted.")}
    if extra:
        rec.update(extra)
    p = os.path.join(PAPER, "TERMINAL_%s.json" % arm)
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    print("TERMINAL: %s cells_run=%d of %d  stop=%s" % (arm, n_ran, n_registered, stop_reason))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--rest", action="store_true")
    a = ap.parse_args()
    if a.stage:
        stage()
        return
    if a.cell is not None:
        r = run_cell(a.cell)
        print(json.dumps({k: v for k, v in r.items() if k not in
                          ("stdout_tail", "stderr_tail")}, indent=1))
        return
    if a.rest:
        for i in range(len(cells())):
            f = os.path.join(PAPER, "RUN_DFSEVERE_r293_cell%02d.json" % i)
            if os.path.exists(f):
                continue
            r = run_cell(i)
            print("cell %02d %-18s %-14s wall %.1f s  obj %s"
                  % (i, r["prefix"], r["status"], r.get("wall_clock_s", 0),
                     r.get("terminal_objective")))
            sys.stdout.flush()
            if r["status"] == "YIELDED":
                print("stopping: yielded to the user's own work")
                write_terminal("r293",
                               len(glob.glob(os.path.join(PAPER,
                                                          "RUN_DFSEVERE_r293_cell*.json"))),
                               len(cells()), "YIELDED to another sconecmd")
                return
        write_terminal("r293",
                       len(glob.glob(os.path.join(PAPER, "RUN_DFSEVERE_r293_cell*.json"))),
                       len(cells()), "REGISTERED STOP -- all cells run")


if __name__ == "__main__":
    main()
