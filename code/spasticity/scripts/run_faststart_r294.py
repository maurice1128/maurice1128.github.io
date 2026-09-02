"""run_faststart_r294.py -- launcher for PREREG_faststart_r294.md rev 2 (b5da395f...).

Control model, no lesion. min_velocity 1.0 -> 1.5 IN PLACE inside the corpus's own
CompositeMeasure, altering nothing else. 600 generations, 2 seeds, warm-started from each
seed's own control endpoint.

SECTION 2d VALIDATION GATES THE RUN. Before any cell optimises:
  1. diff(vendor 1.0 file, vendor 1.5 file) must be exactly min_velocity: 1.0 -> 1.5
  2. diff(corpus staged, corpus original) must be the same single token change
If either diff touches anything else, NOTHING RUNS.

Endpoint: achieved speed only. No lesion, no channel.
"""
import argparse
import difflib
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
SRC = os.path.join(ROOT, "reopt_r151", "R151C_s101")
STAGE = os.path.join(ROOT, "faststart_r294")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
V10 = r"C:\Program Files\SCONE\scone\scenarios\Examples2\data\MeasureGait10Grf15.scone"
V15 = r"C:\Program Files\SCONE\scone\scenarios\Tutorials2\data\MeasureGait15Grf15.scone"
SEEDS = [101, 102]
GENS = 600
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


def norm(txt):
    """Strip comments and blank lines; keep token content."""
    out = []
    for ln in txt.splitlines():
        ln = re.sub(r"#.*", "", ln).strip()
        if ln:
            out.append(ln)
    return out


def token_diff(a, b):
    """Return the list of changed lines between two normalised texts."""
    d = [l for l in difflib.unified_diff(norm(a), norm(b), lineterm="", n=0)
         if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    return d


def validate():
    """PREREG section 2d. Returns (ok, report)."""
    rep = {}
    v10 = io.open(V10, encoding="utf-8").read()
    v15 = io.open(V15, encoding="utf-8").read()
    d1 = token_diff(v10, v15)
    rep["vendor_diff"] = d1
    ok1 = (sorted(d1) == sorted(["-min_velocity = 1.0", "+min_velocity = 1.5"]))
    rep["vendor_diff_is_one_token"] = ok1

    orig = io.open(os.path.join(SRC, "config.scone"), encoding="utf-8").read()
    staged = orig.replace("min_velocity = 1.0", "min_velocity = 1.5")
    d2 = token_diff(orig, staged)
    rep["corpus_diff"] = d2
    ok2 = (sorted(d2) == sorted(["-min_velocity = 1.0", "+min_velocity = 1.5"]))
    rep["corpus_diff_is_one_token"] = ok2
    rep["same_change"] = bool(ok1 and ok2 and sorted(d1) == sorted(d2))
    rep["PASSES"] = bool(ok1 and ok2 and rep["same_change"])
    return rep["PASSES"], rep


def best_par(cd):
    pars = sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
    if not pars:
        return None

    def key(p):
        b = os.path.basename(p).split("_")
        return (float(b[2].replace(".par", "")), -int(b[0]))
    return min(pars, key=key)


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d" % (tag, len(g))
    return g[0]


def stage_one(seed):
    d = os.path.join(STAGE, "R294FAST_s%d" % seed)
    for sub in ("models", "data", "par"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copyfile(os.path.join(SRC, "H1922v7b3.hfd"),
                    os.path.join(d, "models", "H1922v7b3.hfd"))
    shutil.copyfile(os.path.join(SRC, "InitStateH0918Gait10ActA.zml"),
                    os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
    # warm start: this seed's own control endpoint
    src_par = best_par(rd("R151C_s%d" % seed))
    warm = os.path.basename(src_par)
    shutil.copyfile(src_par, os.path.join(d, "par", warm))

    cfg = io.open(os.path.join(SRC, "config.scone"), encoding="utf-8").read()
    cfg, n_kv = re.subn(r"min_velocity\s*=\s*1\.0", "min_velocity = 1.5", cfg)
    assert n_kv == 1, "expected 1 min_velocity substitution, made %d" % n_kv
    cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = %d" % seed, cfg, count=1)
    cfg = re.sub(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, count=1)
    cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = R294FAST_s%d" % seed,
                 cfg, count=1)
    cfg = re.sub(r'init\s*\{\s*file\s*=\s*"[^"]+"\s*\}',
                 'init { file = "par/%s" }' % warm, cfg, count=1)
    io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="\n").write(cfg)

    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    mv = re.search(r"min_velocity\s*=\s*([0-9.]+)", back).group(1)
    return d, warm, mv


def achieved_speed(cd):
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return None
    cols, dat = S.load_sto(stos[-1])
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= 1.0 and t[idx[k + 1]] <= 13.58]
    if len(cyc) < 2:
        return None
    a, b = cyc[0][0], cyc[-1][1]
    x = S.col(cols, dat, "pelvis_tx")
    return float((x[b] - x[a]) / (t[b] - t[a]))


def competing():
    try:
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, text=True, timeout=30).stdout
        return sum(1 for ln in o.splitlines() if "sconecmd" in ln.lower())
    except Exception:
        return -1


def main():
    argparse.ArgumentParser().parse_args()
    ok, rep = validate()
    io.open(os.path.join(PAPER, "FASTSTART_VALIDATION_r294.json"), "w",
            encoding="utf-8", newline="\n").write(json.dumps(rep, indent=1) + "\n")
    print("SECTION 2d VALIDATION")
    print("  vendor diff : %s" % rep["vendor_diff"])
    print("  corpus diff : %s" % rep["corpus_diff"])
    print("  same change : %s" % rep["same_change"])
    print("  PASSES      : %s" % rep["PASSES"])
    if not ok:
        print("\nGATE FAILED -- nothing runs.")
        return 1

    os.makedirs(STAGE, exist_ok=True)
    for i, seed in enumerate(SEEDS):
        f = os.path.join(PAPER, "RUN_FASTSTART_r294_cell%02d.json" % i)
        if os.path.exists(f):
            continue
        d, warm, mv = stage_one(seed)
        n = competing()
        if n > 0:
            print("YIELD: %d sconecmd running. Suspending." % n)
            return 0
        before = set(os.listdir(RES))
        t0 = time.time()
        p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                           capture_output=True, text=True, cwd=d)
        wall = time.time() - t0
        new = sorted(set(os.listdir(RES)) - before)
        for nd in new:
            assert not PROTECTED.match(nd), "refusing: protected " + nd
        rec = {"cell": i, "seed": seed, "generations": GENS, "warm_start": warm,
               "min_velocity_read_back": mv, "wall_clock_s": wall,
               "returncode": p.returncode, "new_result_dirs": new,
               "validation": rep}
        if new:
            cd = os.path.join(RES, new[0])
            rec["result_dir"] = new[0]
            bp = best_par(cd)
            rec["resolved_par"] = os.path.basename(bp) if bp else None
            if bp and not glob.glob(os.path.join(cd, "*.par.sto")):
                subprocess.run([SCONE, "-e", os.path.basename(bp)], cwd=cd,
                               capture_output=True, timeout=1800)
            rec["achieved_speed_mps"] = achieved_speed(cd)
        io.open(f, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1) + "\n")
        print("cell %02d seed %d  min_velocity=%s  wall %.1f s  achieved %s m/s"
              % (i, seed, mv, wall,
                 ("%.4f" % rec["achieved_speed_mps"]) if rec.get("achieved_speed_mps") else "-"),
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
