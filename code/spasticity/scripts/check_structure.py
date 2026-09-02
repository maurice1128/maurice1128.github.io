"""PRE-RUN STRUCTURAL verification of a SCONE scenario file. Reads STRUCTURE, not SIGNAL.

WHY THIS EXISTS.
A signal-keyed verifier cannot distinguish a correctly-instantiated zero-gain control from a
silently discarded block: both emit identical numbers. `delivered_gain.py` reads `.sto` channels,
`check_unused.py` reads the launcher log -- both are downstream of a run that already happened,
and the first is blind to a KV = 0 control by construction. This module reads the `.scone` FILE,
before any simulation, and answers a different question: **is the block WHERE IT MUST BE?**

WHAT IT ASSERTS
  1. The file parses as a brace-matched tree. No regex. Unbalanced braces, stray `}`, dangling
     identifiers and trailing garbage are ERRORS (this is failure mode 4: the scenarios are
     produced by `rindex`/regex splicing and that surgery has produced malformed nesting before).
  2. No UTF-8 BOM. A BOM makes SCONE reject the whole file with "Invalid label CmaOptimizer";
     one was introduced by an edit on 2026-07-27 and survived until the pipeline gate.
  3. The injected block exists EXACTLY ONCE and its PARENT CHAIN is one of the accepted forms.
     This is failure modes 1 and 2. Both are Warnings in SCONE; the optimization runs to
     completion and produces a normal-looking gait with zero injection.
  4. `SimulationObjective` holds exactly ONE controller child. That is the mechanical cause of
     failure mode 1: it takes one controller, so a bare sibling of `GaitStateController` is
     parsed, warned about, and dropped.
  5. No controller anywhere beneath a Measure. That is failure mode 2 (`ConditionalController`
     spliced under `CompositeMeasure`).
  6. Forbidden / silently-ignored property values (failure mode 3): `legs = opposite` and
     `legs = other` are accepted by `scone::Side` but select NO leg; `legs` on anything other
     than a `ConditionalController` is discarded; an explicit `_l`/`_r` target suffix OVERRIDES
     an enclosing `legs`, so declaring both is a silent contradiction.
  7. The number of injected `MuscleReflex` entries, when the caller states an expectation.

IT FAILS CLOSED. A missing file, a parse error, an unreadable encoding, an unrecognised block
name in the injected block's own parent chain -- all are ERROR, never a pass. Anything it did not
or could not check is returned in a machine-readable `could_not_verify` list, so the caller can
never mistake silence for evidence.

WHAT IT CANNOT DETECT -- read this before trusting a PASS.
  * A MISSPELLED OR UNSUPPORTED PROPERTY NAME. `zzqqbogus = left` on a correctly-placed
    ConditionalController parses fine here and is structurally invisible; only SCONE's log names
    it (see legs_calibration/legstest/log_T2BOGUS.txt). There is no property schema to check
    against -- keywords.txt lists 83 class doc files, not property names or their types.
  * WHETHER SCONE'S PARSER AGREES WITH THIS ONE. `ACCEPTED_CHAINS` is EMPIRICAL: it is the set of
    chains observed to produce no unused-property warning in this project's own logs. A third
    valid chain would be reported as a failure; a chain SCONE quietly drops for a reason not yet
    observed would be reported as a pass.
  * PER-SIDE MULTIPLICITY. A side-unscoped ReflexController is built once per side. Form B
    (CompositeController) passes here and is the empirically-measured 2.0x delivery mode. The
    file cannot show the resulting factor -- only delivered_gain.py can.
  * DELIVERED GAIN. Nothing about torque, activation or fitness is read.
  * THE MODEL SIDE. Muscle weakening lives in the .osim; only the controller tree is parsed.
  * SEMANTIC CORRECTNESS OF `states`, `delay`, `allow_neg_V`, or any other value it is not told
    to expect. It checks placement and a named short list, not intent.
  * ANYTHING BEHIND A `<<` INCLUDE. The include is not followed; its presence is a failure
    rather than a guess.

Usage:
    python check_structure.py SCEN.scone [SCEN2.scone ...] [--name SpasticL]
                              [--expect-reflexes N] [--expect-kv X] [--json]
"""
import json
import os
import sys

# ---------------------------------------------------------------------------------------------
# SCONE class inventory, derived from C:\Program Files\SCONE\resources\help\keywords.txt
# (83 entries, snake_case -> CamelCase). ConditionalController / ConditionalControllers / Reflexes
# are NOT in keywords.txt -- they are documented inside gait_state_controller.txt and
# reflex_controller.txt as sub-objects -- so they are added by hand. The list is therefore NOT
# exhaustive: an unknown block name is reported, not silently accepted.
# ---------------------------------------------------------------------------------------------
CONTROLLER_TYPES = {
    "CompositeController", "ConditionalController", "ExternalController", "FeedForwardController",
    "GaitStateController", "LuaController", "MirrorController", "NeuralController",
    "NoiseController", "PerturbationController", "ReflexController", "ScriptController",
    "SequentialController", "TrackingController", "Controller",
}
MEASURE_TYPES = {
    "BalanceMeasure", "BodyMeasure", "CompositeMeasure", "DofMeasure", "EffortMeasure",
    "GaitCycleMeasure", "GaitMeasure", "HeightMeasure", "JointLoadMeasure", "JumpMeasure",
    "Measure", "MimicMeasure", "MuscleMeasure", "ReactionForceMeasure", "ScriptMeasure",
    "StepMeasure",
}
MODEL_TYPES = {"Model", "ModelHfd", "ModelHyfydy", "ModelOpenSim3", "ModelOpenSim4"}
OBJECTIVE_TYPES = {"ImitationObjective", "ModelObjective", "Objective", "ReplicationObjective",
                   "SimulationObjective", "TestObjective"}
OPTIMIZER_TYPES = {"CmaOptimizer", "CmaPoolOptimizer", "EsOptimizer", "Optimizer"}
REFLEX_TYPES = {"BodyOrientationReflex", "BodyPointReflex", "BodyPostureMuscleReflex",
                "ComPivotReflex", "ConditionalMuscleReflex", "DofReflex", "MuscleReflex",
                "Reflex", "SensorReflex"}
CONTAINER_TYPES = {"ConditionalControllers", "Reflexes"}
KNOWN_TYPES = (CONTROLLER_TYPES | MEASURE_TYPES | MODEL_TYPES | OBJECTIVE_TYPES |
               OPTIMIZER_TYPES | REFLEX_TYPES | CONTAINER_TYPES)

# `legs` is a real typed property in sconelib.dll but is undocumented (no shipped scenario, not in
# keywords.txt). `legs = banana` raises "Could not convert to enum scone::Side"; `legs = opposite`
# and `legs = other` are ACCEPTED and select nothing.
FATAL_LEGS = {"opposite", "other"}
# Values for which there is POSITIVE evidence in this project's own fixtures that the enclosing
# ConditionalController is built for a definite limb. `legs = banana` is a hard SCONE error
# ("Could not convert to enum scone::Side"), and `legs = both` / `0` / `1` / `"left right"` all
# appear in legs_calibration/legstest with no preserved artifact establishing what they select.
# Fail closed: a `legs` value outside this allowlist is a FAILURE, not a pass.
SAFE_LEGS = {"left", "right"}
# `legs` is honoured on ConditionalController. On a bare ReflexController it is silently
# discarded and the reflex is built once per side (the empirically-measured 2.0x bilateral mode).
LEGS_HOST_TYPES = {"ConditionalController"}

# The two parent chains under which an injected block has been OBSERVED to reach the model.
# Role tokens <OPTIMIZER>/<OBJECTIVE> match any member of the corresponding set above.
ACCEPTED_CHAINS = [
    # Form A -- current correct form. GATE2/config.scone and gen_conditions.make_scenario.
    ("<OPTIMIZER>", "<OBJECTIVE>", "GaitStateController", "ConditionalControllers",
     "ConditionalController", "ReflexController"),
    # Form B -- the 2x2x2 grid wrapper=1 cells (G100/G101/G110/G111) and ARMA/ARMB/ARMC.
    # Accepted by SCONE (no unused-property warning) but delivers the reflex once per side.
    ("<OPTIMIZER>", "<OBJECTIVE>", "CompositeController", "ReflexController"),
]


class ParseError(Exception):
    pass


class Node(object):
    __slots__ = ("type", "line", "props", "children", "parent")

    def __init__(self, type_, line, parent):
        self.type = type_
        self.line = line
        self.parent = parent
        self.props = []       # list of (key, value, line)
        self.children = []    # list of Node

    def chain(self):
        out, n = [], self
        while n is not None and n.type != "<file>":
            out.append(n.type)
            n = n.parent
        return tuple(reversed(out))

    def get(self, key):
        for k, v, _ in self.props:
            if k == key:
                return v
        return None

    def walk(self):
        yield self
        for c in self.children:
            for d in c.walk():
                yield d


def tokenize(text):
    toks, i, line, n = [], 0, 1, len(text)
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
            continue
        if c in " \t\r":
            i += 1
            continue
        if c == "#":                       # SCONE zml line comment
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "{":
            toks.append(("LB", "{", line)); i += 1; continue
        if c == "}":
            toks.append(("RB", "}", line)); i += 1; continue
        if c == "=":
            toks.append(("EQ", "=", line)); i += 1; continue
        if c == '"':
            j, buf = i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\n":
                    raise ParseError("line %d: unterminated quoted string" % line)
                buf.append(text[j]); j += 1
            if j >= n:
                raise ParseError("line %d: unterminated quoted string at end of file" % line)
            toks.append(("STR", "".join(buf), line)); i = j + 1; continue
        j = i
        while j < n and text[j] not in ' \t\r\n{}="#':
            j += 1
        if j == i:
            raise ParseError("line %d: unexpected character %r" % (line, c))
        toks.append(("WORD", text[i:j], line)); i = j
    return toks


def parse(text):
    """Brace-matched parse. Raises ParseError on ANY malformation -- this is the bracket-surgery
    detector, and it is the reason the checker does not use a regex."""
    toks = tokenize(text)
    root = Node("<file>", 0, None)
    stack, pos = [root], 0
    while pos < len(toks):
        kind, val, line = toks[pos]
        if kind == "RB":
            if len(stack) == 1:
                raise ParseError("line %d: closing brace '}' with no matching open brace "
                                 "-- bracket-surgery damage" % line)
            stack.pop(); pos += 1; continue
        if kind != "WORD":
            raise ParseError("line %d: expected an identifier, found %r" % (line, val))
        if pos + 1 >= len(toks):
            raise ParseError("line %d: identifier %r at end of file with no '=' or '{'"
                             % (line, val))
        if val == "<<":
            # zml include directive:  << "path/to/other.scone" >>
            # The included tree is NOT read. Anything could be in it, including the injected
            # block or a second controller, so the parent chain of this file alone is not
            # decidable. Recorded as a node so analyze() can FAIL on it rather than guess.
            j = pos + 1
            path_tok = toks[j][1] if j < len(toks) else "?"
            while j < len(toks) and toks[j][1] != ">>":
                j += 1
            nd = Node("<<include>>", line, stack[-1])
            nd.props.append(("path", path_tok, line))
            stack[-1].children.append(nd)
            pos = j + 1
            continue
        nk, nv, _ = toks[pos + 1]
        if nk == "LB":
            nd = Node(val, line, stack[-1])
            stack[-1].children.append(nd)
            stack.append(nd)
            pos += 2
        elif nk == "EQ":
            if pos + 2 >= len(toks):
                raise ParseError("line %d: property %r has no value" % (line, val))
            vk, vv, _ = toks[pos + 2]
            if vk == "LB":                       # `blueprint = { ... }` -- property-as-block
                nd = Node(val, line, stack[-1])
                stack[-1].children.append(nd)
                stack.append(nd)
                pos += 3
                continue
            if vk == "WORD" and vv == "[":       # vector literal: force = [ -100.0 0 0 ]
                j, items = pos + 3, []
                while j < len(toks) and toks[j][1] != "]":
                    items.append(toks[j][1]); j += 1
                if j >= len(toks):
                    raise ParseError("line %d: unterminated '[' in property %r" % (line, val))
                stack[-1].props.append((val, "[%s]" % " ".join(items), line))
                pos = j + 1
                continue
            if vk not in ("WORD", "STR"):
                raise ParseError("line %d: property %r assigned %r" % (line, val, vv))
            stack[-1].props.append((val, vv, line))
            pos += 3
        else:
            raise ParseError("line %d: identifier %r followed by %r; expected '=' or '{'"
                             % (line, val, nv))
    if len(stack) != 1:
        raise ParseError("end of file with %d block(s) still open; innermost is %r opened at "
                         "line %d -- bracket-surgery damage"
                         % (len(stack) - 1, stack[-1].type, stack[-1].line))
    return root


def _fmt(chain):
    return "/".join(chain)


def _chain_matches(actual, pattern):
    if len(actual) != len(pattern):
        return False
    for a, p in zip(actual, pattern):
        if p == "<OPTIMIZER>":
            if a not in OPTIMIZER_TYPES:
                return False
        elif p == "<OBJECTIVE>":
            if a not in OBJECTIVE_TYPES:
                return False
        elif a != p:
            return False
    return True


def analyze(path, name="SpasticL", expect_reflexes=None, expect_kv=None,
            accepted_chains=ACCEPTED_CHAINS):
    """Structural verdict for one .scone file.

    Returns a dict with keys: path, status ('OK'|'FAIL'|'ERROR'), failures[], could_not_verify[],
    info{}. Never returns a bare boolean and never returns OK on unreadable input.
    """
    r = {"path": os.path.abspath(path), "instrument": "check_structure",
         "status": "ERROR", "failures": [], "could_not_verify": [], "info": {}}

    def fail(code, msg):
        r["failures"].append({"code": code, "detail": msg})

    def unver(item, why):
        r["could_not_verify"].append({"item": item, "reason": why})

    if not os.path.exists(path):
        fail("NO_FILE", "scenario file does not exist: %s" % os.path.abspath(path))
        return r
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        fail("BOM", "file begins with a UTF-8 BOM; SCONE rejects the whole scenario with "
                    "'Invalid label CmaOptimizer'")
        return r
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        fail("ENCODING", "not valid UTF-8: %s" % e)
        return r
    if "\ufeff" in text:
        fail("BOM", "U+FEFF appears inside the file at offset %d" % text.index("\ufeff"))
        return r
    r["info"]["bytes"] = len(raw)
    r["info"]["open_braces"] = text.count("{")
    r["info"]["close_braces"] = text.count("}")

    try:
        root = parse(text)
    except ParseError as e:
        fail("PARSE", str(e))
        return r

    if len(root.children) != 1:
        fail("ROOT", "expected exactly 1 top-level block, found %d: %s"
             % (len(root.children), [c.type for c in root.children]))
        return r
    top = root.children[0]
    r["info"]["root_block"] = top.type
    if top.type not in OPTIMIZER_TYPES:
        fail("ROOT_TYPE", "top-level block is %r, which is not a known SCONE optimizer %s"
             % (top.type, sorted(OPTIMIZER_TYPES)))

    all_nodes = list(top.walk())
    r["info"]["nodes"] = len(all_nodes)

    # ---- an unresolved `<<` include makes the tree incomplete: FAIL, do not guess -------------
    incs = [n for n in all_nodes if n.type == "<<include>>"]
    if incs:
        r["info"]["includes"] = [n.get("path") for n in incs]
        fail("INCLUDE_UNRESOLVED",
             "%d zml include directive(s) (%s) at line(s) %s. Their contents are not read, so "
             "the controller tree in this file is incomplete and the parent chain cannot be "
             "decided from it. Inline the include or point this checker at the merged scenario."
             % (len(incs), ", ".join(str(n.get("path")) for n in incs),
                [n.line for n in incs]))

    unknown = sorted({n.type for n in all_nodes if n.type not in KNOWN_TYPES})
    # lowercase sub-structs like `position { ... }` / `force { ... }` are properties-with-braces
    unknown = [u for u in unknown if u[:1].isupper()]
    if unknown:
        r["info"]["unknown_block_types"] = unknown
        unver("block types not in SCONE's keyword inventory", ", ".join(unknown))

    # ---- structural invariant: SimulationObjective takes ONE controller ----------------------
    for n in all_nodes:
        if n.type in OBJECTIVE_TYPES:
            ctrls = [c for c in n.children if c.type in CONTROLLER_TYPES]
            r["info"].setdefault("objective_controller_children", []).extend(
                [c.type for c in ctrls])
            if len(ctrls) != 1:
                fail("OBJECTIVE_CONTROLLER_COUNT",
                     "%s at line %d has %d controller children (%s); it accepts exactly ONE, "
                     "the extras are reported as 'unused properties' and DROPPED"
                     % (n.type, n.line, len(ctrls), ", ".join(c.type for c in ctrls) or "none"))

    # ---- structural invariant: no controller beneath a measure -------------------------------
    for n in all_nodes:
        if n.type in CONTROLLER_TYPES:
            anc = n.parent
            while anc is not None and anc.type != "<file>":
                if anc.type in MEASURE_TYPES:
                    fail("CONTROLLER_UNDER_MEASURE",
                         "%s at line %d sits beneath %s (line %d): chain %s. SCONE reports the "
                         "whole subtree as unused and CONTINUES."
                         % (n.type, n.line, anc.type, anc.line, _fmt(n.chain())))
                    break
                anc = anc.parent

    # ---- `legs` hygiene, file-wide -----------------------------------------------------------
    legs_sites = []
    for n in all_nodes:
        for k, v, ln in n.props:
            if k != "legs":
                continue
            legs_sites.append({"host": n.type, "line": ln, "value": v})
            if v.strip().strip('"').lower() in FATAL_LEGS:
                fail("LEGS_SELECTS_NOTHING",
                     "line %d: `legs = %s` on %s. scone::Side accepts the enum but it selects NO "
                     "leg; the child controller is orphaned into 'unused properties' WITHOUT "
                     "SCONE naming `legs`, and the run completes with ZERO injection."
                     % (ln, v, n.type))
            elif v.strip().strip('"').lower() not in SAFE_LEGS:
                fail("LEGS_UNRECOGNISED_VALUE",
                     "line %d: `legs = %s` on %s. The only values with preserved evidence of "
                     "selecting a definite limb are %s. This instrument fails closed on the rest: "
                     "`banana` is a hard SCONE error, `opposite`/`other` select nothing, and "
                     "`both`/`0`/`1`/`\"left right\"` have no artifact establishing what they do."
                     % (ln, v, n.type, sorted(SAFE_LEGS)))
            if n.type not in LEGS_HOST_TYPES:
                fail("LEGS_WRONG_HOST",
                     "line %d: `legs = %s` declared on %s. `legs` is honoured on %s only; here it "
                     "is silently discarded and the reflex is built once per side (bilateral)."
                     % (ln, v, n.type, "/".join(sorted(LEGS_HOST_TYPES))))
    r["info"]["legs_sites"] = legs_sites

    # ---- locate the injected block ------------------------------------------------------------
    inj = [n for n in all_nodes if n.get("name") == name]
    r["info"]["injected_name"] = name
    r["info"]["injected_count"] = len(inj)
    if not inj:
        fail("NO_INJECTED_BLOCK",
             "no block carries `name = %s`. Either nothing was injected, or the splice landed "
             "somewhere this parse does not reach." % name)
        r["status"] = "FAIL"
        return r
    if len(inj) > 1:
        fail("DUPLICATE_INJECTED_BLOCK",
             "%d blocks carry `name = %s` (lines %s); the gain is applied more than once"
             % (len(inj), name, [n.line for n in inj]))

    b = inj[0]
    chain = b.chain()
    r["info"]["actual_chain"] = _fmt(chain)
    r["info"]["injected_line"] = b.line
    r["info"]["accepted_chains"] = [_fmt(c) for c in accepted_chains]
    if not any(_chain_matches(chain, p) for p in accepted_chains):
        landed = chain[-2] if len(chain) >= 2 else "<file>"
        parent = b.parent
        # first position at which the actual chain diverges from EVERY accepted chain
        div = 0
        while div < len(chain) and any(
                _chain_matches(chain[:div + 1], p[:div + 1]) for p in accepted_chains):
            div += 1
        expect_here = sorted({p[div] for p in accepted_chains if len(p) > div}) or ["<end>"]
        found_here = chain[div] if div < len(chain) else "<end>"
        fail("WRONG_PARENT_CHAIN",
             "injected block %r (line %d) has parent chain %s -- it LANDED UNDER %s (line %d). "
             "First divergence at depth %d: found %r, expected one of %s. Accepted chains: %s"
             % (name, b.line, _fmt(chain), landed,
                parent.line if parent is not None else -1,
                div, found_here, expect_here,
                " | ".join(_fmt(c) for c in accepted_chains)))
    else:
        r["info"]["chain_form"] = "A" if _chain_matches(chain, accepted_chains[0]) else "B"

    # ---- injected MuscleReflex count and gains ------------------------------------------------
    mrs = [n for n in b.walk() if n.type in REFLEX_TYPES]
    r["info"]["injected_reflexes"] = len(mrs)
    r["info"]["injected_reflex_types"] = sorted({n.type for n in mrs})
    targets = [n.get("target") for n in mrs]
    r["info"]["injected_targets"] = targets
    kvs = []
    for n in mrs:
        v = n.get("KV")
        if v is not None:
            try:
                kvs.append(float(v.strip('"')))
            except ValueError:
                unver("KV literal on %s line %d" % (n.type, n.line),
                      "value %r is not a plain number (free parameter?)" % v)
    r["info"]["injected_KV"] = kvs
    if expect_reflexes is None:
        unver("number of injected reflexes",
              "no --expect-reflexes given; observed %d (%s). The intended count is a contract "
              "with the caller and is not derivable from the file."
              % (len(mrs), ", ".join(t or "?" for t in targets)))
    elif len(mrs) != expect_reflexes:
        fail("REFLEX_COUNT", "expected %d injected reflexes, found %d (%s)"
             % (expect_reflexes, len(mrs), ", ".join(t or "?" for t in targets)))
    if expect_kv is not None:
        bad = [v for v in kvs if abs(v - expect_kv) > 1e-9]
        if bad or len(kvs) != len(mrs):
            fail("KV_MISMATCH", "expected KV = %g on all %d injected reflexes; found %s"
                 % (expect_kv, len(mrs), kvs))
    if kvs and all(v == 0.0 for v in kvs):
        r["info"]["zero_gain_control"] = True   # legitimate control -- structure still verified

    # ---- side declaration coherence -----------------------------------------------------------
    anc_legs, anc = None, b
    while anc is not None and anc.type != "<file>":
        if anc.get("legs") is not None:
            anc_legs = anc.get("legs")
            break
        anc = anc.parent
    suffixed = [t for t in targets if t and (t.endswith("_l") or t.endswith("_r"))]
    r["info"]["enclosing_legs"] = anc_legs
    r["info"]["side_suffixed_targets"] = suffixed
    if anc_legs and suffixed:
        fail("SIDE_CONTRADICTION",
             "the block is scoped by `legs = %s` yet declares side-suffixed target(s) %s. An "
             "explicit `_l`/`_r` suffix OVERRIDES `legs`, so the two can disagree silently."
             % (anc_legs, suffixed))
    if not anc_legs and not suffixed:
        unver("which limb the injection reaches",
              "no enclosing `legs` and no side-suffixed target; the reflex is built once per "
              "side (bilateral). Not a defect by itself -- state the intent.")

    # ---- things this instrument structurally cannot decide ------------------------------------
    unver("delivered gain magnitude",
          "structure cannot show how much torque the reflex delivered; use delivered_gain.py")
    unver("per-side duplication factor",
          "SCONE may build a side-unscoped reflex once per side; the file cannot show the "
          "resulting multiplicity")
    unver("whether SCONE accepted the file at run time",
          "no launcher log is read by this instrument; run check_unused.py on the log")

    r["status"] = "FAIL" if r["failures"] else "OK"
    return r


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    name, exp_r, exp_kv, as_json, paths = "SpasticL", None, None, False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--name":
            name = argv[i + 1]; i += 2
        elif a == "--expect-reflexes":
            exp_r = int(argv[i + 1]); i += 2
        elif a == "--expect-kv":
            exp_kv = float(argv[i + 1]); i += 2
        elif a == "--json":
            as_json = True; i += 1
        else:
            paths.append(a); i += 1
    if not paths:
        print(__doc__)
        return 2
    results = [analyze(p, name, exp_r, exp_kv) for p in paths]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print("%-10s %s" % (r["status"], r["path"]))
            print("           chain: %s" % r["info"].get("actual_chain", "<not located>"))
            for f in r["failures"]:
                print("    FAIL   [%s] %s" % (f["code"], f["detail"]))
            for u in r["could_not_verify"]:
                print("    UNVER  %s -- %s" % (u["item"], u["reason"]))
    return 0 if all(r["status"] == "OK" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
