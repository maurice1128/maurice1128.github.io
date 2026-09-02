# -*- coding: utf-8 -*-
"""r424: the mixed-lesion grid -- spasticity chained on top of an already-optimised weakness.

Registered by paper/PREREG_mixed_r424.md, sha256 6b68fa0e3033f4d6..., hashed before any mixed cell
existed. This closes the corpus's largest gap: of 679 of our cells, 401 are pure spastic, 150 pure
weak and ZERO carry both, while a real post-stroke patient carries both at once.

Rows are weakness levels whose roots are already optimised and Gate-G passing (R151C x1.00,
R151W x0.80, R393WK060 x0.60). Columns are chained spastic gains 0.0125 -> 0.025 -> 0.050 applied
to BOTH plantarflexors, the same lesion definition as the headline.

Reuses run_chain_r393's verified machinery: wpath() refuses writes outside spasticity_paper,
write_hfd() applies the tibialis-anterior scaling, and the readback assertions fire per cell.
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_chain_r393 as C  # noqa: E402

ROOT = C.ROOT
STAGE = os.path.join(ROOT, "mixed_r424")
PAPER = C.PAPER
SRC_S = C.SRC_S                      # spastic template: BOTH reflexes present
GENS = C.GENS
SEEDS = C.SEEDS

# W070 appended at r426: the registered x0.60 root passes only 2-3/6 by either chaining
# route (RESCUE_RESULT_r426.json), so that row is UNINFORMATIVE and registered P3 cannot be
# judged as written. R426WK070 passes 6/6 and is the deepest weakness this model walks with.
# This row is EXPLICITLY POST-HOC and must be reported as a substitute, never as P3.
ROWS = [("W100", 1.00, "R151C"), ("W080", 0.80, "R151W"), ("W060", 0.60, "R393WK060"),
        ("W070", 0.70, "R426WK070")]
# 1100 added at r424b, BEFORE any r424 cell was read, because the Hyfydy trial expires
# 2026-08-27 and the grid otherwise stops at KV 0.050 while the headline uses KV 0.110.
# The addition is a COLUMN EXTENSION of the registered ladder, not a change to any
# registered threshold or endpoint; PREREG_mixed_r424.md section 8 forbids adding cells
# AFTER seeing a value, and no value has been read.
COLS = [("0125", 0.0125), ("0250", 0.025), ("0500", 0.050), ("1100", 0.110)]


def cells():
    out = []
    for wtag, wscale, wroot in ROWS:
        for k, (stag, kv) in enumerate(COLS):
            for s in SEEDS:
                out.append({
                    "row": wtag, "weak_scale": wscale, "col": stag, "KV": kv,
                    "seed": s, "rung_index": k,
                    "prefix": "R424%s%s_s%d" % (wtag, stag, s),
                    "parent_prefix": ("%s_s%d" % (wroot, s) if k == 0
                                      else "R424%s%s_s%d" % (wtag, COLS[k - 1][0], s)),
                    "parent_is_root": k == 0})
    return out


def make_dirs(c):
    d = os.path.join(STAGE, c["prefix"])
    for sub in ("par", "models", "data"):
        os.makedirs(C.wpath(os.path.join(d, sub)), exist_ok=True)
    shutil.copyfile(os.path.join(SRC_S, "InitStateH0918Gait10ActA.zml"),
                    C.wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))
    # tibialis anterior scaled to this row; soleus and gastroc untouched
    C.write_hfd(os.path.join(SRC_S, "H1922v7b3.hfd"),
                C.wpath(os.path.join(d, "models", "H1922v7b3.hfd")), c["weak_scale"])
    return d


def prepare(c):
    d = make_dirs(c)
    rec = {k: c[k] for k in ("prefix", "row", "weak_scale", "col", "KV", "seed",
                             "parent_prefix", "parent_is_root")}
    pev = C.evaluate(c["parent_prefix"])
    if pev.get("status") != "OK":
        rec.update(status="PARENT_NOT_RUN", parent_status=pev.get("status"))
        return rec
    rec.update(parent_gate_G=pev["gate_G"], parent_t_end_s=pev["t_end_s"],
               parent_n_cycles=pev["n_cycles_in_window"], parent_result_dir=pev["result_dir"])
    if not pev["gate_G"]:
        rec.update(status="BROKEN_PARENT_FAILED_GATE",
                   broken_reason="parent %s failed Gate G; no substitute parent is used"
                                 % c["parent_prefix"])
        return rec

    psrc = os.path.join(C.RES, pev["result_dir"], pev["resolved_par"])
    warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], pev["resolved_par_generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(C.wpath(old))
    shutil.copyfile(psrc, C.wpath(os.path.join(d, "par", warm)))
    assert C.sha(os.path.join(d, "par", warm)) == pev["resolved_par_sha256"], "warm copy differs"
    rec.update(parent_par=pev["resolved_par"], parent_par_sha256=pev["resolved_par_sha256"],
               parent_par_generation=pev["resolved_par_generation"], staged_warm_as=warm)

    cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    cfg, n = re.subn(r"KV\s*=\s*0\.050", "KV = %.4f" % c["KV"], cfg)
    assert n == 2, "expected 2 literal spastic KV substitutions, made %d" % n
    for pat, rep in ((r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS),
                     (r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}', 'init { file = "par/%s" }' % warm),
                     (r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"]),
                     (r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"])):
        cfg, n = re.subn(pat, rep, cfg, count=1)
        assert n == 1, "substitution failed: %s" % pat
    C.wopen(os.path.join(d, "config.scone")).write(cfg)

    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    assert len(re.findall(r"KV\s*=\s*%.4f\b" % c["KV"], back)) == 2, "spastic KV readback"
    assert len(re.findall(r"allow_neg_V\s*=\s*0", back)) >= 2
    assert len(re.findall(r"delay\s*=\s*0\.020", back)) >= 2
    assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
    assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
    assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
    m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
    assert m and m.group(1) == "par/" + warm
    assert os.path.exists(os.path.join(d, "par", warm))

    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    fm = {mm: float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                              chk, re.S).group(1)) for mm in C.FMAX_BASE}
    assert abs(fm["soleus_l"] - 3549.0) < 1e-6 and abs(fm["gastroc_l"] - 2241.0) < 1e-6, fm
    assert abs(fm["tib_ant_l"] - 1759.0 * c["weak_scale"]) < 1e-6, fm
    rec.update(fmax_readback=fm, config_sha256=C.sha(os.path.join(d, "config.scone")),
               init_line_readback=m.group(0), status="PREPARED")
    return rec


def yield_to_foreign():
    fleet = int(os.environ.get("R424_FLEET", "3"))
    while True:
        n = C.competing()
        if n < 0 or n <= fleet:
            return
        time.sleep(60)


def run_cell(i):
    c = cells()[i]
    yield_to_foreign()
    rec = prepare(c)
    if rec["status"] != "PREPARED":
        return rec
    d = os.path.join(STAGE, c["prefix"])
    t0 = time.time()
    r = C.subprocess.run([C.SCONE, "-o", "config.scone", "--quiet"], cwd=d,
                         capture_output=True, text=True, timeout=7200)
    rec["seconds"] = round(time.time() - t0, 1)
    ev = C.evaluate(c["prefix"])
    for k in ("result_dir", "gate_G", "t_end_s", "n_cycles_in_window", "knee_hs_deg"):
        rec[k] = ev.get(k)
    rec["status"] = "RUN_OK" if ev.get("status") == "OK" else ("RUN_%s" % ev.get("status"))
    rec["scone_tail"] = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
    C.wopen(os.path.join(PAPER, "RUN_MIXED_r424_%s.json" % c["prefix"])).write(
        json.dumps(rec, indent=1, ensure_ascii=False))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--range", type=str)
    a = ap.parse_args()
    cs = cells()
    if a.list:
        for i, c in enumerate(cs):
            print("%3d  %-22s weak x%.2f  KV %.4f  parent %s"
                  % (i, c["prefix"], c["weak_scale"], c["KV"], c["parent_prefix"]))
        print("total %d" % len(cs))
        return
    if a.range:
        i, j = (int(x) for x in a.range.split(":"))
        for k in range(i, min(j, len(cs))):
            r = run_cell(k)
            print("%3d  %-22s %-26s gate_G=%s t_end=%s"
                  % (k, cs[k]["prefix"], r.get("status"), r.get("gate_G"), r.get("t_end_s")))
            sys.stdout.flush()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
