"""run_matched20_r289.py -- launcher for PREREG_matched20_r289.md.

Plantarflexor weakness, f = 0.07 and f = 0.08, seeds 107-151.
Run order fixed by section 4: for seed = 107..151, (f=0.07, seed) then (f=0.08, seed).

STOPPING RULE, section 5: stop when THREE in-band cells exist across the pooled
plantarflexor-weakness set, or when 45 cells of this continuation have run.

  IN-BAND means: measured under the r281 guard (t_end >= 9.73) AND t_end inside
  [13.58, 17.85].

  THE RULE READS t_end ONLY. This launcher never computes knee_angle_LmR and never opens
  a channel column. The endpoint is not computed until the arm has stopped.

Each cell is optimised, then evaluated to .sto with `sconecmd -e` so t_end can be read.
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
SRC = os.path.join(ROOT, "reopt_r151", "R151S_s101")   # spastic staging
STAGE = os.path.join(ROOT, "matched20_r289")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
BAND = (13.58, 17.85)
GUARD_T1 = 9.73
MAX_CELLS = 12
TARGET_IN_BAND = 10**9   # no early stop: run all 12
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def cells():
    out = []
    for tag, kv in (("0125", 0.0125), ("00625", 0.00625)):
        for seed in range(101, 107):
            out.append({"tag": tag, "kv": kv, "seed": seed,
                        "prefix": "R289KV%s_s%d" % (tag, seed)})
    return out[:MAX_CELLS]


def scale_hfd(src, dst, scale):
    txt = io.open(src, encoding="utf-8").read()
    n = 0
    for m, base in FMAX.items():
        pat = re.compile(r"(name\s*=\s*%s\b.*?max_isometric_force\s*=\s*)([0-9.]+)" % m, re.S)
        txt, k = pat.subn(lambda g: g.group(1) + ("%.6g" % (base * scale)), txt, count=1)
        n += k
    assert n == 2
    io.open(dst, "w", encoding="utf-8", newline="\n").write(txt)
    chk = io.open(dst, encoding="utf-8").read()
    tib = float(re.search(r"name\s*=\s*tib_ant_l\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                          chk, re.S).group(1))
    assert abs(tib - 1759.0) < 1e-9


def stage_one(c):
    d = os.path.join(STAGE, c["prefix"])
    if os.path.exists(os.path.join(d, "config.scone")):
        return d
    for sub in ("models", "data", "par"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    import shutil as _sh
    _sh.copyfile(os.path.join(SRC, "H1922v7b3.hfd"),
                 os.path.join(d, "models", "H1922v7b3.hfd"))
    shutil.copyfile(os.path.join(SRC, "InitStateH0918Gait10ActA.zml"),
                    os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
    shutil.copyfile(os.path.join(SRC, "par", "H1922v7b3-TSG3Dv8g-989_fixed2.par"),
                    os.path.join(d, "par", "H1922v7b3-TSG3Dv8g-989_fixed2.par"))
    cfg = io.open(os.path.join(SRC, "config.scone"), encoding="utf-8").read()
    cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, count=1)
    cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                 cfg, count=1)
    cfg, nkv = re.subn(r"KV\s*=\s*0\.050", "KV = %g" % c["kv"], cfg)
    assert nkv == 2, "expected 2 KV substitutions, made %d" % nkv
    io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="\n").write(cfg)
    return d


def competing():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
        return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())
    except Exception:
        return -1


def t_end_of(cd):
    """t_end ONLY. No channel column is opened."""
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
    return float(list(S.col(cols, dat, "time"))[-1])


def best_par(cd):
    pars = sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
    if not pars:
        return None
    def key(p):
        b = os.path.basename(p).split("_")
        return (float(b[2].replace(".par", "")), -int(b[0]))
    return os.path.basename(min(pars, key=key))


def pooled_in_band():
    """In-band count across the whole plantarflexor-weakness set: r274 WPF, r285 BF, r287 BF."""
    n, tags = 0, []
    for pat in ("RUN_WEAKPF_r276_cell*.json", "RUN_BANDFILL_r285_cell*.json",
                "RUN_MATCHED20_r289_cell*.json"):
        for p in sorted(glob.glob(os.path.join(PAPER, pat))):
            d = json.load(io.open(p, encoding="utf-8"))
            te = d.get("t_end_s")
            if te is None:
                rdir = d.get("result_dir")
                if rdir and os.path.isdir(os.path.join(RES, rdir)):
                    te = t_end_of(os.path.join(RES, rdir))
            if te is not None and te >= GUARD_T1 and BAND[0] <= te <= BAND[1]:
                n += 1
                tags.append((d.get("prefix"), round(te, 3)))
    return n, tags


def run_cell(i, c):
    d = stage_one(c)
    nc = competing()
    if nc > 0:
        print("YIELD: %d sconecmd running. Suspending." % nc, flush=True)
        return {"status": "YIELDED", "competing": nc}
    before = set(os.listdir(RES))
    t0 = time.time()
    p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                       capture_output=True, text=True, cwd=d)
    wall = time.time() - t0
    new = sorted(set(os.listdir(RES)) - before)
    for nd in new:
        assert not PROTECTED.match(nd), "refusing: protected name " + nd
    rec = {"cell": i, "prefix": c["prefix"],
           "seed": c["seed"], "kv": c["kv"], "wall_clock_s": wall, "returncode": p.returncode,
           "new_result_dirs": new, "status": "OK" if p.returncode == 0 else "NONZERO_EXIT"}
    if new:
        cd = os.path.join(RES, new[0])
        rec["result_dir"] = new[0]
        bp = best_par(cd)
        rec["resolved_par"] = bp
        if bp and not glob.glob(os.path.join(cd, "*.par.sto")):
            subprocess.run([SCONE, "-e", bp], cwd=cd, capture_output=True, timeout=900)
        rec["t_end_s"] = t_end_of(cd)
        te = rec["t_end_s"]
        rec["measured_under_guard"] = bool(te is not None and te >= GUARD_T1)
        rec["in_band"] = bool(te is not None and te >= GUARD_T1
                              and BAND[0] <= te <= BAND[1])
    else:
        rec["status"] = "NO_OUTPUT_DIR"
    io.open(os.path.join(PAPER, "RUN_MATCHED20_r289_cell%02d.json" % i), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rest", action="store_true")
    ap.parse_args()
    os.makedirs(STAGE, exist_ok=True)
    n0, tags0 = pooled_in_band()
    print("pooled in-band before this arm: %d %s" % (n0, tags0), flush=True)
    if n0 >= TARGET_IN_BAND:
        print("STOP: target already met before launching.")
        return
    for i, c in enumerate(cells()):
        f = os.path.join(PAPER, "RUN_MATCHED20_r289_cell%02d.json" % i)
        if os.path.exists(f):
            continue
        r = run_cell(i, c)
        if r.get("status") == "YIELDED":
            print("stopping: yielded to the user's own work", flush=True)
            return
        print("cell %02d %-16s KV=%g s%-4d wall %6.1f s  t_end %8s  completes %s"
              % (i, r["prefix"], c["kv"], c["seed"], r.get("wall_clock_s", 0),
                 ("%.3f" % r["t_end_s"]) if r.get("t_end_s") is not None else "-",
                 (r.get("t_end_s") or 0) >= 19.999), flush=True)
        n, tags = pooled_in_band()
        if n >= TARGET_IN_BAND:
            print("\nSTOP: %d in-band cells exist -> %s" % (n, tags), flush=True)
            print("stopping rule met on COVERAGE. Endpoint not computed by this launcher.")
            return
    print("\nSTOP: %d cells run, in-band count %d < %d -> UNINFORMATIVE again"
          % (MAX_CELLS, pooled_in_band()[0], TARGET_IN_BAND), flush=True)


if __name__ == "__main__":
    main()
