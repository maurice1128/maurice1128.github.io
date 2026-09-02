# -*- coding: utf-8 -*-
"""Emit the reference list from authoritative Europe PMC records rather than by hand, so that no
title, volume, page or identifier in the manuscript is typed from memory."""
import io, json, urllib.request as U

UA = {"User-Agent": "Mozilla/5.0 (citation check; CONTACT_EMAIL_REDACTED)"}
Q = [
 (1,  'DOI:"10.2340/16501977-2226"'), (2,  "EXT_ID:32432331"), (3,  "EXT_ID:35711273"),
 (4,  "EXT_ID:41928260"), (5,  'DOI:"10.3390/neurolint17010010"'), (6,  "EXT_ID:29960141"),
 (7,  'DOI:"10.4102/sajp.v79i1.1926"'), (8, 'DOI:"10.1016/j.clinbiomech.2025.106617"'),
 (9,  "EXT_ID:24885302"), (10, "EXT_ID:31589597"), (11, "EXT_ID:35442531"),
 (12, 'DOI:"10.1186/s12984-025-01767-w"'), (13, 'DOI:"10.3390/ijerph18031343"'),
 (14, "EXT_ID:30710860"), (15, "EXT_ID:21183350"), (16, "EXT_ID:20378480"),
 (17, "EXT_ID:22147298"), (18, "EXT_ID:30594869"), (19, "EXT_ID:26855626"),
 (20, "EXT_ID:33329327"), (21, 'DOI:"10.1371/journal.pcbi.1008935"'),
 (22, 'DOI:"10.1371/journal.pdig.0000467"'), (23, "EXT_ID:17723303"), (24, "EXT_ID:19013070"),
]


def get(q):
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%s&resultType=core&format=json"
         % U.quote(q))
    r = json.loads(U.urlopen(U.Request(u, headers=UA), timeout=60).read())["resultList"]["result"]
    return r[0] if r else None


out = []
for n, q in Q:
    r = get(q)
    if not r:
        out.append("%d. *** NOT RESOLVED (%s) ***" % (n, q)); print("%2d  UNRESOLVED %s" % (n, q)); continue
    ji = r.get("journalInfo", {})
    au = r.get("authorString", "").rstrip(".")
    if au.count(",") >= 6:
        au = ", ".join(au.split(", ")[:6]) + ", et al"
    bits = "%s. %s. %s" % (au, r.get("title", "").rstrip("."),
                           ji.get("journal", {}).get("medlineAbbreviation") or ji.get("journal", {}).get("title"))
    vol, iss, pg = ji.get("volume"), ji.get("issue"), r.get("pageInfo")
    tail = " %s" % ji.get("yearOfPublication")
    if vol: tail += ";%s" % vol
    if iss: tail += "(%s)" % iss
    if pg:  tail += ":%s" % pg
    line = "%d. %s.%s." % (n, bits, tail)
    if r.get("doi"): line += " doi:%s." % r["doi"]
    if r.get("pmid"): line += " PMID %s." % r["pmid"]
    out.append(line)
    print("%2d  %s" % (n, line[:150]))

io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\REFERENCES_verified.md",
        "w", encoding="utf-8", newline="").write("## References\n\n" + "\n".join(out) + "\n")
