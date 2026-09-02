"""A5 RELAXED: gait cycles detected from the OBSERVED (degraded) kinematics, not from the clean GRF.

WHY THIS EXISTS
---------------
`scone/video_degradation.py` states assumption A5 in its own docstring and names it the study's
biggest single optimism:

    A5  GAIT-CYCLE SEGMENTATION IS TAKEN FROM THE CLEAN GROUND-REACTION FORCE and held FIXED across
        every noise level and repetition. A video pipeline has no force plate and must detect
        contacts from the noisy kinematics, which adds a second, independent failure mode.

The companion manuscript then asserts that the excluded effects "can only make it worse", so every
number is an upper bound. THAT IS AN ASSERTION, NOT A MEASUREMENT. This script converts it into a
measurement: the same registered sweep, over the same sigma x yaw x frame-rate grid, on the same 48
archived trajectories, with the gait cycles detected from the observed kinematics instead.

NO SIMULATION IS RUN. NO NEW TRAJECTORY IS GENERATED. Nothing under scone/replay_crossed/ is touched.

WHAT IS REUSED UNCHANGED
------------------------
This file imports `video_degradation` and calls, verbatim and without modification:
    load_runs()      the corpus loader, including its GRF heel-strike segmentation (kept as the
                     paired control arm, see below)
    prepare()        the A4 frame-capture resampling onto the fs grid
    project()        the A2 orthographic yaw projection
    fit_threshold()  the LOSO threshold fitter, direction fixed a priori
    deg_per_px()     the A3 pixel-to-degree mapping
and every registered constant: SETTLE, FC, BUTTER_ORDER, N_REP, FS_LIST, SIGMA_DEG, YAW_FIXED,
YAW_RANDOM, REF_THRESHOLD, MDC_DEG, SEED, the anthropometry, the condition lists and the MILD /
SEVERE / ALL splits. Assumptions A1, A2, A3, A4 and A6 are therefore bit-identical to the registered
study. ONLY A5 CHANGES.

THREE SEGMENTATIONS ARE COMPUTED IN THE SAME PASS, ON THE SAME NOISE REALISATIONS
---------------------------------------------------------------------------------
  GRF    the registered A5 control. Cycles from the clean ground-reaction force, exactly as in
         video_degradation.py. Present so that the A5-relaxed arms are compared against a GRF arm
         computed on the IDENTICAL noise draws rather than against an archived file generated from a
         different RNG stream. It doubles as a reproduction check on the archived JSON.
  DET_A  primary A5-relaxed detector. Heel strike = local MAXIMUM of the observed, projected, noisy,
         6 Hz low-passed SHANK orientation.
  DET_B  secondary, deliberately harsher A5-relaxed detector. Heel strike = local MAXIMUM of the
         observed ANKLE ANGLE -- the only signal the ROM pipeline itself consumes.

MODELLING CHOICES INVENTED FOR THIS RE-ANALYSIS, EVERY ONE OF THEM STATED
-------------------------------------------------------------------------
B1  WHICH SIGNAL THE DETECTOR SEES, AND ITS NOISE.
    The registered study adds one i.i.d. Gaussian of sd SIGMA_DEG to the observed ANKLE ANGLE and
    never needs a noisy shank signal. A kinematic event detector does. A3 already contains the
    decomposition needed, so nothing is invented here beyond making it explicit: with i.i.d.
    isotropic keypoint error SIGMA_PX on knee, ankle and toe,
        sd(shank orientation) = SIGMA_PX*sqrt(2)/L_shank ,  sd(foot orientation) = SIGMA_PX*sqrt(2)/L_foot
    and A3's ankle-angle sd is SIGMA_DEG = sqrt(sd_shank^2 + sd_foot^2). Inverting,
        sd_shank = SIGMA_DEG * L_foot  / hypot(L_shank, L_foot)   = 0.41436 * SIGMA_DEG
        sd_foot  = SIGMA_DEG * L_shank / hypot(L_shank, L_foot)   = 0.91011 * SIGMA_DEG
    Independent draws are applied to the projected shank and foot orientations. The observed ankle
    angle is then their difference, whose sd is exactly SIGMA_DEG. THE ROM COMPUTATION IS THEREFORE
    DISTRIBUTIONALLY IDENTICAL TO THE REGISTERED STUDY; the only new thing is that a shank signal
    with the correct correlated relationship to the ankle signal now exists to detect events on.
    (The realised RNG stream differs from the registered run because more numbers are drawn. That is
    why the GRF control arm is recomputed here rather than quoted.)

B2  THE EVENT RULE FOR DET_A: heel strike = local maximum of the observed shank orientation q_shank'
    (positive = ankle anterior to knee). Motivation is mechanical and standard: the shank reaches
    maximum forward inclination at initial contact, and shank-orientation / shank-angular-velocity
    landmarks are the usual kinematics-only substitute for a force plate. Measured against the GRF
    events on the CLEAN 100 Hz corpus, this landmark sits at 92-99 % of the GRF cycle, i.e. it LEADS
    true heel strike by roughly 0.07 s (2 frames at 30 Hz).
    THAT SYSTEMATIC LEAD IS NOT CORRECTED. A deployed pipeline does not know it, and a whole-cycle
    peak-to-peak is first-order insensitive to a constant phase shift of its window. Correcting it
    would be tuning against the ground truth this study is trying to do without.

B3  THE EVENT RULE FOR DET_B: heel strike = local maximum of the observed ankle angle (the terminal
    swing dorsiflexion peak). This detector is included precisely because it is worse: the ankle
    angle has a fifth of the shank's excursion, so it is the pessimistic bound on detector quality.

B4  PEAK-PICKING PARAMETERS. `scipy.signal.find_peaks` with
        distance   = 0.6 s  (both detectors)  -- a physiological floor on adult stride time; it is
                     below every stride time in this corpus (1.24-1.37 s) by a factor of two.
        prominence = 5.0 deg for DET_A -- an order of magnitude below the 70-90 deg shank excursion.
        prominence = 3.0 deg for DET_B -- a fifth of the smallest clean condition-mean ank_rom
                     (14.88 deg, DR2K100), and above the residual ripple of pose noise that has been
                     through the 6 Hz low-pass.
    DISCLOSED: before this file was hashed, detected CYCLE COUNTS (not any accuracy, margin or
    classification quantity) were inspected at sigma = 0, 2, 4, 8 deg and yaw 0, 30 deg for DET_A at
    prominence 5.0 and for DET_B at prominence 2.0 and 3.0. DET_B's prominence was set to 3.0 on
    that basis. No outcome number of any kind was computed before registration.

B5  THE FILTER IS APPLIED BEFORE DETECTION, with the same registered 4th-order zero-phase 6 Hz
    Butterworth used for the angle. A real pipeline filters once and uses the result for everything.
    This matters because §7.3 of the companion draft shows the filter is itself the largest single
    degradation in the study.

B6  CYCLE CONSTRUCTION AND THE SETTLE WINDOW mirror the registered code exactly: detected events
    before SETTLE = 1.0 s are discarded; cycles are consecutive event pairs; THE LAST CYCLE IS
    DROPPED, as in `load_runs`; a window shorter than 3 samples on the fs grid is discarded, as in
    `prepare`.

B7  WHAT COUNTS AS A DETECTION FAILURE, AND WHAT HAPPENS TO IT.
    HARD FAILURE: fewer than 2 usable cycles remain for a run in a repetition. `ank_rom` is then
    UNDEFINED for that run in that repetition -- the instrument returns no answer.
    A screening instrument that returns no answer has not returned a correct one. So in the PRIMARY
    accounting a hard failure is scored as a CLASSIFICATION ERROR for all three decision rules, and
    such a run is excluded from LOSO threshold FITTING (a missing value cannot vote) while still
    being counted as an error when it falls in the held-out fold. A COMPLETE-CASE accuracy, computed
    over successfully segmented runs only, is reported alongside every primary number so that a
    referee who prefers the other convention can read it directly. THE FAILURE RATE ITSELF IS
    REPORTED PER CELL AND IS A RESULT, NOT A DROPPED ROW.
    If every one of the 8 reference runs hard-fails in a repetition, REFCAL is undefined for that
    repetition and every run in it is scored as an error for REFCAL.
    SOFT FAILURE (over/under-segmentation): the detector returns a usable but wrong number of
    cycles. This is not detectable in deployment and is not scored as an error; it is reported as
    `cycle_count_err_rate` = fraction of runs whose detected cycle count differs from the GRF cycle
    count by more than 1, and it is the mechanism by which DET_B is expected to distort ROM.

WHAT IS BEING TESTED
--------------------
Whether the registered study's numbers are in fact an upper bound. If any A5-relaxed accuracy or
margin comes out HIGHER than its paired GRF value, the claim that the excluded effects "can only
make it worse" is falsified as stated, and the manuscript must say so.

PREDICTED OUTCOME IS REGISTERED IN paper/VIDEO_DEGRADATION_A5_REGISTRATION.txt WITH THE SHA-256 OF
THIS FILE, WRITTEN BEFORE THIS SCRIPT WAS EVER EXECUTED ON THE CORPUS.
"""
import json
import os
import sys
import time

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_degradation as V  # noqa: E402  -- every registered constant and function comes from here

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "paper", "VIDEO_DEGRADATION_A5.json"))

# --- B1: split of the registered SIGMA_DEG into its shank and foot components -------------------
_HYP = float(np.hypot(V.L_SHANK_M, V.L_FOOT_M))
K_SHANK = float(V.L_FOOT_M / _HYP)     # 0.41436
K_FOOT = float(V.L_SHANK_M / _HYP)     # 0.91011

# --- B4: peak-picking parameters ----------------------------------------------------------------
MIN_STRIDE_S = 0.6
PROM_DET_A = 5.0
PROM_DET_B = 3.0

SEGS = ["GRF", "DET_A", "DET_B"]


# ------------------------------------------------------------------------------------------------
def detect_cycles(sig, grid, fs, prominence):
    """B2/B3/B4/B6: local maxima of `sig` -> list of (i, j) cycle windows on the fs grid."""
    pk, _ = signal.find_peaks(sig, distance=max(int(round(MIN_STRIDE_S * fs)), 1),
                              prominence=prominence)
    pk = [int(p) for p in pk if grid[p] >= V.SETTLE]
    cyc = [(pk[i], pk[i + 1]) for i in range(len(pk) - 1)][:-1]      # B6: drop the last cycle
    return [(i, j) for i, j in cyc if j - i >= 3]                    # B6: mirror prepare()


def rom_from_windows(y, wins):
    """A6 peak-to-peak, mean over cycles. y is one 1-D filtered angle trace."""
    if len(wins) < 2:
        return np.nan                                               # B7: hard failure
    return float(np.mean([np.ptp(y[i:j]) for i, j in wins]))


# ------------------------------------------------------------------------------------------------
def loso_masked(vals, lab, seeds, complete_case):
    """LOSO with NaN = hard detection failure. `V.fit_threshold` is reused unchanged."""
    correct = n = 0
    ok_all = ~np.isnan(vals)
    for k in sorted(set(seeds)):
        tr = seeds != k
        te = ~tr
        trv = tr & ok_all
        tev = te & ok_all if complete_case else te
        if trv.sum() < 2 or tev.sum() == 0 or len(set(lab[trv])) < 2:
            continue
        thr = V.fit_threshold(vals[trv], lab[trv])
        pred = (vals[tev] < thr).astype(int)
        good = (pred == lab[tev]) & ~np.isnan(vals[tev])
        correct += int(good.sum())
        n += int(tev.sum())
    return correct / n if n else np.nan


def rule_acc(vals, thr, lab):
    """(primary, complete_case) accuracy of a threshold rule. NaN -> error in primary."""
    ok = ~np.isnan(vals)
    if np.ndim(thr) == 1:
        thr = thr[:, None]
    good = ((vals < thr).astype(int) == lab) & ok
    prim = good.sum(axis=1) / vals.shape[1]
    with np.errstate(invalid="ignore", divide="ignore"):
        cc = np.where(ok.sum(axis=1) > 0, good.sum(axis=1) / np.maximum(ok.sum(axis=1), 1), np.nan)
    return prim, cc


def evaluate(rom, runs, ridx):
    """rom: (nrep, nrun) with NaN for hard failures. -> per-split accuracies and margins."""
    out = {}
    R = rom[:, ridx]
    with np.errstate(invalid="ignore"):
        ref_rom = np.nanmean(np.where(np.isnan(R), np.nan, R), axis=1)
    ref_bad = np.isnan(ref_rom)
    for name, (sp_c, wk_c) in V.SPLITS.items():
        idx = np.array([i for i, r in enumerate(runs) if r["cond"] in sp_c + wk_c])
        lab = np.array([1 if runs[i]["cond"] in sp_c else 0 for i in idx])
        seeds = np.array([runs[i]["seed"] for i in idx])
        A = rom[:, idx]
        nrep = A.shape[0]
        loso = np.array([loso_masked(A[r], lab, seeds, False) for r in range(nrep)])
        loso_cc = np.array([loso_masked(A[r], lab, seeds, True) for r in range(nrep)])
        ref_p, ref_c = rule_acc(A, V.REF_THRESHOLD, lab)
        rc_thr = np.where(ref_bad, -np.inf, ref_rom)      # undefined REFCAL -> everything "weak"
        rcal_p, rcal_c = rule_acc(A, rc_thr, lab)
        rcal_p = np.where(ref_bad, 0.0, rcal_p)
        rcal_c = np.where(ref_bad, 0.0, rcal_c)
        with np.errstate(invalid="ignore"):
            gm_sp = np.nanmean(A[:, lab == 1], axis=1)
            gm_wk = np.nanmean(A[:, lab == 0], axis=1)
            cs = np.array([np.nanmean(A[:, [j for j, i in enumerate(idx)
                                            if runs[i]["cond"] == c]], axis=1) for c in sp_c])
            cw = np.array([np.nanmean(A[:, [j for j, i in enumerate(idx)
                                            if runs[i]["cond"] == c]], axis=1) for c in wk_c])
            gap = np.nanmin(cw, axis=0) - np.nanmax(cs, axis=0)
        fin = lambda x: float(np.nanmean(x)) if np.isfinite(np.asarray(x, float)).any() else None
        out[name] = {
            "n_runs": int(len(idx)),
            "fail_rate": float(np.mean(np.isnan(A))),
            "loso_mean": fin(loso), "loso_sd": float(np.nanstd(loso)),
            "loso_p05": float(np.nanpercentile(loso, 5)),
            "loso_cc_mean": fin(loso_cc),
            "ref_mean": fin(ref_p), "ref_sd": float(np.nanstd(ref_p)), "ref_cc_mean": fin(ref_c),
            "refcal_mean": fin(rcal_p), "refcal_sd": float(np.nanstd(rcal_p)),
            "refcal_cc_mean": fin(rcal_c),
            "margin_groupmean": fin(gm_wk - gm_sp),
            "margin_groupmean_sd": float(np.nanstd(gm_wk - gm_sp)),
            "margin_gap": fin(gap), "margin_gap_sd": float(np.nanstd(gap)),
            "margin_gap_p_negative": float(np.mean(np.asarray(gap) < 0)),
            "rom_spastic": fin(gm_sp), "rom_weak": fin(gm_wk),
        }
    out["_ref_rom"] = fin(ref_rom)
    out["_ref_undefined_rate"] = float(np.mean(ref_bad))
    return out


# ------------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    rng = np.random.default_rng(V.SEED)
    runs = V.load_runs()
    ridx = np.array([i for i, r in enumerate(runs) if r["cond"] in V.REFERENCE])
    print("loaded %d runs (%d reference); A5-relaxed re-analysis" % (len(runs), len(ridx)))
    print("B1 noise split: sd_shank = %.5f*sigma, sd_foot = %.5f*sigma (sum of squares %.6f)"
          % (K_SHANK, K_FOOT, K_SHANK ** 2 + K_FOOT ** 2))

    prep = {}
    for fs in V.FS_LIST:
        b, a = signal.butter(V.BUTTER_ORDER, V.FC / (fs / 2.0), btype="low")
        prep[fs] = (b, a, [V.prepare(r, fs) for r in runs])

    dpp_1080, dpp_720 = V.deg_per_px(V.PX_PER_M_1080), V.deg_per_px(V.PX_PER_M_720)
    cells = []
    yaws = [("fixed", y) for y in V.YAW_FIXED] + [("random", y) for y in V.YAW_RANDOM]
    for fs in V.FS_LIST:
        b, a, pr = prep[fs]
        for ymode, ymax in yaws:
            for sd in V.SIGMA_DEG:
                nrep = 1 if (sd == 0.0 and ymode == "fixed") else V.N_REP
                rom = {s: np.full((nrep, len(runs)), np.nan) for s in SEGS}
                ncyc = {s: np.zeros((nrep, len(runs)), int) for s in SEGS}
                terr = {s: [] for s in ("DET_A", "DET_B")}
                for k, (grid, qs, qf, wins_grf) in enumerate(pr):
                    if ymode == "fixed":
                        cos_t = np.cos(np.radians(ymax))
                        qs_o = np.arctan2(np.sin(qs) * cos_t, np.cos(qs))[None, :]
                        qf_o = np.arctan2(np.sin(qf), np.cos(qf) * cos_t)[None, :]
                        if nrep > 1:
                            qs_o = np.repeat(qs_o, nrep, axis=0)
                            qf_o = np.repeat(qf_o, nrep, axis=0)
                    else:
                        th = rng.uniform(0.0, ymax, size=nrep)[:, None]      # per-subject yaw
                        ct = np.cos(np.radians(th))
                        qs_o = np.arctan2(np.sin(qs)[None, :] * ct, np.cos(qs)[None, :])
                        qf_o = np.arctan2(np.sin(qf)[None, :], np.cos(qf)[None, :] * ct)
                    sh = np.degrees(qs_o)
                    ft = np.degrees(qf_o)
                    if sd > 0:                                               # B1
                        sh = sh + rng.normal(0.0, sd * K_SHANK, size=sh.shape)
                        ft = ft + rng.normal(0.0, sd * K_FOOT, size=ft.shape)
                    y_ank = signal.filtfilt(b, a, ft - sh, axis=-1)          # A6 / B5
                    y_sh = signal.filtfilt(b, a, sh, axis=-1)                # B5
                    gt = np.array([grid[i] for i, j in wins_grf]) if wins_grf else np.array([])
                    for r in range(nrep):
                        wa = detect_cycles(y_sh[r], grid, fs, PROM_DET_A)
                        wb = detect_cycles(y_ank[r], grid, fs, PROM_DET_B)
                        rom["GRF"][r, k] = rom_from_windows(y_ank[r], wins_grf)
                        rom["DET_A"][r, k] = rom_from_windows(y_ank[r], wa)
                        rom["DET_B"][r, k] = rom_from_windows(y_ank[r], wb)
                        ncyc["GRF"][r, k] = len(wins_grf)
                        ncyc["DET_A"][r, k] = len(wa)
                        ncyc["DET_B"][r, k] = len(wb)
                        if len(gt):
                            for nm, w in (("DET_A", wa), ("DET_B", wb)):
                                if w:
                                    d = np.array([grid[i] for i, j in w])
                                    terr[nm].append(np.abs(d[:, None] - gt[None, :]).min(axis=1))
                cell = {"fs": fs, "yaw_mode": ymode, "yaw_deg": ymax, "sigma_deg": sd,
                        "sigma_px_1080p": sd / dpp_1080, "sigma_px_720p": sd / dpp_720,
                        "n_rep": nrep, "seg": {}}
                for s in SEGS:
                    d = {"splits": evaluate(rom[s], runs, ridx),
                         "hard_fail_rate": float(np.mean(np.isnan(rom[s]))),
                         "mean_cycles": float(np.mean(ncyc[s])),
                         "cycle_count_err_rate":
                             float(np.mean(np.abs(ncyc[s] - ncyc["GRF"]) > 1))}
                    if s in terr and terr[s]:
                        err = np.concatenate(terr[s])
                        d["event_abs_err_median_s"] = float(np.median(err))
                        d["event_abs_err_p90_s"] = float(np.percentile(err, 90))
                    cell["seg"][s] = d
                cells.append(cell)
            print("  fs=%g yaw %s %g done (%.0f s)" % (fs, ymode, ymax, time.time() - t0))

    # ---- console tables ------------------------------------------------------------------------
    def show(fs, ymode, ymax):
        print("\n=== fs=%g Hz, yaw %s %g deg : GRF vs DET_A vs DET_B ===" % (fs, ymode, ymax))
        print("%6s | %-23s | %-23s | %-23s | %-17s"
              % ("sd", "GRF  loso/ref/refcal", "DET_A loso/ref/refcal",
                 "DET_B loso/ref/refcal", "MILDgap G/A/B"))
        for c in cells:
            if c["fs"] != fs or c["yaw_mode"] != ymode or c["yaw_deg"] != ymax:
                continue
            row = "%6.1f |" % c["sigma_deg"]
            for s in SEGS:
                m = c["seg"][s]["splits"]["MILD"]
                row += " %.3f %.3f %.3f |" % (m["loso_mean"], m["ref_mean"], m["refcal_mean"])
            row += " " + " ".join("%+6.2f" % c["seg"][s]["splits"]["MILD"]["margin_gap"]
                                  for s in SEGS)
            print(row)
        print("  detection: " + "; ".join(
            "%s fail %.3f%% cyc %.2f cycerr %.3f" % (
                s, 100 * np.mean([c["seg"][s]["hard_fail_rate"] for c in cells
                                  if c["fs"] == fs and c["yaw_mode"] == ymode
                                  and c["yaw_deg"] == ymax]),
                np.mean([c["seg"][s]["mean_cycles"] for c in cells
                         if c["fs"] == fs and c["yaw_mode"] == ymode and c["yaw_deg"] == ymax]),
                np.mean([c["seg"][s]["cycle_count_err_rate"] for c in cells
                         if c["fs"] == fs and c["yaw_mode"] == ymode and c["yaw_deg"] == ymax]))
            for s in SEGS))

    for ymode, ymax in yaws:
        show(30.0, ymode, ymax)
    show(60.0, "fixed", 0.0)

    # ---- failure rates against noise, the registered deliverable --------------------------------
    print("\n=== HARD DETECTION FAILURE RATE (%% of run-repetitions), fs = 30 Hz ===")
    print("%6s | %-28s | %-28s" % ("sd", "DET_A  yaw0/10/20/30/r15/r30", "DET_B  same"))
    for sdv in V.SIGMA_DEG:
        parts = []
        for s in ("DET_A", "DET_B"):
            vals = []
            for ymode, ymax in yaws:
                c = [c for c in cells if c["fs"] == 30.0 and c["yaw_mode"] == ymode
                     and c["yaw_deg"] == ymax and c["sigma_deg"] == sdv][0]
                vals.append(100 * c["seg"][s]["hard_fail_rate"])
            parts.append(" ".join("%5.2f" % v for v in vals))
        print("%6.1f | %s | %s" % (sdv, parts[0], parts[1]))

    print("\n=== MEAN DETECTED CYCLES vs GRF, fs = 30 Hz, yaw 0 ===")
    for c in sorted([c for c in cells if c["fs"] == 30.0 and c["yaw_mode"] == "fixed"
                     and c["yaw_deg"] == 0.0], key=lambda c: c["sigma_deg"]):
        print("  sd %4.1f : GRF %.2f  DET_A %.2f (cycerr %.3f)  DET_B %.2f (cycerr %.3f)"
              % (c["sigma_deg"], c["seg"]["GRF"]["mean_cycles"],
                 c["seg"]["DET_A"]["mean_cycles"], c["seg"]["DET_A"]["cycle_count_err_rate"],
                 c["seg"]["DET_B"]["mean_cycles"], c["seg"]["DET_B"]["cycle_count_err_rate"]))

    # ---- did anything get BETTER? the registered question ---------------------------------------
    better = []
    for c in cells:
        for s in ("DET_A", "DET_B"):
            for split in ("MILD", "SEVERE"):
                g = c["seg"]["GRF"]["splits"][split]
                d = c["seg"][s]["splits"][split]
                for key in ("loso_mean", "ref_mean", "refcal_mean", "margin_gap"):
                    if d[key] is not None and g[key] is not None and d[key] > g[key] + 1e-9:
                        better.append({"fs": c["fs"], "yaw_mode": c["yaw_mode"],
                                       "yaw_deg": c["yaw_deg"], "sigma_deg": c["sigma_deg"],
                                       "seg": s, "split": split, "key": key,
                                       "grf": g[key], "a5": d[key]})
    ntest = len(cells) * 2 * 2 * 4
    print("\n=== 'CAN ONLY MAKE IT WORSE' TEST ===")
    print("  %d of %d paired comparisons come out HIGHER under A5-relaxed segmentation (%.1f%%)"
          % (len(better), ntest, 100.0 * len(better) / ntest))
    inv = [c for c in cells
           if c["seg"]["DET_A"]["splits"]["MILD"]["margin_gap"] is not None
           and c["seg"]["DET_A"]["splits"]["MILD"]["margin_gap"] < 0]
    invb = [c for c in cells
            if c["seg"]["DET_B"]["splits"]["MILD"]["margin_gap"] is not None
            and c["seg"]["DET_B"]["splits"]["MILD"]["margin_gap"] < 0]
    print("  MILD margin mean SIGN INVERTED (< 0): DET_A in %d/%d cells, DET_B in %d/%d cells"
          % (len(inv), len(cells), len(invb), len(cells)))
    for c in inv + invb:
        print("    INVERTED: fs%g yaw %s %g sd %g" % (c["fs"], c["yaw_mode"], c["yaw_deg"],
                                                      c["sigma_deg"]))

    out = {
        "what": "A5-relaxed re-analysis: gait cycles from observed kinematics, not clean GRF",
        "no_simulation_run": True,
        "parent_study": "scone/video_degradation.py -> paper/VIDEO_DEGRADATION.json",
        "n_runs": len(runs),
        "segmentations": {
            "GRF": "clean ground-reaction force (the registered A5 control, recomputed here on the "
                   "same noise draws)",
            "DET_A": "local maximum of the observed 6 Hz low-passed SHANK orientation, "
                     "prominence %.1f deg, min stride %.1f s" % (PROM_DET_A, MIN_STRIDE_S),
            "DET_B": "local maximum of the observed 6 Hz low-passed ANKLE ANGLE, "
                     "prominence %.1f deg, min stride %.1f s" % (PROM_DET_B, MIN_STRIDE_S),
        },
        "parameters": {
            "inherited_from_video_degradation": {
                "settle_s": V.SETTLE, "lowpass_hz": V.FC, "butter_order": V.BUTTER_ORDER,
                "n_rep": V.N_REP, "fs_list": V.FS_LIST, "sigma_deg": V.SIGMA_DEG,
                "yaw_fixed_deg": V.YAW_FIXED, "yaw_random_max_deg": V.YAW_RANDOM,
                "ref_threshold_deg": V.REF_THRESHOLD, "mdc_deg": V.MDC_DEG, "rng_seed": V.SEED,
                "l_shank_m": V.L_SHANK_M, "l_foot_m": V.L_FOOT_M,
            },
            "new_for_a5": {
                "k_shank": K_SHANK, "k_foot": K_FOOT, "min_stride_s": MIN_STRIDE_S,
                "prominence_det_a_deg": PROM_DET_A, "prominence_det_b_deg": PROM_DET_B,
                "hard_failure": "fewer than 2 usable cycles -> ank_rom undefined -> scored as a "
                                "classification error in the primary accounting; complete-case "
                                "accuracies reported alongside",
            },
        },
        "cells": cells,
        "improved_vs_grf": better,
        "n_paired_comparisons": ntest,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("\nwrote %s (%d bytes) in %.0f s" % (OUT, os.path.getsize(OUT), time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
