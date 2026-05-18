---
name: apify-REPLACE-skill-name
description: >-
  REPLACE: One or two sentences describing what the skill does, including
  trigger phrases a user would say (e.g. "scrape Amazon reviews", "find
  leads on LinkedIn"). Max 1024 characters per agentskills.io spec.
author: REPLACE Your Name
author_url: https://github.com/REPLACE-your-handle
---

# REPLACE: Skill Title

REPLACE: One-line summary of what this skill helps the agent accomplish.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. REPLACE: Understand the user's goal, pick the right Actor(s).
2. REPLACE: Fetch the Actor's input schema, build a valid input.
3. REPLACE: Run the Actor, confirm with user if estimated cost is significant.
4. REPLACE: Deliver results (count, format, link to dataset/console).

For a worked 4-step workflow, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| REPLACE | `apify/REPLACE-actor` | apify | REPLACE |
| REPLACE | `community/REPLACE-actor` | community | REPLACE |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

Skills in this repo can call Actors via any of these interfaces. Pick the one
that fits your runtime; cross-tool compatibility is your responsibility.

### Option A: Apify CLI (recommended for portability)

Works in any shell-capable agent. Three flags on every call:

    apify actors call "ACTOR_ID" -i 'JSON_INPUT' \
      --json \
      --user-agent apify-agent-skills/REPLACE-skill-name \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

Other useful commands:

    # Search Actors
    apify actors search "KEYWORDS" --json --limit 10 2>/dev/null

    # Fetch Actor schema
    apify actors info "ACTOR_ID" --input --json 2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json

For the canonical command set with all flags, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- REPLACE: common error 1 → fix
- REPLACE: common error 2 → fix
- For detailed cost guardrails and recovery, see [references/gotchas.md](references/gotchas.md).
