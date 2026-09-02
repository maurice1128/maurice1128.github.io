"""run_adapt_r390.py -- launcher for PREREG_adaptation_r390.md
(9664b8edbe2f3232bcd3f2dc4ad07f81897b9143c8436b226a703a42d23b8334).

ADAPTATION-TIME SWEEP. Every cell in this corpus so far gave CMA-ES a full run with the
lesion in place -- a fully compensated nervous system. Generations of CMA-ES stand in for
adaptation time: 1 generation is the acute state, 91 is the chronic state already measured.

  two lesions x five adaptation budgets x six seeds = 60 cells
  SPASTIC  -- the SpasticL ConditionalController (soleus + gastroc, left, delay 0.020,
              KV 0.050, allow_neg_V 0).  The block is EXTRACTED BYTE-FOR-BYTE from an
              existing R203*S cell by prefix/suffix diff against the base cell; it is
              never retyped.  See spastic_insert().
  DFWEAK   -- H1922v7b3.hfd with tib_ant_l max_isometric_force 1759 -> 1407.2 (x0.80),
              soleus_l 3549 and gastroc_l 2241 asserted unchanged.  scale_hfd() is taken
              verbatim from run_dfsevere_r293.py.
  BUDGETS  -- the CmaOptimizer key is `max_generations`.  In the base cell R151C_s101 its
              value is 90, which yields 90 rows in history.txt (generations 0..89).  The
              registration names the budgets {1, 5, 15, 40, 91} and this launcher writes
              those literal values.  NOTE FOR THE READER: g091 therefore runs ONE
              generation more than the existing chronic corpus (which used 90).

BASE CELL: scone\\probe3d_r141\\reopt_r151\\R151C_s101 -- the matched unlesioned control,
min_velocity 1.0, no SpasticL, tib_ant_l 1759.  Verified in verify_base() at stage time.

ENDPOINT of the registration is a kinematic gap computed later by a separate analyser.
This launcher deposits the run record plus t_end, which requires a replay: sconecmd -e on
the best par is an EVALUATION of an already-produced parameter set, not an optimisation.

SCOPE OF THE CLEARANCE, ENFORCED IN CODE:
  * writes ONLY into a new staging tree under spasticity_paper, and SCONE writes ONLY new
    directories under SCONE\\results;
  * the 112 protected directories and every existing cell are never opened for write;
  * YIELD: before each cell, count sconecmd processes. If any is running that is not ours,
    suspend and report rather than compete.

Usage:  python run_adapt_r390.py --stage        build the 60 scenarios, run nothing
        python run_adapt_r390.py --probe        run ONLY R390ADAPTSg005_s101, deposit
                                                paper\\ADAPT_PROBE_r390.json
        python run_adapt_r390.py --cell N       run one cell (0-based) and deposit
        python run_adapt_r390.py --rest         run the remaining cells in order
"""
import argparse
import glob
import hashlib
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
DONOR = os.path.join(ROOT, "speed_r203", "R203V105S_s101")    # SpasticL block donor
STAGE = os.path.join(ROOT, "adapt_r390")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

WARM = "H1922v7b3-TSG3Dv8g-989_fixed2.par"
FMAX = {"tib_ant_l": 1759.0}
LESIONS = [("S", "SPASTIC", 1.00), ("W", "DFWEAK", 0.80)]
BUDGETS = [("001", 1), ("005", 5), ("015", 15), ("040", 40), ("091", 91)]
SEEDS = list(range(101, 107))
PROBE_PREFIX = "R390ADAPTSg005_s101"
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def cells():
    out = []
    for lz, lname, scale in LESIONS:
        for gtag, g in BUDGETS:
            for s in SEEDS:
                out.append({"lesion": lz, "lesion_name": lname, "scale": scale,
                            "gtag": gtag, "max_generations": g, "seed": s,
                            "prefix": "R390ADAPT%sg%s_s%d" % (lz, gtag, s)})
    return out


def probe_index():
    for i, c in enumerate(cells()):
        if c["prefix"] == PROBE_PREFIX:
            return i
    raise AssertionError("probe cell %s is not in the cell list" % PROBE_PREFIX)


def rd(p):
    return io.open(p, encoding="utf-8").read()


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


# --------------------------------------------------------------------------- base checks
def verify_base():
    """The base cell must be the matched unlesioned control before anything is staged."""
    cfg = rd(os.path.join(SRC, "config.scone"))
    hfd = rd(os.path.join(SRC, "H1922v7b3.hfd"))
    out = {"src": SRC}
    assert "SpasticL" not in cfg, "base cell already carries a SpasticL controller"
    out["spasticL_absent"] = True
    mv = re.search(r"min_velocity\s*=\s*([0-9.]+)", cfg)
    assert mv and abs(float(mv.group(1)) - 1.0) < 1e-12, \
        "base min_velocity must be 1.0, found %s" % (mv and mv.group(1))
    out["min_velocity"] = float(mv.group(1))
    mg = re.search(r"max_generations\s*=\s*(\d+)", cfg)
    assert mg, "base config has no max_generations key"
    out["max_generations_original"] = int(mg.group(1))
    for m, base in (("tib_ant_l", 1759.0), ("soleus_l", 3549.0), ("gastroc_l", 2241.0)):
        v = float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                            hfd, re.S).group(1))
        assert abs(v - base) < 1e-9, "base %s must be %s, found %s" % (m, base, v)
        out[m] = v
    for f in ("config.scone", "H1922v7b3.hfd", "InitStateH0918Gait10ActA.zml",
              os.path.join("par", WARM)):
        assert os.path.exists(os.path.join(SRC, f)), "base cell is missing " + f
    out["sha256_config"] = sha(os.path.join(SRC, "config.scone"))
    out["sha256_hfd"] = sha(os.path.join(SRC, "H1922v7b3.hfd"))
    return out


# ------------------------------------------------------- SpasticL: extracted, not retyped
def spastic_insert():
    """Recover the SpasticL block from the donor cell as a literal byte range.

    The donor R203V105S_s101 differs from the base R151C_s101 in exactly three places:
    signature_prefix, min_velocity, and the inserted SpasticL ConditionalController.  The
    first two are scalars and are normalised away here; what is left is the block, which is
    then lifted out by longest-common-prefix / longest-common-suffix.  Nothing about the
    controller is typed into this file, and the round-trip assertion below proves it: the
    base with the extracted text spliced back in must equal the normalised donor byte for
    byte.
    """
    base = rd(os.path.join(SRC, "config.scone"))
    don = rd(os.path.join(DONOR, "config.scone"))
    base_sig = re.search(r"signature_prefix\s*=\s*(\S+)", base).group(1)
    don_n = re.sub(r"signature_prefix\s*=\s*\S+",
                   "signature_prefix = %s" % base_sig, don, count=1)
    don_n = re.sub(r"min_velocity\s*=\s*[0-9.]+", "min_velocity = 1.0", don_n, count=1)
    assert "SpasticL" not in base and "SpasticL" in don_n
    assert len(don_n) > len(base)

    p = 0
    while p < len(base) and base[p] == don_n[p]:
        p += 1
    s = 0
    while s < len(base) - p and base[len(base) - 1 - s] == don_n[len(don_n) - 1 - s]:
        s += 1
    old = base[p:len(base) - s]
    new = don_n[p:len(don_n) - s]

    assert old.strip(" \t\r\n") == "", \
        "the diff removes non-layout text from the base: %r" % old[:200]
    for tok in ("ConditionalController", "legs = left", "name = SpasticL",
                "target = soleus", "target = gastroc",
                "delay = 0.020", "KV = 0.050", "allow_neg_V = 0"):
        assert tok in new, "extracted block is missing %r" % tok
    assert new.count("MuscleReflex") == 2, \
        "expected exactly 2 MuscleReflex in the block, found %d" % new.count("MuscleReflex")
    assert base[:p] + new + base[len(base) - s:] == don_n, \
        "round trip failed: the extracted block does not reconstruct the donor"
    return p, s, new


def apply_spastic(cfg, p, s, new):
    """Splice the extracted block into a config that is still byte-identical to the base."""
    assert "SpasticL" not in cfg
    return cfg[:p] + new + cfg[len(cfg) - s:]


# ----------------------------------------------------------- hfd scaling (from r293, kept)
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
    return got


# ------------------------------------------------------------------------------- staging
def stage():
    assert os.path.commonprefix([os.path.abspath(STAGE),
                                 r"C:\Users\maurice\Desktop\spasticity_paper"]) \
        == r"C:\Users\maurice\Desktop\spasticity_paper", "staging escapes the clearance"
    base_rec = verify_base()
    p, s, block = spastic_insert()
    base_cfg = rd(os.path.join(SRC, "config.scone"))

    os.makedirs(STAGE, exist_ok=True)
    rows = []
    for c in cells():
        d = os.path.join(STAGE, c["prefix"])
        os.makedirs(os.path.join(d, "models"), exist_ok=True)
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        os.makedirs(os.path.join(d, "par"), exist_ok=True)

        f_tib = scale_hfd(os.path.join(SRC, "H1922v7b3.hfd"),
                          os.path.join(d, "models", "H1922v7b3.hfd"), c["scale"])
        shutil.copyfile(os.path.join(SRC, "InitStateH0918Gait10ActA.zml"),
                        os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
        shutil.copyfile(os.path.join(SRC, "par", WARM), os.path.join(d, "par", WARM))

        cfg = base_cfg
        if c["lesion"] == "S":
            cfg = apply_spastic(cfg, p, s, block)
        cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, count=1)
        cfg = re.sub(r"max_generations\s*=\s*\d+",
                     "max_generations = %d" % c["max_generations"], cfg, count=1)
        cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                     cfg, count=1)
        cp = os.path.join(d, "config.scone")
        io.open(cp, "w", encoding="utf-8", newline="\n").write(cfg)

        # read back from disk -- never trust the in-memory string
        w = rd(cp)
        got_g = int(re.search(r"max_generations\s*=\s*(\d+)", w).group(1))
        got_seed = int(re.search(r"random_seed\s*=\s*(\d+)", w).group(1))
        got_sig = re.search(r"signature_prefix\s*=\s*(\S+)", w).group(1)
        got_mv = float(re.search(r"min_velocity\s*=\s*([0-9.]+)", w).group(1))
        assert got_g == c["max_generations"], "%s max_generations %s" % (c["prefix"], got_g)
        assert got_seed == c["seed"]
        assert got_sig == c["prefix"]
        assert abs(got_mv - 1.0) < 1e-12, "min_velocity drifted to %s" % got_mv
        has_sp = "SpasticL" in w
        assert has_sp == (c["lesion"] == "S"), "%s SpasticL=%s" % (c["prefix"], has_sp)
        if has_sp:
            for tok in ("legs = left", "delay = 0.020", "KV = 0.050", "allow_neg_V = 0"):
                assert tok in w, "%s lost %r" % (c["prefix"], tok)
        want_f = 1759.0 * c["scale"]
        assert abs(f_tib - want_f) < 1e-6

        rows.append({"cell": len(rows), "prefix": c["prefix"], "lesion": c["lesion_name"],
                     "gtag": c["gtag"], "seed": c["seed"],
                     "max_generations_written": got_g, "random_seed_written": got_seed,
                     "signature_prefix_written": got_sig, "min_velocity": got_mv,
                     "spasticL_present": has_sp,
                     "tib_ant_l_force": f_tib, "hfd_scale": c["scale"],
                     "sha256_config": sha(cp),
                     "sha256_hfd": sha(os.path.join(d, "models", "H1922v7b3.hfd"))})

    man = {"arm": "r390", "prereg": "PREREG_adaptation_r390.md",
           "prereg_sha256": "9664b8edbe2f3232bcd3f2dc4ad07f81897b9143c8436b226a703a42d23b8334",
           "stage_dir": STAGE, "n_cells": len(rows),
           "base_cell": base_rec, "donor_cell": DONOR,
           "donor_sha256_config": sha(os.path.join(DONOR, "config.scone")),
           "budget_key": "max_generations",
           "budget_key_original_value": base_rec["max_generations_original"],
           "budget_key_note": ("The base cell R151C_s101 carries max_generations = 90, which "
                               "produces 90 rows in history.txt (generations 0..89). The "
                               "registration names the budgets {1,5,15,40,91} and those "
                               "literal values are written here, so the g091 arm runs one "
                               "generation more than the existing chronic corpus."),
           "budgets": [g for _, g in BUDGETS],
           "spasticL_provenance": ("extracted as a literal byte range from "
                                   "R203V105S_s101/config.scone by longest-common-prefix / "
                                   "longest-common-suffix against the base config, with a "
                                   "round-trip assertion that the splice reproduces the "
                                   "donor byte for byte; not retyped"),
           "spasticL_block_bytes": len(block),
           "spasticL_block_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
           "spasticL_block": block,
           "probe_cell_index": probe_index(), "probe_cell_prefix": PROBE_PREFIX,
           "cells": rows}
    mp = os.path.join(PAPER, "ADAPT_STAGE_r390.json")
    io.open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(man, indent=1) + "\n")
    print("staged %d cells under %s" % (len(rows), STAGE))
    print("budget key = max_generations (base value %d) -> %s"
          % (base_rec["max_generations_original"], [g for _, g in BUDGETS]))
    print("manifest -> %s" % mp)
    for _, g in BUDGETS:
        ex = [r for r in rows if r["max_generations_written"] == g][0]
        print("  budget %3d verified in %s (read back %d)"
              % (g, ex["prefix"], ex["max_generations_written"]))


# ---------------------------------------------------------------------------- run / yield
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
            out["last_generation"] = run[-1][0]
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
    bp = best_par_by_generation(cd, WARM)
    out["par_by_generation"] = os.path.basename(bp) if bp else None
    return out


def replay_t_end(cd):
    """sconecmd -e on the highest-generation par. An EVALUATION, not an optimisation."""
    bp = best_par_by_generation(cd, WARM)
    if not bp:
        return {"t_end_s": None, "replay": "no par produced"}
    sto = bp + ".sto"
    t0 = time.time()
    if not os.path.exists(sto):
        try:
            subprocess.run([SCONE, "-e", bp], cwd=cd, capture_output=True, timeout=900)
        except Exception as e:
            return {"t_end_s": None, "replay": "failed: %s" % e}
    if not os.path.exists(sto):
        cand = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
        if not cand:
            return {"t_end_s": None, "replay": "no .par.sto after -e"}
        sto = cand[-1]
    last = None
    with io.open(sto, encoding="utf-8", errors="replace") as f:
        hdr_done = False
        ti = 0
        for ln in f:
            if not hdr_done:
                if ln.strip().lower() == "endheader":
                    hdr_done = True
                    continue
                continue
            cc = ln.rstrip("\n").split("\t")
            if not hdr_done or not cc or cc[0] == "":
                continue
            if cc[0].strip().lower() == "time":
                ti = 0
                continue
            try:
                last = float(cc[ti])
            except ValueError:
                continue
    return {"t_end_s": last, "replay_sto": os.path.basename(sto),
            "replay_wall_s": time.time() - t0}


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

    rec = {"cell": i, "prefix": c["prefix"], "lesion": c["lesion_name"],
           "gtag": c["gtag"], "max_generations": c["max_generations"],
           "hfd_scale": c["scale"], "seed": c["seed"],
           "wall_clock_s": wall, "returncode": p.returncode,
           "new_result_dir_appeared": bool(new), "new_result_dirs": new,
           "stdout_tail": (p.stdout or "")[-400:], "stderr_tail": (p.stderr or "")[-400:]}
    if not new:
        rec["status"] = "NO_OUTPUT_DIR"
    else:
        rec["status"] = "OK" if p.returncode == 0 else "NONZERO_EXIT"
        cd = os.path.join(RES, new[0])
        rec.update(harvest(cd))
        rec.update(replay_t_end(cd))
    rec["total_wall_clock_s"] = time.time() - t0
    io.open(os.path.join(PAPER, "RUN_ADAPT_r390_cell%02d.json" % i), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    return rec


def probe():
    i = probe_index()
    r = run_cell(i)
    rec = dict(r)
    rec["probe_of"] = PROBE_PREFIX
    rec["purpose"] = ("single timing probe: does the 60-cell arm fit inside the Hyfydy "
                      "licence window (expires 2026-08-27)?")
    io.open(os.path.join(PAPER, "ADAPT_PROBE_r390.json"), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rec.items()
                      if k not in ("stdout_tail", "stderr_tail")}, indent=1))
    return rec


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
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--rest", action="store_true")
    a = ap.parse_args()
    if a.stage:
        stage()
        return
    if a.probe:
        probe()
        return
    if a.cell is not None:
        r = run_cell(a.cell)
        print(json.dumps({k: v for k, v in r.items() if k not in
                          ("stdout_tail", "stderr_tail")}, indent=1))
        return
    if a.rest:
        for i in range(len(cells())):
            f = os.path.join(PAPER, "RUN_ADAPT_r390_cell%02d.json" % i)
            if os.path.exists(f):
                continue
            r = run_cell(i)
            print("cell %02d %-22s %-14s wall %.1f s  obj %s  t_end %s"
                  % (i, r["prefix"], r["status"], r.get("wall_clock_s", 0),
                     r.get("terminal_objective"), r.get("t_end_s")))
            sys.stdout.flush()
            if r["status"] == "YIELDED":
                print("stopping: yielded to the user's own work")
                write_terminal("r390",
                               len(glob.glob(os.path.join(PAPER,
                                                          "RUN_ADAPT_r390_cell*.json"))),
                               len(cells()), "YIELDED to another sconecmd")
                return
        write_terminal("r390",
                       len(glob.glob(os.path.join(PAPER, "RUN_ADAPT_r390_cell*.json"))),
                       len(cells()), "REGISTERED STOP -- all cells run")


if __name__ == "__main__":
    main()
