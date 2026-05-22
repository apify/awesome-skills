# `data/companies.json` — schema & workflow

Unified portfolio dataset. Single source of truth for every Apify Actor in this repo
(news, social, registries, OSINT). Merged from 13 source files (one news-intel base + one
ppf-ma fallback + 11 country-/topic-specific registry files in `~/Projects/cowork/local/*`).

---

## 1. Top-level structure

```jsonc
{
  "_metadata":  { ... },           // version, source provenance, actor field mapping, data quality notes, upstream issues
  "portfolio":  [ ...30 entries ], // portfolio companies (public + private)
  "group":      { ... },           // group-level monitoring entry (M&A, leadership). Not in portfolio array.
  "prospects":  []                 // reserved for future M&A targets, currently empty
}
```

| Key           | Type   | Purpose                                                                              |
| ------------- | ------ | ------------------------------------------------------------------------------------ |
| `_metadata`   | object | Version, last-updated date, list of source repos, schema pointer, actor-field map.   |
| `portfolio`   | array  | Portfolio companies. Order is preserved from source (chronological by `monitoring_since`). |
| `group`       | object | Single group-level entry. Same schema as portfolio entries but kept top-level — it's an aggregator, not an investee. |
| `prospects`   | array  | Empty placeholder for future acquisition targets / scouting list.                |

### `_metadata` sub-fields

| Field                  | Type   | Description                                                                                       |
| ---------------------- | ------ | ------------------------------------------------------------------------------------------------- |
| `version`              | string | Semantic version of this file (`1.0`). Bump on schema changes.                                    |
| `last_updated`         | date   | ISO-8601 date of last edit (`YYYY-MM-DD`).                                                        |
| `source_repos`         | array  | Provenance — every source path with its date, in merge-priority order (news-intel wins).          |
| `schema`               | string | Pointer to this README.                                                                           |
| `actor_field_mapping`  | object | Maps each scrapable field → Apify Actor(s) that consume it. See section 2.                        |
| `data_quality_notes`   | array  | Verification status per identifier type (IČO verified, Glassdoor verified, etc.).                 |
| `upstream_issues`      | array  | Known problems in source files (e.g. misclassified entries, placeholder LEIs) — informational, doesn't affect this file. |

---

## 2. Portfolio entry schema

```jsonc
{
  "id":               "ppf-banka",          // string, slug (lowercase ASCII, hyphens). Stable key.
  "name":             "PPF banka",          // string, human-readable display name.
  "country":          "CZ",                 // string, ISO-3166 alpha-2 (HQ / primary registration).
  "type":             "private",            // string, "public" | "private".
  "identifiers":      { ... },              // object, see §2.1
  "sector":           "Financial Services", // string, free-text industry tag.
  "stake":            "100%",               // string, free-text — "100%", "~29%", "via e& PPF Telecom", etc.
  "monitoring_since": "2026-03-01",         // ISO date or null. When monitoring started.
  "queries":          { ... },              // object, see §2.2
  "trustpilot_urls":  [],                   // array of strings (no scheme — "trustpilot.com/review/...")
  "google_play_ids":  [],                   // array of Google Play package IDs ("cz.airbank.android")
  "app_store_ids":    [],                   // array of Apple App Store numeric IDs (as strings)
  "linkedin_hashtags":[],                   // array, with leading "#" ("#InPost")
  "instagram_hashtags":[],                  // array, no leading "#"
  "instagram_profile":"airbank.cz",         // string handle, or null
  "notes":            "..."                 // free-text — context, verification provenance, gotchas.
}
```

### 2.1 `identifiers` sub-fields

The `identifiers` object holds **only globally-namespaced fields**. Country-specific
registry numbers (CZ IČO/DIČ, NL KVK, PL KRS, UK CRN, …) live exclusively under
`identifiers.registry_ids` — see §2.3. There is **no top-level `ico` or `dic`**.

| Field                    | Type             | Source / format                                                                |
| ------------------------ | ---------------- | ------------------------------------------------------------------------------ |
| `lei`                    | string \| null   | 20-char ISO 17442 Legal Entity Identifier (GLEIF).                             |
| `isin`                   | string \| null   | 12-char ISO 6166 security identifier.                                          |
| `ticker`                 | string \| null   | Primary exchange ticker w/ suffix (e.g. `INPST.AS`, `MONET.PR`, `PSM.DE`).     |
| `ticker_us`              | string \| null   | OTC / ADR ticker for US-listed equivalent (e.g. `INPOY`, `PBSFF`).             |
| `sec_cik`                | string \| null   | 10-digit zero-padded SEC Central Index Key. Currently only Autolus.            |
| `seeking_alpha_ticker`   | string \| null   | Ticker as recognized by seekingalpha.com.                                      |
| `glassdoor_id`           | integer \| null  | Numeric Glassdoor company ID.                                                  |
| `glassdoor_search`       | string \| null   | Display name to use for Glassdoor name-based search.                           |
| `linkedin_url`           | string \| null   | Full URL of LinkedIn company page.                                             |
| `ir_url`                 | string \| null   | Investor Relations / press-release page (for change-monitor).                  |
| `registry_ids`           | object           | Map of country-/registry-specific IDs. See §2.3.                               |

**Empty-vs-null convention:** scalar identifiers use `null` when unknown. The `registry_ids`
map only contains keys with real values — never pad with `null`. An entity with no known
registry IDs has `"registry_ids": {}`.

### 2.2 `queries` sub-fields (Apify Actor inputs)

Each query bucket is a list of search strings. Empty arrays are intentional — they mean
"this company has no presence on this platform, verified, do not scrape".

| Field          | Consumed by Actor (allowed per SKILL.md)                                         |
| -------------- | -------------------------------------------------------------------------------- |
| `gnews_en`     | `data_xplorer/google-news-scraper-fast` (apify-financial-news)                   |
| `gnews_cz`     | `data_xplorer/google-news-scraper-fast` with region `CZ:cs`                      |
| `bloomberg`    | `jamie_tran/bloomberg-article-scraper` (discovery via google-news-scraper-fast)   |
| `twitter`      | `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest` (apify-financial-osint) |
| `reddit`       | `fatihtahta/reddit-scraper-search-fast` (apify-financial-osint)                  |
| `youtube`      | `topaz_sharingan/Youtube-Transcript-Scraper-1`                                   |
| `linkedin`     | `harvestapi/linkedin-post-search` (keyword search across all LI posts)           |
| `tender`       | `stagsz/ted-tender-crawler` (TED EU public procurement)                          |

### 2.3 `registry_ids` — naming convention

Keys follow the pattern **`{COUNTRY}_{TYPE}`** where:

- `{COUNTRY}` = ISO-3166 alpha-2 of the registry jurisdiction.
- `{TYPE}` = canonical short code of the identifier type in that jurisdiction.

| Key         | Country    | Identifier             | Authority                            |
| ----------- | ---------- | ---------------------- | ------------------------------------ |
| `CZ_ICO`    | Czechia    | IČO (Identifikační číslo osoby) | or.justice.cz / ARES        |
| `CZ_DIC`    | Czechia    | DIČ (VAT)              | Finanční správa                      |
| `SK_ICO`    | Slovakia   | IČO                    | orsr.sk / FinStat                    |
| `PL_KRS`    | Poland     | KRS (court register)   | Krajowy Rejestr Sądowy               |
| `PL_NIP`    | Poland     | NIP (VAT)              | Ministerstwo Finansów                |
| `PL_REGON`  | Poland     | REGON (statistical)    | GUS                                  |
| `NL_KVK`    | Netherlands| KVK / Handelsregister  | Kamer van Koophandel                 |
| `DE_HRB`    | Germany    | HRB (commercial register, court-prefixed e.g. `HRB-M-241023`) | Handelsregister |
| `UK_CRN`    | UK         | Company Number         | Companies House                      |
| `UK_CRN_PARENT` | UK     | Company Number of immediate UK parent (when relevant) | Companies House           |
| `RO_CUI`    | Romania    | CUI (fiscal code)      | ONRC                                 |
| `SE_ORG`    | Sweden     | Organisationsnummer    | Bolagsverket                         |
| `HR_MBS`    | Croatia    | MBS (court register)   | Sudski registar                      |
| `HR_OIB`    | Croatia    | OIB (personal/company ID) | Porezna uprava                    |

Add new keys following the same pattern. Skip the `registry_ids` entry for any country
where you don't have a confirmed value — never invent placeholders.

---

## 3. Add-company workflow

When a new company is added to the portfolio (or a `prospects` candidate gets promoted),
follow these three steps.

### Step 1 — Register identifiers

Run the **`apify-public-registries`** skill (see `skills/apify-public-registries/SKILL.md`) for the company's
HQ country to fetch the canonical registry ID, then enrich:

| Source                              | Fields populated                                              |
| ----------------------------------- | ------------------------------------------------------------- |
| `apify-public-registries` (per HQ)  | `identifiers.registry_ids.{COUNTRY}_{TYPE}` (e.g. `CZ_ICO`, `NL_KVK`) |
| GLEIF API (free, `api.gleif.org`)   | `identifiers.lei`                                             |
| Stock exchange / IR page            | `identifiers.ticker`, `ticker_us`, `isin`                     |
| SEC EDGAR (US-listed only)          | `identifiers.sec_cik`                                         |
| seekingalpha.com                    | `identifiers.seeking_alpha_ticker`                            |
| **Manual lookup** (one-off)         | `glassdoor_id` (URL inspect), `linkedin_url`, `ir_url`        |
| App stores (manual or scraper)      | `google_play_ids`, `app_store_ids`                            |
| Trustpilot                          | `trustpilot_urls`                                             |

Slugify the company name into `id`: lowercase, ASCII transliteration of diacritics,
hyphenate spaces and special chars. Examples:

- `"PPF banka a.s."` → `"ppf-banka"`
- `"MONETA Money Bank"` → `"moneta-money-bank"`
- `"e& PPF Telecom Group"` → `"eand-ppf-telecom-group"`
- `"CME (Central European Media Enterprises)"` → `"cme"`

### Step 2 — Write queries

For each `queries.*` bucket, write **2–4 distinct search strings**. Always include the
canonical company name + 1–2 brand variants (CZ name, ticker, abbreviation).

| Bucket        | Always? | Rule                                                                    |
| ------------- | ------- | ----------------------------------------------------------------------- |
| `gnews_en`    | yes     | English-press monitoring.                                                |
| `gnews_cz`    | yes     | Czech-press monitoring (use `[]` if the company has zero CZ exposure).  |
| `bloomberg`   | yes     | Single canonical name usually enough.                                    |
| `twitter`     | if active on X | Skip if company has no X presence (use `[]`).                    |
| `reddit`      | if consumer-facing | B2B fintech / biotech often skip.                            |
| `youtube`     | if relevant | Earnings calls + investor day talks. Skip otherwise.                |
| `linkedin`    | yes     | All 30 entries currently have queries (whitelisting drives `harvestapi`).|
| `tender`      | if EU public-procurement exposure | Telecom, transport, infra mostly.            |

After writing each query bucket, cross-reference `_metadata.actor_field_mapping` to
confirm which Actor will consume it — that determines query syntax conventions
(e.g. Twitter accepts `$TICKER`, GNews does not).

### Step 3 — Validate

```sh
# 3a. Sanity-check the entry exists and parses
jq '.portfolio[] | select(.id=="<new-id>")' data/companies.json

# 3b. Test scrape (5 articles, EN news)
# Run via apify-financial-news skill, limit=5, query bucket=gnews_en

# 3c. Confirm: scraped article titles mention the company. If you get drift
# (e.g. "Apple Bank" results when querying "Air Bank"), tighten queries
# (add country qualifier, exact-phrase quotes, or use Bloomberg-style canonical name).
```

If validation fails, iterate on Step 2. Do **not** commit until at least `gnews_en` and
`gnews_cz` (when applicable) return on-topic results.

---

## 4. Data quality notes

(adapted from news-intel v3.0 `_metadata.data_quality_notes`)

- IČO: verified via or.justice.cz / ARES (`CZ_ICO` key in `identifiers.registry_ids`).
- Glassdoor IDs: verified for companies with employer profiles.
- LEI: verified via GLEIF lookup.
- SEC CIK: only Autolus actively files with SEC.
- Seeking Alpha: verified tickers for publicly traded companies.
- Trustpilot: verified URLs for consumer-facing brands.
- App IDs: verified for companies with consumer apps. B2B companies have none.
- IR URLs: verified for public companies + group-level entry.
- Empty arrays = intentional: company has no presence on that platform (verified, not missing data).
- LinkedIn queries: all portfolio companies have queries for `harvestapi/linkedin-post-search`.
- Instagram hashtags: B2C + consumer-facing brands. B2B/biotech = empty (verified no IG presence).
- Instagram profiles: best-effort handles. Verify via `apify/instagram-profile-scraper` before bulk scraping.

---

## 5. Editing rules

1. **News-intel wins on conflicts.** When you see a value disagreement between sources, the news-intel snapshot (newest, v3.0) is canonical.
2. **Never invent identifiers.** Every IČO, KVK, LEI, ISIN must come from a verified registry source. Leave fields `null` if unverified.
3. **Preserve order.** Append new portfolio entries to the end (chronological by `monitoring_since`). Don't reorder existing entries.
4. **Bump `_metadata.version`** on any schema change (new field, removed field, type change). Update `_metadata.last_updated` on every commit that touches data.
5. **Country code = HQ jurisdiction**, not legal-entity registration country. `Home Credit` is `NL` (parent = Home Credit N.V.) even though primary IČO is the CZ subsidiary.

---

## 6. Upstream issues

Source files in `~/Projects/cowork/local/*` and `~/Projects/cowork/portfolio-research/` have
known problems. They are **fixed in this file** but flagged in `_metadata.upstream_issues` so
they can be addressed in their respective repos.

| # | Source                      | Issue                                                                                                  | Fix in this file                                                |
| - | --------------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| 1 | `local/CZ`                  | MONETA Money Bank classified under `competitors.banking` instead of `portfolio` (it's a portfolio company, ~29% via Tanemo a.s.). | Treated as portfolio per news-intel.                            |
| 2 | `local/ESG`                 | `air_bank` and `ppf_banka` LEI placeholders (`TODO_lookup_LEI`).                                       | Resolved via GLEIF: Air Bank `31570010000000049662`, PPF banka `31570010000000036567`. |
| 3 | `local/UK`                  | ClearBank entry was a placeholder (search URL only, no CRN).                                           | Resolved via UK Companies House: `UK_CRN` 09736376 (operating), `UK_CRN_PARENT` 14254435 (group). |
| 4 | news-intel v3.0             | `_metadata.data_quality_notes` claimed "16 Czech IČO verified" — actual 14 portfolio + 1 group = 15.   | Note adjusted; running count maintained going forward.          |
| 5 | news-intel v3.0             | Sazka/Allwyn included as portfolio (`stake: "via KKCG partnership"`). No documented direct stake in portfolio — KKCG (Karel Komárek) owns Allwyn. | Removed from portfolio.                                         |
| 6 | News-intel + ppf-ma         | CME entry didn't carry RO/HR subsidiary registry IDs (PRO TV, Nova TV).                                | CME `registry_ids` enriched: `RO_CUI` 2835636, `HR_MBS` 080222668, `HR_OIB` 75399377119. |
| 7 | News-intel + local/CZ       | `dic` (CZ DIČ) lived at top-level `identifiers.dic` for 12 entries but was missing from `registry_ids.CZ_DIC`; `ico` had partial duplication too. | Top-level `ico`/`dic` removed entirely; values consolidated under `registry_ids.CZ_ICO` / `CZ_DIC` (single source of truth). |
