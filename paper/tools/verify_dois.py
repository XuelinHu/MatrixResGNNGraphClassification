"""Resolve each curated DOI and print the authoritative title it points at.

This is the reverse check: a DOI is only accepted if the metadata service
returns a title that matches the intended reference.
"""
import json
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "BibVerify/1.0 (mailto:researcher@example.com)"
STOP = {"a", "an", "the", "of", "on", "in", "for", "and", "with", "to", "via", "using"}


def norm(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = "".join(c if c.isalnum() or c == " " else " " for c in text)
    return " ".join(w for w in text.split() if w not in STOP)


def sim(a, b):
    sa, sb = set(a.split()), set(b.split())
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def resolve(doi):
    """Try Crossref first, then DataCite (arXiv DOIs live in DataCite)."""
    req = urllib.request.Request(
        "https://api.crossref.org/works/" + urllib.parse.quote(doi),
        headers={"User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            m = json.load(r)["message"]
            return {
                "title": (m.get("title") or [""])[0],
                "container": (m.get("container-title") or [None])[0],
                "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "type": m.get("type"),
                "source": "crossref",
            }
    except Exception:  # noqa: BLE001 - fall through to DataCite
        pass
    req = urllib.request.Request(
        "https://api.datacite.org/dois/" + urllib.parse.quote(doi),
        headers={"User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            a = json.load(r)["data"]["attributes"]
            return {
                "title": (a.get("titles") or [{}])[0].get("title", ""),
                "container": a.get("publisher"),
                "year": a.get("publicationYear"),
                "type": (a.get("types") or {}).get("resourceTypeGeneral"),
                "source": "datacite",
            }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def main():
    with open("tools/curated_dois.json", encoding="utf-8") as fh:
        curated = json.load(fh)

    report = {}
    bad = []
    for key, item in curated.items():
        doi = item["doi"]
        got = resolve(doi)
        score = sim(norm(item["title"]), norm(got.get("title", ""))) if "title" in got else 0.0
        report[key] = {"doi": doi, "expected": item["title"], "resolved": got, "score": round(score, 3)}
        if score >= 0.6:
            print(f"OK  [{score:.2f}] {key:34s} {doi}")
            print(f"            -> {got.get('title', '')[:88]}")
        else:
            bad.append(key)
            print(f"BAD [{score:.2f}] {key:34s} {doi}")
            print(f"            expected: {item['title'][:80]}")
            print(f"            resolved: {got.get('title', got.get('error', ''))[:80]}")
        time.sleep(0.35)

    with open("tools/doi_verification.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"\n{len(curated) - len(bad)}/{len(curated)} verified")
    if bad:
        print("NEEDS REVIEW:", bad)


if __name__ == "__main__":
    main()
