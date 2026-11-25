# Brief for audit fixers

You apply corrections from an independent audit report to (a) the section markdown files in /home/user/maurice1128.github.io/reports/sections/ and (b) the live Claude Doc.

Rules:
1. Read the audit report fully. For each problem marked misattributed / fabricated / wrong number / wrong date / wrong biblio / unsupported / dead link / inconsistency, decide the minimal correct fix. Prefer the auditor's suggested correction when it is backed by evidence. If you disagree, re-verify yourself (Crossref, Open Library, LoC JSON, publisher pages, WebFetch; send no email address) and note why.
2. Quotations taken from blurbs/reviews: either paraphrase without quotation marks or attribute correctly. Unsupported details: soften or remove, or mark *[verify]*.
3. Edit the section file(s) with exact replacements (Python with -I, or the Edit tool). Also fix the matching *_refs.md entries.
4. Apply the SAME change to the live doc with mcp__Claude_Docs__update (load via ToolSearch "select:mcp__Claude_Docs__update"; for reading blocks use "select:mcp__Claude_Docs__read"):
   - ref={"object":"node","id":"fb0e3d80-fa34"}, engine="prose", container={"kind":"project","id":"45d1c62d-42ea-45fe-b97c-8362d45232bc"}
   - For a phrase inside a paragraph without formatting changes: {"op":"replace","target":{"kind":"find","text":"<exact current words>"},"with":{"from":{"kind":"inline","content":"<new words>"},"as":"text"}}. Note: "as":"text" inherits the formatting (bold/italic) of the replaced run; if the old text was partly italic/bold, instead replace the whole paragraph: find its block id and hash via mcp__Claude_Docs__read with payload {"kind":"search","text":"<words>"}, then {"op":"replace","target":{"kind":"blocks","ids":["<full id>"]},"ifHash":"<h>","ifRev":<rev of that read>,"with":{"from":{"kind":"inline","content":"<full paragraph markdown>"},"as":"markdown"}}.
   - Several ops per call are fine. If an op is refused (find_none = the text differs), read that block and retry with exact text. Never use force.
   - The doc's reference lists live inside each section; fix entries there too.
5. Append to the audit report a "## Fixes applied" table: item · action · file changed · doc changed (yes/no).
6. Return a short summary of what changed and anything you could not fix.
