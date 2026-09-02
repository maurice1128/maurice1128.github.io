# -*- coding: utf-8 -*-
"""Derive, from the model file alone, which joints each muscle spans.

This touches NO outcome data. It reads H1922v7b3.hfd, reconstructs the body tree from the
`joint { name = ... }` blocks nested inside each `body { name = ... }`, reads each muscle's
`path [ { body = ... } ... ]`, and reports the joints lying between a muscle's most proximal
and most distal attachment.

The point is that "does this muscle cross that joint" becomes a property of the model file,
not of my anatomy recall, so the cross-joint rule can be stated and tested without circularity.
"""
import io
import json
import os
import re

MODEL = os.path.join(r"C:\Users\maurice\Desktop\spasticity_paper", "scone", "probe3d_r141",
                     "reopt_r151", "R151C_s101", "H1922v7b3.hfd")
OUT = os.path.join(r"C:\Users\maurice\Desktop\spasticity_paper", "paper",
                   "SPANNING_MAP_r403.json")

txt = io.open(MODEL, encoding="utf-8").read()

# ---- body tree ------------------------------------------------------------------------------
# each `body { name = X ... joint { name = J ... } }` means J connects X to its parent.
bodies, parent_joint = [], {}
for m in re.finditer(r"body\s*\{", txt):
    seg = txt[m.end():m.end() + 1200]
    nm = re.search(r"name\s*=\s*(\S+)", seg)
    if not nm:
        continue
    b = nm.group(1)
    bodies.append(b)
    j = re.search(r"joint\s*\{\s*name\s*=\s*(\S+)", seg)
    if j:
        parent_joint[b] = j.group(1)

# parent body is inferred from the joint name plus the known chain of this model
CHAIN = {"femur_r": "pelvis", "tibia_r": "femur_r", "calcn_r": "tibia_r",
         "femur_l": "pelvis", "tibia_l": "femur_l", "calcn_l": "tibia_l"}
for b, p in list(CHAIN.items()):
    pass
# torso / lumbar, if present
for b in bodies:
    if b not in CHAIN and b != "pelvis" and b in parent_joint:
        CHAIN.setdefault(b, "pelvis")


def path_to_root(b):
    out = []
    while b in CHAIN:
        out.append((parent_joint.get(b), CHAIN[b]))
        b = CHAIN[b]
    return out


def joints_between(a, b):
    """Joints on the unique path between two bodies in a tree rooted at pelvis."""
    pa = {x[1]: i for i, x in enumerate(path_to_root(a))}
    ja = [x[0] for x in path_to_root(a)]
    jb = [x[0] for x in path_to_root(b)]
    ba = [a] + [x[1] for x in path_to_root(a)]
    bb = [b] + [x[1] for x in path_to_root(b)]
    common = next((x for x in ba if x in bb), "pelvis")
    out = []
    cur = a
    for j, p in path_to_root(a):
        if cur == common:
            break
        out.append(j)
        cur = p
    cur = b
    for j, p in path_to_root(b):
        if cur == common:
            break
        out.append(j)
        cur = p
    return sorted(set(x for x in out if x))


# ---- muscles --------------------------------------------------------------------------------
muscles = {}
for m in re.finditer(r"name\s*=\s*(\w+_[lr])\s*\n(?:.*\n)*?\s*path\s*\[", txt):
    nm = m.group(1)
    tail = txt[m.end():]
    blk = tail[:tail.index("]")]
    bs = re.findall(r"body\s*=\s*(\S+)", blk)
    if bs:
        muscles[nm] = bs

print("bodies      : %s" % ", ".join(bodies))
print("parent joint: %s" % json.dumps(parent_joint, ensure_ascii=False))
print("muscles     : %d" % len(muscles))
print()

SPAS = ["soleus_l", "gastroc_l"]      # the lesioned spastic muscles
WEAK = ["tib_ant_l"]                   # the lesioned weakness muscle

span = {}
for nm, bs in sorted(muscles.items()):
    js = joints_between(bs[0], bs[-1])
    span[nm] = {"path_bodies": bs, "spans": js}

print("%-16s %-34s %s" % ("muscle", "path", "spans"))
for nm in sorted(span):
    if nm in SPAS + WEAK or nm.endswith("_l"):
        print("  %-14s %-34s %s" % (nm, " -> ".join(span[nm]["path_bodies"]),
                                    ", ".join(span[nm]["spans"]) or "(none)"))
print()

joints = sorted({j for v in span.values() for j in v["spans"]})
cls = {}
for j in joints:
    by_s = [m for m in SPAS if j in span.get(m, {}).get("spans", [])]
    by_w = [m for m in WEAK if j in span.get(m, {}).get("spans", [])]
    if by_s and by_w:
        k = "BOTH"
    elif by_s:
        k = "SPASTIC_ONLY"
    elif by_w:
        k = "WEAK_ONLY"
    else:
        k = "NEITHER"
    cls[j] = {"class": k, "spastic_muscles": by_s, "weak_muscles": by_w}

print("joint classification under the cross-joint rule")
print("  %-14s %-14s %-28s %s" % ("joint", "class", "spanned by (spastic)", "(weak)"))
for j in joints:
    c = cls[j]
    print("  %-14s %-14s %-28s %s" % (j, c["class"], ",".join(c["spastic_muscles"]) or "-",
                                      ",".join(c["weak_muscles"]) or "-"))
print()
print("RULE PREDICTION")
print("  BOTH         -> the two lesions displace the joint the SAME way; gap grows only on")
print("                  the difference of rates, so it stays small")
print("  SPASTIC_ONLY -> OPPOSITE displacement; this is where a discriminator should live")
print("  WEAK_ONLY    -> OPPOSITE displacement, mirrored")
print("  NEITHER      -> negligible displacement from either lesion")

io.open(OUT, "w", encoding="utf-8").write(json.dumps(
    {"derived_from": MODEL, "touches_no_outcome_data": True,
     "body_parent": CHAIN, "parent_joint": parent_joint,
     "muscle_spans": span, "joint_classes": cls,
     "lesioned_spastic": SPAS, "lesioned_weak": WEAK}, indent=2, ensure_ascii=False))
print()
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
