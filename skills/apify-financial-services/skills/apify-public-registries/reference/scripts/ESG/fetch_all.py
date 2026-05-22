#!/usr/bin/env python3
"""Fetch structured ESG data from verified working sources.

Usage:
    python fetch_all.py                        # fetch all sources
    python fetch_all.py ets                    # EU ETS verified emissions
    python fetch_all.py climate_trace          # Climate TRACE country emissions
    python fetch_all.py eba                    # EBA bank capital/risk data (100MB+)
    python fetch_all.py eba_esg               # EBA Pillar 3 ESG signposting (XLSX)
    python fetch_all.py ratings               # ESG rating URLs for listed portfolio companies
    python fetch_all.py lookup "Czech Republic" # lookup country in EU ETS + Climate TRACE

Sources (all verified working, free, no auth):
  ets            — EU ETS (GitHub CSV). Ověřené CO2 emise per průmyslová instalace.
                   76K řádků, filtrováno na portfolio země (BG, HU, PL, RO, SK).
                   CZ v tomto datasetu chybí. Portfolio firmy většinou nejsou těžký průmysl,
                   takže přímé matche jsou nepravděpodobné — spíš kontextový benchmark.

  climate_trace  — Climate TRACE REST API. Celkové GHG emise per země + global rank.
                   CZ: 232M tCO2e (#61), PL: 817M (#29). Kontextový zdroj, ne firemní data.

  eba            — EBA Transparency CSVs (100MB+ per soubor). Bankovní metriky: kapitál,
                   credit risk, sovereign exposure pro ~120 EU bank. Filtruje přes LEI.
                   Relevantní pro Air Bank + PPF banka pokud mají LEI v EBA datasetu (company names).

  eba_esg        — EBA Pillar 3 ESG signposting (XLSX, 62KB). Linky na ESG disclosures
                   ~120 EU bank. Vyžaduje Referer header pro download.

  ratings        — ESG rating URLs (jen linky, žádná strojová data). S&P Global score
                   pro InPost a O2 CZ. Sustainalytics risk rating pro InPost.
                   NÍZKÁ HODNOTA: jen URL pro manuální lookup, nelze programově extrahovat.
                   PPF Group je privátní — hlavní ESG ratingové agentury ji nekryjí.
                   ESAP (centrální EU ESG databáze s API) spustí CSRD data až leden 2028.
"""

import json
import csv
import io
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)


# --- 1. EU ETS (Emissions Trading System) ---

def fetch_eu_ets():
    """Download EU ETS verified emissions and filter by portfolio countries."""
    print("=== EU ETS (Verified CO2 Emissions) ===")
    url = COMPANIES["eu_ets"]["csv_url"]
    countries = set(COMPANIES["eu_ets"]["countries"])

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(data))
    results = {}
    total = 0
    for row in reader:
        total += 1
        country = row.get("country", "")
        if country in countries:
            if country not in results:
                results[country] = []
            results[country].append(dict(row))

    summary = {c: len(rows) for c, rows in results.items()}
    print(f"  Total rows: {total}")
    for c, count in sorted(summary.items()):
        print(f"  {c}: {count} installations")

    out = OUTPUT_DIR / "eu_ets.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {out}")


# --- 2. Climate TRACE (country-level emissions) ---

def fetch_climate_trace_country(country_code: str) -> dict:
    """Fetch country emissions from Climate TRACE API."""
    url = f"https://api.climatetrace.org/v6/country/emissions?since=2022&to=2023&countries={country_code}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_climate_trace_sectors(country_code: str) -> list:
    """Fetch sector breakdown for a country."""
    url = f"https://api.climatetrace.org/v6/country/emissions?since=2023&to=2023&countries={country_code}&subsectors=true"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_all_climate_trace():
    """Fetch Climate TRACE emissions for all portfolio countries."""
    print("=== Climate TRACE (Country Emissions) ===")
    countries = COMPANIES["climate_trace"]["countries"]
    results = {}

    for cc in countries:
        try:
            data = fetch_climate_trace_country(cc)
            if data and isinstance(data, list) and len(data) > 0:
                entry = data[0]
                emissions = entry.get("emissions", {})
                co2e = emissions.get("co2e_100yr", 0)
                results[cc] = {
                    "co2e_100yr_tonnes": co2e,
                    "co2_tonnes": emissions.get("co2", 0),
                    "ch4_tonnes": emissions.get("ch4", 0),
                    "rank": entry.get("rank"),
                }
                print(f"  {cc}: {co2e/1e6:.1f}M tCO2e (rank #{entry.get('rank', '?')})")
            else:
                results[cc] = {"error": "no data"}
                print(f"  {cc}: no data")
            time.sleep(0.3)
        except Exception as e:
            results[cc] = {"error": str(e)}
            print(f"  {cc}: {e}")

    out = OUTPUT_DIR / "climate_trace.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {out}")


# --- 3. EBA Transparency (bank capital/risk CSVs) ---

def fetch_eba_transparency():
    """Download EBA transparency CSVs and filter for portfolio bank LEIs."""
    print("=== EBA Transparency Exercise (Bank Data) ===")
    base = COMPANIES["eba_transparency"]["base_url"]
    files = COMPANIES["eba_transparency"]["files"]

    # Known portfolio bank LEIs (from GLEIF)
    # TODO: replace with actual LEIs from local/EU/output/gleif.json
    portfolio_leis = set()
    gleif_path = BASE_DIR.parent / "EU" / "output" / "gleif.json"
    if gleif_path.exists():
        with open(gleif_path) as f:
            gleif = json.load(f)
            for lei, info in gleif.items():
                if isinstance(info, dict):
                    name = info.get("name", "").lower()
                    if any(k in name for k in ("air bank", "ppf banka", "ppf bank", "home credit")):
                        portfolio_leis.add(lei)
                        print(f"  LEI match: {lei} ({info.get('name')})")

    if not portfolio_leis:
        print("  No portfolio bank LEIs found in GLEIF data. Run local/EU/fetch_all.py gleif first.")
        print("  Downloading full CSVs for manual inspection...")

    results = {}
    for label, fname in files.items():
        url = f"{base}/{fname}"
        print(f"  Downloading {fname}...")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=120) as resp:
                reader = csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8"))
                matched = []
                total = 0
                for row in reader:
                    total += 1
                    if portfolio_leis and row.get("LEI_Code") in portfolio_leis:
                        matched.append(dict(row))

                results[label] = {
                    "file": fname,
                    "total_rows": total,
                    "matched": len(matched),
                    "data": matched[:200],
                }
                print(f"    {total} rows, {len(matched)} matched portfolio LEIs")
        except Exception as e:
            results[label] = {"error": str(e)}
            print(f"    Error: {e}")

    out = OUTPUT_DIR / "eba_transparency.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {out}")


# --- 4. EBA Pillar 3 ESG signposting ---

def fetch_eba_esg():
    """Download EBA Pillar 3 ESG signposting XLSX."""
    print("=== EBA Pillar 3 ESG (Signposting XLSX) ===")
    url = COMPANIES["eba_transparency"]["pillar3_esg"]
    out = OUTPUT_DIR / "eba_pillar3_esg_signposting.xlsx"
    try:
        req = urllib.request.Request(url, headers={
            "Referer": "https://www.eba.europa.eu/",
            "User-Agent": "Mozilla/5.0",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(out, "wb") as f:
                f.write(resp.read())
        size = out.stat().st_size
        print(f"  Downloaded {size/1024:.0f} KB to {out}")
        print("  Contains: ESG disclosure links for ~120 EU banks")
    except Exception as e:
        print(f"  Error: {e}")


# --- 5. ESG Ratings (URLs for listed companies) ---

def fetch_ratings_info():
    """Print ESG rating URLs for listed portfolio companies."""
    print("=== ESG Ratings (Free Lookup URLs) ===")
    listed = COMPANIES.get("listed_companies", {})

    for key, info in listed.items():
        name = info.get("name", key)
        print(f"\n  {name}:")
        if info.get("spglobal_url"):
            print(f"    S&P Global ESG Score: {info['spglobal_url']}")
        if info.get("sustainalytics_url"):
            print(f"    Sustainalytics Risk Rating: {info['sustainalytics_url']}")
        print(f"    MSCI: search at https://www.msci.com/data-and-analytics/sustainability-solutions/esg-ratings-climate-search-tool")
        print(f"    LSEG: search at https://www.lseg.com/en/data-analytics/sustainable-finance/esg-scores")

    print("\n  Note: Group-level entity is private — ESG raters cover mainly listed companies.")
    print("  ESAP (centralized CSRD reports + API) launches January 2028.")


# --- Single lookup ---

def lookup_country(name: str):
    """Lookup a country in EU ETS and Climate TRACE."""
    print(f"=== ESG Lookup: {name} ===\n")

    # Map common names to ISO codes
    name_to_code = {
        "czech republic": "CZE", "czechia": "CZE", "cz": "CZE",
        "slovakia": "SVK", "sk": "SVK",
        "poland": "POL", "pl": "POL",
        "hungary": "HUN", "hu": "HUN",
        "bulgaria": "BGR", "bg": "BGR",
        "serbia": "SRB", "rs": "SRB",
        "romania": "ROU", "ro": "ROU",
    }
    code = name_to_code.get(name.lower(), name.upper())

    print("--- Climate TRACE ---")
    try:
        data = fetch_climate_trace_country(code)
        if data and isinstance(data, list) and data:
            e = data[0].get("emissions", {})
            print(f"  CO2e (100yr): {e.get('co2e_100yr', 0)/1e6:.1f}M tonnes")
            print(f"  CO2: {e.get('co2', 0)/1e6:.1f}M tonnes")
            print(f"  CH4: {e.get('ch4', 0)/1e6:.2f}M tonnes")
            print(f"  Global rank: #{data[0].get('rank', '?')}")
        else:
            print(f"  No data for {code}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- EU ETS ---")
    # Map ISO3 to country names used in ETS CSV
    code_to_name = {"CZE": "Czech Republic", "SVK": "Slovakia", "POL": "Poland",
                    "HUN": "Hungary", "BGR": "Bulgaria", "ROU": "Romania"}
    ets_name = code_to_name.get(code, name)
    print(f"  Filter EU ETS CSV for country='{ets_name}'")
    print(f"  Run: python fetch_all.py ets")

    ets_path = OUTPUT_DIR / "eu_ets.json"
    if ets_path.exists():
        with open(ets_path) as f:
            ets = json.load(f)
        rows = ets.get(ets_name, [])
        print(f"  Found {len(rows)} installations in cached data")
        for r in rows[:3]:
            print(f"    {r.get('main activity sector name', '?')}: {r.get('value', '?')} {r.get('unit', '')}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_country(" ".join(sys.argv[2:]))
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["ets", "climate_trace", "eba_esg", "ratings"]
        # Note: 'eba' downloads 100MB+ CSVs, run separately
        runners = {
            "ets": fetch_eu_ets,
            "climate_trace": fetch_all_climate_trace,
            "eba": fetch_eba_transparency,
            "eba_esg": fetch_eba_esg,
            "ratings": fetch_ratings_info,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <country>, {list(runners.keys())}")
