#!/usr/bin/env python3
"""quantifier_audit.py -- a STOP-CONDITION INSTRUMENT, not advice.

DOCUMENTATION RULE OBSERVED HERE: this file is registered by hash, so its documentation carries no
corpus-specific facts -- no counts, no rates, no file names, no catalogue numbers, no superlatives.
A hash protects a file from being CHANGED; it does nothing to protect its claims from becoming
UNTRUE. Measurements against a particular corpus belong in the dated record that made them.

WHY THIS EXISTS.
Repeated measurement of one editing loop found that the mechanical part of a repair is reliable and
the prose written to DESCRIBE the repair is not. A rename executed perfectly at every site still
produced false statements, every one of them in the new sentences characterising the rename. The
edit is reliable; the description of the edit is not, and a manuscript is made of descriptions.

The defects that motivated this tool were mostly of one shape: a claim of completeness over a
collection, asserted without enumerating the collection. The governing rule reads:

    Any claim of completeness, over any collection, must be checked by ENUMERATING THE COLLECTION
    FROM ITS OWN CONTAINER. Any sentence containing 'no', 'only', 'all', 'every', 'none', 'at all',
    or a numeral describing a set carries a domain -- enumerate the domain before writing the word.

The rule was correct and simply not executed. Writing another scope-specific clause would be the
thing the rule exists to stop, so this file turns the rule into something a machine performs.

WHAT IT CANNOT REACH -- and this bound is the important part.
One motivating defect was NOT a completeness claim: an INVERTED MECHANISM ATTRIBUTION, asserting a
quantity moves when it is fixed. It carries no operator, no quantifier and no domain. No
quantifier-scanning instrument can reach it. That is why the known-answer self-test deliberately
does NOT score full marks and exits non-zero rather than claiming success.

    A CLEAN REPORT FROM THIS TOOL IS NOT EVIDENCE THAT PROSE IS SOUND. It excludes, by
    construction, a class of defect that motivated the tool.

WHAT IT DOES.
Given a baseline and a target, it extracts the ADDED prose only, strips the markup constructs that
have repeatedly defeated naive scanners, splits into sentences, and emits one row per sentence
containing a completeness operator -- each with a blank DOMAIN: field the author must fill with the
enumeration that establishes the claim.

NON-EMPTY OUTPUT IS A STOP CONDITION, NOT ADVICE. Exit status 1 means: do not close the round.
The target is not zero. Resolving a flag means writing prose, and writing prose generates flags;
a round reporting zero residue would be a round that stopped writing. The criterion is that every
flag is either enumerated or withdrawn, and the remainder counted and disclosed.

WHAT IT IS NOT.
It cannot tell a true completeness claim from a false one. It locates sentences that carry a domain
and forces the domain to be written down. A filled-in DOMAIN: field is a claim by the author, not a
verification by this script.

FILES READ: exactly the two named on the command line, or the fixture named to --selftest. The run
prints that list in its own output, because a tool that walks a corpus and does not say what it
touched is unauditable by whoever is responsible for the boundary.

USAGE
    python quantifier_audit.py BASELINE TARGET      # audit added prose
    python quantifier_audit.py --validate           # show the stripper's behaviour on a fixture
    python quantifier_audit.py --selftest FIXTURE   # known-answer test

THIS SCRIPT NEVER WRITES A PROJECT FILE. It prints to stdout. A caller redirecting output must open
with newline="" -- writing text with the platform default has silently rewritten every line ending
in this project's deliverables before now.
"""

import argparse
import difflib
import io
import os
import re
import sys

# --------------------------------------------------------------------------------------------
# THE POPULATION. Requirement 3 says a loose rule that flags everything is worthless -- that is the
# lesson that an instrument whose failure list is most of its input has not detected anything.
# The fix is a TIGHTER POPULATION, not a looser rule. So:
#   - bare operators must be whole words;
#   - "no" and "all" are excluded in high-frequency idioms that carry no domain
#     ("no longer", "at all times", "all the same", "not at all" is kept -- it IS a domain claim);
#   - a numeral counts only when it QUANTIFIES A NOUN, not when it is a measurement, a line
#     reference, a byte count, a percentage, a p-value or a version.
# --------------------------------------------------------------------------------------------

# TIGHTENED after measurement: the first operator list flagged most added sentences across
# several real diffs -- the flag-everything failure, in the instrument built to prevent it.
# Dropped because they fire constantly in ordinary prose and almost never carry an
# exhaustiveness claim: "each", "any", "always", "entire", "anywhere", "every one", "each of",
# "all of", "none of", "only one". What is kept is the set that asserts the EXTENT OF A COLLECTION.
WORD_OPS = [
    "no", "only", "all", "every", "none", "never", "both", "neither",
    "remaining", "complete", "exhaustive",
]
PHRASE_OPS = [
    "at all", "the two", "the three", "the four", "the five", "the six",
    "the seven", "the eight", "the nine", "the ten",
    "no other", "nothing else", "the only", "in either", "in both",
]

# Phrases dropped from PHRASE_OPS as non-carrying. Retained HERE as a mask so that dropping
# them actually takes effect -- see the fix in operators_in(). A phrase listed
# here suppresses only the head-word match INSIDE it; the same head word elsewhere in the sentence
# still counts.
DROPPED_PHRASES = [
    "every one", "each of", "all of", "none of", "only one", "any of", "all the same",
]

# SECOND TIGHTENING: an operator counts only when it is near a COLLECTION NOUN. "all" in "all the
# same" or "no" in "no reason" quantifies nothing. A collection noun is a plural, or one of the
# set-denoting singulars this corpus actually uses.
SET_NOUNS = frozenset("""
set collection corpus population registry namespace file directory manuscript table record row
column key entry field group condition run seed reference site occurrence instance sentence case
axis reading revision state backup prediction outcome script artifact defect claim figure value
list item member category element token line count series arm cell rung namespace subset
""".split())
# ROUND 68, DISCLOSED PROVENANCE: the second line above was added AFTER observing that the defect-b
# fix removed a flag on "no LIST of them appears here" -- a sentence round 67 had independently
# found defective. It had been caught only by accident, because "appears" satisfied the loose
# plural rule the fix removed. "list" was absent from this lexicon entirely, which is a genuine
# omission and not a threshold: a list is a collection by definition. The words added are all
# collection nouns this corpus uses. *The provenance is recorded because the edit was prompted by
# seeing which flag disappeared, and a reader must be able to judge whether that is a principled
# lexicon repair or a tuning to a known answer.*

# ROUND 68 FIX (defect b, found by the round-67 cold reader). The generic-plural rule below read
#     len(w) > 4 and w.endswith("s") and not w.endswith(("ss","us","is"))
# which accepts ANY long word ending in s -- "across", "always", "perhaps", "unless", "towards",
# "gives", "carries". That is far looser than the comment above it, and the whole "tighter
# population, not looser rule" argument rests on this gate. The rule is kept (a plural IS the right
# signal) and the non-noun words ending in s are excluded explicitly. Adverbs, prepositions,
# conjunctions and common verb forms only -- NOT nouns, so no collection noun is lost.
NON_NOUN_S = frozenset("""
across always perhaps unless towards upwards downwards afterwards backwards besides thus
nevertheless nonetheless regardless whereas otherwise likewise sometimes anyhow
is was has does goes gives takes makes shows means says needs seems looks
gets puts sets runs holds keeps leaves lives moves comes exists remains appears
carries applies implies varies differs occurs refers rests sits stands yields
its his hers theirs ours yours whose thens plus versus status bias basis
""".split())
_WORD = re.compile(r"[a-z][a-z\-]*")


def _has_collection_noun(window):
    for w in _WORD.findall(window.lower()):
        if w in SET_NOUNS:
            return True
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss") and w[:-1] in SET_NOUNS:
            return True
        if (len(w) > 4 and w.endswith("s") and not w.endswith(("ss", "us", "is"))
                and w not in NON_NOUN_S):
            return True
    return False

# Idioms that contain an operator word but assert nothing about a collection.
IDIOM_EXCLUSIONS = [
    r"\bno longer\b", r"\bno reason\b", r"\bno doubt\b", r"\bat all times\b",
    r"\ball the same\b", r"\bnever mind\b", r"\bevery revision\b",
    r"\bin any case\b", r"\bany\s+of\s+which\b", r"\bnot any more\b",
]

CARDINAL_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight",
                  "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                  "sixteen", "seventeen", "eighteen", "nineteen", "twenty")

# Units that mark a numeral as a MEASUREMENT rather than a set size.
UNIT_WORDS = (
    "b", "kb", "mb", "gb", "byte", "bytes", "s", "ms", "sec", "secs", "second", "seconds",
    "minute", "minutes", "hour", "hours", "hz", "khz", "deg", "degrees", "sd", "sds",
    "px", "pixel", "pixels", "line", "lines", "m", "cm", "mm", "kg", "n", "nm",
)

# Function words that can never be the head noun of a quantified set. Without this, "987,831 B and
# ..." matched num=831 noun=and -- caught by the requirement-1 validation run, not by reasoning.
NOUN_STOPWORDS = frozenset("""
and or but the a an of to in on at by for with from as is are was were be been being that this
these those it its than then so such not no nor if when while which who whom whose there here
""".split())

# numeral + optional adjectives + plural-ish noun, e.g. "three conditions", "13 sites", "four axes".
# The lookbehind must exclude a preceding COMMA and PERIOD as well as word characters, or a
# thousands separator ("987,831") and a decimal ("0.0625") each yield a spurious numeral.
NUMERAL_RE = re.compile(
    r"(?<![\w.,\-])(?P<num>\d{1,4}|" + "|".join(CARDINAL_WORDS) + r")\s+"
    r"(?P<mid>(?:[a-z\-]+\s+){0,2}?)"
    r"(?P<noun>[a-z][a-z\-]{2,})\b",
    re.IGNORECASE,
)


def _is_measurement(num, noun):
    """A numeral is a measurement, not a set size, if its noun is a unit; and it is not a set
    quantifier at all if the following word is a function word."""
    n = noun.lower()
    return n in UNIT_WORDS or n in NOUN_STOPWORDS


# --------------------------------------------------------------------------------------------
# THE STRIPPER. Requirement 1. Four instruments in this project have been defeated by this
# corpus's syntax, the most recent being the round-65 markdown checker, WHICH FAILED ON THE
# SENTENCE DESCRIBING ITSELF. The constructs that did it, each handled explicitly below:
#   (a) markdown emphasis wrapping the token being searched for
#   (b) inline code spans
#   (c) a DOUBLE-backtick span wrapping a single-backtick span
#   (d) blockquote markers, which hide a sentence's leading text
#   (e) fenced code blocks
# The code-span rule below is the CommonMark rule -- an opening run of N backticks is closed by the
# next run of EXACTLY N -- which is what (c) requires. A regex that deletes `+[^`]*`+ consumes the
# opening delimiter of a nested span and leaves its content exposed. That is precisely the bug.
# --------------------------------------------------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```|~~~).*?^\s*\1\s*$", re.S | re.M)
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
EMPHASIS_RE = re.compile(r"(\*{1,3}|_{1,3})")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def strip_markup(text, placeholder=" CODE "):
    """Remove markup that has defeated previous instruments. Code spans are REPLACED with a
    placeholder, never deleted -- deleting them fuses adjacent emphasis markers into a longer run,
    which is how the round-65 checker manufactured six phantom '****' runs."""
    text = FENCE_RE.sub("\n FENCED_CODE \n", text)
    text = CODE_SPAN_RE.sub(placeholder, text)
    text = LINK_RE.sub(r"\1", text)
    text = EMPHASIS_RE.sub("", text)
    # blockquote markers and list bullets: strip the marker, KEEP the text
    out = []
    for ln in text.split("\n"):
        ln = re.sub(r"^\s*>+\s?", "", ln)
        ln = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", ln)
        out.append(ln)
    return "\n".join(out)


def is_table_row(line):
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 2


# --------------------------------------------------------------------------------------------
# ADDED PROSE ONLY
# --------------------------------------------------------------------------------------------

def added_lines(baseline_path, target_path):
    """Return [(target_lineno, text)] for lines present in target and not in baseline."""
    a = io.open(baseline_path, encoding="utf-8", newline="").read().split("\n")
    b = io.open(target_path, encoding="utf-8", newline="").read().split("\n")
    out = []
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("insert", "replace"):
            for j in range(j1, j2):
                out.append((j + 1, b[j]))
    return out


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“‘(⛔⚠★])")

# Length-PRESERVING substitutions. Deleting text shifts every later offset, which is why the first
# version reported "line 8" for all ten hits: the chunk's first line number was used for every
# sentence in it. Offsets must survive stripping if a sentence is to be traced back to its line.
_PAD = lambda m: " " * len(m.group(0))


def _strip_inline_preserving(text):
    """Remove code spans, links and emphasis WITHOUT changing string length."""
    text = CODE_SPAN_RE.sub(_PAD, text)
    text = LINK_RE.sub(lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), text)
    text = EMPHASIS_RE.sub(_PAD, text)
    return text


def _strip_line_markers(line):
    """Strip blockquote '>' and list bullets, replacing with spaces so offsets are preserved.
    This MUST run per line -- the '^' anchor cannot match once lines are joined, which is how
    '>' markers leaked into the first version's reported sentences."""
    m = re.match(r"^(\s*(?:>+\s?)+)", line)
    if m:
        line = " " * len(m.group(1)) + line[len(m.group(1)):]
    m = re.match(r"^(\s*(?:[-*+]|\d+\.)\s+)", line)
    if m:
        line = " " * len(m.group(1)) + line[len(m.group(1)):]
    return line


def fenced_line_numbers(path):
    """1-based line numbers inside fenced code blocks, so they can be excluded outright."""
    inside, out, fence = False, set(), None
    for i, ln in enumerate(io.open(path, encoding="utf-8", newline="").read().split("\n"), 1):
        m = re.match(r"^\s*(```+|~~~+)", ln)
        if m and not inside:
            inside, fence = True, m.group(1)[:3]
            out.add(i)
        elif m and inside and m.group(1).startswith(fence):
            inside = False
            out.add(i)
        elif inside:
            out.add(i)
    return out


def sentences_with_lines(pairs, fenced=frozenset()):
    """Chunk added lines into paragraphs and split into sentences, tracing each sentence back to
    the line its first character came from."""
    chunks, cur = [], []
    for ln, txt in pairs:
        if txt.strip() == "" or ln in fenced or is_table_row(txt):
            if cur:
                chunks.append(cur); cur = []
        else:
            cur.append((ln, _strip_line_markers(txt)))
    if cur:
        chunks.append(cur)
    results = []
    for chunk in chunks:
        joined, offsets, pos = [], [], 0
        for ln, t in chunk:
            joined.append(t)
            offsets.append((pos, ln))
            pos += len(t) + 1
        blob = _strip_inline_preserving(" ".join(joined))
        for m in _iter_sentences(blob):
            s = re.sub(r"\s+", " ", m.group(0)).strip()
            if len(s) <= 3:
                continue
            ln = offsets[0][1]
            for off, l in offsets:
                if off <= m.start():
                    ln = l
                else:
                    break
            results.append((ln, s))
    return results


def _iter_sentences(blob):
    start = 0
    for m in SENT_SPLIT.finditer(blob):
        yield re.compile(r".*", re.S).match(blob, start, m.start())
        start = m.end()
    if start < len(blob):
        yield re.compile(r".*", re.S).match(blob, start, len(blob))


# --------------------------------------------------------------------------------------------
# MATCHING
# --------------------------------------------------------------------------------------------

def operators_in(sentence):
    low = sentence.lower()
    for pat in IDIOM_EXCLUSIONS:
        low = re.sub(pat, " ", low)
    hits = []
    WINDOW = 60  # characters after the operator in which a collection noun must appear
    for p in PHRASE_OPS:
        for m in re.finditer(r"(?<![\w])" + re.escape(p) + r"(?![\w])", low):
            if _has_collection_noun(low[m.start():m.end() + WINDOW]):
                hits.append(p)
                break
    # ROUND 68 FIX (defect c, found by the round-67 cold reader). DROPPED_PHRASES were removed from
    # PHRASE_OPS on the stated ground that they "fire constantly and almost never carry an
    # exhaustiveness claim" -- but WORD_OPS still contains their head words (every, all, none,
    # only, each, any), and (?<![\w-])every(?![\w-]) matches inside "every one". So removing them
    # from the phrase list achieved NOTHING: they kept firing through the head word. The head-word
    # scan below runs against a MASKED copy in which each dropped phrase is blanked, so a head word
    # counts only when it occurs outside one.
    masked = low
    for p in DROPPED_PHRASES:
        masked = re.sub(r"(?<![\w])" + re.escape(p) + r"(?![\w])",
                        lambda m: " " * len(m.group(0)), masked)
    for w in WORD_OPS:
        for m in re.finditer(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", masked):
            if _has_collection_noun(masked[m.start():m.end() + WINDOW]):
                hits.append(w)
                break
    # A numeral counts only when DEFINITE -- "the two files", "all three rows", "four of the five".
    # A bare "16 runs" is a measurement report, not a claim about a set's extent, and including it
    # was most of the first version's false-positive volume.
    for m in NUMERAL_RE.finditer(low):
        num, noun = m.group("num"), m.group("noun")
        if _is_measurement(num, noun):
            continue
        pre = low[max(0, m.start() - 12):m.start()]
        if not re.search(r"\b(the|all|only|both|these|those|its|our)\s*$", pre):
            continue
        hits.append("#%s %s" % (num, noun))
    # de-duplicate, keep order, drop a word op subsumed by a phrase op containing it
    seen, out = set(), []
    joined_phrases = " ".join(h for h in hits if " " in h and not h.startswith("#"))
    for h in hits:
        if h in seen:
            continue
        if " " not in h and not h.startswith("#") and re.search(r"(?<![\w])" + re.escape(h) + r"(?![\w])", joined_phrases):
            continue
        seen.add(h)
        out.append(h)
    return out


def audit(baseline, target, show_clean=False):
    rows = []
    for lineno, sent in sentences_with_lines(added_lines(baseline, target)):
        ops = operators_in(sent)
        if ops:
            rows.append((lineno, ops, sent))
    return rows


def read_report(paths):
    """State, in the OUTPUT, which files this run read.

    A docstring is a claim; output is a record. This exists because a boundary breach was
    found in a sibling instrument: a reviewer honouring a prohibition on opening certain
    files invoked a tool that opened them on the reviewer's behalf. Every prohibition in this
    project is phrased as a rule about what a READER opens, and a tool the reader invokes
    obeys no such rule. A tool that walks a tree and does not say what it touched is
    unauditable by the person responsible for the boundary.
    """
    out = ["\n" + "-" * 100 + "\n", "FILES READ BY THIS RUN (contents opened, not merely named):\n"]
    for p in paths:
        out.append("    %s\n" % p)
    out.append("Nothing else was opened. This tool reads only the two files named on the\n")
    out.append("command line (or, in --selftest, the fixtures it names above).\n")
    return "".join(out)


def emit(rows, target, total_sentences):
    w = sys.stdout
    w.write("=" * 100 + "\n")
    w.write("QUANTIFIER AUDIT -- %s\n" % target)
    w.write("=" * 100 + "\n")
    if not rows:
        w.write("\nNo completeness or quantifier claim found in the added prose.\n")
        w.write("Added prose sentences scanned: %d\n" % total_sentences)
        return 0
    w.write("\n%d of %d added sentences carry a completeness operator.\n" % (len(rows), total_sentences))
    w.write("EACH REQUIRES A DOMAIN. Fill every DOMAIN: field with the enumeration that\n")
    w.write("establishes the claim -- from the collection's own container, per WATCHDOG #324.\n\n")
    for i, (lineno, ops, sent) in enumerate(rows, 1):
        w.write("-" * 100 + "\n")
        w.write("[%d] line %d   operators: %s\n" % (i, lineno, ", ".join(ops)))
        w.write("    %s\n" % sent)
        w.write("    DOMAIN: \n")
    w.write("-" * 100 + "\n")
    w.write("\nSTOP CONDITION: %d unfilled DOMAIN fields. Do not close the round.\n" % len(rows))
    return 1


# --------------------------------------------------------------------------------------------
# REQUIREMENT 1 -- validate the extractor against the corpus's real syntax BEFORE trusting it.
# --------------------------------------------------------------------------------------------

VALIDATION_FIXTURE = """\
Plain sentence with no operator at all here.

**Bold claim: all six groups are present.**

> Blockquoted: the only survivors are in this box.

A code span `all of them` must NOT be scanned.

A double-backtick span `` `**` `` wrapping a backtick span -- this is the construct that
defeated the round-65 checker.

```
fenced code: every one of these is invisible
```

| table | row | with every operator |
|---|---|---|

Measurement numerals: 987,831 B and 0.0625 and 16 runs and three conditions.

Definite numerals: excluding the two files above 200 kB, and all three rows are present.

The file is 122081 bytes and grew by 2 lines.

No reason to worry and it is no longer relevant.
"""


def _fixture_fenced():
    inside, out = False, set()
    for i, ln in enumerate(VALIDATION_FIXTURE.split(chr(10)), 1):
        if re.match(r"^\s*```", ln):
            out.add(i)
            inside = not inside
        elif inside:
            out.add(i)
    return out


def run_validation():
    print("=" * 100)
    print("REQUIREMENT 1 -- EXTRACTOR VALIDATION. Read this output; do not assume it.")
    print("=" * 100)
    print("\n--- RAW FIXTURE ---")
    print(VALIDATION_FIXTURE)
    stripped = strip_markup(VALIDATION_FIXTURE)
    print("--- AFTER strip_markup() ---")
    print(stripped)
    print("--- PER-LINE TABLE-ROW CLASSIFICATION ---")
    for i, ln in enumerate(VALIDATION_FIXTURE.split("\n"), 1):
        if ln.strip():
            print("  line %-3d table=%-5s | %s" % (i, is_table_row(ln), ln[:70]))
    print("\n--- SENTENCES AND OPERATOR MATCHES ---")
    pairs = [(i, t) for i, t in enumerate(VALIDATION_FIXTURE.split("\n"), 1)]
    for lineno, sent in sentences_with_lines(pairs, _fixture_fenced()):
        ops = operators_in(sent)
        print("  line %-3d ops=%-28s | %s" % (lineno, ",".join(ops) if ops else "-", sent[:80]))
    print("\nEYEBALL CHECKLIST -- these encode the TIGHTENED rules, not the first draft's.")
    print("  (This list was itself stale once: it still demanded numeral hits for bare '16 runs'")
    print("   after the numeral rule had been narrowed to definite forms. A checklist is a")
    print("   description and goes stale exactly like any other description.)")
    print("  * code-span content must NOT appear above  ('all of them')")
    print("  * the double-backtick construct must be fully consumed, leaving no bare asterisks")
    print("  * fenced content must NOT appear ('every one of these'), and its lines are excluded")
    print("  * blockquote text MUST appear, without its '>' marker")
    print("  * table rows must be classified table=True and excluded from prose")
    print("  * each sentence's reported line number must be the line it STARTS on, not the")
    print("    first line of its paragraph")
    print("  * '987,831 B', '0.0625', '122081 bytes' must NOT produce numeral hits")
    print("  * BARE 'three conditions' / '16 runs' must NOT flag -- indefinite numerals are")
    print("    measurement reports, and including them was most of the first draft's volume")
    print("  * DEFINITE 'the two files' / 'all three rows' MUST flag -- they claim a set's extent")
    print("  * 'no reason' and 'no longer' must NOT flag -- idiom exclusions")


# --------------------------------------------------------------------------------------------
# REQUIREMENT 2 -- known-answer self-test.
# --------------------------------------------------------------------------------------------

TARGET_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def run_selftest(fixture_path):
    """Score ONLY the numbered target sentences. The fixture's own explanatory prose is not part of
    the known answer -- scoring it would let the tool pass by flagging commentary."""
    print("=" * 100)
    print("REQUIREMENT 2 -- KNOWN-ANSWER SELF-TEST")
    print("Each numbered target is a real false statement this project published and retracted.")
    print("=" * 100)
    text = io.open(fixture_path, encoding="utf-8", newline="").read()
    targets = []
    for i, ln in enumerate(text.split("\n"), 1):
        m = TARGET_RE.match(ln.strip())
        if m:
            targets.append((i, int(m.group(1)), strip_markup(m.group(2))))
    caught = 0
    for lineno, num, sent in targets:
        ops = operators_in(sent)
        if ops:
            caught += 1
        print("\n  [%d] %s  line %d" % (num, "FLAGGED" if ops else "*** MISSED ***", lineno))
        print("      ops: %s" % (", ".join(ops) if ops else "(none)"))
        print("      %s" % sent[:150])
    sys.stdout.write(read_report([fixture_path]))
    print("\n" + "=" * 100)
    print("  RESULT: %d of %d known-false target sentences flagged." % (caught, len(targets)))
    if caught < len(targets):
        print("  *** THE TOOL DOES NOT CATCH EVERY DEFECT THAT MOTIVATED IT. ***")
        print("  Do not claim it works. The missed targets are recorded in the fixture header.")
    print("=" * 100)
    return 0 if caught == len(targets) else 1


def main():
    # The corpus contains U+26A0 and en/em dashes. A Windows console defaults to a legacy codepage
    # and raises UnicodeEncodeError mid-report -- which a caller counting
    # lines with grep reads as a SMALL PLAUSIBLE NUMBER rather than as a failure. That is the same
    # class as every other pattern artifact this project has logged, so the encoding is forced
    # rather than left to the environment.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", nargs="?")
    ap.add_argument("target", nargs="?")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--selftest", metavar="FIXTURE")
    a = ap.parse_args()
    if a.validate:
        run_validation()
        return 0
    if a.selftest:
        return run_selftest(a.selftest)
    if not (a.baseline and a.target):
        ap.error("need BASELINE and TARGET, or --validate, or --selftest FIXTURE")
    for p in (a.baseline, a.target):
        if not os.path.isfile(p):
            ap.error("no such file: %s" % p)
    pairs = added_lines(a.baseline, a.target)
    sents = sentences_with_lines(pairs, fenced_line_numbers(a.target))
    rows = [(ln, operators_in(s), s) for ln, s in sents]
    rows = [(ln, ops, s) for ln, ops, s in rows if ops]
    rc = emit(rows, a.target, len(sents))
    sys.stdout.write(read_report([a.baseline, a.target]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
