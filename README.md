# Mu-Hua (Maurice) Wang — academic website

Static site for graduate-school applications. No build step: plain HTML, one shared
stylesheet, and assets as files.

```
index.html              homepage — research interest, five projects, systems, publications
cv.html                 full CV
css/style.css           shared design system (light + dark, three-state theme)
projects/
  motor-prior.html      Two Routes to a Motor Prior
  hand-composition.html Which Hand-Motion Composition Axes Are Worth Measuring
  body-codes.html       What Master-Then-Reorganise Does Not Buy
  capture-error.html    How Much Joint-Angle Error Can Identification Tolerate?
  spasticity.html       Hyperreflexia vs dorsiflexor weakness
assets/<project>/       figures, videos and the one released PDF
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

Also: nothing here is a preprint, none of this is on arXiv, and no public code repository
exists yet. Do not add wording that implies otherwise.
