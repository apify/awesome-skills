#!/usr/bin/env python3
"""Fetch data from all EU-level sources for portfolio companies.

Usage:
    python fetch_all.py                      # fetch all sources (except EBA)
    python fetch_all.py gleif esma           # fetch specific sources
    python fetch_all.py eba                  # fetch EBA (100MB+ download!)
    python fetch_all.py lookup PPF           # search GLEIF + ESMA + TED for name
    python fetch_all.py lookup_lei 31570048XH84U51GGT05  # lookup by LEI

Sources:
  gleif    — GLEIF REST API. LEI identifikátory + vlastnická struktura (parent/ultimate
             parent chain). Nejcennější EU zdroj — mapuje vlastnické řetězce →
             AMALAR Holding. 51 LEI záznamů nalezeno. Zdarma, bez auth.

  esma     — ESMA FIRDS (Solr API). Finanční instrumenty: dluhopisy, akcie, deriváty.
             InPost: 4394 instrumentů, O2 CZ: 37, CETIN: 40, PPF Arena bonds: 2.
             Zdarma, bez auth.

  eba      — EBA Transparency Exercise (CSV download, 100MB+ per soubor). Bankovní metriky:
             kapitál, credit risk, market risk, sovereign exposure pro ~120 EU bank.
             Filtruje se přes LEI kódy. Zdarma, bez auth.

  ted      — TED API (veřejné zakázky). Contract awards s hodnotou, buyer/winner.
             NÍZKÁ HODNOTA: většina portfolio firem jsou soukromé a nezadávají
             veřejné zakázky. Výjimka: CETIN (116 zakázek). Winner-name jen u
             novějších eForms notices (~2024+).

  eurostat — Eurostat SDMX API. Makroekonomické statistiky (GDP, sektorová data).
             NÍZKÁ HODNOTA: příliš agregované, žádná firemní data. Jen jako kontextový
             benchmark pro země kde portfolio operuje.
"""

import json
import os
import sys
import time
import urllib.request
import csv
import io
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)

# Also load CZ companies for LEI cross-referencing
CZ_COMPANIES_PATH = BASE_DIR.parent / "CZ" / "lookup_targets.json"
CZ_COMPANIES = {}
if CZ_COMPANIES_PATH.exists():
    with open(CZ_COMPANIES_PATH) as f:
        CZ_COMPANIES = json.load(f)


# --- 1. GLEIF API (LEI + ownership) ---

def gleif_search_name(name: str) -> list:
    encoded = urllib.parse.quote(name)
    url = f"https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D={encoded}&page%5Bsize%5D=10"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read()).get("data", [])


def gleif_get_lei(lei: str) -> dict:
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read()).get("data", {})


def gleif_get_parent(lei: str) -> dict:
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}/direct-parent-relationship"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("data", {})
    except urllib.error.HTTPError:
        return {}


def fetch_all_gleif():
    print("=== GLEIF (LEI + Ownership) ===")
    results = {}

    # Search for all portfolio entities by name
    for search_term in ["PPF", "Home Credit", "CETIN", "Air Bank", "O2 Czech", "Heureka", "SOTIO", "InPost"]:
        try:
            records = gleif_search_name(search_term)
            for rec in records:
                lei = rec["attributes"]["lei"]
                entity = rec["attributes"]["entity"]
                results[lei] = {
                    "lei": lei,
                    "name": entity["legalName"]["name"],
                    "jurisdiction": entity.get("jurisdiction"),
                    "status": entity["status"],
                    "registered_as": entity.get("registeredAs"),
                    "category": entity.get("category"),
                }
            print(f"  Search '{search_term}': {len(records)} results")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ERR search '{search_term}': {e}")

    # Get parent relationships for known portfolio LEIs
    portfolio_leis = list(COMPANIES["portfolio"].keys())
    for lei in portfolio_leis:
        try:
            parent = gleif_get_parent(lei)
            if parent:
                rel = parent.get("attributes", {}).get("relationship", {})
                end_lei = rel.get("endNode", {}).get("id", "")
                if end_lei:
                    results.setdefault(lei, {})["parent_lei"] = end_lei
                    # Resolve parent name
                    parent_rec = gleif_get_lei(end_lei)
                    if parent_rec:
                        parent_name = parent_rec.get("attributes", {}).get("entity", {}).get("legalName", {}).get("name")
                        results[lei]["parent_name"] = parent_name
                        print(f"  Ownership: {lei[:12]}... -> {parent_name}")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ERR parent {lei}: {e}")

    out = OUTPUT_DIR / "gleif.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} LEI records to {out}")
    return results


# --- 2. TED (Public Procurement — contract awards only) ---
# TED expert query syntax: buyer-name ~ "*keyword*" AND notice-type = can-standard
# Output fields: total-value, winner-name, buyer-name, buyer-country, place-of-performance
# NOTE: winner-name is only populated in eForms notices (~2023+). Older notices have
#       winner data only in the XML document (fetch via notice links.xml.MUL URL).

TED_OUTPUT_FIELDS = [
    "publication-date", "notice-type", "buyer-name", "buyer-country",
    "contract-nature", "procedure-type", "total-value",
    "winner-name", "place-of-performance", "dispatch-date",
]


def fetch_ted_awards(query: str, limit: int = 50) -> list:
    """Search TED for contract award notices (won contracts) matching buyer name."""
    url = "https://api.ted.europa.eu/v3/notices/search"
    expert_query = f'buyer-name ~ "*{query}*" AND notice-type = can-standard'
    body = json.dumps({"query": expert_query, "fields": TED_OUTPUT_FIELDS, "limit": limit})
    req = urllib.request.Request(url, data=body.encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data.get("notices", []), data.get("totalNoticeCount", 0)


def _extract_name(field_val):
    """Extract name from TED multi-lang dict."""
    if isinstance(field_val, dict):
        return field_val.get("ces", field_val.get("eng", field_val.get("mul", [""])))[0] if field_val else ""
    return str(field_val) if field_val else ""


def fetch_all_ted():
    print("=== TED (Contract Awards) ===")
    results = {}
    search_terms = ["PPF", "O2 Czech", "CETIN", "Air Bank", "Home Credit",
                    "Škoda Transportation", "CzechToll", "InPost", "Heureka"]
    for term in search_terms:
        try:
            notices, total = fetch_ted_awards(term, limit=200)
            awards = []
            for n in notices:
                awards.append({
                    "id": n.get("publication-number"),
                    "date": n.get("publication-date", ""),
                    "buyer": _extract_name(n.get("buyer-name")),
                    "buyer_country": n.get("buyer-country", []),
                    "winner": _extract_name(n.get("winner-name")),
                    "value_eur": n.get("total-value"),
                    "nature": n.get("contract-nature", []),
                    "procedure": n.get("procedure-type", ""),
                    "nuts": n.get("place-of-performance", []),
                })
            results[term] = {"total": total, "awards": awards}
            print(f"  '{term}': {total} contract awards")
            for a in awards[:3]:
                val = f"€{a['value_eur']:,.0f}" if a.get("value_eur") else "?"
                print(f"    {a['date'][:10]} | {a['buyer'][:30]} | {val} | winner: {a['winner'][:30]}")
            time.sleep(0.5)
        except Exception as e:
            results[term] = {"error": str(e)}
            print(f"  ERR '{term}': {e}")

    out = OUTPUT_DIR / "ted.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} searches to {out}")
    return results


# --- 3. ESMA FIRDS (Financial Instruments) ---

def fetch_esma_firds(query: str) -> dict:
    encoded = urllib.parse.quote(f'"{query}"')
    url = f"https://registers.esma.europa.eu/solr/esma_registers_firds/select?q=gnr_full_name:{encoded}&rows=20&wt=json&fl=id,isin,lei,gnr_full_name,status,gnr_cfi_code"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_all_esma():
    print("=== ESMA FIRDS (Financial Instruments) ===")
    results = {}
    search_terms = ["PPF Arena", "PPF Group", "O2 Czech", "Home Credit", "CETIN", "InPost"]
    for term in search_terms:
        try:
            data = fetch_esma_firds(term)
            docs = data.get("response", {}).get("docs", [])
            num_found = data.get("response", {}).get("numFound", 0)
            results[term] = {
                "total_found": num_found,
                "instruments": [
                    {
                        "isin": d.get("isin"),
                        "name": d.get("gnr_full_name"),
                        "lei": d.get("lei"),
                        "status": d.get("status"),
                        "cfi": d.get("gnr_cfi_code"),
                    }
                    for d in docs
                ],
            }
            print(f"  '{term}': {num_found} instruments")
            time.sleep(0.3)
        except Exception as e:
            results[term] = {"error": str(e)}
            print(f"  ERR '{term}': {e}")

    out = OUTPUT_DIR / "esma_firds.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} searches to {out}")
    return results


# --- 4. EBA Transparency Exercise ---

EBA_BASE = "https://www.eba.europa.eu/assets/TE2025/Full_database/883401"
EBA_FILES = ["tr_cre.csv", "tr_mrk.csv", "tr_sov.csv"]


def fetch_eba_for_leis(lei_list: list):
    """Download EBA CSV and filter for specific LEI codes."""
    print("=== EBA Transparency Exercise ===")
    results = {}
    lei_set = set(lei_list)

    for fname in EBA_FILES:
        url = f"{EBA_BASE}/{fname}"
        print(f"  Downloading {fname}...")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=120) as resp:
                # Stream and filter - these files are 100MB+
                reader = csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8"))
                matched_rows = []
                total = 0
                for row in reader:
                    total += 1
                    if row.get("LEI_Code") in lei_set:
                        matched_rows.append(dict(row))
                results[fname] = {
                    "total_rows": total,
                    "matched_rows": len(matched_rows),
                    "data": matched_rows[:500],  # cap to avoid huge files
                }
                print(f"  {fname}: {total} total rows, {len(matched_rows)} matched for our LEIs")
        except Exception as e:
            results[fname] = {"error": str(e)}
            print(f"  ERR {fname}: {e}")

    out = OUTPUT_DIR / "eba_transparency.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {out}")
    return results


def fetch_all_eba():
    # Get LEIs from GLEIF results or known list
    gleif_path = OUTPUT_DIR / "gleif.json"
    lei_list = list(COMPANIES["portfolio"].keys())
    if gleif_path.exists():
        with open(gleif_path) as f:
            gleif_data = json.load(f)
            lei_list.extend(gleif_data.keys())
    return fetch_eba_for_leis(lei_list)


# --- 5. Eurostat (sector benchmarks) ---

def fetch_eurostat(dataset: str, params: dict) -> dict:
    param_str = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{dataset}?{param_str}&format=JSON&lang=en"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_all_eurostat():
    print("=== Eurostat (sector benchmarks) ===")
    results = {}
    queries = {
        "gdp_cz_pl": {"dataset": "nama_10_gdp", "params": {"na_item": "B1GQ", "geo": "CZ+PL", "unit": "CP_MEUR", "time": "2021+2022+2023+2024"}},
    }
    for name, q in queries.items():
        try:
            data = fetch_eurostat(q["dataset"], q["params"])
            results[name] = {
                "label": data.get("label"),
                "value_count": len(data.get("value", {})),
            }
            print(f"  {name}: {len(data.get('value', {}))} data points")
        except Exception as e:
            results[name] = {"error": str(e)}
            print(f"  ERR {name}: {e}")

    out = OUTPUT_DIR / "eurostat.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {out}")
    return results


# --- Single company lookup ---

def lookup_by_name(name: str):
    """Search for a company across GLEIF, ESMA, and TED by name."""
    print(f"=== Lookup: {name} ===\n")

    print("--- GLEIF (LEI) ---")
    try:
        records = gleif_search_name(name)
        for rec in records[:5]:
            e = rec["attributes"]["entity"]
            lei = rec["attributes"]["lei"]
            print(f"  LEI: {lei}  {e['legalName']['name']}  [{e.get('jurisdiction','?')}] {e['status']}")
    except Exception as ex:
        print(f"  Error: {ex}")

    print("\n--- ESMA FIRDS (instruments) ---")
    try:
        data = fetch_esma_firds(name)
        docs = data.get("response", {}).get("docs", [])
        num = data.get("response", {}).get("numFound", 0)
        print(f"  Found: {num} instruments")
        for d in docs[:5]:
            print(f"    ISIN: {d.get('isin')}  {d.get('gnr_full_name')}  [{d.get('status')}]")
    except Exception as ex:
        print(f"  Error: {ex}")

    print("\n--- TED (contract awards) ---")
    try:
        awards, total = fetch_ted_awards(name, limit=10)
        print(f"  Found: {total} contract awards")
        for a in awards[:5]:
            buyer = _extract_name(a.get("buyer-name"))
            winner = _extract_name(a.get("winner-name"))
            val = a.get("total-value")
            val_str = f"€{val:,.0f}" if val else "?"
            print(f"    {a.get('publication-date','')[:10]} | {buyer[:30]} | {val_str} | winner: {winner[:30]}")
    except Exception as ex:
        print(f"  Error: {ex}")


def lookup_by_lei(lei: str):
    """Lookup a specific LEI with ownership chain."""
    print(f"=== Lookup LEI: {lei} ===\n")

    print("--- GLEIF record ---")
    try:
        rec = gleif_get_lei(lei)
        e = rec.get("attributes", {}).get("entity", {})
        print(f"  Name: {e.get('legalName', {}).get('name')}")
        print(f"  Jurisdiction: {e.get('jurisdiction')}")
        print(f"  Status: {e.get('status')}")
        print(f"  Registered as: {e.get('registeredAs')}")
        addr = e.get("legalAddress", {})
        print(f"  Address: {addr.get('addressLines', [''])} {addr.get('city', '')} {addr.get('country', '')}")
    except Exception as ex:
        print(f"  Error: {ex}")

    print("\n--- Ownership chain ---")
    try:
        parent = gleif_get_parent(lei)
        if parent:
            rel = parent.get("attributes", {}).get("relationship", {})
            parent_lei = rel.get("endNode", {}).get("id", "")
            if parent_lei:
                parent_rec = gleif_get_lei(parent_lei)
                parent_name = parent_rec.get("attributes", {}).get("entity", {}).get("legalName", {}).get("name")
                print(f"  Direct parent: {parent_name} (LEI: {parent_lei})")
            else:
                print("  No parent relationship found")
        else:
            print("  No parent relationship found")
    except Exception as ex:
        print(f"  Error: {ex}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_by_name(" ".join(sys.argv[2:]))
    elif len(sys.argv) > 2 and sys.argv[1] == "lookup_lei":
        lookup_by_lei(sys.argv[2])
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["gleif", "ted", "esma", "eurostat"]
        # Note: EBA download is 100MB+ per file, run separately with: python fetch_all.py eba
        runners = {
            "gleif": fetch_all_gleif,
            "ted": fetch_all_ted,
            "esma": fetch_all_esma,
            "eba": fetch_all_eba,
            "eurostat": fetch_all_eurostat,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <name>, lookup_lei <LEI>, {list(runners.keys())}")
