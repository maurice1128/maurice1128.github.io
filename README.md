# Mu-Hua (Maurice) Wang — academic website

Static site for graduate-school applications, served by GitHub Pages from `main`.
Plain HTML, one shared stylesheet, assets as files.

```
index.html              homepage. The Research and Manuscripts blocks are generated.
cv.html                 web CV
css/style.css           shared design system (light + dark)
projects/<slug>.html    one page per project
assets/<slug>/          that project's figures, videos and paper PDF
assets/papers/          PDFs of published conference papers
assets/systems/, cv/    homepage and CV assets
```

The homepage entries are generated from one JSON card per project, kept outside this
repository together with the build script and the editing rules. Do not edit the text between
the `BEGIN:` / `END:` markers in `index.html` by hand.

## Rules that must not be relaxed

1. Every number on a page traces to a stored run artifact or a table in the manuscript.
2. A non-significant result is "not detected at this power", never "absent" or "equal".
3. Status wording (draft, submitted, under review, accepted) matches the evidence held for it.
   Nothing is described as a preprint unless it is posted to a preprint server.
4. Every project states its scope: where the result stops.
