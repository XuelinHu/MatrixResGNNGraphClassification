"""Fetch full metadata for a list of DOIs supplied on the command line."""
import json
import sys
import urllib.parse
import urllib.request

UA = "BibVerify/1.0 (mailto:researcher@example.com)"


def crossref(doi):
    req = urllib.request.Request(
        "https://api.crossref.org/works/" + urllib.parse.quote(doi),
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]


def main():
    for doi in sys.argv[1:]:
        try:
            m = crossref(doi)
        except Exception as exc:  # noqa: BLE001
            print(f"{doi}\n  ERROR: {exc}\n")
            continue
        authors = ", ".join(
            f"{a.get('given','')} {a.get('family','')}".strip()
            for a in (m.get("author") or [])
        )
        print(f"DOI        : {doi}")
        print(f"  title    : {(m.get('title') or [''])[0]}")
        print(f"  authors  : {authors}")
        print(f"  container: {(m.get('container-title') or [None])[0]}")
        print(f"  vol/iss  : {m.get('volume')} / {m.get('issue')}")
        print(f"  pages    : {m.get('page')}  art: {m.get('article-number')}")
        print(f"  year     : {(m.get('issued', {}).get('date-parts') or [[None]])[0][0]}")
        print(f"  type     : {m.get('type')}")
        print()


if __name__ == "__main__":
    main()
