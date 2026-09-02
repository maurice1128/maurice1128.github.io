# -*- coding: utf-8 -*-
"""Round 134, part 2. Completeness + positive control + the PR<n> channel."""
import io, json, re, os, glob

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
MSS = {"METHODS": os.path.join(PAPER, "METHODS_contribution.md"),
       "RESULTS": os.path.join(PAPER, "RESULTS_discrimination.md")}
TXT = dict((k, io.open(v, encoding="utf-8").read()) for k, v in MSS.items())


def keys_at(obj, depth, want, out):
    if depth > want:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if depth == want:
                out.add(k)
            keys_at(v, depth + 1, want, out)
    elif isinstance(obj, list):
        for v in obj:
            keys_at(v, depth, want, out)


print("=" * 74)
print("A. ALL result JSONs: does 'refcal' EVER sit in the top two levels?")
print("   (the definition says 'a result JSON' and does not say which files)")
print("=" * 74)
files = sorted(glob.glob(os.path.join(PAPER, "*.json")))
tot_pop = set()
anywhere = []
for f in files:
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception as e:
        print("  %-34s UNPARSEABLE (%s)" % (os.path.basename(f), e.__class__.__name__))
        continue
    s1, s2 = set(), set()
    keys_at(d, 1, 1, s1)
    keys_at(d, 1, 2, s2)
    pop = s1 | s2
    tot_pop |= pop
    hits = [k for k in pop if "refcal" in k.lower()]
    deep = "refcal" in io.open(f, encoding="utf-8").read().lower()
    if hits:
        anywhere.append(f)
    print("  %-34s |L1|=%-3d |L2|=%-4d top2=%-4d  refcal in top2: %-5s  in file: %s"
          % (os.path.basename(f), len(s1), len(s2), len(pop),
             bool(hits), deep))

print()
print("  union population over ALL result JSONs (top two levels) = %d names" % len(tot_pop))
print("  files where refcal reaches the top two levels: %r" % anywhere)
print("  >>> DEFINED GREP FLAGS REFCAL ANYWHERE? %s" % ("YES" if anywhere else "NO"))

print()
print("=" * 74)
print("B. POSITIVE CONTROL, required by the manuscript at :625")
print("   'without which no zero may be read as an absence'")
print("=" * 74)


def wb(name, txt):
    return len(re.findall(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", txt))


for probe in ("ank_rom", "refcal_mean", "refcal_sd", "rom_spastic", "margin_gap"):
    inpop = probe in tot_pop
    print("  %-14s in top-2 population: %-5s   METHODS=%-3d RESULTS=%-3d"
          % (probe, inpop, wb(probe, TXT["METHODS"]), wb(probe, TXT["RESULTS"])))
print("  ^ ank_rom fires on this corpus, so a zero elsewhere is an absence, not a dead pattern.")

print()
print("=" * 74)
print("C. THE PR<n> CHANNEL - the other half of the defined population")
print("=" * 74)
print("  METHODS:529 says the registration 'predicts its behaviour by name under V-PR4'.")
for lab in ("V-PR1", "V-PR2", "V-PR3", "V-PR4", "V-PR5"):
    print("    %-6s  METHODS=%-3d RESULTS=%-3d" % (lab, wb(lab, TXT["METHODS"]), wb(lab, TXT["RESULTS"])))
print("  ^ if V-PR4 is PRESENT in the manuscripts, the PR channel reports the")
print("    prediction as covered while the quantity it predicts is absent.")

print()
print("=" * 74)
print("D. THE MANUSCRIPT'S OWN REPORTED POPULATION SIZE")
print("=" * 74)
m = re.search(r"flags \*\*(\d+) of (\d+)\*\*", TXT["METHODS"])
print("  METHODS:637 reports: %s" % (m.group(0) if m else "NOT FOUND"))
print("  union top-2 population measured here: %d" % len(tot_pop))
print("  ^ the reported denominator and the measured one are different numbers;")
print("    which files the grep scanned is not stated in the text.")
