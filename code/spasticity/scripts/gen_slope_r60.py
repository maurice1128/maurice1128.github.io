"""Build + gate + launch the downhill-provocation study EXACTLY as PREREG_slope.md registers it.

WHY THIS FILE EXISTS ALONGSIDE gen_slope.py
-------------------------------------------
`gen_slope.py` (written 21:04) predates the final registration (21:12) and implements the
SUPERSEDED design: 7 conditions including K100/W60 as "secondary anchors", 8 seeds per cell,
`PG*` tags, 168 runs. The registration that is hashed and binding registers a DIFFERENT design:
manipulation-check conditions `DR2K200` / `CMW80` (not K100/W60), n = 6 primary + control and
n = 4 manipulation check, `SG{0,2,5}_<COND>` tags, 114 runs at Tier 1. `gen_slope.py` is left
byte-untouched as the artifact of the superseded draft; nothing here reads it.

THE GRAVITY SIGN, COMPUTED NOT COPIED
-------------------------------------
No pre-existing slope `.osim` is reused. The 5-degree pair shipped in 16 directories each is
sign-swapped relative to the 1/2-degree convention (`H0914M_DN5.osim` carries gx = -0.854706,
`H0914M_UP5.osim` carries gx = +0.854706), so the archived `SLOPEDN5` walked UPHILL. The
documented convention, consistent at 1 and 2 degrees and stated in PREREG_slope.md section 5.2, is

    DOWNHILL grade theta  ->  gx = +g*sin(theta) ,  gy = -g*cos(theta)

Every slope model here is derived from its OWN level parent by rewriting the single `<gravity>`
line with those computed components, and gate G3 byte-diffs the result against that parent.

Usage
    python gen_slope_r60.py --build        build models + scenarios, run gates G3/G8/G5 and print
    python gen_slope_r60.py --structgate   discarded 2-generation control launch -> log for G1/G2
    python gen_slope_r60.py --feasibility  ONE control cell at -5 deg; the G4 convergence probe
    python gen_slope_r60.py --tier1        launch Tier 1 (114 runs) throttled
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_conditions as GC          # noqa: E402
import gen_seeds as GS               # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
OPTDIR = os.path.join(HERE, "opt_slope_r60")
LOGDIR = os.path.join(OPTDIR, "launch_logs")
GATEDIR = os.path.join(OPTDIR, "structgate")
PAPER = os.path.abspath(os.path.join(HERE, "..", "paper"))
STATUS = os.path.join(OPTDIR, "LAUNCH_STATUS.json")

G = 9.80665
# CONCURRENCY, measured rather than guessed. `sconecmd` logs `pooled_evaluator started threads:
# 32` on this 32-logical-core box, i.e. ONE cell already opens a thread pool the width of the
# whole machine; effective parallelism per cell is bounded by the CMA-ES population (dim = 36 ->
# lambda ~ 14), so 2 concurrent cells fill the box without heavy oversubscription and leave the
# user's foreground work responsive. Cells additionally run BELOW_NORMAL_PRIORITY_CLASS, so they
# yield on contention rather than competing with the user.
MAX_CONCURRENT = 2
DORSIFLEXOR = GC.DORSIFLEXOR                       # tib_ant_l

#: PREREG section 5.2. Downhill magnitudes only -- uphill is dropped entirely (section 5.1).
GRADES = [0, 2, 5]

#: (condition, weak_map, KV, n_seeds, role).  PREREG section 5.2 + 5.4.
#: n = 6 for the 12 primary cells and the 3 control cells; n = 4 for the 6 manipulation-check
#: cells, which never enter beta_int.
CONDS = [
    ("DR2K000", {},                   0.000, 6, "CONTROL"),
    ("DR2K050", {},                   0.050, 6, "PRIMARY_SPASTIC"),
    ("DR2K075", {},                   0.075, 6, "PRIMARY_SPASTIC"),
    ("PAR20",   {DORSIFLEXOR: 0.80},  0.000, 6, "PRIMARY_WEAK"),
    ("PAR40",   {DORSIFLEXOR: 0.60},  0.000, 6, "PRIMARY_WEAK"),
    ("DR2K200", {},                   0.200, 4, "MANIP_CHECK"),
    ("CMW80",   {DORSIFLEXOR: 0.20},  0.000, 4, "MANIP_CHECK"),
]

#: Distinct model families. The four KV conditions share the unlesioned plant, so 4 level parents
#: x 2 slopes = the 8 new .osim files section 5.2 registers.
FAMILIES = [
    ("BASE",  {}),
    ("PAR20", {DORSIFLEXOR: 0.80}),
    ("PAR40", {DORSIFLEXOR: 0.60}),
    ("CMW80", {DORSIFLEXOR: 0.20}),
]

#: Registered TA max_isometric_force readback targets (section 5.2). Intact tib_ant_l = 1759.
TA_EXPECT = {"BASE": 1759.0, "PAR20": 1407.2, "PAR40": 1055.4, "CMW80": 351.8}

FIRST_SEED = 101            # random_seed 101..106 (Tier 1); 107..116 reserved for Tier 2

#: 112 protected directories. Never written, never deleted, and no tag of ours may collide.
PROTECTED_RE = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L|^opt_s[1-4]")

D5_GATE_TAG = "SG5_DR2K000_s101"       # the -5 deg control seed IS the G4 feasibility probe


def family_of(cond):
    return cond if cond in ("PAR20", "PAR40", "CMW80") else "BASE"


def tag_of(grade, cond):
    return "SG%d_%s" % (grade, cond)


def model_name(family, grade):
    return "H0914_SGM_%s_D%d.osim" % (family, grade)


def gravity_for(deg):
    """Downhill grade magnitude in degrees -> (gx, gy). gx POSITIVE for downhill."""
    th = math.radians(deg)
    return G * math.sin(th), -G * math.cos(th)


def read_gravity(path):
    got = re.findall(r"<gravity>([^<]*)</gravity>",
                     open(path, encoding="utf-8", errors="ignore").read())
    if len(got) != 1:
        raise RuntimeError("%s declares <gravity> %d times" % (path, len(got)))
    return [float(x) for x in got[0].split()], got[0]


def read_ta_force(path):
    """max_isometric_force of tib_ant_l, read from the model file itself."""
    s = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r'name="%s"' % DORSIFLEXOR, s)
    if not m:
        raise RuntimeError("%s: no %s" % (path, DORSIFLEXOR))
    seg = s[m.end():m.end() + 3000]
    f = re.search(r"<max_isometric_force>\s*([\d.eE+-]+)", seg)
    if not f:
        raise RuntimeError("%s: no max_isometric_force for %s" % (path, DORSIFLEXOR))
    return float(f.group(1))


# =============================================================================================
# BUILD
# =============================================================================================
def build_models():
    """4 level parents (from BASE_OSIM) + 8 slope children (from their own level parent).

    A slope child is produced by copying its level parent's TEXT and rewriting ONLY the
    `<gravity>` line, which is what makes gate G3's one-changed-line assertion meaningful:
    the child cannot differ anywhere else because nothing else was ever touched.
    """
    os.makedirs(OPTDIR, exist_ok=True)
    GC.MODELS, GC.OPT = OPTDIR, OPTDIR         # redirect OUTPUT only; BASE_OSIM/TEMPLATE unchanged

    parents = {}
    for fam, weak in FAMILIES:
        # level parent: the audited base plant with this family's weakness, gravity UNTOUCHED
        emitted = GC.make_osim("SGM_%s_D0" % fam, weak)
        p = os.path.join(OPTDIR, emitted)
        if emitted != model_name(fam, 0):
            os.rename(p, os.path.join(OPTDIR, model_name(fam, 0)))
            p = os.path.join(OPTDIR, model_name(fam, 0))
        v, raw = read_gravity(p)
        if abs(v[0]) > 1e-12 or v[1] >= 0:
            raise RuntimeError("level parent %s is not level: <gravity>%s</gravity>" % (p, raw))
        parents[fam] = p

    children = {}
    for fam, _weak in FAMILIES:
        ptxt = open(parents[fam], encoding="utf-8", errors="ignore").read()
        for grade in GRADES:
            if grade == 0:
                children[(fam, 0)] = parents[fam]
                continue
            gx, gy = gravity_for(grade)
            new = "<gravity>%.6f %.6f 0</gravity>" % (gx, gy)
            ctxt, n = re.subn(r"<gravity>[^<]*</gravity>", new, ptxt, count=1)
            if n != 1:
                raise RuntimeError("no <gravity> element in parent %s" % parents[fam])
            cp = os.path.join(OPTDIR, model_name(fam, grade))
            open(cp, "w", encoding="utf-8").write(ctxt)
            children[(fam, grade)] = cp
    return parents, children


def build_scenarios():
    os.makedirs(LOGDIR, exist_ok=True)
    for f in ("InitStateGait10.zml", "ResultH0914Gait10.par"):
        src = os.path.join(GC.OPT if os.path.exists(os.path.join(GC.OPT, f))
                           else os.path.join(HERE, "opt2"), f)
        if not os.path.exists(src):
            src = os.path.join(GC.DATA, f)
        if not os.path.exists(os.path.join(OPTDIR, f)):
            shutil.copy(src, os.path.join(OPTDIR, f))

    if GC.REGISTERED_MAX_GENERATIONS != 90 or str(GC.REGISTERED_MIN_PROGRESS) != "0":
        raise RuntimeError("gen_conditions registers max_generations=%r min_progress=%r; the "
                           "registration requires 90 and 0 in every cell with no exceptions"
                           % (GC.REGISTERED_MAX_GENERATIONS, GC.REGISTERED_MIN_PROGRESS))

    GC.OPT = OPTDIR
    base, seeded = [], []
    for grade in GRADES:
        for cond, _weak, kv, n, role in CONDS:
            tag = tag_of(grade, cond)
            osim = model_name(family_of(cond), grade)
            p = GC.make_scenario(tag, osim, kv)
            base.append((tag, p, grade, cond, kv, role, osim))
            txt = open(p, encoding="utf-8", errors="ignore").read()
            for k in range(n):
                seed = FIRST_SEED + k
                t2 = "%s_s%d" % (tag, seed)
                s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % t2,
                           txt, count=1)
                s = GS.set_seed(s, seed)
                sp = os.path.join(OPTDIR, t2 + ".scone")
                open(sp, "w", encoding="utf-8").write(s)
                seeded.append((t2, sp))
    return base, seeded


# =============================================================================================
# GATES
# =============================================================================================
def gate_G3(parents, children):
    """GRAVITY READBACK -- BLOCKING. Prints the actual numbers; a bare PASS is not evidence."""
    print("\n" + "=" * 92)
    print("GATE G3 -- GRAVITY READBACK (blocking).  convention: downhill => gx POSITIVE")
    print("=" * 92)
    bad = 0
    for grade in GRADES:
        gx, gy = gravity_for(grade)
        print("\n  D = %d deg    registered vector: gx = %+.6f = +g*sin(%d) , "
              "gy = %+.6f = -g*cos(%d)   |g| = %.6f"
              % (grade, gx, grade, gy, grade, math.hypot(gx, gy)))
        for fam, _w in FAMILIES:
            cp = children[(fam, grade)]
            pp = parents[fam]
            v, raw = read_gravity(cp)
            ta = read_ta_force(cp)

            # --- byte-diff against the level parent -------------------------------------
            if grade == 0:
                nlines, difflines, diffidx = 0, [], []
                same_file = True
            else:
                same_file = False
                a = open(pp, encoding="utf-8", errors="ignore").read().splitlines()
                b = open(cp, encoding="utf-8", errors="ignore").read().splitlines()
                if len(a) != len(b):
                    print("      %-8s LINE COUNT CHANGED %d -> %d" % (fam, len(a), len(b)))
                    bad += 1
                    continue
                diffidx = [i for i in range(len(a)) if a[i] != b[i]]
                difflines = [b[i] for i in diffidx]
                nlines = len(diffidx)

            okx = (v[0] > 0) if grade > 0 else (abs(v[0]) < 1e-12)
            okmag = abs(v[0] - gx) <= 1e-6 and abs(v[1] - gy) <= 1e-6 and abs(v[2]) <= 1e-9
            okdiff = same_file or (nlines == 1 and "<gravity>" in difflines[0])
            okta = abs(ta - TA_EXPECT[fam]) < 1e-6
            ok = okx and okmag and okdiff and okta
            bad += 0 if ok else 1

            print("      %-6s %-26s gx=%+.6f gy=%+.6f gz=%.1f  |g|=%.6f  theta=%.4f deg"
                  % (fam, os.path.basename(cp), v[0], v[1], v[2],
                     math.hypot(v[0], v[1]),
                     math.degrees(math.atan2(abs(v[0]), abs(v[1])))))
            print("             raw <gravity>%s</gravity>" % raw)
            print("             x-sign   : %s   (%s)"
                  % ("POSITIVE" if v[0] > 0 else ("ZERO" if abs(v[0]) < 1e-12 else "NEGATIVE"),
                     "DOWNHILL, correct" if okx else "*** WRONG SIGN -- WOULD RUN UPHILL ***"))
            print("             |dx|=%.3e  |dy|=%.3e vs registered   -> %s"
                  % (abs(v[0] - gx), abs(v[1] - gy), "match" if okmag else "*** MISMATCH ***"))
            print("             tib_ant_l max_isometric_force = %.1f (expect %.1f) -> %s"
                  % (ta, TA_EXPECT[fam], "ok" if okta else "*** WRONG ***"))
            if same_file:
                print("             byte-diff: IS the level parent (identity); "
                      "sha-identical by construction")
            else:
                print("             byte-diff vs %s: %d changed line(s) of %d"
                      % (os.path.basename(pp), nlines, len(a)))
                for i, ln in zip(diffidx, difflines):
                    print("               line %d: %s" % (i + 1, ln.strip()))
                print("             -> %s"
                      % ("exactly one changed line and it is <gravity>" if okdiff
                         else "*** NOT a single <gravity>-only change ***"))
    print("\n  G3 verdict: %s  (%d model file(s) failed)"
          % ("PASS" if bad == 0 else "FAIL", bad))
    if bad:
        raise RuntimeError("G3 GRAVITY GATE FAILED on %d model file(s)" % bad)
    return "PASS"


def gate_stopping(seeded):
    """Stopping-rule readback with printed counts."""
    print("\n" + "=" * 92)
    print("GATE -- STOPPING-RULE READBACK  (min_progress = 0, max_generations = 90)")
    print("=" * 92)
    GS.assert_registered_stopping_rule(seeded)
    mp = mg = iv = sp = 0
    for t2, p in seeded:
        txt = open(p, encoding="utf-8", errors="ignore").read()
        mp += 1 if re.findall(r"^[ \t]*min_progress[ \t]*=[ \t]*0[ \t]*$", txt, re.M) else 0
        mg += 1 if re.findall(r"^[ \t]*max_generations[ \t]*=[ \t]*90[ \t]*$", txt, re.M) else 0
        iv += 1 if re.findall(r"^[ \t]*min_velocity[ \t]*=[ \t]*1\.0[ \t]*$", txt, re.M) else 0
        sp += 1 if re.findall(r"^[ \t]*init_file[ \t]*=[ \t]*ResultH0914Gait10\.par[ \t]*$",
                              txt, re.M) else 0
    n = len(seeded)
    print("  min_progress    = 0                      : %3d / %3d scenarios" % (mp, n))
    print("  max_generations = 90 (terminal index 89) : %3d / %3d scenarios" % (mg, n))
    print("  min_velocity    = 1.0  (S10W)            : %3d / %3d scenarios" % (iv, n))
    print("  init_file = ResultH0914Gait10.par (cold) : %3d / %3d scenarios" % (sp, n))
    resume = [t for t, p in seeded
              if "_resume.par" in open(p, encoding="utf-8", errors="ignore").read()]
    print("  scenarios naming any *_resume.par        : %3d / %3d  (must be 0)" % (len(resume), n))
    ok = (mp == mg == iv == sp == n) and not resume
    print("\n  stopping-rule verdict: %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        raise RuntimeError("STOPPING-RULE GATE FAILED")
    return "PASS"


def gate_collision(seeded):
    """Tag-collision check BEFORE launch. Lists what would collide; stops if any."""
    print("\n" + "=" * 92)
    print("GATE -- TAG-COLLISION CHECK (SCONE appends ' (1)' rather than overwriting)")
    print("=" * 92)
    existing = sorted(os.path.basename(d) for d in glob.glob(os.path.join(RES, "*"))
                      if os.path.isdir(d))
    protected = [n for n in existing if PROTECTED_RE.match(n)]
    paren = [n for n in existing if " (1)" in n]
    print("  results root                        : %s" % RES)
    print("  existing result directories         : %d" % len(existing))
    print("  matching the protected pattern      : %d  (never read, never written, never deleted)"
          % len(protected))
    print("  already carrying ' (1)' in the name : %d  (evidence the hazard is live)" % len(paren))
    hits, prot = [], []
    for t2, _p in seeded:
        for n in existing:
            if n == t2 or n.startswith(t2 + " ") or n.startswith(t2 + "."):
                hits.append((t2, n))
        if PROTECTED_RE.match(t2):
            prot.append(t2)
    print("  tags to be launched                 : %d" % len(seeded))
    if hits:
        print("\n  *** COLLISIONS ***")
        for t2, n in hits:
            print("    %-24s -> existing %s" % (t2, n))
    else:
        print("  colliding tags                      : 0  (none of our %d tags resolves to any "
              "existing directory)" % len(seeded))
    if prot:
        print("  *** tags matching the protected pattern: %s ***" % prot)
    print("\n  tag-collision verdict: %s" % ("PASS" if not hits and not prot else "FAIL"))
    if hits or prot:
        raise RuntimeError("TAG COLLISION GATE FAILED: %d colliding, %d protected"
                           % (len(hits), len(prot)))
    return "PASS"


# =============================================================================================
# STRUCTGATE -- a discarded short launch of the CONTROL cell, so check_unused has a real log
# =============================================================================================
def structgate():
    os.makedirs(GATEDIR, exist_ok=True)
    for f in (glob.glob(os.path.join(OPTDIR, "*.osim")) + glob.glob(os.path.join(OPTDIR, "*.zml"))
              + glob.glob(os.path.join(OPTDIR, "*.par"))):
        shutil.copy(f, GATEDIR)
    src = os.path.join(OPTDIR, "SG0_DR2K000_s101.scone")
    txt = open(src, encoding="utf-8", errors="ignore").read()
    txt = re.sub(r"^([ \t]*)max_generations[ \t]*=[ \t]*\S+[ \t]*$",
                 lambda m: "%smax_generations = 2" % m.group(1), txt, count=1, flags=re.M)
    txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = GATE_SGSTRUCT", txt, count=1)
    p = os.path.join(GATEDIR, "GATE_SGSTRUCT.scone")
    open(p, "w", encoding="utf-8").write(txt)
    lgp = os.path.join(GATEDIR, "log_GATE_SGSTRUCT.txt")
    lg = open(lgp, "w")
    pr = subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=GATEDIR,
                          stdout=lg, stderr=subprocess.STDOUT,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    print("structgate launched pid=%d -> %s" % (pr.pid, lgp))
    pr.wait(timeout=3600)
    lg.close()
    print("structgate exited rc=%s, log %d bytes" % (pr.returncode, os.path.getsize(lgp)))
    return p, lgp


# =============================================================================================
# LAUNCH
# =============================================================================================
def _popen(t2):
    """One cell, BELOW_NORMAL so our cells yield to the user's own work on contention."""
    p = os.path.join(OPTDIR, t2 + ".scone")
    lg = open(os.path.join(LOGDIR, "log_%s.txt" % t2), "w")
    flags = (getattr(subprocess, "CREATE_NO_WINDOW", 0)
             | getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    pr = subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=OPTDIR,
                          stdout=lg, stderr=subprocess.STDOUT, creationflags=flags)
    return pr, lg


def _write_status(d):
    d["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)


def tier1_queue():
    """The 114 Tier-1 runs, -5 deg LAST so the feasibility cell can gate them."""
    q = []
    for grade in GRADES:
        for cond, _w, _kv, n, _role in CONDS:
            for k in range(n):
                t2 = "%s_s%d" % (tag_of(grade, cond), FIRST_SEED + k)
                q.append((grade, t2))
    return q


def launch(tags, label):
    os.makedirs(LOGDIR, exist_ok=True)
    queue, running, done, pids = list(tags), [], [], {}
    print("launching %d cell(s) [%s], max %d concurrent, BELOW_NORMAL priority"
          % (len(queue), label, MAX_CONCURRENT))
    _write_status({"phase": "starting", "label": label, "queue": len(queue)})
    while queue or running:
        while queue and len([r for r in running if r[0].poll() is None]) < MAX_CONCURRENT:
            t2 = queue.pop(0)
            pr, lg = _popen(t2)
            running.append((pr, t2, lg, time.time()))
            pids[t2] = pr.pid
            print("launched %-24s pid=%-7d (%d running, %d queued)"
                  % (t2, pr.pid, len([r for r in running if r[0].poll() is None]), len(queue)))
            _write_status({"phase": "running", "label": label, "queued": len(queue),
                           "done": len(done), "pids": pids,
                           "running": [r[1] for r in running if r[0].poll() is None]})
            time.sleep(2)
        time.sleep(20)
        still = []
        for pr, t2, lg, t0 in running:
            if pr.poll() is None:
                still.append((pr, t2, lg, t0))
                continue
            lg.close()
            done.append(t2)
            print("finished %-24s rc=%s in %.2f h" % (t2, pr.returncode, (time.time() - t0) / 3600))
        running = still
        _write_status({"phase": "running", "label": label, "queued": len(queue),
                       "done": len(done), "pids": pids, "running": [r[1] for r in running]})
    _write_status({"phase": "complete", "label": label, "done": len(done), "pids": pids})
    print("\n%s COMPLETE: %d cell(s)" % (label, len(done)))
    return pids


def main():
    if "--build" in sys.argv:
        parents, children = build_models()
        base, seeded = build_scenarios()
        print("built %d model files (%d level parents + %d slope children), "
              "%d base scenarios, %d seed scenarios"
              % (len(set(children.values())), len(parents),
                 len(set(children.values())) - len(parents), len(base), len(seeded)))
        gate_G3(parents, children)
        gate_stopping(seeded)
        gate_collision(seeded)
        print("\nALL BUILD-TIME GATES PASSED")
        return 0
    if "--structgate" in sys.argv:
        structgate()
        return 0
    if "--feasibility" in sys.argv:
        launch([D5_GATE_TAG], "D5-FEASIBILITY")
        return 0
    if "--tier1" in sys.argv:
        q = [t for _g, t in tier1_queue() if t != D5_GATE_TAG]
        launch(q, "TIER1")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
