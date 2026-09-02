# -*- coding: utf-8 -*-
"""r553: third batch of round-four council repairs."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r65_MANUSCRIPT"))
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


# --- abstract: the counts are a range, and the weakness claims carry their tested range
rep(u"""The asymmetry runs through the whole scan: 25 of the 81 candidates grade calf overactivity
usably and 3 grade weakness, each of those 3 responding 1.8 to 2.7 times more strongly to tone at the
same phase. With both lesions present no estimator blind to the tone recovers weakness, because the
weakness signal reverses direction across the reflex range.""",
u"""The asymmetry runs through the whole scan, though its size depends on how it is scored: crossing
three defensible measurement-error bars with three rank conventions, 14 to 28 of the 81 candidates
grade calf overactivity usably against 1 to 7 for weakness, a ratio between 3.7 and 14 that never
inverts. Under the study's own motion-capture noise model the weakness count falls to zero. With both
lesions present, over the \u00d70.80 to \u00d70.95 dorsiflexor range tested, no estimator blind to the tone
recovers weakness, because the weakness signal reverses direction between the two lowest reflex
gains.""")
rep(u"""both magnitudes are known here and in no patient, the reading grades calf overactivity and not
its mechanism, the two ladders differ in survival and in severity, and one patient cohort reports an
association with dorsiflexor force inside the range this model calls faint.""",
u"""both magnitudes are known here and in no patient, the reading grades calf overactivity and not its
mechanism, the two ladders differ in survival and in severity and the weakness ladder stops at \u00d70.80
where patients reach far lower, and one patient cohort reports an association with dorsiflexor force
of the size this model calls faint.""")

# --- the Welch interval used a hard-coded critical value for df 4
rep(u"""At the family level the difference is +9.117\u00b0 (95 per cent CI [6.985, 11.249], Welch, df 4.12),""",
    u"""At the family level the difference is +9.117\u00b0 (95 per cent CI [7.008, 11.226], Welch, df 4.12),""")

# --- rounding
rep(u"""calibration error of 0.0063 in delivered gain, 4.5 per cent of the ladder's width.""",
    u"""calibration error of 0.0062 in delivered gain, 4.5 per cent of the ladder's width.""")

# --- the rectification comparator was the control arm, the conclusion is about the arm difference
rep(u"""At 3\u00b0 of per-frame jitter the reading is biased upward by 5.260\u00b0 in the hyperreflexia arm
against 3.897\u00b0 in the control arm, compressing the arm difference from 8.731 to 7.431\u00b0,""",
    u"""At 3\u00b0 of per-frame jitter the reading is biased upward by 5.260\u00b0 in the hyperreflexia arm
against 3.960\u00b0 in the weakness arm, which is the pair that sets the arm difference, compressing it
from 8.731 to 7.431\u00b0 (the control arm's bias, 3.897\u00b0, is close to the weakness arm's and is what
Fig. 5 plots),""")

# --- the pooled duration slope is deposited and never named
rep(u"""The honest reading of the regression is 0.30 \u00b1 0.74\u00b0, or 3 \u00b1 9 per cent.""",
    u"""The honest reading of the regression is 0.30 \u00b1 0.74\u00b0 at one standard error, or 0.30 \u00b1 2.06\u00b0 at
95 per cent on five families, which is 3 \u00b1 24 per cent of the effect. One alternative estimator
deserves naming because it is deposited with the rest and is far larger: pooling all cells across
both arms rather than fitting within families gives 1.101 \u00b0\u00b7s\u207b\u00b9, which propagates 8.02\u00b0 or 92 per cent
of the effect. That figure is circular, because pooling across arms recovers the arm difference the
regression is meant to test, and we do not use it. A reader should know it exists and why it is not
the number reported.""")

# --- the control ankle is normal in phase and not in value
rep(u"""We take the endpoint in swing because that is the one place the model's ankle behaves as a normal""",
    u"""We take the endpoint in swing because that is the one place the phase of the model's ankle matches
a normal one. Its value there does not: the unlesioned peak is 9.56\u00b0 where a normal swing peak is 0
to 5\u00b0, which is discussed in \u00a74.5 and bears on every displacement measured from this control. What
holds in swing and nowhere else is that the model's ankle moves as a normal""")

# --- the cohort supplying the between-patient SD excluded braced walkers
rep(u"""That figure, 5.55\u00b0, is
computed here from the two subgroup means and SDs and is not reported in [5].""",
u"""That figure, 5.55\u00b0, is computed here from the two
subgroup means and SDs, assuming the two subgroups are of equal size, and is not reported in [5]. The
cohort it comes from excluded 67 of 116 screened patients for walking with an orthosis or a walking
device, so it is the aid-free tail of the spastic population and probably its mildest. That cuts both
ways: a wider cohort would raise the denominator and lower *d*, and it is also the population in
which a barefoot recording of this variable is possible at all.""")

# --- the lesioned calf is at full strength
rep(u"""scaling of `tib_ant_l` maximum isometric force from its base 1759 N.""",
    u"""scaling of `tib_ant_l` maximum isometric force from its base 1759 N, at \u00d70.80, \u00d70.87, \u00d70.892,
\u00d70.90, \u00d70.915 and \u00d70.95. The two lesions are imposed separately, so the hyperreflexia arm carries a
calf at full strength. No hemiparetic calf is: [4] reports affected plantarflexor manual muscle test
4 against 5, and [1] describes a lack of push-off from triceps surae weakness. \u00a74.5 returns to this.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("edits applied: %d" % n[0])
