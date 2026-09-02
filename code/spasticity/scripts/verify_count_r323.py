# -*- coding: utf-8 -*-
"""Independently reproduce both deposit-count rules for RESULTS_3d_r214.md.

Rule A is gen_inventory_r246.py's: backtick-quoted `name.json` inside the body slice that
starts at the first "\n## 0". Rule B is a plain whole-file filename scan. The two differ by
citations that appear only in the front matter, which is why Rule B moves whenever the header
is edited and Rule A does not.
"""
import io, os, re

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
t = io.open(os.path.join(P, "RESULTS_3d_r214.md"), encoding="utf-8").read()
body = t[t.index("\n## 0"):]

A = sorted(set(re.findall(r"`([A-Za-z0-9_]+\.json)`", body)))
B = sorted(set(re.findall(r"([A-Za-z0-9_]+\.json)", t)))
ex = lambda xs: sum(os.path.exists(os.path.join(P, x)) for x in xs)

print("Rule A (generator, body only) : %d cited, %d exist" % (len(A), ex(A)))
print("Rule B (whole file, any)      : %d cited, %d exist" % (len(B), ex(B)))
print("front-matter only             : %s" % sorted(set(B) - set(A)))
