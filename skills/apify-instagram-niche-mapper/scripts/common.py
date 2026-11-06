"""Shared helpers for the instagram-niche-mapper scripts."""
import json
import re
import sys

import pandas as pd


def load_items(paths):
    """Load Apify dataset items from one or more JSON files (list or JSONL)."""
    items = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            continue
        if text.startswith("["):
            items.extend(json.loads(text))
        else:
            items.extend(json.loads(line) for line in text.splitlines() if line.strip())
    return items


def plays_of(x):
    """Reel plays. Apify returns plays in videoPlayCount; fall back to the others."""
    for k in ("videoPlayCount", "igPlayCount", "videoViewCount"):
        v = x.get(k)
        if v is not None:
            return float(v)
    return None


def original_audio(x):
    m = x.get("musicInfo")
    if isinstance(m, dict):
        return m.get("uses_original_audio")
    return x.get("musicInfo.uses_original_audio")


def creator_of(x):
    """The account the reel was requested for (keeps collab reels with the right creator)."""
    u = x.get("inputUrl") or ""
    m = re.search(r"instagram\.com/([^/?#]+)/?$", u.rstrip("/") + "/")
    name = m.group(1) if m else None
    if name and name not in ("p", "reel", "explore", "popular"):
        return name
    return x.get("ownerUsername")


def query_of(x):
    u = (x.get("inputUrl") or "").rstrip("/")
    q = u.split("/")[-1].replace("?q=", "").replace("%20", " ")
    return q


def first_line(caption):
    """First line of a caption that is not just hashtags, mentions or punctuation."""
    for line in (caption or "").strip().split("\n"):
        line = line.strip()
        if line and not re.fullmatch(r"[#@.\s\W]*", line) and not re.fullmatch(r"(#\S+\s*)+", line):
            return line
    return ""


def first_line_type(line):
    s = line.lower()
    if "?" in line[:200]:
        return "question"
    if re.search(r"\b(just|new|now|announced|rolling out|launch(ed|es)?|update|breaking|this week)\b", s):
        return "news"
    if re.search(r"\b(how to|how i|steps?|do this|here.?s how|tips?|checklist|guide|ways|hack|trick)\b|^\d", s):
        return "how-to"
    return "claim"


COMMENT_CTA = re.compile(
    r"(?i)comment\s*[\"“”'‘’*]+\s*\w+|comment\s+[A-Z]{2,}\b|DM (?:me|us)?\s*[\"“”]?[A-Z]{2,}"
)


def topic_regex(words):
    """Build a case-insensitive regex from comma-separated topic words/phrases.
    Plain words match on word boundaries and as hashtags (#word, #wordtips)."""
    parts = []
    for w in [w.strip() for w in words.split(",") if w.strip()]:
        esc = re.escape(w).replace(r"\ ", r"[\s_-]?")
        parts.append(rf"\b{esc}\b|#\w*{esc}\w*")
    return re.compile("|".join(parts), re.I)


def non_latin_share(texts):
    """Share of letters that are not Latin script; a rough language signal."""
    letters = [ch for t in texts for ch in (t or "") if ch.isalpha()]
    if not letters:
        return None
    nl = sum(1 for ch in letters if ord(ch) > 0x024F)
    return nl / len(letters)


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def to_ts(s):
    return pd.to_datetime(s, utc=True, errors="coerce")
