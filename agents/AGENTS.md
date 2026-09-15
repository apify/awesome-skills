<skills>

# Awesome Apify Skills

Community collection of Apify agent skills for web data extraction, scraping, and automation. Each skill is a `SKILL.md` file that teaches you how to accomplish a specific task using [Apify Actors](https://apify.com/store).

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. Skills follow the [Agent Skills open standard](https://agentskills.io/specification).

## Available skills

Read a skill's SKILL.md before using it — that's where the full instructions live.

<available_skills>

- **apify-ads-intelligence** by [Sameh Jarour](https://github.com/samehjarour) → `skills/apify-ads-intelligence/SKILL.md`: Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries.
- **apify-ai-search-visibility-tracker** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-ai-search-visibility-tracker/SKILL.md`: Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, see if their brand shows up in AI search, discover which prompts competitors rank for in AI search, find citation opportunities, or audit a website for AI visibility readiness.
- **apify-ashby-jobs-scraper** by [John Cole](https://github.com/johnisanerd) → `skills/apify-ashby-jobs-scraper/SKILL.md`: "Scrape Ashby jobs or discover companies using Ashby with the Apify Ashby Job Board API Actor (johnvc/ashby-job-board-scraper). Job mode returns live job rows with title, company, location, remote and employment fields, publish date, apply URL, employer-published salary columns, equity flag, and Markdown descriptions. Company mode finds Ashby boards from a bundled directory or checks a prospect list, returning company name, board slug and URL, live open-job count, and verification fields. Takes company names, board slugs, or board URLs; supports pre-billing job filters and publishedAfter feeds. Use for Ashby jobs data or API requests, salary and remote-role collection, job-board pipelines, companies using Ashby/Ashby customers, ATS market maps, prospect checks, and recruiting or sales target lists. Billed per delivered result with no start fee, and MCP-ready for Claude and other AI agents."
- **apify-booking-host-leads** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-booking-host-leads/SKILL.md`: Find and enrich B2B leads from Booking.com - hotels, apartments, and vacation rentals - and pull each host's or property manager's real contact details (email, phone, company name, registration number). Use when the user says things like "get emails from Booking.com", "Booking.com lead generation", "find tour operator / property manager / host contacts", "scrape accommodation owner emails", or "build a list of Booking hosts". The host's email is usually already inside the Booking scraper's traderInfo field (EU/AU trader-transparency disclosure) - this skill leads with that and uses a Google Maps email scraper only as a fallback, instead of relying on Google Maps first (which mostly returns the wrong business).
- **apify-buying-signal-detection** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-buying-signal-detection/SKILL.md`: Set up a recurring buying-signal detection pipeline that finds companies showing buying intent across three signal types — job postings (hiring for the persona), fundraising events (recent raises), and LinkedIn content (pain-point posts, hiring announcements) — then aggregates results into a deduplicated leads.csv with the signal source, evidence URL, and detection timestamp per row. Split-schedule architecture — Apify Actor Tasks pull raw data on their own cadence, a Claude-side aggregation task normalizes, deduplicates against a blacklist, and appends new leads with a weekly-idempotent guard. Use when the user says "find companies with buying signals", "detect intent signals for outbound", "set up a weekly lead pipeline", "monitor hiring signals for lead gen", "track startup funding leads", "find LinkedIn buying signals", "schedule Apify Actors for prospecting", "build a signals-based lead list", or "set up buying-intent monitoring for my ICP".
- **apify-company-data-api** by [John Cole](https://github.com/johnisanerd) → `skills/apify-company-data-api/SKILL.md`: "Pull structured B2B company data from Clutch.co with the Clutch.co Agency API Actor (johnvc/clutch-agency-api). Give it company profile URLs or bare slugs and get one JSON record per company: name, website, rating, review_count, verification badges, min_project_size, hourly_rate, employees, founded_year, headquarters and every office location, languages, service_lines and focus_areas with percentages, industries, clients, cost_rating, most_common_project_size, pricing_by_service, and published packages. Each profile row can also carry LLM-ready markdown at no extra fetch, and verified client reviews as their own rows. Use when someone wants a company data api, to enrich a CRM with firmographics and service mix, pull B2B service provider records, or turn a list of agency profiles into structured company data as JSON. Billed per profile delivered with no start fee, and MCP-ready for Claude and other AI agents."
- **apify-creator-emails** by [Zakariae (Flash Scrape) — routes to Actors built by the author; no affiliate or referral parameters](https://github.com/ZAKRIAZ) → `skills/apify-creator-emails/SKILL.md`: Find creators and their published contact emails in one run. Routes "find YouTube channels about <niche> with emails", "get the email for these TikTok / Instagram handles", "build a micro-influencer outreach list", "creator email finder", "influencer contact list for a sponsorship campaign" and "alert me when new creators appear in <niche>" to a single Actor that discovers YouTube channels by keyword, optionally hops to the Instagram and TikTok profiles those channels link, enriches user-supplied TikTok and Instagram handles, crawls each creator's linked site for an email, MX-verifies it and scores every row 0-100 in one 51-column schema. No login, no API key. Use when the user asks to scrape creator or influencer emails, find YouTube creators by topic, enrich a list of TikTok or Instagram usernames with contact details, or set up a weekly new-creator watch. Does not search TikTok or Instagram by keyword or hashtag.
- **apify-easy-competitive-intelligence** by [chocholous](https://github.com/chocholous) → `skills/apify-easy-competitive-intelligence/SKILL.md`: This skill should be used when the user asks to "analyze a competitor", "compare pricing", "competitive landscape", "market research", "what do customers think", "review intelligence", "hiring signals", "content strategy", "SEO battle", "build a battlecard", "competitive analysis", "who are the players", "who competes with", "market intelligence", "competitive positioning", "deep dive on a company", "board prep", "SWOT analysis", "how does [X] compare to [Y]", or mentions competitor analysis, pricing comparison, customer sentiment, or market landscape research. Requires Apify CLI or Apify MCP server.
- **apify-ecommerce** by [Luis Pinto](https://github.com/luispintoapify) → `skills/apify-ecommerce/SKILL.md`: Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence.
- **apify-google-maps-leads** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-google-maps-leads/SKILL.md`: Build a local-business lead database from Google Maps in one Apify pipeline: search by target audience + geography, enrich each place with company contacts from its website, leads enrichment (names, emails, phones, LinkedIn), Instagram + Facebook profiles, and optionally reviews for lead scoring. For places with no named contacts, escalate to apify/ai-web-scraper to pull owner / decision-maker names from the business website. Backfill missing phones via scalelist/phone-finder and missing emails via scalelist/email-finder. Use when the user asks to build a lead list from Google Maps, scrape local businesses, generate B2B leads by city/industry, find owner/decision-maker contacts for restaurants / dentists / gyms / hotels / any local vertical, score leads by review volume or rating, or says "Google Maps lead-gen pipeline", "leads from Maps", "prospect local businesses", "scrape Google Maps for outreach", "find companies in <city>", or mentions chaining Google Maps + AI web scraper + Scalelist Actors.
- **apify-influencer-brand-collabs** by [Natasha Lekh](https://github.com/natashalekh) → `skills/apify-influencer-brand-collabs/SKILL.md`: Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks who collabs with a brand, which brands a creator has done paid posts for, wants to audit an influencer's branded-content history, or wants to scope a brand's sponsorship roster. **Triggers:** - "who collabs with [brand] on Instagram?" - "what brands has [creator] done sponsored posts for?" - "find paid partnerships / branded content for [handle]" - "audit [influencer]'s brand deals" - "show me [brand]'s influencer roster" Works in either direction — brand → creators or creator → brands — and detects direction from the data, so don't ask the user to declare it. Requires Apify MCP tools.
- **apify-job-boards** by [Zakariae (Flash Scrape)](https://github.com/ZAKRIAZ) → `skills/apify-job-boards/SKILL.md`: Pull job postings from many boards in one run and prepare one validated, deduplicated table. Routes "find jobs / scrape job postings / build a job list / monitor new jobs / track a company's careers page" requests to a multi-board job scraper (LinkedIn, Indeed, Glassdoor, The Muse plus keyless boards) or a remote-only aggregator (RemoteOK, We Work Remotely, Remotive, Jobicy, Himalayas, HN Who is hiring), with output-locality checks, per-board raw/qualified/deduplicated counts, only-new-jobs monitoring, per-board caps and honest cost estimates. Use when the user asks to scrape jobs across job boards, get Indeed or Glassdoor postings without an API key, collect remote developer jobs, watch a company's Greenhouse/Lever/Ashby careers page, or set up a daily new-jobs alert.
- **apify-lead-scoring-enrichment** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-lead-scoring-enrichment/SKILL.md`: Score and enrich a CSV of B2B leads using Apify Actors. Takes a CSV with company URLs, free-text scoring rules, and an enrichment preference; runs BuiltWith (tech stack), Website Content Crawler (content classification), and Contact Info Scraper (company metadata) for scoring; enriches with either department-specific contacts (Contact Info Scraper + Bulk Email Finder fallback) or copywriter discovery (Google Search Scraper → AI Web Scraper → Bulk Email Finder). Outputs an enriched CSV with a numeric score and a per-lead outreach_hook column that personalizes cold email copy (e.g. "uses Shopify → send Shopify install guide"). Use when user asks to score leads, qualify leads, enrich a lead list, detect a company's tech stack for outreach, find marketing/sales/engineering contacts at a list of companies, hunt down blog copywriters for guest-post pitches, personalize cold email at scale, or turn a raw domain list into a ready-to-pitch account list.
- **apify-link-prospecting-outreach** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-link-prospecting-outreach/SKILL.md`: Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building.
- **apify-local-business-leads-osm** by [Zakariae (Flash Scrape) — routes to Actors built by the author; no affiliate or referral parameters](https://github.com/ZAKRIAZ) → `skills/apify-local-business-leads-osm/SKILL.md`: Build a local-business lead list without scraping Google Maps. Routes "find dentists / plumbers / salons / restaurants in <city> with emails", "business email finder for <category> in <city>", "web-design prospects with no website or a weak one", "enrich my list of business websites with verified emails", "leads within 5 km of an address" and "alert me when new businesses appear" to an OpenStreetMap-based Actor that crawls each business's own website and returns one 73-column row per business with an MX-verified email, phone, social profiles, website platform and a 0-100 lead score. No Google Maps, no API key, no proxy, no login; every filter runs before billing. Use when the user wants local B2B leads for cold email or calls, a Google Maps alternative that avoids Google's terms, a bring-your-own-website-list enrichment pass, or a scheduled new-business watch for one category and city.
- **apify-marketing-agency-database** by [John Cole](https://github.com/johnisanerd) → `skills/apify-marketing-agency-database/SKILL.md`: "Build a marketing agency database from Clutch.co with the Clutch.co Agency API Actor (johnvc/clutch-agency-api). Point it at any Clutch directory or category or location URL and get one JSON row per listed agency: name, profile_url, website, rating, review_count, verification, min_project_size, hourly_rate, employees, location, and service_lines. Pagination and cross-page de-duplication are handled for you, so one company is never billed twice. Use when someone wants a marketing agency database, a list of digital marketing agencies, a B2B agency directory as structured data, top agencies by service or city, or to export agencies from Clutch into a spreadsheet, CRM, or vector store. Billed per listing delivered with no start fee, and MCP-ready for Claude and other AI agents."
- **apify-osint-threat-intel** by [karthik-zoro-96](https://github.com/karthik-zoro-96) → `skills/apify-osint-threat-intel/SKILL.md`: Use this skill when the user asks to "find CVEs for", "check if my domain is breached", "threat intel on", "OSINT on", "security news about", "attack surface of", "is this IP malicious", "what vulnerabilities affect", "security advisory for", "monitor threats for", "threat actor research", "recent exploits for", "data breach check", "security posture of", "what's the threat landscape for", "investigate [domain/IP/software]", "is [company] exposed", or any request involving vulnerability research, breach detection, threat actor profiling, or security intelligence. Requires Apify CLI or Apify MCP server.
- **apify-product-data-setup** by [Luís Pinto](https://github.com/luispintoapify) → `skills/apify-product-data-setup/SKILL.md`: Wire an AI agent to live e-commerce product data using Apify's E-commerce Scraping Tool over MCP, either as runtime tool calls or as a scheduled refresh into a vector store. Trigger on "give my agent live product data", "my agent quotes stale prices", "connect Apify MCP to Claude or Cursor or n8n", "add product data to my RAG pipeline", "keep my product catalog fresh", "set up a shopping agent", or any request to stop an agent answering product questions from training data. Use for the integration work; use apify-product-lookup to actually answer a product question.
- **apify-verified-email-finder** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-verified-email-finder/SKILL.md`: Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative.
- **apify-x402-agentic-wallet** by [Martin Forejt](https://github.com/martinforejt) → `skills/apify-x402-agentic-wallet/SKILL.md`: Discover, pay for, and run any Apify Actor by paying USDC on Base over the x402 protocol with a Coinbase Agentic Wallet (awal) — no Apify account or API key. You buy one small, spend-capped prepaid Apify token, then run as many Actors as the request needs with it. Use when the user wants to use Apify tools without signing up, pay per use with crypto / USDC, set up an agentic wallet, mentions "x402", "awal", "agentic wallet", "Coinbase wallet", "pay with USDC", "no API key", or asks to pull live web data (social media, search, maps, marketplaces, news) while paying on-chain per use.
- **apify-yandex-image-search-api** by [John Cole (links use the author’s Apify affiliate code; routed Actors are built by the author)](https://github.com/johnisanerd) → `skills/apify-yandex-image-search-api/SKILL.md`: Search the Yandex Images vertical and get full-size image URLs as structured JSON with the Apify Yandex Search Scraper Actor (johnvc/Scrape-Yandex). A yandex image search api for agents and pipelines. One text query returns image results with the original full-size image URL, hosting page link, thumbnail, and source, filtered by image type, color, orientation, file type, exact size, site, and recency. Use when the user wants a yandex image search api or yandex images api, wants to search Yandex Images programmatically, collect image datasets with full-size URLs, source images from Russian-language sites, or filter image results by color, size, or license-friendly site. Pay-per-page billing, MCP-ready for Claude and other AI agents.
- **apify-yandex-search-api** by [John Cole (links use the author’s Apify affiliate code; routed Actors are built by the author)](https://github.com/johnisanerd) → `skills/apify-yandex-search-api/SKILL.md`: Get structured Yandex search results without an official API key using the Apify Yandex Search Scraper Actor (johnvc/Scrape-Yandex). One query returns the full SERP as JSON, with organic results (position, title, link, displayed_link, snippet), and optional ads, knowledge graph, inline images, and inline videos, targeted by Yandex domain, language, and any of 123,000 plus lr region IDs. Use when the user wants a yandex search api, a yandex serp api, Yandex search results as JSON or CSV, to scrape Yandex search, to check what ranks on yandex.ru for a query or region, or SEO research for Russian-speaking markets. Pay-per-page billing, MCP-ready for Claude and other AI agents.

</available_skills>

Paths are relative to the repository root.

</skills>

---

# How to add a new skill (for AI agents)

A contributor asked you to add a new skill to this repo. Follow these steps.

## Files to create

1. **`skills/apify-<name>/SKILL.md`** — copy from `skills/_template/SKILL.md` and replace every `REPLACE` placeholder. Required frontmatter:
   - `name: apify-<name>` (must match the folder name; kebab-case)
   - `description: ...` (≤ 1024 characters; include trigger phrases the user would say)
   - `author: ...` (optional)
   - `author_url: https://...` (optional)
   - `metadata:` block with:
     - `keywords: "keyword-one, keyword-two, ..."` (comma-separated string; required)
     - `category: data-extraction` (optional; defaults to `data-extraction`)
2. **`skills/apify-<name>/references/actor-index.md`** and **`references/gotchas.md`** — copy the templates from `skills/_template/references/` and fill them in. Optional but recommended.

## Marketplace entry

There is nothing to add manually. `.claude-plugin/marketplace.json` is generated
from SKILL.md frontmatter after your PR merges — do **not** edit it in your PR.

## Rules

- **One skill per PR.** CI rejects PRs that touch multiple skills (unless a maintainer adds the `maintainer` label).
- **No unnecessary changes.** Edit only files inside `skills/apify-<name>/`.
- **Do not edit** `.claude-plugin/marketplace.json`, `agents/AGENTS.md` or the skills table in `README.md` — all three are regenerated from frontmatter after merge.
- **Use Apify Actors only** — they must be publicly available on the [Apify Store](https://apify.com/store).

## Calling Actors — your choice

This repo does not mandate any specific interface. Pick one of:

- **Apify CLI** (`apify actors call ...`) — recommended for portability; see [`skills/_template/SKILL.md`](../skills/_template/SKILL.md) for the three flags to include on every call.
- **Apify MCP connector** at <https://mcp.apify.com>.
- **MCP client** of your choice (e.g. [mcpc](https://github.com/apify/mcpc)).

Whichever you pick, cross-tool compatibility is your responsibility.

## Validation

Run locally before opening the PR:

```bash
uv run scripts/generate_agents.py
```

This validates `name`/`description`/`author_url`/`metadata.keywords` and regenerates `.claude-plugin/marketplace.json`, `agents/AGENTS.md` and the README skills table from frontmatter. CI runs the same script on the PR (don't commit the regenerated files — the bot pushes them after merge).

## Submitting a skill (for AI agents)

Follow this flow when the user wants to contribute their own skill — "submit my skill", "add my skill to awesome-skills", "contribute a skill". It layers a short user interview on top of the mechanical steps above. [CONTRIBUTING.md](../CONTRIBUTING.md) is the source of truth for every rule and limit; this section only sequences the work.

### Step 1 — Interview the user

Collect all six answers before writing any files:

1. **Task & trigger phrases.** What does the skill accomplish, and what exact phrases would a user say to invoke it? → frontmatter `description` (≤ 1024 chars, trigger phrases included).
2. **Actors.** Which public Actors from the [Apify Store](https://apify.com/store) does it use? Verify each one with `apify actors info <actor-id>`; if an Actor is private, deprecated or missing, stop and resolve it with the user.
3. **Inputs & outputs.** What does a working input JSON look like for each Actor, and what fields come back in the dataset items? → usage examples in SKILL.md.
4. **Costs.** What costs money, and where are the traps (per-result pricing, memory limits, runaway pagination)? → cost guardrails in `references/gotchas.md`.
5. **Failure modes.** What fails in practice (empty results, blocked pages, timeouts), and how should an agent recover? → error-recovery guidance.
6. **Attribution.** Author name and URL for credit? → optional frontmatter `author` / `author_url`. If any link carries an affiliate or referral parameter, or routes to a paid Actor the author owns, add the disclosure line CONTRIBUTING.md requires.

### Step 2 — Draft, validate, open the PR

1. Fork the repo and work on a branch of the fork.
2. Copy `skills/_template/` to `skills/apify-<name>/`.
3. Fill in `SKILL.md` (and optionally `references/`) from the interview answers.
4. Add the `metadata:` block to the frontmatter — `keywords` is required. Do **not** touch `.claude-plugin/marketplace.json`: the catalog is generated from frontmatter after merge, and editing it fails CI.
5. Validate locally — all three must pass:

   ```bash
   bash scripts/lint_telemetry.sh skills/apify-<name>
   uv run scripts/lint_references.py skills/apify-<name> --check-actors skills/apify-<name>
   uv run scripts/generate_agents.py
   ```

6. Do **not** commit the generated files (`.claude-plugin/marketplace.json`, `agents/AGENTS.md`, the README skills table) — the bot regenerates them after merge. Keep the PR inside your skill directory; changes to CI, `scripts/` or the template belong in a separate PR that a maintainer labels `maintainer`.
7. Open the PR with `gh pr create`, filling in the PR template. Check a box only once it is actually true — CI fails the PR if the description is empty or any box is left unchecked.

### Hard rules

- Only **public Actors** from the Apify Store.
- **One skill per PR**, and nothing outside `skills/apify-<name>/`.
- Every `apify` CLI command in SKILL.md code blocks carries `--user-agent apify-awesome-skills/<skill-name>`, `--json` and `2>/dev/null` (see CONTRIBUTING.md for the documented exceptions).
- Frontmatter `name` = folder name (`apify-<name>`).
