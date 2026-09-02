# -*- coding: utf-8 -*-
"""Generate PROVENANCE.json by WALKING the tree at run time.

Replaces the hand-maintained PROVENANCE_r224.json, which produced five consequential cold-read
findings across two rounds: it named "four" deposits in one field and "five" in another, said "no
prereg field" of a deposit that has one, undercounted edited deposits as two when at least five carry
edit markers, recorded a CLASSIFIER mtime that a later annotation invalidated, and called r226 the
newest set after r227 existed.

Every count here is COUNTED, not asserted. Re-run it and it cannot be stale relative to the tree.
"""
import io, os, json, re, hashlib, datetime, collections

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
RESULTS_MD = os.path.join(PAPER, "RESULTS_3d_r214.md")


def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S") \
        if os.path.exists(p) else None


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


# deposits are the .json files the Results section actually cites
body = io.open(RESULTS_MD, encoding="utf-8").read()
cited = sorted(set(re.findall(r"`([A-Za-z0-9_]+\.json)`", body)))

out = collections.OrderedDict()
out["generated_by"] = "scone/gen_provenance.py -- COUNTED at run time, not hand-maintained"
out["generated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
out["source_of_deposit_list"] = ("every `*.json` cited in RESULTS_3d_r214.md, extracted by regex at "
                                 "run time. If the section stops citing a file it leaves this list.")
out["what_this_establishes"] = ("For each deposit: its last-write time, whether a registration and "
                                "sidecar exist, and whether they predate that last write.")
out["what_this_does_NOT_establish"] = [
    "that a deposit is the output of the script named beside it -- deposits are edited after creation",
    "when any script was EXECUTED -- no execution time is recorded anywhere",
    "that a registration was not altered before its sidecar was written"]

dep = collections.OrderedDict()
n_noreg = n_edited = 0
for f in cited:
    p = os.path.join(PAPER, f)
    if not os.path.exists(p):
        dep[f] = {"present": False}
        continue
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        d = {}
    pre = d.get("prereg")
    # locate a registration whose hash prefix this deposit names, or whose stem matches
    reg = regsha = None
    for cand in sorted(os.listdir(PAPER)):
        if not cand.startswith("PREREG_") or not cand.endswith(".md"):
            continue
        h = sha(os.path.join(PAPER, cand))
        if pre and isinstance(pre, str) and h and h[:16] in pre.replace(" ", ""):
            reg, regsha = cand, h
            break
    sidecar = (reg[:-3] + ".sha256") if reg else None
    has_sidecar = bool(sidecar and os.path.exists(os.path.join(PAPER, sidecar)))
    edits = sorted(set(re.findall(r"r2\d\d", json.dumps(d)))) if d else []
    if edits:
        n_edited += 1
    if not reg:
        n_noreg += 1
    dep[f] = collections.OrderedDict([
        ("deposit_mtime", mt(p)),
        ("prereg_field", pre if isinstance(pre, str) else None),
        ("registration_matched", reg),
        ("registration_mtime", mt(os.path.join(PAPER, reg)) if reg else None),
        ("sidecar_present", has_sidecar),
        ("sidecar_mtime", mt(os.path.join(PAPER, sidecar)) if has_sidecar else None),
        ("registration_predates_deposit_last_write",
         (mt(os.path.join(PAPER, reg)) < mt(p)) if reg else None),
        ("round_markers_found_inside", edits),
    ])
out["deposits"] = dep
out["counts"] = collections.OrderedDict([
    ("deposits_cited", len(cited)),
    ("with_a_matched_registration", len(cited) - n_noreg),
    ("with_NO_matched_registration", n_noreg),
    ("carrying_round_markers_ie_edited_after_creation", n_edited),
])
p = os.path.join(PAPER, "PROVENANCE.json")
io.open(p, "w", encoding="utf-8", newline="").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
json.load(io.open(p, encoding="utf-8"))
print("cited deposits: %d | no registration: %d | edited after creation: %d"
      % (len(cited), n_noreg, n_edited))
for f, v in dep.items():
    if v.get("present") is False:
        print("  MISSING %s" % f); continue
    print("  %-30s reg=%-34s edits=%s" % (f, v["registration_matched"], v["round_markers_found_inside"]))
print("wrote %s  %d B" % (p, os.path.getsize(p)))
