<skills>

# Awesome Apify Skills

Community collection of Apify agent skills for web data extraction, scraping, and automation. Each skill is a `SKILL.md` file that teaches you how to accomplish a specific task using [Apify Actors](https://apify.com/store).

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. Skills follow the [Agent Skills open standard](https://agentskills.io/specification).

## Available skills

Read a skill's SKILL.md before using it — that's where the full instructions live.

<available_skills>

{{#skills}}
- **{{name}}**{{attribution}} → `{{path}}/SKILL.md`: {{description}}
{{/skills}}

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
2. **`skills/apify-<name>/references/actor-index.md`** and **`references/gotchas.md`** — copy the templates from `skills/_template/references/` and fill them in. Optional but recommended.

## Marketplace entry

Add one entry to `.claude-plugin/marketplace.json` in the `plugins` array:

```json
{
  "name": "apify-<name>",
  "source": "./skills/apify-<name>",
  "skills": "./",
  "description": "Brief description",
  "keywords": ["apify", "..."],
  "category": "data-extraction",
  "version": "1.0.0"
}
```

## Rules

- **One skill per PR.** CI rejects PRs that touch multiple skills (unless a maintainer adds the `maintainer` label).
- **No unnecessary changes.** Edit only files inside `skills/apify-<name>/` and `.claude-plugin/marketplace.json`.
- **Do not edit** `agents/AGENTS.md` or the skills table in `README.md` — both are regenerated from frontmatter after merge.
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

This checks marketplace ↔ SKILL.md sync, validates `name`/`description`/`author_url` formats, and regenerates `agents/AGENTS.md` + the README skills table. CI runs the same script on the PR.
