"""Query Crossref/DataCite for a list of titles and print top candidates."""
import json
import sys
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


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def crossref(title, rows=5):
    params = urllib.parse.urlencode({"query.bibliographic": title, "rows": rows})
    data = get(f"https://api.crossref.org/works?{params}")
    out = []
    for it in data["message"]["items"]:
        t = (it.get("title") or [""])[0]
        out.append(
            {
                "score": round(sim(norm(title), norm(t)), 3),
                "doi": it.get("DOI"),
                "title": t,
                "type": it.get("type"),
                "container": (it.get("container-title") or [None])[0],
                "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            }
        )
    return sorted(out, key=lambda x: -x["score"])


if __name__ == "__main__":
    for line in sys.stdin:
        title = line.strip()
        if not title:
            continue
        print("=" * 100)
        print("QUERY:", title)
        try:
            for c in crossref(title)[:4]:
                print(f"  [{c['score']:.2f}] {c['doi']}")
                print(f"        {c['title'][:95]}")
                print(f"        {c['container']} | {c['year']} | {c['type']}")
        except Exception as exc:  # noqa: BLE001
            print("  ERROR:", exc)
        time.sleep(0.5)
