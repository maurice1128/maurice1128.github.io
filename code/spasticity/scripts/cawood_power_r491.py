# -*- coding: utf-8 -*-
"""r491: power for the correlations Cawood and Mashola's Table 5 actually reports.

An earlier revision of this manuscript quoted the five p-values 0.22, 0.45, 0.24, 0.48, 0.85 as that
paper's gastrocnemius-tone nulls. Those five values are its dorsiflexor muscle-STRENGTH column. The
plantarflexion muscle-tone column -- gastrocnemius, the muscle lesioned in this study -- reports
larger coefficients, two of them significant. This recomputes the sample size the study would have
needed for the coefficients that column actually contains.
"""
import math

Z = 1.959963985, 0.8416212336  # two-sided alpha 0.05, power 0.80


def n_for(rho, spearman=True):
    z = 0.5 * math.log((1.0 + rho) / (1.0 - rho))
    n = (Z[0] + Z[1]) ** 2 / z ** 2 + 3.0
    if spearman:                      # Bonett & Wright variance inflation for a rank correlation
        n *= 1.0 + rho ** 2 / 2.0
    return n


def detectable(n, spearman=True):
    lo, hi = 1e-4, 0.999
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if n_for(mid, spearman) > n:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


T5 = [("initial contact", 0.542, 0.069), ("loading response", 0.321, 0.309),
      ("midstance", 0.492, 0.104), ("terminal stance", 0.745, 0.005),
      ("pre-swing", 0.672, 0.017)]
print("Cawood Table 5, muscle tone / plantar-flexion column (= gastrocnemius), n = 12")
print("%-18s %8s %8s   %s" % ("phase", "rho", "p", "n needed for 80% power"))
for ph, r, p in T5:
    print("%-18s %8.3f %8.3f   %.0f" % (ph, r, p, math.ceil(n_for(r))))
print()
print("detectable at 80%% power with n = 12   rho >= %.2f" % detectable(12))
print("smallest coefficient in that column   rho  = %.3f  -> needs n = %d"
      % (min(r for _, r, _ in T5), math.ceil(n_for(min(r for _, r, _ in T5)))))
print("value at this study's endpoint        rho  = 0.542 -> needs n = %d" % math.ceil(n_for(0.542)))
print()
print("for reference, the dorsiflexor STRENGTH column an earlier revision quoted as the tone nulls:")
for ph, r in [("initial contact", -0.382), ("loading response", 0.239), ("midstance", 0.368),
              ("terminal stance", 0.225), ("pre-swing", 0.062)]:
    print("  %-18s rho %+.3f  -> needs n = %d" % (ph, r, math.ceil(n_for(abs(r)))))
