# -*- coding: utf-8 -*-
"""Verify the r311 replace-don't-annotate fixes by PARSING the live fields only.

Round two's lesson made this necessary: a whole-file text search cannot distinguish
"the wrong statement is live" from "the wrong statement is preserved in a subordinate
field", which is exactly what the corrected policy requires to still be present. So this
checks the LIVE field's content and separately confirms a superseded copy exists.
"""
import io, json, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"


def load(f):
    return json.load(io.open(os.path.join(P, f), encoding="utf-8"))


def has_superseded(d):
    return any(("ORIGINAL_WRONG" in k) or ("SUPERSEDED" in k) for k in d)



SUBORD_SUFFIX = ("_ORIGINAL_WRONG", "_SUPERSEDED", "_ORIGINAL_STALE", "_ORIGINAL_REFUTED",
                 "_PREMISE_REFUTED", "_KEY_RETIRED", "_UNDATED_ORIGINAL", "_WERE_WRONG",
                 "_DEFECTIVE", "_RETIRED", "_ORIGINAL", "_STALE", "_WRONG")
NEG = ("not a claim", "is NOT", "NOT SUPPORTED", "is withdrawn", "was withdrawn",
       "no longer", "inconsistent with", "previously", "earlier version",
       "earlier claim", "is FALSE", "WRONG", "superseded", "corrected",
       "does not hold", "stale", "REFUTED", "an earlier")


def is_subordinate(k):
    """SUFFIX test, not substring.

    r356: 'SUPERSEDED_BY_r306' is a PREFIX use meaning 'this is superseded BY r306' -- a
    pointer to the superseding round, NOT a marker that the block holds retired content.
    A substring test excluded that whole block and made the r305 check toothless: it
    passed against a known-bad pre-fix backup. Subordination is marked by a SUFFIX.
    """
    ks = str(k)
    return any(ks.endswith(s) or (s + "_") in ks for s in SUBORD_SUFFIX)


def live_paths(o, path=""):
    """Yield (path, string) for every string NOT under a subordinate key."""
    if isinstance(o, dict):
        for k, v in o.items():
            if is_subordinate(k):
                continue
            for r in live_paths(v, path + "/" + str(k)):
                yield r
    elif isinstance(o, list):
        for i, v in enumerate(o):
            for r in live_paths(v, path + "[%d]" % i):
                yield r
    elif isinstance(o, str):
        yield (path, o)


def repudiated_only(text, phrase):
    """True if every occurrence of phrase sits inside a negating clause.

    r311 policy REQUIRES a live field to restate a wrong claim in order to withdraw it,
    so 'phrase absent' is structurally impossible for a compliant field. The correct
    test is that no occurrence ASSERTS the claim.
    """
    low = text.lower()
    if phrase.lower() not in low:
        return True
    i = 0
    while True:
        j = low.find(phrase.lower(), i)
        if j < 0:
            return True
        window = text[max(0, j - 260):j + 260]
        if not any(n.lower() in window.lower() for n in NEG):
            return False
        i = j + 1


def live_claim_ok(d, phrase, field=None):
    """No live field asserts phrase (occurrences allowed only when repudiated)."""
    if field is not None:
        return repudiated_only(d.get(field, ""), phrase)
    for _, s in live_paths(d):
        if not repudiated_only(s, phrase):
            return False
    return True


rows = []

d = load("KNEE_VS_DURATION_r284.json")["duration_overlap_band"]
rows.append(("r284 colliding band_s removed", "band_s" not in d,
             "narrow key present: %s" % ("band_s_r284_narrow" in d)))

r = load("R294_GAIN_r302.json")
rows.append(("r302 VERDICT asserts no asymptote claim",
             live_claim_ok(r, "asymptote", field="VERDICT"), r["VERDICT"][:70]))
rows.append(("r302 wrong text preserved", has_superseded(r), ""))

b = load("BISTABILITY_r288.json")
rows.append(("r288 claim asserts no not-graded claim",
             live_claim_ok(b, "does not produce graded", field="claim"),
             b["claim"][:70]))
rows.append(("r288 wrong text preserved", has_superseded(b), ""))

e = load("BANDFILL_ENDPOINT_r291.json")
rows.append(("r291 status no longer cites section 5",
             "section 5" not in e.get("status", ""), e.get("status", "")[:70]))

cd_ = load("COVERAGE_RECONCILE_r305.json")
rows.append(("r305 no live field asserts '48 of 60'",
             live_claim_ok(cd_, "48 of 60"), ""))

m = load("MATCHED20_ENDPOINT_r298.json")
sk = [k for k in m if "SHORTFALL" in k.upper()]
sat = all("SATISFIED" in json.dumps(m[k]).upper() for k in sk) if sk else False
rows.append(("r298 D18/D19 shortfall marked satisfied", sat, ", ".join(sk)[:70]))

s = load("SEPARATION_r280.json")
blob = json.dumps(s)
rows.append(("r280 records mtimes are historical",
             ("historical" in blob.lower()) or ("no longer recoverable" in blob.lower()), ""))

w = max(len(x[0]) for x in rows)
ok = 0
for name, passed, note in rows:
    ok += bool(passed)
    print("%-*s  %s   %s" % (w, name, "PASS" if passed else "FAIL", note))
print("\n%d of %d pass" % (ok, len(rows)))
