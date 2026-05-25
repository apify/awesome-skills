# Awesome Apify Skills

[![skills.sh](https://skills.sh/b/apify/awesome-skills)](https://skills.sh/apify/awesome-skills)

Community collection of [Apify](https://apify.com) agent skills for web scraping, data extraction, and automation.

> Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. This repo collects community contributions that follow the same [agentskills.io](https://agentskills.io/specification) open standard.

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
| [`apify-ai-search-visibility-tracker`](skills/apify-ai-search-visibility-tracker/SKILL.md) | Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, or see if their brand shows up in AI search. | — |
| [`apify-audience-analysis`](skills/apify-audience-analysis/SKILL.md) | Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and TikTok. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-brand-reputation-monitoring`](skills/apify-brand-reputation-monitoring/SKILL.md) | Track reviews, ratings, sentiment, and brand mentions across Google Maps, Booking.com, TripAdvisor, Facebook, Instagram, YouTube, and TikTok. Use when user asks to monitor brand reputation, analyze reviews, track mentions, or gather customer feedback. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-competitor-intelligence`](skills/apify-competitor-intelligence/SKILL.md) | Analyze competitor strategies, content, pricing, ads, and market positioning across Google Maps, Booking.com, Facebook, Instagram, YouTube, and TikTok. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-content-analytics`](skills/apify-content-analytics/SKILL.md) | Track engagement metrics, measure campaign ROI, and analyze content performance across Instagram, Facebook, YouTube, and TikTok. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-easy-competitive-intelligence`](skills/apify-easy-competitive-intelligence/SKILL.md) | This skill should be used when the user asks to "analyze a competitor", "compare pricing", "competitive landscape", "market research", "what do customers think", "review intelligence", "hiring signals", "content strategy", "SEO battle", "build a battlecard", "competitive analysis", "who are the players", "who competes with", "market intelligence", "competitive positioning", "deep dive on a company", "board prep", "SWOT analysis", "how does [X] compare to [Y]", or mentions competitor analysis, pricing comparison, customer sentiment, or market landscape research. Requires Apify CLI or Apify MCP server. | — |
| [`apify-ecommerce`](skills/apify-ecommerce/SKILL.md) | Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence. | [Luis Pinto](https://github.com/luispintoapify) |
| [`apify-financial-services`](skills/apify-financial-services/) | Financial company intelligence — news monitoring (33 sources), social listening (Reddit, Twitter/X, Trustpilot), and public registry lookups (11 European countries). 3 skills + portfolio-sweep command. | — |
| [`apify-influencer-brand-collabs`](skills/apify-influencer-brand-collabs/SKILL.md) | Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks who collabs with a brand, which brands a creator has done paid posts for, wants to audit an influencer's branded-content history, or wants to scope a brand's sponsorship roster. **Triggers:** - "who collabs with [brand] on Instagram?" - "what brands has [creator] done sponsored posts for?" - "find paid partnerships / branded content for [handle]" - "audit [influencer]'s brand deals" - "show me [brand]'s influencer roster" Works in either direction — brand → creators or creator → brands — and detects direction from the data, so don't ask the user to declare it. Requires Apify MCP tools. | — |
| [`apify-influencer-discovery`](skills/apify-influencer-discovery/SKILL.md) | Find and evaluate influencers for brand partnerships, verify authenticity, and track collaboration performance across Instagram, Facebook, YouTube, and TikTok. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-lead-generation`](skills/apify-lead-generation/SKILL.md) | Generates B2B/B2C leads by scraping Google Maps, websites, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search. Use when user asks to find leads, prospects, businesses, build lead lists, enrich contacts, or scrape profiles for sales outreach. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-link-prospecting-outreach`](skills/apify-link-prospecting-outreach/SKILL.md) | Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building. | — |
| [`apify-market-research`](skills/apify-market-research/SKILL.md) | Analyze market conditions, geographic opportunities, pricing, consumer behavior, and product validation across Google Maps, Facebook, Instagram, Booking.com, and TripAdvisor. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-trend-analysis`](skills/apify-trend-analysis/SKILL.md) | Discover and track emerging trends across Google Trends, Instagram, Facebook, YouTube, and TikTok to inform content strategy. | [Dušan Vystrčil](https://github.com/vystrcild) |
| [`apify-verified-email-finder`](skills/apify-verified-email-finder/SKILL.md) | Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative. | — |
<!-- END_SKILLS_TABLE -->

## Add your skill

See [CONTRIBUTING.md](CONTRIBUTING.md) — 1-minute setup.

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
