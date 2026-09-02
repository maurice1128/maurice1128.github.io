"""Single source of truth for counts quoted in derived artefacts (deck, cover letter).

Never hardcode a word or reference count anywhere else, and never re-implement these
functions — import them. A derived file that computes its own count can agree with a bug
instead of with the manuscript, which is what happened before: a surname regex that could
not match "Della Croce, U." undercounted the reference list by one, and the consistency
check re-implemented the same regex, so it reported MATCHES against a wrong number.
"""
import io
import re

SRC = "D:/ROWV_paper/MANUSCRIPT_SUBMISSION.md"

# A reference entry opens with a surname (which may contain spaces, hyphens or
# apostrophes — "Della Croce", "de Paula Oliveira", "O'Brien") followed by initials.
_ENTRY = re.compile(
    r"^[A-Za-z\u00c0-\u024f]"        # a letter, accented Latin included; "van der Kruk" is lowercase
    r"[^\s,]*"                       # the rest of that word
    r"(?: [^\s,]+)*"                 # particles / multi-word surnames: Della Croce, de Paula Oliveira
    r", [A-Z\u00c0-\u024f]\."        # then the first initial
)


def _read():
    return io.open(SRC, encoding="utf-8").read()


def _reference_block(s=None):
    s = s or _read()
    return s[s.index("## References"):s.index("## Conflict of interest")]


def references(s=None):
    """The reference entries themselves, one string each."""
    out = []
    for para in re.split(r"\n\s*\n", _reference_block(s)):
        flat = " ".join(para.split())
        if not flat or flat.startswith("##") or flat.startswith("_") or set(flat) <= set("- "):
            continue
        if _ENTRY.match(flat):
            out.append(flat)
    return out


def reference_count(s=None):
    return len(references(s))


def title(s=None):
    """The manuscript title, so no derived file can carry a stale one.

    The title lived in three files at once -- manuscript, supplement builder and slide deck --
    which is the drift class this project keeps recommitting. They import it now.
    """
    s = s or _read()
    for line in s.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("no H1 title found in " + SRC)


def word_count(s=None):
    """Introduction through Conclusion — what journals mean by 'manuscript text'."""
    s = s or _read()
    body = s[s.index("## 1. Introduction"):s.index("## Figure captions")]
    return len([w for w in body.split() if any(c.isalnum() for c in w)])


def abstract_words(s=None):
    s = s or _read()
    a = s[s.index("## Abstract"):s.index("**Keywords")]
    return len([w for w in a.split() if any(c.isalnum() for c in w)]) - 1  # drop the heading


def self_test():
    """Guard the entry regex against the surname forms that have broken it before."""
    cases = [
        ("Della Croce, U., Leardini, A., 2005. Title. Journal 1, 2.", True),
        ("Das, K., de Paula Oliveira, T., Newell, J., 2023. Title. J 1, 2.", True),
        ("van der Kruk, E., Reijne, M.M., 2018. Title. J 1, 2.", True),
        ("O'Brien, T.D., Reeves, N.D., 2010. Title. J 1, 2.", True),
        ("Kidzi\u0144ski, \u0141., Delp, S., 2020. Title. J 1, 2.", True),
        ("The BioCV dataset is available from the University of Bath.", False),
        ("--- a horizontal rule ---", False),
    ]
    bad = [(t, want) for t, want in cases if bool(_ENTRY.match(t)) != want]
    return bad


if __name__ == "__main__":
    bad = self_test()
    if bad:
        print("REGEX SELF-TEST FAILED:")
        for t, want in bad:
            print(f"   expected {want}: {t[:60]}")
        raise SystemExit(1)
    print("regex self-test: pass")
    print(f"abstract   {abstract_words():>5} words")
    print(f"body       {word_count():>5} words")
    print(f"references {reference_count():>5}")
