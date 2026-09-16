# IEEE Conference Submission

IEEE conference manuscript for *Matrix-Residual Graph Neural Networks for Graph
Classification*, typeset with the IEEE conference template
(`IEEEtran.cls`, `conference` option).

**Both the English and the Chinese version are exactly 6 pages, references
included.**

## Files

| File | Purpose |
| --- | --- |
| `main.tex` | English manuscript (submission version) |
| `main_zh.tex` | Chinese companion version, same structure and numbers |
| `sections/` | English section sources included by `main.tex` |
| `references.bib` | Bibliography — 29 entries, every one with a DOI |
| `IEEEtran.cls` | IEEE conference document class |
| `compile.bat` / `compile.sh` | Build both PDFs |
| `main.pdf` / `main_zh.pdf` | Compiled output |

## Building

```
bash compile.sh        # or: compile.bat on Windows
```

English uses `pdflatex`; Chinese uses `xelatex` (`extarticle` + `ctex`). Both
run `bibtex` between passes. The script reports the page count and fails on
LaTeX errors or undefined citations.

## Structure

I. Introduction · II. Related Work · III. Method · IV. Results ·
V. Discussion · VI. Conclusion · Acknowledgment · Data and Code Availability ·
References

The three research questions are stated in Section I and answered in Section V.

## Authors and funding

| Author | Email | Role |
| --- | --- | --- |
| Jingchao Wang | static@zut.edu.cn | |
| Xiaodan Cui | cuixiaodan2026@163.com | Corresponding author |
| Fangfang Shan | 6129@zut.edu.cn | |

All three share one affiliation:

> School of Computer Science, Zhongyuan University of Technology,
> Zhengzhou 450000, China

Funding is declared in the first-page footnote, as the IEEE template expects:

> This work was supported by the Science and Technology Research Project of
> Henan Province under Grant No. 262102211055.

In the Chinese companion the author names are kept in their pinyin form,
because only the pinyin was supplied; replace them with the Chinese characters
if you want them rendered that way. The grant program is translated literally
as 河南省科技研究项目 — correct it if the official name differs.

## Fitting the six-page limit

The manuscript was compressed from 12 pages to 6 without dropping any result:

- Related Work reduced from four subsections to three compact paragraphs.
- Method merged from eight subsections into three; the Plain/VerticalRes/
  HorizontalRes neighborhood definitions became inline text, keeping only the
  MatrixRes stencil and the gating rule as display equations.
- Results keeps all four tables and three figures, but the per-operator winner
  table, the mechanism table, the sensitivity table, and the tuned-candidate
  table were folded into prose.
- Discussion compresses the three RQ answers and limitations into continuous
  prose, dropping the separate future-directions subsection into the final
  limitation paragraph.
- References reduced from 40 to 29 by removing the least load-bearing citations
  and shortening venue names to standard IEEE abbreviations.
- Redundant `url` fields were dropped from `references.bib`: the DOI already
  resolves to the same page, and IEEEtran.bst otherwise prints both.

The Chinese version is set at 9pt because Chinese glyphs occupy more vertical
space than Latin text at the same nominal size; at 10pt it ran to 7 pages.

## References and DOIs

Every one of the 29 bibliography entries carries a DOI. Entries were rebuilt
from authoritative records, not copied from the earlier draft:

1. `../tools/curated_dois.json` maps each citation key to an intended DOI.
2. `../tools/verify_dois.py` resolves every DOI against Crossref/DataCite and
   checks that the returned title matches the intended reference.
   Results: `../tools/doi_verification.json`.
3. `../tools/fetch_bib_meta.py` pulls the authoritative author list, venue,
   volume, issue, pages and year for each DOI.
4. `../tools/build_bib.py` assembles `references.bib` from that metadata.

Notes on DOI coverage:

- **Journals and IEEE/ACM proceedings** use their native publisher DOI
  (e.g. `10.1109/TNNLS.2020.2978386`, `10.1038/30918`).
- **ICLR, ICML (PMLR) and NeurIPS** do not issue DOIs. For papers published at
  those venues the DOI points at the arXiv record of the same work. This is
  noted at the top of `references.bib`.

## Corrections made to the earlier bibliography

Rebuilding from Crossref surfaced several problems in the previous
`references.bib`, which was not carried over:

- `keriven2020benchmark` ("A unified benchmark for the diagnosis and treatment
  of graph neural networks") **does not exist** — the DOI it pointed at
  (`arXiv:2012.01450`) resolves to an unrelated physics paper, and no matching
  publication could be found. It has been **replaced** by Errica *et al.*,
  *A Fair Comparison of Graph Neural Networks for Graph Classification*
  (ICLR 2020), which supports the same controlled-comparison argument.
- `oono2020simple` mixed the title of a different paper with the authors of
  Oono & Suzuki. It now cites their actual ICLR 2020 paper.
- Incorrect author lists in `sun2023attention` (dropped in the trim),
  `bianchi2020graph` (dropped), and `du2024densegnn`; venue and year errors
  elsewhere (e.g. GAT is ICLR 2018, DropEdge is ICLR 2020).

## Recent literature

The submission checklist requires references from the last three years. Seven
references from 2023–2025 remain after the trim, all with verified DOIs:

- Sui *et al.*, BMC Bioinformatics, 2023 — plant vacuole protein identification
- Li *et al.*, Artificial Intelligence Review, 2024 — graph pooling survey
- Du *et al.*, npj Computational Materials, 2024 — DenseGNN
- Ngo *et al.*, bioRxiv, 2025 — plant functional annotation from knowledge graphs
- Wang *et al.*, Expert Systems with Applications, 2025 — multi-granularity
  contextual semantics for inductive knowledge graph completion
- Wang *et al.*, Expert Systems with Applications, 2024 — ConeE, global and
  local context-enhanced embedding
- Wang *et al.*, IEEE Intelligent Systems, 2024 — text-enhanced transformer
  fusion for multimodal knowledge graph completion

The three knowledge-graph-completion references were supplied by the authors and
are cited in the Introduction, alongside the plant-protein application. All
three are first-authored by Jingchao Wang.

## Figures

Figures resolve through `\graphicspath{{../../}{../../figures/}{figures/}}`,
i.e. they are read from the repository-level `figures/` directory. The path is
relative, so the build must be run from this directory.
