"""Fetch full bibliographic metadata for each curated DOI.

Writes tools/doi_metadata.json with authors, container, volume, issue, pages,
year and type, so the final .bib can be assembled from authoritative records
rather than from memory.
"""
import json
import time
import urllib.parse
import urllib.request

UA = "BibVerify/1.0 (mailto:researcher@example.com)"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def crossref(doi):
    m = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    authors = []
    for a in m.get("author") or []:
        authors.append(
            {
                "given": a.get("given", ""),
                "family": a.get("family", ""),
                "name": a.get("name", ""),
            }
        )
    return {
        "source": "crossref",
        "title": (m.get("title") or [""])[0],
        "authors": authors,
        "container": (m.get("container-title") or [None])[0],
        "short_container": (m.get("short-container-title") or [None])[0],
        "event": (m.get("event") or {}).get("name"),
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "page": m.get("page"),
        "article_number": m.get("article-number"),
        "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    }


def datacite(doi):
    a = get_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi))["data"]["attributes"]
    authors = []
    for cr in a.get("creators") or []:
        authors.append(
            {
                "given": cr.get("givenName", ""),
                "family": cr.get("familyName", ""),
                "name": cr.get("name", ""),
            }
        )
    return {
        "source": "datacite",
        "title": (a.get("titles") or [{}])[0].get("title", ""),
        "authors": authors,
        "container": a.get("publisher"),
        "year": a.get("publicationYear"),
        "type": (a.get("types") or {}).get("resourceTypeGeneral"),
        "publisher": a.get("publisher"),
    }


def main():
    with open("tools/curated_dois.json", encoding="utf-8") as fh:
        curated = json.load(fh)
    out = {}
    for key, item in curated.items():
        doi = item["doi"]
        try:
            meta = crossref(doi)
        except Exception:
            try:
                meta = datacite(doi)
            except Exception as exc:  # noqa: BLE001
                meta = {"error": str(exc)}
        meta["curated_title"] = item["title"]
        out[key] = meta
        n = len(meta.get("authors", []))
        print(f"{key:36s} {meta.get('source','?'):9s} authors={n:2d} {meta.get('year')} | {(meta.get('container') or '')[:44]}")
        time.sleep(0.3)
    with open("tools/doi_metadata.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nwrote tools/doi_metadata.json")


if __name__ == "__main__":
    main()
