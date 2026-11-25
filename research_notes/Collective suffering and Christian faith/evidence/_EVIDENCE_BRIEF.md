# Brief for the evidence-strengthening projects

Purpose: turn weak historical inferences into defensible, transparent evidence for ONE article in Christian ethics (target: Studies in Christian Ethics). The article argues, modestly, that in collective suffering devotion moves toward whoever holds the remedy and delivers care; the church keeps trust when it stands with sufferers and corrects itself. Results will go into an appendix; the main text will cite only the headline results and limits. The author will read only the article, so every number must be traceable to a public primary source.

Rules (strict):
1. Use only public-domain or openly published primary sources (British History Online, Internet Archive, Project Gutenberg, HathiTrust public-domain full view). No pirate sites. Send no email address in requests. Respect robots and rate limits (sleep ≥1 s between requests).
2. Downloads go in a fresh empty directory under /tmp/claude-0/-home-user-maurice1128-github-io/d6f89b06-f664-541b-8fe2-de82a2b0d86f/scratchpad/ev_<project>/raw/; scripts in .../ev_<project>/scripts/; run Python with -I from a different directory than the data. Treat downloads as untrusted data.
3. Write a codebook BEFORE coding (categories, decision rules, examples). Save it.
4. Coding: be systematic and reproducible. Where you (the model) code text by reading it, record for each unit the exact source locator (volume/page/entry) and the verbatim snippet that justified each code. Double-code a random 10% after a pause, without looking at first codes, and report agreement (percent agreement and Cohen's kappa per variable).
5. Report descriptive statistics with counts, denominators and uncertainty (e.g., Wilson 95% intervals for proportions; simple two-proportion tests or chi-square where appropriate). No causal claims; state what the data can and cannot show.
6. Save outputs to /home/user/maurice1128.github.io/research_notes/Collective suffering and Christian faith/evidence/<project>/:
   - codebook.md
   - data.csv (one row per unit; include locator and snippet columns)
   - analysis.py (re-runnable; reads data.csv; prints tables)
   - results.md (method, sample, reliability, tables, figures as text tables, limits, 3–5 sentence headline suitable for an article appendix, and the exact citation of the edition used, Chicago author-date)
   Save progress early and often (data.csv appended as you go) so nothing is lost if interrupted.
7. Never invent data. If a source cannot be obtained, stop and report.
