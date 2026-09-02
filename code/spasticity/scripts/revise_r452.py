# -*- coding: utf-8 -*-
"""r452: second batch from the three cold reads -- arithmetic errors, selective anchoring,
and the mechanical defects. Each verified before applying.

ARITHMETIC. 4.29 x sqrt(2) = 6.07, not 7.25, so "understated by sqrt(2)" does not produce the
corrected value and was wrong as written. The real inconsistency in the source is between its
reported SEM (1.55) and its own Bland-Altman SD_diff (3.70): sqrt(2)*1.55 = 2.19, not 3.70. The
assumption-free change-score MDC is 1.96*3.70 = 7.25, which matches the printed LoA half-width 7.26.
Likewise "6.39 deg is 1.7-2.1 SD of the change score" is wrong: 6.39/3.70 = 1.73 and 6.39/3.89 =
1.64, so the range is 1.6-1.7 SD.

SELECTIVE ANCHORING. The 6.39 deg used as the favourable anchor in 3.4 and 3.5 comes from KV 0.110 --
the one rung where the manuscript's own unlesioned-side control fails. Both sections now carry that.

GATE G. The 9.73 s threshold is NOT tuned to the spastic failure times: it appears in
PREREG_3d_injection_r145, PREREG_3d_discrimination_r150 and PREREG_3d_continuation_r172, all long
before the r393/r396 spastic cells. Provenance now stated, because the suspicion is reasonable from
the text alone.

STATIONARITY. STATIONARITY_r434 sets the bar at a drift ratio of ~10x; knee-at-contact is 0.98x.
The manuscript gave the two drifts without the ratio or the rule, which is why it read as an
unsupported assertion.
"""
import io
import re
import shutil

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper\MANUSCRIPT_r445.md"
shutil.copyfile(P, P + ".bak_r452_premech")
s = io.open(P, encoding="utf-8").read()


def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (tag, n)
    s = s.replace(old, new)
    print("  fixed:", tag)


# ---- header / submission hygiene -------------------------------------------------------------
rep("""*Submission-length draft r445. Supersedes the long-form r442, which is retained as the internal
record. Provenance for every number is in `spasticity_paper/paper/`; a deposit-by-claim table is
supplied as Additional file 1.*

---

""", "", "draft header removed")

# ---- MDC arithmetic --------------------------------------------------------------------------
rep("""**The published 4.29° must not be used.** Its formula substitutes SD_diff where the between-subject
SD is required, understating the MDC by √2; the same paper's limits of agreement (−6.78° to +7.74°,
half-width 7.26°) contradict its own table and confirm 7.25°.""",
    """**The published 4.29° must not be used.** Its reported SEM and its own Bland–Altman statistics are
mutually inconsistent: 4.29° is 1.96·√2·SEM with SEM = 1.55°, which requires a change-score SD of
2.19°, whereas the same paper reports limits of agreement of −6.78° to +7.74°, i.e. a change-score SD
of 3.70° and a half-width of 7.26°. The assumption-free change-score MDC₉₅ from their own
Bland–Altman data is 1.96 × 3.70 = **7.25°**, matching that half-width. (Note this is a correction
by a factor of 1.69, not the factor of √2 an earlier draft of this manuscript stated.)""",
    "MDC arithmetic")

rep("""In change-score terms 6.39° is 1.7–2.1 SD, which
is why it lands just under rather than far below a 95% threshold.""",
    """In change-score terms the largest gap is 1.6–1.7 SD of the between-session change, which is why it
lands just under rather than far below a 95% threshold.""", "change-score SD")

# ---- KV 0.110 anchoring ----------------------------------------------------------------------
rep("""like-for-like comparisons the edge gaps run 1.49–6.39° (median 4.61°); 14 reach 3.8°, three reach
5.7°, one reaches 6.39°, and **zero reach 7.25°**.""",
    """like-for-like comparisons the edge gaps run 1.49–6.39° (median 4.61°); 14 reach 3.8°, three reach
5.7°, one reaches 6.39°, and **zero reach 7.25°**. ⚠ The single largest gap, 6.39°, comes from
KV 0.110 — the one rung at which the unlesioned-side control fails (§3.1) — so it should not be
read as the study's best lesion-side evidence. Excluding that rung the ladder tops out below 5.8°,
which does not change the conclusion.""", "3.4 KV0110 anchor")

rep("""A sham control addresses the obvious objection to warm-start chaining: reading the endpoint across a
protocol change with no lesion difference shifts it by 0.586°, against the 6.39° the chained ladder
produces. Chaining cannot account for the gap.""",
    """A sham control addresses the obvious objection to warm-start chaining: reading the endpoint across a
protocol change with no lesion difference shifts it by 0.586°. Against the ladder's *median* gap of
4.61° that is 13%, and against its smallest gap of 1.49° it is 39%; an earlier draft compared it
only with the 6.39° maximum, which is both the most favourable comparison available and drawn from
the rung where the side control fails. Chaining does not account for the typical gap, but it is not
negligible at the bottom of the ladder.

⚠ One further limit on this null. It was measured among six weakness families that all walk the full
20 s and were optimised in overlapping rounds. It therefore does **not** contain the two batch
differences that distinguish the real contrast — falling versus not falling, and disjoint
optimisation rounds — so it bounds ordinary batch-to-batch variation, not the specific confound of
§3.1.""", "3.5 sham + null mismatch")

# ---- Gate G provenance + stationarity rule ---------------------------------------------------
rep("""A cell is analysed only if the simulation reaches t ≥ 9.73 s **and** yields ≥ 5 complete gait cycles
wholly inside [1.00, 9.73] s, the last kept cycle dropped; stance is `leg0_l.grf_norm_y > 0.05`.
Failing cells are reported, not discarded.""",
    """A cell is analysed only if the simulation reaches t ≥ 9.73 s **and** yields ≥ 5 complete gait cycles
wholly inside [1.00, 9.73] s, the last kept cycle dropped; stance is `leg0_l.grf_norm_y > 0.05`.
Failing cells are reported, not discarded. The 9.73 s threshold sits close to the earliest spastic
failure (9.81 s), which invites the suspicion that it was tuned to admit that arm. It was not: the
same threshold and window are fixed in registrations predating the spastic cells analysed here by
several hundred rounds, and are unchanged since. It was chosen as the shortest window that reliably
yields five post-settling cycles, not against these data.""", "Gate G provenance")

rep("""3. **Within-window stationarity.** Any endpoint reported as a window mean also reports per-cycle
   drift against the control arm's drift on the same channel. Knee-at-contact drift is +0.296°/cycle
   against the control's −0.303°/cycle, and mixed-grid drift spans −0.51 to +0.45°/cycle: the
   endpoint is stationary.""",
    """3. **Within-window stationarity.** Any endpoint reported as a window mean also reports per-cycle
   drift against the control arm's drift on the same channel, with a pass bar of a drift **ratio**
   below roughly 10. Knee-at-contact drift is +0.296°/cycle in the spastic arm against −0.303°/cycle
   in control — a ratio of 0.98, and the raw per-cycle series oscillates about −13.5° rather than
   trending — so the endpoint passes. Mixed-grid drift spans −0.51 to +0.45°/cycle. ⚠ The two arms
   nonetheless drift in *opposite* directions at ~0.3°/cycle, so their difference accumulates within
   the window; the rule as written bounds each arm against control but does not bound that
   differential, and no endpoint other than knee-at-contact has been through this check.""",
    "rule 3 bar")

# ---- mechanical ------------------------------------------------------------------------------
rep("verified. Deviations are disclosed at §6.4 and labelled at every point of use.",
    "verified. Deviations are disclosed in Limitation 4 and labelled at every point of use.",
    "6.4 xref")

rep("""| endpoint | control | weakness | spasticity | weak − ctrl | spas − ctrl | lesion difference | *d* | seed SD |""",
    """| endpoint | control | weakness | spasticity | weak − ctrl | spas − ctrl | lesion difference | *d* | in seed SD |""",
    "seed SD column header")

rep("""    present with several. The second body model does not test this endpoint. **No figures are
    included in this draft.**""",
    """    present with several. **No figures are included in this draft**, which for a paper whose claims
    are sub-phase-resolved kinematics is a substantive gap, not a formatting one: full-cycle ankle,
    knee and hip traces for the three arms against a normative band would let a reader check the
    equinus point of Limitation 3 directly.""", "limitation 12 tail")

# renumber the Limitations list (it currently skips 6)
head, tail = s.split("## 5. Limitations\n", 1)
lim, rest = tail.split("\n---\n\n## 6. Conclusions", 1)
items = re.split(r"(?m)^(\d+)\. ", lim)
out, n = [items[0]], 0
for i in range(1, len(items), 2):
    n += 1
    body = items[i + 1]
    body = re.sub(r"(?m)^   (?=\S)", "   " if n < 10 else "    ", body)
    out.append("%d. %s" % (n, body))
s = head + "## 5. Limitations\n" + "".join(out) + "\n---\n\n## 6. Conclusions" + rest
print("  fixed: limitation numbering (%d items, contiguous)" % n)

# ---- cite the three orphan references --------------------------------------------------------
rep("""association at
a different event, not discrimination. Plantarflexor **weakness** is separately associated with knee
hyperextension in adult hemiplegia [17], i.e. weakness also moves the knee.""",
    """association at
a different event, not discrimination. Plantarflexor **weakness** is separately associated with knee
hyperextension in adult hemiplegia [17], i.e. weakness also moves the knee. Dynamic EMG is an
established non-invasive adjunct in assessing equinus after stroke [20], so kinematics is not the
only alternative to a block on offer. And when contractures of different muscles are distinguished
in spastic gait, the knee has been reported as a *common* feature rather than the discriminating
variable, discrimination being carried by neighbouring joints [18] — a direct counterpoint to the
present result.""", "cite 18 and 20")

rep("""the knee angle — while the simulated endpoint carries no marker error at all. (ii) **The modality""",
    """the knee angle — while the simulated endpoint carries no marker error at all. For scale, the standard
tiering for 3D gait kinematics treats errors above 5° as large enough to mislead clinical
interpretation [24], and the effect here is 5.28°. (ii) **The modality""", "cite 24")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("\nwrote %d chars" % len(s))

body = s.split("## References")[0]
orphan = [n for n in range(1, 25) if ("[%d]" % n) not in body and ("[%d," % n) not in body
          and (" %d]" % n) not in body]
print("orphan references:", orphan or "none")
for bad in ["§6.4", "Additional file", "second body model", "1.7–2.1 SD"]:
    assert bad not in s, "STILL PRESENT: %s" % bad
print("stale strings: none")
