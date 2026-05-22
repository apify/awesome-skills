#!/usr/bin/env python3
"""Fetch data from German Handelsregister via Apify actor.

Requires: mcpc CLI with authenticated @apify session.
Actor: radeance/handelsregister-api ($0.01/search, 99.5% success, rating 5.0)

Usage:
    python fetch_all.py                # fetch all companies
    python fetch_all.py keyword Siemens # search by keyword

Sources:
  handelsregister — Německý obchodní rejstřík (via Apify). Strukturovaná data: název,
                    právní forma, sídlo, základní kapitál, předmět podnikání, management
                    (jména + data narození), registrační soud, HRB číslo.
                    Žádné přímé DE entity, ale konkurenti Škoda Transportation ano
                    (Siemens Mobility, Stadler, Alstom). Relevantní pro DE telco (T-Mobile).
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

ACTOR = "radeance/handelsregister-api"
UA = "User-Agent: apify-agent-skills/apify-mcpc-1.4.1/call_actor"


def mcpc_call_actor(input_data: dict, timeout: int = 120) -> dict:
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


def mcpc_get_output(dataset_id: str, limit: int = 100) -> list:
    """Get actor output from dataset."""
    cmd = [
        "mcpc", "-H", UA, "@apify", "tools-call", "get-actor-output",
        f"datasetId:={dataset_id}", f"limit:={limit}", "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return []
    return json.loads(result.stdout).get("structuredContent", {}).get("items", [])


def search_company(keyword: str) -> dict:
    """Search Handelsregister by company keyword."""
    return mcpc_call_actor({"keyword": keyword})


def fetch_all():
    print(f"=== DE Handelsregister (via {ACTOR}) ===")
    results = {}

    all_companies = {}
    for sector, companies in COMPANIES.get("competitors", {}).items():
        for reg_id, info in companies.items():
            all_companies[reg_id] = {**info, "sector": sector}

    for reg_id, info in all_companies.items():
        keyword = info.get("keyword", info.get("name", ""))
        print(f"  Searching: {keyword}...")
        try:
            result = search_company(keyword)
            run_id = result.get("runId")
            dataset_id = result.get("datasetId")
            item_count = result.get("itemCount", 0)
            items = result.get("items", [])

            results[reg_id] = {
                "keyword": keyword,
                "sector": info.get("sector"),
                "run_id": run_id,
                "item_count": item_count,
                "data": items[:5],
            }
            print(f"    OK: {item_count} results, runId={run_id}")
            time.sleep(1.0)
        except Exception as e:
            results[reg_id] = {"keyword": keyword, "error": str(e)}
            print(f"    ERR: {e}")

    out = OUTPUT_DIR / "handelsregister.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} searches to {out}")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "keyword":
        keyword = " ".join(sys.argv[2:])
        print(f"Searching: {keyword}")
        result = search_company(keyword)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
    else:
        fetch_all()
