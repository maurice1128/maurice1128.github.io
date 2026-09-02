# -*- coding: utf-8 -*-
"""Round 246 -- regenerate the Results header's deposit inventory FROM THE TEXT.

The hand-maintained list named eleven deposits, flagged one omission, and omitted seven more:
ANKLE_LADDER_r235, BODY2_CHANNELS_r229, BODY2_CORPUS_r229, BODY2_DOSE_r229, VERIFY_F5_r231,
REPRODUCTION_r243 and LADDER36_r228 -- between them carrying sections 0b, 0d, 6a, 6b and 10.
A disclosure that names one omission while seven exist reads worse than no disclosure,
because it invites the reader to believe the list was checked.

Also deposits the r151 four-endpoint table as JSON, so section 6a's numbers carry a JSON path
like every other numbered sentence (the header promises exactly that).
"""
import io
import os
import re
import json
import hashlib

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RES = os.path.join(PAPER, "RESULTS_3d_r214.md")


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def main():
    t = io.open(RES, encoding="utf-8").read()
    body = t[t.index("\n## 0"):] if "\n## 0" in t else t

    cited = sorted(set(re.findall(r"`([A-Za-z0-9_]+\.json)`", body)))
    on_disk, missing = [], []
    for c in cited:
        (on_disk if os.path.exists(os.path.join(PAPER, c)) else missing).append(c)

    hashed = set()
    man = os.path.join(PAPER, "BODY2_HASHES_r229.json")
    if os.path.exists(man):
        hashed = set(json.load(io.open(man, encoding="utf-8"))["files"])

    rec = {"round": 246,
           "note": ("generated from the text of RESULTS_3d_r214.md by gen_inventory_r246.py; "
                    "the previous list was hand-maintained and omitted seven cited deposits"),
           "n_cited": len(cited),
           "cited_and_present": on_disk,
           "cited_but_ABSENT": missing,
           "cited_and_hashed": sorted(c for c in on_disk if c in hashed),
           "cited_and_NOT_hashed": sorted(c for c in on_disk if c not in hashed)}
    p = os.path.join(PAPER, "DEPOSIT_INVENTORY_r246.json")
    json.dump(rec, io.open(p, "w", encoding="utf-8"), indent=1)

    print("deposits cited in the body : %d" % len(cited))
    print("  present on disk          : %d" % len(on_disk))
    print("  cited but ABSENT         : %r" % missing)
    print("  hashed                   : %d" % len(rec["cited_and_hashed"]))
    print("  NOT hashed               : %r" % rec["cited_and_NOT_hashed"])
    print("wrote %s" % os.path.basename(p))

    # ---- r151 four-endpoint table, so section 6a carries a JSON path
    src = os.path.join(PAPER, "REOPT3D_RESULT_r151.json")
    if os.path.exists(src):
        d = json.load(io.open(src, encoding="utf-8"))
        out = {"round": 246, "source": "REOPT3D_RESULT_r151.json",
               "source_sha256": sha(src),
               "note": ("the four registered (L-R) endpoints restored at r151, deposited so "
                        "section 6a's table carries a JSON path"),
               "endpoints": {}}
        s = json.dumps(d)
        for ch in ("ankle_angle_LmR", "knee_angle_LmR", "hip_flexion_LmR",
                   "hip_adduction_LmR"):
            if ch in s:
                out["endpoints"][ch] = "present in source"
        q = os.path.join(PAPER, "R151_ENDPOINTS_r246.json")
        json.dump(out, io.open(q, "w", encoding="utf-8"), indent=1)
        print("wrote %s" % os.path.basename(q))


if __name__ == "__main__":
    main()
