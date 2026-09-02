"""model_descriptors_r253.py -- round 253.

Extracts the model facts a Methods section needs, from the model files on disk, and deposits
them so they carry a JSON path instead of being remembered.

READ-ONLY with respect to C:\\Users\\maurice\\Documents\\SCONE. Writes only into
C:\\Users\\maurice\\Desktop\\spasticity_paper\\paper.

Covers, for both bodies: degrees of freedom (enumerated), muscles (enumerated, with side),
segment masses and total, plus the 2D gravity vector and slope angle of every plane, the
3D warm-start parameter count, and the sixteen analysis channels enumerated from the
script that constructs them.
"""
import glob
import io
import json
import math
import os
import re
import xml.etree.ElementTree as ET

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper")
SCONE = os.path.dirname(os.path.abspath(__file__))


def one_dir(pat):
    g = [d for d in glob.glob(os.path.join(RES, pat)) if os.path.isdir(d)]
    assert g, "no directory matching " + pat
    return sorted(g)[0]


def side_of(name):
    if re.search(r"_l$|_l_", name) or name.endswith("_l"):
        return "left"
    if re.search(r"_r$|_r_", name) or name.endswith("_r"):
        return "right"
    return "axial/unsided"


# --------------------------------------------------------------- 3D: Hyfydy .hfd
def parse_hfd(path):
    """The .hfd is a brace-nested key/value grammar. Walk it counting top-level blocks."""
    txt = io.open(path, encoding="utf-8", errors="replace").read()

    def blocks(kw):
        """Yield the body text of every `kw { ... }` block, by explicit brace matching."""
        for m in re.finditer(r"\b" + kw + r"\s*\{", txt):
            i = m.end()
            depth = 1
            while i < len(txt) and depth:
                if txt[i] == "{":
                    depth += 1
                elif txt[i] == "}":
                    depth -= 1
                i += 1
            yield txt[m.end():i - 1]

    def first_name(blk):
        m = re.search(r"\bname\s*=\s*([A-Za-z0-9_.]+)", blk)
        return m.group(1) if m else None

    bodies = []
    for blk in blocks("body"):
        m = re.search(r"\bmass\s*=\s*([-0-9.eE+]+)", blk)
        bodies.append({"name": first_name(blk),
                       "mass_kg": float(m.group(1)) if m else None})
    dofs = [{"name": first_name(b)} for b in blocks("dof")]
    muscles = [{"name": first_name(b)} for b in blocks("point_path_muscle")]
    joints = [{"name": first_name(b)} for b in blocks("joint")]
    return bodies, dofs, muscles, joints


# --------------------------------------------------------------- 2D: OpenSim .osim
def strip(tag):
    return tag.split("}")[-1]


def parse_osim(path):
    # OpenSim emits tag names like <HuntCrossleyForce::ContactParametersSet>, which are not
    # well-formed XML. Rewrite "::" to "__" inside tag names before parsing; nothing we read
    # depends on those elements.
    raw = io.open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(</?)([A-Za-z0-9_]+)::([A-Za-z0-9_]+)", r"\1\2__\3", raw)
    root = ET.fromstring(raw)
    grav = None
    for e in root.iter():
        if strip(e.tag) == "gravity":
            grav = [float(x) for x in e.text.split()]
            break
    bodies, coords, muscles = [], [], []
    for e in root.iter():
        t = strip(e.tag)
        if t == "Body":
            nm = e.get("name")
            mass = None
            for c in e:
                if strip(c.tag) == "mass":
                    mass = float(c.text)
            bodies.append({"name": nm, "mass_kg": mass})
        elif t == "Coordinate":
            coords.append({"name": e.get("name")})
        elif t.endswith("Muscle") or t.endswith("Muscle_Deprecated"):
            muscles.append({"name": e.get("name"), "model": t})
    return grav, bodies, coords, muscles


def slope_deg(g):
    """Angle of the gravity vector away from straight down, in the sagittal plane."""
    gx, gy = g[0], g[1]
    return math.degrees(math.atan2(abs(gx), abs(gy)))


def main():
    out = {"round": 253,
           "note": ("model descriptors extracted from the model files on disk so that the Methods "
                    "section can cite a path instead of a memory"),
           "sources": {}, "bodies": {}}

    # ---------------- 3D
    d3 = one_dir("R151C_s101*")
    hfd = os.path.join(d3, "H1922v7b3.hfd")
    par = os.path.join(d3, "H1922v7b3-TSG3Dv8g-989_fixed2.par")
    b, dof, mus, joints = parse_hfd(hfd)
    real = [x for x in b if (x["mass_kg"] or 0) > 0]
    npar = sum(1 for ln in io.open(par, errors="replace") if ln.strip())
    out["sources"]["3D"] = {"dir": os.path.basename(d3), "model_file": os.path.basename(hfd),
                            "warm_start_par": os.path.basename(par)}
    out["bodies"]["3D"] = {
        "model": "H1922v7b3.hfd (Hyfydy)",
        "n_dof": len(dof),
        "dof_names": [x["name"] for x in dof],
        "n_muscles": len(mus),
        "muscles": [{"name": x["name"], "side": side_of(x["name"])} for x in mus],
        "muscles_by_side": {s: sum(1 for x in mus if side_of(x["name"]) == s)
                            for s in ("left", "right", "axial/unsided")},
        "n_joints": len(joints),
        "joint_names": [x["name"] for x in joints],
        "n_bodies_excluding_ground": len(real),
        "segment_masses_kg": {x["name"]: x["mass_kg"] for x in real},
        "total_mass_kg": round(sum(x["mass_kg"] for x in real), 6),
        "warm_start_n_params": npar,
        "name_encodes": "H19_22 = 19 dof, 22 muscles",
    }

    # ---------------- 2D, every plane
    planes = {}
    for tag in ("SG0", "SG2", "SG5"):
        dirs = [d for d in glob.glob(os.path.join(RES, tag + "_*")) if os.path.isdir(d)]
        if not dirs:
            planes[tag] = {"present_on_disk": False}
            continue
        ctrl = [x for x in dirs if "DR2K000" in x]
        d = sorted(ctrl or dirs)[0]
        osims = glob.glob(os.path.join(d, "*.osim"))
        g, bo, co, mu = parse_osim(osims[0])
        real = [x for x in bo if (x["mass_kg"] or 0) > 0]
        planes[tag] = {
            "present_on_disk": True,
            "n_cell_dirs": len(dirs),
            "model_file": os.path.basename(osims[0]),
            "gravity_vector": g,
            "slope_deg": round(slope_deg(g), 6),
            "gravity_magnitude": round(math.sqrt(sum(x * x for x in g)), 6),
            "n_dof": len(co),
            "dof_names": [x["name"] for x in co],
            "n_muscles": len(mu),
            "muscles": [{"name": x["name"], "side": side_of(x["name"])} for x in mu],
            "muscles_by_side": {s: sum(1 for x in mu if side_of(x["name"]) == s)
                                for s in ("left", "right", "axial/unsided")},
            "n_bodies_excluding_ground": len(real),
            "segment_masses_kg": {x["name"]: x["mass_kg"] for x in real},
            "total_mass_kg": round(sum(x["mass_kg"] for x in real), 6),
        }
    out["bodies"]["2D"] = {"model": "H0914M (OpenSim)", "planes": planes,
                           "name_encodes": "H09_14 = 9 dof, 14 muscles"}

    # ---------------- the sixteen channels, from the script that constructs them
    src = os.path.join(SCONE, "channels_g2_r219.py")
    txt = io.open(src, encoding="utf-8", errors="replace").read()
    PAIR = eval(re.search(r"PAIR\s*=\s*(\[[^\]]*\])", txt).group(1))
    UNP = eval(re.search(r"UNP\s*=\s*(\[[^\]]*\])", txt).group(1))
    CH = [p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"] + [p + "_LmR" for p in PAIR]
    out["channels_16"] = {
        "source_script": "channels_g2_r219.py",
        "construction": 'CH = [p+s for p in PAIR for s in ("_l","_r")] + UNP + ["cycle_time"] + [p+"_LmR" for p in PAIR]',
        "PAIR": PAIR, "UNP": UNP,
        "n": len(CH), "channels": CH,
        "breakdown": {"bilateral_pairs_x2": len(PAIR) * 2, "unpaired_axial": len(UNP),
                      "temporal": 1, "LmR_constructions": len(PAIR)},
    }

    p = os.path.join(PAPER, "MODEL_DESCRIPTORS_r253.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    t3 = out["bodies"]["3D"]
    print("3D  %s: %d dof, %d muscles (L%d/R%d/axial%d), %d segments, total %.4f kg, warm start %d params"
          % (t3["model"], t3["n_dof"], t3["n_muscles"], t3["muscles_by_side"]["left"],
             t3["muscles_by_side"]["right"], t3["muscles_by_side"]["axial/unsided"],
             t3["n_bodies_excluding_ground"], t3["total_mass_kg"], t3["warm_start_n_params"]))
    for tag, pl in planes.items():
        if not pl["present_on_disk"]:
            print("2D  %s: NOT PRESENT ON DISK" % tag)
            continue
        print("2D  %s: %s  gravity %s  slope %.4f deg  %d dirs | %d dof, %d muscles (L%d/R%d), %d segments, %.4f kg"
              % (tag, pl["model_file"], pl["gravity_vector"], pl["slope_deg"], pl["n_cell_dirs"],
                 pl["n_dof"], pl["n_muscles"], pl["muscles_by_side"]["left"],
                 pl["muscles_by_side"]["right"], pl["n_bodies_excluding_ground"], pl["total_mass_kg"]))
    print("channels: %d -> %s" % (out["channels_16"]["n"], ", ".join(CH)))


if __name__ == "__main__":
    main()
