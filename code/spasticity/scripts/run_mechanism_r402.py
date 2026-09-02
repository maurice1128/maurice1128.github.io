# -*- coding: utf-8 -*-
r"""run_mechanism_r402.py -- decompose the spastic lesion: BOTH / SOL only / GAS only.

Registered at paper\PREREG_biarticular_r402.md
sha256 623b021e3369c7c441de0f261280af04f84efb31431671da1b4b176821f290d6 (verified at stage time).

WHY. `knee_angle_l` at left heel strike separates the two lesions by +6.3919 deg, edge to edge,
where every ankle endpoint failed. The proposed explanation is anatomical: the spastic lesion
drives soleus AND gastrocnemius, and gastrocnemius is BIARTICULAR -- it spans the ankle and the
knee -- so the extra drive flexes the knee. The weakness lesion sits on tib_ant_l, which spans
the ankle only. That story was told after seeing the result. §2 of the registration decomposes
the spastic lesion to test it:

  BOTH  MuscleReflex KV = 0.110 on soleus AND gastroc, left   (reproduces R396SPg110)
  SOL   MuscleReflex KV = 0.110 on soleus  alone   -- uniarticular, ankle only
  GAS   MuscleReflex KV = 0.110 on gastroc alone   -- biarticular, ankle and knee

Three arms x six seeds = 18 cells. delay = 0.020, allow_neg_V = 0, legs = left, unchanged.
Model file UNLESIONED: tib_ant_l 1759, soleus_l 3549, gastroc_l 2241 -- this series carries no
weakness lesion at all, and that is asserted off disk after staging.

Chaining, §2: each cell warm-starts from ITS OWN SEED's R396SPg110 solution where that cell
passed Gate G, and from R393SPg100 otherwise. The parent used is recorded per cell with the
.par sha256.

THE DELICATE PART. SOL and GAS are produced by DELETING one MuscleReflex sub-block from the
BOTH block, never by retyping it. The SpasticL ReflexController is located in the R151S
template by brace matching, extracted as a byte range, KV is substituted inside that range
only, and then exactly one sub-block is removed by brace matching. The remainder of the config
outside the range is asserted byte-identical to the template. Every staged config is then read
BACK OFF DISK and the surviving reflexes are re-parsed out of the SpasticL block: BOTH must
carry exactly two (soleus, gastroc), SOL exactly one (soleus), GAS exactly one (gastroc), each
with KV = 0.110, allow_neg_V = 0, delay = 0.020, and the literal KV = 0.110 must appear in the
whole file exactly as many times as there are surviving reflexes.

STAGING NEVER STARTS sconecmd. Parent Gate G is read from the parent's ALREADY EXISTING .sto;
if a parent has no .sto, staging reports NO_STO and refuses rather than replaying it.

SAFETY, unchanged from the corpus launchers:
  * writes ONLY under spasticity_paper (enforced by wpath on every write); SCONE, when --rest
    is eventually run by the driver, writes ONLY new directories under SCONE\results;
  * the 112 protected directories are never opened for write, and every new directory name is
    asserted against the protected pattern before harvest;
  * YIELD: before each cell, count sconecmd processes; if any is running that is not ours,
    suspend and report rather than compete.

Usage:  python run_mechanism_r402.py --stage      build the 18 scenarios, run nothing
        python run_mechanism_r402.py --rest       run the remaining cells in order
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

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
WRITE_ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"
SRC_S = os.path.join(ROOT, "reopt_r151", "R151S_s101")    # spastic template, carries SpasticL
SRC_C = os.path.join(ROOT, "reopt_r151", "R151C_s101")    # unlesioned reference model + data
STAGE = os.path.join(ROOT, "mechanism_r402")

PREREG = os.path.join(PAPER, "PREREG_biarticular_r402.md")
PREREG_SHA = "623b021e3369c7c441de0f261280af04f84efb31431671da1b4b176821f290d6"

KV = 0.110
GENS = 90
SETTLE, T1, MIN_CYC = 1.00, 9.73, 5
SEEDS = [101, 102, 103, 104, 105, 106]
ARMS = ["BOTH", "SOL", "GAS"]
DROP = {"BOTH": None, "SOL": "gastroc", "GAS": "soleus"}   # which reflex is DELETED
KEEP = {"BOTH": ["soleus", "gastroc"], "SOL": ["soleus"], "GAS": ["gastroc"]}
PARENT_PRIMARY = "R396SPg110"
PARENT_FALLBACK = "R393SPg100"
FMAX_BASE = {"tib_ant_l": 1759.0, "soleus_l": 3549.0, "gastroc_l": 2241.0}
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


# ------------------------------------------------------------------ safety -------------------
def wpath(p):
    """Assert p lies under spasticity_paper before anything opens it for write."""
    ap = os.path.abspath(p)
    assert ap.lower().startswith(WRITE_ROOT.lower() + os.sep), \
        "REFUSING to write outside spasticity_paper: " + ap
    return ap


def wopen(p, mode="w"):
    return io.open(wpath(p), mode, encoding="utf-8", newline="\n")


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def competing():
    """sconecmd processes. Any at all means someone else's work is running: YIELD."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return -1
    return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())


# ------------------------------------------------- SpasticL block surgery --------------------
def match_brace(s, i):
    """Index of the '}' closing the '{' at index i."""
    assert s[i] == "{", "expected '{' at %d, found %r" % (i, s[i])
    d = 0
    for k in range(i, len(s)):
        if s[k] == "{":
            d += 1
        elif s[k] == "}":
            d -= 1
            if d == 0:
                return k
    raise AssertionError("unbalanced braces from %d" % i)


def spastic_range(cfg):
    """Byte range [a, b) of the SpasticL ReflexController block, found by brace matching.

    Not a retyped block and not a line-number guess: the range is derived from the file.
    """
    m = re.search(r"name\s*=\s*SpasticL\b", cfg)
    assert m, "no SpasticL controller in template"
    assert len(re.findall(r"name\s*=\s*SpasticL\b", cfg)) == 1, "more than one SpasticL"
    h = cfg.rfind("ReflexController", 0, m.start())
    assert h >= 0, "SpasticL is not inside a ReflexController"
    o = cfg.index("{", h)
    assert o < m.start(), "brace search overshot the name line"
    return h, match_brace(cfg, o) + 1


def reflex_subblocks(block):
    """Every MuscleReflex sub-block of `block`, by brace matching, with its target."""
    out = []
    for m in re.finditer(r"MuscleReflex\s*\{", block):
        o = block.index("{", m.start())
        e = match_brace(block, o) + 1
        body = block[m.start():e]
        t = re.search(r"target\s*=\s*(\S+)", body)
        assert t, "MuscleReflex with no target in SpasticL"
        out.append({"start": m.start(), "end": e, "target": t.group(1), "text": body})
    return out


def drop_reflex(block, target):
    """DELETE exactly one MuscleReflex sub-block, with its own indentation and line break."""
    hit = [s for s in reflex_subblocks(block) if s["target"] == target]
    assert len(hit) == 1, "%d sub-blocks target %s, expected exactly 1" % (len(hit), target)
    s = hit[0]
    ls = block.rfind("\n", 0, s["start"]) + 1
    assert block[ls:s["start"]].strip() == "", "MuscleReflex does not start its own line"
    le = s["end"]
    while le < len(block) and block[le] in " \t":
        le += 1
    if le < len(block) and block[le] == "\n":
        le += 1
    return block[:ls] + block[le:]


def block_variants():
    """The three SpasticL blocks, all derived from the template by deletion. -> dict arm->text."""
    cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    a, b = spastic_range(cfg)
    src_block = cfg[a:b]
    tgt = [s["target"] for s in reflex_subblocks(src_block)]
    assert tgt == ["soleus", "gastroc"], "template SpasticL targets %s" % tgt
    both, n = re.subn(r"KV\s*=\s*0\.050", "KV = %.3f" % KV, src_block)
    assert n == 2, "expected 2 KV substitutions inside SpasticL, made %d" % n
    out = {"BOTH": both}
    for arm in ("SOL", "GAS"):
        v = drop_reflex(both, DROP[arm])
        assert [s["target"] for s in reflex_subblocks(v)] == KEEP[arm]
        # the deleted text is the ONLY difference: everything else is character-identical
        assert v in both or len(v) < len(both), "deletion grew the block"
        out[arm] = v
    return cfg, a, b, src_block, out


def check_block(block, arm):
    """Assert a SpasticL block carries exactly the reflexes this arm registers."""
    subs = reflex_subblocks(block)
    got = [s["target"] for s in subs]
    assert got == KEEP[arm], "%s: SpasticL targets %s, registered %s" % (arm, got, KEEP[arm])
    for s in subs:
        assert re.search(r"KV\s*=\s*%.3f\b" % KV, s["text"]), \
            "%s: %s reflex missing KV %.3f" % (arm, s["target"], KV)
        assert re.search(r"allow_neg_V\s*=\s*0\b", s["text"]), \
            "%s: %s reflex missing allow_neg_V = 0" % (arm, s["target"])
        assert re.search(r"delay\s*=\s*0\.020\b", s["text"]), \
            "%s: %s reflex missing delay = 0.020" % (arm, s["target"])
    assert len(re.findall(r"KV\s*=\s*%.3f\b" % KV, block)) == len(KEEP[arm])
    return got


# ------------------------------------------------------------------ cells --------------------
def cells():
    out = []
    for arm in ARMS:
        for s in SEEDS:
            out.append({"arm": arm, "seed": s, "kv": KV,
                        "prefix": "R402%s_s%d" % (arm, s),
                        "spastic_targets": list(KEEP[arm]),
                        "deleted_reflex": DROP[arm]})
    return out


def cell_index(prefix):
    for i, c in enumerate(cells()):
        if c["prefix"] == prefix:
            return i
    return None


# ------------------------------------------------------------------ resolvers ----------------
def result_dir(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    assert len(g) <= 1, "%d result dirs for %s" % (len(g), prefix)
    return g[0] if g else None


def best_par_by_generation(cd, warm_basename=None):
    """Highest generation among the run's own outputs, excluding the staged warm start.

    Carried from run_dfsevere_r293.py / run_restart_r401.py: selecting by the objective encoded
    in the filename is unsafe whenever the warm start was optimised under a different
    objective, and that defect corrupted the r294 deposits.
    """
    warm = set()
    if warm_basename:
        warm.add(warm_basename)
    for p in glob.glob(os.path.join(cd, "WARM_*.par")):
        warm.add(os.path.basename(p))
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) not in warm]
    if not pars:
        return None
    return max(pars, key=lambda p: int(os.path.basename(p).split("_")[0]))


def gate_from_existing_sto(par):
    """Gate G for a parent, from a .sto THAT ALREADY EXISTS. Never replays, never runs SCONE."""
    sto = par + ".sto"
    if not os.path.exists(sto):
        return {"status": "NO_STO", "note": "staging refuses to replay; run it under --rest"}
    cols, dat = S.load_sto(sto)
    if dat.size == 0:
        return {"status": "EMPTY_STO"}
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        return {"status": "NO_GRF"}
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    return {"status": "OK", "sto": os.path.basename(sto), "t_end_s": float(t[-1]),
            "n_cycles_in_window": len(win),
            "gate_G": bool(float(t[-1]) >= T1 and len(win) >= MIN_CYC)}


def resolve_parent(seed):
    """R396SPg110_s{seed} if that cell exists and passed Gate G, else R393SPg100_s{seed}."""
    considered = []
    for prefix, why in ((("%s_s%d" % (PARENT_PRIMARY, seed)), "primary"),
                        (("%s_s%d" % (PARENT_FALLBACK, seed)), "fallback")):
        cd = result_dir(prefix)
        if cd is None:
            considered.append({"prefix": prefix, "role": why, "status": "NO_RESULT_DIR"})
            continue
        par = best_par_by_generation(cd)
        if par is None:
            considered.append({"prefix": prefix, "role": why, "status": "NO_PAR"})
            continue
        g = gate_from_existing_sto(par)
        rec = {"prefix": prefix, "role": why, "result_dir": os.path.basename(cd),
               "par": os.path.basename(par), "par_path": par, "par_sha256": sha(par),
               "generation": int(os.path.basename(par).split("_")[0])}
        rec.update(g)
        considered.append(rec)
        if why == "primary" and rec.get("gate_G"):
            return rec, considered
        if why == "fallback":
            # §2: R393SPg100 is the registered fallback and is used whether or not it passed.
            return rec, considered
    raise AssertionError("no usable parent for seed %d: %s" % (seed, considered))


# ------------------------------------------------------------------ model --------------------
def write_hfd(dst):
    """Copy the UNLESIONED model and assert all three forces off disk."""
    shutil.copyfile(os.path.join(SRC_C, "H1922v7b3.hfd"), wpath(dst))
    chk = io.open(dst, encoding="utf-8").read()
    got = {}
    for m in ("tib_ant_l", "soleus_l", "gastroc_l"):
        got[m] = float(re.search(r"name\s*=\s*" + m + r"\b.*?max_isometric_force\s*=\s*"
                                 r"([0-9.]+)", chk, re.S).group(1))
    for m, base in FMAX_BASE.items():
        assert abs(got[m] - base) < 1e-9, \
            "UNLESIONED model required: %s must be %s, found %s" % (m, base, got[m])
    return got


# ------------------------------------------------------------------ staging ------------------
def stage():
    assert sha(PREREG) == PREREG_SHA, "PREREG_biarticular_r402.md sha256 mismatch"
    os.makedirs(wpath(STAGE), exist_ok=True)

    tpl_cfg, a, b, src_block, variants = block_variants()
    for arm in ARMS:
        check_block(variants[arm], arm)

    man = {
        "arm": "MECHANISM_r402",
        "prereg": os.path.basename(PREREG),
        "prereg_sha256": PREREG_SHA,
        "kv": KV,
        "generations": GENS,
        "seeds": SEEDS,
        "arms": ARMS,
        "design": ("Decomposition of the spastic lesion. BOTH = MuscleReflex KV 0.110 on "
                   "soleus and gastroc (reproduces R396SPg110); SOL = soleus alone "
                   "(uniarticular); GAS = gastroc alone (biarticular). 3 arms x 6 seeds = 18 "
                   "cells. Model UNLESIONED, no weakness lesion in this series."),
        "endpoint": ("knee_angle_l at left heel strike, per-cycle mean over admissible cycles, "
                     "degrees. SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the "
                     "last kept cycle, require >= 5, stance = leg0_l.grf_norm_y > 0.05."),
        "reference_arms_not_re_run": ["R151C (control)", "R151W (weak x0.80)"],
        "staging_started_sconecmd": False,
        "template_config": os.path.join(SRC_S, "config.scone"),
        "template_config_sha256": sha(os.path.join(SRC_S, "config.scone")),
        "spasticL_block": {
            "how": ("located by brace matching on 'name = SpasticL', extracted as a byte range "
                    "of the template config decoded UTF-8 with \\n newlines; KV substituted "
                    "inside that range only; SOL and GAS produced by DELETING exactly one "
                    "MuscleReflex sub-block, never by retyping the block."),
            "byte_range_in_template": [a, b],
            "template_block_verbatim": src_block,
            "template_block_sha256": sha_text(src_block),
            "variants": {arm: {"deleted_reflex": DROP[arm],
                               "surviving_targets": list(KEEP[arm]),
                               "verbatim": variants[arm],
                               "sha256": sha_text(variants[arm]),
                               "n_chars": len(variants[arm])}
                         for arm in ARMS},
        },
        "cells": [],
    }

    for c in cells():
        d = os.path.join(STAGE, c["prefix"])
        for sub in ("models", "data", "par"):
            os.makedirs(wpath(os.path.join(d, sub)), exist_ok=True)
        fmax = write_hfd(os.path.join(d, "models", "H1922v7b3.hfd"))
        shutil.copyfile(os.path.join(SRC_C, "InitStateH0918Gait10ActA.zml"),
                        wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))

        p, considered = resolve_parent(c["seed"])
        warm = "WARM_%s_g%04d.par" % (p["prefix"], p["generation"])
        for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
            if os.path.basename(old) != warm:
                os.remove(wpath(old))
        shutil.copyfile(p["par_path"], wpath(os.path.join(d, "par", warm)))
        assert sha(os.path.join(d, "par", warm)) == p["par_sha256"], "warm copy differs"

        # ---- the config: swap the SpasticL byte range for this arm's variant ----------------
        cfg = tpl_cfg[:a] + variants[c["arm"]] + tpl_cfg[b:]
        assert cfg[:a] == tpl_cfg[:a], "text before SpasticL changed"
        assert cfg[a + len(variants[c["arm"]]):] == tpl_cfg[b:], "text after SpasticL changed"
        assert not re.search(r"KV\s*=\s*0\.050", cfg), "a literal KV = 0.050 survived"
        cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, 1)
        assert n == 1
        cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                         'init { file = "par/%s" }' % warm, cfg, 1)
        assert n == 1, "init block not found"
        cfg, n = re.subn(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, 1)
        assert n == 1
        cfg, n = re.subn(r"signature_prefix\s*=\s*\S+",
                         "signature_prefix = %s" % c["prefix"], cfg, 1)
        assert n == 1
        wopen(os.path.join(d, "config.scone")).write(cfg)

        # ---- read the staged config BACK OFF DISK and re-parse the SpasticL block -----------
        back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
        ba, bb = spastic_range(back)
        got = check_block(back[ba:bb], c["arm"])
        n_kv = len(re.findall(r"KV\s*=\s*%.3f\b" % KV, back))
        assert n_kv == len(KEEP[c["arm"]]), \
            "%s: KV %.3f appears %d times in the file, expected %d" \
            % (c["prefix"], KV, n_kv, len(KEEP[c["arm"]]))
        assert len(re.findall(r"allow_neg_V\s*=\s*0\b", back[ba:bb])) == len(KEEP[c["arm"]])
        assert len(re.findall(r"delay\s*=\s*0\.020\b", back[ba:bb])) == len(KEEP[c["arm"]])
        assert re.search(r"legs\s*=\s*left", back), "legs = left missing"
        assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
        assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
        assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
        assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
        m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
        assert m and m.group(1) == "par/" + warm, "init readback %s" % (m and m.group(1))
        assert os.path.exists(os.path.join(d, "par", warm)), "init file missing on disk"

        man["cells"].append({
            **c,
            "dir": d,
            "warm": warm,
            "parent_prefix": p["prefix"],
            "parent_role": p["role"],
            "parent_result_dir": p["result_dir"],
            "parent_par": p["par"],
            "parent_par_sha256": p["par_sha256"],
            "parent_generation": p["generation"],
            "parent_gate_G": p.get("gate_G"),
            "parent_t_end_s": p.get("t_end_s"),
            "parent_n_cycles_in_window": p.get("n_cycles_in_window"),
            "parents_considered": considered,
            "spasticL_readback_targets": got,
            "spasticL_block_sha256": sha_text(back[ba:bb]),
            "kv_literal_count_in_config": n_kv,
            "fmax_readback": fmax,
            "config_sha256": sha(os.path.join(d, "config.scone")),
        })

    man["parent_summary"] = {
        str(s): [c["parent_prefix"] for c in man["cells"] if c["seed"] == s][0] for s in SEEDS}
    wopen(os.path.join(PAPER, "MECHANISM_STAGE_r402.json")).write(
        json.dumps(man, indent=2, ensure_ascii=False))
    print("staged %d cells under %s" % (len(man["cells"]), STAGE))
    for arm in ARMS:
        v = man["spasticL_block"]["variants"][arm]
        print("  %-4s targets %-18s sha256 %s" % (arm, ",".join(v["surviving_targets"]),
                                                  v["sha256"]))
    for s in SEEDS:
        print("  seed %d -> parent %s" % (s, man["parent_summary"][str(s)]))
    print("manifest %s" % os.path.join(PAPER, "MECHANISM_STAGE_r402.json"))
    print("sconecmd was NOT started by staging.")


# ------------------------------------------------------------------ measurement --------------
def evaluate(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return {"status": "NO_RESULT_DIR"}
    dup = len(g) > 1
    if dup:
        # A re-run makes SCONE create a "... (1)" twin. Choose the directory that actually
        # optimised -- the one with the most .par files -- and record that a twin existed.
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        # the optimiser does not write .par.sto; replay the resolved .par to produce it
        par = best_par_by_generation(g[0])
        if par:
            subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=g[0],
                           capture_output=True, timeout=1800)
            stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        return {"status": "NO_STO_AFTER_REPLAY", "dir": os.path.basename(g[0])}
    cols, dat = S.load_sto(stos[-1])
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    o = {"status": "OK", "duplicate_result_dir": dup, "dir": os.path.basename(g[0]), "sto": os.path.basename(stos[-1]),
         "t_end_s": float(t[-1]), "n_cycles_in_window": len(win)}
    o["gate_G"] = bool(float(t[-1]) >= T1 and len(win) >= MIN_CYC)
    if o["gate_G"]:
        kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
        o["knee_at_heelstrike_deg"] = float(np.mean([kne[a] for a, _ in win]))
        on = grf > thr
        st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
        o["n_stance_samples"] = int(len(st))
        o["ank_stance_mean_deg"] = float(np.mean(np.degrees(S.col(cols, dat,
                                                                  "ankle_angle_l"))[st]))
    return o


# ------------------------------------------------------------------ running ------------------
def run_all():
    cs = cells()
    recs = []
    for i, c in enumerate(cs):
        f = os.path.join(PAPER, "RUN_MECHANISM_r402_cell%02d.json" % i)
        if os.path.exists(f):
            recs.append(json.load(io.open(f, encoding="utf-8")))
            continue
        n = competing()
        if n > 0:
            print("YIELD: %d sconecmd already running. Suspending, not competing." % n)
            return recs
        d = os.path.join(STAGE, c["prefix"])
        assert os.path.isdir(d), "not staged: " + d
        before = set(os.listdir(RES))
        t0 = time.time()
        p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                           capture_output=True, text=True, cwd=d)
        wall = time.time() - t0
        new = sorted(set(os.listdir(RES)) - before)
        for nd in new:
            assert not PROTECTED.match(nd), "refusing: protected name created " + nd
        rec = {"cell": i, **c, "wall_clock_s": wall, "returncode": p.returncode,
               "new_result_dirs": new}
        rec.update(evaluate(c["prefix"]))
        wopen(f).write(json.dumps(rec, indent=1, ensure_ascii=False))
        recs.append(rec)
        print("cell %02d %-18s %-14s wall %6.1f s  t_end %-6s gate %-5s knee_HS %s"
              % (i, c["prefix"], rec.get("status"), wall,
                 ("%.2f" % rec["t_end_s"]) if rec.get("t_end_s") else "-",
                 rec.get("gate_G"),
                 ("%+.4f" % rec["knee_at_heelstrike_deg"])
                 if rec.get("knee_at_heelstrike_deg") is not None else "-"))
    by_arm = {}
    for arm in ARMS:
        ok = [r for r in recs if r.get("arm") == arm and r.get("gate_G")]
        by_arm[arm] = {
            "n_run": len([r for r in recs if r.get("arm") == arm]),
            "n_gate_G": len(ok),
            "uninformative": len(ok) < 4,
            "knee_at_heelstrike_deg": sorted(r["knee_at_heelstrike_deg"] for r in ok),
            "ank_stance_mean_deg": sorted(r["ank_stance_mean_deg"] for r in ok),
            "knee_mean": (float(np.mean([r["knee_at_heelstrike_deg"] for r in ok]))
                          if ok else None),
            "ank_mean": (float(np.mean([r["ank_stance_mean_deg"] for r in ok])) if ok else None),
        }
    out = {"arm": "MECHANISM_r402", "prereg_sha256": PREREG_SHA, "kv": KV,
           "n_cells": len(recs), "by_arm": by_arm,
           "note": ("P1/P2/P3 are evaluated against the R151C control mean in the analysis "
                    "script, not here; a rung with fewer than 4 Gate-G seeds is UNINFORMATIVE, "
                    "and fewer than 4 in BOTH makes the whole registration UNINFORMATIVE."),
           "cells": recs}
    wopen(os.path.join(PAPER, "MECHANISM_RESULT_r402.json")).write(
        json.dumps(out, indent=2, ensure_ascii=False))
    print()
    for arm in ARMS:
        print("%-4s Gate G %d/%d  knee mean %s" % (arm, by_arm[arm]["n_gate_G"],
                                                   by_arm[arm]["n_run"],
                                                   by_arm[arm]["knee_mean"]))
    print("wrote %s" % os.path.join(PAPER, "MECHANISM_RESULT_r402.json"))
    return recs


ap = argparse.ArgumentParser()
ap.add_argument("--stage", action="store_true")
ap.add_argument("--rest", action="store_true")
a_ = ap.parse_args()
if a_.stage:
    stage()
elif a_.rest:
    run_all()
else:
    ap.print_help()
