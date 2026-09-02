"""PRE-REGISTERED analysis for the downhill-provocation study (PREREG_slope.md).

THIS FILE IS HASHED BEFORE THE FIRST CELL LAUNCHES. Every constant, every exclusion, every
test and every verdict string below was fixed in advance. If this file's sha256 does not match
`paper/PREREG_slope.sha256`, the analysis is NOT the registered one and its output must be
discarded.

WHAT IS BEING ASKED
-------------------
Post-stroke equinus has two causes needing opposite treatments: plantarflexor SPASTICITY
(velocity-dependent stretch reflex, gain KV) and tibialis-anterior WEAKNESS (scaled
`max_isometric_force`). On level ground the two arms separate statistically but the MILD-severity
margin is +2.31 deg on `ank_stance_mean`, against a 3.8 deg clinical minimal detectable change.
Every candidate feature has died at that gap.

MECHANISM UNDER TEST (registered rationale, not a post-hoc story). Downhill walking drives faster
loading-phase dorsiflexion, which is exactly what a velocity-dependent stretch reflex resists; a
weak tibialis anterior is not provoked by the same demand. The two arms should therefore DIVERGE
MORE AS SLOPE STEEPENS.

The registered primary is therefore a SLOPE x MECHANISM INTERACTION, not "the margin got bigger".
A main effect of slope -- both arms gaining equinus together -- is a task effect and does NOT
count. That rule is inherited verbatim from PREREGISTRATION_slope_velocity_dependence.md and is
the whole reason the interaction, and not the margin, is primary.

WHY THERE IS NO UPHILL ARM. Every uphill run in this project's history carries min_velocity = 0.8
(signature S08W) against 1.0 (S10W) everywhere else, because uphill does not converge at 1.0 m/s.
Walking speed is the strongest single determinant of walking cost (r = -0.89), so an uphill anchor
would let a SPEED effect enter as a TASK effect. Uphill is dropped entirely and is not to be
reintroduced. Every cell in this study is S10W.

ENDPOINT, FIXED AND COMPUTABLE NOW
----------------------------------
    ank_stance_mean = sto_utils.cycle_features(sto, side="l", settle=1.0)["ank_stance_mean"]

  degrees; left (lesioned) ankle; mean over the GRF-DEFINED stance samples of each complete
  heel-strike-to-heel-strike cycle beginning at or after t = 1.0 s, averaged over cycles, with the
  last cycle dropped. Stance is the measured stance (vertical GRF above the same threshold the
  heel-strike detector used), never a fixed fraction of the stride.

    Delta_EQ(run) = mean(ank_stance_mean over the SAME-SLOPE K000 control cell) - ank_stance_mean(run)

  positive = MORE equinus. This is the identical convention and identical measure as the
  level-ground study's registered primary (COUNCIL_round48.md Section 1); running this pipeline on
  the existing level corpus reproduces that table's Delta_EQ column to four decimals
  (DR2K050 +2.5676, DR2K075 +1.4171, DR2K100 +2.0061, DR2K150 +5.8054, DR2K200 +7.3632).

  REFERENCING TO THE SAME-SLOPE CONTROL IS LOAD-BEARING. Walking downhill changes the ankle angle
  of ANY walker; without the per-slope control subtraction the "slope effect" would be dominated by
  that trivial geometric offset, which is common to both arms and carries no mechanism information.

PRIMARY TEST
------------
Fitted on the FOUR MILD RUNGS ONLY -- spastic K050/K075 x weak W20/W40 -- at three downhill
grades S = 0, 2, 5 (S is the downhill grade MAGNITUDE in degrees; there is no uphill):

    Delta_EQ_cond,slope = b0 + b_arm*ARM + b_slope*S + b_int*(ARM*S) + e      ARM = 1 spastic, 0 weak

UNIT OF ANALYSIS = CONDITION, not seed. Seeds are replicate searches of one physics, not subjects.
This is the level-ground study's registered unit and it is not changed here.
n = 2 arms x 2 rungs x 3 slopes = 12 condition means, residual df = 8.

    b_int = d(MARGIN)/dS,  MARGIN(S) = mean Delta_EQ(mild spastic) - mean Delta_EQ(mild weak)

DIRECTIONAL, one-sided, alpha = 0.05: the mechanism predicts b_int > 0 and nothing else is a
confirmation. A significant b_int < 0 is a REFUTATION, reported as such, never as "an effect".

CO-PRIMARY ESTIMATION TARGET (registered alongside, not instead)
    MARGIN(-5 deg) and its two-sided 95% CI, read against the 3.8 deg MDC.
    This is the clinically interpretable quantity and it is registered because the interaction
    p-value alone cannot say whether the margin became USABLE.

SECONDARY (never promotable to primary -- R45-S)
    S1  the same interaction fitted on ALL SIX lesion rungs (adds K100, W60). Better powered
        because three rungs per arm cut the rung-to-rung variance term; still secondary, because
        the problem this study exists to solve is at the MILD end.
    S2  seed-level refit of the primary. Reported as a sensitivity only; seeds are not subjects
        and a seed-level df is not an honest df if rung heterogeneity is real.
    S3  MARGIN(S) at each slope with CIs, at BOTH seed level and condition level.

REGISTERED EXCLUSIONS (applied in this order, before any endpoint is read)
    E1  launcher log missing, empty, or lacking "Starting optimization"
    E2  check_unused verdict is not clean for that cell's log (the injected block was discarded,
        or the log cannot establish either way)
    E3  the result directory cannot be resolved BY CONTENT to exactly one candidate. Content =
        min_progress == 0 AND max_generations == 90 AND terminal generation from history.txt == 89.
        NEVER by name and NEVER by mtime: SCONE appends " (1)" to colliding directories, and prior
        tag collisions in this project silently mixed two corpora at different budgets.
    E4  the registered replay does not produce exactly one .sto larger than 100000 bytes
    E5  cycle_features returns None -- fewer than two complete GRF-delimited cycles after settle.
        This is the "fell over" exclusion.
    E6  best fitness >= 3.0. That threshold is this project's existing convergence criterion
        (task_slope.GEN_CAP block, uphill_ladder.CONVERGED), not a number invented here.

    A cell retaining fewer than 6 of its 8 seeds is reported INDETERMINATE-BY-ATTRITION and is
    excluded from the primary fit, which is then reported as degraded and flagged. This follows
    the analysability-floor rule of PREREGISTRATION_dose_response_v2.md Section 3.3.

WHAT A NULL BUYS -- STATED BEFORE THE DATA EXIST
-----------------------------------------------
If b_int is not significantly positive and the MARGIN does not grow with slope, then the effect
size is NOT recoverable by provocation, and the level-ground negative becomes FINAL rather than
provisional. That is a publishable outcome and it is the reason this study is worth running. It is
NOT to be followed by another feature search, another manoeuvre, or another endpoint. Saying this
in advance is what stops it being spun afterwards.

Usage:  python slope_analysis.py            # resolve, replay, analyse, write SLOPE_RESULT.json
        python slope_analysis.py --no-replay # reuse an existing replay tree
"""
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sto_utils  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
OPTDIR = os.path.join(HERE, "opt_slope58")
LOGDIR = os.path.join(OPTDIR, "launch_logs")
DEST = os.path.join(HERE, "replay_slope58")
PAPER = os.path.abspath(os.path.join(HERE, "..", "paper"))

# ---------------------------------------------------------------- registered design constants
SEEDS = 8
SLOPES = [("L0", 0.0), ("D2", 2.0), ("D5", 5.0)]          # downhill grade MAGNITUDE, degrees
CONTROL = "K000"
MILD_SPASTIC = ["K050", "K075"]
MILD_WEAK = ["W20", "W40"]
MOD_SPASTIC = ["K100"]
MOD_WEAK = ["W60"]
ALL_SPASTIC = MILD_SPASTIC + MOD_SPASTIC
ALL_WEAK = MILD_WEAK + MOD_WEAK
CONDS = [CONTROL] + ALL_SPASTIC + ALL_WEAK

MDC = 3.8                      # clinical minimal detectable change, degrees
ALPHA = 0.05
FIT_MAX = 3.0                  # E6 convergence threshold
MIN_RETAINED = 6               # of SEEDS, below which a cell is INDETERMINATE-BY-ATTRITION
REGISTERED = {"min_progress": "0", "max_generations": "90"}
TERMINAL_GEN = 89
PAR_RE = re.compile(r"^(\d+)_([-0-9.eE+]+)_([-0-9.eE+]+)\.par$")

#: Registered magnitude predictions, Delta_EQ in degrees (positive = more equinus).
#: Level-ground entries are the MEASURED values from the existing crossed corpus and are
#: reproduced here so the predictions can be scored, not re-derived.
PREDICTED = {
    ("K050", 0.0): 2.57, ("K050", 2.0): 3.6, ("K050", 5.0): 5.4,
    ("K075", 0.0): 1.42, ("K075", 2.0): 2.4, ("K075", 5.0): 4.2,
    ("K100", 0.0): 2.01, ("K100", 2.0): 3.1, ("K100", 5.0): 5.0,
    ("W20", 0.0): -0.77, ("W20", 2.0): -0.7, ("W20", 5.0): -0.6,
    ("W40", 0.0): -0.13, ("W40", 2.0): -0.1, ("W40", 5.0): 0.0,
    ("W60", 0.0): 3.17, ("W60", 2.0): 3.3, ("W60", 5.0): 3.5,
}
PREDICTED_MARGIN = {0.0: 2.31, 2.0: 3.20, 5.0: 4.80}
PREDICTED_B_INT = 0.50         # deg per deg of downhill grade
MIN_MEANINGFUL_B_INT = (MDC - 2.31) / 5.0   # 0.298: the smallest interaction that would carry
#                                             the mild margin to the MDC at -5 deg


def tag_of(slope_code, cond):
    return "PG%s%s" % (slope_code, cond)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def prop(txt, key):
    m = re.search(r"^[ \t]*%s[ \t]*=[ \t]*(\S+)[ \t]*$" % key, txt, re.M)
    return m.group(1) if m else None


def parse_pars(d):
    out = []
    for p in glob.glob(os.path.join(d, "*.par")):
        m = PAR_RE.match(os.path.basename(p))
        if m:
            out.append((int(m.group(1)), float(m.group(3)), p))
    return out


# =============================================================================================
# E3 -- CONTENT-BASED DIRECTORY RESOLUTION. Name and mtime are never consulted.
# =============================================================================================
def is_registered_cell(d):
    cfg = os.path.join(d, "config.scone")
    if not os.path.exists(cfg):
        return False, "no config.scone"
    txt = open(cfg, encoding="utf-8", errors="ignore").read()
    for k, want in REGISTERED.items():
        got = prop(txt, k)
        if got != want:
            return False, "%s = %r (registered %r)" % (k, got, want)
    if not parse_pars(d):
        return False, "no .par"
    hist = os.path.join(d, "history.txt")
    if not os.path.exists(hist):
        return False, "no history.txt -- terminal generation cannot be established"
    with open(hist, encoding="utf-8", errors="ignore") as f:
        rows = sum(1 for ln in f if ln.strip())
    term = rows - 2                       # minus header, minus 1 for 0-indexing
    if term != TERMINAL_GEN:
        return False, "terminal generation %d (registered %d)" % (term, TERMINAL_GEN)
    return True, "ok"


def resolve(tag):
    cands = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    hits, why = [], []
    for d in cands:
        ok, note = is_registered_cell(d)
        (hits if ok else why).append((d, note))
    if len(hits) == 1:
        return hits[0][0], "1 of %d candidates by content" % len(cands)
    if not hits:
        raise ValueError("E3 %s: no candidate satisfies the content rule -> %s"
                         % (tag, "; ".join("%s: %s" % (os.path.basename(d), n) for d, n in why)))
    raise ValueError("E3 %s: %d candidates satisfy the content rule -- ambiguous, refusing to guess"
                     % (tag, len(hits)))


# =============================================================================================
# E1 / E2 -- launcher-log artifacts
# =============================================================================================
def log_verdict(tag):
    """(ok, detail). E1 then E2, using check_unused's own checker rather than a re-implementation."""
    lg = os.path.join(LOGDIR, "log_%s.txt" % tag)
    if not os.path.exists(lg):
        return False, "E1 no launcher log at %s" % lg
    if os.path.getsize(lg) == 0:
        return False, "E1 launcher log is zero bytes"
    txt = open(lg, encoding="utf-8", errors="ignore").read()
    if "Starting optimization" not in txt:
        return False, "E1 launcher log never reached 'Starting optimization'"
    try:
        import check_unused
        ok, msg = check_unused.check(lg)
    except Exception as e:                                    # pragma: no cover
        return False, "E2 check_unused could not run: %s" % e
    if ok is None:
        return False, "E2 check_unused ABSTAINED: %s" % msg
    if not ok:
        return False, "E2 check_unused FAILED: %s" % msg
    return True, "log ok (%d bytes); check_unused clean" % len(txt)


# =============================================================================================
# E4 / E5 / E6 -- registered replay and endpoint
# =============================================================================================
def replay(tag, do_replay=True):
    rec = {"tag": tag}
    ok, detail = log_verdict(tag)
    rec["log_ok"], rec["log_detail"] = ok, detail
    if not ok:
        rec["status"] = "EXCLUDED"
        return rec
    try:
        run_dir, note = resolve(tag)
    except ValueError as e:
        rec.update(status="EXCLUDED", detail=str(e))
        return rec
    rec["run_dir"], rec["resolved"] = run_dir, note

    newest = max((os.path.getmtime(p) for p in glob.glob(os.path.join(run_dir, "*.par"))),
                 default=0)
    if time.time() - newest < 120:
        rec.update(status="LIVE", detail="a .par was written %.0fs ago" % (time.time() - newest))
        return rec

    pars = parse_pars(run_dir)
    best = min(pars, key=lambda t: t[1])
    ties = [t for t in pars if abs(t[1] - best[1]) < 1e-12]
    if len(ties) > 1:
        rec.update(status="EXCLUDED",
                   detail="E3 tie: fitness %.6f at generations %s"
                          % (best[1], sorted(t[0] for t in ties)))
        return rec
    rec.update(best_gen=best[0], fitness=best[1], last_par_gen=max(t[0] for t in pars),
               terminal_gen=TERMINAL_GEN, gen_gap=TERMINAL_GEN - best[0], n_par=len(pars),
               min_progress=REGISTERED["min_progress"],
               max_generations=REGISTERED["max_generations"])
    if best[1] >= FIT_MAX:
        rec.update(status="EXCLUDED", detail="E6 best fitness %.3f >= %.1f -- not a gait"
                   % (best[1], FIT_MAX))
        return rec

    work = os.path.join(DEST, tag)
    if do_replay:
        if os.path.isdir(work):
            shutil.rmtree(work)
        os.makedirs(work)
        aux = (glob.glob(os.path.join(run_dir, "*.osim")) + glob.glob(os.path.join(run_dir, "*.zml"))
               + glob.glob(os.path.join(run_dir, "config.scone"))
               + [p for p in glob.glob(os.path.join(run_dir, "*.par"))
                  if not PAR_RE.match(os.path.basename(p))])
        for a in aux:
            shutil.copy2(a, work)
        local = os.path.join(work, os.path.basename(best[2]))
        shutil.copy2(best[2], local)
        try:
            subprocess.run([SCONECMD, "-e", local], cwd=work, capture_output=True, timeout=1800)
        except Exception as e:
            rec.update(status="EXCLUDED", detail="E4 replay failed: %s" % e)
            return rec
    if not os.path.isdir(work):
        rec.update(status="EXCLUDED", detail="E4 no replay directory")
        return rec
    stos = [s for s in glob.glob(os.path.join(work, "*.sto")) if os.path.getsize(s) > 100000]
    if len(stos) != 1:
        rec.update(status="EXCLUDED", detail="E4 replay produced %d .sto (want exactly 1)"
                   % len(stos))
        return rec
    f = sto_utils.cycle_features(stos[0], side="l")
    if f is None:
        rec.update(status="EXCLUDED",
                   detail="E5 fewer than 2 complete GRF-delimited cycles after settle")
        return rec
    rec.update(status="ok", sto=stos[0], sto_sha256=sha256(stos[0]),
               ank_stance_mean=f["ank_stance_mean"], ank_rom=f["ank_rom"],
               ank_hs=f["ank_hs"], n_cycles=f["n_cycles"], cycle_time=f["cycle_time"],
               utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with open(os.path.join(work, "PROVENANCE.json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    return rec


# =============================================================================================
# the registered model
# =============================================================================================
def ols(X, y):
    """-> (beta, se, df, resid_sd). Plain OLS; no library dependence beyond lstsq."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    df = len(y) - X.shape[1]
    s2 = float(r @ r) / df
    cov = s2 * np.linalg.pinv(X.T @ X)
    return beta, np.sqrt(np.diag(cov)), df, math.sqrt(s2)


def interaction_fit(cond_means, spastic, weak, label):
    """Delta_EQ ~ 1 + ARM + S + ARM*S on condition means. Returns a dict."""
    X, y, rows = [], [], []
    for arm, conds in ((1, spastic), (0, weak)):
        for c in conds:
            for code, S in SLOPES:
                v = cond_means.get((c, S))
                if v is None or not np.isfinite(v):
                    continue
                X.append([1.0, arm, S, arm * S])
                y.append(v)
                rows.append((c, S, arm, v))
    if len(y) < 6:
        return {"label": label, "status": "INSUFFICIENT", "n": len(y)}
    beta, se, df, rsd = ols(X, y)
    t = beta[3] / se[3] if se[3] > 0 else float("nan")
    p_one = 1.0 - stats.t.cdf(t, df)          # directional: b_int > 0 is the prediction
    tc = stats.t.ppf(1 - ALPHA / 2, df)
    return {"label": label, "status": "ok", "n": len(y), "df": int(df),
            "b0": beta[0], "b_arm": beta[1], "b_slope": beta[2], "b_int": beta[3],
            "se_b_int": se[3], "t_b_int": float(t), "p_one_sided": float(p_one),
            "ci95_b_int": [beta[3] - tc * se[3], beta[3] + tc * se[3]],
            "resid_sd": rsd,
            "significant_positive": bool(p_one < ALPHA and beta[3] > 0),
            "significant_negative": bool((1.0 - p_one) < ALPHA and beta[3] < 0),
            "rows": rows}


def margin_ci(a, b):
    """Two-sample t CI for mean(a) - mean(b). -> (diff, half_width, df)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float(np.mean(a) - np.mean(b)) if na and nb else float("nan"), float("nan"), 0
    sp2 = (((na - 1) * np.var(a, ddof=1)) + ((nb - 1) * np.var(b, ddof=1))) / (na + nb - 2)
    se = math.sqrt(sp2 * (1.0 / na + 1.0 / nb))
    df = na + nb - 2
    return float(np.mean(a) - np.mean(b)), float(stats.t.ppf(1 - ALPHA / 2, df) * se), int(df)


def main():
    do_replay = "--no-replay" not in sys.argv
    os.makedirs(DEST, exist_ok=True)

    want = ["%s_s%d" % (tag_of(code, c), s)
            for code, _S in SLOPES for c in CONDS for s in range(1, SEEDS + 1)]
    runs = {}
    print("=" * 96)
    print("DOWNHILL PROVOCATION STUDY -- REGISTERED ANALYSIS (PREREG_slope.md)")
    print("  endpoint  ank_stance_mean (deg), GRF-defined stance, settle 1.0 s, left ankle")
    print("  Delta_EQ  same-slope K000 control mean MINUS the run (positive = more equinus)")
    print("  primary   slope x mechanism INTERACTION on the four MILD rungs, condition-level,")
    print("            one-sided alpha = %.2f, predicted b_int = +%.2f deg/deg" % (ALPHA, PREDICTED_B_INT))
    print("=" * 96)
    for tag in want:
        r = replay(tag, do_replay)
        runs[tag] = r
        if r["status"] == "ok":
            print("  %-18s ok    fit %7.4f  best gen %2d/%d  %2d cycles  ank_stance_mean %+8.4f"
                  % (tag, r["fitness"], r["best_gen"], TERMINAL_GEN, r["n_cycles"],
                     r["ank_stance_mean"]))
        else:
            print("  %-18s %-9s %s" % (tag, r["status"], str(r.get("detail", r.get("log_detail", "")))[:78]))

    # ---- cell assembly + attrition -----------------------------------------------------------
    cells, attrition = {}, []
    for code, S in SLOPES:
        for c in CONDS:
            t = tag_of(code, c)
            v = [runs["%s_s%d" % (t, s)]["ank_stance_mean"] for s in range(1, SEEDS + 1)
                 if runs["%s_s%d" % (t, s)]["status"] == "ok"]
            cells[(c, S)] = v
            if len(v) < MIN_RETAINED:
                attrition.append((c, S, len(v)))

    print("\n  CELL RETENTION (registered floor %d of %d seeds)" % (MIN_RETAINED, SEEDS))
    for code, S in SLOPES:
        print("    %-3s (-%.0f deg): %s" % (code, S,
              "  ".join("%s %d/%d" % (c, len(cells[(c, S)]), SEEDS) for c in CONDS)))
    if attrition:
        print("\n  [INDETERMINATE-BY-ATTRITION] %s"
              % ", ".join("%s@-%.0f (%d/%d)" % (c, S, n, SEEDS) for c, S, n in attrition))

    # ---- Delta_EQ ----------------------------------------------------------------------------
    delta_seed, cond_means = {}, {}
    ctl_mean = {}
    for code, S in SLOPES:
        cv = cells[(CONTROL, S)]
        ctl_mean[S] = float(np.mean(cv)) if cv else float("nan")
        for c in CONDS:
            d = [ctl_mean[S] - x for x in cells[(c, S)]]
            delta_seed[(c, S)] = d
            cond_means[(c, S)] = float(np.mean(d)) if d else float("nan")

    print("\n  Delta_EQ (deg, positive = more equinus) -- condition means, predicted in brackets")
    print("    %-6s %22s %22s %22s" % ("cond", "level (0 deg)", "downhill -2 deg", "downhill -5 deg"))
    for c in ALL_SPASTIC + ALL_WEAK:
        cellsline = []
        for code, S in SLOPES:
            pr = PREDICTED.get((c, S))
            cellsline.append("%+8.3f [pred %+6.2f]" % (cond_means[(c, S)], pr if pr is not None else float("nan")))
        print("    %-6s %22s %22s %22s" % (c, cellsline[0], cellsline[1], cellsline[2]))
    print("    %-6s %22s %22s %22s"
          % ("K000", "control %+.3f" % ctl_mean[0.0], "control %+.3f" % ctl_mean[2.0],
             "control %+.3f" % ctl_mean[5.0]))

    # ---- PRIMARY -----------------------------------------------------------------------------
    primary = interaction_fit(cond_means, MILD_SPASTIC, MILD_WEAK, "PRIMARY mild-rung interaction")
    sec_all = interaction_fit(cond_means, ALL_SPASTIC, ALL_WEAK, "S1 all-rung interaction")

    print("\n  " + "-" * 92)
    for fit in (primary, sec_all):
        if fit["status"] != "ok":
            print("  %-34s %s (n=%d)" % (fit["label"], fit["status"], fit.get("n", 0)))
            continue
        print("  %-34s b_int %+7.4f  SE %6.4f  t(%d) %+6.3f  one-sided p %.4f  95%% CI [%+.3f, %+.3f]"
              % (fit["label"], fit["b_int"], fit["se_b_int"], fit["df"], fit["t_b_int"],
                 fit["p_one_sided"], fit["ci95_b_int"][0], fit["ci95_b_int"][1]))
        print("  %-34s b_arm %+7.4f  b_slope %+7.4f  residual SD %.4f"
              % ("", fit["b_arm"], fit["b_slope"], fit["resid_sd"]))

    # ---- CO-PRIMARY: MARGIN vs MDC -----------------------------------------------------------
    print("\n  MARGIN(S) = mild spastic - mild weak, Delta_EQ deg, against the %.1f deg MDC" % MDC)
    print("    %-8s %10s %10s %24s %10s %s"
          % ("slope", "margin", "predicted", "95% CI (seed-level)", "half-w", "vs MDC"))
    margins = {}
    for code, S in SLOPES:
        a = [x for c in MILD_SPASTIC for x in delta_seed[(c, S)]]
        b = [x for c in MILD_WEAK for x in delta_seed[(c, S)]]
        d, hw, df = margin_ci(a, b)
        ac = [cond_means[(c, S)] for c in MILD_SPASTIC]
        bc = [cond_means[(c, S)] for c in MILD_WEAK]
        dc, hwc, dfc = margin_ci(ac, bc)
        if d - hw > MDC:
            verdict = "CLEARS MDC (CI above)"
        elif d + hw < MDC:
            verdict = "BELOW MDC (CI below)"
        else:
            verdict = "indeterminate vs MDC"
        margins[S] = {"margin": d, "half_width": hw, "df": df, "n_spastic": len(a),
                      "n_weak": len(b), "verdict": verdict,
                      "cond_level_margin": dc, "cond_level_half_width": hwc,
                      "predicted": PREDICTED_MARGIN.get(S)}
        print("    -%-7.0f %10.3f %10.2f   [%+7.3f, %+7.3f] %10.3f %s"
              % (S, d, PREDICTED_MARGIN.get(S, float("nan")), d - hw, d + hw, hw, verdict))
        print("    %-8s (condition-level sensitivity: %+.3f +/- %.3f, df %d)"
              % ("", dc, hwc, dfc))

    # ---- S2 seed-level sensitivity -----------------------------------------------------------
    Xs, ys = [], []
    for arm, conds in ((1, MILD_SPASTIC), (0, MILD_WEAK)):
        for c in conds:
            for code, S in SLOPES:
                for v in delta_seed[(c, S)]:
                    Xs.append([1.0, arm, S, arm * S])
                    ys.append(v)
    seed_fit = None
    if len(ys) >= 8:
        beta, se, df, rsd = ols(Xs, ys)
        t = beta[3] / se[3] if se[3] > 0 else float("nan")
        seed_fit = {"b_int": beta[3], "se": se[3], "t": float(t), "df": int(df),
                    "p_one_sided": float(1.0 - stats.t.cdf(t, df)), "n": len(ys)}
        print("\n  S2 seed-level sensitivity (NOT the registered unit; seeds are not subjects):")
        print("     b_int %+7.4f  SE %6.4f  t(%d) %+6.3f  one-sided p %.4f  n=%d"
              % (beta[3], se[3], df, t, seed_fit["p_one_sided"], len(ys)))

    # ---- REGISTERED VERDICT ------------------------------------------------------------------
    print("\n" + "=" * 96)
    blocked = bool(attrition)
    if primary["status"] != "ok":
        verdict = "NO VERDICT -- the primary fit could not be formed (%s)" % primary["status"]
    elif primary["significant_positive"]:
        m5 = margins.get(5.0, {})
        if m5 and m5.get("verdict") == "CLEARS MDC (CI above)":
            verdict = ("PROVOCATION WORKS. The slope x mechanism interaction is positive and "
                       "significant AND the -5 deg mild margin clears the %.1f deg MDC." % MDC)
        else:
            verdict = ("INTERACTION CONFIRMED BUT NOT SUFFICIENT. b_int > 0 at alpha = %.2f, but "
                       "the -5 deg mild margin does not clear the %.1f deg MDC. Downhill "
                       "provocation moves the effect in the predicted direction without making it "
                       "clinically usable." % (ALPHA, MDC))
    elif primary["significant_negative"]:
        verdict = ("MECHANISM REFUTED IN THE OPPOSITE DIRECTION. b_int is significantly NEGATIVE: "
                   "the arms CONVERGE as the slope steepens, which contradicts the registered "
                   "velocity-dependence rationale outright.")
    else:
        verdict = ("NULL -- AND THE NEGATIVE IS NOW FINAL. The mild margin does not grow with "
                   "slope. Per the registration written before these data existed: the effect "
                   "size is NOT recoverable by provocation, the level-ground negative ceases to "
                   "be provisional, and this is NOT to be followed by another feature search, "
                   "another manoeuvre, or another endpoint.")
    if blocked:
        verdict = "[DEGRADED -- INDETERMINATE-BY-ATTRITION cells present] " + verdict
    print("  REGISTERED VERDICT: %s" % verdict)
    print("=" * 96)

    out = {"verdict": verdict, "alpha": ALPHA, "mdc": MDC, "seeds": SEEDS,
           "predicted_b_int": PREDICTED_B_INT,
           "min_meaningful_b_int": MIN_MEANINGFUL_B_INT,
           "predicted_delta_eq": {"%s@%.0f" % (c, S): v for (c, S), v in PREDICTED.items()},
           "primary": {k: v for k, v in primary.items() if k != "rows"},
           "secondary_all_rungs": {k: v for k, v in sec_all.items() if k != "rows"},
           "seed_level_sensitivity": seed_fit,
           "margins": {"%.0f" % S: v for S, v in margins.items()},
           "control_means": {"%.0f" % S: ctl_mean[S] for _c, S in SLOPES},
           "condition_means": {"%s@%.0f" % (c, S): cond_means[(c, S)] for c in CONDS for _c2, S in SLOPES},
           "retention": {"%s@%.0f" % (c, S): len(cells[(c, S)]) for c in CONDS for _c2, S in SLOPES},
           "attrition": [{"cond": c, "slope": S, "retained": n} for c, S, n in attrition],
           "runs": {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in runs.items()},
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(PAPER, exist_ok=True)
    o = os.path.join(PAPER, "SLOPE_RESULT.json")
    with open(o, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nwritten: %s" % o)
    return 0


if __name__ == "__main__":
    sys.exit(main())
