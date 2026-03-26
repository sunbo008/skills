---
name: web-search
description: Perform web searches and fetch web page content without any API keys, supporting Baidu, Bing, and DuckDuckGo search engines. Use this skill whenever the user needs to search the internet, look up current information, find documentation, research a topic, check latest news, or fetch content from a URL. Also trigger when the user mentions searching online, googling something, looking something up on the web, or needs real-time/up-to-date information that the model doesn't have. Even if the user just casually says "search for", "look up", "query", or "find", use this skill.
---

# Web Search (No API Key Required)

Multi-engine web search and page content extraction — no API keys needed.

Supported engines: **Baidu** (default), **Bing**, **DuckDuckGo**. Auto-fallback: if the chosen engine fails, the script tries the next one automatically.

## First-Time Setup

If `~/.cursor/skills/web-search/.venv` does not exist, run:

```bash
bash ~/.cursor/skills/web-search/scripts/setup.sh
```

## Python Executable

Always use the venv Python (`$PY` below):

```
~/.cursor/skills/web-search/.venv/bin/python
```

## Scripts

### 1. Web Search — `search.py`

```bash
# Baidu search (default)
$PY ~/.cursor/skills/web-search/scripts/search.py "搜索内容"

# Use Bing
$PY ~/.cursor/skills/web-search/scripts/search.py "query" --engine bing

# Use DuckDuckGo
$PY ~/.cursor/skills/web-search/scripts/search.py "query" --engine ddgs

# Limit results
$PY ~/.cursor/skills/web-search/scripts/search.py "query" --max 5

# JSON output
$PY ~/.cursor/skills/web-search/scripts/search.py "query" --json
```

Engine selection tips:
- **baidu**: Best for Chinese content, very stable in China
- **bing**: Good for both Chinese and English, stable worldwide
- **ddgs**: DuckDuckGo, privacy-friendly but may be unstable in some networks

### 2. Fetch Page — `fetch.py`

```bash
$PY ~/.cursor/skills/web-search/scripts/fetch.py "https://example.com/article"
$PY ~/.cursor/skills/web-search/scripts/fetch.py "https://example.com" --max-chars 8000
$PY ~/.cursor/skills/web-search/scripts/fetch.py "https://example.com" --json
```

Strips scripts, styles, navigation — returns clean readable text.

## Typical Workflow

1. **Search** for the topic
2. **Fetch** the best result(s)
3. **Summarize** or extract needed information

```bash
$PY ~/.cursor/skills/web-search/scripts/search.py "Python dataclass 用法"
$PY ~/.cursor/skills/web-search/scripts/fetch.py "https://docs.python.org/zh-cn/3/library/dataclasses.html"
```

## Notes

- Baidu ads are auto-filtered; redirect links are auto-resolved to real URLs
- All commands need network access — request `all` permissions when running via Shell tool
- Some sites block automated access; try a different URL from results if one fails
