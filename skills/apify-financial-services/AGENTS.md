# Agent Guide — Financial Services Plugin

This file is for AI agents. Humans → [README.md](README.md).

## Non-Claude Code agents (Cursor, Codex CLI, Antigravity, etc.)

These skills are tool-agnostic — markdown instructions + shell commands. No Claude Code
dependency beyond discovery. To use from any AI coding assistant:

1. Clone this repo (or point your agent at it)
2. Read the routing table below to pick the right skill
3. Open the relevant `skills/*/SKILL.md` and follow the workflow
4. `${CLAUDE_PLUGIN_ROOT}` in SKILL.md paths = root of this repository

## What this plugin does

Three skills for financial company intelligence:

| Skill | Trigger phrases | Data source |
|-------|----------------|-------------|
| `apify-financial-news` | "find news about X", "press coverage", "headlines", "news scan" | 33 verified Tier 1 sources + Google News |
| `apify-financial-osint` | "sentiment", "what are people saying", "social media mentions", "OSINT", "customer reviews" | Reddit, Twitter/X, Trustpilot |
| `apify-public-registries` | "look up company", "check registry", "IČO/KRS/LEI/CRN", "due diligence", "VAT status" | 11 European countries, 27 registry endpoints |

Each skill has its own `SKILL.md` with a step-by-step workflow checklist. Read the relevant
`SKILL.md` after matching the user's intent.

## Setup verification

Run these checks before first use:

```bash
# Apify CLI (required for news + OSINT, optional for registries)
apify --version && apify info 2>&1 | head -1 || echo "MISSING: npm install -g apify-cli && apify login"

# Python 3 (required for registry scripts)
python3 --version
```

## File locations

```
data/companies.json          ← shared portfolio (all 3 skills read this)
data/README.md               ← schema + how to add a company

skills/apify-financial-news/SKILL.md       ← news workflow
skills/apify-financial-osint/SKILL.md      ← OSINT workflow
skills/apify-public-registries/SKILL.md    ← registry workflow
```

## Commands

| Command | Trigger phrases | What it does |
|---------|----------------|--------------|
| `/portfolio-sweep [1d\|7d\|1y]` | "full portfolio scan", "weekly sweep", "complete data pull", "portfolio report" | Runs all 3 skills across all portfolio companies. Output saved to `output/`. |

## Skill routing rules

- News about a company → `apify-financial-news`
- Social sentiment, Reddit, Twitter, reviews → `apify-financial-osint`
- Official registry data, ownership, filings → `apify-public-registries`
- Marketing, social-listening campaigns → do NOT use this plugin (use apify/awesome-skills)
- Morning briefing formatting → out of scope

## Portfolio data

`data/companies.json` contains tracked companies with pre-computed queries and identifiers.
Each company entry has: `id`, `name`, `country`, `queries` (per-platform search terms),
`identifiers` (IČO, LEI, KRS, etc.), and platform-specific IDs (Glassdoor, Trustpilot, apps).

To add a company, follow the workflow in `data/README.md`.

## Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `apify: command not found` | Apify CLI not installed | `npm install -g apify-cli` |
| `You are not logged in` | Not authenticated | Run `apify login` |
| Empty Reddit results | `maxPosts` not set (default 50000 overloads) | Use `data/osint-targets.json` pre-built inputs |
| Registry script returns nothing | Missing API key for that country | Check REGISTRATION/*.md for access guide |
