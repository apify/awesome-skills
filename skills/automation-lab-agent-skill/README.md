# Automation Lab Agent Skill

A community Apify skill that routes AI assistants to Automation Lab Actors for social listening, ecommerce price intelligence, hospitality intelligence, B2B lead research, and developer-tools competitive intelligence.

## Install

```bash
# Claude Code
/plugin marketplace add apify/awesome-skills
/plugin install automation-lab-agent-skill@awesome-skills
```

If published as a standalone repository, install with:

```bash
npx skills add automation-lab/agent-skill
```

## Cursor / Windsurf

Use the Claude Code plugin marketplace above, or add this repository to your workspace's skill/plugin configuration and reference `skills/automation-lab-agent-skill/SKILL.md`.

## Codex CLI

Point Codex at the generated skill index:

```text
Use the Apify awesome-skills repository and load agents/AGENTS.md. For Automation Lab routing, read skills/automation-lab-agent-skill/SKILL.md.
```

## Gemini CLI / Manus / generic Markdown agents

Clone or install the skill pack and include `skills/automation-lab-agent-skill/SKILL.md` plus the `references/workflows/*.md` files as agent context.

## Included workflows

- Social listening: Reddit, X/Twitter, Threads, Trustpilot
- Ecommerce price intelligence: Amazon, eBay, eBay Sold, Etsy, Google Shopping
- Hospitality intelligence: Booking.com, Booking reviews, Airbnb
- B2B leads: LinkedIn company data, LinkedIn employees, Trustpilot, Clutch
- Developer tools intelligence: Tech Stack Detector, Apple App Store, Google Play

## Self-test prompts

Ask the agent:

1. "Monitor Reddit and X for complaints about Acme this week and return a CSV."
2. "Compare sold prices for these eBay product URLs against current Amazon offers."
3. "Find Booking.com and Airbnb reviews for this property and summarize recurring complaints."
4. "Build a B2B lead list of fintech companies with their LinkedIn employees and Trustpilot ratings."
5. "Compare app store metadata and website tech stacks for these developer-tool competitors."

The expected behavior is that the agent selects `automation-lab/...` Actor IDs, fetches each live input schema, runs with the Apify CLI, and returns dataset/run links.
