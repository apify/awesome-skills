#!/usr/bin/env python3
"""Fetch data from all Czech sources for portfolio + competitors.

Usage:
    python fetch_all.py                    # fetch all sources for all companies
    python fetch_all.py ares               # fetch only ARES
    python fetch_all.py ares dph           # fetch ARES + DPH
    python fetch_all.py lookup 25099345    # lookup single company by IČO (all sources)

Sources:
  ares       — ARES REST API (MF ČR). Základní profil firmy: název, adresa, IČO, DIČ,
               NACE kódy, právní forma, datum vzniku, statusy registrací.
               Klíčový identifikační zdroj pro všechny CZ firmy.

  dph        — Registr DPH (SOAP). Status plátce DPH, nespolehlivý plátce ANO/NE,
               zveřejněné bankovní účty. Užitečné pro due diligence a ověření protistrany.

  cnb_banks  — ČNB seznam bank (CSV open data). Kompletní seznam licencovaných bank v ČR
               s IČO a adresou. Matchuje portfolio banky (Air Bank, PPF banka).

  cnb_oam    — ČNB Centrální úložiště regulovaných informací (Oracle BI XML export).
               Regulované zprávy emitentů — výroční zprávy, pololetní zprávy, ad hoc.
               Relevantní pro O2 CZ (veřejně obchodovaná) a banky.

  justice    — Justice.cz Open Data (CKAN API). Bulk datasety sbírky listin — účetní
               závěrky a výroční zprávy všech firem. 13GB+ XML/CSV.
               Pozn: SSL certifikát občas selhává na macOS.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
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


# --- 1. ARES REST API ---

def fetch_ares(ico: str) -> dict:
    url = f"https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_all_ares():
    print("=== ARES ===")
    results = {}
    icos = all_icos()
    for ico, info in icos.items():
        try:
            data = fetch_ares(ico)
            results[ico] = {
                "name": data.get("obchodniJmeno"),
                "dic": data.get("dic"),
                "address": data.get("sidlo", {}).get("textovaAdresa"),
                "legal_form": data.get("pravniForma"),
                "nace_codes": data.get("czNace", []),
                "founded": data.get("datumVzniku"),
                "registrations": data.get("seznamRegistraci", {}),
            }
            print(f"  OK {ico} {data.get('obchodniJmeno')}")
            time.sleep(0.3)
        except Exception as e:
            results[ico] = {"error": str(e), "name": info.get("name", "")}
            print(f"  ERR {ico} {e}")

    out = OUTPUT_DIR / "ares.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 2. Registr DPH (SOAP) ---

def fetch_dph(dic: str) -> dict:
    soap = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:roz="http://adis.mfcr.cz/rozhraniCRPDPH/">
  <soapenv:Body>
    <roz:StatusNespolehlivyPlatceRequest>
      <roz:dic>{dic}</roz:dic>
    </roz:StatusNespolehlivyPlatceRequest>
  </soapenv:Body>
</soapenv:Envelope>"""
    req = urllib.request.Request(
        "https://adisrws.mfcr.cz/adistc/axis2/services/rozhraniCRPDPH.rozhraniCRPDPHSOAP",
        data=soap.encode(),
        headers={"Content-Type": "text/xml"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode()


def fetch_all_dph():
    print("=== Registr DPH ===")
    results = {}
    icos = all_icos()
    for ico, info in icos.items():
        dic = f"CZ{ico}"
        try:
            xml_str = fetch_dph(dic)
            import re
            unreliable = re.findall(r'nespolehlivyPlatce="([^"]+)"', xml_str)
            accounts = re.findall(r'<standardniUcet cislo="([^"]+)" kodBanky="([^"]+)"/>', xml_str)
            results[ico] = {
                "dic": dic,
                "unreliable": unreliable[0] if unreliable else None,
                "bank_accounts": [{"number": a[0], "bank_code": a[1]} for a in accounts],
            }
            status = unreliable[0] if unreliable else "N/A"
            print(f"  OK {ico} unreliable={status} accounts={len(accounts)}")
            time.sleep(0.2)
        except Exception as e:
            results[ico] = {"error": str(e)}
            print(f"  ERR {ico} {e}")

    out = OUTPUT_DIR / "dph.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 3. ČNB Open Data (bank list CSV) ---

def fetch_cnb_banks():
    print("=== ČNB Banks ===")
    url = "https://jerrs.cnb.cz/apljerrsdad/JERRS.OPENDATA.STAHUJ?p_seznam=1"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")

    import csv, io
    reader = csv.DictReader(io.StringIO(data))
    banks = {}
    our_icos = set(all_icos().keys())
    for row in reader:
        ico = row.get("ičo", row.get("ico", ""))
        banks[ico] = dict(row)
        if ico in our_icos:
            print(f"  MATCH {ico} {row.get('název', row.get('nazev', ''))}")

    out = OUTPUT_DIR / "cnb_banks.json"
    with open(out, "w") as f:
        json.dump(banks, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(banks)} banks to {out}")
    return banks


# --- 4. ČNB Centrální úložiště (OAM XML) ---

def fetch_cnb_oam(ico: str) -> str:
    params = urllib.parse.urlencode({
        "_xpf": "",
        "_xpt": "1",
        "_xdo": "/OAM_CNB_CZ/R1_K22.xdo",
        "_paramspar_emit_ico": ico,
        "_paramspar_emit": "EMIT*",
        "_paramspar_count": "200",
        "_xt": "lay_R1_K22",
        "_xf": "xml",
        "_xmode": "4",
        "par_lang": "cs",
    })
    url = f"https://oam.cnb.cz/xmlpserver/OAM_CNB_CZ/R1_K22.xdo?{params}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_all_cnb_oam():
    print("=== ČNB OAM (Centrální úložiště) ===")
    results = {}
    # Only fetch for companies likely to be emitents (banks, O2, etc.)
    emitent_icos = {
        "60193336": "O2 Czech Republic a.s.",
        "29045371": "Air Bank a.s.",
        "47116129": "PPF banka a.s.",
        "45244782": "Česká spořitelna, a.s.",
        "00001350": "ČSOB a.s.",
        "45317054": "Komerční banka, a.s.",
        "25672720": "MONETA Money Bank, a.s.",
    }
    for ico, name in emitent_icos.items():
        try:
            xml_str = fetch_cnb_oam(ico)
            import re
            docs = re.findall(r"<DOCUMENT_ID>(\d+)</DOCUMENT_ID>", xml_str)
            doc_names = re.findall(r"<DOCUMENT_NAME>(.*?)</DOCUMENT_NAME>", xml_str)
            results[ico] = {
                "name": name,
                "document_count": len(docs),
                "documents": [{"id": d, "name": n} for d, n in zip(docs[:20], doc_names[:20])],
            }
            print(f"  OK {ico} {name}: {len(docs)} documents")
            time.sleep(0.5)
        except Exception as e:
            results[ico] = {"error": str(e), "name": name}
            print(f"  ERR {ico} {name}: {e}")

    out = OUTPUT_DIR / "cnb_oam.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 5. Justice.cz Open Data (CKAN dataset list) ---

def fetch_justice_datasets():
    print("=== Justice.cz Open Data ===")
    url = "https://dataor.justice.cz/api/3/action/package_list"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    datasets = data.get("result", [])
    # Filter for a.s. datasets (most portfolio companies are a.s.)
    relevant = [d for d in datasets if d.startswith(("as-", "sro-"))]

    out = OUTPUT_DIR / "justice_datasets.json"
    with open(out, "w") as f:
        json.dump({"total": len(datasets), "as_sro_datasets": relevant}, f, ensure_ascii=False, indent=2)
    print(f"  Total datasets: {len(datasets)}, a.s./s.r.o.: {len(relevant)}")
    return datasets


# --- Single company lookup ---

def lookup_company(ico: str):
    """Lookup a single company across all sources."""
    print(f"=== Lookup IČO: {ico} ===\n")

    print("--- ARES ---")
    try:
        data = fetch_ares(ico)
        print(f"  Název: {data.get('obchodniJmeno')}")
        print(f"  Adresa: {data.get('sidlo', {}).get('textovaAdresa')}")
        print(f"  DIČ: {data.get('dic')}")
        print(f"  NACE: {data.get('czNace', [])[:5]}")
        print(f"  Založeno: {data.get('datumVzniku')}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- DPH ---")
    try:
        xml_str = fetch_dph(f"CZ{ico}")
        import re
        unreliable = re.findall(r'nespolehlivyPlatce="([^"]+)"', xml_str)
        accounts = re.findall(r'<standardniUcet cislo="([^"]+)" kodBanky="([^"]+)"/>', xml_str)
        print(f"  Nespolehlivý plátce: {unreliable[0] if unreliable else 'N/A'}")
        print(f"  Bankovní účty: {len(accounts)}")
        for a in accounts[:3]:
            print(f"    {a[0]}/{a[1]}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- ČNB OAM ---")
    try:
        xml_str = fetch_cnb_oam(ico)
        import re
        docs = re.findall(r"<DOCUMENT_ID>(\d+)</DOCUMENT_ID>", xml_str)
        print(f"  Regulované dokumenty: {len(docs)}")
    except Exception as e:
        print(f"  Error: {e}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_company(sys.argv[2])
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["ares", "dph", "cnb_banks", "cnb_oam", "justice"]
        runners = {
            "ares": fetch_all_ares,
            "dph": fetch_all_dph,
            "cnb_banks": fetch_cnb_banks,
            "cnb_oam": fetch_all_cnb_oam,
            "justice": fetch_justice_datasets,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <IČO>, {list(runners.keys())}")
