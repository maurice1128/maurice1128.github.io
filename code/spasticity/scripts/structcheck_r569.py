# -*- coding: utf-8 -*-
"""r569: structural checks that selfcheck_r541 cannot perform.

selfcheck_r541 asks whether a string is present or absent. That catches a retired claim quoted
verbatim and nothing else. Five classes of defect escaped it entirely across two council rounds, and
in every case the defect was introduced by a repair rather than by the original draft:

  A  bold markers that pair across paragraph and heading boundaries, so half the manuscript renders
     bold while the total marker count stays even and the parity test passes
  B  a section cross-reference to a section that does not exist, or that no longer says what the
     reference claims
  C  a promise of the form "Supplement Sn gives X" whose target does not contain X
  D  a number that lives in only one of the two files, in particular a result introduced for the
     first time in the Discussion or Conclusions
  E  the same sentence appearing in both files with different numbers in it

This checks all five. It is a structural checker: it knows nothing about the science and cannot
replace selfcheck_r541, which knows which claims are retired. Run both.
"""
import io, os, re, sys

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
MS = os.path.join(PAP, "MANUSCRIPT_r541.md")
SUP = os.path.join(PAP, "SUPPLEMENT_r541.md")
S = io.open(MS, encoding="utf-8").read()
Q = io.open(SUP, encoding="utf-8").read() if os.path.exists(SUP) else ""

fails, warns = [], []


def fail(m):
    fails.append(m)


def warn(m):
    warns.append(m)


def lineno(txt, i):
    return txt.count("\n", 0, i) + 1


# ---------------------------------------------------------------- A. bold pairing
def check_bold(txt, name):
    pos = [m.start() for m in re.finditer(r"\*\*", txt)]
    if len(pos) % 2:
        fail("%s: %d bold markers, an odd number, so one is unmatched" % (name, len(pos)))
        return
    for a, b in zip(pos[0::2], pos[1::2]):
        span = txt[a + 2:b]
        if "\n\n" in span:
            fail("%s line %d: a bold span crosses a paragraph break and runs %d characters "
                 "(%r ... %r). The parity test passes and the document still renders wrong."
                 % (name, lineno(txt, a), b - a, span[:44].replace("\n", " "),
                    span[-30:].replace("\n", " ")))
        elif re.search(r"^#{1,4} ", span, re.M):
            fail("%s line %d: a bold span crosses a heading" % (name, lineno(txt, a)))
        elif len(span) > 320:
            warn("%s line %d: bold run of %d characters, %r"
                 % (name, lineno(txt, a), len(span), span[:50]))


check_bold(S, "manuscript")
if Q:
    check_bold(Q, "supplement")

# ---------------------------------------------------------------- B. section references
heads = set()
for m in re.finditer(r"^#{2,4}\s+([0-9]+(?:\.[0-9]+)?)\.?\s", S, re.M):
    heads.add(m.group(1))
for m in re.finditer(r"^##\s+([0-9]+)\.\s", S, re.M):
    heads.add(m.group(1))
sup_heads = set(m.group(1) for m in re.finditer(r"^##\s+(S[0-9]+)\.", Q, re.M))

for name, txt in (("manuscript", S), ("supplement", Q)):
    for m in re.finditer(r"\u00a7\u00a7?\s*([0-9]+(?:\.[0-9]+)?)", txt):
        r = m.group(1)
        # a reference to 3.4 must find a 3.4 heading. Falling back to 3 would accept a pointer
        # into a subsection that has been merged away, which is how a dangling 1.1 survived r586.
        if r not in heads:
            fail("%s line %d: reference to \u00a7%s, which is not a heading in the manuscript"
                 % (name, lineno(txt, m.start()), r))
    for m in re.finditer(r"\bSupplement\s+(S[0-9]+)|\b(S[0-9]+)\b(?=[ ,.])", txt):
        r = m.group(1) or m.group(2)
        if sup_heads and r not in sup_heads:
            fail("%s line %d: reference to %s, which is not a section of the supplement"
                 % (name, lineno(txt, m.start()), r))

# ---------------------------------------------------------------- C. delegation promises
STOP = set("""the a an and or of in to for is are was were be been it its this that these those with
by on at as from than then so which what where when how not no we our us they their there here also
each every both all some any one two three four five full detail details rather instead alone""".split())
sup_sections = {}
for m in re.finditer(r"^##\s+(S[0-9]+)\.(.*?)(?=^##\s+S[0-9]+\.|\Z)", Q, re.M | re.S):
    sup_sections[m.group(1)] = m.group(2).lower()

PROMISE = re.compile(
    r"(?:Supplement\s+)?(S[0-9]+)\s+(?:gives|holds|sets out|states|reports|derives|contains|carries|"
    r"lists|records)\s+([^.;]{6,150})", re.I)
for m in PROMISE.finditer(S):
    sec, what = m.group(1).upper(), m.group(2)
    body = sup_sections.get(sec)
    if body is None:
        fail("manuscript line %d: promises %s, which does not exist" % (lineno(S, m.start()), sec))
        continue
    words = [w for w in re.findall(r"[a-z]{4,}", what.lower()) if w not in STOP]
    if not words:
        continue
    miss = [w for w in words if w not in body]
    if len(miss) > max(1, len(words) // 2):
        fail("manuscript line %d: promises %s %r, but %s does not mention %s"
             % (lineno(S, m.start()), sec, what.strip()[:70], sec, ", ".join(miss[:5])))

# ---------------------------------------------------------------- D. numbers born late
def sec_split(txt):
    out, cur, buf = {}, "front", []
    for ln in txt.split("\n"):
        h = re.match(r"^#{2,4}\s+(.*)$", ln)
        if h:
            out[cur] = "\n".join(buf)
            cur, buf = h.group(1), []
        else:
            buf.append(ln)
    out[cur] = "\n".join(buf)
    return out


secs = sec_split(S)
NUM = re.compile(r"(?<![0-9.])[0-9]+\.[0-9]{2,}")
early = set()
for k, v in secs.items():
    if re.match(r"^(Abstract|[123]\.|[123]\.[0-9])", k.strip()):
        early |= set(NUM.findall(v))
early |= set(NUM.findall(Q))
for k, v in secs.items():
    if not re.match(r"^([45]\.|5\b|Conclusions)", k.strip()):
        continue
    for m2 in NUM.finditer(v):
        tok = m2.group(0)
        # a literature value is one whose own paragraph carries a citation bracket.
        pstart = v.rfind('\n\n', 0, m2.start()) + 2
        pend = v.find('\n\n', m2.end())
        near = v[pstart:pend if pend > 0 else len(v)]
        if re.search(r"\[[0-9]{1,2}(,\s*[0-9]{1,2})*\]", near):
            continue                      # quoted from a cited work, not produced here
        if tok not in early:
            fail("a result appears for the first time in %r: %s is in no Results section and in no "
                 "supplement section" % (k.strip()[:44], tok))

# ---------------------------------------------------------------- E. same sentence, different number
def sents(txt):
    txt = re.sub(r"^\|.*$", "", txt, flags=re.M)
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", txt) if len(x.split()) > 7]


def sig(x):
    return tuple(w for w in re.findall(r"[a-z]{4,}", x.lower()) if w not in STOP)


ms_s, sp_s = sents(S), sents(Q)
idx = {}
for x in sp_s:
    g = sig(x)
    if len(g) >= 8:
        idx.setdefault(g[:10], []).append(x)
seen = set()
for x in ms_s:
    g = sig(x)
    if len(g) < 8:
        continue
    for y in idx.get(g[:10], []):
        nx, ny = set(NUM.findall(x)), set(NUM.findall(y))
        if nx != ny and (nx or ny) and (x, y) not in seen:
            seen.add((x, y))
            fail("the same sentence carries different numbers in the two files:\n"
                 "        manuscript: %s\n        supplement: %s"
                 % (" ".join(x.split())[:118], " ".join(y.split())[:118]))

# ---------------------------------------------------------------- F. unfinished edits
# 'Ouyang et al. measured' is not a lowercase sentence start. Skip when the text before the
# stop ends in an abbreviation or a single letter.
ABBREV = re.compile(r'(et\s+al|vs|cf|Fig|ref|no|approx|[A-Za-z])\s*$', re.I)
for name, txt in (("manuscript", S), ("supplement", Q)):
    for m in re.finditer(r'(?<=[a-z])\.\s+([a-z][a-z]{3,})', txt):
        if ABBREV.search(txt[max(0, m.start() - 26):m.start()]):
            continue
        warn("%s line %d: sentence appears to start lowercase, %r"
             % (name, lineno(txt, m.start()), txt[m.start():m.start() + 46].replace(chr(10), ' ')))
    for m in re.finditer(r'^\s*\*\*\s*$', txt, re.M):
        fail("%s line %d: a bold marker alone on its line" % (name, lineno(txt, m.start())))

# ------------------------------------------------- G. damage left by automated editing
# Every one of these classes was produced by a pass in this project and found by a human
# reader rather than by a check. They are cheap to test for and were expensive to miss.
for name, txt in (("manuscript", S), ("supplement", Q)):
    if not txt:
        continue
    body = txt.split("## References")[0]
    # headings are not sentences; joining them to the next sentence invents repeats
    body = re.sub(r"^#{1,4} .*$", "", body, flags=re.M)

    # a clause repeated inside one sentence
    for sent in re.split(r"(?<=[.!?])\s+", " ".join(body.split())):
        w = sent.lower().split()
        for span in range(6, 12):
            seen = set()
            for k in range(len(w) - span):
                g = " ".join(w[k:k + span])
                if g in seen and "|" not in sent:
                    fail("%s: a clause repeats inside one sentence: %r" % (name, g[:60]))
                    break
                seen.add(g)
            else:
                continue
            break

    # a paragraph opening on a pronoun or ordinal with nothing before it
    DANGLE = re.compile(r"^(It|They|That|Those|These|Them|Both|Neither|Such|A (?:second|third|fourth))\b")
    for para in body.split("\n\n"):
        p = " ".join(para.split())
        if len(p.split()) > 12 and DANGLE.match(p):
            warn("%s: a paragraph opens on an anaphor: %r" % (name, p[:70]))

    # a supplement section opening mid-argument rather than orienting the reader
    if name == "supplement":
        for m in re.finditer(r"^## (S[0-9]+)\.(.*?)(?=^## S[0-9]+\.|\Z)", body, re.M | re.S):
            rest = m.group(2).split("\n", 1)[1] if "\n" in m.group(2) else ""
            paras = [x for x in rest.strip().split("\n\n") if x.strip()]
            if not paras:
                continue
            opener = " ".join(paras[0].split())
            if not re.search(r"\u00a7[0-9]|this section|Supplement|reports|gives|sets out|carries",
                             opener, re.I) and not opener.startswith("**"):
                warn("%s %s opens without orienting the reader: %r"
                     % (name, m.group(1), opener[:70]))

print("manuscript sections: %d;  supplement sections: %d" % (len(heads), len(sup_heads)))
print()
for f in fails:
    print("  FAIL  %s" % f)
for w in warns:
    print("  warn  %s" % w)
print("\n=== %d structural failures, %d warnings ===" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
