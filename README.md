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
| [`apify-audience-analysis`](skills/apify-audience-analysis/SKILL.md) | Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and TikTok. | — |
| [`apify-brand-reputation-monitoring`](skills/apify-brand-reputation-monitoring/SKILL.md) | Track reviews, ratings, sentiment, and brand mentions across Google Maps, Booking.com, TripAdvisor, Facebook, Instagram, YouTube, and TikTok. Use when user asks to monitor brand reputation, analyze reviews, track mentions, or gather customer feedback. | — |
| [`apify-competitor-intelligence`](skills/apify-competitor-intelligence/SKILL.md) | Analyze competitor strategies, content, pricing, ads, and market positioning across Google Maps, Booking.com, Facebook, Instagram, YouTube, and TikTok. | — |
| [`apify-content-analytics`](skills/apify-content-analytics/SKILL.md) | Track engagement metrics, measure campaign ROI, and analyze content performance across Instagram, Facebook, YouTube, and TikTok. | — |
| [`apify-ecommerce`](skills/apify-ecommerce/SKILL.md) | Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence. | — |
| [`apify-influencer-discovery`](skills/apify-influencer-discovery/SKILL.md) | Find and evaluate influencers for brand partnerships, verify authenticity, and track collaboration performance across Instagram, Facebook, YouTube, and TikTok. | — |
| [`apify-lead-generation`](skills/apify-lead-generation/SKILL.md) | Generates B2B/B2C leads by scraping Google Maps, websites, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search. Use when user asks to find leads, prospects, businesses, build lead lists, enrich contacts, or scrape profiles for sales outreach. | — |
| [`apify-market-research`](skills/apify-market-research/SKILL.md) | Analyze market conditions, geographic opportunities, pricing, consumer behavior, and product validation across Google Maps, Facebook, Instagram, Booking.com, and TripAdvisor. | — |
| [`apify-trend-analysis`](skills/apify-trend-analysis/SKILL.md) | Discover and track emerging trends across Google Trends, Instagram, Facebook, YouTube, and TikTok to inform content strategy. | — |
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
