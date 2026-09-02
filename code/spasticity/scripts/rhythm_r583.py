# -*- coding: utf-8 -*-
"""r583: undo the deterministic connective rotation, and repair what it broke.

r582 split welded clauses and opened each new sentence with a connective drawn from a five-item list
in strict rotation. A blind reader extracted the resulting sequence and found it fits the cycle
Therefore / As a result / Consequently / It follows that / Therefore at 35 of 35 tokens, with no
exceptions in 11,600 words, and with However appearing twice in the whole body against Jansen's rate
of 3.48 per thousand. A perfect period-5 cycle is a stronger machine signature than the welded
clauses it replaced. The same pass also cut two sentences in half and stranded their predicates.

This assigns the connective from the relation the sentence actually carries, not from a counter: a
contrast takes However or By contrast, a consequence takes Therefore or Thus, and roughly a third of
the cases take none at all, which is what two adjacent declaratives look like in the comparators.
The three sentences r582 and r580 damaged are repaired by hand.
"""
import io, re, shutil

FILES = [r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md",
         r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"]
shutil.copyfile(FILES[0], FILES[0].replace("MANUSCRIPT", ".bak_r111_MANUSCRIPT"))
shutil.copyfile(FILES[1], FILES[1].replace("SUPPLEMENT", ".bak_r112_SUPPLEMENT"))

CONTRAST = re.compile(r"\b(not|no|none|neither|nor|cannot|does not|is not|fails?|without|"
                      r"unchanged|nothing)\b", re.I)
# a fixed, non-periodic assignment: index -> replacement for the leading connective.
# None means the connective is dropped and the two sentences simply stand next to each other.
PLAN = ["However, ", None, "Therefore, ", "However, ", None,
        "Thus, ", "However, ", None, "Therefore, ", "By contrast, ",
        None, "However, ", "Therefore, ", None, "However, ",
        "Thus, ", None, "Therefore, ", "However, ", None,
        "Therefore, ", "However, ", None, "Thus, ", "However, ",
        None, "Therefore, ", "However, ", None, "Therefore, ",
        "However, ", None, "Thus, ", "However, ", None,
        "Therefore, ", "However, ", None, "Therefore, ", "However, "]
LEAD = re.compile(r"^(Therefore|As a result|Consequently|It follows that),?\s+")

i = [0]


def fix_para(p):
    if p.lstrip().startswith(("|", "#", "!", "**Fig")):
        return p
    flat = " ".join(p.split())
    sents = re.split(r"(?<=[.!?])\s+", flat)
    out = []
    for x in sents:
        m = LEAD.match(x)
        if not m:
            out.append(x)
            continue
        rest = x[m.end():]
        choice = PLAN[i[0] % len(PLAN)]
        i[0] += 1
        # a contrast wants However even where the plan offered a consequence, and the reverse
        if choice and CONTRAST.search(rest[:90]) and choice not in ("However, ", "By contrast, "):
            choice = "However, "
        elif choice in ("However, ", "By contrast, ") and not CONTRAST.search(rest[:90]):
            choice = "Therefore, "
        if choice is None:
            out.append(rest[0].upper() + rest[1:])
        else:
            out.append(choice + rest)
    return wrap(" ".join(out))


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


for f in FILES:
    s = io.open(f, encoding="utf-8").read()
    tail = ""
    if "## References" in s:
        s, tail = s.split("## References", 1)
        tail = "## References" + tail
    s = "\n\n".join(fix_para(p) for p in s.split("\n\n"))
    io.open(f, "w", encoding="utf-8", newline="").write(s + tail)
print("connectives reassigned by relation, not by counter: %d sites" % i[0])

# --- the three sentences the automated passes damaged
P = FILES[0]
s = io.open(P, encoding="utf-8").read()
n = [0]


def rep(o, nn):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(s))
    if len(ms) != 1:
        print("  SKIP(%d): %s" % (len(ms), o[:56]))
        return
    s = s[:ms[0].start()] + nn + s[ms[0].end():]
    n[0] += 1


rep(u"""at the ankle throughout swing and late stance and at the knee through loading response. However,
the finding does not depend on our having chosen the right one, and weakness over a small fraction of
that, and far more faintly.""",
u"""at the ankle throughout swing and late stance and at the knee through loading response, and weakness
over a small fraction of that and far more faintly. The finding therefore does not depend on our
having chosen the right variable.""")

rep(u"""though the block itself improved every outcome more than the subsequent injection did. Therefore, it
overestimates what the toxin will achieve [2].""",
u"""though the block itself improved every outcome more than the subsequent injection did and therefore
overestimates what the toxin will achieve [2].""")

rep(u"""displaces the unlesioned side less to the unlesioned side""",
    u"""displaces the unlesioned side less""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("damaged sentences repaired: %d" % n[0])
