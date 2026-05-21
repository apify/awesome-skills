# Apify Actor Usage: `apify/link-prospecting-tool`

Reference for how this skill calls the link-prospecting Actor: full input schema, recommended payload, dataset structure, sub-Actor access, billing, and the timeout gotcha.

## Actor at a glance

- **Actor ID**: `apify/link-prospecting-tool`
- **Apify Store page**: https://apify.com/apify/link-prospecting-tool
- **What it does**: Runs each query against Google Search, ChatGPT Search, Perplexity, and Google AI Mode / AI Overviews; filters out the user's own and competitor domains; crawls each remaining source page to detect brand mentions and backlinks; enriches the domains that don't already link to the user with contact details; and optionally identifies article authors via AI.
- **Live latest build at time of skill authoring**: 0.0.5

## Required vs optional inputs

| Field | Type | Required | Default | What it does |
|---|---|---|---|---|
| `queries` | string (newline-separated) | **Yes** | — | One search query per line. Join keywords with `\n` before passing. |
| `brand` | string | **Yes** | — | The user's brand name. Used case-insensitively to detect mentions and backlinks on crawled pages. The Actor will not start without this. |
| `organicResult` | integer | No | 10 | Number of Google organic SERP results per query. Asking for more than 10 slows the run and raises Google Search Scraper cost ($4.5 per 1k results). Max 500. |
| `enableChatGpt` | boolean | No | true | Include ChatGPT Search results. Adds Google Search Scraper cost per result. |
| `enableGemini` | boolean | No | true | Include Google Gemini results. Adds Google Search Scraper cost per result. |
| `enableCopilot` | boolean | No | true | Include Microsoft Copilot (Bing AI) results. Adds Google Search Scraper cost per result. |
| `enablePerplexity` | boolean | No | true | Include Perplexity Sonar results. Adds Google Search Scraper cost per result. |
| `enableAiMode` | boolean | No | true | Include Google AI Mode results. Adds Google Search Scraper cost per result. |
| `enableAiOverviews` | boolean | No | true | Process Google AI Overviews surfaced in the SERP. **No extra cost** — parsed from the SERP already fetched for organic results. |
| `enableEmailVerification` | boolean | No | true | Verify every email returned by the Contact Details Scraper sub-Actor. Adds Email Verifier sub-Actor cost per email (typically much cheaper than the other sub-Actors). Each lead gets an `email_verification` field with one of: `verified`, `catch-all`, `risky`, `invalid`, `unknown`. |
| `ownDomains` | string[] | No | [] | The user's own domains, skipped during source analysis. |
| `competitorDomains` | string[] | No | [] | Competitor domains, skipped during source analysis. |
| `ignoreDomains` | string[] | No | [] | Other domains to exclude. The skill defaults to the standard prefill list (UGC + giants) — see "Recommended payload" below. |
| `maxContactsPerDomain` | integer | No | 1 | Max contacts per source domain (range 1-10). The skill defaults to 3. |
| `includeMention` | boolean | No | true | When true, sources that mention the brand without linking are also routed to the contact-enrichment step. |
| `department` | string[] (enum) | No | `["marketing","c_suite"]` | Departments to target for contact enrichment. Valid values: `c_suite`, `engineering_technical`, `product`, `design`, `finance`, `education`, `human_resources`, `information_technology`, `legal`, `marketing`, `medical_health`, `operations`, `sales`, `consulting`. |
| `searchAuthorName` | boolean | No | false | Identify the article author via AI Web Scraper sub-Actor ($25/1k sources). The skill enables this by default for personalisation. |

## Recommended payload for this skill

```json
{
  "queries": "<keyword 1>\n<keyword 2>",
  "brand": "<user's brand name>",
  "ownDomains": ["<user-domain.com>"],
  "competitorDomains": [],
  "ignoreDomains": [
    "wikipedia.org", "github.com", "stackoverflow.com", "stackexchange.com",
    "reddit.com", "quora.com", "youtube.com", "twitter.com", "x.com",
    "linkedin.com", "facebook.com", "medium.com", "archive.org",
    "chromewebstore.google.com", "addons.mozilla.org", "apps.apple.com",
    "play.google.com", "microsoftedge.microsoft.com", "marketplace.visualstudio.com"
  ],
  "organicResult": 10,
  "maxContactsPerDomain": 3,
  "department": ["marketing"],
  "searchAuthorName": true,
  "includeMention": true,
  "enableChatGpt": true,
  "enableGemini": true,
  "enableCopilot": true,
  "enablePerplexity": true,
  "enableAiMode": true,
  "enableAiOverviews": true,
  "enableEmailVerification": true
}
```

Override `department` only if the user has a specific outreach angle (e.g., add `sales` if they want BD-style partnerships). Override the LLM-source booleans (`enableChatGpt`, `enableGemini`, `enableCopilot`, `enablePerplexity`, `enableAiMode`) only to cut cost in tight budgets. `enableAiOverviews` is free — keep on. `enableEmailVerification` is recommended on; turn off only when verification quota is constrained or for cost-tight smoke tests.

## Timeout gotcha (critical)

The Actor's own run-level `timeoutSecs` defaults to 60000 (~16 hours) — that is fine.

The trap is the **API client wait timeout** — how long the calling code polls for completion before giving up. Apify's JS client and most lightweight runners default to a few minutes. The link-prospecting Actor typically runs 5-15 minutes per query, much longer for big keyword lists, and 18 of 24 recent public runs ended in `TIMED-OUT` status with default polling.

In this skill, `scripts/run_actor.js` exposes `--timeout` (in seconds) for the client-side wait, not the Actor's runtime. Always pass at least `--timeout 900`. Raise to 1800 or 3600 for runs with more than three queries.

## Datasets produced by one run

Every run emits one **default dataset** plus several others accessible from the run's Storage tab:

| Dataset | What it contains |
|---|---|
| Default (All leads) | One row per enriched contact. Split into three batches by the Actor — one contact per domain per batch. |
| Mentions | One row per source URL. Records which engines surfaced it and whether the brand was mentioned / backlinked. |
| Domains with leads | Distinct list of domains that yielded a contact. Useful to feed into the next run's `competitorDomains` after a successful outreach round. |
| Author list | One row per source URL with `searchAuthorName: true`. Contains author name and (when discoverable) email. |
| Sub-Actor results | Index of sub-runs (Google Search Scraper, Website Content Crawler, Contact Details Scraper, AI Web Scraper). Each entry links to its own dataset and run page. |

### All leads row shape (from Actor README)

```json
{
  "firstName": "first name",
  "lastName": "last name",
  "linkedinProfile": "http://www.linkedin.com/in/fullName",
  "email": "firstName@example.com",
  "email_verification": "verified",
  "mobileNumber": null,
  "jobTitle": "SEO specialist",
  "industry": null,
  "city": "Prague",
  "country": "Czechia",
  "companyName": "example",
  "companyWebsite": "example.com",
  "companySize": null,
  "companyLinkedin": "http://www.linkedin.com/company/example",
  "companyCity": "Prague",
  "departments": ["marketing"],
  "seniority": "vp",
  "twitter": null,
  "domain": "example.com",
  "source_url": [],
  "brand_mentioned": false
}
```

The `email_verification` field is only populated when `enableEmailVerification: true` ran for the run. Possible values: `verified` (deliverable to a real inbox), `catch-all` (domain accepts everything — uncertain), `risky` (role-based, free-mail, or other low-confidence pattern), `invalid` (no MX / bounces / known bad), `unknown` (verifier didn't return a determination). If verification didn't run, the field is absent and the skill treats it as `-`.

### Mentions row shape

```json
{
  "url": "https://www.example.com/article",
  "domain": "https://www.example.com",
  "brand_mentioned_in_source": true,
  "backlink_in_source": false,
  "Perplexity_mention": false,
  "ChatGPT_mention": true,
  "Gemini_mention": false,
  "Copilot_mention": false,
  "AIOverview_mention": false,
  "AIMode": false,
  "OrganicResult_mention": true,
  "queries": ["best search engine"]
}
```

`Gemini_mention` and `Copilot_mention` are present only when the corresponding `enable*` flag was true for the run. The skill comma-joins all `true` engine flags into the `Source Engines` column (with friendly labels: `Google Organic`, `ChatGPT`, `Gemini`, `Copilot`, `Perplexity`, `Google AI Mode`, `Google AI Overview`).

## Sub-Actor access

The Actor orchestrates four sub-Actors. The skill needs two of them for output enrichment; the runner script's `--fetch-sub-datasets` flag walks the Sub-Actor results index and downloads them.

| Sub-Actor | Used to populate |
|---|---|
| [Google Search Scraper](https://apify.com/apify/google-search-scraper) | `SERP Position` (rank within organic results), `Article Title`, `Publish Date`. Also drives the per-engine result fetch when `enableChatGpt`, `enableGemini`, `enableCopilot`, `enablePerplexity`, `enableAiMode` are true. Join on `url` + `query`. |
| [Website Content Crawler](https://apify.com/apify/website-content-crawler) | `Placement Source Sentence`, `Placement With Link`, `Placement New Insertion` (needs page body text). Cross-check for `Article Author` via `metadata.author` / openGraph `article:author` / JSON-LD `Person.name`. |
| [Contact Details Scraper](https://apify.com/apify/contact-details-scraper) | Already merged into the All leads dataset. Rarely needed directly. |
| Email Verifier (sub-Actor) | Runs only when `enableEmailVerification: true`. Populates `email_verification` on each lead. |
| [AI Web Scraper](https://apify.com/apify/ai-web-scraper) | Only runs when `searchAuthorName: true`. Already merged into the Author list dataset. |

## Output column to dataset map

| Output column | Source |
|---|---|
| `SERP Position` | Google Search Scraper sub-dataset (rank within organic results, joined by URL + keyword). `"-"` if the row didn't appear in organic SERP. |
| `Source Engines` | Mentions dataset. Comma-join the engines where the corresponding flag is `true` (e.g., `OrganicResult_mention` → "Google Organic", `ChatGPT_mention` → "ChatGPT", `AIMode` → "Google AI Mode", `AIOverview_mention` → "Google AI Overview", `Perplexity_mention` → "Perplexity"). |
| `Keyword` | Mentions dataset `queries[0]` (or join row to the query that surfaced it). |
| `Article Title` | Google Search Scraper sub-dataset `title`. |
| `Article URL` | Mentions dataset `url`. |
| `Domain` | All leads dataset `domain`. |
| `Article Author` | Author list dataset (primary). Fallback to WCC sub-dataset `metadata.author` / openGraph / JSON-LD when missing. |
| `Author Source` | `searchAuthorName` if filled from Author list; `metadata.author` / `openGraph` / `jsonld` for fallback paths; `"not found"` otherwise. |
| `Publish Date` | Google Search Scraper sub-dataset `publishDate` or WCC sub-dataset `metadata.publishedAt`. |
| `Contact Full Name` | All leads dataset `firstName + ' ' + lastName`. |
| `Contact Job Title` | All leads dataset `jobTitle`. |
| `Department` | All leads dataset `departments[0]`. |
| `Seniority` | All leads dataset `seniority`. |
| `Contact Email` | All leads dataset `email`. |
| `Contact LinkedIn` | All leads dataset `linkedinProfile`. |
| `Company` | All leads dataset `companyName`. |
| `Partnership Offer` | User-supplied at Step 2. Same value for every row in a run. |
| `Suggested Link Placement` | Agent-generated using WCC page body. |
| `Suggested Email Copy` | Agent-generated using brand voice + article context. |
| `Outreach Status` | Constant default `"Not started"`. |
| `Notes` | Agent-generated flags (own-domain, competitor, vendor page, UGC) plus manual-lookup hints. |

## Cost notes

Per the Actor's README, billing fan-outs through the sub-Actors. Rough order-of-magnitude per single-query run with `organicResult: 10`:

- Parent Actor: ~$0.02 per query.
- Google Search Scraper: $4.5 per 1k organic results + per-query for each enabled LLM source (ChatGPT, Gemini, Copilot, Perplexity, AI Mode). AI Overviews is free.
- Website Content Crawler: runs once per surviving source.
- Contact Details Scraper: runs only for sources without a backlink. Bounded by `maxContactsPerDomain`.
- Email Verifier (only when `enableEmailVerification: true`): typically much cheaper than the other sub-Actors (~$1 per 1k emails), but adds up at scale.
- AI Web Scraper (only when `searchAuthorName: true`): $25 per 1k sources.

To cut cost during testing: one or two queries, `organicResult: 5`, `maxContactsPerDomain: 1`, disable some LLM sources (keep `enableAiOverviews` since it's free), leave `searchAuthorName: false`. Keep `enableEmailVerification: true` unless quota is tight — bad emails skipped early save more than the verification cost.
