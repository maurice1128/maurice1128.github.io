"""run_weakpf_r276.py -- round 276. Launcher for PREREG_weakpf_r274.md rev 2 (9338ce8a...).

WEAK-PF: max_isometric_force scaled on soleus_l AND gastroc_l, left, three doses
(f = 0.05, 0.10, 0.20), six seeds each = 18 cells.

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
STAGE = os.path.join(ROOT, "weakpf_r276")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
DOSES = [("f005", 0.05), ("f010", 0.10), ("f020", 0.20)]
SEEDS = list(range(101, 107))
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def cells():
    out = []
    for tag, f in DOSES:
        for s in SEEDS:
            out.append({"tag": tag, "f": f, "scale": 1.0 - f, "seed": s,
                        "prefix": "R276WPF%s_s%d" % (tag[1:], s)})
    return out


def scale_hfd(src, dst, scale):
    txt = io.open(src, encoding="utf-8").read()
    n = 0
    for m, base in FMAX.items():
        pat = re.compile(r"(name\s*=\s*%s\b.*?max_isometric_force\s*=\s*)([0-9.]+)" % m, re.S)
        new = "%.6g" % (base * scale)
        txt, k = pat.subn(lambda g: g.group(1) + new, txt, count=1)
        n += k
    assert n == 2, "expected 2 substitutions, made %d" % n
    io.open(dst, "w", encoding="utf-8", newline="\n").write(txt)
    # verify by re-reading
    chk = io.open(dst, encoding="utf-8").read()
    for m, base in FMAX.items():
        v = float(re.search(r"name\s*=\s*%s\b.*?max_isometric_force\s*=\s*([0-9.]+)" % m,
                            chk, re.S).group(1))
        assert abs(v - base * scale) < 1e-6, "%s wrote %s" % (m, v)
    tib = float(re.search(r"name\s*=\s*tib_ant_l\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                          chk, re.S).group(1))
    assert abs(tib - 1759.0) < 1e-9, "tib_ant_l must remain 1759, found %s" % tib


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
    io.open(os.path.join(PAPER, "RUN_WEAKPF_r276_cell%02d.json" % i), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    return rec


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
            f = os.path.join(PAPER, "RUN_WEAKPF_r276_cell%02d.json" % i)
            if os.path.exists(f):
                continue
            r = run_cell(i)
            print("cell %02d %-18s %-14s wall %.1f s  obj %s"
                  % (i, r["prefix"], r["status"], r.get("wall_clock_s", 0),
                     r.get("terminal_objective")))
            sys.stdout.flush()
            if r["status"] == "YIELDED":
                print("stopping: yielded to the user's own work")
                return


if __name__ == "__main__":
    main()
