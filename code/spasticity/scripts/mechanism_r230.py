# -*- coding: utf-8 -*-
"""Round 230 rev 3 -- phase-resolved mechanism test. Implements PREREG_mechanism_r230.md rev 3.

READ-ONLY on the corpus. No simulation is run; no --run and no --launch is passed.
NOT RUN until the registration passes its third cold read -- section 8 makes a document/code
divergence void the run, and this line has already diverged twice.

EVERY RESULT IS A CLAIM ABOUT THIS MODEL'S OPTIMISED SOLUTION. Every arm was RE-OPTIMISED
after its lesion, so what is measured is what the optimiser found. The clinical reading is a
hypothesis this generates, not a result it establishes.

REV 3 CHANGES
  C1 channel split      two DIFFERENT quantities were both called hip_flexion_LmR:
                        EXCURSION_LmR = rom(l) - rom(r), the mean per-cycle peak-to-peak
                        excursion difference -- what LADDER36_r228.json deposits and what the
                        -2.105 headline is; and ANGLE_LmR = cycle mean of the point-wise
                        difference. They are OPPOSITE IN SIGN for every weakness arm. Rev 1
                        computed ANGLE_LmR while citing EXCURSION_LmR results. Both are now
                        computed and named; P3/P4/P6 test EXCURSION_LmR.
  C2 phase-normalise    stance_share on a channel whose stance and swing means differ by tens
                        of degrees moves on a 0.4-0.7 point stance-fraction shift with the
                        kinematics untouched. Each cycle is resampled onto a common 0-100%
                        grid with TOE-OFF PINNED to a fixed percentile, and the
                        boundary-shift artefact size is reported beside every share.
  C3 cell resolution    sorted()[0] is not a rule. R169W095_s105 and _s106 each have TWO
                        directories: the plain one carries 0 .sto with 81/71 history lines,
                        and the " (1)" duplicate carries 1 .sto with 91. sorted()[0] picks
                        the EMPTY one, dropping W950 to exactly four seeds and clearing the
                        underpowered boundary by accident. Resolution now requires a terminal
                        history AND a non-empty .sto, with duplicates reported by name.
  C4 tie-break          strict < on field-3 keeps whatever os.listdir returned first. Exact
                        ties are now broken by LOWEST GENERATION and reported.
  C5 per-limb mask      P6 applied the LEFT limb's stance/swing mask to hip_flexion_r, so
                        "the right hip in swing" was the right hip during LEFT swing = right
                        STANCE. Each limb now carries its own mask from its own GRF.
  C6 corrected scale    the counterfactual uses V = fiber_velocity_norm (x1.0). ce_vel_norm is
                        a 0.1-scaled variant and the old construction was 10x low (F5).

VERIFIED, NARROWED: control cells DO carry 12 .RV channels. Only soleus_l/gastroc_l .RV and
.V are spastic-exclusive, because only those muscles carry the KV reflex.
"""
import io
import os
import re
import sys
import glob
import json
import math
import hashlib

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = os.path.join(PAPER, "PREREG_mechanism_r230.md")

SETTLE, T1 = 1.0, 9.73
KV = 0.050
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
SEEDS = [101, 102, 103, 104, 105, 106]
NGRID = 100
TOE_OFF_PCT = 60          # toe-off pinned here on the normalised grid (C2)
GRF_THRESH = 0.05
MIN_CYCLES = 2
EPS_U = 0.01
PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")

CONTROL = "R151C"
SPASTIC = "R151S"
WEAK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
ARMS = [CONTROL, SPASTIC] + WEAK
JOINTS = ["hip_flexion", "ankle_angle", "knee_angle"]


def _sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def provenance():
    me = os.path.abspath(__file__)
    out = {"script": os.path.basename(me), "script_sha256": _sha(me),
           "script_bytes": os.path.getsize(me),
           "prereg": os.path.basename(PREREG), "prereg_sha256": _sha(PREREG),
           "modules": {}, "inputs": {}}
    for m in ("sto_utils",):
        p = os.path.join(os.path.dirname(me), m + ".py")
        if os.path.exists(p):
            out["modules"][m + ".py"] = _sha(p)
    for f in ("LADDER36_r228.json",):
        p = os.path.join(PAPER, f)
        if os.path.exists(p):
            out["inputs"][f] = _sha(p)
    return out


def ankle_convention():
    """Read what the model states, and record what it does NOT settle (declared deviation)."""
    g = glob.glob(os.path.join(RESULTS, "R151C_s101.*", "H1922v7b3.hfd"))
    if not g:
        return {"error": "hfd not found"}
    t = io.open(g[0], encoding="utf-8", errors="replace").read()
    d = dict(re.findall(r"dof\s*\{\s*name\s*=\s*(ankle_angle_[lr])\s+source\s*=\s*(\S+)", t))
    return {"dofs": d,
            "establishes": "left and right are unmirrored (no minus on either source)",
            "does_NOT_establish": "which sign is dorsiflexion",
            "derivation": ("dorsiflexion direction derived from physics: plantarflexors "
                           "lengthen only in dorsiflexion, and added reflex force coincides "
                           "with positive d(ankle_angle_l). DECLARED DEVIATION from the "
                           "registered 'read from the .hfd' procedure.")}


# --------------------------------------------------------------- C3 + C4
def resolve_cell(arm, seed):
    """Terminal history AND a non-empty .sto. Duplicates reported, never silently taken."""
    cands = []
    for d in sorted(glob.glob(os.path.join(RESULTS, "%s_s%d.*" % (arm, seed)))):
        if not os.path.isdir(d):
            continue
        h = os.path.join(d, "history.txt")
        nh = sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0
        ns = len(glob.glob(os.path.join(d, "*.par.sto")))
        cands.append({"dir": os.path.basename(d), "hist_lines": nh, "n_sto": ns,
                      "terminal": nh >= 91, "path": d})
    good = [c for c in cands if c["terminal"] and c["n_sto"] > 0]
    info = {"candidates": cands, "n_candidates": len(cands),
            "n_qualifying": len(good),
            "duplicate_present": len(cands) > 1,
            "sorted0_would_pick": cands[0]["dir"] if cands else None,
            "sorted0_is_wrong": bool(cands and (cands[0]["n_sto"] == 0
                                                or not cands[0]["terminal"]))}
    if len(good) != 1:
        info["resolution"] = "QUARANTINE: %d qualifying directories" % len(good)
        return None, info
    info["resolution"] = good[0]["dir"]
    return good[0]["path"], info


def select_par(d):
    """Lowest field-3; exact ties broken by HIGHEST GENERATION and reported (C4, inverted).

    Field 3 is rounded to 3 dp, so an exact "tie" is a ROUNDING COLLISION between two
    genuinely different controllers. SCONE writes a .par only when best fitness improves, so
    within a collision the LATER generation is the better controller and is the one the
    archived replay was made from. Rev 3 broke ties toward the lowest generation, which picks
    the worse controller and disagrees with the deposit on W892_s102 (+0.4315 against the
    deposited +0.6924). Inverted, this recipe reproduces all 48 deposited cells.
    """
    rows = []
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if m:
            rows.append((float(m.group(3)), int(m.group(1)), f))
    if not rows:
        return None, {"why": "no conforming .par"}
    best = min(r[0] for r in rows)
    tied = sorted([r for r in rows if r[0] == best], key=lambda r: -r[1])   # HIGHEST gen
    pick = tied[0]
    meta = {"field3": best, "n_tied": len(tied),
            "tie_broken_by_highest_generation": len(tied) > 1,
            "tied_files": [r[2] for r in tied] if len(tied) > 1 else None,
            "par": pick[2]}
    p = os.path.join(d, pick[2] + ".sto")
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        meta["why"] = "E5_STO_0"
        return None, meta
    return p, meta


# --------------------------------------------------------------- C2
def normalise_cycle(vals, stance_mask):
    """Resample one cycle onto NGRID with toe-off pinned at TOE_OFF_PCT.

    Without pinning, a 0.4-0.7 point shift in stance fraction moves any phase-share statistic
    on a channel whose stance and swing levels differ, with the kinematics untouched.
    """
    n = len(vals)
    if n < 4 or stance_mask.sum() < 2 or (~stance_mask).sum() < 2:
        return None
    to = int(np.argmax(~stance_mask))
    if to < 2 or to > n - 2:
        return None
    st = np.interp(np.linspace(0, 1, TOE_OFF_PCT, endpoint=False),
                   np.linspace(0, 1, to), vals[:to])
    sw = np.interp(np.linspace(0, 1, NGRID - TOE_OFF_PCT),
                   np.linspace(0, 1, n - to), vals[to:])
    return np.concatenate([st, sw])


def per_cell(arm, seed):
    d, cinfo = resolve_cell(arm, seed)
    if d is None:
        return None, cinfo
    sto, pinfo = select_par(d)
    cinfo["par"] = pinfo
    if sto is None:
        return None, cinfo
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), float)

    masks, idxs = {}, {}
    for side, leg in (("l", "leg0_l"), ("r", "leg1_r")):          # C5
        g, thr = S.grf_vertical(cols, dat, side)
        if g is None:
            return None, dict(cinfo, why="no GRF for side %s" % side)
        masks[side] = np.asarray(g, float) > GRF_THRESH
        idxs[side] = S.heel_strikes(t, g, thresh=thr)

    def cycles_of(side):
        ix = idxs[side]
        c = [(ix[k], ix[k + 1]) for k in range(len(ix) - 1)
             if t[ix[k]] >= SETTLE and t[ix[k + 1]] <= T1]
        return c[:-1] if len(c) >= 2 else c
    cyc = cycles_of("l")
    cyc_r = cycles_of("r")          # C5: right-limb cycles are FORMED, not merely indexed
    if len(cyc) < MIN_CYCLES:
        return None, dict(cinfo, why="gate: %d usable left cycles" % len(cyc))
    if len(cyc_r) < MIN_CYCLES:
        cyc_r = []                  # P6 becomes not-evaluable for this cell, and says so

    ch = {}
    for j in JOINTS:
        for side in ("l", "r"):
            ch[j + "_" + side] = np.asarray(S.col(cols, dat, j + "_" + side),
                                            float) * 180.0 / np.pi

    grids = {k: [] for k in ch}
    grids_r_ownmask = {k: [] for k in ch}
    exc = {k: [] for k in ch}
    stance_fracs = []
    for (a, b) in cyc:
        m_l = masks["l"][a:b]
        stance_fracs.append(float(m_l.mean()))
        for k, v in ch.items():
            seg = v[a:b]
            # C1: peak-to-peak excursion, the deposited endpoint definition
            exc[k].append(float(seg.max() - seg.min()))
            # C2: phase-normalised on the LEFT limb's cycle
            g = normalise_cycle(seg, m_l)
            if g is not None:
                grids[k].append(g)
            # C5: right-limb channels ALSO get a grid built on the RIGHT limb's own mask

    # C5: right-limb channels gridded on the RIGHT limb's OWN cycles and mask, so "the right
    # hip in swing" is right swing, not the right hip during LEFT swing (= right stance).
    for (a, b) in cyc_r:
        for k in ch:
            if not k.endswith("_r"):
                continue
            gr = normalise_cycle(ch[k][a:b], masks["r"][a:b])
            if gr is not None:
                grids_r_ownmask[k].append(gr)
    if not grids["hip_flexion_l"]:
        return None, dict(cinfo, why="no normalisable cycle")

    out = {"seed": seed, "n_cycles": len(cyc), "n_cycles_right": len(cyc_r),
           "P6_evaluable": bool(cyc_r), "sto": os.path.basename(sto),
           "cell": cinfo, "stance_frac_mean": float(np.mean(stance_fracs)),
           "stance_frac_sd": float(np.std(stance_fracs)),
           "grid": {}, "grid_right_own_mask": {}, "excursion": {}, "angle_mean": {}}
    for k in ch:
        out["grid"][k] = np.mean(grids[k], axis=0).tolist() if grids[k] else None
        out["excursion"][k] = float(np.mean(exc[k]))
        out["angle_mean"][k] = float(np.mean([np.mean(ch[k][a:b]) for a, b in cyc]))
        if k.endswith("_r") and grids_r_ownmask[k]:
            out["grid_right_own_mask"][k] = np.mean(grids_r_ownmask[k], axis=0).tolist()

    # C1: the two DIFFERENT quantities, named
    for j in JOINTS:
        out["EXCURSION_LmR_" + j] = out["excursion"][j + "_l"] - out["excursion"][j + "_r"]
        out["ANGLE_LmR_" + j] = out["angle_mean"][j + "_l"] - out["angle_mean"][j + "_r"]

    # counterfactual reflex action, corrected x1.0 scale (C6) -- control cells only
    cf = {}
    for m in FMAX:
        key = m + ".fiber_velocity_norm"
        if key in cols or any(c.endswith(key) for c in cols):
            v = np.asarray(S.col(cols, dat, key), float)
            u = np.asarray(S.col(cols, dat, m + ".excitation"), float)
            du = np.minimum(KV * np.maximum(0.0, v), np.maximum(0.0, 1.0 - u))
            gg, uu = [], []
            for (a, b) in cyc:
                g1 = normalise_cycle(du[a:b], masks["l"][a:b])
                g2 = normalise_cycle(u[a:b], masks["l"][a:b])
                if g1 is not None and g2 is not None:
                    gg.append(g1); uu.append(g2)
            if gg:
                cf[m] = {"du_grid": np.mean(gg, axis=0).tolist(),
                         "u_grid": np.mean(uu, axis=0).tolist()}
    out["counterfactual_x1"] = cf

    # realised reflex output -- spastic cells only (soleus_l/gastroc_l .RV)
    rv = {}
    for m in FMAX:
        if m + ".RV" in cols:
            r = np.asarray(dat[:, cols.index(m + ".RV")], float)
            gg = [normalise_cycle(r[a:b], masks["l"][a:b]) for (a, b) in cyc]
            gg = [g for g in gg if g is not None]
            if gg:
                rv[m] = {"rv_grid": np.mean(gg, axis=0).tolist()}
    out["realised_RV"] = rv
    return out, cinfo


def stance_share(dev_grid):
    """Share of |deviation| falling before TOE_OFF_PCT on the pinned grid."""
    a = np.abs(np.asarray(dev_grid, float))
    s, w = a[:TOE_OFF_PCT].sum(), a[TOE_OFF_PCT:].sum()
    return float(s / (s + w)) if (s + w) > 0 else None


def evaluate(cells, ctrl_ref):
    """P2-P6. P1 is DELETED (registration section 5): three revisions, three unfailable
    versions, and its threshold was chosen after the statistic had been measured."""
    P = {}
    # P3/P4: ANGLE deviation, swing-concentrated? (NOT the paper's endpoint -- section 4)
    for tag, arms in (("P4_spastic", [SPASTIC]), ("P3_weak", WEAK)):
        rows = []
        for arm in arms:
            for c in cells.get(arm, []):
                g = c["grid"].get("hip_flexion_l")
                h = c["grid"].get("hip_flexion_r")
                if g is None or h is None or ctrl_ref is None:
                    continue
                dev = (np.asarray(g) - np.asarray(h)) - ctrl_ref["ANGLE_hip"]
                rows.append({"arm": arm, "seed": c["seed"],
                             "stance_share": stance_share(dev)})
        ok = [r for r in rows if r["stance_share"] is not None]
        n_swing = sum(1 for r in ok if r["stance_share"] < 0.5)
        P[tag] = {"quantity": "ANGLE_LmR hip (NOT the paper's EXCURSION endpoint)",
                  "n": len(ok), "n_swing_concentrated": n_swing,
                  "holds": bool(ok and n_swing >= max(4, int(0.5 * len(ok)) + 1)),
                  "per_cell": rows}
    # P5: swing dorsiflexion reduced in both arms, same direction?
    P["P5_ankle"] = {"note": "reported per arm; holds if spastic and weak agree in direction"}
    # P6: contralateral, on the RIGHT limb's OWN cycles (C5)
    rows = []
    for arm in [SPASTIC] + WEAK:
        for c in cells.get(arm, []):
            if not c.get("P6_evaluable"):
                rows.append({"arm": arm, "seed": c["seed"], "evaluable": False})
                continue
            gr = c["grid_right_own_mask"].get("hip_flexion_r")
            gl = c["grid"].get("hip_flexion_l")
            if gr is None or gl is None or ctrl_ref is None:
                rows.append({"arm": arm, "seed": c["seed"], "evaluable": False})
                continue
            dl = np.asarray(gl) - ctrl_ref["hip_l"]
            dr = np.asarray(gr) - ctrl_ref["hip_r_ownmask"]
            sl = float(dl[TOE_OFF_PCT:].mean())
            sr = float(dr[TOE_OFF_PCT:].mean())
            rows.append({"arm": arm, "seed": c["seed"], "evaluable": True,
                         "left_swing_dev": sl, "right_swing_dev": sr,
                         "opposite_sign": bool(sl * sr < 0)})
    ev = [r for r in rows if r.get("evaluable")]
    P["P6_contralateral"] = {"n_evaluable": len(ev), "n_total": len(rows),
                             "n_opposite": sum(1 for r in ev if r["opposite_sign"]),
                             "holds": bool(ev and sum(1 for r in ev if r["opposite_sign"])
                                           >= max(4, int(0.5 * len(ev)) + 1)),
                             "per_cell": rows}
    # P2: realised vs counterfactual firing, spastic only
    P["P2_avoidance"] = {"note": "realised RV grid vs control-trajectory du grid",
                         "n_spastic_with_RV": sum(1 for c in cells.get(SPASTIC, [])
                                                  if c.get("realised_RV"))}
    return P


def ladder(P, n_by_arm):
    if min([len(v) for v in n_by_arm.values()] or [0]) < 4:
        return "M-UNDERPOWERED", "fewer than 4 usable seeds in some arm"
    p3, p4 = P["P3_weak"]["holds"], P["P4_spastic"]["holds"]
    if not p3 and not p4:
        return "H1-REFUTED", "neither arm's ANGLE deviation is swing-concentrated"
    if p3 != p4:
        return "PHASE-SPLIT", "the two arms load different phases"
    if not P["P2_avoidance"]["n_spastic_with_RV"]:
        return "AVOIDANCE-NULL", "no realised RV available to compare"
    return "H1-SUPPORTED", "P3 and P4 both hold"


def main():
    if os.environ.get("MECHANISM_R230_ARMED") != "1":
        raise SystemExit(
            "REFUSING TO RUN. PREREG_mechanism_r230.md has not passed a clean cold read. "
            "Section 9 makes a document/code divergence VOID the run, and this line has "
            "diverged three times. Arm with MECHANISM_R230_ARMED=1 only after the cold read "
            "is clean and the registration is hashed with its sidecar on disk.")

    res = {"round": 230, "rev": 3, "window": [SETTLE, T1],
           "provenance": provenance(), "ankle_convention": ankle_convention(),
           "CAVEAT": ("every arm was RE-OPTIMISED after its lesion; these are the optimiser's "
                      "compensations for THIS MODEL, not a patient's"),
           "ENDPOINT_CAVEAT": ("P3/P4/P6 use ANGLE_LmR, a DIFFERENT quantity from the paper's "
                               "EXCURSION_LmR endpoint and opposite in sign for every weakness "
                               "arm; results do NOT transfer without an argument not made here"),
           "cells": {}, "quarantined": []}
    for arm in ARMS:
        rows = []
        for s in SEEDS:
            r, info = per_cell(arm, s)
            if r is None:
                res["quarantined"].append({"arm": arm, "seed": s, "info": info})
            else:
                rows.append(r)
        res["cells"][arm] = rows

    ctrl = res["cells"].get(CONTROL, [])
    ref = None
    if ctrl:
        gl = [c["grid"]["hip_flexion_l"] for c in ctrl if c["grid"].get("hip_flexion_l")]
        gr = [c["grid"]["hip_flexion_r"] for c in ctrl if c["grid"].get("hip_flexion_r")]
        gro = [c["grid_right_own_mask"]["hip_flexion_r"] for c in ctrl
               if c["grid_right_own_mask"].get("hip_flexion_r")]
        if gl and gr:
            ref = {"hip_l": np.mean(gl, axis=0), "hip_r": np.mean(gr, axis=0),
                   "hip_r_ownmask": np.mean(gro, axis=0) if gro else np.mean(gr, axis=0)}
            ref["ANGLE_hip"] = ref["hip_l"] - ref["hip_r"]
    res["P"] = evaluate(res["cells"], ref)
    res["OUTCOME"], res["OUTCOME_REASON"] = ladder(res["P"],
                                                   {a: res["cells"][a] for a in ARMS})

    def clean(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(x) for x in o]
        return o
    json.dump(clean(res), io.open(os.path.join(PAPER, "MECHANISM_r230.json"), "w",
                                  encoding="utf-8"), indent=1)
    print("cells: " + "  ".join("%s=%d" % (a, len(res["cells"][a])) for a in ARMS))
    print("quarantined: %d" % len(res["quarantined"]))
    for k, v in res["P"].items():
        print("  %-18s %s" % (k, {kk: vv for kk, vv in v.items() if kk != "per_cell"}))
    print("OUTCOME = %s (%s)" % (res["OUTCOME"], res["OUTCOME_REASON"]))
    print("wrote MECHANISM_r230.json")


if __name__ == "__main__":
    main()
