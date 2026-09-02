# -*- coding: utf-8 -*-
"""Check the r330 ruling: which provenance file actually carries the OK verdicts, and whether
PROVENANCE_r224.json's own mtime is load-bearing for the r316 conjecture.
"""
import io, json, os, time

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"


def ok_count(f):
    d = json.load(io.open(os.path.join(P, f), encoding="utf-8"))
    n = [0]
    keys = []

    def w(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if "ordering" in k:
                    keys.append(p + "/" + k)
                w(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                w(v, p + "[%d]" % i)
        elif isinstance(o, str) and o.strip() == "OK":
            n[0] += 1
    w(d)
    return n[0], keys, d


for f in ("PROVENANCE.json", "PROVENANCE_r224.json"):
    n, keys, d = ok_count(f)
    mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(os.path.join(P, f))))
    print("%-24s literal 'OK': %-3d ordering fields: %-2d mtime %s" % (f, n, len(keys), mt))

pj = json.load(io.open(os.path.join(P, "PROVENANCE.json"), encoding="utf-8"))
rec = []


def find(o):
    if isinstance(o, dict):
        if "deposit" in o and "deposit_mtime" in o:
            rec.append((o["deposit"], o["deposit_mtime"]))
        for v in o.values():
            find(v)
    elif isinstance(o, list):
        for v in o:
            find(v)


find(pj)
r224 = time.strftime("%Y-%m-%d %H:%M:%S",
                     time.localtime(os.path.getmtime(os.path.join(P, "PROVENANCE_r224.json"))))
print()
print("PROVENANCE_r224.json own mtime : %s" % r224)
for dep, m in rec:
    if str(m).endswith(r224[-8:]):
        print("  coincides with PROVENANCE.json's record for: %s = %s" % (dep, m))
