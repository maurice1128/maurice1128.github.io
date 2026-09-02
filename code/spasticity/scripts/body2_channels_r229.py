# -*- coding: utf-8 -*-
"""Round 229 rev 4 -- the three (L-R) channels in the 2D H0914M body.

REV 4 changes:
  * ADJUDICATING STATISTIC IS GRADED. Rev 3 adjudicated on a disjointness gap, which is a
    deterministic switch, not a test: whenever the primary channel is disjoint at most 3 of
    C(n, n_s) assignments reach the observed gap, so familywise_p < alpha fires
    automatically. Worse, its false-positive rate is 2/C(2n, n) -- 2.2e-03 at n=6 (the 3D
    study) but 3.3e-09 at n=16 (the 2D primary pair) -- so the criterion TIGHTENS with n and
    the replication would face a bar ~1e6 times stricter than the finding it replicates.
    Replaced by the standardised mean difference, with a Hodges-Lehmann shift and bootstrap
    CI reported as the effect size. Disjointness is still reported but adjudicates nothing.
  * p = (k + 1) / (B + 1) for Monte Carlo: the observed assignment is included. Rev 3's k/B
    could report p = 0.
  * B-reversed is evaluated BEFORE B. Rev 3 placed it after, so B always fired first and the
    reversed rung was unreachable.
  * Outcome E compares THE SAME pair across planes; if that pair is unavailable in SG2, E is
    not evaluable and says so rather than silently passing.
  * Gate B guard corrected to >= 2 usable cycles (rev 3 admitted single-cycle cells).
  * The cycle-count-matched analysis is DESCRIPTIVE ONLY and adjudicates nothing: it selects
    on a post-treatment variable, which dose_r174.py's own header disqualifies.
  * The two-convention machinery and outcome G are gone; the convention was measured (x1.0).

Primary plane SG0 (level, gravity 0 -9.80665 0). SG2 is 2.0000 deg uphill.
"""
import io
import os
import re
import sys
import glob
import json
import math
import random
import itertools

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

SETTLE, T1 = 1.0, 8.00
RAD2DEG = 180.0 / np.pi
ALPHA = 0.05                    # TOTAL directional-claim rate, declared
ALPHA_PER_DIRECTION = 0.025
SPECIFICITY_MARGIN = 0.50     # rung A: hip SMD must exceed every other channel by this     # A and B-reversed each; the two are symmetric



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


def _load_delta_3d():
    """Delta_3D is READ from LADDER36_r228.json, not transcribed. Rev 6 hand-carried both
    constants with their sources neither read nor hashed."""
    import numpy as _np
    p = os.path.join(PAPER, "LADDER36_r228.json")
    ps = json.load(io.open(p, encoding="utf-8"))["per_seed_hip_flexion_LmR"]
    sv = ps["S"]
    shifts = sorted(float(_np.median([w - s for w in ps[k] for s in sv]))
                    for k in ("W870", "W892", "W915"))
    return float(_np.median(shifts)), [shifts[0], shifts[-1]], p


def _load_delta_equiv():
    p = os.path.join(PAPER, "BODY2_DELTA_r229.json")
    return float(json.load(io.open(p, encoding="utf-8"))["registered_delta_equiv_deg"]), p


DELTA_3D_HL, DELTA_3D_HL_RANGE, _SRC_D3D = _load_delta_3d()
DELTA_EQUIV, _SRC_DEQ = _load_delta_equiv()
TOST_CI = (5.0, 95.0)           # 90 percent interval; TOST at alpha = 0.05
MIN_N_SG2_FOR_E = 5             # rung E needs a supported disagreement, not a sign
MIN_N_PER_ARM = 5
MIN_CYCLES = 2
EXHAUSTIVE_MAX = 200000
B_RESAMPLES = 100000
B_BOOTSTRAP = 10000
SEED = 229229
GATE_B_IMBALANCE = 0.20

CHANNELS = ["hip_flexion", "knee_angle", "ankle_angle"]
PRIMARY_CHANNEL = "hip_flexion_LmR"
ANKLE_CHANNEL = "ankle_angle_LmR"
JOINT = {"hip_flexion": "hip", "knee_angle": "knee", "ankle_angle": "ankle"}
PATH = "/jointset/%s_%s/%s_%s/value"
SPASTIC = ["DR2K050", "DR2K075", "DR2K200"]
WEAK = ["PAR20", "PAR40", "CMW80"]
PLANES = ["SG0", "SG2"]
PRIMARY_PLANE = "SG0"



# --- provenance: every deposit records the sha256 of the script that produced it and
# --- of the registration it implements. Revisions 1-4 asserted this while no script
# --- contained the string "sha256"; with no digest on disk every registered constant
# --- was silently mutable after reading a deposit.
PREREG = os.path.join(r"C:\Users\maurice\Desktop\spasticity_paper\paper",
                      "PREREG_2ndbody_r229.md")


def _sha256(path):
    import hashlib
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def module_hashes():
    """Hash every imported module that carries an operational definition.

    sto_utils.heel_strikes(min_stance=0.15) and its bounce-merge define Gate B's usable-cycle
    count -> arm sizes -> the imbalance rate -> the outcome. It was unhashed and unregistered
    through rev 5, which is the class section 0 claims to have closed.
    """
    out = {}
    for m in ("sto_utils", "dose_r174"):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), m + ".py")
        if os.path.exists(p):
            out[m + ".py"] = {"sha256": _sha256(p), "bytes": os.path.getsize(p)}
    return out


def provenance():
    me = os.path.abspath(__file__)
    return {"script": os.path.basename(me), "script_sha256": _sha256(me),
            "script_bytes": os.path.getsize(me),
            "prereg": os.path.basename(PREREG), "prereg_sha256": _sha256(PREREG),
            "prereg_bytes": os.path.getsize(PREREG),
            "scope": "baseline forward only (defect register #534, #539)"}


def exact_col(cols, dat, coord, side):
    want = PATH % (JOINT[coord], side, coord, side)
    if want not in cols:
        raise SystemExit("EXACT COLUMN MISSING: %s" % want)
    return np.asarray(dat[:, cols.index(want)], dtype=float)


def cell_dirs(plane, fam):
    out = []
    for d in sorted(glob.glob(os.path.join(RESULTS, "%s_%s_s*.H0914M.*" % (plane, fam)))):
        if os.path.isdir(d):
            m = re.search(r"_s(\d+)\.", os.path.basename(d))
            if m:
                out.append((int(m.group(1)), d))
    return sorted(out)


def per_cell(d):
    sto, why = registered_sto(d)
    if sto is None:
        return None, why
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    if t[-1] < T1:
        return None, "gate B: t_end %.2f < %.2f" % (t[-1], T1)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if len(cyc) < MIN_CYCLES:                       # rev 4: was MIN_CYCLES - 1
        return None, "gate B: %d usable cycles" % len(cyc)
    a, b = cyc[0][0], cyc[-1][1]
    out = {"n_cycles": len(cyc), "t_end": float(t[-1]),
           "cycle_span_s": [float(t[a]), float(t[b - 1])]}
    for c in CHANNELS:
        l = exact_col(cols, dat, c, "l")[a:b]
        r = exact_col(cols, dat, c, "r")[a:b]
        out[c + "_LmR"] = float(np.mean(l - r) * RAD2DEG)
    return out, None


# ------------------------------------------------------------------ statistics
def smd(sv, wv, reverse=False):
    """Standardised mean difference, predicted direction = weak above spastic."""
    sv, wv = np.asarray(sv, float), np.asarray(wv, float)
    ns, nw = len(sv), len(wv)
    if ns < 2 or nw < 2:
        return 0.0
    sp = math.sqrt((((ns - 1) * sv.var(ddof=1)) + ((nw - 1) * wv.var(ddof=1)))
                   / float(ns + nw - 2))
    if sp <= 0:
        return 0.0
    d = (sv.mean() - wv.mean()) if reverse else (wv.mean() - sv.mean())
    return float(d / sp)


def hodges_lehmann(sv, wv):
    """Median of all pairwise weak - spastic differences, in degrees."""
    return float(np.median([w - s for w in wv for s in sv]))


def hl_bootstrap_ci(sv, wv, b=B_BOOTSTRAP, seed=SEED, lo=2.5, hi=97.5):
    rng = random.Random(seed)
    ns, nw = len(sv), len(wv)
    out = []
    for _ in range(b):
        a = [sv[rng.randrange(ns)] for _ in range(ns)]
        c = [wv[rng.randrange(nw)] for _ in range(nw)]
        out.append(hodges_lehmann(a, c))
    return [float(np.percentile(out, lo)), float(np.percentile(out, hi))]


def null_test(sp, wk, chans, reverse=False):
    n_s = len(sp[chans[0]])
    pooled = {c: list(sp[c]) + list(wk[c]) for c in chans}
    n = len(pooled[chans[0]])
    n_assign = math.comb(n, n_s)                 # decided BEFORE any loop

    obs = {c: smd(sp[c], wk[c], reverse) for c in chans}
    obs_fw = max(obs[c] for c in chans)

    def stat(idx):
        ss = set(idx)
        return {c: smd([pooled[c][i] for i in range(n) if i in ss],
                       [pooled[c][i] for i in range(n) if i not in ss], reverse)
                for c in chans}

    cnt = {c: 0 for c in chans}
    fw = 0
    if n_assign <= EXHAUSTIVE_MAX:
        method, tot, it = "exhaustive", n_assign, itertools.combinations(range(n), n_s)
    else:
        method, tot = "monte_carlo", B_RESAMPLES
        rng = random.Random(SEED)
        it = (rng.sample(range(n), n_s) for _ in range(B_RESAMPLES))
    for idx in it:
        g = stat(idx)
        for c in chans:
            if g[c] >= obs[c] - 1e-12:
                cnt[c] += 1
        if max(g[c] for c in chans) >= obs_fw - 1e-12:
            fw += 1

    if method == "monte_carlo":
        # observed assignment included: (k+1)/(B+1)
        pc = {c: (cnt[c] + 1) / float(tot + 1) for c in chans}
        pf = (fw + 1) / float(tot + 1)
        floor = 1.0 / (tot + 1)
    else:
        pc = {c: cnt[c] / float(tot) for c in chans}
        pf = fw / float(tot)
        floor = 1.0 / tot
    return {"method": method, "n_assignments_total": n_assign, "n_evaluated": tot,
            "B": B_RESAMPLES if method == "monte_carlo" else None,
            "seed": SEED, "resolution_floor": floor,
            "observed_smd": obs, "observed_familywise_smd": obs_fw,
            "per_channel_count": cnt, "per_channel_p": pc,
            "familywise_count": fw, "familywise_p": pf}


def compare(rows_s, rows_w, sfam, wfam, chans, tag="full"):
    sp = {c: [r[c] for r in rows_s] for c in chans}
    wk = {c: [r[c] for r in rows_w] for c in chans}
    comp = {"tag": tag, "spastic": sfam, "weak": wfam,
            "n_spastic": len(rows_s), "n_weak": len(rows_w),
            "spastic_seeds": [r["seed"] for r in rows_s],
            "weak_seeds": [r["seed"] for r in rows_w],
            "spastic_values": sp, "weak_values": wk,
            "cycles_spastic": [r["n_cycles"] for r in rows_s],
            "cycles_weak": [r["n_cycles"] for r in rows_w],
            "disjoint_DESCRIPTIVE_ONLY": {}, "direction": {},
            "raw_gap_deg": {}, "smd": {}, "hodges_lehmann_deg": {}}
    for c in chans:
        smax, smin, wmax, wmin = max(sp[c]), min(sp[c]), max(wk[c]), min(wk[c])
        comp["disjoint_DESCRIPTIVE_ONLY"][c] = bool(smax < wmin or wmax < smin)
        comp["direction"][c] = ("spastic_below_weak" if smax < wmin else
                                "weak_below_spastic" if wmax < smin else "overlapping")
        comp["raw_gap_deg"][c] = float(wmin - smax)
        comp["smd"][c] = smd(sp[c], wk[c])
        comp["hodges_lehmann_deg"][c] = hodges_lehmann(sp[c], wk[c])
    comp["hl_ci95_primary"] = hl_bootstrap_ci(sp[PRIMARY_CHANNEL], wk[PRIMARY_CHANNEL])
    comp["hl_ci90_primary"] = hl_bootstrap_ci(sp[PRIMARY_CHANNEL], wk[PRIMARY_CHANNEL],
                                              lo=TOST_CI[0], hi=TOST_CI[1])
    comp["hl_ci90_ankle"] = hl_bootstrap_ci(sp[ANKLE_CHANNEL], wk[ANKLE_CHANNEL],
                                            lo=TOST_CI[0], hi=TOST_CI[1])
    comp["meets_n_floor"] = bool(len(rows_s) >= MIN_N_PER_ARM
                                 and len(rows_w) >= MIN_N_PER_ARM)
    comp["null_forward"] = null_test(sp, wk, chans, reverse=False)
    comp["null_reverse"] = null_test(sp, wk, chans, reverse=True)
    return comp


def assert_conservation(label, total, parts):
    """Every count that partitions a set must sum to it. Checked at WRITE time; refused if not.

    Four of the ten halts on this document were machinery that could not fire. A partition
    that does not sum is machinery ANNOUNCING it did not fire, in a form a script can refuse.
    The rev-8 F6 bug would have deposited cells=16, admitted=14, excluded=0, quarantined=0 --
    16 != 14+0+0 -- and this assertion catches that class outright.
    """
    s = sum(parts.values())
    if s != total:
        raise SystemExit("CONSERVATION VIOLATED in %s: total %d != sum %d of %r"
                         % (label, total, s, parts))
    return True


def ledger_quarantined():
    """Cells the replay ledger records as E5_STO_0 (defect register #205).

    Rev 7 decided quarantine with os.path.exists, so DELETING one .sto moved a spastic
    exclusion rate from 0.250 to 0.200 and converted a voided null into a live substantive
    rung, with nothing on disk recording it. The ledger is the record; the filesystem is not.
    """
    p = os.path.join(PAPER, "BODY2_REPLAY_LEDGER_r229.json")
    if not os.path.exists(p):
        return None
    out = set()
    for a in json.load(io.open(p, encoding="utf-8")).get("attempts", []):
        if a.get("outcome") == "E5_STO_0":
            out.add((a.get("family"), a.get("seed")))
    return out


def preconditions():
    """Section 8's three preconditions, executed rather than asserted in prose.

    Rev 7 required sidecar VERIFICATION and map currency in the document only; nothing
    checked either at run time. A precondition that lives in prose is a hope.
    """
    import subprocess
    fails = []

    # (a) every sidecar verifies
    # THE SIDECARS are the independent second copy. Rev 9 compared against the manifest,
    # which is a single file -- so editing a deposit plus its one manifest line passed.
    man = os.path.join(PAPER, "BODY2_HASHES_r229.json")
    if not os.path.exists(man):
        fails.append("no BODY2_HASHES_r229.json -- nothing is hashed")
    else:
        rec = json.load(io.open(man, encoding="utf-8"))["files"]
        here = os.path.dirname(os.path.abspath(__file__))
        for name in rec:
            p = (os.path.join(PAPER, name) if name.endswith((".md", ".json"))
                 else os.path.join(here, name))
            side = p + ".sha256"
            if not os.path.exists(p):
                fails.append("hashed target missing: %s" % name)
                continue
            if not os.path.exists(side):
                fails.append("NO SIDECAR for %s" % name)
                continue
            want = io.open(side, encoding="utf-8").readline().split()[0]
            got = _sha256(p)
            if got != want:
                fails.append("SIDECAR MISMATCH: %s" % name)
            elif rec[name]["sha256"] != got:
                fails.append("MANIFEST DISAGREES WITH SIDECAR: %s" % name)

    # (b) the reachability map passes AND was driven against this exact file
    rm = os.path.join(PAPER, "BODY2_REACHABILITY_r229.json")
    if not os.path.exists(rm):
        fails.append("no reachability map")
    else:
        r = json.load(io.open(rm, encoding="utf-8"))
        if not r.get("GATE_PASSES"):
            fails.append("reachability gate does not pass")
        me = _sha256(os.path.abspath(__file__))
        if r.get("channels_sha256") != me:
            fails.append("reachability map is STALE: driven against %s, this file is %s"
                         % ((r.get("channels_sha256") or "?")[:12], me[:12]))

    # (d) THE CORPUS IS FROZEN. cell_dirs() globs at run time; without a registered manifest
    # new CMA-ES seeds enter the arms silently. This was the largest live degree of freedom.
    cm = os.path.join(PAPER, "BODY2_CORPUS_r229.json")
    if not os.path.exists(cm):
        fails.append("no BODY2_CORPUS_r229.json -- the corpus is not frozen")
    else:
        reg = json.load(io.open(cm, encoding="utf-8"))["cells"]
        for plane in PLANES:
            for fam in SPASTIC + WEAK:
                got = sorted(os.path.basename(d) for _s, d in cell_dirs(plane, fam))
                want = sorted(reg.get("%s_%s" % (plane, fam), []))
                if got != want:
                    fails.append("CORPUS DRIFT in %s_%s: %d on disk, %d registered"
                                 % (plane, fam, len(got), len(want)))

    # (c) the user's study is not running
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=60).stdout
        n = sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())
    except Exception:
        n = 999
    if n:
        fails.append("machine-wide sconecmd = %d; our cells give way" % n)

    if fails:
        raise SystemExit("PRECONDITIONS FAILED (section 8) -- run is void:\n  "
                         + "\n  ".join(fails))
    print("preconditions: sidecars verify, map current, sconecmd 0")


def decide(primary, gbrate, planes_agree):
    """THE CUT LADDER. Strict precedence, first match wins.

    Rev 9 declared fifteen rungs. Driving real synthetic data at n = 16 and the MEASURED
    sigma_2D = 0.1757 showed that ATTENUATED, ATTENUATED-reversed, CONSISTENT-WITH-3D, D5 and
    D4 cannot fire at any sigma inside the measured CI: a non-significant SMD bounds |HL|
    small enough that the 90 percent interval always lies inside +/-DELTA_EQUIV, so EQUIV
    absorbs the entire non-significant branch before any of them is reached. They are deleted
    rather than carried.

    Two further changes forced by the same analysis:

    B-REVERSED IS EVALUATED BEFORE THE A-FAMILY. Rev 9 placed it after, so a SIGNIFICANT hip
    reversal co-occurring with a forward-separating ankle was relabelled A-ANKLE-ONLY and the
    message asserted the hip "does not separate" while p_rev = 0.005.

    THE -ONLY RUNGS REQUIRE A BOUND, NOT A FAILURE. Rev 9 licensed "the ankle does not
    transfer" on a bare p >= alpha, which is the structure section 4 deleted an entire outcome
    to prevent. Each now requires the QUIET channel's HL 90 percent CI inside +/-DELTA_EQUIV.
    Where the quiet channel is neither significant nor bounded, A-MIXED says so.
    """
    if primary is None:
        return "D1", "no primary comparison object could be formed"
    if not primary["meets_n_floor"]:
        return "D2", "n < %d per arm after Gate B" % MIN_N_PER_ARM
    if gbrate is not None and abs(gbrate[0] - gbrate[1]) > GATE_B_IMBALANCE:
        return "F", ("Gate B exclusion rates %.2f vs %.2f differ by more than %.2f: null is "
                     "VOID: no substantive rung may be claimed"
                     % (gbrate[0], gbrate[1], GATE_B_IMBALANCE))
    if planes_agree is False:
        return "E", ("SG0 and SG2 disagree in SMD sign on the primary channel for the same "
                     "pair, and the SG2 comparison is large enough and significant enough "
                     "to support the disagreement")
    if primary.get("partial_only"):
        return "C", "primary pair relative dose difference exceeds 25 percent"

    nf, nr = primary["null_forward"], primary["null_reverse"]
    ci90 = primary.get("hl_ci90_primary")
    ci90a = primary.get("hl_ci90_ankle")
    if not ci90 or not ci90a:
        return "D1", "no primary comparison object could be formed (no HL interval)"

    pf, pr = nf["per_channel_p"], nr["per_channel_p"]
    smd = primary.get("smd", {})
    hip_fwd = pf.get(PRIMARY_CHANNEL, 1.0) < ALPHA_PER_DIRECTION and smd.get(PRIMARY_CHANNEL, 0.0) > 0
    ank_fwd = pf.get(ANKLE_CHANNEL, 1.0) < ALPHA_PER_DIRECTION and smd.get(ANKLE_CHANNEL, 0.0) > 0
    hip_rev = pr.get(PRIMARY_CHANNEL, 1.0) < ALPHA_PER_DIRECTION and smd.get(PRIMARY_CHANNEL, 0.0) < 0
    # A significant ANKLE reversal was booked as A-MIXED ("neither significant nor bounded",
    # "no claim about the quiet channel") at p = 0.001 -- the identical mislabelling fixed for
    # the hip one revision earlier, left uncorrected for the co-primary channel. It is not
    # exotic: the 3D ankle gap goes NEGATIVE at x0.915 (-0.0583) and x0.950 (-0.5560).
    ank_rev = pr.get(ANKLE_CHANNEL, 1.0) < ALPHA_PER_DIRECTION and smd.get(ANKLE_CHANNEL, 0.0) < 0

    def bounded(ci):
        return ci[0] > -DELTA_EQUIV and ci[1] < DELTA_EQUIV

    # B-reversed FIRST: a significant reversal is a finding, not a channel-transfer story.
    if hip_rev and ank_rev:
        return "B-reversed-BOTH", (
            "both %s (p %.5f) and %s (p %.5f) separate in the OPPOSITE direction: a positive "
            "reversed finding on both channels"
            % (PRIMARY_CHANNEL, pr[PRIMARY_CHANNEL], ANKLE_CHANNEL, pr[ANKLE_CHANNEL]))
    if hip_rev:
        return "B-reversed", ("%s separates in the OPPOSITE direction (p %.5f): a positive "
                              "reversed finding" % (PRIMARY_CHANNEL, pr[PRIMARY_CHANNEL]))
    if ank_rev:
        return "B-reversed-ANKLE", (
            "%s separates in the OPPOSITE direction (p %.5f): a positive reversed finding on "
            "the site channel" % (ANKLE_CHANNEL, pr[ANKLE_CHANNEL]))

    if hip_fwd and ank_fwd:
        return "A", ("both %s (p %.5f) and %s (p %.5f) separate in the predicted direction: "
                     "this is what the 3D data shows at the only shared severity"
                     % (PRIMARY_CHANNEL, pf[PRIMARY_CHANNEL], ANKLE_CHANNEL, pf[ANKLE_CHANNEL]))
    if hip_fwd and bounded(ci90a):
        return "A-HIP-ONLY", ("%s separates (p %.5f) and %s is BOUNDED below %.2f deg "
                              "(HL 90%% CI [%.3f, %.3f]): the 2D body separates more "
                              "specifically than 3D does here"
                              % (PRIMARY_CHANNEL, pf[PRIMARY_CHANNEL], ANKLE_CHANNEL,
                                 DELTA_EQUIV, ci90a[0], ci90a[1]))
    if ank_fwd and bounded(ci90):
        return "A-ANKLE-ONLY", ("%s separates (p %.5f) and %s is BOUNDED below %.2f deg "
                                "(HL 90%% CI [%.3f, %.3f]): the site channel transfers and "
                                "the compensation channel is bounded"
                                % (ANKLE_CHANNEL, pf[ANKLE_CHANNEL], PRIMARY_CHANNEL,
                                   DELTA_EQUIV, ci90[0], ci90[1]))
    if hip_fwd or ank_fwd:
        return "A-MIXED", ("one channel separates and the other is neither significant nor "
                           "bounded below %.2f deg: no claim may be made about the quiet "
                           "channel" % DELTA_EQUIV)
    if bounded(ci90) and bounded(ci90a):
        return "EQUIV", ("neither channel separates and both are BOUNDED below %.2f deg "
                         "(hip HL 90%% CI [%.3f, %.3f]): the effect does not transfer at a "
                         "magnitude this design can detect"
                         % (DELTA_EQUIV, ci90[0], ci90[1]))
    # ---- RESTORED. The five rungs deleted at r237 were deleted on the premise that a
    # ---- non-significant SMD always bounds |HL| inside +/-DELTA_EQUIV, so EQUIV would absorb
    # ---- the whole non-significant branch. THE PREMISE FAILED: the run measured a primary
    # ---- channel HL 95% CI of [-1.3914, -0.2473], half-width 0.572, ABOVE the 0.476 the
    # ---- attainability filter had called the ceiling. In that regime EQUIV is unreachable and
    # ---- these rungs are exactly what the non-significant branch needs. Registration section
    # ---- 1b registered the cut as PROVISIONAL pending this measurement; the measurement
    # ---- refuted it, so the deletions do not stand.
    ci95 = primary.get("hl_ci95_primary")
    if not ci95:
        # a missing 95% interval is a missing comparison OBJECT, not an uninformative result;
        # labelling it D4 put a degenerate guard ahead of D5 and broke the ladder order
        return "D1", "no primary comparison object could be formed (no 95% HL interval)"
    if ci95[0] > DELTA_3D_HL:
        return "D5", ("HL 95%% CI [%+.3f, %+.3f] lies ENTIRELY ABOVE the 3D shift %+.3f while "
                      "the SMD test is non-significant: internally inconsistent, to be "
                      "investigated rather than reported"
                      % (ci95[0], ci95[1], DELTA_3D_HL))
    if ci95[1] < 0.0:
        return "ATTENUATED-reversed", ("HL 95%% CI [%+.3f, %+.3f] lies entirely BELOW zero: "
                                       "the 2D effect runs opposite to the 3D one, with the "
                                       "SMD test non-significant" % (ci95[0], ci95[1]))
    if ci95[0] > 0.0 and ci95[1] < DELTA_3D_HL:
        return "ATTENUATED", ("HL 95%% CI [%+.3f, %+.3f] is positive and bounded above by the "
                              "3D shift %+.3f: the 2D effect is SMALLER than the 3D one, and "
                              "is not absent" % (ci95[0], ci95[1], DELTA_3D_HL))
    if ci95[0] > 0.0 and ci95[1] >= DELTA_3D_HL:
        return "CONSISTENT-WITH-3D", ("HL 95%% CI [%+.3f, %+.3f] is wholly positive and "
                                      "reaches or exceeds the 3D shift %+.3f: the interval is "
                                      "consistent with a 3D-sized effect"
                                      % (ci95[0], ci95[1], DELTA_3D_HL))
    return "D4", ("neither channel separates, the interval spans zero and at least one channel "
                  "is not bounded below %.2f deg: uninformative" % DELTA_EQUIV)


def main():
    preconditions()
    global DELTA_3D_HL
    dose_path = os.path.join(PAPER, "BODY2_DOSE_r229.json")
    if not os.path.exists(dose_path):
        raise SystemExit("HARD STOP: %s missing. Dose is measured first." % dose_path)
    dose = json.load(io.open(dose_path, encoding="utf-8"))
    prov = provenance()
    prov["inputs"] = {}
    for f in ("BODY2_DOSE_r229.json", "LADDER36_r228.json", "BODY2_DELTA_r229.json",
              "BODY2_REPLAY_LEDGER_r229.json", "BODY2_REACHABILITY_r229.json",
              "BODY2_CORPUS_r229.json"):
        fp = os.path.join(PAPER, f)
        if os.path.exists(fp):
            prov["inputs"][f] = _sha256(fp)
    prov["modules"] = module_hashes()
    # Rev 5: a control-seed-floor failure is NOT a dose-overlap stop. Rev 4 printed the
    # overlap message for both, so an infrastructure failure would have been recorded as a
    # substantive finding about matching.
    pl0 = dose.get("planes", {}).get(PRIMARY_PLANE, {})
    if pl0.get("error") == "CONTROL_SEED_FLOOR":
        raise SystemExit("HALT (section 5c, control-seed floor): %s\n"
                         "This is an INFRASTRUCTURE failure, not a finding about dose "
                         "matching. The overlap question was never reached."
                         % pl0.get("detail"))
    if "error" in pl0:
        raise SystemExit("HALT: primary plane not analysed: %r" % pl0)
    if not dose.get("ANY_OVERLAP_PRIMARY_PLANE"):
        raise SystemExit("HARD STOP (section 5c): no dose overlap in the primary plane after\n"
                         "leave-one-out. An unmatched pair answers a different question.")

    chans = [c + "_LmR" for c in CHANNELS]
    res = {"rev": 5, "window": [SETTLE, T1], "channel_family": chans,
           "primary_channel": PRIMARY_CHANNEL, "primary_plane": PRIMARY_PLANE,
           "alpha_total": ALPHA, "alpha_per_direction": ALPHA_PER_DIRECTION,
           "delta_3d_hl_deg": DELTA_3D_HL,
           "delta_3d_hl_range": DELTA_3D_HL_RANGE,
           "delta_3d_source": _SRC_D3D, "delta_equiv_source": _SRC_DEQ, "delta_3d_hl_range": DELTA_3D_HL_RANGE,
           "adjudicating_statistic": "standardised mean difference (primary channel)",
           "predicted_direction": "spastic_below_weak",
           "prediction_source_3D": {"spastic_mean_deg": -2.105,
                                    "weak_means_deg": [0.359, 0.443, 0.553],
                                    "deposit": "LADDER36_r228.json"},
           "provenance": prov,
           "note": "replicates the channel's behaviour, not the selection procedure",
           "planes": {}}

    primary_comp = None
    pinfo = dose.get("PRIMARY_PAIR")
    for plane in PLANES:
        arms, excluded = {}, []
        for fam in SPASTIC + WEAK:
            rows = []
            for seed, d in cell_dirs(plane, fam):
                r, why = per_cell(d)
                if r is None:
                    excluded.append({"family": fam, "seed": seed, "why": why})
                else:
                    r["seed"] = seed
                    rows.append(r)
            arms[fam] = rows

        pl = {"excluded": excluded, "gate_b": {}, "comparisons": []}
        for fam in SPASTIC + WEAK:
            tot = len(cell_dirs(plane, fam))
            ex = [e for e in excluded if e["family"] == fam]
            # F6: an absent or empty replay is an INFRASTRUCTURE non-result
            # (defect register #205's E5_STO_0), not evidence that the gait failed. Booking
            # it as Gate B attrition would let a sconecmd crash inflate the imbalance rate
            # and VOID the null via rung F.
            led = ledger_quarantined()
            if led is None:
                raise SystemExit("F6: no replay ledger. Quarantine may not be decided from "
                                 "the filesystem (section 5). Run body2_replay_r229.py first.")
            # PLANE-PREFIXED. body2_replay_r229.py writes FAMILIES entries
            # ("SG0_DR2K075"); rev 8 looked up the bare family and never matched,
            # so the ledger mechanism was dead code and quarantine stayed
            # filesystem-decided -- the exact defect it was written to close.
            key = "%s_%s" % (plane, fam)
            quar = [e for e in ex if (key, e["seed"]) in led]
            gateb = [e for e in ex if e["why"] != "REPLAY_MISSING"]
            denom = max(1, tot - len(quar))
            pl["gate_b"][fam] = {"cells": tot, "admitted": len(arms[fam]),
                                 "excluded_gate_b": len(gateb),
                                 "quarantined_replay_missing": len(quar),
                                 "quarantined_seeds": [e["seed"] for e in quar],
                                 "excluded_seeds": [e["seed"] for e in gateb],
                                 "rate": len(gateb) / float(denom),
                                 "rate_denominator": denom}
            assert_conservation("gate_b[%s/%s]" % (plane, fam), tot,
                                {"admitted": len(arms[fam]),
                                 "excluded_gate_b": len(gateb),
                                 "quarantined": len(quar)})

        pairs = [(p["spastic"], p["weak"])
                 for p in dose["planes"].get(plane, {}).get("pairs", [])
                 if p.get("overlaps_loo_unanimous")]
        # outcome E needs the SAME pair in both planes, so always evaluate it if present
        if pinfo and (pinfo["spastic"], pinfo["weak"]) not in pairs \
                and arms.get(pinfo["spastic"]) and arms.get(pinfo["weak"]):
            pairs = pairs + [(pinfo["spastic"], pinfo["weak"])]
        pl["matched_pairs"] = pairs
        for sfam, wfam in pairs:
            if len(arms.get(sfam, [])) < 2 or len(arms.get(wfam, [])) < 2:
                continue
            comp = compare(arms[sfam], arms[wfam], sfam, wfam, chans)
            comp["is_primary"] = bool(pinfo and plane == PRIMARY_PLANE
                                      and pinfo["spastic"] == sfam
                                      and pinfo["weak"] == wfam)
            comp["is_same_pair_as_primary"] = bool(pinfo and pinfo["spastic"] == sfam
                                                   and pinfo["weak"] == wfam)
            comp["role"] = "PRIMARY" if comp["is_primary"] else "secondary"
            comp["partial_only"] = bool(comp["is_primary"] and pinfo.get("partial_only"))
            rs, rw = pl["gate_b"][sfam]["rate"], pl["gate_b"][wfam]["rate"]
            comp["gate_b_rate"] = [rs, rw]
            comp["arm_imbalanced"] = bool(abs(rs - rw) > GATE_B_IMBALANCE)
            if comp["is_primary"]:
                primary_comp = comp
            pl["comparisons"].append(comp)
        res["planes"][plane] = pl

    nsec = sum(1 for p in PLANES for c in res["planes"][p]["comparisons"]
               if not c["is_primary"])
    # F10: familywise_p is ALREADY a max over the three channels, so the channel factor
    # is priced in it. Rev 6 multiplied by nsec * 3, counting the channels twice.
    res["secondary_family_size_pairs"] = nsec
    res["secondary_family_size_note"] = ("Bonferroni over PAIRS only; the 3-channel factor "
                                         "is already inside familywise_p")
    for p in PLANES:
        for c in res["planes"][p]["comparisons"]:
            if not c["is_primary"] and nsec:
                c["familywise_p_bonferroni"] = min(
                    1.0, c["null_forward"]["familywise_p"] * max(1, nsec))

    # outcome E: SAME pair, both planes
    def same_pair(plane):
        for c in res["planes"][plane]["comparisons"]:
            if c["is_same_pair_as_primary"]:
                # The n-floor and the alpha requirement are registered for SG2 ONLY. Rev 9
                # applied them to SG0 as well, so a non-significant SG0 made E unevaluable.
                if plane != PRIMARY_PLANE and (c["n_spastic"] < MIN_N_SG2_FOR_E
                                               or c["n_weak"] < MIN_N_SG2_FOR_E):
                    return None          # too small to support a disagreement
                # a disagreement must be SUPPORTED: the other plane's own primary-channel
                # test must reach alpha in its direction, or the sign is a coin flip
                if plane != PRIMARY_PLANE:
                    pf = c["null_forward"]["per_channel_p"][PRIMARY_CHANNEL]
                    pr = c["null_reverse"]["per_channel_p"][PRIMARY_CHANNEL]
                    if min(pf, pr) >= ALPHA_PER_DIRECTION:
                        return None      # SG2 unsupported: do not let it fire E
                # SMD SIGN ONLY. Rev 4 returned the raw disjointness string, so a plane pair
                # agreeing on sign, magnitude and significance still fired E when one plane
                # had a single crossing cell -- disjointness adjudicating through the back
                # door, and destroying exactly the strongest results.
                return (c["smd"][PRIMARY_CHANNEL] > 0,)
        return None
    a, b = same_pair(PRIMARY_PLANE), same_pair("SG2")
    if a is None or b is None:
        planes_agree, why_e = None, "same pair not available in both planes; E not evaluable"
    else:
        planes_agree, why_e = bool(a == b), "same pair compared in both planes"
    res["planes_agree_on_primary_channel"] = planes_agree
    res["planes_agree_note"] = why_e

    # DESCRIPTIVE ONLY: cycle-count-matched subset. Adjudicates nothing (post-treatment).
    if primary_comp:
        cs, cw = primary_comp["cycles_spastic"], primary_comp["cycles_weak"]
        lo, hi = max(min(cs), min(cw)), min(max(cs), max(cw))
        res["cycle_matched_DESCRIPTIVE_ONLY"] = {
            "band": [lo, hi],
            "note": ("selects on a post-treatment variable (usable-cycle count is a child of "
                     "achieved gait); reported as a description of the sample and adjudicates "
                     "nothing"),
            "n_spastic_in_band": int(sum(lo <= x <= hi for x in cs)),
            "n_weak_in_band": int(sum(lo <= x <= hi for x in cw))}

    outcome, why = decide(primary_comp,
                          primary_comp["gate_b_rate"] if primary_comp else None,
                          planes_agree)
    res["OUTCOME"] = outcome
    res["OUTCOME_REASON"] = why

    # Delta_3D SENSITIVITY. The registration says the range is USED, not merely computed:
    # re-decide at both endpoints of [2.4900, 2.7276] and record whether the label is stable.
    # Rev 6 computed DELTA_3D_HL_RANGE and never touched it.
    _keep = DELTA_3D_HL
    sens = {}
    for tag, val in (("low", DELTA_3D_HL_RANGE[0]), ("high", DELTA_3D_HL_RANGE[1])):
        DELTA_3D_HL = val
        o, w = decide(primary_comp,
                      primary_comp["gate_b_rate"] if primary_comp else None, planes_agree)
        sens[tag] = {"delta_3d": val, "outcome": o, "reason": w}
    DELTA_3D_HL = _keep
    sens["stable_across_range"] = bool(
        sens["low"]["outcome"] == outcome == sens["high"]["outcome"])
    res["delta_3d_sensitivity"] = sens
    if not sens["stable_across_range"]:
        print("WARNING: the outcome LABEL is not stable across the Delta_3D range: "
              "%s / %s / %s" % (sens["low"]["outcome"], outcome, sens["high"]["outcome"]))

    out = os.path.join(PAPER, "BODY2_CHANNELS_r229.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), indent=1)

    for plane in PLANES:
        pl = res["planes"][plane]
        print("=" * 88)
        print("PLANE %s" % plane)
        for fam, g in pl["gate_b"].items():
            if g["excluded_gate_b"] or g["quarantined_replay_missing"]:
                print("   gate B %-9s %d/%d excluded (rate %.2f)  quarantined %d  seeds %s"
                      % (fam, g["excluded_gate_b"], g["rate_denominator"], g["rate"],
                         g["quarantined_replay_missing"], g["excluded_seeds"]))
        for comp in pl["comparisons"]:
            print("-" * 88)
            print("  [%s] %s (n=%d) vs %s (n=%d)  n-floor %s  imbalanced %s"
                  % (comp["role"], comp["spastic"], comp["n_spastic"], comp["weak"],
                     comp["n_weak"], comp["meets_n_floor"], comp["arm_imbalanced"]))
            for c in chans:
                print("    %-18s SMD %+7.3f  HL %+7.4f deg  gap %+8.4f  %s (%s)"
                      % (c, comp["smd"][c], comp["hodges_lehmann_deg"][c],
                         comp["raw_gap_deg"][c],
                         "disjoint" if comp["disjoint_DESCRIPTIVE_ONLY"][c] else "overlapping",
                         comp["direction"][c]))
            print("    HL 95%% CI (primary channel): [%+.4f, %+.4f] deg"
                  % tuple(comp["hl_ci95_primary"]))
            n = comp["null_forward"]
            print("    forward null: %s, %d evaluated, primary p %.6f, familywise p %.6f"
                  % (n["method"], n["n_evaluated"], n["per_channel_p"][PRIMARY_CHANNEL],
                     n["familywise_p"]))
            print("    reverse null: primary p %.6f"
                  % comp["null_reverse"]["per_channel_p"][PRIMARY_CHANNEL])
    print("=" * 88)
    print("secondary family size (pairs) = %d" % res["secondary_family_size_pairs"])
    print("planes agree (same pair) = %s  [%s]" % (planes_agree, why_e))
    print("OUTCOME = %s  (%s)" % (outcome, why))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
