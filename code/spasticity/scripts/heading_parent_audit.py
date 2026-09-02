#!/usr/bin/env python3
"""heading_parent_audit.py -- round 73. Detects ONE structural class, precisely.

WHY THIS EXISTS.
A subsection was once inserted into the middle of a section of one of this project's
manuscripts. The insertion was correct at every line it added. It nevertheless broke the
document: several paragraphs of
7.1's body came to sit under a heading about a different subject, leaving a sentence reading "REFCAL
tracks LOSO ... in this column" pointing at a block with no column, and a sentence reading "this is
reported before the confirmed predictions" sitting BELOW a confirmed prediction.

NO EXISTING INSTRUMENT IN THIS PROJECT COULD SEE IT:
  * a diff-scoped prose auditor saw nothing, because the orphaned lines were UNCHANGED;
  * emphasis-balance, code-span, lazy-continuation and line-ending checks all returned clean;
  * the byte count rose exactly as an insertion should.
A human reading the section in order found it in one pass.

Round 72 asserted that no line-oriented or diff-oriented instrument could detect this class. A cold
reader refuted that constructively, and this file is that refutation implemented:

    FOR EVERY UNCHANGED LINE, COMPUTE ITS NEAREST PRECEDING HEADING IN THE BASELINE AND IN THE
    TARGET. REPORT ANY LINE WHOSE PARENT HEADING CHANGED.

An unchanged line is text the author did not touch. If its parent heading moved, the author changed
what the document SAYS that line is about, without changing the line. That is the class.

WHAT IT IS NOT.
It is not another attempt to lower the defect rate; earlier such attempts have been
pre-registered and disconfirmed. It detects one structural class and its success criterion is whether it flags a known
real incident, not whether any rate moves. It cannot judge whether a re-parenting is WRONG -- moving
a paragraph under a new heading deliberately is a legitimate edit, and this tool will flag it. It
locates re-parented text and makes the author confirm the move was intended.

KNOWN BLIND SPOTS -- properties of the ALGORITHM, stated because the declared ones are the
transferable part. Deliberately free of corpus-specific facts: no counts, no file names, no
"largest gap" claims. Those age, and a sealed artifact must not carry a claim about a world that
moves -- the hash protects the logic, and the logic does not rot. Current measurements against any
particular corpus belong in the dated round file that made them.
  * BOLD PSEUDO-HEADINGS ARE INVISIBLE. A line-initial bold run used as a de-facto heading is
    not a heading; every line under it keeps the enclosing ATX heading as its parent, so any
    boundary moved within such a span is undetectable.
  * SETEXT HEADINGS (underlined with === or ---) are not recognised. ATX only.
  * DUPLICATE HEADING TEXT defeats it: parenthood is compared by heading string, so moving
    text under a different heading with identical text is silent.
  * INDENTED HEADINGS are missed. CommonMark permits up to three leading spaces on an ATX
    heading; the regex here is anchored at column 0.
  * PHYSICAL MOVES are missed. difflib scores a relocated paragraph as delete+insert, never
    'equal'. This catches headings moving around stationary text, not text moving between
    headings.
  * MIXED LINE ENDINGS DISABLE IT ENTIRELY: a CRLF baseline against an LF target has zero
    equal lines and therefore zero findings. It reports clean and means nothing.
  * EDITING the orphaned text in the same commit hides the orphaning, by construction.
  * HEADING RENAMES are the dominant FALSE POSITIVE: retitling a heading re-parents its whole
    body by this tool's definition, so every line under it is reported.

USAGE
    python heading_parent_audit.py BASELINE TARGET
    python heading_parent_audit.py --selftest        # positive AND negative control

EXIT STATUS -- note that --selftest OVERLOADS these with different meanings.
  audit mode (BASELINE TARGET):
    0  no unchanged line was re-parented
    1  re-parented lines found (a stop condition, not advice)
    2  usage error
  --selftest mode:
    0  both controls passed
    1  THE DETECTOR FAILED ITS OWN SUCCESS CRITERION -- not a document defect
    2  the self-test could not be run (a pre-image is missing)
  A caller keyed on the audit-mode meanings would misread a self-test failure as a
  document defect. Do not wire both into one CI check.

Output goes to stdout only; this script never writes a project file.
"""

import argparse
import difflib
import io
import os
import re
import sys

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*(```+|~~~+)")


def headings_by_line(lines):
    """For each 0-based line index, the nearest preceding heading text (or None).

    Headings inside fenced code blocks are ignored -- a '# comment' in a shell block is not a
    section. Getting this wrong would manufacture re-parenting on every code block, which is the
    kind of format-blindness this project has logged repeatedly.
    """
    out = []
    cur = None
    in_fence = False
    fence_ch = None
    fence_len = 0
    for ln in lines:
        m = FENCE.match(ln)
        if m:
            run = m.group(1)
            ch, ln_len = run[0], len(run)
            rest = ln[m.end():].strip()
            if not in_fence:
                in_fence, fence_ch, fence_len = True, ch, ln_len
            elif ch == fence_ch and ln_len >= fence_len and rest == "":
                # CommonMark: a closing fence must be AT LEAST as long as the opener and
                # must carry no info string. Truncating to 3 chars let a ```` block be
                # closed by an inner ```, which manufactured a phantom heading.
                in_fence = False
            out.append(cur)
            continue
        if not in_fence:
            h = HEADING.match(ln)
            if h:
                cur = "%s %s" % (h.group(1), h.group(2))
                out.append(cur)
                continue
        out.append(cur)
    return out


def reparented(baseline_lines, target_lines):
    """[(target_lineno, text, old_parent, new_parent)] for UNCHANGED lines whose parent changed."""
    bh = headings_by_line(baseline_lines)
    th = headings_by_line(target_lines)
    sm = difflib.SequenceMatcher(None, baseline_lines, target_lines, autojunk=False)
    hits = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            continue
        for k in range(i2 - i1):
            bi, tj = i1 + k, j1 + k
            if baseline_lines[bi].strip() == "":
                continue
            if HEADING.match(target_lines[tj]):
                continue          # a heading is not re-parented by itself
            if bh[bi] != th[tj]:
                hits.append((tj + 1, target_lines[tj], bh[bi], th[tj]))
    return hits


def group(hits):
    """Collapse consecutive lines sharing the same (old,new) parent into one finding."""
    out = []
    for h in hits:
        if out and out[-1][3] == h[2] and out[-1][4] == h[3] and h[0] == out[-1][1] + 1:
            out[-1][1] = h[0]
            out[-1][2] += 1
        else:
            out.append([h[0], h[0], 1, h[2], h[3], h[1]])
    return out


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


def emit(hits, target):
    w = sys.stdout
    w.write("=" * 100 + "\n")
    w.write("HEADING-PARENT AUDIT -- %s\n" % target)
    w.write("=" * 100 + "\n")
    if not hits:
        w.write("\nNo unchanged line changed its parent heading.\n")
        return 0
    g = group(hits)
    w.write("\n%d unchanged lines were RE-PARENTED, in %d run(s).\n" % (len(hits), len(g)))
    w.write("Each run is text the author did not edit that now sits under a different heading.\n")
    w.write("Confirm each move was intended, or the insertion has orphaned it.\n\n")
    for a, b, n, old, new, first in g:
        w.write("-" * 100 + "\n")
        w.write("lines %d-%d  (%d lines)\n" % (a, b, n))
        w.write("    WAS under: %s\n" % (old if old else "(no heading)"))
        w.write("    NOW under: %s\n" % (new if new else "(no heading)"))
        w.write("    first line: %s\n" % first.strip()[:90])
    w.write("-" * 100 + "\n")
    w.write("\nSTOP CONDITION: %d re-parented lines. Confirm or repair.\n" % len(hits))
    return 1


# --------------------------------------------------------------------------------------------
# SELF-TEST. The positive control RE-ENACTS a past splice: the inserted block and the baseline
# are both lifted from retained pre-images, but the splice ANCHOR is a literal in this file and
# NO RETAINED PRE-IMAGE CONTAINS THE BROKEN ARRANGEMENT -- it was repaired before a backup was
# taken. So this is a faithful re-enactment, NOT a reconstruction from evidence, and an earlier
# version of this comment overclaimed by calling it the latter.
#
# The anchor is not cherry-picked: an independent reviewer re-ran the positive control at every
# possible splice position inside the section; all but the last few flag, and the ones that do
# not are immediately before the next heading, where an insertion re-parents nothing.
#
# THE NEGATIVE CONTROL IS WEAK and is labelled so: the correctly-placed target puts the
# insertion immediately before the next heading, one of the few positions that cannot flag for
# any reason internal to the re-parenting logic. It exercises heading assignment over the whole
# file and would catch an off-by-one or a fence bug, but it does not test discrimination.
# The evidence that does is a sweep over adjacent pairs of real history; that measurement is
# corpus-specific and therefore lives in the dated round file that made it, not here.
# --------------------------------------------------------------------------------------------

PAPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper")


def _read(name):
    return io.open(os.path.join(PAPER, name), encoding="utf-8", newline="").read().split("\n")


def run_selftest():
    print("=" * 100)
    print("SELF-TEST -- the round-71 splice, reconstructed from retained pre-images")
    print("=" * 100)
    try:
        base = _read(".bak_r86_RESULTS_discrimination.md")   # before 7.1.1 existed
        good = _read(".bak_r87_RESULTS_discrimination.md")   # 7.1.1 in its CORRECT position
    except OSError as e:
        print("cannot run: %s" % e)
        return 2

    # lift the 7.1.1 block out of the good target
    s, e = None, None
    for i, ln in enumerate(good):
        if ln.startswith("#### 7.1.1"):
            s = i
        elif s is not None and ln.startswith("### 7.2"):
            e = i
            break
    if s is None or e is None:
        print("cannot locate the 7.1.1 block in .bak_r87_; self-test not run")
        return 2
    block = good[s:e]
    print("  lifted the 7.1.1 block from .bak_r87_: %d lines" % len(block))

    # POSITIVE CONTROL: splice it where round 71 actually put it -- immediately after the 7.1
    # table, i.e. before the REFCAL paragraph, which is what orphaned 7.1's body.
    anchor = None
    for i, ln in enumerate(base):
        if ln.startswith("**REFCAL tracks LOSO to within about two points"):
            anchor = i
            break
    if anchor is None:
        print("cannot locate the REFCAL paragraph in .bak_r86_; self-test not run")
        return 2
    bad = base[:anchor] + block + base[anchor:]
    print("  spliced it at line %d (mid-section), reproducing the round-71 arrangement" % (anchor + 1))

    print("\n--- POSITIVE CONTROL: baseline -> spliced ---")
    hits = reparented(base, bad)
    rc_pos = emit(hits, "<reconstructed splice>")

    print("\n--- NEGATIVE CONTROL: baseline -> correctly-placed (.bak_r87_) ---")
    hits2 = [h for h in reparented(base, good)]
    rc_neg = emit(hits2, ".bak_r87_RESULTS_discrimination.md")

    print("\n" + "=" * 100)
    ok_pos = rc_pos == 1
    ok_neg = rc_neg == 0
    sys.stdout.write(read_report([os.path.join(PAPER, ".bak_r86_RESULTS_discrimination.md"),
                                  os.path.join(PAPER, ".bak_r87_RESULTS_discrimination.md")]))
    print("=" * 100)
    print("  POSITIVE control (must flag):     %s" % ("PASS" if ok_pos else "*** FAIL ***"))
    print("  NEGATIVE control (must not flag): %s" % ("PASS" if ok_neg else "*** FAIL ***"))
    if not (ok_pos and ok_neg):
        print("  *** THE DETECTOR DOES NOT MEET ITS SUCCESS CRITERION. Do not claim it works. ***")
    print("=" * 100)
    return 0 if (ok_pos and ok_neg) else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", nargs="?")
    ap.add_argument("target", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return run_selftest()
    if not (a.baseline and a.target):
        ap.error("need BASELINE and TARGET, or --selftest")
    for p in (a.baseline, a.target):
        if not os.path.isfile(p):
            ap.error("no such file: %s" % p)
    b = io.open(a.baseline, encoding="utf-8", newline="").read().split("\n")
    t = io.open(a.target, encoding="utf-8", newline="").read().split("\n")
    rc = emit(reparented(b, t), a.target)
    sys.stdout.write(read_report([a.baseline, a.target]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
