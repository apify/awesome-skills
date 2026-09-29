---
name: apify-linkedin-profile-intelligence
description: Turn LinkedIn profile URLs into validated, CRM-ready people records using the data-slayer/linkedin-profile-scraper Apify Actor. Use when the user says "refresh my CRM from LinkedIn URLs", "enrich a CSV of LinkedIn profiles", "get current titles and companies for these profile URLs", "find who changed jobs", "champion tracking", "build a stakeholder map from profile URLs", "refresh candidate records", "speaker research", or "turn LinkedIn URLs into structured people data". Defaults to profile-only enrichment; optional verified work-email enrichment only when explicitly requested.
author: Mayank Chaba
author_url: https://github.com/MayankChaba
metadata:
  category: data-extraction
  keywords: "linkedin, profile scraper, crm refresh, people enrichment, champion tracking, job change, sales intelligence, recruiting, apify actor"
---

# LinkedIn Profile Intelligence

Turn a list of LinkedIn profile URLs into current, structured people records — name, headline, current title and company, experience, education, skills, location — ready for a CRM, sheet, or AI workflow. No LinkedIn login or cookies.

**Disclosure:** the routed Actor (`data-slayer/linkedin-profile-scraper`) is built by the author; links use the author's UTM parameters for attribution.

## Example prompts

Prompts this skill handles:

- "Refresh these 200 LinkedIn profile URLs in my CRM — half the titles are stale"
- "Enrich this CSV of LinkedIn URLs with current role and company"
- "Compare this list against last quarter's snapshot — who changed jobs?"

Out of scope (the boundary):

- "Find me emails for every decision-maker at Acme Corp" — this skill enriches *known* profile URLs; discovering new people from a company is a different workflow (use a people/company search Actor instead).

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Identify the business outcome, source LinkedIn URLs, delivery format, and whether verified work email is actually required.
2. Normalize and deduplicate URLs. Preserve the original URL for traceability.
3. Default to profile-only enrichment. Enable email enrichment only when the user explicitly needs work emails and understands the added cost and latency.
4. Show the input count, selected mode, expected output, and delivery format before any paid run. Require confirmation for email enrichment or batches above ten profiles.
5. Run the Actor. Verify one output or explicit error per requested URL — do not silently discard failures.
6. Normalize only the fields required for the named workflow. Retain the untouched Actor dataset as evidence.
7. Deliver a concise run summary: requested, succeeded, failed, emails found / not found (if email mode), dataset link when available, and known limitations.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Profile records from URLs | `data-slayer/linkedin-profile-scraper` | community | Bulk URL → structured profile records, no cookies; ~$4 per 1,000 profiles |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "data-slayer/linkedin-profile-scraper" -i '{
      "linkedin_urls": [
        "https://www.linkedin.com/in/jane-doe-1234a5b/",
        "https://www.linkedin.com/in/john-smith-678c9d/"
      ]
    }' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-profile-intelligence \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

### Option B: Apify API

    curl -X POST "https://api.apify.com/v2/acts/data-slayer~linkedin-profile-scraper/runs?token=$APIFY_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"linkedin_urls": ["https://www.linkedin.com/in/jane-doe-1234a5b/"]}'

Poll the run, then fetch dataset items from the run's `defaultDatasetId`.

## Guardrails

- Treat public-profile data as personal data. Use it only for the user's stated legitimate workflow.
- Do not infer protected or sensitive traits.
- Do not claim an email is verified unless the Actor returns a verification result.
- A missing email is not a failed profile scrape. Report profile and email outcomes separately.
- Do not promise job-change detection from a single snapshot. Compare two dated snapshots or an authoritative CRM baseline.
- Do not send outreach, update a CRM, or publish records unless the user separately requests that write.
- Never bypass Actor pricing, charge limits, platform policies, or source-site controls.

## Output shape

Return the smallest useful table for the workflow, followed by failures and a provenance note. Prefer stable fields such as requested URL, canonical LinkedIn URL, name, headline, current title, current company, company domain, location, email, verification status, and captured-at timestamp.
