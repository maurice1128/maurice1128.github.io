# -*- coding: utf-8 -*-
"""Check that the r324 fix replaced line-number citations with a content anchor.

Deliberately inspects the LIVE `note` field only. The wrong line numbers are expected to
survive in the subordinate `LINE_NUMBERS_WERE_WRONG_r324` block — that is the r312 policy —
so a whole-file search cannot answer this question.
"""
import io, json, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
for f in ("LMRONLY_r223.json", "CLASSIFIER_r222.json"):
    d = json.load(io.open(os.path.join(P, f), encoding="utf-8"))
    w = d.get("PERMUTATION_NULL_WITHDRAWAL", {})
    note = w.get("note", "")
    print("=== %s ===" % f)
    print("  block keys        : %s" % ", ".join(w))
    print("  live note cites LN: %s" % any(x in note for x in ("475", "477", "544")))
    print("  live note anchored: %s" % ("WITHDRAWN AT r250" in note))
    print("  note[:130]        : %s" % note[:130].replace("\n", " "))
    sub = [k for k in w if "WRONG" in k.upper() or "SUPERSED" in k.upper()]
    print("  subordinate block : %s" % (sub or "NONE"))
    print()
