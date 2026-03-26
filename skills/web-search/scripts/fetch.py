#!/usr/bin/env python3
"""
Fetch a web page and extract readable text content.
Usage:
    python fetch.py "https://example.com" [--max-chars N]
"""
import argparse
import json
import sys
import re

def ensure_deps():
    mods = {}
    try:
        import requests
        mods["requests"] = requests
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests"])
        import requests
        mods["requests"] = requests

    try:
        from bs4 import BeautifulSoup
        mods["BeautifulSoup"] = BeautifulSoup
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "beautifulsoup4"])
        from bs4 import BeautifulSoup
        mods["BeautifulSoup"] = BeautifulSoup

    return mods

def fetch_page(url: str, max_chars: int = 15000) -> dict:
    mods = ensure_deps()
    requests = mods["requests"]
    BeautifulSoup = mods["BeautifulSoup"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main is None:
        main = soup

    text = main.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n... [truncated]"

    return {"title": title, "url": url, "content": text}

def main():
    parser = argparse.ArgumentParser(description="Fetch and extract web page text")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--max-chars", type=int, default=15000,
                        help="Max characters to return (default: 15000)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = fetch_page(args.url, args.max_chars)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Title: {result['title']}")
        print(f"URL:   {result['url']}")
        print("-" * 60)
        print(result["content"])

if __name__ == "__main__":
    main()
