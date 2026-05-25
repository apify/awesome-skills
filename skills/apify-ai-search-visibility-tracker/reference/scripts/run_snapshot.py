#!/usr/bin/env python3
"""
AI Search Visibility Tracker — snapshot runner.

Reads config.json + APIFY_TOKEN from env, calls apify/google-search-scraper,
appends parsed rows to a named Apify Dataset, writes a Markdown diff report.

Non-interactive by design -- no stdin reads. Suitable for invocation from
launchd, cron, Task Scheduler, or any other non-interactive caller.

Usage:
    APIFY_TOKEN=xxx python3 run_snapshot.py --config /path/to/config.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    sys.stderr.write("Error: 'requests' is required. Install with: pip3 install requests\n")
    sys.exit(2)

try:
    import tldextract
    _HAS_TLDEXTRACT = True
except ImportError:
    _HAS_TLDEXTRACT = False


USER_AGENT = "apify-awesome-skills/ai-search-visibility-tracker-1.0.0"
APIFY_API = "https://api.apify.com/v2"

SOURCE_FIELDS = {
    "ai_overviews": ("aiOverview", "ai_overview"),
    "ai_mode":      ("aiModeResult", "ai_mode_result"),
    "chatgpt":      ("chatGptSearchResult", "chat_gpt_search_result"),
    "perplexity":   ("perplexitySearchResult", "perplexity_search_result"),
    "copilot":      ("copilotSearchResult", "copilot_search_result"),
    "gemini":       ("geminiSearchResult", "gemini_search_result"),
}

SOURCE_TOGGLES = {
    "ai_mode":     ("aiModeSearch",     "enableAiMode"),
    "chatgpt":     ("chatGptSearch",    "enableChatGpt"),
    "perplexity":  ("perplexitySearch", "enablePerplexity"),
    "copilot":     ("copilotSearch",    "enableCopilot"),
    "gemini":      ("geminiSearch",     "enableGemini"),
}


# ---------- helpers ----------

def registrable_domain(url: str) -> str:
    """Return the registrable domain (e.g. apify.com) for a URL."""
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    if _HAS_TLDEXTRACT:
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}".lower().strip(".")
    host = (urlparse(url).hostname or "").lower()
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def mentions(text: str, surface_forms: list[str]) -> bool:
    if not text:
        return False
    for form in surface_forms:
        if not form:
            continue
        pattern = r"\b" + re.escape(form) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def load_dotenv_into_env(config_dir: Path) -> None:
    """Best-effort .env loader (no python-dotenv dependency)."""
    env_path = config_dir / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def log(msg: str) -> None:
    print(f"[{dt.datetime.utcnow().isoformat()}Z] {msg}", flush=True)


# ---------- Apify API ----------

def api_headers(token: str, suffix: str) -> dict[str, str]:
    return {"User-Agent": f"{USER_AGENT}/{suffix}", "Authorization": f"Bearer {token}"}


def get_or_create_dataset(token: str, name: str) -> str:
    """Return the dataset ID for a named dataset; create it if missing."""
    resp = requests.get(
        f"{APIFY_API}/datasets",
        params={"unnamed": "false", "limit": 1000},
        headers=api_headers(token, "list_datasets"),
        timeout=30,
    )
    resp.raise_for_status()
    for item in resp.json().get("data", {}).get("items", []):
        if item.get("name") == name:
            return item["id"]
    resp = requests.post(
        f"{APIFY_API}/datasets",
        params={"name": name},
        headers=api_headers(token, "create_dataset"),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def start_actor(token: str, actor_id: str, actor_input: dict) -> tuple[str, str]:
    api_actor = actor_id.replace("/", "~")
    resp = requests.post(
        f"{APIFY_API}/acts/{api_actor}/runs",
        headers={**api_headers(token, "start_actor"), "Content-Type": "application/json"},
        json=actor_input,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()["data"]
    return data["id"], data["defaultDatasetId"]


def poll_until_done(token: str, run_id: str, timeout_s: int = 1800, interval_s: int = 5) -> str:
    deadline = time.time() + timeout_s
    last_status = None
    while True:
        resp = requests.get(
            f"{APIFY_API}/actor-runs/{run_id}",
            headers=api_headers(token, "poll_run"),
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json()["data"]["status"]
        if status != last_status:
            log(f"Run status: {status}")
            last_status = status
        if status in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
            return status
        if time.time() > deadline:
            return "TIMED-OUT"
        time.sleep(interval_s)


def fetch_dataset_items(token: str, dataset_id: str) -> list[dict]:
    resp = requests.get(
        f"{APIFY_API}/datasets/{dataset_id}/items",
        params={"format": "json", "clean": "true"},
        headers=api_headers(token, "fetch_items"),
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def get_or_create_kv_store(token: str, name: str) -> str:
    """Return the key-value-store ID for a named store; create it if missing."""
    resp = requests.get(
        f"{APIFY_API}/key-value-stores",
        params={"unnamed": "false", "limit": 1000},
        headers=api_headers(token, "list_kv_stores"),
        timeout=30,
    )
    resp.raise_for_status()
    for item in resp.json().get("data", {}).get("items", []):
        if item.get("name") == name:
            return item["id"]
    resp = requests.post(
        f"{APIFY_API}/key-value-stores",
        params={"name": name},
        headers=api_headers(token, "create_kv_store"),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def put_kv_record(token: str, store_id: str, key: str, value: dict) -> None:
    resp = requests.put(
        f"{APIFY_API}/key-value-stores/{store_id}/records/{key}",
        headers={**api_headers(token, "put_kv_record"), "Content-Type": "application/json"},
        data=json.dumps(value, ensure_ascii=False).encode("utf-8"),
        timeout=60,
    )
    resp.raise_for_status()


def push_dataset_items(token: str, dataset_id: str, items: list[dict]) -> None:
    if not items:
        return
    for chunk_start in range(0, len(items), 200):
        chunk = items[chunk_start:chunk_start + 200]
        resp = requests.post(
            f"{APIFY_API}/datasets/{dataset_id}/items",
            headers={**api_headers(token, "push_items"), "Content-Type": "application/json"},
            json=chunk,
            timeout=60,
        )
        resp.raise_for_status()


# ---------- parsing ----------

def _extract_block(item: dict, primary_key: str) -> dict | None:
    """Return the source block dict from a result item, trying common shapes."""
    block = item.get(primary_key)
    if isinstance(block, dict):
        return block
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", primary_key).lower()
    block = item.get(snake)
    return block if isinstance(block, dict) else None


def _block_text(block: dict | None) -> str:
    if not block:
        return ""
    for key in ("content", "text", "answer", "markdown", "response"):
        v = block.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _block_citations(block: dict | None) -> list[dict]:
    """Return citations as a list of {url, title, description} dicts."""
    if not block:
        return []
    for key in ("sources", "citations", "references", "links"):
        v = block.get(key)
        if not isinstance(v, list):
            continue
        out = []
        for entry in v:
            if isinstance(entry, str):
                out.append({"url": entry, "title": "", "description": ""})
            elif isinstance(entry, dict):
                url = entry.get("url") or entry.get("link") or entry.get("href") or ""
                title = entry.get("title") or entry.get("name") or ""
                desc = entry.get("description") or entry.get("snippet") or ""
                if url:
                    out.append({"url": url, "title": title, "description": desc})
        if out:
            return out
    # Fallback: Perplexity exposes plain "citationUrls" alongside structured sources.
    if isinstance(block.get("citationUrls"), list):
        return [{"url": u, "title": "", "description": ""}
                for u in block["citationUrls"] if isinstance(u, str)]
    return []


def parse_run_into_rows(
    raw_items: list[dict],
    config: dict,
    run_id: str,
    run_timestamp: str,
) -> list[dict]:
    """Turn the Actor's per-query items into one row per (prompt, source, entity)."""
    enabled = config["ai_sources"]
    brand = config["brand"]
    competitors = config.get("competitors", [])
    entities = [("brand", brand)] + [("competitor", c) for c in competitors]

    rows: list[dict] = []

    # Index items by prompt for stable lookup.
    by_prompt: dict[str, dict] = {}
    for item in raw_items:
        prompt = (
            (item.get("searchQuery") or {}).get("term")
            or item.get("query")
            or item.get("keyword")
            or ""
        )
        if prompt:
            by_prompt.setdefault(prompt, item)

    for prompt in config["prompts"]:
        item = by_prompt.get(prompt) or {}
        for source_key, (primary_field, _) in SOURCE_FIELDS.items():
            if not enabled.get(source_key, False):
                continue
            block = _extract_block(item, primary_field)
            answer = _block_text(block)
            citations = _block_citations(block)  # list of {url, title, description}

            if not answer and not citations:
                answer_text = "[no answer returned]"
            else:
                answer_text = answer or ""

            citation_urls = [c["url"] for c in citations]
            cited_domains = [registrable_domain(u) for u in citation_urls]
            total_citations = len(citation_urls)

            for entity_kind, ent in entities:
                ent_domain = ent["domain"].lower()
                matched_urls = [
                    citation_urls[i]
                    for i, d in enumerate(cited_domains)
                    if d == ent_domain
                ]
                cited = len(matched_urls) > 0
                mentioned_flag = mentions(answer, ent.get("surface_forms") or [ent["name"]])
                sov = (len(matched_urls) / total_citations * 100.0) if total_citations else 0.0

                rows.append({
                    "run_timestamp": run_timestamp,
                    "run_id": run_id,
                    "prompt": prompt,
                    "source": source_key,
                    "entity": entity_kind,
                    "entity_name": ent["name"],
                    "entity_domain": ent_domain,
                    "cited": cited,
                    "mentioned": mentioned_flag,
                    "matched_citation_urls": matched_urls,
                    "citation_urls": citation_urls,
                    "citations": citations,
                    "answer_text": answer_text,
                    "share_of_voice_pct": round(sov, 1),
                })

    return rows


# ---------- history ----------

def build_history(current: list[dict], all_prior: list[dict]) -> dict:
    """
    Build per-(prompt, source, entity_name) history across ALL prior runs.

    Returns:
        {
          "by_cell": {(prompt, source, entity_name): {
              "total_prior_runs": int,
              "cited_in_prior_runs": int,
              "mentioned_in_prior_runs": int,
              "first_cited_at": str | None,   # earliest prior run_timestamp where cited
              "last_cited_at": str | None,    # most recent prior run_timestamp where cited
              "last_cited_url_examples": [str],
              "newly_cited": bool,            # cited now, never cited before
              "newly_mentioned": bool,        # mentioned now, never mentioned before
              "dropped": bool,                # not cited now, but cited in the latest prior run
          }},
          "prior_run_count": int,             # distinct prior runs seen
          "prior_run_ids": [str],             # newest-first
        }
    """
    # Group prior rows by cell, sorted by timestamp asc.
    by_cell: dict[tuple, list[dict]] = {}
    prior_run_ids: list[tuple[str, str]] = []  # (timestamp, run_id) deduped
    seen_runs = set()
    for r in all_prior:
        key = (r["prompt"], r["source"], r["entity_name"])
        by_cell.setdefault(key, []).append(r)
        rid = r.get("run_id")
        if rid and rid not in seen_runs:
            seen_runs.add(rid)
            prior_run_ids.append((r.get("run_timestamp", ""), rid))
    for k in by_cell:
        by_cell[k].sort(key=lambda r: r.get("run_timestamp", ""))
    prior_run_ids.sort(reverse=True)

    cur_idx = {(r["prompt"], r["source"], r["entity_name"]): r for r in current}

    out: dict[tuple, dict] = {}
    for key, cur in cur_idx.items():
        history = by_cell.get(key, [])
        total = len(history)
        cited_n = sum(1 for h in history if h.get("cited"))
        ment_n = sum(1 for h in history if h.get("mentioned"))
        first_cited = next((h["run_timestamp"] for h in history if h.get("cited")), None)
        last_cited_row = next((h for h in reversed(history) if h.get("cited")), None)
        last_cited = last_cited_row["run_timestamp"] if last_cited_row else None
        last_cited_urls = (last_cited_row or {}).get("matched_citation_urls", []) if last_cited_row else []
        # Was the entity cited in the LATEST prior run for this cell?
        latest_prior_cited = history[-1]["cited"] if history else False
        out[key] = {
            "total_prior_runs": total,
            "cited_in_prior_runs": cited_n,
            "mentioned_in_prior_runs": ment_n,
            "first_cited_at": first_cited,
            "last_cited_at": last_cited,
            "last_cited_url_examples": last_cited_urls[:5],
            "newly_cited": cur["cited"] and cited_n == 0,
            "newly_mentioned": cur["mentioned"] and ment_n == 0,
            "dropped": (not cur["cited"]) and latest_prior_cited,
        }

    return {
        "by_cell": out,
        "prior_run_count": len(prior_run_ids),
        "prior_run_ids": [rid for _, rid in prior_run_ids],
    }


# ---------- report ----------

def _quote_snippet(text: str, surface_forms: list[str], window: int = 60) -> str | None:
    """Return ~window chars on either side of the first surface-form match, single-lined."""
    if not text:
        return None
    for form in surface_forms:
        if not form:
            continue
        m = re.search(r"\b" + re.escape(form) + r"\b", text, flags=re.IGNORECASE)
        if not m:
            continue
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        snippet = text[start:end].replace("\n", " ").strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        return snippet
    return None


def render_report(
    current: list[dict],
    prior: list[dict] | None,
    history: dict | None,
    config: dict,
    run_id: str,
    run_timestamp: str,
) -> str:
    iso_date = run_timestamp[:10]
    enabled_sources = [k for k, v in config["ai_sources"].items() if v]
    entities_full = [("brand", config["brand"])] + [
        ("competitor", c) for c in config.get("competitors", [])
    ]
    entity_names = [e[1]["name"] for e in entities_full]
    by_cell = (history or {}).get("by_cell", {})
    prior_count = (history or {}).get("prior_run_count", 0)
    include_full_answers = (config.get("include_full_answers") or "on_demand").lower() == "always"

    def cell_history(prompt: str, source: str, entity_name: str) -> dict:
        return by_cell.get((prompt, source, entity_name), {})

    lines = []
    lines.append(f"# AI Visibility Snapshot -- {iso_date}")
    lines.append("")
    lines.append(f"- Run ID: `{run_id}` ([console](https://console.apify.com/actors/runs/{run_id}))")
    lines.append(f"- Prompts: {len(config['prompts'])}")
    lines.append(f"- Sources enabled: {', '.join(enabled_sources)}")
    lines.append(f"- Entities: {', '.join(entity_names)}")
    if prior_count:
        lines.append(f"- Prior runs compared against: **{prior_count}**")
    else:
        lines.append("- Prior runs compared against: **0** (first run)")
    lines.append(f"- Verbosity: `include_full_answers = {'always' if include_full_answers else 'on_demand'}`")
    lines.append("")

    # Summary -- highlight what FLIPPED today vs. all prior history.
    lines.append("## Summary")
    if prior_count == 0:
        lines.append("_First run -- nothing to compare against yet._")
    else:
        newly_cited = [k for k, h in by_cell.items() if h.get("newly_cited")]
        newly_mentioned = [k for k, h in by_cell.items() if h.get("newly_mentioned")]
        dropped = [k for k, h in by_cell.items() if h.get("dropped")]
        lines.append(f"- **First-ever citations today:** {len(newly_cited)} (entity x source combinations cited for the first time)")
        for prompt, source, ent in newly_cited:
            lines.append(f"  - {source} / \"{prompt}\" -> **{ent}**")
        lines.append(f"- **First-ever mentions today:** {len(newly_mentioned)}")
        for prompt, source, ent in newly_mentioned:
            lines.append(f"  - {source} / \"{prompt}\" -> **{ent}**")
        lines.append(f"- **Drops today** (cited in last run, not today): {len(dropped)}")
        for prompt, source, ent in dropped:
            lines.append(f"  - {source} / \"{prompt}\" -> **{ent}**")
    lines.append("")

    # Per-entity tables (entity-major: one table per entity, sources as rows).
    # This is the mandatory primary output format -- see SKILL.md "Output format".
    lines.append("## Per-entity scorecards")
    for kind, ent in entities_full:
        ent_name = ent["name"]
        ent_domain = ent["domain"]
        surface_forms = ent.get("surface_forms") or [ent_name]
        lines.append("")
        lines.append(f"### {ent_name} ({kind})")
        lines.append("")
        lines.append("| Source | Cited | Mentioned | SoV% | Matched URLs | History |")
        lines.append("|--------|-------|-----------|------|--------------|---------|")
        for source in enabled_sources:
            cell_rows = [r for r in current if r["source"] == source and r["entity_name"] == ent_name]
            if not cell_rows:
                continue
            # Aggregate across the (possibly multiple) prompts for this (source, entity).
            cited_any = any(r["cited"] for r in cell_rows)
            ment_any = any(r["mentioned"] for r in cell_rows)
            sov_vals = [r["share_of_voice_pct"] for r in cell_rows]
            sov = round(sum(sov_vals) / len(sov_vals), 1) if sov_vals else 0.0
            matched_urls = []
            for r in cell_rows:
                for u in r.get("matched_citation_urls") or []:
                    if u not in matched_urls:
                        matched_urls.append(u)
            urls_cell = "<br>".join(matched_urls) if matched_urls else "--"
            # History across all prior runs of this (source, entity).
            cited_prior = sum(
                cell_history(r["prompt"], source, ent_name).get("cited_in_prior_runs", 0)
                for r in cell_rows
            )
            total_prior = sum(
                cell_history(r["prompt"], source, ent_name).get("total_prior_runs", 0)
                for r in cell_rows
            )
            history_cell = f"cited {cited_prior}/{total_prior} prior runs" if total_prior else "first run"
            # Flag any newly-cited / dropped status.
            flags = []
            for r in cell_rows:
                h = cell_history(r["prompt"], source, ent_name)
                if h.get("newly_cited"): flags.append("first-ever cited")
                if h.get("newly_mentioned"): flags.append("first-ever mentioned")
                if h.get("dropped"): flags.append("dropped vs last")
            if flags:
                history_cell += " (" + ", ".join(sorted(set(flags))) + ")"
            lines.append(
                f"| {source} | {'yes' if cited_any else 'no'} | {'yes' if ment_any else 'no'} "
                f"| {sov} | {urls_cell} | {history_cell} |"
            )

        # Interpretive note under the table -- single sentence summarising
        # citations + mentions with quoted phrases. This is the compact
        # default; full LLM answers are gated below on include_full_answers.
        cited_in_sources = []
        mentioned_in_sources = []
        for source in enabled_sources:
            cell_rows = [r for r in current if r["source"] == source and r["entity_name"] == ent_name]
            if any(r["cited"] for r in cell_rows):
                cited_in_sources.append(source)
            if any(r["mentioned"] for r in cell_rows):
                # Pull a quoted snippet from one of the matching answer texts.
                snippet = None
                for r in cell_rows:
                    if r["mentioned"]:
                        snippet = _quote_snippet(r["answer_text"], surface_forms)
                        if snippet:
                            break
                mentioned_in_sources.append((source, snippet))
        bits = []
        if cited_in_sources:
            bits.append(f"**cited** in {', '.join(cited_in_sources)}")
        if mentioned_in_sources:
            ms = ", ".join(
                f'{s} ("{snip}")' if snip else s for s, snip in mentioned_in_sources
            )
            bits.append(f"**mentioned by name** in {ms}")
        if not bits:
            note = f"{ent_name} has zero citations and zero mentions across all enabled sources."
        else:
            note = f"{ent_name} is " + "; ".join(bits) + "."
        lines.append("")
        lines.append(note)

    # Top citation URLs (today only).
    lines.append("")
    lines.append("## Top 10 most-cited URLs (this run)")
    for source in enabled_sources:
        counts: dict[str, int] = {}
        seen_cells: set[str] = set()
        for r in current:
            if r["source"] != source:
                continue
            cell_key = f"{r['prompt']}|{r['source']}"
            if cell_key in seen_cells:
                continue
            seen_cells.add(cell_key)
            for url in r["citation_urls"]:
                counts[url] = counts.get(url, 0) + 1
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
        lines.append("")
        lines.append(f"### {source}")
        if not top:
            lines.append("_No citations returned._")
        else:
            for url, n in top:
                lines.append(f"- ({n}x) {url}")

    # Per-prompt detail with FULL answer text when any entity is mentioned in
    # the cell, otherwise an 800-char preview.
    lines.append("")
    lines.append("## Per-prompt detail")
    for prompt in config["prompts"]:
        lines.append("")
        lines.append(f"### Prompt: \"{prompt}\"")
        for source in enabled_sources:
            cell_rows = [r for r in current if r["prompt"] == prompt and r["source"] == source]
            if not cell_rows:
                continue
            cell = cell_rows[0]
            any_mentioned = any(r.get("mentioned") for r in cell_rows)
            lines.append("")
            lines.append(f"#### {source}")
            for ent_name in entity_names:
                ent_row = next((r for r in cell_rows if r["entity_name"] == ent_name), None)
                if not ent_row:
                    continue
                h = cell_history(prompt, source, ent_name)
                history_bits = []
                if h.get("total_prior_runs"):
                    history_bits.append(
                        f"cited in {h['cited_in_prior_runs']}/{h['total_prior_runs']} prior runs"
                    )
                    if h.get("last_cited_at") and not ent_row["cited"]:
                        history_bits.append(f"last cited {h['last_cited_at'][:10]}")
                    if h.get("newly_cited"):
                        history_bits.append("**first-ever citation today**")
                    if h.get("newly_mentioned"):
                        history_bits.append("**first-ever mention today**")
                    if h.get("dropped"):
                        history_bits.append("**dropped vs last run**")
                history_str = " -- " + ", ".join(history_bits) if history_bits else ""
                lines.append(
                    f"- **{ent_name}** -- cited: {ent_row['cited']}, "
                    f"mentioned: {ent_row['mentioned']}, SoV: {ent_row['share_of_voice_pct']}%"
                    f"{history_str}"
                )
            # Per-entity matched citation URLs (the EXACT URL that triggered "yes").
            for ent_name in entity_names:
                ent_row = next((r for r in cell_rows if r["entity_name"] == ent_name), None)
                if ent_row and ent_row.get("matched_citation_urls"):
                    lines.append(f"- **{ent_name}** matched citation URLs:")
                    for url in ent_row["matched_citation_urls"]:
                        lines.append(f"  - {url}")
            if cell["citation_urls"]:
                lines.append("- All citation URLs:")
                for url in cell["citation_urls"][:20]:
                    lines.append(f"  - {url}")
            # Default: short quoted snippet around the surface-form match for
            # each mentioned entity. Full answer text only when config sets
            # include_full_answers="always".
            if any_mentioned and include_full_answers:
                lines.append("- Answer (full text, for mention context):")
                lines.append("")
                lines.append("```")
                lines.append(cell["answer_text"].strip())
                lines.append("```")
            elif any_mentioned:
                lines.append("- Mention context (quoted snippets):")
                for ent_name in entity_names:
                    ent_row = next((r for r in cell_rows if r["entity_name"] == ent_name), None)
                    if not ent_row or not ent_row["mentioned"]:
                        continue
                    ent_full = next(e for k, e in entities_full if e["name"] == ent_name)
                    snippet = _quote_snippet(
                        cell["answer_text"],
                        ent_full.get("surface_forms") or [ent_name],
                    )
                    if snippet:
                        lines.append(f"  - **{ent_name}**: \"{snippet}\"")
            else:
                lines.append("- Answer (first 400 chars):")
                excerpt = cell["answer_text"].replace("\n", " ").strip()[:400]
                lines.append(f"  > {excerpt}")

    return "\n".join(lines) + "\n"


# ---------- main ----------

def build_actor_input(config: dict) -> dict:
    apify_cfg = config["apify"]
    ai = config["ai_sources"]
    inp: dict[str, Any] = {
        "queries": "\n".join(config["prompts"]),
        "maxPagesPerQuery": 1,
        "resultsPerPage": 10,
        "countryCode": apify_cfg.get("country_code", "us"),
        "languageCode": apify_cfg.get("language_code", "en"),
    }
    for source_key, (obj_key, flag_key) in SOURCE_TOGGLES.items():
        inp[obj_key] = {flag_key: bool(ai.get(source_key, False))}
    return inp


def main() -> int:
    ap = argparse.ArgumentParser(description="AI visibility snapshot runner.")
    ap.add_argument("--config", required=True, help="Path to config.json")
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        sys.stderr.write(f"Error: config.json not found at {config_path}\n")
        return 2
    config_dir = config_path.parent
    load_dotenv_into_env(config_dir)

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.stderr.write(
            "Error: APIFY_TOKEN not found in environment.\n"
            "Export it (`export APIFY_TOKEN=...`) or add it to a .env file next to config.json.\n"
        )
        return 2

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: config.json is not valid JSON: {e}\n")
        return 2

    actor_id = config["apify"]["actor_id"]
    dataset_name = config["apify"]["dataset_name"]
    log(f"Loaded config: {config_path}")
    log(f"Resolving named dataset: {dataset_name}")
    dataset_id = get_or_create_dataset(token, dataset_name)
    log(f"Dataset ID: {dataset_id}")

    actor_input = build_actor_input(config)
    log(f"Starting actor: {actor_id}")
    run_id, run_default_dataset_id = start_actor(token, actor_id, actor_input)
    run_timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    log(f"Run ID: {run_id}")

    status = poll_until_done(token, run_id)
    if status != "SUCCEEDED":
        sys.stderr.write(
            f"Error: Actor run finished with status {status}. "
            f"Inspect: https://console.apify.com/actors/runs/{run_id}\n"
        )
        return 1

    raw_items = fetch_dataset_items(token, run_default_dataset_id)
    log(f"Fetched {len(raw_items)} raw result(s).")

    rows = parse_run_into_rows(raw_items, config, run_id, run_timestamp)
    log(f"Parsed {len(rows)} snapshot row(s).")

    # Load ALL prior rows BEFORE pushing, so the history view sees every previous
    # run and the current run is not double-counted.
    all_prior_rows = fetch_dataset_items(token, dataset_id)
    all_prior_rows = [r for r in all_prior_rows if r.get("run_id") != run_id]
    distinct_prior_runs = len({r.get("run_id") for r in all_prior_rows if r.get("run_id")})
    if distinct_prior_runs:
        log(f"Loaded {len(all_prior_rows)} rows across {distinct_prior_runs} prior runs.")
    else:
        log("No previous runs found -- first snapshot.")

    push_dataset_items(token, dataset_id, rows)
    log(f"Appended {len(rows)} rows to dataset '{dataset_name}'.")

    # Long-term raw preservation: write the full Apify dataset item to a named
    # KV store, keyed by run_timestamp + prompt slug. Lets the user open any
    # historical snapshot and inspect organicResults, peopleAlsoAsk, the full
    # AI answer text, and every citation with title + description -- even
    # months later, after the original actor run's retention window expires.
    kv_store_name = config["apify"].get("kv_store_name") or f"{dataset_name}-raw"
    try:
        kv_store_id = get_or_create_kv_store(token, kv_store_name)
        log(f"KV store: {kv_store_name} ({kv_store_id})")
        for item in raw_items:
            prompt_text = (item.get("searchQuery") or {}).get("term") or "unknown"
            slug = re.sub(r"[^a-z0-9]+", "-", prompt_text.lower()).strip("-")[:80]
            key = f"{run_timestamp.replace(':', '-')}__{slug}"
            put_kv_record(token, kv_store_id, key, item)
        log(f"Wrote {len(raw_items)} raw record(s) to KV store '{kv_store_name}'.")
    except Exception as e:
        sys.stderr.write(f"Warning: KV store write failed ({e}); dataset rows still appended.\n")

    history = build_history(rows, all_prior_rows) if all_prior_rows else None
    report = render_report(rows, all_prior_rows or None, history, config, run_id, run_timestamp)

    reports_dir = config_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    iso_date = run_timestamp[:10]
    report_path = reports_dir / f"snapshot-{iso_date}.md"
    report_path.write_text(report, encoding="utf-8")
    log(f"Wrote report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
