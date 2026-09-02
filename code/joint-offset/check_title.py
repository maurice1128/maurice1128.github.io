"""The cover letter quotes the manuscript title. Titles changed four times during revision and
the quoted copy went stale twice, the second time surviving three checker runs because no checker
read the cover letter. This compares the two literally.
"""
import io, re

M = "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"
C = "D:/ROWV_paper/COVER_LETTER.md"
title = io.open(M, encoding="utf-8").read().split("\n", 1)[0].lstrip("# ").strip()
cover = io.open(C, encoding="utf-8").read()
quoted = re.search(r"enclosed manuscript, \*(.+?)\*", cover, re.S)
if not quoted:
    print("FAIL: the cover letter does not quote a title in the expected form")
    raise SystemExit(1)
q = " ".join(quoted.group(1).split())
if q != title:
    print("FAIL: the cover letter quotes a title the manuscript no longer carries")
    print("  manuscript:", title)
    print("  cover:     ", q)
    raise SystemExit(1)
print("the cover letter quotes the manuscript's current title")
