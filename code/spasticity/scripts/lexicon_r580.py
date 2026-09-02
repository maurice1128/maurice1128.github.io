# -*- coding: utf-8 -*-
"""r580: replace the private lexicon with the field's own words.

Four published papers in this area were searched for the terms this manuscript relies on. Across
Jansen 2014, Ong 2019, Mendes-Andrade 2025 and Kesar 2011, the words readout, cell, arm, ladder,
rung, corpus, gate, floor and leakage occur zero times. What those papers use instead: simulation and
case for a single run (Ong 85 and 40 uses), condition for a level of a manipulated variable, gait
variable and kinematic variable for a candidate measure, threshold for a cut-off, and minimal
detectable change or standard error of measurement for a measurement error.

A blind reader judged cell, corpus, leakage and the software sense of binding as not understood on
first encounter, and arm and gate as actively confusing here: arm collides with limb in a paper about
the lower limb, and gate is a homophone of gait. family and lineage were added to that list as
evolutionary metaphors for what are optimisation chains.

The replacements below are context-aware. "cell" survives where it means a cell of the factorial
grid, which is standard usage; it is replaced where it meant one simulation run.
"""
import io, re, shutil

FILES = [r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md",
         r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"]
for i, f in enumerate(FILES):
    shutil.copyfile(f, f.replace("MANUSCRIPT", ".bak_r104_MANUSCRIPT").replace(
        "SUPPLEMENT", ".bak_r105_SUPPLEMENT"))

SUB = [
    # --- lineage and family: optimisation chains and the conditions they realise
    (r"\bone control lineage\b", "one control chain"),
    (r"\bcontrol lineage\b", "control chain"),
    (r"\bwithin-lineage\b", "within-condition"),
    (r"\blineage-seed\b", "chain-seed"),
    (r"\blineage labels\b", "condition labels"),
    (r"\blineages\b", "chains"),
    (r"\blineage\b", "chain"),
    (r"\blesion families\b", "lesion conditions"),
    (r"\bhyperreflexia families\b", "hyperreflexia conditions"),
    (r"\bweakness families\b", "weakness conditions"),
    (r"\bfamily means\b", "condition means"),
    (r"\bfamily-level\b", "condition-level"),
    (r"\bfamily level\b", "condition level"),
    (r"\bper-family\b", "per-condition"),
    (r"\bbetween-family\b", "between-condition"),
    (r"\bwithin-family\b", "within-condition"),
    (r"\bleave-one-family-out\b", "leave-one-condition-out"),
    (r"\bfamilies\b", "conditions"),
    (r"\bfamily\b", "condition"),

    # --- arm: a lesion group, not a trial arm, in a paper about the lower limb
    (r"\bthe two arms'\b", "the two groups'"),
    (r"\bthe two arms\b", "the two groups"),
    (r"\bhyperreflexia arm\b", "hyperreflexia group"),
    (r"\bweakness arm\b", "weakness group"),
    (r"\bcontrol arm\b", "control group"),
    (r"\barm difference\b", "group difference"),
    (r"\barm comparison\b", "group comparison"),
    (r"\barm gap\b", "group gap"),
    (r"\bper arm\b", "per group"),
    (r"\barms\b", "groups"),
    (r"\barm\b", "group"),

    # --- readout: a candidate kinematic variable
    (r"\bcandidate readouts\b", "candidate variables"),
    (r"\breadouts\b", "variables"),
    (r"\breadout\b", "variable"),

    # --- gate: an inclusion criterion, and a homophone of gait
    (r"\badmissibility gate\b", "admissibility criterion"),
    (r"\bGate G\b", "criterion G"),
    (r"\bgate G\b", "criterion G"),
    (r"\bthe gate\b", "the criterion"),

    # --- leakage: crosstalk to the unlesioned side
    (r"\bunlesioned-side leakage\b", "contralateral displacement"),
    (r"\bleaks less\b", "displaces the unlesioned side less"),

    # --- bar: a threshold
    (r"\bclear two bars\b", "clear two criteria"),
    (r"\bthree defensible bars\b", "three defensible thresholds"),
    (r"\bmeasurement-error bars\b", "measurement-error thresholds"),
    (r"\bthe 0\.8 bar\b", "the 0.8 criterion"),
    (r"\bfour-seed bar\b", "four-seed criterion"),
    (r"\bseed bar\b", "seed criterion"),
    (r"\bthe bar\b", "the threshold"),
    (r"\ba bar\b", "a threshold"),
    (r"\bbars\b", "thresholds"),

    # --- cell: one simulation run, except where it is a cell of the factorial grid
    (r"\bcell-level\b", "run-level"),
    (r"\bwithin-cell\b", "within-condition"),
    (r"\bleave-one-cell-out\b", "leave-one-run-out"),
    (r"\bcontrol cells\b", "control runs"),
    (r"\bhyperreflexia cells\b", "hyperreflexia runs"),
    (r"\bweakness cells\b", "weakness runs"),
    (r"\bfaller cells\b", "faller runs"),
    (r"\badmitted cells\b", "admitted runs"),
    (r"\blesion cells\b", "lesion runs"),
    (r"\bA cell is one lesion run under one optimisation seed\b",
     "A run is one lesioned simulation under one optimisation seed"),
]

for f in FILES:
    s = io.open(f, encoding="utf-8").read()
    tot = 0
    for pat, new in SUB:
        s, k = re.subn(pat, new, s)
        tot += k
    io.open(f, "w", encoding="utf-8", newline="").write(s)
    print("%-26s %4d substitutions" % (f.split("\\")[-1], tot))
