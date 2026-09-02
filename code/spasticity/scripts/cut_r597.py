# -*- coding: utf-8 -*-
"""r597: Methods, 3.6 and 3.8 to length. Corpus accounting and the noise model's limits move to S6 and S1."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r137_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r138_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()


def swap(a, b, new, lab):
    global s
    i, j = s.index(a), s.index(b)
    old = s[i:j]
    s = s[:i] + new + s[j:]
    print("%-10s %4d -> %4d" % (lab, len(old.split()), len(new.split())))
    return old


i = s.index("| delivered KV |")
j = s.index("\n\n", s.index("| archived label |"))
kvtable = s[i:j]

swap("### 2.1 Model, controller", "### 2.3 Admissibility", u"""### 2.1 Model, controller, optimisation

3D model `H1922v7b3`: 19 degrees of freedom, 22 muscles, pelvis to femur to tibia to calcaneus, in
SCONE 2.4.4.3333 with Hyfydy 1.12.6.1412. A reflex controller of the Geyer and Herr type [16], their
positive and negative force and length feedback laws extended from the original planar
seven-muscles-per-leg formulation to this model's 22 muscles, with gains optimised by CMA-ES over 90
generations from a converged unlesioned parameter file, 20 s maximum duration and a 5 ms control
step, at six seeds per condition except at the two deepest reflex gains, which we ran with four.

The objective is a composite of five terms: a gait term (weight 100) with a minimum velocity of 1.0
m/s and a termination height of 0.85; cubed muscle activation (1000); metabolic effort on the Wang
2012 model as cost of transport (0.1); ground-reaction force above 1.3 body weights (10); and
joint-limit penalties on ankle and knee (0.1 each). No term rewards toe clearance, so nothing in the
objective pushes the weakness group to compensate for a dropped foot by exaggerated hip and knee
flexion; that absence follows from the objective and is not a result, and \u00a74.4 returns to it. We
re-optimised the controller for every lesion, so each analysed gait is that lesioned system's own best
solution, and reached severe conditions by warm-start chaining, seeding each severity level from the
previous level's optimum, following Ong et al. [10].

### 2.2 Lesions

**Hyperreflexia**: a `MuscleReflex` on left soleus and gastrocnemius, velocity gain KV, delay 0.020 s,
`allow_neg_V = 0`, with maximum isometric forces unchanged (soleus 3549 N, gastrocnemius 2241 N). The
velocity feedback is an addition to the Geyer\u2013Herr formulation, not one of its laws. **Weakness**:
scaling of `tib_ant_l` maximum isometric force from its base 1759 N, at \u00d70.80, \u00d70.87, \u00d70.892, \u00d70.90,
\u00d70.915 and \u00d70.95. We imposed the two lesions separately, so the hyperreflexia group carries a calf at
full strength, which no hemiparetic calf is [1, 4]; \u00a74.4 returns to this. Gains below are delivered,
measured directly in the model file as a multiplier of 2.000000 \u00b1 7 \u00d7 10\u207b\u2076 over 102 measurements, and
the archived outputs are labelled with nominal values, exactly half:

""" + kvtable + u"""

""", "2.1-2.2")

swap("### 2.3 Admissibility", "### 2.4 Analysis", u"""### 2.3 Admissibility

A run is one lesioned simulation under one optimisation seed. Criterion G requires a simulation end
time of at least 9.73 s and at least five complete gait cycles inside [1.00, 9.73] s, with the last
kept cycle dropped. Foot contact is the rising edge of `leg0_l.grf_norm_y` through 0.05, and every
angle reported at contact is the value at that sample averaged over the kept cycles, a mean of 5.3
cycles per run.

Twenty-three hyperreflexia runs, 36 weakness runs and 6 control runs pass, from five hyperreflexia
conditions, six weakness conditions and one control chain. A separate 84-cell mixed grid, 74 of them
admitted, crosses four tibialis anterior scalings with four delivered reflex gains and supports \u00a7\u00a73.4
and 3.7. Attrition falls entirely on the hyperreflexia group and is not monotone in gain: 6 of 6 at
KV 0.100 and 0.140, 4 of 6 at 0.200, 4 of 4 at 0.220 and 3 of 4 at 0.240. The earliest hyperreflexia
failure is at 9.81 s, only 0.08 s above the threshold, which makes the threshold's provenance matter;
it was fixed in registrations predating these runs by several hundred optimisation rounds. Two
protocol artefact values are used, 0.586\u00b0 for knee angle at contact and 0.036\u00b0 for peak dorsiflexion
in swing; they are not interchangeable and each is used only against its own endpoint (\u00a73.3).
Supplement S10 gives both corpora in full, including the five further lesion conditions used only as
the duration control of \u00a73.3 and the grid's registered seed criterion, and S6 the sub-phase boundaries
and the construction of the artefact.

""", "2.3")

swap("### 3.6 The measurement model", "### 3.7 The registered prediction", u"""### 3.6 The measurement model and the recording modality

The noise model behind \u00a73.5 is optimistic in four respects that Supplement S1 sets out: the jitter is
independent and Gaussian, the yaw term is inert on a planar trace, event detection is exempted by
taking the swing window from the noise-free ground reaction force where a real pipeline must estimate
it [23], and it models one recording rather than two, so the error governing a patient's reading is
the 1.77\u00b0 of \u00a73.5 and not anything in this grid.

Published sagittal errors for markerless video are, for the knee, 5.6\u00b0 MAE in unimpaired adults [21]
and 4.0\u00b0 post-stroke [22]. For the ankle, this paper's endpoint, they are worse: 7.4\u00b0 MAE with a
cross-correlation of 0.74 to 0.78 against 0.97 to 0.98 for the hip and knee [21], and 6.3 to 7.4\u00b0
post-stroke depending on limb and camera view [22], comparable to the whole 8.731\u00b0 effect and larger
than the 4.14\u00b0 tone series. Video-based pose estimation cannot support the grading proposed here, and
marker-based capture is the only modality these results transfer to.

""", "3.6")

swap("### 3.8 Localisation", "\n---\n\n## 4. Discussion", u"""### 3.8 Localisation of the separation

Because the controller is re-optimised for every lesion, the joint at which a difference appears does
not identify the muscle responsible. The unlesioned knee is displaced from control by 3.44 and 4.01\u00b0
at the two deepest gains and carries 35.5 per cent of that endpoint's group separation (\u00a73.3), so a
re-optimised body redistributes a local deficit and a single-joint reading registers the
redistribution along with it. That a distal constraint displaces proximal kinematics is not itself
surprising, since imposing equinus mechanically on unimpaired adults alters knee kinematics during
gait [19].

The reported endpoint is the least exposed to this. Its displacement of the unlesioned side is 0.5 per
cent against the knee's 35.5, both scored at the unlesioned limb's own contact (\u00a73.3), and scored
instead at the lesioned limb's contact the knee figure is 30.8 per cent while the ankle figure is
unchanged. What it registers is therefore almost entirely a lesion-side displacement, although it
grades calf overactivity as a marker and not as a direct observation of the calf. We searched for a
mechanism behind the redistribution and found none whose effect exceeds the protocol artefact; one
candidate, a left-minus-right hip asymmetry, is examined in Supplement S11 and is not reported here.

Two results do not survive as stated. The ankle-at-contact null fails two of the four decision rules
and is not certified by this design, and knee angle at contact loses lesion-side specificity at the
deeper gains where the unlesioned knee moves as well (\u00a73.3). No control here can reach a third
question, whether the separation follows from lesion type or from the lesion's effect on stability.

""", "3.8")

io.open(P, "w", encoding="utf-8", newline="").write(s)
b = s[s.index("## 1. Background"):s.index("## Figures")]
print("body %d" % len(b.split()))
