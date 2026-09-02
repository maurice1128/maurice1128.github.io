# -*- coding: utf-8 -*-
"""warmstart_probe_r392.py -- ONE decisive probe before committing the licence.

QUESTION. Our KV 0.070 spastic condition falls in all six seeds (t_end 8.24-9.52 s against a
9.73 s gate). Ong et al. 2019 (PLoS Comput Biol 15(10):e1006993) carried a far deeper lesion
and still walked. Two differences: (1) budget -- 1500 generations x 10 parallel runs per cell
vs our ~90 generations x 1 run; (2) WARM-START CHAINING -- "the solution from the unimpaired
case was used to seed the mild SOL weakness case, which was used to seed the moderate case,
which was finally used to seed the severe case". Our launchers stage EVERY severity from the
same unlesioned base par. No chaining.

THREE ARMS, seed 101 only, KV 0.070 only.
  A  BASELINE   exact reproduction of the corpus recipe (run_bandfill_r291.py), 90 gens,
                init = the unlesioned base par H1922v7b3-TSG3Dv8g-989_fixed2.par
  B  WARM       identical to A except init = the optimised KV 0.050 solution
                (R151S_s101 generation 0056, t_end 17.85 s), 90 gens
  C  BUDGET     identical to A except max_generations = 400

A and B differ in EXACTLY ONE LINE of config.scone. A and C differ in EXACTLY ONE LINE.
The model file, the init state, the seed, the objective and every measure are byte-identical
across the three arms (asserted below).

INIT SETTINGS. The corpus init block is `init { file = "par/<name>.par" }` and sets neither
std_factor nor use_best_as_mean. This probe does NOT set them either, in any arm: adding them
to B would confound the chaining test with a search-width change. SCONE's defaults therefore
apply in all three arms (std_factor 1, no std offset, the par file's MEAN column used as the
CMA mean). The two candidate init pars carry comparable stds (e.g. pelvis_tilt.offset
1.117e-4 in the base vs 1.010e-4 in the KV 0.050 solution), so B is not a covertly narrowed
search -- see "init_std_audit" in the deposit.

SAFETY, the user's standing orders, enforced in code:
  * writes go ONLY under C:\\Users\\maurice\\Desktop\\spasticity_paper\\; SCONE may create NEW
    directories under SCONE\\results and nothing else is opened for write;
  * before each cell, count sconecmd processes. If any is running, YIELD and report;
  * assert no newly created results directory matches the protected pattern.

Usage:  python warmstart_probe_r392.py --stage
        python warmstart_probe_r392.py --run
"""
import argparse
import difflib
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

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC_S = os.path.join(ROOT, "reopt_r151", "R151S_s101")   # KV 0.050 staging cell, seed 101
STAGE = os.path.join(ROOT, "warmprobe_r392")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "WARMSTART_PROBE_r392.json")

# the optimised KV 0.050 solution used as arm B's init
CHAIN_DIR = os.path.join(RES, "R151S_s101.H1922v7b3.TSG3Dv8g.R3.S10WA3K0G13.D20.R101")
CHAIN_PAR = "0056_65.682_19.381.par"        # highest generation AND objective minimum
CHAIN_STAGED_AS = "WARM_R151S_s101_g0056.par"   # non-numeric name: never mistaken for output

BASE_PAR = "H1922v7b3-TSG3Dv8g-989_fixed2.par"
GATE_T1 = 9.73
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")

ARMS = [
    {"arm": "A", "prefix": "R392A_s101", "init": "par/" + BASE_PAR,      "gens": 90,
     "label": "BASELINE, corpus recipe, unlesioned base par, 90 generations"},
    {"arm": "B", "prefix": "R392B_s101", "init": "par/" + CHAIN_STAGED_AS, "gens": 90,
     "label": "WARM-STARTED from the optimised KV 0.050 solution, 90 generations"},
    {"arm": "C", "prefix": "R392C_s101", "init": "par/" + BASE_PAR,      "gens": 400,
     "label": "BIGGER BUDGET, no chaining, 400 generations"},
]


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def stage():
    os.makedirs(STAGE, exist_ok=True)
    src_cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    diffs = {}
    for a in ARMS:
        d = os.path.join(STAGE, a["prefix"])
        for sub in ("models", "data", "par"):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        # model: byte-identical to the KV 0.050 / KV 0.070 source. NO Fmax is altered.
        shutil.copyfile(os.path.join(SRC_S, "H1922v7b3.hfd"),
                        os.path.join(d, "models", "H1922v7b3.hfd"))
        shutil.copyfile(os.path.join(SRC_S, "InitStateH0918Gait10ActA.zml"),
                        os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
        shutil.copyfile(os.path.join(SRC_S, "par", BASE_PAR),
                        os.path.join(d, "par", BASE_PAR))
        if a["arm"] == "B":
            shutil.copyfile(os.path.join(CHAIN_DIR, CHAIN_PAR),
                            os.path.join(d, "par", CHAIN_STAGED_AS))

        cfg = src_cfg
        # (1) the lesion: KV 0.050 -> 0.070 in the SpasticL block, exactly as r291 does
        cfg, n = re.subn(r"KV\s*=\s*0\.050", "KV = 0.07", cfg)
        assert n == 2, "expected 2 KV substitutions, made %d" % n
        # (2) generations
        cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % a["gens"],
                         cfg, count=1)
        assert n == 1
        # (3) the init file -- THE ONE LINE THAT SEPARATES ARM B FROM ARM A
        cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                         'init { file = "%s" }' % a["init"], cfg, count=1)
        assert n == 1, "init block not found"
        cfg = re.sub(r"random_seed\s*=\s*\d+", "random_seed = 101", cfg, count=1)
        cfg = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % a["prefix"],
                     cfg, count=1)
        io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8",
                newline="\n").write(cfg)

        # verify by reading the staged config BACK OFF DISK
        back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
        assert len(re.findall(r"KV\s*=\s*0\.07\b", back)) == 2
        assert re.search(r"max_generations\s*=\s*%d\b" % a["gens"], back)
        m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
        assert m and m.group(1) == a["init"], "init readback %s" % (m and m.group(1))
        assert os.path.exists(os.path.join(d, m.group(1).replace("/", os.sep))), \
            "init file missing on disk: " + m.group(1)
        assert re.search(r"signature_prefix\s*=\s*%s\b" % a["prefix"], back)
        diffs[a["arm"]] = [l for l in difflib.unified_diff(
            src_cfg.splitlines(), back.splitlines(),
            fromfile="R151S_s101/config.scone", tofile=a["prefix"] + "/config.scone",
            lineterm="", n=1)]
        a["_init_line_readback"] = m.group(0)

    # the three arms must differ ONLY in the intended lines
    ca = io.open(os.path.join(STAGE, "R392A_s101", "config.scone"), encoding="utf-8").read()
    cb = io.open(os.path.join(STAGE, "R392B_s101", "config.scone"), encoding="utf-8").read()
    cc = io.open(os.path.join(STAGE, "R392C_s101", "config.scone"), encoding="utf-8").read()
    ab = [l for l in difflib.unified_diff(ca.splitlines(), cb.splitlines(), lineterm="", n=0)
          if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    ac = [l for l in difflib.unified_diff(ca.splitlines(), cc.splitlines(), lineterm="", n=0)
          if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    diffs["A_vs_B"] = ab
    diffs["A_vs_C"] = ac
    # 2 lines changed each = signature_prefix + (init | max_generations)
    assert len(ab) == 4, "A vs B differs in %d lines, expected 4" % len(ab)
    assert len(ac) == 4, "A vs C differs in %d lines, expected 4" % len(ac)
    for a in ARMS:
        d = os.path.join(STAGE, a["prefix"])
        assert sha(os.path.join(d, "models", "H1922v7b3.hfd")) == \
               sha(os.path.join(STAGE, "R392A_s101", "models", "H1922v7b3.hfd"))
    print("staged 3 arms under %s" % STAGE)
    return diffs


def init_std_audit():
    """Are the two init pars comparably wide? A narrowed B would confound the test."""
    def rd(p):
        rows = {}
        for ln in io.open(p, encoding="utf-8"):
            c = ln.split()
            if len(c) >= 4:
                rows[c[0]] = (float(c[1]), float(c[2]), float(c[3]))
        return rows
    a = rd(os.path.join(SRC_S, "par", BASE_PAR))
    b = rd(os.path.join(CHAIN_DIR, CHAIN_PAR))
    common = sorted(set(a) & set(b))
    ra = [b[k][2] / a[k][2] for k in common if a[k][2] > 0]
    ra.sort()
    return {"n_params_base": len(a), "n_params_chain": len(b), "n_common": len(common),
            "std_ratio_chain_over_base": {
                "min": ra[0], "median": ra[len(ra) // 2], "max": ra[-1],
                "geomean": float(__import__("math").exp(
                    sum(__import__("math").log(x) for x in ra) / len(ra)))},
            "interpretation": ("ratios near 1 mean arm B's search is not narrower than "
                               "arm A's, so any difference in outcome is chaining, not "
                               "search width")}


def competing():
    try:
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, text=True, timeout=30).stdout
        return sum(1 for ln in o.splitlines() if "sconecmd" in ln.lower())
    except Exception:
        return -1


def best_par_by_generation(cd, exclude):
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) not in exclude]
    if not pars:
        return None
    return max(pars, key=lambda p: int(os.path.basename(p).split("_")[0]))


def best_par_by_objective(cd, exclude):
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) not in exclude]
    if not pars:
        return None

    def key(p):
        b = os.path.basename(p).split("_")
        return (float(b[2].replace(".par", "")), -int(b[0]))
    return min(pars, key=key)


def history(cd):
    h = os.path.join(cd, "history.txt")
    if not os.path.exists(h):
        return {}
    rows = []
    with io.open(h, encoding="utf-8", errors="replace") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        gi, bi = hdr.index("generation"), hdr.index("best_fitness")
        for ln in f:
            c = ln.rstrip("\n").split("\t")
            if len(c) > bi:
                rows.append((int(float(c[gi])), float(c[bi])))
    if not rows:
        return {}
    run, m = [], float("inf")
    for g, bf in rows:
        m = min(m, bf)
        run.append((g, m))
    at10 = [v for g, v in run if g <= run[-1][0] - 10]
    return {"n_generations": len(rows), "last_generation": rows[-1][0],
            "objective_gen0": run[0][1], "terminal_objective": run[-1][1],
            "descent_final_10_gens": (at10[-1] - run[-1][1]) if at10 else 0.0}


def t_end_of(sto):
    cols, dat = S.load_sto(sto)
    return float(list(S.col(cols, dat, "time"))[-1])


def run_arm(a):
    d = os.path.join(STAGE, a["prefix"])
    assert os.path.isdir(d), "not staged: " + d
    n = competing()
    if n > 0:
        print("YIELD: %d sconecmd running that is not ours. Suspending." % n, flush=True)
        return {"arm": a["arm"], "status": "YIELDED", "competing": n}
    before = set(os.listdir(RES))
    t0 = time.time()
    p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                       capture_output=True, text=True, cwd=d)
    wall = time.time() - t0
    new = sorted(set(os.listdir(RES)) - before)
    for nd in new:
        assert not PROTECTED.match(nd), "refusing: protected name created " + nd
    rec = {"arm": a["arm"], "label": a["label"], "prefix": a["prefix"],
           "kv": 0.070, "seed": 101, "max_generations": a["gens"],
           "init_file": a["init"], "wall_clock_s": round(wall, 2),
           "returncode": p.returncode, "new_result_dirs": new,
           "stdout_tail": (p.stdout or "")[-600:], "stderr_tail": (p.stderr or "")[-600:]}
    if not new:
        rec["status"] = "NO_OUTPUT_DIR"
        return rec
    cd = os.path.join(RES, new[0])
    rec["status"] = "OK" if p.returncode == 0 else "NONZERO_EXIT"
    rec["result_dir"] = new[0]
    rec.update(history(cd))
    excl = {BASE_PAR, CHAIN_STAGED_AS}
    bg = best_par_by_generation(cd, excl)
    bo = best_par_by_objective(cd, excl)
    rec["resolved_par_by_generation"] = os.path.basename(bg) if bg else None
    rec["resolved_par_by_objective"] = os.path.basename(bo) if bo else None
    rec["resolvers_agree"] = (bg == bo)
    if bg:
        if not os.path.exists(bg + ".sto"):
            subprocess.run([SCONE, "-e", os.path.basename(bg)], cwd=cd,
                           capture_output=True, timeout=1800)
        if os.path.exists(bg + ".sto"):
            rec["t_end_s"] = t_end_of(bg + ".sto")
    if bo and bo != bg:
        if not os.path.exists(bo + ".sto"):
            subprocess.run([SCONE, "-e", os.path.basename(bo)], cwd=cd,
                           capture_output=True, timeout=1800)
        if os.path.exists(bo + ".sto"):
            rec["t_end_s_objective_par"] = t_end_of(bo + ".sto")
    te = rec.get("t_end_s")
    rec["passes_gate_9.73"] = bool(te is not None and te >= GATE_T1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    diffs = stage()
    if a.stage:
        io.open(os.path.join(STAGE, "_diffs.json"), "w", encoding="utf-8",
                newline="\n").write(json.dumps(diffs, indent=1) + "\n")
        return
    if not a.run:
        return

    dep = {"probe": "WARMSTART_PROBE_r392",
           "question": ("Does warm-start chaining, or a bigger budget, or neither, let this "
                        "model carry the KV 0.070 spastic lesion it currently cannot?"),
           "condition": {"kv": 0.070, "seed": 101, "gate_t1_s": GATE_T1,
                         "max_duration_s": 20},
           "reference_failure": {
               "cell": "R291KV0070_s101", "t_end_s": 8.24, "wall_clock_s": 72.04,
               "source": "paper/RUN_BANDFILL_r291_cell06.json"},
           "chain_parent": {
               "cell": "R151S_s101", "kv": 0.050, "seed": 101,
               "par": CHAIN_PAR, "t_end_s": 17.85,
               "why": ("the immediately milder rung of the same KV ladder, same seed, same "
                       "min_velocity 1.0, same base model -- Ong et al.'s chaining is rung "
                       "to rung, not arbitrary donor to recipient")},
           "init_syntax": 'init { file = "par/<name>.par" }  (relative to the config dir; '
                          'SCONE is invoked with cwd = that dir)',
           "init_settings": {"std_factor": "NOT SET in any arm (SCONE default)",
                             "std_offset": "NOT SET in any arm (SCONE default)",
                             "use_best_as_mean": "NOT SET in any arm (SCONE default)",
                             "why": ("the corpus sets none of them; setting any of them in "
                                     "arm B alone would confound chaining with a change of "
                                     "search width, which is the whole point of the probe")},
           "init_std_audit": init_std_audit(),
           "config_diffs": diffs,
           "arms": []}
    for a_ in ARMS:
        print("running arm %s (%s)..." % (a_["arm"], a_["label"]), flush=True)
        r = run_arm(a_)
        r["init_line_readback"] = a_.get("_init_line_readback")
        dep["arms"].append(r)
        print("arm %s  status %-10s wall %7.1f s  gens %-4s t_end %s"
              % (r["arm"], r.get("status"), r.get("wall_clock_s", 0),
                 r.get("n_generations"), r.get("t_end_s")), flush=True)
        io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(dep, indent=1) + "\n")
        if r.get("status") == "YIELDED":
            dep["stop_reason"] = "YIELDED to another sconecmd"
            break
    else:
        dep["stop_reason"] = "all three arms run"

    got = {r["arm"]: r.get("t_end_s") for r in dep["arms"]}
    pas = {r["arm"]: r.get("passes_gate_9.73") for r in dep["arms"]}
    dep["verdict"] = {"t_end_s": got, "passes_gate": pas}
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(dep, indent=1) + "\n")
    print("deposited %s (%d bytes)" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
