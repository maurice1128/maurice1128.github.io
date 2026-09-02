# -*- coding: utf-8 -*-
"""r587: remove the physical residue of this session's automated edits, and the antecedents they ate.

A blind reader found the mechanical signature before finding any stylistic one. The file is hard
wrapped at about 100 columns, and six paragraphs begin with a stub line far below that width, which
happens when text is deleted from a paragraph head and the paragraph is never re-flowed. The clearest
case is a paragraph whose first line is the single word "No". Other lines run to 259 characters inside
otherwise 95-column paragraphs, which is the same fault in the opposite direction: a sentence spliced
in and the paragraph left unwrapped. No comparator can show this, because none was produced by
patch-editing.

Removing a bold heading also removes whatever it referred forward to. "Crossing them to obtain
independent magnitudes is what makes the apportionment question answerable at all" lost its antecedent
when the heading "The two lesions are imposed independently; in patients they co-occur" was deleted in
r584. Two further anaphors are repaired here, and three connectives that mark an additive or
consequential relation as an adversative one.
"""
import io, re, shutil

FILES = [r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md",
         r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"]
shutil.copyfile(FILES[0], FILES[0].replace("MANUSCRIPT", ".bak_r117_MANUSCRIPT"))
shutil.copyfile(FILES[1], FILES[1].replace("SUPPLEMENT", ".bak_r118_SUPPLEMENT"))

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


# ---- antecedents eaten by the removal of the numbered headings
rep(u"""Crossing them to obtain
independent magnitudes is what makes the apportionment question answerable at all, and patients do
not present that way""",
u"""The two lesions are imposed independently here, and crossing them to obtain independent magnitudes
is what makes the apportionment question answerable at all. Patients do not present that way""")

rep(u"""and ref [1] describes that blockade as reversible over three to six months""",
    u"""and ref [1] describes botulinum toxin as producing a reversible blockade lasting three to six
months""")

rep(u"""but takes that maximum over the whole gait cycle rather than during swing. However, it corroborates
the direction without being the same variable.) It is one point on one of three curves, and it had
never been compared with the rest of them.""",
u"""but takes that maximum over the whole gait cycle rather than during swing, so it corroborates the
direction without being the same variable.) The angle at contact is one point on one of three curves,
and it had never been compared with the rest of them.""")

# ---- three connectives marking the opposite of the relation they carry
rep(u"""it is the procedure the field would like to avoid, and it removes only one of the two components.
However, it cannot calibrate the other.""",
u"""it is the procedure the field would like to avoid, it removes only one of the two components, and it
cannot calibrate the other.""")

rep(u"""overactivity arising from a stretch reflex and overactivity arising from cocontraction are both
treated by chemodenervation or neurotomy. However, the reading need not distinguish them to be
useful. But the retreat is larger than that""",
u"""overactivity arising from a stretch reflex and overactivity arising from cocontraction are both
treated by chemodenervation or neurotomy, and the reading need not distinguish them to be useful.
The retreat is larger than that""")

rep(u"""Only the published abstract of [28] was retrieved. However, we can verify the coefficient, the p value
and the cohort size and nothing else.""",
u"""Only the published abstract of [28] was retrieved, so the coefficient, the p value and the cohort
size are all we can verify.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("anaphors and connectives repaired: %d" % n[0])


# ---- re-flow every prose paragraph to the file's own 100-column convention
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


SKIP = re.compile(r"^\s*(\||#|!|```|\s*$)")

for f in FILES:
    s = io.open(f, encoding="utf-8").read()
    tail = ""
    if "## References" in s:
        s, tail = s.split("## References", 1)
        tail = "## References" + tail
    out = []
    for para in s.split("\n\n"):
        first = para.split("\n")[0] if para else ""
        if SKIP.match(first) or "|" in first[:4] or not para.strip():
            out.append(para)
        else:
            out.append(wrap(para))
    io.open(f, "w", encoding="utf-8", newline="").write("\n\n".join(out) + tail)
    L = [len(x) for x in io.open(f, encoding="utf-8").read().split("\n")]
    print("%-26s max line %d" % (f.split("\\")[-1], max(L)))
