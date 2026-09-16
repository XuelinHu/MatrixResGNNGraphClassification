"""Report which bib keys are cited and which are orphaned."""
import re
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CITE_RE = re.compile(r"\\cite[tp]?\{([^}]*)\}")
ENTRY_RE = re.compile(r"@\w+\{([^,]+),")

keys = set()
for f in glob.glob("sections/*.tex") + ["main.tex", "main_zh.tex"]:
    with open(f, encoding="utf-8") as fh:
        text = fh.read()
    for group in CITE_RE.findall(text):
        keys.update(k.strip() for k in group.split(",") if k.strip())

with open("references.bib", encoding="utf-8") as fh:
    bib = fh.read()
all_keys = set(ENTRY_RE.findall(bib))

print(f"cited: {len(keys)} | in bib: {len(all_keys)}")
print()
print("cited but NOT in bib:", sorted(keys - all_keys))
print()
print("in bib but NOT cited:")
for k in sorted(all_keys - keys):
    print("  ", k)
