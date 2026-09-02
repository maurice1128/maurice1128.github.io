# -*- coding: utf-8 -*-
"""Exercise the ALARM PATH of backup_integrity_r145.py, not just the pass path.

Round 149: three defects were found in the alarm branch, which only executes when
something is wrong -- so every clean run left it untested. The planted-failure
discipline was right and stopped one step short: it verified that C4 FIRES, not
that the report survives being printed, nor that the alarm survives to a second run.

Each test states what it would mean if it failed.
"""
import io, os, subprocess, sys, json

ROOT = r"C:\Users\maurice\Desktop\spasticity_paper"
PY = r"C:\Users\maurice\Desktop\robotic_research\.venv_mm\Scripts\python.exe"
CHK = os.path.join(ROOT, "scone", "backup_integrity_r145.py")
MAN = os.path.join(ROOT, "paper", "BACKUP_MANIFEST_r145.json")
PLANT = os.path.join(ROOT, "paper", ".bak_r998_ALARM_PATH_TEST.md")
KEY = os.path.relpath(PLANT, ROOT)

ORIG = "ORIGINAL -- a retained pre-image is immutable\n"
TAMPER = "TAMPERED -- this is the failure the alarm exists for\n"


def run(*args, enc="utf-8"):
    env = dict(os.environ, PYTHONIOENCODING=enc)
    r = subprocess.run([PY, CHK] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.stdout + r.stderr, r.returncode


def flagged_keys():
    d = json.load(io.open(MAN, encoding="utf-8"))
    return set(d.get("flagged", {})), d


ok = True


def check(n, cond, msg, meaning):
    global ok
    print("  [%s] %-58s %s" % ("PASS" if cond else "FAIL", n, msg))
    if not cond:
        ok = False
        print("        would mean: %s" % meaning)


print("=" * 74)
print("ALARM-PATH TEST")
print("=" * 74)

# --- SETUP: make the test idempotent -----------------------------------------
# A previous aborted run left a stale entry for the plant in the manifest, so the
# next run compared fresh content against a dead baseline and every assertion
# below inverted. A test that cannot be re-run from a dirty state tests only the
# state it happens to start in.
if os.path.exists(PLANT):
    os.remove(PLANT)
run("--retire-all")                     # drop any flag left by an aborted run
run()                                   # entries := current, so the stale key is dropped
_stale = KEY in json.load(io.open(MAN, encoding="utf-8"))["entries"]
print("  [%s] setup: manifest clean of the plant" % ("PASS" if not _stale else "FAIL"))

io.open(PLANT, "w", encoding="utf-8").write(ORIG)
out, rc = run()
check("T0 baseline recorded", KEY in json.load(io.open(MAN, encoding="utf-8"))["entries"]
      and rc == 0, "plant recorded, exit %d" % rc,
      "the plant never entered the manifest, so nothing below tests anything")

# --- T1: the alarm path must not CRASH, under the console that crashed it ---
io.open(PLANT, "w", encoding="utf-8").write(TAMPER)
out, rc = run(enc="cp950")
check("T1 alarm path survives cp950", "Traceback" not in out and "UnicodeEncodeError" not in out,
      "no traceback, exit %d" % rc,
      "the tool dies at the moment it detects -- defect 1, unfixed")
check("T1b alarm actually printed", "*** OVERWRITTEN ***" in out and KEY in out,
      "report reached stdout",
      "the detection happened but the operator never saw it")
check("T1c exit non-zero on detection", rc == 1, "exit %d" % rc,
      "a detected overwrite would not fail a script that checks the exit code")

# --- T2: the alarm must PERSIST to the next run (no self-clearing) ---
out2, rc2 = run()
f2, man = flagged_keys()
check("T2 alarm persists to run 2", KEY in f2 and rc2 == 1, "still flagged, exit %d" % rc2,
      "the alarm clears itself -- defect 2: one run to see it, gone the next")
check("T2b baseline NOT re-written", man["entries"][KEY]["sha256"]
      == man["flagged"][KEY]["baseline_sha256"],
      "manifest still holds the ORIGINAL digest",
      "C3 re-baselined the tampered content, destroying the evidence")

# --- T3: explicit retirement is what clears it ---
out3, rc3 = run("--retire=%s" % KEY)
f3, _ = flagged_keys()
check("T3 --retire clears the flag", KEY not in f3 and rc3 == 0, "retired, exit %d" % rc3,
      "an overwrite could never be acknowledged and the alarm would be permanent noise")

# --- T4: restoring the content self-heals ---
# NOTE: T3 retired while the file held TAMPER, so TAMPER is now the accepted
# baseline. Re-establish ORIG as the baseline explicitly before testing restore --
# an earlier revision of this test omitted this and read the tool's CORRECT flag
# (ORIG differs from the accepted TAMPER baseline) as a tool defect.
io.open(PLANT, "w", encoding="utf-8").write(ORIG)
run("--retire=%s" % KEY)                # accept ORIG as baseline
io.open(PLANT, "w", encoding="utf-8").write(TAMPER)
_, rc_flag = run()                      # re-flag
check("T4a re-flagged before restore", rc_flag == 1, "exit %d" % rc_flag,
      "the restore test would be vacuous -- nothing to heal")
io.open(PLANT, "w", encoding="utf-8").write(ORIG)
out4, rc4 = run()
f4, _ = flagged_keys()
check("T4 restore self-heals", KEY not in f4 and rc4 == 0,
      "content restored -> flag cleared, exit %d" % rc4,
      "a legitimate restore would leave a permanent false alarm")

# --- cleanup: the plant leaves the .bak namespace entirely ---
os.remove(PLANT)
out5, rc5 = run()
check("T5 clean state", rc5 == 0 and "C4 overwrites : 0" in out5, "exit %d" % rc5,
      "the repository is left in an alarmed state by the test itself")

print()
print("ALARM-PATH TEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
sys.exit(0 if ok else 1)
