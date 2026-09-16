"""Assemble the IEEE submission bibliography from verified DOI metadata.

Author names, titles, years and volume/page data come from tools/doi_metadata.json
(fetched from Crossref/DataCite). Venue names are supplied here because the
arXiv records, which carry the DOI, do not include the peer-reviewed venue.

For venues that do not issue DOIs (ICLR, ICML/PMLR, NeurIPS), the DOI field
points at the corresponding arXiv record, which is the freely available
version of the same work.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# key -> (entry type, venue field name, venue value, extra field dict)
VENUE = {
    "kipf2017gcn": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2017"}),
    "xu2019gin": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2019"}),
    "hamilton2017inductive": ("inproceedings", "booktitle", "Proc. NeurIPS", {"volume": "30", "pages": "1024--1034", "year": "2017"}),
    "velivckovic2017graph": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2018"}),
    "duvenaud2015convolutional": ("inproceedings", "booktitle", "Proc. NeurIPS", {"volume": "28", "pages": "2224--2232", "year": "2015"}),
    "gilmer2017neural": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "1263--1272", "year": "2017"}),
    "ying2018hierarchical": ("inproceedings", "booktitle", "Proc. NeurIPS", {"volume": "31", "pages": "4800--4810", "year": "2018"}),
    "lee2019self": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "3634--3643", "year": "2019"}),
    "cangea2018towards": ("inproceedings", "booktitle", "NeurIPS Workshop Rel. Represent. Learn.", {"year": "2018"}),
    "xu2018representation": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "5453--5462", "year": "2018"}),
    "rong2019dropedge": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2020"}),
    "bresson2017residual": ("article", "journal", "arXiv preprint arXiv:1711.07553", {"year": "2017"}),
    "fey2019fast": ("inproceedings", "booktitle", "ICLR Workshop Represent. Learn. Graphs Manifolds", {"year": "2019"}),
    "kingma2014adam": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2015"}),
    "abu2019mixhop": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "21--29", "year": "2019"}),
    "dwivedi2020generalization": ("article", "journal", "arXiv preprint arXiv:2012.09699", {"year": "2020"}),
    "li2021training": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "6403--6413", "year": "2021"}),
    "oono2020simple": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2020"}),
    "chenSimpleDeepGraph2020": ("inproceedings", "booktitle", "Proc. ICML", {"pages": "1725--1735", "year": "2020"}),
    "topping2021understanding": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2022"}),
    "alon2020bottleneck": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2021"}),
    "errica2020fair": ("inproceedings", "booktitle", "Proc. ICLR", {"year": "2020"}),
    "morris2020tudataset": ("inproceedings", "booktitle", "ICML Workshop Graph Represent. Learn. Beyond", {"year": "2020"}),
    "bianchi2020graph": ("article", "journal", "IEEE Trans. Pattern Anal. Mach. Intell.", {"volume": "44", "number": "4", "pages": "2129--2140", "year": "2022"}),
    "baongoImprovingPlantFunctional2025": ("article", "journal", "bioRxiv", {"year": "2025"}),
    # Conference proceedings recorded by Crossref as journal-articles.
    "gori2005new": ("inproceedings", "booktitle", "Proc. IJCNN", {"volume": "2", "pages": "729--734", "year": "2005"}),
    "he2016deep": ("inproceedings", "booktitle", "Proc. CVPR", {"pages": "770--778", "year": "2016"}),
    "li2019deepgcns": ("inproceedings", "booktitle", "Proc. ICCV", {"pages": "9266--9275", "year": "2019"}),
    "li2018deeper": ("inproceedings", "booktitle", "Proc. AAAI", {"volume": "32", "number": "1", "pages": "3538--3545", "year": "2018"}),
    # Edited volumes.
    "wormald1999models": ("incollection", "booktitle", "Surveys in Combinatorics, 1999", {"publisher": "Cambridge Univ. Press", "pages": "239--298", "year": "1999"}),
    "charulekhaUncoveringComplicatedPlant": ("incollection", "booktitle", "AI in Plant Science and Precision Agriculture", {"publisher": "CRC Press", "pages": "225--242", "year": "2026"}),
}

# Crossref occasionally carries a degraded author string; these are the
# authoritative forms.
AUTHOR_FIX = {
    "barabasi1999emergence": r"Barab{\'a}si, Albert-L{\'a}szl{\'o} and Albert, R{\'e}ka",
    "li2019deepgcns": r"Li, Guohao and M{\"u}ller, Matthias and Thabet, Ali and Ghanem, Bernard",
    "baongoImprovingPlantFunctional2025": "Ngo, Tran Gia Bao and Liseron-Monfils, Christophe and Das, Shreyan and Ubbens, Jordan and Ashe, Paula and Konkin, David",
    "sun2023attention": "Sun, Chengcheng and Li, Chenhao and Lin, Xiang and Zheng, Tianji and Meng, Fanrong and Rui, Xiaobin and Wang, Zhixiao",
}

TITLE_FIX = {
    "watts1998collective": r"Collective dynamics of `small-world' networks",
}

NUM_FIX = {
    "sun2023attention": {"number": "S2"},
}

ORDER = [
    "kipf2017gcn", "hamilton2017inductive", "velivckovic2017graph",
    "xu2019gin", "gilmer2017neural", "ying2018hierarchical",
    "wu2020comprehensive", "li2018deeper",
    "oono2020simple", "he2016deep",
    "xu2018representation", "rong2019dropedge", "bresson2017residual",
    "abu2019mixhop", "dwivedi2020generalization", "topping2021understanding",
    "alon2020bottleneck", "errica2020fair", "morris2020tudataset", "fey2019fast",
    "kingma2014adam", "suiIdentificationPlantVacuole2023",
    "li2024graph", "du2024densegnn", "baongoImprovingPlantFunctional2025",
    "gilbert1959random", "barabasi1999emergence",
    "holland1983stochastic", "watts1998collective",
]

# LaTeX escapes for characters that BibTeX/LaTeX would otherwise mis-typeset.
ACCENTS = {
    "á": r"{\'a}", "à": r"{\`a}", "â": r"{\^a}", "ä": r"{\"a}", "ã": r"{\~a}", "å": r"{\r a}",
    "é": r"{\'e}", "è": r"{\`e}", "ê": r"{\^e}", "ë": r"{\"e}",
    "í": r"{\'i}", "ì": r"{\`i}", "î": r"{\^i}", "ï": r"{\"i}",
    "ó": r"{\'o}", "ò": r"{\`o}", "ô": r"{\^o}", "ö": r"{\"o}", "õ": r"{\~o}",
    "ú": r"{\'u}", "ù": r"{\`u}", "û": r"{\^u}", "ü": r"{\"u}",
    "ç": r"{\c c}", "ñ": r"{\~n}", "š": r"{\v s}", "ž": r"{\v z}", "ć": r"{\'c}",
    "č": r"{\v c}", "ř": r"{\v r}", "ý": r"{\'y}", "ß": r"{\ss}", "ł": r"{\l}",
    "ā": r"{\=a}", "ē": r"{\=e}", "ī": r"{\=i}", "ō": r"{\=o}", "ū": r"{\=u}",
    "Á": r"{\'A}", "É": r"{\'E}", "Í": r"{\'I}", "Ó": r"{\'O}", "Ú": r"{\'U}",
}

LATEX_SPECIAL = [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]


ESCAPE_MAP = dict(LATEX_SPECIAL)


def texify(text):
    """Convert unicode text into BibTeX-safe LaTeX.

    Accent macros are emitted verbatim; only plain characters that are special
    to LaTeX get escaped, so accent commands are never double-escaped.
    """
    out = []
    for ch in text:
        if ch in ACCENTS:
            out.append(ACCENTS[ch])
        elif ch in ESCAPE_MAP:
            out.append(ESCAPE_MAP[ch])
        elif ord(ch) > 127:
            decomposed = unicodedata.normalize("NFKD", ch)
            base = "".join(c for c in decomposed if not unicodedata.combining(c))
            out.append(ACCENTS.get(base, base))
        else:
            out.append(ch)
    return "".join(out)


def author_field(meta):
    names = []
    for a in meta.get("authors", []):
        fam, giv = a.get("family", "").strip(), a.get("given", "").strip()
        if fam and giv:
            names.append(f"{texify(fam)}, {texify(giv)}")
        elif fam or giv or a.get("name"):
            names.append(texify(fam or giv or a["name"]))
    return " and ".join(names)


def main():
    with open("tools/doi_metadata.json", encoding="utf-8") as fh:
        meta_all = json.load(fh)
    with open("tools/curated_dois.json", encoding="utf-8") as fh:
        curated = json.load(fh)

    lines = [
        "% Bibliography for the IEEE conference submission.",
        "%",
        "% Every entry carries a DOI. Author lists, titles and pagination were",
        "% taken from Crossref/DataCite records and verified by resolving each DOI",
        "% (see tools/verify_dois.py and tools/doi_verification.json).",
        "%",
        "% ICLR, ICML (PMLR) and NeurIPS proceedings do not issue DOIs. For papers",
        "% published at those venues the DOI field points to the arXiv record of the",
        "% same work, which is the freely available version.",
        "",
    ]

    missing = []
    for key in ORDER:
        meta = meta_all.get(key)
        if meta is None:
            missing.append(key)
            continue
        typ, venue_field, venue_val, extra = VENUE.get(key, ("article", "journal", None, {}))

        fields = {}
        title = TITLE_FIX.get(key) or texify(meta["title"])
        fields["title"] = title
        fields["author"] = AUTHOR_FIX.get(key) or author_field(meta)
        if venue_val is not None:
            fields[venue_field] = texify(venue_val)

        if typ == "article" and venue_val is None:
            fields["journal"] = texify(meta.get("container") or "")

        # Journal-derived numeric fields, unless overridden.
        if "volume" not in extra and meta.get("volume"):
            fields["volume"] = str(meta["volume"])
        if "number" not in extra and meta.get("issue"):
            fields["number"] = str(meta["issue"])
        if "pages" not in extra and meta.get("page") and meta["page"] != "1-1":
            fields["pages"] = meta["page"].replace("--", "-").replace("-", "--")
        if meta.get("article_number") and "pages" not in fields and "pages" not in extra:
            fields["pages"] = str(meta["article_number"])

        fields.update(extra)
        fields.update(NUM_FIX.get(key, {}))

        year = extra.get("year") or meta.get("year")
        if year:
            fields["year"] = str(year)

        # The DOI alone is emitted: IEEEtran.bst would otherwise add a second
        # "Available: https://doi.org/..." line that duplicates it and lengthens
        # every entry. The DOI resolves to the same landing page.
        fields["doi"] = curated[key]["doi"]

        lines.append(f"@{typ}{{{key},")
        for name in ["author", "title", "journal", "booktitle", "publisher",
                     "volume", "number", "pages", "year", "doi"]:
            if name in fields and fields[name]:
                lines.append(f"  {name} = {{{fields[name]}}},")
        lines.append("}")
        lines.append("")

    if missing:
        raise SystemExit(f"missing metadata for: {missing}")

    out = "\n".join(lines)
    with open("tools/references_new.bib", "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"wrote tools/references_new.bib with {len(ORDER)} entries")


if __name__ == "__main__":
    main()
