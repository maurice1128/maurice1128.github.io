"""Stage-2 fallback: asymmetric refinement for the spastic conditions.

Why this is needed. Stage 1 keeps the controller `symmetric = 1` so the warm-start parameter
names match the healthy `.par`. That works for WEAKNESS (a symmetric control law can absorb a
weaker muscle) but is structurally unable to handle a UNILATERAL spastic reflex: compensating
for extra excitation on one side requires an asymmetric control response, which a symmetric
controller cannot express. Hence the spastic conditions stall at the fall penalty (~85-95)
while the paretic ones converge.

Stage 2 therefore re-runs each spastic/mixed condition with `symmetric = 0`, warm-started from
the best stage-1 result for that same condition (or from the converged HEALTHY result if
stage 1 produced nothing usable). SCONE matches warm-start parameters BY NAME, so the
symmetric->asymmetric transition may only partially import; that is expected and is reported.

Usage:  python stage2_asym.py [--launch]
"""
import os, re, sys, glob, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt2")
OPT2 = os.path.join(HERE, "opt3")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"

SPASTIC = ["SPAS02", "SPAS05", "SPAS10", "SPAS20",
           "MIX20S05", "MIX40S05", "MIX40S02", "MIX20S10"]


def best_par(tag, max_fit=None):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None
    d = max(ds, key=os.path.getmtime)
    best, bf = None, 1e9
    for p in glob.glob(os.path.join(d, "0*.par")):
        try:
            f = float(os.path.basename(p)[:-4].split("_")[2])
        except Exception:
            continue
        if f < bf:
            best, bf = p, f
    if best and (max_fit is None or bf < max_fit):
        return best, bf
    return (best, bf) if best else None


def main():
    os.makedirs(OPT2, exist_ok=True)
    # stage the data files SCONE resolves relative to the scenario
    for f in glob.glob(os.path.join(OPT, "*.osim")) + \
             glob.glob(os.path.join(OPT, "*.zml")) + \
             glob.glob(os.path.join(OPT, "*.par")):
        shutil.copy(f, OPT2)

    launched = []
    for tag in SPASTIC:
        src = os.path.join(OPT, tag + ".scone")
        if not os.path.exists(src):
            print("%-10s no stage-1 scenario" % tag)
            continue
        s = open(src, encoding="utf-8", errors="ignore").read()
        # asymmetric controller: the whole point of stage 2
        s = re.sub(r"symmetric\s*=\s*1", "symmetric = 0", s, count=1)
        s = re.sub(r"signature_prefix\s*=\s*\S+",
                   "signature_prefix = %sA" % tag, s, count=1)

        # warm-start from this condition's own best stage-1 par when it exists
        bp = best_par(tag)
        if bp:
            par, f = bp
            shutil.copy(par, os.path.join(OPT2, "init_%s.par" % tag))
            s = re.sub(r"init_file\s*=\s*\S+",
                       "init_file = init_%s.par" % tag, s, count=1)
            note = "stage1 best %.2f" % f
        else:
            note = "healthy par"
        p = os.path.join(OPT2, tag + "A.scone")
        open(p, "w", encoding="utf-8").write(s)
        launched.append((tag, p))
        print("%-10s stage2 asym scenario built (warm-start: %s)" % (tag, note))

    if "--launch" in sys.argv:
        for tag, p in launched:
            with open(os.path.join(OPT2, "log_%sA.txt" % tag), "w") as lg:
                subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=OPT2,
                                 stdout=lg, stderr=subprocess.STDOUT)
            print("launched", tag + "A")
    return launched


if __name__ == "__main__":
    main()
