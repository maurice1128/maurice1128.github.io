# -*- coding: utf-8 -*-
"""r582: break the one sentence shape this manuscript over-uses.

Measured per thousand words against the two simulation comparators:

                        rather than   X and not Y   ", so ..."   sentence-initial connective
    this manuscript            2.90          5.21         3.97                          0.00
    Jansen 2014                0.15          0.74         0.00                          5.89
    Ong 2019                   0.72          0.82         0.10                          0.92

The manuscript runs one antithetical frame at four to forty times the comparators' rate and opens no
sentence with an ordinary connective at all. Both blind readers named this as the dominant tell, and
the two figures are the same fault seen from either side: a clause a human author would begin as a
new sentence with "Therefore" or "However" is instead welded on with ", so".

This splits those welds. A sentence longer than twenty words whose second clause begins with a
determiner or pronoun after ", so" becomes two sentences, the second opening on a connective drawn in
rotation so that no single word becomes the next tic. Only that construction is touched; no number,
citation or claim moves. "moreover", "furthermore" and "in addition" are excluded by house rule.

Tables, headings, figure captions, numbered reference entries and everything from the reference list
onward are left alone, and paragraphs are re-wrapped to the file's existing 100-column width. An
earlier attempt at this flattened the reference list into a single paragraph and destroyed the hard
wrapping; the self-check caught both.
"""
import io, re, shutil

FILES = [r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md",
         r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"]
shutil.copyfile(FILES[0], FILES[0].replace("MANUSCRIPT", ".bak_r108_MANUSCRIPT"))
shutil.copyfile(FILES[1], FILES[1].replace("SUPPLEMENT", ".bak_r109_SUPPLEMENT"))

CONN = ["Therefore, ", "As a result, ", "Consequently, ", "It follows that ", "Therefore, "]
LEAD = re.compile(r"^(the|this|that|it|they|we|no|none|neither|any|each|every|a|an|its|their|"
                  r"nothing|both|two|three|four|five|there)\b", re.I)
SKIP = re.compile(r"^\s*(\||#|!|\*\*Fig|[0-9]{1,2}\.\s+[A-Z])")


def wrap(p, w=100):
    out, line = [], ""
    for word in p.split():
        if line and len(line) + 1 + len(word) > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word) if line else word
    if line:
        out.append(line)
    return "\n".join(out)


def split_welds(text):
    out, used = [], [0]
    for para in text.split("\n\n"):
        if SKIP.match(para) or "|" in para.split("\n")[0][:4]:
            out.append(para)
            continue
        sents = re.split(r"(?<=[.!?])\s+", " ".join(para.split()))
        new = []
        for x in sents:
            m = re.match(r"^(.{45,}?), so (.{25,})$", x)
            if (m and len(x.split()) > 20 and LEAD.match(m.group(2))
                    and "et al" not in m.group(1)[-8:]):
                head, tail = m.group(1).rstrip(","), m.group(2)
                conn = CONN[used[0] % len(CONN)]
                used[0] += 1
                if not tail[:3].isupper():
                    tail = tail[0].lower() + tail[1:]
                new.append(head + ". " + conn + tail)
            else:
                new.append(x)
        out.append(wrap(" ".join(new)))
    return "\n\n".join(out), used[0]


total = 0
for f in FILES:
    s = io.open(f, encoding="utf-8").read()
    tail = ""
    if "## References" in s:
        s, tail = s.split("## References", 1)
        tail = "## References" + tail
    if "## 1. Background" in s:
        head, body = s.split("## 1. Background", 1)
        body, k = split_welds(body)
        body = head + "## 1. Background" + body
    else:
        body, k = split_welds(s)
    io.open(f, "w", encoding="utf-8", newline="").write(body + tail)
    total += k
    print("%-26s %3d welds split" % (f.split("\\")[-1], k))
print("total: %d" % total)
