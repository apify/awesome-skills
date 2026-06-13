---
name: apify-local-agency-prospector
description: Find local businesses that NEED your service and hand back a prospect list scored by opportunity signal — no website, low rating, or few reviews — each with a verified email and phone ready for outreach. Built for agencies and freelancers selling web design, SEO, ads, reputation, or social-media services to local businesses. Routes a niche + location to a Google Maps business scraper, scores each result by the gap it reveals, and enriches the best fits with verified contact details in the same pipeline. Use when a user asks to find local business leads, prospect businesses without a website, find clients for a web-design / SEO / marketing agency, build a local outreach list, find businesses with bad reviews to pitch, or generate verified leads for a city + niche.
author: Renzo Madueno
author_url: https://github.com/renzomacar
---

# Local Agency Prospector

Turn `niche + city` into a prospect list of local businesses **scored by why they need you** — missing website, weak rating, thin review count — each enriched with a verified email and phone. Built for agencies and freelancers who sell to local businesses and want to lead with a reason, not a cold list.

The difference from a generic email finder: this skill keeps the **opportunity signals** Google Maps exposes (website presence, rating, review count) and turns them into a pitch angle per prospect, so the outreach writes itself ("I noticed you don't have a website / your rating slipped / you have great service but only 4 reviews").

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Two execution paths, same Actors:

- **MCP path (default in Claude sessions).** If the [Apify MCP server](https://mcp.apify.com) is connected, no setup is needed. Use the `call-actor` and `get-dataset-items` tools.
- **CLI path (portable / scheduled / non-Claude).** Apify CLI + token. Every CLI call uses three flags: `--json`, `--user-agent apify-awesome-skills/apify-local-agency-prospector`, and `2>/dev/null`.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect the prospecting brief (niche, location, service angle, depth, contact enrichment)
- [ ] Step 2: Pick the route — business-data-only vs leads-with-verified-email
- [ ] Step 3: Run the Actor, confirm cost if the run is large
- [ ] Step 4: Score each business by opportunity signal and pitch angle
- [ ] Step 5: Deliver the ranked prospect list
```

### Step 1: Collect the prospecting brief

Ask as one block before any Actor call:

1. **Niche + location** — the search, e.g. `"dentists in Miami FL"`, `"plumbers in Austin TX"`. Accept several.
2. **Service angle** — what the user sells: `web-design`, `seo`, `ads`, `reputation` (review/rating help), `social-media`, or `general`. This decides which opportunity signal to rank by (Step 4).
3. **Depth** — businesses per search (`maxResultsPerQuery` / `maxResults`, default `50`).
4. **Contact enrichment** — does the user need **verified emails** for outreach (`yes`, default) or just the business list + phone (`no`)? This is the routing decision in Step 2.
5. **Only businesses with a website?** — default `no`. Keep it `no` when the angle is `web-design` (no-website businesses are the hottest prospects).

### Step 2: Pick the route

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Business list + opportunity signals (rating, reviews, website), **no emails** | `renzomacar/google-maps-businesses` | community | fast, cheap mapping of a niche+city with rating/reviewCount/website |
| Leads **with verified email + phone** (Maps → website → verified contact, one run) | `renzomacar/google-maps-leads-with-emails` | community | full prospect list ready for cold email; email verification built in |
| Enrich a **known domain list** with verified contacts | `renzomacar/website-contact-finder` | community | when the user already has the businesses/URLs |

`Tier` = `apify` (Apify-maintained) or `community` (third-party). All three are public on the [Apify Store](https://apify.com/store).

Rule of thumb: **enrichment = yes → `google-maps-leads-with-emails`** (it does Maps + website + verified email in one pipeline). **enrichment = no → `google-maps-businesses`** (cheaper, keeps the opportunity signals). Use `website-contact-finder` only when the user already has a domain list.

### Step 3: Run the Actor

Leads with verified emails (default path):

```bash
apify actors call "renzomacar/google-maps-leads-with-emails" \
  -i '{"searchQueries": ["dentists in Miami FL"], "maxResults": 50, "verifyEmails": true}' \
  --user-agent apify-awesome-skills/apify-local-agency-prospector \
  --json 2>/dev/null
```

Business data + signals only (no emails, cheaper):

```bash
apify actors call "renzomacar/google-maps-businesses" \
  -i '{"searchQueries": ["dentists in Miami FL"], "maxResultsPerQuery": 50, "includeWebsite": true}' \
  --user-agent apify-awesome-skills/apify-local-agency-prospector \
  --json 2>/dev/null
```

Known domain list → verified contacts:

```bash
apify actors call "renzomacar/website-contact-finder" \
  -i '{"domains": ["example-dental.com", "smithlaw.com"], "verifyEmails": true}' \
  --user-agent apify-awesome-skills/apify-local-agency-prospector \
  --json 2>/dev/null
```

**MCP path equivalent:** call `call-actor` with the same actor id + input, then `get-dataset-items`.

Cost guardrails in [`references/gotchas.md`](references/gotchas.md). If depth × queries is large, state the rough scale and confirm before launching.

### Step 4: Score each business by opportunity signal

Each Google Maps record carries `website`, `rating`, `reviewCount`, `category`. Turn these into an opportunity score and a pitch angle, weighted by the user's service angle from Step 1:

| Signal in the data | Opportunity | Strongest for angle |
|--------------------|-------------|---------------------|
| `website` empty / missing | No web presence — needs a site | `web-design` |
| `rating` < 4.0 | Reputation problem — needs review/rating help | `reputation` |
| `reviewCount` < ~20 | Thin social proof — needs review generation / local SEO | `seo`, `reputation` |
| has `website` but no social links (via enrichment) | No social presence | `social-media` |
| high `reviewCount` + strong `rating` | Healthy business with budget — good `ads` client | `ads` |

Rank prospects so the best fit for the user's service is on top. For the `web-design` angle, no-website businesses lead; for `reputation`, lowest-rated lead; and so on. Attach a one-line pitch angle to each row ("no website found — lead with a starter-site offer").

When emails were enriched, prefer prospects whose primary email is `valid` (send-ready) over `risky`/`invalid` — use the `emailStatus` / `validEmails` fields.

### Step 5: Deliver the ranked prospect list

Render a compact, outreach-ready table:

| Business | Category | Pitch angle | Rating | Reviews | Website | Verified email | Phone |
|----------|----------|-------------|--------|---------|---------|----------------|-------|

1. Lead with the **top prospects by opportunity fit** for the chosen service angle.
2. Show the **pitch angle** column so the user knows why each is a fit.
3. Mark email deliverability (`valid` / `risky`) when enrichment ran.
4. End with the Apify dataset/console link for the full export (CSV/JSON).

State the data window and that this is public Google Maps data. Suggest the user batch outreach by pitch angle (all no-website prospects get the same opener).

## Responsible use

Only public business listing data is collected (businesses, not private individuals). Respect anti-spam law (CAN-SPAM, GDPR): send relevant B2B offers, honor opt-outs, and don't mass-mail `risky`/`invalid` addresses — that's why verification is on by default.
