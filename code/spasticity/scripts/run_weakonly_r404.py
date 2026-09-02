# -*- coding: utf-8 -*-
r"""run_weakonly_r404.py -- move the weakness lesion so the cross-joint rule has a WEAK_ONLY joint.

NO REGISTRATION EXISTS YET. This launcher stages the design and deposits it in
paper\WEAKONLY_STAGE_r404.json precisely enough that a pre-registration can be written from
the manifest alone, before any cell is run.

WHY. paper\SPANNING_MAP_r403.json derives, from the model file and nothing else, which joints
each muscle spans. Under the CURRENT lesion pair -- spastic on soleus_l and gastroc_l, weak on
tib_ant_l -- the joint classes come out:

    ankle_l  BOTH           (soleus_l, gastroc_l spastic; tib_ant_l weak)
    knee_l   SPASTIC_ONLY   (gastroc_l, biarticular)
    hip_l    NEITHER

so there is no WEAK_ONLY joint anywhere and the cross-joint rule -- that a lesion shows itself
at the joints its muscles span and not at the others -- can only ever be tested on its spastic
half. r402 tests that half. This launcher tests the OTHER half, by moving the weakness lesion
onto a muscle that spans a joint the spastic muscles do not.

`hamstrings_l` spans hip_l and knee_l and is neither soleus_l nor gastroc_l. Putting the
weakness there gives:

    ankle_l  SPASTIC_ONLY   (soleus_l, gastroc_l)
    knee_l   BOTH           (gastroc_l spastic; hamstrings_l weak)
    hip_l    WEAK_ONLY      (hamstrings_l)   <-- the joint the rule predicts on

The rule's prediction for this arm is therefore AT THE HIP, which is why evaluate() records
hip_flexion_l at heel strike and the peak hip_flexion_l in swing alongside the corpus knee and
ankle endpoints. The joint classes above are recomputed in code from SPANNING_MAP_r403.json at
stage time and deposited, not asserted from this docstring.

THE EXPERIMENT.
  arm WKHAM060   max_isometric_force on hamstrings_l x0.60   6 seeds
  arm WKHAM040   max_isometric_force on hamstrings_l x0.40   6 seeds
  12 cells, 90 generations each, the corpus budget.

  NO ANKLE LESION AT ALL. tib_ant_l stays 1759, soleus_l stays 3549, gastroc_l stays 2241, and
  the controller template is the UNLESIONED R151C config -- it carries no SpasticL block. All
  four facts are asserted off disk after staging.

  The spastic comparator is the EXISTING R396SPg110 cells. They are NOT re-run and NOT touched.

CHAINING, the corpus protocol (Ong et al. 2019, as in r393/r396):
  x0.60 warm-starts from THAT SEED's unlesioned control R151C_s{seed};
  x0.40 warm-starts from THAT SEED's OWN x0.60 result, R404WKHAM060_s{seed}.
  Never from another seed. Parents and .par sha256 are recorded per cell.

  Because the x0.40 parent does not exist until x0.60 has run, staging prepares the x0.60 rung
  in full and records the x0.40 rung as PARENT_NOT_RUN; run_all() calls prepare() for each cell
  immediately before running it, and a cell whose parent failed Gate G is BROKEN and is not
  substituted with another seed's parent.

STAGING NEVER STARTS sconecmd. Parent Gate G is read from the parent's ALREADY EXISTING .sto;
a parent with no .sto is reported, never replayed, at stage time.

SAFETY, unchanged from the corpus launchers:
  * writes ONLY under spasticity_paper (enforced by wpath on every write); SCONE, when --rest
    is eventually run by the driver, writes ONLY new directories under SCONE\results;
  * the 112 protected directories are never opened for write, and every new directory name is
    asserted against the protected pattern before harvest;
  * YIELD: before each cell, count sconecmd processes; if any is running that is not ours,
    suspend and report rather than compete.

Usage:  python run_weakonly_r404.py --stage      build the 12 scenarios, run nothing
        python run_weakonly_r404.py --rest       run the remaining cells in order
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
SRC_C = os.path.join(ROOT, "reopt_r151", "R151C_s101")    # unlesioned template: model + config
STAGE = os.path.join(ROOT, "weakonly_r404")
SPANMAP = os.path.join(PAPER, "SPANNING_MAP_r403.json")

GENS = 90
SETTLE, T1, MIN_CYC = 1.00, 9.73, 5
SEEDS = [101, 102, 103, 104, 105, 106]

LESION_MUSCLE = "hamstrings_l"
FMAX_BASE = {"hamstrings_l": 2594.0, "hamstrings_r": 2594.0,
             "tib_ant_l": 1759.0, "soleus_l": 3549.0, "gastroc_l": 2241.0}
UNTOUCHED = ("tib_ant_l", "soleus_l", "gastroc_l", "hamstrings_r")
SPASTIC_MUSCLES = ["soleus_l", "gastroc_l"]

# rung tag, scale.  index 0 is the EXISTING unlesioned root R151C and is never re-run.
RUNGS = [("100", 1.00), ("060", 0.60), ("040", 0.40)]
ROOT_PREFIX = "R151C"
COMPARATOR = "R396SPg110"          # existing spastic cells, NOT re-run

PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")


# ------------------------------------------------------------------ safety -------------------
def wpath(p):
    ap = os.path.abspath(p)
    assert ap.lower().startswith(WRITE_ROOT.lower() + os.sep), \
        "REFUSING to write outside spasticity_paper: " + ap
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


# --------------------------------------------------------- the spanning argument -------------
def spanning_analysis():
    """Confirm FROM SPANNING_MAP_r403.json that the new lesion creates a WEAK_ONLY joint.

    Nothing here is asserted from the docstring: the muscle list and the joint classes are
    recomputed from the deposited map, which was itself derived from the model file alone.
    """
    m = json.load(io.open(SPANMAP, encoding="utf-8"))
    spans = m["muscle_spans"]
    assert m["lesioned_spastic"] == SPASTIC_MUSCLES, \
        "map's spastic pair %s != %s" % (m["lesioned_spastic"], SPASTIC_MUSCLES)

    spastic_joints = sorted({j for mm in SPASTIC_MUSCLES for j in spans[mm]["spans"]})

    # left-side muscles spanning hip_l and/or knee_l that are NOT the spastic pair
    cand = {}
    for mm, v in sorted(spans.items()):
        if not mm.endswith("_l") or mm in SPASTIC_MUSCLES:
            continue
        js = [j for j in v["spans"] if j in ("hip_l", "knee_l")]
        if js:
            cand[mm] = sorted(js)
    assert LESION_MUSCLE in cand, "%s does not span hip_l or knee_l in the map" % LESION_MUSCLE

    # the joint classes UNDER THE NEW PAIR
    joints = sorted({j for v in spans.values() for j in v["spans"]})
    classes = {}
    for j in joints:
        sp = [mm for mm in SPASTIC_MUSCLES if j in spans[mm]["spans"]]
        wk = [LESION_MUSCLE] if j in spans[LESION_MUSCLE]["spans"] else []
        classes[j] = {"class": ("BOTH" if sp and wk else "SPASTIC_ONLY" if sp
                                else "WEAK_ONLY" if wk else "NEITHER"),
                      "spastic_muscles": sp, "weak_muscles": wk}
    weak_only = sorted(j for j, v in classes.items() if v["class"] == "WEAK_ONLY")
    assert weak_only, "the new lesion still creates no WEAK_ONLY joint"
    assert "hip_l" in weak_only, "hip_l is not WEAK_ONLY under this lesion: %s" % weak_only

    return {
        "source": os.path.basename(SPANMAP),
        "source_sha256": sha(SPANMAP),
        "derived_from_model": m.get("derived_from"),
        "spastic_muscles": SPASTIC_MUSCLES,
        "spastic_joints_spanned": spastic_joints,
        "left_muscles_spanning_hip_or_knee_excluding_spastic_pair": cand,
        "chosen_weak_muscle": LESION_MUSCLE,
        "chosen_weak_muscle_spans": spans[LESION_MUSCLE]["spans"],
        "joint_classes_under_old_pair": {k: v["class"]
                                         for k, v in sorted(m["joint_classes"].items())},
        "joint_classes_under_new_pair": classes,
        "weak_only_joints_created": weak_only,
        "why": ("Under the old pair (weak = tib_ant_l, ankle only) no joint is WEAK_ONLY, so "
                "the cross-joint rule has nothing to predict on for the weakness half. Moving "
                "the weakness to %s, which spans %s, makes hip_l WEAK_ONLY and knee_l BOTH."
                % (LESION_MUSCLE, ", ".join(spans[LESION_MUSCLE]["spans"]))),
    }


# ------------------------------------------------------------------ cells --------------------
def cells():
    out = []
    for k in range(1, len(RUNGS)):
        tag, f = RUNGS[k]
        ptag = RUNGS[k - 1][0]
        for s in SEEDS:
            out.append({
                "arm": "WKHAM%s" % tag, "rung": tag, "rung_index": k, "scale": f, "seed": s,
                "lesion_muscle": LESION_MUSCLE,
                "fmax_target": FMAX_BASE[LESION_MUSCLE] * f,
                "prefix": "R404WKHAM%s_s%d" % (tag, s),
                "parent_prefix": ("%s_s%d" % (ROOT_PREFIX, s) if k == 1
                                  else "R404WKHAM%s_s%d" % (ptag, s)),
                "parent_is_root": k == 1})
    return out


def cell_index(prefix):
    for i, c in enumerate(cells()):
        if c["prefix"] == prefix:
            return i
    return None


# ------------------------------------------------------------------ model --------------------
def write_hfd(dst, scale):
    """Scale hamstrings_l by `scale`. NOTHING at the ankle may move -- asserted off disk.

    Same approach as run_dfsevere_r293.scale_hfd / run_chain_r396.write_hfd: one anchored
    substitution, then a full read-back of every force this arm is allowed and forbidden to
    change.
    """
    txt = io.open(os.path.join(SRC_C, "H1922v7b3.hfd"), encoding="utf-8").read()
    pat = re.compile(r"(name\s*=\s*" + LESION_MUSCLE + r"\b.*?max_isometric_force\s*=\s*)"
                     r"([0-9.]+)", re.S)
    want = FMAX_BASE[LESION_MUSCLE] * scale
    txt, n = pat.subn(lambda g: g.group(1) + ("%.6g" % want), txt, count=1)
    assert n == 1, "expected 1 %s substitution, made %d" % (LESION_MUSCLE, n)
    io.open(wpath(dst), "w", encoding="utf-8", newline="\n").write(txt)

    chk = io.open(dst, encoding="utf-8").read()
    got = {}
    for mm in FMAX_BASE:
        got[mm] = float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*"
                                  r"([0-9.]+)", chk, re.S).group(1))
    assert abs(got[LESION_MUSCLE] - want) < 1e-6, \
        "%s wanted %s, wrote %s" % (LESION_MUSCLE, want, got[LESION_MUSCLE])
    # THE ASSERTION THIS ARM TURNS ON: no ankle lesion, and the lesion is unilateral.
    for mm in UNTOUCHED:
        assert abs(got[mm] - FMAX_BASE[mm]) < 1e-9, \
            "%s must remain %s, found %s -- this arm carries NO ankle lesion" \
            % (mm, FMAX_BASE[mm], got[mm])
    return got


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


def gate_from_sto(sto):
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


def parent_state(prefix, allow_replay):
    """Resolve a parent and its Gate G. allow_replay=False at stage time: never starts SCONE."""
    cd = result_dir(prefix)
    if cd is None:
        return {"prefix": prefix, "status": "NO_RESULT_DIR"}
    par = best_par_by_generation(cd)
    if par is None:
        return {"prefix": prefix, "status": "NO_PAR", "result_dir": os.path.basename(cd)}
    rec = {"prefix": prefix, "result_dir": os.path.basename(cd),
           "par": os.path.basename(par), "par_path": par, "par_sha256": sha(par),
           "generation": int(os.path.basename(par).split("_")[0])}
    sto = par + ".sto"
    if not os.path.exists(sto):
        if not allow_replay:
            rec["status"] = "NO_STO"
            rec["note"] = "staging refuses to replay; the .sto is produced under --rest"
            return rec
        subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=cd,
                       capture_output=True, timeout=1800)
    if not os.path.exists(sto):
        rec["status"] = "NO_STO"
        return rec
    rec.update(gate_from_sto(sto))
    return rec


# ------------------------------------------------------------------ staging ------------------
def make_dirs(c):
    d = os.path.join(STAGE, c["prefix"])
    for sub in ("models", "data", "par"):
        os.makedirs(wpath(os.path.join(d, sub)), exist_ok=True)
    fmax = write_hfd(os.path.join(d, "models", "H1922v7b3.hfd"), c["scale"])
    shutil.copyfile(os.path.join(SRC_C, "InitStateH0918Gait10ActA.zml"),
                    wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))
    return d, fmax


def prepare(c, allow_replay=False):
    """Resolve the parent, stage its .par, write and read back the config.

    -> record.  status PREPARED | PARENT_NOT_RUN | BROKEN_PARENT_FAILED_GATE
    """
    d = os.path.join(STAGE, c["prefix"])
    assert os.path.isdir(d), "not staged: " + d
    rec = {k: c[k] for k in ("arm", "rung", "scale", "seed", "prefix", "parent_prefix",
                             "parent_is_root", "lesion_muscle", "fmax_target")}
    rec["dir"] = d
    p = parent_state(c["parent_prefix"], allow_replay)
    rec["parent"] = {k: v for k, v in p.items() if k != "par_path"}
    if p.get("status") != "OK":
        rec["status"] = "PARENT_NOT_RUN"
        rec["parent_status"] = p.get("status")
        rec["note"] = ("this rung is chained from the same seed's previous rung, which has not "
                       "run yet; prepare() is called again by run_all() immediately before the "
                       "cell is launched")
        return rec
    if not p["gate_G"]:
        rec["status"] = "BROKEN_PARENT_FAILED_GATE"
        rec["broken_reason"] = ("parent %s failed Gate G (t_end %.2f s, %d cycles); no other "
                                "parent is substituted, this seed's chain is BROKEN"
                                % (c["parent_prefix"], p["t_end_s"], p["n_cycles_in_window"]))
        return rec

    warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], p["generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(wpath(old))
    shutil.copyfile(p["par_path"], wpath(os.path.join(d, "par", warm)))
    assert sha(os.path.join(d, "par", warm)) == p["par_sha256"], "warm copy differs"
    rec["staged_warm_as"] = warm

    cfg = io.open(os.path.join(SRC_C, "config.scone"), encoding="utf-8").read()
    # the unlesioned template must carry NO spastic block and NO literal spastic KV
    assert not re.search(r"name\s*=\s*SpasticL\b", cfg), "template carries a SpasticL block"
    assert not re.search(r"KV\s*=\s*0\.0[0-9]+\s*$", cfg, re.M), \
        "template carries a literal spastic KV"
    cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, 1)
    assert n == 1
    cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                     'init { file = "par/%s" }' % warm, cfg, 1)
    assert n == 1, "init block not found"
    cfg, n = re.subn(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], cfg, 1)
    assert n == 1
    cfg, n = re.subn(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"],
                     cfg, 1)
    assert n == 1
    wopen(os.path.join(d, "config.scone")).write(cfg)

    # ---- read the staged config and model BACK OFF DISK ---------------------------------
    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    assert not re.search(r"name\s*=\s*SpasticL\b", back), "SpasticL appeared in a staged config"
    assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
    assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
    assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
    m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
    assert m and m.group(1) == "par/" + warm, "init readback %s" % (m and m.group(1))
    assert os.path.exists(os.path.join(d, "par", warm)), "init file missing on disk"
    rec["init_line_readback"] = m.group(0)

    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    fm = {mm: float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                              chk, re.S).group(1)) for mm in FMAX_BASE}
    assert abs(fm[LESION_MUSCLE] - c["fmax_target"]) < 1e-6, fm
    for mm in UNTOUCHED:
        assert abs(fm[mm] - FMAX_BASE[mm]) < 1e-9, "%s moved: %s" % (mm, fm)
    rec["fmax_readback"] = fm
    rec["config_sha256"] = sha(os.path.join(d, "config.scone"))
    rec["status"] = "PREPARED"
    return rec


def comparator_state():
    """The existing spastic comparator cells. Read only -- never re-run, never written to."""
    out = []
    for s in SEEDS:
        pfx = "%s_s%d" % (COMPARATOR, s)
        cd = result_dir(pfx)
        if cd is None:
            out.append({"prefix": pfx, "status": "NO_RESULT_DIR"})
            continue
        par = best_par_by_generation(cd)
        rec = {"prefix": pfx, "result_dir": os.path.basename(cd),
               "par": os.path.basename(par), "par_sha256": sha(par)}
        sto = par + ".sto"
        rec.update(gate_from_sto(sto) if os.path.exists(sto) else {"status": "NO_STO"})
        out.append(rec)
    return out


def stage():
    os.makedirs(wpath(STAGE), exist_ok=True)
    span = spanning_analysis()

    man = {
        "arm": "WEAKONLY_r404",
        "registration": "NONE YET -- this manifest is the design of record, written before any "
                        "cell of the R404 series has been run.",
        "generations": GENS,
        "seeds": SEEDS,
        "design": {
            "question": ("The cross-joint rule says a lesion shows itself at the joints its "
                         "muscles span and not at the others. r402 tests the SPASTIC half. "
                         "This tests the WEAKNESS half, which the current lesion pair cannot "
                         "test because it creates no WEAK_ONLY joint."),
            "lesion": ("max_isometric_force on %s (base %.0f N) scaled to x0.60 and x0.40, "
                       "left side only." % (LESION_MUSCLE, FMAX_BASE[LESION_MUSCLE])),
            "no_ankle_lesion": ("tib_ant_l 1759, soleus_l 3549, gastroc_l 2241 and "
                                "hamstrings_r 2594 are asserted unchanged in every cell; the "
                                "controller template is the unlesioned R151C config and "
                                "carries no SpasticL block."),
            "arms": [{"arm": "WKHAM060", "scale": 0.60,
                      "fmax": FMAX_BASE[LESION_MUSCLE] * 0.60, "n_seeds": len(SEEDS)},
                     {"arm": "WKHAM040", "scale": 0.40,
                      "fmax": FMAX_BASE[LESION_MUSCLE] * 0.40, "n_seeds": len(SEEDS)}],
            "n_cells": len(cells()),
            "comparator": ("the EXISTING %s cells, not re-run and not modified" % COMPARATOR),
            "chaining": ("x0.60 from that seed's unlesioned control %s_s{seed}; x0.40 from "
                         "that seed's OWN x0.60 result R404WKHAM060_s{seed}. Never across "
                         "seeds. A cell whose parent failed Gate G is BROKEN and no substitute "
                         "parent is used." % ROOT_PREFIX),
            "gate_G": ("t_end >= %.2f s and >= %d admissible cycles. SETTLE %.2f, T1 %.2f, "
                       "cycles wholly inside the window, drop the last kept cycle, stance = "
                       "leg0_l.grf_norm_y > 0.05." % (T1, MIN_CYC, SETTLE, T1)),
            "endpoints": {
                "primary_registered_at": "hip_l",
                "hip_flexion_l_at_heelstrike_deg": ("per-cycle mean of hip_flexion_l at left "
                                                    "heel strike, degrees -- the WEAK_ONLY "
                                                    "joint, where the rule predicts an effect"),
                "hip_flexion_l_swing_peak_deg": ("mean over cycles of the per-cycle maximum of "
                                                 "hip_flexion_l during swing (grf <= "
                                                 "threshold), degrees"),
                "knee_at_heelstrike_deg": "corpus endpoint, knee_l is BOTH under this pair",
                "ank_stance_mean_deg": ("corpus endpoint; ankle_l is SPASTIC_ONLY under this "
                                        "pair, so the rule predicts LITTLE weakness effect "
                                        "here -- this is the specificity control"),
            },
            "prediction_shape": ("If the cross-joint rule holds, the hamstrings weakness "
                                 "displaces hip_l (WEAK_ONLY) and knee_l (BOTH) and leaves "
                                 "ankle_l (SPASTIC_ONLY, spanned by neither hamstrings head) "
                                 "essentially where the control is. The quantitative "
                                 "thresholds are NOT set here -- they belong in the "
                                 "registration that will be written from this manifest."),
        },
        "spanning_analysis": span,
        "template_config": os.path.join(SRC_C, "config.scone"),
        "template_config_sha256": sha(os.path.join(SRC_C, "config.scone")),
        "template_model_sha256": sha(os.path.join(SRC_C, "H1922v7b3.hfd")),
        "staging_started_sconecmd": False,
        "comparator_cells": comparator_state(),
        "cells": [],
    }

    for c in cells():
        d, fmax = make_dirs(c)
        rec = prepare(c, allow_replay=False)
        rec["fmax_after_make_dirs"] = fmax
        man["cells"].append(rec)

    man["staged_summary"] = {
        st: [r["prefix"] for r in man["cells"] if r["status"] == st]
        for st in sorted({r["status"] for r in man["cells"]})}
    wopen(os.path.join(PAPER, "WEAKONLY_STAGE_r404.json")).write(
        json.dumps(man, indent=2, ensure_ascii=False))

    print("staged %d cells under %s" % (len(man["cells"]), STAGE))
    print("WEAK_ONLY joints created: %s" % ", ".join(span["weak_only_joints_created"]))
    print("left muscles spanning hip_l/knee_l, excluding the spastic pair:")
    for mm, js in sorted(span["left_muscles_spanning_hip_or_knee_excluding_spastic_pair"]
                         .items()):
        print("   %-14s %s" % (mm, ", ".join(js)))
    for st, ps in sorted(man["staged_summary"].items()):
        print("  %-26s %d  %s" % (st, len(ps), " ".join(ps)))
    print("manifest %s" % os.path.join(PAPER, "WEAKONLY_STAGE_r404.json"))
    print("sconecmd was NOT started by staging.")


# ------------------------------------------------------------------ measurement --------------
def evaluate(prefix):
    """Gate G, the corpus knee/ankle endpoints, and the HIP endpoints this arm turns on."""
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
    if not o["gate_G"]:
        return o
    on = grf > thr
    kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
    ank = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    hip = np.degrees(S.col(cols, dat, "hip_flexion_l"))
    o["knee_at_heelstrike_deg"] = float(np.mean([kne[a] for a, _ in win]))
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    o["n_stance_samples"] = int(len(st))
    o["ank_stance_mean_deg"] = float(np.mean(ank[st]))
    # ---- the hip, the WEAK_ONLY joint -----------------------------------------------------
    o["hip_at_heelstrike_deg"] = float(np.mean([hip[a] for a, _ in win]))
    o["hip_at_heelstrike_per_cycle_deg"] = [float(hip[a]) for a, _ in win]
    peaks = [float(np.max(hip[np.arange(a, b)[~on[a:b]]]))
             for a, b in win if (~on[a:b]).any()]
    o["n_cycles_with_swing"] = len(peaks)
    o["hip_swing_peak_per_cycle_deg"] = peaks
    o["hip_swing_peak_deg"] = float(np.mean(peaks)) if peaks else None
    o["hip_stance_mean_deg"] = float(np.mean(hip[st]))
    return o


# ------------------------------------------------------------------ running ------------------
def run_all():
    cs = cells()
    recs = []
    for i, c in enumerate(cs):
        f = os.path.join(PAPER, "RUN_WEAKONLY_r404_cell%02d.json" % i)
        if os.path.exists(f):
            recs.append(json.load(io.open(f, encoding="utf-8")))
            continue
        n = competing()
        if n > 0:
            print("YIELD: %d sconecmd already running. Suspending, not competing." % n)
            return recs
        prep = prepare(c, allow_replay=True)
        if prep["status"] != "PREPARED":
            rec = {"cell": i, **c, "status": prep["status"], "prepare": prep}
            wopen(f).write(json.dumps(rec, indent=1, ensure_ascii=False))
            recs.append(rec)
            print("cell %02d %-22s %s" % (i, c["prefix"], prep["status"]))
            continue
        d = os.path.join(STAGE, c["prefix"])
        before = set(os.listdir(RES))
        t0 = time.time()
        p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                           capture_output=True, text=True, cwd=d)
        wall = time.time() - t0
        new = sorted(set(os.listdir(RES)) - before)
        for nd in new:
            assert not PROTECTED.match(nd), "refusing: protected name created " + nd
        rec = {"cell": i, **c, "wall_clock_s": wall, "returncode": p.returncode,
               "new_result_dirs": new, "prepare": prep}
        rec.update(evaluate(c["prefix"]))
        wopen(f).write(json.dumps(rec, indent=1, ensure_ascii=False))
        recs.append(rec)
        print("cell %02d %-22s %-14s wall %6.1f s  t_end %-6s gate %-5s hip_HS %-9s hip_sw %s"
              % (i, c["prefix"], rec.get("status"), wall,
                 ("%.2f" % rec["t_end_s"]) if rec.get("t_end_s") else "-",
                 rec.get("gate_G"),
                 ("%+.4f" % rec["hip_at_heelstrike_deg"])
                 if rec.get("hip_at_heelstrike_deg") is not None else "-",
                 ("%+.4f" % rec["hip_swing_peak_deg"])
                 if rec.get("hip_swing_peak_deg") is not None else "-"))
    by_arm = {}
    for tag, _f in RUNGS[1:]:
        arm = "WKHAM%s" % tag
        ok = [r for r in recs if r.get("arm") == arm and r.get("gate_G")]
        by_arm[arm] = {
            "n_run": len([r for r in recs if r.get("arm") == arm]),
            "n_gate_G": len(ok),
            "uninformative": len(ok) < 4,
            "hip_at_heelstrike_deg": sorted(r["hip_at_heelstrike_deg"] for r in ok),
            "hip_swing_peak_deg": sorted(r["hip_swing_peak_deg"] for r in ok
                                         if r.get("hip_swing_peak_deg") is not None),
            "knee_at_heelstrike_deg": sorted(r["knee_at_heelstrike_deg"] for r in ok),
            "ank_stance_mean_deg": sorted(r["ank_stance_mean_deg"] for r in ok),
        }
    out = {"arm": "WEAKONLY_r404", "n_cells": len(recs), "by_arm": by_arm,
           "comparator": COMPARATOR,
           "note": ("A rung with fewer than 4 Gate-G seeds is UNINFORMATIVE, reported not "
                    "dropped. Verdicts are read against KNEE_MDC_BATCHNULL_r399.json, not "
                    "against a permutation floor."),
           "cells": recs}
    wopen(os.path.join(PAPER, "WEAKONLY_RESULT_r404.json")).write(
        json.dumps(out, indent=2, ensure_ascii=False))
    print()
    for arm, v in by_arm.items():
        print("%-9s Gate G %d/%d  hip@HS %s" % (arm, v["n_gate_G"], v["n_run"],
                                                v["hip_at_heelstrike_deg"]))
    print("wrote %s" % os.path.join(PAPER, "WEAKONLY_RESULT_r404.json"))
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
