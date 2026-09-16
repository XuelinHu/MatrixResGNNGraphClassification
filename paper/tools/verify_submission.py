"""Pre-submission checks for the IEEE manuscript.

Verifies that every citation resolves, every bibliography entry carries a DOI,
no entries are orphaned, and the recent-literature requirement is met.
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = os.path.join(ROOT, "ieee_version")
os.chdir(VERSION)

CITE_RE = re.compile(r"\\cite[tp]?\{([^}]*)\}")
ENTRY_RE = re.compile(r"@(\w+)\{([^,]+),", re.M)


def load_bib(path="references.bib"):
    """Return {key: (type, body)}."""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        out[m.group(2).strip()] = (m.group(1), m.group(3))
    return out


def main():
    # Only count citations from files the manuscript actually inputs.
    sources = ["main.tex"]
    for inc in re.findall(r"\\input\{([^}]*)\}", open("main.tex", encoding="utf-8").read()):
        sources.append(inc if inc.endswith(".tex") else inc + ".tex")

    cited = set()
    for src in sources:
        for group in CITE_RE.findall(open(src, encoding="utf-8").read()):
            cited.update(k.strip() for k in group.split(",") if k.strip())

    bib = load_bib()
    ok = True

    missing = sorted(cited - set(bib))
    orphan = sorted(set(bib) - cited)
    no_doi = sorted(k for k, (_, body) in bib.items() if not re.search(r"\bdoi\s*=", body, re.I))

    print(f"cited keys       : {len(cited)}")
    print(f"bibliography      : {len(bib)} entries")
    print()

    if missing:
        ok = False
        print("FAIL  cited but missing from references.bib:", missing)
    else:
        print("PASS  every cited key exists in references.bib")

    if orphan:
        ok = False
        print("FAIL  bibliography entries never cited:", orphan)
    else:
        print("PASS  no orphaned bibliography entries")

    if no_doi:
        ok = False
        print("FAIL  entries without a DOI:", no_doi)
    else:
        print("PASS  every entry carries a DOI")

    # Reference recency: conference requires work from the last three years.
    years = []
    for key, (_, body) in bib.items():
        m = re.search(r"\byear\s*=\s*\{?(\d{4})", body)
        if m:
            years.append(int(m.group(1)))
    cutoff = datetime.date.today().year - 3
    recent = [y for y in years if y >= cutoff]
    if recent:
        print(f"PASS  {len(recent)} references from {cutoff} or later (years: {sorted(set(recent))})")
    else:
        ok = False
        print(f"FAIL  no references from {cutoff} or later")

    # LaTeX sanity: no leftover template placeholders.
    body = " ".join(open(s, encoding="utf-8").read() for s in sources)
    for bad in ["Given Name Surname", "Conference Paper Title", "component, formatting"]:
        if bad in body:
            ok = False
            print(f"FAIL  template placeholder still present: {bad!r}")

    for f in ["main.pdf", "main_zh.pdf"]:
        if not os.path.exists(f):
            ok = False
            print(f"FAIL  missing build output: {f}")

    print()
    print("RESULT:", "all checks passed" if ok else "CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
