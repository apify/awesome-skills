<a href="https://skills.sh/apify/awesome-skills"><img src="https://skills.sh/b/apify/awesome-skills" alt="skills.sh installs"></a>

<p align="center">
  <img src="https://docs.apify.com/img/apify_logo.svg" alt="Apify" width="96" height="96">
</p>

<h1 align="center">Awesome Apify Skills</h1>

<p align="center">
  <strong>Community-driven agent skills for AI coding assistants</strong>
</p>

<p align="center">
  <a href="https://apify.com"><img src="https://img.shields.io/badge/Powered%20by-Apify-20A34E?style=for-the-badge" alt="Powered by Apify"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache--2.0-555555?style=for-the-badge" alt="Apache 2.0"></a>
  <a href="#available-skills"><img src="https://img.shields.io/badge/Skills-13-246DFF?style=for-the-badge" alt="13 Skills"></a>
  <a href="https://apify.com/store"><img src="https://img.shields.io/badge/Actors-30%2C000%2B-F86606?style=for-the-badge" alt="30,000+ Actors"></a>
  <a href="https://github.com/apify/awesome-skills/stargazers"><img src="https://img.shields.io/github/stars/apify/awesome-skills?style=for-the-badge&color=9D97F4&label=Stars" alt="GitHub stars"></a>
</p>

<p align="center">
  <a href="#install">Quick start</a> &bull;
  <a href="#available-skills">Skills</a> &bull;
  <a href="#contribute">Contribute</a> &bull;
  <a href="#for-ai-agents">For AI agents</a> &bull;
  <a href="#support">Support</a>
</p>

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. This repo collects community contributions that follow the same [agentskills.io](https://agentskills.io/specification) open standard.

## What's a skill?

A skill is a `SKILL.md` file with YAML frontmatter that teaches an AI agent how to do a specific task with [Apify Actors](https://apify.com/store) — which Actors to use, how to build inputs, how to handle errors.

## Install

```bash
npx skills add apify/awesome-skills
```

Works with Claude Code, Codex, Cursor, Gemini CLI, Windsurf, OpenCode, and [50+ other agents](https://skills.sh). Pass `--list` to preview, `-s <name>` to install one specific skill.

## Available skills

<!-- BEGIN_SKILLS_TABLE -->
| Name | Description | Author |
|------|-------------|--------|
| [`apify-ads-intelligence`](skills/apify-ads-intelligence/SKILL.md) | Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries. | [Sameh Jarour](https://github.com/samehjarour) |
| [`apify-ai-search-visibility-tracker`](skills/apify-ai-search-visibility-tracker/SKILL.md) | Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, see if their brand shows up in AI search, discover which prompts competitors rank for in AI search, find citation opportunities, or audit a website for AI visibility readiness. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-booking-host-leads`](skills/apify-booking-host-leads/SKILL.md) | Find and enrich B2B leads from Booking.com - hotels, apartments, and vacation rentals - and pull each host's or property manager's real contact details (email, phone, company name, registration number). Use when the user says things like "get emails from Booking.com", "Booking.com lead generation", "find tour operator / property manager / host contacts", "scrape accommodation owner emails", or "build a list of Booking hosts". The host's email is usually already inside the Booking scraper's traderInfo field (EU/AU trader-transparency disclosure) - this skill leads with that and uses a Google Maps email scraper only as a fallback, instead of relying on Google Maps first (which mostly returns the wrong business). | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-buying-signal-detection`](skills/apify-buying-signal-detection/SKILL.md) | Set up a recurring buying-signal detection pipeline that finds companies showing buying intent across three signal types — job postings (hiring for the persona), fundraising events (recent raises), and LinkedIn content (pain-point posts, hiring announcements) — then aggregates results into a deduplicated leads.csv with the signal source, evidence URL, and detection timestamp per row. Split-schedule architecture — Apify Actor Tasks pull raw data on their own cadence, a Claude-side aggregation task normalizes, deduplicates against a blacklist, and appends new leads with a weekly-idempotent guard. Use when the user says "find companies with buying signals", "detect intent signals for outbound", "set up a weekly lead pipeline", "monitor hiring signals for lead gen", "track startup funding leads", "find LinkedIn buying signals", "schedule Apify Actors for prospecting", "build a signals-based lead list", or "set up buying-intent monitoring for my ICP". | [Fabian Maume](https://github.com/fmaume) |
| [`apify-easy-competitive-intelligence`](skills/apify-easy-competitive-intelligence/SKILL.md) | This skill should be used when the user asks to "analyze a competitor", "compare pricing", "competitive landscape", "market research", "what do customers think", "review intelligence", "hiring signals", "content strategy", "SEO battle", "build a battlecard", "competitive analysis", "who are the players", "who competes with", "market intelligence", "competitive positioning", "deep dive on a company", "board prep", "SWOT analysis", "how does [X] compare to [Y]", or mentions competitor analysis, pricing comparison, customer sentiment, or market landscape research. Requires Apify CLI or Apify MCP server. | [chocholous](https://github.com/chocholous) |
| [`apify-ecommerce`](skills/apify-ecommerce/SKILL.md) | Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence. | [Luis Pinto](https://github.com/luispintoapify) |
| [`apify-financial-services`](skills/apify-financial-services/) | Financial company intelligence — news monitoring (33 sources), social listening (Reddit, Twitter/X, Trustpilot), and public registry lookups (11 European countries). 3 skills + portfolio-sweep command. | — |
| [`apify-google-maps-leads`](skills/apify-google-maps-leads/SKILL.md) | Build a local-business lead database from Google Maps in one Apify pipeline: search by target audience + geography, enrich each place with company contacts from its website, leads enrichment (names, emails, phones, LinkedIn), Instagram + Facebook profiles, and optionally reviews for lead scoring. For places with no named contacts, escalate to apify/ai-web-scraper to pull owner / decision-maker names from the business website. Backfill missing phones via scalelist/phone-finder and missing emails via scalelist/email-finder. Use when the user asks to build a lead list from Google Maps, scrape local businesses, generate B2B leads by city/industry, find owner/decision-maker contacts for restaurants / dentists / gyms / hotels / any local vertical, score leads by review volume or rating, or says "Google Maps lead-gen pipeline", "leads from Maps", "prospect local businesses", "scrape Google Maps for outreach", "find companies in <city>", or mentions chaining Google Maps + AI web scraper + Scalelist Actors. | [Fabian Maume](https://github.com/fmaume) |
| [`apify-influencer-brand-collabs`](skills/apify-influencer-brand-collabs/SKILL.md) | Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks who collabs with a brand, which brands a creator has done paid posts for, wants to audit an influencer's branded-content history, or wants to scope a brand's sponsorship roster. **Triggers:** - "who collabs with [brand] on Instagram?" - "what brands has [creator] done sponsored posts for?" - "find paid partnerships / branded content for [handle]" - "audit [influencer]'s brand deals" - "show me [brand]'s influencer roster" Works in either direction — brand → creators or creator → brands — and detects direction from the data, so don't ask the user to declare it. Requires Apify MCP tools. | [Natasha Lekh](https://github.com/natashalekh) |
| [`apify-lead-scoring-enrichment`](skills/apify-lead-scoring-enrichment/SKILL.md) | Score and enrich a CSV of B2B leads using Apify Actors. Takes a CSV with company URLs, free-text scoring rules, and an enrichment preference; runs BuiltWith (tech stack), Website Content Crawler (content classification), and Contact Info Scraper (company metadata) for scoring; enriches with either department-specific contacts (Contact Info Scraper + Bulk Email Finder fallback) or copywriter discovery (Google Search Scraper → AI Web Scraper → Bulk Email Finder). Outputs an enriched CSV with a numeric score and a per-lead outreach_hook column that personalizes cold email copy (e.g. "uses Shopify → send Shopify install guide"). Use when user asks to score leads, qualify leads, enrich a lead list, detect a company's tech stack for outreach, find marketing/sales/engineering contacts at a list of companies, hunt down blog copywriters for guest-post pitches, personalize cold email at scale, or turn a raw domain list into a ready-to-pitch account list. | [Fabian Maume](https://github.com/fmaume) |
| [`apify-link-prospecting-outreach`](skills/apify-link-prospecting-outreach/SKILL.md) | Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-verified-email-finder`](skills/apify-verified-email-finder/SKILL.md) | Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-x402-agentic-wallet`](skills/apify-x402-agentic-wallet/SKILL.md) | Discover, pay for, and run any Apify Actor by paying USDC on Base over the x402 protocol with a Coinbase Agentic Wallet (awal) — no Apify account or API key. You buy one small, spend-capped prepaid Apify token, then run as many Actors as the request needs with it. Use when the user wants to use Apify tools without signing up, pay per use with crypto / USDC, set up an agentic wallet, mentions "x402", "awal", "agentic wallet", "Coinbase wallet", "pay with USDC", "no API key", or asks to pull live web data (social media, search, maps, marketplaces, news) while paying on-chain per use. | [Martin Forejt](https://github.com/martinforejt) |
<!-- END_SKILLS_TABLE -->

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) — 1-minute setup. Maintainers: [REVIEWING.md](REVIEWING.md) describes how incoming skill PRs are judged.

### Submit with your AI agent

Have your coding agent (Claude Code, Cursor, Codex, or any agent with shell access) do the mechanical work — paste this prompt:

> Fetch https://raw.githubusercontent.com/apify/awesome-skills/main/agents/AGENTS.md and follow its "Submitting a skill" flow. Interview me about my Apify skill, draft it in this repo's format, validate it locally, and open the PR.

## For AI agents

See [agents/AGENTS.md](agents/AGENTS.md) — same content as this README plus the contributing guide, in a format optimised for autonomous agents.

## Prerequisites

- [Apify account](https://apify.com)
- (Optional) [Apify CLI](https://docs.apify.com/cli): `npm install -g apify-cli`
- Authentication: `apify login` or `APIFY_TOKEN` env var ([get a token](https://console.apify.com/settings/integrations))

## Support

- [Apify Documentation](https://docs.apify.com)
- [Apify Discord](https://discord.gg/jyEM2PRvMU)
- [Agent Skills Specification](https://agentskills.io/specification)
