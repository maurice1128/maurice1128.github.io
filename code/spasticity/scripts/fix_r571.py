# -*- coding: utf-8 -*-
"""r571: the round-five container audit. Four claims did not match their own deposits."""
import io, re, shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r541.md"
Q = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUPPLEMENT_r541.md"
shutil.copyfile(P, P.replace("MANUSCRIPT", ".bak_r88_MANUSCRIPT"))
shutil.copyfile(Q, Q.replace("SUPPLEMENT", ".bak_r89_SUPPLEMENT"))
s = io.open(P, encoding="utf-8").read()
q = io.open(Q, encoding="utf-8").read()
n = [0, 0]


def _rep(txt, o, nn, which):
    pat = re.compile(r"\s+".join(re.escape(w) for w in o.split()))
    ms = list(pat.finditer(txt))
    if len(ms) != 1:
        print("  SKIP(%d) in %s: %s" % (len(ms), which, o[:52]))
        return txt
    n[0 if which == "MS" else 1] += 1
    return txt[:ms[0].start()] + nn + txt[ms[0].end():]


def rep(o, nn):
    global s
    s = _rep(s, o, nn, "MS")


def qrep(o, nn):
    global q
    q = _rep(q, o, nn, "SUP")


# ---- 1. the hash disclosure: right that there was a breach, wrong on every number and on the
#         mechanism. Two audits exist and neither gives 61 of 78.
rep(u"""Sixty-one of
the 78 deposited hashes verify; one registration was edited after its result was produced, together
with its analysis script and outputs, and the hash sidecars were re-baselined, so hash verification
cannot detect that breach.""",
u"""Two audits of the attestations exist and this
paragraph reports both. Of 72 registrations, 55 carry a hash sidecar and all 55 still hash to it,
with no mismatches; the remaining 17 were never hashed, which is a coverage gap and not a tampering
signal. Of the 97 sidecars in the deposit directory, 84 verify, 8 do not, 2 more do not by design,
and 3 cannot be resolved to a target. Separately from the hashes, one registration,
`PREREG_2ndbody_r229.md`, was edited after its results were produced in order to restore four outcome
rungs, so the version the run executed is unrecoverable.""")

qrep(u"""Predictions were registered with hashes before the corresponding cells were run; 61 of 78 carry""",
     u"""Predictions were registered with hashes before the corresponding cells were run; 55 of the 72
registrations carry""")

qrep(u"""**The hash audit.** Sixty-one of the 78 deposited hashes verify. The seventeen that do not fall into
two groups. Most are files regenerated after a cosmetic change to an analysis script, where the
result is unchanged and the sidecar was not rewritten. One is a genuine breach: a registration was
edited after its result was produced, together with its analysis script and its regenerated outputs,
and the hash sidecars were re-baselined at the same time. Hash verification cannot detect that,
because the baseline moved with the file.""",
u"""**The hash audit.** Two audits exist over two different populations and they must not be conflated.
Over the 72 registrations: 55 carry a `.sha256` sidecar and every one of the 55 still hashes to it,
so there are no mismatched registrations; the other 17 carry no sidecar at all, being pre-r160 or
superseded, which is a coverage gap rather than a tampering signal. Over the 97 sidecars in the
deposit directory: 84 verify, 8 do not, 2 further mismatch by design because they are pre-read
snapshots taken before a cold read and are expected to diverge from the final file, and 3 cannot be
resolved to a target. No sidecar has been rewritten at any point, deliberately: re-hashing would
certify the present state and destroy the evidence that an attestation had broken.

The chain of custody is broken in one place and it is not a hash. `PREREG_2ndbody_r229.md` was edited
after its results were produced, to restore four outcome rungs. The provenance block for that
analysis cannot match, because it hashes the registration and the registration changed after the run,
and the version the run actually executed is unrecoverable. What survives is the reproduction check:
every value in the corresponding deposit is re-derivable from the frozen corpus by the executed code.
The breach touches the claim that those values were produced under a registration fixed in advance,
and not the values themselves.""")

# ---- 2. a disjoint readout CAN fail the classification. Deposited counterexample.
rep(u"""Neither statistic can fail for a readout whose arms are disjoint, of which
the scan holds thirty, so neither discriminates among them; what separates the reported endpoint is
the size of its gap against its own noise, not either of these gates.""",
u"""The permutation cannot fall below 1/462 on an eleven-family design and returns exactly that for
each of the thirty candidates whose arms are disjoint, so it does not discriminate among them. The
classification is not saturated in the same way: leave-one-family-out fits its threshold on ten
families, so a held-out family can fall the wrong side of it even where the arms are globally
disjoint, and knee angle at contact, which is disjoint, returns 0.983 rather than 1.000. What
separates the reported endpoint from the rest is the size of its gap against its own noise.""")

qrep(u"""**What neither shows.** The permutation cannot return a value below 1/462 on an eleven-family design
and returns exactly that for each of the thirty candidates whose arms are disjoint; the
classification returns 1.000 for each of them too. Neither statistic discriminates among the
separating readouts and neither can fail for one.""",
u"""**What the permutation does not show.** It cannot return a value below 1/462 on an eleven-family
design and returns exactly that for each of the thirty candidates whose arms are disjoint, so it does
not discriminate among them. The classification is different and an earlier version of this section
said otherwise: because the threshold is fitted on ten families, a held-out family can fall on the
wrong side of it even where the arms are globally disjoint. Knee angle at contact is cell-disjoint
and returns 0.983, not 1.000. The nested classification was run for the winning candidate and not for
all thirty, so the claim that it returns 1.000 for every disjoint candidate is withdrawn as
unmeasured and, in the one case that was measured, false.""")

# ---- 3. seven readouts grade weakness at family level; four went through the noise model
rep(u"""Three do on noise-free traces, seven if the ordering is
scored at the family level, and none survives 3\u00b0 of simulated jitter (\u00a7\u00a73.4, 3.5).""",
u"""Three do on noise-free traces at cell level and seven if the ordering is scored at the family
level. Of those, the three cell-level readouts were put through the noise model and none survives 3\u00b0
of jitter; the four that appear only in the family-level count were not tested under noise
(\u00a7\u00a73.4, 3.5).""")

# ---- 4. the retired pair reappears in other words
rep(u"""The statement that holds across all 81 is the displacement asymmetry above and the
three-against-25 count.""",
u"""The statement that holds across all 81 is the displacement asymmetry above and the direction of the
count, which survives every bar and rank convention tested even though its value does not.""")

# ---- 5. the sentence r567 tried to add to S9 and silently failed to place
qrep(u"""The observed maximum is 111.3 seed SD, at peak ankle dorsiflexion in swing.""",
u"""The observed maximum is 111.3 seed SD, at peak ankle dorsiflexion in swing. That figure and
\u00a73.1's 76.5 share a denominator, the 0.0819\u00b0 within-lineage seed SD, and differ in the numerator:
76.5 divides the cell-level gap of 6.265\u00b0 and 111.3 divides the family-level mean difference of
9.117\u00b0. The permutation uses the family-level statistic because the unit of analysis is the family.""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
io.open(Q, "w", encoding="utf-8", newline="").write(q)
print("manuscript edits: %d;  supplement edits: %d" % (n[0], n[1]))
