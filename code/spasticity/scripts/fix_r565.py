# -*- coding: utf-8 -*-
"""r565: retune the contract to the r564 wording, and fold 5's trailing qualifications into its claims."""
import io, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
F = r"C:\Users\maurice\Desktop\spasticity_paper\scone\selfcheck_r541.py"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r81_MANUSCRIPT"))

c = io.open(F, encoding="utf-8").read()
for a, b in (("admitted hyperreflexia cells of the primary corpus none reaches",
              "admitted hyperreflexia cells reaches the simulation horizon"),
             ("36 weakness cells all do", "all 36 weakness cells do")):
    assert a in c, a
    c = c.replace(a, b)
io.open(F, "w", encoding="utf-8", newline="").write(c)
print("contract retuned to the new wording")

s = io.open(P, encoding="utf-8").read()
i, j = s.index(u"## 5. Conclusions"), s.index(u"\n---\n\n## Figures")
old = s[i:j]
new = u"""## 5. Conclusions

Peak ankle dorsiflexion during swing separates plantarflexor hyperreflexia from dorsiflexor weakness
completely at the cell level and grades the reflex at \u03c1 = \u22121.000 across the five gain levels, and it
does both under a simulated motion-capture error that leaves knee angle at contact substantially
degraded on the detection and grading columns. Gait laboratories already record the variable, so what
this study offers is its calibration rather than a new measurement. Both figures are the maximum of
an 81-candidate scan and so an upper estimate of what a pre-specified choice would have found.

The same corpus sets the bound. Of the 81 candidates, between 14 and 28 grade the reflex usably
against 1 to 7 for dorsiflexor weakness, the range depending on which published measurement error
serves as the bar and whether the rank correlation handles ties; the ratio between them stays between
3.7 and 14 and never inverts, and under this study's own motion-capture noise model the weakness
count falls to zero. Each readout that does grade weakness responds 1.8 to 2.7 times more strongly to
tone at the same phase. Where both lesions are present, no readout and no combination we tested
recovers how weak the dorsiflexors are without first knowing the tone, because the weakness signal is
locally strong and reverses direction between the two lowest gains on the grid. Of the one two-stage
estimator tested, grading gain from the ankle recovers it at R\u00b2 = 0.95 and reading weakness off the
knee residual afterwards recovers R\u00b2 = 0.13; the sign-appropriate variant, applying a different
weakness relation on each side of the reversal, remains open. Half the apportionment a clinician needs
is answerable from gait, and the other half requires a strength measurement gait cannot supply.

None of the simulation-side figures is a clinical accuracy. Against the spread a chronic stroke
cohort presents at this landmark, the same effect misassigns about one reading in four, a figure that
already contains a single measurement's error and that rests on the model's 8.731\u00b0 transferring
unchanged to patients. Better instrumentation would not reduce it, because the limit is set by the
spread between patients and only faintly by the precision of the reading. Whether it improves on what
a clinician achieves unaided is a comparison nobody has made, and the one study setting clinical
assessment against diagnostic nerve block found the clinical data unassociated with the instrumented
findings [3].

Four conditions define where the result holds. Both lesion magnitudes are known here and in no
patient. The reading grades calf overactivity and not the mechanism producing it, a stretch reflex
being neither the only nor necessarily the dominant source of plantarflexor activity in swing [3, 26].
The hyperreflexia arm falls before the horizon while the weakness arm reaches only \u00d70.80, against a
population whose median dorsiflexor manual muscle test is 1 of 5 [4], so the two ladders are matched
neither in survival nor in severity. And the blindness claim holds where walking speed is nearly
matched: across the range a stroke cohort walks at, the indirect path from weakness through speed to
the endpoint is about 0.23\u00b0, comparable to the entire direct effect of 0.430\u00b0.

Within those conditions this delivers a calibration of an existing measurement, a bound on what any
sagittal angle can carry, and a patient study whose second predictor is now known to be necessary
rather than merely prudent. It does not deliver a spasticity meter.

"""
s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("5: %d -> %d words" % (len(old.split()), len(new.split())))
