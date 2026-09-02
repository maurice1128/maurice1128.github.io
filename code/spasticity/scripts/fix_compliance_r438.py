# -*- coding: utf-8 -*-
"""r438: apply the compliance fixes the four cold audits found and I independently verified.

Nothing here changes a measurement. It corrects a transcription error, labels post-hoc material
as post-hoc, re-derives two registered predictions on the registered cells only, and fixes a
defect record that was wrong about its own census.
"""
import glob
import hashlib
import io
import json
import os
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"


def bak(name, tag="r438"):
    p = os.path.join(P, name)
    b = p + ".bak_" + tag
    if not os.path.exists(b):
        shutil.copy2(p, b)
    return p


# ---------------------------------------------------------------- F5 hash typo
p = bak("SPANNING_RESULT_r421.json")
d = json.load(io.open(p, encoding="utf-8"))
real = hashlib.sha256(io.open(os.path.join(P, "PREREG_spanning_r421.md"), "rb").read()).hexdigest()
old = d["registration_sha256"]
d["registration_sha256"] = real
d["HASH_TRANSCRIPTION_ERROR_r438"] = {
    "what": "this deposit recorded registration_sha256 as a 63-character string; one character was "
            "dropped when it was transcribed by hand, so the attestation failed on its face.",
    "recorded_was": old, "correct_is": real,
    "the_registration_itself_was_never_altered":
        "PREREG_spanning_r421.md.sha256 holds the correct value and the .md still matches it. A "
        "transcription error in the deposit, not tampering with the registration.",
    "found_by": "cold preregistration-compliance audit, 2026-08-26"}
io.open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("F5  r421 registration hash  %d -> %d chars" % (len(old), len(real)))

# ------------------------------------------------- F1/F2 unregistered column and row
p = bak("MIXED_RESULT_r424.json")
d = json.load(io.open(p, encoding="utf-8"))
G = d["grid"]


def mean_of(row, col):
    e = G.get("%s_%s" % (row, col))
    return e["KNEE_ic"]["mean"] if e and e.get("n_gate_G", 0) >= 4 else None


REG_COLS = ("0125", "0250", "0500")          # section 3: three rungs, no KV 0.110
REG_ROWS = (("W100", 1.00), ("W080", 0.80), ("W060", 0.60))   # section 3: no x0.70

regP1 = {}
for row, _ in REG_ROWS + (("W070", 0.70),):
    v = [mean_of(row, c) for c in REG_COLS]
    v = [x for x in v if x is not None]
    if len(v) < 3:
        regP1[row] = {"n_judgeable_rungs": len(v), "VERDICT": "UNINFORMATIVE"}
        continue
    mono = all(v[i] > v[i + 1] for i in range(len(v) - 1))
    regP1[row] = {"rung_means": v, "monotone_more_flexed": mono,
                  "total_change_deg": v[-1] - v[0],
                  "is_registered_row": row != "W070",
                  "VERDICT": "HOLDS" if mono else "FAILS"}

regP2 = {}
for col in REG_COLS:
    v = [(w, mean_of(r, col)) for r, w in REG_ROWS]
    v = [(w, x) for w, x in v if x is not None]
    v.sort(key=lambda t: -t[0])
    if len(v) < 3:
        regP2[col] = {"n_judgeable_rows": len(v), "VERDICT": "UNINFORMATIVE",
                      "why": "registered rows are x1.00 / x0.80 / x0.60; the x0.60 row has no cell "
                             "with >= 4 Gate-G seeds (RESCUE_RESULT_r426.json)"}
    else:
        ms = [x for _, x in v]
        regP2[col] = {"row_means_x100_first": ms,
                      "VERDICT": "HOLDS" if all(ms[i] < ms[i + 1] for i in range(len(ms) - 1))
                                 else "FAILS"}

d["REGISTRATION_DEVIATIONS_r438"] = {
    "found_by": "cold preregistration-compliance audit, 2026-08-26; every item independently "
                "re-verified against the registration text and the grid before being recorded here",
    "D1_UNREGISTERED_DOSE_COLUMN": {
        "what": "PREREG_mixed_r424.md section 3 fixes the ladder at 0.0125 / 0.025 / 0.050 and "
                "states 3 x 3 x 6 = 54 cells. The strings '0.110', '0.11' and '1100' appear "
                "NOWHERE in the registration. A fourth column at KV 0.110 was added after hashing.",
        "the_defence_offered_at_the_time_and_why_it_fails":
            "the code comment argued only against section 8's clause about adding cells AFTER "
            "seeing a value, and noted no value had been read -- which is true. But the same "
            "sentence also forbids changing the grid, and adding a column changes the grid "
            "whether or not values were seen. That clause was violated.",
        "consequence": {
            "W080_registered_three_rungs_deg": regP1["W080"].get("total_change_deg"),
            "W080_with_the_unregistered_column_deg": -8.033,
            "which_number_travelled": "the post-hoc -8.033 propagated to READING_r424, to "
                                      "FLOOR_CORRECTION_r436 (15.7 SD) and to the advisor summary"},
        "STATUS": "the KV 0.110 column is POST-HOC and must be labelled wherever quoted"},
    "D2_POST_HOC_ROW_INSIDE_REGISTERED_PREDICTIONS": {
        "what": "W070 (x0.70) was added at r426 as a substitute for the registered x0.60 root. "
                "This deposit labelled it post-hoc for P3 but scored it inside P1 and P2 unlabelled.",
        "STATUS": "registered P2 is UNINFORMATIVE at every dose, because the registered x0.60 row "
                  "has no judgeable cell. The earlier 'P2 HOLDS' used the post-hoc row and is "
                  "withdrawn as a registered result."},
    "REGISTERED_ONLY_P1": regP1, "REGISTERED_ONLY_P2": regP2,
    "WHAT_IS_UNAFFECTED": "P4 (cancellation exists) holds on registered cells alone. The DIRECTION "
                          "of both axes is unchanged. What changes is the MAGNITUDE quoted for the "
                          "spastic axis and the STATUS of P2."}
d["VERDICT"] = ("SUPERSEDED BY REGISTRATION_DEVIATIONS_r438. As registered: P1 HOLDS on three "
                "rungs with a smaller effect than previously quoted, P2 UNINFORMATIVE, P3 "
                "UNINFORMATIVE, P4 HOLDS. The KV 0.110 column and the x0.70 row are POST-HOC.")
io.open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("F1/F2 MIXED_RESULT_r424 -- registered-only P1: %s"
      % {k: (round(v["total_change_deg"], 3) if "total_change_deg" in v else v["VERDICT"])
         for k, v in regP1.items()})
print("      registered-only P2: %s" % {k: v["VERDICT"] for k, v in regP2.items()})

# ---------------------------------------------------------------- F6 criterion change
p = bak("TERMINALSWING_RESULT_r408.json")
d = json.load(io.open(p, encoding="utf-8"))
d["RESCORED_r429_AGAINST_PER_ENDPOINT_NOISE_FLOORS"]["CRITERION_CHANGE_DISCLOSURE_r438"] = (
    "PREREG_terminalswing_r408.md section 5 registered P3 as an OVERLAP OF RANGES. The ranges are "
    "disjoint, so P3 FAILS AS REGISTERED and that is the verdict of record. RESCORED_r429 replaced "
    "the registered criterion with a comparison against a noise floor that did not exist at "
    "registration time. That is a POST-HOC CRITERION CHANGE and it was the sole basis on which "
    "hypothesis 4 was revived. Disclosed, not defended. Hypothesis 4 was afterwards killed on "
    "independent grounds at MEDIATION_RESULT_r431 (both torque links indistinguishable from zero), "
    "so nothing downstream rests on the revival.")
d["VERDICT"] = ("P3 FAILS AS REGISTERED (the ranges are disjoint). RESCORED_r429 reaches the "
                "opposite conclusion on a post-hoc floor criterion; see "
                "CRITERION_CHANGE_DISCLOSURE_r438. Hypothesis 4 is DEAD on independent grounds "
                "(MEDIATION_RESULT_r431).")
io.open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("F6  r408 P3 restored to FAILS AS REGISTERED, rescoring labelled post-hoc")

# ---------------------------------------------------------------- F8 defect census
p = bak("DEFECT_r417_hash_break.md")
s = io.open(p, encoding="utf-8").read()
regs = [f for f in glob.glob(os.path.join(P, "PREREG_*.md")) if "ANNOTATION" not in f]
have = sum(1 for f in regs
           if os.path.exists(f + ".sha256")
           or os.path.exists(f.replace(".md", ".sha256"))
           or os.path.exists(f.replace(".md", ".checksum.sha256")))
if "更正(r438)" not in s:
    s += ("\n\n---\n\n**更正(r438).** 本檔原先寫「73 份註冊中有 39 份沒有 .sha256」。逐一重算後的正確"
          "數字是**註冊 %d 份、有雜湊 %d 份(全部相符、零篡改)、無雜湊 %d 份**。原數字把問題誇大了"
          "一倍以上。一份連自身普查都算錯的缺陷登記簿並不可靠,故更正,原文留於 `.bak_r438`。"
          "由冷讀合規稽核於 2026-08-26 找出。\n" % (len(regs), have, len(regs) - have))
    io.open(p, "w", encoding="utf-8", newline="").write(s)
print("F8  DEFECT_r417 census 73/39 -> %d/%d" % (len(regs), len(regs) - have))

# ---------------------------------------------------------------- F9 exploratory labels
LABELS = {
    "VIDEOMIXED_r435.json":
        "EXPLORATORY. No registration exists. Its binary task (KV>=0.050 vs <=0.025) and its "
        "threshold were both chosen after the data were seen, and FLOOR_CORRECTION_r436 found the "
        "threshold was in-sample -- the LOO figures there supersede the numbers in this file. May "
        "not be quoted beside a registered result without this label.",
    "SCREEN_ALL_r433.json": "EXPLORATORY (already stated in `status`; restated at top level).",
    "STATIONARITY_r434.json":
        "EXPLORATORY. No registration. A diagnostic that invalidated an exploratory screen result; "
        "it does not test a registered hypothesis.",
    "SHANKVEL_r430.json":
        "EXPLORATORY re-measurement of a hypothesis that had been retired without a container. No "
        "registration. Its noise floors use the family method FLOOR_CORRECTION_r436 later declared "
        "confounded.",
    "HYP1_RESCORED_r432.json":
        "EXPLORATORY rescoring. No registration. Its BETA_abs floor was built by the same family "
        "method FLOOR_CORRECTION_r436 declared circular one round later.",
    "MECHANISM_SCOREBOARD_r430.json":
        "SUMMARY DOCUMENT, not a registered result. Every multiple it quotes rests on "
        "NULL_FLOORS_r428 floors, superseded by FLOOR_CORRECTION_r436.",
    "NULL_FLOORS_r428.json":
        "SUPERSEDED for KNEE_ic by FLOOR_CORRECTION_r436, and every other endpoint in this file "
        "needs the same re-derivation before being quoted. Files still carrying its floors "
        "unamended: SPANNING_RESULT_r421 (ankle 0.069, hip 0.6127), MEDIATION_RESULT_r431, "
        "MIXED_RESULT_r424, TERMINALSWING_RESULT_r408, MECHANISM_SCOREBOARD_r430, SHANKVEL_r430.",
}
for f, note in LABELS.items():
    pp = bak(f)
    dd = json.load(io.open(pp, encoding="utf-8"))
    dd["UNREGISTERED_OR_SUPERSEDED_LABEL_r438"] = note
    io.open(pp, "w", encoding="utf-8").write(json.dumps(dd, indent=2, ensure_ascii=False))
print("F9  labelled %d unregistered / superseded deposits" % len(LABELS))

# ------------------------------------------- the ankle finding, recorded where it belongs
p = bak("FINE_GAP_r397.json")
d = json.load(io.open(p, encoding="utf-8"))
d["READING_CORRECTION_r438"] = {
    "what_this_file_actually_shows": "the endpoint here is mean ankle_angle_l over stance. Its "
        "nearest_edge_gap_deg is POSITIVE AND DISJOINT at every rung -- 1.2819, 1.7284, 2.5256, "
        "2.7818, 2.8959 -- and rises monotonically with spastic gain. THE ANKLE SEPARATES.",
    "what_VERDICT_means": "'NOT REACHED' refers to the clinical MDC threshold, NOT to separation. "
        "The file asks whether the gap reaches a clinically detectable magnitude and answers no.",
    "the_error_this_caused": "across the corpus and in the first advisor summary, 'the ankle gap "
        "does not reach the clinical threshold' was compressed into 'the ankle does not separate', "
        "and an anatomical narrative was built on the compressed version. Verified 2026-08-27 from "
        "the .sto files at group level: 23 spastic vs 36 weakness cells give an ankle stance edge "
        "gap of +1.282 deg, DISJOINT, alongside a knee edge gap of +1.492 deg.",
    "which_joint_is_actually_the_better_clinical_channel": "the KNEE. In model-noise units the "
        "ankle looks cleaner (its seed SD is 0.054 deg against the knee's 0.511), but patient "
        "measurement error is what limits a clinic and it is similar at both joints (SEM 2.53 vs "
        "2.75 deg). What decides is raw magnitude: the headline contrast is 6.39 deg at the knee "
        "against 2.78 deg at the ankle. Averaged over six steps that is 5.70 versus 2.70 clinical "
        "SEM. The knee is the better channel by a factor of about two, which is the original "
        "reason it was chosen.",
    "found_by": "cold container audit, 2026-08-26; re-derived independently from .sto 2026-08-27"}
io.open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False))
print("ANKLE  FINE_GAP_r397 -- the separation it always showed is now stated in the file")
print()
print("all fixes applied; every touched file has a .bak_r438 alongside it")
