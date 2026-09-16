"""Resolve DOIs for cited bib entries via the Crossref REST API.

Queries Crossref by bibliographic string, scores candidate titles with a
normalised token-overlap measure, and writes the results to dois_resolved.json
for review. Nothing is written back to references.bib by this script.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MAILTO = "researcher@example.com"
CROSSREF = "https://api.crossref.org/works"
UA = f"MatrixResGNGBibTool/1.0 (mailto:{MAILTO})"

# Normalised-title allowlist for entries whose bibliographic record is
# ambiguous or where the well-known published version is wanted explicitly.
OVERRIDES = {
    "kipf2017gcn": "Semi-Supervised Classification with Graph Convolutional Networks",
    "xu2019gin": "How Powerful are Graph Neural Networks",
    "velivckovic2017graph": "Graph Attention Networks",
    "hamilton2017inductive": "Inductive Representation Learning on Large Graphs",
    "he2016deep": "Deep Residual Learning for Image Recognition",
    "gilmer2017neural": "Neural Message Passing for Quantum Chemistry",
    "ying2018hierarchical": "Hierarchical Graph Representation Learning with Differentiable Pooling",
    "wu2020comprehensive": "A Comprehensive Survey on Graph Neural Networks",
    "xu2018representation": "Representation Learning on Graphs with Jumping Knowledge Networks",
    "li2019deepgcns": "DeepGCNs: Can GCNs Go as Deep as CNNs",
    "kingma2014adam": "Adam: A Method for Stochastic Optimization",
    "rong2019dropedge": "DropEdge: Towards Deep Graph Convolutional Networks on Node Classification",
    "bresson2017residual": "Residual Gated Graph ConvNets",
    "oono2020simple": "Simple and Deep Graph Convolutional Networks",
    "topping2021understanding": "Understanding over-squashing and bottlenecks on graphs via curvature",
    "alon2020bottleneck": "On the Bottleneck of Graph Neural Networks and its Practical Implications",
    "keriven2020benchmark": "A Unified Benchmark for the Diagnosis and Treatment of Graph Neural Networks",
    "fey2019fast": "Fast Graph Representation Learning with PyTorch Geometric",
    "dwivedi2020generalization": "A Generalization of Transformer Networks to Graphs",
    "morris2020tudataset": "TUDataset: A Collection of Benchmark Datasets for Learning with Graphs",
    "lee2019self": "Self-Attention Graph Pooling",
    "gilmor2017neural": None,
}

STOP = {"a", "an", "the", "of", "on", "in", "for", "and", "with", "to", "via"}


def norm(text):
    """Lowercase, strip accents/punctuation, drop stopwords."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    words = [w for w in text.split() if w and w not in STOP]
    return " ".join(words)


def similar(a, b):
    """Token Jaccard similarity between two normalised titles."""
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def crossref_lookup(title, author_hint=None):
    """Return the best Crossref candidate for a title, or None."""
    query = title
    if author_hint:
        query = f"{title} {author_hint}"
    params = urllib.parse.urlencode(
        {"query.bibliographic": query, "rows": 5, "select": "DOI,title,author,type,container-title,issued,volume,issue,page,publisher,event"}
    )
    try:
        data = fetch(f"{CROSSREF}?{params}")
    except Exception as exc:  # noqa: BLE001 - network variability
        return {"error": str(exc)}

    target = norm(title)
    best = None
    for item in data.get("message", {}).get("items", []):
        cand_titles = item.get("title") or []
        if not cand_titles:
            continue
        score = similar(target, norm(cand_titles[0]))
        if best is None or score > best["score"]:
            best = {
                "score": round(score, 3),
                "doi": item.get("DOI"),
                "title": cand_titles[0],
                "type": item.get("type"),
                "container": (item.get("container-title") or [None])[0],
                "publisher": item.get("publisher"),
                "volume": item.get("volume"),
                "issue": item.get("issue"),
                "page": item.get("page"),
                "year": (item.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "event": (item.get("event") or {}).get("name"),
                "authors": [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in (item.get("author") or [])
                ][:12],
            }
    return best


def arxiv_lookup(title, author_hint=None):
    """Return an arXiv DOI for a preprint title, or None."""
    query = f'ti:"{title}"'
    if author_hint:
        query += f' AND au:"{author_hint}"'
    params = urllib.parse.urlencode({"search_query": query, "max_results": 3})
    try:
        raw = urllib.request.urlopen(
            urllib.request.Request(
                f"http://export.arxiv.org/api/query?{params}", headers={"User-Agent": UA}
            ),
            timeout=30,
        ).read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}

    entries = re.findall(r"<entry>(.*?)</entry>", raw, re.S)
    target = norm(title)
    best = None
    for entry in entries:
        m = re.search(r"<title>(.*?)</title>", entry, re.S)
        if not m:
            continue
        cand = re.sub(r"\s+", " ", m.group(1)).strip()
        score = similar(target, norm(cand))
        if best is None or score > best["score"]:
            idm = re.search(r"<id>(.*?)</id>", entry)
            pub = re.search(r"<published>(\d{4})", entry)
            short = idm.group(1).rsplit("/abs/", 1)[-1] if idm else None
            best = {
                "score": round(score, 3),
                "arxiv_id": short,
                "title": cand,
                "year": pub.group(1) if pub else None,
                "doi": f"10.48550/arXiv.{short}" if short else None,
            }
    return best


def parse_bib():
    """Yield (key, type, field-dict) for every entry in references.bib."""
    with open("references.bib", encoding="utf-8") as fh:
        text = fh.read()
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        typ, key, body = m.group(1), m.group(2).strip(), m.group(3)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n", body, re.S):
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", fm.group(2)).strip()
        for fm in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', body):
            fields.setdefault(fm.group(1).lower(), fm.group(2).strip())
        yield key, typ, fields


def main():
    only = set(sys.argv[1:])
    cited = [k.strip() for k in open("cited_keys.txt", encoding="utf-8") if k.strip()]
    results = {}
    for key, typ, fields in parse_bib():
        if key not in cited:
            continue
        if only and key not in only:
            continue
        title = OVERRIDES.get(key) or fields.get("title", "")
        if not title:
            results[key] = {"status": "no-title"}
            continue
        author = fields.get("author", "").split(" and ")[0].split(",")[0].strip()
        cr = crossref_lookup(title, author)
        time.sleep(0.4)
        row = {
            "bib_title": title,
            "bib_type": typ,
            "has_doi": bool(fields.get("doi")),
            "existing_doi": fields.get("doi"),
            "crossref": cr,
        }
        strong = cr and cr.get("score", 0) >= 0.7
        if not strong:
            ar = arxiv_lookup(title, author)
            time.sleep(0.4)
            row["arxiv"] = ar
        results[key] = row
        flag = "OK " if strong else "?? "
        doi = (cr or {}).get("doi") if strong else (row.get("arxiv") or {}).get("doi")
        print(f"{flag}{key:28s} score={((cr or {}).get('score'))} doi={doi}")

    with open("tools/dois_resolved.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote tools/dois_resolved.json ({len(results)} entries)")


if __name__ == "__main__":
    main()
