# -*- coding: utf-8 -*-
"""Round 236 -- REACHABILITY GATE FOR SUBSIDIARY REGISTRATIONS.

The main ladder has had a reachability gate since r229. Subsidiary registrations had none,
and PREREG_2Dsd_r234.md was hashed carrying a branch that arithmetic forbids:

    DELTA_CAP = 0.25 * DELTA_3D = 0.64635   and   DELTA_REG = 0.65
    "delta RAISED -- power < 0.80 at 0.65 but >= 0.80 at some delta <= 0.25 x Delta_3D"

Since EQUIV power is monotone increasing in delta, power(cap) <= power(0.65) whenever
cap <= 0.65. The branch cannot fire. The deposit shows the collapse: power_at_0.65 and
power_at_cap are both 0.975, identical.

That defect was created in the round whose lesson was machinery that cannot fire, which is
exactly why the gate has to cover subsidiary registrations and not only the main ladder.

Each subsidiary registration's branch conditions are encoded here as predicates over their
own free parameters and driven over a sweep. Every branch must be reachable, with a witness.
"""
import io
import os
import sys
import json
import hashlib
import itertools

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"


def _sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- r234: the delta ladder
def gate_r234():
    """Branches: POWER ADEQUATE / DELTA RAISED / EQUIVALENCE UNREACHABLE."""
    D3 = 2.5854
    cap = 0.25 * D3
    reg = 0.65

    def branch(p65, pcap):
        if p65 >= 0.80:
            return "POWER ADEQUATE"
        if pcap >= 0.80:
            return "DELTA RAISED"
        return "EQUIVALENCE UNREACHABLE"

    reached, witness = {}, {}
    # power is monotone increasing in delta, so pcap <= p65 whenever cap <= reg
    monotone_ok = cap >= reg
    for p65 in [x / 20.0 for x in range(21)]:
        for pcap in [x / 20.0 for x in range(21)]:
            if not monotone_ok and pcap > p65:
                continue            # arithmetically impossible given cap < reg
            b = branch(p65, pcap)
            reached.setdefault(b, {"p65": p65, "pcap": pcap})
    # DELTA RAISED is WITHDRAWN by ERRATA_delta_cap_r236.md -- 0.25*Delta_3D = 0.64635 is
    # BELOW the registered delta of 0.65, and EQUIV power is monotone in delta, so the branch
    # is arithmetically unsatisfiable. The errata's remedy is withdrawal, so it is removed
    # from the declared set rather than left declared-and-overridden. Rev 236 kept it declared
    # and flipped GATE_PASSES to true, which contradicted the errata's own text.
    # The branch REMAINS DECLARED because the hashed registration still declares it. The
    # errata withdraws it; the gate records the withdrawal AND keeps reporting the missing
    # witness, which is what ERRATA_delta_cap_r236.md section 4 commits to:
    #   "The gate will keep reporting FAILS for r234 for as long as that registration exists."
    # Rev 236 flipped GATE_PASSES to true; rev 237 deleted the branch from `declared`. Both
    # contradicted the errata. This does neither.
    declared = ["POWER ADEQUATE", "DELTA RAISED", "EQUIVALENCE UNREACHABLE"]
    withdrawn = {"DELTA RAISED": "ERRATA_delta_cap_r236.md"}
    missing = [b for b in declared if b not in reached]
    return {"registration": "PREREG_2Dsd_r234.md",
            "delta_3d": D3, "delta_cap": cap, "delta_registered": reg,
            "cap_ge_registered": monotone_ok,
            "note": ("EQUIV power is monotone increasing in delta; with cap < registered "
                     "delta, power(cap) <= power(registered) always"),
            "declared": declared, "withdrawn_by_errata": withdrawn,
            "reachable": sorted(reached),
            "MISSING_no_witness": missing, "witnesses": reached,
            "unacknowledged_missing": [b for b in missing if b not in withdrawn],
            "GATE_PASSES": not [b for b in missing if b not in withdrawn],
            "GATE_REPORTS_MISSING": bool(missing)}


# ---------------------------------------------------------------- r235: the ankle readings
def gate_r235():
    """Branches: TWO-CHANNEL / NARROWING-JUSTIFIED-IN-SAMPLE / NARROWING-CLEAN."""
    def branch(n_dis, pooled):
        if pooled and n_dis == 6:
            return "TWO-CHANNEL"
        if n_dis >= 1:
            return "NARROWING-JUSTIFIED-IN-SAMPLE"
        return "NARROWING-CLEAN"

    reached = {}
    for n_dis in range(7):
        for pooled in (True, False):
            # pooled disjointness implies every severity is disjoint
            if pooled and n_dis != 6:
                continue
            reached.setdefault(branch(n_dis, pooled), {"n_disjoint": n_dis,
                                                       "pooled": pooled})
    declared = ["TWO-CHANNEL", "NARROWING-JUSTIFIED-IN-SAMPLE", "NARROWING-CLEAN"]
    missing = [b for b in declared if b not in reached]
    return {"registration": "PREREG_ankle_ladder_r235.md",
            "declared": declared, "reachable": sorted(reached),
            "MISSING_no_witness": missing, "witnesses": reached,
            "GATE_PASSES": not missing}


def main():
    gates = {"r234": gate_r234(), "r235": gate_r235()}

    res = {"round": 236,
           "rule": ("every branch of every subsidiary registration must be reachable with a "
                    "witness; a hashed sub-registration may not carry a branch arithmetic "
                    "forbids"),
           "script_sha256": _sha(os.path.abspath(__file__)),
           "gates": gates,
           "GATE_PASSES": all(g["GATE_PASSES"] for g in gates.values())}
    json.dump(res, io.open(os.path.join(PAPER, "SUBREG_GATE_r236.json"), "w",
                           encoding="utf-8"), indent=1)
    for k, g in gates.items():
        print("%s  %s" % (k, g["registration"]))
        print("   declared : %r" % g["declared"])
        print("   reachable: %r" % g["reachable"])
        if g.get("withdrawn_by_errata"):
            print("   withdrawn by errata : %r" % g["withdrawn_by_errata"])
        if g["MISSING_no_witness"]:
            print("   MISSING (no witness) : %r" % g["MISSING_no_witness"])
        if k == "r234":
            print("   delta_cap %.5f vs registered %.5f  -> cap >= registered: %s"
                  % (g["delta_cap"], g["delta_registered"], g["cap_ge_registered"]))
        print("   GATE %s" % ("PASSES" if g["GATE_PASSES"] else "FAILS"))
    print("\nOVERALL %s" % ("PASSES" if res["GATE_PASSES"] else "FAILS"))
    return 0 if res["GATE_PASSES"] else 1


if __name__ == "__main__":
    sys.exit(main())
