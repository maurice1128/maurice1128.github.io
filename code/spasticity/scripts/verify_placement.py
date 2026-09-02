"""SINGLE ENTRY POINT for STRUCTURAL injection verification. Runs the pre-run structural check
(`check_structure.py`) and the launcher-log unused-property-tree check (`check_unused.py`) and
emits one structured verdict plus a machine-readable list of what it could NOT verify.

    python verify_placement.py <target> [<target> ...] [options]

A <target> is either
    * a `.scone` file            -- the sibling `log_<TAG>.txt` is auto-discovered
    * a SCONE result directory   -- `config.scone` + `optimization.log` are used

Options
    --log PATH            use this launcher log instead of the auto-discovered one
    --name NAME           name of the injected block                  (default SpasticL)
    --expect-reflexes N   assert the injected block holds exactly N reflexes
    --expect-kv X         assert every injected reflex declares KV = X
    --json                emit JSON

NOT TO BE CONFUSED WITH `verify_injection.py`, which is signal-keyed: its three gates read the
`R<n>` results-directory token and `.sto` channel residuals. This one reads the FILE.

VERDICTS -- there are three, and none of them is a bare "PASS":

    ERROR                  the input could not be read or parsed. Fails closed.
    FAIL                   at least one check failed. `failures` says which and why.
    PASS_WITH_UNVERIFIED   every check that RAN passed. `could_not_verify` is never empty:
                           a structural instrument cannot see delivered torque, per-side
                           multiplicity, or run-time behaviour, so those are always listed.

WHY TWO INSTRUMENTS AND NOT ONE.
The log instrument is the simulator's own confession and is therefore the strongest evidence
available -- but it only exists AFTER a run, and a missing/empty/truncated log yields nothing.
The structural instrument runs BEFORE any simulation, needs no log, and answers the question a
signal-keyed verifier provably cannot: a correctly-instantiated KV = 0 control and a silently
discarded block produce bit-identical output, so no amount of `.sto` reading separates them.
Only the parent chain in the file separates them.

LOG ABSENCE IS NOT A COMBINED FAILURE, IT IS AN UNVERIFIED ITEM. When no usable log exists the
placement question has still been answered structurally; what remains unanswered is whether the
SCONE build that actually ran agreed with this parser. That is stated explicitly in
`could_not_verify`, never swallowed. (`check_unused.py` run standalone still treats a missing log
as its own hard failure -- its input is the log.)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_structure                                                    # noqa: E402
from check_unused import parse_unused_tree, check_legs, ACCEPTED_CHAINS   # noqa: E402


def _resolve(target):
    """(scenario_path_or_None, log_path_or_None, tag)."""
    if os.path.isdir(target):
        scen = os.path.join(target, "config.scone")
        log = os.path.join(target, "optimization.log")
        return (scen if os.path.exists(scen) else None,
                log if os.path.exists(log) else None,
                os.path.basename(os.path.normpath(target)))
    tag = os.path.splitext(os.path.basename(target))[0]
    d = os.path.dirname(os.path.abspath(target))
    for cand in (os.path.join(d, "log_%s.txt" % tag), os.path.join(d, "%s.log" % tag)):
        if os.path.exists(cand):
            return target, cand, tag
    return target, None, tag


def verify(target, name="SpasticL", expect_reflexes=None, expect_kv=None, log_override=None):
    scen, log, tag = _resolve(target)
    if log_override:
        log = log_override
    v = {"target": os.path.abspath(target), "tag": tag,
         "scenario": os.path.abspath(scen) if scen else None,
         "log": os.path.abspath(log) if log else None,
         "verdict": "ERROR", "failures": [], "could_not_verify": [],
         "structural": None, "log_check": None}

    def unver(item, why):
        v["could_not_verify"].append({"instrument": "entrypoint", "item": item, "reason": why})

    # ---- (b) PRE-RUN STRUCTURAL CHECK ---------------------------------------------------------
    if scen is None:
        v["failures"].append({"instrument": "structure", "code": "NO_SCENARIO",
                              "detail": "no .scone file found for target %s" % target})
        return v
    s = check_structure.analyze(scen, name=name, expect_reflexes=expect_reflexes,
                                expect_kv=expect_kv)
    v["structural"] = s
    for f in s["failures"]:
        v["failures"].append(dict(f, instrument="structure"))
    v["could_not_verify"].extend(dict(u, instrument="structure") for u in s["could_not_verify"])

    # the legacy regex `legs` screen, kept as an independent second opinion on the same file
    ok_legs, msg_legs = check_legs(scen)
    v["legs_regex_screen"] = {"ok": ok_legs, "detail": msg_legs}
    if not ok_legs and not any(f.get("code") == "LEGS_SELECTS_NOTHING" for f in s["failures"]):
        v["failures"].append({"instrument": "legs_regex", "code": "LEGS_SELECTS_NOTHING",
                              "detail": msg_legs})

    # ---- (a) LOG / UNUSED-PROPERTY-TREE CHECK -------------------------------------------------
    state, nodes, block = parse_unused_tree(log) if log else ("NO_LOG", [], "")
    lc = {"instrument": "check_unused", "state": state,
          "log": os.path.abspath(log) if log else None,
          "log_bytes": os.path.getsize(log) if log and os.path.exists(log) else None,
          "discarded_nodes": ["/".join(n["chain"]) for n in nodes],
          # only the nodes that actually CARRY a discarded property; the ancestors above them are
          # printed by SCONE purely to show the path
          "discarded_leaves": ["%s { %s }" % ("/".join(n["chain"]),
                                              ", ".join("%s = %s" % (k, val)
                                                        for k, val, _ in n["props"]))
                               for n in nodes if n["props"]]}
    v["log_check"] = lc
    if state == "NO_LOG":
        unver("SCONE's own acceptance of this scenario",
              "no launcher log found for %s; the simulator's `Warning, unused properties:` report "
              "could not be read. Placement was decided structurally only." % tag)
    elif state == "LOG_UNUSABLE":
        unver("SCONE's own acceptance of this scenario",
              "log %s is %d bytes and never reached 'Creating folder'/'Starting optimization', "
              "so it stops before the point where the warning would be printed. Absence of a "
              "warning in it is absence of evidence."
              % (os.path.abspath(log), os.path.getsize(log)))
    elif state == "WARNING":
        hits = [n for n in nodes
                if any(k == "name" and val == name for k, val, _ in n["props"])] or \
               [n for n in nodes if n["type"] == name]
        if hits:
            for n in hits:
                chain = "/".join(n["chain"])
                landed = n["chain"][-2] if len(n["chain"]) >= 2 else "<root>"
                v["failures"].append({
                    "instrument": "check_unused", "code": "DISCARDED_BY_SCONE",
                    "detail": "SCONE reported the injected block %r as unused. ACTUAL PARENT "
                              "CHAIN FROM THE LOG: %s ; it LANDED UNDER %s. Accepted: %s"
                              % (name, chain, landed, " | ".join(ACCEPTED_CHAINS)),
                    "actual_chain": chain, "landed_under": landed})
        else:
            v["failures"].append({
                "instrument": "check_unused", "code": "UNUSED_PROPERTIES_ELSEWHERE",
                "detail": "SCONE discarded something that is not %r: %s. The scenario is not "
                          "clean." % (name, "; ".join(lc["discarded_leaves"]) or "<unnamed>")})

    # ---- invariants no structural instrument can establish ------------------------------------
    unver("that this parser and SCONE's parser agree",
          "the accepted parent chains are EMPIRICAL -- derived from observed logs, not from "
          "SCONE source. A chain SCONE accepts that is not in the list is reported as a failure.")
    unver("model / .osim side of the impairment",
          "only the controller tree is parsed; muscle weakening lives in the .osim and is not "
          "checked here")

    if s["status"] == "ERROR":
        v["verdict"] = "ERROR"
    elif v["failures"]:
        v["verdict"] = "FAIL"
    else:
        v["verdict"] = "PASS_WITH_UNVERIFIED"
    return v


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    name, exp_r, exp_kv, as_json, log_ov, targets = "SpasticL", None, None, False, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--name":
            name = argv[i + 1]; i += 2
        elif a == "--expect-reflexes":
            exp_r = int(argv[i + 1]); i += 2
        elif a == "--expect-kv":
            exp_kv = float(argv[i + 1]); i += 2
        elif a == "--log":
            log_ov = argv[i + 1]; i += 2
        elif a == "--json":
            as_json = True; i += 1
        else:
            targets.append(a); i += 1
    if not targets:
        print(__doc__)
        return 2
    out = [verify(t, name, exp_r, exp_kv, log_ov) for t in targets]
    if as_json:
        print(json.dumps(out, indent=2))
        return 1 if any(v["verdict"] != "PASS_WITH_UNVERIFIED" for v in out) else 0
    for v in out:
        print("=" * 100)
        print("%-22s %s" % (v["verdict"], v["tag"]))
        print("  scenario : %s" % v["scenario"])
        print("  log      : %s  [%s]"
              % (v["log"], v["log_check"]["state"] if v["log_check"] else "n/a"))
        if v["structural"]:
            print("  chain    : %s"
                  % v["structural"]["info"].get("actual_chain", "<block not located>"))
        for f in v["failures"]:
            print("  FAIL  <%s> [%s] %s" % (f["instrument"], f["code"], f["detail"]))
        for u in v["could_not_verify"]:
            print("  UNVERIFIED  %s" % u["item"])
            print("              -> %s" % u["reason"])
    n_fail = sum(1 for v in out if v["verdict"] == "FAIL")
    n_err = sum(1 for v in out if v["verdict"] == "ERROR")
    print("=" * 100)
    print("%d target(s): %d FAIL, %d ERROR, %d PASS_WITH_UNVERIFIED"
          % (len(out), n_fail, n_err, len(out) - n_fail - n_err))
    print("PASS_WITH_UNVERIFIED is NOT a clean bill of health. Read could_not_verify.")
    return 1 if any(v["verdict"] != "PASS_WITH_UNVERIFIED" for v in out) else 0


if __name__ == "__main__":
    sys.exit(main())
