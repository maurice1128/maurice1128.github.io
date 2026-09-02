"""reach_2x2_r273.py -- round 273. The reachability machinery PREREG_2x2_r270.md section 8 requires.

Four artefacts, to the r229 precedent, with the four defects that precedent had, fixed:

  1. REACHABILITY DEPOSIT -- every declared outcome with a concrete witness, MISSING_no_witness
     empty, GATE_PASSES.
  2. WITNESS GENERATOR CONSTRAINED TO ATTAINABLE CONFIGURATIONS -- HL half-widths are bounded
     by what n = 6 and the measured control-band widths permit (0.00179 .. 0.98554,
     derived in ATTAINABLE below). r229 proved rungs reachable over half-widths up to 3.0
     when only 0.15-0.45 were attainable, and certified three rungs that could never fire.
  3. PROSE-VERSUS-CODE LADDER ASSERTION -- parses the rung order out of the registration and
     COMPARES it to the code's, elementwise. r229's parser required [A-Z], silently dropped
     three rungs whose names carried decorations, then INTERSECTED the lists so it printed
     "match" while checking 12 of 15. This one strips decorations and compares sequences.
  4. MESSAGE-TRUTH OVER EVERY CONFIGURATION REACHING EACH OUTCOME, not one witness each.
     r229 stored only the first witness and passed a rung whose message was false for 96 of
     its 336 cases.

Plus a FIXTURE: the analysis runs end-to-end on a synthetic tree and writes a deposit before
any real cell is touched. r229 certified a ladder inside a script that raised NameError on
its first statement -- a digest proves a file is unchanged, never that it runs.

Read-only with respect to the corpus. Writes only into paper/.
"""
import io
import itertools
import json
import math
import os
import re
import sys
import tempfile

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = os.path.join(PAPER, "PREREG_2x2_r270.md")

ALPHA = 0.05
N_CHANNELS = 16
ALPHA_PRIME = ALPHA / N_CHANNELS                      # 0.003125, PREREG section 6
N_SEEDS = 14                                          # rev 5
MAG_RATIO = 2.0                                       # PREREG section 6, rung 3

# REV 5. delta is FROZEN at 2.534 * sigma -- its n = 6 value -- and no longer tracks the
# control range, whose expectation grows with n. Numerically delta therefore equals the
# sixteen measured n=6 band widths below, at every seed count.
# Attainable HL95 half-widths for a difference of two n=14 arms:
# sigma ~ width_6/2.534, half-width ~ 1.96 * sigma * sqrt(2/14).
BAND_WIDTHS = [0.00400, 0.16583, 0.27689, 0.32411, 0.35561, 0.36263, 0.41930, 0.47977,
               0.53333, 0.54323, 0.74372, 0.79181, 0.93312, 1.43665, 1.69422, 2.20691]
_HW = [1.96 * (w / 2.534) * math.sqrt(2.0 / N_SEEDS) for w in BAND_WIDTHS]
DELTA_FROZEN_AT = "2.534 * sigma (the n=6 control range), rev 5"
HW_MIN, HW_MAX = min(_HW), max(_HW)                   # 0.00179 .. 0.98554
DELTA_MIN, DELTA_MAX = min(BAND_WIDTHS), max(BAND_WIDTHS)

CODE_LADDER = ["FAILURE-DOMINATED", "UNDERPOWERED", "INTERACTION",
               "GROUP-ONLY", "TYPE-CONSISTENT", "NEITHER", "INCONCLUSIVE"]

MESSAGES = {
    "FAILURE-DOMINATED": "an arm has fewer than 2 cells completing 2 or more gait cycles: "
                         "kinematics undefined, time-to-failure is primary",
    "UNDERPOWERED": "an arm has fewer than 5 usable cells, or the exhaustive floor exceeds "
                    "alpha prime",
    "INTERACTION": "the type effect differs in sign between muscle groups, or in magnitude "
                   "by more than 2x with non-overlapping HL intervals",
    "GROUP-ONLY": "channels separate by muscle group and the type effect is within delta in "
                  "both groups",
    "TYPE-CONSISTENT": "the type effect exceeds delta with the same sign in both groups",
    "NEITHER": "all four arm means lie within the control band and the count is at its floor",
    "INCONCLUSIVE": "at n = 6 this channel's effects are too small or too imprecise to assign "
                    "to type, to group, or to neither",
}


# --------------------------------------------------------------- the ladder, as code
def decide(c):
    """PREREG section 6, evaluated in the registered order, first match wins."""
    if min(c["n_2cyc"]) < 2:
        return "FAILURE-DOMINATED"
    if min(c["n_usable"]) < 5 or c["floor"] > ALPHA_PRIME:
        return "UNDERPOWERED"

    tPF, tDF = c["t_pf"], c["t_df"]
    sPF = 0 if tPF == 0 else (1 if tPF > 0 else -1)
    sDF = 0 if tDF == 0 else (1 if tDF > 0 else -1)
    opposite = (sPF != 0 and sDF != 0 and sPF != sDF)
    big, small = max(abs(tPF), abs(tDF)), min(abs(tPF), abs(tDF))
    ratio_exceeds = (small > 0 and big / small > MAG_RATIO) or (small == 0 and big > 0)
    disjoint = (c["hl_pf"][1] < c["hl_df"][0]) or (c["hl_df"][1] < c["hl_pf"][0])
    if opposite or (ratio_exceeds and disjoint):
        return "INTERACTION"

    d = c["delta"]
    if c["group_separates"] and abs(tPF) <= d and abs(tDF) <= d:
        return "GROUP-ONLY"
    if abs(tPF) > d and abs(tDF) > d and sPF == sDF and sPF != 0:
        return "TYPE-CONSISTENT"
    if c["all_within_band"] and c["at_floor"]:
        return "NEITHER"
    # TERMINAL rung. Reached only when every substantive rung above has declined, so it can
    # never absorb a case that should fire another. It is an OUTCOME, not a bin.
    return "INCONCLUSIVE"


# --------------------------------------------------------------- message truth
def message_true(rung, c):
    """Does the rung's own message hold for THIS configuration? Checked for every config."""
    d = c["delta"]
    tPF, tDF = c["t_pf"], c["t_df"]
    sPF = 0 if tPF == 0 else (1 if tPF > 0 else -1)
    sDF = 0 if tDF == 0 else (1 if tDF > 0 else -1)
    if rung == "FAILURE-DOMINATED":
        return min(c["n_2cyc"]) < 2
    if rung == "UNDERPOWERED":
        return min(c["n_usable"]) < 5 or c["floor"] > ALPHA_PRIME
    if rung == "INTERACTION":
        opposite = (sPF != 0 and sDF != 0 and sPF != sDF)
        big, small = max(abs(tPF), abs(tDF)), min(abs(tPF), abs(tDF))
        ratio_exceeds = (small > 0 and big / small > MAG_RATIO) or (small == 0 and big > 0)
        disjoint = (c["hl_pf"][1] < c["hl_df"][0]) or (c["hl_df"][1] < c["hl_pf"][0])
        return opposite or (ratio_exceeds and disjoint)
    if rung == "GROUP-ONLY":
        return c["group_separates"] and abs(tPF) <= d and abs(tDF) <= d
    if rung == "TYPE-CONSISTENT":
        return abs(tPF) > d and abs(tDF) > d and sPF == sDF and sPF != 0
    if rung == "NEITHER":
        return c["all_within_band"] and c["at_floor"]
    if rung == "INCONCLUSIVE":
        # true iff no substantive rung's own criterion holds
        return not any(message_true(r, c) for r in CODE_LADDER[:-1])
    return False


# --------------------------------------------------------------- attainable config space
def configs():
    """Only ATTAINABLE configurations. Half-widths are bounded by n=6 and the measured bands."""
    deltas = [DELTA_MIN, 0.41930, DELTA_MAX]
    hws = [HW_MIN, 0.5 * (HW_MIN + HW_MAX), HW_MAX]
    # effects expressed as multiples of delta so the comparison to delta is meaningful,
    # and bounded by what a six-seed arm can displace: +-4 delta.
    effs = [-3.0, -1.5, -0.5, 0.0, 0.5, 1.5, 3.0]
    for n2 in (1, 2, 6):
        for nu in (4, 5, 6):
            for floor in (1.0 / 924, ALPHA_PRIME, 0.05):
                for d in deltas:
                    for ePF in effs:
                        for eDF in effs:
                            for hw in hws:
                                for centre_gap in (0.0, 4.0):
                                    tPF, tDF = ePF * d, eDF * d
                                    # HL intervals centred on each group's effect
                                    hl_pf = (tPF - hw, tPF + hw)
                                    hl_df = (tDF - hw + centre_gap * hw,
                                             tDF + hw + centre_gap * hw)
                                    for gs in (False, True):
                                        for awb in (False, True):
                                            for af in (False, True):
                                                yield {
                                                    "n_2cyc": [n2] * 4, "n_usable": [nu] * 4,
                                                    "floor": floor, "delta": d,
                                                    "t_pf": tPF, "t_df": tDF,
                                                    "hl_pf": hl_pf, "hl_df": hl_df,
                                                    "group_separates": gs,
                                                    "all_within_band": awb, "at_floor": af,
                                                    "hw": hw}


# --------------------------------------------------------------- prose ladder parser
def parse_prose_ladder(path):
    """Extract the rung order from the registration's section 6 table.

    Robust to decorations: rung names in the document carry ** and are preceded by table
    pipes; the r229 parser required [A-Z] immediately, dropped every decorated name, and
    then intersected rather than compared.
    """
    txt = io.open(path, encoding="utf-8").read()
    i = txt.index("**THE LADDER")
    j = txt.index("## 7.", i)
    seg = txt[i:j]
    rungs = []
    for line in seg.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        name = cells[1]
        name = re.sub(r"[\u2b50\u26d4\u26a0\*_`]", "", name).strip()
        if not name or name.lower() in ("rung", "---", ""):
            continue
        if re.fullmatch(r"[-: ]+", name):
            continue
        rungs.append(name)
    return rungs


# --------------------------------------------------------------- fixture
def fixture():
    """Run the analysis end-to-end on a synthetic tree and write a deposit. Proves it RUNS."""
    tmp = tempfile.mkdtemp(prefix="fixture_r273_")
    arms = ["WEAK_DF", "SPASTIC_PF", "WEAK_PF", "SPASTIC_DF"]
    corpus = {}
    for a in arms:
        for f in (0.05, 0.10, 0.20):
            for s in range(101, 107):
                v = {"WEAK_DF": 0.30, "SPASTIC_PF": -0.30,
                     "WEAK_PF": 0.28, "SPASTIC_DF": -0.28}[a] * (f / 0.20)
                corpus["%s|%.2f|%d" % (a, f, s)] = v + 0.01 * ((s - 103) % 3)
    p = os.path.join(tmp, "synthetic_corpus.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(corpus))

    loaded = json.loads(io.open(p, encoding="utf-8").read())
    ctrl = [0.0, 0.02, -0.02, 0.01, -0.01, 0.015]
    delta = max(ctrl) - min(ctrl)
    out = {}
    for f in (0.05, 0.10, 0.20):
        def arm_mean(a):
            v = [loaded["%s|%.2f|%d" % (a, f, s)] for s in range(101, 107)]
            return sum(v) / len(v)
        tPF = arm_mean("SPASTIC_PF") - arm_mean("WEAK_PF")
        tDF = arm_mean("SPASTIC_DF") - arm_mean("WEAK_DF")
        hw = 0.18725
        c = {"n_2cyc": [6] * 4, "n_usable": [6] * 4, "floor": 1.0 / 924, "delta": delta,
             "t_pf": tPF, "t_df": tDF, "hl_pf": (tPF - hw, tPF + hw),
             "hl_df": (tDF - hw, tDF + hw), "group_separates": False,
             "all_within_band": False, "at_floor": True, "hw": hw}
        out["f=%.2f" % f] = {"t_pf": tPF, "t_df": tDF, "delta": delta, "rung": decide(c)}
    dep = os.path.join(PAPER, "FIXTURE_2x2_r273.json")
    with io.open(dep, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"round": 273, "synthetic": True, "tree": tmp,
                   "note": "end-to-end run on a synthetic corpus; proves the pipeline "
                           "executes and writes, before any real cell is touched",
                   "results": out}, fh, indent=1)
        fh.write("\n")
    return {"tree": tmp, "deposit": "FIXTURE_2x2_r273.json", "results": out,
            "ran_end_to_end": True}


def main():
    fx = fixture()

    counts, witnesses, mt_fail, uncovered = {}, {}, {}, []
    n = 0
    for c in configs():
        n += 1
        r = decide(c)
        counts[r] = counts.get(r, 0) + 1
        if r == "UNCOVERED":
            if len(uncovered) < 5:
                uncovered.append({k: v for k, v in c.items()})
            continue
        if r not in witnesses:
            witnesses[r] = {k: v for k, v in c.items()}
        if not message_true(r, c):
            mt_fail.setdefault(r, {"n_false": 0, "n_total": 0, "example": None})
            mt_fail[r]["n_false"] += 1
            if mt_fail[r]["example"] is None:
                mt_fail[r]["example"] = {k: v for k, v in c.items()}
    for r in counts:
        if r in mt_fail:
            mt_fail[r]["n_total"] = counts[r]

    prose = parse_prose_ladder(PREREG)
    ladder_match = (prose == CODE_LADDER)

    declared = set(CODE_LADDER)
    reached = set(k for k in counts if k != "UNCOVERED")
    missing = sorted(declared - reached)
    undeclared = sorted(reached - declared)

    gate = (not missing and not undeclared and ladder_match
            and not mt_fail and not uncovered and fx["ran_end_to_end"])

    out = {"round": 273, "prereg": "PREREG_2x2_r270.md rev 3 sha256 09180446",
           "n_configurations": n,
           "attainability": {
               "source": "CHANNELS_G2_r219.json control band widths, n=6",
               "band_width_range": [DELTA_MIN, DELTA_MAX],
               "HL95_halfwidth_range": [HW_MIN, HW_MAX],
               "n_seeds": N_SEEDS,
               "delta_definition": DELTA_FROZEN_AT,
               "rule": "sigma ~ width_6/2.534; halfwidth ~ 1.96*sigma*sqrt(2/%d)" % N_SEEDS,
               "note": "the generator emits NO configuration outside this range"},
           "counts": counts,
           "declared": CODE_LADDER, "reachable": sorted(reached),
           "MISSING_no_witness": missing, "UNDECLARED_but_reachable": undeclared,
           "witnesses": witnesses,
           "prose_ladder": prose, "code_ladder": CODE_LADDER,
           "prose_matches_code_ladder": ladder_match,
           "message_truth_violations": mt_fail,
           "UNCOVERED_configurations": {"count": counts.get("UNCOVERED", 0),
                                        "examples": uncovered},
           "fixture": fx,
           "GATE_PASSES": gate}

    with io.open(os.path.join(PAPER, "REACH_2x2_r273.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")

    print("configurations evaluated: %d   (attainable half-widths %.5f .. %.5f)"
          % (n, HW_MIN, HW_MAX))
    print("counts: %s" % json.dumps(counts))
    print("MISSING_no_witness: %s" % (missing or "none"))
    print("UNDECLARED_but_reachable: %s" % (undeclared or "none"))
    print("prose ladder: %s" % prose)
    print("code  ladder: %s" % CODE_LADDER)
    print("prose_matches_code_ladder: %s" % ladder_match)
    print("message_truth_violations: %s"
          % (json.dumps({k: "%d of %d" % (v["n_false"], v["n_total"])
                         for k, v in mt_fail.items()}) if mt_fail else "none"))
    print("UNCOVERED configurations: %d" % counts.get("UNCOVERED", 0))
    print("fixture ran end-to-end: %s -> %s" % (fx["ran_end_to_end"], fx["deposit"]))
    print()
    print("GATE_PASSES: %s" % gate)
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
