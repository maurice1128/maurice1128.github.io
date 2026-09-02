# -*- coding: utf-8 -*-
"""r412 checks 1-4: PREREG hashes, registration->deposit coverage, JSON health, protected dirs.
READ-ONLY on SCONE results."""
import glob
import hashlib
import json
import os
import re
import sys
import time

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
RES = r"C:\Users\maurice\Documents\SCONE\results"

PROT = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")
OPT = re.compile(r"^opt_s[1-4]")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_preregs():
    out = {"registrations": {}, "no_sidecar": [], "hash_mismatch": [], "ok": []}
    for md in sorted(glob.glob(os.path.join(PAPER, "PREREG_*.md"))):
        base = os.path.basename(md)
        if base.startswith(".bak"):
            continue
        cands = [md + ".sha256", os.path.splitext(md)[0] + ".sha256",
                 os.path.splitext(md)[0] + ".checksum.sha256"]
        side = [c for c in cands if os.path.exists(c)]
        rec = {"file": base, "size": os.path.getsize(md), "actual_sha256": sha256(md)}
        if not side:
            rec["status"] = "NO_SIDECAR"
            out["no_sidecar"].append(base)
        else:
            rec["sidecar"] = os.path.basename(side[0])
            txt = open(side[0], "r", errors="replace").read()
            found = re.findall(r"\b[0-9a-fA-F]{64}\b", txt)
            rec["recorded_sha256"] = found
            if any(f.lower() == rec["actual_sha256"] for f in found):
                rec["status"] = "MATCH"
                out["ok"].append(base)
            else:
                rec["status"] = "MISMATCH"
                out["hash_mismatch"].append(base)
        out["registrations"][base] = rec
    out["n_registrations"] = len(out["registrations"])
    out["n_match"] = len(out["ok"])
    out["n_no_sidecar"] = len(out["no_sidecar"])
    out["n_mismatch"] = len(out["hash_mismatch"])
    return out


def json_health():
    bad = {}
    files = [f for f in sorted(glob.glob(os.path.join(PAPER, "*.json")))
             if not os.path.basename(f).startswith(".bak")]
    parse_fail, nan_hits, empty = [], {}, []
    for f in files:
        b = os.path.basename(f)
        raw = open(f, "r", errors="replace").read()
        if not raw.strip():
            empty.append(b)
            continue
        # literal NaN / Infinity tokens are invalid JSON and break strict readers
        toks = re.findall(r"(?<![\"\w])(NaN|-?Infinity)(?![\"\w])", raw)
        if toks:
            nan_hits[b] = {"n": len(toks), "tokens": sorted(set(toks))}
        try:
            json.loads(raw)
        except Exception as e:
            parse_fail.append({"file": b, "error": str(e)[:200]})
    bad["n_json_scanned"] = len(files)
    bad["strict_parse_failures"] = parse_fail
    bad["literal_NaN_or_Infinity_tokens"] = nan_hits
    bad["empty_files"] = empty
    return bad


def protected_dirs():
    dirs = [d for d in os.listdir(RES) if os.path.isdir(os.path.join(RES, d))]
    prot = [d for d in dirs if PROT.match(d) or OPT.match(d)]
    now = time.time()
    recent = []
    for d in prot:
        p = os.path.join(RES, d)
        m = os.path.getmtime(p)
        if now - m < 48 * 3600:
            recent.append({"dir": d, "mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                            time.localtime(m))})
    return {"n_result_dirs_total": len(dirs), "n_protected": len(prot),
            "protected_names": sorted(prot),
            "n_modified_last_48h": len(recent), "modified_last_48h": recent,
            "regex_used": ["^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L", "^opt_s[1-4]"]}


if __name__ == "__main__":
    what = sys.argv[1]
    print(json.dumps({"prereg": check_preregs, "json": json_health,
                      "prot": protected_dirs}[what](), indent=1)[:60000])
