"""The check that was free all along: did SCONE report discarding the injected block?

WHY THIS EXISTS, AND WHY IT IS EMBARRASSING.
This project spent twenty adversarial review rounds inferring, from `.sto` residuals and directory
tokens, whether an injected reflex reached the model. Two conditions (`SPASpf` KV = 3.0, `SPASpf2`
KV = 8.0) delivered exactly nothing and were called "silent zeros" throughout.

They were never silent. SCONE printed this to stdout at launch, every time:

    Warning, unused properties:
    CmaOptimizer
      SimulationObjective
        ReflexController
          name = SpasticL *
          MuscleReflex
            target = soleus_l *
            KV = 0.100 *

The simulator named the discarded block, its target, and its gain, in plain English, on the first
line of every affected run's log. Verified on the 2x2x2 grid: all four wrapper=0 cells emit it,
all four wrapper=1 cells emit zero warnings.

Cause: `SimulationObjective` takes ONE controller child. An injected `ReflexController` placed as a
bare sibling of `GaitStateController` is parsed, warned about, and dropped.

⛔ CORRECTED 2026-08-02 (round 37, referee "register the instruments" item). The two sentences
that stood here said that "wrapping both in a `CompositeController` is what makes it reach the
model". THAT IS NOT THE CURRENT DESIGN AND `gen_conditions.make_scenario` NOW FORBIDS IT.

What the generator actually does, and why:

  * The injected block is a `ConditionalController` (it carries `legs = left`, which is the
    single source of truth for which limb is lesioned). It is spliced in as ONE MORE
    `ConditionalController` inside `GaitStateController / ConditionalControllers`, immediately
    before that node's closing brace. `make_scenario` does this by brace-matching, and its own
    block comment records the four-way placement probe that established it:

        ConditionalController{legs} under CompositeController      -> DISCARDED
        ConditionalController{legs} inside ConditionalControllers  -> ACCEPTED, 1.0x
        bare ReflexController, target = soleus_l (the old form)    -> ACCEPTED, 2.0x
        bare ReflexController carrying `legs` itself               -> `legs` DISCARDED, 2.0x

  * So a `ConditionalController` under a `CompositeController` is the DISCARD case, not the fix:
    `ConditionalController` is not a valid child of `CompositeController`, and SCONE names the
    whole subtree in `Warning, unused properties:` and CONTINUES AS A WARNING. An earlier version
    of `make_scenario` did exactly that, so every scenario it generated was a KV = 0 run wearing
    a SPAS label.

  * `CmaOptimizer/SimulationObjective/CompositeController/ReflexController` remains in
    ACCEPTED_CHAINS below, because SCONE does accept it -- but it accepts a BARE
    `ReflexController` there, not a `ConditionalController`, and that is the historical form
    measured at 2.0x delivery (side-unscoped, built once per side, both landing on the left
    muscle). It is "accepted" in the sense of "reaches the model", NOT in the sense of
    "is what this study uses".

This check is cheaper and STRICTER than `delivered_gain.py`: it catches the 0x mode with certainty
from the simulator's own report, rather than inferring it from a missing channel -- and "channel
absent" is ambiguous, because SCONE also omits channels for contributions that are identically zero
for legitimate reasons (an optimised gain reaching 0).

Run it on the launcher log BEFORE reading any result. It requires no simulation and no .sto.

EXTENDED 2026-08-02: it no longer merely COUNTS the warning. It PARSES the warning tree by
indentation and ASSERTS THE PARENT CHAIN of the injected block. SCONE prints the full path from
the root optimizer down to the discarded node, so the log alone distinguishes

    CmaOptimizer/SimulationObjective/ReflexController
        -- failure mode 1: bare sibling of GaitStateController, SimulationObjective takes one
           controller, the extra one is dropped (the four wrapper=0 grid cells)

from

    CmaOptimizer/SimulationObjective/CompositeMeasure/ConditionalController/ReflexController
        -- failure mode 2: the splice landed under a Measure (ARMD)

and the checker now REPORTS WHICH PARENT the block actually landed under instead of only saying
that something was discarded.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The two parent chains under which an injected block has been OBSERVED to reach the model; kept
# in sync with check_structure.ACCEPTED_CHAINS. Anything the log names as unused is by definition
# NOT one of these -- the list is carried here so the failure message can state the contrast.
ACCEPTED_CHAINS = (
    "CmaOptimizer/SimulationObjective/GaitStateController/ConditionalControllers/"
    "ConditionalController/ReflexController",
    "CmaOptimizer/SimulationObjective/CompositeController/ReflexController",
)


# `legs = opposite` and `legs = other` are ACCEPTED by SCONE's scone::Side enum but select no leg.
# The whole child controller is then orphaned into the unused list -- and SCONE does NOT name
# `legs` in the warning, so the message looks like an ordinary unknown-property complaint about the
# reflex itself. It is a Warning, not an Error: the optimization runs to completion and produces a
# normal-looking gait with ZERO injection. That is exactly the SPASpf / SPASpf2 failure, in which a
# declared KV of 8.0 delivered nothing while reaching generation 584.
FATAL_LEGS = ("opposite", "other")


def check_legs(scenario_path):
    """Refuse a scenario declaring a `legs` value that silently selects no leg."""
    if not os.path.exists(scenario_path):
        return True, "no scenario file"
    txt = open(scenario_path, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r"legs\s*=\s*\"?(\w+)\"?", txt):
        if m.group(1).lower() in FATAL_LEGS:
            return False, ("legs = %s selects NO leg -- SCONE accepts the enum, orphans the whole "
                           "child controller into 'unused properties' WITHOUT naming `legs`, and "
                           "continues as a Warning. The injection is silently absent."
                           % m.group(1))
    return True, "legs value ok"


def parse_unused_tree(log_path):
    """Parse SCONE's `Warning, unused properties:` block into a node list.

    Returns (state, nodes, raw) where
      state  : 'NO_LOG' | 'LOG_UNUSABLE' | 'NO_WARNING' | 'WARNING'
      nodes  : list of {'type', 'chain' (tuple, root-first, includes own type), 'depth',
                        'props' [(key, value, unused_flag)], 'line'}
      raw    : the de-timestamped warning block, verbatim

    The block is an indentation tree, 2 spaces per level, printed root-first:

        CmaOptimizer
          SimulationObjective
            CompositeMeasure
              ConditionalController
                states = ... *
                ReflexController
                  name = SpasticL *

    Lines containing ' = ' are properties of the node above them; bare identifiers are nodes.
    Every SCONE line carries an 'HH:MM:SS ' prefix, which is stripped FIRST -- an earlier version
    delimited the block before stripping and therefore terminated after one line.
    """
    if not os.path.exists(log_path):
        return "NO_LOG", [], ""
    txt = open(log_path, encoding="utf-8", errors="ignore").read()
    lines = [re.sub(r"^\d\d:\d\d:\d\d\s?", "", ln) for ln in txt.splitlines()]
    start = next((i for i, ln in enumerate(lines) if "unused properties" in ln), None)
    if start is None:
        # FAIL CLOSED ON A LOG THAT NEVER REACHED THE POINT WHERE THE WARNING IS PRINTED.
        # SCONE emits the warning after `pooled_evaluator started threads:` and before
        # `Creating folder .../<sig>`. A truncated, still-being-written, or ZERO-BYTE log
        # therefore contains no warning for a reason that has nothing to do with the scenario.
        # The pre-2026-08-02 version returned "no unused-property warning" -> `ok` -> the suite
        # printed "PASSED: no injected block was reported as unused" for a 0-byte
        # `optimization.log`. Every SCONE result dir ships one of those, empty, so the suite
        # could be handed a file that proves nothing and would call it clean.
        if not any(("Creating folder" in ln) or ("Starting optimization" in ln) for ln in lines):
            return "LOG_UNUSABLE", [], ""
        return "NO_WARNING", [], ""
    body = []
    for j, ln in enumerate(lines[start + 1:]):
        if not ln.strip():
            break
        ind = len(ln) - len(ln.lstrip(" \t"))
        if ind == 0 and body:      # a second root-level line ends the tree
            break
        body.append((start + 1 + j, ln))
    nodes, stack = [], []          # stack of (depth, node)
    for lineno, ln in body:
        ind = len(ln) - len(ln.lstrip(" \t"))
        depth = ind // 2
        s = ln.strip()
        m = re.match(r"^([A-Za-z_][\w.]*)\s*=\s*(.*?)(\s\*)?$", s)
        if m:                                   # property of the current node
            key, val, star = m.group(1), m.group(2).strip(), bool(m.group(3))
            while stack and stack[-1][0] >= depth:
                stack.pop()
            if stack:
                stack[-1][1]["props"].append((key, val, star))
            continue
        while stack and stack[-1][0] >= depth:  # node line
            stack.pop()
        chain = tuple(n["type"] for _, n in stack) + (s,)
        nd = {"type": s, "chain": chain, "depth": depth, "props": [], "line": lineno + 1}
        nodes.append(nd)
        stack.append((depth, nd))
    return "WARNING", nodes, "\n".join(ln for _, ln in body)


def check(log_path, expect_names=("SpasticL",), accepted_chains=ACCEPTED_CHAINS):
    """(ok, message). ok=False if SCONE reported discarding anything we care about."""
    if not os.path.exists(log_path):
        # FAILS CLOSED. This returned (None, ...) and main() did not count it, so
        #     check_unused.py good.txt DOES_NOT_EXIST.txt
        # printed "PASSED: no injected block was reported as unused" and exited 0 having read
        # no evidence at all for the second run. That violates this project's own acceptance
        # condition #4 (an instrument must fail closed on unknown input), and it is exactly the
        # case that matters: SPASpf/SPASpf2 -- the two runs that delivered a declared KV of
        # 3.0 and 8.0 as nothing -- retained no launcher log.
        return False, ("NO LAUNCHER LOG -- absence of a warning cannot be established, so this "
                       "run is UNVERIFIED, not clean")
    state, nodes, block = parse_unused_tree(log_path)
    if state == "LOG_UNUSABLE":
        return False, ("LOG UNUSABLE (%d bytes) -- it never reached 'Creating folder' / "
                       "'Starting optimization', the point after which SCONE has already printed "
                       "any unused-property warning. Absence of a warning here is absence of "
                       "evidence, not evidence of absence." % os.path.getsize(log_path))
    if state == "NO_WARNING":
        return True, "no unused-property warning"

    # Which node in the discarded tree IS our injected block? SCONE prints `name = SpasticL *`
    # as a PROPERTY of the ReflexController node, so match on the property, not the node type.
    hits = [n for n in nodes
            if any(k == "name" and v in expect_names for k, v, _ in n["props"])]
    if not hits:   # fall back: any node whose own type is one of the expected names
        hits = [n for n in nodes if n["type"] in expect_names]

    gains = re.findall(r"(KV|KL|KF|KP|C0)\s*=\s*([-0-9.eE+]+)\s*\*", block)
    g = ", ".join("%s=%s" % kv for kv in gains) or "gain not shown"

    if hits:
        msgs = []
        for n in hits:
            chain = "/".join(n["chain"])
            landed = n["chain"][-2] if len(n["chain"]) >= 2 else "<root>"
            msgs.append("SCONE DISCARDED %s (%s) -- the injection never reached the model. "
                        "ACTUAL PARENT CHAIN: %s ; it LANDED UNDER %s. Accepted: %s"
                        % (n["props"][0][1] if n["props"] else n["type"], g, chain, landed,
                           " | ".join(accepted_chains)))
        # `legs` appearing in the discarded tree means SCONE threw the side scoping away too
        if any(k == "legs" for n in nodes for k, _, _ in n["props"]):
            legs_vals = [v for n in nodes for k, v, _ in n["props"] if k == "legs"]
            msgs.append("`legs = %s` is INSIDE the discarded tree, so the side scoping was "
                        "discarded with it" % ", ".join(legs_vals))
        return False, " || ".join(msgs)

    other = "; ".join("/".join(n["chain"]) for n in nodes if n["props"]) or "<no named node>"
    return False, ("unused properties reported, but not for %s -- discarded node(s): %s"
                   % (list(expect_names), other))


def main():
    args = sys.argv[1:]
    logs = []
    for a in args:
        logs.extend(glob.glob(a) if ("*" in a or "?" in a) else [a])
    if not logs:
        logs = sorted(glob.glob(os.path.join(HERE, "opt_*", "log_*.txt")))
    print("Checking %d launcher log(s) for discarded injections\n" % len(logs))
    bad = 0
    for lg in logs:
        ok, msg = check(lg)
        tag = os.path.basename(lg).replace("log_", "").replace(".txt", "")
        if ok is None:
            print("  %-16s %s" % (tag, msg))
        elif ok:
            print("  %-16s ok" % tag)
        else:
            print("  %-16s *** %s ***" % (tag, msg))
            bad += 1
    print("\n%s" % ("=" * 70))
    if bad:
        print("FAILED: %d log(s) are NOT CLEAN -- the block was discarded, something else was "
              "discarded, or the log cannot establish either way." % bad)
        print("Do not read any result from these. Each line above says which of the three it is.")
    else:
        print("PASSED: no injected block was reported as unused.")
        print("NOTE: this proves the block was ACCEPTED, not that it was delivered ONCE.")
        print("The 2x duplication produces no warning. Use delivered_gain.py for the amount.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
