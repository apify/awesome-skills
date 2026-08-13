<skills>

# Awesome Apify Skills

Community collection of Apify agent skills for web data extraction, scraping, and automation. Each skill is a `SKILL.md` file that teaches you how to accomplish a specific task using [Apify Actors](https://apify.com/store).

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. Skills follow the [Agent Skills open standard](https://agentskills.io/specification).

## Available skills

Read a skill's SKILL.md before using it — that's where the full instructions live.

<available_skills>

{{#skills}}
- **{{name}}**{{attribution}} → `{{path}}`: {{description}}
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
