# Contributing

Add your Apify skill to this list in under a minute.

## Setup (1 minute)

1. **Fork** this repo
2. **Copy** `skills/_template/` → `skills/apify-<your-name>/`
3. **Edit** `skills/apify-<your-name>/SKILL.md`:
   - `name: apify-<your-name>` (must match the folder name)
   - `description: ...` (≤ 1024 chars; include trigger phrases a user would say)
   - `author`, `author_url` (optional)
   - Replace every `REPLACE` placeholder in the body
4. **Add** one entry to `.claude-plugin/marketplace.json` (see existing entries)
5. **Open a PR** — CI validates, a maintainer reviews and merges

## Rules

- **One skill per PR.** CI enforces this. Exception: maintainers can add a `maintainer` label.
- **No unnecessary changes.** Edit only files inside your skill dir and `.claude-plugin/marketplace.json`. Don't touch `agents/AGENTS.md` or the skills table in `README.md` — both are regenerated automatically.
- **Use Apify Actors only** — publicly available on the [Apify Store](https://apify.com/store).

## Quality (recommended, not required)

The `skills/_template/` shows the recommended structure with three optional pieces:

- **Apify CLI pattern** with three standard flags (`--json`, `--user-agent`, `2>/dev/null`)
- **`references/actor-index.md`** — full Actor routing table
- **`references/gotchas.md`** — cost guardrails and error recovery

For a polished reference implementation, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## FAQ

**Must I use the Apify CLI?**
No. We recommend it for cross-tool compatibility, but anything works — the [Apify MCP connector](https://mcp.apify.com), an MCP client of your choice, or [mcpc](https://github.com/apify/mcpc). Cross-tool compatibility is your responsibility.

**Where do generated files live?**
`agents/AGENTS.md` and the skills table in `README.md`. CI regenerates both after merge — you don't commit them.

**Can I test locally?**
Yes. After editing, run `uv run scripts/generate_agents.py` to validate. To preview installation, use [`npx skills add <path-to-your-fork>`](https://github.com/vercel-labs/skills).

## Telemetry on CLI commands

Every `apify` CLI invocation inside a `SKILL.md` file must follow three rules. CI will fail the PR if any of them are missing.

### Rule 1 — `--user-agent` flag

Every `apify` CLI command must include:

```
--user-agent apify-awesome-skills/<skill-name>
```

where `<skill-name>` is the exact directory name of the skill (e.g., `apify-awesome-skills/apify-ai-search-visibility-tracker`).

**Important:** the namespace is `apify-awesome-skills/` — NOT `apify-agent-skills/`. The `apify-agent-skills/` namespace belongs to the separate [apify/agent-skills](https://github.com/apify/agent-skills) repository. Using it here blurs Snowflake attribution between the two repos.

### Rule 2 — `--json` flag

Always pass `--json` (or `--format json` for `datasets get-items`) to get machine-readable output. This ensures structured data that downstream tools and agents can parse reliably.

### Rule 3 — `2>/dev/null` stderr redirect

Always append `2>/dev/null` to suppress CLI progress messages and spinners. These messages are written to stderr and break JSON parsers that consume the combined output stream.

### Example

```bash
apify actors call apify/web-scraper \
  --input '{"startUrls": [{"url": "https://example.com"}]}' \
  --user-agent apify-awesome-skills/apify-my-skill \
  --json 2>/dev/null
```

CI checks these rules automatically via `scripts/lint_telemetry.sh`. Run it locally before opening a PR:

```bash
bash scripts/lint_telemetry.sh
```
