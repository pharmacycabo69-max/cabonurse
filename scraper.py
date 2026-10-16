"""Scraper de cabonurse.com: rastrea enlaces internos y guarda HTML + datos en JSON."""
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://cabonurse.com/"
OUT = Path("data")
HEADERS = {"User-Agent": "Mozilla/5.0 (cabonurse-scraper)"}


def parse(url, html):
    soup = BeautifulSoup(html, "html.parser")
    meta = lambda **kw: (soup.find("meta", attrs=kw) or {}).get("content")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return {
        "url": url,
        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
        "description": meta(name="description"),
        "headings": [{"tag": h.name, "text": h.get_text(" ", strip=True)}
                     for h in soup.find_all(["h1", "h2", "h3"])],
        "links": sorted({urldefrag(urljoin(url, a["href"]))[0] for a in soup.find_all("a", href=True)}),
        "images": sorted({urljoin(url, i["src"]) for i in soup.find_all("img", src=True)}),
        "text": soup.get_text("\n", strip=True),
    }


def main():
    (OUT / "html").mkdir(parents=True, exist_ok=True)
    host = urlparse(BASE).netloc
    queue, seen, pages = [BASE], set(), []
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = "utf-8"
        if r.status_code != 200 or "text/html" not in r.headers.get("content-type", ""):
            continue
        name = (urlparse(url).path.strip("/").replace("/", "_") or "index") + ".html"
        (OUT / "html" / name).write_text(r.text, encoding="utf-8")
        page = parse(url, r.text)
        pages.append(page)
        queue += [l for l in page["links"] if urlparse(l).netloc == host and l not in seen]
        print("OK", url)
        time.sleep(1)
    (OUT / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
