<skills>

# Awesome Apify Skills

Community collection of Apify agent skills for web data extraction, scraping, and automation. Each skill is a `SKILL.md` file that teaches you how to accomplish a specific task using [Apify Actors](https://apify.com/store).

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. Skills follow the [Agent Skills open standard](https://agentskills.io/specification).

## Available skills

Read a skill's SKILL.md before using it — that's where the full instructions live.

<available_skills>

- **apify-ads-intelligence** by [Sameh Jarour](https://github.com/samehjarour) → `skills/apify-ads-intelligence/SKILL.md`: Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries.
- **apify-ai-search-visibility-tracker** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-ai-search-visibility-tracker/SKILL.md`: Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, see if their brand shows up in AI search, discover which prompts competitors rank for in AI search, find citation opportunities, or audit a website for AI visibility readiness.
- **apify-booking-host-leads** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-booking-host-leads/SKILL.md`: Find and enrich B2B leads from Booking.com - hotels, apartments, and vacation rentals - and pull each host's or property manager's real contact details (email, phone, company name, registration number). Use when the user says things like "get emails from Booking.com", "Booking.com lead generation", "find tour operator / property manager / host contacts", "scrape accommodation owner emails", or "build a list of Booking hosts". The host's email is usually already inside the Booking scraper's traderInfo field (EU/AU trader-transparency disclosure) - this skill leads with that and uses a Google Maps email scraper only as a fallback, instead of relying on Google Maps first (which mostly returns the wrong business).
- **apify-buying-signal-detection** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-buying-signal-detection/SKILL.md`: Set up a recurring buying-signal detection pipeline that finds companies showing buying intent across three signal types — job postings (hiring for the persona), fundraising events (recent raises), and LinkedIn content (pain-point posts, hiring announcements) — then aggregates results into a deduplicated leads.csv with the signal source, evidence URL, and detection timestamp per row. Split-schedule architecture — Apify Actor Tasks pull raw data on their own cadence, a Claude-side aggregation task normalizes, deduplicates against a blacklist, and appends new leads with a weekly-idempotent guard. Use when the user says "find companies with buying signals", "detect intent signals for outbound", "set up a weekly lead pipeline", "monitor hiring signals for lead gen", "track startup funding leads", "find LinkedIn buying signals", "schedule Apify Actors for prospecting", "build a signals-based lead list", or "set up buying-intent monitoring for my ICP".
- **apify-easy-competitive-intelligence** by [chocholous](https://github.com/chocholous) → `skills/apify-easy-competitive-intelligence/SKILL.md`: This skill should be used when the user asks to "analyze a competitor", "compare pricing", "competitive landscape", "market research", "what do customers think", "review intelligence", "hiring signals", "content strategy", "SEO battle", "build a battlecard", "competitive analysis", "who are the players", "who competes with", "market intelligence", "competitive positioning", "deep dive on a company", "board prep", "SWOT analysis", "how does [X] compare to [Y]", or mentions competitor analysis, pricing comparison, customer sentiment, or market landscape research. Requires Apify CLI or Apify MCP server.
- **apify-ecommerce** by [Luis Pinto](https://github.com/luispintoapify) → `skills/apify-ecommerce/SKILL.md`: Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence.
- **apify-financial-services** → `skills/apify-financial-services/`: Financial company intelligence — news monitoring (33 sources), social listening (Reddit, Twitter/X, Trustpilot), and public registry lookups (11 European countries). 3 skills + portfolio-sweep command.
- **apify-google-maps-leads** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-google-maps-leads/SKILL.md`: Build a local-business lead database from Google Maps in one Apify pipeline: search by target audience + geography, enrich each place with company contacts from its website, leads enrichment (names, emails, phones, LinkedIn), Instagram + Facebook profiles, and optionally reviews for lead scoring. For places with no named contacts, escalate to apify/ai-web-scraper to pull owner / decision-maker names from the business website. Backfill missing phones via scalelist/phone-finder and missing emails via scalelist/email-finder. Use when the user asks to build a lead list from Google Maps, scrape local businesses, generate B2B leads by city/industry, find owner/decision-maker contacts for restaurants / dentists / gyms / hotels / any local vertical, score leads by review volume or rating, or says "Google Maps lead-gen pipeline", "leads from Maps", "prospect local businesses", "scrape Google Maps for outreach", "find companies in <city>", or mentions chaining Google Maps + AI web scraper + Scalelist Actors.
- **apify-influencer-brand-collabs** by [Natasha Lekh](https://github.com/natashalekh) → `skills/apify-influencer-brand-collabs/SKILL.md`: Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks who collabs with a brand, which brands a creator has done paid posts for, wants to audit an influencer's branded-content history, or wants to scope a brand's sponsorship roster. **Triggers:** - "who collabs with [brand] on Instagram?" - "what brands has [creator] done sponsored posts for?" - "find paid partnerships / branded content for [handle]" - "audit [influencer]'s brand deals" - "show me [brand]'s influencer roster" Works in either direction — brand → creators or creator → brands — and detects direction from the data, so don't ask the user to declare it. Requires Apify MCP tools.
- **apify-lead-scoring-enrichment** by [Fabian Maume](https://github.com/fmaume) → `skills/apify-lead-scoring-enrichment/SKILL.md`: Score and enrich a CSV of B2B leads using Apify Actors. Takes a CSV with company URLs, free-text scoring rules, and an enrichment preference; runs BuiltWith (tech stack), Website Content Crawler (content classification), and Contact Info Scraper (company metadata) for scoring; enriches with either department-specific contacts (Contact Info Scraper + Bulk Email Finder fallback) or copywriter discovery (Google Search Scraper → AI Web Scraper → Bulk Email Finder). Outputs an enriched CSV with a numeric score and a per-lead outreach_hook column that personalizes cold email copy (e.g. "uses Shopify → send Shopify install guide"). Use when user asks to score leads, qualify leads, enrich a lead list, detect a company's tech stack for outreach, find marketing/sales/engineering contacts at a list of companies, hunt down blog copywriters for guest-post pitches, personalize cold email at scale, or turn a raw domain list into a ready-to-pitch account list.
- **apify-link-prospecting-outreach** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-link-prospecting-outreach/SKILL.md`: Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building.
- **apify-verified-email-finder** by [Daniela Ryplová](https://github.com/danielarypl) → `skills/apify-verified-email-finder/SKILL.md`: Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative.
- **apify-x402-agentic-wallet** by [Martin Forejt](https://github.com/martinforejt) → `skills/apify-x402-agentic-wallet/SKILL.md`: Discover, pay for, and run any Apify Actor by paying USDC on Base over the x402 protocol with a Coinbase Agentic Wallet (awal) — no Apify account or API key. You buy one small, spend-capped prepaid Apify token, then run as many Actors as the request needs with it. Use when the user wants to use Apify tools without signing up, pay per use with crypto / USDC, set up an agentic wallet, mentions "x402", "awal", "agentic wallet", "Coinbase wallet", "pay with USDC", "no API key", or asks to pull live web data (social media, search, maps, marketplaces, news) while paying on-chain per use.

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
