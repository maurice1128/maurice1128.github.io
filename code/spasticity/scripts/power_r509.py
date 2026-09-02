# -*- coding: utf-8 -*-
"""r509: deposit the power analysis. A referee found that every sample size in the manuscript --
the rho >= 0.79 detectable at n = 12, the required-n series for the coefficients ref [7] observed,
and the 51/66/89 design targets -- appeared in no container, while carrying section 4.2's argument
that the adverse null is uninformative and the whole of section 4.3's proposed study.
"""
import io, json, math

Z = 1.959963985 + 0.8416212336          # two-sided alpha 0.05, power 0.80


def n_for(rho):
    """Bonett-Wright: Fisher z with the (1 + rho^2/2) variance inflation for a rank correlation."""
    z = math.atanh(rho)
    return Z * Z / (z * z) * (1.0 + rho * rho / 2.0) + 3.0


def detectable(n):
    lo, hi = 1e-4, 0.999
    for _ in range(300):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if n_for(m) > n else (lo, m)
    return 0.5 * (lo + hi)


CAWOOD_GAS = [("initial contact", 0.362), ("loading response", 0.278), ("midstance", 0.350),
              ("terminal stance", 0.290), ("pre-swing", 0.065)]
dep = {
 "id": "POWER_r509",
 "convention": ("Spearman rank correlation. Fisher z transform, two-sided alpha 0.05, power 0.80, "
                "with the Bonett-Wright variance inflation (1 + rho^2/2). The SAME convention is "
                "applied to the back-calculated required n for observed coefficients and to the "
                "design targets; no figure in the manuscript mixes conventions."),
 "formula": "n = (z_{alpha/2} + z_beta)^2 / atanh(rho)^2 * (1 + rho^2/2) + 3",
 "detectable_at_n12": round(detectable(12), 4),
 "required_n_for_observed_coefficients": {
     ph: {"rho": r, "n": math.ceil(n_for(r))} for ph, r in CAWOOD_GAS},
 "design_targets": {str(r): math.ceil(n_for(r)) for r in (0.40, 0.35, 0.30)},
 "what_this_licenses": ("that a 12-participant rank correlation could only have detected rho >= 0.79, "
                        "so a null at that n does not distinguish 'no relationship' from 'a "
                        "relationship of the size observed'."),
 "what_this_does_NOT_license": ("a sample size for the two-predictor regression section 4.3 "
                                "proposes. These are bivariate figures and are a LOWER BOUND for "
                                "that design. The predictor is also a five-level ordinal grade with "
                                "heavy ties, which this continuous-data formula does not model; the "
                                "manuscript says the study must be sized by simulation instead."),
}
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\POWER_r509.json", "w",
        encoding="utf-8", newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print(json.dumps(dep, indent=1, ensure_ascii=False)[:900])
