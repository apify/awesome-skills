#!/usr/bin/env python3
"""Fetch Apify dataset items and clean article HTML via readability-lxml.

Usage:
    python3 extract_and_clean.py <datasetId> [--limit N]

Output: JSON array of cleaned articles to stdout.

For rag-web-browser items (HTML): strips nav/menu/footer via readability.
For workhard3000/bloomberg items (already clean): passes through as-is.

Requirements: pip install readability-lxml lxml
Environment: APIFY_TOKEN must be set.
"""

import json
import os
import re
import sys
import urllib.request

TOKEN = os.environ.get("APIFY_TOKEN", "")
BASE = "https://api.apify.com/v2"


def fetch_items(dataset_id: str, limit: int = 50) -> list:
    """Fetch items from Apify dataset."""
    url = f"{BASE}/datasets/{dataset_id}/items?limit={limit}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def clean_html(html: str) -> dict:
    """Extract clean article text from HTML using readability-lxml."""
    from readability import Document

    doc = Document(html)
    title = doc.title()
    clean = doc.summary()
    text = re.sub(r"<[^>]+>", " ", clean)
    text = re.sub(r"\s+", " ", text).strip()
    return {"title": title, "text": text, "chars": len(text)}


def process_item(item: dict) -> dict:
    """Process a single dataset item. Auto-detects format."""
    result = {}

    # rag-web-browser items have 'html' and/or 'text' fields + metadata
    html = item.get("html", "")
    raw_text = item.get("text", "")
    metadata = item.get("metadata", {})

    # Bloomberg scraper items have 'headline', 'body', etc.
    headline = item.get("headline", "")

    # workhard3000 items have 'title', 'text', 'byline', etc.
    wh_title = item.get("title", "")
    wh_text = item.get("text", "")

    if html and len(html) > 200:
        # rag-web-browser with HTML — clean it
        cleaned = clean_html(html)
        result = {
            "title": cleaned["title"],
            "text": cleaned["text"],
            "chars": cleaned["chars"],
            "url": metadata.get("url", item.get("url", "")),
            "source": "rag-web-browser",
            "cleaned": True,
        }
    elif headline:
        # Bloomberg scraper — already structured
        body = item.get("body", "")
        if isinstance(body, list):
            # Bloomberg body is structured JSON
            body = json.dumps(body)
        result = {
            "title": headline,
            "text": str(body),
            "chars": len(str(body)),
            "url": item.get("url", ""),
            "source": "bloomberg-scraper",
            "cleaned": False,
        }
    elif wh_title and wh_text:
        # workhard3000 — already clean text
        result = {
            "title": wh_title,
            "text": wh_text,
            "chars": len(wh_text),
            "url": item.get("url", ""),
            "author": item.get("byline", item.get("author", "")),
            "date": item.get("publishedDate", item.get("date", "")),
            "source": "workhard3000",
            "cleaned": False,
        }
    elif raw_text and len(raw_text) > 100:
        # Fallback: raw text without HTML
        result = {
            "title": metadata.get("title", "") if metadata else "",
            "text": raw_text,
            "chars": len(raw_text),
            "url": metadata.get("url", item.get("url", "")),
            "source": "raw-text",
            "cleaned": False,
        }
    else:
        # Empty or unrecognized format
        result = {
            "title": "",
            "text": "",
            "chars": 0,
            "url": item.get("url", ""),
            "source": "unknown",
            "cleaned": False,
            "error": "No extractable content",
        }

    # Warn on likely paywall/blocked extraction
    if result.get("chars", 0) < 500 and result.get("cleaned"):
        result["quality_warning"] = f"Low content ({result['chars']} chars) — likely paywalled or blocked"

    return result


MIN_CHARS_WARN = 500


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_and_clean.py <datasetId> [--limit N]", file=sys.stderr)
        sys.exit(1)

    dataset_id = sys.argv[1]
    limit = 50
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])

    if not TOKEN:
        print("ERROR: APIFY_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    items = fetch_items(dataset_id, limit)
    results = []
    for item in items:
        if isinstance(item, dict):
            results.append(process_item(item))

    # Summary to stderr
    total = len(results)
    cleaned = sum(1 for r in results if r.get("cleaned"))
    passthrough = sum(1 for r in results if not r.get("cleaned") and r.get("chars", 0) > 0)
    empty = sum(1 for r in results if r.get("chars", 0) == 0)
    low_quality = sum(1 for r in results if r.get("quality_warning"))
    print(f"Processed {total} items: {cleaned} cleaned, {passthrough} passthrough, {empty} empty", file=sys.stderr)
    if low_quality:
        print(f"WARNING: {low_quality} items below {MIN_CHARS_WARN} chars (likely paywalled)", file=sys.stderr)

    # Output to stdout
    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
