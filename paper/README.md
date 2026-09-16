# Paper Directory

Manuscripts and submission artifacts for the matrix-residual graph-classification
study.

Repository identity for the paper submission:

- Repository name: `MatrixResGNNGraphClassification`
- Canonical local branch: `master`

Paper focus:

- graph classification
- structured residual connectivity
- `branch x layer` matrix view
- comparison of vertical, horizontal, and matrix-style reuse

## Versions

| Folder | Description |
| --- | --- |
| [`ieee_version/`](ieee_version/) | **Current.** IEEE conference submission (English + Chinese), IEEEtran class, 40 references all with DOIs |
| [`old_version/`](old_version/) | Previous PeerJ-format manuscript (English + Chinese), kept for reference |
| [`templates/`](templates/) | IEEE conference template and the conference submission checklist |
| [`tools/`](tools/) | Scripts and data used to verify and rebuild the bibliography |

## Tools

The bibliography in `ieee_version/` was rebuilt from authoritative records
rather than copied from the earlier draft. The pipeline lives in `tools/`:

| Script | Purpose |
| --- | --- |
| `list_cited.py` | List the bib keys actually cited by the manuscript |
| `lookup_titles.py` | Query Crossref by title and score candidate matches |
| `curated_dois.json` | Hand-checked mapping from citation key to intended DOI |
| `verify_dois.py` | Resolve every DOI and confirm the returned title matches |
| `fetch_bib_meta.py` | Fetch authoritative author/venue/pagination for each DOI |
| `build_bib.py` | Assemble `references.bib` from the verified metadata |
| `check_cites.py` | Report cited-but-missing and orphaned bibliography entries |

Generated data: `dois_resolved.json`, `doi_verification.json`,
`doi_metadata.json`, `references_new.bib`.

## Submission checklist status

Against the conference requirements in `templates/notice_text.txt`:

| Requirement | Status |
| --- | --- |
| English manuscript, IEEE conference format | Done |
| Page limit — 6 pages including references | Done — 6 pages for both English and Chinese |
| Title, authors, corresponding author, affiliation, abstract, keywords, sections, acknowledgment, references | Done — 3 authors, Xiaodan Cui corresponding |
| Funding acknowledgment | Done — first-page footnote, Grants 262102211055 and 27AQ520018 |
| All figures cited in order and readable at 100% | Done |
| All tables cited in order and editable | Done (LaTeX source) |
| Every reference has a DOI | Done — 29/29 |
| At least 10 references | Done — 29 |
| References from the last three years | Done — 7 from 2023–2025 |
| Reference authors from 3+ countries | Done |
| AI-assistance disclosure | Kept in Acknowledgment |
