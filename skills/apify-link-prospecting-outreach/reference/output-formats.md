# Output Formats

The skill supports two output formats: `xlsx` (spreadsheet file) and `markdown` (table + email drafts inline in chat). Both share the same 30-column row schema and produce a `run_metadata.json` sidecar.

## Row schema (30 columns)

| # | Column | Type | Source | Notes |
|---|---|---|---|---|
| 1 | `SERP Position` | int or `"-"` | Google Search Scraper sub-dataset | Rank within organic results for the row's keyword. `"-"` for rows that surfaced only via AI engines. |
| 2 | `Source Engines` | string | Mentions dataset | Comma-joined list of engines (only those enabled in Step 1 input #9): "Google Organic", "ChatGPT", "Gemini", "Copilot", "Perplexity", "Google AI Mode", "Google AI Overview". |
| 3 | `Keyword` | string | Mentions dataset `queries[0]` | The keyword that surfaced the source. If a source appears for multiple keywords, emit one row per keyword. |
| 4 | `Article Title` | string | Google Search Scraper sub-dataset `title` (primary); WCC `metadata.title` (fallback). | |
| 5 | `Article URL` | URL | Mentions dataset `url` | |
| 6 | `Domain` | string | All leads dataset `domain` | |
| 7 | `Domain DR` | int 0–100 or `"-"` | Ahrefs `site-explorer-domain-rating` | `"-"` if Ahrefs has no data; do not fabricate. |
| 8 | `Page Traffic` | int or `"-"` | Ahrefs `site-explorer-metrics` (mode=`exact`, target=Article URL) | Monthly organic visits to the specific article URL, last 30 days. `"-"` if Ahrefs has no data. |
| 9 | `Referring Domains` | int or `"-"` | Ahrefs `site-explorer-backlinks-stats` (target=Domain) | Domain-level refdomain count. `"-"` if Ahrefs has no data. |
| 10 | `Prospect Tier` | enum | Computed from DR + Page Traffic + user goal | One of: `A`, `B`, `C`. See SKILL.md Step 5 for thresholds. Empty for rows where Ahrefs failed. |
| 11 | `Why This Prospect` | string | Computed (see SKILL.md Step 7) | One or two comma-joined tags, ordered by pitch strength. `"-"` when no tag fits. |
| 12 | `Article Author` | string | Author list dataset (primary); WCC metadata fallback. | `"Not found"` if unknown. Never fabricate. |
| 13 | `Author Source` | enum | how the author was sourced | One of: `searchAuthorName`, `metadata.author`, `openGraph`, `jsonld`, `not found`. |
| 14 | `Publish Date` | ISO date or `"Not found"` | Google Search Scraper sub-dataset `publishDate` (primary); WCC `metadata.publishedAt` (fallback). | |
| 15 | `Contact Full Name` | string | All leads dataset `firstName + ' ' + lastName`, prioritised by editorial-leaning job title (see SKILL.md Step 8 rule 2) | |
| 16 | `Contact Job Title` | string | All leads dataset `jobTitle` | |
| 17 | `Department` | string | All leads dataset `departments[0]` | |
| 18 | `Seniority` | string | All leads dataset `seniority` | e.g., `vp`, `head`, `manager`. |
| 19 | `Contact Email` | string | All leads dataset `email` | `"Not found"` if unknown. Never fabricate. |
| 20 | `Email Verification` | enum | All leads dataset `email_verification` (when `enableEmailVerification: true`) | One of: `verified`, `catch-all`, `risky`, `invalid`, `unknown`, `-` (when verification didn't run). `invalid` triggers an auto-skip in Step 6 rule 11; `catch-all` / `risky` / `unknown` are informational and surface a Notes hint. |
| 21 | `Contact LinkedIn` | URL | All leads dataset `linkedinProfile` | |
| 22 | `Company` | string | All leads dataset `companyName` | |
| 23 | `Outreach Type` | enum | Computed from `Why This Prospect` + goal (see SKILL.md Step 8 rule 4) | One of: `unlinked-mention-claim`, `competitor-link-replacement`, `resource-page-inclusion`, `outdated-content-replacement`, `topical-niche-edit`. Empty for skipped rows. |
| 24 | `Partnership Offer` | string | User-supplied at Step 2 | Same value for every row. |
| 25 | `Placement Source Sentence` | string | Agent-generated from WCC page body | The verbatim sentence from the article where the link will go. Filled in strategies 1 (drop-in) and 2 (additive); `"-"` for strategy 3 (new insertion). |
| 26 | `Placement With Link` | string | Agent-generated | For drop-in: the source sentence with the link added on an existing word (no other text change). For additive: the source sentence kept verbatim + one new follow-on sentence containing the link. `"-"` for new insertion. |
| 27 | `Placement New Insertion` | string | Agent-generated | A drafted 1–2 sentence paragraph in the article's voice with a precise insertion location. Used only when no existing sentence is a natural fit (strategy 3); `"-"` otherwise. |
| 28 | `Suggested Email Copy` | string | Agent-generated | Subject + body, separated by `\n---\n`. ≤150 words including subject. Brand-voice matched. Outreach-type template per `Outreach Type` column. Empty for skipped rows. |
| 29 | `Outreach Status` | enum | Default `"Not started"`; `"Skip"` for rows dropped in the skip pass | |
| 30 | `Notes` | string | Agent-generated | Placement strategy tag (`Placement: drop-in` / `additive` / `new insertion`), skip reason if skipped, email-verification hints if status is non-`verified`, auto-flags, manual-lookup hints when fields are `"Not found"`, alternate contacts. |

### Placement column rule (critical)

Exactly one of columns 24, 25, 26 is filled per non-skipped row:

- If the article already contains a sentence that the link fits naturally → fill **25** (`Placement With Link`) AND **24** (`Placement Source Sentence`); leave 26 as `"-"`.
- If no existing sentence is a natural fit but the article topic still supports a link → fill **26** (`Placement New Insertion`); leave 24 and 25 as `"-"`.
- If the article topic is wrong for the user's URL entirely → set `Outreach Status = "Skip"` with `Notes: "No natural placement — article topic mismatch"` and leave all three placement columns as `"-"`.

## xlsx rendering

The runner script writes a styled `.xlsx` to the path passed via `--output` with **two sheets**:

### Sheet 1: `Outreach` (active rows, full schema)

This is the send-ready deliverable. Only rows with `Outreach Status != "Skip"` appear here, with the full 30-column row schema documented above.

### Sheet 2: `Skipped` (filtered rows, reduced columns)

For auditing what the pipeline filtered. Reduced 6-column schema so missing Ahrefs / placement / email data doesn't visually clutter the view:

| # | Column | Source |
|---|---|---|
| 1 | `Domain` | Same as Outreach sheet col 6 |
| 2 | `Article URL` | Same as Outreach sheet col 5 |
| 3 | `Article Title` | Same as Outreach sheet col 4 |
| 4 | `Skip Reason` | Extracted from Outreach sheet col 30 (Notes) — the part after `SKIP:` and before any `|` separator |
| 5 | `Source Engines` | Same as Outreach sheet col 2 |
| 6 | `Why This Prospect` | Same as Outreach sheet col 11 |

User opens the file → lands on `Outreach` by default → sees only actionable rows. Switches to `Skipped` when they want to audit what was filtered or recover a borderline row manually.

Common Outreach-sheet styling:

- Header row in bold, frozen.
- Column widths (in order, columns 1–30):
  - 12 (SERP Position), 32 (Source Engines), 24 (Keyword), 60 (Article Title), 70 (Article URL),
  - 24 (Domain), 10 (Domain DR), 14 (Page Traffic), 14 (Referring Domains), 12 (Prospect Tier),
  - 40 (Why This Prospect), 24 (Article Author), 14 (Author Source), 12 (Publish Date),
  - 24 (Contact Full Name), 30 (Contact Job Title), 16 (Department), 14 (Seniority),
  - 30 (Contact Email), 16 (Email Verification), 50 (Contact LinkedIn), 24 (Company), 24 (Outreach Type), 30 (Partnership Offer),
  - 80 (Placement Source Sentence), 80 (Placement With Link), 80 (Placement New Insertion),
  - 100 (Suggested Email Copy), 16 (Outreach Status), 60 (Notes).
- Cell wrap-text enabled for the long columns (Article Title, Why This Prospect, Placement Source Sentence, Placement With Link, Placement New Insertion, Suggested Email Copy, Notes).
- `"Not found"` and `"-"` rendered in italic.
- Row sort: `Prospect Tier` ascending (A first), then `Domain DR` descending, then `SERP Position` ascending. Skipped rows render last.
- Conditional formatting on `Prospect Tier`: green = A, yellow = B, grey = C, red strikethrough = skipped.

The runner writes only the columns it can populate from the Actor datasets (columns 1–6, 12–21, 28). The agent must then:
1. Load the .json after the Actor run finishes.
2. Run Step 5 (Ahrefs enrichment) → fill columns 7, 8, 9, 10.
3. Run Step 6 (skip pass) → fill column 28 + 29 for skipped rows.
4. Run Step 7 (Why This Prospect) → fill column 11.
5. Run Step 8 (placement + email + outreach type) → fill columns 22, 24, 25, 26, 27.
6. Re-save the .xlsx.

See `scripts/run_actor.js` for the round-trip pattern.

## Markdown rendering

The agent renders this directly in chat. Structure:

```
# Link prospecting results — <date>

Run ID: <apify-run-id>
Keywords: <comma-joined>
Brand: <brand name>
Content URL: <user url>
Goal: <user's goal>
Partnership: <partnership type>
Tier breakdown: A: <n>, B: <n>, C: <n>, Skipped: <n>

| # | Tier | Why | SERP | Domain | DR | Traffic | Article | Contact | Outreach Type | Placement |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | Links to competitor (X.com) | 3 | example.com | 72 | 1,200 | [Title](url) | Mark Lee (Head of Content) — mark@example.com | competitor-link-replacement | (sentence diff or insertion preview, truncated to 80 chars) |
| ... |

## Email drafts

### Row 1 — Tier A — example.com — competitor-link-replacement — Mark Lee

**Subject:** ...

> Hi Mark,
>
> ...

Placement:
- Source: "Several tools handle this well, including X and Y."
- With link: "Several tools handle this well, including X, Y, and **[Brand](URL)**."

### Row 2 — ...
```

Skipped rows render in a separate collapsed section at the bottom:

```
## Skipped (<n>)

| Domain | Reason |
|---|---|
| example.org | Stale content (published 2018-04-11) |
| ... |
```

Keep the main Markdown table to the most actionable columns (the 11 above) and surface the rest via the JSON sidecar if the user asks. Output ALL columns in xlsx.

## `run_metadata.json` sidecar

Always emit this alongside the main output, even in Markdown mode (write it to disk in the same directory the user ran from):

```json
{
  "runId": "abc123...",
  "actorId": "apify/link-prospecting-tool",
  "startedAt": "2026-05-13T10:15:00Z",
  "finishedAt": "2026-05-13T10:23:11Z",
  "inputs": {
    "goal": "Topical authority links to specific URL",
    "queries": "best search engine\nalternative to google",
    "brand": "Acme",
    "ownDomains": ["acme.com"],
    "competitorDomains": [],
    "alreadyPitchedDomains": [],
    "organicResult": 10,
    "maxContactsPerDomain": 3,
    "department": ["marketing"],
    "searchAuthorName": true,
    "includeMention": true,
    "enableChatGpt": true,
    "enableAiMode": true,
    "enableAiOverviews": true,
    "enablePerplexity": true
  },
  "datasetIds": {
    "default": "...",
    "mentions": "...",
    "domainsWithLeads": "...",
    "authors": "...",
    "subActors": "...",
    "googleSearch": "...",
    "websiteContentCrawler": "..."
  },
  "tierCounts": { "A": 8, "B": 15, "C": 7 },
  "skipCounts": {
    "goalMismatch": 5,
    "alreadyPitched": 2,
    "staleContent": 3,
    "nonEditorialPage": 1,
    "ugc": 0,
    "noContactNoAuthor": 1,
    "topicMismatch": 0
  }
}
```

This is what makes the outreach work reproducible. Reference it when the user asks "where did row 7 come from?" — they (or you) can re-fetch each dataset from Apify storage by the IDs.
