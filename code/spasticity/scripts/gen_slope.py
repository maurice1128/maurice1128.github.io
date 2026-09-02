"""Generate and launch the downhill-provocation cells (PREREG_slope.md).

REUSE, NOT A FORK. The load-bearing pieces are imported from the audited generators rather than
retyped:
  * `gen_conditions.spastic_block` / `make_scenario` -- the brace-matched splice of the
    `ConditionalController{legs = left}` INSIDE `GaitStateController/ConditionalControllers`.
    That placement is the difference between a 1.0x delivery and a scenario that is silently a
    KV = 0 run wearing a spastic label.
  * `gen_conditions.apply_registered_stopping_rule` -- min_progress = 0, max_generations = 90,
    written and read back.
  * `gen_seeds.set_seed` / `assert_registered_stopping_rule` -- structural seed write with
    readback, plus the pre-launch stopping-rule gate.
Only the OUTPUT DIRECTORY is redirected (`gen_conditions.OPT` / `.MODELS`); `TEMPLATE` and
`BASE_OSIM` are module-level and keep pointing at the audited originals in `opt2/` and `models/`.

------------------------------------------------------------------------------------------------
THE SIGN TRAP, FOUND BEFORE LAUNCH AND THE REASON THIS FILE BUILDS ITS OWN .osim FILES
------------------------------------------------------------------------------------------------
Slope is imposed by tilting gravity; the terrain `blueprint` property is silently ignored by
`ModelOpenSim`. The model walks in +X -- measured, not assumed: `DHEALTHY_s1`'s replay has
pelvis_tx 0.0000 -> +10.0740 over 10 s. Gravity's component along the direction of travel therefore
AIDS travel when walking DOWNHILL, so

    DOWNHILL grade theta  ->  gx = +g*sin(theta),  gy = -g*cos(theta)

The project's own historical downhill runs agree: every real downhill run (`D2*`, `RD2*`, `E2*`,
`SLDN2`) used an .osim with gx = +0.342247 = +g*sin(2deg), and the uphill ladder wrote
gx = -g*sin(theta).

**BUT `opt2/H0914M_DN5.osim` CARRIES gx = -0.854706 AND `opt2/H0914M_UP5.osim` CARRIES
gx = +0.854706 -- THE PAIR IS SIGN-SWAPPED.** Copies of both sit in eleven `opt_*` directories.
The consequence is on disk: the archived run `SLOPEDN5` walked 5 deg UPHILL and `SLOPEUP5` walked
5 deg DOWNHILL, each under the opposite label. Reusing `H0914M_DN5.osim` for a "downhill" arm
would have produced an uphill study named downhill, and nothing downstream would have noticed.

So this file NEVER reuses a pre-existing slope .osim. It derives gx and gy from the grade, writes
them, and READS THEM BACK before any scenario referencing them may be built.

------------------------------------------------------------------------------------------------
Usage
    python gen_slope.py --build          build osims + scenarios + seed scenarios, run all gates
    python gen_slope.py --structgate     1-generation control launch -> log for check_unused
    python gen_slope.py --run            supervisor: throttled launch with the D5 feasibility gate
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
OPTDIR = os.path.join(HERE, "opt_slope58")
LOGDIR = os.path.join(OPTDIR, "launch_logs")
GATEDIR = os.path.join(OPTDIR, "structgate")
PAPER = os.path.abspath(os.path.join(HERE, "..", "paper"))
STATUS = os.path.join(OPTDIR, "LAUNCH_STATUS.json")

G = 9.80665
SEEDS = 8
MAX_CONCURRENT = 4
DORSIFLEXOR = GC.DORSIFLEXOR                       # tib_ant_l

#: (code, downhill grade magnitude in degrees). NO UPHILL -- see PREREG_slope.md section 2.
SLOPES = [("L0", 0.0), ("D2", 2.0), ("D5", 5.0)]

#: (code, weakness map, KV). Mild rungs first; K100/W60 are the registered SECONDARY anchors.
CONDS = [
    ("K000", {},                     0.000),       # zero-gain structural control
    ("K050", {},                     0.050),       # mild spastic  (PRIMARY)
    ("K075", {},                     0.075),       # mild spastic  (PRIMARY)
    ("K100", {},                     0.100),       # moderate spastic (SECONDARY anchor)
    ("W20",  {DORSIFLEXOR: 0.80},    0.000),       # mild weak     (PRIMARY)
    ("W40",  {DORSIFLEXOR: 0.60},    0.000),       # mild weak     (PRIMARY)
    ("W60",  {DORSIFLEXOR: 0.40},    0.000),       # moderate weak (SECONDARY anchor)
]

#: 112 protected directories. Never written, never deleted, and no tag of ours may collide.
PROTECTED_RE = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L|^opt_s[1-4]")

D5_GATE_TAG = "PGD5K000_s1"        # the first -5 deg control seed IS the feasibility gate


def tag_of(code, cond):
    return "PG%s%s" % (code, cond)


def gravity_for(deg):
    """Downhill grade magnitude -> (gx, gy). gx POSITIVE for downhill; see the block comment."""
    th = math.radians(deg)
    return G * math.sin(th), -G * math.cos(th)


def set_gravity(path, deg):
    """Write the gravity vector and PROVE it landed. Never a silent no-op."""
    gx, gy = gravity_for(deg)
    s = open(path, encoding="utf-8", errors="ignore").read()
    new = "<gravity>%.6f %.6f 0</gravity>" % (gx, gy)
    s2, n = re.subn(r"<gravity>[^<]*</gravity>", new, s, count=1)
    if n != 1:
        raise RuntimeError("no <gravity> element in %s" % path)
    open(path, "w", encoding="utf-8").write(s2)
    got = re.findall(r"<gravity>([^<]*)</gravity>", open(path, encoding="utf-8").read())
    if len(got) != 1:
        raise RuntimeError("%s declares <gravity> %d times" % (path, len(got)))
    v = [float(x) for x in got[0].split()]
    if abs(v[0] - gx) > 1e-6 or abs(v[1] - gy) > 1e-6 or abs(v[2]) > 1e-9:
        raise RuntimeError("gravity write did not land in %s: %r wanted (%.6f, %.6f, 0)"
                           % (path, got[0], gx, gy))
    return gx, gy


# =============================================================================================
# BUILD
# =============================================================================================
def build():
    os.makedirs(OPTDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)

    if GC.REGISTERED_MAX_GENERATIONS != 90 or str(GC.REGISTERED_MIN_PROGRESS) != "0":
        raise RuntimeError("gen_conditions registers max_generations=%r min_progress=%r; this "
                           "study requires 90 and 0 with no exceptions"
                           % (GC.REGISTERED_MAX_GENERATIONS, GC.REGISTERED_MIN_PROGRESS))

    for f in ("InitStateGait10.zml", "ResultH0914Gait10.par"):
        src = os.path.join(GC.OPT, f)
        if not os.path.exists(src):
            src = os.path.join(GC.DATA, f)
        shutil.copy(src, os.path.join(OPTDIR, f))

    # redirect OUTPUT only; TEMPLATE and BASE_OSIM stay pointed at the audited originals
    GC.OPT, GC.MODELS = OPTDIR, OPTDIR

    built_base, grav_expect = [], {}
    for code, deg in SLOPES:
        gx, gy = gravity_for(deg)
        for cond, weak, kv in CONDS:
            tag = tag_of(code, cond)
            osim = GC.make_osim(tag, weak)                 # -> H0914_<tag>.osim in OPTDIR
            set_gravity(os.path.join(OPTDIR, osim), deg)
            p = GC.make_scenario(tag, osim, kv)
            built_base.append((tag, p))
            grav_expect[tag] = (gx, gy)
            print("built %-10s osim=%-22s KV=%.3f  weak=%-18s gx=%+.6f gy=%+.6f"
                  % (tag, osim, kv, (list(weak.items()) or "-"), gx, gy))

    built = []
    for tag, src in built_base:
        base = open(src, encoding="utf-8", errors="ignore").read()
        for s in range(1, SEEDS + 1):
            t2 = "%s_s%d" % (tag, s)
            txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % t2, base, count=1)
            txt = GS.set_seed(txt, s)
            p = os.path.join(OPTDIR, t2 + ".scone")
            open(p, "w", encoding="utf-8").write(txt)
            built.append((t2, p))
    print("\nbuilt %d base scenarios, %d seed scenarios" % (len(built_base), len(built)))
    return built_base, built, grav_expect


# =============================================================================================
# PRE-LAUNCH GATES
# =============================================================================================
def gate_stopping_rule(built):
    """V1: min_progress = 0, max_generations = 90, random_seed present and distinct. Raises."""
    GS.assert_registered_stopping_rule(built)
    return "PASS"


def gate_gravity(built, grav_expect):
    """V2: every scenario's model_file carries the gravity vector its slope requires."""
    bad = 0
    for t2, p in built:
        txt = open(p, encoding="utf-8", errors="ignore").read()
        m = re.search(r"model_file\s*=\s*(\S+)", txt)
        if not m:
            print("  %-18s NO model_file" % t2); bad += 1; continue
        op = os.path.join(OPTDIR, m.group(1))
        if not os.path.exists(op):
            print("  %-18s model_file %s missing" % (t2, m.group(1))); bad += 1; continue
        got = re.findall(r"<gravity>([^<]*)</gravity>",
                         open(op, encoding="utf-8", errors="ignore").read())
        if len(got) != 1:
            print("  %-18s %d <gravity> elements" % (t2, len(got))); bad += 1; continue
        v = [float(x) for x in got[0].split()]
        gx, gy = grav_expect[re.sub(r"_s\d+$", "", t2)]
        if abs(v[0] - gx) > 1e-6 or abs(v[1] - gy) > 1e-6 or abs(v[2]) > 1e-9:
            print("  %-18s gravity %r wanted (%.6f, %.6f, 0)" % (t2, got[0], gx, gy)); bad += 1
        elif v[0] < -1e-9:
            print("  %-18s NEGATIVE gx = UPHILL -- forbidden by the design" % t2); bad += 1
    print("  gravity readback: %d/%d scenarios carry the correct DOWNHILL gravity vector"
          % (len(built) - bad, len(built)))
    if bad:
        raise RuntimeError("GRAVITY GATE FAILED on %d scenario(s)" % bad)
    return "PASS"


def gate_speed_and_kv(built):
    """V3: every cell is S10W (min_velocity = 1.0 exactly once) and carries its registered KV
    exactly twice (soleus + gastroc), inside a `legs = left` ConditionalController."""
    kv_of = {tag_of(c, cond): kv for c, _d in SLOPES for cond, _w, kv in CONDS}
    bad = 0
    for t2, p in built:
        txt = open(p, encoding="utf-8", errors="ignore").read()
        mv = re.findall(r"^[ \t]*min_velocity[ \t]*=[ \t]*(\S+)[ \t]*$", txt, re.M)
        if mv != ["1.0"]:
            print("  %-18s min_velocity %r -- every cell must be S10W" % (t2, mv)); bad += 1
        want = "KV = %.3f" % kv_of[re.sub(r"_s\d+$", "", t2)]
        n = len(re.findall(r"^[ \t]*KV[ \t]*=[ \t]*%.3f[ \t]*$"
                           % kv_of[re.sub(r"_s\d+$", "", t2)], txt, re.M))
        if n != 2:
            print("  %-18s %r appears %d times (want 2: soleus + gastroc)" % (t2, want, n)); bad += 1
        if "legs = left" not in txt:
            print("  %-18s no `legs = left` -- the lesion side is not pinned" % t2); bad += 1
        if txt.count("SpasticL") != 1:
            print("  %-18s SpasticL appears %d times" % (t2, txt.count("SpasticL"))); bad += 1
    print("  speed/KV readback: %d/%d scenarios are S10W with the registered KV twice"
          % (len(built) - bad, len(built)))
    if bad:
        raise RuntimeError("SPEED/KV GATE FAILED on %d scenario(s)" % bad)
    return "PASS"


def gate_tag_collision(built):
    """V4: no tag of ours resolves to an existing result directory, and none is protected."""
    existing = [os.path.basename(d) for d in glob.glob(os.path.join(RES, "*")) if os.path.isdir(d)]
    protected = [n for n in existing if PROTECTED_RE.match(n)]
    hits, prot_hits = [], []
    for t2, _p in built:
        for n in existing:
            if n == t2 or n.startswith(t2 + "."):
                hits.append((t2, n))
        if PROTECTED_RE.match(t2):
            prot_hits.append(t2)
    print("  %d existing result directories; %d match the protected pattern (never touched)"
          % (len(existing), len(protected)))
    if hits:
        for t2, n in hits[:20]:
            print("  COLLISION %-18s -> %s" % (t2, n))
        raise RuntimeError("TAG COLLISION GATE FAILED: %d of our tags already exist in RESULTS. "
                           "SCONE appends ' (1)' rather than overwriting, so launching would "
                           "silently mix two corpora." % len(hits))
    if prot_hits:
        raise RuntimeError("TAG COLLISION GATE FAILED: %s match the protected pattern" % prot_hits)
    print("  tag-collision gate: 0 of %d tags collide with any existing directory" % len(built))
    return "PASS"


def structgate():
    """V5: launch the CONTROL cell at max_generations = 1 through the SHIPPED launch path, so
    `check_unused.py` has a real launcher log to return a real verdict on.

    A fix verified anywhere other than the shipped path is not verified -- so this uses the same
    Popen + redirect block the real launch uses, not a hand invocation.
    """
    os.makedirs(GATEDIR, exist_ok=True)
    for f in glob.glob(os.path.join(OPTDIR, "*.osim")) + glob.glob(os.path.join(OPTDIR, "*.zml")) \
            + glob.glob(os.path.join(OPTDIR, "*.par")):
        shutil.copy(f, GATEDIR)
    src = os.path.join(OPTDIR, "PGL0K000_s1.scone")
    txt = open(src, encoding="utf-8", errors="ignore").read()
    txt = re.sub(r"^([ \t]*)max_generations[ \t]*=[ \t]*\S+[ \t]*$",
                 lambda m: "%smax_generations = 1" % m.group(1), txt, count=1, flags=re.M)
    txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = PGSGATE", txt, count=1)
    p = os.path.join(GATEDIR, "PGSGATE.scone")
    open(p, "w", encoding="utf-8").write(txt)
    lgp = os.path.join(GATEDIR, "log_PGSGATE.txt")
    lg = open(lgp, "w")
    pr = subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=GATEDIR,
                          stdout=lg, stderr=subprocess.STDOUT,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    print("structgate launched pid=%d -> %s" % (pr.pid, lgp))
    pr.wait(timeout=1800)
    lg.close()
    print("structgate exited rc=%s, log %d bytes" % (pr.returncode, os.path.getsize(lgp)))
    return p, lgp


# =============================================================================================
# LAUNCH SUPERVISOR
# =============================================================================================
def _popen(t2):
    """One cell, BELOW_NORMAL priority so our cells yield to the user's own work on contention."""
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


def run():
    """Throttled launch. The -5 deg control seed goes FIRST and gates the rest of the -5 deg arm.

    THE D5 FEASIBILITY GATE, REGISTERED IN ADVANCE. A one-step -5 deg downhill has never been
    shown to converge in this model: the only real -5 deg downhill run in the archive (`SLOPEUP5`,
    mislabelled -- see the sign trap above) reached fitness 73.709 of 40 generations from the same
    warm start, against 0.61-0.89 for every -2 deg run. So `PGD5K000_s1` is launched first and the
    remaining 55 -5 deg cells launch ONLY if it passes the registered exclusions E5 and E6
    (>= 2 complete GRF-delimited cycles, best fitness < 3.0) -- evaluated by calling the HASHED
    `slope_analysis.replay`, so the criterion is the registered one and not a fresh judgement.

    If it fails, the -5 deg arm is dropped IN FULL, `SLOPE_D5_GATE.json` records it, and the
    primary is refitted on the two-level slope factor {0, -2} with the registered loss of power.
    NO SUBSTITUTE GRADE IS INTRODUCED -- choosing a new grade after seeing that -5 failed would be
    a data-dependent design change.
    """
    l0d2 = ["%s_s%d" % (tag_of(code, cond), s)
            for code, _d in SLOPES if code != "D5"
            for cond, _w, _kv in CONDS for s in range(1, SEEDS + 1)]
    d5_rest = ["%s_s%d" % (tag_of("D5", cond), s)
               for cond, _w, _kv in CONDS for s in range(1, SEEDS + 1)
               if "%s_s%d" % (tag_of("D5", cond), s) != D5_GATE_TAG]

    queue = [D5_GATE_TAG] + l0d2
    running, done, gate_state = [], [], "pending"
    started_pids = {}
    _write_status({"phase": "starting", "queue": len(queue), "d5_gate": gate_state})

    while queue or running:
        while queue and len([r for r in running if r[0].poll() is None]) < MAX_CONCURRENT:
            t2 = queue.pop(0)
            pr, lg = _popen(t2)
            running.append((pr, t2, lg, time.time()))
            started_pids[t2] = pr.pid
            print("launched %-18s pid=%-7d (%d running, %d queued)"
                  % (t2, pr.pid, len([r for r in running if r[0].poll() is None]), len(queue)))
            _write_status({"phase": "running", "queued": len(queue), "done": len(done),
                           "d5_gate": gate_state, "pids": started_pids,
                           "running": [r[1] for r in running if r[0].poll() is None]})
        time.sleep(20)
        still = []
        for pr, t2, lg, t0 in running:
            if pr.poll() is None:
                still.append((pr, t2, lg, t0))
                continue
            lg.close()
            done.append(t2)
            print("finished %-18s rc=%s in %.2f h" % (t2, pr.returncode, (time.time() - t0) / 3600))
            if t2 == D5_GATE_TAG and gate_state == "pending":
                gate_state = "evaluating"
                _write_status({"phase": "running", "queued": len(queue), "done": len(done),
                               "d5_gate": gate_state, "pids": started_pids})
                time.sleep(150)               # let the last .par settle past the LIVE window
                verdict = {"tag": D5_GATE_TAG}
                try:
                    import slope_analysis
                    r = slope_analysis.replay(D5_GATE_TAG)
                    verdict.update({k: v for k, v in r.items() if k != "rows"})
                    passed = (r.get("status") == "ok")
                except Exception as e:
                    verdict["error"] = repr(e)
                    passed = False
                verdict["passed"] = bool(passed)
                verdict["criterion"] = ("registered exclusions E5 (>=2 complete GRF-delimited "
                                        "cycles after settle) and E6 (best fitness < 3.0), "
                                        "evaluated by the hashed slope_analysis.replay")
                verdict["consequence"] = ("launch the remaining 55 -5 deg cells" if passed else
                                          "DROP the -5 deg arm in full; refit the primary on the "
                                          "two-level slope factor {0, -2} with the registered "
                                          "loss of power; introduce no substitute grade")
                verdict["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                os.makedirs(PAPER, exist_ok=True)
                with open(os.path.join(PAPER, "SLOPE_D5_GATE.json"), "w", encoding="utf-8") as f:
                    json.dump(verdict, f, indent=1, default=str)
                gate_state = "PASS" if passed else "FAIL"
                print("\n*** D5 FEASIBILITY GATE: %s -- %s ***\n"
                      % (gate_state, verdict["consequence"]))
                if passed:
                    queue.extend(d5_rest)
        running = still
        _write_status({"phase": "running", "queued": len(queue), "done": len(done),
                       "d5_gate": gate_state, "pids": started_pids,
                       "running": [r[1] for r in running]})

    _write_status({"phase": "complete", "done": len(done), "d5_gate": gate_state,
                   "pids": started_pids})
    print("\nALL DONE: %d cells, D5 gate %s" % (len(done), gate_state))
    return 0


def main():
    if "--build" in sys.argv:
        base, built, grav = build()
        print("\n---- PRE-LAUNCH GATES ----")
        print("V1 stopping rule:", gate_stopping_rule(built))
        print("V2 gravity      :", gate_gravity(built, grav))
        print("V3 speed / KV   :", gate_speed_and_kv(built))
        print("V4 tag collision:", gate_tag_collision(built))
        return 0
    if "--structgate" in sys.argv:
        structgate()
        return 0
    if "--run" in sys.argv:
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
