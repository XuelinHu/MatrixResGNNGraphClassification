# Previous Manuscript (PeerJ Format)

This is the earlier version of the manuscript, typeset with the PeerJ
`wlpeerj.cls` class. It is retained unchanged for reference and comparison with
the IEEE submission in `../ieee_version/`.

## Contents

| File | Purpose |
| --- | --- |
| `main.tex` | English manuscript (PeerJ format) |
| `main_zh.tex` | Chinese companion version |
| `sections/` | Section sources included by `main.tex` |
| `references.bib` | Original bibliography (76 entries; most lack DOIs) |
| `wlpeerj.cls` | PeerJ document class |
| `templatex.tex` | Template scratch file |
| `compile.bat` | Build script |
| `main.pdf` / `main_zh.pdf` | Compiled output |
| `submission_figures_png/` | Numbered PNG figures for submission |
| `supporting_evidence_csv/` | Numbered CSV evidence tables |

## Notes

- `\graphicspath` was updated to `{{../../}{../../figures/}{figures/}}` because
  this directory moved one level deeper; the figures themselves still live in
  the repository-level `figures/` directory.
- `references.bib` here is the **original** file and is deliberately left as it
  was. Its problems — missing DOIs on 68 of 76 entries, one fabricated
  reference, and several incorrect author lists — are documented and corrected
  in `../ieee_version/`.
- Build with `compile.bat` (XeLaTeX → BibTeX → XeLaTeX ×2).
