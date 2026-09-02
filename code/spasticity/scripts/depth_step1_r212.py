# -*- coding: utf-8 -*-
"""ZERO-COST RECONNAISSANCE r212, STEP 1 -- THE RANGE CHECK. Gate G only.

⛔ NOT A REGISTERED STUDY. No endpoint is computed. Nothing here may be cited as evidence
for or against a hypothesis. The single question: DOES THE UNADAPTED END WALK?

Replays generation 0 and the nearest saved point to generation 10, in both arms, and applies
Gate G. Uses analyse_ladder_r169.py's OWN cycles_in(), exec'd definitions-only.

⛔ SAFETY: this script NEVER deletes a .sto (replay_speed_r203.py does, and these are archived
cells whose final .sto is the input to the PUBLISHED PRIMARYB_RESULT_r179.json). It also asserts,
per directory, that the file `sorted(glob("*.par.sto"))[-1]` resolves to -- which is how
pb_r179.py selects the solution -- is UNCHANGED by the replays. Generations are zero-padded to
four digits and the final is always the maximum, so adding shallow points cannot displace it;
the assertion is there because that reasoning is a precondition, not a guarantee.
"""
import io, os, sys, glob, json, time, subprocess

SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\analyse_ladder_r169.py"
src = io.open(SRC, encoding="utf-8").read()
ns = {"__name__": "_defs_only"}
exec(compile(src[:src.index("# ================================================== 0. selection + replay")],
             SRC, "exec"), ns)
cycles_in, S = ns["cycles_in"], ns["S"]

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
CENSUS = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DEPTH_CENSUS_r212.json"
DST = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DEPTH_STEP1_r212.json"
SETTLE, T1, MIN_DUR, MIN_CYC = 1.00, 13.58, 9.73, 4
ANCHORS = [0, 10]

cen = json.load(io.open(CENSUS, encoding="utf-8"))

# ---------------------------------------------------------------- 1. choose the two depths
targets = []          # (arm, tag, dirname, gen, parfile)
for arm in ("S", "W892"):
    for tag in sorted(k for k in cen["arms"][arm]):
        rec = cen["arms"][arm][tag]
        d = os.path.join(RES, rec["dir"])
        chosen = []
        for a in ANCHORS:
            r = min(rec["rows"], key=lambda r: abs(r["gen"] - a))
            if r["gen"] not in [c["gen"] for c in chosen]:
                chosen.append(r)
        for r in chosen:
            targets.append((arm, tag, d, r["gen"], r["file"]))

print("=" * 96)
print("STEP 1 -- RANGE CHECK.  RECONNAISSANCE, NOT A STUDY.  GATE G ONLY, NO ENDPOINT.")
print("=" * 96)
print("%d replay targets over %d cells" % (len(targets), len(set(t[1] for t in targets))))

# ------------------------------------------------- 2. record what pb_r179.py currently selects
before = {}
for _, tag, d, _, _ in targets:
    if d not in before:
        stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
        before[d] = stos[-1] if stos else None

# ---------------------------------------------------------------------------- 3. replay
t0 = time.time(); made = skipped = 0
for arm, tag, d, gen, parf in targets:
    sto = os.path.join(d, parf + ".sto")
    if os.path.exists(sto):
        skipped += 1; continue
    subprocess.run([SCONECMD, "-e", parf], cwd=d, capture_output=True, timeout=900)
    made += os.path.exists(sto)
print("replayed %d, already present %d, %.1f s" % (made, skipped, time.time() - t0))

# ------------------------------------------------- 4. the published selection must be unchanged
for d, was in before.items():
    now = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    assert now == was, "SELECTION CHANGED in %s: %s -> %s" % (d, was, now)
print("⛔ selection guard: sorted(*.par.sto)[-1] unchanged in all %d directories" % len(before))

# ---------------------------------------------------------------------------- 5. Gate G
print("\n⚠ G1 (history.txt >= 91 lines) is a property of the OPTIMISATION RUN, not of the replayed")
print("  controller, so it is 91 at every depth in every cell and DISCRIMINATES NOTHING HERE.")
print("  G2 (duration >= 9.73 s) and G3 (>= 4 cycles in [1.00, 13.58]) are what the depth tests.\n")
print("%-6s %-16s %5s %8s %6s %5s %5s %5s  %s"
      % ("arm", "cell", "gen", "t_end", "ncyc", "G1", "G2", "G3", "GATE"))
rows = []
for arm, tag, d, gen, parf in targets:
    sto = os.path.join(d, parf + ".sto")
    lines = sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace"))
    if not os.path.exists(sto):
        rows.append({"arm": arm, "cell": tag, "gen": gen, "sto": False, "pass": False})
        print("%-6s %-16s %5d %8s %6s %5s %5s %5s  NO .sto" % (arm, tag, gen, "-", "-", "-", "-", "-"))
        continue
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, T1)
    g1, g2, g3 = bool(lines >= 91), bool(t[-1] >= MIN_DUR), bool(len(cyc) >= MIN_CYC)
    ok = bool(g1 and g2 and g3)
    rows.append({"arm": arm, "cell": tag, "gen": gen, "par": parf, "sto": True,
                 "t_end": float(t[-1]), "ncyc": len(cyc),
                 "G1": g1, "G2": g2, "G3": g3, "pass": ok})
    print("%-6s %-16s %5d %8.2f %6d %5s %5s %5s  %s"
          % (arm, tag, gen, t[-1], len(cyc), "Y" if g1 else "N", "Y" if g2 else "N",
             "Y" if g3 else "N", "PASS" if ok else "⛔ FAIL"))

# ------------------------------------------------------------------------- 6. the verdict
print("\n" + "-" * 96)
for arm in ("S", "W892"):
    z = [r for r in rows if r["arm"] == arm and r["gen"] == 0]
    sh = [r for r in rows if r["arm"] == arm and r["gen"] != 0]
    print("ARM %-5s generation 0: %d of %d pass Gate G   |   shallow(~10): %d of %d pass"
          % (arm, sum(r["pass"] for r in z), len(z), sum(r["pass"] for r in sh), len(sh)))
print("-" * 96)

json.dump({"label": "RECONNAISSANCE STEP 1 -- range check, Gate G only, no endpoint computed",
           "anchors": ANCHORS, "min_dur": MIN_DUR, "min_cyc": MIN_CYC,
           "window": [SETTLE, T1], "rows": rows},
          io.open(DST, "w", encoding="utf-8", newline="\n"), indent=1)
print("deposited paper/DEPTH_STEP1_r212.json")
