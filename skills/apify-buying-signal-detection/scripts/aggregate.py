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
        r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        return r.json()

    def _post(url: str, params: dict[str, Any] | None, body: dict, timeout: int = 300) -> dict | list:
        r = requests.post(url, params=params, json=body, timeout=timeout, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        return r.json()
except ImportError:  # pragma: no cover
    import urllib.parse
    import urllib.request

    def _get(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict | list:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(url: str, params: dict[str, Any] | None, body: dict, timeout: int = 300) -> dict | list:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


APIFY_API = "https://api.apify.com/v2"
USER_AGENT = "apify-awesome-skills/apify-buying-signal-detection"
LINKEDIN_PROFILE_ACTOR = "harvestapi/linkedin-profile-scraper"
LINKEDIN_COMPANY_ACTOR = "harvestapi/linkedin-company"
# harvestapi/linkedin-profile-scraper enum literal — validated against Actor
# input schema. The "no email" variant is $4/1k profiles, the email variant is
# $10/1k. Domain resolution doesn't need emails so we take the cheap tier.
LINKEDIN_PROFILE_MODE = "Profile details no email ($4 per 1k)"

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
    return re.sub(r"[?&](trackingId|utm_[a-z_]+|si|ref|miniProfileUrn|rcm|dashCommentUrn|commentUrn)=[^&]+", "", url).rstrip("?&")


def canonical_linkedin_profile_url(raw: str, public_identifier: str = "") -> str:
    """Return `https://www.linkedin.com/in/{slug}` — stable across post samples.

    harvestapi post output puts the profile URL with a `?miniProfileUrn=…` tail
    that varies per-sample, so N posts by the same author look like N distinct
    profile URLs. Prefer the `publicIdentifier` when the post scraper hands it
    over; fall back to the URL slug.
    """
    if public_identifier:
        return f"https://www.linkedin.com/in/{public_identifier}"
    if not raw:
        return ""
    stripped = strip_tracking(raw)
    m = re.match(r"https?://[^/]*linkedin\.com/in/([^/?#]+)", stripped, re.I)
    if m:
        return f"https://www.linkedin.com/in/{m.group(1)}"
    return stripped


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


def apify_run_actor_sync(actor_id: str, input_body: dict, token: str, timeout: int = 600) -> list[dict]:
    """Run an Actor synchronously and return its default dataset items.

    Uses Apify's `run-sync-get-dataset-items` endpoint. Caller controls the
    input shape — no assumptions about task registry. Returns [] on any
    non-list response (including empty runs and API errors surfaced as JSON).
    """
    actor_slug = actor_id.replace("/", "~")
    url = f"{APIFY_API}/acts/{actor_slug}/run-sync-get-dataset-items"
    items = _post(url, params={"token": token, "format": "json", "clean": "true"}, body=input_body, timeout=timeout)
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
    # harvestapi/linkedin-post-search output shape (verified against live Actor
    # response 2026-08): top-level `linkedinUrl` = post URL, `content` = text,
    # `postedAt.date` = ISO date, `engagement.likes` = int, `author.name`,
    # `author.info` = headline, `author.linkedinUrl` = profile URL (with a
    # `?miniProfileUrn=…` query that varies per sample), `author.publicIdentifier`
    # = the /in/<slug> segment. Keep older field names in the fallback chain in
    # case harvestapi evolves the schema.
    author_name = (
        _nested(item, "author.name")
        or _first(item, "authorName", "author", "posterName")
        or _nested(item, "author.fullName")
    )
    author_headline = (
        _nested(item, "author.info")
        or _first(item, "authorHeadline", "authorTitle")
        or _nested(item, "author.headline")
        or _nested(item, "author.title")
    ).lower()
    # harvestapi doesn't return the current employer on the post row — only on
    # the profile scraper. `company` starts as the author's own name and gets
    # replaced during enrich_linkedin_domains when the profile lookup succeeds.
    company = (
        _first(item, "authorCompany", "companyName")
        or _nested(item, "author.company.name")
        or _nested(item, "author.currentCompany")
        or author_name
    )
    # Post scraper virtually never returns the company website — this stays
    # empty and is filled in by enrich_linkedin_domains via the profile +
    # company Actor chain.
    domain = normalize_domain(
        _first(item, "authorCompanyDomain", "companyDomain")
        or _nested(item, "author.company.domain")
        or _nested(item, "author.company.website")
    )
    text = _first(item, "content", "text", "postText", "postContent", "commentary")
    url = strip_tracking(_first(item, "linkedinUrl", "postUrl", "url", "link"))
    reactions = (
        _nested(item, "engagement.likes")
        or _first(item, "reactionsCount", "likes", "numLikes")
        or _nested(item, "reactions.count")
    )
    posted_at = _nested(item, "postedAt.date") or _first(item, "postedAt", "postDate", "date")
    public_identifier = _nested(item, "author.publicIdentifier") or _first(item, "authorPublicIdentifier")
    raw_profile_url = (
        _nested(item, "author.linkedinUrl")
        or _first(item, "authorProfileUrl", "authorUrl", "authorLinkedinUrl")
        or _nested(item, "author.profileUrl")
        or _nested(item, "author.url")
    )
    author_profile_url = canonical_linkedin_profile_url(raw_profile_url, public_identifier)
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
        # Private field consumed by enrich_linkedin_domains — not written to CSV
        # (LeadsCsv.append_atomic filters to CSV_COLUMNS).
        "_author_profile_url": author_profile_url,
    }


SIGNAL_MAPPERS = {
    "jobs": map_jobs_row,
    "funding": map_funding_row,
    "linkedin_content": map_linkedin_content_row,
}


# ---------- LinkedIn author → company-domain enrichment ----------
#
# harvestapi/linkedin-post-search returns author identity + post text, but the
# author's current-company website is virtually never on the post row. Without
# a domain, the aggregator cannot check the blacklist or dedup against existing
# leads for this signal — which the user flagged as a leak.
#
# Verified against live Actor output (2026-08), resolving domain takes THREE
# steps, not two:
#   1. post-search   → author profile URL (already on the row from mapping)
#   2. profile-scraper → currentPosition[0].companyLinkedinUrl + companyName
#   3. company scraper → website  ← the actual domain source
#
# The profile scraper alone returns the current company as a LinkedIn URL and
# a display name, not a website. Only the company scraper closes the last hop.
# Both hops are batched and deduplicated: N posts by the same author cost one
# profile lookup; N authors at the same company cost one company lookup.

def _extract_company_linkedin_url_from_profile(profile: dict) -> tuple[str, str]:
    """Return (companyLinkedinUrl, companyName) from a profile scraper item.

    Prefers `currentPosition[0]` since harvestapi puts the active role there.
    Falls back to `experience[]` first entry lacking `endDate.text != "Present"`.
    Returns ("", "") when the profile has no current employer (freelancers,
    retirees).
    """
    current = profile.get("currentPosition") or []
    if isinstance(current, list) and current:
        first = current[0]
        if isinstance(first, dict):
            url = str(first.get("companyLinkedinUrl") or "")
            name = str(first.get("companyName") or "")
            if url or name:
                return url, name
    experience = profile.get("experience") or profile.get("experiences") or []
    if isinstance(experience, list):
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            end_text = _nested(exp, "endDate.text").lower()
            is_current = (not exp.get("endDate")) or end_text in ("", "present")
            if not is_current:
                continue
            url = str(exp.get("companyLinkedinUrl") or exp.get("companyUrl") or "")
            name = str(exp.get("companyName") or exp.get("company") or "")
            if url or name:
                return url, name
    return "", ""


def enrich_linkedin_domains(rows: list[dict], token: str, audit: dict) -> None:
    """Fill row['domain'] for linkedin_content rows via a two-Actor chain.

    Mutates `rows` in place. Deduplicates at both hops:
      - unique author profile URLs → one profile-scraper call each
      - unique companyLinkedinUrls across all resolved profiles → one
        company-scraper call each

    Rows still lacking a domain after both hops (profile has no current
    employer, or the company page has no website) fall through to the
    filter loop and get dropped into the `linkedin_no_domain` bucket.
    """
    to_enrich = [
        r for r in rows
        if r.get("signal_type") == "linkedin_content"
        and not r.get("domain")
        and r.get("_author_profile_url")
    ]
    if not to_enrich:
        return

    # ---- Hop 1: profile scraper on unique author profile URLs
    unique_profile_urls = sorted({r["_author_profile_url"] for r in to_enrich})
    audit["linkedin_profile_lookups"] = len(unique_profile_urls)
    try:
        profiles = apify_run_actor_sync(
            LINKEDIN_PROFILE_ACTOR,
            {"profileScraperMode": LINKEDIN_PROFILE_MODE, "urls": unique_profile_urls},
            token,
        )
    except Exception as e:
        print(f"warn: LinkedIn profile enrichment failed ({e}); leaving domains empty", file=sys.stderr)
        audit["linkedin_profile_error"] = str(e)
        return

    # Map: profile URL → (companyLinkedinUrl, companyName). Also index by
    # publicIdentifier so we can join back on either key.
    profile_to_company: dict[str, tuple[str, str]] = {}
    for p in profiles:
        if not isinstance(p, dict):
            continue
        company_url, company_name = _extract_company_linkedin_url_from_profile(p)
        if not (company_url or company_name):
            continue
        key_candidates = set()
        raw_url = _first(p, "linkedinUrl", "url", "publicUrl", "profileUrl") or _nested(p, "profile.url")
        canon = canonical_linkedin_profile_url(raw_url, _first(p, "publicIdentifier"))
        if canon:
            key_candidates.add(canon)
        pub_id = _first(p, "publicIdentifier")
        if pub_id:
            key_candidates.add(f"https://www.linkedin.com/in/{pub_id}")
        for key in key_candidates:
            profile_to_company[key] = (company_url, company_name)

    audit["linkedin_profile_resolved"] = len(profile_to_company)

    # ---- Hop 2: company scraper on unique companyLinkedinUrls
    company_urls_needed = sorted({url for url, _ in profile_to_company.values() if url})
    company_to_domain: dict[str, str] = {}
    if company_urls_needed:
        audit["linkedin_company_lookups"] = len(company_urls_needed)
        try:
            companies = apify_run_actor_sync(
                LINKEDIN_COMPANY_ACTOR,
                {"companies": company_urls_needed},
                token,
            )
        except Exception as e:
            print(f"warn: LinkedIn company enrichment failed ({e}); leaving domains empty", file=sys.stderr)
            audit["linkedin_company_error"] = str(e)
            companies = []
        for c in companies:
            if not isinstance(c, dict):
                continue
            company_url = str(c.get("linkedinUrl") or "")
            website = str(c.get("website") or "")
            if company_url and website:
                company_to_domain[company_url.rstrip("/")] = normalize_domain(website)
        audit["linkedin_company_resolved"] = len(company_to_domain)
    else:
        audit["linkedin_company_lookups"] = 0
        audit["linkedin_company_resolved"] = 0

    # ---- Join: profile URL → company URL → domain (and overwrite row.company
    # with the resolved company name if we found one).
    resolved_domains = 0
    for r in to_enrich:
        entry = profile_to_company.get(r["_author_profile_url"])
        if not entry:
            continue
        company_url, company_name = entry
        if company_name:
            r["company"] = company_name
        if not company_url:
            continue
        domain = company_to_domain.get(company_url.rstrip("/"))
        if domain:
            r["domain"] = domain
            resolved_domains += 1
    audit["linkedin_domain_resolved"] = resolved_domains


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
    audit = {
        "fetched_by_signal": {},
        "dropped": {
            "blacklist": 0,
            "dup_domain": 0,
            "dup_url": 0,
            "post_filter": 0,
            "unmappable": 0,
            "linkedin_no_domain": 0,
        },
    }

    # ---- Pass 1: fetch + map all items across every task
    candidate_rows: list[dict[str, str]] = []
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
            candidate_rows.append(row)

    # ---- Pass 2: enrich LinkedIn rows with missing company domain so that
    # blacklist and domain-dedup can actually see them.
    enrich_linkedin_domains(candidate_rows, token, audit)

    # ---- Pass 3: filter (blacklist → post-filter → dedup) and collect new rows
    for row in candidate_rows:
        # LinkedIn rows that still have no domain after enrichment are
        # unblacklistable and unmergeable — drop with a dedicated bucket so
        # the user can spot when the profile scraper is missing data.
        if row.get("signal_type") == "linkedin_content" and not row.get("domain"):
            audit["dropped"]["linkedin_no_domain"] += 1
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
