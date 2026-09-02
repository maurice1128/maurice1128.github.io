# -*- coding: utf-8 -*-
"""r572: bind every numeric claim in the text to a deposited container, and fail when they part.

Why this exists. selfcheck_r541 tests whether a string is present and does arithmetic between
constants typed into the checker itself; not one of its sixteen arithmetic calls reads a number out
of the manuscript, and it opens no container at all. Across five council rounds every defect that
mattered was of one shape: a number in the text that no deposit supports, or a deposit that has since
moved and left the text behind. A string checker cannot see either.

What this does.

  1. Extracts every numeric token of three or more significant decimals from the manuscript and the
     supplement, with the sentence it sits in.
  2. Flattens every JSON deposit in paper/ to path -> value.
  3. Binds each text token to the deposits that carry it.
  4. Freezes the binding. On later runs a token that was bound and is no longer, or a token whose
     container value has moved, is a failure rather than a silent drift.

It also reports, and this is the part no earlier check could give: which numeric claims rest on no
deposit at all. Those are not automatically wrong. Some are arithmetic on other reported values and
some are quoted from cited work. But they are the set within which every unsupported claim this
project has produced was found, so the count is worth watching and worth keeping small.

Run alongside selfcheck_r541 (which knows which claims are retired) and structcheck_r569 (which
knows what a well-formed document looks like). None of the three subsumes another.
"""
import glob, io, json, os, re, sys


def ascii_safe(x):
    return re.sub(r"[^ -~]", ".", x)

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
MS = os.path.join(PAP, "MANUSCRIPT_r541.md")
SUP = os.path.join(PAP, "SUPPLEMENT_r541.md")
BIND = os.path.join(PAP, "BINDING_r572.json")

TOK = re.compile(r"(?<![0-9A-Za-z.])(\d{1,3}\.\d{3,})(?![0-9])")
CITE = re.compile(r"\[[0-9]{1,2}(?:\s*,\s*[0-9]{1,2})*\]")
fails, warns, notes = [], [], []


def load(p):
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""


S, Q = load(MS), load(SUP)


def sentences(txt):
    # the reference list is bibliographic, not evidential: its DOI prefixes are not measurements
    cut = txt.find("## References")
    if cut > 0:
        txt = txt[:cut]
    txt = re.sub(r"^\|", " ", txt, flags=re.M)
    return [x for x in re.split(r"(?<=[.!?])\s+", txt) if "doi:" not in x.lower()]


STOP = set("""the a an and or of in to for is are was were be been it its this that these those with
by on at as from than then so which what where when how not no we our us they their there here also
each every both all some any one two three four five per cent against about over under between
same other more less than into within across using used give gives given report reports reported""".split())


def keywords(sent):
    w = set(x for x in re.findall(r"[a-z]{4,}", sent.lower()) if x not in STOP)
    return w | set(x[:-1] for x in w if x.endswith("s"))


def path_words(container, path):
    # four characters, not five: deposit keys are terse (span, gap, rho, seed, weak, kv) and a
    # five-character floor drops exactly the ones that name the quantity.
    w = set(re.findall(r"[a-z]{4,}", (container + " " + path).lower()))
    return w | set(x[:-1] for x in w if x.endswith("s")) | set(x + "s" for x in w)


def text_tokens():
    """token -> list of (file, sentence)"""
    out = {}
    for name, txt in (("manuscript", S), ("supplement", Q)):
        for sent in sentences(txt):
            for m in TOK.finditer(sent):
                out.setdefault(m.group(1), []).append((name, " ".join(sent.split())[:150]))
    return out


def flatten(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            for r in flatten(v, pre + "/" + str(k)):
                yield r
    elif isinstance(o, list):
        for i, v in enumerate(o):
            for r in flatten(v, pre + "[%d]" % i):
                yield r
    elif isinstance(o, bool):
        return
    elif isinstance(o, (int, float)):
        yield pre, float(o)


def container_values():
    """value-string -> list of (container, path, raw)"""
    idx = {}
    for p in sorted(glob.glob(os.path.join(PAP, "*.json"))):
        if os.path.basename(p) == os.path.basename(BIND):
            continue
        try:
            d = json.load(io.open(p, encoding="utf-8"))
        except Exception as e:
            warns.append("%s could not be parsed: %s" % (os.path.basename(p), e))
            continue
        for path, v in flatten(d):
            for nd in (3, 4, 5, 6):
                idx.setdefault("%.*f" % (nd, abs(v)), []).append(
                    (os.path.basename(p), path, v))
    return idx


def norm(tok):
    """the forms a container value might take for this printed token"""
    v = float(tok)
    nd = len(tok.split(".")[1])
    return {"%.*f" % (nd, v), "%.*f" % (nd + 1, v), "%.*f" % (max(0, nd - 1), v)}


toks = text_tokens()
idx = container_values()

bound, unbound = {}, {}
for tok, where in sorted(toks.items()):
    kw = set()
    for _, sent in where:
        kw |= keywords(sent)
    hits, weak = [], []
    for form in norm(tok):
        for c, path, raw in idx.get(form, []):
            if abs(abs(raw) - float(tok)) > 0.5 * 10 ** -len(tok.split(".")[1]):
                continue
            pw = path_words(c, path)
            (hits if (kw & pw) else weak).append((c, path))
    if not hits and weak:
        # co-occurrence: if the other numbers in the same sentence agree on a container, a value
        # carried by that same container is bound by the sentence rather than by its own keywords.
        sibling = set()
        for _, sent in where:
            for m2 in TOK.finditer(sent):
                if m2.group(1) == tok:
                    continue
                for form2 in norm(m2.group(1)):
                    for c2, p2, raw2 in idx.get(form2, []):
                        if keywords(sent) & path_words(c2, p2):
                            sibling.add(c2)
        co = [(c2, p2) for c2, p2 in weak if c2 in sibling]
        if co:
            hits = co
    if not hits and weak:
        # the value exists somewhere but in nothing whose name relates to the claim
        unbound[tok] = {"n_sites": len(where),
                        "all_sites_carry_a_citation": all(CITE.search(s) for _, s in where),
                        "value_present_but_unrelated": True,
                        "n_unrelated_deposits": len(set(weak)),
                        "first_site": where[0][1]}
        continue
    if hits:
        seen, ded = set(), []
        for c, path in hits:
            if (c, path) not in seen:
                seen.add((c, path))
                ded.append([c, path])
        bound[tok] = {"n_sites": len(where), "containers": ded[:4], "n_containers": len(ded)}
    else:
        cited = all(CITE.search(sent) for _, sent in where)
        unbound[tok] = {"n_sites": len(where), "all_sites_carry_a_citation": cited,
                        "first_site": where[0][1]}

prev = {}
if os.path.exists(BIND):
    try:
        prev = json.load(io.open(BIND, encoding="utf-8")).get("bound", {})
    except Exception:
        prev = {}

for tok, rec in prev.items():
    if tok not in toks:
        notes.append("%s no longer appears in the text (was bound to %s)"
                     % (tok, rec["containers"][0][0] if rec.get("containers") else "?"))
    elif tok in unbound:
        fails.append("%s was bound to %s and is now supported by no deposit: either the text changed "
                     "or the container did" % (tok, rec["containers"][0][0]
                                               if rec.get("containers") else "?"))

# a container value that is close to a printed one but not equal is the stale-deposit signature
for tok in sorted(unbound):
    v = float(tok)
    near = []
    for form, rows in idx.items():
        try:
            fv = float(form)
        except ValueError:
            continue
        if v and 1e-9 < abs(fv - v) <= max(0.002, abs(v) * 0.004):
            near += [(c, p, raw) for c, p, raw in rows]
    if near:
        c, p, raw = near[0]
        warns.append("%s is in no deposit, but %s%s holds %.6g, within 0.4 per cent. If the text was "
                     "corrected the deposit was not." % (tok, c, p, raw))

# The baseline is the evidence. Rewriting it while reporting drift would certify the new state
# and destroy the record that anything moved, which is the failure mode this checker exists to
# catch. Freeze only on a clean run, or when explicitly asked with --freeze.
if fails and "--freeze" not in sys.argv:
    print("NOT re-freezing the binding: %d failures stand. Fix them, or re-run with --freeze "
          "if the change is intended." % len(fails))
else:
    io.open(BIND, "w", encoding="utf-8", newline="").write(json.dumps({
        "id": "BINDING_r572",
        "what": ("every numeric token of three or more decimals in the manuscript and supplement, and "
                 "the deposits that carry it. Frozen so that a later unbinding is a failure."),
        "n_tokens": len(toks), "n_bound": len(bound), "n_unbound": len(unbound),
        "bound": bound, "unbound": unbound,
    }, indent=1, ensure_ascii=False, sort_keys=True))

print("numeric tokens in the text: %d" % len(toks))
print("   bound to at least one deposit: %d" % len(bound))
unrel = {k: v for k, v in unbound.items() if v.get("value_present_but_unrelated")}
print("   bound to a deposit whose name relates to the claim: %d" % len(bound))
print("   value present only in unrelated deposits:            %d" % len(unrel))
print("   in no deposit at all:                                %d" % (len(unbound) - len(unrel)))
uncited = {k: v for k, v in unbound.items() if not v["all_sites_carry_a_citation"]}
print("   of those, not attributable to a cited work: %d" % len(uncited))
if uncited:
    print("\nnumeric claims with neither a deposit nor a citation:")
    for k in sorted(uncited, key=lambda k: -uncited[k]["n_sites"])[:16]:
        print("   %-10s x%d  %s" % (k, uncited[k]["n_sites"], ascii_safe(uncited[k]["first_site"][:96])))
print()
for f in fails:
    print("  FAIL  %s" % ascii_safe(f))
for w in warns:
    print("  warn  %s" % ascii_safe(w))
for x in notes:
    print("  note  %s" % x)
print("\n=== %d binding failures, %d warnings, %d notes ===" % (len(fails), len(warns), len(notes)))
print("-> BINDING_r572.json")
sys.exit(1 if fails else 0)
