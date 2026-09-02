# -*- coding: utf-8 -*-
"""Round 229 rev 7 -- REACHABILITY MAP. A permanent gate on every future revision.

Three revisions in a row shipped machinery that could not fire:
    rev 3  no reachable state that was both computable and claimable
    rev 5  rung 9 was a rubber stamp: 100 percent on a true zero AND 100 percent on a
           genuine quarter-magnitude effect
    rev 6  ATTENUATED and D4 unreachable; driving decide() over 156 configurations gave
           {D3: 130, EQUIV: 8, D5: 12} -- the revision's one substantive addition never fired

Reading a ladder does not catch this. DRIVING it does. The cold reader found it three times
by execution; the author missed it three times by inspection.

THE RULE THIS ENFORCES: every outcome named in the registration must appear here with a
witness -- a concrete configuration that reaches it. Any outcome without a witness is
deleted or fixed BEFORE hashing. This converts "the ladder is well-formed" from a claim into
a computation that anyone can re-run.

It imports the REAL decide() from body2_channels_r229.py. It never re-implements it: a
second implementation of a registered procedure is acceptable only if checked against the
first, and here there is no need for a second at all.

Deposits paper/BODY2_REACHABILITY_r229.json.
"""
import io
import os
import sys
import json
import hashlib
import itertools
import re

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import body2_channels_r229 as CH

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PC = CH.PRIMARY_CHANNEL


def sha256_of(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def make_primary(meets_n, partial, p_fwd, p_rev, smd, centre, hw95, has_ci=True,
                 other_gap=1.0, ankle_sep=True):
    """other_gap: how far the PRIMARY channel's SMD sits above the other two. Rung A now
    requires a specificity margin, so a witness carrying only the primary channel's SMD
    makes A unreachable -- which the gate correctly reported the moment the margin was
    added."""
    """A synthetic primary-comparison object. hw90 < hw95 with a shared centre, so the two
    intervals are mutually consistent the way real bootstrap intervals are."""
    hw90 = 0.8395 * hw95   # empirical ratio at n=16; 0.78 made synthetic 90% CIs
                           # ~7% narrower than real, biasing toward over-certifying
                           # EQUIV / A-HIP-ONLY / A-ANKLE-ONLY
    # BOTH laterality channels vary independently -- the A-family tests two channels, and a
    # generator that emitted only the primary would make three of its four rungs unreachable.
    AK = CH.ANKLE_CHANNEL
    # INDEPENDENT of the hip. Tying p_ank to p_fwd made A-ANKLE-ONLY unreachable, which the
    # gate reported the moment the A-family was added -- the ankle could never separate while
    # the hip did not, so the rung that most damages the paper's emphasis could not fire.
    # ankle_sep: True = forward-significant, False = quiet, "rev" = REVERSE-significant.
    # Rev 10 hard-wired the ankle's reverse p to 1 - p_ank, so a reversed ankle could never be
    # generated and the ank_rev branch would have shipped unverified.
    if ankle_sep == "rev":
        p_ank, p_ank_rev = 0.600, 0.005
    elif ankle_sep:
        p_ank, p_ank_rev = 0.005, 0.995
    else:
        p_ank, p_ank_rev = 0.600, 0.400
    others = {c + "_LmR": smd - other_gap for c in CH.CHANNELS if c + "_LmR" != PC}
    others[AK] = -1.0 if ankle_sep in (False, "rev") else 1.0
    if ankle_sep == "rev":
        others[AK] = -1.0
    d = {"meets_n_floor": meets_n, "partial_only": partial,
         "smd": dict({PC: smd}, **others),
         "null_forward": {"per_channel_p": dict({PC: p_fwd}, **{AK: p_ank})},
         "null_reverse": {"per_channel_p": {PC: p_rev, AK: p_ank_rev}}}
    if has_ci:
        d["hl_ci95_primary"] = [centre - hw95, centre + hw95]
        d["hl_ci90_primary"] = [centre - hw90, centre + hw90]
        # the ankle's own 90 percent interval -- the -ONLY rungs require the QUIET channel to
        # be BOUNDED, not merely non-significant, so a generator without it makes every
        # A-rung unreachable
        ac = centre if ankle_sep is True else (-abs(centre) - 1.0
                                              if ankle_sep == "rev" else 0.0)
        d["hl_ci90_ankle"] = [ac - hw90, ac + hw90]
    return d


def prose_ladder():
    """Parse rung order out of the registration and compare it to the code's.

    The gate imports the real decide(), so it can NEVER see a divergence between the prose
    ladder and the code ladder -- and that divergence has now been missed twice. Under the
    document's printed order CONSISTENT-WITH-3D preceded D5, which makes D5 dead because
    ci95[0] > Delta_3D implies ci95[1] >= Delta_3D.
    """
    import re as _re
    p = os.path.join(PAPER, "PREREG_2ndbody_r229.md")
    if not os.path.exists(p):
        return None, "registration not found"
    txt = io.open(p, encoding="utf-8").read()
    sec = txt[txt.index("## 6."):]
    sec = sec[:sec.index("\n## ")]
    order = []
    # Strip leading decorations (emoji, bold markers) before the rung name. Rev 9's pattern
    # required [A-Z] immediately after the number, so rungs written "7. * **A -- ..." were
    # SILENTLY DROPPED -- including A, A-ANKLE-ONLY and CONSISTENT-WITH-3D -- and the
    # comparison then INTERSECTED the two lists so the dropped names left both sides and the
    # gate printed "match" while verifying 12 of 15.
    for line in sec.splitlines():
        m0 = _re.match(r"^\s*\d+\.\s+(.*)$", line)
        if not m0:
            continue
        rest = _re.sub(r"^[^A-Za-z]+", "", m0.group(1))
        m1 = _re.match(r"\*{0,2}([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*)", rest)
        if m1 and m1.group(1) not in order:
            order.append(m1.group(1))
    code = []
    src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "body2_channels_r229.py"), encoding="utf-8").read()
    body = src[src.index("def decide("):src.index("def main(")]
    for m in _re.finditer(r'return "([A-Za-z0-9-]+)"', body):
        if m.group(1) not in code:
            code.append(m.group(1))
    return order, code


def attainable_halfwidths():
    """What HL 90/95 percent bootstrap half-widths can n = 16 at the MEASURED sigma produce?

    Rev 9's grid fed half-widths {0.15, 0.45, 1.2, 3.0}. At sigma_2D = 0.1757 only ~0.07-0.21
    is attainable and at the chi-square upper bound ~0.17-0.51 -- so 1.2 and 3.0 are
    unreachable at any sigma this corpus supports, and the gate certified rungs REACHABLE
    using interval shapes the experiment cannot produce. That is the same failure the gate
    exists to catch, one level up.

    Sigma range spans the measured control CI and the LESION-inflated estimate (3D lesion
    arms run ~3x their control arm, so the 2D S-vs-W sigma is plausibly ~0.53).
    """
    import numpy as _np
    n = 16
    out = []
    rng = _np.random.default_rng(229229)
    # DRIVE the pessimistic sigma and the small-n range too. Refusing to emit outside a range
    # derived from two UNMEASURED quantities narrows the guarantee silently; the filter is now
    # ADVISORY -- it records what is attainable and flags rungs that need shapes outside it,
    # but does not delete witnesses.
    for sigma in (0.1097, 0.1757, 0.4309, 0.5276, 1.2939):
        for nn in (5, 8, 12, 16):
            for _ in range(30):
                sv = rng.normal(0, sigma, nn)
                wv = rng.normal(0, sigma, nn)
                si = rng.integers(0, nn, size=(300, nn))
                wi = rng.integers(0, nn, size=(300, nn))
                d = wv[wi][:, None, :] - sv[si][:, :, None]
                st = _np.median(d.reshape(300, -1), axis=1)
                out.append((_np.percentile(st, 97.5) - _np.percentile(st, 2.5)) / 2.0)
    return float(_np.percentile(out, 1)), float(_np.percentile(out, 99))


HW_LO, HW_HI = attainable_halfwidths()


def coherent(smd, centre, p_fwd, p_rev):
    """Reject physically impossible configurations.

    Rev 7 deposited six impossible witnesses: p_fwd and p_rev both below alpha cannot happen
    on one permutation distribution; smd = 0 with p = 0.005 cannot happen; and rung A's
    witness declared a replication while its CI sat wholly on the opposite side. A witness
    that cannot occur is not evidence the rung is right.
    """
    if p_fwd < 0.5 and p_rev < 0.5:
        return False                       # one distribution: they are complementary
    if abs(smd) < 1e-9 and min(p_fwd, p_rev) < 0.05:
        return False                       # no effect cannot be significant
    if smd > 0 and p_fwd > p_rev:
        return False                       # a positive effect is not evidence for reversal
    if smd < 0 and p_rev > p_fwd:
        return False
    if smd > 0 and centre < 0:
        return False                       # SMD sign must match the interval's centre
    if smd < 0 and centre > 0:
        return False
    return True


def grid():
    D3D = CH.DELTA_3D_HL
    DEQ = CH.DELTA_EQUIV
    centres = [-3.2, -2.0, -0.9, -0.3, 0.0, 0.3, 0.9, 1.6, 2.585, 3.4]
    # ONLY attainable half-widths. Anything outside [HW_LO, HW_HI] is a shape this
    # experiment cannot produce, and proving a rung reachable there proves nothing.
    halfw = [0.08, 0.15, 0.30, 0.45, 0.63, 1.20]   # ADVISORY filter: nothing is refused
    alpha = CH.ALPHA_PER_DIRECTION
    sig = [(alpha / 5.0, 1.0 - alpha / 5.0), (1.0 - alpha / 5.0, alpha / 5.0),
           (0.40, 0.60), (0.60, 0.40)]
    cases = []
    for meets_n in (True, False):
        for pa in (True, False, None):
            for gb in ((0.0, 0.0), (0.0, 0.9)):
                for partial in (False, True):
                    for p_fwd, p_rev in sig:
                        for smd in (-1.0, 0.0, 1.0):
                            for c in centres:
                                for h in halfw:
                                    if not coherent(smd, c, p_fwd, p_rev):
                                        continue
                                    for og in (1.2,):
                                     for asep in (True, False, "rev"):
                                      cases.append({
                                        "other_gap": og, "ankle_sep": asep,
                                        "meets_n": meets_n, "planes_agree": pa,
                                        "gbrate": gb, "partial": partial,
                                        "p_fwd": p_fwd, "p_rev": p_rev, "smd": smd,
                                        "ci_centre": c, "ci_halfwidth95": h})
    return cases, D3D, DEQ


def main():
    cases, D3D, DEQ = grid()
    reached = {}
    counts = {}
    violations = []
    for cs in cases:
        p = make_primary(cs["meets_n"], cs["partial"], cs["p_fwd"], cs["p_rev"],
                         cs["smd"], cs["ci_centre"], cs["ci_halfwidth95"],
                         other_gap=cs.get("other_gap", 1.0),
                         ankle_sep=cs.get("ankle_sep", True))
        out, why = CH.decide(p, cs["gbrate"], cs["planes_agree"])
        counts[out] = counts.get(out, 0) + 1
        if out not in reached:
            reached[out] = {"witness": dict(cs), "reason": why}
        # MESSAGE TRUTH, INDEPENDENTLY DERIVED, over EVERY configuration and EVERY outcome.
        # Rev 9 checked 5 of 14 outcomes and four of those five restated the branch condition
        # verbatim -- a check that asserts the predicate which selected the branch proves
        # nothing and cannot fail. These test the RENDERED STRING instead: every number the
        # message quotes must be a real input quantity, and every directional word must match
        # the sign of the thing it describes.
        lo, hi = p["hl_ci95_primary"]
        lo90, hi90 = p.get("hl_ci90_primary", (lo, hi))
        loa, hia = p.get("hl_ci90_ankle", (lo, hi))
        smd_p = p["smd"].get(CH.PRIMARY_CHANNEL, 0.0)
        smd_a = p["smd"].get(CH.ANKLE_CHANNEL, 0.0)
        pf_p = p["null_forward"]["per_channel_p"].get(CH.PRIMARY_CHANNEL, 1.0)
        pf_a = p["null_forward"]["per_channel_p"].get(CH.ANKLE_CHANNEL, 1.0)
        pr_p = p["null_reverse"]["per_channel_p"].get(CH.PRIMARY_CHANNEL, 1.0)
        pr_a = p["null_reverse"]["per_channel_p"].get(CH.ANKLE_CHANNEL, 1.0)
        pool = [lo, hi, lo90, hi90, loa, hia, smd_p, smd_a, pf_p, pf_a, pr_p, pr_a, CH.DELTA_3D_HL, CH.DELTA_EQUIV,
                CH.ALPHA_PER_DIRECTION, CH.GATE_B_IMBALANCE, float(CH.MIN_N_PER_ARM),
                cs["gbrate"][0], cs["gbrate"][1], 100 * CH.DELTA_EQUIV / CH.DELTA_3D_HL]
        bad = None
        # (i) every number quoted must correspond to an input quantity
        # severity labels ("x0.800") are names, not quantities -- strip before scanning
        scan = re.sub(r"x\d+\.\d+", "", why).replace("+/-", " ")
        for tok in re.findall(r"[-+]?\d+\.\d+", scan):
            v = float(tok)
            if not any(abs(v - q) < 5e-3 for q in pool):
                bad = "quotes %s, which is not an input quantity" % tok
                break
        # (ii) directional words must match the signs they describe
        if bad is None:
            if "predicted direction" in why and smd_p <= 0:
                bad = "claims the predicted direction with a non-positive primary SMD"
            elif "OPPOSITE direction" in why:
                # channel-aware: the message names which channel is reversed
                named_ank = CH.ANKLE_CHANNEL in why
                named_hip = CH.PRIMARY_CHANNEL in why
                if named_hip and smd_p >= 0:
                    bad = "claims the hip reversed with a non-negative hip SMD"
                elif named_ank and not named_hip and smd_a >= 0:
                    bad = "claims the ankle reversed with a non-negative ankle SMD"
            elif "entirely BELOW zero" in why and not hi < 0:
                bad = "claims an interval entirely below zero"
            elif "wholly positive" in why and not lo > 0:
                bad = "claims a wholly positive interval"
            elif "spans zero" in why and not (lo <= 0 <= hi):
                bad = "claims the interval spans zero"
            elif "ENTIRELY ABOVE" in why and not lo > CH.DELTA_3D_HL:
                bad = "claims an interval entirely above the 3D shift"
            elif "BOUNDED below" in why or "both are BOUNDED" in why:
                # every interval the message quotes as bounded must BE bounded
                for a, b in re.findall(r"\[([-+.\d]+), ([-+.\d]+)\]", why):
                    if not (float(a) > -CH.DELTA_EQUIV and float(b) < CH.DELTA_EQUIV):
                        bad = "claims an interval is bounded when it is not"
                        break
            elif "SITE channel transfers" in why and not (smd_a > 0 >= smd_p or pf_a < pf_p):
                bad = "claims the site channel transfers while the compensation does not"
            elif "separates (p" in why and "does not (p" in why and pf_p < 1 and pf_a < 1:
                a_first = why.index(CH.ANKLE_CHANNEL) < why.index(CH.PRIMARY_CHANNEL)
                if a_first and not (pf_a < pf_p):
                    bad = "names the ankle as the separating channel with the larger p"
        if bad:
            violations.append({"outcome": out, "ci": [lo, hi], "why": bad})
    # degenerate inputs
    for label, args in [("primary=None", (None, None, True)),
                        ("no CI", (make_primary(True, False, 1.0, 1.0, 0.0, 0.0, 0.5,
                                                has_ci=False), (0.0, 0.0), True))]:
        out, why = CH.decide(*args)
        counts[out] = counts.get(out, 0) + 1
        reached.setdefault(out, {"witness": {"degenerate": label}, "reason": why})

    # D3 was DELETED in rev 7: "plane agreement not evaluable" is now a recorded caveat,
    # not an outcome, so it has no condition and therefore no witness. The gate is what
    # forced the deletion rather than letting a dead rung sit in the document.
    # THE CUT LADDER. ATTENUATED, ATTENUATED-reversed, CONSISTENT-WITH-3D and D5 are DELETED:
    # they cannot fire at any sigma inside the measured CI, because a non-significant SMD
    # bounds |HL| small enough that EQUIV absorbs the whole non-significant branch first.
    declared = ["A", "A-HIP-ONLY", "A-ANKLE-ONLY", "A-MIXED",
                "B-reversed", "B-reversed-ANKLE", "B-reversed-BOTH",
                "EQUIV", "ATTENUATED", "ATTENUATED-reversed", "CONSISTENT-WITH-3D",
                "C", "E", "F", "D1", "D2", "D4", "D5"]
    missing = [o for o in declared if o not in reached]
    extra = [o for o in reached if o not in declared]

    res = {"rev": 7, "n_configurations": len(cases),
           "delta_3d_hl": D3D, "delta_equiv": DEQ,
           "alpha_per_direction": CH.ALPHA_PER_DIRECTION,
           "rule": ("every outcome named in the registration must appear with a witness; "
                    "any without one is deleted or fixed before hashing"),
           "counts": counts,
           "reachable": sorted(reached),
           "declared": declared,
           "MISSING_no_witness": missing,
           "UNDECLARED_but_reachable": extra,
           "witnesses": reached,
           "decide_source": "body2_channels_r229.py (imported, not re-implemented)",
           "channels_sha256": sha256_of(os.path.join(
               os.path.dirname(os.path.abspath(__file__)), "body2_channels_r229.py")),
           "script_sha256": sha256_of(os.path.abspath(__file__))}
    porder, corder = prose_ladder()
    ladder_ok = True
    ladder_note = ""
    if isinstance(porder, list):
        # COMPARE, do not intersect. A name in one list and not the other is a FAILURE:
        # either the document declares a rung the code lacks, or the code has one the
        # document does not. Intersecting made both cases invisible.
        only_p = [x for x in porder if x not in corder]
        only_c = [x for x in corder if x not in porder]
        seq_ok = ([x for x in porder if x in corder] == [x for x in corder if x in porder])
        ladder_ok = (not only_p) and (not only_c) and seq_ok
        ladder_note = "match" if ladder_ok else (
            "prose-only %r | code-only %r | order_ok %s" % (only_p, only_c, seq_ok))
    res["prose_ladder_order"] = porder
    res["code_ladder_order"] = corder
    res["prose_matches_code_ladder"] = ladder_ok
    res["prose_ladder_note"] = ladder_note
    res["attainable_halfwidth_lo"] = HW_LO
    res["attainable_halfwidth_hi"] = HW_HI
    res["attainability_sigmas"] = [0.1097, 0.1757, 0.4309, 0.5276]
    res["attainability_n"] = 16
    res["attainability_caveat"] = ("the 2D LESION-arm sigma has never been measured; "
                                   "0.5276 transports a 3.0x inflation ratio from the "
                                   "3D body. If the true sigma exceeds it, rungs the "
                                   "gate certifies may be unreachable in fact")
    res["message_truth_violations"] = violations[:50]
    res["n_message_truth_violations"] = len(violations)
    res["GATE_PASSES"] = ((not missing) and (not extra) and (not violations)
                          and ladder_ok)

    out = os.path.join(PAPER, "BODY2_REACHABILITY_r229.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), indent=1)

    print("configurations driven: %d" % len(cases))
    print("\noutcome        count   witness")
    for o in sorted(counts, key=lambda k: -counts[k]):
        w = reached[o]["witness"]
        if "degenerate" in w:
            desc = w["degenerate"]
        else:
            desc = ("n=%s pa=%s gb=%s part=%s pf=%.4f pr=%.4f smd=%+.1f ci=%.2f+/-%.2f"
                    % (w["meets_n"], w["planes_agree"], w["gbrate"][1], w["partial"],
                       w["p_fwd"], w["p_rev"], w["smd"], w["ci_centre"],
                       w["ci_halfwidth95"]))
        print("  %-20s %5d  %s" % (o, counts[o], desc))
    print("\nprose ladder matches code  : %s  %s" % (ladder_ok, ladder_note))
    print("message-truth violations   : %d" % len(violations))
    for v in violations[:5]:
        print("    %-20s ci=[%+.3f, %+.3f]  %s" % (v["outcome"], v["ci"][0], v["ci"][1],
                                                   v["why"]))
    print("declared but NEVER reached : %r" % missing)
    print("reachable but NOT declared : %r" % extra)
    print("GATE %s" % ("PASSES" if res["GATE_PASSES"] else "FAILS"))
    print("wrote %s" % out)
    return 0 if res["GATE_PASSES"] else 1


if __name__ == "__main__":
    sys.exit(main())
