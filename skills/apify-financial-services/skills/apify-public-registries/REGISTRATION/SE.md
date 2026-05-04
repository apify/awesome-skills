# SE — Bolagsverket (Swedish Companies Registration Office) API registrace

## PPF firmy v SE
- Viaplay Group AB (publ) — Organisationsnummer 559124-6847

## Registrace API

### Free datasets (od února 2025, EU High-Value Datasets regulace)

1. Jdi na https://portal.api.bolagsverket.se/devportal
2. Vyber "Värdefulla datamängder" (Valuable datasets) — tyto jsou FREE
3. Data obsahují: základní údaje o firmách, adresy, právní formy

### Plný API přístup

1. Jdi na https://bolagsverket.se/apierochoppnadata
2. Kontaktuj Bolagsverket pro uzavření smlouvy (avtal)
3. Po podpisu dostaneš přístup k:
   - Företagsinformation API v3 — detailní firemní data
   - Årsredovisningar API — výroční zprávy (iXBRL formát)
   - UBO API (od 2025) — beneficial ownership

## Endpointy (free)

```
Base URL: https://api.bolagsverket.se/foretagsinformation-vardefulladatamangder/v1/

GET /organisationer/{organisationsnummer}  — detail firmy
```

## Formát
- REST/JSON
- Swagger dokumentace na developer portálu
- Response time <200ms
- RSS feed pro API updates

## Alternativa (scraping)
Allabolag.se má detailní firemní data, ale je chráněn Cloudflare.
Použij Apify website-content-crawler s residential proxy.

## Po registraci
```bash
export SE_BOLAGSVERKET_API_KEY=<key>
```
Pak spusť `fetch_all.py`.
