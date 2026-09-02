# -*- coding: utf-8 -*-
"""Resolve each remaining reference to an open-access full text so its citation can be checked
against the primary source rather than an abstract. PMC first (clean XML), then OpenAlex OA PDFs."""
import io, json, os, re, sys, urllib.request as U

OUT = r"C:\Users\maurice\Desktop\spasticity_paper\refs"
UA = {"User-Agent": "Mozilla/5.0 (research citation check; CONTACT_EMAIL_REDACTED)"}

WANT = [
    (1,  "ref01_deltombe2017",     "10.2340/16501977-2226", None),
    (2,  "ref02_picelli2020",      None, "32432331"),
    (4,  "ref04_ouyang2026",       None, None),
    (6,  "ref06_choi2018",         "10.1016/j.gaitpost.2018.06.169", None),
    (8,  "ref08_korkusuz2025",     "10.1016/j.clinbiomech.2025.106617", None),
    (14, "ref14_geiger2019",       "10.1016/j.humov.2019.01.008", None),
    (15, "ref15_kesar2011",        None, "21183353"),
    (16, "ref16_geyer2010",        "10.1109/TNSRE.2010.2047592", None),
    (17, "ref17_cooper2012",       "10.1002/pri.528", None),
    (18, "ref18_attias2019",       "10.1016/j.gaitpost.2018.12.031", None),
    (19, "ref19_drefus2016",       None, "26855627"),
    (23, "ref23_zeni2008",         "10.1016/j.gaitpost.2007.07.007", None),
]


def get(url, timeout=60):
    return U.urlopen(U.Request(url, headers=UA), timeout=timeout).read()


def epmc(doi, pmid):
    q = ("DOI:%s" % doi) if doi else ("EXT_ID:%s" % pmid)
    j = json.loads(get("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                       "?query=%s&resultType=core&format=json" % U.quote(q)))
    r = j.get("resultList", {}).get("result", [])
    return r[0] if r else None


def pmc_fulltext(pmcid):
    x = get("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid).decode("utf-8", "replace")
    x = re.sub(r"<xref[^>]*>.*?</xref>", " ", x, flags=re.S)
    x = re.sub(r"<[^>]+>", " ", x)
    return re.sub(r"[ \t]+", " ", x)


def openalex_pdf(doi):
    j = json.loads(get("https://api.openalex.org/works/doi:%s?mailto=CONTACT_EMAIL_REDACTED" % doi))
    urls = []
    for l in j.get("locations", []):
        if l.get("is_oa") and l.get("pdf_url"):
            urls.append(l["pdf_url"])
    return urls, j.get("title")


for n, name, doi, pmid in WANT:
    dst = os.path.join(OUT, name + ".txt")
    if os.path.exists(dst):
        print("%-24s already have full text" % name); continue
    got = False
    try:
        rec = epmc(doi, pmid)
    except Exception as e:
        rec = None; print("%-24s epmc error %s" % (name, e))
    if rec:
        pmcid = rec.get("pmcid")
        oa = rec.get("isOpenAccess") == "Y" or rec.get("inEPMC") == "Y"
        if pmcid and oa:
            try:
                t = pmc_fulltext(pmcid)
                if len(t) > 8000:
                    io.open(dst, "w", encoding="utf-8", newline="").write(t)
                    print("%-24s PMC %s  %d chars  FULL TEXT" % (name, pmcid, len(t))); got = True
            except Exception as e:
                print("%-24s pmc fetch failed: %s" % (name, e))
    if not got and doi:
        try:
            urls, title = openalex_pdf(doi)
            for u in urls:
                try:
                    b = get(u, timeout=90)
                    if b[:5] == b"%PDF-":
                        p = os.path.join(OUT, name + ".pdf")
                        io.open(p, "wb").write(b)
                        print("%-24s OA PDF %d bytes <- %s" % (name, len(b), u[:70])); got = True; break
                    else:
                        print("%-24s not a pdf (%s) <- %s" % (name, b[:14], u[:60]))
                except Exception as e:
                    print("%-24s pdf error %s <- %s" % (name, e, u[:60]))
        except Exception as e:
            print("%-24s openalex error %s" % (name, e))
    if not got:
        print("%-24s NO OPEN FULL TEXT FOUND" % name)
