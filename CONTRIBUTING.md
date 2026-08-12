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
4. **Add** a `metadata:` block to your SKILL.md frontmatter — `keywords: "kw-one, kw-two, ..."` (required) and optionally `category:` (defaults to `data-extraction`). Do **not** touch `.claude-plugin/marketplace.json` — it is generated from frontmatter after merge.
5. **Open a PR** — CI validates, a maintainer reviews and merges

## Rules

- **One skill per PR.** CI enforces this. Exception: maintainers can add a `maintainer` label.
- **No unnecessary changes.** Edit only files inside your skill dir. Don't touch `.claude-plugin/marketplace.json`, `agents/AGENTS.md` or the skills table in `README.md` — all three are regenerated automatically after merge.
- **A skill PR is not an infra PR.** A PR that adds or edits a skill may change files inside `skills/apify-<name>/` and nothing else. Changes to `.github/`, `scripts/`, `agents/` or `skills/_template/` go in a separate PR that a maintainer labels `maintainer` — CI runs those files out of the PR checkout, so they decide how every submission is validated. Doc-only PRs (README prose, this file, `LICENSE`) need no label.
- **Use Apify Actors only** — publicly available on the [Apify Store](https://apify.com/store).
- **Disclose financial interest.** Affiliate/referral parameters on links (e.g. `?fpr=…`)
  and routing to paid Actors you own are allowed, but the skill must say so — add a short
  disclosure line next to the `author` credit (e.g. "Links use the author's Apify affiliate
  code; routed Actors are built by the author."). CI warns on undisclosed referral params.

## Quality (recommended, not required)

The `skills/_template/` shows the recommended structure with these optional pieces:

- **Apify CLI pattern** with three standard flags (`--json`, `--user-agent`, `2>/dev/null`)
- **`references/actor-index.md`** — full Actor routing table
- **`references/gotchas.md`** — cost guardrails and error recovery
- **`author` + `author_url`** in the frontmatter — you get credit in the catalog
- **Example prompts** — one to three real prompts the skill handles, and one it
  deliberately does not (the boundary). Reviewers use these as the input for a live test.

For a polished reference implementation, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## After you open a PR

CI runs every check in one pass, so you see all problems at once instead of iterating.
A maintainer then reviews per [REVIEWING.md](REVIEWING.md) — expect one of: a merge
(small fixes are applied for you, with credit), a specific list of changes in the form
`path: problem — fix`, or a consolidation suggestion if the skill overlaps an existing
one.

Updating an existing skill works the same way as adding one: one skill per PR, edit only
that skill's directory.

## FAQ

**Must I use the Apify CLI?**
No. We recommend it for cross-tool compatibility, but anything works — the [Apify MCP connector](https://mcp.apify.com), an MCP client of your choice, or [mcpc](https://github.com/apify/mcpc). Cross-tool compatibility is your responsibility.

**Where do generated files live?**
`agents/AGENTS.md` and the skills table in `README.md`. CI regenerates both after merge — you don't commit them.

**Can I test locally?**
Yes. After editing, run `uv run scripts/generate_agents.py` to validate. To preview installation, use [`npx skills add <path-to-your-fork>`](https://github.com/vercel-labs/skills).

## Telemetry on CLI commands

Every `apify` CLI invocation inside a `SKILL.md` file must follow three rules. CI will fail the PR if any of them are missing. Checked surfaces: fenced code blocks, indented code blocks, and inline code spans that carry flags (a span like `` `apify actors call X --json ...` `` is a command an agent will copy verbatim; a bare `` `apify actors call` `` mention in prose is fine).

### Rule 1 — `--user-agent` flag

Every `apify` CLI command must include:

```
--user-agent apify-awesome-skills/<skill-name>
```

where `<skill-name>` is the exact directory name of the skill (e.g., `apify-awesome-skills/apify-ai-search-visibility-tracker`).

**Important:** the namespace is `apify-awesome-skills/` — NOT `apify-agent-skills/`. The `apify-agent-skills/` namespace belongs to the separate [apify/agent-skills](https://github.com/apify/agent-skills) repository. Using it here blurs Snowflake attribution between the two repos.

### Rule 2 — `--json` flag

Always pass `--json` (or `--format json` for `datasets get-items`) to get machine-readable output. Exceptions: `--readme` fetches and `apify actors info --input` (bare schema fetch) return non-JSON output by design and are exempt; `--format csv` is allowed but CI emits a warning — make sure the skill handles non-JSON output deliberately. This ensures structured data that downstream tools and agents can parse reliably.

### Rule 3 — `2>/dev/null` stderr redirect

Always append `2>/dev/null` to suppress CLI progress messages and spinners. These messages are written to stderr and break JSON parsers that consume the combined output stream.

**Exception — `--readme`:** commands that fetch an Actor README (e.g. `apify actors info "<actor-id>" --readme`) return markdown, not JSON, so Rules 2 and 3 do not apply to them. Rule 1 (`--user-agent`) still does.

### Example

```bash
apify actors call apify/web-scraper \
  --input '{"startUrls": [{"url": "https://example.com"}]}' \
  --user-agent apify-awesome-skills/apify-my-skill \
  --json 2>/dev/null
```

CI checks these rules automatically via `scripts/lint_telemetry.sh`, and skill references (paths, Apify Store actors, URLs) via `scripts/lint_references.py` — both run on the skills your PR changes. Run them locally before opening a PR:

```bash
bash scripts/lint_telemetry.sh skills/apify-<name>
uv run scripts/lint_references.py skills/apify-<name> --check-actors skills/apify-<name>
```
