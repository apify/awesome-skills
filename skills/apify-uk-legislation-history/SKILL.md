---
name: apify-uk-legislation-history
description: "Fetch the point-in-time amendment history of a UK Act or Statutory Instrument from legislation.gov.uk, including diffs between historical versions. Use when a user asks what a UK law said on a past date, how a section changed over time, to track amendments to a specific Act/SI, or to build a timeline of legislative changes. Also covers extracting the title and meta description from any URL for SEO audits or data enrichment."
author: yummy_persimmon_er1
author_url: https://apify.com/yummy_persimmon_er1
metadata:
  category: data-extraction
  keywords: "uk legislation, legislation.gov.uk, point-in-time law, statutory instrument, amendment history, legal diff, seo meta extractor, title extractor"
---

# UK Legislation History & URL Meta Extractor

Fetch the full point-in-time amendment history of a UK Act or Statutory
Instrument (with diffs between versions), or pull the title and meta
description from any URL for quick SEO/enrichment checks.

Disclosure: the author of this skill owns both Actors it routes to
(`yummy_persimmon_er1/uk-legislation-history` and
`yummy_persimmon_er1/url-title-meta-extractor`). Both are pay-per-event
Actors on the Apify Store; no referral or tracking parameters are used
anywhere in this skill.

## Example prompts

Prompts this skill handles:

- "What did section 9 of the Consumer Rights Act 2015 say before it was amended?"
- "Give me every historical version of this Statutory Instrument with diffs."
- "Extract the page title and meta description from these 20 URLs for an SEO audit."

Out of scope (the boundary):

- General legal advice or interpretation of what a law means — this returns
  the sourced text and diffs only, not legal analysis. Send that to a
  qualified professional.
- Non-UK legislation (this Actor is scoped to legislation.gov.uk).

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Identify the legislation.gov.uk Act/SI URL (or ask the user for it) —
   e.g. `https://www.legislation.gov.uk/ukpga/2015/15` for the Consumer
   Rights Act 2015.
2. Run `uk-legislation-history` with that URL. For a single section, pass
   `sections: ["9"]`; for a whole Act, leave `sections` empty and set
   `maxSections` (default 5, or `0` for no cap — expect ~5s/section under
   legislation.gov.uk's own polite rate limit).
3. Set `includeFullHistory: true` to get every point-in-time version with
   diffs, or `false` for just the current text plus change dates (faster).
4. For a quick title/meta check on any URL instead, run
   `url-title-meta-extractor` with a list of URLs.
5. Deliver results: version dates, diffs, and a link to the Apify dataset
   for the full record.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| UK Act/SI point-in-time history + diffs | `yummy_persimmon_er1/uk-legislation-history` | community | Legal research, compliance timelines, tracking amendments |
| Page title + meta description extraction | `yummy_persimmon_er1/url-title-meta-extractor` | community | SEO audits, data enrichment, quick research |

## Calling Actors — choose your interface

Skills in this repo can call Actors via any of these interfaces. Pick the one
that fits your runtime; cross-tool compatibility is your responsibility.

### Option A: Apify CLI (recommended for portability)

    apify actors call "yummy_persimmon_er1/uk-legislation-history" \
      -i '{"actUrl": "https://www.legislation.gov.uk/ukpga/2015/15", "sections": ["9"], "includeFullHistory": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-uk-legislation-history \
      2>/dev/null

    apify actors call "yummy_persimmon_er1/url-title-meta-extractor" \
      -i '{"urls": ["https://example.com"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-uk-legislation-history \
      2>/dev/null

Other useful commands:

    # Fetch Actor schema
    apify actors info "yummy_persimmon_er1/uk-legislation-history" --input --json \
      --user-agent apify-awesome-skills/apify-uk-legislation-history 2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-uk-legislation-history 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- Empty diffs returned → the section had no amendments in the requested
  range; check `sections` matches the Act's real numbering (legislation.gov.uk
  numbers can include "A" suffixes, e.g. "9A").
- Run taking longer than expected on a full Act → `maxSections` is set to
  `0` (no cap) on a large Act; set an explicit cap or narrow `sections`.
- For detailed cost guardrails and recovery, see [references/gotchas.md](references/gotchas.md).
