# influencer-brand-collabs (skill)

A Claude Code skill that teaches an agent how to surface Instagram
brand–creator partnerships by chaining four Apify Actors against Meta's
public Ad Library.

Distilled from the production mini-tool at
`mini-tools-main/src/app/api/tools/influencer-brand-collabs/route.ts`.

## What it covers

- Resolving a target's Facebook `fbid` from their Instagram handle
- Building the Meta Ad Library "branded content" URL
- Running `apify/brand-collaboration-scraper` against that URL
- Optional content enrichment (likes / comments / views) via the
  Instagram post and reel scrapers
- Optional profile enrichment (followers, bio, verified) on the
  *result* side — never the input
- Detecting direction (brand-to-creators vs creator-to-brands)
  empirically from the data, not from `isBusinessAccount`
- The URL-parsing edge cases (`_u/` / `_n/` deep links, reserved
  paths), engagement formula, and weekly timeline aggregation

## When it activates

Natural-language asks like:

- "Who collabs with Nike on Instagram?"
- "What brands has @bellahadid done sponsored posts for?"
- "Show me Adidas's recent influencer roster"
- "Audit @cristiano's branded-content history"

See the `description:` block in `SKILL.md` for the full trigger list.

## Requirements

Apify MCP tools must be available in the session:

- `mcp__claude_ai_Apify__call-actor`
- `mcp__claude_ai_Apify__fetch-actor-details`
- `mcp__claude_ai_Apify__get-actor-output`

Plus an Apify account with credits for:
`apify/instagram-profile-scraper`, `apify/brand-collaboration-scraper`,
`apify/instagram-post-scraper`, `apify/instagram-reel-scraper`.

## Install

Pick one:

```bash
# Global — available in every Claude Code session
ln -s "$PWD" ~/.claude/skills/influencer-brand-collabs

# Project-local — only loaded in that repo
ln -s "$PWD" /path/to/repo/.claude/skills/influencer-brand-collabs
```

Use a symlink (not a copy) so future edits to `SKILL.md` here propagate.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The skill itself — loaded into the agent's context when triggered |
| `README.md` | This file — human-facing overview |
