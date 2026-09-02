"""run_bandfill_r291.py -- launcher for PREREG_bandfill_r291.md rev 2 (0b2b7274...).

TWO SIDES, section 3:
  SPASTIC   KV 0.035 and KV 0.070, seeds 101-106, 12 cells -- this is what closes GAP 2.
            SpasticL block byte-identical to R151S except KV. No Fmax altered.
  WEAKNESS  plantarflexor weakness f = 0.05, 0.07, 0.08, seeds 152 upward, continuing r287.
            max_isometric_force scaled on soleus_l AND gastroc_l. No controller change.

Run order: the 12 spastic cells first, then the weakness sampling in seed order.

STOPPING RULE, section 4: stop when the in-band count reaches EIGHT weakness cells AND at
least THREE spastic conditions are represented in band, or when 60 cells of this arm have
run, whichever comes first.

  THE RULE READS t_end AND THE KV / f LABEL ONLY. It never computes knee_angle_LmR, and the
  endpoint is not computed until the arm has stopped.

Resolver: best_par_by_generation -- selecting by the objective in the filename is unsafe for
any arm whose warm start was optimised under a different objective or lesion (r302).
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

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC_C = os.path.join(ROOT, "reopt_r151", "R151C_s101")
SRC_S = os.path.join(ROOT, "reopt_r151", "R151S_s101")
STAGE = os.path.join(ROOT, "bandfill_r291")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

PF = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
BAND = (13.58, 17.85)
GUARD_T1 = 9.73
MAX_CELLS = 60
TARGET_WEAK_IN_BAND = 8
TARGET_SPASTIC_CONDITIONS = 3
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def cells():
    out = []
    for tag, kv in (("0035", 0.035), ("0070", 0.070)):
        for seed in range(101, 107):
            out.append({"kind": "spastic", "tag": tag, "kv": kv, "seed": seed,
                        "prefix": "R291KV%s_s%d" % (tag, seed)})
    for seed in range(152, 200):
        for tag, f in (("005", 0.05), ("007", 0.07), ("008", 0.08)):
            out.append({"kind": "weak", "tag": tag, "f": f, "scale": 1.0 - f, "seed": seed,
                        "prefix": "R291BF%s_s%d" % (tag, seed)})
    return out[:MAX_CELLS]


def stage_one(c):
    d = os.path.join(STAGE, c["prefix"])
    if os.path.exists(os.path.join(d, "config.scone")):
        return d
    src = SRC_S if c["kind"] == "spastic" else SRC_C
    for sub in ("models", "data", "par"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copyfile(os.path.join(src, "InitStateH0918Gait10ActA.zml"),
                    os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
    warm = "H1922v7b3-TSG3Dv8g-989_fixed2.par"
    shutil.copyfile(os.path.join(src, "par", warm), os.path.join(d, "par", warm))

    hfd = io.open(os.path.join(src, "H1922v7b3.hfd"), encoding="utf-8").read()
    if c["kind"] == "weak":
        n = 0
        for m, base in PF.items():
            pat = re.compile(r"(name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*)([0-9.]+)",
                             re.S)
            new = "%.6g" % (base * c["scale"])
            hfd, k = pat.subn(lambda g: g.group(1) + new, hfd, count=1)
            n += k
        assert n == 2, "expected 2 Fmax substitutions, made %d" % n
    io.open(os.path.join(d, "models", "H1922v7b3.hfd"), "w",
            encoding="utf-8", newline="\n").write(hfd)

    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    tib = float(re.search(r"name\s*=\s*tib_ant_l\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                          chk, re.S).group(1))
    assert abs(tib - 1759.0) < 1e-9, "tib_ant_l must remain 1759, found %s" % tib
    for m, base in PF.items():
        v = float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                            chk, re.S).group(1))
        want = base * (c["scale"] if c["kind"] == "weak" else 1.0)
        assert abs(v - want) < 1e-6, "%s wanted %s wrote %s" % (m, want, v)

    cfg = io.open(os.path.join(src, "config.scone"), encoding="utf-8").read()
    if c["kind"] == "spastic":
        cfg, nkv = re.subn(r"KV\s*=\s*0\.050", "KV = %g" % c["kv"], cfg)
        assert nkv == 2, "expected 2 KV substitutions, made %d" % nkv
    cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, count=1)
    cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                 cfg, count=1)
    io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="\n").write(cfg)
    return d


def competing():
    try:
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, text=True, timeout=30).stdout
        return sum(1 for ln in o.splitlines() if "sconecmd" in ln.lower())
    except Exception:
        return -1


def best_par_by_generation(cd, warm=None):
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) != (warm or "")]
    if not pars:
        return None
    return max(pars, key=lambda p: int(os.path.basename(p).split("_")[0]))


def t_end_of(cd):
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
    return float(list(S.col(cols, dat, "time"))[-1])


def coverage():
    """In-band weakness count and the set of spastic conditions represented in band."""
    weak, spast = 0, set()
    for pat, kind in (("RUN_WEAKPF_r276_cell*.json", "weak"),
                      ("RUN_BANDFILL_r285_cell*.json", "weak"),
                      ("RUN_BANDFILL_r287_cell*.json", "weak"),
                      ("RUN_BANDFILL_r291_cell*.json", None)):
        for p in sorted(glob.glob(os.path.join(PAPER, pat))):
            d = json.load(io.open(p, encoding="utf-8"))
            te = d.get("t_end_s")
            if te is None or te < GUARD_T1 or not (BAND[0] <= te <= BAND[1]):
                continue
            k = kind or d.get("kind")
            if k == "spastic":
                spast.add(str(d.get("kv")))
            else:
                weak += 1
    spast.add("0.05")           # R151S KV 0.050, all six cells in band
    return weak, spast



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
    argparse.ArgumentParser().parse_args()
    os.makedirs(STAGE, exist_ok=True)
    w0, s0 = coverage()
    print("coverage before: weakness in band %d/%d, spastic conditions in band %d/%d %s"
          % (w0, TARGET_WEAK_IN_BAND, len(s0), TARGET_SPASTIC_CONDITIONS, sorted(s0)),
          flush=True)

    for i, c in enumerate(cells()):
        f = os.path.join(PAPER, "RUN_BANDFILL_r291_cell%02d.json" % i)
        if os.path.exists(f):
            continue
        d = stage_one(c)
        n = competing()
        if n > 0:
            print("YIELD: %d sconecmd running. Suspending." % n, flush=True)
            return
        before = set(os.listdir(RES))
        t0 = time.time()
        p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                           capture_output=True, text=True, cwd=d)
        wall = time.time() - t0
        new = sorted(set(os.listdir(RES)) - before)
        for nd in new:
            assert not PROTECTED.match(nd), "refusing: protected " + nd
        rec = {"cell": i, "prefix": c["prefix"], "kind": c["kind"], "seed": c["seed"],
               "kv": c.get("kv"), "f": c.get("f"), "scale": c.get("scale"),
               "wall_clock_s": wall, "returncode": p.returncode, "new_result_dirs": new}
        if new:
            cd = os.path.join(RES, new[0])
            rec["result_dir"] = new[0]
            bp = best_par_by_generation(cd, "H1922v7b3-TSG3Dv8g-989_fixed2.par")
            rec["resolved_par"] = os.path.basename(bp) if bp else None
            if bp and not glob.glob(os.path.join(cd, "*.par.sto")):
                subprocess.run([SCONE, "-e", os.path.basename(bp)], cwd=cd,
                               capture_output=True, timeout=900)
            rec["t_end_s"] = t_end_of(cd)
            te = rec["t_end_s"]
            rec["in_band"] = bool(te is not None and te >= GUARD_T1
                                  and BAND[0] <= te <= BAND[1])
        io.open(f, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
        print("cell %02d %-16s %-8s wall %6.1f s  t_end %8s  in_band %s"
              % (i, c["prefix"], c["kind"], wall,
                 ("%.3f" % rec["t_end_s"]) if rec.get("t_end_s") is not None else "-",
                 rec.get("in_band")), flush=True)
        w, s = coverage()
        if w >= TARGET_WEAK_IN_BAND and len(s) >= TARGET_SPASTIC_CONDITIONS:
            print("\nSTOP: weakness in band %d, spastic conditions %s -- coverage met"
                  % (w, sorted(s)), flush=True)
            write_terminal("r291", sum(1 for _ in glob.glob(os.path.join(PAPER, "RUN_BANDFILL_r291_cell*.json"))), 60, "REGISTERED STOP")
            return
    print("\nSTOP: %d cells run; coverage %s -- cap reached" % (MAX_CELLS, str(coverage())),
          flush=True)
    w, sp = coverage()
    write_terminal("r291", len(glob.glob(os.path.join(PAPER, "RUN_BANDFILL_r291_cell*.json"))),
                   MAX_CELLS, "REGISTERED STOP -- 60-cell cap",
                   {"weakness_in_band": w, "spastic_conditions_in_band": sorted(sp),
                    "first_clause_unreachable": len(sp) < TARGET_SPASTIC_CONDITIONS})


if __name__ == "__main__":
    main()
