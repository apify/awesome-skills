#!/usr/bin/env python3
"""Fetch data from Slovak business registries for portfolio + competitors.

Usage:
    python fetch_all.py                  # fetch all sources
    python fetch_all.py orsr             # fetch only ORSR
    python fetch_all.py lookup 36234176  # lookup single company by IČO

Sources:
  orsr    — Obchodný register SR (scraping, windows-1250). Název firmy, sídlo, IČO,
            právní forma, předmět podnikání, datum zápisu. Obdoba českého justice.cz.

  finstat — FinStat.sk (scraping). Finanční ukazatele: tržby, zisk, počet zaměstnanců,
            celková aktiva. Nejlepší volně dostupný zdroj finančních dat pro SK firmy.
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)


def all_icos():
    """Return all IČOs (portfolio + competitors)."""
    icos = dict(COMPANIES["portfolio"])
    for sector_companies in COMPANIES["competitors"].values():
        icos.update(sector_companies)
    return icos


# --- 1. ORSR.sk (Obchodný register) ---

def fetch_orsr_search(ico: str) -> dict:
    """Search ORSR by IČO, return search result with link to detail."""
    url = f"https://www.orsr.sk/hladaj_ico.asp?ICO={ico}&SID=0"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("windows-1250", errors="replace")

    # Extract detail link (výpis ID)
    links = re.findall(r'href="vypis\.asp\?ID=(\d+)&(?:amp;)?SID=(\d+)&(?:amp;)?P=(\d+)"', html)
    # Extract company name from table cells
    tds = re.findall(r'<td[^>]*>(.*?)</td>', html, re.S)
    name = ""
    for td in tds:
        clean = re.sub(r'<[^>]+>', '', td).strip()
        if clean and len(clean) > 5 and "Home Credit" in clean or "SkyToll" in clean or "CETIN" in clean or "a.s." in clean or "s.r.o." in clean:
            if "IČO" not in clean and "Stránka" not in clean and "MINISTERSTVO" not in clean:
                name = clean
                break

    return {
        "ico": ico,
        "name": name,
        "detail_ids": [{"id": l[0], "sid": l[1], "p": l[2]} for l in links],
    }


def fetch_orsr_detail(detail_id: str, sid: str = "2", p: str = "1") -> dict:
    """Fetch company detail from ORSR."""
    url = f"https://www.orsr.sk/vypis.asp?ID={detail_id}&SID={sid}&P={p}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("windows-1250", errors="replace")

    text = re.sub(r"<[^>]+>", "|", html)
    cells = [c.strip() for c in text.split("|") if c.strip() and len(c.strip()) > 2]

    # Extract structured fields
    data = {"raw_cells": cells[:50]}
    field_map = {
        "Obchodné meno": "name",
        "Sídlo": "address",
        "IČO": "ico",
        "Deň zápisu": "registration_date",
        "Právna forma": "legal_form",
        "Základné imanie": "share_capital",
        "Predmet podnikania": "business_purpose",
    }
    for i, cell in enumerate(cells):
        for sk_name, en_name in field_map.items():
            if sk_name in cell and i + 1 < len(cells):
                data[en_name] = cells[i + 1] if cells[i + 1] != cell else ""

    return data


def fetch_all_orsr():
    print("=== ORSR (Obchodný register SR) ===")
    results = {}
    for ico, info in all_icos().items():
        try:
            search = fetch_orsr_search(ico)
            if search["detail_ids"]:
                detail = fetch_orsr_detail(search["detail_ids"][0]["id"])
                results[ico] = {
                    "name": search["name"] or detail.get("name", ""),
                    "detail": detail,
                }
                print(f"  OK {ico} {search['name']}")
            else:
                results[ico] = {"name": info.get("name", ""), "found": False}
                print(f"  NOTFOUND {ico} {info.get('name', '')}")
            time.sleep(0.5)
        except Exception as e:
            results[ico] = {"error": str(e), "name": info.get("name", "")}
            print(f"  ERR {ico} {e}")

    out = OUTPUT_DIR / "orsr.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 2. FinStat.sk (financial data, scraping) ---

def fetch_finstat(ico: str) -> dict:
    """Scrape basic financial data from finstat.sk."""
    url = f"https://finstat.sk/{ico}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    data = {}
    # Extract key financial metrics from HTML
    patterns = {
        "revenue": r'Tržby.*?<strong[^>]*>([\d\s,.]+)',
        "profit": r'Zisk.*?<strong[^>]*>([\-\d\s,.]+)',
        "employees": r'Zamestnanci.*?<strong[^>]*>([\d\s]+)',
        "assets": r'Aktíva celkom.*?<strong[^>]*>([\d\s,.]+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, html, re.S | re.I)
        if match:
            data[key] = match.group(1).strip()

    # Also get company name
    title = re.search(r"<title>(.*?)</title>", html)
    if title:
        data["title"] = title.group(1).strip()

    return data


def fetch_all_finstat():
    print("=== FinStat.sk (financial data) ===")
    results = {}
    for ico, info in all_icos().items():
        try:
            data = fetch_finstat(ico)
            results[ico] = data
            print(f"  OK {ico} {data.get('title', '?')[:60]}")
            time.sleep(1.0)  # be polite
        except Exception as e:
            results[ico] = {"error": str(e)}
            print(f"  ERR {ico} {e}")

    out = OUTPUT_DIR / "finstat.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- Single company lookup ---

def lookup_company(ico: str):
    """Lookup a single Slovak company by IČO."""
    print(f"=== Lookup IČO: {ico} ===\n")

    print("--- ORSR ---")
    try:
        search = fetch_orsr_search(ico)
        print(f"  Názov: {search['name']}")
        if search["detail_ids"]:
            detail = fetch_orsr_detail(search["detail_ids"][0]["id"])
            for key in ["address", "registration_date", "legal_form", "share_capital", "business_purpose"]:
                if detail.get(key):
                    print(f"  {key}: {detail[key]}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- FinStat ---")
    try:
        data = fetch_finstat(ico)
        for key in ["title", "revenue", "profit", "employees", "assets"]:
            if data.get(key):
                print(f"  {key}: {data[key]}")
    except Exception as e:
        print(f"  Error: {e}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_company(sys.argv[2])
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["orsr", "finstat"]
        runners = {
            "orsr": fetch_all_orsr,
            "finstat": fetch_all_finstat,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <IČO>, {list(runners.keys())}")
