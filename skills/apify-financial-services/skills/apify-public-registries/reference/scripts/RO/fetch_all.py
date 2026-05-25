#!/usr/bin/env python3
"""Fetch data from Romanian sources for portfolio (PRO TV) + competitors.

Usage:
    python fetch_all.py                # fetch ANAF for all companies
    python fetch_all.py listafirme     # scrape ListaFirme via Apify
    python fetch_all.py status         # check Apify run status
    python fetch_all.py lookup 2835636 # lookup single company by CUI (ANAF)

Sources:
  listafirme — ListaFirme.ro (via Apify, Cloudflare-protected). Firemní profily z rumunského
               registru: CUI, adresa, CAEN kódy, bilanční data. Portfolio entita: PRO TV S.R.L.
               Vyžaduje Apify residential proxy.

  anaf       — ANAF (Agenția Națională de Administrare Fiscală) REST API. Status plátce DPH,
               adresa, aktivní/neaktivní.
               NEFUNKČNÍ od března 2026 — endpoint webservicesp.anaf.ro vrací 404.
               Alternativa: openapi.ro nebo termene.ro (vyžadují API klíč).

Original sources:
  1. ListaFirme.ro — company profiles (via Apify, Cloudflare-protected)
  2. ANAF public data — tax/VAT status (direct API)
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "lookup_targets.json") as f:
    COMPANIES = json.load(f)

UA = "User-Agent: apify-awesome-skills/apify-mcpc-1.4.1/call_actor"


def all_cuis():
    """Return all CUI numbers."""
    companies = dict(COMPANIES["portfolio"])
    for sector_companies in COMPANIES["competitors"].values():
        companies.update(sector_companies)
    return companies


# --- 1. ListaFirme.ro via Apify ---

def fetch_listafirme_apify(cui: str, name: str) -> dict:
    """Scrape company profile from listafirme.ro via Apify."""
    slug = name.lower().replace(" ", "-").replace(".", "").replace(",", "")
    url = f"https://www.listafirme.ro/{slug}-{cui}/"
    input_data = {
        "startUrls": [{"url": url}],
        "maxCrawlPages": 1,
        "crawlerType": "playwright:firefox",
        "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }
    input_json = json.dumps(input_data)
    cmd = [
        "mcpc", "-H", UA, "@apify", "tools-call", "call-actor",
        "actor:=apify/website-content-crawler",
        f"input:={input_json}",
        'callOptions:={"memory": 2048, "timeout": 60}',
        "previewOutput:=false", "async:=true", "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        return {"error": result.stderr[:300]}
    return json.loads(result.stdout).get("structuredContent", {})


def fetch_all_listafirme():
    print("=== ListaFirme.ro (via Apify) ===")
    runs = {}
    for cui, info in all_cuis().items():
        name = info.get("name", "")
        print(f"  Launching: {cui} {name}...")
        try:
            result = fetch_listafirme_apify(cui, name)
            run_id = result.get("runId", "?")
            runs[cui] = {"name": name, "run_id": run_id}
            print(f"    runId={run_id}")
            time.sleep(1.0)
        except Exception as e:
            runs[cui] = {"name": name, "error": str(e)}
            print(f"    ERR: {e}")

    out = OUTPUT_DIR / "listafirme_runs.json"
    with open(out, "w") as f:
        json.dump(runs, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(runs)} async runs to {out}")
    print("  Check status: python fetch_all.py status")
    return runs


# --- 2. ANAF tax validation ---
# NOTE: ANAF webservicesp.anaf.ro API appears offline as of March 2026.
# They may have migrated to a new endpoint. Check https://www.anaf.ro for updates.
# Alternative: use https://termene.ro or https://openapi.ro (need API key)

def fetch_anaf(cui: str) -> dict:
    """Check company VAT status via ANAF public API."""
    from datetime import date
    today = date.today().isoformat()
    url = "https://webservicesp.anaf.ro/AsynchWebApi/api/v8/interogare/getInformatii"
    body = json.dumps([{"cui": int(cui), "data": today}])
    req = urllib.request.Request(url, data=body.encode(), headers={
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_all_anaf():
    print("=== ANAF (tax/VAT status) ===")
    results = {}
    for cui, info in all_cuis().items():
        try:
            data = fetch_anaf(cui)
            found = data.get("found", [])
            if found:
                f = found[0]
                results[cui] = {
                    "name": f.get("denumire", ""),
                    "address": f.get("adresa", ""),
                    "vat_payer": f.get("scpTVA", False),
                    "vat_split": f.get("statusTvaIncasare", False),
                    "active": f.get("statusInactivi", False) is False,
                    "reactivated": f.get("dataReactivare"),
                }
                status = "TVA" if f.get("scpTVA") else "non-TVA"
                print(f"  OK {cui} {f.get('denumire','')} [{status}]")
            else:
                not_found = data.get("notfound", [])
                results[cui] = {"cui": cui, "found": False}
                print(f"  NOTFOUND {cui} {info.get('name', '')}")
            time.sleep(0.3)
        except Exception as e:
            results[cui] = {"error": str(e)}
            print(f"  ERR {cui} {e}")

    out = OUTPUT_DIR / "anaf.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- Status check ---

def check_status():
    fpath = OUTPUT_DIR / "listafirme_runs.json"
    if not fpath.exists():
        print("No runs to check")
        return
    with open(fpath) as f:
        runs = json.load(f)
    for cui, info in runs.items():
        run_id = info.get("run_id")
        if not run_id or run_id == "?":
            continue
        cmd = [
            "mcpc", "-H", UA, "@apify", "tools-call", "get-actor-run",
            f"runId:={run_id}", "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            sc = json.loads(result.stdout).get("structuredContent", {})
            ds = sc.get("dataset", {})
            print(f"  {cui} ({info.get('name','')}): status={sc.get('status')} items={ds.get('itemCount','?')}")


# --- Single company lookup ---

def lookup_company(cui: str):
    """Lookup a single Romanian company by CUI."""
    print(f"=== Lookup CUI: {cui} ===\n")

    print("--- ANAF ---")
    try:
        data = fetch_anaf(cui)
        found = data.get("found", [])
        if found:
            f = found[0]
            print(f"  Denumire: {f.get('denumire')}")
            print(f"  Adresa: {f.get('adresa')}")
            print(f"  Plătitor TVA: {f.get('scpTVA')}")
            print(f"  Activ: {f.get('statusInactivi', False) is False}")
        else:
            print(f"  Not found (ANAF API may be offline — check https://www.anaf.ro)")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- ListaFirme (Apify) ---")
    print(f"  Run: python fetch_all.py listafirme")
    print(f"  Or manually: https://www.listafirme.ro/search?query={cui}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_company(sys.argv[2])
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["anaf"]
        runners = {
            "anaf": fetch_all_anaf,
            "listafirme": fetch_all_listafirme,
            "status": check_status,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <CUI>, {list(runners.keys())}")
