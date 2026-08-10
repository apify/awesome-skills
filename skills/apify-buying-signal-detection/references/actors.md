# Actor catalog

Full routing table for every signal × geo combination. `setup_apify_tasks.py`
reads this list conceptually — the actual selection lives in the `PICK` blocks
below, which the setup script mirrors in code. When adding an Actor, update
both.

## Table of contents

- [Jobs signals](#jobs-signals)
- [Funding signals](#funding-signals)
- [LinkedIn content signals](#linkedin-content-signals)
- [How the aggregator normalizes across Actors](#how-the-aggregator-normalizes-across-actors)

## Jobs signals

Job postings are a strong hiring signal — a company posting 3+ AE roles in a
month is expanding sales. The trick is **geo coverage**: LinkedIn is global but
gets rate-limited; job boards are hyper-regional. Always fan out to a global
Actor + the regional Actor(s) for the campaign's geo list.

Every Actor in the routing table below is **pay-per-event (PPE)** — no monthly rental,
no upfront fees, you pay only for results returned. Rental Actors are deliberately
excluded (see [Rejected: rental Actors](#rejected-rental-actors) at the bottom).

| Actor ID | Pricing (Free tier) | Best for | Cookies? |
|---|---|---|---|
| `lntb/linkedin-jobs-scraper---multiple-titles-locations-in-one` | PPE, $1/1k results | Global LinkedIn jobs — **accepts arrays of titles + locations in one call** | No |
| `curious_coder/linkedin-jobs-scraper` | PPE, $2/1k results | Global LinkedIn jobs — richer per-posting detail (description, apply URL) | Yes |
| `johnvc/Google-Jobs-Scraper` | PPE | Anywhere Google Jobs aggregates results (broadest fallback). Single-string `query`, lowercase `country` code (`us`/`uk`/`ca`/`de`/`fr`/`au`/`jp`/`in`/`br`/`mx`) | No |
| `borderline/indeed-scraper` | PPE | US / UK / IN / CA — Indeed's core markets. Single-string `query`, lowercase `country` (`us`/`uk`/`ca`/`in`) | No |
| `memo23/stepstone-search-cheerio-ppr` | PPE | DE / AT / BE — Stepstone dominates German-language markets | No |
| `blackfalcondata/seek-scraper` | PPE | AU / NZ — Seek dominates ANZ | No |
| `dltik/francetravail-scraper` | PPE | FR — France Travail (ex Pôle Emploi) — official French labor listings | No |

### PICK — jobs

```
Always include:  lntb/linkedin-jobs-scraper---multiple-titles-locations-in-one
                 + johnvc/Google-Jobs-Scraper
If any geo is US, UK, IN, CA:   add borderline/indeed-scraper
If any geo is DE, AT, BE:       add memo23/stepstone-search-cheerio-ppr
If any geo is AU, NZ:           add blackfalcondata/seek-scraper
If any geo is FR:               add dltik/francetravail-scraper
```

Use `curious_coder/linkedin-jobs-scraper` **in addition to** `lntb/...` only when
the campaign needs per-posting detail (job description text, application URL) —
e.g. for buyer research beyond mere headcount signals. It's slower, costs 2× per
result, and requires a `LI_AT` cookie in the Actor input.

**Slug case matters.** `johnvc/Google-Jobs-Scraper` is capitalized as shown; the
lowercase variant is a different (nonexistent) actor and the API returns 400 on
task creation.

**Country codes for `johnvc/Google-Jobs-Scraper` and `borderline/indeed-scraper`
are lowercase, and `GB` → `uk`.** The setup script handles this mapping.

## Funding signals

Funding events fire a short-lived buying window (typically 60–90 days after
announcement — cash is fresh, team is scaling, tooling budget is open).

| Actor ID | Pricing | Best for |
|---|---|---|
| `nexgendata/startup-funding-tracker` | PPE | Global default. Broad coverage, weekly refresh. |
| `complex_intricate_networks/fundraising-and-startup-funding-scraper` | PPE | Secondary global — different upstream sources; dedup catches overlap. |
| `signalbase/signalbase-api` | PPE | API-style Actor pulling from Signalbase's curated feed. Fewer false positives; smaller volume. |
| `memo23/crunchbase-scraper` | PPE | Crunchbase authoritative deals — best for ground-truth stage / amount / lead investor. |
| `johnvc/crunchbase-company-api` | PPE | Enrichment — given a company name, pull firmographic + historical funding rounds. Not a discovery Actor. |
| `advantageous_subcontra/maddyness-french-startup-fundraising-database` | PPE | FR-only, Maddyness feed. Highest coverage on French deals. |

### PICK — funding

```
Always include:  nexgendata/startup-funding-tracker
                 + memo23/crunchbase-scraper
Add for global depth:  complex_intricate_networks/fundraising-and-startup-funding-scraper
Add for curated volume:  signalbase/signalbase-api
If any geo is FR:  add advantageous_subcontra/maddyness-french-startup-fundraising-database
```

`johnvc/crunchbase-company-api` is intentionally **not** in the pick list — it's
an enrichment Actor called on-demand from `aggregate.py` when a row surfaces
without a stage/amount and the user wants that data filled in. Don't schedule it
in the weekly run.

## LinkedIn content signals

The noisiest signal type by design. Companies (and their execs) posting about
hiring, tool pain, or scaling are *inspiration* — a starting point for research,
not a qualified lead. Filter aggressively via `min_reactions` and human review.

| Actor ID | Pricing | Best for | Cookies? |
|---|---|---|---|
| `harvestapi/linkedin-post-search` | PPE, $2/1k posts | **Primary** — no cookies, well-adopted | No |
| `harvestapi/linkedin-post-comments` | PPE | Deep engagement — pull comment threads on a specific post URL | No |
| `harvestapi/linkedin-post-reactions` | PPE | Deep engagement — pull who reacted to a specific post URL | No |

### PICK — LinkedIn content

```
Always include:  harvestapi/linkedin-post-search
```

For deeper engagement analysis (mining reply chains for buying-intent quotes,
identifying who engaged with a competitor's post), chain
`harvestapi/linkedin-post-comments` or `harvestapi/linkedin-post-reactions` on
the URLs returned by the primary search. Both are PPE, no cookies required.

### LinkedIn search phrase design

The Actor takes free-form `keywords`. Broad terms (`sales`, `hiring`) return
mostly noise. Effective phrases fall into three patterns:

1. **Hiring-scale-out phrases** — `"growing our sales team"`,
   `"we're hiring account executives"`, `"scaling from X to Y"`.
2. **Pain-point complaints** — `"cold email is broken"`, `"outbound is dead"`,
   `"our CRM is a mess"`. Anti-competitor complaints for a specific tool are
   gold: `"leaving <competitor>"`, `"switching from <competitor>"`.
3. **Milestone announcements** — `"just closed our series a"`,
   `"launched today"`, `"acquired by"`.

Combine 3–5 per campaign; the aggregator merges results and dedupes by URL.

## How the aggregator normalizes across Actors

Every Actor's schema is slightly different — `aggregate.py` maps each into the
common `leads.csv` row shape ([`csv-schema.md`](./csv-schema.md)). The mapping
table:

| CSV column | Job Actors | Funding Actors | LinkedIn content Actors |
|---|---|---|---|
| `company` | `companyName` / `company` / `company.name` | `companyName` / `startupName` | Post author's `authorName` (or nested `author.name`) when it's a company page; else the author's employer |
| `domain` | `companyDomain` / `companyWebsite` when present | `companyDomain` / `companyUrl` / `companyWebsite` | `authorCompanyDomain` / `author.company.domain` — often empty for personal posts |
| `signal_type` | `"jobs"` | `"funding"` | `"linkedin_content"` |
| `signal_detail` | `f"Job: {title}"` | `f"Raised {amount} {stage} led by {lead_investor}"` | `f"Post: '{first_120_chars}'"` |
| `signal_source_actor` | Actor ID that produced the row | ditto | ditto |
| `signal_date` | `postedDate` / `datePosted` | `announcementDate` / `roundDate` | `postedAt` |
| `evidence_url` | `jobUrl` / `applyUrl` / `postingUrl` | `sourceUrl` / `articleUrl` | `postUrl` |
| `geo` | `locationCountry` / derived from `location` string | `hqCountry` / `location` | Post `author.location` when present |

When an Actor returns a field the mapping table doesn't cover, add a mapping
line in `aggregate.py` and record the new field name here.

## Rejected: rental Actors

Every Actor below is functional, but its pricing model is
`FLAT_PRICE_PER_MONTH` (rental). A weekly buying-signal pipeline can be run for
$5-20/month total on PPE Actors — adding even one rental Actor at $20-30/month
dominates the budget and eliminates the free-tier viability of the pipeline. If
you have a specific reason to use one anyway (deeper feature set, higher volume
cap, no per-event overhead at scale), swap it in your own campaign; do not add
it to the default routing table.

| Actor ID | Rental fee | Trial | Replaced by |
|---|---|---|---|
| `bebity/linkedin-jobs-scraper` | $29.99/mo | 72h | `lntb/linkedin-jobs-scraper---multiple-titles-locations-in-one` |
| `curious_coder/indeed-scraper` | $20/mo | 24h | `borderline/indeed-scraper` |
| `tech_gear/company-funding-details` | $19/mo (**FULL_PERMISSIONS**) | 2h | `johnvc/crunchbase-company-api` |
| `curious_coder/linkedin-post-search-scraper` | $30/mo | 72h | `harvestapi/linkedin-post-search` (already the primary) |

`tech_gear/company-funding-details` also carries `actorPermissionLevel:
FULL_PERMISSIONS`, meaning it requests broader access to the caller's account
than a standard sandboxed Actor. Prefer the PPE Crunchbase alternative on both
grounds.
