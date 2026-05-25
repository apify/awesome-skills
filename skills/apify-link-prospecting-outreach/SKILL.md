---
name: apify-link-prospecting-outreach
description: Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building.
author: Daniela Ryplová
author_url: https://github.com/danielarypl
---

# Link Prospecting Outreach

Turn a goal + a target keyword + a URL the user wants to promote into a tiered, ready-to-send outreach list: SERP-ranking prospects with Ahrefs-scored authority, the strongest pitch angle per prospect, an outreach-type-matched email draft, and a copy-paste-ready link placement.

## Prerequisites
(No need to check it upfront)

- `.env` file with `APIFY_TOKEN`
- Ahrefs MCP available (the skill calls `mcp__claude_ai_Ahrefs__*` tools for prospect scoring)
- Node.js 20.6+ (for native `--env-file` support)
- One-time setup inside the skill's `scripts/` folder: `npm install`

## Helper scripts (one config, four steps)

After Step 1–2 inputs are collected, write them to a single **`campaign.json`** (schema in [`campaign.json.example`](campaign.json.example)). Every downstream script reads `--config campaign.json`, so the agent doesn't fork per-campaign copies. Sequence:

```bash
# 1. Run the Actor (writes {base}.json + sub-Actor sidecars when --fetch-sub-datasets)
node --env-file=.env scripts/run_actor.js --actor "apify/link-prospecting-tool" --input '<json>' --timeout 1800 --fetch-sub-datasets --output {base}.json --format json

# 2. Build unified prospect table from the sidecars
python3 scripts/build_prospects.py --config campaign.json

# 3. (After Step 5 Ahrefs MCP calls → save to {base}_ahrefs_domain.json + {base}_ahrefs_page.json)
python3 scripts/enrich_prospects.py --config campaign.json

# 4. (After Step 8 sub-agents write outputs to /tmp/placement_outputs/row_*.json)
python3 scripts/merge_subagent_outputs.py --config campaign.json --outputs-dir /tmp/placement_outputs

# 5. Write the final xlsx + metadata sidecar
python3 scripts/write_xlsx.py --config campaign.json
```

If the runner's client-side wait elapses with the Actor still running on Apify, use `scripts/fetch_run_artifacts.js --run-id <id> --output {base}.json` instead of restarting. If the parent run is missing `SUB_ACTOR_RESULTS` (post-2026-05-20 Actor schema), `scripts/fetch_subactors_from_log.js` resolves sub-Actor runIds from the parent log.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect required anchor inputs incl. goal (block on these)
- [ ] Step 2: Collect brand voice, partnership type, output format
- [ ] Step 3: Run apify/link-prospecting-tool
- [ ] Step 4: Pull leads, mentions, authors, and sub-Actor datasets
- [ ] Step 5: Enrich every domain with Ahrefs metrics, assign Prospect Tier
- [ ] Step 6: Run skip pass — flag rows to drop before drafting
- [ ] Step 7: Compute "Why This Prospect" tag per surviving row
- [ ] Step 8: Compose per-row 3-artifact placement + outreach-type-aware email
- [ ] Step 9: Render output in chosen format
```

### Step 1: Required Anchor Inputs (ask FIRST, before anything else)

Do NOT proceed to Step 2 until every required input is answered. Surface them as the very first interaction. The dedup input (#7) is optional but must still be explicitly asked.

1. **Concrete goal for this campaign** — pick one preset or supply custom text. The goal drives skip-pass filtering, outreach-type template selection, and Prospect Tier thresholds. Required.

   | Preset | Effect downstream |
   |---|---|
   | `Recover unlinked brand mentions` | Skip pass drops every row where `brand_mentioned_in_source` is `false`. Default outreach type = `unlinked-mention-claim`. |
   | `Replace competitor links` | Skip pass drops every row not tagged `Links to competitor`. Default outreach type = `competitor-link-replacement`. |
   | `Topical authority links to specific URL` | No filter. Tier thresholds tighten (DR ≥ 50 for tier A). Default outreach type chosen per-row from `Why This Prospect`. |
   | `Maximum link volume from any relevant site` | No filter. Tier thresholds relax (DR ≥ 30 for tier A). Default outreach type chosen per-row. |
   | `Custom` | User-supplied paragraph; biases email tone and tier weights. No automatic skip filter. |

2. **Target keyword(s)** — one or more keywords the user wants their link to appear next to. The skill prospects the SERP for each. At least one required.
3. **Brand name** — the user's brand or product name. The Actor will not run without this (it is the `brand` input field).
4. **Product/category description** — one or two sentences describing what the user sells, who they sell to, and what category their product fits in. Example: *"Apify — web scraping platform that runs serverless scrapers as APIs. We sell to developers and data teams who need scraped data without managing infrastructure."* Required. Used in Step 6 (topical-fit gate) and Step 7 (adversarial-mention detection) to recognise prospects who are in the same product category — those won't link no matter the pitch. Without this, the skill cannot distinguish a genuine editorial opportunity from a competitor's blog.
5. **URL of content to link to** — the destination URL that will be inserted into partner articles. Required.
6. **Competitors** — anyone in the user's product category who would publish a "ours vs theirs" comparison page on their own site. Frame the ask this way explicitly: *"List every company that would write an X-vs-YourBrand comparison page. These won't link to you no matter what — small competitors count too."* Encourage 10+ entries; most users default to listing 3–5 obvious ones and miss the long tail. Mapped to `competitorDomains` on the Actor and reused in Steps 6 (adversarial-mention skip) and 7 (`Links to competitor` Why-tag).

   After the user answers, **offer** (do not push) an Ahrefs auto-pull of organic competitors: *"Want me to pull your top organic competitors from Ahrefs and add them to this list? Adds ~50 API units and surfaces smaller competitors you may have missed."* If the user says yes and Ahrefs MCP is available, call `mcp__claude_ai_Ahrefs__site-explorer-organic-competitors` on the user's domain (extracted from input #5) and merge results into `competitorDomains`. If Ahrefs is unavailable or the user declines, proceed with the user-supplied list only.
7. **Already-pitched domains (optional)** — domains the user has already contacted in past campaigns. Accept a comma-separated list, a CSV/Sheet path, or "none". The skill drops these in the skip pass so the user doesn't double-pitch. Not required to proceed.
8. **Number of organic results per keyword** — how many Google organic SERP results to prospect per keyword. Default 10 if the user is unsure, but ask the question so the user knows the lever exists. Mapped to `organicResult`.
9. **LLM sources to track** — multi-select. Each enabled engine queries an additional AI search/chat surface and adds Google Search Scraper sub-Actor cost per result fetched. Default: all enabled. Mapping to Actor input flags:

   | Option | Actor flag | Cost impact |
   |---|---|---|
   | ChatGPT Search | `enableChatGpt` | Per-result Google Search Scraper cost |
   | Gemini | `enableGemini` | Per-result Google Search Scraper cost |
   | Copilot (Microsoft / Bing) | `enableCopilot` | Per-result Google Search Scraper cost |
   | Perplexity | `enablePerplexity` | Per-result Google Search Scraper cost |
   | Google AI Mode | `enableAiMode` | Per-result Google Search Scraper cost |
   | Google AI Overviews | `enableAiOverviews` | **Free** — parsed from the SERP already fetched. Keep on regardless of budget. |

   Surface the multi-select to the user with all six pre-checked. Disabling individual engines is the main cost-cutting lever short of dropping `organicResult` — recommend keeping ChatGPT + Gemini on at minimum (they capture the largest share of LLM-driven discovery traffic in 2026).
10. **Run email verification?** — boolean. Default: `yes`. Mapped to `enableEmailVerification` on the Actor. When enabled, the Actor verifies every email returned by the Contact Details Scraper sub-Actor and tags each lead with a verification status (`verified` / `catch-all` / `risky` / `invalid` / `unknown`). The skill uses the status in Step 6 (invalid emails get auto-skipped) and surfaces it as the `Email Verification` column in the output. Disable only if the user is rate-limited on verification quota or running cost-tight smoke tests.

Once 1–6 and 8–10 are captured (7 is optional), move on.

### Step 2: Secondary Inputs

Ask these next:

1. **Brand info and voice** — a short paragraph describing the product/brand and the tone for outreach (e.g., "casual and helpful", "formal B2B", "founder-led"). Used verbatim to shape every generated email.
2. **Partnership type** — the *offer* the user is willing to make. Determines the offer paragraph substituted into the per-row email. Outreach-type template selection happens separately, per-row, in Step 8.

   | Option | What it offers |
   |---|---|
   | ABC link exchange | Three-way link swap: partner links to user, user links to a third party, third party links to partner. |
   | Direct A B link exchange | Two-way link swap: partner links to user, user links to partner. |
   | Resource page / list inclusion | Ask to be added to an existing curated list or roundup. No reciprocal link offered. |
   | Unilateral ask (no reciprocal) | User asks for the link without offering anything in return — appropriate for unlinked-mention claims and broken-link replacements. |
   | Other | User types their own offer (paid placement, free product, co-authored content, etc.). |

3. **Output format**:

   | Format | Behavior |
   |---|---|
   | `xlsx` | `run_actor.js` writes a styled spreadsheet to disk. |
   | `markdown` | Agent renders the table inline in chat with email drafts beneath each row. |

### Step 3: Run the Actor

The Actor ID is `apify/link-prospecting-tool`. Full input schema lives in `reference/apify-actor-usage.md`.

Recommended call payload for this skill (defaults chosen for outreach-first workflow):

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

The six `enable*` LLM-source flags map 1:1 to the user's Step 1 input #9 multi-select. Pass `false` for any engine the user deselected. `enableEmailVerification` maps to Step 1 input #10.

The `ignoreDomains` default includes two groups:
- **Giants and UGC** (wikipedia, github, stackoverflow, reddit, etc.) — too broad to pitch as editorial partners.
- **App / extension marketplaces** (Chrome Web Store, Firefox Add-ons, Apple/Google Play, VS Code Marketplace, etc.) — product directory listings, no editorial decision-makers.

**Do NOT** auto-add to `ignoreDomains` (let the user decide):
- UGC/community sites like `kaggle.com`, `dev.to`, `substack.com`, `producthunt.com`, `g2.com`, `capterra.com`, `trustpilot.com` — some users get real value pitching these.
- API directories like `rapidapi.com`, `programmableweb.com`, `publicapis.dev` — relevant for some products (especially developer-tool brands), irrelevant for others. Surface these as candidates only if the user wants to add them.

The URL-pattern skip rules in Step 6 catch the per-row noise (subdomain prefixes, path patterns) that `ignoreDomains` can't express.

`department` defaults to `["marketing"]` only. The skill prioritises editorial-leaning contacts within the returned `marketing` department during row composition (see Step 8). Only add `sales` if the user explicitly wants BD-style partnership pitches. Only add `c_suite` if the prospect domains are very small (1–5 person shops) where the founder may also be the editor.

Call the runner script:

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/scripts/run_actor.js \
  --actor "apify/link-prospecting-tool" \
  --input 'JSON_INPUT' \
  --timeout 1800 \
  --fetch-sub-datasets \
  --output YYYY-MM-DD_outreach.json \
  --format json
```

Notes:
- `--timeout 1800` is the recommended client-side wait. The Actor itself runs 15-50+ min depending on keyword count, LLM-engine fan-out, and `enableEmailVerification`. Past calibration runs land in the 20–55 min range. Bumping the default avoids the partial-result situation where the runner gives up but the Actor keeps going.
- If the client-side wait still elapses with the Actor still running on Apify (status `RUNNING` or `READY` when the runner exits), do **not** restart the Actor. Use `scripts/fetch_run_artifacts.js --run-id <id> --output <file>` to poll the existing run and download all artifacts — same output shape as `run_actor.js --fetch-sub-datasets`.
- `--fetch-sub-datasets` downloads sibling files alongside the main output: `*_mentions.json`, `*_authors.json`, `*_serp.json`, `*_wcc.json`. You need all of them to populate every output column.

### Step 4: Access All Datasets

The Actor's output schema **changed on or before 2026-05-20**. The build_prospects script must handle the new shape; older skill versions that joined a separate MENTIONS dataset are broken.

**Current schema (verified 2026-05-20):**

| File written by runner / fetcher | Source | Populates |
|---|---|---|
| `*_output.json` (main) | "All leads" dataset | `Contact Full Name`, `Contact Job Title`, `Department`, `Seniority`, `Contact Email`, `Email Verification` (when `enableEmailVerification: true`), `Contact LinkedIn`, `Company`, `Domain`. **Each lead's `source_url[]` array contains the article URLs that produced this contact, each with a `brand_mentioned_in_source` boolean** — this is the new home of the per-(URL, contact) mention data. |
| `*_serp.json` | Google Search Results Scraper sub-Actor (one item per `(query × engine)` combination) | `SERP Position`, `Article Title`, `Publish Date` (via `organicResults[]`), and **engine attribution per URL** (Google Organic, ChatGPT, Gemini, Copilot, Perplexity, Google AI Mode) by joining `aiModeResult.sources[]`, `perplexitySearchResult.sources[]`, `chatGptSearchResult.sources[]`, `geminiSearchResult.sources[]`, `copilotSearchResult.sources[]`. URLs from ChatGPT carry a `?utm_source=chatgpt.com` query suffix — normalise URLs (strip tracking params) before joining. |
| `*_wcc.json` | Website Content Crawler sub-Actor | `Placement Source Sentence`, `Placement With Link`, `Placement New Insertion`, `Article Author` cross-check, outbound-link inspection for `Links to competitor` and `Resource / roundup page` tags. **Canonical URL list for building rows** — every URL that got body-crawled appears here, including ones that didn't yield a lead. |
| `*_authors.json` | AI Web Scraper sub-Actor (when `searchAuthorName: true`) | `Article Author`, `Author Source` (set to `searchAuthorName`). Note: this sub-Actor frequently TIMES-OUT at its 300s default — partial results are still saved. |

**What changed (vs. pre-2026-05-20 runs):**
1. No separate `MENTIONS` / `AUTHORS` / `DOMAINS_WITH_LEADS` named datasets — mention info is folded into `main_leads[i].source_url[]`.
2. No `SUB_ACTOR_RESULTS` record in the parent run's key-value store. Sub-Actor runIds are now only discoverable from the parent run log via regex `\[apify\.<slug> runId:([A-Za-z0-9]+)\]`. The runner script's `--fetch-sub-datasets` flag now falls back to log-parsing when the KV index is missing; the standalone `scripts/fetch_subactors_from_log.js` does the same for runs whose runner already exited.
3. The mentions schema reduced: `source_url[i]` carries only `{domain, brand_mentioned_in_source, url}` — no per-engine flags like the old `ChatGPT_mention` / `Perplexity_mention`. Engine attribution must be reconstructed from the SERP sub-dataset's LLM-result sub-fields (see SERP row above).

If a column's source is missing, write `"Not found"` and add a manual-lookup hint in `Notes`. Never fabricate.

### Step 5: Ahrefs Enrichment and Prospect Tier

For every unique domain that survived the Actor's filtering, fetch authority and traffic metrics via Ahrefs MCP. Call all three tools in parallel per domain (and across domains — batch parallelise to keep this step under a minute for typical 20–50 prospect lists):

| Ahrefs tool | Used for | Column it populates |
|---|---|---|
| `mcp__claude_ai_Ahrefs__site-explorer-domain-rating` (target = domain) | Domain Rating | `Domain DR` |
| `mcp__claude_ai_Ahrefs__site-explorer-metrics` (target = article URL, mode = `exact`) | Page-level organic traffic (last 30 days) | `Page Traffic` |
| `mcp__claude_ai_Ahrefs__site-explorer-backlinks-stats` (target = domain) | Referring domains count | `Referring Domains` |

If Ahrefs returns no data (domain not indexed, page too new), set the column to `"-"` and add a `Notes` hint `"Ahrefs has no data — verify manually before pitching"`. Do not fabricate values.

Assign `Prospect Tier` using the thresholds matching the user's goal:

| Goal | Tier A | Tier B | Tier C |
|---|---|---|---|
| `Topical authority links to specific URL` | DR ≥ 50 AND Page Traffic ≥ 300/mo | DR 30–49 OR Page Traffic 50–299 | everything below |
| `Maximum link volume from any relevant site` | DR ≥ 30 AND Page Traffic ≥ 100/mo | DR 15–29 OR Page Traffic 20–99 | everything below |
| `Recover unlinked brand mentions` | irrelevant — every mention is worth claiming; tier by DR alone (≥ 40 = A, 20–39 = B, < 20 = C) | | |
| `Replace competitor links` | tier by DR (≥ 50 = A, 30–49 = B, < 30 = C) | | |
| `Custom` | use the `Topical authority` thresholds | | |

Surface tier breakdown to the user before Step 8 — let them confirm whether to draft emails for all tiers or only A/B.

### Step 6: Skip Pass

Before drafting any email, walk every row and apply skip rules. Skipped rows get `Outreach Status = "Skip"`, a one-line reason in `Notes`, and **no email or placement is generated** (saves tokens and user review time).

Skip rules (in order):

1. **Goal mismatch.** If the goal is `Recover unlinked brand mentions` and the row's Mentions data shows `brand_mentioned_in_source: false`, skip. If the goal is `Replace competitor links` and the row's WCC body has no outbound link to any `competitorDomains` entry, skip.
2. **Already pitched.** If the row's domain matches an entry in the optional already-pitched list from Step 1 input #7, skip.
3. **Own / competitor domain leak.** The Actor should already filter these, but double-check — if the row's domain matches `ownDomains` or `competitorDomains`, skip.
4. **Stale content.** If `Publish Date` is older than 5 years, skip (low chance the editor will update the post).
5. **URL-pattern skip.** Skip rows whose URL matches any of these patterns:
   - **Subdomain prefixes**: `developers.*`, `docs.*`, `support.*`, `helpcenter.*`, `legacy.*`, `dsarequests.*`, `connectivity.*`, `community.*`, `dev.*` (when used as a doc subdomain — e.g. `dev.example.com/api/`), `api.*` *only when followed by a path that's clearly documentation* (`/reference/`, `/docs/`, `/spec/`). Do NOT skip `rapidapi.com` or other API-directory domains by this rule alone — `api.*` is a subdomain check, not a substring check.
   - **Path patterns**: `/api-docs/`, `/reference/`, `/marketplace/`, `/extensions/`, `/profile/`, `/users/`, `/free-tools/`, `/spec/`, `/content/privacy`, `/content/terms`, `/content/dma`, `/content/how_we_work`, `/legal/`, `/_redirects`, `/sitemap`.
   - **Vendor product page patterns**: URL ends in `-scraper.php`, `-scraping.php`, contains `-data-scraper.`, `-data-scraping.`, `/bots/`, `/extension/`, `/detail/` (extension detail pages).
6. **Non-editorial page type.** Inspect the WCC page body. Skip vendor product pages, pricing pages, login walls, sign-up pages, terms/legal pages, and pages with fewer than 400 words of body text. Word count <400 is the threshold — most editorial articles are 800+ words.
7. **UGC slipped through.** If the page URL contains `/forum/`, `/thread/`, `/comments/`, `/answers/`, `/q/`, `/topic/`, `/discussion/`, or the WCC body is structured as discussion replies, skip.
8. **Category-fit gate (loose).** Extract 4–6 *category* keywords from the user's product description (Step 1 input #4) — these describe the product *category*, not the specific subject of the user's URL. Examples for a web-scraping product: `scrape`, `scraping`, `scraper`, `crawl`, `extract`, `data extraction`. For a CMS product: `cms`, `headless`, `content`, `editorial`. The row's WCC body must contain **at least 1** of these category keywords. If not, skip with reason `Article isn't in user's product category (no '<kw>' match)` — kills recipe blogs, finance articles, and other off-category content that slipped through SERP filtering.

   **For non-English campaigns**, include both source-language and English keywords in the category set — many Czech/German/French articles cite English brand names and product categories inline. Example for a Czech water-filtration brand: `{filtr, filtrace, vod, voda, filter, filtration, water}`. A pure-Czech keyword set would miss articles by Czech authors who write in mixed CS/EN.

   **Known false negatives this rule can't catch (the per-row sub-agent in Step 8 must catch them):**
   - **Local e-commerce competitors selling the exact same product category.** Past campaigns have seen multiple regional e-shops survive the mechanical pass — typically platform-based stores (e.g. Shoptet, Shopify) with "add to cart" buttons embedded in the article body. The sub-agents correctly skipped them, but the wasted compute is a smell. Future versions of this rule should detect platform fingerprints (platform bundle URLs, locale-specific add-to-cart strings, `/eshop/`, embedded product cards with prices in body) and pre-skip.
   - **Category-name homonyms.** "filtr" in Czech also means "filter" in the photography or coffee sense — a coffee-filter or camera-filter blog would pass this gate but isn't a real fit. Sub-agent catches these by reading the body context.

   **The category gate is intentionally loose.** It is a *category* check, not a *subject* check — fine-grained "does this specific article fit my specific URL?" is delegated to the per-row sub-agent in Step 8. Example: for a user URL specifically about scraping a single travel site, a general "python web scraping" guide that never mentions that travel site **passes** this gate because it's in the user's category. The Step 8 sub-agent then decides whether to draft a placement (e.g., an additive line that names the specific travel site) or to recommend a content-based skip.

   Surface the extracted category keyword list to the user at the start of Step 6 and let them add/remove before the pass runs.
9. **Adversarial-mention detection.** When `brand_mentioned_in_source: true`, scan ±100 characters around the brand mention in the WCC body for *negative-context tokens*: `vs`, `versus`, `alternative to`, `alternatives to`, `compared to`, `compared with`, `instead of`, `better than`, `worse than`, `pros and cons`, `comparison`, `review of`. If any of those appear within the window, skip with reason `Adversarial mention (likely competitor comparison page) — won't link`. This catches "ScrapeHero vs Apify" footer mentions, "alternatives to YourBrand" listicles, and similar non-link contexts. **Critical** — without this rule, the `unlinked-mention-claim` outreach type fires on dozens of false positives.
10. **No contact AND no editorial path.** If `Contact Email = "Not found"` AND no `Article Author` AND no domain-level contact page found in WCC outbound links, skip — there is no one to pitch.
11. **Invalid email (from verification).** When `enableEmailVerification: true` ran, inspect each row's `Email Verification` status. If the primary contact's status is `invalid`, **try the alternate contacts first** before skipping the row — past runs have lost Tier A candidates because the primary contact's email was invalid but a verified alternate existed on the same domain. Only skip with reason `Email failed verification (invalid address)` when no alternate has a verified or unchecked email. Statuses `catch-all`, `risky`, `unknown` are **informational only** (not auto-skipped) — surface them in the `Email Verification` column. Status `verified` ships as-is. If verification didn't run for this campaign, the column shows `-` and this rule is a no-op.

   **Never suggest external lookup services or workaround tools in Notes** — no `hunter.io`, no `LinkedIn search`, no third-party verification services. The skill's job is to surface what *we* found, factually. When information is missing (no email, no author, etc.), state the gap and stop. The user knows where to look; suggesting their tools back at them is condescending and clutters the output.

A row failing any rule above is skipped *before* Step 7. Skipped rows still appear in the final output (so the user can see what was filtered) but with empty placement and email cells and `Outreach Status = "Skip"` plus the reason in `Notes`.

### Step 7: "Why This Prospect" Tags

For every surviving row, compute one or two `Why This Prospect` tags, prioritised by which makes the strongest pitch. These tags drive the outreach-type template selection in Step 8.

| Tag | Trigger | Source of truth |
|---|---|---|
| `Mentions brand, no backlink` | `brand_mentioned_in_source: true` AND `backlink_in_source: false` in Mentions dataset | Mentions dataset |
| `Links to competitor [domain]` | WCC page body contains an outbound link whose host matches any `competitorDomains` entry | WCC dataset |
| `Top-3 SERP for [keyword]` | `SERP Position` is 1, 2, or 3 for any keyword | Google Search Scraper sub-dataset |
| `Resource / roundup page` | WCC page body has 10+ outbound links AND the page title or H1 matches `/(best\|top\|list\|roundup\|tools\|resources\|guide to)/i` | WCC dataset |
| `Outdated content` | `Publish Date` is older than 24 months AND newer than 5 years (5+ years was already skipped) | Google Search Scraper / WCC |

A row may carry up to two tags. Order them by pitch strength using this priority: `Mentions brand, no backlink` > `Links to competitor` > `Resource / roundup page` > `Top-3 SERP` > `Outdated content`. If no tag fits, leave the column as `"-"` — the row still gets pitched, just without a special angle.

### Step 8: Compose Per-Row Placement and Email

Each surviving row gets three placement artifacts plus one email draft. Apply these quality rules without exception:

1. **No fabrication.** If the article author or contact email is unknown, set the field to `"Not found"` and leave a one-line factual note (e.g., `"No email found for this contact"` or `"No author detected"`). **Do not suggest external lookup tools or workarounds in Notes** — see Step 6 rule 11 for the rationale. Just state the fact and stop.

2. **Prioritise editorial-leaning contacts.** When the All leads dataset returned multiple contacts for the same domain, prefer the one whose `jobTitle` matches `/editor|content|writer|managing|editorial|blog|copy/i`, demote anyone whose `jobTitle` matches `/ceo|cfo|cto|founder|chief|vp\b|president/i` unless the company is a 1–5 person shop. Surface the chosen contact in the row; keep alternates in `Notes` as `"Alternate contacts: <name1> (<title>), <name2> (<title>)"`.

3. **Three placement artifacts — try strategies in this priority order.** Use the WCC sub-dataset's page text. Try strategies 1 → 2 → 3 in order; stop at the first one that produces a clean fit. Record which strategy was used by prepending the `Notes` field with `Placement: drop-in` / `Placement: additive` / `Placement: new insertion`.

   **Strategy 1 — drop-in (preferred).** Find a sentence in the article where the user's URL can be added to existing words *without changing any of the surrounding prose*. The link goes on an existing word or short phrase the author already wrote. Output:
   - `Placement Source Sentence` = the verbatim sentence as it appears in the article.
   - `Placement With Link` = the same sentence with the link inserted on an existing word/phrase. **No new prose, no rewording, no deletions.** Example: source = `"Tools like Octoparse and BeautifulSoup work well for hotel data."` → with-link = `"Tools like Octoparse and **[BeautifulSoup](URL)** work well for hotel data."` (link added to existing word). The editor doesn't have to approve any new wording — just a hyperlink.
   - `Placement New Insertion` = `"-"`.

   Drop-in works when the article already names a brand, tool, or technique that maps cleanly to the user's URL. It's the *lowest-friction* ask of any outreach pattern: "could you add a hyperlink to a word you already wrote?"

   **Strategy 2 — additive (second choice).** When no drop-in target exists but the article has a sentence the user's URL would naturally *follow*, keep the original sentence intact and add **one** new sentence after it. The new sentence introduces an adjacent reader-need that the article doesn't already cover and that the user's URL addresses. Output:
   - `Placement Source Sentence` = the verbatim original sentence.
   - `Placement With Link` = original sentence kept verbatim, followed by `→` and a one-sentence follow-on containing the link. Example: source = `"By integrating with Acme Travel's APIs, developers can enrich their platforms with hotel data."` → with-link = `"By integrating with Acme Travel's APIs, developers can enrich their platforms with hotel data. → ...with hotel data. In need of competitor pricing data the API doesn't expose? Then you need a [hotel-data scraper](URL)."` Keep the original sentence verbatim; the follow-on is the only new prose.
   - `Placement New Insertion` = `"-"`.

   The follow-on must (a) raise a reader need the existing sentence doesn't address, (b) connect that need to the user's URL, (c) be one sentence, ≤25 words, written in the article's voice.

   **Strategy 3 — new insertion (last resort).** Only when neither drop-in nor additive works (e.g., no relevant sentence exists in the article body). Draft a fully new 1–2 sentence paragraph in the article's voice with a precise insertion location:
   - `Placement Source Sentence` = `"-"`.
   - `Placement With Link` = `"-"`.
   - `Placement New Insertion` = the drafted paragraph + the exact anchor (`"insert as a new paragraph immediately after the sentence ending in '…X.' in the section under H2 'Y'."`).

   If even a new insertion can't be drafted (the article is the wrong topic for the user's URL), set `Outreach Status = "Skip"` and add `Notes: "No natural placement — article topic mismatch"`. **However**, the topical-fit gate in Step 6 rule 8 should have caught this case already; if a row makes it to Step 8 and can't get a placement, treat that as a hint that the gate needs more keywords.

   **Every surviving row goes through a sub-agent — not just Tier A/B/mention-only.** The mechanical skip pass (Step 6) cuts the *obviously* bad prospects (competitor domains, doc subdomains, policy pages, dead-contact rows, off-category articles). Everything that passes is by definition a candidate worth real consideration, and the sub-agent makes the *final* fit call: read the article, attempt a placement (drop-in → additive → new insertion), and either draft email or return `placement_strategy = "skip"` with a content-specific reason. **Python templates / regex / keyword scoring are not acceptable for the final draft** — they produce mechanical splices that read awkward in context (we've seen this fail in practice on real campaigns).

   Spawn sub-agents in parallel: one per surviving row, each given the WCC text, user URL context, contact info, brand voice, and partnership offer. The output schema (placement strategy, the three placement column values, email subject + body, skip recommendation, notes) is what gets merged back into the spreadsheet row.

   A row that the sub-agent decides to skip after content review gets `Outreach Status = "Skip"` and the agent's reason in Notes — same shape as a Step 6 mechanical skip, just with a more nuanced rationale.

4. **Determine `Outreach Type` per row** from the `Why This Prospect` tags + user goal:

   | Trigger | `Outreach Type` |
   |---|---|
   | Tag `Mentions brand, no backlink` present | `unlinked-mention-claim` |
   | Tag `Links to competitor` present | `competitor-link-replacement` |
   | Tag `Resource / roundup page` present | `resource-page-inclusion` |
   | Tag `Outdated content` present | `outdated-content-replacement` |
   | None of the above OR only `Top-3 SERP` tag | `topical-niche-edit` |

   Pull the matching template from `reference/email-templates.md`. The user's Step 2 `Partnership type` answer substitutes into the `{{offer_paragraph}}` placeholder inside the template — the *outreach type* determines structure and opening hook, the *partnership type* determines the offer.

5. **`Suggested Email Copy` must use the user's brand voice.** Apply the voice paragraph verbatim per the voice substitution rules in `reference/email-templates.md`. If voice input was skipped, use the generic-professional default and note this in `Notes`.

5a. **The email MUST include the exact placement wording — verbatim.** The recipient should never have to ask "what's the wording you're suggesting?" or click through to a separate cell to see the proposed text. Embed the proposal directly:
   - For **drop-in**: quote both the source sentence and the linked version inline. Example: `"In your line 'Tools like X and Y work well for Z', would you turn 'Y' into a hyperlink to <URL>?"`
   - For **additive**: quote the anchor sentence verbatim AND the exact follow-on sentence you're proposing. Example: `"Right after your sentence 'X happens because Y.', would you add: 'For the Z case specifically, see <URL>.'?"`
   - For **new insertion**: quote the anchor sentence the new paragraph should follow, then the full proposed paragraph inline. Example: `"In the 'Honorable mentions' section, after 'each platform has its own trade-offs.', would you add this paragraph: '<full paragraph with link>'?"`

   The email is the ask. If the wording isn't *in* the email, the ask is incomplete. Vague phrasing like "happy to draft it for you" / "happy to send exact wording" / "a follow-on sentence linking to..." is a content-skill bug — always rewrite to include the verbatim proposal.

6. **Word cap: emails are 150 words or less** (subject + body combined).

7. **Personalisation is mandatory.** Every email must open with a concrete reference to the specific article (title + a one-line takeaway from its content). No generic "I loved your article" openers.

### Step 9: Render Output

**Markdown format** — agent renders inline in chat:
1. A header line with the Apify run ID and tier breakdown (`A: 8, B: 15, C: 7, Skipped: 12`).
2. One Markdown table row per prospect with the most actionable columns (tier, why, contact, placement summary). Skipped rows render in a separate collapsed section at the bottom.
3. Below the table, one fenced code block per non-skipped row containing the email draft (subject + body), labeled with the row index, tier, and outreach type.

**xlsx format** — `scripts/write_xlsx.py --config campaign.json` writes a 2-sheet workbook after Steps 5–8 finish.

**xlsx is written as two sheets:**
- **`Outreach`** — active rows only, full 30 columns. This is the send-ready deliverable. Sorted by `Prospect Tier` ascending (A first), then by `Domain DR` descending, then by `SERP Position` ascending.
- **`Skipped`** — skipped rows with **reduced columns**: `Domain`, `Article URL`, `Article Title`, `Skip Reason` (extracted from Notes), `Source Engines`, `Why This Prospect`. This sheet exists for auditing what was filtered without cluttering the main view. Missing Ahrefs columns aren't visible here, so the empty-data confusion goes away.

The user opens the file and lands on `Outreach` by default — only actionable prospects. They can switch to `Skipped` to audit. This pattern replaces the older single-sheet-with-red-rows approach.

Both formats also produce a sidecar `run_metadata.json`: `{ runId, actorId, startedAt, finishedAt, inputs, datasetIds, tierCounts, skipCounts }`. Drop it next to the main output file.

## Output Row Schema (30 columns)

`SERP Position`, `Source Engines`, `Keyword`, `Article Title`, `Article URL`, `Domain`, `Domain DR`, `Page Traffic`, `Referring Domains`, `Prospect Tier`, `Why This Prospect`, `Article Author`, `Author Source`, `Publish Date`, `Contact Full Name`, `Contact Job Title`, `Department`, `Seniority`, `Contact Email`, `Email Verification` (one of `verified` / `catch-all` / `risky` / `invalid` / `unknown` / `-`), `Contact LinkedIn`, `Company`, `Outreach Type`, `Partnership Offer`, `Placement Source Sentence`, `Placement With Link`, `Placement New Insertion`, `Suggested Email Copy`, `Outreach Status` (default `"Not started"`, `"Skip"` for skipped rows), `Notes` (auto-flags + skip reason + manual hints + alternate contacts).

Full schema with types and source datasets per column is in `reference/output-formats.md`.

## Error Handling

| Error / symptom | What to do |
|---|---|
| `APIFY_TOKEN not found` | Ask user to create `.env` with `APIFY_TOKEN=your_token`. Get one at console.apify.com/account/integrations. |
| Ahrefs MCP unavailable | Skip Step 5. Set `Domain DR`, `Page Traffic`, `Referring Domains`, `Prospect Tier` to `"-"` and add a one-line note in the output header explaining tiers were not computed. Continue with the rest of the workflow. |
| `Cannot find module 'xlsx'` | Run `npm install` inside the skill's `scripts/` folder. |
| `Error: 'brand' is required` | The user skipped Step 1 anchor #3. Re-ask brand name. |
| Actor run `TIMED-OUT` (client-side, Actor still running on Apify) | Do not restart. Use `node --env-file=.env scripts/fetch_run_artifacts.js --run-id <runId> --output YYYY-MM-DD_outreach.json --timeout 1800` to poll the existing run and download all datasets when it terminates. Same output shape as the runner. |
| Actor run `TIMED-OUT` (Actor itself ran past its `timeoutSecs`) | See `reference/troubleshooting.md`. Lower `organicResult`, cut keywords, or disable some LLM engines. Almost never the cause — usually it's the client-side wait. |
| `Author = Not found` | Expected for ~30% of pages without bylines. Skill writes `"Not found"` and adds a manual-lookup hint to `Notes`. Do not fabricate. The AI Web Scraper sub-Actor frequently TIMES-OUT at its 300s default mid-crawl (past campaigns have lost author data for ~7 high-DR sites at a time this way); when this happens the `_authors.json` dataset still contains the partial results that finished before the timeout. WCC `metadata.author` / openGraph `article:author` / JSON-LD `Person.name` are the fallbacks the agent should try before writing `"Not found"`. |
| Sub-Actor datasets missing (no `_mentions.json` / `_authors.json` / `_serp.json` / `_wcc.json` after `--fetch-sub-datasets`) | Actor's output schema changed on or before 2026-05-20: `SUB_ACTOR_RESULTS` is no longer in the KV store, and `MENTIONS`/`AUTHORS`/`DOMAINS_WITH_LEADS` named datasets are gone. The runner script now falls back to log-parsing automatically — but if it didn't, run `node --env-file=.env scripts/fetch_subactors_from_log.js --run-id <id> --base <prefix>` to populate `_serp.json`, `_wcc.json`, `_authors.json` from the sub-Actor runIds visible in the parent log. Mention data is now embedded in `main_leads[i].source_url[]`, not a separate file. |
| `Contact Email = Not found` | Contact Details Scraper sub-Actor missed the site. Set the field to `"Not found"` and leave a one-line factual `Notes` entry (`"No email found for this contact"`). Do not fabricate, do not suggest external tools. If both contact and author are missing, the skip pass (Step 6, rule 7) will drop the row. |
| All rows skipped by goal filter | The user's goal is too narrow for the SERP results. Suggest broadening the goal (e.g., `Topical authority` instead of `Recover unlinked brand mentions`) or expanding keywords. |
| `0 leads returned` | Keyword too narrow, or `ownDomains` / `competitorDomains` filtered out all SERP results. Broaden keyword, narrow exclusions, raise `organicResult`. |
| Costs higher than expected | Sub-Actor fan-out (Google Search Scraper, WCC, Contact Details Scraper, AI Web Scraper) stacks. See cost section in `reference/apify-actor-usage.md`. To shrink: drop `searchAuthorName`, disable AI platforms (`enableChatGpt: false`, etc.), lower `maxContactsPerDomain` to 1, lower `organicResult` to 5. |
