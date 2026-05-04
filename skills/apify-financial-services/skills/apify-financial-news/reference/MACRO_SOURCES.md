## Macro Economic Briefing Sources

For country-level economic context (daily/weekly macro overview), use these sources alongside news intelligence:

### Best Open-Access Macro Sources

| Source | Domain | Coverage | Frequency | Extraction | Notes |
|--------|--------|----------|-----------|------------|-------|
| **ING Think** | think.ing.com | CZ, PL, HU, SK, BG + EU | Daily | `rag-web-browser` (11K chars, excellent) | Best free CEE macro source. FX daily, rate decisions, country snaps |
| **IMF** | imf.org | All countries | Annual (Art. IV) + quarterly (WEO) | `rag-web-browser` (22K chars) | Article IV concluding statements fully extractable |
| **ECB** | ecb.europa.eu | Eurozone (SK, BG) + EU | Monthly (rates) + quarterly (projections) | `rag-web-browser` (7K–85K chars) | Already in Tier 1 |
| **EC Press Corner** | ec.europa.eu | EU-wide | Daily | REST API | Already in Tier 1 |

### Central Banks (direct URL extraction, not via Google News)

| Country | Institution | Best URL | Extraction | Notes |
|---------|-------------|----------|------------|-------|
| CZ | **ČNB** | `cnb.cz/en/monetary-policy/` | `rag-web-browser` (35K chars) | Cloudflare blocks GNews `site:` operator — use direct URL |
| PL | **NBP** | `nbp.pl/en/monetary-policy/` | `rag-web-browser` (1.2K chars — nav only) | JS-rendered; use press release URLs directly |
| HU | **MNB** | `mnb.hu/en/monetary-policy` | `rag-web-browser` (moderate) | FX tables + rate decisions |
| BG | **BNB** | `bnb.bg` | Via BTA news articles (11K) | BG joined eurozone Jan 2026 — monetary policy at ECB level |
| SK | **NBS** | `nbs.sk` | GNews indexed but noisy (FX sheets) | SK in eurozone — NBS implements ECB policy |

### Usage in Morning Briefing

When running morning briefing (v2), add a **Market Context** section:
1. Check `think.ing.com` for overnight CEE FX/rates commentary (query: `site:think.ing.com Czech OR Poland OR Hungary`)
2. Check `ecb.europa.eu` for any rate decisions or projections (especially around ECB meeting dates)
3. For specific country deep-dives, scrape the central bank URL directly

