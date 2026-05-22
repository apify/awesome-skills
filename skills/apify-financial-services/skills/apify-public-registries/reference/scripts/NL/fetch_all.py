#!/usr/bin/env python3
"""Fetch data from Dutch KvK (Kamer van Koophandel) API.

REQUIRES: API key from https://developers.kvk.nl (see REGISTRATION.md)
Set env: KVK_API_KEY=<your-key>

Usage:
    python fetch_all.py                    # fetch all NL companies (needs KVK_API_KEY)

Sources:
  kvk — KvK REST API (Kamer van Koophandel). Základní profil firmy, adresy poboček,
        obchodní jména. Nejdůležitější NL registr — PPF Group N.V. (KvK 33264887),
        Home Credit N.V., e& PPF Telecom Group B.V., CME Media Enterprises B.V.
        a dalších 3 NL holdings jsou tu registrovány.
        Vyžaduje registraci na developers.kvk.nl + schválení → API klíč.
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)

API_KEY = os.environ.get("KVK_API_KEY")
BASE_URL = "https://api.kvk.nl/api/v1"


def kvk_request(endpoint: str) -> dict:
    if not API_KEY:
        raise RuntimeError("KVK_API_KEY not set. See REGISTRATION.md")
    url = f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers={"apikey": API_KEY})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_profile(kvk_number: str) -> dict:
    return kvk_request(f"basisprofielen/{kvk_number}")


def fetch_all():
    print("=== NL KvK (Kamer van Koophandel) ===")
    if not API_KEY:
        print("  ERROR: KVK_API_KEY not set.")
        print("  Register at https://developers.kvk.nl — see REGISTRATION.md")
        return {}

    results = {}
    all_companies = dict(COMPANIES["portfolio"])
    for sector_companies in COMPANIES.get("competitors", {}).values():
        all_companies.update(sector_companies)

    for kvk, info in all_companies.items():
        try:
            data = fetch_profile(kvk)
            results[kvk] = data
            print(f"  OK {kvk} {info.get('name', '')}")
            time.sleep(0.5)
        except Exception as e:
            results[kvk] = {"error": str(e), "name": info.get("name", "")}
            print(f"  ERR {kvk} {e}")

    out = OUTPUT_DIR / "kvk.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


if __name__ == "__main__":
    fetch_all()
