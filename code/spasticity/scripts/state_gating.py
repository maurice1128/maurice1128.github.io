"""STATE-GATING oracle for injected SCONE reflex blocks.

Companion to delivered_gain.py.  delivered_gain answers "did the declared AMOUNT arrive?";
this module answers "did it arrive during the declared GAIT PHASES, and only those?".

Retrospective: needs only an archived (config.scone, *.sto) pair.  Runs no simulation.

Method
------
SCONE stores the GaitStateController per-leg phase index as a channel, leg0_l.state /
leg1_r.state.  The mapping index -> phase name was established empirically by running one
scenario per omitted phase (see report): 0 EarlyStance, 1 LateStance, 2 Liftoff,
3 Swing, 4 Landing.  It is re-verified inside every call against the base controller own
gated reflexes when present (a reflex declared over a proper subset of the phases pins that
subset), so a SCONE build that renumbered the enum would ABSTAIN, not mislead.

A ConditionalController that is inactive writes an EXACT 0.0 into its children contribution
channels (measured: soleus_l.RF, declared over EarlyStance/LateStance/Liftoff, is 0.000000
in 459/459 Swing+Landing samples of T1LEGS).  So the temporal support of the contribution
channel IS the gate -- provided one conditions on the reflex having something to contribute.
A half-wave-rectified velocity reflex (allow_neg_V = 0) is legitimately zero wherever the
muscle is not lengthening: in T1LEGS soleus_l.RV is zero in 160 of the 214 EarlyStance
samples with the gate fully open.  The test is therefore run only on OPPORTUNITY samples --
those where the declared, delay-shifted predictor is non-zero.

Verdicts: PASS / FAIL / ABSTAIN.  Never PASS on an unreadable or ambiguous condition.
"""
import numpy as np, os, sys, glob, re

sys.path.insert(0, r"C:/Users/maurice/Desktop/spasticity_paper/scone")
import delivered_gain as dg

STATE_NAMES = ["EarlyStance", "LateStance", "Liftoff", "Swing", "Landing"]
STATE_IDX = {n.lower(): i for i, n in enumerate(STATE_NAMES)}

EPS_C_REL = 1e-9   # a contribution counts as active above this x the channel own peak.
                   # SCONE writes an exact 0.0 when gated off, so this only has to clear
                   # ASCII round-off, not a physical threshold.
EPS_P_REL = 1e-4   # opportunity threshold on the predictor, relative to its own peak
MIN_OPP = 8        # retained only for the reporting threshold below; the OPEN/CLOSED/UNDECIDED
                   # decision no longer uses it -- see the Wilson-interval rule in `check()`.
CI_ALPHA = 0.05    # two-sided level for the Wilson interval on duty
ERODE = 1          # opportunity samples this close to a predictor on/off edge are discarded
OPEN_MIN = 0.90    # duty at or above this -> the gate is OPEN in that phase
CLOSED_MAX = 0.10  # duty at or below this -> the gate is CLOSED in that phase
                   # Anything between the two is AMBIGUOUS and forces ABSTAIN. The band is
                   # empty in practice: over the eight calibration runs every open phase
                   # scored 0.95-1.00 and every closed phase scored exactly 0.00.


def walk_states(node, path=(), sym=None, legs=None, cname=None, states=None, out=None):
    """dg.walk_reflexes() carries symmetric/legs/name down the tree but discards `states`,
    which is the whole subject of this module. Same traversal, one more inherited field."""
    if out is None:
        out = []
    for key, val in node:
        if isinstance(val, list):
            mysym, mylegs, myname, myst = sym, legs, cname, states
            for k2, v2 in val:
                if isinstance(v2, list):
                    continue
                if k2 == "symmetric":
                    mysym = int(float(v2))
                elif k2 == "legs":
                    mylegs = str(v2).strip().strip('"').lower()
                elif k2 == "name":
                    myname = str(v2).strip().strip('"')
                elif k2 == "states":
                    myst = str(v2).strip().strip('"')
            if key.endswith("Reflex"):
                out.append({"kind": key, "symmetric": mysym, "legs": mylegs,
                            "cname": myname, "states": myst,
                            "props": {k: v for k, v in val if not isinstance(v, list)}})
            else:
                walk_states(val, path + (key,), mysym, mylegs, myname, myst, out)
    return out


def state_set(s):
    """Declared states string -> set of indices. Raises on any token SCONE would reject
    (SCONE itself aborts with 'Invalid string: <tok>' -- verified -- so an unparseable token
    can never reach an archived .sto; raising here keeps the two consistent)."""
    if s is None:
        return set(range(5))
    toks = [t for t in re.split(r"[\s;,]+", s.strip()) if t]
    idx = set()
    for t in toks:
        if t.lower() not in STATE_IDX:
            raise ValueError("unknown gait state %r in states=%r" % (t, s))
        idx.add(STATE_IDX[t.lower()])
    if not idx:
        raise ValueError("empty states list")
    return idx


GRF_STANCE_MIN = 0.15   # mean normalised vertical GRF a load-bearing phase must exceed
GRF_FLIGHT_MAX = 0.15   # ... and a flight phase must stay under


def _grf_anchor(col, side, t):
    """Ground the phase INDICES in ground-reaction force, not only in the enum order.

    EarlyStance/LateStance/Liftoff are load-bearing and Swing/Landing are not, whatever a
    SCONE build calls them.  If the run's own GRF does not agree with that, the index->phase
    map cannot be trusted for this file and the check must ABSTAIN rather than report a
    phase-resolved verdict against the wrong indices.  Measured on T1LEGS, mean
    leg0_l.grf_norm_y by index: 0.900, 0.942, 0.487, 0.005, 0.003.
    """
    stc = [k for k in col if re.match(r"^leg\d+_%s\.state$" % side[-1], k)]
    grf = [k for k in col if re.match(r"^leg\d+_%s\.grf_norm_y$" % side[-1], k)]
    if len(stc) != 1 or len(grf) != 1:
        return None
    st, g = col[stc[0]], col[grf[0]]
    means = {}
    for j in range(5):
        m = st == j
        means[j] = float(np.mean(g[m])) if m.sum() >= MIN_OPP else float("nan")
    for j in (0, 1, 2):
        if np.isfinite(means[j]) and means[j] < GRF_STANCE_MIN:
            raise ValueError("GRF anchor rejects the phase index map: index %d is assumed to "
                             "be %s (load-bearing) but its mean normalised vertical GRF is "
                             "%.3f" % (j, STATE_NAMES[j], means[j]))
    for j in (3, 4):
        if np.isfinite(means[j]) and means[j] > GRF_FLIGHT_MAX:
            raise ValueError("GRF anchor rejects the phase index map: index %d is assumed to "
                             "be %s (flight) but its mean normalised vertical GRF is %.3f"
                             % (j, STATE_NAMES[j], means[j]))
    return means


def _state_channel(col, side):
    pat = re.compile(r"^leg\d+_%s\.state$" % side[-1])
    c = [k for k in col if pat.match(k)]
    if len(c) != 1:
        raise ValueError("expected exactly one leg*_%s.state channel, found %s" % (side[-1], c))
    return c[0]


def _reverify_enum(col, refl):
    """Independent re-verification of the index->phase map from the run OWN base reflexes.

    Any non-injected MuscleReflex declared over a PROPER SUBSET of the phases must have a
    contribution channel whose support is contained in that subset indices. If any such
    reflex contradicts STATE_NAMES the map is wrong for this build and we must not proceed."""
    wit = []
    for r in refl:
        P = r["props"]
        if r["kind"] != "MuscleReflex" or "C0" in P:
            continue
        try:
            S = state_set(r.get("states"))
        except ValueError:
            continue
        if len(S) == 5:
            continue
        # A declaration that pins the side with an explicit _l/_r suffix but sits inside a
        # symmetric controller with no `legs` is instantiated ONCE PER LEG and both instances
        # write the SAME channel. Its support is then the union of the two legs' gating, which
        # says nothing about the enum order. Such a declaration cannot serve as a witness.
        if dg.sided(P["target"]) and r.get("legs") is None and r.get("symmetric") in (None, 1):
            continue
        for m in dg.concrete_targets(r):
            src = P.get("source", P["target"])
            sm = src if dg.sided(src) else dg.base_name(src) + m[-2:]
            for term in dg.SUPPORTED_GAINS:
                if term not in P:
                    continue
                ch = dg.chan(m, sm, term)
                if ch not in col:
                    continue
                try:
                    stc = col[_state_channel(col, m[-2:])]
                except ValueError:
                    continue
                nz = np.abs(col[ch]) > 0.0
                obs = set(int(v) for v in np.unique(stc[nz]))
                wit.append((ch, S, obs))
                if not obs <= S:
                    raise ValueError(
                        "gait-state index map contradicted by this run own base controller: "
                        "%s is declared over indices %s but is non-zero in state index/es %s -- "
                        "the enum order assumed by this module does not hold for this SCONE "
                        "build" % (ch, sorted(S), sorted(obs - S)))
    return wit


def wilson(k, n, alpha=None):
    """Two-sided Wilson score interval for a binomial proportion k/n.

    Chosen over the normal approximation because every case that matters here is small-n and
    near a boundary, which is exactly where the normal interval misbehaves (it can extend past
    0 or 1, and it collapses to zero width at k = 0 or k = n -- the `soleus_l` EarlyStance cell
    was 21/22). Wilson stays inside [0, 1] and keeps finite width at the extremes, so a phase
    observed as 22/22 is still reported with the uncertainty its sample size actually carries.
    """
    if n <= 0:
        return float("nan"), float("nan")
    from math import sqrt
    a = CI_ALPHA if alpha is None else alpha
    # two-sided normal quantile; 1.959964 at alpha = 0.05, avoids a scipy dependency
    z = 1.959963984540054 if abs(a - 0.05) < 1e-12 else _z_two_sided(a)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - h) / d), min(1.0, (c + h) / d)


def _z_two_sided(alpha):
    """Inverse standard-normal CDF at 1 - alpha/2 (Acklam's rational approximation)."""
    from math import sqrt, log
    p = 1.0 - alpha / 2.0
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = sqrt(-2 * log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - pl:
        q = sqrt(-2 * log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def check(result_dir, sto_path=None, require_full_cycle=True):
    """require_full_cycle: the spasticity protocol intends the injected reflex to be active
    over the WHOLE gait cycle. Two independent things can break that, and both are checked:

      (a) CONSISTENCY -- the phases in which the contribution channel is actually non-zero
          must equal the phases the config declares. This is the SCONE-side failure: a
          declaration that does not take effect the way it reads.
      (b) COMPLETENESS -- the declared phase list must be all five. This is the human-side
          failure the task names: a phase omitted or renamed in the config text. SCONE itself
          rejects a MISTYPED phase name (verified: `states = "... Liftof ..."` aborts with
          'Error creating GaitStateController: Invalid string: Liftof'), so only a
          well-spelled OMISSION can reach an archived .sto silently -- and (b) catches it.

    Set require_full_cycle=False to check (a) alone, e.g. on a deliberately phase-restricted
    control condition."""
    rep = {"dir": result_dir, "verdict": None, "reasons": [], "muscles": [], "notes": []}
    try:
        cfg = os.path.join(result_dir, "config.scone")
        if not os.path.isfile(cfg):
            raise ValueError("no config.scone in " + result_dir)
        if sto_path is None:
            c = sorted(f for f in os.listdir(result_dir) if f.endswith(".sto"))
            if len(c) != 1:
                raise ValueError("expected exactly one .sto beside config.scone, found %d" % len(c))
            sto_path = os.path.join(result_dir, c[0])
        cols, d = dg.load_sto(sto_path)
        t = d[:, 0]
        dt = float(np.median(np.diff(t)))
        col = {c: d[:, i] for i, c in enumerate(cols)}

        refl = walk_states(dg.parse_config(cfg))
        inj = [r for r in refl if r["kind"] == "MuscleReflex"
               and (r.get("cname") or "").upper().startswith(dg.INJ_MARKER)]
        base = [r for r in refl if r not in inj]
        if not inj:
            raise ValueError("no reflex under a controller named %s* -- nothing to gate-check"
                             % dg.INJ_MARKER)
        rep["enum_witnesses"] = [(c, sorted(S), sorted(o)) for c, S, o in
                                 _reverify_enum(col, base)]
        if not rep["enum_witnesses"]:
            rep["notes"].append("no partially-gated base reflex in this config, so the "
                                "index->phase map could not be re-verified from this run alone")

        bad = []
        for r in inj:
            S = state_set(r.get("states"))
            if require_full_cycle and S != set(range(5)):
                bad.append("%s: injected block declares states=%r, i.e. %s -- the injection is "
                           "gated OFF during %s. A whole-gait-cycle injection must declare all "
                           "five phases."
                           % (r["props"].get("target"), r.get("states"),
                              [STATE_NAMES[j] for j in sorted(S)],
                              [STATE_NAMES[j] for j in sorted(set(range(5)) - S)]))
            P = r["props"]
            delay = float(P.get("delay", 0.0))
            k = int(round(delay / dt))
            terms = [g for g in dg.SUPPORTED_GAINS if g in P]
            if len(terms) != 1:
                raise ValueError("%s: gate check supports exactly one gain term, found %s"
                                 % (P.get("target"), terms))
            term = terms[0]
            if dg.is_free(P[term]):
                raise ValueError("%s: %s is a free parameter" % (P.get("target"), term))
            K = float(P[term]); X0 = float(P.get(dg.TERM_OFF[term], 0.0))
            an = int(float(P.get(dg.TERM_NEG[term], 1)))
            for m in dg.concrete_targets(r):
                src = P.get("source", P["target"])
                sm = src if dg.sided(src) else dg.base_name(src) + m[-2:]
                ch = dg.chan(m, sm, term)
                if ch not in col:
                    raise ValueError("%s: contribution channel %s absent from the .sto" % (m, ch))
                sch = "%s.%s" % (sm, dg.TERM_SEN[term])
                if sch not in col:
                    raise ValueError("%s: plant channel %s absent" % (m, sch))
                st = col[_state_channel(col, m[-2:])]
                if set(np.unique(st).astype(int).tolist()) - set(range(5)):
                    raise ValueError("leg state channel carries indices outside 0..4")
                gm = _grf_anchor(col, m[-2:], t)
                rep.setdefault("grf_by_state", {})[m[-2:]] = gm

                pred = dg.design_col(col[sch], X0, an, K)
                pd = np.concatenate([np.zeros(k), pred[:len(pred) - k]]) if k else pred.copy()
                c = col[ch]
                eps_p = EPS_P_REL * float(np.max(np.abs(pd)))
                eps_c = EPS_C_REL * max(float(np.max(np.abs(c))), 1e-12)
                opp_raw = np.abs(pd) > eps_p
                act = np.abs(c) > eps_c
                # ERODE the opportunity mask by ERODE samples on each side. The declared delay
                # is applied by SCONE to the integrator's own irregular sub-steps and then
                # resampled onto the .sto grid, so within one .sto sample of a rectifier
                # zero-crossing the reconstructed predictor and the stored contribution
                # legitimately disagree about whether the term is on. Measured on the correctly
                # gated T1LEGS: without erosion 6/43 EarlyStance opportunity samples read
                # "silent"; every one of them is adjacent to a sign change of
                # fiber_velocity_norm. Erosion removes all of them and does not remove any
                # sample of a genuinely closed gate, because a closed gate is silent for a whole
                # phase, not for one sample.
                opp = opp_raw.copy()
                for s in range(1, ERODE + 1):
                    opp[:-s] &= opp_raw[s:]
                    opp[s:] &= opp_raw[:-s]
                trans = np.zeros(len(t), bool)
                for i in np.nonzero(np.diff(st) != 0)[0]:
                    trans[max(0, i - 1):min(len(t), i + 2)] = True

                e = {"muscle": m, "channel": ch, "declared": sorted(S), "delay": delay,
                     "duty": {}, "opp": {}, "ci": {}, "inferred": set(), "closed": set(),
                     "undecided": set(), "margin_open": 1.0, "margin_closed": 0.0}
                for j in range(5):
                    sel = (st == j) & opp & (~trans)
                    n = int(sel.sum())
                    e["opp"][j] = n
                    e["duty"][j] = float(act[sel].mean()) if n else float("nan")
                    lo, hi = wilson(int(act[sel].sum()), n)
                    e["ci"][j] = (lo, hi)
                    # DECISION BY INTERVAL, NOT BY POINT ESTIMATE (round-33 repair of #119/#111/#126).
                    # The old rule was `n < MIN_OPP -> undecided` else compare the POINT estimate to
                    # OPEN_MIN/CLOSED_MAX. That reported a verdict its sample size could not support:
                    # `soleus_l` EarlyStance read duty 0.95 from n = 22 -- 21 of 22, a ONE-FRAME
                    # difference from 1.00 -- and was printed as though decided. A fixed sample floor
                    # cannot fix this, because the floor needed depends on how far the observed duty
                    # sits from the decision boundary: 8 samples can settle duty = 0.0 but cannot
                    # settle duty = 0.95 against a 0.90 threshold. So the phase is called OPEN only
                    # if the whole Wilson interval clears OPEN_MIN, CLOSED only if the whole interval
                    # is under CLOSED_MAX, and UNDECIDED otherwise. Small n now yields a wide
                    # interval and lands in UNDECIDED on its own -- the resolution becomes visible
                    # per cell instead of being stipulated by a constant.
                    if not n:
                        e["undecided"].add(j)
                    elif lo >= OPEN_MIN:
                        e["inferred"].add(j)
                        e["margin_open"] = min(e["margin_open"], lo)
                    elif hi <= CLOSED_MAX:
                        e["closed"].add(j)
                        e["margin_closed"] = max(e["margin_closed"], hi)
                    else:
                        e["undecided"].add(j)
                        bad.append("%s: %s is active in %.0f%% of the %d opportunity samples of "
                                   "%s (Wilson %.0f%% CI %.2f-%.2f) -- the interval does not clear "
                                   "open (>=%.0f%%) nor fall under closed (<=%.0f%%); the gate "
                                   "state in that phase cannot be decided at this sample size"
                                   % (m, ch, 100 * e["duty"][j], e["opp"][j], STATE_NAMES[j],
                                      100 * (1 - CI_ALPHA), lo, hi,
                                      100 * OPEN_MIN, 100 * CLOSED_MAX))
                for j in sorted(e["inferred"] - S):
                    bad.append("%s: %s is ACTIVE in %s (index %d) in %d of %d opportunity "
                               "samples, but %s is NOT in the declared state list %s"
                               % (m, ch, STATE_NAMES[j], j,
                                  int(round(e["duty"][j] * e["opp"][j])), e["opp"][j],
                                  STATE_NAMES[j], [STATE_NAMES[x] for x in sorted(S)]))
                for j in sorted(e["closed"] & S):
                    bad.append("%s: %s is SILENT in all %d opportunity samples of %s (index %d) "
                               "although %s IS declared -- the block is not active over the "
                               "phase it claims"
                               % (m, ch, e["opp"][j], STATE_NAMES[j], j, STATE_NAMES[j]))
                if S - (e["inferred"] | e["closed"]):
                    rep["notes"].append(
                        "%s: %s declared but UNTESTABLE -- fewer than %d samples in which the "
                        "declared predictor is non-zero, so whether the gate is open there "
                        "cannot be decided from this .sto"
                        % (m, [STATE_NAMES[j] for j in
                               sorted(S - (e["inferred"] | e["closed"]))], MIN_OPP))
                tot = float(np.trapezoid(np.abs(pd), t))
                inS = float(np.trapezoid(np.abs(pd) * np.isin(st, list(S)), t))
                e["mass_declared_frac"] = inS / tot if tot > 0 else float("nan")
                e["mass_delivered_frac"] = (float(np.trapezoid(np.abs(c), t)) / tot
                                            if tot > 0 else float("nan"))
                rep["muscles"].append(e)
        rep["verdict"] = "PASS" if not bad else "FAIL"
        rep["reasons"] += bad
    except Exception as ex:
        rep["verdict"] = "ABSTAIN"
        rep["reasons"].append("%s: %s" % (type(ex).__name__, ex))
    return rep


def fmt(rep):
    L = ["%-44s %s" % (os.path.basename(rep["dir"].rstrip("\\/"))[:44], rep["verdict"])]
    for e in rep.get("muscles", []):
        L.append("   %-10s decl=%-14s infer=%-14s duty=%s opp=%s massdecl=%.3f massdlv=%.3f"
                 % (e["muscle"],
                    ",".join(STATE_NAMES[j][:2] for j in e["declared"]),
                    ",".join(STATE_NAMES[j][:2] for j in sorted(e["inferred"])) or "-",
                    # Print a duty ONLY for a testable phase. The test was `if e["opp"][j]`,
                    # i.e. truthiness -- so a phase with ONE opportunity sample printed "1.00",
                    # visually identical to a phase verified over 250 samples, sitting in a row
                    # of genuine 1.00s. `gastroc_l` EarlyStance is exactly that case (opp = 1).
                    # Liftoff (opp = 0) printed "--" and was noticed; EarlyStance was not.
                    # The annotation listed both as untestable, but the TABLE is what gets read.
                    "[" + ",".join("%.2f" % e["duty"][j] if e["opp"][j] >= MIN_OPP else " -- "
                                   for j in range(5)) + "]",
                    "[" + ",".join("%3d" % e["opp"][j] for j in range(5)) + "]",
                    e["mass_declared_frac"], e["mass_delivered_frac"]))
    for r in rep["notes"]:
        L.append("   ~ " + r)
    for r in rep["reasons"]:
        L.append("   ! " + r)
    return "\n".join(L)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        for d in sorted(glob.glob(a)):
            if os.path.isdir(d):
                print(fmt(check(d)))
