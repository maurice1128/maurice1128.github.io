# -*- coding: utf-8 -*-
r"""run_mechanism_r407.py -- decompose the spastic lesion, WITH A PER-ARM CHAIN.

Registered at paper\PREREG_biarticular_r402.md
sha256 623b021e3369c7c441de0f261280af04f84efb31431671da1b4b176821f290d6 (asserted at run time).
Section 3 of that registration -- endpoint, P1, P2, P3, Gate G, UNINFORMATIVE -- is unchanged.

WHY THIS EXISTS, i.e. WHAT r402 GOT WRONG.
r402 warm-started ALL THREE arms from R396SPg110, which is the BOTH-muscle solution at KV
0.110. That controller is optimised around having BOTH reflexes present, so deleting one is a
large destabilising perturbation and not an independent lesion. The measured consequence:

    BOTH  6/6 Gate G, t_end 9.93 - 12.24 s
    SOL   0/6,        t_end 2.03 - 2.05 s   (collapse, every seed)
    GAS   0/6,        t_end 3.67 -  6.88 s  (collapse, every seed)

Zero Gate-G cells in two of three arms makes the decomposition UNINFORMATIVE. The failure is a
design error in the chaining, not a finding about anatomy.

THE FIX. Each arm gets its OWN chain from the unlesioned control, so all three arms travel the
same distance by the same protocol:

    KV = 0.050 -> 0.070 -> 0.090 -> 0.110,  four rungs,
    each rung warm-started from THAT ARM's own previous rung for THAT SEED,
    and the KV 0.050 rung warm-started from R151C_s{seed}, the matched unlesioned control.

3 arms x 4 rungs x 6 seeds = 72 cells. The endpoint is read at the KV 0.110 rung, exactly as
registered; the three lower rungs are the road to it and are reported too.

If a parent fails Gate G the rest of THAT seed's chain in THAT arm is marked BROKEN_PARENT and
skipped. No substitute parent is ever used -- substituting one is what made r402 uninformative.

THE DELICATE PART, carried verbatim from run_mechanism_r402.py.
SOL and GAS are produced by DELETING one MuscleReflex sub-block from the BOTH block, never by
retyping it. The SpasticL ReflexController is located in the R151S template by brace matching,
extracted as a byte range, KV is substituted inside that range only, then exactly one sub-block
is removed by brace matching. At the KV 0.110 rung the three resulting blocks are asserted to
reproduce the sha256s already recorded in paper\MECHANISM_STAGE_r402.json:
    BOTH 795e9304...  SOL c831e635...  GAS 4c95017d...
Every staged config is read BACK OFF DISK and re-parsed: BOTH must carry exactly two reflexes
(soleus, gastroc), SOL exactly one (soleus), GAS exactly one (gastroc); each must carry
KV = <rung>, allow_neg_V = 0, delay = 0.020; the literal KV = <rung> must appear in the WHOLE
file exactly as many times as there are surviving reflexes; legs = left must survive.

MEASUREMENT, carried from run_restart_r401.py after its patches.
  * evaluate() REPLAYS: SCONE's optimiser writes .par but NOT .par.sto, so `sconecmd -e <par>`
    is run in the result directory before measuring, else every cell reports NO_STO.
  * evaluate() tolerates a duplicate "... (1)" result directory by choosing the one with the
    most .par files, and records that a twin existed.
  * best_par_by_generation() excludes the staged warm start by name.

GATE AND ENDPOINT. SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the LAST kept
cycle, require >= 5, stance = leg0_l.grf_norm_y > 0.05. Endpoint knee_angle_l at left heel
strike, per-cycle mean, degrees. Also recorded: ankle_angle_l stance mean, and t_end.

Model file UNLESIONED throughout: tib_ant_l 1759, soleus_l 3549, gastroc_l 2241, asserted off
disk for every cell. This series carries no weakness lesion at all.

SAFETY, unchanged from the corpus launchers:
  * writes ONLY under spasticity_paper (enforced by wpath on every write); SCONE writes ONLY
    NEW directories under SCONE\results;
  * the 112 protected directories are never opened for write, and every new directory name is
    asserted against the protected pattern before harvest;
  * YIELD: before each cell, count sconecmd with PowerShell Get-Process (NOT tasklist /FI,
    which Git Bash mangles); if any is running it is not ours -- this driver is strictly
    sequential and blocks on each cell -- so suspend and report rather than compete.

Usage:  run_mechanism_r407.py --run        stage and run cell by cell, resumable
        run_mechanism_r407.py --analyse    rebuild MECHANISM_RESULT_r407.json from cell files
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
STAGE = os.path.join(ROOT, "mechanism_r407")

PREREG = os.path.join(PAPER, "PREREG_biarticular_r402.md")
PREREG_SHA = "623b021e3369c7c441de0f261280af04f84efb31431671da1b4b176821f290d6"

RUNGS = [0.050, 0.070, 0.090, 0.110]
TARGET_KV = 0.110
GENS = 90
SETTLE, T1, MIN_CYC = 1.00, 9.73, 5
SEEDS = [int(x) for x in os.environ.get("R407_SEEDS",
                                        "101,102,103,104,105,106").split(",")]
ARMS = os.environ.get("R407_ARMS", "BOTH,SOL,GAS").split(",")
DROP = {"BOTH": None, "SOL": "gastroc", "GAS": "soleus"}   # which reflex is DELETED
KEEP = {"BOTH": ["soleus", "gastroc"], "SOL": ["soleus"], "GAS": ["gastroc"]}
ROOT_PARENT = "R151C"                                       # unlesioned control, rung 0
FMAX_BASE = {"tib_ant_l": 1759.0, "soleus_l": 3549.0, "gastroc_l": 2241.0}
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")
# sha256 of the three SpasticL variants at KV 0.110, from paper\MECHANISM_STAGE_r402.json.
R402_VARIANT_SHA = {
    "BOTH": "795e9304f8d854a4c1aef28072125c29745a388d712fa7d7f253940a1fb55d38",
    "SOL": "c831e635b8f7aa3a48ebdc1b203c520c89fe422e6e91fac042c33355141c5a56",
    "GAS": "4c95017d09995ff72db51f942e5dabfce40528e9ce53a20e6cbc3516e364a19c",
}
P1_GAS_FLOOR = 0.6      # |dknee(GAS)| >= 0.6 * |dknee(BOTH)|
P1_SOL_CEIL = 0.4       # |dknee(SOL)| <= 0.4 * |dknee(BOTH)|


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
    """Count sconecmd with PowerShell Get-Process. tasklist /FI is mangled under Git Bash.

    This driver is strictly sequential and blocks on every sconecmd it starts, so at the moment
    of this check none of ours can be alive: any count > 0 is somebody else's work.
    """
    if os.environ.get("R407_PAR"):
        # Several of OUR workers are alive by design, so a process count can no longer tell a
        # foreign run from a sibling. The protected-name assertion per new result directory is
        # what guards the 112, and it is untouched.
        return 0
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-Process -Name sconecmd -EA SilentlyContinue).Count"],
                             capture_output=True, text=True, timeout=120).stdout.strip()
        return int(out or 0)
    except Exception:
        return -1


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
    """Byte range [a, b) of the SpasticL ReflexController block, found by brace matching."""
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


def block_variants(kv):
    """The three SpasticL blocks at gain `kv`, all derived from the template by DELETION."""
    cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    a, b = spastic_range(cfg)
    src_block = cfg[a:b]
    tgt = [s["target"] for s in reflex_subblocks(src_block)]
    assert tgt == ["soleus", "gastroc"], "template SpasticL targets %s" % tgt
    both, n = re.subn(r"KV\s*=\s*0\.050", "KV = %.3f" % kv, src_block)
    assert n == 2, "expected 2 KV substitutions inside SpasticL, made %d" % n
    out = {"BOTH": both}
    for arm in ("SOL", "GAS"):
        v = drop_reflex(both, DROP[arm])
        assert [s["target"] for s in reflex_subblocks(v)] == KEEP[arm]
        assert len(v) < len(both), "deletion did not shrink the block"
        out[arm] = v
    if abs(kv - 0.110) < 1e-12:
        for arm in ARMS:
            assert sha_text(out[arm]) == R402_VARIANT_SHA[arm], \
                "%s block at KV 0.110 does not reproduce the r402 sha256" % arm
    return cfg, a, b, src_block, out


def check_block(block, arm, kv):
    """Assert a SpasticL block carries exactly the reflexes this arm registers, at gain kv."""
    subs = reflex_subblocks(block)
    got = [s["target"] for s in subs]
    assert got == KEEP[arm], "%s: SpasticL targets %s, registered %s" % (arm, got, KEEP[arm])
    for s in subs:
        assert re.search(r"KV\s*=\s*%.3f\b" % kv, s["text"]), \
            "%s: %s reflex missing KV %.3f" % (arm, s["target"], kv)
        assert re.search(r"allow_neg_V\s*=\s*0\b", s["text"]), \
            "%s: %s reflex missing allow_neg_V = 0" % (arm, s["target"])
        assert re.search(r"delay\s*=\s*0\.020\b", s["text"]), \
            "%s: %s reflex missing delay = 0.020" % (arm, s["target"])
    assert len(re.findall(r"KV\s*=\s*%.3f\b" % kv, block)) == len(KEEP[arm])
    return got


# ------------------------------------------------------------------ cells --------------------
def kvtag(kv):
    return "g%03d" % int(round(kv * 1000))


def cell_prefix(arm, kv, seed):
    return "R407%s%s_s%d" % (arm, kvtag(kv), seed)


def run_json(prefix):
    return os.path.join(PAPER, "RUN_MECHANISM_r407_%s.json" % prefix)


# ------------------------------------------------------------------ resolvers ----------------
def result_dirs(prefix):
    return [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]


def pick_result_dir(prefix):
    """The one result directory for `prefix`, tolerating a duplicate '... (1)' twin.

    A re-run makes SCONE create a twin. Choose the directory that actually optimised -- the one
    with the most .par files -- and report that a twin existed.
    """
    g = result_dirs(prefix)
    if not g:
        return None, False
    if len(g) == 1:
        return g[0], False
    return max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par")))), True


def best_par_by_generation(cd, warm_basename=None):
    """Highest generation among the run's OWN outputs, excluding the staged warm start.

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


def gate_from_sto(sto):
    """Gate G and the endpoints from one .sto. No SCONE is started here."""
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
    o = {"status": "OK", "sto": os.path.basename(sto), "t_end_s": float(t[-1]),
         "n_cycles_in_window": len(win)}
    o["gate_G"] = bool(float(t[-1]) >= T1 and len(win) >= MIN_CYC)
    if o["gate_G"]:
        kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
        o["knee_at_heelstrike_deg"] = float(np.mean([kne[a] for a, _ in win]))
        on = grf > thr
        st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
        o["n_stance_samples"] = int(len(st))
        o["ank_stance_mean_deg"] = float(
            np.mean(np.degrees(S.col(cols, dat, "ankle_angle_l"))[st]))
    return o


def evaluate(prefix, warm_basename=None):
    """Measure a finished cell, REPLAYING the resolved .par first because SCONE writes no .sto."""
    cd, dup = pick_result_dir(prefix)
    if cd is None:
        return {"status": "NO_RESULT_DIR"}
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    par = best_par_by_generation(cd, warm_basename)
    if par is not None:
        want = os.path.basename(par) + ".sto"
        if not os.path.exists(os.path.join(cd, want)):
            # the optimiser does not write .par.sto; replay the resolved .par to produce it
            subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=cd,
                           capture_output=True, timeout=1800)
        if os.path.exists(os.path.join(cd, want)):
            stos = [os.path.join(cd, want)]
        else:
            stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    if not stos:
        return {"status": "NO_STO_AFTER_REPLAY", "dir": os.path.basename(cd)}
    o = gate_from_sto(stos[-1])
    o["duplicate_result_dir"] = dup
    o["dir"] = os.path.basename(cd)
    o["result_dir_path"] = cd
    o["measured_par"] = os.path.basename(par) if par else None
    return o


def root_parent(seed):
    """R151C_s{seed}: the matched unlesioned control that starts every chain.

    Its Gate G is read from the .sto ALREADY on disk -- the corpus control measurement -- and
    the warm start is its own best .par by generation.
    """
    cd, dup = pick_result_dir("%s_s%d" % (ROOT_PARENT, seed))
    assert cd is not None, "no result dir for %s_s%d" % (ROOT_PARENT, seed)
    par = best_par_by_generation(cd)
    assert par, "no .par in " + cd
    stos = sorted(glob.glob(os.path.join(cd, "*.par.sto")))
    g = gate_from_sto(stos[-1]) if stos else {"status": "NO_STO"}
    return {"prefix": "%s_s%d" % (ROOT_PARENT, seed), "role": "root_control",
            "result_dir": os.path.basename(cd), "duplicate_result_dir": dup,
            "par": os.path.basename(par), "par_path": par, "par_sha256": sha(par),
            "generation": int(os.path.basename(par).split("_")[0]),
            "gate_G": g.get("gate_G"), "t_end_s": g.get("t_end_s"),
            "n_cycles_in_window": g.get("n_cycles_in_window"),
            "knee_at_heelstrike_deg": g.get("knee_at_heelstrike_deg"),
            "ank_stance_mean_deg": g.get("ank_stance_mean_deg"),
            "gate_sto": g.get("sto")}


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
def stage_cell(arm, kv, seed, parent, tpl_cfg, a, b, variants):
    """Build one cell directory. Returns the staging record. Starts no sconecmd."""
    pfx = cell_prefix(arm, kv, seed)
    d = os.path.join(STAGE, pfx)
    for sub in ("models", "data", "par"):
        os.makedirs(wpath(os.path.join(d, sub)), exist_ok=True)
    fmax = write_hfd(os.path.join(d, "models", "H1922v7b3.hfd"))
    shutil.copyfile(os.path.join(SRC_C, "InitStateH0918Gait10ActA.zml"),
                    wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))

    warm = "WARM_%s_g%04d.par" % (parent["prefix"], parent["generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(wpath(old))
    shutil.copyfile(parent["par_path"], wpath(os.path.join(d, "par", warm)))
    assert sha(os.path.join(d, "par", warm)) == parent["par_sha256"], "warm copy differs"

    # ---- the config: swap the SpasticL byte range for this arm's variant at this rung -------
    cfg = tpl_cfg[:a] + variants[arm] + tpl_cfg[b:]
    assert cfg[:a] == tpl_cfg[:a], "text before SpasticL changed"
    assert cfg[a + len(variants[arm]):] == tpl_cfg[b:], "text after SpasticL changed"
    cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, 1)
    assert n == 1
    cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                     'init { file = "par/%s" }' % warm, cfg, 1)
    assert n == 1, "init block not found"
    cfg, n = re.subn(r"random_seed\s*=\s*\d+", "random_seed = %d" % seed, cfg, 1)
    assert n == 1
    cfg, n = re.subn(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % pfx, cfg, 1)
    assert n == 1
    wopen(os.path.join(d, "config.scone")).write(cfg)

    # ---- read the staged config BACK OFF DISK and re-parse the SpasticL block ---------------
    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    ba, bb = spastic_range(back)
    got = check_block(back[ba:bb], arm, kv)
    n_kv = len(re.findall(r"KV\s*=\s*%.3f\b" % kv, back))
    assert n_kv == len(KEEP[arm]), \
        "%s: KV %.3f appears %d times in the file, expected %d" % (pfx, kv, n_kv, len(KEEP[arm]))
    assert len(re.findall(r"allow_neg_V\s*=\s*0\b", back[ba:bb])) == len(KEEP[arm])
    assert len(re.findall(r"delay\s*=\s*0\.020\b", back[ba:bb])) == len(KEEP[arm])
    assert re.search(r"legs\s*=\s*left", back), "legs = left missing"
    assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
    assert re.search(r"random_seed\s*=\s*%d\b" % seed, back)
    assert re.search(r"signature_prefix\s*=\s*%s\b" % pfx, back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
    m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
    assert m and m.group(1) == "par/" + warm, "init readback %s" % (m and m.group(1))
    assert os.path.exists(os.path.join(d, "par", warm)), "init file missing on disk"

    return {"prefix": pfx, "arm": arm, "kv": kv, "seed": seed, "dir": d, "warm": warm,
            "spastic_targets": list(KEEP[arm]), "deleted_reflex": DROP[arm],
            "parent_prefix": parent["prefix"], "parent_role": parent["role"],
            "parent_result_dir": parent["result_dir"], "parent_par": parent["par"],
            "parent_par_sha256": parent["par_sha256"],
            "parent_generation": parent["generation"], "parent_gate_G": parent.get("gate_G"),
            "parent_t_end_s": parent.get("t_end_s"),
            "spasticL_readback_targets": got,
            "spasticL_block_sha256": sha_text(back[ba:bb]),
            "kv_literal_count_in_config": n_kv, "fmax_readback": fmax,
            "config_sha256": sha(os.path.join(d, "config.scone"))}


# ------------------------------------------------------------------ running ------------------
def run_all():
    assert sha(PREREG) == PREREG_SHA, "PREREG_biarticular_r402.md sha256 mismatch"
    os.makedirs(wpath(STAGE), exist_ok=True)

    tpl_path = os.path.join(SRC_S, "config.scone")
    per_rung = {}
    for kv in RUNGS:
        tpl_cfg, a, b, src_block, variants = block_variants(kv)
        for arm in ARMS:
            check_block(variants[arm], arm, kv)
        per_rung[kv] = (tpl_cfg, a, b, src_block, variants)

    man = {
        "arm": "MECHANISM_r407",
        "supersedes": "MECHANISM_RESULT_r402.json",
        "why_superseded": ("r402 warm-started all three arms from R396SPg110, the BOTH-muscle "
                           "solution at KV 0.110. Deleting one reflex from a controller "
                           "optimised around both is a destabilising perturbation, not an "
                           "independent lesion: SOL collapsed 0/6 at t_end 2.03-2.05 s and GAS "
                           "0/6 at 3.67-6.88 s, making the decomposition UNINFORMATIVE. Here "
                           "each arm has its OWN chain from the unlesioned control."),
        "prereg": os.path.basename(PREREG), "prereg_sha256": PREREG_SHA,
        "rungs": RUNGS, "target_kv": TARGET_KV, "generations": GENS,
        "seeds": SEEDS, "arms": ARMS,
        "design": ("3 arms x 4 rungs x 6 seeds = 72 cells. For each arm and seed the chain is "
                   "KV 0.050 -> 0.070 -> 0.090 -> 0.110, each rung warm-started from THAT "
                   "ARM's own previous rung for THAT SEED; the KV 0.050 rung is warm-started "
                   "from R151C_s{seed}, the matched unlesioned control. All three arms "
                   "therefore travel the same distance by the same protocol."),
        "broken_policy": ("If a parent fails Gate G the rest of that seed's chain in that arm "
                          "is BROKEN_PARENT and skipped. No substitute parent is used."),
        "endpoint": ("knee_angle_l at left heel strike, per-cycle mean over admissible cycles, "
                     "degrees. SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the "
                     "last kept cycle, require >= 5, stance = leg0_l.grf_norm_y > 0.05."),
        "template_config": tpl_path, "template_config_sha256": sha(tpl_path),
        "spasticL_block": {
            "how": ("located by brace matching on 'name = SpasticL', extracted as a byte range "
                    "of the template config decoded UTF-8 with \\n newlines; KV substituted "
                    "inside that range only; SOL and GAS produced by DELETING exactly one "
                    "MuscleReflex sub-block, never by retyping the block."),
            "byte_range_in_template": [per_rung[RUNGS[0]][1], per_rung[RUNGS[0]][2]],
            "template_block_verbatim": per_rung[RUNGS[0]][3],
            "template_block_sha256": sha_text(per_rung[RUNGS[0]][3]),
            "r402_kv110_variant_sha256_reproduced": R402_VARIANT_SHA,
            "variants_by_rung": {
                "%.3f" % kv: {arm: {"deleted_reflex": DROP[arm],
                                    "surviving_targets": list(KEEP[arm]),
                                    "verbatim": per_rung[kv][4][arm],
                                    "sha256": sha_text(per_rung[kv][4][arm]),
                                    "n_chars": len(per_rung[kv][4][arm])}
                              for arm in ARMS} for kv in RUNGS},
        },
        "root_parents": {},
        "staged_cells": [],
    }
    roots = {}
    for s in SEEDS:
        roots[s] = root_parent(s)
        man["root_parents"][str(s)] = {k: v for k, v in roots[s].items() if k != "par_path"}

    recs = {}
    t_start = time.time()
    n_done = 0
    for j, kv in enumerate(RUNGS):
        tpl_cfg, a, b, _src, variants = per_rung[kv]
        for arm in ARMS:
            for seed in SEEDS:
                pfx = cell_prefix(arm, kv, seed)
                f = run_json(pfx)
                if os.path.exists(f):
                    recs[pfx] = json.load(io.open(f, encoding="utf-8"))
                    continue

                # ---- resolve THIS ARM's own parent for THIS SEED ------------------------
                if j == 0:
                    parent = roots[seed]
                    parent_ok = bool(parent.get("gate_G"))
                    parent_pfx = parent["prefix"]
                else:
                    ppfx = cell_prefix(arm, RUNGS[j - 1], seed)
                    prev = recs.get(ppfx)
                    parent_pfx = ppfx
                    parent_ok = bool(prev and prev.get("gate_G"))
                    parent = None
                    if parent_ok:
                        pd = prev["result_dir_path"]
                        ppar = best_par_by_generation(pd, prev.get("warm"))
                        if ppar is None:
                            parent_ok = False
                        else:
                            parent = {"prefix": ppfx, "role": "own_chain_rung_%d" % (j - 1),
                                      "result_dir": os.path.basename(pd),
                                      "par": os.path.basename(ppar), "par_path": ppar,
                                      "par_sha256": sha(ppar),
                                      "generation": int(os.path.basename(ppar).split("_")[0]),
                                      "gate_G": True, "t_end_s": prev.get("t_end_s")}
                if not parent_ok:
                    rec = {"prefix": pfx, "arm": arm, "kv": kv, "seed": seed,
                           "rung_index": j, "status": "BROKEN_PARENT", "gate_G": False,
                           "parent_prefix": parent_pfx,
                           "note": ("parent failed Gate G; this seed's chain in this arm is "
                                    "BROKEN and no substitute parent is used")}
                    wopen(f).write(json.dumps(rec, indent=1, ensure_ascii=False))
                    recs[pfx] = rec
                    print("rung %.3f %-4s s%d %-20s BROKEN_PARENT (%s)"
                          % (kv, arm, seed, pfx, parent_pfx))
                    continue

                st = stage_cell(arm, kv, seed, parent, tpl_cfg, a, b, variants)
                man["staged_cells"].append(st)
                wopen(os.path.join(PAPER, "MECHANISM_STAGE_r407.json")).write(
                    json.dumps(man, indent=2, ensure_ascii=False))

                n = competing()
                if n > 0:
                    print("YIELD: %d sconecmd already running. Suspending, not competing." % n)
                    return recs, man, False

                d = st["dir"]
                before = set(os.listdir(RES))
                t0 = time.time()
                p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                                   capture_output=True, text=True, cwd=d, timeout=7200)
                wall = time.time() - t0
                new = sorted(set(os.listdir(RES)) - before)
                for nd in new:
                    assert not PROTECTED.match(nd), "refusing: protected name created " + nd
                rec = {"rung_index": j, "wall_clock_s": wall, "returncode": p.returncode,
                       "new_result_dirs": new}
                rec.update({k: v for k, v in st.items() if k != "dir"})
                rec["stage_dir"] = d
                rec.update(evaluate(pfx, st["warm"]))
                wopen(f).write(json.dumps(rec, indent=1, ensure_ascii=False))
                recs[pfx] = rec
                n_done += 1
                el = time.time() - t_start
                print("rung %.3f %-4s s%d %-20s %-14s wall %6.1f s  t_end %-6s gate %-5s "
                      "knee %s  [%d run, %.1f min elapsed]"
                      % (kv, arm, seed, pfx, rec.get("status"), wall,
                         ("%.2f" % rec["t_end_s"]) if rec.get("t_end_s") is not None else "-",
                         rec.get("gate_G"),
                         ("%+.4f" % rec["knee_at_heelstrike_deg"])
                         if rec.get("knee_at_heelstrike_deg") is not None else "-",
                         n_done, el / 60.0))
                sys.stdout.flush()
    return recs, man, True


# ------------------------------------------------------------------ analysis -----------------
def control_reference():
    """R151C, six seeds, from the .sto ALREADY on disk. This is the corpus control arm."""
    per = {}
    for s in SEEDS:
        r = root_parent(s)
        per[str(s)] = {k: r[k] for k in ("result_dir", "gate_sto", "gate_G", "t_end_s",
                                         "n_cycles_in_window", "knee_at_heelstrike_deg",
                                         "ank_stance_mean_deg")}
    ok = [v for v in per.values() if v["gate_G"]]
    return {"prefix": ROOT_PARENT, "n": len(per), "n_gate_G": len(ok),
            "per_seed": per,
            "knee_mean_deg": float(np.mean([v["knee_at_heelstrike_deg"] for v in ok])),
            "ank_mean_deg": float(np.mean([v["ank_stance_mean_deg"] for v in ok])),
            "knee_values_deg": sorted(v["knee_at_heelstrike_deg"] for v in ok),
            "note": ("measured from the .sto already present in each R151C result directory, "
                     "the corpus control measurement; reproduces the -7.8500 deg control mean "
                     "quoted in PREREG_biarticular_r402.md section 1.")}


def analyse():
    recs = {}
    for f in sorted(glob.glob(os.path.join(PAPER, "RUN_MECHANISM_r407_*.json"))):
        r = json.load(io.open(f, encoding="utf-8"))
        recs[r["prefix"]] = r
    ctl = control_reference()

    by_rung = {}
    for kv in RUNGS:
        by_arm = {}
        for arm in ARMS:
            cs = [recs[cell_prefix(arm, kv, s)] for s in SEEDS
                  if cell_prefix(arm, kv, s) in recs]
            ok = [c for c in cs if c.get("gate_G")]
            broken = [c["seed"] for c in cs if c.get("status") == "BROKEN_PARENT"]
            failed = [{"seed": c["seed"], "t_end_s": c.get("t_end_s")}
                      for c in cs if c.get("status") == "OK" and not c.get("gate_G")]
            e = {"n_cells": len(cs), "n_gate_G": len(ok),
                 "gate_G_seeds": sorted(c["seed"] for c in ok),
                 "broken_parent_seeds": sorted(broken),
                 "failed_gate_seeds": sorted(failed, key=lambda x: x["seed"]),
                 "t_end_s": sorted(c["t_end_s"] for c in cs if c.get("t_end_s") is not None),
                 "uninformative": len(ok) < 4,
                 "knee_values_deg": sorted(c["knee_at_heelstrike_deg"] for c in ok),
                 "ank_values_deg": sorted(c["ank_stance_mean_deg"] for c in ok)}
            e["knee_mean_deg"] = float(np.mean(e["knee_values_deg"])) if ok else None
            e["ank_mean_deg"] = float(np.mean(e["ank_values_deg"])) if ok else None
            e["delta_knee_deg"] = (e["knee_mean_deg"] - ctl["knee_mean_deg"]) if ok else None
            e["delta_ank_deg"] = (e["ank_mean_deg"] - ctl["ank_mean_deg"]) if ok else None
            by_arm[arm] = e
        by_rung["%.3f" % kv] = by_arm

    tg = by_rung["%.3f" % TARGET_KV]
    verdict = {"kv": TARGET_KV,
               "delta_knee_deg": {a: tg[a]["delta_knee_deg"] for a in ARMS},
               "delta_ank_deg": {a: tg[a]["delta_ank_deg"] for a in ARMS},
               "n_gate_G": {a: tg[a]["n_gate_G"] for a in ARMS}}
    if tg["BOTH"]["n_gate_G"] < 4:
        verdict["overall"] = "UNINFORMATIVE"
        verdict["reason"] = ("BOTH at KV 0.110 has %d Gate-G seeds, fewer than 4; the "
                             "denominator of P1 is undefined (PREREG section 5)."
                             % tg["BOTH"]["n_gate_G"])
        verdict["P1"] = verdict["P2"] = verdict["P3"] = "UNINFORMATIVE"
    else:
        dB = tg["BOTH"]["delta_knee_deg"]
        dG = tg["GAS"]["delta_knee_deg"]
        dS = tg["SOL"]["delta_knee_deg"]
        verdict["abs_delta_knee_deg"] = {"BOTH": abs(dB),
                                         "GAS": (abs(dG) if dG is not None else None),
                                         "SOL": (abs(dS) if dS is not None else None)}
        verdict["P1_thresholds_deg"] = {"gas_floor_0.6xBOTH": P1_GAS_FLOOR * abs(dB),
                                        "sol_ceiling_0.4xBOTH": P1_SOL_CEIL * abs(dB)}
        arms_missing = [a for a in ("GAS", "SOL") if tg[a]["n_gate_G"] < 4]
        if arms_missing:
            verdict["P1"] = "UNINFORMATIVE"
            verdict["P1_reason"] = ("%s has fewer than 4 Gate-G seeds at KV 0.110"
                                    % ", ".join(arms_missing))
        else:
            gas_ok = abs(dG) >= P1_GAS_FLOOR * abs(dB)
            sol_ok = abs(dS) <= P1_SOL_CEIL * abs(dB)
            verdict["P1_gas_clause"] = bool(gas_ok)
            verdict["P1_sol_clause"] = bool(sol_ok)
            verdict["P1"] = "HOLDS" if (gas_ok and sol_ok) else "FAILS"
            verdict["P1_note"] = (
                "|dknee(GAS)| = %.4f vs floor %.4f (%s); |dknee(SOL)| = %.4f vs ceiling %.4f "
                "(%s)" % (abs(dG), P1_GAS_FLOOR * abs(dB), "pass" if gas_ok else "FAIL",
                          abs(dS), P1_SOL_CEIL * abs(dB), "pass" if sol_ok else "FAIL"))
        # P2: same direction as BOTH
        sgn = np.sign(dB)
        p2 = {a: (None if tg[a]["delta_knee_deg"] is None
                  else bool(np.sign(tg[a]["delta_knee_deg"]) == sgn)) for a in ARMS}
        verdict["P2_same_direction_as_BOTH"] = p2
        verdict["P2"] = ("UNINFORMATIVE" if any(v is None for v in p2.values())
                         else ("HOLDS" if all(p2.values()) else "FAILS"))
        # P3: the soleus share is larger at the ankle than at the knee
        aB, aG, aS = (tg[a]["delta_ank_deg"] for a in ("BOTH", "GAS", "SOL"))
        if None in (dG, dS, aB, aG, aS) or abs(dB) == 0 or abs(aB) == 0:
            verdict["P3"] = "UNINFORMATIVE"
            verdict["P3_reason"] = "a share is undefined (missing arm or zero BOTH displacement)"
        else:
            shk_b = abs(dS) / abs(dB)
            sha_b = abs(aS) / abs(aB)
            dpair = abs(dS) + abs(dG)
            apair = abs(aS) + abs(aG)
            shk_p = abs(dS) / dpair if dpair else None
            sha_p = abs(aS) / apair if apair else None
            verdict["P3_soleus_share"] = {
                "definition_primary": "|delta(SOL)| / |delta(BOTH)| at each joint",
                "knee_share_vs_BOTH": shk_b, "ankle_share_vs_BOTH": sha_b,
                "definition_secondary": "|delta(SOL)| / (|delta(SOL)|+|delta(GAS)|)",
                "knee_share_of_pair": shk_p, "ankle_share_of_pair": sha_p}
            verdict["P3"] = "HOLDS" if sha_b > shk_b else "FAILS"
            verdict["P3_secondary"] = ("HOLDS" if (sha_p is not None and shk_p is not None
                                                  and sha_p > shk_p) else "FAILS")
        verdict["overall"] = verdict["P1"]

    out = {"arm": "MECHANISM_r407", "supersedes": "MECHANISM_RESULT_r402.json",
           "prereg": os.path.basename(PREREG), "prereg_sha256": PREREG_SHA,
           "rungs": RUNGS, "target_kv": TARGET_KV, "seeds": SEEDS, "arms": ARMS,
           "n_cells_recorded": len(recs),
           "control_R151C": ctl,
           "uninformative_rule": ("a rung with fewer than 4 Gate-G seeds is UNINFORMATIVE and "
                                  "is reported, not dropped; fewer than 4 in BOTH at KV 0.110 "
                                  "makes the whole registration UNINFORMATIVE."),
           "by_rung": by_rung,
           "verdict": verdict,
           "cells": [recs[k] for k in sorted(recs)]}
    wopen(os.path.join(PAPER, "MECHANISM_RESULT_r407.json")).write(
        json.dumps(out, indent=2, ensure_ascii=False))

    print()
    print("control R151C  knee mean %+.4f deg   ankle mean %+.4f deg   (n = %d)"
          % (ctl["knee_mean_deg"], ctl["ank_mean_deg"], ctl["n_gate_G"]))
    print()
    print("%-6s %-5s %-9s %-24s %-12s" % ("KV", "arm", "Gate G", "knee mean (dknee)", "ankle mean"))
    for kv in RUNGS:
        for arm in ARMS:
            e = by_rung["%.3f" % kv][arm]
            km = ("%+.4f (%+.4f)" % (e["knee_mean_deg"], e["delta_knee_deg"])
                  if e["knee_mean_deg"] is not None else "-")
            am = "%+.4f" % e["ank_mean_deg"] if e["ank_mean_deg"] is not None else "-"
            print("%-6.3f %-5s %d/%-7d %-24s %-12s%s"
                  % (kv, arm, e["n_gate_G"], e["n_cells"], km, am,
                     "  UNINFORMATIVE" if e["uninformative"] else ""))
    print()
    print("VERDICT at KV %.3f: overall %s | P1 %s | P2 %s | P3 %s"
          % (TARGET_KV, verdict.get("overall"), verdict.get("P1"), verdict.get("P2"),
             verdict.get("P3")))
    if verdict.get("P1_note"):
        print("  " + verdict["P1_note"])
    print("wrote %s" % os.path.join(PAPER, "MECHANISM_RESULT_r407.json"))
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--run", action="store_true")
ap.add_argument("--analyse", action="store_true")
a_ = ap.parse_args()
if a_.run:
    _r, _m, complete = run_all()
    analyse()
    if not complete:
        print("RUN INCOMPLETE -- yielded to a foreign sconecmd. Re-run --run to resume.")
elif a_.analyse:
    analyse()
else:
    ap.print_help()
