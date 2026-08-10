#!/usr/bin/env python3
"""Aggregate the latest buying-signal Actor runs into a deduplicated leads.csv.

Reads an ICP config (icp.json), pulls each configured Apify task's latest
dataset via the Apify REST API, normalizes rows into the leads.csv schema,
filters against a blacklist CSV if provided, deduplicates against existing
rows (first-seen wins on `domain`), and atomically appends new rows.

Weekly idempotent: if the CSV's max detected_at falls in the current ISO
week, exits early with "skipped: already run this week" unless --force is
passed.

Usage:
    APIFY_TOKEN=... python aggregate.py --config icp.json [--force] [--dry-run]

Requires: Python 3.10+, `requests` (stdlib `urllib` fallback used when
requests is absent).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import requests  # type: ignore

    def _get(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict | list:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
except ImportError:  # pragma: no cover
    import urllib.parse
    import urllib.request

    def _get(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict | list:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


APIFY_API = "https://api.apify.com/v2"
USER_AGENT = "apify-awesome-skills/apify-buying-signal-detection"

CSV_COLUMNS = [
    "detected_at",
    "company",
    "domain",
    "signal_type",
    "signal_detail",
    "signal_source_actor",
    "signal_date",
    "evidence_url",
    "geo",
    "notes",
]

CORP_SUFFIXES = ("inc", "ltd", "gmbh", "sa", "sarl", "bv", "llc", "co", "corp", "ag", "sl")


# ------------------------------ helpers ------------------------------

def normalize_company(name: str) -> str:
    """Lowercase, strip punctuation, drop trailing corporate suffix, collapse ws."""
    if not name:
        return ""
    n = re.sub(r"[^\w\s]", " ", name.lower())
    n = re.sub(r"\s+", " ", n).strip()
    tokens = n.split()
    while tokens and tokens[-1] in CORP_SUFFIXES:
        tokens.pop()
    return " ".join(tokens)


def normalize_domain(raw: str) -> str:
    if not raw:
        return ""
    d = raw.strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    d = d.split("/")[0]
    d = d.split("?")[0]
    return d


def strip_tracking(url: str) -> str:
    if not url:
        return ""
    return re.sub(r"[?&](trackingId|utm_[a-z_]+|si|ref)=[^&]+", "", url).rstrip("?&")


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_week(dt_str: str) -> tuple[int, int] | None:
    """Return (iso_year, iso_week) for a UTC timestamp string, or None if unparseable."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(dt_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            y, w, _ = dt.astimezone(timezone.utc).isocalendar()
            return (y, w)
        except ValueError:
            continue
    return None


def current_iso_week() -> tuple[int, int]:
    y, w, _ = datetime.now(timezone.utc).isocalendar()
    return (y, w)


# ------------------------------ CSV I/O ------------------------------

@dataclass
class LeadsCsv:
    path: Path
    rows: list[dict[str, str]] = field(default_factory=list)

    def load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8", newline="") as f:
            self.rows = list(csv.DictReader(f))

    def max_detected_at(self) -> str | None:
        stamps = [r.get("detected_at", "") for r in self.rows if r.get("detected_at")]
        return max(stamps) if stamps else None

    def existing_domains(self) -> set[str]:
        return {r["domain"] for r in self.rows if r.get("domain")}

    def existing_urls(self) -> set[str]:
        return {strip_tracking(r["evidence_url"]) for r in self.rows if r.get("evidence_url")}

    def append_atomic(self, new_rows: list[dict[str, str]]) -> None:
        if not new_rows:
            return
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for r in self.rows + new_rows:
                writer.writerow({k: r.get(k, "") for k in CSV_COLUMNS})
        os.replace(tmp, self.path)


def load_blacklist(path: Path | None) -> tuple[set[str], set[str]]:
    if not path or not path.exists():
        return set(), set()
    domains, companies = set(), set()
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("domain"):
                domains.add(normalize_domain(row["domain"]))
            if row.get("company"):
                companies.add(normalize_company(row["company"]))
    return domains, companies


# ------------------------------ Apify API ------------------------------

def apify_task_last_dataset_items(task_id: str, token: str) -> list[dict]:
    """Fetch items from the last successful run's default dataset of a task."""
    url = f"{APIFY_API}/actor-tasks/{task_id}/runs/last"
    data = _get(url, params={"token": token, "status": "SUCCEEDED"})
    if not isinstance(data, dict) or "data" not in data:
        return []
    run = data["data"]
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []
    items_url = f"{APIFY_API}/datasets/{dataset_id}/items"
    items = _get(items_url, params={"token": token, "format": "json", "clean": "true"})
    return items if isinstance(items, list) else []


# ------------------------------ signal mappers ------------------------------

def _first(d: dict, *keys: str, default: str = "") -> str:
    for k in keys:
        v = d.get(k)
        if v:
            return str(v)
    return default


def _nested(item: dict, path: str) -> str:
    """Read `a.b.c` from nested dicts, return '' if any hop is missing."""
    cur: Any = item
    for part in path.split("."):
        if not isinstance(cur, dict):
            return ""
        cur = cur.get(part)
        if cur is None:
            return ""
    return str(cur) if cur else ""


def map_jobs_row(item: dict, actor_id: str) -> dict[str, str] | None:
    # Field names span multiple Actors — bebity uses `company`, google/indeed use `companyName`.
    company = _first(item, "companyName", "company", "employerName", "companyDisplayName") or _nested(item, "company.name")
    domain = normalize_domain(_first(item, "companyDomain", "companyWebsite", "companyUrl", "website"))
    title = _first(item, "title", "jobTitle", "positionName", "position", "role", "jobPosition")
    url = strip_tracking(
        _first(item, "jobUrl", "applyUrl", "postingUrl", "url", "link", "linkedinUrl")
        or _nested(item, "job.url")
    )
    if not (company and url):
        return None
    return {
        "detected_at": iso_now(),
        "company": company,
        "domain": domain,
        "signal_type": "jobs",
        "signal_detail": f"Job: {title}" if title else "Job posting",
        "signal_source_actor": actor_id,
        "signal_date": _first(item, "postedDate", "datePosted", "publicationDate", "postedAt", "listedAt"),
        "evidence_url": url,
        "geo": _first(item, "locationCountry", "countryCode", "country") or _nested(item, "location.country"),
        "notes": "",
    }


def map_funding_row(item: dict, actor_id: str) -> dict[str, str] | None:
    company = _first(item, "companyName", "startupName", "company", "name")
    domain = normalize_domain(_first(item, "companyDomain", "companyUrl", "website", "companyWebsite"))
    # nexgendata: fundingAmount / roundType / filingDate. crunchbase: amount / stage / date.
    amount = _first(item, "fundingAmount", "amount", "roundAmount", "raised")
    stage = _first(item, "roundType", "stage", "series", "fundingStage")
    investor = _first(item, "leadInvestor", "investors", "lead")
    url = strip_tracking(_first(item, "sourceUrl", "articleUrl", "url", "link"))
    if not (company and url):
        return None
    detail_bits = [b for b in [f"Raised {amount}" if amount else "", stage, f"led by {investor}" if investor else ""] if b]
    return {
        "detected_at": iso_now(),
        "company": company,
        "domain": domain,
        "signal_type": "funding",
        "signal_detail": " ".join(detail_bits) or "Funding event",
        "signal_source_actor": actor_id,
        "signal_date": _first(item, "filingDate", "announcementDate", "roundDate", "date"),
        "evidence_url": url,
        "geo": _first(item, "hqCountry", "country") or _nested(item, "hq.country"),
        "notes": "",
        # Private field consumed by apply_post_filters. LeadsCsv.append_atomic
        # only writes columns in CSV_COLUMNS so this never lands in the CSV.
        "_stage_raw": stage,
    }


def map_linkedin_content_row(item: dict, actor_id: str) -> dict[str, str] | None:
    # harvestapi returns nested `author.name`, `content`, `linkedinUrl`, `postedAt`, `reactions.count` etc.
    author_name = (
        _first(item, "authorName", "author", "posterName")
        or _nested(item, "author.name")
        or _nested(item, "author.fullName")
    )
    author_headline = (
        _first(item, "authorHeadline", "authorTitle")
        or _nested(item, "author.headline")
        or _nested(item, "author.title")
    ).lower()
    company = (
        _first(item, "authorCompany", "companyName")
        or _nested(item, "author.company.name")
        or _nested(item, "author.currentCompany")
        or author_name
    )
    domain = normalize_domain(
        _first(item, "authorCompanyDomain", "companyDomain")
        or _nested(item, "author.company.domain")
        or _nested(item, "author.company.website")
    )
    text = _first(item, "text", "postText", "content", "postContent", "commentary")
    url = strip_tracking(_first(item, "postUrl", "linkedinUrl", "url", "link"))
    reactions = _first(item, "reactionsCount", "likes", "numLikes") or _nested(item, "reactions.count")
    posted_at = _first(item, "postedAt", "postDate", "date") or _nested(item, "postedAt.date")
    if not (author_name and url):
        return None
    is_probable_agency = any(t in author_headline for t in ("consultant", "agency", "advisor", "founder"))
    notes_bits = []
    if is_probable_agency:
        notes_bits.append("flag:probable-agency-or-advisor")
    if reactions:
        notes_bits.append(f"reactions={reactions}")
    excerpt = (text[:120] + "…") if text and len(text) > 120 else text
    return {
        "detected_at": iso_now(),
        "company": company,
        "domain": domain,
        "signal_type": "linkedin_content",
        "signal_detail": f"Post: '{excerpt}'" if excerpt else "LinkedIn post",
        "signal_source_actor": actor_id,
        "signal_date": posted_at,
        "evidence_url": url,
        "geo": _first(item, "authorCountry", "country") or _nested(item, "author.location.country"),
        "notes": "; ".join(notes_bits),
    }


SIGNAL_MAPPERS = {
    "jobs": map_jobs_row,
    "funding": map_funding_row,
    "linkedin_content": map_linkedin_content_row,
}


# ------------------------------ post-filters ------------------------------

STAGE_ALIASES = {
    "pre_seed": {"pre-seed", "pre seed", "preseed", "angel"},
    "seed": {"seed"},
    "series_a": {"series a", "series-a", "a"},
    "series_b": {"series b", "series-b", "b"},
    "series_c": {"series c", "series-c", "c"},
    "growth": {"growth", "late stage", "series d", "series e", "series f", "series g"},
}


def _stage_matches(row_stage_raw: str, allowed_stages: list[str]) -> bool:
    if not allowed_stages:
        return True
    row_stage = row_stage_raw.lower().strip()
    for allowed in allowed_stages:
        for alias in STAGE_ALIASES.get(allowed, {allowed.lower().replace("_", " ")}):
            if alias in row_stage:
                return True
    return False


def apply_post_filters(row: dict[str, str], icp: dict) -> tuple[bool, str]:
    """Return (keep, reason_if_dropped) based on ICP settings."""
    signal = row["signal_type"]
    geo = row.get("geo", "").upper()
    icp_geos = [g.upper() for g in icp.get("geo", [])]
    if geo and icp_geos and geo not in icp_geos:
        return False, f"geo mismatch ({geo} not in {icp_geos})"

    if signal == "funding":
        cfg = icp.get("funding", {})
        max_days = cfg.get("max_days_since_announcement", 90)
        sig_date = row.get("signal_date", "")
        if sig_date:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
                try:
                    dt = datetime.strptime(sig_date, fmt).replace(tzinfo=timezone.utc)
                    if (datetime.now(timezone.utc) - dt).days > max_days:
                        return False, f"funding older than {max_days} days"
                    break
                except ValueError:
                    continue
        stages = cfg.get("stages", [])
        row_stage = row.get("_stage_raw", "")
        if stages and row_stage and not _stage_matches(row_stage, stages):
            return False, f"stage '{row_stage}' not in {stages}"

    if signal == "linkedin_content":
        cfg = icp.get("linkedin_content", {})
        posted_within = cfg.get("posted_within_days", 14)
        sig_date = row.get("signal_date", "")
        if sig_date:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
                try:
                    dt = datetime.strptime(sig_date, fmt).replace(tzinfo=timezone.utc)
                    if (datetime.now(timezone.utc) - dt).days > posted_within:
                        return False, f"post older than {posted_within} days"
                    break
                except ValueError:
                    continue
        # `notes` carries "reactions=N" when the Actor returned reaction counts.
        min_reactions = cfg.get("min_reactions", 0)
        if min_reactions > 0:
            m = re.search(r"reactions=(\d+)", row.get("notes", ""))
            if m and int(m.group(1)) < min_reactions:
                return False, f"reactions {m.group(1)} < min_reactions {min_reactions}"

    return True, ""


# ------------------------------ main ------------------------------

def load_task_registry(campaign_name: str, campaign_dir: Path) -> list[dict]:
    """Read the task registry setup_apify_tasks.py wrote next to icp.json.

    Registry shape: [{task_id, actor_id, signal_type}, ...]
    """
    reg_path = campaign_dir / f".{campaign_name}.tasks.json"
    if not reg_path.exists():
        return []
    return json.loads(reg_path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate Apify buying-signal runs into leads.csv")
    ap.add_argument("--config", required=True, help="Path to icp.json")
    ap.add_argument("--force", action="store_true", help="Bypass weekly idempotency guard")
    ap.add_argument("--dry-run", action="store_true", help="Skip CSV write; print planned appends to stdout")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("error: APIFY_TOKEN env var is required", file=sys.stderr)
        return 2

    config_path = Path(args.config).resolve()
    icp = json.loads(config_path.read_text(encoding="utf-8"))
    campaign_dir = config_path.parent
    leads_path = (campaign_dir / icp["leads_csv"]).resolve()
    blacklist_path = campaign_dir / icp["blacklist_csv"] if icp.get("blacklist_csv") else None

    leads = LeadsCsv(leads_path)
    leads.load()
    last_stamp = leads.max_detected_at()
    if last_stamp and not args.force:
        if iso_week(last_stamp) == current_iso_week():
            print(f"skipped: already run this week (last detected_at={last_stamp})")
            return 0

    bl_domains, bl_companies = load_blacklist(blacklist_path)
    seen_domains = leads.existing_domains()
    seen_urls = leads.existing_urls()

    tasks = load_task_registry(icp["campaign_name"], campaign_dir)
    if not tasks:
        print(
            f"error: no task registry for campaign '{icp['campaign_name']}'. "
            "Run setup_apify_tasks.py first.",
            file=sys.stderr,
        )
        return 2

    all_new_rows: list[dict[str, str]] = []
    audit = {"fetched_by_signal": {}, "dropped": {"blacklist": 0, "dup_domain": 0, "dup_url": 0, "post_filter": 0, "unmappable": 0}}

    for task in tasks:
        signal = task["signal_type"]
        mapper = SIGNAL_MAPPERS.get(signal)
        if not mapper:
            continue
        items = apify_task_last_dataset_items(task["task_id"], token)
        audit["fetched_by_signal"].setdefault(signal, 0)
        audit["fetched_by_signal"][signal] += len(items)
        for item in items:
            row = mapper(item, task["actor_id"])
            if not row:
                audit["dropped"]["unmappable"] += 1
                continue

            if row["domain"] and row["domain"] in bl_domains:
                audit["dropped"]["blacklist"] += 1
                continue
            if normalize_company(row["company"]) in bl_companies:
                audit["dropped"]["blacklist"] += 1
                continue

            keep, reason = apply_post_filters(row, icp)
            if not keep:
                audit["dropped"]["post_filter"] += 1
                continue

            if row["domain"] and row["domain"] in seen_domains:
                audit["dropped"]["dup_domain"] += 1
                continue
            if row["evidence_url"] in seen_urls:
                audit["dropped"]["dup_url"] += 1
                continue

            all_new_rows.append(row)
            seen_urls.add(row["evidence_url"])
            if row["domain"]:
                seen_domains.add(row["domain"])

    print(json.dumps({"summary": {"appended": len(all_new_rows), **audit}}, indent=2))

    if args.dry_run:
        print("(dry-run: no CSV write)")
        return 0

    leads.append_atomic(all_new_rows)
    print(f"wrote {len(all_new_rows)} new rows to {leads_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
