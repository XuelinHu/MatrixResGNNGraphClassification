"""Print the cited bib keys, one per line."""
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
    all_keys = set(ENTRY_RE.findall(fh.read()))

for k in sorted(keys & all_keys):
    print(k)
