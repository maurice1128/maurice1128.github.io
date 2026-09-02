# -*- coding: utf-8 -*-
"""Round 134. Run the manuscript's tightened grep, as defined at
METHODS_contribution.md:614-616 (population) and :618-622 (matching rule),
against the case that motivated it: REFCAL.

Population, quoted from :614-616:
    "a registered outcome is a key in the **top two levels** of a result JSON
     -- a quantity the analysis chose to *report*, not one it happened to name
     internally -- plus the `PR<n>` prediction labels."

Matching rule, quoted from :619-621:
    "Case-**sensitive**; word-boundary on both sides; **`holdout_l` does not
     count as a hit for `holdout`**"

NOTHING is modified to make it pass. Depth variants are reported separately.
"""
import io, json, re, os

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RJSON = os.path.join(PAPER, "VIDEO_DEGRADATION.json")
MSS = [os.path.join(PAPER, "METHODS_contribution.md"),
       os.path.join(PAPER, "RESULTS_discrimination.md")]

d = json.load(io.open(RJSON, encoding="utf-8"))


def keys_at(obj, depth, want, out):
    """Collect dict keys at exactly `depth`. Lists are traversed WITHOUT
    consuming a level (a list is not a naming level); this is one of the
    ambiguities and is reported."""
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


lv = {}
for n in (1, 2, 3, 4):
    s = set()
    keys_at(d, 1, n, s)
    lv[n] = s

pop_top2 = lv[1] | lv[2]
print("=" * 72)
print("POPULATION, as defined: keys in the TOP TWO LEVELS of the result JSON")
print("=" * 72)
print("level 1 keys: %d" % len(lv[1]))
print("  ", sorted(lv[1]))
print("level 2 keys: %d" % len(lv[2]))
print("  ", sorted(lv[2])[:40])
print("level 3 keys: %d" % len(lv[3]))
print("  ", sorted(lv[3])[:40])
print("level 4 keys: %d" % len(lv[4]))
print("  ", sorted(lv[4])[:40])
print()
print("population size (levels 1+2) = %d" % len(pop_top2))

# --- THE QUESTION ---
def has_refcal(s):
    return sorted([k for k in s if "refcal" in k.lower()])

print()
print("=" * 72)
print("IS REFCAL IN THE POPULATION?")
print("=" * 72)
for n in (1, 2, 3, 4):
    print("  level %d: refcal-bearing keys -> %r" % (n, has_refcal(lv[n])))
print()
print("  IN POPULATION (top two levels): %r" % (has_refcal(pop_top2),))
print("  >>> FLAGGED BY THE DEFINED GREP? %s" % ("YES" if has_refcal(pop_top2) else "NO"))

# --- the caveat: 720 is a string count, not evidence about depth ---
raw = io.open(RJSON, encoding="utf-8").read()
print()
print("string occurrences of 'refcal' (case-insensitive) in the file: %d"
      % len(re.findall("refcal", raw, re.I)))
print("string occurrences of 'refcal' (case-SENSITIVE, as defined):   %d"
      % len(re.findall("refcal", raw)))
print("string occurrences of 'REFCAL' (upper):                        %d"
      % len(re.findall("REFCAL", raw)))
print("  ^ these are STRING counts. They say nothing about JSON depth.")

# --- where do the refcal keys actually live? ---
paths = []
def walk(obj, path):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "refcal" in k.lower():
                paths.append(path + [k])
            walk(v, path + [k])
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + ["[%d]" % i])

walk(d, [])
print()
print("distinct refcal key PATHS: %d ; first 5:" % len(paths))
for p in paths[:5]:
    print("   depth %d : %s" % (len(p), " > ".join(str(x) for x in p)))
depths = sorted(set(len(p) for p in paths))
print("depths at which refcal keys occur: %r" % (depths,))

# --- would the grep have found it in the manuscripts anyway? (the second half) ---
print()
print("=" * 72)
print("SECOND HALF: does the name appear in the manuscripts?")
print("=" * 72)
for m in MSS:
    txt = io.open(m, encoding="utf-8").read()
    for name in ("refcal", "REFCAL"):
        n = len(re.findall(r"(?<![A-Za-z0-9_])" + name + r"(?![A-Za-z0-9_])", txt))
        print("  %-28s %-8s -> %d" % (os.path.basename(m), name, n))
