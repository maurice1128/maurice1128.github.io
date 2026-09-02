# -*- coding: utf-8 -*-
"""r613: read the archived model file so the animation can draw the actual body, not a stick figure.

The run directories each carry the Hyfydy model they were simulated with. It is plain text and it
holds what a proper drawing needs: every body's centre of mass offset, the bone meshes attached to
it and where they sit in its frame, every joint's position in its parent and child, and every
muscle's attachment points. The bone meshes themselves are the OpenSim geometry shipped with SCONE.

Two things are worth being explicit about. The silhouettes are computed once per bone by projecting
its mesh onto the body's own sagittal plane, so an out-of-plane rotation is not re-projected during
the animation; gait here is close to sagittal and the error is small, but it is an approximation and
the only one in the drawing. The muscle lines, by contrast, are exact: they are the model's own path
points, transformed by the model's own body poses.

The joint centres this file reads are also an independent check on r610, which estimated the same
centres from the trajectory alone without opening the model.
"""
import io, os, re
import numpy as np
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

GEOM = r"C:\Program Files\SCONE\resources\geometry"
_TOK = re.compile(r"\s*(\{|\}|\[|\]|=|[^\s{}\[\]=]+)")


def _tokens(text):
    i, n = 0, len(text)
    while i < n:
        m = _TOK.match(text, i)
        if not m:
            break
        i = m.end()
        yield m.group(1)


def _parse_block(it):
    """Nested brace format into dicts; repeated keys become lists."""
    out = {}
    for tok in it:
        if tok == "}" or tok == "]":
            return out
        key = tok
        nxt = next(it)
        if nxt == "=":
            val = next(it)
            try:
                val = float(val)
            except ValueError:
                pass
        elif nxt == "{":
            val = _parse_block(it)
        elif nxt == "[":
            val = []
            while True:
                t = next(it)
                if t == "]":
                    break
                if t == "{":
                    val.append(_parse_block(it))
            pass
        else:
            continue
        if key in out:
            if not isinstance(out[key], list) or (val and isinstance(val, dict)
                                                  and not isinstance(out[key][0], dict)):
                out[key] = [out[key]]
            elif not isinstance(out[key], list):
                out[key] = [out[key]]
            out[key].append(val)
        else:
            out[key] = val
    return out


def _vec(d):
    if not isinstance(d, dict):
        return np.zeros(3)
    return np.array([float(d.get("x", 0)), float(d.get("y", 0)), float(d.get("z", 0))])


def _listed(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def read_model(path):
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    it = _tokens(txt)
    root = None
    for tok in it:
        if tok == "model":
            assert next(it) == "{"
            root = _parse_block(it)
            break
    bodies, joints = {}, {}
    for b in _listed(root.get("body")):
        name = b.get("name")
        meshes = [(m.get("file"), _vec(m.get("pos"))) for m in _listed(b.get("mesh"))]
        bodies[name] = {"com": _vec(b.get("pos")), "meshes": meshes}
        j = b.get("joint")
        if isinstance(j, dict):
            joints[j.get("name")] = {"child": name, "parent": j.get("parent"),
                                     "in_parent": _vec(j.get("pos_in_parent")),
                                     "in_child": _vec(j.get("pos_in_child"))}
    muscles = {}
    for m in _listed(root.get("point_path_muscle")):
        muscles[m.get("name")] = [(p.get("body"), _vec(p.get("pos"))) for p in _listed(m.get("path"))]
    return {"bodies": bodies, "joints": joints, "muscles": muscles}


_VTP_CACHE = {}


def vtp_mesh(fname):
    """Vertices and triangles of an OpenSim .vtp mesh, in metres."""
    if fname in _VTP_CACHE:
        return _VTP_CACHE[fname]
    p = os.path.join(GEOM, fname)
    if not os.path.exists(p):
        _VTP_CACHE[fname] = (None, None)
        return _VTP_CACHE[fname]
    root = ET.parse(p).getroot()
    pts = tris = None
    for piece in root.iter("Piece"):
        for arr in piece.find("Points").iter("DataArray"):
            if arr.get("format", "ascii") == "ascii":
                pts = np.fromstring(" ".join(arr.text.split()), sep=" ").reshape(-1, 3)
        po = piece.find("Polys")
        if po is not None:
            conn = off = None
            for arr in po.iter("DataArray"):
                v = np.fromstring(" ".join((arr.text or "").split()), sep=" ").astype(int)
                if arr.get("Name") == "connectivity":
                    conn = v
                elif arr.get("Name") == "offsets":
                    off = v
            if conn is not None and off is not None:
                # faces are not all triangles in these meshes; fan-triangulate the larger ones
                st = np.r_[0, off[:-1]]
                tl = []
                for a, b in zip(st, off):
                    face = conn[a:b]
                    for i in range(1, len(face) - 1):
                        tl.append((face[0], face[i], face[i + 1]))
                tris = np.array(tl) if tl else None
    _VTP_CACHE[fname] = (pts, tris)
    return pts, tris


def vtp_points(fname):
    return vtp_mesh(fname)[0]


def _outline_tris(P2, tris, px=520):
    """Silhouette of a projected triangle mesh, taken by rendering the faces and contouring them.

    Rasterising the faces rather than the vertices matters: these meshes carry most of their
    vertices at the joint surfaces and very few along a shaft, so a point cloud alone breaks into
    disconnected blobs and loses the bone.
    """
    from matplotlib.collections import PolyCollection
    lo, hi = P2.min(0), P2.max(0)
    span = np.maximum(hi - lo, 1e-4)
    lo, hi = lo - span * .06, hi + span * .06
    fig = plt.figure(figsize=(px / 100.0, px / 100.0), dpi=100)
    try:
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1])
        ax.add_collection(PolyCollection(P2[tris], facecolors="k", edgecolors="k", lw=0.8))
        fig.canvas.draw()
        img = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].mean(axis=2)
    finally:
        plt.close(fig)
    g = (img < 128).astype(float)[::-1]
    g = ndimage.binary_closing(g > .5, iterations=2)
    g = ndimage.binary_fill_holes(g).astype(float)
    g = ndimage.gaussian_filter(g, 2.0)
    n = g.shape[0]
    gx = np.linspace(lo[0], hi[0], g.shape[1])
    gy = np.linspace(lo[1], hi[1], n)
    fig = plt.figure()
    try:
        segs = fig.gca().contour(gx, gy, g, [0.5]).allsegs[0]
    finally:
        plt.close(fig)
    return max(segs, key=len) if segs else None


def silhouettes(model, body, plane=(0, 1)):
    """One local-frame outline per mesh on this body, plus that mesh's out-of-plane offset."""
    out = []
    for fname, off in model["bodies"][body]["meshes"]:
        P, T = vtp_mesh(fname)
        if P is None or T is None or len(T) < 4:
            continue
        Q = (P + off)[:, list(plane)]
        poly = _outline_tris(Q, T)
        if poly is None:
            continue
        out.append((poly, float(off[2])))
    return out


if __name__ == "__main__":
    import glob, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from skel_r610 import skeleton
    f = glob.glob(r"C:\Users\maurice\Documents\SCONE\results\R151C_s101.*\H1922v7b3.hfd")[0]
    M = read_model(f)
    print("bodies %d, joints %d, muscles %d"
          % (len(M["bodies"]), len(M["joints"]), len(M["muscles"])))
    for b in ["pelvis", "femur_l", "tibia_l", "calcn_l", "torso"]:
        if b in M["bodies"]:
            sil = silhouettes(M, b)
            print("  %-9s com %s  meshes %d  outline vertices %s"
                  % (b, np.round(M["bodies"][b]["com"], 4), len(M["bodies"][b]["meshes"]),
                     [len(s[0]) for s in sil]))
    print("\nmodel joint offsets against the r610 estimates made without the model:")
    s = skeleton("R151C")
    for jn, par, chi in [("knee_l", "femur_l", "tibia_l"), ("ankle_l", "tibia_l", "calcn_l")]:
        j = M["joints"][jn]
        d_model = float(np.linalg.norm(j["in_parent"] - j["in_child"]))
        print("  %-8s model |in_parent - in_child| = %.4f m" % (jn, d_model))
    print("  r610 closure residuals (m):",
          {k: round(v, 5) for k, v in s["residual_m"].items()})
