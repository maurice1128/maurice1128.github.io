# -*- coding: utf-8 -*-
"""r594: 2.5, 3.7 and the Conclusions to the length their comparators run to."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r132_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()


def swap(start, stop, new, label):
    global s
    i, j = s.index(start), s.index(stop)
    old = s[i:j]
    s = s[:i] + new + s[j:]
    print("%-16s %4d -> %4d" % (label, len(old.split()), len(new.split())))


swap("### 2.5 Preregistration", "## 3. Results", u"""### 2.5 Preregistration

We registered the analysis of the mixed grid before reading its results, and that registration does
not certify what we report here. Of its four predictions two are uninformative as registered, one was
made at an endpoint this paper does not use, and one, P4, is tested in \u00a73.7; two grid elements
entered afterwards and are marked where they are used. Of 72 registrations, 55 carry a hash sidecar
and all 55 still hash to it, and the remaining 17 were never hashed, which is a coverage gap and not
a tampering signal. One registration, `PREREG_2ndbody_r229.md`, was edited after its results were
produced in order to restore four outcome levels, so the version the run executed is unrecoverable.
We report the registration as a record of what was planned and not as assurance about any result, and
a reader should treat every analysis here as exploratory. Supplement S7 gives the four predictions in
full, the audit of all 97 deposited sidecars, and the post hoc elements.

""", "2.5")

swap("### 3.7 The registered prediction", "### 3.8 Localisation", u"""### 3.7 The registered prediction, tested at both endpoints (Fig. 4)

The registered prediction that bears on apportionment was made at the contact instant, and it held
there. It predicted that different lesion combinations would produce overlapping readings, and at the
knee they do: among the six pairs the registration covers, the closest two differ by 0.302\u00b0, less
than that endpoint's artefact floor, so two limbs with different amounts of each lesion read the same.
At peak swing dorsiflexion the answer depends on which pairs are counted. Among the 96 pairs that
differ in reflex gain the closest differ by 0.833\u00b0, 9.3 times that endpoint's grid floor of 0.089\u00b0,
but of the 24 that hold gain fixed and vary dorsiflexor strength alone, four fall below the floor and
the closest at 0.044\u00b0. The endpoint therefore does not separate two limbs whose calves are equally
overactive and whose dorsiflexors differ, which is \u00a73.4's asymmetry restated one pair at a time; the
earlier claim that no pair falls within one seed SD is withdrawn.

The two endpoints differ in resolution and not in excursion. Over the grid's gain range of 0.025 to
0.220 the gain axis moves the swing peak by 8.210\u00b0 and the contact knee by 8.113\u00b0, on noise floors
differing about sixfold, and neither endpoint rescues the weakness axis (\u00a73.4). Supplement S2 gives
the dose response, the sub-phase sign reversal at the knee, and the difference in the two populations
of pairs.

""", "3.7")

swap("## 5. Conclusions", "\n---\n\n## Figures", u"""## 5. Conclusions

Peak ankle dorsiflexion during swing separates plantarflexor hyperreflexia from dorsiflexor weakness
completely at the run level and grades the reflex at \u03c1 = \u22121.000 across the five gain levels, and it
does both under a simulated motion-capture error that leaves knee angle at contact substantially
degraded. Gait laboratories already record the variable, so what this study offers is its calibration
rather than a new measurement. Both figures are the maximum of an 81-candidate scan and so an upper
estimate of what a pre-specified choice would have found.

The same dataset sets the bound. Of the 81 candidates, between 14 and 28 grade the reflex usably
against 1 to 7 for dorsiflexor weakness, a ratio that stays between 3.7 and 14 and never inverts, and
under this study's own noise model the weakness count falls to zero. Where both lesions are present,
no variable and no combination we tested recovers how weak the dorsiflexors are without first knowing
the tone, because the weakness signal reverses direction across the gain range. Half the apportionment
a clinician needs is answerable from gait; the other half requires a strength measurement gait cannot
supply.

None of the simulation-side figures is a clinical accuracy. Against the spread a chronic stroke cohort
presents at this landmark the same effect misassigns about one reading in four, a figure that already
contains a single measurement's error and rests on the model's 8.731\u00b0 transferring unchanged to
patients. Better instrumentation would not reduce it, because the limit is set by the spread between
patients. Whether it improves on what a clinician achieves unaided is a comparison nobody has made,
and the one study setting clinical assessment against diagnostic nerve block found the clinical data
unassociated with the instrumented findings [3].

Both lesion magnitudes are known here and in no patient. The reading grades calf overactivity and not
the mechanism producing it [3, 26]. The hyperreflexia group falls before the horizon while the
weakness group reaches only \u00d70.80, against a population whose median dorsiflexor manual muscle test is
1 of 5 [4], so the two series are matched neither in survival nor in severity. And the insensitivity
to weakness holds where walking speed is nearly matched: across the range a stroke cohort walks at,
the indirect path from weakness through speed to the endpoint is about 0.23\u00b0, comparable to the entire
direct effect of 0.430\u00b0.

Within those conditions this delivers a calibration of an existing measurement, a bound on what any
sagittal angle can carry, and a patient study whose second predictor is now known to be necessary
rather than merely prudent. These results do not support using the variable as an absolute measure of
tone in an individual patient.
""", "Conclusions")

io.open(P, "w", encoding="utf-8", newline="").write(s)
b = s[s.index("## 1. Background"):s.index("## Figures")]
print("body %d" % len(b.split()))
