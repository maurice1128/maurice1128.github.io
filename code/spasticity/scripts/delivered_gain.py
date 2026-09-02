"""DELIVERED-AMOUNT oracle for injected SCONE reflex blocks.

Question answered:  "did the injected reflex term arrive at the model in the DECLARED amount?"

Works retrospectively on an archived (config.scone, *.sto) pair. Runs no simulation.

Headline number, per injected (target muscle, gain):

        rho = K_delivered_hat / K_declared

    rho ~ 1.0  delivered as declared
    rho ~ 2.0  delivered at twice the declared gain  (duplicate instantiation)
    rho ~ 0.0  the block never reached the model

K_delivered_hat is obtained from the muscle's TOTAL unexplained excitation, regressed on
PLANT channels (fiber_velocity_norm / fiber_length_norm / mtu_force_norm).  Those channels
carry no controller gain, so rho is a MAGNITUDE, not a structure check: writing the wrong KV
moves rho, writing the right KV twice moves rho, deleting the block moves rho.

Every abnormal, ambiguous or unparseable condition returns FAIL or ABSTAIN, never PASS.
"""
import numpy as np, os, re, sys

# ---- thresholds --------------------------------------------------------------------
INJ_MARKER = "SPASTIC"   # enclosing ReflexController name identifying the injection.
                    # Structural, declared, and consumed by SCONE without warning -- unlike
                    # target-suffix matching, which the correct unilateral form removes.
TOL_COPIES = 1e-3   # THE GATE. |copies-1| must be <= this. `copies` is the structural instance
                    # count: numerator and denominator are the SAME waveform, so shape, delay and
                    # sampling errors cancel. It reads 2.000000 to seven digits on every doubled
                    # run in the archive, from a one-generation staggering gait to a converged one.
TOL_RHO   = 0.15    # |rho-1| must be <= this to PASS.  Set from the measured reproducibility
                    # of the estimator itself: 46 archived runs of known delivery factor 2.0
                    # gave rho in [1.909, 2.178], i.e. +-9% at a 0.010 s .sto sample interval.
TOL_ZERO  = 1e-8    # absolute floor for the closure identities
TOL_REL   = 1e-5    # closure tolerance relative to the muscle's own peak excitation. SCONE
                    # writes .sto values at ~6 significant digits, so summing two contribution
                    # channels of magnitude ~0.25 already carries ~1e-6 of print round-off.
                    # Consequence: an injected drive below 1e-5 x peak input is INVISIBLE.
TOL_IQR   = 0.30    # per-window scatter of rho above this -> shape mismatch, cannot certify
TOL_LAG   = 0.015   # |fitted lag - declared delay| above this -> delay flag (diagnostic)
NWIN      = 10      # windows for the per-window scatter / multi-term solve

TERM_CH  = {"KL": "RL", "KV": "RV", "KF": "RF", "KS": "RS"}
TERM_SEN = {"KL": "fiber_length_norm", "KV": "fiber_velocity_norm", "KF": "mtu_force_norm"}
TERM_OFF = {"KL": "L0", "KV": "V0", "KF": "F0", "KS": "S0"}
TERM_NEG = {"KL": "allow_neg_L", "KV": "allow_neg_V", "KF": "allow_neg_F", "KS": "allow_neg_S"}
SUPPORTED_GAINS = ("KL", "KV", "KF")


# ---- strict .sto reader (own; sto_utils.col() does fuzzy suffix matching and can silently
#      return the wrong column, which is unacceptable in a verification instrument) --------
def load_sto(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    hi = None
    for i, l in enumerate(lines):
        if l.strip().lower() == "endheader":
            hi = i + 1
            break
    if hi is None:
        raise ValueError("no 'endheader' line in %s" % path)
    cols = [c.strip() for c in lines[hi].split("\t")]
    if len(set(cols)) != len(cols):
        raise ValueError("duplicate column names in %s" % path)
    body = [r for r in lines[hi + 1:] if r.strip()]
    if len(body) < 50:
        raise ValueError("only %d data rows in %s" % (len(body), path))
    w = len(cols)
    rows = []
    for r in body:
        p = r.split("\t")
        if len(p) != w:
            raise ValueError("ragged row (%d fields, %d columns) in %s" % (len(p), w, path))
        rows.append([float(x) for x in p])
    d = np.asarray(rows, float)
    if not np.isfinite(d).all():
        raise ValueError("non-finite values in %s" % path)
    return cols, d


# ---- config.scone parser -------------------------------------------------------------
def strip_comments(s):
    """Strip # and // comments, never inside a double-quoted value.
    (SCONE values such as "*_tx*;*_ty*;*_u;*/speed" contain '/' and ';'.)"""
    out = []
    for line in s.splitlines():
        q, cut, i = False, len(line), 0
        while i < len(line):
            c = line[i]
            if c == '"':
                q = not q
            elif not q and (c == "#" or (c == "/" and line[i:i + 2] == "//")):
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return "\n".join(out)


def parse_block(s, i):
    assert s[i] == "{"
    i += 1
    out = []
    while i < len(s):
        while i < len(s) and s[i] in " \t\r\n":
            i += 1
        if i >= len(s):
            raise ValueError("unterminated block")
        if s[i] == "}":
            return out, i + 1
        m = re.match(r'([A-Za-z_][A-Za-z_0-9]*)\s*', s[i:])
        if not m:
            raise ValueError("cannot parse token at %r" % s[i:i + 40])
        key = m.group(1)
        i += m.end()
        if i < len(s) and s[i] == "{":
            sub, i = parse_block(s, i)
            out.append((key, sub))
        elif i < len(s) and s[i] == "=":
            i += 1
            while i < len(s) and s[i] in " \t":
                i += 1
            if i < len(s) and s[i] == '"':
                j = s.index('"', i + 1)
                out.append((key, s[i + 1:j]))
                i = j + 1
            else:
                j = i
                while j < len(s) and s[j] not in " \t\r\n}":
                    j += 1
                out.append((key, s[i:j].strip()))
                i = j
        else:
            raise ValueError("unexpected syntax at %r" % s[i:i + 40])
    raise ValueError("unterminated block")


def parse_config(path):
    s = strip_comments(open(path, encoding="utf-8", errors="ignore").read())
    i = s.index("{")
    body, _ = parse_block(s, i)
    return [(s[:i].strip(), body)]


def walk_reflexes(node, path=(), sym=None, legs=None, cname=None, out=None):
    """Collect reflexes, carrying down `symmetric`, `legs` and the enclosing controller `name`.

    `legs` and `name` were previously not captured at all, which is why this module could not see
    a unilateral injection expressed as `ConditionalController { legs = left ... }` with side-free
    targets -- the form that actually delivers 1.0x.
    """
    if out is None:
        out = []
    for key, val in node:
        if isinstance(val, list):
            mysym, mylegs, myname = sym, legs, cname
            for k2, v2 in val:
                if isinstance(v2, list):
                    continue
                if k2 == "symmetric":
                    mysym = int(float(v2))
                elif k2 == "legs":
                    mylegs = str(v2).strip().strip('"').lower()
                elif k2 == "name":
                    myname = str(v2).strip().strip('"')
            if key.endswith("Reflex"):
                out.append({"kind": key, "path": path + (key,), "symmetric": mysym,
                            "legs": mylegs, "cname": myname,
                            "props": {k: v for k, v in val if not isinstance(v, list)}})
            else:
                walk_reflexes(val, path + (key,), mysym, mylegs, myname, out)
    return out


# `legs` values, verified empirically against SCONE 2.4.4: left/l -> left leg only,
# right/r -> right only, both/absent -> bilateral. `opposite` and `other` are ACCEPTED by the
# enum but select NO leg -- SCONE reports the whole child controller as unused and the block is
# silently dropped. They must therefore map to the empty set and be reported, never treated as
# bilateral.
LEGS_SIDES = {"left": ("_l",), "l": ("_l",), "right": ("_r",), "r": ("_r",),
              "both": ("_l", "_r"), None: ("_l", "_r"),
              "opposite": (), "other": ()}


def sides_for(r):
    """Concrete side suffixes a declaration resolves to. An explicit target suffix wins."""
    tgt = r["props"].get("target", "")
    if sided(tgt):
        return (tgt[-2:],)
    lg = r.get("legs")
    if lg not in LEGS_SIDES:
        raise ValueError("unknown legs=%r; SCONE would reject or silently drop this" % lg)
    return LEGS_SIDES[lg]


def is_free(v):
    return isinstance(v, str) and ("~" in v or "<" in v)


def sided(n):
    return n.endswith("_l") or n.endswith("_r")


def mirror(n):
    return n[:-2] + ("_r" if n.endswith("_l") else "_l")


def base_name(n):
    """Muscle name with any side suffix removed. mirror()/chan() are only meaningful on
    names that carry a side, so every name that reaches them must go through here first."""
    return n[:-2] if sided(n) else n


def concrete_targets(r):
    """The sided muscle names a declaration ACTUALLY lands on.

    THIS IS THE CALL SITE sides_for() WAS MISSING. Without it a side-free `target = soleus`
    under `legs = left` was handed to closure() / chan() / mirror() verbatim, so the tool
    looked up channels named `soleus.input`, `soleus.RV` and `sole_l.input` -- none of which
    any .sto contains. Every consumer of a target name below now goes through this function.

    An explicit `_l`/`_r` suffix on the target still wins over `legs`, because that is what
    SCONE does: GetSidedName() returns an already-sided name unchanged, so a `legs = right`
    controller with `target = soleus_l` still drives the LEFT soleus. That asymmetry is the
    original defect and this function must reproduce it, not correct it.
    """
    return [base_name(r["props"]["target"]) + s for s in sides_for(r)]


def chan(target, source, term):
    t = TERM_CH[term]
    return "%s.%s" % (target, t) if source == target else "%s-%s.%s" % (target, source, t)


# ---- estimator -----------------------------------------------------------------------
def design_col(v, X0, allow_neg, Kdecl):
    c = v - X0
    if not allow_neg:
        s = 1.0 if Kdecl >= 0 else -1.0
        c = s * np.maximum(0.0, s * c)
    return c


def integral_solve(t, D, cols_pred, k, nwin):
    """Delay-aligned windowed integral least squares.

    D(t) is the delivered drive; cols_pred[j](t) are the declared design columns evaluated
    on the UNDELAYED plant signal.  If the reflex is correct then
        D(t) = sum_j K_j * col_j(t - tau),  tau = k*dt
    so integrating D over [t_a+tau, t_b+tau] equals sum_j K_j * integral of col_j over
    [t_a, t_b].  Integration is used rather than pointwise regression because SCONE's delayed
    sensor interpolates on the integrator's own irregular step grid, so D is NOT equal to
    K*col(t-tau) sample by sample -- but its integral is, to O(h^2).

    Returns K_hat over the whole record plus the per-window scatter.
    """
    n = len(t)
    Dw = D[k:]
    tw = t[k:]
    Pw = [c[:n - k] for c in cols_pred]
    tp = t[:n - k]
    A = np.array([[np.trapezoid(c, tp) for c in Pw]])
    b = np.array([np.trapezoid(Dw, tw)])
    K, *_ = np.linalg.lstsq(A, b, rcond=None) if A.shape[1] > 1 else (
        np.array([b[0] / A[0, 0]]) if A[0, 0] != 0 else np.array([np.nan]), None, None, None)
    if A.shape[1] > 1:
        edges = np.linspace(0, n - k, nwin + 1).astype(int)
        Aw = np.array([[np.trapezoid(c[e0:e1], tp[e0:e1]) for c in Pw]
                       for e0, e1 in zip(edges[:-1], edges[1:])])
        bw = np.array([np.trapezoid(Dw[e0:e1], tw[e0:e1])
                       for e0, e1 in zip(edges[:-1], edges[1:])])
        cond = np.linalg.cond(Aw)
        K, *_ = np.linalg.lstsq(Aw, bw, rcond=None)
        return K, cond, None
    # single-term: per-window rho scatter as an empirical error bar
    edges = np.linspace(0, n - k, nwin + 1).astype(int)
    rw = []
    for e0, e1 in zip(edges[:-1], edges[1:]):
        den = np.trapezoid(Pw[0][e0:e1], tp[e0:e1])
        num = np.trapezoid(Dw[e0:e1], tw[e0:e1])
        if abs(den) > 1e-12:
            rw.append(num / den)
    return K, 1.0, np.array(rw)


def fit_lag(t, D, cols_pred, K, declared_delay):
    """Diagnostic only: which delay best explains D pointwise."""
    best = (np.nan, -np.inf)
    ss = float(np.sum(D ** 2))
    if ss <= 0:
        return np.nan, np.nan
    for lag in np.arange(0.0, max(0.08, 4 * declared_delay) + 1e-9, 0.0005):
        pred = sum(K[j] * np.interp(t - lag, t, cols_pred[j]) for j in range(len(K)))
        r2 = 1.0 - float(np.sum((D - pred) ** 2)) / ss
        if r2 > best[1]:
            best = (float(lag), float(r2))
    return best


# ---- main criterion ------------------------------------------------------------------
def verify(result_dir, sto_path=None, allow_external_sto=False):
    rep = {"dir": result_dir, "verdict": None, "reasons": [], "gains": [], "notes": []}
    try:
        cfg = os.path.join(result_dir, "config.scone")
        if not os.path.isfile(cfg):
            raise ValueError("no config.scone in " + result_dir)
        if sto_path is None:
            c = sorted(f for f in os.listdir(result_dir) if f.endswith(".sto"))
            if len(c) != 1:
                raise ValueError("expected exactly one .sto beside config.scone, found %d" % len(c))
            sto_path = os.path.join(result_dir, c[0])
        elif not allow_external_sto and os.path.dirname(os.path.abspath(sto_path)) != \
                os.path.abspath(result_dir):
            raise ValueError("the .sto must be the one SCONE wrote beside this config.scone; "
                             "a .sto from another run cannot be validated against it")
        rep["sto"] = os.path.basename(sto_path)
        cols, d = load_sto(sto_path)
        t = d[:, 0]
        dt = float(np.median(np.diff(t)))
        col = {c: d[:, i] for i, c in enumerate(cols)}
        rep["dt"] = dt

        refl = walk_reflexes(parse_config(cfg))
        allrefl = refl
        # ---- IDENTIFY THE INJECTION BY STRUCTURAL MARKER, NOT BY TARGET SYNTAX ---------------
        # This previously read: "an INJECTED reflex is one whose target names an explicit side".
        # That heuristic is defeated by the very fix that makes delivery correct -- a unilateral
        # block written as `ConditionalController { legs = left ... target = soleus }` has NO side
        # suffix, so it was classified as a BASE reflex, its channels folded into the base set,
        # the closure identity closed, and the module returned
        # NO_INJECTION_DECLARED_AND_NONE_DELIVERED on a verified 0.9975x unilateral delivery.
        # Certification by silence, on exactly the configuration the project was trying to adopt.
        #
        # The marker is the enclosing controller's `name`, which SCONE consumes without warning.
        # Every syntactic heuristic this project built was eventually defeated by a syntax it did
        # not anticipate; a declared marker cannot be, because it is chosen rather than inferred.
        inj = [r for r in refl if r["kind"] == "MuscleReflex"
               and (r.get("cname") or "").upper().startswith(INJ_MARKER)]
        base = [r for r in refl if r not in inj]
        # sides_for() raises on an unrecognised `legs` value and returns () for the values that
        # SCONE's enum accepts but that select no leg. Run it over EVERY declaration, not just the
        # injected ones: a base reflex that silently selects no leg emits no channel, and the
        # closure identity would then charge its absence to the injection as over-delivery.
        for r in allrefl:
            if r["props"].get("target") is None:
                raise ValueError("%s without a target" % r["kind"])
            if not sides_for(r):
                raise ValueError(
                    "%s: legs=%r selects NO leg -- SCONE accepts the enum but drops the whole "
                    "child controller, so this declaration is silently absent from the model."
                    % (r["props"].get("target"), r.get("legs")))

        # base contribution channels, side-expanded; plus the set of muscles whose base
        # contribution CANNOT be fully enumerated from stored channels.
        base_ch, opaque = {}, set()
        for r in base:
            P = r["props"]
            tgt = P["target"]
            tset = concrete_targets(r)
            # `symmetric` only has to disambiguate when the declaration still resolves to BOTH
            # sides. `legs = left` pins the side by itself, so it no longer needs to be waived.
            if len(tset) > 1 and r["symmetric"] not in (None, 1):
                raise ValueError("side-generic target with symmetric=%s: side unresolvable"
                                 % r["symmetric"])
            enumerable = (r["kind"] == "MuscleReflex" and "C0" not in P
                          and not any(g in P for g in TERM_CH if g not in SUPPORTED_GAINS))
            if not enumerable:
                opaque.update(tset)
                continue
            src = P.get("source", tgt)
            for m in tset:
                # SECOND SIDE-FREE-NAME-AS-CHANNEL-NAME BUG, independent of the target one:
                # the old expression appended the side suffix only when the TARGET was side-free,
                # so `target = tib_ant_l, source = soleus` produced the channel `tib_ant_l-soleus.RF`
                # instead of `tib_ant_l-soleus_l.RF`. The source side must follow the side of the
                # concrete target, whatever syntax the target was written in.
                sm = src if sided(src) else src + m[-2:]
                for term in SUPPORTED_GAINS:
                    if term in P:
                        base_ch.setdefault(m, set()).add(chan(m, sm, term))

        def ztol(m):
            """Closure tolerance for muscle m, set by the .sto's own print precision."""
            if m + ".input" not in col:
                return TOL_ZERO
            return max(TOL_ZERO, TOL_REL * float(np.max(np.abs(col[m + ".input"]))))

        def closure(m):
            """input(m) - sum(declared base contribution channels for m).
            Returns (value_array, ok) ; ok is False if the base set is not enumerable."""
            if m + ".input" not in col:
                return None, False
            bch = base_ch.get(m, set())
            # A base reflex declared with a gain that optimised to exactly 0 emits NO channel;
            # SCONE omits identically-zero contribution channels. Treat a missing channel as
            # zero -- the contralateral closure test below is what actually guards this.
            miss = [c for c in bch if c not in col]
            s = sum((col[c] for c in bch if c in col), np.zeros(len(t)))
            # `or True` was here, making the flag unconditionally True while both call sites
            # discarded it -- a dead branch that disabled this module's stated invariant
            # ("never PASS on an ambiguous condition", docstring line 20). A missing declared
            # base channel was silently substituted with zero, which reports a misnamed or
            # absent base channel as OVER-delivery rather than as an unreadable file.
            return col[m + ".input"] - s, miss

        for r in allrefl:
            tg = r["props"]["target"]
            for m in concrete_targets(r):
                if m + ".input" not in col:
                    raise ValueError("config declares a reflex on '%s' but the .sto has no "
                                     "'%s.input' channel -- the declaration cannot have taken "
                                     "effect" % (tg, m))

        # ---------- GLOBAL LEAK SWEEP -------------------------------------------------
        # Every muscle that is NOT a declared injection target and whose base drive is fully
        # enumerable must close to machine zero. This is what catches an injection that landed
        # on the wrong muscle, the wrong side, or on a muscle the config never mentions.
        # CONCRETE, SIDED names. This set was previously built from the raw target strings, so
        # under the side-free form it held {"soleus","gastroc"} and matched no muscle at all --
        # the injected muscles would have been swept as if they were controls.
        inj_tgts = set()
        for r in inj:
            inj_tgts.update(concrete_targets(r))
        leaks = []
        for m in sorted(c[:-len(".input")] for c in cols if c.endswith(".input")):
            if m in inj_tgts or m in opaque:
                continue
            D, miss = closure(m)
            if D is None:
                continue
            if miss:
                # Consume the flag here too. A declared base channel missing from the .sto means
                # this muscle's closure identity cannot be formed, so "carries undeclared drive"
                # is not a statement the data supports. Report it as unreadable, not as a leak.
                leaks.append("%s: declared base channel(s) %s absent from the .sto; its closure "
                             "identity cannot be formed" % (m, sorted(miss)))
                continue
            v = float(np.max(np.abs(D)))
            if v > ztol(m):
                leaks.append("%s carries %.3e of drive that the config does not declare"
                             % (m, v))
        rep["leaks"] = leaks

        if not inj:
            rep["verdict"] = "FAIL" if leaks else "NO_INJECTION_DECLARED_AND_NONE_DELIVERED"
            rep["reasons"] += leaks
            return rep

        # Group by the CONCRETE muscle, so a bilateral `legs = both` block becomes two independent
        # measurements and two declarations that land on the same muscle by different syntaxes
        # (`target = soleus_l` and `legs = left; target = soleus`) are caught as a collision.
        side_conflicts = []
        by_tgt = {}
        for r in inj:
            for m in concrete_targets(r):
                by_tgt.setdefault(m, []).append(r)

        for tgt, rs in sorted(by_tgt.items()):
            if len(rs) != 1:
                raise ValueError("%s: %d injected reflexes share one target; their gains "
                                 "are not separately attributable" % (tgt, len(rs)))
            P = rs[0]["props"]
            # A declaration whose `legs` and whose explicit target suffix disagree is
            # SELF-CONTRADICTORY and delivers to the side the SUFFIX names, not the side the
            # config appears to say. Measured: `legs = right` + `target = soleus_l` produces a
            # .sto bit-identical to `legs = left` + `target = soleus`. The delivered AMOUNT is
            # right and every other test here passes, so without this the tool would bless a
            # block that drives the opposite limb from the one it declares.
            dtgt = P["target"]
            if sided(dtgt):
                implied = set(LEGS_SIDES.get(rs[0].get("legs"), ()))
                if implied != {dtgt[-2:]}:
                    side_conflicts.append(
                        "%s: declaration is self-contradictory -- legs=%r selects %s but the "
                        "explicit target suffix in '%s' pins the side to %s, which is what SCONE "
                        "actually delivers"
                        % (tgt, rs[0].get("legs"), sorted(implied) or "no leg", dtgt, dtgt[-2:]))
            if base_name(P.get("source", P["target"])) != base_name(P["target"]):
                raise ValueError("%s: source != target is not supported by this build" % tgt)
            src = tgt   # concrete and sided; `soleus.fiber_velocity_norm` is not a channel
            delay = float(P.get("delay", 0.0))
            decl = []
            for term in SUPPORTED_GAINS:
                if term in P:
                    if is_free(P[term]):
                        raise ValueError("%s.%s is a free parameter; declared amount unknown"
                                         % (tgt, term))
                    decl.append((term, float(P[term]), float(P.get(TERM_OFF[term], 0.0)),
                                 int(float(P.get(TERM_NEG[term], 1)))))
            for term in P:
                if term in TERM_CH and term not in SUPPORTED_GAINS:
                    raise ValueError("%s: unsupported gain %s" % (tgt, term))
            if "C0" in P:
                raise ValueError("%s: C0 is not stored as a channel; delivered amount "
                                 "not separable" % tgt)
            if not decl:
                # `continue` here used to drop the muscle silently -- and it had already been
                # removed from the global leak sweep by inj_tgts, so NOTHING checked it and the
                # run could still PASS. An injected block that declares no measurable gain is an
                # unanalysable declaration, not a clean one.
                raise ValueError("%s: injected block declares no supported gain (%s); there is "
                                 "nothing to measure and the muscle is excluded from the leak "
                                 "sweep, so no verdict is possible"
                                 % (tgt, "/".join(SUPPORTED_GAINS)))

            clash = {chan(tgt, src, x[0]) for x in decl} & base_ch.get(tgt, set())
            if clash:
                raise ValueError("%s: injected and base contributions share channel name(s) "
                                 "%s -> not separable" % (tgt, sorted(clash)))

            mate = mirror(tgt)
            for m in (tgt, mate):
                if m in opaque:
                    raise ValueError("%s: base drive to %s includes a reflex whose "
                                     "contribution SCONE does not store (C0 / DofReflex / "
                                     "ConditionalMuscleReflex); the injected amount cannot be "
                                     "isolated" % (tgt, m))
            D, miss = closure(tgt)
            if D is None:
                raise ValueError("%s: no .input channel" % tgt)
            if miss:
                # Consume the flag. A declared base contribution with no stored channel means the
                # closure identity does not close, so the injected amount cannot be isolated and
                # no verdict is possible. ABSTAIN, never PASS -- this is the invariant the
                # `or True` disabled.
                raise ValueError("%s: declared base channel(s) %s absent from .sto; the closure "
                                 "identity cannot be formed, so delivery cannot be measured"
                                 % (tgt, sorted(miss)))
            Dm, miss_m = closure(mate)
            if Dm is not None and miss_m:
                raise ValueError("%s: control muscle %s has declared base channel(s) %s absent "
                                 "from the .sto, so it cannot serve as a zero reference"
                                 % (tgt, mate, sorted(miss_m)))
            ctrl = float(np.max(np.abs(Dm))) if Dm is not None else None
            # For a BILATERAL injection the mirror muscle is itself injected, so it is not a zero
            # control. Its own entry in by_tgt carries the copies/rho gate; do not additionally
            # demand that it be silent, and say so explicitly rather than dropping the check.
            mate_injected = mate in inj_tgts

            sens = {}
            for term, *_ in decl:
                ch = "%s.%s" % (src, TERM_SEN[term])
                if ch not in col:
                    raise ValueError("%s: plant channel %s absent; cannot form the declared "
                                     "predictor" % (tgt, ch))
                sens[term] = col[ch]

            k = int(round(delay / dt))
            if abs(k * dt - delay) > 0.25 * dt:
                rep["notes"].append("%s: declared delay %.4f s is not a multiple of the .sto "
                                    "interval %.4f s; alignment error up to %.1f%%"
                                    % (tgt, delay, dt, 100 * abs(k * dt - delay) / max(delay, dt)))
            e = {"target": tgt, "declared": {x[0]: x[1] for x in decl},
                 "delay": delay, "Dmax": float(np.max(np.abs(D))), "ctrl": ctrl,
                 "ctrl_muscle": mate, "copies": None, "rho": {}, "K_hat": {},
                 "ztol": ztol(tgt), "ctrl_ztol": ztol(mate),
                 "mate_injected": mate_injected, "copies_required": False,
                 "iqr": None, "lag_fit": None, "lag_r2": None}
            if mate_injected:
                rep["notes"].append("%s: mirror muscle %s is itself an injection target "
                                    "(bilateral declaration), so it is NOT used as a zero "
                                    "control; it is verified as its own instance instead"
                                    % (tgt, mate))

            if e["Dmax"] <= ztol(tgt):
                for term, Kd, *_ in decl:
                    e["rho"][term] = 0.0 if Kd != 0 else float("nan")
                    e["K_hat"][term] = 0.0
                e["note"] = "delivered drive is identically zero"
            else:
                cp = [design_col(sens[x[0]], x[2], x[3], x[1]) for x in decl]
                K, cond, rw = integral_solve(t, D, cp, k, NWIN)
                if cond > 100:
                    raise ValueError("%s: design matrix condition %.1f -- declared terms are "
                                     "collinear, gains not separable" % (tgt, cond))
                for (term, Kd, *_), Kh in zip(decl, K):
                    e["K_hat"][term] = float(Kh)
                    e["rho"][term] = float(Kh / Kd) if Kd != 0 else float("nan")
                if rw is not None and len(rw) >= 4:
                    med = float(np.median(rw))
                    e["iqr"] = float(np.subtract(*np.percentile(rw, [75, 25])) / abs(med)) \
                        if med != 0 else float("inf")
                lag, r2 = fit_lag(t, D, cp, K, delay)
                e["lag_fit"], e["lag_r2"] = lag, r2
                # exact structural copy count: the single stored instance vs the total delivered
                # DEFECT #100, THIRD FORM. This read `(len(decl) == 1)`, so for a MULTI-TERM
                # injected reflex `copies` was never computed AND `copies_required` was False --
                # the missing-copies complaint could not fire, and PASS rested entirely on `rho`
                # (measured +-5-9% error against TOL_RHO = 0.15). A gate whose failure mode is to
                # not execute emits the same PASS as a gate that ran and passed. The first form
                # was the `or True` dead branch; the second was the KV = 0 control; this is the
                # third, and all three lived inside the instrument built to prevent exactly this.
                # A multi-term injection is now REQUIRED to produce a copy count, and abstains if
                # it cannot -- it is never silently exempted.
                e["copies_required"] = True
                for term, *_ in decl:
                    cn = chan(tgt, src, term)
                    if cn in col and len(decl) == 1:
                        den = np.trapezoid(col[cn], t)
                        if abs(den) > 1e-12:
                            e["copies"] = float(np.trapezoid(D, t) / den)
                        break
            rep["gains"].append(e)

        bad = list(leaks) + side_conflicts
        for e in rep["gains"]:
            # ---- COPIES IS THE GATE, rho is the cross-check ------------------------------------
            # `copies` = integral(delivered) / integral(one stored instance). Numerator and
            # denominator are the SAME waveform, so shape, delay and sampling errors cancel: it
            # reads 2.000000 to seven digits across every doubled run in the archive, from a
            # one-generation staggering gait to a converged one. `rho` regresses against a
            # 10 ms-subsampled rectified plant signal and carries a measured +-5-9% bias -- the
            # single stored instance alone scores rho 1.045-1.092. Gating a structural question on
            # the biased estimator while computing the unbiased one and discarding it was
            # backwards. copies now decides; rho remains as a magnitude cross-check.
            if e.get("copies") is None and e.get("copies_required"):
                # The gate must not be able to skip itself. A single-term injection that
                # delivered a non-zero drive but whose stored contribution channel is missing or
                # integrates to zero leaves ONLY the +-9%-biased rho behind, and TOL_RHO = 0.15
                # would let a 1.14x delivery through unchallenged.
                bad.append("%s: structural copy count unavailable (contribution channel %s "
                           "missing or integrating to zero) -- the gate cannot run"
                           % (e["target"], chan(e["target"], e["target"],
                                                list(e["declared"])[0])))
            # CALIBRATED AT {0, 1, 2} ONLY. A widening to {0,1,2,3,4} was applied and then
            # REVERTED: the N=3 / N=4 figures (2.999999 / 3.999997) came from probes
            # `P3_TRIPLE`, `P4_QUAD` and `PDUP`, and running THIS tool on those probes returns
            # ABSTAIN -- "N injected reflexes share one target" -- so the numbers are not
            # reproducible from the preserved artifacts. The abstention is correct fail-closed
            # behaviour; the probe design trips a legitimate guard. But it means the instrument
            # abstains on the very probes built to calibrate it, and a calibration point you
            # cannot re-measure is not a calibration point.
            #
            # To widen legitimately: either rebuild the probes so no two injected reflexes share
            # a target, or emit PER-MUSCLE copies on partial abstention (soleus_l may read 3.0
            # while gastroc_l is ambiguous; a run-level ABSTAIN currently discards a valid
            # reading). Produce the evidence -- do not lower the bar.
            #
            # WHY IT WORKS -- the premise this project assumed was FALSE, and its falseness is the
            # mechanism. SCONE does NOT sum N instances into one channel. Each instance writes its
            # own contribution under its (target, source, term) label; identical labels COLLIDE and
            # the last write wins. So the .sto stores exactly ONE instance regardless of N while
            # `muscle.input` carries all N -- which is precisely why the ratio reads N. (Verified:
            # no .sto ever contained a duplicate column name, the alternative failure mode.)
            #
            # Extrapolation beyond the calibrated integers is still refused: a non-integer means
            # the same-label instances differ in gain or delay, in which case one of them has been
            # silently erased from the .sto and the record is not faithful to the controller.
            _c = e.get("copies")
            if _c is not None and min(abs(_c - k) for k in (0.0, 1.0, 2.0)) > 0.15:
                raise ValueError(
                    "%s: copies = %.6f lies outside the calibrated set {0, 1, 2}. Values at 3 or "
                    "4 are NOT currently certifiable -- the probes built to calibrate them are "
                    "themselves ABSTAINed by this tool. A non-integer additionally means "
                    "same-label instances differ in gain or delay, so one was erased from the "
                    ".sto and it no longer records the controller. No verdict."
                    % (e["target"], _c))
            if e.get("copies") is not None and abs(e["copies"] - 1.0) > TOL_COPIES:
                bad.append("%s: STRUCTURAL COPY COUNT %.6f (expected 1.000000) -- the block is "
                           "instantiated %s, independent of any gain estimate"
                           % (e["target"], e["copies"],
                              "%.0f times" % round(e["copies"]) if
                              abs(e["copies"] - round(e["copies"])) < 1e-3 else "a non-integer "
                              "number of times, which no mirroring account explains"))
            for term, rho in e["rho"].items():
                Kd = e["declared"][term]
                if Kd == 0:
                    if e["Dmax"] > e["ztol"]:
                        bad.append("%s.%s declared 0 but %.3e delivered"
                                   % (e["target"], term, e["Dmax"]))
                elif not np.isfinite(rho):
                    bad.append("%s.%s delivery ratio not computable" % (e["target"], term))
                elif abs(rho - 1.0) > TOL_RHO:
                    bad.append("%s.%s DELIVERY RATIO %.4f (declared %g, delivered %.5g)"
                               % (e["target"], term, rho, Kd, e["K_hat"][term]))
            if e["ctrl"] is None:
                bad.append("%s: control muscle %s not checkable" % (e["target"], e["ctrl_muscle"]))
            elif e["mate_injected"]:
                pass   # declared bilateral; the mirror muscle is verified as its own instance
            elif e["ctrl"] > e["ctrl_ztol"]:
                bad.append("%s: control muscle %s carries %.3e of undeclared drive"
                           % (e["target"], e["ctrl_muscle"], e["ctrl"]))
            if e["iqr"] is not None and e["iqr"] > TOL_IQR:
                bad.append("%s: per-window delivery ratio scatter IQR/median = %.2f -- the "
                           "delivered signal does not have the declared shape"
                           % (e["target"], e["iqr"]))
            if e["lag_fit"] is not None and np.isfinite(e["lag_fit"]) \
                    and abs(e["lag_fit"] - e["delay"]) > TOL_LAG:
                bad.append("%s: best-fit delay %.4f s vs declared %.4f s"
                           % (e["target"], e["lag_fit"], e["delay"]))
        rep["verdict"] = "PASS" if not bad else "FAIL"
        rep["reasons"] += bad
    except Exception as ex:
        rep["verdict"] = "ABSTAIN"
        rep["reasons"].append("%s: %s" % (type(ex).__name__, ex))
    return rep


def fmt(rep):
    L = ["%-46s %s" % (os.path.basename(rep["dir"].rstrip("\\/"))[:46], rep["verdict"])]
    for e in rep.get("gains", []):
        L.append("   %-10s declared %-18s %s | copies=%s IQR=%s lag=%s(R2=%s) |D|max=%.3e ctrl(%s)=%.1e"
                 % (e["target"],
                    ",".join("%s=%g" % kv for kv in e["declared"].items()),
                    "  ".join("rho[%s]=%s" % (k, "%.4f" % v if np.isfinite(v) else "n/a")
                              for k, v in e["rho"].items()),
                    "%.6f" % e["copies"] if e["copies"] is not None else "-",
                    "%.2f" % e["iqr"] if e["iqr"] is not None else "-",
                    "%.4f" % e["lag_fit"] if e["lag_fit"] is not None else "-",
                    "%.2f" % e["lag_r2"] if e["lag_r2"] is not None else "-",
                    e["Dmax"], e["ctrl_muscle"] + ("[also injected]" if e.get("mate_injected")
                                                   else ""),
                    e["ctrl"] if e["ctrl"] is not None else float("nan")))
    for r in rep["notes"]:
        L.append("   ~ " + r)
    for r in rep["reasons"]:
        L.append("   ! " + r)
    return "\n".join(L)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(fmt(verify(a)))
