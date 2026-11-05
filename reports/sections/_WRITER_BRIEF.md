# Shared brief for section writers

Project: a comprehensive English-language literature review (Chicago author-date) for a series of journal articles on:
"Why does collective suffering sometimes intensify Christian faith and sometimes erode trust in religious institutions?"

Working model (test it, refine it, do not merely assert it):
- Collective suffering almost always raises demand for meaning, intercession and community.
- Outcome depends on (1) sufferers' position in the power structure, (2) the theological interpretation of suffering (divine punishment for collective sin vs. God suffering with the afflicted / Exodus), (3) the church's role (the sufferers' own community / a failing establishment / allied with perpetrators).
- Typical outcomes: faith up + institution up (own church); faith up + establishment trust down, faith migrates to sufferer-controlled bodies; rejection of Christianity when it is identified with perpetrators and alternatives exist.
- Open problems: power position and church role are confounded in the US slave case (Brazil helps separate them); duration/recurrence of suffering (Cohn: 1363 not 1348); the loss-of-faith branch (W. R. Jones, Pinn); timing of mass conversion (Fountain 2010: largely after emancipation).
- Race is NOT an explanatory variable; situation is.

Readers: journal reviewers in history of Christianity and sociology of religion; and the author, who wants a deep understanding and may later study theology.

## Step A — verify citations before writing
For every work you will cite that is tagged [unverified], partial, [GK], [knowledge-based] or similar in your notes, try to verify it with these reachable APIs (WebSearch quota is exhausted; use curl via Bash):
- Crossref (articles, chapters, many books): https://api.crossref.org/works?query.bibliographic=<url-encoded author title>&rows=5&select=title,author,issued,container-title,publisher,DOI,page,volume,issue
- Library of Congress (books): https://www.loc.gov/books/?q=<terms>&fo=json
- Open Library (books): https://openlibrary.org/search.json?q=<terms>&limit=5
- BnF SRU (French): https://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.title%20all%20%22<title>%22&maximumRecords=3
- DNB SRU (German): https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&query=tit%3D<title words>&recordSchema=oai_dc
- Taiwan theses: https://ndltd.ncl.edu.tw/ (may need HTML parsing)
- Google Scholar HTML (use sparingly, sleep 3s between calls; may block)
Pace requests (sleep 1s). Do not send any email address in requests. Record results: in your notes file, update the tag to [verified: Crossref/LoC/BnF/...]. Anything still unconfirmed stays cited but is marked *[verify]* in the section text and listed in the section's "To verify" list. Never invent bibliographic details or page numbers.

Also use Crossref to add notable 2020–2026 publications on your section's topic (query with &filter=from-pub-date:2020-01-01), only if clearly relevant.

## Step B — write the section
- English. Chicago author-date in-text citations, e.g. (Raboteau 1978, 212) — page numbers only if verified in notes.
- Start the section with `## <number>. <Title>` exactly as assigned. Use `###` subheadings.
- First sentence = the section's main finding. Sentences under ~25 words; paragraphs of 2–4 sentences.
- Be comprehensive: map the debates (who argues what, on what evidence), state where scholarship agrees, disagrees, and what is unknown. Tie every subsection back to the working model (does it support, complicate, or contradict it?).
- Use pipe tables where items are compared on several attributes (e.g., a debates table: position · main proponents · evidence · implication for the model). No tables duplicating prose.
- End with: `### Implications for the model` (3–6 bullets) and `### To verify` (bullet list of citations or claims the author must check, or "None").
- Length: aim 1,800–3,500 words. No emoji. No filler intro.

## Step C — save files
1. Save the full section markdown to /home/user/maurice1128.github.io/reports/sections/<NN>_<slug>.md
2. Save the reference list for every work cited in the section (full Chicago author-date entries, alphabetical; mark unverified ones with [verify]) to /home/user/maurice1128.github.io/reports/sections/<NN>_<slug>_refs.md

## Step D — write the section into the live Claude Doc
Call the tool mcp__Claude_Docs__update exactly once (if it isn't loaded, load it with ToolSearch query "select:mcp__Claude_Docs__update"), with:
- ref = {"object":"node","id":"fb0e3d80-fa34"}
- engine = "prose"
- container = {"kind":"project","id":"45d1c62d-42ea-45fe-b97c-8362d45232bc"}
- payload = {"ops":[{"op":"replace","target":{"kind":"blocks","ids":["<YOUR PENDING BLOCK ID>"]},"with":{"from":{"kind":"inline","content":"<the full section markdown>"},"as":"markdown"}}]}
Replace ONLY your own pending block. Do not read or touch other blocks. If the call is refused, read the refusal, fix the JSON, and resend once. If the section is very long and gets refused for size, split: first replace the pending block with the first half, then insert the second half after the last block id returned in the ack ({"op":"insert","target":{"kind":"blocks","ids":["<last id>"]},"side":"after","source":{"from":{"kind":"inline","content":"..."},"as":"markdown"}}).

Return a short summary: word count, number of works cited, number verified in Step A, items left to verify.
