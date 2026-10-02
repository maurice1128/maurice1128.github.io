# Mu-Hua (Maurice) Wang — academic website

Static site for graduate-school applications. No build step: plain HTML, one shared
stylesheet, and assets as files.

```
index.html              homepage — research interest, current work, projects, systems, publications
cv.html                 full CV (web version; the PDF CVs are withdrawn until rebuilt)
css/style.css           shared design system (light + dark, three-state theme)
projects/
  caregiving-safety-sim.html  Measuring whether a care robot hurts the patient (platform, work in progress)
  gentle-care-robot.html      Gentle by Knowing (person knowledge vs. force thresholds for robotic arm lifting)
  motor-prior.html            Withdrawn teachers and learned body models in muscle-driven motor learning
  hand-modularity.html        Learned in-betweeners make simulated dexterous hands learn faster
  hand-composition.html       Partial labels hide compositional difficulty (hand datasets, TMLR draft)
  body-codes.html             Reparameterisation invariance limits reorganising a body code
  capture-error.html          How much joint-angle error can identification tolerate?
  joint-offset.html           Joint-centre offset dominates 3D position error
  spasticity.html             Hyperreflexia vs dorsiflexor weakness
  methadone.html              Methadone dose patterns around random urine tests
  gentle-other-model.html     Superseded earlier stage of the care-robot line
assets/<project>/       figures and videos; assets/papers/ holds the manuscript PDFs
```

## Publishing to GitHub Pages

Push this folder as the repository root, then in **Settings → Pages** set
*Source: Deploy from a branch*, *Branch: `main` / `(root)`*.

`.nojekyll` is present so paths beginning with `_` are served unmodified.

## Editing rules that must not be relaxed

Each project's source folder (`../<project>/HANDOFF.md`) lists numbers that were verified
against stored run artifacts, and phrasings that earlier audits rejected. Two rules apply
to every page here:

1. **Every number must trace to that project's HANDOFF §4 (or its verified figure caption).**
   Do not round, recompute, or add a number that is not listed there.
2. **A non-significant result is "not detected at this power", never "absent" or "equal".**
   Several pages carry intervals wide enough to contain their own study's headline effect.

Also: nothing here is a preprint and none of this is on arXiv. Do not add wording that
implies otherwise. Code repositories do exist for some projects and are linked from the
pages that have one; do not claim one for a project that does not.
