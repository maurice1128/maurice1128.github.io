# -*- coding: utf-8 -*-
"""r560: consistency sweep. Stale counts survived in 4.1 and 5 because the guard matched one wording."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
F = r"C:\Users\maurice\Desktop\spasticity_paper\scone\selfcheck_r541.py"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r73_MANUSCRIPT"))
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:56]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


# --- 4.1: stale counts, and it restates what 5 says; compress while correcting
rep(u"""The two halves of the result are one finding. Plantarflexor overactivity is legible across a third
of the sagittal readouts a gait laboratory produces; dorsiflexor weakness, over the range this model
can walk with, is legible in an eighth as many places and at 0.37 to 0.55 of the amplitude where it
is legible at all. A gait recording therefore grades one component of a spastic equinovarus foot
well and the other faintly and unreliably, and the difference is not an instrumental limitation that
a better laboratory would remove.""",
u"""The two halves of the result are one finding. Plantarflexor overactivity is legible over between a
sixth and a third of the sagittal readouts a gait laboratory produces, and dorsiflexor weakness, over
the range this model can walk with, over a fraction of that: between a quarter and a fourteenth as
many places depending on how the count is scored (\u00a73.4), and at 0.37 to 0.55 of the amplitude where
it is legible at all. A gait recording grades one component of a spastic equinovarus foot well and
the other faintly, and the difference is not an instrumental limitation a better laboratory would
remove.""")

# --- 4.1: the sample-size arithmetic belongs with the study design in 4.4
rep(u"""A correlational study
of the size proposed in \u00a74.4 therefore needs roughly a sixth the sample at the ankle that it would
need at the knee, the two *d* values corresponding to correlations of 0.60 and 0.28 whose Fisher
transforms stand at 0.693 and 0.291. On that arithmetic the choice of instant decides whether the
patient study is affordable. These data support measuring the ankle in swing instead of at contact;
they do not support moving from the ankle to the knee.""",
u"""A correlational study of the size proposed in \u00a74.4 therefore
needs roughly a sixth the sample at the ankle that it would need at the knee, so the choice of
instant decides whether the patient study is affordable. These data support measuring the ankle in
swing instead of at contact; they do not support moving from the ankle to the knee.""")

# --- 5: stale counts and the missing noise result
rep(u"""The same corpus sets the bound. Of 81 candidate sagittal readouts, 25 grade the reflex usably and
three grade dorsiflexor weakness, and each of those three responds 1.8 to 2.7 times more strongly to
tone at the same phase. Where both lesions are present, no readout and no combination we tested
recovers how weak the dorsiflexors are without first knowing the tone, because the weakness signal
is locally strong but reverses direction across the reflex range. One two-stage estimator was tested: grading gain from
the ankle recovers it at R\u00b2 = 0.95, but reading weakness off the knee residual afterwards recovers
only R\u00b2 = 0.13. What that leaves open is the sign-appropriate variant, which applies a different
weakness relation on each side of the reversal and which we did not test. The apportionment a clinician needs is half-answerable from
gait, and the other half requires a strength measurement gait cannot supply.""",
u"""The same corpus sets the bound. Of 81 candidate sagittal readouts, between 14 and 28 grade the reflex
usably against 1 to 7 for dorsiflexor weakness, depending on which published measurement error is
used as the bar and whether the rank correlation handles ties; the ratio lies between 3.7 and 14 and
never inverts, and under this study's own motion-capture noise model the weakness count falls to
zero. Each readout that does grade weakness responds 1.8 to 2.7 times more strongly to tone at the
same phase. Where both lesions are present, no readout and no combination we tested recovers how weak
the dorsiflexors are without first knowing the tone, because the weakness signal is locally strong
but reverses direction between the two lowest gains on the grid. One two-stage estimator was tested:
grading gain from the ankle recovers it at R\u00b2 = 0.95, but reading weakness off the knee residual
afterwards recovers only R\u00b2 = 0.13. What that leaves open is the sign-appropriate variant, which
applies a different weakness relation on each side of the reversal. The apportionment a clinician
needs is half-answerable from gait, and the other half requires a strength measurement gait cannot
supply.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)

# --- widen the guard so a reworded stale count cannot pass again
c = io.open(F, encoding="utf-8").read()
c = c.replace('forbid(r"written in an eighth as many places",',
              'forbid(r"(written|legible) in an eighth as many|\\b25 grade the reflex|three grade dorsiflexor weakness",')
c = c.replace('forbid(r"only two of the 81 variables|published between-session errors exist for only two",',
              'forbid(r"only two of the 81 variables|published between-session errors exist for only two|'
              'legible across a third of the sagittal",')
io.open(F, "w", encoding="utf-8", newline="").write(c)
print("edits applied: %d;  guards widened" % n[0])
