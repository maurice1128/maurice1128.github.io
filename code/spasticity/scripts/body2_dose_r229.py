# -*- coding: utf-8 -*-
"""Round 229 rev 4 -- UPSTREAM lesion dose in the 2D H0914M body, on the CONTROL trajectory.

REV 4: the two-convention design is DELETED, not repaired. The velocity convention was an
empirical question and the answer was already on disk: existing spastic .sto files carry
soleus_l.RV / gastroc_l.RV -- the velocity reflex's own output -- beside fiber_velocity_norm,
in cells with a declared KV. At the 2-sample lag matching the declared 0.020 s reflex delay,
median RV / (KV * max(0, fiber_velocity_norm)) is

    CMS020_s1   KV 0.0200 -> 0.9923
    BSPAS005_s1 KV 0.0500 -> 0.9503
    SPAS005     KV 0.0500 -> 0.9615

Under the x0.1 branch these would be ~10.0. SCONE's MuscleReflex KV multiplies
fiber_velocity_norm DIRECTLY: the convention is x1.0, and rev 3's default was the wrong
branch -- it would have divided the entire spastic dose by ten. CONVENTIONS_AGREE and
outcome G are gone with it, and so is the proof that the reachable set was {G, STOP, D}.

Each engine's reflex reads its own engine's channel, which is why dose_r174.py was right to
use ce_vel_norm in 3D. 2D and 3D dose numbers are therefore NOT on a common scale; every
comparison here is within-body and no 2D dose is compared to a 3D dose.

Also rev 4: Gate B is applied to the CONTROL arm too (rev 3 gated both lesion arms and left
the control arm ungated), and the >= 2 usable cycle guard is corrected.
"""
import io
import os
import re
import sys
import glob
import json

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\dose_r174.py"

SETTLE, T1 = 1.0, 8.00
MIN_CYCLES = 2
MIN_CONTROL_SEEDS = 5
MIN_N_PER_ARM = 5
PARTIAL_MATCH_FRAC = 0.25
CE_VEL_FACTOR = 1.0            # MEASURED, section 1. Not a choice.

FMAX_EXPECT = {"soleus_l": 3549.0, "gastroc_l": 2241.0, "tib_ant_l": 1759.0}
KV_EXPECT = {"DR2K000": 0.000, "DR2K050": 0.050, "DR2K075": 0.075, "DR2K200": 0.200}
SCALE_EXPECT = {"PAR20": 0.800, "PAR40": 0.600, "CMW80": 0.200}
SPASTIC = ["DR2K050", "DR2K075", "DR2K200"]
WEAK = ["PAR20", "PAR40", "CMW80"]
PLANES = ["SG0", "SG2"]
PRIMARY_PLANE = "SG0"
MUSCLE_TAGS = ("Millard2012EquilibriumMuscle", "Thelen2003Muscle",
               "Schutte1993Muscle_Deprecated")



# --- provenance: every deposit records the sha256 of the script that produced it and
# --- of the registration it implements. Revisions 1-4 asserted this while no script
# --- contained the string "sha256"; with no digest on disk every registered constant
# --- was silently mutable after reading a deposit.
PREREG = os.path.join(r"C:\Users\maurice\Desktop\spasticity_paper\paper",
                      "PREREG_2ndbody_r229.md")



PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")


def registered_sto(d):
    """F7: the .sto is selected BY THE REGISTERED RULE, not by lexicographic luck.

    Rev 6 took sorted(glob("*.par.sto"))[-1], which is whichever filename sorts last. The
    registered rule is the lowest FIELD-3 (best fitness) .par, so the phenotype is the replay
    of THAT .par. Returns (path, why_not).
    """
    best = None
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if not m:
            continue                     # excludes ResultH0914Gait10.par
        fit = float(m.group(3))
        if best is None or fit < best[1]:
            best = (os.path.join(d, f), fit)
    if best is None:
        return None, "no conforming .par"
    p = best[0] + ".sto"
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None, "REPLAY_MISSING"    # quarantined, NOT Gate B attrition
    return p, None


def _sha256(path):
    import hashlib
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def provenance():
    me = os.path.abspath(__file__)
    return {"script": os.path.basename(me), "script_sha256": _sha256(me),
            "script_bytes": os.path.getsize(me),
            "prereg": os.path.basename(PREREG), "prereg_sha256": _sha256(PREREG),
            "prereg_bytes": os.path.getsize(PREREG),
            "scope": "baseline forward only (defect register #534, #539)"}


def assert_transcription():
    t = io.open(SRC, encoding="utf-8").read()
    need = ["du = KV * np.maximum(0.0, v)",
            "du = np.minimum(du, np.maximum(0.0, 1.0 - u))",
            "add = add + du * FMAX[m]",
            '"soleus_l": 3549.0', '"gastroc_l": 2241.0', '"tib_ant_l": 1759.0']
    miss = [n for n in need if n not in t]
    if miss:
        raise SystemExit("TRANSCRIPTION MISMATCH against dose_r174.py: %r" % miss)


def osim_fmax(path):
    t = io.open(path, encoding="utf-8", errors="replace").read()
    got = {}
    for tag in MUSCLE_TAGS:
        for m in re.finditer("<" + tag + r'\s+name="([^"]+)"(.*?)</' + tag + ">", t, re.S):
            v = re.search(r"<max_isometric_force>\s*([\d.eE+-]+)", m.group(2))
            if v:
                got[m.group(1)] = float(v.group(1))
    return got


def config_kv(path):
    t = io.open(path, encoding="utf-8", errors="replace").read()
    i = t.find("SpasticL")
    if i < 0:
        return None
    vals = [float(x) for x in re.findall(r"KV\s*=\s*([\d.]+)", t[i:i + 900])]
    if not vals or len(set(vals)) != 1:
        return None
    return vals[0]


def cell_dirs(plane, fam):
    out = []
    for d in sorted(glob.glob(os.path.join(RESULTS, "%s_%s_s*.H0914M.*" % (plane, fam)))):
        if os.path.isdir(d):
            m = re.search(r"_s(\d+)\.", os.path.basename(d))
            if m:
                out.append((int(m.group(1)), d))
    return sorted(out)


def assert_family_constants(plane):
    base = None
    for seed, d in cell_dirs(plane, "DR2K000"):
        o = glob.glob(os.path.join(d, "*.osim"))
        if o:
            base = osim_fmax(o[0])
            break
    if base is None:
        raise SystemExit("%s: no base .osim on the control family" % plane)
    for k, v in FMAX_EXPECT.items():
        if abs(base.get(k, -1) - v) > 1e-6:
            raise SystemExit("%s base FMAX mismatch %s" % (plane, k))
    rep = {"base_fmax": {k: base[k] for k in FMAX_EXPECT}}
    for fam in ["DR2K000"] + SPASTIC + WEAK:
        cd = cell_dirs(plane, fam)
        if not cd:
            raise SystemExit("%s_%s: no cells" % (plane, fam))
        # EVERY cell, not one probe: section 5b says all, and a per-family spot check cannot
        # detect a single cell carrying a different lesion.
        kvs, scales = set(), set()
        for _s, d in cd:
            k = config_kv(os.path.join(d, "config.scone"))
            o = glob.glob(os.path.join(d, "*.osim"))
            fm = osim_fmax(o[0]) if o else {}
            sc = (fm.get("tib_ant_l", float("nan")) / base["tib_ant_l"]) if fm else None
            kvs.add(k)
            scales.add(None if sc is None else round(sc, 6))
        if len(kvs) != 1 or len(scales) != 1:
            raise SystemExit("%s_%s: cells disagree -- KV %r scales %r"
                             % (plane, fam, kvs, scales))
        kv = kvs.pop()
        scale = scales.pop()
        if fam in KV_EXPECT:
            if kv is None or abs(kv - KV_EXPECT[fam]) > 1e-9:
                raise SystemExit("%s_%s: KV %r vs registered %r" % (plane, fam, kv,
                                                                   KV_EXPECT[fam]))
            if scale is not None and abs(scale - 1.0) > 1e-6:
                raise SystemExit("%s_%s: spastic family tib_ant scale %.4f" % (plane, fam,
                                                                              scale))
        if fam in SCALE_EXPECT:
            if scale is None or abs(scale - SCALE_EXPECT[fam]) > 1e-4:
                raise SystemExit("%s_%s: scale %r vs registered %r" % (plane, fam, scale,
                                                                      SCALE_EXPECT[fam]))
            if kv is not None and abs(kv) > 1e-9:
                raise SystemExit("%s_%s: weak family carries KV=%r" % (plane, fam, kv))
        rep[fam] = {"kv_read": kv, "tib_ant_scale_read": scale}
    return rep


def cycles_of(cols, dat, t):
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    return c[:-1] if len(c) >= 2 else c


def gate_b(d):
    """Gate B only. Reads NO channel. Applied to EVERY arm including the control."""
    sto, why = registered_sto(d)
    if sto is None:
        return False, {"why": why}, None
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    if t[-1] < T1:
        return False, {"why": "t_end %.2f < %.2f" % (t[-1], T1),
                       "t_end": float(t[-1])}, None
    cyc = cycles_of(cols, dat, t)
    if len(cyc) < MIN_CYCLES:                       # rev 4: was MIN_CYCLES - 1
        return False, {"why": "%d usable cycles" % len(cyc), "n_cycles": len(cyc)}, None
    return True, {"t_end": float(t[-1]), "n_cycles": len(cyc)}, (cols, dat, t, cyc)


def control_dose(payload):
    cols, dat, t, cyc = payload
    a, b = cyc[0][0], cyc[-1][1]
    ta = np.asarray(S.col(cols, dat, "tib_ant_l.mtu_force_norm"),
                    dtype=float)[a:b] * FMAX_EXPECT["tib_ant_l"]
    out = {"tib_ant_mean_force_N": float(np.mean(np.abs(ta))),
           "n_cycles": len(cyc), "t_end": float(t[-1])}
    for kvname in SPASTIC:
        kv = KV_EXPECT[kvname]
        add = np.zeros(b - a)
        for m in ("soleus_l", "gastroc_l"):
            v = np.asarray(S.col(cols, dat, m + ".fiber_velocity_norm"),
                           dtype=float)[a:b] * CE_VEL_FACTOR
            u = np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]
            du = kv * np.maximum(0.0, v)
            du = np.minimum(du, np.maximum(0.0, 1.0 - u))
            add = add + du * FMAX_EXPECT[m]
        out["spastic_N__" + kvname] = float(np.mean(add))
    return out


def pair_table(rows, eligible):
    ta = [r["tib_ant_mean_force_N"] for r in rows]
    sp = {k: [r["spastic_N__" + k] for r in rows] for k in SPASTIC}
    wk = {k: [(1.0 - SCALE_EXPECT[k]) * x for x in ta] for k in WEAK}

    def verdict(sub):
        out = {}
        for s in SPASTIC:
            for w in WEAK:
                sv = [sp[s][i] for i in sub]
                wv = [wk[w][i] for i in sub]
                out[(s, w)] = bool(max(min(sv), min(wv)) <= min(max(sv), max(wv)))
        return out

    full = list(range(len(rows)))
    base = verdict(full)
    loo = [verdict([i for i in full if i != k]) for k in full]
    unan = {p: bool(base[p] and all(v[p] for v in loo)) for p in base}

    pairs = []
    for s in SPASTIC:
        for w in WEAK:
            ms, mw = float(np.mean(sp[s])), float(np.mean(wk[w]))
            smaller = min(ms, mw)
            rel = abs(ms - mw) / smaller if smaller else None
            pairs.append({"spastic": s, "weak": w,
                          "spastic_mean_N": ms, "weak_mean_N": mw,
                          "spastic_range_N": [float(min(sp[s])), float(max(sp[s]))],
                          "weak_range_N": [float(min(wk[w])), float(max(wk[w]))],
                          "overlaps_full": base[(s, w)],
                          "overlaps_loo_unanimous": unan[(s, w)],
                          "rel_mean_diff": rel,
                          "partial_only": bool(rel is not None
                                               and rel > PARTIAL_MATCH_FRAC),
                          "n_spastic_gateB": eligible.get(s, 0),
                          "n_weak_gateB": eligible.get(w, 0),
                          "eligible_primary": bool(unan[(s, w)]
                                                   and eligible.get(s, 0) >= MIN_N_PER_ARM
                                                   and eligible.get(w, 0) >= MIN_N_PER_ARM)})
    cand = [p for p in pairs if p["eligible_primary"] and p["rel_mean_diff"] is not None]
    cand.sort(key=lambda p: (p["rel_mean_diff"], KV_EXPECT[p["spastic"]]))
    return {"tib_ant_mean_force_N": float(np.mean(ta)), "n_control_seeds": len(rows),
            "pairs": pairs,
            "any_overlap": any(p["overlaps_loo_unanimous"] for p in pairs),
            "primary_pair": ({"spastic": cand[0]["spastic"], "weak": cand[0]["weak"],
                              "rel_mean_diff": cand[0]["rel_mean_diff"],
                              "partial_only": cand[0]["partial_only"]} if cand else None)}


def main():
    assert_transcription()
    res = {"rev": 5, "window": [SETTLE, T1], "primary_plane": PRIMARY_PLANE,
           "ce_vel_factor": CE_VEL_FACTOR,
           "ce_vel_factor_provenance":
               "measured from soleus_l.RV / gastroc_l.RV against KV*max(0,fiber_velocity_norm) "
               "in BSPAS005_s1 (0.9503), CMS020_s1 (0.9923), SPAS005 (0.9615); x0.1 would give ~10",
           "min_control_seeds": MIN_CONTROL_SEEDS, "min_n_per_arm": MIN_N_PER_ARM,
           "min_cycles": MIN_CYCLES, "partial_match_frac": PARTIAL_MATCH_FRAC,
           "provenance": provenance(), "asserted_constants": {}, "gate_b": {}, "planes": {}}

    for plane in PLANES:
        res["asserted_constants"][plane] = assert_family_constants(plane)

    gb, ctrl = {}, {}
    for plane in PLANES:
        gb[plane] = {}
        for fam in ["DR2K000"] + SPASTIC + WEAK:      # control arm gated too
            passed, failed, rows = [], [], []
            for seed, d in cell_dirs(plane, fam):
                ok, info, payload = gate_b(d)
                if ok:
                    passed.append(seed)
                    if fam == "DR2K000":
                        r = control_dose(payload)
                        r["seed"] = seed
                        rows.append(r)
                else:
                    failed.append({"seed": seed, **info})
            gb[plane][fam] = {"cells": len(cell_dirs(plane, fam)), "passed": len(passed),
                              "failed": len(failed), "failed_detail": failed,
                              "passed_seeds": passed}
            if fam == "DR2K000":
                ctrl[plane] = rows
    res["gate_b"] = gb
    res["control_per_seed"] = ctrl

    for plane in PLANES:
        rows = ctrl.get(plane, [])
        if len(rows) < MIN_CONTROL_SEEDS:
            res["planes"][plane] = {"error": "CONTROL_SEED_FLOOR",
                                    "detail": "%d control cells passed Gate B, floor is %d" % (len(rows), MIN_CONTROL_SEEDS)}
            continue
        elig = {f: gb[plane][f]["passed"] for f in SPASTIC + WEAK}
        res["planes"][plane] = pair_table(rows, elig)

    p = res["planes"].get(PRIMARY_PLANE, {})
    res["ANY_OVERLAP_PRIMARY_PLANE"] = bool(p.get("any_overlap"))
    res["PRIMARY_PAIR"] = p.get("primary_pair")

    out = os.path.join(PAPER, "BODY2_DOSE_r229.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), indent=1)

    print("constants asserted from each family's own .osim / config.scone: OK")
    print("ce_vel factor = %.1f (measured, section 1)" % CE_VEL_FACTOR)
    for plane in PLANES:
        print("=" * 84)
        print("PLANE %s  (%s)" % (plane, "PRIMARY, level"
                                 if plane == PRIMARY_PLANE else "secondary, 2 deg uphill"))
        for fam in ["DR2K000"] + SPASTIC + WEAK:
            g = gb[plane][fam]
            print("   gate B %-9s %2d/%2d passed" % (fam, g["passed"], g["cells"]))
        pl = res["planes"][plane]
        if "error" in pl:
            print("   %s" % pl["error"]); continue
        for q in pl["pairs"]:
            print("   %-8s vs %-7s full=%-5s loo=%-5s rel %s elig=%s"
                  % (q["spastic"], q["weak"], q["overlaps_full"],
                     q["overlaps_loo_unanimous"],
                     ("%6.1f%%" % (100 * q["rel_mean_diff"]))
                     if q["rel_mean_diff"] is not None else "   -  ",
                     q["eligible_primary"]))
        print("   primary pair: %s" % pl["primary_pair"])
    print("=" * 84)
    print("ANY_OVERLAP_PRIMARY_PLANE = %s" % res["ANY_OVERLAP_PRIMARY_PLANE"])
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
