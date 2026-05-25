---
name: apify-influencer-brand-collabs
description: |
  Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks
  who collabs with a brand, which brands a creator has done paid posts for, wants to audit an
  influencer's branded-content history, or wants to scope a brand's sponsorship roster.

  **Triggers:**
  - "who collabs with [brand] on Instagram?"
  - "what brands has [creator] done sponsored posts for?"
  - "find paid partnerships / branded content for [handle]"
  - "audit [influencer]'s brand deals"
  - "show me [brand]'s influencer roster"

  Works in either direction — brand → creators or creator → brands — and detects direction from the
  data, so don't ask the user to declare it. Requires Apify MCP tools.
---

# Influencer–Brand Collaborations

Surface Instagram branded-content partnerships by chaining four Apify Actors against Meta's Ad
Library. Distilled from the production `influencer-brand-collabs` mini-tool.

## When to use

- "Who has Nike paid to promote them this quarter?"
- "What brands does @bellahadid do sponsored posts for?"
- Auditing an account's branded-content history
- Building a competitor's influencer roster

**Don't use for:** organic mentions or tags (use a hashtag/mentions scraper), TikTok or YouTube
collabs (different platforms), generic competitor ads (query Meta Ad Library directly).

## Inputs to gather

1. **Instagram handle or URL** — `@adidas` or `https://www.instagram.com/adidas/`
2. **Lookback window** — days; default 90
3. **Enrichment toggles** (each adds cost + time):
   - **Content insights** — likes, comments, views per collab
   - **Profile enrichment** — followers, bio, verified status of the *other* side

Direction (brand vs creator) is detected empirically. Do not ask.

## The pipeline

| # | Actor | Purpose | Required |
|---|---|---|---|
| 1 | `apify/instagram-profile-scraper` | Resolve the target's Facebook `fbid` | ✓ |
| 2 | `apify/brand-collaboration-scraper` | Pull branded-content posts from Meta's Ad Library | ✓ |
| 3 | `apify/instagram-post-scraper` + `apify/instagram-reel-scraper` | Engagement metrics | optional |
| 4 | `apify/instagram-profile-scraper` (again) | Enrich the result-side partners | optional |

Call each via `mcp__claude_ai_Apify__call-actor`. Use `mcp__claude_ai_Apify__fetch-actor-details`
first if you've never run one of these and want the exact input schema.

### Step 1 — Resolve the target

```jsonc
// actor: apify/instagram-profile-scraper
{ "usernames": ["adidas"] }
```

Grab `fbid` from the first item. **No `fbid` → can't query Ad Library → stop and tell the user.**
Most common cause: private account.

### Step 2 — Build the Meta Ad Library URL

```
https://www.facebook.com/ads/library/branded_content/?id={fbid}&query={username}&target=instagram&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}
```

Date range = the lookback window (default 90 days, ending today).

### Step 3 — Fetch collaborations

```jsonc
// actor: apify/brand-collaboration-scraper
{ "startUrls": ["<ad library url>"], "resultsLimit": 10 }
```

Schema is **fixed**: every item has `creator` (always the influencer side) and `brandPartners[0]`
(always the brand side). Do not try to infer direction from these fields.

### Step 4 — Detect direction empirically

Count how often the target username appears on each side of the results:

- target appears more on `creator` side → **target is the influencer**; results are the **brands**
- target appears more on `brandPartners` side → **target is the brand**; results are the **creators**

> ⚠️ Do **not** use `isBusinessAccount` to infer this. It's unreliable — e.g. `@fifaworldcup` is a
> business account but appears as the creator of its own branded content.

### Step 5 — (optional) Content metrics

Split collab URLs by type:
- `/reel/...` → reel scraper
- `/p/...` or `/tv/...` → post scraper

```jsonc
// actor: apify/instagram-post-scraper
{ "username": ["<post urls>"], "resultsLimit": 1, "dataDetailLevel": "basicData" }

// actor: apify/instagram-reel-scraper
{ "username": ["<reel urls>"], "resultsLimit": 1 }
```

Match back to collabs via shortcode in the URL: `/(p|reel|tv)/([A-Za-z0-9_-]+)`.

**Engagement formula:** `likesCount + commentsCount + (videoViewCount ?? videoPlayCount ?? 0)`.

Run the two scrapers in parallel — they're independent.

### Step 6 — (optional) Enrich the *result* side

Collect unique usernames from the side that is **not** the target. Then:

```jsonc
// actor: apify/instagram-profile-scraper
{ "usernames": [<unique result-side usernames>] }
```

Only enrich the side the user actually cares about. The input handle is already known.

## What to present

After aggregation, surface:

- **Headline counts:** total collabs, unique partners, total engagement (if metrics enriched)
- **Top 5 collabs by engagement** — only meaningful when content insights were toggled on
- **Content-type mix:** Post vs Reel; Reels usually dominate engagement
- **Weekly timeline** across the date range — spikes reveal campaign launches
- **Per-partner card** (when profiles enriched): handle, full name, followers, verified, category,
  collabs in this run, avg engagement

For *who*-questions, the partner list alone is enough. Metrics only matter for
*which-was-best*-questions.

## URL parsing

Strip Instagram's `_u/` and `_n/` deep-link prefixes before extracting the handle:

```
/instagram\.com\/(?:_u\/|_n\/)?([A-Za-z0-9_.]+)/i
```

These slugs are **not** usernames — skip them:
`explore`, `reels`, `stories`, `direct`, `accounts`, `about`, `p`, `reel`, `tv`, `tags`,
`locations`, `_u`, `_n`.

## Pitfalls

- **Target is private** → profile scraper returns no `fbid`. Bail early with a clear message.
- **No results** → try in order: widen the date range, double-check the handle (strip `_u/`),
  confirm the account actually runs branded content. Meta only indexes ads they've classified as
  branded content.
- **Engagement is all zeros** → user skipped content enrichment. Offer to re-run with it on.
- **Direction looks wrong in the output** → re-check the empirical count. Don't trust
  `isBusinessAccount`.
- **Brand collabs with no metrics** are still answer-shaped for *who* questions — don't gate the
  whole flow on enrichment.

## Cost & time

Full 4-actor run: **~3–5 minutes**, a few cents of Apify compute. Order of magnitude:

| Enrichment | Actors run | Approx time |
|---|---|---|
| None | 2 | 1–2 min |
| + Content | 3–4 | 2–4 min |
| + Profiles | +1 | +30–60 s |

If the user just needs a partner list, skip both toggles.

## Reference implementation

Production route this skill was distilled from:
`mini-tools-main/src/app/api/tools/influencer-brand-collabs/route.ts` — full transformation logic,
error handling, and slimmed display shapes for each scraper's output.
