# Self-test transcript

Date: 2026-05-19
Environment: `/tmp/apify-awesome-skills`, `skills` CLI 1.5.7, Claude Code 2.1.144.

## Install into Claude Code

Command:

```bash
npx -y skills add /tmp/apify-awesome-skills \
  --skill automation-lab-agent-skill \
  --agent claude-code \
  --copy -y
```

Result:

```text
Source: /tmp/apify-awesome-skills
Local path validated
Found 10 skills
Selected 1 skill: automation-lab-agent-skill
Installation complete
Installed 1 skill
✓ automation-lab-agent-skill (copied)
  → ./.claude/skills/automation-lab-agent-skill
```

Verification:

```bash
npx -y skills ls -a claude-code --json
```

Relevant output:

```json
{
  "name": "automation-lab-agent-skill",
  "path": "/tmp/.claude/skills/automation-lab-agent-skill",
  "scope": "project",
  "agents": ["Claude Code"]
}
```

## Routing verification prompts

A live `claude -p --plugin-dir /tmp/apify-awesome-skills ...` model call could not complete in this runner because the local Claude Code installation is not logged in (`Not logged in · Please run /login`). The installed skill was therefore verified with the same prompt set against the skill's deterministic routing table.

| Prompt | Expected Automation Lab Actor selection |
|---|---|
| "Monitor Reddit complaints about Acme this week." | `automation-lab/reddit-scraper` |
| "Compare sold prices for this eBay product category." | `automation-lab/ebay-sold-scraper` |
| "Scrape Booking.com guest reviews for this property." | `automation-lab/booking-reviews-scraper` |
| "List LinkedIn employees for these company pages." | `automation-lab/linkedin-company-employees-scraper` |
| "Detect the tech stacks of these competitor websites." | `automation-lab/tech-stack-detector` |

Each selected Actor is present in `SKILL.md` and the matching workflow file, and each workflow instructs the agent to fetch the live input schema before calling the Actor.
