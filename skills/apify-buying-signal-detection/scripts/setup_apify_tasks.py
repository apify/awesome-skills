#!/usr/bin/env python3
"""Provision Apify Actor Tasks from an ICP config.

Reads icp.json, decides which Actors to enable per the routing tables in
`references/actors.md`, and creates (or updates in place) one Apify Actor Task
per Actor with the correct input payload derived from the ICP.

Optionally provisions a single Apify Schedule that fires all the tasks on the
configured cron. Writes a task registry sidecar at
`<campaign_dir>/.<campaign_name>.tasks.json` — `aggregate.py` reads this to
know which tasks to pull dataset items from.

Usage:
    APIFY_TOKEN=... python setup_apify_tasks.py --config icp.json [--dry-run]
                                                                 [--no-schedule]
                                                                 [--refresh-auth]

The script is idempotent: running it twice against the same ICP renames-in-place
rather than creating duplicates.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

APIFY_API = "https://api.apify.com/v2"
USER_AGENT = "apify-awesome-skills/apify-buying-signal-detection"


# ------------------------------ HTTP helpers ------------------------------

def _req(method: str, path: str, token: str, body: dict | None = None) -> dict | list:
    url = f"{APIFY_API}{path}"
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}token={urllib.parse.quote(token)}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def apify_get(path: str, token: str) -> Any:
    return _req("GET", path, token)


def apify_post(path: str, token: str, body: dict) -> Any:
    return _req("POST", path, token, body)


def apify_put(path: str, token: str, body: dict) -> Any:
    return _req("PUT", path, token, body)


# ------------------------------ Actor routing ------------------------------

def pick_actors(icp: dict) -> list[dict]:
    """Return [{actor_id, signal_type, input_builder}] based on ICP signals + geo."""
    signals = set(icp.get("signals", []))
    geo = {g.upper() for g in icp.get("geo", [])}
    kws = icp.get("industry_keywords", [])
    persona = icp.get("persona", {})
    fund_cfg = icp.get("funding", {})
    li_cfg = icp.get("linkedin_content", {})

    picks: list[dict] = []

    if "jobs" in signals:
        titles = persona.get("titles") or kws
        # LinkedIn Jobs: lntb/... is PPE ($1/1k) and accepts arrays of titles + locations natively,
        # so a multi-title ICP does not get collapsed to titles[0].
        _country_names = {
            "US": "United States", "GB": "United Kingdom", "IN": "India", "CA": "Canada",
            "DE": "Germany", "AT": "Austria", "BE": "Belgium", "FR": "France",
            "AU": "Australia", "NZ": "New Zealand", "IE": "Ireland", "ES": "Spain",
            "IT": "Italy", "NL": "Netherlands", "PL": "Poland", "SE": "Sweden",
        }
        job_locations = [_country_names.get(g, g) for g in sorted(geo)] if geo else ["United States"]
        picks.append({
            "actor_id": "lntb/linkedin-jobs-scraper---multiple-titles-locations-in-one",
            "signal_type": "jobs",
            "input": {
                "jobTitles": list(titles) if titles else [],
                "jobLocations": job_locations,
                "totalRows": 200,
            },
        })
        # johnvc/Google-Jobs-Scraper wants lowercase ISO codes with `uk` (not `gb`),
        # and rejects anything outside its own enum — an ICP targeting BE/NL/PL
        # would otherwise fail task creation with `invalid-input`. Pick the first
        # geo the Actor actually supports; if none match, omit `country` and let
        # Google aggregate globally (the field is optional).
        _gjs_geo = {"GB": "uk"}
        _gjs_supported = {"us", "ca", "uk", "de", "fr", "au", "jp", "in", "br", "mx"}
        gjs_country = next(
            (c for c in (_gjs_geo.get(g, g.lower()) for g in sorted(geo)) if c in _gjs_supported),
            None,
        )
        gjs_input = {
            "query": titles[0] if titles else "",
            "location": ", ".join(sorted(geo)) if geo else "",
            "num_results": 200,
        }
        if gjs_country:
            gjs_input["country"] = gjs_country
        picks.append({
            "actor_id": "johnvc/Google-Jobs-Scraper",
            "signal_type": "jobs",
            "input": gjs_input,
        })
        if geo & {"US", "GB", "IN", "CA"}:
            # borderline/indeed-scraper: lowercase codes, `uk` (not `gb`).
            _indeed_geo = {"GB": "uk"}
            indeed_country_raw = sorted(list(geo & {"US", "GB", "IN", "CA"}))[0]
            indeed_country = _indeed_geo.get(indeed_country_raw, indeed_country_raw.lower())
            picks.append({
                "actor_id": "borderline/indeed-scraper",
                "signal_type": "jobs",
                "input": {
                    "query": titles[0] if titles else "",
                    "country": indeed_country,
                    "maxRows": 200,
                },
            })
        if geo & {"DE", "AT", "BE"}:
            picks.append({
                "actor_id": "memo23/stepstone-search-cheerio-ppr",
                "signal_type": "jobs",
                "input": {"searchTerms": titles, "maxItems": 200},
            })
        if geo & {"AU", "NZ"}:
            picks.append({
                "actor_id": "blackfalcondata/seek-scraper",
                "signal_type": "jobs",
                "input": {"searchTerms": titles, "maxItems": 200},
            })
        if "FR" in geo:
            picks.append({
                "actor_id": "dltik/francetravail-scraper",
                "signal_type": "jobs",
                "input": {"searchTerms": titles, "maxItems": 200},
            })

    if "funding" in signals:
        # nexgendata: `mode`, `searchQuery` (string), `daysBack`, `maxResults`.
        max_days = fund_cfg.get("max_days_since_announcement", 90)
        picks.append({
            "actor_id": "nexgendata/startup-funding-tracker",
            "signal_type": "funding",
            "input": {
                "mode": "all_sources",
                "searchQuery": " ".join(kws) if kws else "",
                "daysBack": max_days,
                "maxResults": 300,
                "enrich_companies": True,
            },
        })
        picks.append({
            "actor_id": "memo23/crunchbase-scraper",
            "signal_type": "funding",
            "input": {
                "categories": kws,
                "fundingRounds": fund_cfg.get("stages", []),
                "maxItems": 300,
            },
        })
        picks.append({
            "actor_id": "complex_intricate_networks/fundraising-and-startup-funding-scraper",
            "signal_type": "funding",
            "input": {"keywords": kws, "maxItems": 300},
        })
        picks.append({
            "actor_id": "signalbase/signalbase-api",
            "signal_type": "funding",
            "input": {"industries": kws, "maxItems": 200},
        })
        if "FR" in geo:
            picks.append({
                "actor_id": "advantageous_subcontra/maddyness-french-startup-fundraising-database",
                "signal_type": "funding",
                "input": {"maxItems": 200},
            })

    if "linkedin_content" in signals:
        # harvestapi/linkedin-post-search: `searchQueries` (array), `maxPosts`, `sortBy`, `postedLimit`.
        posted_within = li_cfg.get("posted_within_days", 14)
        posted_limit = "24h" if posted_within <= 1 else ("week" if posted_within <= 7 else "month")
        picks.append({
            "actor_id": "harvestapi/linkedin-post-search",
            "signal_type": "linkedin_content",
            "input": {
                "searchQueries": li_cfg.get("search_terms", kws),
                "maxPosts": 500,
                "sortBy": "date",
                "postedLimit": posted_limit,
                "scrapeReactions": False,
            },
        })

    return picks


# ------------------------------ task ops ------------------------------

def find_task_by_name(token: str, name: str) -> dict | None:
    resp = apify_get(f"/actor-tasks?limit=1000", token)
    for t in resp.get("data", {}).get("items", []):
        if t.get("name") == name:
            return t
    return None


def _task_name(campaign: str, actor_id: str) -> str:
    """Build an Apify-valid task name (max 63 chars, no trailing dash).

    Apify only accepts `a-z`, `0-9` and hyphens, and hyphens may not sit at
    either end. Store usernames routinely break both rules — underscores
    (`complex_intricate_networks`) and capitals (`johnvc/Google-Jobs-Scraper`)
    are common — so every disallowed character is folded to a hyphen before
    the length cap is applied.

    Format: `{campaign}-{slug}` truncated to 63 chars.
    """
    slug = actor_id.replace("/", "-")
    name = re.sub(r"[^a-z0-9-]+", "-", f"{campaign}-{slug}".lower())
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name[:63].rstrip("-")


def upsert_task(token: str, campaign: str, pick: dict) -> str:
    """Create-or-update a task for one Actor pick. Returns the task id."""
    name = _task_name(campaign, pick["actor_id"])
    existing = find_task_by_name(token, name)
    body = {
        "name": name,
        "actId": pick["actor_id"],
        "options": {"build": "latest"},
        "input": pick["input"],
    }
    if existing:
        apify_put(f"/actor-tasks/{existing['id']}", token, body)
        return existing["id"]
    created = apify_post("/actor-tasks", token, body)
    return created["data"]["id"]


def upsert_schedule(token: str, campaign: str, cron: str, task_ids: list[str]) -> str | None:
    name = f"{campaign}-schedule"
    resp = apify_get("/schedules?limit=1000", token)
    existing = next((s for s in resp.get("data", {}).get("items", []) if s.get("name") == name), None)
    body = {
        "name": name,
        "cronExpression": cron,
        "timezone": "UTC",
        "isEnabled": True,
        "actions": [
            {"type": "RUN_ACTOR_TASK", "actorTaskId": tid} for tid in task_ids
        ],
    }
    if existing:
        apify_put(f"/schedules/{existing['id']}", token, body)
        return existing["id"]
    created = apify_post("/schedules", token, body)
    return created["data"]["id"]


# ------------------------------ main ------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-schedule", action="store_true", help="Provision tasks but not the Apify Schedule")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("error: APIFY_TOKEN env var is required", file=sys.stderr)
        return 2

    config_path = Path(args.config).resolve()
    icp = json.loads(config_path.read_text(encoding="utf-8"))
    campaign = icp["campaign_name"]
    campaign_dir = config_path.parent

    picks = pick_actors(icp)
    if not picks:
        print("error: no Actors matched the ICP (empty signals or unsupported geo)", file=sys.stderr)
        return 2

    print(f"Will provision {len(picks)} tasks for campaign '{campaign}':")
    for p in picks:
        print(f"  - {p['signal_type']:>18s}  ← {p['actor_id']}")

    if args.dry_run:
        print("(dry-run: no Apify calls made)")
        return 0

    registry: list[dict] = []
    for p in picks:
        try:
            task_id = upsert_task(token, campaign, p)
        except Exception as exc:
            print(f"  ! failed to upsert task for {p['actor_id']}: {exc}", file=sys.stderr)
            continue
        registry.append({"task_id": task_id, "actor_id": p["actor_id"], "signal_type": p["signal_type"]})
        print(f"  ok  {p['actor_id']}  →  task {task_id}")

    reg_path = campaign_dir / f".{campaign}.tasks.json"
    reg_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"wrote task registry → {reg_path}")

    if args.no_schedule:
        return 0
    cron = icp.get("schedule", {}).get("apify_side_cron")
    if not cron:
        print("no schedule.apify_side_cron in ICP — skipping schedule creation")
        return 0
    sched_id = upsert_schedule(token, campaign, cron, [r["task_id"] for r in registry])
    print(f"schedule '{campaign}-schedule' → {sched_id} (cron: {cron})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
