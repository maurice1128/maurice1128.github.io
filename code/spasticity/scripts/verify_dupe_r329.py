# -*- coding: utf-8 -*-
"""Check the §7c.1 duplication fix by reading, not by line-oriented search.

The agent's own grep missed the duplication because "strongest\nrow in the ladder" spans a line
break. This normalises whitespace first, so a phrase cannot hide behind wrapping.
"""
import io, re, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\RESULTS_3d_r214.md"
t = io.open(P, encoding="utf-8").read()
flat = re.sub(r"\s+", " ", t)

for phrase in ("strongest row in the ladder", "cleanest datum in this corpus"):
    n = flat.count(phrase)
    print("%-34s occurrences: %d" % (phrase, n))

# Where does each sit -- live prose or a subordinate note?
for phrase in ("cleanest datum in this corpus",):
    for m in re.finditer(re.escape(phrase), flat):
        s = max(0, m.start() - 190)
        print()
        print("context for '%s':" % phrase)
        print("  ..." + flat[s:m.end() + 40] + "...")
print()
print("file bytes: %d" % os.path.getsize(P))
