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


def save_site(url, html, name):
    """Guarda una copia estática navegable (HTML + css/js/imágenes) en data/site/."""
    site = OUT / "site"
    site.mkdir(parents=True, exist_ok=True)
    (site / name).write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    refs = {urljoin(url, t[a]) for t, a in
            [(x, "src") for x in soup.find_all(src=True)] +
            [(x, "href") for x in soup.find_all("link", href=True)]}
    for ref in refs:
        ref = urldefrag(ref)[0]
        path = urlparse(ref).path.lstrip("/")
        if urlparse(ref).netloc != urlparse(BASE).netloc or not path:
            continue
        a = requests.get(ref, headers=HEADERS, timeout=20)
        if a.status_code == 200:
            dest = site / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(a.content)


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
        save_site(url, r.text, name)
        pages.append(page)
        queue += [l for l in page["links"] if urlparse(l).netloc == host and l not in seen]
        print("OK", url)
        time.sleep(1)
    (OUT / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
