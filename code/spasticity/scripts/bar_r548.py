# -*- coding: utf-8 -*-
"""r548: the 25-vs-3 count under each variable's OWN published measurement error.

GRADEALL_r543 applied a single bar of 1.77 deg to all 81 candidates, justified in the manuscript by
the claim that published between-session errors exist for only two of the 81 variables. That claim is
false against the deposited source. Kesar et al. Table 2 publishes between-session MDCs for FIVE
sagittal variables, four of which are members of the 81 by our own construction:

    peak ankle angle during swing      MDC 4.9  -> SEM 1.77
    ankle angle at initial contact     MDC 7.0  -> SEM 2.53
    peak knee flexion during swing     MDC 5.7  -> SEM 2.06
    hip angle at toe off               MDC 11.5 -> SEM 4.15
    trailing limb angle                MDC 3.8            (not one of the 81)

all inverted through that paper's own MDC = SEM x 1.96 x sqrt(2). We selected the smallest of the
four and applied it everywhere, which is the most permissive choice available. This recomputes the
counts three ways and reports the count as a function of the bar, so the reader can see how much of
the headline asymmetry is a property of the corpus and how much is a property of the bar.
"""
import io, json, math, os

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
G = json.load(io.open(os.path.join(P, "GRADEALL_r543.json"), encoding="utf-8"))
ROWS = G["all"]
INV = 1.0 / (1.96 * math.sqrt(2.0))
KESAR = {"ankle peak in swing": 4.9 * INV, "ankle at 0% of cycle": 7.0 * INV,
         "ankle at 100% of cycle": 7.0 * INV, "knee peak in swing": 5.7 * INV,
         "hip at toe-off": 11.5 * INV}
JOINTMAX = {"ankle": 7.0 * INV, "knee": 5.7 * INV, "hip": 11.5 * INV}
RHO = 0.8


def joint(n):
    return n.split()[0]


def count(barfn):
    w = [r["name"] for r in ROWS
         if abs(r["weak"]["rho"]) >= RHO and r["weak"]["span_deg"] >= barfn(r["name"])]
    h = [r["name"] for r in ROWS
         if abs(r["hyper"]["rho"]) >= RHO and r["hyper"]["span_deg"] >= barfn(r["name"])]
    return w, h


print("candidates scored: %d\n" % len(ROWS))
SC = [("A  single permissive bar, as published (1.77 deg everywhere)",
       lambda n: 4.9 * INV),
      ("B  each variable's own published error where one exists, 1.77 elsewhere",
       lambda n: KESAR.get(n, 4.9 * INV)),
      ("C  each joint's largest published error (conservative)",
       lambda n: JOINTMAX[joint(n)])]

out = {}
for lab, fn in SC:
    w, h = count(fn)
    out[lab[0]] = {"scenario": lab, "n_weakness": len(w), "n_tone": len(h),
                   "weakness": w, "tone": h,
                   "ratio": (len(h) / float(len(w))) if w else None}
    print("%s\n    tone %2d of 81   weakness %2d of 81   ratio %s"
          % (lab, len(h), len(w), ("%.1f" % (len(h) / float(len(w)))) if w else "undefined"))
    if w:
        print("    weakness-gradable: %s" % ", ".join(w))
    print()

print("the count as a function of a single common bar:")
print("  %8s %8s %10s" % ("bar deg", "tone", "weakness"))
curve = []
for b in [0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.77, 2.06, 2.5, 2.53, 3.0, 4.0, 4.15, 5.0]:
    w, h = count(lambda n, b=b: b)
    curve.append({"bar": b, "tone": len(h), "weak": len(w)})
    print("  %8.2f %8d %10d" % (b, len(h), len(w)))

sw = [r for r in ROWS if r["name"] == "ankle peak in swing"][0]
print("\nthe reported endpoint under its OWN published error (1.77 deg):")
print("   tone  rho %+.3f  span %.3f deg   -> %s"
      % (sw["hyper"]["rho"], sw["hyper"]["span_deg"],
         "gradable" if abs(sw["hyper"]["rho"]) >= RHO and sw["hyper"]["span_deg"] >= 4.9 * INV else "NOT"))
print("   weak  rho %+.3f  span %.3f deg   -> %s"
      % (sw["weak"]["rho"], sw["weak"]["span_deg"],
         "gradable" if abs(sw["weak"]["rho"]) >= RHO and sw["weak"]["span_deg"] >= 4.9 * INV else "NOT"))

io.open(os.path.join(P, "BAR_r548.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "BAR_r548",
 "why": ("The manuscript justified a single 1.77 deg bar across all 81 candidates by claiming that "
         "published between-session errors exist for only two of the 81 variables. Kesar Table 2 "
         "publishes five, four of which are members of the 81, and 1.77 is the smallest of them. "
         "This recomputes the counts under each variable's own error and as a function of the bar."),
 "kesar_between_session_SEM_deg": KESAR,
 "rho_bar": RHO,
 "scenarios": out,
 "count_vs_bar": curve,
}, indent=1, ensure_ascii=False))
print("\n-> BAR_r548.json")
