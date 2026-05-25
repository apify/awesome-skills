#!/usr/bin/env python3
"""Fetch data from UK Companies House via Apify actor.

Requires: mcpc CLI with authenticated @apify session.
Actor: dhrumil/company-house-scraper (pay-per-event, 95.7% success, rating 5.0)

Usage:
    python fetch_all.py              # fetch all companies
    python fetch_all.py search NAME  # search by name

Sources:
  companies_house — UK Companies House (via Apify). Company number, status, adresa,
                    SIC kódy, datum inkorporace, officers (directors + secretary),
                    accounts timeline, confirmation statement.
                    Portfolio entita: ClearBank Group Holdings Ltd (#14254435).
                    Konkurenti: Modulr, Starling Bank, Monzo Bank.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)

ACTOR = "dhrumil/company-house-scraper"
UA = "User-Agent: apify-awesome-skills/apify-mcpc-1.4.1/call_actor"

CH_SEARCH_BASE = "https://find-and-update.company-information.service.gov.uk/advanced-search/get-results"


def build_search_url(company_name: str) -> str:
    """Build Companies House advanced search URL."""
    from urllib.parse import urlencode
    params = {
        "companyNameIncludes": company_name,
        "companyNameExcludes": "",
    }
    return f"{CH_SEARCH_BASE}?{urlencode(params)}"


def mcpc_call_actor(input_data: dict, timeout: int = 180) -> dict:
    """Call Apify actor via mcpc and return structured result."""
    input_json = json.dumps(input_data)
    cmd = [
        "mcpc", "-H", UA, "@apify", "tools-call", "call-actor",
        f"actor:={ACTOR}",
        f"input:={input_json}",
        f'callOptions:={{"timeout": {timeout}}}',
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
    if result.returncode != 0:
        return {"error": result.stderr[:500]}
    return json.loads(result.stdout).get("structuredContent", {})


def search_company(name: str, max_companies: int = 10) -> dict:
    """Search Companies House by company name."""
    search_url = build_search_url(name)
    return mcpc_call_actor({
        "listUrls": [{"url": search_url}],
        "maxCompanies": max_companies,
    })


def fetch_all():
    print(f"=== UK Companies House (via {ACTOR}) ===")
    results = {}

    # Collect all companies to search
    all_searches = {}
    for key, info in COMPANIES.get("portfolio", {}).items():
        if isinstance(info, dict) and "keyword" in info:
            all_searches[key] = info
    for sector, companies in COMPANIES.get("competitors", {}).items():
        for key, info in companies.items():
            all_searches[key] = {**info, "sector": sector}

    for key, info in all_searches.items():
        keyword = info.get("keyword", info.get("name", ""))
        print(f"  Searching: {keyword}...")
        try:
            result = search_company(keyword, max_companies=5)
            run_id = result.get("runId")
            item_count = result.get("itemCount", 0)
            items = result.get("items", [])

            results[key] = {
                "keyword": keyword,
                "sector": info.get("sector", "unclassified"),
                "run_id": run_id,
                "item_count": item_count,
                "data": items[:3],
            }
            print(f"    OK: {item_count} results")
            time.sleep(1.0)
        except Exception as e:
            results[key] = {"keyword": keyword, "error": str(e)}
            print(f"    ERR: {e}")

    out = OUTPUT_DIR / "companies_house.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} searches to {out}")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "search":
        name = " ".join(sys.argv[2:])
        print(f"Searching: {name}")
        result = search_company(name)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
    else:
        fetch_all()
