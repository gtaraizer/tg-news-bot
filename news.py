
import requests
from bs4 import BeautifulSoup
import feedparser
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com/bot)"
}

SOURCES = [
    {
        "name": "banki",
        "type": "html",
        "url": "https://www.banki.ru/news/",
        "selector": "a.WidgetNews__title",
        "link_prefix": "https://www.banki.ru"
    },
    {
        "name": "ria-economy",
        "type": "rss",
        "url": "https://ria.ru/export/rss2/economy/index.xml"
    },
]

def _fetch_html_list(url: str, selector: str, link_prefix: str = "") -> List[Dict]:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for a in soup.select(selector)[:8]:
        href = a.get("href")
        if not href:
            continue
        link = href if href.startswith("http") else f"{link_prefix}{href}"
        title = a.get_text(strip=True)
        if title and link:
            items.append({"title": title, "link": link})
    return items

def _fetch_rss(url: str) -> List[Dict]:
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:8]:
        link = e.get("link")
        title = e.get("title")
        if link and title:
            items.append({"title": title, "link": link})
    return items

def get_candidates() -> List[Dict]:
    all_items = []
    for src in SOURCES:
        try:
            if src["type"] == "html":
                items = _fetch_html_list(src["url"], src["selector"], src.get("link_prefix", ""))
            elif src["type"] == "rss":
                items = _fetch_rss(src["url"])
            else:
                items = []
            for it in items:
                it["source"] = src["name"]
            all_items.extend(items)
        except Exception:
            continue
    return all_items

def fetch_article_text(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        from readability import Document
        doc = Document(r.text)
        html = doc.summary(html_partial=True)
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text("\n", strip=True)
        return text[:12000]
    except Exception:
        return ""
