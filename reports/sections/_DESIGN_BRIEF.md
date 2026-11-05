# Brief for article-design writers

You are writing ONE article design (not the article itself) for a journal series on:
"Why does collective suffering sometimes intensify Christian faith and sometimes erode trust in religious institutions?"

Evidence base (read what is relevant to your article):
- Finished literature-review sections: /home/user/maurice1128.github.io/reports/sections/*.md (and *_refs.md for full citations)
- Research notes: /home/user/maurice1128.github.io/research_notes/Collective suffering and Christian faith/*.md
- Verified fact-check results: research_notes/.../wf_factcheck_key_claims.md (use its corrections: e.g., Belloc et al. 2016 measured delayed communal self-government, not religious authority; Robinson 2019 is in *Archives* 54/2; Ralph of Shrewsbury's mandate is dated 10 January 1349; Dittmar & Meisenzahl 11–14 pp, 14 baseline; Jedwab et al. needs the aggregate-increase caveat)
- Journal requirements: research_notes/.../methodology_and_journals.md (journal table) — mark anything not confirmed there as *[verify guidelines]*.

Current model (refine for your article):
- Suffering raises demand for meaning/intercession/community.
- Conditions: (1) sufferers' power position; (2) theology of suffering (punishment vs God-with-sufferer) AND who controls the remedy it prescribes; (3) church role (own community / failing establishment / allied with perpetrators), incl. capacity to deliver care; (4) duration/recurrence of the suffering; (5) intergenerational transmission requires community.
- Outcomes: faith up + institution up; faith up + establishment trust down → migration to sufferer-controlled bodies (often inside the church, e.g., lay confraternities); rejection.
- Rival explanations to test: deliverance/emancipation (Fountain 2010), provision/relief (Madsen 2012 "flour Christians"), political alignment (contemporary).

Write in English. Structure your section exactly:
## Article N — <working title>
### At a glance  (pipe table: question · thesis (one sentence) · contribution · design · core evidence · length · first/second/third-choice journals)
### Research question and thesis  (2–3 paragraphs; state the falsifiable claim and what evidence would refute it)
### Contribution and closest prior work  (table: prior work · what it does · what this article adds)
### Design and evidence  (case selection logic, comparison/within-case design, sources and how each measures devotion vs institutional trust)
### Section-by-section outline  (numbered list; each section: purpose, ~word budget, key sources/citations by author-year, the primary sources the author must read)
### Anticipated reviewer objections  (table: objection · response · supporting citations)
### What the author must do personally  (checklist `- [ ]`: books to read in full, archives/primary sources to consult, citations to verify, writing to do; realistic hours/weeks)
### Target journals  (table: journal · fit · length/style · fees/OA · status of guideline check)
### Risks and fallbacks

Rules: cite author-year only for works present in the section/refs files; keep *[verify]* tags from the sources; never invent works, numbers or page numbers. Neutral tone on contested contemporary issues. Length 1,800–3,000 words.

Save to /home/user/maurice1128.github.io/reports/design/article_<N>.md

Then write into the live plan doc with ONE call to mcp__Claude_Docs__update (load via ToolSearch "select:mcp__Claude_Docs__update" if needed):
ref={"object":"node","id":"3d76fd6a-8142"}, engine="prose", container={"kind":"project","id":"a2647392-ecb0-44e2-a149-7c5f082ca44c"},
payload={"ops":[{"op":"replace","target":{"kind":"blocks","ids":["<YOUR PENDING ID>"]},"with":{"from":{"kind":"inline","content":"<markdown>"},"as":"markdown"}}]}
Replace only your pending block. If refused, fix and resend once. Return a short summary.
