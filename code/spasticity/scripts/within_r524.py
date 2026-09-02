# -*- coding: utf-8 -*-
"""r524: the only design in which this readout could work on one patient, and what it would cost.

Section 3.5 shows the readout cannot ASSIGN a lesion class to one patient, because the spread a
stroke population presents at this landmark is larger than either lesion moves it. That verdict is
specific to a cross-sectional reading. A within-patient design -- the same limb before and after a
diagnostic block or a toxin injection -- cancels the between-patient spread entirely and leaves only
measurement error, and it is the design a clinician would actually run. This asks whether the change
such a design would have to detect is larger than the noise, and if not, how many sessions it takes.

A change threshold is the correct statistic HERE: the question is whether one patient CHANGED, which
is what the statistic was built for. Section 3.5 rejects it for the assignment question, not for this
one.
"""
import io, json, math, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
L = json.load(io.open(os.path.join(P, "LIMBDIFF_r521.json"), encoding="utf-8"))["per_cell"]

# knee at contact, lesioned side, by delivered gain -- the within-lineage dose response is the
# simulation's analogue of reducing one patient's plantarflexor tone
by = {}
for c in L:
    if c["arm"] == "hyper":
        by.setdefault(round(c["kv"], 3), []).append(c["L"])
rungs = sorted(by)
mean = {k: sum(v) / len(v) for k, v in by.items()}
print("knee at contact by delivered gain (hyperreflexia arm):")
for k in rungs:
    print("   KV %.3f   %8.3f deg   (n=%d)" % (k, mean[k], len(by[k])))

full = mean[rungs[0]] - mean[rungs[-1]]          # top rung relaxed to bottom rung
half = mean[rungs[len(rungs) // 2]] - mean[rungs[-1]]
print("\nknee excursion recovered by relaxing the gain:")
print("   full ladder  KV %.3f -> %.3f : %+.3f deg" % (rungs[-1], rungs[0], full))
print("   half ladder  KV %.3f -> %.3f : %+.3f deg" % (rungs[-1], rungs[len(rungs) // 2], half))

SEM = 3.7041 / math.sqrt(2.0)                     # single-measurement SEM, section 3.5
print("\nsingle-measurement SEM %.3f deg" % SEM)


def sessions(target):
    """sessions per timepoint for a change of `target` to clear the 95% noise band"""
    for k in range(1, 41):
        band = 1.96 * (SEM / math.sqrt(k)) * math.sqrt(2.0)
        if band < abs(target):
            return k, band
    return None, None


rows = {}
for name, d in (("full ladder", full), ("half ladder", half)):
    k, band = sessions(d)
    band1 = 1.96 * SEM * math.sqrt(2.0)
    rows[name] = {"expected_change_deg": d, "one_session_noise_band_deg": band1,
                  "detectable_with_one_session": abs(d) > band1,
                  "sessions_per_timepoint_needed": k,
                  "noise_band_at_that_n_deg": band}
    print("   %-12s change %+.3f deg vs one-session band %.3f -> %s; needs %s sessions per timepoint"
          % (name, d, band1, "detectable" if abs(d) > band1 else "NOT detectable",
             k if k else ">40"))

dep = {
 "id": "WITHIN_r524",
 "why": ("Section 3.5's verdict is about a cross-sectional reading. The design a clinician would "
         "actually run is longitudinal -- the same limb before and after a block -- which cancels "
         "the between-patient spread and leaves only measurement error. This asks whether that "
         "design works, and at what cost."),
 "knee_at_contact_by_delivered_gain_deg": {str(k): mean[k] for k in rungs},
 "single_measurement_SEM_deg": SEM,
 "designs": rows,
 "STATISTIC_NOTE": ("A change threshold is used here and is the right statistic for this question: "
                    "it asks whether one patient changed, which is what it was built for. Section "
                    "3.5 rejects it for the assignment question, which it was not built for."),
 "READING": ("Relaxing the reflex gain across the full ladder recovers %.2f degrees of knee "
             "extension at contact. A single session either side of a block carries a 95 per cent "
             "noise band of %.2f degrees, so one session either side cannot see it. It takes %s "
             "sessions at each timepoint for the expected change to clear the band. That is the "
             "answer to whether this readout could serve a clinician on one patient in the design "
             "where the population spread does not apply: not in one visit, and not in a number of "
             "visits a clinic would run." % (full, 1.96 * SEM * math.sqrt(2.0),
                                             rows["full ladder"]["sessions_per_timepoint_needed"])),
}
io.open(os.path.join(P, "WITHIN_r524.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> WITHIN_r524.json")
