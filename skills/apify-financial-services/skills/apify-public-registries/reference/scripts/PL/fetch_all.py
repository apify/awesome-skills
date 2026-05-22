#!/usr/bin/env python3
"""Fetch data from all Polish sources for portfolio (InPost) + competitors.

Usage:
    python fetch_all.py                    # fetch all sources
    python fetch_all.py krs               # fetch only KRS
    python fetch_all.py lookup 0000536554  # lookup single company by KRS number
    python fetch_all.py lookup_nip 6793087624  # lookup by NIP (Biała Lista + GUS)

Sources:
  krs          — KRS REST API (Krajowy Rejestr Sądowy). Název, NIP, REGON, kapitál,
                 právní forma. Plný výpis z polského obchodního rejstříku. Zdarma, bez auth.

  biala_lista  — Biała Lista VAT API (MF PL). Status plátce DPH, KRS, REGON,
                 bankovní účty. 100 dotazů/den. Obdoba českého registru DPH.

  gus          — GUS/REGON SOAP (Główny Urząd Statystyczny). Statistický registr firem:
                 REGON, NIP, adresa, PKD kódy. Vyžaduje API klíč (GUS_API_KEY).
                 Test env funguje s klíčem 'abcde12345abcde12345' ale nemá reálná data.

  financials   — Finanční výkazy z eKRS (via Apify actor minute_contest/poland-krs-financial-scraper).
                 Parsované účetní závěrky: aktiva, equity, tržby, zisk. $0.03/result.
                 Vyžaduje mcpc CLI s autentizovanou @apify session.
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


def all_krs():
    """Return all KRS numbers (portfolio + competitors)."""
    companies = dict(COMPANIES["portfolio"])
    for sector_companies in COMPANIES["competitors"].values():
        companies.update(sector_companies)
    return companies


# --- 1. KRS REST API ---

def fetch_krs(krs: str) -> dict:
    url = f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=P&format=json"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_all_krs():
    print("=== KRS (Krajowy Rejestr Sądowy) ===")
    results = {}
    for krs, info in all_krs().items():
        try:
            data = fetch_krs(krs)
            odpis = data.get("odpis", {})
            dane = odpis.get("dane", {}).get("dzial1", {}).get("danePodmiotu", {})
            nazwa = dane.get("nazwa", "?")
            if isinstance(nazwa, str):
                nazwa = nazwa.strip('"')
            ids = dane.get("identyfikatory", {})
            nip = ids.get("nip", "") if isinstance(ids, dict) else ""
            regon = ids.get("regon", "") if isinstance(ids, dict) else ""

            # Get capital info from dzial1
            kapital = odpis.get("dane", {}).get("dzial1", {}).get("kapital", {})

            results[krs] = {
                "name": nazwa,
                "nip": nip,
                "regon": regon,
                "capital": kapital,
            }
            print(f"  OK KRS:{krs} {nazwa}")
            time.sleep(0.5)
        except Exception as e:
            results[krs] = {"error": str(e), "name": info.get("name", "")}
            print(f"  ERR KRS:{krs} {info.get('name', '')}: {e}")

    out = OUTPUT_DIR / "krs.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 2. Biała Lista VAT ---

def fetch_biala_lista(nip: str) -> dict:
    from datetime import date
    today = date.today().isoformat()
    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={today}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_all_biala_lista():
    print("=== Biała Lista VAT ===")
    results = {}
    for krs, info in all_krs().items():
        nip = info.get("nip", "")
        if not nip:
            continue
        try:
            data = fetch_biala_lista(nip)
            subject = data.get("result", {}).get("subject")
            if subject:
                results[nip] = {
                    "name": subject.get("name"),
                    "nip": subject.get("nip"),
                    "status": subject.get("statusVat"),
                    "krs": subject.get("krs"),
                    "regon": subject.get("regon"),
                    "bank_accounts": subject.get("accountNumbers", [])[:5],
                }
                print(f"  OK NIP:{nip} {subject.get('name', '?')}")
            else:
                results[nip] = {"nip": nip, "subject": None}
                print(f"  OK NIP:{nip} (no subject returned)")
            time.sleep(1.0)  # rate limit: 100/day
        except Exception as e:
            results[nip] = {"error": str(e)}
            print(f"  ERR NIP:{nip} {e}")

    out = OUTPUT_DIR / "biala_lista.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- 3. KRS Financial Statements (via Apify) ---
# Note: This requires Apify/mcpc CLI. Run separately:
#   mcpc @apify tools-call call-actor actor:="minute_contest/poland-krs-financial-scraper"
#     input:='{"krs":"0000536554"}' async:=true

def fetch_krs_financials_instructions():
    print("=== KRS Financial Statements ===")
    print("  Financial statements require Apify actor: minute_contest/poland-krs-financial-scraper")
    print("  Run for each company:")
    companies = all_krs()
    cmds = []
    for krs, info in companies.items():
        cmd = (
            f'mcpc @apify tools-call call-actor '
            f'actor:="minute_contest/poland-krs-financial-scraper" '
            f'input:=\'{{"krs":"{krs}"}}\' async:=true'
        )
        cmds.append(cmd)
        print(f"  {krs} ({info.get('name', '?')})")

    out = OUTPUT_DIR / "krs_financials_commands.txt"
    with open(out, "w") as f:
        f.write("\n".join(cmds))
    print(f"  Commands saved to {out}")


# --- 4. GUS/REGON SOAP ---

GUS_TEST_KEY = "abcde12345abcde12345"
GUS_TEST_URL = "https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
GUS_PROD_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"


def gus_login(api_key: str = None, url: str = None) -> str:
    key = api_key or os.environ.get("GUS_API_KEY")
    if not key:
        sys.stderr.write(
            "  WARNING: GUS_API_KEY not set — using TEST environment (fake data only).\n"
            "  Request production key via email to regon_bir@stat.gov.pl\n"
        )
        key = GUS_TEST_KEY
    endpoint = url or (GUS_TEST_URL if key == GUS_TEST_KEY else GUS_PROD_URL)

    soap = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:ns="http://CIS/BIR/PUBL/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/Zaloguj</wsa:Action>
    <wsa:To>{endpoint}</wsa:To>
  </soap:Header>
  <soap:Body>
    <ns:Zaloguj>
      <ns:pKluczUzytkownika>{key}</ns:pKluczUzytkownika>
    </ns:Zaloguj>
  </soap:Body>
</soap:Envelope>"""
    req = urllib.request.Request(endpoint, data=soap.encode(), headers={"Content-Type": "application/soap+xml"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        import re
        text = resp.read().decode()
        sid = re.findall(r"<ZalogujResult>(.*?)</ZalogujResult>", text)
        return sid[0] if sid and sid[0] else ""


def gus_search_nip(sid: str, nip: str, url: str = None) -> dict:
    endpoint = url or GUS_TEST_URL
    soap = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:ns="http://CIS/BIR/PUBL/2014/07"
               xmlns:dat="http://CIS/BIR/PUBL/2014/07/DataContract">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/DaneSzukajPodmioty</wsa:Action>
    <wsa:To>{endpoint}</wsa:To>
  </soap:Header>
  <soap:Body>
    <ns:DaneSzukajPodmioty>
      <ns:pParametryWyszukiwania>
        <dat:Nip>{nip}</dat:Nip>
      </ns:pParametryWyszukiwania>
    </ns:DaneSzukajPodmioty>
  </soap:Body>
</soap:Envelope>"""
    req = urllib.request.Request(endpoint, data=soap.encode(), headers={
        "Content-Type": "application/soap+xml",
        "sid": sid,
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        import re
        import html
        text = resp.read().decode()
        result = re.findall(r"<DaneSzukajPodmiotyResult>(.*?)</DaneSzukajPodmiotyResult>", text, re.S)
        if result:
            decoded = html.unescape(result[0])
            data = {}
            for tag in ["Regon", "Nip", "Nazwa", "Wojewodztwo", "Powiat", "Gmina",
                        "Miejscowosc", "KodPocztowy", "Ulica", "Typ", "SilosID"]:
                vals = re.findall(f"<{tag}>(.*?)</{tag}>", decoded)
                if vals:
                    data[tag] = vals[0]
            return data
        return {}


def fetch_all_gus():
    print("=== GUS/REGON ===")
    sid = gus_login()
    if not sid:
        print("  Login failed — need production API key (set GUS_API_KEY env var)")
        print("  Request key via email to regon_bir@stat.gov.pl")
        return {}

    print(f"  Session: {sid[:10]}...")
    results = {}
    for krs, info in all_krs().items():
        nip = info.get("nip", "")
        if not nip:
            continue
        try:
            data = gus_search_nip(sid, nip)
            if data:
                results[nip] = data
                print(f"  OK NIP:{nip} {data.get('Nazwa', '?')}")
            else:
                results[nip] = {"nip": nip, "empty": True}
                print(f"  OK NIP:{nip} (empty result — test env may not have this data)")
            time.sleep(0.3)
        except Exception as e:
            results[nip] = {"error": str(e)}
            print(f"  ERR NIP:{nip} {e}")

    out = OUTPUT_DIR / "gus_regon.json"
    with open(out, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(results)} records to {out}")
    return results


# --- Single company lookup ---

def lookup_by_krs(krs: str):
    """Lookup a single company by KRS number across all sources."""
    print(f"=== Lookup KRS: {krs} ===\n")

    print("--- KRS Registry ---")
    try:
        data = fetch_krs(krs)
        dane = data.get("odpis", {}).get("dane", {}).get("dzial1", {}).get("danePodmiotu", {})
        nazwa = dane.get("nazwa", "?")
        if isinstance(nazwa, str):
            nazwa = nazwa.strip('"')
        ids = dane.get("identyfikatory", {})
        nip = ids.get("nip", "") if isinstance(ids, dict) else ""
        regon = ids.get("regon", "") if isinstance(ids, dict) else ""
        print(f"  Nazwa: {nazwa}")
        print(f"  NIP: {nip}")
        print(f"  REGON: {regon}")
    except Exception as e:
        print(f"  Error: {e}")
        nip = ""

    if nip:
        print("\n--- Biała Lista VAT ---")
        try:
            data = fetch_biala_lista(nip)
            subject = data.get("result", {}).get("subject")
            if subject:
                print(f"  Status VAT: {subject.get('statusVat')}")
                print(f"  KRS: {subject.get('krs')}")
                accts = subject.get("accountNumbers", [])
                print(f"  Bank accounts: {len(accts)}")
            else:
                print("  Subject not found")
        except Exception as e:
            print(f"  Error: {e}")

        print("\n--- GUS/REGON ---")
        try:
            sid = gus_login()
            if sid:
                data = gus_search_nip(sid, nip)
                if data:
                    for k, v in data.items():
                        print(f"  {k}: {v}")
                else:
                    print("  Empty (test env may not have data)")
            else:
                print("  Login failed (need GUS_API_KEY)")
        except Exception as e:
            print(f"  Error: {e}")


def lookup_by_nip(nip: str):
    """Lookup a single company by NIP."""
    print(f"=== Lookup NIP: {nip} ===\n")

    print("--- Biała Lista VAT ---")
    try:
        data = fetch_biala_lista(nip)
        subject = data.get("result", {}).get("subject")
        if subject:
            print(f"  Nazwa: {subject.get('name')}")
            print(f"  NIP: {subject.get('nip')}")
            print(f"  REGON: {subject.get('regon')}")
            print(f"  KRS: {subject.get('krs')}")
            print(f"  Status VAT: {subject.get('statusVat')}")
        else:
            print("  Subject not found")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- GUS/REGON ---")
    try:
        sid = gus_login()
        if sid:
            data = gus_search_nip(sid, nip)
            if data:
                for k, v in data.items():
                    print(f"  {k}: {v}")
            else:
                print("  Empty (test env may not have data)")
        else:
            print("  Login failed (need GUS_API_KEY)")
    except Exception as e:
        print(f"  Error: {e}")


# --- MAIN ---

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "lookup":
        lookup_by_krs(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "lookup_nip":
        lookup_by_nip(sys.argv[2])
    else:
        sources = sys.argv[1:] if len(sys.argv) > 1 else ["krs", "biala_lista", "gus", "financials"]
        runners = {
            "krs": fetch_all_krs,
            "biala_lista": fetch_all_biala_lista,
            "gus": fetch_all_gus,
            "financials": fetch_krs_financials_instructions,
        }
        for source in sources:
            if source in runners:
                try:
                    runners[source]()
                except Exception as e:
                    print(f"FATAL {source}: {e}")
            else:
                print(f"Unknown source: {source}. Available: lookup <KRS>, lookup_nip <NIP>, {list(runners.keys())}")
