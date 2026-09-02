# -*- coding: utf-8 -*-
"""r547: how far is this manuscript's prose from the papers it sits beside?

The style objection is that the text reads as generated. That is checkable rather than a matter of
taste: a comparison paper in the same journal, on the same kind of study, has a measurable profile,
and the distance from it can be reported per thousand words. Two comparators are used, both already
in the reference list: Jansen et al. [9], a reflex-gain gait simulation in this journal, and Ong et
al. [10], the template this study's method follows.
"""
import io, os, re

REF = r"C:\Users\maurice\Desktop\spasticity_paper\refs"
MAN = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"

PATS = [
    (r"\u2014", "em dash"),
    (r"\*\*", "bold marker"),
    (r";", "semicolon"),
    (r"(?<![0-9§]):(?![0-9/])", "colon"),
    (r"\brather than\b", "rather than"),
    (r"\band not\b", "and not"),
    (r"\bhowever\b", "however"),
    (r"\b(?:moreover|furthermore|in addition)\b", "moreover/furthermore"),
    (r"\bet al\.", "et al."),
    (r"\b(?:we|our|us)\b", "first person"),
    (r"\b[Ww]hat [a-z][^.;]{4,60}? is\b", "pseudo-cleft"),
    (r"\((?:[^()]*?)\)", "parenthesis"),
    (r"\b(?:Two|Three|Four|Five|Six|Seven) [a-z]", "enumerative opener"),
]


def profile(txt, name):
    words = txt.split()
    w = len(words)
    sents = [x for x in re.split(r"(?<=[.!?])\s+", txt) if len(x.split()) > 3]
    paras = [p for p in re.split(r"\n\s*\n", txt) if len(p.split()) > 25]
    out = {"name": name, "words": w,
           "mean_sentence": sum(len(x.split()) for x in sents) / float(len(sents)) if sents else 0,
           "mean_paragraph": sum(len(p.split()) for p in paras) / float(len(paras)) if paras else 0,
           "long_sentences": 100.0 * sum(1 for x in sents if len(x.split()) > 40) / len(sents) if sents else 0}
    for p, nm in PATS:
        flags = 0 if nm in ("enumerative opener", "pseudo-cleft") else re.I
        out[nm] = 1000.0 * len(re.findall(p, txt, flags)) / w
    return out


def load_ref(fn, start_keys, stop_keys):
    p = os.path.join(REF, fn)
    if not os.path.exists(p):
        return None
    s = io.open(p, encoding="utf-8").read()
    i = -1
    for k in start_keys:
        i = s.find(k)
        if i > 0:
            break
    if i < 0:
        i = 0
    j = len(s)
    for k in stop_keys:
        t = s.find(k, i + 500)
        if t > 0:
            j = min(j, t)
    return s[i:j]


refs = []
j = load_ref("ref09_jansen2014.txt", ["Hemiparetic gait after stroke is"], ["Competing interests", "References"])
if j:
    refs.append((j, "Jansen 2014, JNER"))
o = load_ref("ref10_ong2019.txt", ["Walking is", "Plantarflexor", "Introduction"],
             ["Supporting information", "References", "Acknowledg"])
if o:
    refs.append((o, "Ong 2019, PLOS CB"))

m = io.open(MAN, encoding="utf-8").read()
ours = m[m.index("## 1. Background"):m.index("## Figures")]
ours = re.sub(r"^\|.*$", "", ours, flags=re.M)          # drop tables, which no comparator has
rows = [profile(t, n) for t, n in refs] + [profile(ours, "THIS MANUSCRIPT")]

keys = ["words", "mean_sentence", "mean_paragraph", "long_sentences"] + [nm for _, nm in PATS]
print("%-22s" % "" + "".join("%18s" % r["name"][:17] for r in rows))
for k in keys:
    line = "%-22s" % k
    for r in rows:
        v = r.get(k, 0)
        line += "%18s" % (("%.0f" % v) if k == "words" else "%.1f" % v)
    print(line)

print("\nunits: counts are per 1000 words; mean_sentence and mean_paragraph are words;")
print("long_sentences is the percentage of sentences over 40 words.")

if len(rows) >= 2:
    ref_mean = {k: sum(r.get(k, 0) for r in rows[:-1]) / float(len(rows) - 1) for k in keys}
    us = rows[-1]
    print("\nlargest departures from the comparators' mean:")
    dev = []
    for k in keys:
        if k == "words":
            continue
        a, b = ref_mean[k], us.get(k, 0)
        if max(a, b) < 0.3:
            continue
        dev.append((abs(b - a) / max(a, 0.2), k, a, b))
    for _, k, a, b in sorted(dev, reverse=True)[:9]:
        print("   %-22s comparators %6.1f   ours %6.1f" % (k, a, b))
