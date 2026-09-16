# IEEE Conference Submission

IEEE conference manuscript for *Matrix-Residual Graph Neural Networks for Graph
Classification*, typeset with the IEEE conference template
(`IEEEtran.cls`, `conference` option).

## Files

| File | Purpose |
| --- | --- |
| `main.tex` | English manuscript (submission version) |
| `main_zh.tex` | Chinese companion version, same structure and numbers |
| `sections/` | English section sources included by `main.tex` |
| `references.bib` | Bibliography — 40 entries, every one with a DOI |
| `IEEEtran.cls` | IEEE conference document class |
| `compile.bat` / `compile.sh` | Build both PDFs |
| `main.pdf` / `main_zh.pdf` | Compiled output |

## Building

```
bash compile.sh        # or: compile.bat on Windows
```

English uses `pdflatex`; Chinese uses `xelatex` (via `ctexart`). Both run
`bibtex` between passes. The script fails loudly on LaTeX errors or undefined
citations.

## Structure

I. Introduction · II. Related Work · III. Method · IV. Results ·
V. Discussion · VI. Conclusion · Acknowledgment · Data and Code Availability ·
References

The three research questions from the original manuscript are preserved in
Section I and answered in Section V. All tables and figures from the original
study are retained; wide tables span both columns using `table*`.

## References and DOIs

Every one of the 40 bibliography entries carries a DOI. The entries were not
copied from the earlier draft — they were rebuilt from authoritative records:

1. `../tools/curated_dois.json` maps each citation key to an intended DOI.
2. `../tools/verify_dois.py` resolves every DOI against Crossref/DataCite and
   checks that the returned title matches the intended reference.
   Results: `../tools/doi_verification.json` — 40/40 verified.
3. `../tools/fetch_bib_meta.py` pulls the authoritative author list, venue,
   volume, issue, pages and year for each DOI.
4. `../tools/build_bib.py` assembles `references.bib` from that metadata,
   applying venue names where the DOI record is an arXiv preprint.

Notes on DOI coverage:

- **Journals and IEEE/ACM proceedings** use their native publisher DOI
  (e.g. `10.1109/TNNLS.2020.2978386`, `10.1038/s30918`).
- **ICLR, ICML (PMLR) and NeurIPS** do not issue DOIs. For papers published at
  those venues the DOI points at the arXiv record of the same work, which is
  the freely available version. This is noted at the top of `references.bib`.

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
  Oono & Suzuki. It now cites their actual ICLR 2020 paper, *Graph Neural
  Networks Exponentially Lose Expressive Power for Node Classification*.
- `sun2023attention`, `bianchi2020graph` and `du2024densegnn` had incorrect
  author lists. They now match the publisher records.
- Venue and year errors were corrected throughout (e.g. GAT is ICLR 2018,
  DropEdge is ICLR 2020, ARMA filters are TPAMI 2022).

## Recent literature

The submission checklist requires references from the last three years. Six
references from 2023–2026 were added, all with verified DOIs:

- Sui *et al.*, BMC Bioinformatics, 2023 — plant vacuole protein identification
- Sun *et al.*, Artificial Intelligence Review, 2023 — attention-based GNN survey
- Du *et al.*, npj Computational Materials, 2024 — DenseGNN
- Li *et al.*, Artificial Intelligence Review, 2024 — graph pooling survey
- Ngo *et al.*, bioRxiv, 2025 — plant functional annotation from knowledge graphs
- Charulekha *et al.*, CRC Press, 2026 — plant biological networks and AI

## Figures

Figures resolve through `\graphicspath{{../../}{../../figures/}{figures/}}`,
i.e. they are read from the repository-level `figures/` directory. The path is
relative, so the build must be run from this directory.
