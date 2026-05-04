---
name: apify-public-registries
description: Look up official company data from European public registries across 11 countries/regions (CZ, SK, PL, DE, UK, NL, RO, HR, SE + EU-level + ESG). Covers company registration, ownership, financial filings, VAT status, ESG data. Use when the user asks to "look up a company", "check registry", "find company info", "look up IČO/KRS/LEI/CRN", "company due diligence", "check VAT status", "find ownership structure", or needs official data from European registries. Reads tracked companies from data/companies.json. Some lookups use Python scripts (stdlib), some fall back to Apify actors for scraping-based registries.
---

# Public Company Registries — 11 Countries

Look up official company data from European public registries via Python scripts (direct REST API)
or Apify actor fallback (scraping when no API exists).

## Prerequisites

- Python 3 (scripts use stdlib — no pip dependencies for most countries)
- Apify access (only for DE, UK, PL financials, CZ justice.cz, RO fallback) — preferred: `apify` CLI (`npm install -g apify-cli && apify login`); fallback: Apify MCP connector (`call-actor` tool). CLI is faster and preferred when both are available.
- **NL**: `KVK_API_KEY` env var (register at developers.kvk.nl — see [REGISTRATION/NL.md](REGISTRATION/NL.md))
- **PL GUS**: `GUS_API_KEY` env var (email regon_bir@stat.gov.pl)
- **SE**: Bolagsverket requires registration (see [REGISTRATION/SE.md](REGISTRATION/SE.md))
- **HR**: Sudski registar requires OAuth registration (see [REGISTRATION/HR.md](REGISTRATION/HR.md))

`${CLAUDE_PLUGIN_ROOT}` is the plugin's root directory (where `.claude-plugin/` lives). It is resolved automatically by Claude Code when the plugin is installed, or set to the `--plugin-dir` path during development.

## Workflow checklist

Copy this and tick boxes as you progress:

```
Task Progress:
- [ ] Step 0: Verify prerequisites — run `python3 --version` (required); for Apify-dependent registries: try `apify --version && apify info`, or check for `call-actor` MCP tool; if neither, tell user to install apify CLI or Apify MCP connector
- [ ] Step 1: Identify country + identifier type (IČO/KRS/CUI/LEI/company name)
- [ ] Step 2: Run the lookup command per country table
- [ ] Step 3: Interpret results (key fields vary by source)
- [ ] Optional: Apify fallback for scraping-based registries
- [ ] Optional: Cross-reference with EU-level sources (GLEIF LEI, ESMA bonds, EBA)
```

## Quick Reference — Lookup by Country

All paths relative to `${CLAUDE_PLUGIN_ROOT}/skills/apify-public-registries/`.

| Country | Command | Identifier | Access |
|---|---|---|---|
| **CZ** | `python3 reference/scripts/CZ/fetch_all.py lookup <IČO>` | IČO (8-digit) | Free (ARES API) |
| **SK** | `python3 reference/scripts/SK/fetch_all.py lookup <IČO>` | IČO | Free (ORSR scraping) |
| **PL** | `python3 reference/scripts/PL/fetch_all.py lookup <KRS>` | KRS (10-digit, zero-padded) | Free (KRS API) |
| **PL** | `python3 reference/scripts/PL/fetch_all.py lookup_nip <NIP>` | NIP (10-digit) | Free (Biała Lista, 100/day) |
| **PL GUS** | (included in batch `fetch_all.py`) | NIP | **`GUS_API_KEY` REQUIRED** — without it, returns fake test data silently (see gotchas) |
| **DE** | `python3 reference/scripts/DE/fetch_all.py keyword <name>` | Company name | Apify (mcpc CLI) |
| **UK** | `python3 reference/scripts/UK/fetch_all.py search <name>` | Company name | Apify (mcpc CLI) |
| **NL** | `python3 reference/scripts/NL/fetch_all.py` | KVK number (configured) | API key (`KVK_API_KEY`) |
| **RO** | `python3 reference/scripts/RO/fetch_all.py lookup <CUI>` | CUI number | Free (ANAF — offline since 2026-03) |
| **HR** | Manual — see [REGISTRATION/HR.md](REGISTRATION/HR.md) | OIB / MBS | OAuth registration |
| **SE** | Manual — see [REGISTRATION/SE.md](REGISTRATION/SE.md) | Org.nr | Bolagsverket registration |
| **EU** | `python3 reference/scripts/EU/fetch_all.py lookup <name>` | Company name | Free (GLEIF + ESMA + TED) |
| **EU** | `python3 reference/scripts/EU/fetch_all.py lookup_lei <LEI>` | LEI (20-char) | Free (GLEIF) |
| **ESG** | `python3 reference/scripts/ESG/fetch_all.py lookup <country>` | Country name/ISO code | Free |

## By Data Type

| Need | Best source | Command |
|---|---|---|
| Basic profile (name, address, legal form) | CZ: ARES, SK: ORSR, PL: KRS, DE: Handelsregister, UK: Companies House | See country table above |
| Ownership / corporate tree | EU GLEIF | `EU/fetch_all.py lookup_lei <LEI>` |
| Financial filings (CZ) | Justice.cz sbírka listin (Apify fallback) | `CZ/fetch_all.py justice` |
| Financial filings (SK) | FinStat.sk | `SK/fetch_all.py finstat` |
| Financial filings (PL) | eKRS via Apify | `PL/fetch_all.py financials` |
| Bonds & instruments | ESMA FIRDS | `EU/fetch_all.py lookup <name>` |
| VAT / due diligence (CZ) | DPH register | Included in `CZ/fetch_all.py lookup` |
| VAT / due diligence (PL) | Biała Lista | `PL/fetch_all.py lookup_nip <NIP>` |
| Bank regulatory data | EBA Transparency CSVs (100MB+) | `EU/fetch_all.py eba` |
| ESG / emissions | Climate TRACE + EU ETS | `ESG/fetch_all.py lookup <country>` |
| Regulated entities (CZ) | ČNB bank list + OAM | `CZ/fetch_all.py cnb_banks` / `cnb_oam` |
| Public procurement | TED | `EU/fetch_all.py lookup <name>` |

## Step 1: Identify country + identifier

- Check `${CLAUDE_PLUGIN_ROOT}/data/companies.json` -> `identifiers.registry_ids` for existing IDs.
- If identifier unknown, start with **EU GLEIF by name** — returns LEI + registered-as numbers usable in country-specific lookups.

**Identifier types by country:**
- **CZ/SK**: IČO (8-digit)
- **PL**: KRS (10-digit zero-padded) or NIP (10-digit)
- **DE**: Company name keyword
- **UK**: Company name
- **NL**: KVK number (8-digit)
- **RO**: CUI (numeric)
- **HR**: OIB (11-digit) or MBS
- **SE**: Organisationsnummer (10-digit, e.g. 559124-6847)
- **EU**: LEI (20-char alphanumeric) or company name

## Step 2: Run lookup

Execute the command from the country table. Scripts are at:
`${CLAUDE_PLUGIN_ROOT}/skills/apify-public-registries/reference/scripts/<CC>/fetch_all.py`

**Example — look up a company in Czech ARES:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/apify-public-registries/reference/scripts/CZ/fetch_all.py lookup 25099345
```

**Example — find ownership chain via GLEIF:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/apify-public-registries/reference/scripts/EU/fetch_all.py lookup_lei 31570048XH84U51GGT05
```

**Example — look up InPost in KRS:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/apify-public-registries/reference/scripts/PL/fetch_all.py lookup 0000536554
```

**Batch fetch (all companies in a country):**
```bash
python3 reference/scripts/CZ/fetch_all.py          # all CZ sources (ares, dph, cnb_banks, cnb_oam, justice)
python3 reference/scripts/PL/fetch_all.py          # all PL sources (krs, biala_lista, gus, financials)
python3 reference/scripts/EU/fetch_all.py          # all EU sources except EBA (gleif, ted, esma, eurostat)
```

## Step 3: Interpret results

Key fields vary by source:

| Source | Key fields |
|---|---|
| **ARES** (CZ) | obchodniJmeno, dic, sidlo.textovaAdresa, czNace, datumVzniku, pravniForma |
| **DPH** (CZ) | nespolehlivyPlatce (unreliable payer flag), bank accounts |
| **GLEIF** (EU) | lei, legalName, jurisdiction, status, registeredAs, parent LEI + name |
| **KRS** (PL) | nazwa, nip, regon, kapital (share capital) |
| **Biała Lista** (PL) | statusVat, krs, regon, accountNumbers |
| **ORSR** (SK) | name, address, legal_form, share_capital, registration_date |
| **FinStat** (SK) | revenue, profit, employees, assets |
| **Handelsregister** (DE) | name, legal form, share capital, management, HRB number |
| **Companies House** (UK) | company number, SIC codes, directors, incorporation date |
| **ESMA FIRDS** (EU) | isin, lei, instrument name, cfi_code, status |
| **TED** (EU) | buyer-name, winner-name, total-value, procedure-type |
| **ANAF** (RO) | denumire, adresa, scpTVA (VAT payer flag), active status |

## Apify fallback

When no direct API exists, use Apify CLI with a specific actor or `apify/website-content-crawler`:

```bash
apify call apify/website-content-crawler \
  --input '{"startUrls":[{"url":"https://or.justice.cz/ias/ui/rejstrik-$firma?ico=25099345"}],"maxCrawlPages":1}'
```

**Apify-dependent registries:**

| Country | Registry | Actor | Trigger |
|---|---|---|---|
| DE | Handelsregister | `radeance/handelsregister-api` | `DE/fetch_all.py keyword <name>` |
| UK | Companies House | `dhrumil/company-house-scraper` | `UK/fetch_all.py search <name>` |
| PL | eKRS Financials | `minute_contest/poland-krs-financial-scraper` | `PL/fetch_all.py financials` |
| CZ | Justice.cz filings | `apify/website-content-crawler` | Direct via apify CLI |
| RO | ListaFirme.ro | `apify/website-content-crawler` | `RO/fetch_all.py listafirme` |
| SE | Allabolag.se | `apify/website-content-crawler` | Manual (residential proxy needed) |

Note: DE, UK, and RO scripts use `mcpc` CLI internally (not apify CLI).

## Dependencies

### Python stdlib only (no pip)
CZ (ares, dph, cnb_banks, cnb_oam, justice), SK (orsr, finstat), PL (krs, biala_lista, gus),
EU (gleif, esma, ted, eurostat), ESG (ets, climate_trace), RO (anaf)

### Requires Apify + APIFY_TOKEN
DE (handelsregister), UK (companies_house), PL (financials via eKRS),
CZ (justice.cz sbírka listin via scraping), RO (listafirme.ro)

### Requires API key registration
- **NL**: `KVK_API_KEY` — register at developers.kvk.nl ([REGISTRATION/NL.md](REGISTRATION/NL.md))
- **PL GUS**: `GUS_API_KEY` — email regon_bir@stat.gov.pl (test key `abcde12345abcde12345` exists but has no real data)
- **SE**: Bolagsverket — register at portal.api.bolagsverket.se ([REGISTRATION/SE.md](REGISTRATION/SE.md))
- **HR**: Sudski registar — register at sudreg-data.gov.hr, OAuth2 flow ([REGISTRATION/HR.md](REGISTRATION/HR.md))

## Critical gotchas

- **CZ ARES** is the best single starting point for Czech companies — aggregates data from multiple source registers.
- **EU GLEIF** is the best cross-country starting point — maps LEI to registered-as numbers usable in country lookups.
- **RO ANAF API is offline since March 2026** — lookup returns errors. Use listafirme.ro (Apify) as fallback.
- **SK ORSR uses HTML scraping** with windows-1250 encoding and regex parsing — fragile, may break if page layout changes.
- **SK FinStat** is also HTML scraping — may block automated access.
- **PL Biała Lista** has a hard rate limit: 100 queries/day (search method) or 5,000/day (check method).
- **PL GUS silently returns fake data** when `GUS_API_KEY` is unset — test server returns plausible-looking records (`ul. Test-Krucza`, `Kraków-Podgórze`) for any valid NIP. Production key required: email regon_bir@stat.gov.pl. Always inspect first GUS record to confirm prod vs test.
- **DE + UK scripts use mcpc CLI** (not apify CLI) — require authenticated `@apify` session.
- **UK Companies House has a free API** at api.company-information.service.gov.uk, but the script uses Apify scraping instead.
- **CZ Justice.cz bulk datasets** are 13GB+ XML/CSV. The CKAN API returns a dataset list, not per-company data.
- **CZ ČNB OAM** is only relevant for emitents (listed companies, banks) — uses Oracle BI XML export.
- **ESG data is country-level**, not company-level — useful only as contextual benchmark.
- **ESAP** (centralized EU ESG/financial database with API) launches CSRD data January 2028.
- **EBA Transparency CSVs** are 100MB+ each — run `EU/fetch_all.py eba` separately, not as part of normal batch.
- **TED** has low value — most portfolio companies are private. Winner-name only in eForms notices (2024+).
- **Batch mode** (`fetch_all.py` without arguments) reads `lookup_targets.json` from the script's directory — these are per-country ID→name mappings, NOT copies of `data/companies.json`. For single-company lookups, pass the identifier directly.

## Reference

- [data/registries.json](data/registries.json) — machine-readable: 11 countries, 27 registry entries
- [REGISTRATION/HR.md](REGISTRATION/HR.md), [REGISTRATION/NL.md](REGISTRATION/NL.md), [REGISTRATION/SE.md](REGISTRATION/SE.md) — per-country API access guides
- [reference/european-company-data-institutions.md](reference/european-company-data-institutions.md) — full narrative catalog (413 lines, CZ + PL + EU institutions)
- reference/scripts/{CZ,DE,ESG,EU,NL,PL,RO,SK,UK}/fetch_all.py — per-country lookup scripts
