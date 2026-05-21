# Troubleshooting

Common failures and how to fix them. Listed roughly in order of how often they hit.

## Actor run `TIMED-OUT`

This is the single most common failure for `apify/link-prospecting-tool`. Public stats at time of skill authoring show 18 of 24 recent runs ending in `TIMED-OUT`.

There are two different timeouts and only one of them is the problem:

- **Actor run-level `timeoutSecs`** — Apify-side, defaults to 60000 (~16h). Almost never the cause.
- **API client wait timeout** — your-side, how long `run_actor.js` polls the run before giving up. This is what trips. The skill exposes it via `--timeout` (seconds).

Fixes, cheapest first:

1. **If the Actor is still RUNNING on Apify when the client gives up** — don't restart. Use `scripts/fetch_run_artifacts.js --run-id <id> --output <file> --timeout 1800` to poll the existing run and download all artifacts when it terminates. Same output shape as `run_actor.js --fetch-sub-datasets`. This is the most common case — runs frequently take 20-50 min on multi-keyword + multi-LLM-engine campaigns.
2. Raise `--timeout` for the next run. The default is now `1800`; on big campaigns (5+ keywords, all LLM engines on, email verification on) push to `2700` or `3600`.
3. Lower `organicResult` to 5. Each result triggers a WCC + Contact Details Scraper fan-out — halving this halves the bottleneck.
4. Cut the number of queries. Run two keywords at a time, not ten.
5. Disable AI platforms that you don't need (`enableChatGpt: false`, `enableAiMode: false`, `enablePerplexity: false`). AI Overviews stays on — it's free.
6. Lower `maxContactsPerDomain` to 1 for the first run; raise it only on subsequent runs against a known-good keyword.

Past run durations (for calibration):
- 3 keywords, all LLM engines off: ~20 min.
- 5 keywords, partial LLM coverage: ~52 min.
- 1 keyword, all LLM engines + email verification: exceeded 900s client wait at the 16-min mark with the default dataset still empty; recovered via `fetch_run_artifacts.js`.

## `Error: 'brand' is required` (or similar 400 from the Actor)

You called the Actor without the `brand` field. Re-prompt the user for their brand name (Step 1 anchor input #2) and rerun.

The Actor's required fields are `queries` and `brand`. Everything else has a default.

## `Author = Not found`

Expected for ~30% of pages. Many publishers don't expose author bylines in machine-readable form, and the AI Web Scraper sub-Actor only finds names when they're textually visible.

The skill writes `"Not found"` to the column and `"No author detected"` to `Notes`. Never invent a name. **Do not suggest external lookup tools or workarounds in Notes** — see SKILL.md Step 6 rule 11 for the rationale (the user knows where to look; the skill's job is to state what it found, not coach the user on third-party tools).

A secondary check the skill can run automatically: look in the WCC sub-dataset for the page's `metadata.author`, openGraph `article:author`, and JSON-LD `Person.name`. If any of those are populated, use them and set `Author Source` accordingly. The runner script's `--fetch-sub-datasets` flag already downloads the WCC dataset; the agent just needs to join on URL.

## `Contact Email = Not found`

The Contact Details Scraper sub-Actor missed this domain. Reasons it misses:

- The domain has no public team page or contact page.
- The published contacts are in roles outside the configured `department` filter (the skill defaults to `marketing` — see SKILL.md Step 3).
- The site uses contact forms only.

Skill response: write `"Not found"` and add `Notes: "No email found for this contact"`. **Do not suggest external lookup tools or workarounds.** Optional automatic fix: rerun with `department` widened — e.g., `["marketing", "sales", "operations", "consulting"]`.

## `0 leads returned`

The whole run completed but the All leads dataset is empty. Causes:

- Keyword too narrow (no SERP coverage).
- `ownDomains` + `competitorDomains` + `ignoreDomains` filtered out every result.
- Every surviving source already mentions or backlinks the user's brand (the Actor de-prioritises these for outreach).

Diagnostic steps:

1. Check the Mentions dataset — if it has rows, the filtering is the issue.
2. Loosen `ignoreDomains` (remove some entries).
3. Drop `competitorDomains` for one diagnostic run.
4. Raise `organicResult` to 20.
5. Broaden the keyword (drop modifiers, try plurals, try the head term).

## `Cannot find module 'xlsx'`

The `xlsx` dependency wasn't installed. Run `npm install` inside the skill's `scripts/` folder once. The runner script's `package.json` declares the dep.

## `APIFY_TOKEN not found`

The runner expects a `.env` file in the current working directory with `APIFY_TOKEN=...`. Get one from https://console.apify.com/account/integrations and create the file.

`node --env-file=.env` requires Node.js 20.6+.

## Costs higher than expected

The Actor's billing fan-outs through sub-Actors. A single run of `organicResult: 10` with all four AI platforms enabled and `searchAuthorName: true` can easily cost 5-10x what the parent Actor's $0.02/query suggests.

Cost-shaving levers, ordered by impact:

1. `searchAuthorName: false` — saves $25 per 1k sources (this is the biggest single cost in many runs).
2. `organicResult: 5` instead of 10 — halves the WCC + Contact Details Scraper cost.
3. `enableChatGpt: false`, `enablePerplexity: false` — each one adds a per-result Google Search Scraper cost.
4. `maxContactsPerDomain: 1` — fewer Contact Details Scraper calls per domain.
5. Tighter `ignoreDomains` — exclude obvious non-targets before they get crawled.

`enableAiOverviews` is free (parsed from the SERP that's already fetched), so keep it on regardless.

## Run completed but only some sub-datasets were fetched

The `--fetch-sub-datasets` flag walks the Sub-Actor results index and downloads four sibling files: `*_mentions.json`, `*_authors.json`, `*_serp.json`, `*_wcc.json`. If one is missing:

- `*_authors.json` missing → `searchAuthorName: false` for this run. Re-enable and rerun if you need author names.
- `*_wcc.json` missing → all sources were filtered out before crawling. Almost always paired with `0 leads returned`. See that section.
- `*_serp.json` missing → no organic SERP scraping happened. Should not occur unless the Actor's behavior changed; check the parent run's Sub-Actor index manually in the Apify console.

## "Brand mentioned everywhere — no outreach targets"

If the user's brand is already widely cited, the All leads dataset will be small even on a successful run. This is a feature, not a bug — the Actor specifically routes leads to sources that don't yet link back. To find sources that mention but don't link:

- Confirm `includeMention: true` (default). This pulls in mention-only sources for outreach.
- If the user wants pure cold (no mentions yet), set `includeMention: false` — but then mention-only sites are also excluded.

## Domain in `ownDomains` still shows up as a prospect

The Actor's domain matching is case-insensitive but exact-suffix. If the user owns `acme.com` and the source is on `blog.acme.com`, the filter catches it. If the user owns `acme.io` and the source is on `getacme.com`, the filter misses — add the variant explicitly.
