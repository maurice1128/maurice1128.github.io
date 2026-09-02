# -*- coding: utf-8 -*-
r"""run_chain_r393.py -- WARM-START CHAINING up BOTH lesion axes to clinical magnitudes.

WHY. Every severity in the corpus was staged from the SAME unlesioned base par, so the
optimiser had to rediscover walking from scratch at each rung and fell off the ladder well
below clinically realistic lesion magnitudes. WARMSTART_PROBE_r392 tested the alternative on
one cell: arm A (corpus recipe, KV 0.070, seed 101) reproduced the failure exactly
(t_end 8.24 s against a 9.73 s gate); arm B, identical except that its init par was the
optimised KV 0.050 solution OF THE SAME SEED, reached t_end 13.95 s and passed, terminal
objective 64.24 -> 37.23. An init-std audit (ratios 0.90-0.92) showed arm B's search was not
narrower, so the gain is chaining, not a narrowed search. This is Ong et al. 2019's published
protocol: "the solution from the unimpaired case was used to seed the mild ... which was used
to seed the moderate ... which was finally used to seed the severe case".

THE EXPERIMENT. Two ladders, six seeds each, every rung warm-started from THE SAME SEED's
solution at the previous rung.

  SPASTIC   KV on soleus_l and gastroc_l, allow_neg_V = 0, delay 0.020
            0.050 -> 0.070 -> 0.100 -> 0.150
            root = R151S (already run, verified here to carry KV 0.050 and min_velocity 1.0)
  WEAKNESS  tib_ant_l max_isometric_force, base 1759
            x0.80 -> x0.60 -> x0.40 -> x0.30
            root = R151W (already run, verified here to carry tib_ant_l 1407.2)
            soleus_l 3549 and gastroc_l 2241 are ASSERTED unchanged in every weakness cell.

36 new cells = 3 new rungs x 6 seeds x 2 axes. 90 generations per cell, the corpus value: the
ONLY change from the corpus recipe is the init file.

CHAINING DISCIPLINE, the part that is easy to get wrong.
  * The parent .par is THE CHILD SEED's OWN parent. Seed 104's KV 0.100 cell is seeded from
    seed 104's KV 0.070 solution, never from seed 101's.
  * The parent's best .par is resolved by HIGHEST GENERATION among the run's own outputs,
    EXCLUDING the staged warm-start file by name -- see best_par_by_generation(), transcribed
    with its docstring from run_dfsevere_r293.py. Selecting by the objective field encoded in
    the filename is UNSAFE across differing objectives: a warm start optimised under a milder
    lesion routinely carries a LOWER number than every genuine child output and would be
    picked as the child's "best". The staged warm file is additionally named WARM_*.par, which
    the "[0-9]*.par" glob cannot match, so the exclusion is belt and braces.
  * If a parent cell FAILS Gate G its child CANNOT be chained from it. No other parent is
    substituted. That seed's remaining chain is marked BROKEN, recorded, and the other seeds
    continue.
  * Every cell records the exact parent .par it was seeded from and that file's sha256.

GATE G, the corpus admissibility gate, unchanged:
    t_end >= 9.73 s AND >= 5 admissible cycles in the window
    (SETTLE 1.00, T1 9.73, cycles between left heel strikes with t[start] >= SETTLE and
     t[end] <= T1, drop the LAST kept cycle, stance = leg0_l.grf_norm_y > 0.05)

SAFETY, the user's standing orders, enforced in code:
  * every path opened for write is asserted to lie under spasticity_paper\; SCONE may create
    NEW directories under SCONE\results and nothing else there is opened for write;
  * before each cell, count sconecmd processes and YIELD if any is running;
  * no newly created results directory may match the protected pattern
    ^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L .

Usage:  python run_chain_r393.py --stage       build the tree, resolve what is resolvable
        python run_chain_r393.py --cell N      run one cell (0-based)
        python run_chain_r393.py --rest        run the remaining cells in order
        python run_chain_r393.py --headline    the spastic-vs-weakness gap per rung
"""
import argparse
import datetime
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

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC_S = os.path.join(ROOT, "reopt_r151", "R151S_s101")   # spastic template, KV 0.050
SRC_W = os.path.join(ROOT, "reopt_r151", "R151W_s101")   # weakness template, x0.80
SRC_C = os.path.join(ROOT, "reopt_r151", "R151C_s101")   # unlesioned reference
STAGE = os.path.join(ROOT, "chain_r400")
WRITE_ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"

BASE_PAR = "H1922v7b3-TSG3Dv8g-989_fixed2.par"
GENS = 90
GATE_T1 = 9.73
SETTLE = 1.00
MIN_CYC = 5
SEEDS = [101, 102, 103, 104, 105, 106]
FMAX_BASE = {"tib_ant_l": 1759.0, "soleus_l": 3549.0, "gastroc_l": 2241.0}

# rung tag, value.  index 0 is the EXISTING chain root and is never re-run.
SP_RUNGS = [("050", 0.050), ("c1", 0.050), ("c2", 0.050), ("c3", 0.050)]
WK_RUNGS = [("080", 0.80), ("c1", 0.80), ("c2", 0.80), ("c3", 0.80)]
SP_ROOT = "R151S"                   # sham chain starts at the unchained spastic root
WK_ROOT = "R151W"

PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


# ------------------------------------------------------------------ safety ------------------
def wpath(p):
    """Assert p lies under spasticity_paper before anything opens it for write."""
    ap = os.path.abspath(p)
    assert ap.lower().startswith(WRITE_ROOT.lower() + os.sep), "REFUSING to write outside " \
        "spasticity_paper: " + ap
    return ap


def wopen(p, mode="w"):
    return io.open(wpath(p), mode, encoding="utf-8", newline="\n")


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def competing():
    """sconecmd processes. Any at all means someone else's work is running: YIELD."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return -1
    return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())


# ------------------------------------------------------------------ cells -------------------
def cells():
    out = []
    for k in range(1, len(SP_RUNGS)):
        tag, kv = SP_RUNGS[k]
        ptag = SP_RUNGS[k - 1][0]
        for s in SEEDS:
            out.append({
                "axis": "spastic", "rung": tag, "rung_index": k, "value": kv, "seed": s,
                "prefix": "R400SPg%s_s%d" % (tag, s),
                "parent_prefix": ("%s_s%d" % (SP_ROOT, s) if k == 1
                                  else "R400SPg%s_s%d" % (ptag, s)),
                "parent_is_root": k == 1})
    for k in range(1, len(WK_RUNGS)):
        tag, f = WK_RUNGS[k]
        ptag = WK_RUNGS[k - 1][0]
        for s in SEEDS:
            out.append({
                "axis": "weakness", "rung": tag, "rung_index": k, "value": f, "seed": s,
                "prefix": "R400WK%s_s%d" % (tag, s),
                "parent_prefix": ("%s_s%d" % (WK_ROOT, s) if k == 1
                                  else "R400WK%s_s%d" % (ptag, s)),
                "parent_is_root": k == 1})
    return out


def cell_index(prefix):
    for i, c in enumerate(cells()):
        if c["prefix"] == prefix:
            return i
    return None


# ------------------------------------------------------------------ model ------------------
def write_hfd(src, dst, scale):
    """Scale tib_ant_l by `scale`; the plantarflexors must remain at base."""
    txt = io.open(src, encoding="utf-8").read()
    if scale is None:                                     # spastic axis: model untouched
        io.open(wpath(dst), "w", encoding="utf-8", newline="\n").write(txt)
    else:
        pat = re.compile(r"(name\s*=\s*tib_ant_l\b.*?max_isometric_force\s*=\s*)([0-9.]+)",
                         re.S)
        txt, n = pat.subn(lambda g: g.group(1) + ("%.6g" % (FMAX_BASE["tib_ant_l"] * scale)),
                          txt, count=1)
        assert n == 1, "expected 1 tib_ant_l substitution, made %d" % n
        io.open(wpath(dst), "w", encoding="utf-8", newline="\n").write(txt)
    # read BACK off disk
    chk = io.open(dst, encoding="utf-8").read()
    got = {}
    for m in ("tib_ant_l", "soleus_l", "gastroc_l"):
        got[m] = float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*"
                                 r"([0-9.]+)", chk, re.S).group(1))
    want_ta = FMAX_BASE["tib_ant_l"] * (1.0 if scale is None else scale)
    assert abs(got["tib_ant_l"] - want_ta) < 1e-6, \
        "tib_ant_l wanted %s, wrote %s" % (want_ta, got["tib_ant_l"])
    # THE ASSERTION THE PREREGISTRATION DEMANDS
    assert abs(got["soleus_l"] - 3549.0) < 1e-9, "soleus_l must stay 3549, found %s" % got["soleus_l"]
    assert abs(got["gastroc_l"] - 2241.0) < 1e-9, "gastroc_l must stay 2241, found %s" % got["gastroc_l"]
    return got


# ------------------------------------------------------------------ resolvers ----------------
def result_dir(prefix):
    """The one results directory for a signature prefix, or None."""
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    assert len(g) <= 1, "%d result dirs for %s" % (len(g), prefix)
    return g[0] if g else None


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


def ensure_sto(cd, par):
    """Replay one .par into a .sto if SCONE has not already written it."""
    sto = par + ".sto"
    if not os.path.exists(sto):
        subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=cd,
                       capture_output=True, timeout=1800)
    return sto if os.path.exists(sto) else None


def measure(cd, par):
    """Gate G and the ankle endpoint, corpus convention, on ONE resolved .par's .sto.

    SETTLE 1.00, T1 9.73; cycles between left heel strikes with t[start] >= SETTLE, wholly
    inside the window; drop the LAST kept cycle; require >= 5; stance = leg0_l.grf_norm_y
    > 0.05 (S.grf_vertical returns that threshold).
    """
    out = {"sto": None, "t_end_s": None, "n_cycles_in_window": None, "gate_G": False,
           "ank_stance_mean_deg": None}
    sto = ensure_sto(cd, par)
    if sto is None:
        out["guard"] = "replay produced no .sto"
        return out
    out["sto"] = os.path.basename(sto)
    cols, dat = S.load_sto(sto)
    if dat.size == 0:
        out["guard"] = "empty sto"
        return out
    t = dat[:, 0]
    out["t_end_s"] = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        out["guard"] = "no left vertical GRF"
        return out
    out["grf_threshold"] = thr
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= GATE_T1]
    win = win[:-1] if len(win) >= 2 else win
    out["n_cycles_in_window"] = len(win)
    if out["t_end_s"] < GATE_T1 or len(win) < MIN_CYC:
        out["guard"] = ("t_end %.3f < %.2f" % (out["t_end_s"], GATE_T1)
                        if out["t_end_s"] < GATE_T1
                        else "only %d cycles in window, need %d" % (len(win), MIN_CYC))
        return out
    out["gate_G"] = True
    on = grf > thr
    ank = S.col(cols, dat, "ankle_angle_l")
    if ank is None:
        out["gate_G"] = False
        out["guard"] = "no ankle_angle_l"
        return out
    idx = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    out["n_stance_samples"] = int(len(idx))
    out["ank_stance_mean_deg"] = float(np.degrees(np.mean(ank[idx])))
    return out


def evaluate(prefix):
    """Gate G + endpoint for any cell that has a results directory. Cached on disk."""
    cd = result_dir(prefix)
    if cd is None:
        return {"prefix": prefix, "status": "NO_RESULT_DIR"}
    warm = [os.path.basename(p) for p in glob.glob(os.path.join(cd, "WARM_*.par"))]
    bg = best_par_by_generation(cd, warm[0] if warm else None)
    if bg is None:
        return {"prefix": prefix, "status": "NO_PAR"}
    rec = {"prefix": prefix, "status": "OK", "result_dir": os.path.basename(cd),
           "resolved_par": os.path.basename(bg),
           "resolved_par_sha256": sha(bg),
           "resolved_par_generation": int(os.path.basename(bg).split("_")[0])}
    rec.update(history(cd))
    rec.update(measure(cd, bg))
    return rec


# ------------------------------------------------------------------ staging -----------------
def make_dirs(c):
    d = os.path.join(STAGE, c["prefix"])
    for sub in ("models", "data", "par"):
        os.makedirs(wpath(os.path.join(d, sub)), exist_ok=True)
    write_hfd(os.path.join(SRC_C, "H1922v7b3.hfd"),
              os.path.join(d, "models", "H1922v7b3.hfd"),
              None if c["axis"] == "spastic" else c["value"])
    shutil.copyfile(os.path.join(SRC_C, "InitStateH0918Gait10ActA.zml"),
                    wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))
    shutil.copyfile(os.path.join(SRC_C, "par", BASE_PAR),
                    wpath(os.path.join(d, "par", BASE_PAR)))
    return d


def prepare(c):
    """Resolve the parent, stage its .par, write and read back the config.

    -> record.  status PREPARED | PARENT_NOT_RUN | BROKEN_PARENT_FAILED_GATE
    """
    d = os.path.join(STAGE, c["prefix"])
    assert os.path.isdir(d), "not staged: " + d
    pev = evaluate(c["parent_prefix"])
    rec = {"prefix": c["prefix"], "axis": c["axis"], "rung": c["rung"],
           "value": c["value"], "seed": c["seed"], "parent_prefix": c["parent_prefix"],
           "parent_is_root": c["parent_is_root"]}
    if pev.get("status") != "OK":
        rec["status"] = "PARENT_NOT_RUN"
        rec["parent_status"] = pev.get("status")
        return rec
    rec["parent_result_dir"] = pev["result_dir"]
    rec["parent_gate_G"] = pev["gate_G"]
    rec["parent_t_end_s"] = pev["t_end_s"]
    rec["parent_n_cycles"] = pev["n_cycles_in_window"]
    if not pev["gate_G"]:
        rec["status"] = "BROKEN_PARENT_FAILED_GATE"
        rec["broken_reason"] = ("parent %s failed Gate G (%s); no other parent is substituted, "
                                "this seed's remaining chain on this axis is BROKEN"
                                % (c["parent_prefix"], pev.get("guard")))
        return rec

    psrc = os.path.join(RES, pev["result_dir"], pev["resolved_par"])
    warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], pev["resolved_par_generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(wpath(old))
    shutil.copyfile(psrc, wpath(os.path.join(d, "par", warm)))
    rec["parent_par"] = pev["resolved_par"]
    rec["parent_par_path"] = psrc
    rec["parent_par_sha256"] = pev["resolved_par_sha256"]
    rec["parent_par_generation"] = pev["resolved_par_generation"]
    rec["parent_terminal_objective"] = pev.get("terminal_objective")
    rec["staged_warm_as"] = warm
    assert sha(os.path.join(d, "par", warm)) == pev["resolved_par_sha256"], "warm copy differs"

    src_cfg = os.path.join(SRC_S if c["axis"] == "spastic" else SRC_W, "config.scone")
    cfg = io.open(src_cfg, encoding="utf-8").read()
    if c["axis"] == "spastic":
        cfg, n = re.subn(r"KV\s*=\s*0\.050", "KV = %.3f" % c["value"], cfg)
        assert n == 2, "expected 2 literal KV substitutions, made %d" % n
    else:
        assert not re.search(r"KV\s*=\s*0\.0[0-9]+\s*$", cfg, re.M), \
            "weakness template must carry no literal spastic KV"
    cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, count=1)
    assert n == 1
    cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                     'init { file = "par/%s" }' % warm, cfg, count=1)
    assert n == 1, "init block not found in " + src_cfg
    cfg, n = re.subn(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, count=1)
    assert n == 1
    cfg, n = re.subn(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                     cfg, count=1)
    assert n == 1
    wopen(os.path.join(d, "config.scone")).write(cfg)

    # ---- read the staged config BACK OFF DISK and assert every intended field --------------
    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    if c["axis"] == "spastic":
        got = len(re.findall(r"KV\s*=\s*%.3f\b" % c["value"], back))
        assert got == 2, "KV %.3f appears %d times, expected 2" % (c["value"], got)
        assert len(re.findall(r"allow_neg_V\s*=\s*0", back)) >= 2
        assert len(re.findall(r"delay\s*=\s*0\.020", back)) >= 2
    assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
    assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
    assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
    m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
    assert m and m.group(1) == "par/" + warm, "init readback %s" % (m and m.group(1))
    assert os.path.exists(os.path.join(d, "par", warm)), "init file missing on disk"
    rec["init_line_readback"] = m.group(0)
    # the model, read back off disk one more time
    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    fm = {mm: float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                              chk, re.S).group(1))
          for mm in ("tib_ant_l", "soleus_l", "gastroc_l")}
    assert fm["soleus_l"] == 3549.0 and fm["gastroc_l"] == 2241.0, fm
    want_ta = 1759.0 if c["axis"] == "spastic" else 1759.0 * c["value"]
    assert abs(fm["tib_ant_l"] - want_ta) < 1e-6, fm
    rec["fmax_readback"] = fm
    rec["config_sha256"] = sha(os.path.join(d, "config.scone"))
    rec["status"] = "PREPARED"
    return rec


def verify_roots():
    """The two chain roots are used, not re-run. Verify they are what they are claimed to be."""
    v = {}
    s_cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    v["R151S_template"] = {
        "kv_literal_count": len(re.findall(r"KV\s*=\s*0\.050", s_cfg)),
        "allow_neg_V_0_count": len(re.findall(r"allow_neg_V\s*=\s*0", s_cfg)),
        "delay_0.020_count": len(re.findall(r"delay\s*=\s*0\.020", s_cfg)),
        "min_velocity": re.search(r"min_velocity\s*=\s*([0-9.]+)", s_cfg).group(1),
        "max_generations": re.search(r"max_generations\s*=\s*(\d+)", s_cfg).group(1),
        "hfd_sha256": sha(os.path.join(SRC_S, "H1922v7b3.hfd"))}
    assert v["R151S_template"]["kv_literal_count"] == 2
    assert v["R151S_template"]["min_velocity"] == "1.0"
    w_cfg = io.open(os.path.join(SRC_W, "config.scone"), encoding="utf-8").read()
    wch = io.open(os.path.join(SRC_W, "H1922v7b3.hfd"), encoding="utf-8").read()
    v["R151W_template"] = {
        "kv_literal_count": len(re.findall(r"KV\s*=\s*0\.050", w_cfg)),
        "min_velocity": re.search(r"min_velocity\s*=\s*([0-9.]+)", w_cfg).group(1),
        "max_generations": re.search(r"max_generations\s*=\s*(\d+)", w_cfg).group(1),
        "fmax": {m: float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*"
                                    r"([0-9.]+)", wch, re.S).group(1))
                 for m in ("tib_ant_l", "soleus_l", "gastroc_l")}}
    assert v["R151W_template"]["kv_literal_count"] == 0
    assert v["R151W_template"]["min_velocity"] == "1.0"
    assert abs(v["R151W_template"]["fmax"]["tib_ant_l"] - 1407.2) < 1e-6
    assert v["R151W_template"]["fmax"]["soleus_l"] == 3549.0
    assert v["R151W_template"]["fmax"]["gastroc_l"] == 2241.0
    # the unlesioned model this launcher scales from is the same file the spastic root used
    assert sha(os.path.join(SRC_C, "H1922v7b3.hfd")) == sha(os.path.join(SRC_S, "H1922v7b3.hfd"))
    v["base_hfd_sha256"] = sha(os.path.join(SRC_C, "H1922v7b3.hfd"))
    # and scaling it by 0.80 must REPRODUCE the corpus weakness root byte for byte
    tmp = os.path.join(STAGE, "_verify_x080.hfd")
    os.makedirs(wpath(STAGE), exist_ok=True)
    write_hfd(os.path.join(SRC_C, "H1922v7b3.hfd"), tmp, 0.80)
    def _norm(p):
        return io.open(p, "rb").read().replace(b"\r\n", b"\n")

    _w = os.path.join(SRC_W, "H1922v7b3.hfd")
    v["x080_reproduces_R151W_model"] = (sha(tmp) == sha(_w))
    v["x080_reproduces_R151W_model_EOL_NORMALISED"] = (_norm(tmp) == _norm(_w))
    v["x080_byte_exact_fails_because"] = (
        "R151W's H1922v7b3.hfd is CRLF throughout EXCEPT line 388, the one line an old script "
        "rewrote, which is LF only: 470 CRLF against 471 in R151C, 14260 bytes against 14259. "
        "No recipe writing consistent line endings can reproduce it byte for byte. The lesion "
        "value itself, 1407.2 = 1759 x 0.80, is reproduced exactly. Checked EOL-normalised.")
    os.remove(wpath(tmp))
    assert v["x080_reproduces_R151W_model_EOL_NORMALISED"], (
        "scaling recipe does not reproduce R151W's model even after EOL normalisation")
    # the roots themselves must pass Gate G, else there is no ladder at all
    v["roots"] = {}
    for fam in (SP_ROOT, WK_ROOT):
        for s in SEEDS:
            p = "%s_s%d" % (fam, s)
            e = evaluate(p)
            v["roots"][p] = {k: e.get(k) for k in
                             ("status", "resolved_par", "resolved_par_sha256", "t_end_s",
                              "n_cycles_in_window", "gate_G", "ank_stance_mean_deg",
                              "terminal_objective")}
    return v


def stage():
    os.makedirs(wpath(STAGE), exist_ok=True)
    v = verify_roots()
    cs = cells()
    for c in cs:
        make_dirs(c)
    prep = []
    for c in cs:
        try:
            prep.append(prepare(c))
        except AssertionError as e:
            prep.append({"prefix": c["prefix"], "status": "PREPARE_ERROR", "error": str(e)})
    man = {
        "arm": "CHAIN_r400",
        "written_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "basis": ("WARMSTART_PROBE_r392: arm A (corpus recipe, KV 0.070, seed 101) t_end "
                  "8.24 s FAIL; arm B (identical but warm-started from the same seed's "
                  "optimised KV 0.050 solution) t_end 13.95 s PASS, terminal objective "
                  "64.24 -> 37.23; init-std ratios 0.90-0.92 so the search was not narrowed"),
        "protocol": ("Ong et al. 2019: the solution of each severity seeds the next. Here the "
                     "chain is rung-to-rung WITHIN a seed on each of the two lesion axes."),
        "only_change_from_corpus_recipe": "the init file. 90 generations, as the corpus.",
        "gate_G": {"min_t_end_s": GATE_T1, "min_cycles": MIN_CYC, "settle_s": SETTLE,
                   "stance": "leg0_l.grf_norm_y > 0.05",
                   "cycles": ("between left heel strikes, t[start] >= SETTLE, wholly inside "
                              "[SETTLE, T1], drop the LAST kept cycle")},
        "axes": {
            "spastic": {"target": "soleus_l and gastroc_l MuscleReflex KV, ConditionalController "
                                  "SpasticL, legs = left", "allow_neg_V": 0, "delay_s": 0.020,
                        "rungs": [r[1] for r in SP_RUNGS], "root_cell": SP_ROOT,
                        "root_rung": SP_RUNGS[0][1]},
            "weakness": {"target": "tib_ant_l max_isometric_force, base 1759",
                         "rungs": [r[1] for r in WK_RUNGS], "root_cell": WK_ROOT,
                         "root_rung": WK_RUNGS[0][1],
                         "asserted_unchanged": {"soleus_l": 3549.0, "gastroc_l": 2241.0}}},
        "seeds": SEEDS,
        "n_new_cells": len(cs),
        "stage_dir": STAGE,
        "root_verification": v,
        "resolver": ("best_par_by_generation: highest generation among the run's own "
                     "[0-9]*.par outputs, excluding the staged warm start by name. Selecting "
                     "by the filename's objective field is unsafe across differing objectives."),
        "parent_map": prep,
        "cells": [{"cell": i, "prefix": c["prefix"], "axis": c["axis"], "rung": c["rung"],
                   "value": c["value"], "seed": c["seed"],
                   "parent_prefix": c["parent_prefix"]} for i, c in enumerate(cs)]}
    p = os.path.join(PAPER, "CHAIN_STAGE_r400.json")
    wopen(p).write(json.dumps(man, indent=1) + "\n")
    print("staged %d cells under %s" % (len(cs), STAGE))
    print("manifest %s (%d bytes)" % (p, os.path.getsize(p)))
    n_ready = sum(1 for r in prep if r["status"] == "PREPARED")
    print("parents resolvable now: %d of %d (the rest are deeper rungs, resolved at run time)"
          % (n_ready, len(cs)))
    return man


# ------------------------------------------------------------------ running -----------------
def cell_json(i):
    return os.path.join(PAPER, "RUN_CHAIN_r400_cell%02d.json" % i)


def run_cell(i):
    c = cells()[i]
    d = os.path.join(STAGE, c["prefix"])
    assert os.path.isdir(d), "not staged: " + d

    pr = prepare(c)
    if pr["status"] != "PREPARED":
        rec = dict(pr)
        rec["cell"] = i
        rec["status"] = pr["status"]
        rec["ran"] = False
        wopen(cell_json(i)).write(json.dumps(rec, indent=1) + "\n")
        return rec

    n = competing()
    if n > 0:
        print("YIELD: %d sconecmd process(es) already running. Suspending, not competing." % n)
        return {"cell": i, "prefix": c["prefix"], "status": "YIELDED", "competing": n}

    before = set(os.listdir(RES))
    t0 = time.time()
    p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                       capture_output=True, text=True, cwd=d)
    wall = time.time() - t0
    new = sorted(set(os.listdir(RES)) - before)
    for nd in new:
        assert not PROTECTED.match(nd), "refusing: protected name created " + nd

    rec = dict(pr)
    rec.update({"cell": i, "ran": True, "wall_clock_s": round(wall, 2),
                "returncode": p.returncode, "new_result_dirs": new,
                "max_generations": GENS,
                "stdout_tail": (p.stdout or "")[-400:],
                "stderr_tail": (p.stderr or "")[-400:]})
    if not new:
        rec["status"] = "NO_OUTPUT_DIR"
    else:
        rec["status"] = "OK" if p.returncode == 0 else "NONZERO_EXIT"
        ev = evaluate(c["prefix"])
        for k in ("result_dir", "resolved_par", "resolved_par_sha256",
                  "resolved_par_generation", "n_generations", "last_generation",
                  "objective_gen0", "terminal_objective", "descent_final_10_gens",
                  "sto", "t_end_s", "n_cycles_in_window", "gate_G", "ank_stance_mean_deg",
                  "n_stance_samples", "guard"):
            if k in ev:
                rec[k] = ev[k]
    wopen(cell_json(i)).write(json.dumps(rec, indent=1) + "\n")
    return rec


def aggregate():
    cs = cells()
    recs = []
    for i, c in enumerate(cs):
        f = cell_json(i)
        r = {"cell": i, "prefix": c["prefix"], "axis": c["axis"], "rung": c["rung"],
             "value": c["value"], "seed": c["seed"], "parent_prefix": c["parent_prefix"],
             "status": "NOT_RUN"}
        if os.path.exists(f):
            j = json.load(io.open(f, encoding="utf-8"))
            j.pop("stdout_tail", None)
            j.pop("stderr_tail", None)
            r.update(j)
        recs.append(r)
    out = {"arm": "CHAIN_r400",
           "written_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "n_cells": len(cs),
           "n_run": sum(1 for r in recs if r.get("ran")),
           "n_gate_G": sum(1 for r in recs if r.get("gate_G")),
           "gate_G": {"min_t_end_s": GATE_T1, "min_cycles": MIN_CYC},
           "cells": recs}
    # per-rung survival
    surv = {}
    for ax, rungs, pre in (("spastic", SP_RUNGS, "R393SPg"), ("weakness", WK_RUNGS, "R393WK")):
        surv[ax] = {}
        root = SP_ROOT if ax == "spastic" else WK_ROOT
        rr = {}
        for s in SEEDS:
            e = evaluate("%s_s%d" % (root, s))
            rr[s] = bool(e.get("gate_G"))
        surv[ax][rungs[0][0]] = {"value": rungs[0][1], "source": "existing chain root " + root,
                                 "n_gate_G": sum(1 for v in rr.values() if v),
                                 "seeds_pass": [s for s in SEEDS if rr[s]]}
        for tag, val in rungs[1:]:
            got = [r for r in recs if r["axis"] == ax and r["rung"] == tag]
            surv[ax][tag] = {
                "value": val,
                "n_run": sum(1 for r in got if r.get("ran")),
                "n_gate_G": sum(1 for r in got if r.get("gate_G")),
                "seeds_pass": sorted(r["seed"] for r in got if r.get("gate_G")),
                "seeds_broken": sorted(r["seed"] for r in got
                                       if str(r.get("status", "")).startswith("BROKEN"))}
    out["survival"] = surv
    p = os.path.join(PAPER, "CHAIN_RESULT_r400.json")
    wopen(p).write(json.dumps(out, indent=1) + "\n")
    return out, p


def write_terminal(n_ran, n_reg, stop_reason, extra=None):
    rec = {"arm": "r393", "cells_run": n_ran, "cells_registered": n_reg,
           "complete": bool(n_ran >= n_reg), "stop_reason": stop_reason,
           "written_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "note": ("A partially-run arm leaves valid deposits and a consistent results tree; "
                    "only the absence of a live process reveals it. This file is the explicit "
                    "signal. If it is missing, the launcher was interrupted.")}
    if extra:
        rec.update(extra)
    p = os.path.join(PAPER, "TERMINAL_r393.json")
    wopen(p).write(json.dumps(rec, indent=1) + "\n")
    print("TERMINAL: cells_run=%d of %d  stop=%s" % (n_ran, n_reg, stop_reason))


def rest():
    cs = cells()
    for i, c in enumerate(cs):
        if os.path.exists(cell_json(i)):
            continue
        r = run_cell(i)
        print("cell %02d %-18s %-26s wall %6.1f s  obj %-10s t_end %-7s cyc %-3s gate %s"
              % (i, c["prefix"], r.get("status"), r.get("wall_clock_s", 0) or 0,
                 ("%.3f" % r["terminal_objective"]) if r.get("terminal_objective") is not None
                 else "-",
                 ("%.2f" % r["t_end_s"]) if r.get("t_end_s") is not None else "-",
                 r.get("n_cycles_in_window"), r.get("gate_G")))
        sys.stdout.flush()
        aggregate()
        if r.get("status") == "YIELDED":
            write_terminal(len(glob.glob(os.path.join(PAPER, "RUN_CHAIN_r400_cell*.json"))),
                           len(cs), "YIELDED to another sconecmd")
            return
    out, p = aggregate()
    write_terminal(len(glob.glob(os.path.join(PAPER, "RUN_CHAIN_r400_cell*.json"))),
                   len(cs), "REGISTERED STOP -- all cells reached")
    print("deposited %s (%d bytes)" % (p, os.path.getsize(p)))


# ------------------------------------------------------------------ headline ----------------
MDC_DEG = 3.8


def headline():
    """The spastic-vs-weakness gap on mean ankle_angle_l over stance, per matched rung.

    A rung index k pairs SP_RUNGS[k] with WK_RUNGS[k]: the k-th step up each ladder. A rung is
    REPORTABLE only if BOTH axes have >= 4 Gate-G seeds there, as registered.
    """
    per = {}
    for ax, rungs, pre, root in (("spastic", SP_RUNGS, "R393SPg", SP_ROOT),
                                 ("weakness", WK_RUNGS, "R393WK", WK_ROOT)):
        per[ax] = {}
        for k, (tag, val) in enumerate(rungs):
            vals, seeds, fails = {}, [], []
            for s in SEEDS:
                prefix = ("%s_s%d" % (root, s)) if k == 0 else ("%s%s_s%d" % (pre, tag, s))
                e = evaluate(prefix)
                if e.get("gate_G") and e.get("ank_stance_mean_deg") is not None:
                    vals[s] = e["ank_stance_mean_deg"]
                    seeds.append(s)
                else:
                    fails.append({"seed": s, "prefix": prefix,
                                  "status": e.get("status"), "t_end_s": e.get("t_end_s"),
                                  "n_cycles": e.get("n_cycles_in_window"),
                                  "guard": e.get("guard")})
            per[ax][tag] = {"value": val, "rung_index": k,
                            "per_seed_ank_stance_mean_deg": vals,
                            "n_gate_G": len(vals), "seeds_pass": seeds,
                            "seeds_fail": fails,
                            "mean_deg": (float(np.mean(list(vals.values()))) if vals else None),
                            "sd_deg": (float(np.std(list(vals.values()), ddof=1))
                                       if len(vals) > 1 else None)}
    rungs_out = []
    for k in range(len(SP_RUNGS)):
        st, wt = SP_RUNGS[k][0], WK_RUNGS[k][0]
        a, b = per["spastic"][st], per["weakness"][wt]
        rep = a["n_gate_G"] >= 4 and b["n_gate_G"] >= 4
        gap = (abs(a["mean_deg"] - b["mean_deg"]) if rep else None)
        rungs_out.append({
            "rung_index": k, "spastic_KV": SP_RUNGS[k][1], "weakness_scale": WK_RUNGS[k][1],
            "spastic_n_gate_G": a["n_gate_G"], "weakness_n_gate_G": b["n_gate_G"],
            "reportable": bool(rep),
            "why_not": (None if rep else
                        "needs >= 4 Gate-G seeds on BOTH axes; spastic %d, weakness %d"
                        % (a["n_gate_G"], b["n_gate_G"])),
            "spastic_mean_deg": a["mean_deg"], "weakness_mean_deg": b["mean_deg"],
            "gap_deg": gap,
            "signed_gap_spastic_minus_weakness_deg":
                ((a["mean_deg"] - b["mean_deg"]) if rep else None),
            "reaches_MDC_3.8": (bool(gap >= MDC_DEG) if gap is not None else None)})
    reached = [r for r in rungs_out if r.get("reaches_MDC_3.8")]
    out = {"arm": "CHAIN_r400_HEADLINE",
           "written_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "endpoint": ("mean ankle_angle_l over stance samples of the admissible cycles, "
                        "degrees; corpus convention SETTLE 1.00, T1 9.73, cycles wholly inside "
                        "the window, drop the last kept cycle, require >= 5, stance = "
                        "leg0_l.grf_norm_y > 0.05"),
           "gap": "|mean(spastic rung k) - mean(weakness rung k)| over Gate-G seeds",
           "reportability_rule": "both axes must have >= 4 Gate-G seeds at that rung",
           "clinical_floor_deg": MDC_DEG,
           "per_axis": per,
           "rungs": rungs_out,
           "any_rung_reaches_MDC": bool(reached),
           "rungs_reaching_MDC": [r["rung_index"] for r in reached]}
    p = os.path.join(PAPER, "CHAIN_HEADLINE_r400.json")
    wopen(p).write(json.dumps(out, indent=1) + "\n")
    print("\nRUNG  KV      xFmax   nS  nW   spastic   weakness    gap   >=3.8")
    for r in rungs_out:
        print("  %d   %-6.3f  %-6.2f  %-2d  %-2d   %-9s %-9s  %-6s %s"
              % (r["rung_index"], r["spastic_KV"], r["weakness_scale"],
                 r["spastic_n_gate_G"], r["weakness_n_gate_G"],
                 ("%.3f" % r["spastic_mean_deg"]) if r["spastic_mean_deg"] is not None else "-",
                 ("%.3f" % r["weakness_mean_deg"]) if r["weakness_mean_deg"] is not None else "-",
                 ("%.3f" % r["gap_deg"]) if r["gap_deg"] is not None else "n/r",
                 r["reaches_MDC_3.8"]))
    print("\nany rung reaching the %.1f deg MDC floor: %s" % (MDC_DEG, bool(reached)))
    print("deposited %s (%d bytes)" % (p, os.path.getsize(p)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--rest", action="store_true")
    ap.add_argument("--headline", action="store_true")
    ap.add_argument("--aggregate", action="store_true")
    a = ap.parse_args()
    if a.stage:
        stage()
        return
    if a.cell is not None:
        r = run_cell(a.cell)
        print(json.dumps({k: v for k, v in r.items()
                          if k not in ("stdout_tail", "stderr_tail")}, indent=1))
        return
    if a.rest:
        rest()
        return
    if a.aggregate:
        out, p = aggregate()
        print("deposited %s (%d bytes)" % (p, os.path.getsize(p)))
        return
    if a.headline:
        headline()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
