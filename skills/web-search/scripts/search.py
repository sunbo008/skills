#!/usr/bin/env python3
"""
Multi-engine web search without API keys.
Supports: baidu (default), bing, ddgs
Usage:
    python search.py "search query" [--engine baidu|bing|ddgs] [--max N] [--json]
"""
import argparse
import json
import random
import re
import sys
import textwrap
import time
import urllib.parse

def _get_requests_and_bs4():
    try:
        import requests
        from bs4 import BeautifulSoup
        return requests, BeautifulSoup
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests", "beautifulsoup4"])
        import requests
        from bs4 import BeautifulSoup
        return requests, BeautifulSoup

_UA_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

def _make_session():
    requests, _ = _get_requests_and_bs4()
    session = requests.Session()
    ua = random.choice(_UA_LIST)
    session.headers.update({
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    })
    return session

# ---------------------------------------------------------------------------
# Baidu
# ---------------------------------------------------------------------------
def _is_baidu_ad(container, href: str) -> bool:
    if not href:
        return True
    ad_patterns = ["baidu.com/baidu.php", "pos.baidu.com", "click.hm.baidu.com",
                   "smartapps.baidu.com"]
    if any(p in href for p in ad_patterns):
        return True
    full_text = container.get_text()
    if "广告" in full_text[-20:]:
        return True
    if container.select_one("span[class*='ec-']"):
        return True
    return False

def _extract_baidu_desc(container):
    """Extract description from a Baidu result container."""
    _, BeautifulSoup = _get_requests_and_bs4()
    clone = BeautifulSoup(str(container), "html.parser")
    for tag in clone.find_all("h3"):
        tag.decompose()
    for tag in clone.find_all("style"):
        tag.decompose()
    for tag in clone.find_all("script"):
        tag.decompose()

    for sel in [
        "span.content-right_8Zs40",
        "div.c-abstract",
        "span.c-abstract",
        "div[class*='content-right']",
        "span[class*='content-right']",
    ]:
        tag = clone.select_one(sel)
        if tag:
            text = tag.get_text(strip=True)
            if len(text) > 15:
                return text

    text = clone.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    for noise in ["百度快照", "百度首页", "播报", "暂停", "收起"]:
        text = text.replace(noise, "")
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = re.sub(r"[.\s]+$", "", text).strip()
    return text if len(text) > 10 else ""

def _resolve_baidu_url(session, baidu_link: str) -> str:
    if not baidu_link or "baidu.com/link" not in baidu_link:
        return baidu_link
    try:
        r = session.head(baidu_link, timeout=5, allow_redirects=True)
        return r.url
    except Exception:
        return baidu_link

def search_baidu(query: str, max_results: int = 8) -> list:
    requests, BeautifulSoup = _get_requests_and_bs4()
    session = _make_session()

    session.get("https://www.baidu.com/", timeout=10)
    time.sleep(random.uniform(0.3, 0.8))

    results = []
    page = 0
    while len(results) < max_results:
        params = {"wd": query, "pn": page * 10, "rn": 10, "ie": "utf-8"}
        url = "https://www.baidu.com/s?" + urllib.parse.urlencode(params)
        session.headers["Referer"] = "https://www.baidu.com/"
        resp = session.get(url, timeout=15)
        resp.encoding = "utf-8"

        if "百度安全验证" in resp.text:
            print("[warn] Baidu captcha detected, aborting baidu engine", file=sys.stderr)
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        containers = soup.select("div.result.c-container")
        if not containers:
            containers = soup.select("div.c-container[id]")
        if not containers:
            break

        found_any = False
        for c in containers:
            if len(results) >= max_results:
                break
            h3 = c.find("h3")
            if not h3:
                continue
            a = h3.find("a")
            if not a:
                continue
            href = a.get("href", "")
            if _is_baidu_ad(c, href):
                continue

            title = a.get_text(strip=True)
            real_url = _resolve_baidu_url(session, href)
            description = _extract_baidu_desc(c)

            results.append({
                "title": title,
                "href": real_url,
                "body": description,
            })
            found_any = True

        if not found_any:
            break
        page += 1
        if page > 3:
            break
        time.sleep(random.uniform(0.2, 0.5))
    return results

# ---------------------------------------------------------------------------
# Bing
# ---------------------------------------------------------------------------
def _extract_bing_desc(li):
    """Extract description from a Bing result item."""
    for sel in [
        "div.b_caption p",
        "p.b_lineclamp2",
        "p.b_lineclamp3",
        "p.b_lineclamp4",
        "div.b_caption .b_snippet",
        "p",
    ]:
        tag = li.select_one(sel)
        if tag:
            text = tag.get_text(strip=True)
            if len(text) > 10:
                return text
    return ""

def search_bing(query: str, max_results: int = 8) -> list:
    requests, BeautifulSoup = _get_requests_and_bs4()
    session = _make_session()
    results = []
    page = 0
    while len(results) < max_results:
        params = {"q": query, "first": page * 10 + 1, "count": 10}
        url = "https://www.bing.com/search?" + urllib.parse.urlencode(params)
        resp = session.get(url, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select("li.b_algo")
        if not items:
            break

        for li in items:
            if len(results) >= max_results:
                break
            h2 = li.find("h2")
            if not h2:
                continue
            a = h2.find("a")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            description = _extract_bing_desc(li)

            results.append({
                "title": title,
                "href": href,
                "body": description,
            })

        page += 1
        if page > 3:
            break
    return results

# ---------------------------------------------------------------------------
# DuckDuckGo (via ddgs library)
# ---------------------------------------------------------------------------
def search_ddgs(query: str, max_results: int = 8) -> list:
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "ddgs"])
            from ddgs import DDGS
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

# ---------------------------------------------------------------------------
# Engine dispatcher with auto-fallback
# ---------------------------------------------------------------------------
ENGINE_MAP = {
    "baidu": search_baidu,
    "bing": search_bing,
    "ddgs": search_ddgs,
}
FALLBACK_ORDER = ["baidu", "bing", "ddgs"]

def search(query: str, engine: str = "baidu", max_results: int = 8) -> list:
    """Search with the chosen engine; auto-fallback on failure."""
    order = [engine] + [e for e in FALLBACK_ORDER if e != engine]
    last_err = None
    for eng in order:
        try:
            results = ENGINE_MAP[eng](query, max_results)
            if results:
                if eng != engine:
                    print(f"[info] {engine} unavailable, fell back to {eng}", file=sys.stderr)
                return results
        except Exception as e:
            last_err = e
            print(f"[warn] {eng} error: {e}", file=sys.stderr)
    if last_err:
        raise last_err
    return []

# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def format_results(results: list) -> str:
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("href") or r.get("url", "")
        body = r.get("body") or r.get("description", "")
        date = r.get("date", "")
        lines.append(f"[{i}] {title}")
        if date:
            lines.append(f"    Date: {date}")
        lines.append(f"    URL:  {url}")
        if body:
            wrapped = textwrap.fill(body, width=80, initial_indent="    ",
                                    subsequent_indent="    ")
            lines.append(wrapped)
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Multi-engine web search (no API key)")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--engine", choices=["baidu", "bing", "ddgs"], default="baidu",
                        help="Search engine (default: baidu)")
    parser.add_argument("--max", type=int, default=8, help="Max results (default: 8)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    results = search(args.query, engine=args.engine, max_results=args.max)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_results(results))

if __name__ == "__main__":
    main()
