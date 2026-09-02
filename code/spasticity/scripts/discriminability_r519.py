# -*- coding: utf-8 -*-
"""r519: the statistic that actually answers 'could a clinician read one patient?'

The manuscript answers that question with a minimal detectable change, which is a criterion for
whether ONE patient CHANGED between two sessions. The question at issue is different -- whether one
patient can be ASSIGNED to a lesion class from one reading -- and its statistic is a discriminability
and the misclassification rate it implies, against the total spread a patient population presents.

Nothing here is a new measurement: it combines the effect sizes already reported with the
between-patient SDs of ref [5] and the single-measurement SEM of section 3.5.
"""
import io, json, math

SEM = 3.7041 / math.sqrt(2.0)          # single-measurement SEM implied by the change-score SD
BIO = {"7.93": 7.93, "9.16": 9.16}     # between-patient SD of knee at contact, ref [5] subgroups
EFF = {"pooled 5.280": 5.2799, "round-151 4.087": 4.0874, "dose-matched 3.420": 3.4197}
Phi = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

rows = {}
print("single-measurement SEM %.3f deg" % SEM)
for en, e in EFF.items():
    r = {"effect_deg": e,
         "d_against_measurement_error_only": e / SEM,
         "error_rate_measurement_only": Phi(-(e / SEM) / 2)}
    for bn, b in BIO.items():
        tot = math.sqrt(b * b + SEM * SEM)
        d = e / tot
        r["against_between_patient_SD_" + bn] = {"total_SD_deg": tot, "cohens_d": d,
                                                 "misclassification_rate": Phi(-d / 2)}
    rows[en] = r
    print("  %-22s d(meas only) %.2f -> %4.1f%% | d(+bio 7.93) %.2f -> %4.1f%% | d(+bio 9.16) %.2f -> %4.1f%%"
          % (en, r["d_against_measurement_error_only"], 100 * r["error_rate_measurement_only"],
             r["against_between_patient_SD_7.93"]["cohens_d"],
             100 * r["against_between_patient_SD_7.93"]["misclassification_rate"],
             r["against_between_patient_SD_9.16"]["cohens_d"],
             100 * r["against_between_patient_SD_9.16"]["misclassification_rate"]))

rel = {bn: 1.0 - SEM * SEM / (b * b) for bn, b in BIO.items()}
dep = {
 "id": "DISCRIMINABILITY_r519",
 "why": ("A minimal detectable change asks whether one patient CHANGED between sessions. The "
         "question the readout raises is whether one patient can be ASSIGNED to a lesion class from "
         "one reading. That is a discriminability, and its statistic is Cohen's d against the total "
         "spread a patient presents, with the misclassification rate it implies at the best "
         "threshold."),
 "single_measurement_SEM_deg": SEM,
 "between_patient_SD_deg": BIO,
 "by_effect_size": rows,
 "reliability_of_one_session": rel,
 "attenuation_of_a_correlation": {bn: 1.0 - math.sqrt(v) for bn, v in rel.items()},
 "READING": ("Against measurement error alone the pooled effect is 2.0 SEM and would misclassify "
             "about one reading in six. Against the spread a stroke population actually presents it "
             "is 0.6 SD and misclassifies about two in five, close to chance. The binding constraint "
             "on a per-patient reading is therefore biological, not instrumental: a perfect "
             "instrument would not fix it. For a correlational design across patients the same "
             "spread is the denominator rather than the obstacle, and measurement error costs only "
             "the attenuation above."),
}
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\DISCRIMINABILITY_r519.json", "w",
        encoding="utf-8", newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print()
for bn in BIO:
    print("  reliability of one session (SD %s): %.3f -> correlation attenuated %.1f%%"
          % (bn, rel[bn], 100 * (1 - math.sqrt(rel[bn]))))
