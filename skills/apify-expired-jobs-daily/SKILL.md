---
name: apify-expired-jobs-daily
description: "One run returns dated expired jobs: company, title, firstSeen, lastSeen, closedOn, absentObservations, URL and an asOf/n/historyCeilingDays receipt. Built for buyers of an expired jobs api who need a no-longer-listed date, not a filled claim. Monitor mode bills only new or changed closures. Uses the Apify Actor redomic/expired-jobs-daily. Use when the user asks to 'expired jobs api', 'expired jobs', 'closed jobs api', or wants Expired Jobs API: Dated Closures From 8 ATS results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "expired jobs api, expired jobs, closed jobs api, expired jobs daily"
author: Redomic
author_url: https://apify.com/redomic
---

# Expired Jobs API: Dated Closures From 8 ATS

One run returns dated expired jobs: company, title, firstSeen, lastSeen, closedOn, absentObservations, URL and an asOf/n/historyCeilingDays receipt. Built for buyers of an expired jobs api who need a no-longer-listed date, not a filled claim. Monitor mode bills only new or changed closures.

Disclosure: the routed Actor, `redomic/expired-jobs-daily`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Expired Jobs API: Dated Closures From 8 ATS results for mode search; closedWithinDays 7; maxItems 5"
- "Get Expired Jobs API: Dated Closures From 8 ATS results for mode search; closedWithinDays 30; maxItems 20"
- "Get Expired Jobs API: Dated Closures From 8 ATS results for mode search; closedWithinDays 0; maxItems 10"

Out of scope (the boundary):

- Personal contact data or logged-in content: this Actor reads public pages only.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Map the request onto the input fields below; fetch the live schema for anything unusual.
2. Run the Actor and read its dataset. Rows with a `_status` field are per-input status rows, not data.
3. Deliver a count, a short table of the key fields, and the dataset link or an export.

## Input

- `mode` (string): search returns filtered closure rows. detail checks job IDs or URLs, one status per input. monitor compares with the previous run and returns changeType new, changed or removed; an unchanged rerun cos
- `company` (string): Keep closures from this company name or board token, ignoring case. Empty means all companies.
- `keyword` (string): Keep closures whose title or department contains this text, ignoring case. Empty means all roles.
- `ats` (array): Limit to these ATS platforms. Empty means all.
- `roleFamilies` (array): Keep closures whose role family starts with any of these values, ignoring case: engineering covers every Engineering family (Backend/Fullstack, Data, ML/AI...); sales, marketing, healthcare and data w
- `closedWithinDays` (integer): Only closures dated in the last N days. 0 means the full tracked history. Search mode only; monitor compares the full history so a shifting window never looks like a removal.
- `minAbsentObservations` (integer): Daily snapshots in which the ad was absent before we call it a closure. The default 2 filters out one-day board flapping; set 1 to include same-day closures.
- `includeGeneralApplications` (boolean): Talent pools, 'general application' and template postings collect CVs rather than fill a role, so their disappearance is not a closed job. They are left out by default; turn this on to include them (e
- `jobIds` (array): Detail mode only: job IDs or job URLs from any scraper. Each input gets its own status row in the STATUS record, even when no closure was found.
- `maxItems` (integer): Maximum result rows returned and billed per run.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Expired Jobs API: Dated Closures From 8 ATS | `redomic/expired-jobs-daily` | community | expired jobs api |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/expired-jobs-daily" \
      -i '{"mode": "search", "closedWithinDays": 7, "minAbsentObservations": 2, "includeGeneralApplications": false, "maxItems": 500}' \
      --json \
      --user-agent apify-awesome-skills/apify-expired-jobs-daily \
      2>/dev/null

    apify actors info "redomic/expired-jobs-daily" --input --json \
      --user-agent apify-awesome-skills/apify-expired-jobs-daily 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-expired-jobs-daily 2>/dev/null
