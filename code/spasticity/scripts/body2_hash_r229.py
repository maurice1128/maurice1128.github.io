# -*- coding: utf-8 -*-
"""Round 229 rev 5 -- write .sha256 sidecars for the registration and every script.

Revisions 1-4 ASSERTED that sidecars existed. None did, and no script contained the string
"sha256". With no digest anywhere, ALPHA, T1, GATE_B_IMBALANCE, PARTIAL_MATCH_FRAC, SEED,
MIN_N_PER_ARM and EXHAUSTIVE_MAX could all have been changed after reading a deposit with
nothing on disk to record it. That was the live degree of freedom, sitting inside the section
written to prevent exactly that.

SCOPE, per defect-register #534 and #539: a digest computed now is a baseline FORWARD. It
attests that these files have not changed since this run; it attests NOTHING about their
state before it. It is written into the sidecar itself so it travels with the record.

Per #540, digests are written to SEPARATE sidecar files. Nothing is written into the
registration, because editing a registration to carry its own hash destroys the property the
hash exists to record.
"""
import io
import os
import sys
import json
import time
import hashlib

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"

TARGETS = [os.path.join(PAPER, "PREREG_2ndbody_r229.md"),
           os.path.join(SCONE, "body2_replay_r229.py"),
           os.path.join(SCONE, "body2_dose_r229.py"),
           os.path.join(SCONE, "body2_channels_r229.py"),
           os.path.join(SCONE, "body2_convention_r229.py"),
           os.path.join(SCONE, "body2_hash_r229.py"),
           os.path.join(SCONE, "body2_delta_r229.py"),
           os.path.join(SCONE, "body2_reachability_r229.py"),
           # NOT ours, but they carry operational definitions this design depends on:
           # sto_utils.heel_strikes(min_stance=0.15) and its 0.3 s bounce-merge define Gate
           # B's usable-cycle count, hence arm sizes, hence the imbalance rate, hence the
           # outcome. dose_r174.py is the construction the dose script asserts against.
           os.path.join(SCONE, "sto_utils.py"),
           os.path.join(SCONE, "dose_r174.py"),
           # INPUT DEPOSITS. body2_channels_r229.py reads DELTA_EQUIV from the first and
           # DELTA_3D_HL from the second at run time. Unhashed, either could be edited to
           # move a decision boundary -- changing DELTA_EQUIV from 0.65 to 1.20 flips
           # ATTENUATED to EQUIV -- with no code change and no sidecar break.
           os.path.join(PAPER, "BODY2_DELTA_r229.json"),
           os.path.join(PAPER, "LADDER36_r228.json"),
           # The manifest and the map are the artefacts preconditions() TRUSTS. Unhashed,
           # editing a deposit plus its one manifest line passes precondition (a), and a
           # hand-written map with GATE_PASSES true passes (b).
           os.path.join(PAPER, "BODY2_REACHABILITY_r229.json"),
           os.path.join(PAPER, "BODY2_CORPUS_r229.json"),
           os.path.join(SCONE, "body2_fixture_r229.py"),
           os.path.join(SCONE, "body2_sd_r234.py"),
           os.path.join(SCONE, "ankle_ladder_r235.py"),
           os.path.join(SCONE, "subreg_gate_r236.py"),
           os.path.join(PAPER, "PREREG_2Dsd_r234.md"),
           os.path.join(PAPER, "BODY2_SD_r234.json"),
           os.path.join(PAPER, "PREREG_ankle_ladder_r235.md"),
           os.path.join(PAPER, "ANKLE_LADDER_r235.json"),
           os.path.join(PAPER, "SUBREG_GATE_r236.json"),
           os.path.join(PAPER, "ERRATA_delta_cap_r236.md"),
           os.path.join(PAPER, "ERRATA_transfer_framing_r240.md"),
           os.path.join(PAPER, "BODY2_POWERTABLE_r238.json"),
           # the script AS EXECUTED, byte-exact to what the run deposits record
           os.path.join(SCONE, "body2_channels_r229_AS_EXECUTED.py"),
           # the three run deposits: sole surviving witnesses to the executed
           # registration, and previously the only unhashed objects in the chain
           os.path.join(PAPER, "BODY2_CHANNELS_r229.json"),
           os.path.join(PAPER, "BODY2_DOSE_r229.json"),
           os.path.join(PAPER, "BODY2_REPLAY_LEDGER_r229.json"),
           os.path.join(PAPER, "REPRODUCTION_r243.json"),
           os.path.join(SCONE, "gen_inventory_r246.py"),
           os.path.join(PAPER, "RESULTS_3d_r214.md"),
           os.path.join(PAPER, "DEPOSIT_INVENTORY_r246.json")]

SCOPE = ("baseline forward only: attests this file is unchanged since the timestamp below; "
         "attests nothing about its state before it (defect register #534, #539)")


def sha256_of(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest = {"written": ts, "scope": SCOPE, "files": {}}
    missing = [p for p in TARGETS if not os.path.exists(p)]
    if missing:
        raise SystemExit("missing targets: %r" % [os.path.basename(p) for p in missing])
    for p in TARGETS:
        h = sha256_of(p)
        n = os.path.getsize(p)
        side = p + ".sha256"
        # newline="\n" is REQUIRED. Python text mode translates \n to \r\n on Windows, and
        # `sha256sum -c` then reads the filename with a trailing \r and reports
        # "No such file or directory" -- a sidecar that looks written and fails under the
        # real tool (#77). The first rev-5 pass shipped exactly that.
        with io.open(side, "w", encoding="utf-8", newline="\n") as f:
            f.write("%s  %s\n" % (h, os.path.basename(p)))
            f.write("# bytes  : %d\n" % n)
            f.write("# written: %s\n" % ts)
            f.write("# scope  : %s\n" % SCOPE)
        manifest["files"][os.path.basename(p)] = {"sha256": h, "bytes": n,
                                                  "sidecar": os.path.basename(side)}
        print("%s  %8d B  %s" % (h[:16] + "...", n, os.path.basename(p)))
    mp = os.path.join(PAPER, "BODY2_HASHES_r229.json")
    json.dump(manifest, io.open(mp, "w", encoding="utf-8"), indent=1)
    print("\nwrote %d sidecars and %s" % (len(TARGETS), os.path.basename(mp)))


if __name__ == "__main__":
    sys.exit(main())
